# Test actif — M19 P2.3 BOBS natif R86

**Seul ASC actif** : [M19_P23_BOBS_BATCH_01.asc](M19_P23_BOBS_BATCH_01.asc).

- Requiert la bibliothèque R86 candidate dans `dist/AMOSPro_AGA.Lib` et installée dans AMOS (la R84 LAST_GOOD ne possède pas la commande).
- Crée ses propres banques AGAPIC v1/v2, FICON8, et BOB1 dans AMOS, sans ressource externe.
- **Gates B/C déjà PASS** selon les journaux fournis du 15/11/2026 : Runtime `PRG_STATE 1`, Compiled `PRG_STATE -1`, les deux `RESULT 1`, `ERR 0`, `VERDICT PASS`, Chip/Fast sans delta. [Rapport détaillé](../../docs/M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md). Ces journaux attestent le scénario, mais les compteurs de clipping/ordre/transparence ne comparent pas les pixels à un oracle WinUAE.
- **Ne pas modifier cet ASC** tant qu'il sert de preuve des Gates B/C ; garder un seul ASC actif. Un retour 0 au Batch signifie **ne pas faire Swap** avant reconstitution du fond. Le benchmark 4 itérations a donné 13 ticks BASIC / 13 ticks Batch (aucun gain démontré).
- Le test historique de quatrième unité est archivé **octet pour octet** dans `tests/passed/M19_P22_4UNIT_PROBE_01.asc`.

Voir [contrat M19 P2.3](../../docs/M19_P23_BOBS_BATCH_CONTRACT.md).
