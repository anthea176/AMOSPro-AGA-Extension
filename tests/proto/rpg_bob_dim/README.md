# M19 P2d - Differential Bob 16/20 pixels

These non-distributed prototypes derive from the byte-exact passing source `examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc` (Git blob `c48d334fd4508d402d28399bffdfec08d4cb4acb`). The **same P2d Auto Update / 240-frame AMAL / Swap / pixel-validation sequence** runs in each file. The later collision, flip and plane tests are skipped to avoid geometry-dependent expectations.

| Source | Bob 1 | Runtime log |
|---|---|---|
| `P2_DIM_16X16.asc` | 16x16 | `RAM:P2_DIM16X16_RUNTIME.TXT` |
| `P2_DIM_20X16.asc` | 20x16 | `RAM:P2_DIM20X16_RUNTIME.TXT` |
| `P2_DIM_20X18.asc` | 20x18 | `RAM:P2_DIM20X18_RUNTIME.TXT` |

The source pixels on the two extra lines are cleared in all three tests. The **only graphics change between variants** is the `Get AGA Bob 1` crop; identifying titles and log paths differ. No IFF or ABK is required.

**Run `P2_DIM_20X18.asc` first** under AMOS Runtime with M19 P2d LAST_GOOD (SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`). If it fails, try `P2_DIM_20X16.asc`; the 16x16 case is the control.

Expected PASS for each: `PHASE_LAST 1`, `VALID_SAMPLES 240`, `RESULT 1`, `ERR 0`, `CLOSE_RETURNED 1`. This is a **static-preflight-ready experiment**, not a WinUAE/Compiler PASS until user logs are received. Active `tests/current/`, `tests/passed/`, `examples/`, Lib and LAST_GOOD remain untouched.
