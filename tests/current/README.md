# Tests AMOS actifs

**Aucun test `.asc` actif.** R43 v0.11.4 `Aga Circle(CX,CY,Radius,Pen)` a passé **Gate A CPU/CI (436 scénarios 68000) et Gate B AMOS interprété / WinUAE** le 12/11/2026, confirmé par l'utilisateur (« parfait !!! »).

**Capture utilisateur :** `CIRCLES 1 1 1 1 DOT 1`, `CORNERS 1 1 1 1`, `CLIPPED 1 1 1 1`, `PEN0 1 OUTSIDE 0 0 0 0`, `WRAP 0 BADR 0 0`, `BADXY 0 0 BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`** ; rendu visuel validé.

**Bibliothèque actuelle `LAST_GOOD` : R43 v0.11.4**, 48 commandes AP20, 27 092 octets, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf`. `dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib` et l'archive R43 sont octet pour octet identiques ; [test R43 original archivé](../passed/M15_R43_CIRCLE_01.asc) sans modification (Git blob `088158365a64accf0417fdda3fbba74e2e58ebf7`, 3 466 octets). R42 reste archivée, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`. Gates C Compiler et D Amiga AGA physique non testées.
