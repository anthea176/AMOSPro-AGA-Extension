# M18 — tests AMOS actifs

**Aucun ASC actif** dans `tests/current/` après les deux essais **PERF-02 WinUAE JIT OFF PASS** du 13 novembre 2026.

[**Rapport benchmark PERF-02**](../../docs/M18_R68_CBLOCK_PERF_02_WINUAE_2026-11-13.md) · [**ASC PERF-02 archivé, inchangé**](../passed/M18_R68_CBLOCK_PERF_02.asc).

- **68020 à 14 MHz / 128 Mo Fast Z3 / JIT OFF / AMOS interprété** : 6 tailles, 17 chemins validés, `RUNS/ERR/MIS/MEM 17 0 0 0`, `CHIP START/END 1845800 1845800`, `RESULT 1`.
- **68030 à 28 MHz / 128 Mo Fast Z3 / JIT OFF / AMOS interprété** : mêmes 17 chemins validés, `RUNS/ERR/MIS/MEM 17 0 0 0`, `CHIP START/END 1845768 1845768`, `RESULT 1`.
- **CBlock R68 v0.13.13 reste l'unique bibliothèque candidate** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Le binaire n'a pas été modifié.
- **R63 `LAST_GOOD` protégée**, aucune promotion. **Gate C Compiler AMOS réelle uniquement à la fin M18**, Gate D physique non testée.

L'ASC Gate B R68 initial reste [archivé et immuable](../passed/M18_R68_CBLOCK_CHIP_01.asc).

**Suite :** analyser les seuils de choix CPU16/Blitter et la répétabilité si une sélection automatique est envisagée. Ne créer un nouvel ASC unique que pour un essai nouveau, ne jamais modifier `tests/passed/`.
