# Test actif AMOS — R35 Fade To White

**Un seul ASC actif :** [`M13_R35_FADE_TO_WHITE_01.asc`](M13_R35_FADE_TO_WHITE_01.asc).

**Gate A CPU/CI R35 PASS : 50 scénarios natifs 68000 et source stricte PASS** ([CI Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43057199711)). **Gate B AMOS/WinUAE NON TESTÉE.** Ne pas utiliser ce test avec la bibliothèque R34, car elle ne contient pas `Aga Fade To White`. Installer la candidate R35 0.10.7 (21 300 octets, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`) maintenant publiée, en conservant le slot `APSystem` et en redémarrant AMOS. Importer par **New → Project → Merge ASCII**.

Le test affiche trois grandes bandes rouge, verte et bleue avant le fondu blanc de **150 VBL** (`Aga Swap` puis `Amos To Back` avant `Aga Fade To White`). Il vérifie le blanc exact de tous les pens testés, les durées 0, 256, -1 et 65536 rejetées, les durées 1/2 VBL, le cas déjà blanc et la fermeture de l'écran. **Aucune banque AMOS, aucun fichier ABK ou IFF remplacé.**

Résultats attendus :

```text
FADE150 1 WHITE 16777215 16777215
WHITE2 16777215 16777215
BAD0 0 BAD256 0 BADNEG 0 BADL 0
BEFOREBAD 7915560 AFTERBAD 7915560
FADE1 1 ONE 16777215 FADE2 1 TWO 16777215
SAME 1 SAME28 16777215
NOSCREEN 0 CLOSED -1
RESULT 1
CLOSE RETURNED
```

**R34 0.10.6 reste `LAST_GOOD` WinUAE-PASS** jusqu'à validation utilisateur de R35. Gates C Compiler/D Amiga réel non testées.
