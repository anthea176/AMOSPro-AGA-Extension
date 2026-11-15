# Test actif — M19 P2.3 BOBS natif R86

**Seul ASC actif** : [M19_P23_BOBS_BATCH_01.asc](M19_P23_BOBS_BATCH_01.asc).

- Requiert la bibliothèque R86 candidate dans `dist/AMOSPro_AGA.Lib` et installée dans AMOS (la R84 LAST_GOOD ne possède pas la commande).
- Crée ses propres banques AGAPIC v1/v2, FICON8, et BOB1 dans AMOS, sans ressource externe.
- Exécuter d'abord en **Runtime** puis **Compiled**, recopier les journaux `RAM:M19_P23_RUNTIME.TXT` et `RAM:M19_P23_COMPILED.TXT` avant reset. Vérifier `RESULT 1`, `ERR 0`, `VERDICT PASS`.
- Un retour 0 au Batch signifie **ne pas faire Swap** avant reconstitution du fond.
- Le test historique de quatrième unité est archivé **octet pour octet** dans `tests/passed/M19_P22_4UNIT_PROBE_01.asc`.

Voir [contrat M19 P2.3](../../docs/M19_P23_BOBS_BATCH_CONTRACT.md).
