# Test AMOS actif — R34 Fade To Black

**Un seul ASC actif :** [`M13_R34_FADE_TO_BLACK_01.asc`](M13_R34_FADE_TO_BLACK_01.asc).

**Gate A CPU/CI R34 PASS : 48 scénarios natifs 68000 et export strict PASS** ([CI Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43053032571)). **Gate B WinUAE NON TESTÉE.** Ne pas exécuter avec R33 : la fonction n'y existe pas. Installer la candidate R34 0.10.6, 20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033` dans APSystem (même slot, redémarrage AMOS), puis **New → Project → Merge ASCII**.

Test : écran AGA 320×256×256, trois grandes bandes colorées affichées avec `Aga Swap` puis `Amos To Back` **avant** un fondu de 150 VBL. Vérifier les pens 28, 29, 30 et 224 noirs, les durées invalides (0/256/-1/65536), durées 1/2 VBL, noir déjà atteint, fermeture et retour sans erreur. **Aucune banque AMOS ni fichier ABK/IFF n'est remplacé.**

Résultats attendus : `FADE150 1 BLACK 0 0 0 0`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 0 FADE2 1 TWO 0`, `SAME 1 SAME28 0`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**.

**R33 0.10.5 reste la dernière version WinUAE-validée et `LAST_GOOD` ; `dist/AMOSPro_AGA.Lib` est maintenant la candidate R34.** Gates Compiler et Amiga réel non testées.
