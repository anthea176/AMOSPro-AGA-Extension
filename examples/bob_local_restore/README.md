# AGA Bobs — local background restoration

An **interactive AMOS Professional example** for the AMOSPro AGA extension, **not a benchmark**. It displays an on-screen title, a multi-colour patterned background and **four moving Bobs**. Only their former positions are restored by the Blitter rather than repainting the entire screen every frame.

**Program:** [BOB_LOCAL_RESTORE.asc](BOB_LOCAL_RESTORE.asc) — standalone ASCII source, no external IFF or ABK files.

## Requirements

- **Library:** `dist/AMOSPro_AGA.Lib`, B7-m1, **102,360 bytes**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`.
- **System:** AGA chipset, MC68020 or higher; WinUAE PAL 320×256, 256 colours; 68030/JIT ON functional configuration.
- **AMOS banks 24 and 25 must be unused.** This demo refuses occupied banks; it never calls `Erase All`.
- **Runtime only** until actual B7-m1 Compiler Gate C is tested; the example deliberately rejects compiled mode.

## How to run

1. Install the extension in the chosen AMOS `APSystem` slot and restart AMOS Professional.
2. Start with an empty program and use **Project → Merge ASCII** on `BOB_LOCAL_RESTORE.asc`.
3. Run in Runtime mode. **Press any key or click to exit**; an automatic 2,400-frame limit prevents an endless unattended loop.
4. Check that AMOS returns, `RESULT 1 ERR 0` appears, the two owned banks are erased, and a second launch works without `Erase All`.

## Design

- A fixed `Aga Text` title uses y=0..31.
- The immutable clean **32-pixel-high tile source** occupies y=32..63, separate from the title. Tiles are constructed in the Blitter, with no outside assets.
- Four moving Bobs share two Bob banks: masked red shapes and opaque yellow shapes; horizontal clipping is exercised.
- Each hidden page is initialized once. Later frames **restore the old Bob rectangles for that same page** using `Aga Blit Copy`, split at 32-pixel tile boundaries; then `Aga Bob Draw` and explicit `Aga Swap` follow.
- Guarded 0/1 return handling, bounded retries, AGA close and selective bank cleanup.

**Validation:** the original textured-background benchmark **did** pass WinUAE Runtime Gate B (720/720 frames, zero errors, visual confirmation); see the [test report](../../docs/M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md). **This newly adapted titled/interactive source has not yet been run under WinUAE**; only AMOS static preflight and two-buffer geometry tests have passed. Compiler Gate C and physical Gate D remain **untested**.
