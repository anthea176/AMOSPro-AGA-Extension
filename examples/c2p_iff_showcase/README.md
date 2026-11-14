# C2P reference demo — genuine 320×256, 256-colour AGA IFF

**Status: WinUAE runtime PASS (2026-11-14)** — user screenshot and `C2P_IFF_SHOWCASE.TXT` log; 14/14 indices, `ERR 0`, Chip/Fast deltas 0/0. This is a standalone end-to-end visual example and does **not** replace the single active five-depth test under `tests/current/`.

## Files and setup

- [C2P_IFF_SHOWCASE.asc](C2P_IFF_SHOWCASE.asc): import into **an empty AMOS program with Merge ASCII** (not binary Load).
- [AGA_DEMO_320x256_256c.iff](../../iff-TEST/AGA_DEMO_320x256_256c.iff): unmodified, original 320×256 × 8-plane ILBM with 256 RGB colours and ByteRun1 compression.
- [AGA_DEMO_320x256_256c.chk](../../iff-TEST/AGA_DEMO_320x256_256c.chk): companion **81,920-byte raw indexed chunky** image generated deterministically from the same IFF.
- [EXPECTED_C2P_SHOWCASE.png](EXPECTED_C2P_SHOWCASE.png): **fixed expected 320×256 indexed PNG**, generated offline using the original IFF palette and precisely the Blit/Zoom rectangles from this example. It is a visual comparison target, NOT proof of WinUAE execution. PNG SHA256 `919b166c1c815df2fe08bb0d0d8c3fdbb6224bdd8b9c0bcb08e40ae3b8cedadb`.
- [Fixture regression audit](../../tools/test_c2p_iff_showcase.py): strict IFF decode, SHA checks, exact reference geometry and fourteen golden pixels.

**Place the IFF and .chk in the same AmigaDOS directory.** The program asks the user to choose the **IFF once** using `Fsel$("**")`; it derives the adjacent `.chk` path, verifies the file size and loads the raw pixels into **AMOS DATA banks 12 and 13**. **Warning: these banks are overwritten and erased.** Do not keep important project banks there.

Requirements: AMOS AGA R79 v0.13.24 candidate, `LIBS:c2p.library` v1.9, WinUAE AGA and CPU 68020+, sufficient memory. Run **interpreted first**; leave Compiler Gate C for after full C2P validation.

## Three visual stages

1. The genuine IFF is displayed with its original 256-entry palette via `Aga Iff Load`, `Aga Palette Load` and `Aga Swap`.
2. The same full image is reproduced from the raw indices through `Aga C2P Open(12)`, `Aga C2P Convert` and `Aga Swap`.
3. The **unchanged source in bank 13** is copied/scaled into chunky bank 12 with **3 Blit** and **7 nearest-neighbour Zoom** calls, including enlargement, reduction, noninteger scaling and clipping at each screen edge. The result is converted and swapped; Close → ReOpen → Convert/Swap verifies reuse and preserves the final image.

A golden reference model verifies **14 individual pixel indices**, including index 0 as an opaque sample; the AMOS program checks the same indices by `Peek` before converting. Two invalid calls must be refused without touching the destination. `Amos To Back` is called before the final ESC wait; after **ESC** the program closes resources and returns to AMOS.

Collect **`RAM:C2P_IFF_SHOWCASE.TXT`** before resetting. Expected: `RESULT 1`, `VERDICT PASS`, `PIXEL_CHECK_COUNT 14`, all `*_OK 1`, `ERR 0`, `SCREEN_CLOSE_COUNT 1`, normal `CLOSE RETURNED`. Chip/Fast before/after are logged; analyse any difference instead of automatically claiming a leak.

## Actual WinUAE result

The screenshot shows the expected Blit/Zoom regions without an obvious visual anomaly. The log confirms `RESULT 1`, `VERDICT PASS`, `PIXEL_CHECK_COUNT 14`, invalid-call rejection, Close/ReOpen/ESC success, `ERR 0` and normal return. Chip Free **1,384,608 -> 1,384,608**, Fast Free **130,438,400 -> 130,438,400**. No full native-resolution pixel diff against the golden PNG was performed on the enlarged screenshot. `PRG_STATE 1` = RUNTIME, **not** Compiler Gate C. [Report](../../docs/C2P_INTEGRATED_IFF_REFERENCE_2026-11-14.md).

### Stable reference fingerprints

| Asset | SHA256 |
|---|---|
| Original IFF (80,776 B) | `1820df9bcd77ae111b55927981482ce90c67da06d74646f6b6d92082f00db2db` |
| Raw chunky (81,920 B) | `3f4df7bc229d36ab5a2711913fa8798d1d11bfe82a6792a98e5be67ad470b694` |
| Expected composed chunky frame (81,920 B) | `57604d9abf991cc5fe17425e4247431048d4cdc3276083302bbf1359b484cd09` |

The expected composition checksum is **computed offline**, not a WinUAE measurement. Run the **stdlib-only** regression audit with `python -B tools/test_c2p_iff_showcase.py` (or `--write` to deliberately regenerate the tracked companion asset). Full AGA 16–256 colour depth coverage remains in `tests/current/`.

**Graphics copyright:** derived chunky pixels are governed by the [original art's asset licence](../../ASSETS_LICENSE.md), not by the repository's general MIT licence.

**Milestone acceptance requires actual WinUAE visual inspection and the journal.** No implicit promotion of R73 `LAST_GOOD`, Compiler Gate C, or new API is performed by this example.
