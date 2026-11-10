# Test M9 R24 — Hotspot Hit : Gate A CPU/CI PASS, WinUAE NON TESTÉE

**Unique test actif :** [`current/M9_R24_HOTSPOT_HIT_01.asc`](current/M9_R24_HOTSPOT_HIT_01.asc), sur [mire originale](../iff-TEST/AGA_TESTCARD_320x256_256C.iff) 320×256×8. Installer la **Lib R24**, relancer AMOS, choisir l'IFF, puis cliquer **gauche dans le recouvrement des rectangles** autour de `(130,100)` et **droit hors de toutes les zones** autour de `(300,220)`. Les deux premiers rectangles se recouvrent ; la deuxième zone (ID 20) gagne. La fenêtre reste affichée au plus 900 VBL (~18 secondes).

Attendu : `STATIC=1`, `OVERLAP=20`, `LEFT ID=20`, `RIGHT OUT=1`, `RESULT=1` et `CLOSE X2 RETURNED`. Les cas de bord, les dimensions nulles et les coordonnées négatives sont également testés sans écran. **Gate A CPU/CI PASS 402 cas** (CI (archive CI privée, run #42908096685)), mais Gate B exige une capture réelle sous WinUAE. R23 et `LAST_GOOD` inchangées. [Contrat](../docs/M9_HOTSPOT_R24.md).

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
