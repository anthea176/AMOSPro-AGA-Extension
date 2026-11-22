# S0 — Audit d'intégration des Sprites matériels AGA (21 novembre 2026)

## 22/11/2026 — S0d : Gates B/C WinUAE closes, visuels confirmes

Les journaux **originaux** [Runtime, 478 octets CRLF](evidence/M19_S0D_ROB_RUNTIME_2026-11-22.TXT) (SHA256 `87ae3944c5703cd3b014894caeca5261130e8e521b58b1c7cdf3f9d185faf928`) et [Compiler, 479 octets CRLF](evidence/M19_S0D_ROB_COMPILED_2026-11-22.TXT) (SHA256 `818381dfdb46c88e10a5c2dbe4a7b217b0469114d45938ed5897c7956a8fc81a`) correspondent au meme [ASC S0d](../tests/design/sprites_aga/SPRITE_PROBE.asc), Git blob `eb4e9d0275edbe3266724705910fa66747c743ea`, `SOURCE_TAG M19_S0D_ROB_V1`. En Compiler : `PRG_STATE -1`, `RUN_MODE COMPILED`, `RESULT 1`, `ERR 0`, `CYCLES_OK 3`, `GETS/FREES 3`, `MOVES 108`, `COPPER_ON/OFF 1/1`, `BANK_FREES 3`, `OWN_REMAINING -1`. Les logs sont **identiques hors PRG_STATE/RUN_MODE**. L'auteur confirme le rendu du Sprite 16x16 et du raster en Runtime et Compiler, sans artefacts. **S0d Gates B/C PASS pour ces scenarios**, sans transfert de preuve vers une nouvelle API native.

**Non clos :** synchronisation DMA/detachement formel, mesure independante de fuites Chip, autres configurations, Amiga AGA reel (Gate D). Le `FreeSprite` retourne le canal OS ; ce fait n'est pas une preuve qu'une ancienne liste Copper a cesse de lire le tampon DMA. Les 2 VBL et 3 WaitTOF du banc ne sont **pas** un protocole de liberation valide sur tout materiel. Un futur S1 doit lever ce verrou avant de gerer lui-meme des ressources Chip/Screen.

**Suite documentaire :** [contrat S1 PROPOSE](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md) ; sa presence n'autorise aucun nouveau token AP20, ASM, builder ou binaire. L'ancien corps de ce rapport conserve les etapes et annonces historiques, non le statut le plus recent.


## 22/11/2026 — S0d : preuve Runtime et protocole Compiler

Le [journal S0d brut, CRLF](evidence/M19_S0D_ROB_RUNTIME_2026-11-22.TXT) (478 octets, SHA256 `87ae3944c5703cd3b014894caeca5261130e8e521b58b1c7cdf3f9d185faf928`) confirme `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `CYCLES_OK 3`, `MOVES 108`, `GETS/FREES 3`, `BANK_FREES 3`, `BANK_HELD_ANY 0`, `COPPER_ON_OK/OFF_OK 1`. L'auteur confirme les Sprites et le raster visibles sous WinUAE ; **Gate B PASS pour ce scenario uniquement**. Les compteurs attestent la sequence du programme, pas un audit DMA materiel ou une mesure directe de fuites.

**Gate C a venir** : conserver sans modification [l'unique ASC S0d](../tests/design/sprites_aga/SPRITE_PROBE.asc), Git blob `eb4e9d0275edbe3266724705910fa66747c743ea` ; effectuer une vraie compilation AMOS Professional sous WinUAE de cette source avec la Lib P2d deja installee, puis lancer la **version compilee**. Journal attendu : `RAM:M19_S0D_ROB_COMPILED.TXT`, `PRG_STATE -1`, `RUN_MODE COMPILED`, `RESULT 1`, `ERR 0`, `CYCLES_OK 3`, `VERDICT PASS_ROBUSTNESS_SEQUENCE_ONLY`. Un log Runtime recopie ou une compilation sans lancement ne suffit pas. Voir [procedure complete](NEXT_SESSION.md). **Gates C/D non testees**, protocole de detach DMA toujours experimental.


## 22/11/2026 — Preuve S0c et test S0d de robustesse

Le [journal S0c d'origine](evidence/M19_S0C_VIS_RUNTIME_2026-11-22.TXT) (**565 octets, CRLF, SHA256 `266444494d1ced0fc0e401bfca4c145b5a097ca9bcf066b7c0957e5701d50160`**) affiche `RESULT 1`, `ERR 0`, `MOVE_FRAMES 100`, `GET_CHANNEL 1`, `FREE_SPRITE 1`, `CLOSE_RETURNED 1`, `BANK_CLEAN 1`. L'utilisateur a confirme que le F etait visible, mobile, sans artefact. **Gate B scenario S0c PASS**, pas de preuve de detach DMA formel.

Le [programme unique de travail](../tests/design/sprites_aga/SPRITE_PROBE.asc) passe a **S0d**, trois cycles consecutifs avec cursor toggle puis Copper RGB4 On/Off. Allocation par OS exclusivement, stockage Chip propre a chaque cycle, compteur de liberation et cleanup en cas d'erreur. Le Copper ne modifie que `COLOR00` via les fonctions existantes et est desactive avant fermeture. La source ne contient aucun nouveau token Sprite, aucun nouvel ASM, aucun ecrasement de Lib. **Gates B/C/D S0d non testees** ; WinUAE Runtime et capture de rendu a faire, snapshot avant essai. Aucun mecanisme d'arret DMA universel n'est encore formellement qualifie ; ne pas utiliser S0d comme preuve de securite de `FreeSprite/FreeMem` sur Amiga physique.


## 22/11/2026 — S0b Runtime PASS et S0c Sprite 16x16 experimental

[Log S0b original](evidence/M19_S0B_SPR_RUNTIME_2026-11-22.TXT) : `RESULT 1`, `ERR 0`, deux acquisitions successives du canal 1 (curseur visible puis masque), deux liberations, `OWN_REMAINING -1`, `CLOSE_RETURNED 1`. **Gate B de l'allocation OS seulement PASS**, aucun sprite actif. L'ancien ASC S0b reste dans l'historique Git. 

La nouvelle revision de [`tests/design/sprites_aga/SPRITE_PROBE.asc`](../tests/design/sprites_aga/SPRITE_PROBE.asc) est **S0c, premier Sprite 16x16 potentiellement visible** : SimpleSprite 12 octets + image 72 octets + image vide 72 octets dans une seule banque Chip Work, GetSprite/ChangeSprite/MoveSprite/FreeSprite par Gfxcall, aucun DMA ecrit en direct. Le nettoyage redirige la source vers une image transparente, attend deux VBL, rend le canal, ferme l'ecran, attend trois WaitTOF apres retour AMOS puis libere Chip. Autodocs : `FreeSprite` ne fait que marquer le canal libre ; ni l'image vide ni les attentes ne sont encore une **preuve WinUAE ou physique du detach DMA**. Le programme journalise `PASS_SEQUENCE_ONLY` et demande capture pour valider l'affichage ; aucune Gate B/C/D sur S0c. [AmigaOS Hardware Sprites](https://wiki.amigaos.net/wiki/Hardware_Sprites), [NDK SimpleSprite](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node060B.html). Ne pas promouvoir en S1/API avant verification.


## Mise a jour du 22/11/2026 — observation WinUAE S0 et probe S0b

Le journal Runtime S0 [archive tel que fourni](evidence/M19_S0_VIEWPORT_RUNTIME_2026-11-21.TXT) confirme `ViewPort.Modes=$5000` (SPRITES `$4000` present) sur les cinq echantillons Open/DB/cursor/Swap, `RESULT=1`, `ERR=0`, `CLOSE_RETURNED=1`, `PRG_STATE=1`. **Gate B du contexte ViewPort seulement PASS.** `SPRINS=0` et `UCOPINS=0` ne prouvent aucune disponibilite de canal. Aucune Gate C ou D et aucun sprite reel affiche.

Pour lever le second verrou, [un seul ASC experimental S0b](../tests/design/sprites_aga/SPRITE_PROBE.asc) utilise la fonction native AMOS `Gfxcall` pour appeler `graphics.library/GetSprite` `-408` (A0/D0) et `FreeSprite` `-414` (D0), sans ajouter de token AGA. Deux acquisitions successives suivies chacune d'une liberation : curseur visible puis masque. Le banc ne fait **ni `MoveSprite`, ni `ChangeSprite`, ni DMA de sprite** et ne prouve pas le detach DMA du futur S1. `GetSprite` modifie temporairement les canaux OS : effectuer d'abord un snapshot WinUAE. `-1` renvoye dans le WORD bas est journalise comme `65535` et signifie absence de canal libre. **S0b B/C/D restent a tester**, P2d protegee.


## Sonde AMOS S0 du ViewPort, en attente de WinUAE

**Banc source-only prêt à être exécuté :** [`examples/sprite_s0_viewport/VIEWPORT_PROBE.asc`](../examples/sprite_s0_viewport/VIEWPORT_PROBE.asc) · [notice et risques](../examples/sprite_s0_viewport/README.md). Il utilise les commandes **AMOS natives** `AREG(5)`, `LEEK`, `DEEK` et les API P2d existantes, donc **aucune nouvelle Lib ni commande Sprite**. Il vérifie `A5+$1C8`, `Screen*`, `Window.WScreen` et les dimensions, puis mesure `ViewPort.Modes` à `Screen+76` et le drapeau `SPRITES=$4000` après Open, Double Buffer, Cursor Hide/Show et Swap. Le dessin est une paire de glyphes F/L asymétriques, écran avancé par `Amos To Back`, logs `RAM:M19_S0_VP_RUNTIME.TXT` et `RAM:M19_S0_VP_COMPILED.TXT` **séparés**.

**Preuve présente :** cinq contrôles de régression statique Python PASS localement, préflight AMOS/CI à confirmer. **Aucune exécution WinUAE (B), aucune compilation AMOS (C), aucun matériel réel (D)**. Les lectures de pointeurs privés peuvent provoquer un Guru si le contrat a changé : snapshot WinUAE obligatoire avant le premier essai. `SPRITES=1` n'est **pas** une acquisition de canal, et `SPRITES=0` n'autorise **pas** à forcer un bit matériel. Si `ERR=3..7`, arrêter le test et inspecter le contrat au lieu de modifier les offsets à l'aveugle.

**Includes consultés :** [`intuition/screens.i`](https://d0.se/include/intuition/screens.i) et [`graphics/view.h`](https://d0.se/include/graphics/view.h), plus le [manuel AMOS `AREG/LEEK/DEEK`](https://amospromanual.dev/99-appendix-a-machine-code.html). Le rapport original conserve les verrous de détachement DMA et disponibilité de canaux à lever ensuite.


**État : AUDIT S0 EN COURS — modèle hôte 12/12 PASS ; aucun Sprite natif / ASC / WinUAE.**
Référence protégée : **M19 P2d**, `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` byte-identiques, **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, cible MC68020/68EC020 minimum. Les deux bibliothèques et le banc `tests/current/M19_P2_ALL_IN_ONE.asc` ne sont pas modifiés.

## 1. Architecture source examinée (autorité = sources du dépôt)

- `tools/build_m19_p2d_in_memory.py` : assemble P2d de manière déterministe à partir de P2c/P1e ; 100 commandes / 203 sections AP20. **Pas de commandes Sprite DMA**. Le binaire est une référence à préserver, pas un point de départ à désassembler pour produire du nouveau code.
- `tools/build_ntsc_pal_r10.py` et `docs/M3_SCREEN_DESIGN.md` : l'écran privé est issu d'Intuition `OpenScreenTagList`, avec tags de largeur, hauteur, profondeur et ModeID, sous le contrôle de l'OS. Les builders historiques prouvent l'intention et la provenance ; **la valeur effective du bit Sprites sur le ViewPort du P2d installé n'est pas observée**.
- `tools/m15bis_cursor_r44_emit.py` : contexte AMOS `A5+$01C8`, `Screen*` à l'offset 0 du contexte, `IntuitionBase` à +4, `GfxBase` à +8, `Window*` à +36 ; vérifie `Window.WScreen` à +46 ; pointeur transparent local à la fenêtre, tampon 72 octets Chip, `SetPointer/ClearPointer`, et hook `CloseWindow`. Ne pas réutiliser son tampon pour le nouveau Sprite.
- `tools/m19_p0c_screen_close_bridge_emit.py`, `tools/m19_p0c_screen_preclose_emit.py`, `tools/m19_p0j_swap_barrier_emit.py` : fermeture privée et `Aga Swap` à état propriétaire vérifié, avec armement/cleanup Bob/Chip ; **un nouveau Sprite doit être détaché et libéré AVANT la fermeture effective de sa fenêtre/Screen**, sans effacer les gardes Bob, et sans jamais déclencher un Swap.
- `docs/M7_COPPER_R18.md` : liste `UCopList` appartenant à `ViewPort.UCopIns`, états de Copper dans les deux bits bas de `Screen.UserData`. Aucun nouveau champ Sprite dans ces bits. **Ne pas écrire `COP1LC/COP2LC` ou changer `FMODE/BPLCON3/BPLCON4` directement** dans S1.

**Attention** : les offsets internes AMOS et les structures OS ci-dessous sont deux espaces distincts ; les données historiques doivent être confirmées par une sonde sur la Lib P2d et par les includes NDK réellement employés avant émission MC68020.

## 2. API NDK AmigaOS V39 — direction S1

Pour le **premier Sprite 16 pixels, 2 bits/pixel, non attaché**, choisir le chemin OS le plus réduit :
  
| Fonction `graphics.library` | Contrat et registres ABI documentés | Résultat attendu |
| --- | --- | --- |
| `GetSprite(SimpleSprite*, -1)` | `A0=SimpleSprite*`, `D0=-1` (premier canal libre), LVO **-408** | Canal **0..7 réellement attribué**, ou **-1**. Ne jamais inventer/sélectionner un numéro fixe |
| `MoveSprite(ViewPort*,SimpleSprite*,X,Y)` | `A0=ViewPort*`, `A1=SimpleSprite*`, `D0=X`, `D1=Y`, LVO **-426** | Position sur le ViewPort ; vérifier la convention et l'offset réel d'affichage |
| `ChangeSprite(ViewPort*,SimpleSprite*,data)` | `A0=ViewPort*`, `A1=SimpleSprite*`, `A2=data`, LVO **-420** | Changement d'image par l'OS uniquement après vérification du format/ownership |
| `FreeSprite(n)` | `D0=n`, LVO **-414** | Libérer **seulement** le canal obtenu avec succès |

Inclure les signatures/offsets exacts des versions NDK utilisées dans les tests futurs avant de coder une routine. Les API **étendues**, à étudier en S2, sont `AllocSpriteDataA`, `GetExtSpriteA`, `ChangeExtSpriteA`, `FreeSpriteData` ; ne pas mélanger les ressources `SimpleSprite` et `ExtSprite` dans le modèle S1.

La structure NDK `SimpleSprite` contient `posctldata` (LONG), `height`, `x`, `y`, `num` (WORD) : **12 octets**, hors données image. Pour un Sprite 16×16 classique, prévoir **72 octets Chip** : 2 mots de contrôle, 16×2 mots de pixels 2 bpp, 2 mots terminateurs. Pas d'index couleur 256 direct dans un Sprite : **transparent + trois couleurs visibles**, dont les registres peuvent interagir avec le Copper/les bitplanes. Le bitmap source peut exister en Fast, mais **le tampon réellement référencé par DMA doit être en Chip**.

Les offsets `struct Screen` (ViewPort embarqué à **+44**) et `struct ViewPort` (`Modes` à **+32**) indiquent une **sonde candidate `Screen*+76`** pour `ViewPort.Modes`. Le mode `V_SPRITES=$4000` est une constante NDK à recouper ; **ce calcul d'offset n'est PAS encore une mesure sur la P2d sous WinUAE**, et ne justifie pas d'écriture dans ces structures. Utiliser les includes réels `intuition/screens.i`, `graphics/view.i`, `graphics/sprite.h` et les Autodocs V39 au jalon natif.

Sources NDK/AmigaOS : https://developer.amigaos3.net/autodocs/graphics.library/ ; https://d0.se/include/graphics/sprite.h ; https://d0.se/include/graphics/view.h ; https://wiki.amigaos.net/wiki/Hardware_Sprites .

## 3. Modèle de propriété host-only exécuté

- Source : [`tools/aga_sprite_s0_model.py`](../tools/aga_sprite_s0_model.py).
- Tests : [`tools/test_aga_sprite_s0_model.py`](../tools/test_aga_sprite_s0_model.py).
- CI dédiée : [`.github/workflows/aga-sprite-s0-host.yml`](../.github/workflows/aga-sprite-s0-host.yml) ; **12 tests hôtes PASS localement**, confirmation CI indépendante à relever.
- Phases : `EMPTY → DATA_READY → CHANNEL_OWNED → VISIBLE → DMA_DETACHED → RELEASED`, avec les raccourcis d'échec `DATA_READY → RELEASED` si aucun canal.
- La mémoire image est affectée à **un seul écran privé et ViewPort**, et le numéro de canal est **strictement celui renvoyé par `GetSprite(-1)`**. Un retour `-1` n'autorise jamais `FreeSprite`. Le canal 0 **n'est ni choisi par défaut ni interdit arbitrairement** : seul l'OS peut l'accorder, si disponible.
- Un nettoyage bloqué tant que DMA est susceptible de référencer l'image. Les obligations sont ordonnées : **détacher le Sprite / prouver l'arrêt de la référence DMA → `FreeSprite` du canal possédé → `FreeMem` de l'image Chip → fermeture écran**.
- `confirm_dma_detached()` est uniquement **une attestation passée par un futur adaptateur externe**. Le modèle n'appelle aucun LVO et **ne démontre pas que le DMA est réellement arrêté**. Il ne valide ni un simple VBL, ni un `Aga Swap`, ni un `ChangeSprite(NULL)` non documenté. L'adaptateur OS réel devra lever ce verrou.
- Les tests couvrent allocation normale, mouvement, canal saturé, plage 0..7, propriétaire incorrect, double acquisition, OOM, refus de release si DMA référencé, libération idempotente et réouverture avec propriétaire neuf. Ils ne testent **aucun pixel** et n'impliquent **aucune interruption, Copper, AMAL ou Bob**.

**Exécution du modèle** : `PYTHONPATH=tools python -B -m unittest discover -s tools -p 'test_aga_sprite_s0_model.py' -v`.

## 4. Verrous encore ouverts — avant S1 natif

1. **Sonde WinUAE de l'écran AGA réel** : `Screen*`, `ViewPort*`, `Modes`, état Sprite autorisé, conflits avec le pointeur Intuition et canaux réellement libres. La sonde doit lire, sans réécrire `Screen.ViewPort` ou `UserData`.
2. **Propriété et DMA** : obtenir un protocole démontrable de mise hors DMA/attente/FreeSprite/FreeMem conforme aux Autodocs et au comportement Intuition, sur fermeture normale, erreurs, Ctrl+C et réouverture ; les 12 tests hôtes ne couvrent pas le matériel.
3. **Palette et priorité** : distinguer les palettes 2bpp Sprite des 8 bitplanes à 256 couleurs ; mesurer les interactions avec `COLOR16..31`, Copper et pointeur. Ne modifier aucun registre AGA dans S1 sans preuve.
4. **ABI/offsets réels de P2d** : tracer la bonne adresse `Screen*` jusqu'au ViewPort sans écriture intrusive, valider 68020 et les phases de teardown par source autoritative/NDK ; aucun patch de HUNK désassemblé.
5. **S1 minimal seulement après clôture S0** : un Sprite matériel 16×16, mouvement, off/close, échecs canal/OOM, présence du pointeur, Bobs en arrière-plan et Copper On/Off. Essais **Gate A CPU native** puis **B WinUAE Runtime**, **C vrai Compiler**, **D matériel** indépendants.

## 5. Décision de périmètre

S0 reste **ouvert**. Aucune API publique `Aga Sprite`, aucun nouveau fichier `.asc` actif, aucune nouvelle Lib candidate, aucun binaire réassemblé, aucune promotion ou release. Prochaine intervention utile : **sonde native en lecture seule de l'état `Screen/ViewPort`**, puis choix du contrat de détachement DMA ; ne pas déplacer le socle P2d `LAST_GOOD` avant autorisation.
