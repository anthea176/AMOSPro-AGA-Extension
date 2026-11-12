# Tests AMOS actifs

**Aucun test `.asc` actif.** La R42 v0.11.3 `Aga Box(X1,Y1,X2,Y2,Pen)` est validée en **Gate A CPU 68000 / CI (360 cas) et Gate B AMOS interprété / WinUAE** le **12/11/2026**. Le [test `M15_R42_BOX_01.asc`](../passed/M15_R42_BOX_01.asc) est archivé **sans modifier un octet** : Git blob `dbf5cefb215cc0ae1359d648ea34c855a92b2012`, 3 264 octets.

**Capture WinUAE utilisateur :** `OPEN 1 DB 1 CLEAR 1`, `BOXES 1 1 1 REV 1`, `CLIPPED 1 1 1 1`, `LINES 1 1 DOT 1`, `OUTSIDE 0 0 0 0`, `WRAP 0 BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne 119. L'utilisateur confirme que le rendu fonctionne (« ça marche ! bravo »).

**Bibliothèque de référence actuelle : R42 v0.11.3 `LAST_GOOD`**, 47 commandes AP20, 25 896 octets, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`. `dist/AMOSPro_AGA.Lib`, son archive R42 et `dist/AMOSPro_AGA_LAST_GOOD.Lib` sont strictement identiques. Archives R41 et antérieures inchangées. Gates C (AMOS Compiler) et D (Amiga AGA réel) non testées.

Tests précédents : [R41 Draw](../passed/M15_R41_DRAW_01.asc) · [R40 Plot](../passed/M15_R40_PLOT_01.asc).
