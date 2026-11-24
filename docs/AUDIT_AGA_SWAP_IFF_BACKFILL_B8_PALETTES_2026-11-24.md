# Audit AGA P2d — passage 7 : Swap → IFF/Back Fill, B8 et palettes/banques

**24 novembre 2026** · **Dépôt :** `anthea176/AMOSPro-AGA-Extension` · **Branche : `main` uniquement** · Sources P2d revues sur le commit **`defa13266d4cc84d6956d187cc623607677ca606`**. Analyse statique seule, aucune Gate A/B/C/D de cette campagne exécutée.

**Référence P2d auditée :** `dist/AMOSPro_AGA_LAST_GOOD.Lib`, **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, source [master lié MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_P2D_LINKED_EDITABLE.s), builder `tools/build_m19_p2d_in_memory.py`, **100 commandes publiques** (liaisons AP20 documentées séparément). La candidate `dist/AMOSPro_AGA.Lib` **S1-P1e 142 000 octets**, SHA256 `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106`, reste conservée **GELÉE**.

## 1. P0 statique : un Swap réussi publie un nouveau Safe pending que les deux anciennes commandes ignorent

La [cartographie AP20 P2d](AUDIT_AGA_AP20_LIAISONS_P2D_2026-11-24.md) relie effectivement les commandes à ces cibles :

| Entrée | AP20 / cible | Chemin lié | Constat |
|---|---|---|---|
| `Aga Swap` | 181 / BOBS+$0B606 | [P2d Auto/Swap](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s#L73-L152) → [Swap natif UNIT142](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_BLOCK_00BA2_MC68020.s#L6-L88) | Si le chemin de présentation réussit, il positionne **`DB+20 = 3`** (Safe et Disp pending) après `ChangeScreenBuffer(-780)`. |
| `Aga Iff Load` | 24 / UNIT142+$00D3C | [IFF BODY](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L44-L81) → [sélection bitmap](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L321-L403) → [écriture CPU](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L403-L479) | `WaitBlit(-228)` puis `move.b` directement vers chaque plan ; **aucune lecture/acquisition de SafePort entre sélection du back et écriture**. |
| `Aga Back Fill` | 22 / UNIT142+$00C9E | [routine complète](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_BLOCK_00C9E_MC68020.s#L6-L56) | Sélectionne le bitmap de la page arrière, initialise un RastPort, puis **`SetRast(-234)`**, `WaitBlit(-228)`. **Ni test `DB+20 bit0` ni `GetMsg(-372)`** avant SetRast. |
| `Aga Blit Fill` (témoin sûr) | 33 / UNIT142+$02360 | [wrapper](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_BLOCK_02360_MC68020.s) → [Fill natif](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_BLOCK_078A4_MC68020.s) | Vérifie le Safe pending puis `GetMsg(-372)` avant de dessiner ; retour 0 en cas de refus. |

**La séquence `Aga Swap` réussi → `Aga Iff Load` ou `Aga Back Fill` (sans commande intermédiaire consommant SafePort) est donc une violation *atteignable statiquement* de la discipline Safe du projet.** Les deux anciennes commandes peuvent atteindre l'écriture avec `DB+20 bit0=1`. Cela **ne prouve pas** qu'un pixel front a effectivement été corrompu sous WinUAE : le message Safe peut déjà être matériellement disponible, mais le programme ne l'a pas consommé ; il faut distinguer Safe absent et Safe arrivé/non acquitté.

La commande `Back Fill` est une **instruction sans code de retour**, pas une fonction `1/0`. La vérification doit observer les pixels/bitmaps et les messages OS, pas un résultat fictif. `WaitBlit` synchronise le Blitter, **ne consomme pas SafePort**. L'absence de garde était [déjà documentée en R27](M12_SAFE_BLITTER_R27.md), et n'est pas une régression inventée de P2d.

### Rectification matérielle de l'audit précédent

**`graphics.library -234` = `SetRast`, et `-306` = `RectFill`.** Les rapports précédents confondaient les deux vecteurs pour `Aga Back Fill`. Le premier remplit **tout le RastPort/bitmap**, correspondant au contrat public ; le second travaille sur un rectangle et est utilisé ailleurs, notamment pour `Aga Blit Fill`. Voir [table des vecteurs AmigaOS](https://anadoxin.org/blog/amigaos-stdlib-vector-tables.html/) et [LVOs.i](https://github.com/jotd666/amiga68ktools/blob/master/tools/LVOs.i). **Seule l'identification de l'API appelée était fausse ; la lacune Safe reste confirmée.**

**Classement maintenu : AGA-001 / AGA-010 = P0 préventif, lacune Safe avérée dans le code, effet graphique réel non reproduit.** Aucun patch pendant le gel.

## 2. IFF : double passe déterministe en entrée normale ; AGA-007 non avérée

La [routine chargement IFF](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L44-L80) lit une copie privée du fichier dans un bloc RAM alloué via Exec, identifie les chunks ILBM, puis fait :

1. **Première passe** `L_UNIT142_01360` : `100(a5)=0` ; parse toutes les lignes/planes du BODY (ByteRun1 ou sans compression), contrôle tailles et fin.
2. **Allocation** de la table de palette RGB32 dans `L_UNIT142_01492` avant d'écrire les pixels.
3. `WaitBlit`, puis **deuxième passe** : `100(a5)=1`, même buffer BODY, mêmes limites/dimensions, avec écriture dans les plans.
4. **Après la seconde passe seulement**, appel de `LoadRGB32(-882)` suivi de `WaitTOF(-270)` dans [`L_UNIT142_0150E`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L557-L568). La palette est celle du ViewPort/ColorMap actif, **pas un état de palette par page B8**.

**AGA-007 :** le source n'expose **aucune mutation prévue du buffer d'entrée** entre les deux passes ; un BODY tronqué devrait normalement être rejeté par la première. Une erreur atteignant la deuxième passe après la validation reste **non démontrée**. La routine ne dispose toutefois pas d'un rollback des plans *si* une erreur survient après le début des écritures. **Ne pas qualifier « IFF tronqué = corruption partielle » comme bug avéré sans contre-exemple reproductible.** T12 contrôle la stabilité des plans sur refus, y compris un échec avant l'écriture.

La palette peut devenir visible sur le front immédiatement après application, **indépendamment du Swap**. Cela n'implique pas de restauration d'un snapshot bitmap, mais doit être compté distinctement d'une différence de pixels.

## 3. B8 : premier Bind et récupération — AGA-002 confortée, pas nouvellement corrigée

- `Aga Swap` P2d, en mode Auto avec propriétaire et garde propres, trouve un Bob actif et appelle [`p2d_service_update`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s#L95-L140) **avant** `guarded_swap_entry`.
- Lors de la première constitution du pool, [`L_BOBS_0D738`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_P2D_SERVICE_BODY_MC68020.s#L1402-L1457) appelle `L_BOBS_0C51E` → `L_BOBS_0BE32` **avant** de publier le root. Le [sélecteur natif](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_P2D_SUPPORT_TAIL_MC68020.s#L595-L671) teste `DB+20 bit0` et **refuse immédiatement** si Safe pending, sans `GetMsg`.
- `p2d_service_update` retourne alors 0, et **le Swap historique n'est pas appelé** pour acquitter le message. [Le service B8 de régime établi](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_P2D_SYSTEM_SERVICE_MC68020.s#L101-L137) possède `GetMsg`, mais suppose un root/pool déjà constitué.
- **`Aga Wait Vbl` seul n'acquitte pas SafePort**. Un writer sûr comme `Aga Blit Fill`, avec Safe effectivement disponible et retour 1, peut constituer un témoin discriminant de reprise. Un Safe pending **sans notification disponible** doit au contraire aboutir à un refus sans écriture — ce refus est légal.

**Classement AGA-002 : P1 conditionnel statique sur premier Bind**, pas freeze CPU démontré. Les cinq variantes **T02 A–E** restent nécessaires, **non exécutées**.

## 4. Palettes et banques — séparer valeur RGB, pixels, et ressource Chip

### Palettes : pas de « snapshot périmé » du seul fait d'un changement RGB

- `Aga Palette Set` AP20 **67** → [UNIT142+$03A24](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_BLOCK_03A24_MC68020.s#L39-L96) ; vérification du Screen/ColorMap, puis `LoadRGB32(-882)`. **Pas d'écriture de plan bitmap** dans cette entrée.
- `Aga Palette Bank Apply` AP20 **77** → [UNIT142+$044EA](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_ENTRY_044EA_MC68020.s#L104-L201) ; contrôle d'en-tête/slot AGAPAL, construction d'une table RGB32 temporaire et application au ViewPort ; **pas de pixel modifié**.
- `Aga Palette Cycle` AP20 **85** → [UNIT142+$04F58](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_UNIT142_ENTRY_04F58_MC68020.s#L46-L157) : `GetRGB32(-900)` → rotation en mémoire temporaire → **un `LoadRGB32(-882)`** ; aucune sauvegarde de fond.
- Le [cœur snapshot B8](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/tools/m19_b8_planar_snapshot_emit.py) recopie les **plans du BitMap**, index de couleur par pixel, **pas** le ColorMap RGB32. Une palette changée peut donc modifier l'apparence des Bobs et du décor **sur toutes les pages** sans rendre les snapshots de plans invalides.

**Conséquence AGA-003 :** il serait incorrect d'imposer un `Aga Bob Clear` simplement pour `Palette Set`/`Apply`/`Cycle`. Le contrat `Aga Bob Clear → écriture du décor → Aga Swap` s'applique aux **modifications des pixels sous Bob**, non à un changement indépendant de ColorMap. L'affichage palette-only doit être comparé en RGB **et** les snapshots en indices pour éviter les faux positifs.

### AGBO : Bank Free est une libération de cache contrôlée, pas Erase Bank

- `Aga Bob Bank Free` AP20 **198** → BOBS+$0E854 (pont vers [`b8s1_bank_free_entry`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_B8S1_BANK_FREE_MC68020.s#L15-L50)) : garde **frame_guard_state `CLEAN`**, contrôle du propriétaire et des 64 slots, désactivation des Bobs associés au numéro de banque, puis [`p2b_bank_free`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_B8S1_BANK_FREE_MC68020.s#L138-L209).
- Le [pont P2b](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/defa13266d4cc84d6956d187cc623607677ca606/src/native/m19_p2d/M19_P2B_CLEANUP_MC68020.s#L33-L70) appelle le libérateur de registry et purge les variantes de cache de la banque. Le [contrat P0 Bank Free](M19_P0_BANK_FREE_GATES_2026-11-20.md) précise que **la banque AMOS DATA reste conservée**, et qu'un `Poke` direct dans un AGBO déjà préparé est **hors contrat**.
- Ne pas confondre cette libération contrôlée avec **`Load` / `Erase Bank` externes** modifiant une banque AMOS, pouvant remplacer son adresse/numéro tandis que des Bobs ou caches préexistants subsistent. Les contrôles actuels d'owner et `TypeOfMem` ne prouvent pas à eux seuls la validité de toutes ces transitions, en particulier une réallocation à la même adresse.

**Statut :** Bank Free dispose de garde locale/chemin sélectif documenté, mais **T10 reste VM** pour séquences réelles Load/Erase/re-sélection/fermeture avec snapshots, sans annoncer de use-after-free sans preuve.

## 5. Cahier discriminant — pas de 20e scénario

| ID conservé | Variantes nouvelles à vérifier (sans nouveau programme écrit) | FAIL conditionnel |
|---|---|---|
| **T02** | Pool B8 absent, Safe pending message disponible/absent ; témoin avec GetMsg effectif avant Bind ; régime établi | Refus de progression seulement lorsque notification disponible mais non acquittée ; aucune écriture avant Safe |
| **T04** | Swap réussi crée `DB+20=3` ; IFF juste après Swap, avec BODY témoin, deux bitmaps inspectables, puis IFF après GetMsg sûr | BODY écrit sur back non Safe ; aucune garantie de sécurité sans vérification |
| **T10** | AGBO Bank Free en CLEAN, puis re-sélection ; rejet READY/DIRTY ; banque effacée/rechargée à même numéro ou potentiellement même adresse | Lecture de banque morte, cache Chip non invalidé, Bob incorrect après réallocation ; **ne pas confondre usage hors contrat (Poke)** |
| **T12** | IFF tronqué ByteRun1, CMAP/BMHD/plan invalides, vérifier plans et ColorMap séparément, Safe acquis ; même buffer chargé deux passes | Un échec modifie des plans ou palette ; vérifier source exacte, ne pas inférer l'échec de seconde passe |
| **T17** | RPG décor IFF après Swap + premier Bob Auto ; contrôle `Aga Blit Fill` protégé avant IFF et avant premier Bind, sans changer artificiellement le décor de référence | Images divergeant sur pages physiques, root B8 jamais lié ou refus sans cause identifiée |
| **T19** | Back Fill **SetRast** immédiatement après Swap, pending absent puis message arrivé non consommé ; comparer avec Blit Fill protégé | `SetRast(-234)` appelé avant Safe, indépendamment des pixels affichés |

**Gates :** A = simulation Exec/Graphics + flags et appels ; B = WinUAE Runtime exact ; C = véritable exécutable Compiler exact. Aucune Gate passée ici. Ne pas essayer volontairement d'écrire sur un front non Safe sur machine physique ; encadrer d'abord par simulation puis WinUAE.

## 6. Décision de conception à soumettre après l'audit, sans correction

Le système a au minimum **deux écrivains sans acquisition Safe locale** (IFF et Back Fill) et **un lecteur de Safe pending qui refuse sans consommer** pendant le premier Bind B8. Avant toute correction, spécifier un **protocole Safe commun ou une garde réutilisable** avec la propriété suivante : *si Safe pending, consommer une notification quand elle existe ; sinon refuser proprement sans écriture, tout en préservant Disp*. Vérifier séparément les commandes sans retour (Back Fill), les commandes fonction `1/0` (IFF), et les transitions B8. Éviter une solution qui masque les refus par un `WaitTOF` en boucle ou transforme le compteur de la Gate B en preuve de sécurité.

**AUCUNE correction appliquée ; aucun nouveau test exécuté ; aucun programme, binaire, journal ni asset modifié ; S1-P1e toujours GELÉ.**
