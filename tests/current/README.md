# Tests AMOS en cours

## M13 / R28 0.10.0 — palette IFF standard (WinUAE NON TESTÉ)

**Un seul test actif : [`M13_R28_PALETTE_01.asc`](M13_R28_PALETTE_01.asc).** [Archive R28 candidate](../../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib), **16 208 octets**, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`. **Gate A CPU natif 68000 PASS : 159 cas** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43004699618)). **Gate B interprété AMOS / WinUAE reste à exécuter.**

### Procédure WinUAE

1. Sauvegarder la bibliothèque R27 actuelle dans la configuration Amiga, puis installer **une copie de l'archive R28** sous le nom `AMOSPro_AGA.Lib` au chemin d'extension AMOS habituel. **Ne pas remplacer** la bibliothèque R27 du dépôt `dist/AMOSPro_AGA.Lib` ni son archive R27. **Quitter puis relancer AMOS** après avoir remplacé la bibliothèque de l'émulateur : sa table de commandes doit être relue.
2. Dans AMOS Professional, importer le test avec **Project → Merge ASCII** depuis `tests/current/M13_R28_PALETTE_01.asc`.
3. Le sélecteur de fichier demande **un IFF palette enregistré avec Personal Paint ou Deluxe Paint** (palette seule : `FORM ILBM` et `CMAP`, `BMHD` éventuellement présent, **aucun `BODY` nécessaire**). En l'absence d'un IFF palette propre, choisir `examples/demo.iff` pour vérifier avec une image IFF complète : **seule sa palette est importée, jamais les pixels**.
4. Le programme ouvre son propre écran Intuition AGA **320×256 / 256 couleurs / PAL**, trace d'abord un rectangle index 28 et du texte, puis importe `CMAP`. Il fixe la couleur 28 en vert `$00FF00`, la fait évoluer vers `$F80700` en 32 VBL puis la remet en vert sur 32 VBL.
5. Il retourne ensuite à AMOS avec l'affichage de `OPEN 1 DB 1 IFF CMAP 1`, `SET 1 1 1 1`, `GREEN 65280`, `BAD 0 BADG -1`, `DRAW 1 1 1 1 SWAP 1`, `PEAK 16254720`, `FINAL 65280`, `FADEERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. Les valeurs en décimal doivent correspondre aux hexadécimaux indiqués ; la valeur `GET BEFORE` dépend du fichier choisi.

**Contrôle visuel :** le rectangle **doit rester dessiné après le chargement de palette** et varier de vert à rouge puis à vert sans chargement d'image ni rafraîchissement du bitmap. Une capture du résultat final et une confirmation de l'animation seront nécessaires pour déclarer Gate B PASS. **Ce test n'est ni un benchmark 50 FPS ni une commande Fade native.**

**R27 reste le dernier binaire validé sous WinUAE** : [test original M12 R27 archivé inchangé](../passed/M12_R27_SAFE_BLIT_01.asc) ; R26/R25/R24 et `LAST_GOOD` R10 inchangées. Aucun autre `.asc` actif, aucune branche supplémentaire.
