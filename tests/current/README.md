# Tests AMOS actifs

**Aucun test `.asc` actif** : la Gate A CPU/CI (**51 scénarios 68000** et [CI de publication 35/35 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43045308067)) et la Gate B fonctionnelle AMOS interprété/WinUAE ont passé R33 0.10.5 le 11/11/2026. Le programme de régression exact [`M13_R33_AGAPAL_FADE_01.asc`](../passed/M13_R33_AGAPAL_FADE_01.asc) est archivé **sans modification** dans `tests/passed/`. Capture : `FADE0 1 GREEN 65280`, `FADE1 1 BLUE 255 SAME 1 255`, `PART 1 PEN3 660510 PEN28 16711680`, `RELOAD 1 BLUE 255`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale ligne 141.

**Attention : le test fonctionnel ne montre presque pas le fondu à l'écran.** Il réalise `Aga Swap` et `Amos To Back` après les transitions de 12/1/2 VBL. Une [démo visuelle distincte](../../examples/fade_to_bank_r33.asc), confirmée visible et fonctionnelle par l'utilisateur sous WinUAE le 11/11/2026, présente l'écran avant les fondus, des transitions de 150 VBL et des pauses. La démo écrase la banque 12.

`dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R33, 20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`. R32 reste figée en archive. Le fondu visible a été confirmé dans la démo WinUAE ; cadence/FPS et durée réelle non mesurées, Gate C Compiler et Gate D Amiga physique non testées.
