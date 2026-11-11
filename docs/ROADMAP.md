# Roadmap — AMOS Professional 365 / Extension AGA

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
| **M15 — PRIORITÉ 3 (après M14)** | **Primitives de dessin AGA : Plot (pixel), Draw (ligne), Box (rectangle contour), Circle (cercle)** | **Priorité demandée par l'utilisateur le 11/11/2026 ; aucune commande M15 implémentée** | Étudier les conventions des fonctions AMOS/Turbo/AMCAF, puis définir coordonnées, clipping, couleurs indexées, usage du back buffer Intuition AGA et protocole Safe avant toute nouvelle API |
| M16+ — OPTIONS ULTÉRIEURES | Sprites matériels, scrolling, dual playfield, Copper avancé et optimisations | En attente de décision après M13, M14 et M15 | Ne pas démarrer ces chantiers ni créer des commandes anticipées |

**Ordre décidé le 11/11/2026 : M13 palettes → M14 fontes → M15 dessin 2D (`Plot`, `Draw`, `Box`, `Circle`) → réexamen de M16+.** M8–M12 restent des jalons historiques validés sur leurs scénarios. **M13/M14/M15 sont des priorités de développement approuvées, pas des API ni des builds déjà disponibles** ; leurs signatures et sous-jalons restent à confirmer après audit.

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

**M16+** : sprites matériels, scrolling, dual playfield, extensions Copper et optimisations seront réévalués **après** les palettes, les fontes et le dessin 2D. Aucun développement de ces fonctions n'est engagé par cette décision.

## 6. Règles de décision, livraison et suivi

- **Une seule source d'état immédiat :** [`NEXT_SESSION.md`](NEXT_SESSION.md) et le STATUS du jalon ; la roadmap ne reçoit plus les journaux R1→R15 en tête.
- **Chaque API future (M13 et suivantes) reste « proposée »** tant qu'elle ne figure pas dans un binaire et un scénario de validation identifié. Les commandes existantes M7–M12 sont disponibles uniquement dans le périmètre de leur version et de leurs tests documentés ; ne pas présenter les nouvelles fonctions de palette ou de fonte comme déjà implémentées.
- **Gates distinctes** : A = structure HUNK/AP20 + CPU/CI ; B = AMOS interprété/WinUAE ; C = AMOS Compiler ; D = Amiga AGA physique. Ne jamais transformer un préflight Python en PASS matériel.
- **Protection** : `dist/AMOSPro_AGA.Lib` = **candidate testable directement à cet emplacement**, pas de sous-répertoire ; après **Gate B WinUAE PASS utilisateur**, copier automatiquement le binaire validé dans `dist/AMOSPro_AGA_LAST_GOOD.Lib` (même contenu, test archivé) ; ne pas promouvoir une simple Gate A. Archives versionnées immuables. [Règle source](../EXTENSION_SOURCE_RULES.md).
- **Au prochain chantier** : lire [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md), le HEAD réel de `main` et les documents/status du jalon, avant de créer un builder ou un test.

**Navigation :** [index documentaire](README.md) · [architecture actuelle](ARCHITECTURE.md) · [Copper M7](M7_COPPER_DESIGN.md) · [souris / zones / collisions](INTERACTIONS_COLLISIONS.md).
