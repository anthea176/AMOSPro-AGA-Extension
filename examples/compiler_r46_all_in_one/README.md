# R46 C1 — AMOS Compiler / AGA all-in-one test

**Status: prepared, not yet tested in WinUAE.** This is one AMOS ASCII source file plus the two data banks it needs. No extra AMCAF extension is required to use the embedded AMCAF BankFont.

## Contenu / Contents

- `COMPILER_R46_ALL_IN_ONE.asc` — one complete AGA compiler regression program
- `M16_AGAPIC_SAMPLE_BANK10.abk` — AGAPIC image, source bank 10
- `Hwarf1252S.abk` — AMCAF Hwarf bitmap font, source bank 25
- `Hwarf-12xxS.licence` — credit and license for the font artwork

## FR — mode d'emploi

1. Installer **la candidate expérimentale R46 C1** dans le bon `APSystem/AMOSPro_AGA.Lib`, puis relancer complètement AMOS et le Compiler : [candidate C1](../../dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib). Ne pas remplacer les fichiers officiels du dépôt.
2. Copier **tout ce dossier** sur un volume accessible à AmigaOS/WinUAE. Le programme compilé doit s'exécuter avec ce dossier comme **répertoire courant AmigaDOS** (les fichiers `.abk` sont chargés par nom relatif). L'exécutable ne change pas automatiquement le répertoire courant.
3. Dans AMOS : nouveau programme vide, puis **Project → Merge ASCII** du fichier `COMPILER_R46_ALL_IN_ONE.asc`. Compiler ensuite le programme pour créer un **nouvel exécutable**. Ne pas utiliser l'ancien exécutable, qui contient l'ancienne bibliothèque.
4. Lancer l'exécutable depuis le répertoire contenant les deux fichiers ABK. Observer les trois images (opaque, masquée, décalée), les effets de clipping, les textes en police AMCAF et Topaz, puis les phases du curseur (visible → masqué → visible → masqué). Le test effectue **500 bascules** rapides du curseur, puis ferme l'écran tout en le laissant masqué.
5. Lire le compte rendu après le retour à l'écran AMOS : **`RESULT 1`**, **`CLOSE RETURNED`**, `CUR 500 ERR 0`, `IMAGE O/M/S 1 1 1`, `CLIP L/R/T/B 1 1 1 1`, `BAD M/P/L 0 0 0 OUT 1`, `FONT BANK 1 BAD 0`, `FONT OS 1 RESET 1`, `BACKSAFE 1`, et `NO IMG/CUR/FONT/BANK 0 0 0 0`. Le programme conserve l'écran de résultats pendant `Wait 200`. Le relevé de `CHIP DROP` est **informatif**, pas une preuve suffisante de fuite.

Le programme remplace temporairement **les banques AMOS 10 et 25**. Aucune modification des fichiers sources déjà validés. Il vérifie les valeurs de retour et la stabilité générale, mais pas la fidélité pixel par pixel ; comparer aussi visuellement les images et le comportement de la souris.

## EN — quick start

With the experimental R46 C1 library installed, compile the ASCII source in AMOS Professional. Place the compiled executable and both `.abk` files in the same folder, **run it with that folder as the AmigaDOS current directory**, and look for `RESULT 1`, `CLOSE RETURNED`, and the three correctly rendered images. The program also exercises AMCAF and disk fonts, screen cleanup, 500 cursor toggles, and safe double-buffer drawing. Existing release libraries are unchanged.

**Gate C is not automatically fully validated** by generating this example; the user must execute it under WinUAE. See [Compiler diagnostic status](../../docs/GATE_C_R46_MONOLITH_CANDIDATE.md).

Font image rights are governed by [Hwarf's license](Hwarf-12xxS.licence), not the source MIT license. The AGAPIC sample is supplied for the existing test purposes; see [asset terms](../../ASSETS_LICENSE.md).
