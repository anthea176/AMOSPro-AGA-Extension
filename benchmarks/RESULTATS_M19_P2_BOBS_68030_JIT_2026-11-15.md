# M19 P2 — Benchmark complet 4/8/16 Bobs, WinUAE 68030 JIT (15/11/2026)

**Statut : PASS sous AMOS Runtime / WinUAE 68030, JIT activé selon l'auteur.** Il s'agit d'une validation du banc dans cette configuration et **pas d'une mesure représentative du 68020 sans JIT**. Le mode JIT est déclaré par l'auteur ; le journal n'enregistre pas cette option.

**Preuve :** fichier utilisateur `M19_P2_BENCH_BOBS_RUNTIME(1).TXT`, test `M19_P2_BENCH_BOBS_01` ; R84 v0.13.29 `LAST_GOOD`. ASC [actif](../tests/current/M19_P2_BENCH_BOBS_01.asc), blob Git `4345d8728af1d6dba29a5936463219ac49b3b109` **inchangé**. `RUN_MODE RUNTIME`, `PRG_STATE 1`, `CPU 68030`, `CPU_ATTNFLAGS 32823`.

## 1. Validation de fonctionnement

| Champ du log | Résultat |
|---|---:|
| `RESULT / VERDICT / ERR` | **1 / PASS / 0** |
| `CAP_OK / ICON_OK / OBJECTS_PREPARED` | 6 / 4 / 16 |
| `FRAME_OK` | **240 / 240** |
| `DRAW_OK` | **9 088** (attendu 9 088) |
| `SORT_FAIL / FILL_FAIL` | 0 / 0 |
| `DRAW_FAIL / SWAP_FAIL` | **0 / 0** |
| `SAFE_RETRIES / SWAP_RETRIES` | **1 / 0** |
| `CHIP_BEFORE / CHIP_AFTER / DELTA` | 1 702 480 / 1 702 480 / **0** |
| `FAST_BEFORE / FAST_AFTER / DELTA` | 135 762 544 / 135 762 544 / **0** |
| `CLOSE_RETURNED` | **1** |

`DRAW_OK 9088` = 8 × 16 dessins d'échauffement + 2 passages × (120 compositions + 40 présentations) × (4+8+16) objets. Le seul retry Safe est **global** ; les six champs de retries Safe **dans les compositions chronométrées** valent 0. Le log ne localise pas ce retry global ; les deltas mémoire sont des variations nettes, pas des mesures du pic.

## 2. Ticks bruts du benchmark

Chaque charge est testée deux fois : **800 tris BASIC**, **120 effacements de fond**, **120 compositions sans Swap**, **40 frames VBL+Swap** par passage. Timer PAL : 1 tick nominal ≈ 20 ms.

| Charge | Passage | Tri/800 | Fond/120 | Composition/120 | Présentation/40 | Dessins composition | Retry Safe comp. | Retry Swap disp. |
|---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| 4 Bobs | P0 | 0 | 139 | 140 | 80 | 480 | 0 | 0 |
| 4 Bobs | P1 | 0 | 140 | 139 | 80 | 480 | 0 | 0 |
| 8 Bobs | P0 | 1 | 140 | 140 | 80 | 960 | 0 | 0 |
| 8 Bobs | P1 | 1 | 139 | 141 | 80 | 960 | 0 | 0 |
| 16 Bobs | P0 | 6 | 139 | 143 | 80 | 1920 | 0 | 0 |
| 16 Bobs | P1 | 6 | 139 | 143 | 80 | 1920 | 0 | 0 |

## 3. Temps moyens indicatifs

Conversion à **20 ms/tick nominaux** et moyenne P0/P1. Ce sont des **temps écoulés**, pas des cycles CPU.

| Charge | Tri moyen (ms/appel) | Fond moyen (ms/appel) | Composition (ms/frame) | Présentation (ms/frame) |
|---:|---:|---:|---:|---:|
| 4 Bobs | 0,000* | 23,25 | **23,25** | 40,00 |
| 8 Bobs | 0,025* | 23,25 | **23,42** | 40,00 |
| 16 Bobs | 0,150 | 23,17 | **23,83** | 40,00 |

`*` : 0 ou 1 tick pour 800 tris est au voisinage de la résolution du Timer et **ne permet pas de considérer leur coût nul**. La composition passe de **23,25 à 23,83 ms/frame** entre 4 et 16 Bobs (+0,58 ms/frame selon le Timer nominal). Le **fond complet** semble dominer la durée de composition ; sa mesure est toutefois issue d'une boucle indépendante et inclut le fonctionnement du Blitter/émulateur. On ne peut pas isoler les cycles CPU réels de rendu à partir de ces temps.

Les six mesures de présentation sont **80 ticks/40 frames = 40 ms/frame (≈25 frames présentées/s)**, **VBL, composition et Swap inclus**, et ne constituent pas la performance intrinsèque du renderer. JIT et paramètres WinUAE empêchent de transposer ces chiffres directement à un Amiga 68020.

## 4. Historique et comparaison suivante

Le [premier journal](RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md) était **interrompu** après 41 frames avec `ERR 20` (`Aga Key=69`, Échap signalé), sans échec de dessin/Swap. Il reste archivé séparément ; **le second essai complet est PASS**.

**Prochain essai annoncé par l'auteur :** reprendre **exactement le même ASC** sur WinUAE **MC68020 à 14 MHz, PAL, JIT OFF** ; relever le fichier RAM après 240 frames, sans mélanger les deux configurations. La fréquence réelle 68030/JIT et le réglage JIT ne figurent pas dans ce log, hormis le témoignage de l'auteur.

**Aucune décision d'API native M19.** Le benchmark ne qualifie ni AMOS Compiler M19, ni Amiga physique, ni les sprites matériels AGA.

[Protocole](README_M19_P2_BOBS_4_8_16.md) · [Plan M19](../docs/M19_SPRITES_BOBS_AMAL_PLAN.md) · [Test actif](../tests/current/M19_P2_BENCH_BOBS_01.asc)
