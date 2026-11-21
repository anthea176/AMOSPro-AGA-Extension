# Sprites matériels AGA — S0, audit d'intégration initial (21/11/2026)

> **Reprise S0 du 21/11/2026 :** [audit d'intégration NDK et sources P2d](AGA_HARDWARE_SPRITES_S0_INTEGRATION_2026-11-21.md), modèle de propriété [host-only](../tools/aga_sprite_s0_model.py) et [12 tests hôtes PASS](../tools/test_aga_sprite_s0_model.py). S0 reste **OUVERT** tant que le ViewPort réel, les canaux disponibles et le détachement DMA ne sont pas prouvés. Aucun nouveau token/Lib/ASC ; P2d `LAST_GOOD` inchangée. Le banc actuel est [M19_P2_ALL_IN_ONE.asc](../tests/current/M19_P2_ALL_IN_ONE.asc), et non P2e.1.


> **Suite après clôture M19 Bob P2d :** P2d promue `LAST_GOOD` (Gates A/B/C du scénario P2 PASS). **Prochain travail : reprendre S0 ici**, auditer NDK/ABI et la gestion native du `ViewPort`, des canaux Sprite, du pointeur Intuition et des listes Copper. S0 n'est **pas** terminé, S1 non implémenté. Ne pas développer les Sprites en modifiant la Lib P2d promue sans nouvelle autorisation de candidat.


> **Statut : AUDIT DOCUMENTAIRE ET DE CONTRAT EN COURS, PAS S0 TERMINÉ.**
> Dépôt `anthea176/AMOSPro-AGA-Extension`, branche `main` uniquement.
> Ce document n'autorise ni binaire, ni API, ni commande `Aga Sprite`, ni remplacement de l'unique ASC de régression P2 ALL IN ONE actuellement actif.
> Cible native future : **MC68020/68EC020 minimum**, Kickstart 3.0+ / `graphics.library` V39+, chipset AGA.

## 1. Constat sourcé dans l'extension

| Sous-système | Contrat déjà présent | Conséquence Sprite |
| --- | --- | --- |
| Écran privé | [M3](M3_SCREEN_DESIGN.md) : écran `Intuition Screen*`, `ViewPort` géré par l'OS ; `Aga Screen Open/Close` séparés des écrans AMOS | Le Sprite doit être lié au display propriétaire de l'extension, pas à l'écran AMOS OCS. Contrôler l'instance `Screen*` effective. |
| Copper utilisateur | [M7/R18](M7_COPPER_R18.md) : `graphics.library/UCopList`, `ViewPort.UCopIns`, installation via `MakeScreen/RethinkDisplay` ; seuls `COLOR00..31` RGB4 autorisés | **Ne pas écraser** les listes du ViewPort ni `COP1LC/COP2LC`. Le moteur Sprite n'a pas le droit de réutiliser les deux bits privés de `Screen.UserData` affectés au Copper. |
| Pointeur Intuition | [M15bis/R44](M15BIS_MOUSE_CURSOR_R44_DESIGN.md) : `Aga Mouse Cursor` appelle `SetPointer/ClearPointer`, avec un tampon transparent **72 octets Chip** possédé par la fenêtre | Cacher le pointeur **ne prouve pas** la disponibilité d'un canal DMA Sprite. Ne jamais modifier le pointeur global du Workbench. |
| Bobs | [M19 P2d](M19_P2D_BOB_AUTO_UPDATE_MODEL.md) : Bobs logiciels dans les bitplanes, fonds des deux pages, `Aga Swap` gardé, Chip caches privés | Le Sprite DMA est **distinct** du Blitter, ne dessine dans aucun back buffer et ne déclenche aucun `Aga Swap` implicite. |
| AMAL | [P2e.0 Runtime PASS](M19_P2E0_AMAL_BRIDGE_2026-11-21.md) et [banc intégré P2a–P2e VALIDÉ B/C](../examples/bob_p2_all_in_one/README.fr.md) | AMAL fournit des positions/images via des tampons mémoire 8 octets par canal. Une passerelle ultérieure vers Sprite reste facultative ; aucun code DMA en interruption. |

La [feuille S0–S3](AGA_HARDWARE_SPRITES_S0_S3_ROADMAP.md) sépare déjà Bobs et Sprites. **L'audit des offsets, propriétaires, transitions d'écran et de la source native exacte de l'ouverture/fermeture P2d reste à faire avant S1 natif.** Les contrats historiques M3/M7/R44 ne démontrent pas à eux seuls l'état réel des ressources Sprite de la Lib P2d.

## 2. API AmigaOS identifiées (référence V39)

Les tables [graphics.library Autodocs](https://developer.amigaos3.net/autodocs/graphics.library/) et [offsets LVO V39](https://d0.se/autodocs/graphics.library) identifient :

- `AllocSpriteDataA` : créer les données Sprite étendues depuis le format exigé par l'API ; libération par `FreeSpriteData`.
- `GetExtSpriteA` : demander l'allocation d'un canal matériel ; refuser proprement si aucun canal disponible.
- `ChangeExtSpriteA` : changer l'image attachée au Sprite étendu ; `MoveSprite` pour le déplacement selon le contrat des structures.
- `FreeSprite` : rendre au système **seulement le canal réellement acquis**.
- **Alternative plus simple pour S1** : `GetSprite/ChangeSprite/MoveSprite/FreeSprite` avec `SimpleSprite`, seulement si elle coopère correctement avec le pointeur Intuition et le `ViewPort` privé sous WinUAE.

Les noms et la disponibilité V39 sont confirmés. **Les prototypes ABI exacts, tags `SPRITEA_*`, conditions de passage du `ViewPort*`, format d'entrée et règles d'update ne sont PAS encore vérifiés contre les includes NDK installés.** Aucun LVO ou registre n'est émis à ce stade.

La [doc officielle du pointeur Intuition](https://wiki.amigaos.net/wiki/Intuition_Pointer) confirme l'exigence de Chip RAM pour les données que lit le matériel.

## 3. Décisions de travail proposées, non encore APIs

1. **S1 = un Sprite 16 pixels, non attaché** : trois couleurs visibles plus index 0 transparent. Pas de multiplexage, pas de 32/64, pas de couleurs 256 par Sprite.
2. **Allocation via l'OS** ; ne pas réserver arbitrairement le canal 0, 1 ou 2. Enregistrer l'ID réellement attribué, l'appartenance et les ressources Chip ; si allocation échoue, aucun DMA ni restauration artificielle de pointeur.
3. **État propre au contexte écran** : `NON_ALLOCATED → DATA_READY → CHANNEL_OWNED → VISIBLE → DISABLED → RELEASED`. Sur erreur, revenir à un état cohérent et nettoyer **seulement** les ressources possédées.
4. **Position logique en pixels écran** : conversion contrôlée vers coordonnées matérielles avec `ViewPort` et offsets d'affichage, sans réutiliser aveuglément `X Hard/Y Hard` des écrans AMOS. Le hotspot sera un réglage explicite éventuel.
5. **Cycle du dessin distinct** : les updates Sprite ne touchent ni `Aga Bob Update`, ni `Aga Swap` ni les notifications `Safe/Disp` réservées au rendu bitplane ; tester la synchronisation réelle au balayage avant optimisation.
6. **Palette et largeur** : la documentation secondaire donne des cartographies divergentes pour `FMODE` et `BPLCON3/BPLCON4`. **Aucun bit de registre codé** avant recoupement NDK/AGA chipset guide + tests WinUAE. Une palette Sprite ne doit pas modifier inopinément les 256 couleurs de l'écran.
7. **Nettoyage** : désactivation/fin d'utilisation du canal avant libération de ses données Chip, restitution du canal possédé, puis fermeture normale du contexte AGA ; aucun `FreeSprite` sur canal non acquis, ni suppression des listes système du ViewPort.

## 4. Banc discriminant S1 à écrire après clôture du verrou S0

| Cas | Observation attendue (NON TESTÉE) |
| --- | --- |
| Ecran 320×256×8, pointeur visible | Sprite 16×16 dessiné indépendamment du Bob, aucun artefact du pointeur |
| Sprite déplacé devant deux Bobs | Déplacement Sprite sans restauration du fond ; Bobs et Swap P2d inchangés |
| Pointeur caché/restauré via `Aga Mouse Cursor` | Pas de disparition du Sprite ni corruption du pointeur Workbench |
| Copper M7 actif/inactif | `Aga Copper On/Off` ne perd ni les canaux ni les listes Sprite du ViewPort |
| Fermer/réouvrir écran, puis Ctrl+C | Pas de Guru, free invalide, fuite Chip progressive ni pointeur fantôme |
| Aucun canal libre / OOM Chip | Refus déterministe, canal et données inchangés sur l'échec |
| Runtime et vrai Compiler | Même rendu/cleanup, preuves B et C **distinctes** |

L'unique ASC sous `tests/current/` demeure **[M19_P2_ALL_IN_ONE.asc](../tests/current/M19_P2_ALL_IN_ONE.asc)** après validation B/C et promotion de P2d. Ce tableau n'est **pas** un nouveau programme de test, une version de Lib ou une preuve de Gate A/B/C/D.

## 5. Verrous restants avant implémentation native S1

- Inspecter l'émetteur/builder **actuellement autoritatif** de l'écran AGA, les allocations `Screen/Window/DBState`, la fermeture/End et l'enchaînement `Aga Copper On/Off` et `Aga Mouse Cursor` dans la Lib P2d : offsets, propriétaire, hooks et ordre exact.
- Lire les includes NDK `graphics/sprite.h`, `graphics/gfx.h`, prototypes LVO V39, tags et contraintes d'allocation étendue ; établir la signature ABI MC68020 de chaque appel **avant code**.
- Confirmer les limitations de largeur/palette et la façon dont les canaux sont attribués au ViewPort privé sous Kickstart 3.0.
- Réaliser un modèle de propriété/cleanup et ses tests statiques Gate A, puis proposer un protocole d'essai indépendant sans modifier l'actuelle campagne Bob/AMAL.

**Proposition :** ne pas créer de token `Aga Sprite` tant que ces verrous ne sont pas levés. Ensuite, le prototype S1 sera le plus petit Sprite 16×16 possible, avec fenêtre/souris et contrôle de libération ; les paires attachées et 32/64 pixels resteront S2.
