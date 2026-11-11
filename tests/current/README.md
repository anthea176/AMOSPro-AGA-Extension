# Tests AMOS en cours

## M13 / R28 0.10.0 — palette IFF standard (WinUAE NON TESTÉ)

**Un seul test actif : [`M13_R28_PALETTE_01.asc`](M13_R28_PALETTE_01.asc).** [Archive R28 candidate](../../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib), **16 208 octets**, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`. **Gate A CPU natif 68000 PASS : 159 cas** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43004699618)). **Gate B interprété AMOS / WinUAE reste à exécuter.**

### Procédure WinUAE

1. Télécharger directement [**`dist/AMOSPro_AGA.Lib` — R28 0.10.0**](../../dist/AMOSPro_AGA.Lib), sans renommer ni déplacer dans un sous-répertoire du dépôt. Copier ce fichier dans `APSystem` sous le même nom, puis quitter et redémarrer AMOS. **La version validée R27 est sauvegardée par le dépôt dans [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).** Ne pas remplacer cette dernière avec R28 tant que Gate B n'est pas PASS.
2. Dans AMOS Professional, importer le test avec **Project → Merge ASCII** depuis `tests/current/M13_R28_PALETTE_01.asc`.
3. Le sélecteur de fichier demande **un IFF palette enregistré avec Personal Paint ou Deluxe Paint** (palette seule : `FORM ILBM` et `CMAP`, `BMHD` éventuellement présent, **aucun `BODY` nécessaire**). En l'absence d'un IFF palette propre, choisir `examples/demo.iff` pour vérifier avec une image IFF complète : **seule sa palette est importée, jamais les pixels**.
4. Le programme ouvre son propre écran Intuition AGA **320×256 / 256 couleurs / PAL**, trace d'abord un rectangle index 28 et du texte, puis importe `CMAP`. Il fixe la couleur 28 en vert `$00FF00`, la fait évoluer vers `$F80700` en 32 VBL puis la remet en vert sur 32 VBL.
5. Il retourne ensuite à AMOS avec l'affichage de `OPEN 1 DB 1 IFF CMAP 1`, `SET 1 1 1 1`, `GREEN 65280`, `BAD 0 BADG -1`, `DRAW 1 1 1 1 SWAP 1`, `PEAK 16254720`, `FINAL 65280`, `FADEERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. Les valeurs en décimal doivent correspondre aux hexadécimaux indiqués ; la valeur `GET BEFORE` dépend du fichier choisi.

**Contrôle visuel :** le rectangle **doit rester dessiné après le chargement de palette** et varier de vert à rouge puis à vert sans chargement d'image ni rafraîchissement du bitmap. Une capture du résultat final et une confirmation de l'animation seront nécessaires pour déclarer Gate B PASS. **Ce test n'est ni un benchmark 50 FPS ni une commande Fade native.**

**R27 est la dernière bibliothèque validée sous WinUAE, et elle est désormais stockée dans [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib)**, octet-identique à [l'archive R27](../../dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib). R28 dans `dist/AMOSPro_AGA.Lib` attend encore Gate B. **Après une future Gate B PASS**, la candidate validée deviendra automatiquement le nouveau `LAST_GOOD`. R10 et les autres archives figées restent intacts.
