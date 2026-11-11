**AVERTISSEMENT : première candidate R27 retirée avant WinUAE.** Ne pas exécuter le programme R27 tant qu'un binaire corrigé avec relocalisation R23 et Gate A PASS n'est pas publié. [Détails M12](../docs/M12_SAFE_BLITTER_R27.md).

# M12 R27 0.9.3 — Blitters Safe : Gate A CPU/CI PASS, Gate B WinUAE à tester

**Unique programme actif :** [`current/M12_R27_SAFE_BLIT_01.asc`](current/M12_R27_SAFE_BLIT_01.asc), à essayer avec la **bibliothèque candidate R27 0.9.3** (14 252 octets), **pas R26**. **396 cas CPU 68000 Gate A PASS**, [CI complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42995303489). **WinUAE R27 NON TESTÉE**.

Le test présente **40 images alternées vert/rouge**, avec deux rectangles par image dont un copié par `Aga Blit Copy`. Pour chacune des 40 images, le premier dessin est successivement `Aga Blit Clear`, `Aga Blit Fill` ou `Aga Blit Copy` (respectivement **14/13/13 réussites**) ; chaque routine doit se protéger **directement** contre l'utilisation d'un back buffer non-Safe. **Aucune sonde `Aga Text`.** Retours 0 → reprises bornées à 12 VBL, idem pour `Aga Swap`. Console attendue : `DONE 40 C 14 F 13 P 13`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. Compteurs de refus variables, aucune mesure de FPS. [Protocole détaillé](current/README.md).

**Ne pas déplacer dans `tests/passed/` avant capture WinUAE et validation utilisateur.** Les tests R26 [texte](passed/M11_R26_AGA_TEXT_01.asc) et [40 swaps avec sonde](passed/M11_R26_SAFE_SWAP_02.asc) restent archivés à l'octet près, tout comme R25/R24.

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
