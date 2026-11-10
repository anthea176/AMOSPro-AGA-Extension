# AMOSPro AGA — images IFF/ILBM de test (créées pour le projet)

Ces **six images ILBM originales** permettent de tester R12 avec le **même programme AMOS** `tests/current/R12_JEFF_A0_RETRY.asc`. Aucun changement de bibliothèque n'est nécessaire pour le premier essai.

**Statut :** construction, structure FORM/BMHD/CMAP/CAMG/BODY, bitplanes et compression ByteRun1 vérifiés sous Python. **Aucune validation WinUAE/AMOS de ces six fichiers n'a encore été réalisée.** Les PNG du paquet sont des rendus de référence décodés depuis les codes graphiques, notamment les véritables commandes Hold-And-Modify de HAM6/HAM8.

## Priorité des essais

| Ordre | Fichier | ModeID CAMG | Plans | Attendu |
|---|---|---|---:|---|
| 1 | `HAM6_PAL_320x256.iff` | `$00021800` | 6 | HAM6, palette de 16 entrées, dégradés multicolores |
| 2 | `HAM8_PAL_320x256.iff` | `$00021800` | 8 | HAM8 AGA, palette de 64 entrées, dégradés plus fins |
| 3 | `SHIRES_PAL_1280x256.iff` | `$00029020` | 4 | SuperHiRes PAL, motifs fins de 1280 pixels |
| 4 | `SHIRES_LACE_PAL_1280x512.iff` | `$00029024` | 4 | SuperHiRes PAL entrelacé, 1280 × 512 |
| facultatif | `DBLPAL_320x256.iff` | `$000A1000` | 4 | DblPAL, pilote moniteur requis |
| facultatif | `DBLNTSC_320x200.iff` | `$00091000` | 4 | DblNTSC, pilote moniteur requis |

Tous les fichiers ont `masking=0`, `compression=1` (ByteRun1), `FORM ILBM` et `CAMG` explicite. `Aga Pic Info` doit annoncer les dimensions, la profondeur, le nombre de couleurs et le ModeID indiqués.

## Sur WinUAE

1. Décompresser les fichiers `.iff` sur un volume accessible à l'Amiga, par exemple `DH6:TestsAGA/`.
2. Garder **R12** installée ; ne pas modifier `LAST_GOOD`.
3. Lancer **le même test AMOS existant** `tests/current/R12_JEFF_A0_RETRY.asc` et sélectionner chaque `.iff` avec `Fsel$()`.
4. Vérifier : `OPEN=1`, `DB=1`, `LOAD=1`, `SWAP=1`, retour `KEY` puis `CLOSE RETURNED` ; comparer le rendu au `.png` du même nom.
5. En cas de `OPEN=0` sur DblPAL/DblNTSC : vérifier la disponibilité du mode dans `DEVS:Monitors` et la Display Database AmigaOS. Ce résultat **ne prouve pas** un bug du décodeur IFF.

**Important :** 1280 pixels peuvent dépasser la zone visible de l'écran émulé. La taille du bitmap n'implique pas une fenêtre visible de 1280 pixels ; `SA_AutoScroll` peut déplacer la zone visible. Un rognage visuel n'est donc pas nécessairement une perte de données.

### Vérification HAM6/HAM8

Les deux fichiers ne sont **pas** de simples images 64/256 couleurs indexées. Chaque pixel encode une commande **SET**, **MOD BLUE**, **MOD RED** ou **MOD GREEN**. Les commandes modifient la couleur héritée du pixel précédent sur la ligne. Les PNG sont le **résultat après décodage HAM**, à utiliser pour détecter un affichage indexé incorrect ou une palette erronée.

Le résultat **EHB** est déjà validé par l'utilisateur avec `harrison.iff`, ce mode n'est pas répété dans ce paquet.

## Reproductibilité

- `generate_aga_ilbm.py` : crée les six IFF avec Pillow ainsi que leurs PNG et le manifeste JSON.
- `verify_test_pack.py` : revalide les IFF sans invoquer le générateur.
- `manifest.json` et `checksums.sha256` : géométries, CAMG, compression, hashes de référence.
- `PREVIEW_CONTACT_SHEET.png` : vue d'ensemble des six aperçus.

Références techniques : `graphics/modeid.h` de l'AmigaOS NDK39, et spécification ILBM/IFF d'Electronic Arts.
- https://d0.se/include/graphics/modeid.h
- https://wiki.amigaos.net/wiki/ILBM_IFF_Interleaved_Bitmap

*Ces fichiers valident des structures et des décodeurs en Python, **pas** le rendu AMOS/WinUAE avant ton essai.*
