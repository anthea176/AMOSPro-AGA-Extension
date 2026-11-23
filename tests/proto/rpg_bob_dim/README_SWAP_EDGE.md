# P2d - Swap SafePort and 20x18 opaque edge tests

Two independent test programs derived from the passing 20x18 P2d geometry probe, itself based on the byte-exact public example P2_ALL_IN_ONE.

The three source-dimension Runtime logs received 23 November 2026 show RESULT 1, ERR 0, VALID_SAMPLES 240, SWAPS 241, SWAP_REFUSALS 120, SWAP_RECOVERED 120 and RETRY_VBLS 120. The complete reference test also has a 0-refusal run. A zero return from Swap is not by itself evidence of bad Bob pixels.

- **P2_SWAP_VBL_20X18.asc**: adds exactly one Aga Wait Vbl *before* the first Swap attempt in each of the 240 AMAL frames. The post-Swap VBL and bounded Safe retries remain. Compare PRE_SWAP_VBLS, SWAP_REFUSALS, SWAP_RECOVERED, RESULT, ERR against the existing original P2_DIM_20X18.asc. Runtime log: RAM:P2_SWAPVBL20X18_RUNTIME.TXT. This test deliberately adds waits and is NOT a speed benchmark.
- **P2_EDGE_20X18.asc**: the other program uses unchanged swap timing, adds an opaque pixel 165 at the bottom-right Bob-local (19,17), and samples that pixel through the verified 8-pixel-aligned Aga C Block Capture on the previous frame after Swap. EDGE_SOURCE 1, EDGE_SAMPLES >=2, EDGE_VALUE_LAST 165, RESULT 1, ERR 0, CLOSE_RETURNED 1 expected. ERR 81 means capture failure and 82 means pixel mismatch. Runtime log: RAM:P2_EDGE20X18_RUNTIME.TXT.

Run both with AMOS Runtime, P2d LAST_GOOD (SHA256 ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f), in a clean AMOS program via Project > Merge ASCII. No external IFF/ABK required. The test sources passed strict static preflight and 21 validator self-tests locally; neither new variant has a WinUAE PASS yet.

Only these two probes and this note were added to tests/proto. No edits to tests/current, tests/passed, examples, dist or native source.
