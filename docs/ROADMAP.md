# Roadmap — AMOS Professional 365 / Extension AGA

## M15bis/R44 v0.11.5 — Aga Mouse Cursor : Gates A/B PASS (démo combinée en attente) (12/11/2026)

**API approuvée et développée :** `_OK=Aga Mouse Cursor(Visible)` ; `0` masque le pointeur **uniquement dans la fenêtre Intuition de l'écran AGA privé**, `1` rétablit le curseur système pour cette fenêtre. Valeurs autres que 0/1, écran/fenêtre invalide ou allocation refusée retournent `0` sans effet. `1` signifie état de pointeur appliqué (idempotence). Mouse X/Y, boutons et clavier restent actifs.

**Gestion locale et mémoire :** sprite transparent 16×16 à deux plans, **72 octets Chip RAM `MEMF_CHIP|MEMF_CLEAR`**, une seule allocation paresseuse par fenêtre au premier masquage. `ClearPointer` avant `CloseWindow`, puis `FreeMem` 72 octets après fermeture ; état privé réinitialisé. Quatre sites de fermeture **0/8/17/18** interceptés par BSR.w vers le cleanup R44 ; la fermeture de la fenêtre auxiliaire de `Aga Palette Save` (segment 40) est strictement conservée. Les offsets de l'état partagé 40 octets ne changent pas.

**Gate A CPU 68000 et CI complète PASS :** **516 scénarios CPU** dont 500 cycles masqué/visible avec une allocation unique, mémoire, OOM, ABI A3, Win/Screen, quatre hooks de fermeture, ordre `ClearPointer→CloseWindow→FreeMem`, HUNK/AP20, export source natif strict. [CI Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43208679398). **49 commandes AP20 / 55 segments.** Candidat binaire R44 déterministe SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`, **27 460 octets**.

**Candidate publiée :** `dist/AMOSPro_AGA.Lib` = `dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib` à l'octet près. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` demeure R43 v0.11.4**, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf`, Gates A/B PASS ; archives antérieures intactes.

**Gate B R44 PASS confirmée par utilisateur ;** unique test actif `tests/current/M15BIS_R44_MOUSE_CURSOR_01.asc` à importer via **Project → Merge ASCII** dans AMOS interprété/WinUAE. Observer visible→masqué→visible→masqué→fermeture, tester le retour Workbench, lire `SWITCHES 500 ERR 0`, `RESULT 1` et `CLOSE RETURNED` ; examiner `CHIP DROP` et `CHIP WARN` sans les présenter comme preuve complète d'absence de fuite. **Ne pas promouvoir `LAST_GOOD` avant confirmation utilisateur explicite.** Gates C Compiler / D Amiga AGA physique NON TESTÉES. [Contrat M15bis](M15BIS_MOUSE_CURSOR_R44_DESIGN.md), branche **`main` uniquement**.


**Retour WinUAE R44 du 12/11/2026 : Gate B PASS confirmée par l'utilisateur (« ça marche super »).** Capture : `SHOW 1 1 1 ; HIDE 1 1 ; BAD 0 0 ; NOSCREEN 0 ; SWITCHES 500 ERR 0 ; CHIP FREE 1631384 / 1631384 DROP 0 ; BIG FREE 1630656 / 1630656 DROP 0 ; CHIP BEFORE/END 1801928 / 1801928 ; CHIP WARN 0 ; CLOSED -1 ; RESULT 1 ; CLOSE RETURNED`. Le rendu du curseur visible/masqué et le retour AMOS sont confirmés ; aucune fuite Chip mesurée pendant ce test (ne prouve pas tous les chemins Ctrl+C). **R44 reste candidate ; ne pas promouvoir `LAST_GOOD` ni clôturer M15/M15bis avant l'essai de la [démo combinée](../examples/m15_2d_cursor.asc).** Gates C/D non testées.

## M15/R43 v0.11.4 — Aga Circle : Gates A CPU/CI et B AMOS/WinUAE PASS, LAST_GOOD (12/11/2026)

**R43 VALIDÉE par l'utilisateur (capture « parfait !!! ») :** `_OK=Aga Circle(CX,CY,Radius,Pen)` — cercle de contour d'un pixel par Bresenham midpoint 68000 en arithmétique 32 bits avec clipping sécurisé des huit octants, sans dessin hors écran ni bord inventé. Écran AGA privé, uniquement sur le back buffer après `Safe` non bloquant ; aucune allocation persistante, aucun swap/VBL implicite. **48 commandes AP20, 54 segments ; 436 scénarios CPU 68000 Gate A PASS et CI complète PASS** ([CI candidate](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43204551950)).

**Gate B AMOS interprété/WinUAE PASS :** l'utilisateur confirme le rendu et la capture affiche `OPEN 1 DB 1 CLEAR 1`, `CIRCLES 1 1 1 1 DOT 1`, `CORNERS 1 1 1 1`, `CLIPPED 1 1 1 1`, `PEN0 1 OUTSIDE 0 0 0 0`, `WRAP 0 BADR 0 0`, `BADXY 0 0 BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`** et **`CLOSE RETURNED`**. [Test d'origine archivé sans modification](../tests/passed/M15_R43_CIRCLE_01.asc), Git blob `088158365a64accf0417fdda3fbba74e2e58ebf7` (**3 466 octets**) ; aucun fichier ASC dans `tests/current/`.

**Promotion obligatoire réalisée :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib`, **27 092 octets**, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf`, à l'octet près. **R42** reste dans son archive versionnée intacte (25 896 octets, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`) ; toutes les versions précédentes conservées. **Gates C Compiler et D AGA physique NON TESTÉES.** M15 primitives de base (Plot/Draw/Box/Circle) terminé sur les Gates A/B. **Suite à discuter : M15bis, visibilité locale du pointeur souris AGA, avant M16 (images compressées Fast RAM)**. R39 fontes bitmap toujours reportée ; aucun nouveau contrat de commande validé pour M15bis/M16. Dépôt `anthea176/AMOSPro-AGA-Extension`, **`main` uniquement**.

## M15/R42 v0.11.3 — Aga Box : Gates A CPU/CI et B WinUAE PASS, LAST_GOOD (12/11/2026)

**R42 VALIDÉE :** `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, **47 commandes AP20**, **360 tests CPU 68000 + export source natif strict + CI PASS**, Gate B AMOS interprété/WinUAE **PASS confirmé par l'utilisateur** (« ça marche ! bravo »). Capture : `OPEN 1 DB 1 CLEAR 1`, `BOXES 1 1 1 REV 1`, `CLIPPED 1 1 1 1`, `LINES 1 1 DOT 1`, `OUTSIDE 0 0 0 0`, `WRAP 0 BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne **119** ; rendu validé. [Test original archivé sans retouche](../tests/passed/M15_R42_BOX_01.asc), Git blob `dbf5cefb215cc0ae1359d648ea34c855a92b2012` (**3 264 octets**). **`tests/current/` ne contient aucun ASC actif.**

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib` **octet pour octet**, **25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`. L'archive R41 v0.11.2 (SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`), R40, R38 et les précédentes sont inchangées. Contour d'un pixel, coins inclusifs et inversables, clipping des **quatre côtés originaux** sans fausse bordure, sécurité du back buffer `Safe` et refus des paramètres invalides. **Gates C Compiler et D Amiga AGA physique NON TESTÉES.** Prochain chantier éventuel : M15/R43 `Aga Circle` (NON implémenté). R39 fontes bitmap reste reportée. **La proposition M16 de banque d'images compressées en Fast RAM reste une idée de roadmap, pas une fonction livrée.** Dépôt `anthea176/AMOSPro-AGA-Extension`, **`main` uniquement**.

## Historique de préparation avant validation R42

**M15/R42 v0.11.3 — CANDIDATE PUBLIÉE, Gate A CPU/CI PASS (360 scénarios), Gate B WinUAE NON TESTÉE (12/11/2026).** `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, **47 commandes AP20**. Coins inclusifs normalisés, 1 px d'épaisseur, clipping indépendant des quatre côtés d'origine (jamais de bordure inventée), refus sécurisé des rectangles hors écran, validation des coordonnées signed16 et index `Pen`, BitMap physique et signal `Safe` non bloquant. [Test unique WinUAE](../tests/current/M15_R42_BOX_01.asc) à importer via **Project → Merge ASCII**. `dist/AMOSPro_AGA.Lib` et `dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib` identiques (**25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`). **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la R41 v0.11.2 validée** (24 816 octets, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`) ; archives R41 et antérieures inchangées. [CI CPU + source strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43198823212). Gates C Compiler/D AGA physique non testées. Aucun test R42 archivé ou `LAST_GOOD` promu sans validation utilisateur. Travail uniquement sur `main` de `anthea176/AMOSPro-AGA-Extension`.

**M15/R42 — Aga Box autorisée (12/11/2026) :** contrat `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, contour 1 pixel aux coins inclusifs, inversion automatique des coins et **clipping indépendant des quatre côtés d'origine** (pas de fausse bordure si le rectangle englobe l'écran). Vérifier les coordonnées signed16 et le Pen indexé ; seulement le back buffer AGA, `Safe` non bloquant, RastPort temporaire, Move/Draw uniquement après bornage, WritePixel pour segments réduits à un point. Source `tools/m15_box_r42_emit.py`, builder `tools/build_m15_box_r42.py`, test CPU `tools/test_m15_box_r42.py`. [Contrat détaillé](M15_BOX_R42.md). **R42 en cours : Gate A CPU/CI en attente, Gate B WinUAE NON TESTÉE ; pas encore de candidate publiée.** R41 v0.11.2 reste `LAST_GOOD` (46 commandes AP20, 24 816 octets, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`, Gates A/B PASS). Aucune nouvelle branche ; R39 reportée, R43 non engagée.

## M15/R41 v0.11.2 — Gates A CPU/CI et B WinUAE PASS, LAST_GOOD (12/11/2026)

**R41 `Aga Draw(X1,Y1,X2,Y2,Pen)` VALIDÉE** : 46 commandes AP20, **325 tests CPU 68000 + export assembleur strict + CI PASS**, puis test AMOS interprété/WinUAE confirmé par l'utilisateur (« rendu ok ! »). Capture : `OPEN 1 DB 1 CLEAR 1`, `BORDER 1 1 1 1`, `CLIPPED 1 1 1 1`, `STAR 8 ERR 0 CENTER 1`, `OUTSIDE 0 0 0 0`, `BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne **131**. [Test exact archivé](../tests/passed/M15_R41_DRAW_01.asc) (Git blob `aa7de64b37a2842db21bc7452c2fab4570413e9f`, 3 553 octets). `tests/current/` ne contient aucun ASC actif.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib` **octet pour octet**, **24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`. Archive R40 v0.11.1 préservée (SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`), ainsi que R38 et les archives antérieures. Dessin strictement sur le back buffer AGA : tracé rapide `Move/Draw` uniquement si extrémités valides ; clipping logiciel avec contrôle **avant chaque pixel** hors limites. **Gates C AMOS Compiler et D Amiga AGA réel NON TESTÉES.** R39 fontes bitmap reportée ; R42 `Aga Box` et R43 `Aga Circle` non implémentées. Dépôt `anthea176/AMOSPro-AGA-Extension`, branche **`main` uniquement**.

## Historique (avant promotion R41)

**M15/R41 v0.11.2 — CANDIDATE PUBLIÉE, Gate A CPU/CI PASS (325 scénarios), Gate B WinUAE NON TESTÉE (12/11/2026).** `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)`, **46 commandes AP20** ; tracé rapide pour lignes intégralement à l'écran et Bresenham avec vérification de chaque pixel avant `WritePixel` pour les segments qui dépassent. [Test unique WinUAE](../tests/current/M15_R41_DRAW_01.asc), import par **Project → Merge ASCII**. `dist/AMOSPro_AGA.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib` à l'octet près (**24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`). **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la R40 v0.11.1 validée** (23 840 octets, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`), archives R40/R38 et plus anciennes inchangées. [CI CPU 68000 + source strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43193933457). Gates C Compiler/D Amiga réel non testées. Ne promouvoir R41 et n'archiver le test qu'après validation explicite de l'utilisateur. **Uniquement `main` du dépôt `anthea176/AMOSPro-AGA-Extension`.**

**M15/R41 — Aga Draw autorisée le 12/11/2026 :** implémentation de `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)` (nouvelle commande AP20 index 51, **46 commandes prévues**), en deux voies : `graphics.library/Move/Draw` seulement avec extrémités strictement dans le back buffer, **Bresenham logiciel avec contrôle avant chaque pixel** dès qu'une extrémité est extérieure. Paramètres 32 bits AMOS vérifiés dans l'intervalle signé 16 bits pour éviter toute troncature ; segments entièrement hors écran retournent 0. Garde `Safe` non bloquante, validation bitplanes et index couleur. [Contrat R41](M15_DRAW_R41.md) ; émetteur `tools/m15_draw_r41_emit.py`, builder `tools/build_m15_draw_r41.py`, test CPU `tools/test_m15_draw_r41.py`. **Gate A CPU/CI en attente ; Gate B WinUAE NON TESTÉE.** R40 v0.11.1 **LAST_GOOD** SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231` strictement inchangée. La candidate R41 est maintenant publiée (Gate A PASS). R39 rejetée ; R42/43 non engagées. Branche `main` uniquement.

## M15/R40 v0.11.1 — Aga Plot : Gates A CPU/CI + B WinUAE PASS, LAST_GOOD (12/11/2026)

**R40 VALIDÉE sous AMOS interprété / WinUAE :** `_OK=Aga Plot(X,Y,Pen)`, **45 commandes AP20**. 221 scénarios CPU 68000 + export strict et [CI candidate](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43129055588) PASS. Confirmation utilisateur le 12/11/2026 (« ça marche nickel ») avec capture `OPEN 1 DB 1 CLEAR 1`, `PALETTE 1 1 1 1`, `CORNERS 1 1 1 1`, `CENTER 1 PEN0 1`, `DIAG 192 ERR 0`, `BADXY 0 0 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne 99. [Test original archivé octet pour octet](../tests/passed/M15_R40_PLOT_01.asc) (Git blob `6ab9cf4a91cca9f8097ffba40a32e2b85b049c38`). `tests/current/` sans ASC actif.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib` à l'octet près (**23 840 octets**, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`). L'archive R38 v0.11.0 et toutes les versions antérieures restent inchangées. **Gate A CPU/CI PASS, Gate B WinUAE PASS, Gates C Compiler/D Amiga physique NON TESTÉES.** Protection intégrée : refus des coordonnées X/Y hors de `[0,Width-1]`/`[0,Height-1]` et des pen hors de `0..2^Depth-1` avant tout dessin, vérification des bitplanes et du back buffer `Safe`. `Aga Draw`, `Aga Box`, `Aga Circle` non implémentées ; les protections de `Plot` ne constituent pas un clipping général. R39 fontes bitmap 8x8 est reportée. Dépôt unique `anthea176/AMOSPro-AGA-Extension`, **branche `main` uniquement**.

**Décision M15 (12/11/2026) :** l'utilisateur demande de **sauter R39** (fontes `Change Print Font` 8×8) et de passer directement au **dessin 2D AGA M15**. Ordre de travail proposé : **R40 `Aga Plot`**, puis `Aga Draw`, `Aga Box`, `Aga Circle`, un seul appel public par sous-jalon. Le contrat et l'audit sont dans [`docs/M15_DRAWING_2D_DESIGN.md`](M15_DRAWING_2D_DESIGN.md). **Historique de la phase d'étude, depuis dépassée : R40 Plot a ensuite été approuvée, codée et a passé Gate A CPU/CI.** R38 v0.11.0 était alors `LAST_GOOD` ; R40 a depuis été validée A/B et promue, Gates C/D non testées. Travail exclusivement sur `main` du dépôt courant.

## R38 0.11.0 — Aga Font Bank Select : Gates A/B PASS, ancienne LAST_GOOD archivée (12/11/2026)

**Gate B confirmée par l'utilisateur** (« ca a marché ! »), sous AMOS interprété/WinUAE avec la candidate corrigée après les refus BANK 0 / BANK2 0. La fonction `Aga Font Bank Select(Start(bank),Length(bank))` prend en charge les banques AMCAF `BankFont` monochromes fixes et proportionnelles, DATA/WORK, source CHIP/FAST. Le rendu s'effectue sur une copie privée allouée en **Chip RAM**, et les anciennes fontes sont libérées par `StripFont` puis `FreeVec` au remplacement/reset/fermeture. **Contrôle complémentaire WinUAE du 12/11/2026 : 500 changements de fontes et 500 appels à `Aga Text`, sans baisse de la Chip RAM libre ni du plus grand bloc libre** (voir le test d'endurance archivé). Ce résultat ne démontre pas l'absence de fuite dans tous les scénarios. La Gate A a validé **60 groupes CPU 68000**, banques réelles Topaz/Hwarf/Pix3M et régressions R37/R26/R36 ; CI intégrité candidate PASS. **44 commandes AP20**.

**Promotion R38 :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib` à l'octet près (**23 380 octets**, SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`). L'ancienne R38 rejetée est archivée sous `dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38_FAILED_BANK0.Lib` ; R37 v0.10.9 reste archivée, non modifiée. Test original déplacé sans modification de `tests/current/M14_R38_FONT_BANK_01.asc` vers `tests/passed/M14_R38_FONT_BANK_01.asc`, Git blob `4d847f86bfffc9d0d062c75e6bdda97a13b623bf`. `tests/current/` sans ASC actif. Gates C Compiler et D Amiga réel **NON TESTÉES**. R39 a été écartée ; le développement 2D M15 a démarré avec R40 Plot, ensuite validée A/B. Dépôt et branche autorisés : `anthea176/AMOSPro-AGA-Extension` / `main` seulement.

[Stress Chip RAM WinUAE PASS — test archivé](../tests/passed/M14_R38_CHIP_RAM_STRESS_01.asc) · [Contrat R38](M14_FONT_BANK_R38.md) · [Gate A CPU](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43123200900) · [CI intégrité candidate](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43123419858).

---

## R37 0.10.9 — Aga Font Select : Gates A CPU/CI et B AMOS/WinUAE PASS (11/11/2026)

**Commande approuvée et implémentée :** `_OK=Aga Font Select(FontName$,YSize)`, sélection d'une fonte AmigaOS via `OpenDiskFont` (taille demandée 1..255, nom de 1..127 octets) ; `Aga Font Select("",0)` rétablit la fonte système. `Aga Text` applique `SetFont` avant `TextExtent` sur son RastPort AGA privé. Fonte libérée au remplacement, au reset et à `Aga Screen Close`. Les fontes des banques AMCAF ne sont **pas encore prises en charge**. [Contrat R37](M14_FONT_SELECT_R37.md).

**Gate A CPU/CI PASS :** 20 groupes de tests natifs 68000 R37, régressions R26 (64 cas) et R36 (106 scénarios), export assembleur strict PASS. [CI R37](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43075769541) PASS, **43 commandes AP20**.

**Gate B AMOS interprété/WinUAE PASS :** capture de l'utilisateur sur le test [`M14_R37_FONT_SELECT_01.asc`](../tests/passed/M14_R37_FONT_SELECT_01.asc), Git blob original **`5371c310142f33aa2312e59ed81e2e2d6b90da3d`** conservé octet pour octet. `OPEN 1 DB 1 PALETTE 1 1`, `SEL8 1 TX8 1 SEL9 1 TX9 1`, `BAD0 0 BAD256 0 BADNAME 0`, `KEEP 1 RESET 1 DEFAULT 1`, `SWAP 1 NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`** ; rendu visuel et retour AMOS normal confirmés (« fonctionnement nickel »). Aucune métrique de vitesse mesurée.

**R37 promue `LAST_GOOD` :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M14_v0.10.9_FONT_SELECT_R37.Lib`, **22 328 octets**, SHA256 `bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a`. La version antérieure R36 v0.10.8 reste archivée sans changement, **21 836 octets**, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`. **Aucun test actif dans `tests/current/`.** Gates C Compiler et D Amiga réel **NON TESTÉES**.

**Suite M14, sans autorisation de codage :** examiner et contractualiser individuellement R38 (banques de fontes AMCAF `Make Bank Font`), puis R39 (fontes bitmap 8×8 de `Change Print Font`). Aucune fonction nouvelle sans accord explicite ; travailler uniquement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, aucune autre branche ni dépôt.

**Les sections R36 et antérieures ci-dessous sont des checkpoints historiques : leurs références aux binaires et `LAST_GOOD` décrivent leur époque, pas l'état de R37.**

---

## R36 0.10.8 — Aga Palette Cycle : Gates A CPU/CI et B AMOS/WinUAE PASS (11/11/2026)

**Une seule commande approuvée :** `_OK=Aga Palette Cycle(First,Last,Direction)`, une rotation RGB32 complète par appel (+1 : dernière couleur vers premier index, -1 : inverse), indices inclus `0<=First<Last<256` dans les pens logiques/ColorMap de l'écran AGA Intuition privé indexé. Un `GetRGB32`, permutation exacte des triplets 32 bits, un `LoadRGB32` sur la plage seulement, **aucun `WaitTOF` implicite** ; aucun pixel, banque, fichier ou couleur hors plage touché. Scratch Exec public `8+12*N` (max 3 080 octets) libéré. Succès 1, invalides/refus atomiques 0 ; AMOS pilote la cadence. [Contrat technique R36](M13_PALETTE_CYCLE_R36.md).

**Gate A CPU/CI PASS :** **106 scénarios natifs CPU 68000 PASS**, export source 68000 strict PASS, [CI candidate complète 38/38 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43064975345), **42 commandes AP20**.

**Gate B interprété AMOS/WinUAE PASS — capture utilisateur :** quatre bandes affichées avant 20 rotations à huit VBL d'intervalle. `OPEN 1 DB 1 DRAW 1 1 1 1`, `CYC20 1 RESTORED 16711680 16776960`, `FWD 1 COLOR 16776960 16711680 65280 255`, `REV 1 RESTORE 16711680 16776960`, `NEG 1 COLOR 65280 16711680 POS 1`, `RESET 16711680 16776960`, `BADFIRST 0 BADEQ 0 BADORDER 0`, `BADLAST 0 DIR0 0 DIR2 0 DIRN 0`, `AFTERBAD 16711680 NOSCREEN 0`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin AMOS normale **ligne 138**. Confirmation utilisateur « fct nickel ! », sans mesure FPS ni durée réelle.

**R36 promue `LAST_GOOD` à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib`, **21 836 octets**, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`. Archive **R35 0.10.7 préservée intacte**, 21 300 octets, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`. [Test R36 original archivé](../tests/passed/M13_R36_PALETTE_CYCLE_01.asc), Git blob `4644236576033f755ac0dc274f6f22f92a2d9201` conservé **sans modification**. **Aucun ASC actif dans `tests/current/`.** Gates C Compiler et D Amiga AGA réel **NON TESTÉES**.

**Suite :** R36 clôturée côté AMOS interprété/WinUAE. Aucun R37 ou autre fonction sans discussion et accord explicite de l'utilisateur. Travailler uniquement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, sans autre branche ni dépôt.

---

## R35 0.10.7 — Aga Fade To White : Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Contrat approuvé — seule fonction ajoutée :** `_OK=Aga Fade To White(vbl)`, durée entière 1..255 VBL (0/négatifs/>255 refusés sans modification), fondu RGB24 bloquant de tous les pens logiques de l'écran AGA Intuition privé indexé vers le **blanc exact**. Une capture source `GetRGB32` si vbl>1, interpolation signée 8.8 et un `graphics.library/WaitTOF` suivi de `LoadRGB32` par VBL, dernière image RGB32 `0xFFFFFFFF` exacte. Pas de banque AGAPAL, pixel ou fichier touché ; HAM/EHB/dual playfield rejetés, ColorMap contrôlée, tampon Exec `8+42*N` octets (max 10 760) libéré. Pas de mesure FPS ni de garantie de temps écoulé en cadence réelle. [Contrat technique R35](M13_FADE_WHITE_R35.md).

**Gate A CPU/CI PASS :** 50 scénarios natifs 68000 et export source strict PASS, [CI candidate complète 37/37 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43057572164), 41 commandes AP20.

**Gate B PASS — capture utilisateur AMOS interprété/WinUAE :** `OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 WHITE 16777215 16777215`, `WHITE2 16777215 16777215`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 16777215`, `FADE2 1 TWO 16777215`, `SAME 1 SAME28 16777215`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. L'utilisateur a confirmé « c nickel » après le fondu visible de 150 VBL, sans mesure de cadence/FPS.

**R35 promue `LAST_GOOD` à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib`, **21 300 octets**, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`. **R34 0.10.6 est préservée dans son archive** (20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`). [Test R35 exact archivé](../tests/passed/M13_R35_FADE_TO_WHITE_01.asc), Git blob `21115dfbbcff345e6ae8132c03956152b897a6b2` inchangé. **`tests/current/` sans aucun ASC actif.** Gates C Compiler/D Amiga AGA réel NON TESTÉES.

**Suite :** R35 clôturée côté WinUAE. Ne pas implémenter d'autre commande (R36 ou autre) sans discussion et accord explicite. Rester strictement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, aucune autre branche ni dépôt.

---

## R34 0.10.6 — Aga Fade To Black : Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Contrat approuvé et unique fonction ajoutée :** `_OK=Aga Fade To Black(vbl)`, durée entière 1..255 VBL (0, négatifs et >255 refusés). Fondu RGB24 **bloquant** de tous les pens logiques de l'écran AGA Intuition privé indexé vers le **noir exact**, un `graphics.library/WaitTOF` et `LoadRGB32` par étape, interpolation signée 8.8 depuis la capture `GetRGB32` ; dernière étape RGB32 nulle sans erreur d'arrondi. Aucune banque AGAPAL nécessaire, aucune écriture pixels, banques ou fichiers. Scratch Exec `8+42*N` octets (max 10 760) libéré. Refus sans effet ; retour 1 succès, 0 échec. Pas de mesure FPS ni garantie de durée réelle exacte sur 68000. [Contrat technique R34](M13_FADE_BLACK_R34.md).

**Gate A PASS :** 48 scénarios CPU natifs 68000 et export source strict PASS, [CI de publication complète 36/36 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43053552010), 40 commandes AP20.

**Gate B PASS — capture utilisateur WinUAE/AMOS interprété :** `OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 BLACK 0 0 0 0`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 0 FADE2 1 TWO 0`, `SAME 1 SAME28 0`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 113**. L'utilisateur confirme « nickel » sur la démonstration visuelle du fondu 150 VBL ; cadence/FPS non mesurés.

**Promotion R34 à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib`, **20 752 octets**, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`. R33 0.10.5 reste figée dans son archive (20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`). Le [test exact R34 archivé](../tests/passed/M13_R34_FADE_TO_BLACK_01.asc) est conservé **sans modification** (blob Git `5fe2f819048cd3706eedaf363f3415a00270406a`). **Aucun ASC actif dans `tests/current/`**. Gates C Compiler/D Amiga AGA réel **NON TESTÉES**.

**Suite :** aucune nouvelle fonction implémentée ; discuter et approuver un nouveau contrat (par exemple Fade To White) **avant** tout codage. Rester exclusivement sur `main`, pas d'autre branche ni de dépôt sans demande explicite.

---
## R33 0.10.5 VALIDÉE — Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Nouvelle fonction :** `_OK=Aga Fade To Bank(Start(bank),index,vbl)`. Fondu RGB24 **bloquant** sur 1..255 VBL ; `WaitTOF` puis `LoadRGB32` par image, interpolation 8.8 signée, **dernière image RGB24 exacte**. Uniquement les pens 0..compte-1 sont modifiés ; banques/pixels et pens supérieurs restent inchangés. `vbl=0` refusé ; pour une application immédiate utiliser `Aga Palette Bank Apply`. Requiert une banque DATA AGAPAL **vivante** (`Start(bank)` réel), une palette non vide et un écran AGA indexé privé. Scratch Exec temporaire `8+42*N` (10 760 octets max), libéré. Les VBL ne garantissent pas une durée réelle stricte si le calcul dépasse une trame.

**Gate A :** 51 scénarios CPU natifs 68000 PASS, export source 68000 strict PASS, **[CI de publication 35/35 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43045308067)**, 39 commandes AP20.

**Gate B fonctionnelle PASS — capture utilisateur WinUAE/AMOS interprété :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `FADE0 1 GREEN 65280`, `FADE1 1 BLUE 255 SAME 1 255`, `PART 1 PEN3 660510 PEN28 16711680`, `BAD0 0 BAD256 0 BADNEG 0`, `BADINDEX 0 EMPTY 0 BADSIZE 0`, `AFTERBAD 16711680 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 BLUE 255`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 141**. Le test confirmait les couleurs finales et les rejets, **pas la qualité visuelle ni la fluidité du fondu** : son `Aga Swap` et `Amos To Back` étaient exécutés APRÈS les transitions, et celles-ci duraient surtout 12/1/2 VBL. **Démo distincte** [`examples/fade_to_bank_r33.asc`](../examples/fade_to_bank_r33.asc) : affiche d'abord trois grandes bandes, puis rouge → vert → bleu → rouge en 150 VBL avec des pauses. Démo **validée visuellement sous WinUAE par l'utilisateur le 11/11/2026 : fondu visible et fonctionnel**, sans mesure de cadence, FPS ou durée réelle.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R33 `dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib`, **20 208 octets**, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`, strictement identiques. R32 préservée intacte en archive (19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`). ASC fonctionnel archivé à l'octet près : [`tests/passed/M13_R33_AGAPAL_FADE_01.asc`](../tests/passed/M13_R33_AGAPAL_FADE_01.asc). Aucun ASC actif dans `tests/current/`. Gates C (Compiler) et D (Amiga AGA physique) **NON TESTÉES**.

**Suite :** observation visuelle positive enregistrée ; ne pas prétendre à une mesure de fluidité, FPS ou cadence sans instrumentation. Toute prochaine fonction doit être discutée et approuvée avant le codage ; mettre à jour les deux README et rester strictement sur `main`, sans autre branche/dépôt.

---
## R32 0.10.4 VALIDÉE — Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Fonction ajoutée seule :** `_OK=Aga Palette Bank Apply(Start(bank),index)` applique une palette RGB24 AGAPAL non vide (1..256 couleurs) à l'écran AGA privé par `graphics.library/LoadRGB32`, immédiatement sans VBL implicite. Retour entier 1/0, aucun changement des banques/pixels, seuls les pens 0..compte-1 remplacés. Exiger un vrai `Start(bank)` d'une banque DATA vivante, jamais un numéro brut ou une adresse périmée.

**Gate A :** 136 scénarios CPU 68000 PASS, export source 68000 strict PASS, [CI candidate 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040), [CI documentaire 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032630960).

**Gate B PASS — capture utilisateur de `M13_R32_AGAPAL_APPLY_01.asc` :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `AP0 1 AP1 1 PART 1`, `GREEN 65280 RED 16711680 BLUE 255`, `PEN224 795192 PART3 660510 PART28 255`, `BADNEG 0 BAD8 0 EMPTY 0`, `BADSIZE 0 BADCOUNT 0`, `AFTERBAD 255 AFTERCOUNT 255`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 16711680 PART 1`, `REST3 660510 REST28 16711680`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, et fin propre `End of program at line 161`. PASS limité à ce scénario AMOS interprété/WinUAE ; Compiler et vrai Amiga AGA non testés.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib`, **19 244 octets**, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894` (octet pour octet). R31 0.10.3 est préservée en archive versionnée (18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`). ASC validé archivé **sans modification** dans [`tests/passed/M13_R32_AGAPAL_APPLY_01.asc`](../tests/passed/M13_R32_AGAPAL_APPLY_01.asc). **Aucun ASC actif** dans `tests/current/`. Gates C Compiler/D matériel réel **NON TESTÉES**.

**Suite :** aucune fonction Import/Fade/Cycling sans échange et accord explicite sur son contrat ; travailler seulement sur `main`, aucun autre dépôt ni branche.

---


## R31 0.10.3 VALIDÉE — AGAPAL Capture, Gate A CPU + Gate B AMOS/WinUAE PASS (11/11/2026)

**Preuve Gate B utilisateur :** capture de l'exécution du test `M13_R31_AGAPAL_CAPTURE_01.asc` sous AMOS interprété/WinUAE : `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED` et fin AMOS normale ligne 141. **PASS uniquement pour ce scénario interprété/WinUAE ; Gates C Compiler et D matériel Amiga réel NON TESTÉES.**

**Fichier ABK réellement inspecté (fourni par l'utilisateur) :** `R31_AGAPAL_CAPTURE.ABK`, **6 244 octets au total**, en-tête externe natif `AmBk` (bank 10, flags DATA 1), corps interne `AGAPAL` v1 **6 224 octets**, huit emplacements. Indices 0 et 1 : 256 couleurs RGB24 chacun ; pen 28 = `0000FF` dans la palette 0 et `FF0000` dans la palette 1. Indices 2 à 7 : descripteurs à zéro et RGB24 tous à zéro. Pens 3 et 224 conservés ; intégrité des offsets et signatures vérifiée. SHA256 du fichier ABK fourni : `7a3162969b0d700287ae0852872811dae072c19720a794beb8818d01b93f6cd9`. Ce contrôle de fichier corrobore l'essai WinUAE mais ne constitue pas une validation du Compiler.

**Promotion obligatoire effectuée :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib`, **R31 0.10.3**, **18 520 octets**, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`, strictement identiques. R30 0.10.2 reste **intacte dans son archive figée** (17 824 octets, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`). Test `.asc` validé archivé **octet pour octet** : `../tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc` (Git blob `0196fc1ba730345a926f444691be80c16a7fb89c`). **Aucun `.asc` actif** dans `tests/current/`.

**Gate A :** 107 scénarios natifs CPU 68000 PASS, export strict PASS et [CI candidate 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43027906298). [CI du commit de promotion 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43029502969) confirmée. Contrat : `_OK=Aga Palette Bank Capture(Start(bank),index)` copie la `ColorMap` RGB24 de l'écran AGA Intuition privé actif dans un emplacement AGAPAL sans modifier écran ni autres emplacements ; succès 1, refus 0 sans modification persistante. `Start(bank)` doit pointer vers une banque DATA AMOS vivante et initialisée R30 ; jamais un pointeur arbitraire/périmé. **Pas de capture IFF, d'application depuis banque, de fade ou cycling supplémentaire : discuter et approuver chaque future fonction avant codage.**

---



## R30 0.10.2 VALIDÉE — AGAPAL Bank Init, Gate A + Gate B AMOS/WinUAE PASS (11/11/2026)

**Preuve Gate B utilisateur :** capture du test corrigé `M13_R30_AGAPAL_BANK_INIT_01.asc` sous AMOS Professional interprété/WinUAE : `INIT 1 REINIT 1`, `HEADER AGAPAL V 1 COUNT 8`, `OFFSET0 80 OFFSET7 5456`, `BAD0 0 BAD257 0 BADSIZE 0`, `SENTINEL 99 ZERO 0`, `ABK RESTORED AGAPAL SIZE 6224`, `REST0 80 REST7 5456 INDEX 1`, `RESULT 1`, `CLOSE RETURNED` et sortie normale AMOS ligne 101. **Succès limité à ce scénario Gate B ; Gates C Compiler et D matériel physique NON TESTÉES.**

**Promotion obligatoire exécutée :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib`, **R30 0.10.2**, **17 824 octets**, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e` (octet pour octet). **R29 0.10.1 reste figée dans son archive**, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`. Le test corrigé, blob Git `646aa30fb61dfb2ff6b9f5bc5dfe47d8365b2964`, est archivé **sans modification** dans `tests/passed/M13_R30_AGAPAL_BANK_INIT_01.asc`. Aucun test `.asc` actif dans `tests/current/`.

**Gate A :** 39 scénarios CPU 68000 PASS ; export source strict et CI de promotion [32/32 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43024446890). La CI du commit de promotion est confirmée : **32/32 PASS**. La première erreur `Type mismatch` du script (variable `_STILL` au lieu de `_STILL$`) est résolue dans le test archivé ; **le code 68000 R30 n'a pas été modifié**.

**Contrat R30 :** `_OK=Aga Palette Bank Init(Start(bank),N)` initialise les emplacements RGB24 d'une banque DATA AMOS déjà réservée, taille `16+776*N` octets, N=1..256, indices 0..N-1. La banque et le fichier ABK restent gérés par `Reserve As Data`, `Save`, `Load`, `Erase` AMOS. La fonction réinitialise les couleurs et n'intervient pas sur l'écran. Pour la suite M13 : **discuter et approuver la prochaine fonction AGAPAL individuellement avant le moindre nouveau code** (capture/import/application/fades/cycling non implémentés).

---


**R30 — état technique après recherche :** l'enveloppe ABK native `AmBk` et la banque `DATA` Fast-prioritaire sont confirmées. Un **modèle de format Python et un prototype de sauvegarde/chargement ABK utilisant seulement les commandes AMOS** sont préparés : [`docs/M13_AGAPAL_R30_PREVIEW.md`](M13_AGAPAL_R30_PREVIEW.md). **Aucun nouveau token AP20**, aucune candidate R30, aucune Gate A CPU pour l'extension ni Gate B R30. La résolution du numéro de banque vers `Start(bank)` depuis A5 reste à établir à partir d'une interface AMOS documentée, sans offset supposé. **R29 0.10.1 reste la version courante validée et `LAST_GOOD`**.

## Historique de conception R30 — antérieur à l'implémentation et au PASS WinUAE

## R30 M13 — structure AGAPAL approuvée (11/11/2026, conception uniquement)

**Accord utilisateur sur l'architecture, sans nouveau token ni binaire R30 :** banque `DATA` native AMOS, enregistrable et rechargeable avec les commandes de banque AMOS dans un fichier **ABK standard**, contenant **plusieurs palettes AGA RGB24**. L'extension gérera un format intérieur `AGAPAL`, distinct du conteneur externe ABK que gère AMOS. Préférer la **Fast RAM** si le système de banques AMOS le permet : vérifier le comportement réel avant de promettre une zone mémoire.

**Organisation acceptée :** en-tête intérieur de **16 octets** (signature ASCII `AGAPAL` sur 6 octets, version, nombre de palettes et champs réservés), index de **8 octets par palette** (offset 32 bits, nombre de couleurs 16 bits, flags 16 bits), et **768 octets fixes par emplacement** (256 couleurs RGB24). **Indices internes à partir de 0.** Taille proposée : `16 + N × (8 + 768)`, soit **6 224 octets pour huit palettes**. Endianness, offsets exacts, représentation des emplacements libres et contrôle des données seront établis avant le code.

**Première fonction proposée :** `_OK=Aga Palette Bank Init(10,8)` après réservation AMOS DATA (exemple de conception : `Reserve As Data 10,6224`), retour attendu **1/0**. Le nom externe ABK de huit octets `AGAPAL  ` **n'est pas garanti** par une réservation DATA ordinaire : vérifier dans les sources/documentation AMOS les champs d'en-tête `AmBk`, le nom de banque et les mécanismes `Save`/`Load`. Une signature AGAPAL interne ne remplace pas l'enveloppe ABK native.

**Vérifications préalables obligatoires :** conventions `Reserve As Data`, allocation Chip/Fast, accès/taille des banques, identité et durée de vie, `Erase`, persistance ABK, ABI 68000 et limites d'allocation. Le premier incrément ne portera que sur `Aga Palette Bank Init` ; les futures commandes de capture, import, application, fades et cycling restent à discuter **individuellement** avant codage. **R29 0.10.1 reste la bibliothèque courante validée et LAST_GOOD ; seules des références de format et un prototype AMOS natif non testé ont été ajoutés pour R30.**

---

## R29 0.10.1 VALIDÉE (historique, avant la promotion R30) — Gate A + Gate B AMOS/WinUAE PASS, 11/11/2026

**Preuves utilisateur :** test `M13_R29_PALETTE_SAVE_01.asc` exécuté sous AMOS interprété/WinUAE : `OPEN 1 DB 1`, `DRAW 1 1 1 1`, `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. L'utilisateur confirme également l'ouverture de la palette IFF produite avec ses **256 couleurs dans Cloanto Personal Paint (PPaint)** ; le fichier ne contient pas de pixels `BODY`. Cela établit l'interopérabilité **pour ce fichier et cet essai**, pas tous les éditeurs IFF.

**Promotion obligatoire :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib`, **R29 0.10.1**, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, octet pour octet. L'archive R28 est figée et conservée. Le fichier de test original (Git blob `b80baabe5533288cac3285a78c232827cce94085`) est déplacé **sans modification** dans `tests/passed/M13_R29_PALETTE_SAVE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`.

**Validation :** Gate A CPU 68000 **49 scénarios PASS**, [CI R29 avant promotion **30/30 PASS**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43016176793) ; Gate B interprété/WinUAE **PASS** sur le test et PPaint précités. **Gates C (Compiler) et D (matériel réel) NON TESTÉES**. La validation sous PPaint ne démontre pas l'affichage des pixels puisque le format est volontairement sans `BODY`.

**Suite M13 :** fonctions de banques de palettes (Fast RAM privilégiée) et fades natifs `Aga Fade To Bank/Black/White`, puis cycling. **Avant chaque nouvelle fonction, discuter et valider son contrat avec l'utilisateur ; aucune implémentation anticipée.**

---

## M13 — décisions de conception du 11/11/2026 (avant codage R29)

- **Processus obligatoire :** discuter **chaque nouvelle fonction** avec l'utilisateur, arrêter explicitement son contrat, puis seulement coder/tester. Un feu vert sur le jalon R29 n'est pas une validation de toutes ses commandes.
- **R29 accepté en principe :** export de palettes au format **IFF standard `FORM ILBM` / `CMAP`**, sans format maison ; nom de commande, arguments, conditions d'erreur et restauration à définir ensemble.
- **Banques de palettes R30 :** conception approuvée ci-dessus : banque DATA native AMOS, signature interne `AGAPAL`, plusieurs palettes RGB24 indexées depuis 0, Fast RAM privilégiée si prise en charge. En-tête ABK réel et ABI à vérifier avant code.
- **Fades natifs souhaités :** `Aga Fade To Bank`, `Aga Fade To Black`, `Aga Fade To White`, **signatures non figées et tokens non implémentés**. Déterminer durée, synchronisation VBL, comportement bloquant ou non et interpolation RGB24 lors de chaque discussion.
- Puis cycling, M14 fontes et M15 dessin 2D. **R29 Save a passé Gate B et devient `LAST_GOOD` ; aucune nouvelle fonction sans contrat discuté.**

---

## R28 validée — 11/11/2026

M13/R28 0.10.0 : Gate A 159 cas 68000 PASS, CI précédente 29/29 PASS ; Gate B AMOS interprété/WinUAE PASS sur la capture M13-R28-PALETTE-01 du 11/11/2026. Résultats : OPEN/DB/IFF CMAP/SET/DRAW/SWAP = 1 ; BAD 0 BADG -1 ; PEAK 16254720 ($F80700), FINAL 65280 ($00FF00), FADEERR 0, CLOSED -1, RESULT 1, CLOSE RETURNED. Le test AMOS sélectionne un IFF sans que son chemin soit connu depuis la capture ; la compatibilité d'un export palette seule PPaint/DPaint réel n'est donc pas établie. Le résultat numérique n'atteste pas à lui seul l'observation visuelle complète des 64 transitions. Gate C Compiler et Gate D Amiga réel non testées.

**Bibliothèques :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` sont des copies binaires identiques de l'archive `dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib` : 16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`. R27 reste figée dans `dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib` (SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`). Test original déplacé octet pour octet : `tests/passed/M13_R28_PALETTE_01.asc`; aucun test ASC actif.

**Suite autorisée M13 :** palette sauvegardable au format standard IFF FORM ILBM/CMAP, sauvegarde/restauration, fade natif, puis cycling ; incréments séparés et Gate A avant toute nouvelle candidate. M14 fontes et M15 dessin 2D restent ultérieurs.

---

**Les états R28 « candidate / WinUAE en attente » plus bas sont des checkpoints historiques.**

**Objectif :** construire des primitives AGA réutilisables dans les programmes AMOS 365, sans imposer de réécriture du moteur des jeux. La roadmap décrit **l'ordre du travail à venir**, pas les anciens essais R1 à R15.

**R24 M9 Hotspot Hit (10/11/2026) : Gate A CPU/CI PASS (402 cas), Gate B AMOS/WinUAE PASS** sur le scénario utilisateur : `STATIC=1`, `OVERLAP=20`, `LEFT ID=20`, `RIGHT OUT=1`, `RESULT=1` et fermeture AMOS correcte ligne 183. [Test corrigé exact archivé](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc). Compteurs LEFT 13 / RIGHT 3 expliqués par des clics répétés volontairement (confirmation utilisateur) : aucune répétition parasite constatée ; test d'unicité sur clic isolé non réalisé. Focus et stress non vérifiés.

**R23 IDCMP 0.8.7 (10/11/2026) : Gate A CPU/CI PASS 15 cas (CI (archive CI privée, run #42899343161)), Gate B AMOS interprété/WinUAE PASS** sur clics rapides (`PRESSED=RELEASED=3`), FIFO clavier (`KEYS=64/64/-1`, `WAIT=16`, `RESULT=1`), et Ctrl+C : interruption à `_WAITK=Aga Wait Key` avec fermeture correcte de l'écran Intuition. [Test R23 archivé](../tests/passed/M8_R23_IDCMP_QUICK_01.asc) sans modification. Prochains contrôles éventuels : focus réel, stress et saturation. [Contrat R23](M8_IDCMP_R23.md).

**R22 (10/11/2026) :** `Aga Mouse Pressed/Released` **Gate A CPU/CI PASS (25 cas)** et **Gate B WinUAE PASS** sur le scénario utilisateur (fronts gauche/droit uniques, clavier, fermeture/réouverture, fin normale). [Test R22 archivé](../tests/passed/M8_R22_MOUSE_EDGES_01.asc). Clics très brefs et focus réel restent à valider ; [dossier R22](M8_MOUSE_EDGES_R22.md). R21 et `LAST_GOOD` protégées.

**Checkpoint R21 validé (10/11/2026) :** Gate A **PASS 11 cas CPU 68000 et CI verte**, Gate B **PASS utilisateur AMOS interprété/WinUAE** : le clic droit ne provoque plus de barre Intuition. Le test R21 a été archivé sans changement dans [`tests/passed/`](../tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc). R20 conserve son défaut de menu dans les archives, R19 X/Y et R18 Copper restent acquis ; `LAST_GOOD` R10 inchangée. **M8 reste en cours** pour les transitions natives, clics très brefs et gestion du focus. [Statut](M8_STATUS.md) · [R21](M8_RMBTRAP_R21.md).

**État historique antérieur à R29 (11/11/2026) :** **R28 0.10.0** était la candidate dans [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **Gate A CPU 159 cas PASS, Gate B WinUAE en attente**. **R27 0.9.3**, validée sous AMOS interprété/WinUAE (40 swaps, `RESULT 1`), est désormais la bibliothèque de repli [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib). R10 reste disponible dans l'[archive R10](../dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib). [Contrat M13/R28](M13_PALETTE_R28.md).

## 1. Vue d'ensemble — ordre des chantiers

| Jalon | Fonctionnalités | Situation | Prochaine décision / résultat attendu |
|---|---|---|---|
| M0–M4 | ABI AP20/AMOS, détection AGA, écran Intuition, présentation double buffer et VBL | Socle existant ; validations historiques selon leurs tests | Ne pas retoucher sans régression démontrée |
| M5 | Inspection et chargement IFF/ILBM, palettes et modes vidéo (dont HAM6/HAM8 et SuperHiRes) | **Clôturé par l'utilisateur** pour le périmètre testé sous WinUAE | Conserver les réserves Compiler, matériel, DblPAL/NTSC |
| M6 | `Aga Blit Copy`, `Aga Blit Fill`, `Aga Blit Clear` | **PASS AMOS interprété/WinUAE** sur tests archivés ; Compiler / Amiga réel non testés | Base R15 protégée |
| **M7 — VALIDÉ (RGB4 WinUAE)** | **Copper `Clear/Wait/Move/End/On/Off`** | **R16/R17/R18 PASS sous AMOS interprété/WinUAE**, raster visible | Réserves Compiler/Amiga réel, stress/fuites et couleurs AGA avancées |
| **M8 — VALIDÉ sur périmètre R23** | **Souris : positions, boutons, clics, dispatcher IDCMP** | R19–R23 CPU/WinUAE PASS sur scénarios archivés, Ctrl+C et retour Intuition inclus | Conserver R23 comme archive ; focus réel, stress, matériel/Compiler non testés |
| **M9 — R24 VALIDÉ (scénario WinUAE)** | **Hotspots : première primitive `Aga Hotspot Hit`** | Gate A CPU/CI PASS 402 cas ; Gate B WinUAE PASS sur bords, recouvrement ID 20, clic hors zone, fermeture/réouverture ; [test exact archivé](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc) | Évaluer si un registre de zones / l'horodatage du clic ou le drag sont nécessaires ; focus, stress et compilateur non testés |
| **M10 — R25 VALIDÉ (scénario WinUAE)** | **Collision rectangle/rectangle AABB** | `Aga Rect Overlap(ax,ay,aw,ah,bx,by,bw,bh)` ; **704 cas CPU/CI PASS et Gate B WinUAE PASS** : `STATIC 1 PURE 1`, `SEEN FREE 1 HIT 1`, `FRAMES 409 DRAWERR 0`, `RESULT 1`, fermeture AMOS correcte. [Test archivé inchangé](../tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) | Pas de mesure de 50 FPS ; Compiler, Amiga réel et stress non testés. Conserver R25 avant toute étape suivante |
| **M11 — R26 0.9.2 PASS WinUAE (texte + 40 swaps)** | **Rendu texte sur back buffer AGA** via `Aga Text(x,baselineY,pen,text$)` | **Gate A CPU/CI 64 cas PASS**, **Gate B WinUAE PASS sur deux scénarios** : [texte initial](../tests/passed/M11_R26_AGA_TEXT_01.asc) ; [multi-swap Safe/Disp 40 images](../tests/passed/M11_R26_SAFE_SWAP_02.asc) (`PROBE0 39`, `SWAP0 0`, toutes erreurs nulles, `RESULT 1`, alternance A/B confirmée). Les retries sont bornés, mais un retour 0 ne prouve pas à lui seul Safe | Garder R26 figée ; prochaine décision : éventuel contrat de protection des Blitters et tests de robustesse. **Ni Compiler, ni Amiga physique, ni FPS 50, ni stress exhaustif validés** |
| **M12 — R27 0.9.3 VALIDÉE sur scénario WinUAE** | **Auto-contrôle Safe de `Aga Blit Copy`, `Fill`, `Clear`** sans nouveaux tokens AP20 | **Gate A CPU 403 cas PASS, CI complète 28/28**, [run](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997575220), et **Gate B WinUAE PASS** sur [test M12 exact archivé](../tests/passed/M12_R27_SAFE_BLIT_01.asc) : `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, erreurs finales nulles, `RESULT 1`, clignotement visuel et fermeture AMOS ligne 167. Neuf segments modifiés dont six relocalisations R23 | Conserver R27 et R26 figées ; aucun FPS mesuré ni preuve de sûreté exhaustive. Compiler et Amiga AGA physique à tester seulement dans un chantier dédié |
| **M13 — R28 CANDIDATE / Gate A PASS, Gate B attendue** | **Palettes AGA 24 bits : import IFF/ILBM standard `CMAP` sans pixels, RGB Set/Get ; ensuite sauvegarde IFF, fades, color cycling** | [R28 0.10.0 candidate](../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib) de 16 208 octets, [159 cas CPU PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43004699618), **WinUAE non testé** ; binaire courant R27 inchangé | Test utilisateur [M13 R28](../tests/current/M13_R28_PALETTE_01.asc) avec palette IFF PPaint exportée ; garder R27 figée ; après PASS, définir sauvegarde IFF standard, fades puis cycling |
| **M14 — PRIORITÉ 2 (après M13)** | **Fontes / texte AGA : compléter `Aga Text` R26 (choix/chargement de fontes, mesures, styles, alignement, lignes multiples)** | Le rendu R26 actuel est **une ligne, 1 à 128 caractères, police système**, pas un moteur complet de fontes | Étudier `SetFont`, `TextExtent`, les fontes AmigaOS/diskfont et les banques AMOS/AMCAF sans présumer leur compatibilité ; contrat séparé après les palettes |
| **M15 — PRIORITÉ 3 (après M14)** | **Primitives de dessin AGA : Plot (pixel), Draw (ligne), Box (rectangle contour), Circle (cercle)** | **R40 `Aga Plot` candidate Gate A PASS, Gate B WinUAE en attente ; Draw/Box/Circle non implémentés** | Étudier les conventions des fonctions AMOS/Turbo/AMCAF, puis définir coordonnées, clipping, couleurs indexées, usage du back buffer Intuition AGA et protocole Safe avant toute nouvelle API |
| **M15bis — VISIBILITÉ DU POINTEUR AGA (avant M16)** | **Afficher/masquer à la demande le curseur souris uniquement dans la fenêtre Intuition AGA de l'extension** | Idée à étudier, aucune commande implémentée ; visible par défaut, souris toujours active | Utiliser un pointeur transparent propre à la fenêtre, restaurer le pointeur normal sur demande, au changement de fenêtre et à la fermeture ; tester Workbench, Ctrl+C et erreurs |
| **M16 — IDÉE À ÉTUDIER (après M15)** | **Format dédié d'images compressées en banque DATA, de préférence en Fast RAM ; rendu CPU vers le back buffer AGA en Chip RAM** | Proposition non implémentée ; deux modes prévus : opaque et transparent à masque 1 bit | Étudier format/compression rapide, conversion, clipping/Safe, mémoire et performances 68000/68020+ |
| M17+ — OPTIONS ULTÉRIEURES | Sprites matériels, scrolling, dual playfield, Copper avancé et optimisations | Pistes distinctes, à réexaminer après M15/M16 | Aucun développement ni nouvelle API engagé |

**Ordre défini le 11/11/2026 : M13 palettes → M14 fontes → M15 dessin 2D (`Plot`, `Draw`, `Box`, `Circle`).** **Idées ajoutées le 12/11/2026 : M15bis, visibilité du pointeur de la souris AGA, à traiter avant M16 ; puis M16, images compressées en Fast RAM**, à étudier après M15. Les autres pistes restent en M17+. M15bis et M16 sont des propositions sans API, implémentation ni calendrier approuvés. Les statuts réels des jalons précédents restent consignés dans les dossiers techniques.

## 2. M7 — Copper RGB4, bilan du scénario validé

Dossier technique faisant foi : [`M7_COPPER_DESIGN.md`](M7_COPPER_DESIGN.md). Avancement effectif : [`M7_STATUS.md`](M7_STATUS.md).

1. **M7.0 — sécurité (validée sur les scénarios R16–R18, sans stress test) :** confirmer le cycle de vie de `ViewPort.UCopIns` / `UCopList`, la propriété mémoire, l'attachement et le retrait avec l'écran Intuition. Ne jamais détourner `COP1LC/COP2LC`. `FreeVPortCopLists` ne doit pas être utilisé comme simple nettoyage de notre seule liste.
2. **M7.1 — R16/R17 PASS sous WinUAE sur leurs scénarios :** `Aga Copper Clear` crée une liste vide terminée sur l'écran privé ; `Aga Copper On` l'applique avec `MakeScreen/RethinkDisplay` ; `Aga Copper Off` la détache et libère les allocations possédées par l'extension après synchronisation. **R17 validée sur 3 exécutions** avec Off répétés et fermetures d'écran, fin AMOS normale ligne 83. Les 23 segments R16 restent inchangés (hors `GetP`). Les listes raster actives, les fuites mémoire éventuelles et le matériel réel restent hors de ce PASS. **R18 `Wait/Move/End` : PASS WinUAE sur le test raster du 10/11/2026.**
3. **M7.2 — effet raster minimal : PASS WinUAE.** liste contrôlée, WAITs croissants et MOVE limités à `COLOR00..COLOR31`, RGB4 12 bits dans cette première étape. Pas d'accès générique aux registres AGA ni de BPLCON3.
4. **M7.3 — recette : PASS AMOS interprété/WinUAE.** un seul programme AMOS de validation, raster visible, `Off` propre, `Aga Swap`, fermeture/réouverture, interruption clavier. Vérifier séparément CPU/CI, interprété WinUAE, Compiler et Amiga réel.
5. **Après preuve du noyau :** palette AGA 24 bits, banques de couleurs, effets plus sophistiqués ; pas d'anticipation avant le premier PASS.

**R16 WinUAE (10/11/2026) :** `C1/C2/C3=1`, `OPEN/REOPEN=1`, `SWAP=1`, `KEY 67`, `CLOSE X2 RETURNED`, fin ligne 74. **R17 WinUAE (10/11/2026) : PASS 3/3**, `C1/ON1/SWAP/OFF1/OFF2/C2/ON2/OFF3/REOPEN/C3/ON3/OFF4=1`, `KEY 67`, `CLOSE X2 RETURNED`, fin ligne 83. Tests archivés. **R18 WinUAE (10/11/2026) : PASS**, raster rouge/vert/bleu/noir visible ; `W1..W4=M1..M4=1`, rejets `BADREG/RGB/WAIT/END2/AFTER=0`, `END/ON/SWAP/OFF/OFF2/REOPEN/CLEAR2/ON2/OFF3=1`, `KEY 68`, `CLOSE X2 RETURNED`, fin ligne 95. Test corrigé archivé. **Non testés :** stress/fuites, Compiler et matériel réel. Voir [R16](M7_COPPER_R16.md), [R17](M7_COPPER_R17.md) et [R18](M7_COPPER_R18.md).

## 3. M8–M10 — interaction, clics et collisions

Spécification fonctionnelle de référence : [`INTERACTIONS_COLLISIONS.md`](INTERACTIONS_COLLISIONS.md).

- **M8, souris :** R19 X/Y non bloquantes **PASS CPU (76 cas) et WinUAE** le 10/11/2026, `P1=(0,0)` et `P2=(319,255)`. [Test archivé](../tests/passed/M8_R19_MOUSE_POSITION_01.asc). À développer : boutons, transitions, clic unique, focus/drag éventuel. Compiler et Amiga réel non testés.
- **M9, zones cliquables :** rectangles `(x,y,largeur,hauteur)`, identification par ID, activable/désactivable, règle de bord explicite, priorité si deux zones se recouvrent, clic déclenché une seule fois et état lié à l'écran.
- **M10, collisions :** point/rectangle, rectangle/rectangle (AABB), puis Bob/sprite/tuile et masque pixel éventuel. Séparer **détection de collision** et **résolution du déplacement / physique / gameplay**, qui appartient au jeu sauf besoin commun démontré.

Les hit-tests peuvent être de simples fonctions AMOS/extension sans matériel AGA. **Ne pas lier artificiellement les collisions au Copper** : ce sont des fonctions de logique 2D différentes.

## 4. Compatibilité graphique AMOS/AMCAF — axe transversal

Les fonctionnalités de l'extension doivent rester **génériques**, indépendantes d'un programme particulier. Toute compatibilité avec les primitives graphiques AMOS et AMCAF est à démontrer dans des scénarios reproductibles, pas à déduire de l'existence d'une commande.

1. **Écran/RastPort AMOS et AMCAF :** `Text` AMOS cible l'état graphique d'AMOS, pas notre écran Intuition AGA. **Le rendu natif est désormais disponible avec `Aga Text` R26**, via un `RastPort` temporaire lié au back buffer AGA, [validé sous WinUAE sur les scénarios M11](M11_TEXT_R26.md). **M14 doit compléter les fontes**, pas refaire ce premier rendu. `Change Bank Font`, `Scrn Rastport` et les banques AMOS/AMCAF ne sont pas automatiquement réutilisables ; audit nécessaire avant tout adaptateur. [Étude initiale M11](M11_TEXT_COMPAT.md).
2. **Blitter/copie :** `Aga Blit Copy` couvre les copies dans un **même back buffer** ; ce n'est pas un remplacement universel de `Screen Copy` (copies inter-écrans, caches ou autres formats). Définir les besoins par des tests.
3. **Bob/Icon, transparence/masques :** étudier `Paste Bob`, `Paste Icon`, `F 16 Icon` et `Bob Update`, les contraintes Chip RAM et les conversions éventuelles de banques.
4. **Primitives graphiques — M15 :** étudier les commandes AMOS `Plot`, `Draw`, `Box`, `Circle`, ainsi que les variantes optimisées Turbo/AMCAF (notamment `F Plot` et `F Draw`) avant de définir des équivalents AGA. **Ne pas recopier leurs conventions par supposition** : vérifier coordonnées (points finaux, inclusivité), épaisseur, clipping, rayon, encre et états graphiques dans les sources/documentations. Rendre sur le **back buffer AGA Intuition**, pas sur l'écran AMOS ; respecter `Safe` et éviter les appels DMA/CPU pendant une présentation non libérée.
5. **Présentation et palettes :** **M13 est prioritaire** pour piloter le `ColorMap` AGA 24 bits de l'écran Intuition de l'extension, importer une palette sans ses pixels, puis produire fades et cycling. Garder distincts le Copper RGB4 M7 et les commandes `Colour` / `Palette` des écrans AMOS ; ne pas traiter HAM/EHB comme des modes indexés 256 couleurs. Étudier séparément `Autoback` et `Screen Swap`.

Les priorités de compatibilité applicative sont **distinctes** de la roadmap générale de l'extension ; les capacités Copper et souris suivent leurs propres validations.

## 5. Suite décidée : M13 palettes, M14 fontes, puis M15 dessin 2D (11/11/2026)

### M13 — Palettes AGA 24 bits (premier chantier)

**Étape en cours :** [M13/R28 Load/Set/Get](M13_PALETTE_R28.md), **Gate A CPU 159 PASS**, disponible sous le nom exact [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) (16 208 octets). **Gate B WinUAE attend le test utilisateur**. La bibliothèque R27 0.9.3 validée a été promue dans `LAST_GOOD`. Export IFF, fades et cycling restent à développer après validation.


**Fonctions demandées et ordre de travail envisagé**, sans arrêter de noms/signatures AP20 avant analyse du code existant :

1. **Audit du socle :** relire le chargement `CMAP` des IFF/ILBM M5, `SetRGB32`, le `ColorMap` du `ViewPort` Intuition et les interactions avec le Copper RGB4 M7. Définir qui possède les couleurs et comment restaurer l'état à la fermeture de l'écran.
2. **Chargement indépendant des pixels :** importer la palette d'un fichier IFF/ILBM sans remplacer l'image du back buffer ; valider le format, le nombre d'entrées et les bornes. Objectif concret : **les exemples n'ont plus à charger une mire IFF pour simplement obtenir des couleurs**.
3. **Accès RGB 24 bits :** modifier et lire une entrée de palette par index, avec trois composantes 8 bits (R, G, B) et contrôles de profondeur/plage. Étudier la sauvegarde, la copie et la restauration de palettes ou groupes de couleurs.
4. **Fades :** fondu vers le noir, apparition depuis le noir, transition **palette A → palette B**, durée paramétrable en images/VBL, interpolation RGB déterministe et état final exact. Déterminer si l'animation est pilotée par des appels successifs ou par une routine dédiée **sans imposer d'attente bloquante**.
5. **Animations de palette :** color cycling d'une plage d'indices, sens et pas, pause/arrêt puis restauration de l'état initial. Les effets doivent rester compatibles avec la présentation double-buffer et l'écran Intuition.

**Contraintes à vérifier avant implémentation :** chemin système `ColorMap`/`ViewPort` (pas d'écriture directe non justifiée dans `BPLCON3`), synchronisation d'affichage, conflits possibles avec les listes Copper RGB4 actives, mode indexé 1–8 plans contre EHB/HAM, coût CPU et gestion des ressources. La palette n'est pas elle-même un BitMap arrière : son animation et les swaps doivent être testés conjointement. Les gates A/B/C/D restent distinctes.

**Livrable attendu avant R28 :** un contrat technique M13 et un programme de recette WinUAE représentatif (chargement sans pixels, couleur individuelle, fades progressifs et cycling), pas simplement un carré dont la couleur change.

### M14 — Reprendre sérieusement les fontes après M13

Le prototype `Aga Text` **R26** sait afficher **une ligne**, **1–128 caractères**, avec la **fonte système par défaut**, un index de couleur et une coordonnée verticale de **ligne de base**. Il n'expose actuellement **ni choix de fonte, ni chargement de police, ni métriques pour l'appelant**.

Pour M14, étudier dans cet ordre : **sélection/chargement et libération des fontes AmigaOS**, dimensions réelles (`TextExtent`, largeur/hauteur, baseline), styles et alignements, texte sur plusieurs lignes, fond opaque ou transparent et règles de clipping. L'éventuelle **prise en charge des banques de fontes AMOS/AMCAF ou de fontes bitmap personnalisées** demande une étude distincte du format et de la propriété mémoire ; elle n'est pas acquise par `Aga Text`.

### M15 — Primitives de dessin AGA (après M14)

**Fonctions demandées :** tracer un pixel (`Plot`), un segment de droite (`Draw`), le contour d'un rectangle (`Box`) et un cercle (`Circle`). L'objectif est d'obtenir de véritables primitives **sur le back buffer de l'écran Intuition AGA indépendant**, et non des appels aux commandes AMOS qui dessinent sur les écrans gérés par AMOS.

- **Avant de définir l'API :** contrôler les signatures et comportements réels des commandes AMOS `Plot`, `Draw`, `Box`, `Circle` et des extensions Turbo/AMCAF, en priorité `F Plot` / `F Draw`. Vérifier spécialement l'inclusivité des bords, les coordonnées hors écran, le rayon, le dessin du dernier pixel et les conventions d'encre ; **ne pas transposer automatiquement** celles de `Screen Copy`, `Bar` ou `Aga Blit Fill`.
- **Exécution :** dessiner dans le back buffer AGA (bitplanes indexés), avec contrôle du `Safe` introduit en R27, clipping documenté et absence de corruption hors limites. Étudier l'usage correct de `RastPort`/`graphics.library` plutôt que multiplier des implémentations 68000 non justifiées.
- **Contrats de recette :** points extrêmes, diagonales dans toutes les directions, lignes horizontales/verticales, rectangles partiellement hors champ, cercles tronqués, couleurs et profondeur 1–8 plans, double buffering, swaps répétés et fermeture/reprise AMOS. **Distinguer dessin de contour (`Box`) et remplissage (`Aga Blit Fill`)**.
- **Extensions possibles, non engagées :** ellipse, rectangle plein de type `Bar`, polylignes, épaisseur/style et remplissage de cercle, uniquement après validation des quatre primitives de base.

### M15bis — Visibilité du pointeur souris AGA (R44 v0.11.5 candidate Gate A PASS)

**Objectif :** permettre à un programme AMOS de **masquer ou réafficher à la demande le pointeur matériel Intuition** sur la **seule fenêtre de l'écran AGA privé** de l'extension. Par défaut, le pointeur reste visible. Le clavier, les coordonnées `Aga Mouse X/Y` et les boutons `Aga Mouse Buttons/Pressed/Released` continuent de fonctionner lorsque le pointeur est masqué.

- **Portée locale, sans effet global :** passer par `intuition.library/SetPointer` sur la `Window` possédée par l'extension, avec un petit sprite intégralement transparent en **Chip RAM** ; ne jamais couper le DMA des sprites, détourner `SPR0`, ni modifier le pointeur de Workbench ou les préférences système.
- **Restauration :** `ClearPointer(Window)` rétablit le pointeur Intuition normal sur demande ; en quittant la fenêtre pour Workbench ou une autre fenêtre, ce système utilise automatiquement le pointeur associé à la fenêtre devenue active. Si l'écran AGA redevient actif alors que l'option masquer est toujours engagée, le pointeur y reste invisible.
- **Nettoyage obligatoire :** avant `CloseWindow` / `Aga Screen Close`, sur arrêt normal, refus d'ouverture partielle, fermeture d'erreur et chemins Ctrl+C existants : retirer le pointeur personnalisé puis libérer son buffer Chip, sans laisser de pointeur invisible sur Workbench. Les appels répétés et la réouverture d'écran doivent préserver ces invariants.
- **API à contractualiser :** une seule commande de visibilité (par exemple `Aga Mouse Cursor(Visible)`, **nom et retour non arrêtés**) avec valeurs explicites visible/masqué, refus sans effet lorsqu'aucun écran AGA valide n'est ouvert. Aucune influence sur les écrans AMOS natifs.
- **Tests avant validation :** curseur visible par défaut ; bascule visible → masqué → visible ; `Aga Mouse X/Y`, clics et clavier inchangés ; passage vers Workbench puis retour AGA avec option masquée ; fermeture et réouverture ; Ctrl+C, échecs et alternances répétées sans fuite Chip RAM.

**Statut :** [contrat M15bis/R44 accepté](M15BIS_MOUSE_CURSOR_R44_DESIGN.md) et implémentation v0.11.5 : **Gate A CPU/CI PASS (516 cas)**, [candidate R44](../dist/AMOSPro_AGA.Lib) et [test WinUAE courant](../tests/current/M15BIS_R44_MOUSE_CURSOR_01.asc). **Gate B R44 PASS sur la régression, mais R43 reste `LAST_GOOD` jusqu'à la démo combinée.** Ne pas commencer M16 avant clôture R44 ou nouvel accord.

### M16 — Images compressées en Fast RAM (idée à étudier après M15)

**Objectif :** définir un format d'image alternatif aux IFF/ILBM pour les ressources de jeu (portraits, décors, interfaces, sprites logiciels), compressé dans une **banque DATA AMOS**, idéalement située en **Fast RAM**. Le **CPU** lirait et décompresserait les données puis dessinerait sur le **back buffer AGA en Chip RAM**. Il ne s'agit pas de reproduire les banques graphiques AMOS Bob/Icon. Le Blitter ne pouvant pas lire la Fast RAM, le rendu CPU constitue l'hypothèse de départ.

- **Format à définir :** en-tête versionné avec largeur, hauteur, profondeur indexée (1 à 8 bitplanes), type de compression, tailles/offsets et **masque de transparence 1 bit optionnel**. Étudier un convertisseur de ressources hors Amiga. Vérifier la localisation effective de la banque en mémoire : une banque DATA n'est pas automatiquement garantie en Fast RAM.
- **Deux modes d'affichage :** **opaque** (écrire chaque pixel, y compris l'index couleur 0) et **transparent** (masque 1 bit indépendant de la couleur : seuls les pixels visibles écrasent le décor). Alpha partiel hors premier périmètre.
- **Compression/décompression :** comparer RLE et variantes simples à décodage rapide ; privilégier un accès par lignes/blocs pour éviter un tampon contenant toute l'image décompressée en Chip RAM. Mesurer le rapport de compression, le coût CPU et la mémoire temporaire.
- **Rendu sécurisé :** positionnement X/Y, clipping sur les quatre bords, dessin non aligné sur les mots/bitplanes, validation des tailles, contrôle `Safe` avant écriture dans le back buffer AGA, respect du double buffering et absence de débordement mémoire.
- **Évolutions possibles :** sous-images/atlas, plusieurs frames et cache de décodage ; éventuel rendu hybride CPU/Blitter uniquement si un benchmark en démontre l'intérêt.
- **Recette avant validation :** images opaques et transparentes, pixels d'index 0 visibles avec masque, profondeurs 1/2/4/8, clipping sur chaque bord, swaps répétés, fermeture/reprise AMOS ; performances et consommation mémoire sur 68000 puis 68020/030, tests WinUAE et matériel distincts.

**Statut :** idée enregistrée dans la roadmap uniquement. Format, compression exacte, API et jalons d'implémentation restent à discuter avant tout code ; aucune bibliothèque existante n'est modifiée.

**M17+** : sprites matériels, scrolling, dual playfield, extensions Copper et optimisations à réexaminer séparément après M15/M16. Aucun développement engagé.

## 6. Règles de décision, livraison et suivi

- **Une seule source d'état immédiat :** [`NEXT_SESSION.md`](NEXT_SESSION.md) et le STATUS du jalon ; la roadmap ne reçoit plus les journaux R1→R15 en tête.
- **Chaque API future (M13 et suivantes) reste « proposée »** tant qu'elle ne figure pas dans un binaire et un scénario de validation identifié. Les commandes existantes M7–M12 sont disponibles uniquement dans le périmètre de leur version et de leurs tests documentés ; ne pas présenter les nouvelles fonctions de palette ou de fonte comme déjà implémentées.
- **Gates distinctes** : A = structure HUNK/AP20 + CPU/CI ; B = AMOS interprété/WinUAE ; C = AMOS Compiler ; D = Amiga AGA physique. Ne jamais transformer un préflight Python en PASS matériel.
- **Protection** : `dist/AMOSPro_AGA.Lib` = **candidate testable directement à cet emplacement**, pas de sous-répertoire ; après **Gate B WinUAE PASS utilisateur**, copier automatiquement le binaire validé dans `dist/AMOSPro_AGA_LAST_GOOD.Lib` (même contenu, test archivé) ; ne pas promouvoir une simple Gate A. Archives versionnées immuables. [Règle source](../EXTENSION_SOURCE_RULES.md).
- **Au prochain chantier** : lire [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md), le HEAD réel de `main` et les documents/status du jalon, avant de créer un builder ou un test.

**Navigation :** [index documentaire](README.md) · [architecture actuelle](ARCHITECTURE.md) · [Copper M7](M7_COPPER_DESIGN.md) · [souris / zones / collisions](INTERACTIONS_COLLISIONS.md).
