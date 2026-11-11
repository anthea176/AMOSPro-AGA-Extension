# Test AMOS en cours — M13 R29 0.10.1 : sauvegarde palette IFF

**Gate A CPU : PASS 49 scénarios ; Gate B WinUAE : EN ATTENTE.** Un seul test actif : [M13_R29_PALETTE_SAVE_01.asc](M13_R29_PALETTE_SAVE_01.asc).

## Installation et procédure

1. Utiliser directement [`dist/AMOSPro_AGA.Lib` — R29 0.10.1](../../dist/AMOSPro_AGA.Lib) (17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`). Copier **sous son nom exact** dans `APSystem` ; quitter et relancer AMOS. **Ne pas installer `LAST_GOOD` à la place pour ce test** : elle reste R28 0.10.0 WinUAE-PASS, conservée dans [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).
2. Dans l'éditeur AMOS, partir d'un projet vide, puis `Project → Merge ASCII` avec [M13_R29_PALETTE_SAVE_01.asc](M13_R29_PALETTE_SAVE_01.asc). Exécuter en **interprété**.
3. Le test ouvre un écran AGA Intuition 320×256×8, dessine un panneau index 28, définit les couleurs, sauvegarde en IFF `FORM ILBM`, `BMHD` + `CMAP`, **sans `BODY`**, puis sauvegarde à nouveau au même chemin `RAM:M13_R29_PALETTE_TEST.IFF` en changeant la couleur 28 du vert au rouge. **La deuxième sauvegarde écrase la première**, comme approuvé.
4. Il met ensuite le pen 28 au noir, recharge le fichier par `Aga Palette Load`, et contrôle le retour de son rouge, du pen 224 et du pen 3. La géométrie dessinée avant chargement doit **rester visible** : panneau rouge final, barre colorée en bas, texte. L'écran se ferme après 100 VBL et rend la main à AMOS.
5. Attendu en console : `OPEN 1 DB 1`, `DRAW 1 1 1 1`, `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1`, puis `CLOSE RETURNED`.

**Remarques :** le test travaille sur `RAM:` (pas de sélection de fichier). Il ne demande aucune banque mémoire ni fonction Fade native. Conserver la capture finale et confirmer le panneau rouge avant classement dans `tests/passed/`. Vérifier séparément l'ouverture du fichier sauvegardé par Personal Paint/Deluxe Paint : leur prise en charge d'un ILBM sans BODY n'a pas encore été démontrée. Compiler et vrai Amiga AGA non testés.

**Promotion obligatoire seulement après la Gate B confirmée :** copier octet pour octet R29 vers `dist/AMOSPro_AGA_LAST_GOOD.Lib`, archiver le test sans modification et mettre à jour la CI/statut dans le même commit. Voir [contrat R29](../../docs/M13_PALETTE_R29.md) et [règles permanentes](../../EXTENSION_SOURCE_RULES.md).
