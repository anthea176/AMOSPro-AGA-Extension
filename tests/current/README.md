# Test AMOS actif — M15/R42 Aga Box

**Seul programme `.asc` actif :** [`M15_R42_BOX_01.asc`](M15_R42_BOX_01.asc). **R42 v0.11.3 Gate A CPU/CI 68000 PASS (360 scénarios) ; Gate B AMOS interprété / WinUAE NON TESTÉE.** Ne pas déplacer le test dans `tests/passed/` ni promouvoir `LAST_GOOD` sans confirmation de l'utilisateur.

Installer la [candidate R42 `AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) (**25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`) dans **`APSystem`** à la place de l'extension actuelle, **sans changer le slot**, puis redémarrer AMOS. La [R41 `LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) reste une sauvegarde validée sous WinUAE. Dans un programme vide, importer le test avec **Project → Merge ASCII**. **Aucun fichier IFF ou ABK supplémentaire**.

Le test ouvre **320×256×256 couleurs**, affiche un **grand cadre, des rectangles imbriqués, quatre rectangles dépassant chacun l'un des côtés de l'écran, un rectangle aux coins inversés, deux lignes dégénérées et un point unique**. Il vérifie aussi quatre rectangles complètement hors écran, un rectangle géant dont les quatre côtés sont tous hors écran (**`WRAP 0`**), les coordonnées hors signed16, `Pen` invalide, et la reprise d'écriture dans le back buffer après `Aga Swap` et notification `Safe`.

**Valeurs attendues dans la console :** `OPEN 1 DB 1 CLEAR 1`, `BOXES 1 1 1 REV 1`, `CLIPPED 1 1 1 1`, `LINES 1 1 DOT 1`, `OUTSIDE 0 0 0 0`, `WRAP 0 BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. Confirmer aussi le rendu visuel : **pas de rectangle fantôme sur le bord de l'écran**, ni de corruption graphique ou plantage. La console seule ne prouve pas le rendu.

R40 et R41 sont déjà validées et archivées. **Gates C (AMOS Compiler) et D (Amiga AGA réel) non testées**.
