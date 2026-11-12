# EXTENSION_SOURCE_RULES.md

## RÈGLE PERMANENTE — README publics : concision et historique (12/11/2026)

**Les fichiers `README.md` (anglais) et `README.fr.md` (français) décrivent les fonctions disponibles et leur utilisation, et non un journal de développement.** Cette règle est indépendante du numéro de build.

1. Sous `## Libraries and tests` et `## Bibliothèques et tests`, commencer **directement** par un unique résumé actuel débutant par **Latest promoted `LAST_GOOD`** / **Dernière version promue `LAST_GOOD`**. Il précise la bibliothèque installable, la version, les limites de validation et les liens utiles, sans historique détaillé en amont.
2. **Interdiction d'empiler les anciennes versions avant ce résumé.** À chaque build ou promotion, **remplacer** le résumé en place (ne jamais préfixer un nouveau paragraphe `Rxx`). Transférer les anciens résultats, SHA, Gates, captures, échecs, tests et jalons dans [l'historique anglais](docs/LIBRARY_TEST_HISTORY.md), [l'historique français](docs/LIBRARY_TEST_HISTORY.fr.md) et/ou les rapports techniques de `docs/`. Ces historiques sont datés et clairement distingués de l'état courant.
3. Dans le tableau public des commandes AMOS, **première colonne = nom de la commande seulement** : pas de suffixe `(M15 R43, Gates A/B PASS)`, de version Rxx, ni de statut CI/WinUAE. La troisième colonne explique **syntaxe, paramètres, retour, limites et comportement** ; déplacer les preuves de validation et la chronologie hors de ce tableau.
4. Pour `Aga Image Draw`, indiquer **explicitement** que la **source AGAPIC en banque DATA peut résider en Fast RAM** : le **CPU lit/décompresse la source et dessine dans le back buffer AGA en Chip RAM**, sans imposer de copie Chip de l'image entière et sans lecture Fast par le Blitter. **Ne pas affirmer** que l'ABK témoin est physiquement en Fast RAM tant que sa localisation n'a pas été mesurée ; AMOS contrôle le placement réel.
5. Garder README anglais et français synchronisés (mêmes commandes, signatures, état courant et liens valides). Vérifier notamment `python -B tools/test_readme_api_coverage.py` et les règles de validation applicables. Les archives binaires et les tests déjà validés restent immuables.

## RÈGLE PERMANENTE — AP20 / AMOS Compiler : relocation des routines (incident Guru `80000004`, 12/11/2026)

**Obligatoire pour chaque évolution de l'extension**, et pas seulement pour le correctif R46. Les segments d'une bibliothèque AP20 ne constituent **pas** un unique bloc contigu garanti à l'exécution : l'interpréteur peut charger le tout, mais **AMOS Compiler extrait et reloge séparément les routines utilisées**. Un code qui fonctionne en interprété peut donc planter une fois compilé.

**Défaut constaté :** sur la bibliothèque non corrigée, `Aga Probe` revenait, `Aga Screen Open` retournait `1`, puis `Aga Screen Close` entraînait `Software Failure 80000004` après l'étape 05, avant l'étape 06. Plusieurs `BSR.w` (`61 00 xx xx`) visaient des offsets calculés depuis **la disposition complète du fichier AP20**, parfois dans un autre segment (notamment 8→54 pour le curseur et 8→48 pour la fermeture des fontes). **La rupture de relocation est un défaut structurel prouvé par l'inspection des binaire(s) et cohérent avec le correctif fonctionnel ; l'adresse exacte de l'instruction fautive n'a pas été capturée.** Ne pas inventer cette preuve manquante.

### À faire impérativement

1. **Considérer chaque entrée de la jump table AP20 comme relogeable indépendamment.** Un `BSR.w` / `BRA.w` / `LEA d16(PC)` ordinaire n'est acceptable **que si sa cible se trouve à l'intérieur de la même routine effectivement copiée**. Ne jamais supposer que les offsets inter-routines du fichier `.Lib` survivront à la compilation.
2. **Pour appeler une autre routine AP20, utiliser le mécanisme officiel `Rbsr`** (marqueur `$FE31`, suivi de l'index de routine). Les autres branchements relogeables utilisent leurs macros `Rb...` adaptées. Contrôler les index, la jump table, la taille de la cible et le traitement de `GetP` dans l'ABI AMOS. Références : [`+CEqu.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BCEqu.s), [`+Music.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BMusic.s), [`+APComp.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s).
3. **`Rbsr` appelle le DÉBUT du segment cible, pas un offset interne arbitraire.** Si l'ancien `BSR.w` aboutissait à un label au milieu d'un autre segment, il faut **extraire un helper autonome** (nouvelle entrée AP20), ou **placer ensemble les routines qui partagent des branches internes**. Ne pas remplacer aveuglément `BSR.w` par `Rbsr(index)` sans vérifier l'adresse visée et le contrat des registres.
4. **Traiter aussi les accès aux données d'état.** Un `LEA ... (PC)` vers les données situées dans une autre routine devient tout aussi invalide. Garder état et code dépendants dans la même unité relogeable ou fournir un getter/contrat d'accès relogeable explicite. Auditer les chemins de destruction : `CloseWindow`, `CloseScreen`, fonte, pointeur, double buffer, libérations mémoire, reset et sortie du programme.
5. **Avant de produire une candidate**, auditer les cibles de branches à partir **des vrais segments AP20 et des frontières d'instructions 68000** (un simple scan de mots `61 00` peut rencontrer des données, voire des mots à l'intérieur d'une autre instruction). Vérifier le format HUNK/AP20, le nombre de segments, les tokens et signatures, `GetP`, les tailles (une routine copiée doit rester sous la limite de 32 Kio), la reproductibilité, et les SHA des sources et archives figées.
6. **Préserver l'ABI à chaque passerelle** : pile A7 équilibrée et adresse de retour exacte ; pile de paramètres AMOS A3, conventions D2/D3, registres sauvegardés/restaurés, pointers A5/A6, alignement 68000 et états persistants. Exécuter des tests CPU des chemins réellement relogés, pas uniquement un diff de bytes. Ne jamais déduire un résultat runtime d'un contrôle statique.
7. **Vérifier la bibliothèque réellement installée dans `APSystem`**, son emplacement/slot et si possible son SHA256 ; relancer complètement AMOS puis **recompiler le programme**. L'exécutable antérieur intègre les anciennes routines et **ne teste pas** une nouvelle bibliothèque simplement copiée. Garder l'ancienne `.Lib` et sa configuration sauvegardées.
8. **Maintenir des Gates indépendantes** : Gate A (structure/CPU), B (AMOS interprété), C (**nouvel exécutable AMOS Compiler sous WinUAE**), D (machine AGA physique). Pour Gate C, tester **Open → Close → retour AMOS**, puis un usage graphique réel et les fonctions ayant des ressources persistantes ; distinguer absence de Guru, retours corrects, rendu visuel et absence de fuite mémoire. Un `Gate B PASS` ou un benchmark compilé qui démarre ne prouve pas à lui seul toutes les commandes.
9. **Ne pas répéter inutilement les tests déjà passés sans changement du code concerné.** Réutiliser les recettes exactes archivées : [trace Close](tests/diagnostics/R44_COMPILER_STAGE_TRACE.asc), benchmark utilisateur `graphics_32c_v2.asc` et [test R46 `Aga Image Draw`](tests/passed/M16_R46_IMAGE_DRAW_01.asc) avec sa [banque AGAPIC](tests/current/M16_AGAPIC_SAMPLE_BANK10.abk). Conserver les originaux PASS inchangés. En cas de Guru, relever le dernier repère **et l'adresse PC réellement fautive**, pas un `STOP` de Kickstart observé après le crash.
10. **Ne pas modifier ni promouvoir les bibliothèques stables pendant ce diagnostic.** Les expériences vont exclusivement dans `dist/experimental/`, avec constructeur reproductible et SHA distinct. Ne travailler **que sur `main`**, sauf demande explicite contraire.

### Solution expérimentale C1 : ce qu'elle valide et ce qu'elle ne valide pas

Le [pont relogeable C1 de R46](docs/GATE_C_R46_MONOLITH_CANDIDATE.md) conserve les **27 856 octets de code R46** dans un unique segment de **27 888 octets** avec dispatcher, et expose les entrées publiques via `Rbsr`. La trace compilée **Open/Close** et le benchmark `graphics_32c_v2.asc` **fonctionnent sans Guru**, selon les essais utilisateur. Cela confirme une **solution de contournement du scénario observé**, pas encore un correctif définitif ni une Gate C générale. En contrepartie, le Compiler peut incorporer **tout le bloc ~28 Kio pour une seule commande** : ne **pas** transformer silencieusement cette architecture monolithique en règle de production ; une correction modulaire relogeable est préférable si elle est validée.

**`Aga Image Draw` :** maintenir la lecture/décompression CPU depuis une banque DATA AGAPIC **potentiellement en Fast RAM** et le dessin dans les bitplanes AGA en Chip RAM ; conserver les modes opaque/masqué, l'index couleur 0, le clipping, `Safe`, les validations RLE et les contrôles des flags natifs **0/1/3**. Ne pas prétendre que la banque chargée est physiquement en Fast sans mesure et **ne pas marquer son test compilé PASS avant son exécution effective**. La Gate C complète doit également couvrir le curseur, les fontes et leur nettoyage.

**Rapports techniques :** [analyse du Guru](docs/GATE_C_R44_COMPILER_DIAGNOSTIC.md), [audit des appels inter-segments](docs/GATE_C_COMPILER_RELOCATION_AUDIT_2026-11-12.md), [résultats et protocole C1](docs/GATE_C_R46_MONOLITH_CANDIDATE.md). Ne pas répéter cette chronologie dans les README publics.

## M16/R46 v0.12.1 — Gates A/B PASS, LAST_GOOD (12/11/2026)

**AMOS interprété / WinUAE : PASS sur captures utilisateur** du test `M16-R46-IMAGE-DRAW-01`. Images opaque, masquée et décalée visibles, quatre côtés clippés : `OPAQUE 1 MASK 1 SHIFT 1`, `CLIP 1 1 1 1`, `BAD 0 0 0 OUT 1`, `SWAP 1 BACKSAFE 1`, `CHIP BEFORE/END 1801928 1801928`, `NATIVE LEN 1852 WANT 1852`, `NATIVE NO 10 FLAGS 0`, `NATIVE NAME AGAPIC`, `HEAD AGAPIC V 1`, `STREAM 196 TOTAL 1836`, **`ERRORS 0 RESULT 1`**, **`CLOSE RETURNED`** (ligne 148). La chaîne graphique `R45 - CPU AGAPIC IMAGE` est un ancien libellé dans le test R46, conservé sans retouche.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib`, **29 288 octets**, SHA256 `5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580`, même blob Git ; **50 commandes AP20 / 56 segments** ; 258 scénarios natifs CPU 68000 et source strict Gate A PASS ([CI R46](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43221899949)). Test WinUAE exact archivé en `tests/passed/M16_R46_IMAGE_DRAW_01.asc` (**4 240 octets**, Git blob `83eff57323b1cacd0ea58a131ef1ebcec079eceb`) ; aucun ASC actif dans `tests/current/`. Archive R44 validée et archive R45 échouée immuables. **Gate C Compiler non validée** (CI expérimentale distincte en échec), **Gate D Amiga AGA physique non testée**. Emplacement Fast RAM réel et performances 68000 matériel non mesurés. **Branche `main` uniquement.**


## M15 + M15bis — R44 v0.11.5 : CLÔTURE Gates A/B et LAST_GOOD (12/11/2026)

**M15 Plot/Draw/Box/Circle et M15bis Aga Mouse Cursor sont clôturés** après la CI Gate A (516 scénarios CPU 68000 R44) et les validations WinUAE utilisateur : test R44 (500 bascules, 0 erreur, CHIP DROP 0, RESULT 1, CLOSE RETURNED) puis démonstration globale `examples/m15_2d_cursor.asc` (« ça marche super »). Le retour global confirme le fonctionnement visuel, sans capture chiffrée fournie pour cette démo. **49 commandes AP20, 55 segments.**

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive versionnée R44, **27 460 octets**, SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`. Original `M15BIS_R44_MOUSE_CURSOR_01.asc` archivé octet pour octet en `tests/passed/` (blob Git `099f7125260c340dfbb4819f5770d1dbafd6789d`), `tests/current/` sans ASC actif. **R43** et les versions antérieures demeurent archivées et non modifiées. **Gates C Compiler / D AGA physique NON TESTÉES.**

**Rapport de clôture :** [docs/M15_M15BIS_R44_CLOSURE.md](docs/M15_M15BIS_R44_CLOSURE.md). **Étape suivante éventuelle : M16**, format d'images compressées en Fast RAM avec dessin CPU ; aucun code M16 engagé. **Uniquement `main`**, aucune branche créée. Les sections R43 et antérieures ci-dessous sont des archives historiques de leur époque.

## M15/R43 v0.11.4 — Aga Circle : Gates A CPU/CI et B AMOS/WinUAE PASS, LAST_GOOD (12/11/2026)

**R43 VALIDÉE par l'utilisateur (capture « parfait !!! ») :** `_OK=Aga Circle(CX,CY,Radius,Pen)` — cercle de contour d'un pixel par Bresenham midpoint 68000 en arithmétique 32 bits avec clipping sécurisé des huit octants, sans dessin hors écran ni bord inventé. Écran AGA privé, uniquement sur le back buffer après `Safe` non bloquant ; aucune allocation persistante, aucun swap/VBL implicite. **48 commandes AP20, 54 segments ; 436 scénarios CPU 68000 Gate A PASS et CI complète PASS** ([CI candidate](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43204551950)).

**Gate B AMOS interprété/WinUAE PASS :** l'utilisateur confirme le rendu et la capture affiche `OPEN 1 DB 1 CLEAR 1`, `CIRCLES 1 1 1 1 DOT 1`, `CORNERS 1 1 1 1`, `CLIPPED 1 1 1 1`, `PEN0 1 OUTSIDE 0 0 0 0`, `WRAP 0 BADR 0 0`, `BADXY 0 0 BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`** et **`CLOSE RETURNED`**. [Test d'origine archivé sans modification](tests/passed/M15_R43_CIRCLE_01.asc), Git blob `088158365a64accf0417fdda3fbba74e2e58ebf7` (**3 466 octets**) ; aucun fichier ASC dans `tests/current/`.

**Promotion obligatoire réalisée :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib`, **27 092 octets**, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf`, à l'octet près. **R42** reste dans son archive versionnée intacte (25 896 octets, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`) ; toutes les versions précédentes conservées. **Gates C Compiler et D AGA physique NON TESTÉES.** M15 primitives de base (Plot/Draw/Box/Circle) terminé sur les Gates A/B. **Suite à discuter : M15bis, visibilité locale du pointeur souris AGA, avant M16 (images compressées Fast RAM)**. R39 fontes bitmap toujours reportée ; aucun nouveau contrat de commande validé pour M15bis/M16. Dépôt `anthea176/AMOSPro-AGA-Extension`, **`main` uniquement**.

## M15/R42 v0.11.3 — Aga Box : Gates A CPU/CI et B WinUAE PASS, LAST_GOOD (12/11/2026)

**R42 VALIDÉE :** `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, **47 commandes AP20**, **360 tests CPU 68000 + export source natif strict + CI PASS**, Gate B AMOS interprété/WinUAE **PASS confirmé par l'utilisateur** (« ça marche ! bravo »). Capture : `OPEN 1 DB 1 CLEAR 1`, `BOXES 1 1 1 REV 1`, `CLIPPED 1 1 1 1`, `LINES 1 1 DOT 1`, `OUTSIDE 0 0 0 0`, `WRAP 0 BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne **119** ; rendu validé. [Test original archivé sans retouche](tests/passed/M15_R42_BOX_01.asc), Git blob `dbf5cefb215cc0ae1359d648ea34c855a92b2012` (**3 264 octets**). **`tests/current/` ne contient aucun ASC actif.**

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib` **octet pour octet**, **25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`. L'archive R41 v0.11.2 (SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`), R40, R38 et les précédentes sont inchangées. Contour d'un pixel, coins inclusifs et inversables, clipping des **quatre côtés originaux** sans fausse bordure, sécurité du back buffer `Safe` et refus des paramètres invalides. **Gates C Compiler et D Amiga AGA physique NON TESTÉES.** Prochain chantier éventuel : M15/R43 `Aga Circle` (NON implémenté). R39 fontes bitmap reste reportée. **La proposition M16 de banque d'images compressées en Fast RAM reste une idée de roadmap, pas une fonction livrée.** Dépôt `anthea176/AMOSPro-AGA-Extension`, **`main` uniquement**.

## Historique de préparation avant validation R42

**M15/R42 v0.11.3 — CANDIDATE PUBLIÉE, Gate A CPU/CI PASS (360 scénarios), Gate B WinUAE NON TESTÉE (12/11/2026).** `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, **47 commandes AP20**. Coins inclusifs normalisés, 1 px d'épaisseur, clipping indépendant des quatre côtés d'origine (jamais de bordure inventée), refus sécurisé des rectangles hors écran, validation des coordonnées signed16 et index `Pen`, BitMap physique et signal `Safe` non bloquant. [Test unique WinUAE](tests/current/M15_R42_BOX_01.asc) à importer via **Project → Merge ASCII**. `dist/AMOSPro_AGA.Lib` et `dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib` identiques (**25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`). **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la R41 v0.11.2 validée** (24 816 octets, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`) ; archives R41 et antérieures inchangées. [CI CPU + source strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43198823212). Gates C Compiler/D AGA physique non testées. Aucun test R42 archivé ou `LAST_GOOD` promu sans validation utilisateur. Travail uniquement sur `main` de `anthea176/AMOSPro-AGA-Extension`.

**M15/R42 Gate A CPU/CI PASS (12/11/2026) :** **360 tests 68000** avec contrôle pixel à pixel du contour, sécurité des bitplanes, huit orientations de coins, rectangles clippés et hors écran, signal `Safe`, ABI, AP20 **47 commandes / 53 segments**, export assembleur strict et [CI globale PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43198823212). Binaire reproductible R42 v0.11.3 généré **en mémoire uniquement** : **25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`. **Gate B AMOS interprété/WinUAE non testée** ; la R41 v0.11.2 demeure `LAST_GOOD` (24 816 octets), intacte. Le programme de recette R42 est préparé mais non encore publié.

**M15/R42 — Aga Box autorisée (12/11/2026) :** contrat `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, contour 1 pixel aux coins inclusifs, inversion automatique des coins et **clipping indépendant des quatre côtés d'origine** (pas de fausse bordure si le rectangle englobe l'écran). Vérifier les coordonnées signed16 et le Pen indexé ; seulement le back buffer AGA, `Safe` non bloquant, RastPort temporaire, Move/Draw uniquement après bornage, WritePixel pour segments réduits à un point. Source `tools/m15_box_r42_emit.py`, builder `tools/build_m15_box_r42.py`, test CPU `tools/test_m15_box_r42.py`. [Contrat détaillé](docs/M15_BOX_R42.md). **R42 en cours : Gate A CPU/CI en attente, Gate B WinUAE NON TESTÉE ; pas encore de candidate publiée.** R41 v0.11.2 reste `LAST_GOOD` (46 commandes AP20, 24 816 octets, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`, Gates A/B PASS). Aucune nouvelle branche ; R39 reportée, R43 non engagée.

## M15/R41 v0.11.2 — Gates A CPU/CI et B WinUAE PASS, LAST_GOOD (12/11/2026)

**R41 `Aga Draw(X1,Y1,X2,Y2,Pen)` VALIDÉE** : 46 commandes AP20, **325 tests CPU 68000 + export assembleur strict + CI PASS**, puis test AMOS interprété/WinUAE confirmé par l'utilisateur (« rendu ok ! »). Capture : `OPEN 1 DB 1 CLEAR 1`, `BORDER 1 1 1 1`, `CLIPPED 1 1 1 1`, `STAR 8 ERR 0 CENTER 1`, `OUTSIDE 0 0 0 0`, `BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne **131**. [Test exact archivé](tests/passed/M15_R41_DRAW_01.asc) (Git blob `aa7de64b37a2842db21bc7452c2fab4570413e9f`, 3 553 octets). `tests/current/` ne contient aucun ASC actif.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib` **octet pour octet**, **24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`. Archive R40 v0.11.1 préservée (SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`), ainsi que R38 et les archives antérieures. Dessin strictement sur le back buffer AGA : tracé rapide `Move/Draw` uniquement si extrémités valides ; clipping logiciel avec contrôle **avant chaque pixel** hors limites. **Gates C AMOS Compiler et D Amiga AGA réel NON TESTÉES.** R39 fontes bitmap reportée ; R42 `Aga Box` et R43 `Aga Circle` non implémentées. Dépôt `anthea176/AMOSPro-AGA-Extension`, branche **`main` uniquement**.

## Historique (avant promotion R41)

**M15/R41 v0.11.2 — CANDIDATE PUBLIÉE, Gate A CPU/CI PASS (325 scénarios), Gate B WinUAE NON TESTÉE (12/11/2026).** `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)`, **46 commandes AP20** ; tracé rapide pour lignes intégralement à l'écran et Bresenham avec vérification de chaque pixel avant `WritePixel` pour les segments qui dépassent. [Test unique WinUAE](tests/current/M15_R41_DRAW_01.asc), import par **Project → Merge ASCII**. `dist/AMOSPro_AGA.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib` à l'octet près (**24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`). **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la R40 v0.11.1 validée** (23 840 octets, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`), archives R40/R38 et plus anciennes inchangées. [CI CPU 68000 + source strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43193933457). Gates C Compiler/D Amiga réel non testées. Ne promouvoir R41 et n'archiver le test qu'après validation explicite de l'utilisateur. **Uniquement `main` du dépôt `anthea176/AMOSPro-AGA-Extension`.**

**R41 Gate A CPU/CI PASS (12/11/2026) :** **325 scénarios CPU 68000**, audit des 46 jetons AP20/52 segments, clipping par Bresenham en dehors des bords, accès direct `Move/Draw` uniquement dans les bornes, structure bitmap, état `Safe/Disp`, intégrité des anciens segments, pile et registres ; export natif 68000 strict PASS et [CI complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43193933457). **Gate B AMOS/WinUAE non testée**, R40 `LAST_GOOD` inchangée. Binaire déterministe R41 généré en mémoire : **24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`. Publication de candidate en préparation, aucun `.Lib` R41 encore dans `dist/`.

**M15/R41 — Aga Draw autorisée le 12/11/2026 :** implémentation de `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)` (nouvelle commande AP20 index 51, **46 commandes prévues**), en deux voies : `graphics.library/Move/Draw` seulement avec extrémités strictement dans le back buffer, **Bresenham logiciel avec contrôle avant chaque pixel** dès qu'une extrémité est extérieure. Paramètres 32 bits AMOS vérifiés dans l'intervalle signé 16 bits pour éviter toute troncature ; segments entièrement hors écran retournent 0. Garde `Safe` non bloquante, validation bitplanes et index couleur. [Contrat R41](docs/M15_DRAW_R41.md) ; émetteur `tools/m15_draw_r41_emit.py`, builder `tools/build_m15_draw_r41.py`, test CPU `tools/test_m15_draw_r41.py`. **Gate A CPU/CI en attente ; Gate B WinUAE NON TESTÉE.** R40 v0.11.1 **LAST_GOOD** SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231` strictement inchangée. La candidate R41 est maintenant publiée (Gate A PASS). R39 rejetée ; R42/43 non engagées. Branche `main` uniquement.

## M15/R40 v0.11.1 — Aga Plot : Gates A CPU/CI + B WinUAE PASS, LAST_GOOD (12/11/2026)

**R40 VALIDÉE sous AMOS interprété / WinUAE :** `_OK=Aga Plot(X,Y,Pen)`, **45 commandes AP20**. 221 scénarios CPU 68000 + export strict et [CI candidate](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43129055588) PASS. Confirmation utilisateur le 12/11/2026 (« ça marche nickel ») avec capture `OPEN 1 DB 1 CLEAR 1`, `PALETTE 1 1 1 1`, `CORNERS 1 1 1 1`, `CENTER 1 PEN0 1`, `DIAG 192 ERR 0`, `BADXY 0 0 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne 99. [Test original archivé octet pour octet](tests/passed/M15_R40_PLOT_01.asc) (Git blob `6ab9cf4a91cca9f8097ffba40a32e2b85b049c38`). `tests/current/` sans ASC actif.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib` à l'octet près (**23 840 octets**, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`). L'archive R38 v0.11.0 et toutes les versions antérieures restent inchangées. **Gate A CPU/CI PASS, Gate B WinUAE PASS, Gates C Compiler/D Amiga physique NON TESTÉES.** Protection intégrée : refus des coordonnées X/Y hors de `[0,Width-1]`/`[0,Height-1]` et des pen hors de `0..2^Depth-1` avant tout dessin, vérification des bitplanes et du back buffer `Safe`. `Aga Draw`, `Aga Box`, `Aga Circle` non implémentées ; les protections de `Plot` ne constituent pas un clipping général. R39 fontes bitmap 8x8 est reportée. Dépôt unique `anthea176/AMOSPro-AGA-Extension`, **branche `main` uniquement**.

**Historique R40 — lancement du développement avant validation WinUAE :** lancement du codage de la seule commande `_OK=Aga Plot(X,Y,Pen)`. Émetteur natif 68000 `tools/m15_plot_r40_emit.py`, builder déterministe `tools/build_m15_plot_r40.py` depuis **archive R38 immuable**, test CPU `tools/test_m15_plot_r40.py`. Contrat : index de couleur 0..2^Depth-1, bornes x/y strictes, back buffer privé, `Safe` non bloquant, `WritePixel=0` converti en retour AMOS **1**, autres échecs **0**, aucun swap/VBL implicite. **Gate A CPU/CI PASS (221 scénarios et strict export)** ; **Gate B était alors encore non testée** ; binaire courant **R40 candidate**, `LAST_GOOD` **R38 à cette date**. Plan initial (réalisé) : après Gate A PASS, générer la candidate R40 `dist/AMOSPro_AGA.Lib` et un unique test actif `tests/current/`, conserver `LAST_GOOD` R38 jusqu'à validation utilisateur. R39 reste reportée. Aucun dessin de ligne/boîte/cercle encore engagé.

**Décision M15 (12/11/2026) :** l'utilisateur demande de **sauter R39** (fontes `Change Print Font` 8×8) et de passer directement au **dessin 2D AGA M15**. Ordre de travail proposé : **R40 `Aga Plot`**, puis `Aga Draw`, `Aga Box`, `Aga Circle`, un seul appel public par sous-jalon. Le contrat et l'audit sont dans [`docs/M15_DRAWING_2D_DESIGN.md`](docs/M15_DRAWING_2D_DESIGN.md). **Historique de la phase d'étude uniquement, antérieure à l'approbation et à la validation de R40.** R38 v0.11.0 était alors `LAST_GOOD` ; R40 a depuis été validée A/B et promue, Gates C/D non testées. Travail exclusivement sur `main` du dépôt courant.

**Suivi de fuite Chip RAM R38 — VALIDÉ WinUAE (12/11/2026) :** 500 sélections de fontes AMCAF Topaz/Hwarf/Pix3M + Topaz AmigaOS, chacune suivie de `Aga Text` sur un écran AGA privé. `Chip Free = 1 582 088` et plus grand bloc Chip libre `1 320 664` identiques aux six relevés 0..500 ; `CHIP DROP 0`, `BIG DROP 0`, `ERR 0`, `RESULT 1`, `CLOSE RETURNED` (ligne 167). Reset +12 712 octets libres, fermeture +170 472 octets supplémentaires. Aucune fuite mesurée sur ce scénario. `tests/passed/M14_R38_CHIP_RAM_STRESS_01.asc`, Git blob original `976635ad8562c88ed07753c71a4dc2a6d18c2e29` intact ; `tests/current/` sans ASC actif. Binaires R38 et `LAST_GOOD` inchangés. Gates C Compiler/D matériel AGA réel non testées.

## R38 0.11.0 — Aga Font Bank Select : Gates A/B PASS, archive historique (12/11/2026)

**Gate B confirmée par l'utilisateur** (« ca a marché ! »), sous AMOS interprété/WinUAE avec la candidate corrigée après les refus BANK 0 / BANK2 0. La fonction `Aga Font Bank Select(Start(bank),Length(bank))` prend en charge les banques AMCAF `BankFont` monochromes fixes et proportionnelles, DATA/WORK, source CHIP/FAST. Le rendu s'effectue sur une copie privée allouée en **Chip RAM**, et les anciennes fontes sont libérées par `StripFont` puis `FreeVec` au remplacement/reset/fermeture. **Contrôle complémentaire WinUAE du 12/11/2026 : 500 changements de fontes et 500 appels à `Aga Text`, sans baisse de la Chip RAM libre ni du plus grand bloc libre** (voir le test d'endurance archivé). Ce résultat ne démontre pas l'absence de fuite dans tous les scénarios. La Gate A a validé **60 groupes CPU 68000**, banques réelles Topaz/Hwarf/Pix3M et régressions R37/R26/R36 ; CI intégrité candidate PASS. **44 commandes AP20**.

**Promotion R38 :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib` à l'octet près (**23 380 octets**, SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`). L'ancienne R38 rejetée est archivée sous `dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38_FAILED_BANK0.Lib` ; R37 v0.10.9 reste archivée, non modifiée. Test original déplacé sans modification de `tests/current/M14_R38_FONT_BANK_01.asc` vers `tests/passed/M14_R38_FONT_BANK_01.asc`, Git blob `4d847f86bfffc9d0d062c75e6bdda97a13b623bf`. `tests/current/` sans ASC actif. Gates C Compiler et D Amiga réel **NON TESTÉES**. R39 reste à discuter et approuver avant tout codage. Dépôt et branche autorisés : `anthea176/AMOSPro-AGA-Extension` / `main` seulement.

[Contrat R38](docs/M14_FONT_BANK_R38.md) · [Gate A CPU](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43123200900) · [CI intégrité candidate](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43123419858).

---

## R37 0.10.9 — Aga Font Select : Gates A CPU/CI et B AMOS/WinUAE PASS (11/11/2026)

**Commande approuvée et implémentée :** `_OK=Aga Font Select(FontName$,YSize)`, sélection d'une fonte AmigaOS via `OpenDiskFont` (taille demandée 1..255, nom de 1..127 octets) ; `Aga Font Select("",0)` rétablit la fonte système. `Aga Text` applique `SetFont` avant `TextExtent` sur son RastPort AGA privé. Fonte libérée au remplacement, au reset et à `Aga Screen Close`. Les fontes des banques AMCAF ne sont **pas encore prises en charge**. [Contrat R37](docs/M14_FONT_SELECT_R37.md).

**Gate A CPU/CI PASS :** 20 groupes de tests natifs 68000 R37, régressions R26 (64 cas) et R36 (106 scénarios), export assembleur strict PASS. [CI R37](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43075769541) PASS, **43 commandes AP20**.

**Gate B AMOS interprété/WinUAE PASS :** capture de l'utilisateur sur le test [`M14_R37_FONT_SELECT_01.asc`](tests/passed/M14_R37_FONT_SELECT_01.asc), Git blob original **`5371c310142f33aa2312e59ed81e2e2d6b90da3d`** conservé octet pour octet. `OPEN 1 DB 1 PALETTE 1 1`, `SEL8 1 TX8 1 SEL9 1 TX9 1`, `BAD0 0 BAD256 0 BADNAME 0`, `KEEP 1 RESET 1 DEFAULT 1`, `SWAP 1 NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`** ; rendu visuel et retour AMOS normal confirmés (« fonctionnement nickel »). Aucune métrique de vitesse mesurée.

**R37 promue `LAST_GOOD` :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M14_v0.10.9_FONT_SELECT_R37.Lib`, **22 328 octets**, SHA256 `bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a`. La version antérieure R36 v0.10.8 reste archivée sans changement, **21 836 octets**, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`. **Aucun test actif dans `tests/current/`.** Gates C Compiler et D Amiga réel **NON TESTÉES**.

**Suite M14, sans autorisation de codage :** examiner et contractualiser individuellement R38 (banques de fontes AMCAF `Make Bank Font`), puis R39 (fontes bitmap 8×8 de `Change Print Font`). Aucune fonction nouvelle sans accord explicite ; travailler uniquement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, aucune autre branche ni dépôt.

**Les sections R36 et antérieures ci-dessous sont des checkpoints historiques : leurs références aux binaires et `LAST_GOOD` décrivent leur époque, pas l'état de R37.**

---

## R36 0.10.8 — Aga Palette Cycle : Gates A CPU/CI et B AMOS/WinUAE PASS (11/11/2026)

**Une seule commande approuvée :** `_OK=Aga Palette Cycle(First,Last,Direction)`, une rotation RGB32 complète par appel (+1 : dernière couleur vers premier index, -1 : inverse), indices inclus `0<=First<Last<256` dans les pens logiques/ColorMap de l'écran AGA Intuition privé indexé. Un `GetRGB32`, permutation exacte des triplets 32 bits, un `LoadRGB32` sur la plage seulement, **aucun `WaitTOF` implicite** ; aucun pixel, banque, fichier ou couleur hors plage touché. Scratch Exec public `8+12*N` (max 3 080 octets) libéré. Succès 1, invalides/refus atomiques 0 ; AMOS pilote la cadence. [Contrat technique R36](docs/M13_PALETTE_CYCLE_R36.md).

**Gate A CPU/CI PASS :** **106 scénarios natifs CPU 68000 PASS**, export source 68000 strict PASS, [CI candidate complète 38/38 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43064975345), **42 commandes AP20**.

**Gate B interprété AMOS/WinUAE PASS — capture utilisateur :** quatre bandes affichées avant 20 rotations à huit VBL d'intervalle. `OPEN 1 DB 1 DRAW 1 1 1 1`, `CYC20 1 RESTORED 16711680 16776960`, `FWD 1 COLOR 16776960 16711680 65280 255`, `REV 1 RESTORE 16711680 16776960`, `NEG 1 COLOR 65280 16711680 POS 1`, `RESET 16711680 16776960`, `BADFIRST 0 BADEQ 0 BADORDER 0`, `BADLAST 0 DIR0 0 DIR2 0 DIRN 0`, `AFTERBAD 16711680 NOSCREEN 0`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin AMOS normale **ligne 138**. Confirmation utilisateur « fct nickel ! », sans mesure FPS ni durée réelle.

**R36 promue `LAST_GOOD` à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib`, **21 836 octets**, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`. Archive **R35 0.10.7 préservée intacte**, 21 300 octets, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`. [Test R36 original archivé](tests/passed/M13_R36_PALETTE_CYCLE_01.asc), Git blob `4644236576033f755ac0dc274f6f22f92a2d9201` conservé **sans modification**. **Aucun ASC actif dans `tests/current/`.** Gates C Compiler et D Amiga AGA réel **NON TESTÉES**.

**Suite :** R36 clôturée côté AMOS interprété/WinUAE. Aucun R37 ou autre fonction sans discussion et accord explicite de l'utilisateur. Travailler uniquement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, sans autre branche ni dépôt.

---

## R35 0.10.7 — Aga Fade To White : Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Contrat approuvé — seule fonction ajoutée :** `_OK=Aga Fade To White(vbl)`, durée entière 1..255 VBL (0/négatifs/>255 refusés sans modification), fondu RGB24 bloquant de tous les pens logiques de l'écran AGA Intuition privé indexé vers le **blanc exact**. Une capture source `GetRGB32` si vbl>1, interpolation signée 8.8 et un `graphics.library/WaitTOF` suivi de `LoadRGB32` par VBL, dernière image RGB32 `0xFFFFFFFF` exacte. Pas de banque AGAPAL, pixel ou fichier touché ; HAM/EHB/dual playfield rejetés, ColorMap contrôlée, tampon Exec `8+42*N` octets (max 10 760) libéré. Pas de mesure FPS ni de garantie de temps écoulé en cadence réelle. [Contrat technique R35](docs/M13_FADE_WHITE_R35.md).

**Gate A CPU/CI PASS :** 50 scénarios natifs 68000 et export source strict PASS, [CI candidate complète 37/37 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43057572164), 41 commandes AP20.

**Gate B PASS — capture utilisateur AMOS interprété/WinUAE :** `OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 WHITE 16777215 16777215`, `WHITE2 16777215 16777215`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 16777215`, `FADE2 1 TWO 16777215`, `SAME 1 SAME28 16777215`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. L'utilisateur a confirmé « c nickel » après le fondu visible de 150 VBL, sans mesure de cadence/FPS.

**R35 promue `LAST_GOOD` à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib`, **21 300 octets**, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`. **R34 0.10.6 est préservée dans son archive** (20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`). [Test R35 exact archivé](tests/passed/M13_R35_FADE_TO_WHITE_01.asc), Git blob `21115dfbbcff345e6ae8132c03956152b897a6b2` inchangé. **`tests/current/` sans aucun ASC actif.** Gates C Compiler/D Amiga AGA réel NON TESTÉES.

**Suite :** R35 clôturée côté WinUAE. Ne pas implémenter d'autre commande (R36 ou autre) sans discussion et accord explicite. Rester strictement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, aucune autre branche ni dépôt.

---

## R34 0.10.6 — Aga Fade To Black : Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Contrat approuvé et unique fonction ajoutée :** `_OK=Aga Fade To Black(vbl)`, durée entière 1..255 VBL (0, négatifs et >255 refusés). Fondu RGB24 **bloquant** de tous les pens logiques de l'écran AGA Intuition privé indexé vers le **noir exact**, un `graphics.library/WaitTOF` et `LoadRGB32` par étape, interpolation signée 8.8 depuis la capture `GetRGB32` ; dernière étape RGB32 nulle sans erreur d'arrondi. Aucune banque AGAPAL nécessaire, aucune écriture pixels, banques ou fichiers. Scratch Exec `8+42*N` octets (max 10 760) libéré. Refus sans effet ; retour 1 succès, 0 échec. Pas de mesure FPS ni garantie de durée réelle exacte sur 68000. [Contrat technique R34](docs/M13_FADE_BLACK_R34.md).

**Gate A PASS :** 48 scénarios CPU natifs 68000 et export source strict PASS, [CI de publication complète 36/36 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43053552010), 40 commandes AP20.

**Gate B PASS — capture utilisateur WinUAE/AMOS interprété :** `OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 BLACK 0 0 0 0`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 0 FADE2 1 TWO 0`, `SAME 1 SAME28 0`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 113**. L'utilisateur confirme « nickel » sur la démonstration visuelle du fondu 150 VBL ; cadence/FPS non mesurés.

**Promotion R34 à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib`, **20 752 octets**, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`. R33 0.10.5 reste figée dans son archive (20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`). Le [test exact R34 archivé](tests/passed/M13_R34_FADE_TO_BLACK_01.asc) est conservé **sans modification** (blob Git `5fe2f819048cd3706eedaf363f3415a00270406a`). **Aucun ASC actif dans `tests/current/`**. Gates C Compiler/D Amiga AGA réel **NON TESTÉES**.

**Suite :** aucune nouvelle fonction implémentée ; discuter et approuver un nouveau contrat (par exemple Fade To White) **avant** tout codage. Rester exclusivement sur `main`, pas d'autre branche ni de dépôt sans demande explicite.

---
## R33 0.10.5 VALIDÉE — Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Nouvelle fonction :** `_OK=Aga Fade To Bank(Start(bank),index,vbl)`. Fondu RGB24 **bloquant** sur 1..255 VBL ; `WaitTOF` puis `LoadRGB32` par image, interpolation 8.8 signée, **dernière image RGB24 exacte**. Uniquement les pens 0..compte-1 sont modifiés ; banques/pixels et pens supérieurs restent inchangés. `vbl=0` refusé ; pour une application immédiate utiliser `Aga Palette Bank Apply`. Requiert une banque DATA AGAPAL **vivante** (`Start(bank)` réel), une palette non vide et un écran AGA indexé privé. Scratch Exec temporaire `8+42*N` (10 760 octets max), libéré. Les VBL ne garantissent pas une durée réelle stricte si le calcul dépasse une trame.

**Gate A :** 51 scénarios CPU natifs 68000 PASS, export source 68000 strict PASS, **[CI de publication 35/35 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43045308067)**, 39 commandes AP20.

**Gate B fonctionnelle PASS — capture utilisateur WinUAE/AMOS interprété :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `FADE0 1 GREEN 65280`, `FADE1 1 BLUE 255 SAME 1 255`, `PART 1 PEN3 660510 PEN28 16711680`, `BAD0 0 BAD256 0 BADNEG 0`, `BADINDEX 0 EMPTY 0 BADSIZE 0`, `AFTERBAD 16711680 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 BLUE 255`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 141**. Le test confirmait les couleurs finales et les rejets, **pas la qualité visuelle ni la fluidité du fondu** : son `Aga Swap` et `Amos To Back` étaient exécutés APRÈS les transitions, et celles-ci duraient surtout 12/1/2 VBL. **Démo distincte** [`examples/fade_to_bank_r33.asc`](examples/fade_to_bank_r33.asc) : affiche d'abord trois grandes bandes, puis rouge → vert → bleu → rouge en 150 VBL avec des pauses. Démo **validée visuellement sous WinUAE par l'utilisateur le 11/11/2026 : fondu visible et fonctionnel**, sans mesure de cadence, FPS ou durée réelle.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R33 `dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib`, **20 208 octets**, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`, strictement identiques. R32 préservée intacte en archive (19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`). ASC fonctionnel archivé à l'octet près : [`tests/passed/M13_R33_AGAPAL_FADE_01.asc`](tests/passed/M13_R33_AGAPAL_FADE_01.asc). Aucun ASC actif dans `tests/current/`. Gates C (Compiler) et D (Amiga AGA physique) **NON TESTÉES**.

**Suite :** observation visuelle positive enregistrée ; ne pas prétendre à une mesure de fluidité, FPS ou cadence sans instrumentation. Toute prochaine fonction doit être discutée et approuvée avant le codage ; mettre à jour les deux README et rester strictement sur `main`, sans autre branche/dépôt.

---
## R32 0.10.4 VALIDÉE — Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Fonction ajoutée seule :** `_OK=Aga Palette Bank Apply(Start(bank),index)` applique une palette RGB24 AGAPAL non vide (1..256 couleurs) à l'écran AGA privé par `graphics.library/LoadRGB32`, immédiatement sans VBL implicite. Retour entier 1/0, aucun changement des banques/pixels, seuls les pens 0..compte-1 remplacés. Exiger un vrai `Start(bank)` d'une banque DATA vivante, jamais un numéro brut ou une adresse périmée.

**Gate A :** 136 scénarios CPU 68000 PASS, export source 68000 strict PASS, [CI candidate 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040), [CI documentaire 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032630960).

**Gate B PASS — capture utilisateur de `M13_R32_AGAPAL_APPLY_01.asc` :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `AP0 1 AP1 1 PART 1`, `GREEN 65280 RED 16711680 BLUE 255`, `PEN224 795192 PART3 660510 PART28 255`, `BADNEG 0 BAD8 0 EMPTY 0`, `BADSIZE 0 BADCOUNT 0`, `AFTERBAD 255 AFTERCOUNT 255`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 16711680 PART 1`, `REST3 660510 REST28 16711680`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, et fin propre `End of program at line 161`. PASS limité à ce scénario AMOS interprété/WinUAE ; Compiler et vrai Amiga AGA non testés.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib`, **19 244 octets**, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894` (octet pour octet). R31 0.10.3 est préservée en archive versionnée (18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`). ASC validé archivé **sans modification** dans [`tests/passed/M13_R32_AGAPAL_APPLY_01.asc`](tests/passed/M13_R32_AGAPAL_APPLY_01.asc). **Aucun ASC actif** dans `tests/current/`. Gates C Compiler/D matériel réel **NON TESTÉES**.

**Suite :** aucune fonction Import/Fade/Cycling sans échange et accord explicite sur son contrat ; travailler seulement sur `main`, aucun autre dépôt ni branche.

---


## R31 0.10.3 VALIDÉE — AGAPAL Capture, Gate A CPU + Gate B AMOS/WinUAE PASS (11/11/2026)

**Preuve Gate B utilisateur :** capture de l'exécution du test `M13_R31_AGAPAL_CAPTURE_01.asc` sous AMOS interprété/WinUAE : `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED` et fin AMOS normale ligne 141. **PASS uniquement pour ce scénario interprété/WinUAE ; Gates C Compiler et D matériel Amiga réel NON TESTÉES.**

**Fichier ABK réellement inspecté (fourni par l'utilisateur) :** `R31_AGAPAL_CAPTURE.ABK`, **6 244 octets au total**, en-tête externe natif `AmBk` (bank 10, flags DATA 1), corps interne `AGAPAL` v1 **6 224 octets**, huit emplacements. Indices 0 et 1 : 256 couleurs RGB24 chacun ; pen 28 = `0000FF` dans la palette 0 et `FF0000` dans la palette 1. Indices 2 à 7 : descripteurs à zéro et RGB24 tous à zéro. Pens 3 et 224 conservés ; intégrité des offsets et signatures vérifiée. SHA256 du fichier ABK fourni : `7a3162969b0d700287ae0852872811dae072c19720a794beb8818d01b93f6cd9`. Ce contrôle de fichier corrobore l'essai WinUAE mais ne constitue pas une validation du Compiler.

**Promotion obligatoire effectuée :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib`, **R31 0.10.3**, **18 520 octets**, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`, strictement identiques. R30 0.10.2 reste **intacte dans son archive figée** (17 824 octets, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`). Test `.asc` validé archivé **octet pour octet** : `tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc` (Git blob `0196fc1ba730345a926f444691be80c16a7fb89c`). **Aucun `.asc` actif** dans `tests/current/`.

**Gate A :** 107 scénarios natifs CPU 68000 PASS, export strict PASS et [CI candidate 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43027906298). [CI du commit de promotion 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43029502969) confirmée. Contrat : `_OK=Aga Palette Bank Capture(Start(bank),index)` copie la `ColorMap` RGB24 de l'écran AGA Intuition privé actif dans un emplacement AGAPAL sans modifier écran ni autres emplacements ; succès 1, refus 0 sans modification persistante. `Start(bank)` doit pointer vers une banque DATA AMOS vivante et initialisée R30 ; jamais un pointeur arbitraire/périmé. **Pas de capture IFF, d'application depuis banque, de fade ou cycling supplémentaire : discuter et approuver chaque future fonction avant codage.**

---



## R30 0.10.2 VALIDÉE — AGAPAL Bank Init, Gate A + Gate B AMOS/WinUAE PASS (11/11/2026)

**Preuve Gate B utilisateur :** capture du test corrigé `M13_R30_AGAPAL_BANK_INIT_01.asc` sous AMOS Professional interprété/WinUAE : `INIT 1 REINIT 1`, `HEADER AGAPAL V 1 COUNT 8`, `OFFSET0 80 OFFSET7 5456`, `BAD0 0 BAD257 0 BADSIZE 0`, `SENTINEL 99 ZERO 0`, `ABK RESTORED AGAPAL SIZE 6224`, `REST0 80 REST7 5456 INDEX 1`, `RESULT 1`, `CLOSE RETURNED` et sortie normale AMOS ligne 101. **Succès limité à ce scénario Gate B ; Gates C Compiler et D matériel physique NON TESTÉES.**

**Promotion obligatoire exécutée :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib`, **R30 0.10.2**, **17 824 octets**, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e` (octet pour octet). **R29 0.10.1 reste figée dans son archive**, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`. Le test corrigé, blob Git `646aa30fb61dfb2ff6b9f5bc5dfe47d8365b2964`, est archivé **sans modification** dans `tests/passed/M13_R30_AGAPAL_BANK_INIT_01.asc`. Aucun test `.asc` actif dans `tests/current/`.

**Gate A :** 39 scénarios CPU 68000 PASS ; export source strict et CI de promotion [32/32 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43024446890). La CI du commit de promotion est confirmée : **32/32 PASS**. La première erreur `Type mismatch` du script (variable `_STILL` au lieu de `_STILL$`) est résolue dans le test archivé ; **le code 68000 R30 n'a pas été modifié**.

**Contrat R30 :** `_OK=Aga Palette Bank Init(Start(bank),N)` initialise les emplacements RGB24 d'une banque DATA AMOS déjà réservée, taille `16+776*N` octets, N=1..256, indices 0..N-1. La banque et le fichier ABK restent gérés par `Reserve As Data`, `Save`, `Load`, `Erase` AMOS. La fonction réinitialise les couleurs et n'intervient pas sur l'écran. Pour la suite M13 : **discuter et approuver la prochaine fonction AGAPAL individuellement avant le moindre nouveau code** (capture/import/application/fades/cycling non implémentés).

---


## R29 0.10.1 VALIDÉE (historique, avant la promotion R30) — Gate A + Gate B AMOS/WinUAE PASS, 11/11/2026

**Preuves utilisateur :** test `M13_R29_PALETTE_SAVE_01.asc` exécuté sous AMOS interprété/WinUAE : `OPEN 1 DB 1`, `DRAW 1 1 1 1`, `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. L'utilisateur confirme également l'ouverture de la palette IFF produite avec ses **256 couleurs dans Cloanto Personal Paint (PPaint)** ; le fichier ne contient pas de pixels `BODY`. Cela établit l'interopérabilité **pour ce fichier et cet essai**, pas tous les éditeurs IFF.

**Promotion obligatoire :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib`, **R29 0.10.1**, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, octet pour octet. L'archive R28 est figée et conservée. Le fichier de test original (Git blob `b80baabe5533288cac3285a78c232827cce94085`) est déplacé **sans modification** dans `tests/passed/M13_R29_PALETTE_SAVE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`.

**Validation :** Gate A CPU 68000 **49 scénarios PASS**, [CI R29 avant promotion **30/30 PASS**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43016176793) ; Gate B interprété/WinUAE **PASS** sur le test et PPaint précités. **Gates C (Compiler) et D (matériel réel) NON TESTÉES**. La validation sous PPaint ne démontre pas l'affichage des pixels puisque le format est volontairement sans `BODY`.

**Suite M13 :** fonctions de banques de palettes (Fast RAM privilégiée) et fades natifs `Aga Fade To Bank/Black/White`, puis cycling. **Avant chaque nouvelle fonction, discuter et valider son contrat avec l'utilisateur ; aucune implémentation anticipée.**

---

## RÈGLE PRIORITAIRE — DISCUTER ET VALIDER CHAQUE FONCTION AVANT DE CODER (11/11/2026)

**Demande explicite de l'utilisateur : avant chaque nouvelle fonction ou instruction, échanger sur sa conception, puis obtenir son accord sur le contrat de cette fonction, avant toute implémentation.**

1. **Une fonction à la fois :** présenter son besoin, son nom proposé, sa syntaxe AMOS (instruction ou fonction), ses paramètres, valeurs de retour/erreurs, limites, mémoire et durée de vie, effets sur écran/palette, comportement temporel et protocole de test pertinent. Échanger avec l'utilisateur sur les choix encore ouverts.
2. **Pas de code avant accord explicite sur la fonction discutée :** ne pas modifier de source 68000, builder, tests `.asc`, binaire `.Lib` ni API publique pour cette nouvelle fonction tant que la discussion et la validation du contrat ne sont pas terminées. La validation d'une roadmap ou d'un jalon entier (par exemple « OK pour R29 ») **n'autorise pas automatiquement toutes les fonctions suivantes**. À l'issue d'une fonction, présenter et discuter la suivante avant de la coder.
3. **Documentation possible pendant la discussion :** consigner décisions, propositions et points ouverts dans les règles et les documents de suivi, sans transformer un nom envisagé en token déjà disponible ni annoncer un PASS inexistant.
4. **Après accord**, appliquer toutes les règles de développement, les Gate A/B/C/D et la promotion obligatoire de `LAST_GOOD` ; travail exclusivement sur `main`, aucun autre dépôt ni branche sans demande explicite.

## Historique de conception R30 — antérieur à l'implémentation et au PASS WinUAE

## R30 M13 — structure AGAPAL approuvée (11/11/2026, conception uniquement)

**R30 — état technique après recherche :** l'enveloppe ABK native `AmBk` et la banque `DATA` Fast-prioritaire sont confirmées. Un **modèle de format Python et un prototype de sauvegarde/chargement ABK utilisant seulement les commandes AMOS** sont préparés : [`docs/M13_AGAPAL_R30_PREVIEW.md`](docs/M13_AGAPAL_R30_PREVIEW.md). **Aucun nouveau token AP20**, aucune candidate R30, aucune Gate A CPU pour l'extension ni Gate B R30. La résolution du numéro de banque vers `Start(bank)` depuis A5 reste à établir à partir d'une interface AMOS documentée, sans offset supposé. **R29 0.10.1 reste la version courante validée et `LAST_GOOD`**.


**Accord utilisateur sur l'architecture, sans nouveau token ni binaire R30 :** banque `DATA` native AMOS, enregistrable et rechargeable avec les commandes de banque AMOS dans un fichier **ABK standard**, contenant **plusieurs palettes AGA RGB24**. L'extension gérera un format intérieur `AGAPAL`, distinct du conteneur externe ABK que gère AMOS. Préférer la **Fast RAM** si le système de banques AMOS le permet : vérifier le comportement réel avant de promettre une zone mémoire.

**Organisation acceptée :** en-tête intérieur de **16 octets** (signature ASCII `AGAPAL` sur 6 octets, version, nombre de palettes et champs réservés), index de **8 octets par palette** (offset 32 bits, nombre de couleurs 16 bits, flags 16 bits), et **768 octets fixes par emplacement** (256 couleurs RGB24). **Indices internes à partir de 0.** Taille proposée : `16 + N × (8 + 768)`, soit **6 224 octets pour huit palettes**. Endianness, offsets exacts, représentation des emplacements libres et contrôle des données seront établis avant le code.

**Première fonction proposée :** `_OK=Aga Palette Bank Init(10,8)` après réservation AMOS DATA (exemple de conception : `Reserve As Data 10,6224`), retour attendu **1/0**. Le nom externe ABK de huit octets `AGAPAL  ` **n'est pas garanti** par une réservation DATA ordinaire : vérifier dans les sources/documentation AMOS les champs d'en-tête `AmBk`, le nom de banque et les mécanismes `Save`/`Load`. Une signature AGAPAL interne ne remplace pas l'enveloppe ABK native.

**Vérifications préalables obligatoires :** conventions `Reserve As Data`, allocation Chip/Fast, accès/taille des banques, identité et durée de vie, `Erase`, persistance ABK, ABI 68000 et limites d'allocation. Le premier incrément ne portera que sur `Aga Palette Bank Init` ; les futures commandes de capture, import, application, fades et cycling restent à discuter **individuellement** avant codage. **R29 0.10.1 demeure la bibliothèque courante validée et LAST_GOOD ; le prototype Python/AMOS n'est ni un token AP20 ni un test CPU 68000/WinUAE de R30.**

---

### M13 — R29 et futures banques/fades : décisions et points à définir

- **R29 accepté dans son principe :** poursuivre par la sauvegarde/export de palettes au **format IFF standard `FORM ILBM` + `CMAP`**, compatible avec les logiciels de dessin, sans format propriétaire. Les appels AMOS précis, le traitement des erreurs, le fichier de sortie et la restauration restent à discuter avant codage.
- **Banques de palettes demandées :** pouvoir **charger/conserver une palette dans une bank mémoire**, indépendamment de son application immédiate au `ColorMap`. **Privilégier la Fast RAM lorsqu'elle est disponible**, avec comportement de repli et gestion d'échec mémoire à définir. Vérifier d'abord s'il faut une banque AMOS native ou une banque propre à l'extension, ainsi que son identifiant, son propriétaire, sa taille et sa libération ; aucun contrat d'allocation n'est encore arrêté.
- **Fades natifs demandés (noms proposés, non exportés) :** `Aga Fade To Bank`, `Aga Fade To Black`, `Aga Fade To White`. Discuter **séparément, avant de coder chacune**, les paramètres (banque, durée/étapes), l'interpolation RGB24, le rythme VBL, l'aspect bloquant ou non, les cas limites, l'état final exact et l'interaction avec la palette courante/Copper.
- Le **color cycling** viendra ensuite selon le même processus de discussion individuelle. **R29 0.10.1 est validée Gate B et promue dans `LAST_GOOD`, avec uniquement `Aga Palette Save`.** Aucune banque/Fade/cycling supplémentaire n'est implémentée. R28 0.10.0 demeure son archive immuable.

---

## RÈGLE PRIORITAIRE — BINAIRES DANS `dist/` ET PROMOTION DE `LAST_GOOD` (11/11/2026)

**Cette règle permanente prévaut sur tous les checkpoints historiques ci-dessous (R10, R12, R23, etc.) qui décrivent les états passés.** Le numéro indiqué dans les anciennes notes n'est plus un état courant.

1. **Candidat à tester :** placer la version la plus récente ayant passé **Gate A (préflight CPU/CI)** directement dans **`dist/AMOSPro_AGA.Lib`**, avec son **nom exact**. Ne pas la placer dans un sous-répertoire et ne jamais demander à l'utilisateur de renommer un fichier `.Lib`. Préserver en parallèle **une archive versionnée distincte** dans `dist/experimental/`.
2. **Dernière version validée :** dès que l'utilisateur **confirme un test réussi sous AMOS interprété/WinUAE (Gate B)**, recopier **octet pour octet** cette bibliothèque validée dans **`dist/AMOSPro_AGA_LAST_GOOD.Lib`**, dans le même commit que l'archivage du test et la mise à jour du statut. **Cette promotion est obligatoire et ne nécessite pas de nouvelle demande.** Le PASS vaut pour le scénario testé : ne pas prétendre que Compiler/matériel réel ont passé les Gates C/D.
3. **Une candidate non validée en Gate B ne remplace JAMAIS `LAST_GOOD`.** Un échec CPU/CI ou WinUAE ne change pas la dernière référence validée ; conserver les archives figées, SHA256 et tests réussis.
4. **Aucun fichier `AMOSPro_AGA.Lib` dans un sous-répertoire arbitraire de `dist/`.** La version à installer est systématiquement `dist/AMOSPro_AGA.Lib`; les autres bibliothèques y ont un **nom versionné d'archive**, jamais besoin d'une manipulation manuelle/renommage par l'utilisateur.
5. Travailler **uniquement sur `main`**, aucune branche nouvelle, aucun dépôt sans instruction explicite. Mettre à jour ensemble les règles, la CI, les empreintes et les README FR/EN.

**Clôture historique M13/R28 11/11/2026 (avant R29) :** Gate B PASS sur capture `M13-R28-PALETTE-01`, `RESULT 1`, `FADEERR 0`, `CLOSE RETURNED`. `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` sont identiques à l'archive R28 (16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`). Test original archivé octet pour octet dans `tests/passed/`. R27 reste dans son archive immuable (SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`). Gates C/D non testées ; fichier IFF choisi et animation complète non établis par la seule capture. Les états antérieurs « R28 en attente / LAST_GOOD R27 » ci-dessous sont historiques. 

**État de référence immédiat (historique avant ce PASS) :** `dist/AMOSPro_AGA.Lib` = **R28 0.10.0**, candidate palettes, **Gate A PASS 159 scénarios CPU/CI, Gate B en attente** ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` = **R27 0.9.3**, dernière version **confirmée WinUAE PASS** (40 swaps, test `tests/passed/M12_R27_SAFE_BLIT_01.asc`). L'ancienne `LAST_GOOD` **R10** subsiste **sans modification** dans `dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib`. Les R27/R28 restent aussi archivées par version. **Ne pas promouvoir R28 avant Gate B.**

---

## M6 R13 — règles de travail Blitter (premier candidat)

La validation du loader IFF R12 est clôturée. Le prochain chantier **M6** commence par **`Aga Blit Copy`** uniquement, sur le **back buffer**, via `graphics.library/BltBitMap(-30)` et `WaitBlit(-228)`. **R13 0.7.0 est expérimentale : aucune validation runtime AMOS/WinUAE encore acquise.** Préserver R12 `dist/AMOSPro_AGA.Lib` et R10 `LAST_GOOD` ; ne jamais les écraser pour produire un candidat non testé.

Contrat à respecter : paramètres `(sx,sy,dx,dy,w,h)` avec `D3=h`, cinq précédents dans `(A3)+` (20 octets consommés) ; sortie résultat entier en `D3`, `D2=0`. Appels AmigaOS avec leurs registres explicitement réinitialisés. Refuser toute dimension invalide **avant** le blit, y compris stride/depth/Rows du Bitmap. Ne pas recoder les shifts, modulos, overlap, descending en écriture directe des registres au premier candidat. Le test CPU Unicorn est une gate statique/ABI seulement ; le test utilisateur `tests/current/M6_R13_BLIT_COPY_01.asc` est nécessaire avant PASS runtime. `Fill`/`Clear` restent hors de ce candidat, voir `docs/M6_BLITTER_R13.md`.

---


## CLÔTURE IFF / ILBM R12 — 10/11/2026

**Chantier terminé sur décision utilisateur.** Tests R12 0.6.3 réussis : HAM6, HAM8, SuperHiRes 1280×256, SuperHiRes Lace 1280×512. Jeff-Flag (736×482, NTSC HiRes Lace et position correcte) et EHB avaient déjà été essayés avec succès. **DblPAL et DblNTSC non testés** faute de moniteur, sans caractère bloquant. Ne pas les déclarer compatibles sur cette seule base.

**Portée de la validation :** retour visuel utilisateur sur les nouveaux modes, sans identification précise du `.asc` ni preuve de compilation R12. AMOS Compiler R12, vrai Amiga AGA, stress exhaustif, Fallout sous R12 restent non confirmés ; ils ne rouvrent pas le chantier IFF clos. CI HUNK/AP20/ILBM/CPU PASS (archive CI privée, run #42838022562).

**État Git :** PR #4 fusionnée sur `main`. `dist/AMOSPro_AGA.Lib` R12 0.6.3, 8856 octets, SHA256 `b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec`. `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R10 0.6.1, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`, **inchangé**.

**Tests :** test Jeff R12 archivé octet pour octet dans `tests/passed/R12_JEFF_A0_RETRY.asc` ; aucun `.asc` dans `tests/current/`. Ne pas attribuer ce script aux essais HAM/SuperHiRes non identifiés. Prochain chantier possible : **M6 Blitter Copy / Fill / Clear**, sans développement commencé. Les anciennes sections ci-dessous sont historiques si contradictoires.

---


## HISTORIQUE — R12 NewScreen et repli PAL (10/11/2026)

**Échec du test précédent :** déplacer `Amos To Back` avant `Aga Screen Open` sous R10 ne change **strictement rien** au placement trop bas de Jeff. Hypothèse éliminée, test archivé `tests/historical/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc`.

**Erreur concrète trouvée dans R10 :** lors du second `OpenScreenTagList` (repli NTSC → PAL), le helper restaure A1 (TagList) mais pas A0 (NewScreen). Le premier appel initialise pourtant A0 à NULL ; le second peut hériter d'une valeur volatile après les appels système. R12 ajoute uniquement `SUBA.L A0,A0` (`91C8`) juste avant cet appel, avec les trois branchements internes correctement relocalisés. Les **18 autres segments AP20 sont identiques à R10** ; le loader ILBM, les dimensions, palettes, DB, Swap, clavier, fermeture et gestion du mode restent inchangés. **Le retour WinUAE sur R12 confirme que Jeff est désormais affichée à la bonne position**, ce qui renforce le diagnostic ABI A0 ; les autres formats et la compilation R12 ne sont pas encore validés.

**Binaire actif :** `dist/AMOSPro_AGA.Lib` = R12 0.6.3, **8856 octets**, SHA256 `b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec` ; archive `dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib`. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` RESTE R10 0.6.1** (SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`), tel que demandé explicitement. M4b historique et R11 rejetée restent archivés.

**Test unique :** `tests/current/R12_JEFF_A0_RETRY.asc`, bandeau `R12-JEFF-NEWSCREEN-A0-01` : d'abord Jeff-Flag 736×482, vérifier position directe en haut + retour AMOS ; si PASS, Fallout PAL avec le même test. Ce programme conserve l'ordre `Amos To Back` du test R10 qui chargeait les images.

**Tests :** contrôle HUNK/AP20, reproductibilité, ILBM et CPU Unicorn 68000 **PASS en CI** (run 42836826630 (archive CI privée)). Jeff-Flag **PASS utilisateur** sous WinUAE, sans nombre d'itérations précisé. **R12 compilée, Fallout sous R12 et matériel physique non confirmés.** `tools/verify_artifacts.py` a été adapté ; les anciens builders R9/R10/R11 n'écrasent plus la Lib active.

Voir `docs/R12_NEWSCREEN_A0.md` et `tests/README.md`. Même branche `codex/intuition-input-r1`, PR #4 Draft, **`main` inchangée**. Ne pas promouvoir R12 dans LAST_GOOD avant validation.

---

## Vérification en cours — ordre AMOS To Back / écran R10 (10/11/2026)

**La R10 active et LAST_GOOD restent intactes.** Un seul test diagnostique (`tests/current/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc`, bandeau `R10-JEFF-AMOS-BACK-ORDER-01`) déplace `Amos To Back` de l'après-Swap vers **avant `Aga Screen Open`**, avec restauration `Amos To Front` sur échec d'ouverture. Aucun autre changement de logique AGA.

Ce test vise le défaut de position de Jeff observé sur R10 ; le fonctionnement correct **n'est pas encore validé** avec cet ordre. Source AMOS `+W.s` : `TAMOSWb` rend la main au Copper/Workbench. Les Autodocs indiquent déjà `SA_Top=0` par défaut si `SA_Height` est explicite : ajout de tag `SA_Top=0` non justifié. **Ne pas recréer R11** ni modifier le loader. Voir `docs/R10_AMOS_BACK_ORDER.md`.

---

## ÉTAT ACTUEL : R10 restaurée, LAST_GOOD R10, R11 rejetée (10/11/2026)

**R11 0.6.2 REJETÉE sous WinUAE :** l'utilisateur obtient un écran gris au lieu de l'image Jeff. Le débogueur affiche PC `$00F81472`, instruction ROM `STOP #$2000` en mode superviseur. Ce relevé n'établit pas la cause exacte : il ne démontre ni gel CPU ni défaut du loader. La régression graphique par rapport à R10 est en revanche confirmée. La R11 reste conservée dans `dist/experimental/AMOSPro_AGA_M5_v0.6.2_JEFF_POSITION_R11.Lib` et le test de cet échec dans `tests/historical/R11_JEFF_SCREEN_POSITION.asc`.

**Retour à la version fonctionnelle R10 0.6.1** : `dist/AMOSPro_AGA.Lib` = l'archive `dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib`. Taille **8 852 octets**, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`. R10 ouvre et charge Jeff-Flag avec repli NTSC→PAL ; les fonctions DB, Swap, clavier et fermeture fonctionnent selon l'utilisateur. **Limite connue : écran Jeff placé trop bas, repositionnable à la souris.** R9 reste validée 4/4 sur Fallout interprété et en AMOS Compiler selon le retour utilisateur.

**Exception demandée explicitement par l'utilisateur :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` est également remplacé par la **copie binaire identique de R10**. Le LAST_GOOD historique M4b est déjà archivé sans perte à `archive/AMOSPro_AGA_M4b_v0.0.9_R6C_R1_WinUAE_OK.Lib` (même blob Git que l'ancien LAST_GOOD). **R10 est la dernière version M5 fonctionnelle connue, mais le défaut de positionnement et des gates non validés subsistent** : ne pas l'appeler un jalon parfaitement finalisé.

**Reprise :** analyser le cycle de vie de Screen/Window à partir de **R10**, sans modifier les fonctions IFF déjà validées et sans reproduire le helper R11 qui provoque l'écran gris. Aucun nouveau binaire ni test actif créé pour ce retour. `tools/verify_artifacts.py` et le builder historique R11 doivent respecter cette nouvelle référence.

Branche existante `codex/intuition-input-r1` ; PR #4 Draft, **main inchangée**, aucun merge.

---



## Checkpoint R9 0.6.0 — 4/4 PASS WinUAE interprété (10/11/2026)

**Candidat actif :** `dist/AMOSPro_AGA.Lib` = **R9 0.6.0**, 8 772 octets, SHA-256 `58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c`. Identique à `dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib`; R8 conservée dans `dist/experimental/`, `LAST_GOOD` inchangé.

**Runtime utilisateur :** le 10/11/2026, **4 exécutions successives sans problème** du programme identifié par le bandeau `R9-A3-REGRESSION-01`, avec `Fallout.iff` 640 × 512, 4 plans, compression ByteRun1. Capture : `OPEN=1`, `DB=1`, `LOAD=1`, `SWAP=1`, `KEY=68`, `CLOSE RETURNED`, puis boîte de dialogue AMOS `End of program at line 68`. **Gate B (ce scénario interprété) : PASS 4/4.** Ceci appuie la correction A3, sans démontrer la stabilité de tous les formats ou la qualité pixel à pixel.

**Archivage :** test exact `tests/passed/R9_PICINFO_A3_REGRESSION.asc` (SHA GitHub conservé), aucun `.asc` restant dans `tests/current/`. Le fichier n'a pas été retouché depuis le PASS.

**Restent ouverts :** Gate A — tests CPU Unicorn/CI R9 non confirmés ; Gate C — version compilée ; Gate D — vrai Amiga AGA ; Ctrl+C en cours de Swap et stress multi-IFF hors validation. **Ne pas merger la PR #4 (Draft)** et ne pas promouvoir `LAST_GOOD` avant les gates requis. Même branche `codex/intuition-input-r1`, sans nouvelle branche.

Les autres sections de ce document sont historiques lorsque leurs anciens statuts « candidat courant » ou « non testé » contredisent ce checkpoint. Voir `docs/PICINFO_A3_R9.md` et `tests/README.md`.


# Règles source — AMOSPro AGA Extension

## Checkpoint runtime R8 0.5.9 — 10/11/2026

### Rectification après capture `R8-FALLOUT-KEY-POLL-01`

Ce diagnostic affiche `IMAGE 640 X 512 PLANS 4` puis reste sans sortie visible. Comme il ne comporte aucun jalon après Open/DB/Load/Swap, **le point d'attente est inconnu**. Sa limite de 500 VBL couvre seulement la boucle `Aga Key` si celle-ci est atteinte ; elle ne prouve pas une erreur clavier. Test reclassé `tests/historical/` (NON VALIDÉ) et `tests/current/` sans `.asc`. **Faire un relevé WinUAE Shift+F12 / `r` / `d` avant toute nouvelle hypothèse ou Lib**. Voir `docs/NEXT_SESSION.md`.

### Ajout 10/11 : réception clavier après Swap

La capture `KEY 68 - CLOSE RETURNED` valide **une exécution** de la version originale de `M5_R8_ILBM_SINGLE_SWAP.asc` **avec `Aga Wait Key`**. Ce n'est pas une stabilité démontrée. Révision ancienne rétablie dans `tests/passed/`, sans être rejouée.

`Aga Wait Key` est un polling `GetMsg/WaitTOF` **non borné** lorsque la fenêtre ne reçoit pas de RAWKEY. Le focus Intuition peut être différé ; aucune cause précise établie sans observation. Un seul test courant `tests/current/R8_FALLOUT_KEY_POLL_SAFE.asc`, boucle `Aga Key` bornée à 500 VBL, doit distinguer réception de RAWKEY et absence d'événement. Aucune modification du code moteur ou de la Lib R8. Voir `docs/R8_INPUT_FOCUS_AUDIT.md`.

Branche unique `codex/intuition-input-r1`, PR #4 Draft. R8 0.5.9 non mergée ; `main` demeure sur Generic R2, `LAST_GOOD` reste protégé.

- R7 : Open/DB/Close sans Swap ni IFF, 5/5 PASS.
- R8 : Open/DB/un Swap/Close sans IFF, 5/5 PASS.
- R8 Fallout : Open/DB/IFF Load/Close **sans Swap**, PASS et retour à AMOS.
- `M5_R8_ILBM_SINGLE_SWAP.asc` : **PASS signalé par l'utilisateur**. La dernière version GitHub de ce test (désormais dans `tests/passed/`) exécute un Swap sans `Aga Wait Key`. Le nom ayant eu plusieurs contenus successifs, la révision locale de ce PASS n'est pas prouvée par capture. Ne pas prétendre valider Ctrl+C ou le parcours complet clavier.
- Corps réel `Amiga fallout.iff` vérifié : ByteRun1 640×512×4, 57 687 octets compressés, 163 840 octets décompressés sans erreur.

**Aucun nouveau test actif / aucune nouvelle Lib** à cet instant : `tests/current/` peut rester sans fichier `.asc`. Voir `tests/README.md`, `docs/NEXT_SESSION.md`.

---

## Référence antérieure — Generic R2 0.5.1

Checkpoint prioritaire : **Generic R2 0.5.1**, voir `docs/GENERIC_R2.md`.
R1 est rejeté après perte du dernier plan observée dans WinUAE ; R2 ajoute
WaitBlit avant les écritures CPU. Les tests CPU passent, le PASS visuel reste requis.
R5 demeure le repli runtime et LAST_GOOD reste inchangé.

## Checkpoint Generic ILBM R1 0.5.0

Le candidat expérimental courant est documenté dans `docs/GENERIC_ILBM.md`.
Il est construit exclusivement depuis R5 0.4.6 ; R5R1/R5R2 restent interdits comme base.
La validation CPU des 41 images ne vaut pas validation visuelle AMOS.
R5 est le repli runtime à conserver, LAST_GOOD reste M4b.
Les mentions de candidat courant plus bas décrivent l'historique préalable.

Ce fichier est la **porte d'entrée obligatoire** pour toute reprise du développement de `anthea176/AMOSPro-AGA-Extension`.

Il recense les règles de source, les contrats ABI, les pièges déjà rencontrés, les règles de build et de validation, ainsi que la procédure à suivre lorsqu'une nouvelle session reprend le projet.

Le comportement runtime déjà validé ne doit **jamais** être refactoré uniquement pour le style.

---

## 1. Ordre de lecture obligatoire à chaque reprise

Avant de modifier une ligne ou un octet :

1. lire `EXTENSION_SOURCE_RULES.md` ;
2. lire `docs/NEXT_SESSION.md` ;
3. lire `docs/M5_STATUS.md` ou le fichier STATUS du jalon courant ;
4. lire `docs/ROADMAP.md` ;
5. lire `docs/ARCHITECTURE.md` ;
6. lire le builder du candidat validé courant ;
7. vérifier le HEAD réel de `main` et les derniers commits ;
8. vérifier le SHA256 réel de `dist/AMOSPro_AGA.Lib` avant toute modification.

Ne jamais reprendre uniquement depuis la mémoire d'une ancienne discussion.

Si la documentation, le builder et le binaire semblent se contredire, **arrêter l'implémentation et résoudre d'abord la contradiction**.

---

## 2. Hiérarchie des sources d'autorité

Pour le comportement actuel du projet, l'ordre de confiance est :

1. **résultat runtime réellement validé** sous AMOS / WinUAE / matériel ;
2. **builder reproductible** ayant généré le binaire validé ;
3. **SHA256 + taille + audit AP20** du binaire validé, puis vérification `LAST_GOOD` = archive du dernier Gate B confirmé ;
4. `docs/NEXT_SESSION.md` et le STATUS du jalon courant ;
5. `docs/ARCHITECTURE.md` et `docs/ROADMAP.md` ;
6. anciens candidats, diagnostics et notes historiques.

Un commentaire ancien ne l'emporte jamais sur un test runtime plus récent.

### Binaire vs source

- Ne jamais modifier une `.Lib` à la main comme méthode de développement durable.
- Toute modification binaire doit être produite par un **builder reproductible** dans `tools/`.
- L'inspection/disassembly d'un binaire est autorisée pour comprendre ou vérifier un patch.
- Si un builder existe déjà pour le candidat courant, ne pas reconstruire sa logique depuis zéro sans raison.
- Ne jamais déduire une nouvelle convention ABI uniquement depuis quelques octets lorsque les sources AMOS365, les FD, les includes ou un builder validé donnent la réponse.

---

## 3. Politique des builds

### Fichiers

- `dist/AMOSPro_AGA.Lib` = **candidat courant**, nom exact, **directement dans `dist/`** après Gate A/CI PASS.
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` = **copie exacte de la dernière version ayant PASS Gate B confirmé par l'utilisateur**. Référence courante : R28 0.10.0, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`.
- `dist/experimental/` = **archives à nom versionné seulement**, y compris versions rejetées et R10 historique ; pas de copie supplémentaire nommée `AMOSPro_AGA.Lib` dans un sous-dossier.
- `archive/` = jalons clôturés.

### Règle critique

`dist/AMOSPro_AGA_LAST_GOOD.Lib` est **promu systématiquement après confirmation utilisateur Gate B PASS** : remplacer son contenu par les octets exacts du candidat validé, et archiver le test à l'identique. Ne pas le modifier après **Gate A seule** ou sur résultat non confirmé.

**Historique de création (caduc pour l'état courant) :**

- LAST_GOOD global **à la rédaction historique** = M4b R6C-R1 ; depuis le 10/11/2026 le LAST_GOOD actif est R10 0.6.1 (demande explicite) ;
- candidat M5 validé = M5-R3R1 0.3.1 ;
- SHA256 M5-R3R1 = `a1b24aa0f83be86858b2ba495e94259aac211208ff5a8b0d6825a3427a09cb2e`.

La distinction est volontaire.

### Candidat rejeté

Si un nouveau candidat échoue :

1. ne pas écraser l'archive du candidat rejeté ;
2. restaurer `dist/AMOSPro_AGA.Lib` depuis **le dernier candidat du jalon courant réellement validé**, pas automatiquement depuis le vieux LAST_GOOD global ;
3. noter précisément la cause du rejet dans le STATUS ou l'historique ;
4. repartir de la dernière base runtime validée.

---

## 4. ABI AMOS Professional 365

### R9 — règle critique A3 et fonctions à plusieurs paramètres

Les routines de paramètres d'AMOS `+ILib.s` (`Ent_2`, `Ent_3`...) empilent les `N-1` premiers arguments sur **A3** avant de transmettre le dernier par D3. L'extension doit **consommer ces arguments** et laisser A3 avancé à la sortie ; il est interdit de restaurer A3 à la valeur d'entrée si un `(A3)+` a retiré un paramètre. Les autres registres doivent rester conformes à l'ABI et la pile CPU SP équilibrée.

Défaut source vérifié R8 `Aga Pic Info` : `MOVEM` sauve puis restaure A3 après `MOVE.L (A3)+,D3`. Il peut laisser une valeur parasite sur la pile de contrôle AMOS et bloquer `LGoto` sur `ADD.W (A3),A3` avec `(A3)=0`. WinUAE a montré ce gel à PC `$4019CAB8`. Le **R9 expérimental**, qui exclut A3 des deux masques de MOVEM de PicInfo, laisse A3 avancer de 4 octets. Voir `docs/PICINFO_A3_R9.md`. Tester systématiquement ce contrat **sur CPU 68000 réel simulé**, puis WinUAE ; ne pas annoncer de validation runtime avant essai.

Cette couche est fondamentale. Ne jamais l'improviser.

### AP20 / extension

Le format utilisé par ce dépôt est un HUNK unique contenant une extension AP20.

Le chargeur comporte notamment :

- table des offsets / jump table ;
- table des tokens ;
- code bibliothèque ;
- titre / version ;
- fin de structure.

`tools/audit_ap20.py` est la référence de contrôle structurel du dépôt.

### Fonctions entières

Convention validée du projet :

- résultat entier dans **D3** ;
- **D2=0** avant retour pour le type entier ;
- préserver les registres ordinaires selon le patron déjà validé ;
- ne pas restaurer D3 après avoir préparé le résultat.

Piège déjà rencontré : un cleanup ou un restore mal placé peut écraser D3 juste avant le retour.

### Paramètres

Les entrées avec paramètres passent par le mécanisme `GetP`.

Règles :

- ne jamais inventer la convention d'un paramètre à partir de son type supposé ;
- reprendre les patrons déjà validés ;
- vérifier la signature token ;
- vérifier l'ordre réel des paramètres ;
- vérifier interpréteur **et compilateur**.

Pour les chaînes AMOS déjà utilisées par le loader :

- le pointeur AMOS contient la longueur puis les caractères ;
- convertir vers une chaîne C NUL-terminée avant les appels DOS ;
- toujours libérer le buffer temporaire.

### Tokens et noms de commandes

Le parseur AMOS peut avoir des ambiguïtés de préfixe.

Donc :

1. ne pas ajouter une commande de diagnostic juste pour afficher une valeur ;
2. préférer un test AMOS ou une instrumentation temporaire interne ;
3. vérifier la table de tokens avant de choisir un nouveau nom ;
4. éviter plusieurs nouvelles commandes partageant inutilement le même long préfixe ;
5. conserver une API compacte et stable.

Exemple de décision actuelle : une seule fonction `Aga Pic Info("image.iff",field)` est préférée à plusieurs commandes `Aga Pic Width`, `Aga Pic Height`, etc.

---

## 5. AP20 / HUNK : règles de patch binaire

Toute insertion dans une routine 68k peut casser des références PC-relatives.

### Après une insertion/suppression

Contrôler systématiquement :

- branches 16 bits ;
- DBcc ;
- LEA PC-relative ;
- offsets de jump table ;
- longueur du segment ;
- longueur totale du code ;
- sections AP20 paires ;
- taille HUNK ;
- padding final ;
- SHA256.

Le builder R2R4/R3R1 contient déjà des exemples de recalcul et de vérification des références.

### Interdictions

- ne pas insérer des octets dans une routine puis seulement corriger la taille globale ;
- ne pas supposer qu'un déplacement relatif reste valable ;
- ne pas modifier plusieurs segments runtime dans le même candidat sans justification ;
- ne pas masquer une divergence avec des NOP sans comprendre la fenêtre remplacée.

### Audit

Avant runtime :

```text
parse -> inspect -> issues == []
```

Le succès de l'audit signifie seulement que la structure AP20 est cohérente.

**Ce n'est pas une validation runtime.**

---

## 6. État runtime partagé : contrat actuel

L'état extension actuel est partagé entre les commandes.

Offsets actuellement utilisés :

| Offset | Contenu |
|---:|---|
| +0 | `Screen*` |
| +4 | `IntuitionBase` |
| +8 | `GfxBase` |
| +12 | largeur |
| +16 | hauteur |
| +20 | nombre de couleurs |
| +24 | ModeID |
| +28 | profondeur |
| +32 | `DBState*` |
| +36 | `Window*` (depuis Intuition Input R1) |

### DBState actuel

| Offset | Contenu |
|---:|---|
| +0 | ScreenBuffer original |
| +4 | ScreenBuffer alternatif |
| +8 | index front courant |
| +12 | Safe MsgPort |
| +16 | Disp MsgPort |
| +20 | réservé |

Toute extension de cette structure doit être :

- explicite ;
- documentée ;
- initialisée ;
- nettoyée ;
- compatible avec toutes les commandes qui la lisent.

Ne jamais créer un deuxième état parallèle caché dans une nouvelle commande.

---

## 7. Structures Amiga déjà utilisées

Ces offsets ont été utilisés et validés dans le projet courant. Les re-vérifier dans les includes AmigaOS avant toute refonte importante.

### BitMap

- +0 : BytesPerRow (WORD)
- +2 : Rows (WORD)
- +4 : Flags
- +5 : Depth
- +8 : Planes[0]
- +12 : Planes[1]
- ...
- +36 : Planes[7]

### ScreenBuffer

- +0 : `sb_BitMap`
- +4 : `sb_DBufInfo`

### Screen / ViewPort

- ViewPort commence à Screen +44 ;
- ViewPort.ColorMap = Screen +48 ;
- ViewPort.RasInfo = Screen +80.

### RasInfo

- +0 : Next
- +4 : BitMap
- +8 : RxOffset
- +10 : RyOffset

Ne pas recopier ces nombres dans une nouvelle routine sans vérifier qu'une structure déjà centralisée ne peut pas être réutilisée.

---

## 8. Écran AGA / Intuition

### Règles validées

- privilégier Intuition / graphics.library pour les écrans standards ;
- conserver le cycle Open -> Draw/Load -> Swap -> Close ;
- libérer dans l'ordre inverse des allocations ;
- éviter de reconfigurer brutalement un ViewPort déjà actif.

### SA_FullPalette

Pour l'écran indexed 8 plans validé, `Aga Screen Open` utilise :

`SA_FullPalette = TRUE`

Le correctif est appliqué **à l'ouverture de l'écran**.

Ne pas retirer ce tag lors d'une refonte du taglist.

### Approche rejetée

Une tentative de reconfiguration à chaud avec :

- `VideoControl` ;
- `MakeScreen` ;
- `RethinkDisplay`

depuis `Aga Iff Load` a provoqué un Software Failure `80000008`.

**Ne pas réintroduire cette approche.**

Si une reconfiguration de mode devient nécessaire, concevoir une ouverture/recréation d'écran propre au lieu de modifier à chaud le chemin déjà validé.

---

## 9. Règle obligatoire Amos To Front / Amos To Back

Piège déjà reproduit plusieurs fois.

Un test visuel incomplet peut faire croire à un bug de palette ou d'image alors que le mauvais écran est visible.

Patron de test validé :

```amos
_OK=Aga Screen Open(320,200,256,$00021000)
Amos To Front
Print "OPEN = ";_OK

If _OK<>0
   _DB=Aga Double Buffer
   If _DB<>0
      _IFF=Aga Iff Load("DH6:Clown.iff")
      If _IFF<>0
         _SW=Aga Swap
         If _SW<>0
            Amos To Back
            For _I=1 To 200
               Aga Wait Vbl
            Next _I
            Amos To Front
         End If
      End If
   End If
   Aga Screen Close
End If
```

Règle :

**ne jamais conclure à un bug palette/bitplane avant d'avoir vérifié cette séquence.**

---

## 10. Double buffering et sécurité runtime

AMOS traite son interruption utilisateur dans l'interpréteur. Une extension bloquée empêche AMOS de reprendre la main.

### Interdit dans les commandes runtime exposées à AMOS

- Exec `WaitPort()` ;
- Exec `Wait()` ;
- retry infini sur `ChangeScreenBuffer()` ;
- boucle dont la sortie dépend uniquement d'un message externe ;
- attente non bornée.

### Autorisé

- `GetMsg()` pour polling non bloquant ;
- petit budget explicite de `WaitTOF()` ;
- compteur maximal d'essais ;
- retour d'échec/pending à AMOS lorsque le budget est dépassé.

### Séquence de validation buffer

Toujours valider dans cet ordre :

1. Open/Close ;
2. allocation Double Buffer ;
3. **un seul Swap** ;
4. quelques Swaps ;
5. stress test.

Ne jamais commencer par 100 swaps sur un candidat non validé.

---

## 11. IFF / ILBM : architecture obligatoire

Le code IFF doit évoluer vers quatre responsabilités distinctes :

1. **Inspect**
   - FORM/ILBM ;
   - BMHD ;
   - CMAP ;
   - CAMG ;
   - métadonnées seulement.

2. **Validate**
   - dimensions ;
   - profondeur ;
   - compression ;
   - rowBytes ;
   - longueurs ;
   - compatibilité écran.

3. **Decode**
   - BODY brut ;
   - ByteRun1 ;
   - bornes strictes.

4. **Apply**
   - palette ;
   - plans ;
   - nettoyage des plans inutilisés ;
   - synchronisation affichage.

Ne pas reconstruire un nouveau loader monolithique.

---

## 12. IFF : pièges déjà rencontrés

### 12.1 Ne jamais hardcoder les offsets d'un fichier

Le candidat R2R1 utilisait temporairement des offsets propres à `Clown.iff` pour isoler le problème :

- CMAP payload +48 ;
- BODY payload +836.

C'était un diagnostic, pas une architecture.

Le loader durable doit scanner les chunks.

### 12.2 Chunk payload

Ancien bug du scanner R2 :

le code vérifiait les champs BMHD via A6 sans avoir d'abord positionné A6 sur le payload du chunk.

Patron correct :

```text
chunk header -> payload = chunk + 8
```

Toujours distinguer :

- adresse header ;
- taille chunk ;
- adresse payload.

### 12.3 Padding IFF

Un chunk impair est suivi d'un octet de padding.

Avancement :

```text
next = data + size + (size & 1)
```

Ne pas inclure le padding dans la taille logique du chunk.

### 12.4 RowBytes

Formule ILBM :

```text
rowBytes = ((width + 15) / 16) * 2
```

Ne pas utiliser `width/8` pour des largeurs générales.

### 12.5 Ordre BODY

ILBM BODY :

- ligne ;
- plan ;
- données de la ligne du plan.

Ne pas convertir en chunky implicitement.

### 12.6 ByteRun1

Décodage :

- 0..127 -> copier n+1 octets ;
- 129..255 -> répéter l'octet suivant 257-n fois ;
- 128 -> NOP.

Piège réel déjà corrigé :

après extension signée du contrôle négatif, utiliser la largeur correcte du compteur.

Le bug R2 utilisait `NEG.W D0` alors que le compteur était traité en long.

Correctif validé : `NEG.L D0`.

Ne pas réintroduire ce bug.

### 12.7 Bornes

Le décodeur doit être borné simultanément par :

- longueur BODY ;
- hauteur ;
- nombre de plans ;
- rowBytes destination.

Une ligne doit produire exactement rowBytes octets pour le plan courant.

### 12.8 Masque

Le chemin actuellement validé utilise `masking=0`.

Ne pas prétendre supporter un mask plane avant d'avoir explicitement ajouté sa consommation dans BODY.

---

## 13. Palette AGA

### CMAP

CMAP est une suite de triplets RGB 8 bits.

Ne pas supposer 256 couleurs.

Le nombre de couleurs vient de :

```text
CMAP_size / 3
```

avec validation de taille et limite.

### SetRGB32

Le chemin validé utilise graphics.library / `SetRGB32`.

Conserver la convention 32 bits attendue par l'API.

### Synchronisation

R3R1 ajoute un `WaitTOF` après la boucle de chargement palette afin de rendre le passage palette/copper déterministe.

Ne pas retirer cette synchronisation sans test comparatif.

### Diagnostic palette

Avant de modifier la palette, se rappeler que les diagnostics précédents ont déjà démontré sur Clown :

- BODY exact ;
- les 8 plans exacts ;
- ordre des plans affichés 0->0 ... 7->7 ;
- ColorMap logique exacte ;
- PAL LORES ;
- absence de HAM/EHB/DUALPF.

Ne pas refaire ces diagnostics sans nouvelle preuve qu'ils sont nécessaires.

---

## 14. Modes vidéo / CAMG

**R9 / Jeff (10/11/2026) :** un `Aga Screen Open=0` indique un refus lors de la création de Screen ou Window, **pas** une erreur `Aga Iff Load` si celui-ci n'a pas été appelé. Ne pas supposer que toute géométrie dépassant l'overscan visible est interdite : `SA_AutoScroll` est déjà utilisé. Le ModeID `$00019004` est NTSC HiRes Lace ; ses disponibilités doivent être vérifiées via AmigaOS (`ModeNotAvailable` / `SA_ErrorCode`), avant toute conversion de mode. Aucun recadrage silencieux ni modification du loader déjà validé. Détails : `docs/R9_JEFF_MODES.md`.


Ne pas traiter tous les fichiers comme de simples variantes du nombre de couleurs.

À terme :

- indexed LowRes ;
- HiRes ;
- interlace ;
- EHB ;
- HAM6 ;
- HAM8 ;
- overscan.

EHB et HAM ont une sémantique propre.

Ne pas les activer implicitement à partir de la profondeur seule.

Le ModeID / CAMG doit être validé et traduit vers une configuration AmigaOS/AGA cohérente.

---

## 15. Commande Aga Pic Info

API prévue :

```amos
_V=Aga Pic Info("DH6:Image.iff",field)
```

Champs prévus :

- 0 largeur ;
- 1 hauteur ;
- 2 bitplanes ;
- 3 nombre de couleurs CMAP ;
- 4 compression ;
- 5 CAMG / ModeID ;
- -1 erreur.

Règles :

- ne pas ouvrir d'écran ;
- ne pas décoder BODY ;
- scanner seulement les métadonnées utiles ;
- ne pas dupliquer le parser IFF du loader : factoriser conceptuellement la même logique ;
- tester plusieurs fichiers de formats différents ;
- valider interprété puis compilé.

---

## 16. AMOS : syntaxe des tests

Dans les `.asc` du dépôt :

- utiliser les blocs `If ... End If` ;
- ne pas ajouter `Then` dans un bloc structuré ;
- garder les tests simples ;
- éviter les syntaxes AMOS non vérifiées ;
- ne pas inventer une commande pour un diagnostic ponctuel.

Préférer :

```amos
If _OK<>0
   ...
End If
```

Les tests doivent rester lisibles dans AMOS Professional 365.

---

## 17. Diagnostics : politique stricte

Les diagnostics sont un moyen, pas un produit.

Avant d'ajouter un diagnostic, demander :

1. avons-nous déjà une mesure qui exclut cette hypothèse ?
2. pouvons-nous corriger directement le bug ?
3. pouvons-nous observer la valeur depuis un test existant ?
4. faut-il réellement ajouter un token AMOS ?

### Ne pas répéter sans raison

Les diagnostics historiques ont déjà validé pour Clown :

- sommes des 8 plans ;
- hash ordonné des 8 plans ;
- hash palette ;
- flags ViewPort / DisplayID ;
- mapping des plans affichés ;
- chaîne DOS / FORM / ILBM.

Ces tests restent dans `tests/historical/`.

Ne pas reconstruire une série D12/D13/D14 simplement parce qu'une nouvelle session ne les a pas en mémoire.

---

## 18. Tests et répertoires

- `tests/current/` = **zéro ou un test `.asc` réellement à exécuter**, jamais plusieurs fichiers concurrents ; il peut être vide lorsque le dernier essai a passé et que la suite n'est pas définie.
- `tests/passed/` = validations runtime observées, avec portée et réserves écrites.
- `tests/historical/` = diagnostics périmés, variantes remplacées ou rejetées.

Lorsqu'un test est confirmé : le classer, actualiser `tests/README.md`, `docs/M5_STATUS.md` et `docs/NEXT_SESSION.md`, puis retirer les copies redondantes de `current/`. Ne pas confondre un PASS signalé pour un **nom** avec la certification d'une **révision exacte** si plusieurs contenus ont partagé ce nom.

Chaque nouvel essai doit avoir un nom `.asc` et un bandeau `Print` uniques. GitHub ne synchronise pas automatiquement le disque virtuel WinUAE. Ne pas conclure qu'une capture correspond à une version sans avoir vérifié son bandeau.

---

## 19. Portes de validation d'un candidat

Un candidat n'est pas "validé" parce que le builder s'exécute.

### Gate A — statique

- builder reproductible ;
- AP20 valide ;
- jump table valide ;
- tokens valides ;
- aucune référence relative cassée ;
- aucun Wait/WaitPort interdit ;
- taille et SHA connus.

### Gate B — AMOS interprété

- extension charge ;
- syntaxe reconnue ;
- retour correct ;
- fonction cible correcte ;
- cleanup correct ;
- aucun freeze.

### Gate C — AMOS compilé

Le même scénario doit être testé avec AMOS Compiler.

Ne jamais supposer qu'une commande interprétée valide automatiquement l'ABI compilée.

### Gate D — matériel

Pour les fonctions sensibles :

- WinUAE pertinent ;
- vrai AGA quand disponible.

Alice68 est une référence supplémentaire, pas une preuve finale.

---

## 20. Changements isolés

Après validation runtime d'un bloc, le conserver octet pour octet si ce bloc n'est pas la cible du candidat suivant.

Exemples :

- si le candidat vise IFF, ne pas modifier Swap ;
- si le candidat vise Swap, ne pas modifier Close ;
- si le candidat vise palette, ne pas refondre Open en même temps ;
- si le candidat vise un token, ne pas changer trois routines runtime.

Une correction = un delta compréhensible.

---

## 21. GitHub et travail collaboratif

Le développeur peut pousser lui-même un commit entre deux réponses.

Donc avant toute écriture :

1. relire le HEAD de `main` ;
2. vérifier si les fichiers ciblés ont changé ;
3. ne jamais écraser silencieusement un commit utilisateur récent ;
4. créer le commit avec le parent HEAD courant ;
5. utiliser une mise à jour de ref conditionnelle quand possible.

### Documentation

Éviter les remplacements regex larges dans README ou STATUS.

Un remplacement trop permissif a déjà produit une duplication/corruption du README.

Pour une mise à jour documentaire :

- relire le fichier complet ;
- modifier une section clairement identifiée ;
- vérifier le résultat complet avant commit.

### Règle permanente — README public sans historique en introduction

Le `README.md` est un **manuel d'utilisation de la version courante**, pas un journal de développement.

- **Structure obligatoire :** le fichier commence par `# AMOSPro AGA Extension`, une ligne vide et directement `## Bibliothèques et tests`. Aucun bilan Rxx/Mx, chronique, ancienne release ou sous-section entre ces deux titres.
- À chaque release, **mettre à jour sur place** la bibliothèque active, les tests, les commandes et les exemples. **Ne jamais empiler une nouvelle annonce de version en tête du README.**
- Les changements historiques, résultats détaillés de CI/WinUAE, incidents et archives sont maintenus dans `docs/`, `tests/passed/` ou `tests/historical/` ; des liens depuis le README suffisent.
- **Garde-fou CI :** `tools/test_readme_api_coverage.py` doit refuser toute introduction autre que le titre, tout en vérifiant les tokens AP20.
- Relire le README complet pour détecter doublons et statuts périmés. Aucune intervention sur les binaires ou `LAST_GOOD` n'est autorisée par ce nettoyage.

### Règle permanente — DEUX README à CHAQUE instruction ET validation (11/11/2026)

Cette règle complète la documentation de l'API et la promotion de LAST_GOOD. **Elle s'applique à `README.md` (anglais) ET `README.fr.md` (français), sans exception.**

1. **À chaque nouvelle instruction/fonction ou changement d'API :** mettre à jour **les deux README dans le même commit** que la candidate Gate A ; renseigner token AP20 exact, syntaxe AMOS, type/ordre des paramètres, retour et erreurs, limites, exemples, version et **Gates effectivement obtenues**. Ne jamais présenter comme implémentée une fonction encore à l'étude.
2. **À chaque validation (ou échec) :** mettre à jour **les deux README dès le résultat**, en précisant le test exact, la Gate A CPU/CI, B AMOS/WinUAE, C Compiler ou D Amiga physique (selon le cas), PASS/FAIL, les limites et les liens des preuves. Aucun succès simulé ne vaut validation WinUAE.
3. **Après Gate B PASS utilisateur :** mise à jour **dans le même commit** que la copie binaire identique vers `dist/AMOSPro_AGA_LAST_GOOD.Lib`, le test original archivé sans modification dans `tests/passed/`, les empreintes/CI et `docs/NEXT_SESSION.md`. En cas d'échec, ne pas promouvoir LAST_GOOD et consigner le défaut.
4. **Cohérence bloquante :** les deux tableaux publics doivent correspondre aux **mêmes tokens AP20**, signatures, retours, version, taille, SHA256 et statuts. Exécuter `tools/test_readme_api_coverage.py`, relire les deux README complets et vérifier les liens avant livraison ; une divergence bloque le jalon.
5. **Rester un manuel utilisateur :** éditer les sections existantes sur place, **sans empiler un journal des versions en tête**. L'historique détaillé appartient à `docs/` et `tests/passed/`.

### Règle permanente — documentation de toute nouvelle instruction AMOS

**Obligation lors de chaque nouvelle commande/fonction/token exporté par l'extension AP20 : mettre à jour `README.md` ET `README.fr.md` dans le MÊME commit que l'implémentation.** Une note isolée dans `docs/`, un devlog ou une annonce de version ne suffit pas. L'API publique doit être immédiatement visible dans `README.md → Commandes AMOS principales`.

Pour chaque commande ajoutée ou modifiée :

1. **Compléter le tableau principal** avec son nom exact tel qu'exposé par les tokens AP20, sa première version, la syntaxe AMOS (instruction **ou** fonction entière) et le **type, l'ordre et l'unité de chaque paramètre**.
2. Décrire **le retour et les valeurs d'erreur/sentinelles**, les limites (écran fermé, focus, support AmigaOS), les effets secondaires et les règles d'utilisation ; ne pas inventer un comportement non testé.
3. Ajouter dans le README **au moins un exemple AMOS correct**, incluant une affectation pour les fonctions entières et les contrôles de résultat pertinents. Distinguer explicitement une fonction réellement exportée d'un calcul réalisé dans le programme de test.
4. Mettre à jour **la version courante** et le statut de validation (CPU/CI, AMOS interprété/WinUAE, Compiler, matériel réel), avec les liens vers test et documentation ; conserver séparément les limites non validées.
5. **Contrôle bloquant CI :** `tools/test_readme_api_coverage.py` compare les tokens nommés du fichier `dist/AMOSPro_AGA.Lib` à la table du README et contrôle la version courante. Si le README omet une commande, mentionne une commande absente du binaire ou annonce une mauvaise version, le jalon **ne doit pas être accepté**.
6. **Avant de déclarer une nouvelle version prête :** relire le README complet, vérifier le rendu Markdown du tableau, le script de concordance et l'absence d'informations obsolètes dans les rubriques actives.

Cette règle s'applique **à toutes les futures releases**, même si le changement est uniquement une nouvelle fonction souris, Copper, Blitter, une instruction sans paramètre ou une modification des valeurs de retour. Elle ne justifie **aucune** modification des archives validées ni de `LAST_GOOD`.

---

## 22. Versioning et reproductibilité

Chaque candidat binaire doit avoir :

- nom de jalon ;
- version ;
- builder ;
- taille ;
- SHA256 ;
- base de construction ;
- delta documenté.

Le titre interne et le `$VER:` doivent correspondre au candidat.

Ne pas changer de version sans raison, mais ne pas publier deux binaires différents sous la même identité.

---

## 23. Références externes

Ordre recommandé :

1. sources AMOS Professional 365 pour l'ABI extension ;
2. FD / includes / autodocs AmigaOS pour les appels système ;
3. documentation matérielle AGA ;
4. WinUAE pour observation/validation ;
5. Alice68 / AGA-PiStorm pour comparaison comportementale.

### Alice68 / AGA-PiStorm

Utilisable comme référence pour :

- bitplanes 1..8 ;
- palette AGA ;
- BPLCONx ;
- FMODE ;
- DDF/DIW ;
- Copper ;
- sprites ;
- EHB/HAM ;
- logique Blitter.

Ne pas utiliser Alice68 comme référence de performance/timing Blitter.

Le coeur étudié est GPL-2.0-only alors que ce dépôt est MIT.

**Ne jamais copier directement du code GPL dans l'extension.**

---

## 24. Ce qu'il ne faut plus faire

Liste noire issue des erreurs déjà rencontrées :

1. oublier `Amos To Front / Amos To Back` puis diagnostiquer une fausse corruption de palette ;
2. réintroduire `VideoControl + MakeScreen + RethinkDisplay` à chaud dans le loader ;
3. bloquer AMOS avec `WaitPort` ou `Wait` ;
4. hardcoder les offsets CMAP/BODY d'un fixture dans un loader durable ;
5. refaire le bug ByteRun1 `NEG.W` ;
6. lire BMHD depuis le mauvais pointeur de chunk ;
7. inventer de nouveaux noms de commandes diagnostiques sans vérifier le parseur ;
8. modifier plusieurs routines validées pour un seul bug ;
9. considérer un audit AP20 comme une validation runtime ;
10. considérer WinUAE interprété comme preuve du compilateur ;
11. écraser LAST_GOOD avant clôture du jalon ;
12. repartir d'un binaire rejeté simplement parce qu'il est le plus récent ;
13. ignorer un commit utilisateur récent sur `main` ;
14. faire une grosse substitution automatique dans README sans vérifier le résultat ;
15. recopier du code GPL Alice68/AGA-PiStorm dans le dépôt MIT.

---

## 25. Procédure obligatoire de reprise d'une nouvelle session

### Étape 1 — état du dépôt

Relever :

- branche ;
- HEAD ;
- dernier commit ;
- fichiers modifiés récemment.

### Étape 2 — checkpoint

Lire :

- `EXTENSION_SOURCE_RULES.md` ;
- `docs/NEXT_SESSION.md` ;
- STATUS courant ;
- ROADMAP ;
- ARCHITECTURE.

Identifier :

- dernier candidat runtime validé ;
- SHA256 ;
- test passé ;
- prochain objectif exact.

### Étape 3 — builder

Lire le builder du candidat validé et ses parents directs.

Vérifier :

- base binaire ;
- segments touchés ;
- assertions ;
- SHA attendu.

### Étape 4 — test de non-régression

Avant une grosse évolution, conserver un test minimal du comportement déjà validé.

### Étape 5 — nouveau delta

Modifier une seule couche.

Créer :

- builder versionné ;
- candidat `dist/experimental/` ;
- mise à jour `dist/AMOSPro_AGA.Lib` ;
- un test principal `tests/current/`.

### Étape 6 — ne pas sur-diagnostiquer

Si le test échoue :

- comparer au delta réel ;
- utiliser les preuves historiques ;
- corriger directement quand la cause est claire ;
- n'ajouter un diagnostic que si une hypothèse reste réellement indéterminée.

### Étape 7 — validation

Passer les gates dans l'ordre :

1. statique ;
2. interprété ;
3. compilé ;
4. matériel si nécessaire.

### Étape 8 — clôture

Après PASS :

- archiver le candidat ;
- déplacer le test vers `tests/passed/` ;
- mettre à jour STATUS ;
- mettre à jour NEXT_SESSION ;
- mettre à jour ROADMAP si un sous-jalon est clôturé ;
- **promouvoir immédiatement `dist/AMOSPro_AGA_LAST_GOOD.Lib`** en copie byte-identique de la version testée après **Gate B PASS utilisateur**, indépendamment des futurs sous-jalons non commencés ; sinon le laisser intact ;
- vérifier que `dist/AMOSPro_AGA.Lib` reste le candidat courant à nom exact et qu'aucun sous-répertoire parasite `dist/.../AMOSPro_AGA.Lib` n'a été ajouté.

---

## 26. Checkpoint courant

État de référence après validation M5.2 :

- projet : `anthea176/AMOSPro-AGA-Extension` ;
- base de référence : **M5.2 R4 0.4.5** ;
- SHA256 : `b09a94bd4e1ce1487e2776c39e1dd3f75752dcf6f472261af178f47b584b2178` ;
- support confirmé : 8 plans/256 couleurs et 5 plans/32 couleurs ByteRun1 ;
- KEKKO 4 plans/16 couleurs : BODY validé par sommes P0..P3, palette encore incorrecte sous R4 ;
- candidat courant : **M5.2 R5 0.4.6**, correctif palette basse profondeur par LoadRGB32 ;
- PicInfo 0.3.2 : PASS interprété ;
- M5.3 RAW reste suspendu tant que R5 n'est pas validé ;
- M5.4 : HiRes / 640+ ;
- M5.5 : EHB / HAM.

**Historique :** règle remplacée exceptionnellement par la demande du 10/11/2026 ; LAST_GOOD = R10 0.6.1, M4b conservé dans `archive/`. R10 n'est pas réputée sans défaut (position Jeff).

---

## 27. Principe final

**Ne pas casser ce qui marche pour aller plus vite.**

On vérifie d'abord le contrat AMOS, le format, les offsets et le comportement validé ; ensuite seulement on modifie le builder.

Une hypothèse non vérifiée ne doit jamais devenir la base d'une série de correctifs.


## 27. Règle de sécurité IFF / écran

Avant toute écriture palette ou BODY, `Aga Iff Load` doit vérifier que le BMHD est compatible avec l'écran AGA courant.

Au minimum :

- largeur ;
- hauteur ;
- profondeur ;
- masking supporté ;
- compression supportée.

En cas d'incompatibilité : retour `0`, aucune écriture palette/BODY, aucun crash. Un mauvais écran AMOS ne doit jamais provoquer de Guru.


## 28. Transparence des helpers internes

Un helper ajouté autour d'un bloc runtime validé doit préserver tous les registres que le bloc d'origine ne modifiait pas, sauf contrat explicite documenté.

Pour les gardes/validateurs appelés depuis Aga Iff Load :

- préserver les registres de travail du loader ;
- préférer un résultat via CCR/flag ou registre explicitement sacrifiable ;
- vérifier la non-régression registre par registre avant publication.

La régression R5R1 (D0 clobberé) est le cas de référence à ne pas reproduire.


## 29. Point de repli M5.2

Après régression des variantes R5R1/R5R2, le seul candidat courant autorisé est **M5.2 R5 0.4.6**.

Ne pas réutiliser R5R1/R5R2 comme base.

Toute future sécurité mismatch doit être conçue depuis R5 0.4.6 et prouver sa transparence sur le chemin valide avant remplacement de `dist/AMOSPro_AGA.Lib`.

### Règle de non-régression Intuition

Ne jamais placer la fermeture de la Window dans le bloc conditionnel de Double Buffer. Tester le segment **public** Aga Screen Close, avec DBState NULL et non NULL, puis l'ordre exact CloseWindow avant CloseScreen. Un test du helper isolé ne suffit pas.

## Intuition Input R3 — correction CloseScreen (0.5.4)

R1 et R2 ont un défaut runtime confirmé : le BSR vers CloseWindow remplaçait
CLR.L DBState* dans un chemin sauté lorsque DBState*=0. CloseScreen recevait
alors un Screen qui possédait encore sa Window Intuition.

R3 accroche la fermeture au MOVEA.L DBState*(A2),A4 d'entrée, avant le test
conditionnel du DBState. Le helper vide/repond aux messages IDCMP, ferme
la Window, recharge A4, puis laisse le code original libérer le Double Buffer,
le Screen et les bibliothèques. Même correction dans le cleanup d'extension.

Le test Unicorn exécute le segment public Aga Screen Close complet avec
DBState nul/non nul et reproduit explicitement le défaut R2.

Candidat courant : dist/AMOSPro_AGA.Lib (identique à l'archive
dist/experimental/AMOSPro_AGA_M5_v0.5.4_INTUITION_INPUT_R3.Lib).
SHA256 : feb012b30b1adf89b3e0609e19e9a8e475be6fcd375b355c69f0d69b2d37a884.
Validation : 26 tests CPU PASS ; comportement AMOS/WinUAE encore à valider.
Ne pas merger sur main sans ce test runtime.


## Règle Ctrl + Aga Wait Key (R4)

Ne pas traiter le RAWKEY Ctrl seul (`$63`, 99) comme une touche
acceptée par `Aga Wait Key`. Consommer/répondre au message, puis
continuer à attendre par polling coopératif. Ne pas modifier le contrat
brut de `Aga Key` qui conserve le code 99. Détecter Ctrl+C via la
combinaison C (`$33`) + `IEQUALIFIER_CONTROL`, sans état Ctrl privé.
Tester explicitement Ctrl seul, Ctrl relâché puis C, et Ctrl maintenu
puis C dans le vrai segment AP20, sans changer l'ordre de fermeture R3.

## Règle supplémentaire — Ctrl+C Intuition doit réellement exécuter le Break AMOS

La R4 a prouvé qu'un test CPU vérifiant uniquement la pose du
bit `BitControl` n'est **pas** une validation de l'interruption.

AMOS Professional effectue le Break dans `Test_Force`, appelé
notamment par `Test_Normal` / `Test_PaSaut`. Lorsqu'une extension
consomme elle-même les messages RAWKEY, elle doit laisser le
moteur AMOS **exécuter son contrôle natif**, et pas seulement
positionner un drapeau en retournant C.

L'appel AP20 `Rjsr L_Test_PaSaut` (#140) doit intervenir après
cleanup et restauration du contexte de registres. `Break On/Off`
est géré par AMOS. Le test ne doit être déclaré PASS qu'après
interruption effective, fermeture Screen et retour éditeur sans Guru.

Ne jamais changer ou réutiliser la Lib R4 sous le même nom pour
ce correctif ; R5 0.5.6 est versionnée séparément et ne touche
aucun segment loader/PicInfo ni Screen Close.
[Diagnostic source](docs/INTUITION_CTRL_C_R5.md).

## Ctrl+C Intuition — restauration visuelle obligatoire avant le Break

Le R5 interrompt bien AMOS en runtime, mais comme `Amos To Back`
avait basculé l'affichage, Workbench restait au premier plan.

**Ordre impératif du chemin Ctrl+C :**
`ReplyMsg -> cleanup Window/DB/Screen -> Amos To Front ->
restore ABI -> Break natif AMOS`.

Utiliser uniquement le mécanisme officiel `EcCalD AMOS_WB,1`
(`T_EcVect=-8(a5)`, `AMOS_WB=72`, sources `+WEqu.s/+Equ.s/+W.s`).
Ne jamais revenir à la copie maison d'une gestion de Copper,
ni forcer un retour de programme après le Break.

Conserver les segments 0–16 et le chemin de fermeture R3 à l'identique ;
tester le rendu éditeur et la mémoire en plus de l'interruption.
Documenter séparément les tests CPU et les tests WinUAE, sans PASS
anticipé. [Détails R6](docs/INTUITION_CTRL_C_R6.md).

## Règle de sécurité — libération des ScreenBuffers / ports après Swap

Un `ChangeScreenBuffer()` réussi n'est **pas synchrone**. `WaitBlit()` seul n'autorise **pas** la destruction des `ScreenBuffer` ni des `MsgPort` Safe/Disp. Le code doit conserver un état explicite des notifications `dbi_SafeMessage` et `dbi_DispMessage` attendues, et garantir qu'elles ont été récupérées avant `FreeScreenBuffer` et `DeletePort`, dans **tous** les chemins (Aga Screen Close, cleanup extension, Ctrl+C, échecs partiels). Ne pas effacer silencieusement l'état in-flight lors d'un Swap ultérieur. Utiliser `GetMsg()` avec attente coopérative `WaitTOF` quand nécessaire ; pas de `WaitPort()` ni Exec `Wait()`.

Cette règle provient du défaut observé dans `build_m4b_r6b_r4.py` : l'ancien indicateur `DBState+20` de R6B-R1 a été perdu et le cleanup R4 supprime les ports trop tôt. Exiger des tests CPU d'ack Safe/Disp immédiats et différés, appel répété et erreur/timeout, ainsi qu'une validation WinUAE multi-ouverture. Voir `docs/M5_DB_SWAP_CLOSE_INCIDENT.md`. **Pas de PASS sur la base de `WaitBlit` seul.**

## Règle 68000 — contrôle des pointeurs de structures avant tout accès

L'erreur M4b R6B-R1 a produit `2068 4A80` et entraîné
un `MOVEA.L $4A80(A0),A0` au lieu de `MOVEA.L 4(A0),A0`
suivi de `MOVE.L A0,D0 / TST.L D0`. **Une simple recherche
d'opcodes et des tests de structure AP20 ne suffisent pas** :
le code doit être désassemblé ou exécuté sur CPU 68000 simulé
avec des pointeurs plausibles et vérification des écritures.

Pour `ScreenBuffer` (NDK) : `sb_DBufInfo=+4`. Pour `DBufInfo`,
`dbi_SafeMessage.mn_ReplyPort=+22`, `dbi_DispMessage.mn_ReplyPort=+54`.
Tester les deux ScreenBuffers, les échecs partiels et les registres ABI.

Lors de toute réparation d'un segment :
- le réassembler depuis les labels (ne pas conserver de déplacements
  PC-relatifs invalides) ;
- prouver que tous les autres segments sont byte-for-byte identiques ;
- ne jamais annoncer un PASS CPU ou runtime sans exécution réelle ;
- préserver les versions antérieures et les maintenir non mergées
  tant que la validation n'est pas explicite.

[Dossier de régression](docs/DB_POINTER_R7.md).



## Gestion des branches — chantier AMOS AGA

Pour les correctifs successifs de ce chantier, utiliser uniquement la branche active `codex/intuition-input-r1`. Ne pas créer une branche ou une Pull Request supplémentaire pour chaque version Rn : effectuer un nouveau commit et conserver les binaires versionnés sous `dist/experimental/`. La PR de suivi reste la #4, en Draft tant que la validation runtime n'est pas explicite. Ne jamais merger sur `main` sans cette validation. Une branche temporaire déjà intégrée doit être clôturée et supprimée lorsque les outils d'administration le permettent.


### Notifications de Double Buffer : messages *déjà répondus*

Les réponses `DBufInfo.dbi_SafeMessage` et `dbi_DispMessage` sont reçues avec `GetMsg` sur les ports Safe/Disp. **Ne jamais appeler `ReplyMsg()` sur ces réponses** : le système vient précisément de les retourner. C'est différent du port IDCMP de la Window, pour lequel `ReplyMsg` est requis.

Avant `FreeScreenBuffer` et `DeletePort`, attendre coopérativement (GetMsg + WaitTOF si nécessaire) la fin des notifications **en vol** après `ChangeScreenBuffer`, sans `WaitPort` ni Exec `Wait`. `WaitBlit` ne suffit pas. Voir `docs/M5_DB_SWAP_SYNC_DESIGN.md` et les autodocs `AllocDBufInfo`.

---

## 31. Organisation obligatoire de `tools/`

La racine de `tools/` doit rester courte et opérationnelle.

Y conserver uniquement :

1. le builder du candidat courant ;
2. ses générateurs/helpers réellement importés ;
3. les tests exécutés par la CI courante ;
4. les outils génériques de validation/audit ;
5. aucun ancien builder uniquement conservé pour l'historique.

Tout builder, diagnostic ou test Python versionné remplacé doit être déplacé dans :

`tools/obsolete/`

Règles :

- ne pas supprimer un outil historique uniquement parce qu'il est remplacé ;
- ne pas laisser plusieurs générations `R1/R2/R3/.../D1/D2...` actives à la racine ;
- ne jamais importer un script de `tools/obsolete/` depuis un builder courant ;
- la CI normale ne doit rien exécuter sous `tools/obsolete/` ;
- un nouveau chantier part toujours des outils actifs listés dans `tools/README.md` ;
- si un ancien script doit être reproduit, le traiter explicitement comme historique ;
- après chaque promotion majeure, refaire ce tri et mettre à jour `tools/README.md`.

Au checkpoint **M5 R12**, la liste précise des scripts actifs est tenue dans `tools/README.md`. Seuls les scripts nécessaires à R12, à ses tests CPU et aux contrôles génériques sont conservés à la racine. Le rangement effectué sur `main` a été intégré sans modifier les archives M4b et les candidats précédents.

