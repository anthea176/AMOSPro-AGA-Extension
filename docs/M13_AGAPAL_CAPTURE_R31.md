# M13 / R31 0.10.3 — Aga Palette Bank Capture validée WinUAE

## R31 0.10.3 validée — Gate A et Gate B AMOS/WinUAE PASS (11/11/2026)

**Résultat WinUAE utilisateur :** `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, **`CLOSED -1 RESULT 1`**, **`CLOSE RETURNED`**, fin normale à la ligne 141. **Gates C Compiler et D Amiga réel : NON TESTÉES.**

**ABK réel fourni et vérifié :** `R31_AGAPAL_CAPTURE.ABK`, 6 244 octets (AmBk externe : bank 10, flags DATA 1 ; AGAPAL v1 intérieur : 6 224 octets / 8 emplacements). Emplacement 0 : 256 couleurs et pen 28 `0000FF` ; emplacement 1 : 256 couleurs et pen 28 `FF0000` ; emplacements 2 à 7 vides et à zéro. Pens 3/224 inchangés ; SHA256 `7a3162969b0d700287ae0852872811dae072c19720a794beb8818d01b93f6cd9` du fichier transmis.

**R31 promue :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib`, 18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`. R30 conservée en archive figée. Test exact désormais archivé dans [`tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc`](../tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc) (Git blob `0196fc1ba730345a926f444691be80c16a7fb89c`), aucun `.asc` actif. Gate A 107 scénarios CPU PASS et [CI candidate 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43027906298) ; [CI de promotion 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43029502969).

---



**Historique :** la source R31 a d'abord passé Gate A avant les essais WinUAE. Les paragraphes de protocole ci-dessous décrivent les tests ayant conduit à la validation R31 ; ils ne sont pas des tâches en attente.

## Contrat fonctionnel approuvé

`_OK=Aga Palette Bank Capture(Start(bank),index)` : deux entiers.
`Start(bank)` désigne une banque DATA AMOS encore valide et préalablement
initialisée par `Aga Palette Bank Init`. `index` vaut 0..N-1.

- Lire uniquement la palette `ColorMap` de l'écran Intuition AGA privé actif,
  avec `graphics.library/GetRGB32`; les modes HAM/EHB/dual playfield ne
  sont pas pris en charge.
- Capturer `min(State.LogicalColours, ColorMap.Count)` couleurs, borné à
  1..256 ; chaque composante RGB24 est l'octet fort de son RGB32 AmigaOS.
- Écrire les trois composantes RGB24 consécutives par couleur dans l'unique
  emplacement AGAPAL de 768 octets. Remplacer une palette précédente si
  nécessaire ; mettre à zéro les octets inutilisés et enregistrer le nombre
  de couleurs dans le descripteur WORD à l'offset `16 + 8*index + 4`.
- Ne modifier ni les autres palettes/indices de la banque, ni les pixels,
  ni les couleurs de l'écran, ni le Copper. Aucun VBL implicite.
- Retour entier : 1 = réussite complète ; 0 = rejet/échec **sans écriture
  persistante dans la banque**. Rejeter avant toute écriture une banque
  non DATA/AGAPAL, la mauvaise taille, signature, version, flags, offset
  de l'emplacement, l'index invalide, un écran absent/incompatible et
  une allocation temporaire impossible.
- Banque RGB24 conservée dans le mécanisme DATA/ABK natif AMOS. Stocker
  les RGB32 temporaires dans `Exec/AllocVec` (maximum 3072 octets) et
  les libérer via `FreeVec`, sur Fast RAM si le système le permet.

**Sûreté mémoire :** fournir exclusivement `Start(bank)` d'une banque DATA
native AMOS vivante. `TypeOfMem` ne démontre pas qu'un pointeur arbitraire
appartient réellement à l'allocation et ne rend pas sûre une adresse périmée.

## Gate A et Gate B

Builder : `tools/build_m13_agapal_capture_r31.py`.
Émetteur 68000 : `tools/m13_agapal_capture_r31_emit.py`.
Tests Unicorn/Capstone : `tools/test_m13_agapal_capture_r31.py`.
Ces fichiers s'appuient sur l'archive R30 0.10.2 et protègent SHA256
`446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`.

La Gate B a été validée sous AMOS interprété/WinUAE avec un écran Intuition 320×256×8,
une banque AGAPAL initialisée par R30, deux captures sur des indices distincts,
une recapture du même index après changement de couleur, la vérification du
nombre de couleurs et des octets RGB24, des rejets d'index/absence d'écran,
puis `Save` / `Erase` / `Load` du vrai fichier ABK et un retour propre.
Le test a ensuite été réussi sous WinUAE et la promotion `LAST_GOOD` a été
réalisée. Ce scénario n'ajoute aucune nouvelle commande d'application de
palette, de fade ou de cycling.

**Règles permanentes :** une seule instruction nouvelle pour R31,
documentation exacte dans README EN et FR, test validé archivé sans
modification dans `tests/passed/`, `LAST_GOOD` promue après PASS WinUAE
utilisateur et Gate C/D encore non testées.
Aucune branche nouvelle et aucun autre dépôt.

## Protocole historique validé de Gate B

Le protocole validé utilise la bibliothèque R31 0.10.3 dans `APSystem` et **Project → Merge ASCII** avec le fichier désormais archivé [`tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc`](../tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc). **Attention : remplace les banques DATA 10 et 11 et `RAM:R31_AGAPAL_CAPTURE.ABK`.**

Le test ouvre l'écran AGA 320×256×8, crée une banque AGAPAL de huit emplacements, capture la palette avec le pen 28 vert en index 0, passe le pen au rouge et capture l'index 1, puis au bleu et recapture l'index 0. Il vérifie que l'index 1 reste rouge, que le seul index 0 a changé, que le pen 224 est conservé, que les deux descripteurs indiquent 256 couleurs, et que `Aga Palette Get(28)` est inchangé par la capture. Les indices -1/8, une banque mal dimensionnée et l'absence d'écran doivent être refusés. La sauvegarde et le rechargement via `Save/Load` AMOS doivent préserver les RGB24.

Sortie observée et validée : `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. La capture utilisateur et le fichier ABK transmis établissent ce résultat de Gate B ; R31 a été promue en `LAST_GOOD`.
