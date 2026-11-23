# AGTM — Résultats de prototypes WinUAE du 23 novembre 2026

## Journaux et banque fournis

Originaux de l'auteur, conservés en **octets identiques, CRLF conservés**, sans modifier les sources AMOS [AGTM_BANK_ROUNDTRIP.asc](../tests/proto/agtm_prototype/AGTM_BANK_ROUNDTRIP.asc) et [AGTM_TILE_BENCH.asc](../tests/proto/agtm_prototype/AGTM_TILE_BENCH.asc).

| Preuve originale | Taille | SHA256 |
| --- | ---: | --- |
| [AGTM_BANK_RUNTIME.TXT](evidence/AGTM_BANK_RUNTIME_2026-11-23.TXT) | 186 octets | `112772b761c57b21137cc1b9215a9f2021303571ee28dd879b00c278db5e2675` |
| [AGTM_BENCH_RUNTIME.TXT](evidence/AGTM_BENCH_RUNTIME_2026-11-23.TXT) | 408 octets | `880a5c8da425cf25932d818679190bc174a5fc976d7f4df6b2920491bcde8b0e` |
| [AGTM_BENCH_COMPILED.TXT](evidence/AGTM_BENCH_COMPILED_2026-11-23.TXT) | 409 octets | `c539a290817194bd6312c20fa439c0f07e88e850886cf2842b7f0c3b53af5831` |
| [AGTM_V1_TEST.ABK](evidence/AGTM_V1_TEST_RUNTIME_2026-11-23.ABK) | 436 octets | `1aa8bdfa7995d130c0f71bcf12f659e08245759fd09f314bcae3cad18d7d6f6e` |

**Attention :** la mention `LIBRARY_EXPECTED M19_P2D` dans les journaux est une attente, pas la vérification de la SHA de la Lib effectivement chargée. Le CPU, la fréquence, le JIT et la version de l'AMOS Compiler n'y sont pas indiqués : ne pas les inventer.

## Banque DATA AGTM — Gate B Runtime PASS

`AGTM_BANK_ROUNDTRIP.asc` : `PRG_STATE 1`, `RUN_MODE RUNTIME`, `RESULT 1`, `ERR 0`, `VERDICT PASS`, `SAVE_ERROR 0`, `LOAD_ERROR 0`, `BYTE_MISMATCH 0`, `PAYLOAD_LENGTH 416`.

Le binaire fourni est un fichier **AMOS `AmBk` de 436 octets**, banque n°26, drapeau DATA=1, nom `Data    `. Taille `$800001A8` (bit31 positionné, longueur utile 424 = 8 octets nom + 416 payload). Payload `AGTM` version 1 : en-tête de 64 octets, carte **22×16**, tuiles **16×16**, 1 couche, 4 indices 0..3 ; 352 cellules. Les réserves 36..63 sont nulles ; **352/352** indices correspondent au motif `(X+2Y) mod 4` écrit par la sonde. Cela confirme le `Save/Load` DATA de ce prototype sous AMOS Runtime ; **pas** un moteur AGTM natif.

## Benchmark tuiles — Gates B Runtime et C Compiler PASS

`AGTM_TILE_BENCH.asc` : dans les deux modes `RESULT 1`, `ERR 0`, `VERDICT PASS`, `BENCH_RUNS 4`, `FULL_CALLS 2560`, `SCROLL_CALLS 136`, `CAP_A 1`, `CAP_B 1`, `PIXELS_OK 81920`, `PIXEL_BAD 0`, `SWAPS 1`, `RETRY_VBL 0`, `CLOSE_RETURNED 1`. Les champs CHIP/FAST avant/après sont identiques dans chaque journal.

| Mesure `Timer` (ticks cumulés) | Runtime B | Compiler C |
| --- | ---: | ---: |
| FULL : passes 0 + 1 | 90 + 87 = **177** | 70 + 70 = **140** |
| SCROLL : passes 0 + 1 | 17 + 16 = **33** | 15 + 16 = **31** |
| Rapport FULL/SCROLL | **5,36×** | **4,52×** |

Scénario : carte 320×256/8 plans, **déplacement d'une tuile de 16 pixels**. FULL = 320 appels `Aga F Icon`, SCROLL = `Aga Blit Copy` sur 304×256 + 16 appels `Aga F Icon`. Les deux sorties ont été comparées **sur 81 920 octets planaires** sans différence. Les copies de preuve, l'affichage, Swap/VBL sont hors mesure selon la source.

Ces ratios sont des ticks AMOS, pas des cycles CPU. **Ils ne qualifient pas le scrolling par pixel, des couches multiples, les Bobs ou le futur moteur natif M20.** Gate B et Gate C établies pour ce banc exact ; Gate D physique non testée.

## Statuts précis

**AGTM BANK : Gate B Runtime PASS, Gate C banque NON TESTÉE. AGTM BENCH : Gate B Runtime PASS et Gate C vrai Compiler PASS. M20 natif : aucune Gate acquise.** Aucune modification de la Lib P2d, de LAST_GOOD, des sources ASM ou du banc Bob.
