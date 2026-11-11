# Test AMOS actif — M13 R33 0.10.5 Fade To Bank

**Seul ASC actif :** [`M13_R33_AGAPAL_FADE_01.asc`](M13_R33_AGAPAL_FADE_01.asc), à exécuter sous AMOS interprété/WinUAE uniquement après publication de la candidate R33 et PASS Gate A CPU/CI.

**R33 Gate A non encore validée ; Gate B non testée.** Le programme remplace les banques 10/11 et `RAM:R33_AGAPAL_FADE.ABK`. Captures AGAPAL de vert/bleu, fade bloquant 12/1/2 VBL, palette partielle 4 couleurs, refus des durées 0/256/-1, index/banques invalides, Save/Load ABK, fermeture et retour propre. Attendu `RESULT 1`, `CLOSE RETURNED`.

**Ne pas utiliser R32 pour ce test :** la fonction R33 n'y existe pas. `dist/AMOSPro_AGA_LAST_GOOD.Lib` demeure R32 0.10.4 validée WinUAE. Gates C/D non testées.
