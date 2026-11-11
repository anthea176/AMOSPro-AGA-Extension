# Test AMOS actif — M13 R32 0.10.4 AGAPAL Apply

**Un seul ASC :** [`M13_R32_AGAPAL_APPLY_01.asc`](M13_R32_AGAPAL_APPLY_01.asc), à exécuter sous **AMOS interprété/WinUAE**, Gate B **NON TESTÉE**. **Gate A CPU 136 scénarios PASS**, export strict PASS, [CI source 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43031427255). Gates C/D non testées.

Installer directement [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) **R32 0.10.4** (19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`) sous son nom exact dans `APSystem`. Conserver le slot de l'extension, quitter et relancer AMOS. La bibliothèque `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste **R31 0.10.3** : ce n'est pas la R32 à tester.

Dans AMOS : **New → Project → Merge ASCII** avec le fichier actif. **Attention : le test écrase les banques 10/11 et `RAM:R32_AGAPAL_APPLY.ABK`.** Captures de deux palettes, applications immédiates, palette partielle et couleurs supérieures préservées, refus sans changement, sauvegarde/rechargement ABK, fermeture et retour AMOS.

Attendu : `AP0 1 AP1 1 PART 1`, `GREEN 65280 RED 16711680 BLUE 255`, `PEN224 795192 PART3 660510 PART28 255`, `BADNEG 0 BAD8 0 EMPTY 0`, `BADSIZE 0 BADCOUNT 0`, `AFTERBAD 255 AFTERCOUNT 255`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 16711680 PART 1`, `REST3 660510 REST28 16711680`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. La promotion `LAST_GOOD` est interdite avant confirmation WinUAE.

**CI de la candidate R32 publiée :** [34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040) après SHA256/AP20, export 68000 strict, test ASC statique, 136 scénarios CPU et régressions historiques. **R31 reste `LAST_GOOD` jusqu'à Gate B WinUAE R32.**

