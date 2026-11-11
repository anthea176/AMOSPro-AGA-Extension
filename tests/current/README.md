# Tests AMOS actifs

**Aucun test `.asc` actif** après validation R35 sous AMOS interprété/WinUAE le 11/11/2026.

L'[ASC R35 exact](../passed/M13_R35_FADE_TO_WHITE_01.asc) est archivé sans modification dans `tests/passed/` (Git blob `21115dfbbcff345e6ae8132c03956152b897a6b2`). La capture utilisateur montre `FADE150 1 WHITE 16777215 16777215`, `WHITE2 16777215 16777215`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 16777215`, `FADE2 1 TWO 16777215`, `SAME 1 SAME28 16777215`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. Fondu blanc visible confirmé ; cadence/FPS et durée réelle non mesurées.

**R35 0.10.7 est désormais `LAST_GOOD` WinUAE-PASS** : `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R35, **21 300 octets**, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`. R34 0.10.6 reste dans son archive inchangée.

Gates C Compiler et D Amiga AGA réel non testées. Toute nouvelle fonction et tout nouveau test actif doivent faire l'objet d'un contrat discuté et approuvé avant codage.
