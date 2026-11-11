# Test AMOS actif — M13 R33 0.10.5 Fade To Bank

**Seul test actif :** [`M13_R33_AGAPAL_FADE_01.asc`](M13_R33_AGAPAL_FADE_01.asc), candidate R33 0.10.5 à installer sous son nom exact `AMOSPro_AGA.Lib` dans `APSystem`, sans changement du slot, puis redémarrer AMOS et effectuer **New → Project → Merge ASCII**.

**Gate A PASS :** 51 scénarios CPU 68000, export strict et [CI Gate A réussie](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43044805057). **Gate B WinUAE pas encore testée.** **Attention : le programme remplace les banques 10/11 et `RAM:R33_AGAPAL_FADE.ABK` !**

Attendus : `FADE0 1 GREEN 65280`, `FADE1 1 BLUE 255`, `SAME 1 255`, `PART 1 PEN3 660510 PEN28 16711680`, tous les retours `BAD*` à 0, `RELOAD 1 BLUE 255`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. Vérifier aussi visuellement le dégradé vers le vert sur 12 VBL.

**Candidate :** `dist/AMOSPro_AGA.Lib`, R33 0.10.5, 20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste R32 0.10.4** ; Gates C/D non testées.
