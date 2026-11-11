# Tests AMOS actifs

**Aucun test `.asc` actif** après validation R36 0.10.8 sous AMOS interprété/WinUAE le 11/11/2026.

Le [test exact `M13_R36_PALETTE_CYCLE_01.asc`](../passed/M13_R36_PALETTE_CYCLE_01.asc) a été archivé sans modification dans `tests/passed/` (Git blob `4644236576033f755ac0dc274f6f22f92a2d9201`).

Capture : `CYC20 1 RESTORED 16711680 16776960`, `FWD 1 COLOR 16776960 16711680 65280 255`, `REV 1 RESTORE 16711680 16776960`, `NEG 1 COLOR 65280 16711680 POS 1`, invalides à 0, `AFTERBAD 16711680 NOSCREEN 0`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne 138. Cycling visible confirmé, sans mesure FPS ni de durée réelle.

**R36 0.10.8 est `LAST_GOOD` WinUAE-PASS** : `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R36, **21 836 octets**, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`. Archive R35 0.10.7 intacte.

Gates C Compiler et D Amiga AGA réel non testées. Toute nouvelle fonction (R37) doit être discutée et approuvée avant code ou test.
