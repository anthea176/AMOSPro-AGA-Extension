# M13 / R29 0.10.1 — sauvegarde de palette AGA au format IFF

**État courant au 11/11/2026 :** R31 0.10.3 `Aga Palette Bank Capture` a passé Gate B WinUAE et constitue désormais `dist/AMOSPro_AGA_LAST_GOOD.Lib`. Les versions R30 0.10.2 et R29 0.10.1 restent figées dans leurs archives `dist/experimental/`. Les notes ci-dessous décrivent la validation **historique** de R29.

## R29 0.10.1 VALIDÉE — Gate A + Gate B AMOS/WinUAE PASS, 11/11/2026

**Preuves utilisateur :** test `M13_R29_PALETTE_SAVE_01.asc` exécuté sous AMOS interprété/WinUAE : `OPEN 1 DB 1`, `DRAW 1 1 1 1`, `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. L'utilisateur confirme également l'ouverture de la palette IFF produite avec ses **256 couleurs dans Cloanto Personal Paint (PPaint)** ; le fichier ne contient pas de pixels `BODY`. Cela établit l'interopérabilité **pour ce fichier et cet essai**, pas tous les éditeurs IFF.

**Promotion obligatoire :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib`, **R29 0.10.1**, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, octet pour octet. L'archive R28 est figée et conservée. Le fichier de test original (Git blob `b80baabe5533288cac3285a78c232827cce94085`) est déplacé **sans modification** dans `tests/passed/M13_R29_PALETTE_SAVE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`.

**Validation :** Gate A CPU 68000 **49 scénarios PASS**, [CI R29 avant promotion **30/30 PASS**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43016176793) ; Gate B interprété/WinUAE **PASS** sur le test et PPaint précités. **Gates C (Compiler) et D (matériel réel) NON TESTÉES**. La validation sous PPaint ne démontre pas l'affichage des pixels puisque le format est volontairement sans `BODY`.

**Suite M13 :** fonctions de banques de palettes (Fast RAM privilégiée) et fades natifs `Aga Fade To Bank/Black/White`, puis cycling. **Avant chaque nouvelle fonction, discuter et valider son contrat avec l'utilisateur ; aucune implémentation anticipée.**

---



**Historique avant Gate B (11/11/2026) : Gate A CPU native PASS (49 scénarios) ; [CI complète 30/30 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43015949869) ; Gate B attendait le retour utilisateur.** Version candidate réservée à la première fonction R29 explicitement validée par l'utilisateur. Aucune bank de palette, Fade ou cycling nouveau n'est implémenté.

## Bibliothèques et sources

- **Binaire candidat à tester :** `dist/AMOSPro_AGA.Lib` = **R29 0.10.1**, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`.
- **Archive versionnée identique :** `dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib`.
- **État historique lors de la clôture R29 :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` était **R29 0.10.1**, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, copie identique à l'archive R29. R28 reste archivèe.
- **Builder reproductible en mémoire :** `tools/build_m13_palette_save_r29.py` ; émetteur CPU 68000 : `tools/m13_palette_save_r29_emit.py` ; préflight et tests Unicorn/Capstone : `tools/test_m13_palette_save_r29.py`.
- **Test WinUAE validé et archivé :** [`tests/passed/M13_R29_PALETTE_SAVE_01.asc`](../tests/passed/M13_R29_PALETTE_SAVE_01.asc), contenu original inchangé.

## API R29 — une seule nouvelle fonction

`_OK=Aga Palette Save(_FILE$)` : nom de fichier AMOS, chemin standard AmigaDOS ; valeur entière 1 si réussite, 0 si refus/erreur. Le mode **MODE_NEWFILE** remplace le contenu d'un fichier de même chemin. N'appeler qu'avec un écran AGA Intuition indexé valide ; les modes EHB, HAM et dual playfield ne sont pas supportés. La palette est lue depuis le `ViewPort.ColorMap` privé avec `graphics.library/GetRGB32`. Aucune lecture/modification des bitplanes. Aucun `Aga Swap` ou attente VBL implicitement nécessaire.

**Contenu exact du fichier :**
- IFF `FORM ILBM` (big endian), avec chunk `BMHD` standard de 20 octets, puis chunk `CMAP` de `3 × N` octets (R/G/B 8 bits). Aucun `BODY`, aucune compression ni donnée de pixels.
- `N = min(State.LogicalColours, ColorMap.Count)` de 1 à 256 selon l'écran. `BMHD` reprend largeur, hauteur et nombre de plans de l'écran ; masque/compression à 0, proportions x/y à 1/1, coordonnées d'origine à 0. Chaque chunk impair est complété d'un octet nul, sans inclure ce pad dans la taille du chunk.
- Taille totale exacte : `48 + 3*N + (N mod 2)` octets (pour 256 couleurs : 816 octets).

**Mémoire et gestion des erreurs :** conversion de la chaîne AMOS vers une chaîne DOS temporaire allouée par Exec `AllocVec`, puis allocation d'un tampon pour l'IFF et les RGB32 ; tout est libéré après l'opération. Écriture complète validée (longueur retournée par `DOS Write`), `DOS Close` contrôlé, suppression tentée en cas de sortie partielle. Pas de bank persistante, ni changement de couleur ou d'écran. En cas d'erreur d'écriture après `MODE_NEWFILE`, l'ancien fichier peut avoir été écrasé : la suppression évite de laisser une sortie partielle, sans garantir une sauvegarde transactionnelle.

**Interopérabilité :** PPaint a chargé le fichier exporté par R29 selon l'essai utilisateur ; le chargeur R28 sait importer `FORM ILBM` / `CMAP` sans `BODY` ; ce trajet R29 Save → R28 Load est testé par simulation CPU. L'import dans **Personal Paint est confirmé** sur le fichier testé ; l'import dans Deluxe Paint ou d'autres éditeurs reste non testé.

## Validation

- **Gate A CPU :** 49 scénarios dont huit profondeurs, limites de ColorMap, longueur et padding CMAP, headers BMHD, ressources DOS, erreurs de mémoire/ouverture/écriture/fermeture et trois roundtrips R29→R28 sans copie de pixels. Binaire R28 conservé octet pour octet ; R29 ajoute seulement GetP au segment final 39 et la nouvelle entrée AP20 40, sans relocaliser les précédents segments.
- **Gate B WinUAE : PASS sur le test utilisateur archivé ; la procédure suivante est conservée pour référence historique.** Installer directement `dist/AMOSPro_AGA.Lib` sous son nom exact dans `APSystem`, relancer AMOS, puis `Project → Merge ASCII` avec le fichier test courant. Il écrit `RAM:M13_R29_PALETTE_TEST.IFF` deux fois (vert puis rouge), efface la couleur 28, recharge le fichier et vérifie qu'il restaure le rouge RGB `$FF0000` et les autres entrées, sans image BODY. Résultat attendu : `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128`, `CLOSED -1 RESULT 1`, puis `CLOSE RETURNED`. Un panneau rouge doit rester visible.
- **Gate C Compiler et Gate D Amiga physique :** non testées.
- **Promotion R29 :** test archivé dans `tests/passed/` sans modification ; binaire R29 copié octet pour octet vers `dist/AMOSPro_AGA_LAST_GOOD.Lib` et empreintes/CI synchronisées. Aucun test Compiler ou matériel physique.

**Suite M13 :** banques de palettes en RAM, fades natifs `Aga Fade To Bank`, `Aga Fade To Black`, `Aga Fade To White`, puis cycling, **à discuter et approuver une fonction à la fois avant tout code** conformément à `EXTENSION_SOURCE_RULES.md`.
