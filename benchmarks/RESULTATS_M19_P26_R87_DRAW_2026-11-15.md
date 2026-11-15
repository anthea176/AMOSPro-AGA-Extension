# M19 P2.6 — R87 : mesures réelles BASIC individuel vs Aga Bob Batch

**15 novembre 2026.** Deux journaux WinUAE transmis par l'auteur, **Runtime et Compiled PASS** (`RESULT 1`, `ERR 0`, `VERDICT PASS`, `BENCH_RUNS 12`, `CLOSE_RETURNED 1`). Programme exact [M19 P2.6](../tests/passed/M19_P26_R87_DRAW_BENCH_01.asc), Git blob `c6c03b24bb273027492776ba24e53193ec52198b`, archivé sans modification après réception de ses résultats. Candidate attendue R87 v0.13.32 SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`.

La mention `LIBRARY_EXPECTED` provient du code ASC, **elle ne démontre pas le SHA du binaire réellement chargé**. La configuration 68020 / 14 MHz / JIT OFF a été fournie pour la campagne de référence mais n'est pas incluse dans les journaux.

| Bobs | Runtime BASIC (ticks) | Runtime Batch | Gain Runtime | Compiled BASIC | Compiled Batch | Gain Compiled |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 317 | 310 | 2,21 % | 313 | 311 | 0,64 % |
| 8 | 647 | 624 | 3,55 % | 630 | 628 | 0,32 % |
| 16 | 1182 | 1160 | 1,86 % | 1164 | 1159 | 0,43 % |
| **Total** | **2146** | **2094** | **2,42 %** | **2107** | **2098** | **0,43 %** |

**Compteurs :** 64 répétitions, deux passages inversés par charge, 3 584 appels individuels, 384 appels Batch, 3 584 Bobs par méthode ; `CHIP_BEFORE=CHIP_AFTER` et `FAST_BEFORE=FAST_AFTER` pour les deux modes. Les six différences Runtime sont positives, mais les gains Compiled restent inférieurs à 1 %.

**Conclusion limitée :** réduire les appels depuis AMOS BASIC ne suffit pas à accroître significativement le débit ; le rendu effectif est probablement dominant, hypothèse à départager avec un banc utilisant les **mêmes pixels/tailles** en AGAPIC RLE, FICON8 planaire et Blitter. [Campagne P2.7](../docs/M19_P27_AGAPIC_CACHE_BACKENDS_2026-11-15.md). Les anciens temps P2.1 de composition de scènes n'ont pas le même périmètre, ils ne peuvent pas être comparés directement.

**Pas de nouvelle candidate, aucune promotion de R84 LAST_GOOD.**
