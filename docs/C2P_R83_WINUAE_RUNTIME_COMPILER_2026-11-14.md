# R83 v0.13.28 — journaux WinUAE Runtime et AMOS Compiler (14/11/2026)

**Source :** journaux fournis par l'auteur `C2P_R83_RUNTIME(1).TXT` et `C2P_R83_COMPILED(1).TXT`, issus du test `C2P-R83-MODULAR-01`.

| Champ | Runtime | Compiled |
|---|---|---|
| `RUN_MODE` | RUNTIME | COMPILED |
| `PRG_STATE` | 1 | -1 |
| `CPU` | 68030 | 68030 |
| `CPU_ATTNFLAGS` | 32823 | 32823 |
| `SOURCE` | `DH6:tests/current/AGA_DEMO_320x256_256c.iff` | `AMOS AGA :tests/current/AGA_DEMO_320x256_256c.iff` |
| `IMAGE_WIDTH / HEIGHT / DEPTH` | 320 / 256 / 8 | 320 / 256 / 8 |
| `SCREEN_COLORS` | 256 | 256 |
| `GOLDEN_REFERENCE` | 1 | 1 |
| `GOLDEN_PIXEL_COUNT` | 14 | 14 |
| `LOAD12_OK / LOAD13_OK / INVALID_BANK_OK` | 1 / 1 / 1 | 1 / 1 / 1 |
| `RESULT / VERDICT` | 1 / PASS | 1 / PASS |
| `IFF_OK / PALETTE_OK / CHUNKY_OK` | 1 / 1 / 1 | 1 / 1 / 1 |
| `C2P_BASE_OK / BLIT_OK / ZOOM_OK` | 1 / 1 / 1 | 1 / 1 / 1 |
| `PIXEL_CHECK_OK / PIXEL_CHECK_COUNT` | 1 / 14 | 1 / 14 |
| `INVALID_CALLS_OK / REOPEN_OK / ESC_OK` | 1 / 1 / 1 | 1 / 1 / 1 |
| `SCREEN_CLOSE_COUNT` | 1 | 1 |
| `ERR` | 0 | 0 |
| `CHIP_BEFORE / AFTER / DELTA` | 1799632 / 1799632 / 0 | 1861304 / 1861304 / 0 |
| `FAST_BEFORE / AFTER / DELTA` | 138198744 / 138198744 / 0 | 140556800 / 140556800 / 0 |
| `CLOSE_RETURNED` | Présent | Présent |

**Verdict :** Gates B Runtime et C AMOS Compiler PASS sur ce scénario 320×256×8 sous WinUAE MC68030. Les deltas de mémoire nets sont nuls entre mesures ; cela ne prouve pas l'absence d'allocations temporaires. Pas de preuve sur `PRG_STATE 0` strict, autre CPU physique, Gate D matériel, ou vitesse.
