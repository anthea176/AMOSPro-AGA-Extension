# Reprise actuelle — AMOSPro AGA Extension

## R30 M13 — structure AGAPAL approuvée (11/11/2026, conception uniquement)

**Accord utilisateur sur l'architecture, sans nouveau token ni binaire R30 :** banque `DATA` native AMOS, enregistrable et rechargeable avec les commandes de banque AMOS dans un fichier **ABK standard**, contenant **plusieurs palettes AGA RGB24**. L'extension gérera un format intérieur `AGAPAL`, distinct du conteneur externe ABK que gère AMOS. Préférer la **Fast RAM** si le système de banques AMOS le permet : vérifier le comportement réel avant de promettre une zone mémoire.

**Organisation acceptée :** en-tête intérieur de **16 octets** (signature ASCII `AGAPAL` sur 6 octets, version, nombre de palettes et champs réservés), index de **8 octets par palette** (offset 32 bits, nombre de couleurs 16 bits, flags 16 bits), et **768 octets fixes par emplacement** (256 couleurs RGB24). **Indices internes à partir de 0.** Taille proposée : `16 + N × (8 + 768)`, soit **6 224 octets pour huit palettes**. Endianness, offsets exacts, représentation des emplacements libres et contrôle des données seront établis avant le code.

**Première fonction proposée :** `_OK=Aga Palette Bank Init(10,8)` après réservation AMOS DATA (exemple de conception : `Reserve As Data 10,6224`), retour attendu **1/0**. Le nom externe ABK de huit octets `AGAPAL  ` **n'est pas garanti** par une réservation DATA ordinaire : vérifier dans les sources/documentation AMOS les champs d'en-tête `AmBk`, le nom de banque et les mécanismes `Save`/`Load`. Une signature AGAPAL interne ne remplace pas l'enveloppe ABK native.

**Vérifications préalables obligatoires :** conventions `Reserve As Data`, allocation Chip/Fast, accès/taille des banques, identité et durée de vie, `Erase`, persistance ABK, ABI 68000 et limites d'allocation. Le premier incrément ne portera que sur `Aga Palette Bank Init` ; les futures commandes de capture, import, application, fades et cycling restent à discuter **individuellement** avant codage. **R29 0.10.1 reste candidate actuelle et LAST_GOOD ; aucun code ni Gate R30 exécuté.**

---

## R29 0.10.1 VALIDÉE — Gate A + Gate B AMOS/WinUAE PASS, 11/11/2026

**Preuves utilisateur :** test `M13_R29_PALETTE_SAVE_01.asc` exécuté sous AMOS interprété/WinUAE : `OPEN 1 DB 1`, `DRAW 1 1 1 1`, `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. L'utilisateur confirme également l'ouverture de la palette IFF produite avec ses **256 couleurs dans Cloanto Personal Paint (PPaint)** ; le fichier ne contient pas de pixels `BODY`. Cela établit l'interopérabilité **pour ce fichier et cet essai**, pas tous les éditeurs IFF.

**Promotion obligatoire :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib`, **R29 0.10.1**, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, octet pour octet. L'archive R28 est figée et conservée. Le fichier de test original (Git blob `b80baabe5533288cac3285a78c232827cce94085`) est déplacé **sans modification** dans `tests/passed/M13_R29_PALETTE_SAVE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`.

**Validation :** Gate A CPU 68000 **49 scénarios PASS**, [CI R29 avant promotion **30/30 PASS**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43016176793) ; Gate B interprété/WinUAE **PASS** sur le test et PPaint précités. **Gates C (Compiler) et D (matériel réel) NON TESTÉES**. La validation sous PPaint ne démontre pas l'affichage des pixels puisque le format est volontairement sans `BODY`.

**Suite M13 :** fonctions de banques de palettes (Fast RAM privilégiée) et fades natifs `Aga Fade To Bank/Black/White`, puis cycling. **Avant chaque nouvelle fonction, discuter et valider son contrat avec l'utilisateur ; aucune implémentation anticipée.**

---

## Décision utilisateur — processus de développement M13/R29 (11/11/2026)

**Avant toute nouvelle fonction : discussion technique avec l'utilisateur et accord explicite sur SON contrat avant code, builder, test ou binaire.** Cette règle est désormais prioritaire dans [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md). Une validation générale de R29 ou de M13 ne suffit pas à figer les API successives.

**R29 approuvée sur le principe :** sauvegarder/exporter les palettes au format **IFF standard `FORM ILBM` / `CMAP`**, sans format propriétaire. **Proposition à cadrer :** charger/conserver aussi des palettes dans une bank mémoire, de préférence **Fast RAM** si disponible ; compatibilité avec banques AMOS, allocation, libération et repli restent à choisir avant code.

**Futurs fades natifs à discuter une par une :** `Aga Fade To Bank`, `Aga Fade To Black`, `Aga Fade To White`. Le contrat doit encore définir les paramètres, VBL/durée, interpolation et mode d'exécution. Color cycling ensuite. **Mise à jour :** R29 Save est validée sous AMOS/WinUAE, la palette générée est chargée dans PPaint et `LAST_GOOD` est promue à R29 0.10.1. La discussion des futures banques/fades demeure obligatoire avant toute implémentation.

---

## R28 validée — 11/11/2026

M13/R28 0.10.0 : Gate A 159 cas 68000 PASS, CI précédente 29/29 PASS ; Gate B AMOS interprété/WinUAE PASS sur la capture M13-R28-PALETTE-01 du 11/11/2026. Résultats : OPEN/DB/IFF CMAP/SET/DRAW/SWAP = 1 ; BAD 0 BADG -1 ; PEAK 16254720 ($F80700), FINAL 65280 ($00FF00), FADEERR 0, CLOSED -1, RESULT 1, CLOSE RETURNED. Le test AMOS sélectionne un IFF sans que son chemin soit connu depuis la capture ; la compatibilité d'un export palette seule PPaint/DPaint réel n'est donc pas établie. Le résultat numérique n'atteste pas à lui seul l'observation visuelle complète des 64 transitions. Gate C Compiler et Gate D Amiga réel non testées.

**Bibliothèques :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` sont des copies binaires identiques de l'archive `dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib` : 16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`. R27 reste figée dans `dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib` (SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`). Test original déplacé octet pour octet : `tests/passed/M13_R28_PALETTE_01.asc`; aucun test ASC actif.

**Suite autorisée M13 :** palette sauvegardable au format standard IFF FORM ILBM/CMAP, sauvegarde/restauration, fade natif, puis cycling ; incréments séparés et Gate A avant toute nouvelle candidate. M14 fontes et M15 dessin 2D restent ultérieurs.

---


**Historique antérieur ci-dessous : ne pas le lire comme l'état présent de LAST_GOOD ou des tests.**

## M13 — R28 0.10.0 : archive candidate disponible, Gate A 159 cas PASS, Gate B WinUAE à réaliser

**11/11/2026 — M13/R28 à tester** : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) = **R28 0.10.0**, **16 208 octets**, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`. **Gate A CPU/CI PASS 159 cas** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43005222352)), **Gate B WinUAE en attente**. [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) = **R27 0.9.3**, dernière version WinUAE PASS (M12). [Règle de promotion](../EXTENSION_SOURCE_RULES.md). Roadmap : M13 palette IFF/RGB/fades/cycling → M14 fontes → M15 Plot/Draw/Box/Circle.

- **Premier incrément M13** : `_OK=Aga Palette Load(file$)` lit le **CMAP standard IFF/ILBM**, palette PPaint/DPaint seule ou image complète, sans charger `BODY`, même sans BMHD ; `_OK=Aga Palette Set(pen,r,g,b)` modifie RGB 24 bits ; `_RGB=Aga Palette Get(pen)` retourne `$00RRGGBB` ou `-1`. Aucun format maison. **Export / sauvegarde future au même format IFF**, après validation du socle.
- **Sécurité** : couleur indexée, profondeur 1–8, validation ColorMap.Count et des limites, refus explicite HAM/EHB/dual playfield, CMAP valide de 1 à 256 couleurs. `Palette Load` conserve le WaitTOF du loader M5 ; `Palette Set` sans blocage VBL pour permettre animation contrôlée par AMOS.
- **AP20** : candidate R28 **34 commandes, 40 segments**, trois fonctions `Aga Palette Load/Set/Get` ajoutées après R27 ; les anciens segments 0..35 sont préservés, le segment 36 reçoit uniquement `GetP`. [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) **est maintenant R28**, l'archive R28 versionnée est conservée dans `dist/experimental/`.
- **Gates** : R28 **Gate A CPU/CI PASS 159 cas** ; **Gate B WinUAE non testée** ; Compiler/Amiga physique non testés. Importer le test avec `Project → Merge ASCII` depuis [`tests/current/M13_R28_PALETTE_01.asc`](../tests/current/M13_R28_PALETTE_01.asc), sélectionner un IFF palette Personal Paint ou `examples/demo.iff`, observer la transition vert → rouge → vert. **Installer directement `dist/AMOSPro_AGA.Lib` sans renommage**.
- **Repli validé** : [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) = R27 (WinUAE PASS sur M12), **copie octet pour octet de l'archive R27** ; R10 conservée dans son archive historique. **Une seule ASC R28 active** ; aucune branche supplémentaire. À chaque nouvelle Gate B confirmée, promouvoir obligatoirement la bibliothèque correspondante dans `LAST_GOOD`.

---

**Les sections ci-dessous sont historiques ; elles ne décrivent pas le binaire courant ni la politique actuelle de `LAST_GOOD`.**

## Décision de roadmap — M13 palettes, M14 fontes, puis M15 dessin 2D (11/11/2026)

**Choix utilisateur confirmé :** enchaîner **M13 palettes AGA** (chargement sans pixels, RGB 24 bits, fades, cycling, sauvegarde/restauration), **M14 fontes** (compléter `Aga Text` R26), puis **M15 primitives graphiques 2D** (`Plot`, `Draw`, `Box`, `Circle`). Les sprites matériels, scrolling, dual playfield et Copper avancé passent à **M16+**. [Roadmap et périmètres](ROADMAP.md).

- **M13 — note historique antérieure au démarrage :** avant tout builder ou binaire, auditer `Aga Iff Load`/CMAP/`SetRGB32`, `ViewPort.ColorMap` Intuition, interactions Copper RGB4 et modes EHB/HAM ; définir le contrat des opérations palette, fades temporels, VBL et validation WinUAE. **Aucune API M13 ni R28 n'est encore implémentée.**
- **M14 ensuite :** développer choix et chargement des fontes, métriques, styles, alignement, multi-ligne et éventuelles banques AMOS/AMCAF. `Aga Text` R26/R27 actuel se limite à une ligne en police système par défaut ; ne pas considérer le moteur de fontes comme terminé.
- **M15 après M14 :** dessin dans le back buffer AGA Intuition : pixel (`Plot`), trait (`Draw`), rectangle contour (`Box`), cercle (`Circle`). Auditer d'abord la sémantique exacte AMOS/Turbo/AMCAF, notamment `F Plot`/`F Draw` ; vérifier coordonnées, clipping, couleurs indexées, retour Safe et double buffering. **Aucune API M15 ni binaire correspondant n'existe encore.**
- **M16+ :** sprites matériels, scrolling, dual playfield, Copper avancé et optimisations, sans chantier ouvert.
- **Base protégée (état actuel)** : R27 0.9.3 **LAST_GOOD**, archive R27 figée ; R28 0.10.0 candidate active ; R10 reste archivée. Le test R28 est actif et non validé en WinUAE. L'exemple [`examples/show.asc`](../examples/show.asc) reste non validé de bout en bout.
- **Process :** changements exclusivement sur `main`, pas de nouveau binaire ni de branche durant cette mise à jour documentaire. Les gates CPU/WinUAE/Compiler/matériel restent distinctes.

---

## M12 — R27 0.9.3 Blitters Safe : Gates A+B PASS sur scénarios validés

**11/11/2026 — Gate A CPU 68000/CI PASS 403 cas, Gate B AMOS interprété/WinUAE PASS sur 40 swaps.** [CI finale 28/28](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997575220) · [Contrat et compte-rendu M12](M12_SAFE_BLITTER_R27.md) · [test M12 original archivé sans modification](../tests/passed/M12_R27_SAFE_BLIT_01.asc), Git blob `3b3a6d8c120b1ec066669231d382eae6e0e4bd82`.

- **Bibliothèque active** : `dist/AMOSPro_AGA.Lib` = [archive R27](../dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib), **14 252 octets**, SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`. Versions R26 0.9.2 WinUAE-PASS, R25/R24 et `LAST_GOOD` R10 **intactes**.
- **R27** : 31 tokens AP20 inchangés, 37 segments ; fonctions `Aga Blit Copy`, `Aga Blit Fill`, `Aga Blit Clear` protégées contre l'usage d'un buffer en attente Safe. **Neuf segments modifiés** : 19/20/21 Blitters et 6/17/18/31/32/33 relocalisés pour conserver les BSR et l'état clavier/souris R23. Première candidate défectueuse retirée **avant WinUAE** ; seule la candidate corrigée a été exécutée.
- **Capture et observation utilisateur** : `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`, fin AMOS **ligne 167**. Rectangles vus **clignoter**, sans détail individuel des couleurs explicitement confirmé. **Pas de sonde `Aga Text`**.
- **Tests** : `tests/current/` ne contient **aucun `.asc` actif** ; `tests/passed/M12_R27_SAFE_BLIT_01.asc` est archivé **octet pour octet**. La validation vaut pour ce protocole de 40 swaps, pas une garantie de 50 FPS ni une absence exhaustive de courses. Les 13 retours 0 par primitive ne prouvent pas individuellement leur cause.
- **Restent NON TESTÉS** : AMOS Compiler, Amiga AGA physique, stress prolongé, chronométrage FPS ; `Aga Back Fill` historique ne bénéficie pas du garde R27. Aucun nouveau chantier/branche ouvert.


---

## M11 — R26 0.9.2 : tests texte et Safe/Disp multi-swap PASS sous WinUAE

**11/11/2026 — deuxième validation WinUAE utilisateur.** Avec la bibliothèque **R26 0.9.2 inchangée**, le programme [`M11_R26_SAFE_SWAP_02.asc` archivé sans modifier un octet](../tests/passed/M11_R26_SAFE_SWAP_02.asc) a présenté **40 alternances visuelles A/B vert/rouge**, avec retour correct à AMOS **ligne 140**. Ce PASS s'ajoute au test [texte initial R26](../tests/passed/M11_R26_AGA_TEXT_01.asc) et au Gate A CPU/CI PASS (64 cas 68000, [CI complète R26](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42923706360)).

- **Résultats observés :** `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `DONE 40 PROBEOK 40`, `PROBE0 39 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. Alternance visuelle confirmée par l'utilisateur.
- **Signification :** 39 sondes ont renvoyé `0` avant une tentative réussie ; les reprises bornées ont donc bien été exercées, sans échec final. **La cause de chaque retour 0 n'est pas identifiable individuellement** (Safe ou autre rejet) et le test ne prouve pas toute la sûreté mémoire du moteur hors du protocole de sondage. Aucun 50 FPS mesuré.
- **Archivage :** test original déplacé octet pour octet vers [`tests/passed/M11_R26_SAFE_SWAP_02.asc`](../tests/passed/M11_R26_SAFE_SWAP_02.asc), Git blob `d0306efe728032cd85d126338ecc97ec674ad2c4`. **`tests/current/` sans `.asc`**. R26/R25/R24, `LAST_GOOD` R10 et tous les tests archivés existants inchangés.
- **Suite ouverte :** éventuelle sécurisation partagée des Blitters pour des séquences de rendu arbitraires et essais de robustesse plus longs, uniquement après définition d'un contrat distinct. **AMOS Compiler, Amiga AGA physique et stress prolongé toujours NON TESTÉS.** Aucune nouvelle R27 engagée ni nouvelle branche. [Rapport M11](M11_TEXT_R26.md).


---

## M11 — R26 0.9.2 AGA Text : Gate A CPU/CI + Gate B AMOS/WinUAE PASS

**11/11/2026 — validation graphique sous WinUAE par l'utilisateur, sur le scénario exact M11.** Capture : panneau bleu **avec `AGA TEXT R26` affiché en vert** sur l'écran Intuition AGA indépendant ; retour AMOS normal, fin du programme à la ligne 74. **Gate A 64 scénarios CPU/CI PASS**, [CI R26 complète #42922291061](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42922291061). **Gate B PASS pour ce test graphique** ; Compiler, vrai Amiga AGA, alternances rapides Safe/Disp et stress **NON TESTÉS**.

- **Binaire courant** `dist/AMOSPro_AGA.Lib` = [archive R26 0.9.2](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib), **14 044 octets**, SHA256 `0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287`. R25 0.9.1 reste [archivée et WinUAE PASS sur M10](../dist/experimental/AMOSPro_AGA_M10_v0.9.1_RECT_OVERLAP_R25.Lib). R24 et `LAST_GOOD` R10 intacts.
- **Test original** déplacé **octet pour octet** vers [`tests/passed/M11_R26_AGA_TEXT_01.asc`](../tests/passed/M11_R26_AGA_TEXT_01.asc) (Git blob `2cd9acd45f17a07ac77bbd1a340aa14c628a01ad`). **Aucun `.asc` dans `tests/current/`.**
- **Console observée** : `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `CLEAR 1 PANEL 1`, `BAD 0 TEXT 1 SWAP 1`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. La routine graphique rend par `graphics.library/Text` dans le **back buffer AGA** ; `Text` AMOS n'intervient pas.
- **Portée limitée :** le test vérifie un dessin après le premier swap et un rejet géométrique ; **il ne stresse pas le contrôle non bloquant Safe** lors de changements successifs. R26 n'est pas déclarée compatible avec toutes les fontes et séquences de rendu.
- **Suite possible :** étude ciblée du rendu multi-image avec notification Safe/Disp, éventuellement petite démonstration texte ; ne pas toucher aux entrées R26 validées sans preuve de besoin, ne créer aucune autre branche. [Contrat et dossier M11](M11_TEXT_R26.md).

---

## Historique — M11 R26 0.9.2 : préparation de la candidate avant validation WinUAE

**11/11/2026 — Gate A 68000/CI PASS 64 scénarios**, [workflow réussi 42921696298](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42921696298). **Gate B AMOS interprété/WinUAE NON TESTÉE**, Compiler et Amiga physique NON TESTÉS. Ne pas déclarer R26 validée en runtime avant retour utilisateur.

- **Bibliothèque candidate sur `main` :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) = [R26 archive versionnée](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib), **14 044 octets**, SHA256 `0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287`, 37 segments AP20 / 31 tokens nommés.
- **Base figée R25** : [`dist/experimental/AMOSPro_AGA_M10_v0.9.1_RECT_OVERLAP_R25.Lib`](../dist/experimental/AMOSPro_AGA_M10_v0.9.1_RECT_OVERLAP_R25.Lib), 13 408 octets, SHA256 `4835473771629bea697d64c9213ff1064013597f7dabc519914f4ea013af6da6`, Gate A+B PASS **uniquement sur son scénario M10**. R24 et `LAST_GOOD` R10 inchangés.
- **API :** `_OK=Aga Text(x,baselineY,pen,text$)` ; 1 ligne, 1–128 caractères, fonte système, index palette, fond transparent. Cible le back BitMap Intuition AGA via RastPort temporaire ; `TextExtent` valide les bords des glyphes. `_OK=1` si dessin réalisé ; `0` pour paramètres incorrects ou buffer Safe pas encore disponible. [Contrat](M11_TEXT_R26.md).
- **Safe** : un `GetMsg(SafePort)` non bloquant si bit0 de `DBState+20` en attente, aucun `ReplyMsg`. Ce mécanisme ne modifie **pas** les Blitters R25 et ne prouve pas leur sûreté hors du scénario déjà testé.
- **Seul test actif :** [`tests/current/M11_R26_AGA_TEXT_01.asc`](../tests/current/M11_R26_AGA_TEXT_01.asc), bandeau `M11-R26-AGA-TEXT-01`. Importer par `Project → Merge ASCII` sous AMOS avec la **Lib R26** installée, choisir `examples/demo.iff` (320×256×8), observer le **texte vert `AGA TEXT R26` sur fond bleu** pendant 220 VBL, puis lire `BAD 0 TEXT 1 SWAP 1`, `RESULT 1`, `CLOSE RETURNED`. Capture et constat visuel requis ; ce test n'a pas été exécuté sous WinUAE.
- **Builder/CI :** [builder R26](../tools/build_m11_text_r26.py), [source 68000](../tools/m11_text_r26_emit.py), [CPU tests](../tools/test_m11_text_r26.py), contrôle d'intégrité et reproductibilité de la Lib candidate. Aucun nouveau branchement ; ne pas archiver ce test avant validation utilisateur.

---

## M11 — correction d'architecture : commandes AMOS ≠ dessin sur écran AGA indépendant

**11/11/2026 — suite du retour utilisateur :** l'essai proposé `Text` natif AMOS sur l'écran Intuition AGA ne répondait pas à une question ouverte ; AMOS gère ses propres écrans et son état graphique. Le Copper affiche les bitplanes, mais ne transforme pas le `RastPort` cible des commandes AMOS. **Test M11 non exécuté, classé dans [`tests/historical/M11_R25_AMOS_TEXT_01.asc`](../tests/historical/M11_R25_AMOS_TEXT_01.asc) sans le déclarer PASS.**

- **Statut :** M11 = étude d'architecture, **pas de Gate M11, pas de R26, aucun `.asc` actif** dans `tests/current/`.
- **Audit technique achevé (11/11/2026) :** [M11_BACKBUFFER_R25.md](M11_BACKBUFFER_R25.md) compare octet pour octet les segments 10/11/12/19/20 des bibliothèques R23/R25. Le chemin exact est `A5+$1C8 → State+32 → DBState frontIndex+8 → ScreenBuffer inactif → sb_BitMap`. `Aga Back Fill` prépare **déjà** un `RastPort` sur ce `BitMap` avec `InitRastPort`. **Point bloquant avant API :** le bit Safe de `DBState+20` après `Aga Swap` ; `Aga Wait Vbl` n'est pas un accusé Safe. Étudier le rendu `graphics.library/Text` seulement après sécurisation de cette attente non bloquante.
- **Fontes :** les commandes AMOS/AMCAF (`Text`, `Change Bank Font`, `Scrn Rastport`) ne visent pas automatiquement notre écran Intuition. Les banques de fontes peuvent faire l'objet d'une étude de conversion seulement si le besoin le justifie.
- **Aucun code de production modifié** : `dist/AMOSPro_AGA.Lib` R25, son archive, R24 et `LAST_GOOD` R10 préservés. Le **PASS R25** porte toujours uniquement sur le test archivé. [Note de conception M11](M11_TEXT_COMPAT.md).


---

## M10 — R25 0.9.1 : Gate A CPU/CI + Gate B AMOS/WinUAE PASS

**10/11/2026 — scénario de collision validé par l'utilisateur sous AMOS interprété/WinUAE.** [CI CPU/ABI R25 PASS : 704 cas 68000](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42916575209). Les portes A et B passent **sur le périmètre testé** ; AMOS Compiler, Amiga physique, stress et cadence réelle non validés.

- **Bibliothèque courante sur `main` :** `dist/AMOSPro_AGA.Lib` = `dist/experimental/AMOSPro_AGA_M10_v0.9.1_RECT_OVERLAP_R25.Lib` ; **13 408 octets**, SHA256 `4835473771629bea697d64c9213ff1064013597f7dabc519914f4ea013af6da6`. **30 commandes AP20**. Archive R24 WinUAE PASS et `LAST_GOOD` R10 inchangés.
- **Nouvelle API :** `Aga Rect Overlap(ax,ay,aw,ah,bx,by,bw,bh)`, résultat `1` uniquement pour une aire commune positive. Contact bord/coin et dimensions invalides = `0`, origines négatives autorisées, fonction pure sans dépendance à l'écran, ABI `A3+28`.
- **Test R25 validé, déplacé octet pour octet :** [`tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc`](../tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) (blob Git `0eac65e7a92418738d9a3ea6969d131758126cfa`). La R25 est archivée sans modification ; **plus aucun `.asc` actif dans `tests/current/`** depuis la clôture R26.
- **Capture utilisateur :** `IMAGE 320 X 256 PLANES 8`, `STATIC 1 PURE 1`, `OPEN 1 DB 1 LOAD 1`, `SEEN FREE 1 HIT 1`, `FRAMES 409 DRAWERR 0`, `LAST HIT 1`, `CLOSED -1 PRESS -1`, `REOPEN 1 BASE 0 CLOSE2 -1`, `RESULT 1`, `CLOSE X2 RETURNED`. Fin normale sous AMOS.
- **Graphisme :** rectangle fixe bleu index 3, mobile 32×32 vert index 28 hors collision et rouge index 224 lors du recouvrement. Back buffer entièrement effacé/redessiné, puis **un `Aga Swap` et un `Aga Wait Vbl`** à chaque image. La mire IFF fournit les métadonnées du mode et la palette ; ses pixels ne sont pas exploités dans cette animation. **409 images traitées ne prouvent ni 50 FPS ni absence de traces ; pas de chronométrage.**
- **Exemple distinct :** [`examples/collide.asc`](../examples/collide.asc), version pédagogique courte ajoutée avec `examples/README.md` et `README.fr.md`; scripts vérifiés statiquement par la CI, **exemple autonome non testé sous WinUAE**.
- **Suite M11 :** la tentative `Text` AMOS a été écartée avant WinUAE (voir le nouveau checkpoint M11 en tête). Étudier le rendu natif vers le back buffer propre à l'extension avant de décider d'une commande R26 ; aucune autre branche. [Contrat R25](M10_RECT_OVERLAP_R25.md).


---

## M9 — R24 0.9.0 : Gate A + B PASS, test archivé

**10/11/2026 — R24 0.9.0 validée sur son scénario AMOS interprété/WinUAE** (Gate A CPU/CI PASS 402 cas 68000, Gate B PASS utilisateur). Nouvelle fonction `Aga Hotspot Hit(px,py,x,y,w,h)` ; 29 commandes AP20 et priorités gérées dans AMOS.

- **Test exact validé** : [`tests/passed/M9_R24_HOTSPOT_HIT_01.asc`](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc), SHA Git `0476f20a81a8bff1bf282a37a7e3b4b710c72022`, **sans aucune modification des octets**. La version corrigée ne contient aucun `Then` et se termine normalement ligne 183. **Aucun `.asc` actif** dans `tests/current/`.
- **Preuve WinUAE** : `STATIC 1`, `OVERLAP 20`, `PURE 1`, `OPEN/DB/LOAD/SWAP=1`, `FILLS 1/1/1`, `LEFT ID 20`, `RIGHT OUT 1`, `CLOSED=-1`, `PRESS=-1`, `REOPEN 1`, `BASE 0`, `CLOSE2 -1`, **`RESULT 1`** et `CLOSE X2 RETURNED`.
- **Compteurs expliqués par l'utilisateur** : `LEFT COUNT=13`, `RIGHT COUNT=3` proviennent de **clics volontairement répétés** pendant le test, pas d'une répétition parasite constatée. La sélection des zones est validée. Ce scénario ne constitue toutefois pas un essai d'unicité sur un seul clic physique.
- **Bibliothèque courante** : `dist/AMOSPro_AGA.Lib` R24 = archive `dist/experimental/AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib`, 13 228 octets, SHA256 `cc8776e7303c529492fe6761544f4b2be1180063f3787fa840f44129766e3671`. R23 et `LAST_GOOD` R10 inchangées.
- **Hors validation** : focus réel, stress, AMOS Compiler, Amiga physique, position souris au moment exact du clic. L'implémentation M9 reste **stateless** ; un registre de zones, le drag et M10 collisions nécessitent une décision ultérieure. [Rapport R24](M9_HOTSPOT_R24.md).


---

## M8 — R23 0.8.7 : Gate A + B PASS, test archivé

**État sur `main` au 10/11/2026 :** R23 0.8.7 validée dans le périmètre AMOS interprété/WinUAE des **clics rapides gauche/droit**, de la **FIFO clavier**, de la **fermeture/réouverture d'écran** et de **Ctrl+C**. Gate A CPU/CI PASS 15 cas (CI complète (archive CI privée, run #42899343161)), Gate B PASS sur essais utilisateur.

- **Preuve clavier/souris :** `PRESSED=3 RELEASED=3 AGAIN=0/0`, `KEYS=64/64/-1`, `WAIT=16` (A AZERTY), `RESULT=1`, `OPEN/DB/LOAD/SWAP/REOPEN=1`, fermetures et retour AMOS corrects.
- **Preuve Ctrl+C séparée :** interruption à `_WAITK=Aga Wait Key` avec fermeture correcte de l'écran Intuition (retour utilisateur). L'arrêt empêche normalement l'affichage du résultat final.
- **Archive du test exact :** [`tests/passed/M8_R23_IDCMP_QUICK_01.asc`](../tests/passed/M8_R23_IDCMP_QUICK_01.asc), SHA Git `3e73efc9634db4567d20464081ae6f6b8187ad1a` ; **aucun `.asc` actif dans `tests/current/`**.
- **Binaire R23 :** `dist/AMOSPro_AGA.Lib` et archive `dist/experimental/AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib`, SHA256 `899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23`. `LAST_GOOD` R10 et les archives validées précédentes restent inchangées.
- **À ne pas extrapoler :** changements de focus réel, absence de menu pendant le clic droit R23, stress FIFO, AMOS Compiler, Amiga physique non testés. La FIFO fait 16 entrées, le dispatcher est borné à 64 messages et les masques ne comptent pas les clics répétés. **Suite possible :** finaliser les essais de focus/stress avant M9 hotspots ; ne créer aucune branche sans instruction.
- [Contrat R23](M8_IDCMP_R23.md) · [Roadmap](ROADMAP.md) · [API publique EN/FR](../README.md).

---

## M8 — R22 0.8.6 : Pressed/Released, Gate A + B PASS

**R22 courante sur `main` : CPU/CI PASS (25 tests, CI (archive CI privée, run #42893816454)) et AMOS interprété/WinUAE PASS sur le scénario utilisateur du 10/11/2026.** [Test exact archivé](../tests/passed/M8_R22_MOUSE_EDGES_01.asc) ; **aucun `.asc` actif** dans `tests/current/`.

- Bibliothèque `dist/AMOSPro_AGA.Lib` = archive R22 `dist/experimental/AMOSPro_AGA_M8_v0.8.6_MOUSE_EDGES_R22.Lib`, 12 852 octets, SHA256 `96e38d478bd97e7a65801e16e96ce08c0bbd4aaacb4a8a6644e4bc1289a0c997`. R21 et `LAST_GOOD` R10 intacts.
- Nouvelles fonctions `Aga Mouse Pressed/Released` : masques 1/2/4 et historiques de fronts indépendants ; `input.device/PeekQualifier()` sans consommation de la file clavier.
- **Résultat :** `PRESSED=RELEASED=3`, `PL=PR=RL=RR=1`, `DONE=1 ERR=0`, `KEY=64`, `CLOSED=-1/-1`, `REOPEN=1 BASE=0/0`, fin normale à la ligne 117. `FRAME=1001` est une fin normale de boucle For.
- **Limites :** la capture finale ne prouve pas l'absence de menu Intuition pendant le clic droit ; clics très brefs, focus réel, Compiler, matériel Amiga et stress non testés.
- **Suite M8 :** étudier le dispatcher commun `IDCMP_MOUSEBUTTONS/RAWKEY` pour ne plus manquer les clics très brefs sans casser `Aga Key/Wait Key` et Ctrl+C. [Dossier R22](M8_MOUSE_EDGES_R22.md).

---

## M8 — R21 0.8.5 RMBTRAP : PASS WinUAE, test archivé

**10/11/2026 — confirmation explicite de l'utilisateur : « nickel, je valide ! »** après essai R21 sous AMOS interprété/WinUAE. Le clic droit ne laisse plus apparaître la barre de menus Intuition, et les boutons souris fonctionnent dans le scénario demandé. **Gate B R21 PASS sur ce périmètre**, sans capture numérique détaillée R21 jointe à cette validation.

- **HEAD `main` et règles :** relire le HEAD réel, `EXTENSION_SOURCE_RULES.md`, [statut M8](M8_STATUS.md) et [roadmap](ROADMAP.md) à chaque reprise. Ne créer aucune branche sans demande explicite.
- **R21 courante :** `dist/AMOSPro_AGA.Lib` et archive `dist/experimental/AMOSPro_AGA_M8_v0.8.5_RMBTRAP_R21.Lib`, **12 016 octets**, SHA256 `a72e3046df64e3ff8ebe12a5b4b0db45efebe27e17056919d31d11ca61e9c644`.
- **Gate A : PASS** 11 tests natifs CPU 68000 et CI complète #42887916480 (archive CI privée). **Gate B : PASS utilisateur** (clic gauche/droit, suppression du menu Intuition, scénario WinUAE). **Gate C Compiler / Gate D matériel : NON TESTÉES** ; ni stress, ni fuite mémoire, ni clic très bref validés.
- **Test R21 archivé octet pour octet :** [`tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc`](../tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc), bandeau `M8-R21-MOUSE-RMBTRAP-01`. Aucun `.asc` actif dans `tests/current/`.
- **Correction R21 :** `NewWindow.Flags=$00031900` via `WFLG_RMBTRAP`, un seul octet de code changé dans entrée AP20 6 par rapport à R20 ; les 30 autres entrées et tokens conservés. `tools/build_m8_rmbtrap_r21.py`, `tools/test_m8_rmbtrap_r21.py`.
- **R20 :** boutons fonctionnels mais menu Intuition persistant, [test historique conservé](../tests/historical/M8_R20_MOUSE_BUTTONS_01.asc). **R19 X/Y et R18 Copper archivées et PASS WinUAE** sur leurs scénarios ; `LAST_GOOD` **R10 inchangée**.
- **Prochain chantier M8 (non commencé) :** définir les transitions natives `Aga Mouse Pressed/Released`, la gestion des clics rapides et du focus, en préservant `Aga Key`. Les fronts de R21 sont calculés dans l'exemple AMOS à partir du masque, pas dans une nouvelle API native. Puis seulement M9 hotspots et M10 collisions.

**R21 validée, M8 global encore en cours.** Ne pas promouvoir `LAST_GOOD` sans instruction explicite.

## Historique — R20 avant constat du défaut

## M8 — R20 0.8.4 : boutons souris, Gate A PASS, WinUAE à tester

**Relire le HEAD de la branche et `EXTENSION_SOURCE_RULES.md`.** Branche active `main`, base R19 0.8.3 **PASS AMOS/WinUAE** sur X/Y. Aucun autre jalon lancé.

- **Candidat R20 :** `dist/AMOSPro_AGA.Lib` (candidate actuelle sur `main`), **12 016 octets**, SHA256 `9d1e9d6fd13478947c016d3f95973efa2ac766f96c364e091f43c69daa8672fe`, archive `dist/experimental/AMOSPro_AGA_M8_v0.8.4_MOUSE_BUTTONS_R20.Lib` ; nouvelle fonction `Aga Mouse Buttons` (masque 1/2/4 ou -1).
- **Builder / tests :** `tools/build_m8_mouse_buttons_r20.py`, `tools/test_m8_mouse_buttons_r20.py`, test AMOS unique `tests/current/M8_R20_MOUSE_BUTTONS_01.asc`, bandeau `M8-R20-MOUSE-BUTTONS-01`.
- **Gates R20 :** A **PASS : 21 cas CPU 68000 / CI #42883983376 (archive CI privée)** ; B AMOS interprété/WinUAE NON TESTÉE ; C Compiler / D matériel NON TESTÉES. Aucune validation R20 à déduire du PASS R19.
- **Prochaine action :** installer R20 depuis `main` sous WinUAE ; maintenir bouton gauche, relâcher, puis bouton droit, relâcher, puis touche clavier. Attendu `PRESSED And 3=3`, `RELEASED And 3=3`, `IOERR=0`, retours `CLOSED=-1`.
- `input.device/PeekQualifier` ne consomme pas les événements clavier mais fournit un instantané **global** et non les événements IDCMP locaux. Fronts calculés dans AMOS, pas une API Pressed/Released native ; clics rapides non garantis.
- Ne pas déclarer R20 WinUAE PASS ni promouvoir `LAST_GOOD` avant la capture utilisateur ; ne pas toucher R19/R18 ni règles/prompt.

---

## M8 — R19 0.8.3 : positions X/Y PASS WinUAE, suite boutons/transitions

**Relire `EXTENSION_SOURCE_RULES.md`, le HEAD réel et les documents courants avant tout travail.** R19 est la bibliothèque courante ; R18 est archivée et `LAST_GOOD` R10 inchangée.

- **R19 0.8.3 :** `dist/AMOSPro_AGA.Lib`, **11 744 octets**, SHA256 `32c99d9d83affda67058fede26731dace6511ebc033b7974330e6f9eef39e295`. Archive reproductible : `dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib`.
- **Gate A CPU 68000 PASS 76 cas**, CI générale PASS #42878271256 (archive CI privée). **Gate B AMOS interprété/WinUAE PASS** sur scénario de position, capture le 10/11/2026. Compiler et vrai Amiga **NON TESTÉS**.
- **Validation :** premier essai `P1=(112,65), P2=(24,238)`; second essai `P1=(0,0), P2=(319,255)`, `OPEN/DB/LOAD/SWAP/REOPEN=1`, `BEFORE/CLOSED/CLOSED2=-1 -1`, `KEY=64`, `CLOSE X2 RETURNED`, fin AMOS ligne 87.
- **Test archivé sans modification :** [`tests/passed/M8_R19_MOUSE_POSITION_01.asc`](../tests/passed/M8_R19_MOUSE_POSITION_01.asc). **Aucun `.asc` actif** dans `tests/current/`.
- **Builder :** `tools/build_m8_mouse_position_r19.py` ; test CPU : `tools/test_m8_mouse_position_r19.py`. [Statut](M8_STATUS.md), [protocole](M8_MOUSE_R19.md).
- **Suite possible M8 :** incrément séparé sur les boutons gauche/droit et fronts pressed/released, sans perturber `Aga Key`. Voir [INTERACTIONS_COLLISIONS](INTERACTIONS_COLLISIONS.md). Aucun code ou test R20 créé.

**Ne pas modifier `LAST_GOOD`, la bibliothèque R18, les règles ou le prompt universel à l'occasion de cette clôture R19.**

---

## Historique — M7 R18 Copper RGB4 validée WinUAE

## M7 — Copper RGB4 R18 0.8.2 : PASS WinUAE ; suite M8 souris

**Relire le HEAD réel de main et les règles permanentes à chaque reprise.** La R17 0.8.1 a PASS WinUAE 3/3 et est préservée comme archive. **R18 est la bibliothèque courante, créée depuis R17 et validée sous AMOS interprété/WinUAE** pour le scénario raster.

- **Lib courante :** `dist/AMOSPro_AGA.Lib`, R18 0.8.2, 11 480 octets, SHA256 `600b8c2c38486004adef8c0e7924df877f7dd7829e1c622a89bbdc0db9f9808a`. Archive `dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib` identique.
- **Base figée WinUAE :** R17 0.8.1, `dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib`. R16, R15 et M6 conservées. **LAST_GOOD R10 inchangée**.
- **Nouvelles fonctions :** `Aga Copper Wait(v,h)`, `Aga Copper Move(register,value)`, `Aga Copper End` (COLOR00–31 RGB4 uniquement, WAIT ordonnés, édition interdite après activation).
- **Gate A CPU : PASS**, 26 scénarios sur branche préparatoire (CI #42869523014 (archive CI privée)). **CI complète : PASS** (#42870412601 (archive CI privée)). **Gate B WinUAE : PASS**, captures du raster et de la console utilisateur le 10/11/2026 ; **Gates C/D : NON TESTÉES.**
- **Test corrigé et archivé :** [`tests/passed/M7_R18_COPPER_RASTER_01.asc`](../tests/passed/M7_R18_COPPER_RASTER_01.asc). Une syntaxe erronée `Aga Copper Off` isolée a été corrigée par `X=Aga Copper Off` selon l'essai utilisateur. Capture RGB4 rouge/vert/bleu/noir, console `W/M=1`, rejets `BADREG/RGB/WAIT/END2/AFTER=0`, `END/ON/SWAP/OFF/REOPEN/CLEAR2/ON2/OFF3=1`, `KEY 68`, `CLOSE X2 RETURNED`, fin ligne 95. `tests/current/` ne contient aucun `.asc`. Le code exact du fichier local exécuté n'a pas été transféré.
- **Détails :** [`M7_COPPER_R18.md`](M7_COPPER_R18.md), [`M7_STATUS.md`](M7_STATUS.md), [`ROADMAP.md`](ROADMAP.md). **Prochaine action : M8 (souris sur écran Intuition AGA).** Lire les règles et [la spécification interactions](INTERACTIONS_COLLISIONS.md), vérifier le HEAD et le statut de M7 avant tout développement. Ne pas confondre la validation WinUAE de R18 avec une preuve d'absence de fuite ni une validation AMOS Compiler ou Amiga réel ; conserver LAST_GOOD R10.

---

## Historique — checkpoint R17 0.8.1 PASS WinUAE (3/3)

**Checkpoint au 10/11/2026 : relire HEAD réel de `main` avant tout changement.** Références permanentes : `EXTENSION_SOURCE_RULES.md`, `docs/ROADMAP.md`, `docs/M7_STATUS.md`, `docs/M7_COPPER_DESIGN.md`. Le fichier `PROMPT_REPRISE_UNIVERSELLE.md` doit rester indépendant des builds.

- **Lib candidate** `dist/AMOSPro_AGA.Lib` = **R17 0.8.1**, 10 436 octets, SHA256 `cfd74031d6cf75a6c57ed529b2bacc11908cd96a0aad615e325597d5bfb0a02a`.
- **Archive versionnée identique** : `dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib`.
- **Base R16 0.8.0 figée, PASS sous WinUAE** : `dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib`, SHA256 `ba55e92f1d50339b50a06c5b1903767bde549e6738dae320a0ef9ead6251bab1`.
- **LAST_GOOD global R10 0.6.1 inchangée** ; archives M6 R13/R14/R15 intactes.
- **Builder** : `tools/build_m7_copper_on_off_r17.py`. **Test CPU 68000** : `tools/test_m7_copper_on_off_r17.py`. Tests R16/M6 continuent de tourner en non-régression.
- **Deux nouvelles commandes** : `Aga Copper On` / `Aga Copper Off`, sans paramètre, retour 1/0. Utilisent `MakeScreen` / `RethinkDisplay` d'Intuition, puis le retrait et la libération de nos propres allocations. R16 `Clear` et les routines antérieures conservées octet pour octet, séparateur AP20 `GetP` excepté.
- **Gate A CPU/CI : PASS** (CI #42866614578 (archive CI privée), 15 scénarios 68000). **Gate B WinUAE : PASS sur le test R17, exécuté 3 fois le 10/11/2026 sans incident.** Gate C Compiler / Gate D matériel : NON TESTÉES.
- **Test R17 archivé identique** : [`tests/passed/M7_R17_COPPER_ON_OFF_01.asc`](../tests/passed/M7_R17_COPPER_ON_OFF_01.asc), bandeau `M7-R17-COPPER-ON-OFF-01`, **3 exécutions réussies sur MYGIRL.IFF 320×256×8**. Capture : `C1=ON1=SWAP=OFF1=OFF2=C2=ON2=OFF3=REOPEN=C3=ON3=OFF4=1`, `KEY 67`, `CLOSE X2 RETURNED`, fin AMOS ligne 83. **Aucun `.asc` actif dans `tests/current/`**.

**Prochaine action :** R17 clôturée pour son scénario AMOS/WinUAE et son test archivé sans modification. Le prochain candidat **R18** doit introduire séparément `Aga Copper Wait`, `Move`, `End` et un premier raster, après étude des bornes, de la construction des listes et du cycle de vie. Créer **un seul nouvel `.asc`** lors de ce développement. Le PASS R17 ne prouve pas l'absence de fuite mémoire ni la stabilité du raster sous charge. Ne pas promouvoir `LAST_GOOD` sans décision explicite.

## Validations acquises (ne pas relancer sans régression)

- **R16 Copper Clear : PASS WinUAE** le 10/11/2026 : `C1=1 C2=1 C3=1`, `OPEN=1 REOPEN=1`, `SWAP=1`, `KEY 67 CLOSE X2 RETURNED`, fin AMOS à la ligne 74. Test dans `tests/passed/M7_R16_COPPER_CLEAR_01.asc`. N'évalue pas les listes actives ni les fuites mémoire.
- **M6 Blitter : PASS WinUAE** sur R13 Copy, R14 Fill et R15 Clear ; tests exacts archivés.
- **M5 IFF/ILBM clôturé** : HAM6, HAM8, SuperHiRes et SuperHiRes Lace validés ; DblPAL/DblNTSC non testés et non bloquants.

**Attention :** ne pas utiliser `FreeVPortCopLists` comme simple `Off` ; cela libère aussi d'autres listes intermédiaires du ViewPort. Ne pas modifier `DBState+20` (notifications double buffering), ni la logique Screen Close, ni le prompt universel.
