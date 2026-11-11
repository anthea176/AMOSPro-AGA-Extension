# Outils Python actifs — R35 0.10.7 Gates A/B PASS, WinUAE-LAST_GOOD

## R35 0.10.7 — Aga Fade To White : Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Contrat approuvé — seule fonction ajoutée :** `_OK=Aga Fade To White(vbl)`, durée entière 1..255 VBL (0/négatifs/>255 refusés sans modification), fondu RGB24 bloquant de tous les pens logiques de l'écran AGA Intuition privé indexé vers le **blanc exact**. Une capture source `GetRGB32` si vbl>1, interpolation signée 8.8 et un `graphics.library/WaitTOF` suivi de `LoadRGB32` par VBL, dernière image RGB32 `0xFFFFFFFF` exacte. Pas de banque AGAPAL, pixel ou fichier touché ; HAM/EHB/dual playfield rejetés, ColorMap contrôlée, tampon Exec `8+42*N` octets (max 10 760) libéré. Pas de mesure FPS ni de garantie de temps écoulé en cadence réelle. [Contrat technique R35](../docs/M13_FADE_WHITE_R35.md).

**Gate A CPU/CI PASS :** 50 scénarios natifs 68000 et export source strict PASS, [CI candidate complète 37/37 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43057572164), 41 commandes AP20.

**Gate B PASS — capture utilisateur AMOS interprété/WinUAE :** `OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 WHITE 16777215 16777215`, `WHITE2 16777215 16777215`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 16777215`, `FADE2 1 TWO 16777215`, `SAME 1 SAME28 16777215`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. L'utilisateur a confirmé « c nickel » après le fondu visible de 150 VBL, sans mesure de cadence/FPS.

**R35 promue `LAST_GOOD` à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib`, **21 300 octets**, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`. **R34 0.10.6 est préservée dans son archive** (20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`). [Test R35 exact archivé](../tests/passed/M13_R35_FADE_TO_WHITE_01.asc), Git blob `21115dfbbcff345e6ae8132c03956152b897a6b2` inchangé. **`tests/current/` sans aucun ASC actif.** Gates C Compiler/D Amiga AGA réel NON TESTÉES.

**Suite :** R35 clôturée côté WinUAE. Ne pas implémenter d'autre commande (R36 ou autre) sans discussion et accord explicite. Rester strictement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, aucune autre branche ni dépôt.

---

## R34 0.10.6 — Aga Fade To Black : Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Contrat approuvé et unique fonction ajoutée :** `_OK=Aga Fade To Black(vbl)`, durée entière 1..255 VBL (0, négatifs et >255 refusés). Fondu RGB24 **bloquant** de tous les pens logiques de l'écran AGA Intuition privé indexé vers le **noir exact**, un `graphics.library/WaitTOF` et `LoadRGB32` par étape, interpolation signée 8.8 depuis la capture `GetRGB32` ; dernière étape RGB32 nulle sans erreur d'arrondi. Aucune banque AGAPAL nécessaire, aucune écriture pixels, banques ou fichiers. Scratch Exec `8+42*N` octets (max 10 760) libéré. Refus sans effet ; retour 1 succès, 0 échec. Pas de mesure FPS ni garantie de durée réelle exacte sur 68000. [Contrat technique R34](../docs/M13_FADE_BLACK_R34.md).

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



**Outils R32 :** `m13_agapal_apply_r32_emit.py`, `build_m13_agapal_apply_r32.py` (base archive R31), `test_m13_agapal_apply_r32.py` (136 scénarios CPU PASS). Gate B AMOS interprété/WinUAE PASS, test ASC archivé ; R32 est `LAST_GOOD`.

**CI candidate R32 :** [34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040), [CI documentaire 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032630960). La promotion actualise les assertions sur `LAST_GOOD` sans modifier les archives ni le code 68000.

## R31 0.10.3 VALIDÉE — AGAPAL Capture WinUAE PASS (11/11/2026)

**Gate A :** 107 scénarios CPU 68000 PASS, export 68000 strict PASS, [CI candidate 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43027906298). **Gate B AMOS interprété/WinUAE : PASS** sur `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED` et fin propre. **Gates C Compiler / D matériel réel NON TESTÉES**.

**ABK utilisateur inspecté :** `R31_AGAPAL_CAPTURE.ABK` (6 244 octets) = `AmBk` + `AGAPAL` v1 6 224 octets, 8 emplacements, 0/1 contenant 256 couleurs RGB24 (pen 28 bleu/rouge), 2 à 7 vides, pens 3/224 préservés. SHA256 du fichier fourni : `7a3162969b0d700287ae0852872811dae072c19720a794beb8818d01b93f6cd9`.

**R31 promue :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive versionnée R31, 18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`. Archive R30 conservée, inchangée. ASC de test **archivé octet pour octet** (Git blob `0196fc1ba730345a926f444691be80c16a7fb89c`) dans `tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`. [CI de promotion 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43029502969). Pas d'autre commande avant discussion et accord utilisateur.

---


## R30 0.10.2 — AGAPAL Bank Init validée Gate B AMOS/WinUAE

**Gate B PASS confirmé par capture utilisateur le 11/11/2026 :** `INIT 1 REINIT 1`, `HEADER AGAPAL V 1 COUNT 8`, `OFFSET0 80 OFFSET7 5456`, `BAD0 0 BAD257 0 BADSIZE 0`, `SENTINEL 99 ZERO 0`, `ABK RESTORED AGAPAL SIZE 6224`, `REST0 80 REST7 5456 INDEX 1`, **`RESULT 1`**, **`CLOSE RETURNED`**. Fonction `_OK=Aga Palette Bank Init(Start(bank),N)` validée sur le scénario : banque DATA AMOS et rechargement ABK natif, aucun changement d'écran. **Gates C Compiler et D Amiga physique : non testées**.

**R30 promue :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib`, **17 824 octets**, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`. Archive R29 conservée sans changement. Test corrigé archivé **sans modification**, blob Git `646aa30fb61dfb2ff6b9f5bc5dfe47d8365b2964` : [`tests/passed/M13_R30_AGAPAL_BANK_INIT_01.asc`](../tests/passed/M13_R30_AGAPAL_BANK_INIT_01.asc). `tests/current/` ne contient plus de test actif. Gate A 39 cas 68000 et [CI 32/32 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43024446890). CI de promotion **32/32 PASS**.

**Rappel :** l'erreur `Type mismatch` du premier essai était dans l'ASC de test ; elle a été corrigée en remplaçant `_STILL` par `_STILL$`. La R30 binaire n'a pas changé. Capture/import de palettes, fades et cycling sont encore **à discuter individuellement avant programmation**.

---




## R29 0.10.1 VALIDÉE — Gate A + Gate B AMOS/WinUAE PASS, 11/11/2026

**Preuves utilisateur :** test `M13_R29_PALETTE_SAVE_01.asc` exécuté sous AMOS interprété/WinUAE : `OPEN 1 DB 1`, `DRAW 1 1 1 1`, `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. L'utilisateur confirme également l'ouverture de la palette IFF produite avec ses **256 couleurs dans Cloanto Personal Paint (PPaint)** ; le fichier ne contient pas de pixels `BODY`. Cela établit l'interopérabilité **pour ce fichier et cet essai**, pas tous les éditeurs IFF.

**Promotion obligatoire :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib`, **R29 0.10.1**, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, octet pour octet. L'archive R28 est figée et conservée. Le fichier de test original (Git blob `b80baabe5533288cac3285a78c232827cce94085`) est déplacé **sans modification** dans `tests/passed/M13_R29_PALETTE_SAVE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`.

**Validation :** Gate A CPU 68000 **49 scénarios PASS**, [CI R29 avant promotion **30/30 PASS**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43016176793) ; Gate B interprété/WinUAE **PASS** sur le test et PPaint précités. **Gates C (Compiler) et D (matériel réel) NON TESTÉES**. La validation sous PPaint ne démontre pas l'affichage des pixels puisque le format est volontairement sans `BODY`.

**Suite M13 :** fonctions de banques de palettes (Fast RAM privilégiée) et fades natifs `Aga Fade To Bank/Black/White`, puis cycling. **Avant chaque nouvelle fonction, discuter et valider son contrat avec l'utilisateur ; aucune implémentation anticipée.**

---

**Outils R31 :** `m13_agapal_capture_r31_emit.py` (68000), `build_m13_agapal_capture_r31.py` (candidate reproductible depuis R30), `test_m13_agapal_capture_r31.py` (107 scénarios CPU). R31 en Gate A PASS ; test WinUAE actif, R30 toujours `LAST_GOOD`.

**Outils R30 :** `m13_agapal_r30_emit.py` (68000), `build_m13_agapal_r30.py` (reproductible depuis R29), `test_m13_agapal_r30.py` (39 scénarios CPU). La candidate R30 est à tester sous WinUAE ; R29 reste `LAST_GOOD`.

**Outils R29 :** [`m13_palette_save_r29_emit.py`](m13_palette_save_r29_emit.py) (routines 68000 `Aga Palette Save`), [`build_m13_palette_save_r29.py`](build_m13_palette_save_r29.py) (builder reproductible mémoire depuis R28), [`test_m13_palette_save_r29.py`](test_m13_palette_save_r29.py) (49 scénarios CPU natifs et roundtrip R28). La CI couvre R29 et les régressions R28–R10.


## R28 validée — 11/11/2026

M13/R28 0.10.0 : Gate A 159 cas 68000 PASS, CI précédente 29/29 PASS ; Gate B AMOS interprété/WinUAE PASS sur la capture M13-R28-PALETTE-01 du 11/11/2026. Résultats : OPEN/DB/IFF CMAP/SET/DRAW/SWAP = 1 ; BAD 0 BADG -1 ; PEAK 16254720 ($F80700), FINAL 65280 ($00FF00), FADEERR 0, CLOSED -1, RESULT 1, CLOSE RETURNED. Le test AMOS sélectionne un IFF sans que son chemin soit connu depuis la capture ; la compatibilité d'un export palette seule PPaint/DPaint réel n'est donc pas établie. Le résultat numérique n'atteste pas à lui seul l'observation visuelle complète des 64 transitions. Gate C Compiler et Gate D Amiga réel non testées.

**Bibliothèques :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` sont des copies binaires identiques de l'archive `dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib` : 16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`. R27 reste figée dans `dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib` (SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`). Test original déplacé octet pour octet : `tests/passed/M13_R28_PALETTE_01.asc`; aucun test ASC actif.

**Suite autorisée M13 :** palette sauvegardable au format standard IFF FORM ILBM/CMAP, sauvegarde/restauration, fade natif, puis cycling ; incréments séparés et Gate A avant toute nouvelle candidate. M14 fontes et M15 dessin 2D restent ultérieurs.

---

**Descriptions de prévalidation R28 et antérieures conservées ci-dessous pour historique ; elles ne reflètent pas la bibliothèque actuelle.**

## M13 — R28 0.10.0 standard IFF palette (Gate A CPU 159 PASS ; Gate B non testée)

- [`m13_palette_r28_emit.py`](m13_palette_r28_emit.py) : charge CMAP sans modifier BODY, `Palette Set` par `LoadRGB32`, `Palette Get` par `GetRGB32` ; contrôles ColorMap/count/bitplanes, RGB8 et modes HAM/EHB.
- [`build_m13_palette_r28.py`](build_m13_palette_r28.py) : builder **en mémoire** depuis l'archive R27 WinUAE-PASS, 3 fonctions AP20 ajoutées en fin de HUNK, ancien code conservé ; `--emit-base64` pour audit après PASS.
- [`test_m13_palette_r28.py`](test_m13_palette_r28.py) : **159 cas CPU 68000 PASS** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43004699618)) ; IFF palettes seules `FORM ILBM/CMAP` avec ou sans BMHD/CRNG, IFF images ordinaires sans écriture BODY, ABI, RGB32, HUNK AP20 et nettoyage des ressources.
- [Contrat M13/R28](../docs/M13_PALETTE_R28.md) · [candidate prête à l'emploi : `dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) · [archive versionnée](../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib), 16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c` · [test WinUAE actif](../tests/current/M13_R28_PALETTE_01.asc). **R28 Gate B non testée ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R27 0.9.3 validée WinUAE.** Une version validée est immédiatement promue en `LAST_GOOD` après confirmation utilisateur. Sauvegarde IFF standard, fades et cycling restent à réaliser.

## M12 — R27 Safe Blitters (Gate A CPU/CI 403 cas PASS et Gate B AMOS/WinUAE 40 swaps PASS)

- [`m12_blit_safe_r27_emit.py`](m12_blit_safe_r27_emit.py) : même garde `GetMsg(SafePort)` non bloquante avant DMA dans Copy/Fill, préserve `D6`/ABI et le bit Disp.
- [`build_m12_blit_safe_r27.py`](build_m12_blit_safe_r27.py) : builder en mémoire depuis R26 archivée ; **R27 0.9.3 est maintenant `dist/AMOSPro_AGA_LAST_GOOD.Lib`**, octet-identique à [son archive versionnée](../dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib), 14 252 octets, SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe` ; 31 commandes, neuf segments modifiés. **`dist/AMOSPro_AGA.Lib` = R28 candidate**, sans sous-répertoire.
- [`test_m12_blit_safe_r27.py`](test_m12_blit_safe_r27.py) : **403 scénarios CPU 68000 PASS** dont Copy/Fill/Clear Safe/Disp, aucun DMA après rejet, ABI, BSR Clear et relocations clavier/souris R23 ; [CI finale 28/28 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997575220). **Gate B AMOS/WinUAE PASS** sur [40 swaps originaux archivés](../tests/passed/M12_R27_SAFE_BLIT_01.asc).
- [Rapport M12, captures et réserves](../docs/M12_SAFE_BLITTER_R27.md) · [test WinUAE archivé sans modification](../tests/passed/M12_R27_SAFE_BLIT_01.asc) : `DONE 40 C 14 F 13 P 13`, `RESULT 1`, clignotement des rectangles. **C'est la dernière version Gate B PASS, donc `LAST_GOOD` R27.** Le test M13 R28 est maintenant le seul actif et attend Gate B ; Compiler et Amiga réel non testés.


## M11 — R26 `Aga Text` 0.9.2 : validation WinUAE initiale et multi-swap 40 images PASS

- [`build_m11_text_r26.py`](build_m11_text_r26.py) : builder **en mémoire** reproductible depuis R25 figée ; **à la clôture de R26**, la candidate `dist/AMOSPro_AGA.Lib` était égale à [l'archive R26](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib), SHA256 `0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287`. Il ne modifie aucun binaire en étant exécuté.
- [`m11_text_r26_emit.py`](m11_text_r26_emit.py) : nouvelle routine 68000 `TextExtent` + `InitRastPort` + `Text`, sécurité Safe/Disp non bloquante sans `WaitPort` ni `ReplyMsg`.
- [`test_m11_text_r26.py`](test_m11_text_r26.py) : **64 cas CPU 68000 PASS** (ABI, back buffer, Safe/Disp, clipping) lors de la [CI R26 complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42922291061). **Gate B AMOS/WinUAE PASS** sur le [test R26 original archivé](../tests/passed/M11_R26_AGA_TEXT_01.asc), texte vert visible sur fond bleu, `RESULT 1`, fermeture propre.
- [Contrat et résultats R26](../docs/M11_TEXT_R26.md) · [test texte initial PASS](../tests/passed/M11_R26_AGA_TEXT_01.asc) · [test multi-swap PASS archivé](../tests/passed/M11_R26_SAFE_SWAP_02.asc). **40 alternances A/B confirmées**, `PROBE0 39 SWAP0 0`, toutes erreurs nulles, `RESULT 1`. `tests/current/` ne contient aucun `.asc` après archivage du test R27. La R26 et les archives R25/R24/`LAST_GOOD` R10 restent inchangées ; Compiler, matériel réel et longue durée non testés.

### Historique de conception M11 (avant l'implémentation R26 ; non applicable à l'état courant)


- Le diagnostic [`M11_R25_AMOS_TEXT_01.asc`](../tests/historical/M11_R25_AMOS_TEXT_01.asc), qui supposait que `Text` AMOS viserait notre écran Intuition AGA, a été **écarté avant exécution WinUAE** et classé historique sans modification des octets.
- **Aucun test actif** dans `tests/current/`. La prochaine étape est une inspection en lecture seule de la source R25 : `BitMap` du back buffer, `RastPort`, `Aga Swap` et cycle de vie. Envisager `graphics.library/Text` seulement avec une cible graphique explicitement liée à ce back buffer. [Étude](../docs/M11_TEXT_COMPAT.md).
- Aucun builder R26 créé. Binaires R25/R24, `LAST_GOOD` R10 et archives `tests/passed/` intacts.


## M10 — R25 0.9.1 : collisions AABB (Gate A CPU/CI + Gate B WinUAE PASS sur scénario)

- [Émetteur natif 68000](m10_rect_overlap_r25_emit.py) : huit entiers, `D3=bh` et `A3+28`, aucun état/OS, arithmétique signée 32 bits sans `x+w` dangereux.
- [Builder reproductible, sans écriture](build_m10_rect_overlap_r25.py) depuis l'archive validée R24 et [préflight CPU](test_m10_rect_overlap_r25.py) : cas de bords, un pixel, inclusions, tailles invalides, extrêmes, symétrie et non-régression R24.
- [Test AMOS visuel R25 archivé et validé](../tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) · [contrat R25](../docs/M10_RECT_OVERLAP_R25.md). Rectangle bleu fixe, mobile vert/rouge ; `FRAMES 409`, `DRAWERR 0`, `RESULT 1`, fermeture correcte. **Gate A CPU/CI PASS 704 cas** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42916575209)), **Gate B AMOS/WinUAE PASS** sur le scénario utilisateur. Aucun `.asc` actif dans `tests/current/`. CI et contrôle statique ne valent pas validation du Compiler ou du matériel.

## M9 — R24 0.9.0 : Hotspot Hit (Gate A CPU/CI + Gate B WinUAE PASS)

- [Émetteur pur 68000](m9_hotspot_r24_emit.py) : six paramètres, bords fin exclusive, arithmétique 32 bits sans débordement, aucun état ni appel OS.
- [Builder pur R24](build_m9_hotspot_hit_r24.py) : depuis R23 **archivée et validée**, ajout d'une seule entrée AP20 + séparateur `GetP`. `dist/AMOSPro_AGA.Lib` candidate R24 et son archive sont comparées en CI.
- [Test CPU préflight](test_m9_hotspot_hit_r24.py) : contrôles 68000 ABI/A3, frontières, zones superposées, int32, R23 inchangée. **Gate A CPU/CI PASS 402 cas (CI (archive CI privée, run #42908096685)), Gate B WinUAE PASS sur le test R24 archivé.** [Contrat](../docs/M9_HOTSPOT_R24.md) · [test WinUAE exact](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc).

## M8 — R23 0.8.7 : IDCMP clavier/souris (Gate A + B PASS sur scénarios testés)

- [`m8_idcmp_r23_emit.py`](m8_idcmp_r23_emit.py) : dispatcher 68000 non bloquant des messages `IDCMP_MOUSEBUTTONS` et `RAWKEY`, FIFO clavier 16 places.
- [`build_m8_idcmp_r23.py`](build_m8_idcmp_r23.py) : builder **pur**, depuis l'archive R22 PASS, reconstruit la candidate R23 sans écrire les archives. Mode `--emit-base64` réservé à la vérification de l'artifact.
- [`test_m8_idcmp_r23_preflight.py`](test_m8_idcmp_r23_preflight.py) : couverture CPU/emulateur native de la capture des clics courts et de la préservation des touches, sans preuve WinUAE.
- [Contrat R23](../docs/M8_IDCMP_R23.md) · [test WinUAE exact archivé](../tests/passed/M8_R23_IDCMP_QUICK_01.asc). **Gate A CPU/CI PASS (15 cas, CI (archive CI privée, run #42899343161)), Gate B WinUAE PASS** sur clics rapides, FIFO clavier et Ctrl+C à `_WAITK=Aga Wait Key` avec fermeture Intuition. Archive R22 et `LAST_GOOD` R10 inchangées ; Compiler/hardware/stress non testés.

## M8 — R22 0.8.6 : transitions souris natives (CPU + WinUAE PASS sur scénario)

- `m8_mouse_edges_emit.py` : génération déterministe des routines 68000 `Aga Mouse Pressed/Released`, fronts indépendants et contrôle du focus sans toucher à la file clavier.
- `build_m8_mouse_edges_r22.py` : construction reproductible depuis l'archive R21, deux entrées AP20 nouvelles, petite réinitialisation sur ouverture d'écran ; archives et LAST_GOOD inchangées.
- `test_m8_mouse_edges_r22.py` : tests CPU 68000, ABI, états sticky, clavier intact, focus, refus et réouverture.
- [Contrat R22](../docs/M8_MOUSE_EDGES_R22.md) · [test AMOS validé et archivé](../tests/passed/M8_R22_MOUSE_EDGES_01.asc). Gate A/CI PASS (25 scénarios, CI (archive CI privée, run #42893816454)) ; Gate B WinUAE PASS sur capture utilisateur.

## M8 — R21 0.8.5 RMBTRAP (CPU/CI PASS 11 cas ; WinUAE PASS utilisateur)

- `build_m8_rmbtrap_r21.py` : builder depuis R20 archivée, change **un seul octet** de code dans `NewWindow.Flags` de `Aga Screen Open` ; R21 archivée, R22 courante sur `main`.
- `test_m8_rmbtrap_r21.py` : simule CPU 68000 et intercepte les flags transmis à `OpenWindow()`; contrôle régressions des boutons R20 et autres segments immuables.
- [Dossier technique R21](../docs/M8_RMBTRAP_R21.md) · [test AMOS archivé](../tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc).

## M8 — R20 0.8.4 Mouse Buttons (CPU/CI PASS 21 cas ; WinUAE boutons OK mais menu Intuition défectueux)

- `build_m8_mouse_buttons_r20.py` : nouveau builder depuis l'archive R19 figée, ne modifie que l'entrée 29 (`GetP`) et ajoute l'entrée 30 `Aga Mouse Buttons` ; `dist/AMOSPro_AGA.Lib` R20 figée (builder historique ne réécrit pas la candidate R21).
- `test_m8_mouse_buttons_r20.py` : tests CPU 68000 sous Unicorn (appels input.device simulés, masques, ABI/SP, erreurs, R19 inchangé).
- [R20 boutons](../docs/M8_MOUSE_BUTTONS_R20.md), [test AMOS historique](../tests/historical/M8_R20_MOUSE_BUTTONS_01.asc).
- **R19 reste archivée :** ne plus exécuter son builder historique en écriture de `dist/` R20 ; la fonction pure `build()` est conservée pour les tests.

## M8 — R19 0.8.3 Mouse X/Y, PASS CPU/CI et AMOS interprété/WinUAE

- `build_m8_mouse_position_r19.py` — builder historique R19 (archive figée) depuis l'archive R18 figée ; reproduit R19 sans écraser la bibliothèque R21 de `main`.
- `test_m8_mouse_position_r19.py` — 76 cas CPU 68000 **PASS et CI générale PASS** (CI générale #42878271256 (archive CI privée)) : coordonnées signées, 320/640/1280, fenêtres déplacées, écran fermé, écran étranger, ABI D3/D2/A3/SP.
- `test_amos_copper_syntax.py` — contrôle statique étendu aux appels nus des fonctions `Aga Mouse X/Y` ; elles doivent être utilisées dans une expression.
- [`M8_MOUSE_R19.md`](../docs/M8_MOUSE_R19.md), [`M8_STATUS.md`](../docs/M8_STATUS.md) — spécification de l'API et procédure WinUAE.

## M7 — R18 0.8.2 Copper Wait/Move/End, PASS CPU/CI et WinUAE (archivé)

- `m7_copper_contract.py` — API de validation Python pour une liste utilisateur de 64 instructions au maximum : `Clear/Wait/Move/End/On/Off` ; autorise seulement COLOR00..COLOR31, RGB4 et les WAIT bornés. **Aucun code Amiga n'est exécuté.**
- `test_m7_copper_contract.py` — tests de grammaire, limites et erreurs ; **pas une preuve 68000/WinUAE**.
- `test_amos_copper_syntax.py` — vérification automatisée : les fonctions Copper AP20 doivent apparaître dans une expression et non comme instructions isolées.
- `build_m7_copper_raster_r18.py` — builder **historique R18**, régénère uniquement son archive validée ; l'appel direct n'écrase plus la Lib R19 courante.
- `test_m7_copper_raster_r18.py` — 26 scénarios CPU 68000 Gate A PASS (ABI/A3, WAIT croissants, COLOR00..31, CEND, refus de liste active). **Gate B WinUAE PASS** sur le test raster corrigé.
- `build_m7_copper_on_off_r17.py` — builder **historique R17**, ne doit plus écraser le candidat R18 ; conserve sa propre archive.
- `test_m7_copper_on_off_r17.py` — tests CPU Intuition MakeScreen/RethinkDisplay, propriétaires, retour ABI, cas d'erreur, retrait et libération.
- `build_m7_copper_clear_r16.py` — builder **historique R16** depuis R15, désormais limité à la régénération de son archive ; ne doit pas écraser l'actif R18.
- `test_m7_copper_clear_r16.py` — test CPU/ABI 68000, simulation OS, pointeurs Screen, allocation et chemins d'échec ; **ne prouve pas WinUAE**.
- Références : [`M7_COPPER_R18.md`](../docs/M7_COPPER_R18.md), [`M7_COPPER_R17.md`](../docs/M7_COPPER_R17.md), [`M7_STATUS.md`](../docs/M7_STATUS.md), [`M7_COPPER_R16.md`](../docs/M7_COPPER_R16.md) et [`M7_COPPER_DESIGN.md`](../docs/M7_COPPER_DESIGN.md).

## Rappel — M6 R15 validé

La racine de `tools/` conserve les builders, tests CPU et outils génériques utilisés ; les anciennes versions restent dans `obsolete/`.

## M6 — R15 Clear validé sous AMOS interprété/WinUAE

- `build_m6_blit_clear_r15.py` — génère le candidat R15 `dist/AMOSPro_AGA.Lib` et son archive R15 depuis **l'archive R14 figée**, sans modifier les versions validées.
- `test_m6_blit_clear_r15.py` — CPU 68000, wrapper A3+12, BSR vers Fill, contenu pixel par pixel, rejets, non-régression R14 Fill et R13 Copy.
- `build_m6_blit_fill_r14.py` — builder **historique R14**, toujours reproductible depuis R13 archivée ; son exécution en ligne de commande ne doit plus écraser le candidat R15.
- `test_m6_blit_fill_r14.py` — contrôles CPU 68000, bitplanes, couleur, bounds, masques, minterms, ABI et sauvegarde de Copy.
- `build_m6_blit_copy_r13.py` — ancien builder R13, conservé pour reproduire la version **déjà validée** de Copy depuis R12 archivée ; ne pas l'exécuter directement comme livraison active R14.
- `test_m6_blit_copy_r13.py` — CPU 68000 (Unicorn), ABI A3/GetP, géométrie, sélection back buffer, appel BltBitMap et WaitBlit. Ce n'est pas une validation graphique sous WinUAE.
- `.github/workflows/artifact-integrity.yml` — vérifie R15, reconstruit le candidat actif, rejoue les tests CPU R14/R13 et contrôle la protection des archives / `LAST_GOOD`.

## M5 — R12 stable et références

- `build_newscreen_a0_r12.py`, `build_ntsc_pal_r10.py`, `ap20_utils.py`, `audit_ap20.py` : construction et vérification R12/R10.
- `test_newscreen_a0_r12.py`, `test_ntsc_pal_r10.py`, `verify_artifacts.py`, `check_no_blocking_waits.py` : contrôles d'intégrité.
- `validate_ilbm.py`, `build_m5_generic.py`, `build_m5_generic_r2.py`, `m68k_emit.py`, `test_m5_generic.py`, `test_m5_generic_r2.py` : composants génériques IFF/CPU.
- `inspect_winuae_dump.py` : diagnostic WinUAE.

`tools/obsolete/` conserve les anciennes générations. Ne pas promouvoir ni écraser la R10 `LAST_GOOD`. Consulter [les détails du R15 Clear](../docs/M6_BLITTER_R15.md), avec R14 Fill et R13 Copy déjà validés sous WinUAE.
