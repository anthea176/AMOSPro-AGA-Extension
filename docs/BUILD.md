> **État courant 12/11/2026 :** R46 v0.12.1-C1 est **officielle `LAST_GOOD`**, 29 964 octets, SHA256 `d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b`, 50 commandes / 57 entrées AP20. Gates A CPU, B AMOS interprété/WinUAE et C Compiler WinUAE intégrée PASS, Gate D matérielle non testée. L'ancien binaire natif R46 56 segments reste archivé. [Source rules](../EXTENSION_SOURCE_RULES.md) · [Build officiel](../tools/build_aga_current.py) · [État complet](NEXT_SESSION.md).

# Construire, tester et conserver une bibliothèque AGA

**Règle durable :** `dist/AMOSPro_AGA.Lib` est la bibliothèque installable sous son nom exact après validation et promotion. Toute nouvelle version après R46 C1 doit être Compiler-safe. `dist/experimental/` contient uniquement des **archives nommées par version**, jamais un sous-répertoire arbitraire avec un second `AMOSPro_AGA.Lib`. **Dès Gate B WinUAE confirmé par l'utilisateur, la dernière bibliothèque validée est copiée à l'octet près dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`, automatiquement, en même temps que l'archivage du test.** Une version testée seulement en CPU ne devient pas `LAST_GOOD`.

Ne jamais déduire le numéro de build courant depuis ce fichier : consulter [`NEXT_SESSION.md`](NEXT_SESSION.md), le [STATUS du jalon actif](M7_STATUS.md), le HEAD de `main` et les empreintes réelles.

## Chaîne de build officielle (R46 C1 et futures versions)

**Ne jamais publier le binaire 56 segments** de l'ancien builder `build_m16_image_draw_r46.py` : il ne contient pas le correctif de relocation Compiler. Pour verifier la version promue :

```sh
python -B tools/build_aga_current.py --verify
python -B tools/test_compiler_relocation.py
python -B tools/verify_artifacts.py
```

Pour R47 et toute nouvelle version, partir des segments natifs reconstruits de **`dist/AMOSPro_AGA_LAST_GOOD.Lib`** avec `compiler_relocation.native_from_promoted()`, appliquer les changements natifs puis passer **obligatoirement** la sortie candidate par `compiler_relocation.wrap_native_ap20()` avant publication. La CI bloque le retour accidentel au fichier natif, les doubles enveloppes et le dépassement de la limite d'environ 32 Kio du dispatcher. En cas de dépassement, refactoriser en helpers relogeables, jamais contourner la garde. Le surcout monolithique ~28 Kio pour tout exécutable compilé utilisant l'extension est accepté pour C1.

Les archives R44/R45 et l'ancienne R46 native (29 288 octets) restent immuables. [Documentation détaillée](../tools/README.md) · [règles permanentes](../EXTENSION_SOURCE_RULES.md) · [Gate C confirmée](GATE_C_R46_MONOLITH_CANDIDATE.md). Les passages M7/R28 plus bas sont des **jalons historiques**, pas l'état du binaire installable.

## Avant un nouvel essai

1. Partir d'une **archive validée explicitement** ; identifier le builder reproductible et comparer le SHA256.
2. Générer l'archive versionnée et, seulement pour un candidat à présenter, la bibliothèque `dist/AMOSPro_AGA.Lib` à contenu identique.
3. Vérifier HUNK/AP20, table de tokens, ABI AMOS, SHA, reproductibilité, conservation des segments déjà validés.
4. Un test de CPU/CI **ne valide pas** la présence d'une fonction en interprété WinUAE. Suivre les Gates A (statique), B (interprété), C (Compiler), D (Amiga réel).
5. Tester un seul nouvel incrément, conserver intact le programme exact validé dans `tests/passed/` ; diagnostics rejetés dans `tests/historical/`.
6. **Après Gate B AMOS/WinUAE PASS confirmé par l'utilisateur : promouvoir immédiatement cette version dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`, octet pour octet ; aucune confirmation supplémentaire requise.** Tant que Gate B est en attente ou échoue, garder le dernier `LAST_GOOD` intact.

Pour M7 Copper : le préflight Python **n'est pas** un binaire. Les références de build et de statut figurent dans [`M7_STATUS.md`](M7_STATUS.md), avec les validations [R16 Clear](M7_COPPER_R16.md) et [R17 On/Off](M7_COPPER_R17.md). R18 est un **raster validé sur le scénario AMOS interprété/WinUAE** ([spécification](M7_COPPER_R18.md)). Gate A CPU 26 scénarios **PASS** et **CI complète PASS** (#42870412601 (archive CI privée)) ; **test AMOS/WinUAE PASS** sur les captures du rendu et de la fermeture (10/11/2026, ligne 95) ; [test corrigé archivé](../tests/passed/M7_R18_COPPER_RASTER_01.asc). Compiler, matériel réel, stress/fuites restent non testés. Les archives R16/R15 et `LAST_GOOD` restent protégées.
