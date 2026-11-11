# Tests AMOS — R33 0.10.5 validée Gate A CPU/CI et Gate B fonctionnelle AMOS/WinUAE

## R33 0.10.5 VALIDÉE — Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Nouvelle fonction :** `_OK=Aga Fade To Bank(Start(bank),index,vbl)`. Fondu RGB24 **bloquant** sur 1..255 VBL ; `WaitTOF` puis `LoadRGB32` par image, interpolation 8.8 signée, **dernière image RGB24 exacte**. Uniquement les pens 0..compte-1 sont modifiés ; banques/pixels et pens supérieurs restent inchangés. `vbl=0` refusé ; pour une application immédiate utiliser `Aga Palette Bank Apply`. Requiert une banque DATA AGAPAL **vivante** (`Start(bank)` réel), une palette non vide et un écran AGA indexé privé. Scratch Exec temporaire `8+42*N` (10 760 octets max), libéré. Les VBL ne garantissent pas une durée réelle stricte si le calcul dépasse une trame.

**Gate A :** 51 scénarios CPU natifs 68000 PASS, export source 68000 strict PASS, **[CI de publication 35/35 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43045308067)**, 39 commandes AP20.

**Gate B fonctionnelle PASS — capture utilisateur WinUAE/AMOS interprété :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `FADE0 1 GREEN 65280`, `FADE1 1 BLUE 255 SAME 1 255`, `PART 1 PEN3 660510 PEN28 16711680`, `BAD0 0 BAD256 0 BADNEG 0`, `BADINDEX 0 EMPTY 0 BADSIZE 0`, `AFTERBAD 16711680 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 BLUE 255`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 141**. Le test confirmait les couleurs finales et les rejets, **pas la qualité visuelle ni la fluidité du fondu** : son `Aga Swap` et `Amos To Back` étaient exécutés APRÈS les transitions, et celles-ci duraient surtout 12/1/2 VBL. **Démo distincte** [`examples/fade_to_bank_r33.asc`](examples/fade_to_bank_r33.asc) : affiche d'abord trois grandes bandes, puis rouge → vert → bleu → rouge en 150 VBL avec des pauses. Démo **validée visuellement sous WinUAE par l'utilisateur le 11/11/2026 : fondu visible et fonctionnel**, sans mesure de cadence, FPS ou durée réelle.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R33 `dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib`, **20 208 octets**, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`, strictement identiques. R32 préservée intacte en archive (19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`). ASC fonctionnel archivé à l'octet près : [`tests/passed/M13_R33_AGAPAL_FADE_01.asc`](passed/M13_R33_AGAPAL_FADE_01.asc). Aucun ASC actif dans `tests/current/`. Gates C (Compiler) et D (Amiga AGA physique) **NON TESTÉES**.

**Suite :** observation visuelle positive enregistrée ; ne pas prétendre à une mesure de fluidité, FPS ou cadence sans instrumentation. Toute prochaine fonction doit être discutée et approuvée avant le codage ; mettre à jour les deux README et rester strictement sur `main`, sans autre branche/dépôt.

---
**Gate B WinUAE confirmée par capture utilisateur :** le test [`passed/M13_R32_AGAPAL_APPLY_01.asc`](passed/M13_R32_AGAPAL_APPLY_01.asc) est archivé sans modification de son contenu. Résultats observés : `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `AP0 1 AP1 1 PART 1`, `GREEN 65280 RED 16711680 BLUE 255`, `PEN224 795192 PART3 660510 PART28 255`, `BADNEG 0 BAD8 0 EMPTY 0`, `BADSIZE 0 BADCOUNT 0`, `AFTERBAD 255 AFTERCOUNT 255`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 16711680 PART 1`, `REST3 660510 REST28 16711680`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale ligne 161.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R32 0.10.4, **19 244 octets**, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`. Gate A 136 scénarios CPU 68000 PASS et [CI candidate 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040). **Gates C Compiler et D matériel réel NON TESTÉES.** R31 conservée dans son archive. Aucun `.asc` actif sous `tests/current/`.

---


**CI de la candidate R32 publiée :** [34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040) après SHA256/AP20, export 68000 strict, test ASC statique, 136 scénarios CPU et régressions historiques. **R31 reste `LAST_GOOD` jusqu'à Gate B WinUAE R32.**

**Tests R31 et antérieurs ci-dessous : validations historiques.**

# Tests AMOS — R31 0.10.3 validée WinUAE

## R31 0.10.3 VALIDÉE — AGAPAL Capture WinUAE PASS (11/11/2026)

**Gate A :** 107 scénarios CPU 68000 PASS, export 68000 strict PASS, [CI candidate 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43027906298). **Gate B AMOS interprété/WinUAE : PASS** sur `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED` et fin propre. **Gates C Compiler / D matériel réel NON TESTÉES**.

**ABK utilisateur inspecté :** `R31_AGAPAL_CAPTURE.ABK` (6 244 octets) = `AmBk` + `AGAPAL` v1 6 224 octets, 8 emplacements, 0/1 contenant 256 couleurs RGB24 (pen 28 bleu/rouge), 2 à 7 vides, pens 3/224 préservés. SHA256 du fichier fourni : `7a3162969b0d700287ae0852872811dae072c19720a794beb8818d01b93f6cd9`.

**R31 promue :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive versionnée R31, 18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`. Archive R30 conservée, inchangée. ASC de test **archivé octet pour octet** (Git blob `0196fc1ba730345a926f444691be80c16a7fb89c`) dans `passed/M13_R31_AGAPAL_CAPTURE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`. [CI de promotion 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43029502969). Pas d'autre commande avant discussion et accord utilisateur.

---


**Les tests R30 et antérieurs ci-dessous sont historiques.**

# Tests AMOS — R30 0.10.2, Gate A + Gate B WinUAE PASS

**Test validé et archivé :** [`passed/M13_R30_AGAPAL_BANK_INIT_01.asc`](passed/M13_R30_AGAPAL_BANK_INIT_01.asc) (blob Git exact `646aa30fb61dfb2ff6b9f5bc5dfe47d8365b2964`). Sortie AMOS/WinUAE `INIT 1 REINIT 1`, `HEADER AGAPAL V 1 COUNT 8`, `OFFSET0 80 OFFSET7 5456`, `BAD0 0 BAD257 0 BADSIZE 0`, `SENTINEL 99 ZERO 0`, `ABK RESTORED AGAPAL SIZE 6224`, `REST0 80 REST7 5456 INDEX 1`, `RESULT 1`, `CLOSE RETURNED`. Le `Type mismatch` du premier essai provenait du test, corrigé avant validation.

**Bibliothèques courante, archive et LAST_GOOD :** R30 0.10.2, **17 824 octets**, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`, copies strictement identiques. R29 conservée en archive. Gate A : 39 cas CPU + CI [32/32 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43024446890). **Gate B : PASS sur ce scénario. Gates C Compiler/D matériel réel : non testées.** Plus aucun ASC actif dans `tests/current/`.

---


**R29 et états antérieurs ci-dessous sont historiques.**

# M13 R29 0.10.1 — Palette Save : Gate A + Gate B WinUAE PASS (11/11/2026)

**Test utilisateur archivé à l'octet près :** [`passed/M13_R29_PALETTE_SAVE_01.asc`](passed/M13_R29_PALETTE_SAVE_01.asc), Git blob `b80baabe5533288cac3285a78c232827cce94085`. Sortie WinUAE : `OPEN 1 DB 1`, `DRAW 1 1 1 1`, `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. **Personal Paint a chargé la palette IFF 256 couleurs**, sans données pixels BODY.

**Bibliothèques :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R29 0.10.1, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1` ; R28 conservée dans son archive. **Gate A : 49 scénarios CPU PASS et [CI 30/30 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43016176793). Gate B : PASS sur le scénario ci-dessus. Gates C/D non testées.** Aucun `.asc` actif dans `tests/current/`.

---

**Les rapports R28 et antérieurs ci-dessous sont historiques ; ne pas interpréter leur statut de `LAST_GOOD` comme courant.**

# M13 R28 — Gate B WinUAE PASS (11/11/2026)

M13/R28 0.10.0 : Gate A 159 cas 68000 PASS, CI précédente 29/29 PASS ; Gate B AMOS interprété/WinUAE PASS sur la capture M13-R28-PALETTE-01 du 11/11/2026. Résultats : OPEN/DB/IFF CMAP/SET/DRAW/SWAP = 1 ; BAD 0 BADG -1 ; PEAK 16254720 ($F80700), FINAL 65280 ($00FF00), FADEERR 0, CLOSED -1, RESULT 1, CLOSE RETURNED. Le test AMOS sélectionne un IFF sans que son chemin soit connu depuis la capture ; la compatibilité d'un export palette seule PPaint/DPaint réel n'est donc pas établie. Le résultat numérique n'atteste pas à lui seul l'observation visuelle complète des 64 transitions. Gate C Compiler et Gate D Amiga réel non testées.

Test exact : [`passed/M13_R28_PALETTE_01.asc`](passed/M13_R28_PALETTE_01.asc) (Git blob original `1004a700484be2407e860ce7233826825471e91b`). `tests/current/` ne contient plus d'ASC. `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R28 (16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`). R27 conservée dans son archive versionnée.

---

**Checkpoint historique ci-dessous (avant validation de R28) :**

# M13 R28 0.10.0 — palette IFF/ILBM CMAP (Gate A PASS, Gate B WinUAE NON TESTÉE)

**Test courant :** [`M13_R28_PALETTE_01.asc`](current/M13_R28_PALETTE_01.asc). La candidate [R28 0.10.0](../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib) (16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`) passe **159 cas CPU 68000 Gate A** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43004699618)), dont les variantes IFF palettes seules avec `BMHD` et `CRNG`, sans `BODY`. **Aucune validation WinUAE R28 n'a été effectuée.**

**Import standard :** choisir un fichier palette exporté par Personal Paint/Deluxe Paint (`FORM ILBM` + `CMAP`), ou `examples/demo.iff` pour un IFF image complet. Le test ouvre l'écran AGA en 320×256×8 plans indépendamment du fichier source, **dessine avant `Aga Palette Load`**, puis teste `Aga Palette Set/Get` et la transition vert → rouge → vert sur 64 VBL. Il n'appelle ni `Aga Pic Info` ni `Aga Iff Load`. [Procédure complète](current/README.md) · [contrat M13](../docs/M13_PALETTE_R28.md).

**Le binaire courant du dépôt est [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) = R28 0.10.0**, prêt à être installé tel quel (aucun renommage ni sous-dossier). **`dist/AMOSPro_AGA_LAST_GOOD.Lib` = R27 0.9.3, dernière version WinUAE-PASS** ; R10 archivée. Une version passe en `LAST_GOOD` automatiquement **après confirmation Gate B**, jamais sur CPU/CI seuls.

---

# M12 R27 0.9.3 — Blitters Safe : Gates A+B PASS

**11/11/2026 — AMOS interprété/WinUAE : Gate B PASS sur le protocole des 40 swaps.** Le [test original `M12_R27_SAFE_BLIT_01.asc`](passed/M12_R27_SAFE_BLIT_01.asc) a été archivé dans `tests/passed/` **octet pour octet** depuis `tests/current/` (Git blob `3b3a6d8c120b1ec066669231d382eae6e0e4bd82`). **Aucun `.asc` actif**. Bibliothèque **R27 0.9.3 corrigée**, SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`, 14 252 octets. **Gate A : 403 cas CPU 68000 PASS**, CI de publication [28/28 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997575220).

**Capture utilisateur et observation des rectangles clignotant visiblement :**

```text
M12-R27-SAFE-BLIT-01
IMAGE 320 X 256 PLANES 8
OPEN 1 DB 1 LOAD 1
DONE 40 C 14 F 13 P 13
C0 13 F0 13 P0 13 SWAP0 0
SAFEERR 0 SWAPERR 0 DRAWERR 0
CLOSED -1 RESULT 1
CLOSE RETURNED
```

Clear, Fill et Copy ont réussi 14/13/13 opérations respectivement en tant que **premier dessin après Swap**, **sans sonde `Aga Text`** ; chacun a également renvoyé temporairement 0 à 13 reprises, avant la reprise bornée. Les 40 swaps ont réussi sans refus et le programme est revenu normalement dans AMOS à la **ligne 167**. **Le test valide ce scénario** : chaque retour 0 ne constitue pas une preuve individuelle du motif exact Safe ; l'utilisateur a décrit les rectangles comme « clignotants », sans préciser explicitement le détail de leur alternance de couleur. Ni 50 FPS, ni stress exhaustif, ni Compiler, ni matériel AGA physique validés. [Rapport M12/R27](../docs/M12_SAFE_BLITTER_R27.md).

---

# M11 R26 — Safe/Disp multi-swap 40 images : Gate B WinUAE PASS

**11/11/2026 — validation utilisateur sous AMOS interprété/WinUAE.** Le [test original `M11_R26_SAFE_SWAP_02.asc`](passed/M11_R26_SAFE_SWAP_02.asc), Git blob `d0306efe728032cd85d126338ecc97ec674ad2c4`, a été **déplacé octet pour octet** de `tests/current/` à `tests/passed/`. La même bibliothèque **R26 0.9.2** a été utilisée ; **aucun `.asc` actif** dans `tests/current/`.

Le programme a alterné visuellement **40 images A/B (vert / rouge)**, confirmation explicite de l'utilisateur. La capture console montre :

```text
M11-R26-SAFE-SWAP-02
IMAGE 320 X 256 PLANES 8
OPEN 1 DB 1 LOAD 1
DONE 40 PROBEOK 40
PROBE0 39 SWAP0 0
SAFEERR 0 SWAPERR 0 DRAWERR 0
CLOSED -1 RESULT 1
CLOSE RETURNED
```

Le programme termine normalement à la **ligne 140**. Les 39 refus temporaires de la sonde `Aga Text` ont exercé les tentatives bornées (12 VBL au maximum par image). Les 40 appels à `Aga Swap` ont réussi sans refus. **Les 39 retours 0 ne démontrent pas individuellement qu'un message Safe était leur seule cause** : la sonde peut renvoyer 0 pour plusieurs raisons. **Gate B PASS pour ce protocole de 40 swaps**, en complément du [test de texte initial](passed/M11_R26_AGA_TEXT_01.asc) déjà PASS. Pas de mesure 50 FPS, de stress exhaustif, de validation Compiler ou d'essai sur Amiga AGA physique. Le [rapport M11](../docs/M11_TEXT_R26.md) précise ces réserves ; R26/R25/R24 et `LAST_GOOD` R10 restent inchangées.

---

# M11 R26 0.9.2 — AGA Text : Gate A CPU/CI + Gate B AMOS/WinUAE PASS

**11/11/2026 — confirmé par l'utilisateur sous AMOS interprété/WinUAE.** [Test original `M11_R26_AGA_TEXT_01.asc`](passed/M11_R26_AGA_TEXT_01.asc) **déplacé octet pour octet** depuis `tests/current/` (Git blob `2cd9acd45f17a07ac77bbd1a340aa14c628a01ad`). **Aucun `.asc` actif dans `tests/current/`.**

La capture graphique montre **`AGA TEXT R26` en vert sur un panneau bleu** (écran Intuition AGA, 320×256, 8 bitplanes). La capture console donne exactement :

```text
M11-R26-AGA-TEXT-01
IMAGE  320 X  256 PLANES  8
OPEN  1 DB  1 LOAD  1
CLEAR  1 PANEL  1
BAD  0 TEXT  1 SWAP  1
CLOSED -1 RESULT  1
CLOSE RETURNED
```

Le programme termine normalement à la ligne **74**. `BAD 0` confirme le rejet d'une chaîne débordant l'écran ; `TEXT 1`, `SWAP 1` et le rendu visuel confirment la première primitive graphique texte AGA. **Gate A : PASS 64 scénarios CPU 68000** ([CI complète R26](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42922291061)). **Gate B : PASS sur ce scénario unique**, pas de validation du Compiler, du matériel physique, des fontes alternatives, des swaps multiples ou d'un stress de la réponse Safe/Disp. R25/R24 et `LAST_GOOD` R10 inchangés. [Contrat et rapport R26](../docs/M11_TEXT_R26.md).

---

# M10 R25 — Rect Overlap : Gate A CPU/CI + Gate B AMOS/WinUAE PASS

**10/11/2026 :** test R25 validé par l'utilisateur sous AMOS interprété/WinUAE après **704 cas CPU 68000/CI PASS** ([CI R25](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42916575209)). L'original [`M10_R25_RECT_OVERLAP_VISUAL_01.asc`](passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) a été **déplacé octet pour octet** dans `tests/passed/` (blob Git `0eac65e7a92418738d9a3ea6969d131758126cfa`). **Aucun `.asc` actif** dans `tests/current/`.

**Preuve WinUAE :** `IMAGE 320 X 256 PLANES 8`, `STATIC 1 PURE 1`, `OPEN 1 DB 1 LOAD 1`, `SEEN FREE 1 HIT 1`, `FRAMES 409 DRAWERR 0`, `LAST HIT 1`, `CLOSED -1 PRESS -1`, `REOPEN 1 BASE 0 CLOSE2 -1`, **`RESULT 1`**, **`CLOSE X2 RETURNED`**. Retour normal à AMOS.

Le rectangle mobile suit la souris et passe du vert au rouge lorsqu'il chevauche le rectangle bleu ; le back buffer est redessiné à chaque image puis présenté avec `Aga Swap` et `Aga Wait Vbl`. L'IFF apporte palette/mode vidéo mais **pas** ses pixels dans l'animation. La capture ne mesure pas 50 FPS ni un test de stress. Gates C (AMOS Compiler) et D (Amiga AGA physique) **NON TESTÉES**. `LAST_GOOD` R10 et l'archive R24 sont inchangées. [Rapport R25](../docs/M10_RECT_OVERLAP_R25.md).

---

# Test M9 R24 — Hotspot Hit : Gate A + B PASS

[`passed/M9_R24_HOTSPOT_HIT_01.asc`](passed/M9_R24_HOTSPOT_HIT_01.asc) : **test exact validé sous AMOS interprété/WinUAE et archivé octet pour octet** (SHA Git `0476f20a81a8bff1bf282a37a7e3b4b710c72022`). Il s'agit du test AMOS corrigé, **sans `Then` et sans modification après le résultat**. **Aucun `.asc` actif dans `tests/current/`**.

**Résultat du 10/11/2026 :** mire 320×256×8, `STATIC=1`, `OVERLAP=20`, `PURE=1`, `OPEN=DB=LOAD=SWAP=1`, `FILLS=1/1/1`, `LEFT ID=20`, `RIGHT OUT=1`, `CLOSED=-1`, `PRESS=-1`, `REOPEN=1`, `BASE=0`, `CLOSE2=-1`, **`RESULT=1`**, `CLOSE X2 RETURNED`, fin AMOS ligne 183.

Les compteurs `LEFT COUNT=13` et `RIGHT COUNT=3` correspondent à **plusieurs clics volontaires**, comme confirmé par l'utilisateur. **Aucune répétition parasite constatée** ; ce scénario ne vérifie toutefois pas l'unicité pour un seul clic physique. Gate A CPU/CI PASS (402 cas 68000), Gate B WinUAE PASS pour ce scénario. Focus réel, stress, AMOS Compiler et Amiga physique non testés. [Dossier M9](../docs/M9_HOTSPOT_R24.md).

---

# Test R23 — IDCMP clics rapides, clavier FIFO et Ctrl+C : Gate A + B PASS

[`passed/M8_R23_IDCMP_QUICK_01.asc`](passed/M8_R23_IDCMP_QUICK_01.asc) est le **programme AMOS exact** exécuté sous WinUAE, archivé octet pour octet après validation du 10/11/2026. **Aucun `.asc` actif dans `tests/current/`**. Gate A CPU/CI PASS (15 cas, CI complète (archive CI privée, run #42899343161)).

**Scénario normal WinUAE :** mire originale 320×256×8, `PRESSED=RELEASED=3`, `AGAIN=0/0`, `KEYS=64/64/-1`, `WAIT=16` (touche A sur AZERTY), `RESULT=1`, `OPEN=DB=LOAD=SWAP=REOPEN=1` et `CLOSE X2 RETURNED`. **Scénario Ctrl+C séparé :** le programme est interrompu à `_WAITK=Aga Wait Key` et l'écran Intuition est correctement fermé, confirmation utilisateur. Cet arrêt volontaire ne produit normalement pas de `RESULT=1`.

La vérification de la disparition du menu pendant le clic droit n'a pas été documentée par une capture à l'instant du clic ; focus réel, Compiler, Amiga physique et stress non testés. [Dossier technique R23](../docs/M8_IDCMP_R23.md).

---

# R22 — Pressed/Released : Gate A + B PASS

[`passed/M8_R22_MOUSE_EDGES_01.asc`](passed/M8_R22_MOUSE_EDGES_01.asc) est le **test exact validé sous WinUAE**, déplacé sans modification. **Aucun `.asc` actif dans `tests/current/`.** Gate A CPU/CI PASS 25 cas (CI (archive CI privée, run #42893816454)), Gate B AMOS interprété/WinUAE PASS sur le scénario du 10/11/2026.

10/11/2026 — capture WinUAE utilisateur : MYGIRL.IFF 320×256×8 ; OPEN=DB=LOAD=SWAP=REOPEN=1 ; BEFORE=-1/-1 ; BASE=0/0 ; PRESSED=3, RELEASED=3, PL=PR=RL=RR=1 ; DONE=1, ERR=0, FRAME=1001 (fin de boucle For) ; KEY=64, MOUSE=(221,185) ; CLOSED=-1/-1, CLOSE2=-1, REOPEN BASE=0/0 ; CLOSE X2 RETURNED ; fin AMOS normale ligne 117. Pas de preuve visuelle de la barre Intuition pendant le clic droit. Clics très courts, perte/reprise de focus réelle, Compiler, Amiga physique et stress non testés.

[Compte rendu R22](../docs/M8_MOUSE_EDGES_R22.md).

---

# R21 — souris boutons / RMBTRAP : WinUAE PASS

**R21 0.8.5 Gate A CPU/CI PASS (11 cas)**, CI complète #42887916480 (archive CI privée). **Gate B AMOS interprété/WinUAE PASS**, sur confirmation explicite de l'utilisateur le **10/11/2026** : boutons gauche et droit opérationnels, aucune barre Intuition persistante au clic droit. La validation est verbale ; aucune capture numérique détaillée R21 n'a été fournie. Gates Compiler/Amiga réel et stress non testées.

**Test archivé octet pour octet :** [`passed/M8_R21_MOUSE_RMBTRAP_01.asc`](passed/M8_R21_MOUSE_RMBTRAP_01.asc), bandeau `M8-R21-MOUSE-RMBTRAP-01`. **Aucun test `.asc` actif dans `tests/current/`**.

**Historique :** R20 a correctement remonté `PRESSED=RELEASED=SEEN=3`, `DONE=1`, `IOERR=0`, mais ouvrait la barre de menus Intuition au clic droit. [Son test exact reste dans `historical/`](historical/M8_R20_MOUSE_BUTTONS_01.asc), pas dans `passed/`. Le défaut est corrigé par R21.


---

# Tests AMOS — R19 souris X/Y validée sous WinUAE

**R19 M8 : Gate A CPU PASS (76 cas), CI générale PASS, Gate B AMOS interprété/WinUAE PASS** le 10/11/2026. [Test archivé `passed/M8_R19_MOUSE_POSITION_01.asc`](passed/M8_R19_MOUSE_POSITION_01.asc), bandeau `M8-R19-MOUSE-POS-01`, préservé octet pour octet depuis `tests/current/`.

Deux captures WinUAE le 10/11/2026 : premier essai `P1=(112,65)`, `P2=(24,238)` ; second essai confirmatoire `P1=(0,0)`, `P2=(319,255)` sur `MYGIRL.IFF` 320×256×8. `OPEN=DB=LOAD=SWAP=REOPEN=1`, `BEFORE/CLOSED/CLOSED2=-1 -1`, `KEY=64` deux fois, `POS3=(319,255)`, `CLOSE X2 RETURNED`, retour AMOS normal ligne 87. La seconde capture lève la réserve de position du premier essai.

**Aucun `.asc` actif** dans `tests/current/` après clôture de R19. Compiler, matériel réel et stress non testés. Les validations M5/M6/M7 ci-dessous restent acquises dans leurs périmètres.

---

## M6 Blitter : Copy / Fill / Clear — PASS AMOS/WinUAE

**Clôture du périmètre M6 sous AMOS interprété/WinUAE le 10/11/2026.** Les trois tests M6 ci-dessous sont archivés dans `tests/passed/` ; **aucun test M6 actif** (un test **M8/R19** est aujourd'hui dans `tests/current/`).

| Fonction | Bibliothèque | Test validé et archivé | Résultat utilisateur |
|---|---|---|---|
| `Aga Blit Copy` | R13 0.7.0 | [`M6_R13_BLIT_COPY_01.asc`](passed/M6_R13_BLIT_COPY_01.asc) | Deux copies, `COPY1 1 COPY2 1 BAD 0`, `SWAP 1 KEY 68 CLOSE RETURNED` |
| `Aga Blit Fill` | R14 0.7.1 | [`M6_R14_BLIT_FILL_01.asc`](passed/M6_R14_BLIT_FILL_01.asc) | Trois zones remplies ; `F1 1 F2 1 F0 1`, `COL 0 RECT 0`, `COPY 1 SWAP 1`, `KEY 64 CLOSE RETURNED`, fin ligne 77 |
| `Aga Blit Clear` | **R15 0.7.2** | [`M6_R15_BLIT_CLEAR_01.asc`](passed/M6_R15_BLIT_CLEAR_01.asc) | Deux rectangles avec intérieur effacé et copie en bas ; `F1 1 C1 1 F2 1 C2 1`, `NEG 0 EDGE 0 ZERO 0`, `COPY 1 SWAP 1`, `KEY 97 CLOSE RETURNED`, fin normale ligne 79 |

**R15 M6 archivée et inchangée :** [`dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib`](../dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib), **9 784 octets**, SHA256 `44530d28cc33ab2aa1bb9bd81aa3f9799e3aca67a714c36891888c3ece4c6e6e`. **Lib courante : R19 0.8.3** dans [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib). Les archives R14 Fill et R13 Copy sont conservées.

**Gate A HUNK/AP20/CPU/CI : PASS** (R15 CI #42857827475 (archive CI privée), 27 scénarios valides + 25 rejets/erreurs, régressions Fill/Copy). **Gate B AMOS interprété/WinUAE : PASS pour les scénarios ci-dessus. Gate C AMOS Compiler et Gate D Amiga physique : NON TESTÉES**. Ces retours ne certifient pas tous les cas graphiques ni la stabilité en charge.

**M5 IFF/ILBM clôturé :** HAM6, HAM8, SuperHiRes, SuperHiRes Lace PASS utilisateur ; DblPAL/DblNTSC non testés, non bloquants. Ancien test Jeff conservé dans `tests/passed/`.

**M7/R16 : PASS pour le scénario AMOS interprété/WinUAE du 10/11/2026.** [`passed/M7_R16_COPPER_CLEAR_01.asc`](passed/M7_R16_COPPER_CLEAR_01.asc) est archivé octet pour octet. Capture : `IMAGE 320 X 256 PLANES 8`, `C1 1 C2 1 C3 1`, `OPEN 1 REOPEN 1`, `SWAP 1 KEY 67`, `CLOSE X2 RETURNED`, fin normale ligne 74. **Gate A CPU/CI PASS** (CI #42864040653 (archive CI privée), 13 scénarios 68000) ; **Gate B PASS sur ce scénario**. aucun test **M7/R16** actif. Compiler et vrai Amiga non testés ; `LAST_GOOD` demeure R10, sans promotion.

**M7/R17 : PASS AMOS interprété/WinUAE 3/3, le 10/11/2026.** Test exact archivé sans modification : [`passed/M7_R17_COPPER_ON_OFF_01.asc`](passed/M7_R17_COPPER_ON_OFF_01.asc). Image `320×256×8`, tous les retours `C1 ON1 SWAP OFF1 OFF2 C2 ON2 OFF3 REOPEN C3 ON3 OFF4` égaux à 1, `KEY 67 CLOSE X2 RETURNED`, fin ligne 83. **Gate A CPU/CI PASS** (CI #42866614578 (archive CI privée), 15 scénarios 68000) ; **Gate B PASS sur ce scénario**. Aucune preuve d'absence de fuite mémoire ni de raster. **Aucun test M7/R17 actif**. Compiler / vrai Amiga non testés.

**M7/R18 0.8.2 : PASS AMOS interprété/WinUAE le 10/11/2026.** [Test corrigé archivé](passed/M7_R18_COPPER_RASTER_01.asc) : une fonction `Aga Copper Off` isolée du fichier original provoquait une erreur de syntaxe ; elle a été corrigée par `X=Aga Copper Off`. Deux captures montrent les bandes raster COLOR00 rouge/vert/bleu/noir sur `MYGIRL.IFF` 320×256×8, puis `W/M=1`, rejets `BADREG/RGB/WAIT/END2/AFTER=0`, `END/ON/SWAP/OFF/OFF2/REOPEN/CLEAR2/ON2/OFF3=1`, `KEY 68 CLOSE X2 RETURNED`, fin ligne 95. **Gate A CPU/CI 26 scénarios PASS** (#42870412601 (archive CI privée)) et **Gate B WinUAE PASS** pour ce scénario. Aucun test M7/R18 courant ; Compiler/Amiga réel, stress/fuites non testés.
