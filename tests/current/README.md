# Tests AMOS actifs

**Aucun test `.asc` actif** après la validation R34 sous AMOS interprété/WinUAE le 11/11/2026.

Le programme exact [`M13_R34_FADE_TO_BLACK_01.asc`](../passed/M13_R34_FADE_TO_BLACK_01.asc) a été déplacé dans `tests/passed/` **sans modification** (Git blob `5fe2f819048cd3706eedaf363f3415a00270406a`). Résultats utilisateur : `FADE150 1 BLACK 0 0 0 0`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `FADE1 1 ONE 0 FADE2 1 TWO 0`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. Fondu visuellement confirmé ; cadence/FPS non mesurés.

**R34 0.10.6 est la version `LAST_GOOD` WinUAE-PASS** : `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R34 (20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`). R33 reste dans son archive intacte.

Gates C Compiler et D Amiga AGA physique non testées. Ne pas créer de nouveau test actif avant discussion et approbation du contrat d'une future fonction.
