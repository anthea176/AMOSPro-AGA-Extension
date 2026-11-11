> **État courant 11/11/2026 :** `dist/AMOSPro_AGA.Lib` = **R28 0.10.0**, **candidate** (Gate A CPU/CI 159 cas PASS ; Gate B WinUAE en attente). `dist/AMOSPro_AGA_LAST_GOOD.Lib` = **R27 0.9.3**, dernière bibliothèque **confirmée WinUAE PASS**, SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe` ; R10 reste dans son archive versionnée. [Règle prioritaire](../EXTENSION_SOURCE_RULES.md) · [État complet](NEXT_SESSION.md).

# Construire, tester et conserver une bibliothèque AGA

**Règle durable :** `dist/AMOSPro_AGA.Lib` est **toujours la candidate directement téléchargeable sous son nom exact** après Gate A/CI PASS. `dist/experimental/` contient uniquement des **archives nommées par version**, jamais un sous-répertoire arbitraire avec un second `AMOSPro_AGA.Lib`. **Dès Gate B WinUAE confirmé par l'utilisateur, la dernière bibliothèque validée est copiée à l'octet près dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`, automatiquement, en même temps que l'archivage du test.** Une version testée seulement en CPU ne devient pas `LAST_GOOD`.

Ne jamais déduire le numéro de build courant depuis ce fichier : consulter [`NEXT_SESSION.md`](NEXT_SESSION.md), le [STATUS du jalon actif](M7_STATUS.md), le HEAD de `main` et les empreintes réelles.

## Avant un nouvel essai

1. Partir d'une **archive validée explicitement** ; identifier le builder reproductible et comparer le SHA256.
2. Générer l'archive versionnée et, seulement pour un candidat à présenter, la bibliothèque `dist/AMOSPro_AGA.Lib` à contenu identique.
3. Vérifier HUNK/AP20, table de tokens, ABI AMOS, SHA, reproductibilité, conservation des segments déjà validés.
4. Un test de CPU/CI **ne valide pas** la présence d'une fonction en interprété WinUAE. Suivre les Gates A (statique), B (interprété), C (Compiler), D (Amiga réel).
5. Tester un seul nouvel incrément, conserver intact le programme exact validé dans `tests/passed/` ; diagnostics rejetés dans `tests/historical/`.
6. **Après Gate B AMOS/WinUAE PASS confirmé par l'utilisateur : promouvoir immédiatement cette version dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`, octet pour octet ; aucune confirmation supplémentaire requise.** Tant que Gate B est en attente ou échoue, garder le dernier `LAST_GOOD` intact.

Pour M7 Copper : le préflight Python **n'est pas** un binaire. Les références de build et de statut figurent dans [`M7_STATUS.md`](M7_STATUS.md), avec les validations [R16 Clear](M7_COPPER_R16.md) et [R17 On/Off](M7_COPPER_R17.md). R18 est un **raster validé sur le scénario AMOS interprété/WinUAE** ([spécification](M7_COPPER_R18.md)). Gate A CPU 26 scénarios **PASS** et **CI complète PASS** (#42870412601 (archive CI privée)) ; **test AMOS/WinUAE PASS** sur les captures du rendu et de la fermeture (10/11/2026, ligne 95) ; [test corrigé archivé](../tests/passed/M7_R18_COPPER_RASTER_01.asc). Compiler, matériel réel, stress/fuites restent non testés. Les archives R16/R15 et `LAST_GOOD` restent protégées.
