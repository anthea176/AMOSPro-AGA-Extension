# Tests AMOS actifs

**Aucun test `.asc` actif.** La fonction **M15/R41 `Aga Draw(X1,Y1,X2,Y2,Pen)`** a passé les Gates A (CPU 68000 / CI) et B (AMOS interprété / WinUAE) le **12/11/2026**. [Test `M15_R41_DRAW_01.asc` archivé](../passed/M15_R41_DRAW_01.asc) **sans modification**, Git blob `aa7de64b37a2842db21bc7452c2fab4570413e9f` (3 553 octets).

**Preuves Gate B :** capture console du test utilisateur `OPEN 1 DB 1 CLEAR 1`, `BORDER 1 1 1 1`, `CLIPPED 1 1 1 1`, `STAR 8 ERR 0 CENTER 1`, `OUTSIDE 0 0 0 0`, `BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, retour normal à AMOS (fin ligne 131). L'utilisateur a confirmé « rendu ok ! ». R41 est maintenant [`LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).

**Version validée : R41 v0.11.2**, **46 commandes AP20**, **24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`. `dist/AMOSPro_AGA.Lib`, l'archive R41 et `LAST_GOOD` sont identiques. La [R40 v0.11.1](../../dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib) et son [test archivé](../passed/M15_R40_PLOT_01.asc) restent inchangés. Gates C Compiler et D Amiga AGA réel non testées.

Les anciens tests sont conservés dans [`tests/passed/`](../passed/).
