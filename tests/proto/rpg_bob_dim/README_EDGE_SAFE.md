# P2d Bob 20x18 : opaque bottom-right pixel and pre-Swap VBL

Non-distributed Runtime probe derived byte-for-byte from the earlier P2d 20x18 opaque-edge probe, plus a single explicit `Aga Wait Vbl` before the implicit P2d Bob Auto Update and each frame's first `Aga Swap`.

## WinUAE logs received 23 November 2026 (source filenames, not yet archived in Git)

- `P2_SWAPVBL20X18_RUNTIME.TXT`: Gate B PASS, `RESULT 1`, `ERR 0`, `PRE_SWAP_VBLS 240`, `SWAP_REFUSALS 0`, `VALID_SAMPLES 240`, `CLOSE_RETURNED 1`.
- `P2_EDGE20X18_RUNTIME.TXT`: Gate B FAIL, `ERR 15`, `FRAME 221`, `SWAP_REFUSALS 111`, `SWAP_RECOVERED 110`, `LAST_REFUSAL_TRIES 4`. The 123 samples of the opaque pixel at local (19,17) all passed (`EDGE_VALUE_LAST 165`, `EDGE_EXPECTED 165`); this DOES NOT make the whole test PASS.

The new probe isolates whether an already-safe back buffer also makes the 20x18 opaque-edge test stable. A refused Swap can arise from an unavailable SafePort or from a failed implicit Bob Update leaving a protected DIRTY frame; the present logs do not distinguish the two reasons in the last failure.

## New probe

`P2_EDGE_SWAPVBL_20X18.asc`

- Run with M19 P2d LAST_GOOD SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 68020+ AGA PAL, using `Project -> Merge ASCII` into a clean AMOS program.
- No external IFF/ABK. 240 AMAL cycles, the unchanged Bob code path and 8-plane pixel capture are retained.
- Runtime journal: `RAM:P2_EDGESAFE20X18_RUNTIME.TXT`.
- Gate B expected: `RESULT 1`, `ERR 0`, `VALID_SAMPLES 240`, `EDGE_SAMPLES > 2`, `EDGE_VALUE_LAST 165`, `SWAPS 241`, `PRE_SWAP_VBLS 240`, `SWAP_REFUSALS 0`, `CLOSE_RETURNED 1`. Recovered refusal counts are still logged if present; a completed run can remain PASS with recovered refusals.
- A VBL before the Swap is **in addition to** the existing post-Swap VBL. This is a safety/diagnostic test, NOT a claim of 50 fps performance or an optimized render loop.

Static preflight: PASS, validation tool self-tests: 21 PASS. Runtime and Compiler: **NOT TESTED** for the new combined variant until new logs are received.

`dist/`, `tests/current/`, `tests/passed/`, and distributed examples are unchanged.
