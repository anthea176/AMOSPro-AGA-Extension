# Tests AMOS actifs

**Aucun test `.asc` actif.** Le test fonctionnel **M15/R40 `Aga Plot`** a été validé par l'utilisateur sous AMOS interprété / WinUAE le 12/11/2026, puis archivé **sans modification** dans [`tests/passed/M15_R40_PLOT_01.asc`](../passed/M15_R40_PLOT_01.asc), Git blob `6ab9cf4a91cca9f8097ffba40a32e2b85b049c38`.

Capture utilisateur : `OPEN 1 DB 1 CLEAR 1`, `PALETTE 1 1 1 1`, `CORNERS 1 1 1 1`, `CENTER 1 PEN0 1`, `DIAG 192 ERR 0`, `BADXY 0 0 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne 99. Le rendu visuel est confirmé verbalement par l'utilisateur (« ça marche nickel »).

La R40 v0.11.1 (45 commandes AP20, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`) est **`LAST_GOOD`**. Gates A CPU 68000/CI et B WinUAE **PASS** ; Gates C Compiler et D Amiga AGA physique non testées. L'archive R38 v0.11.0 et les essais [R38 précédents](../passed/) sont conservés.
