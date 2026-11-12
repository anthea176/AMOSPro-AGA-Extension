# AMOS Compiler Gate C — R46 C1 experimental single-segment bridge

**12 novembre 2026 — EXPERIMENTAL ONLY. Gate C AMOS Compiler/WinUAE NOT PASSED.**

The user-supplied AMOSPro_AGA.Lib is exactly R46 v0.12.1 (29,288 bytes; SHA256 5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580). The GitHub main branch has since promoted the same R46 to LAST_GOOD after interpreted AMOS/WinUAE Gate B PASS. This experimental compiler bridge does not replace that validated R46, historical R44 or frozen R45.

## Why

The compiled trace established Aga Probe PASS, Aga Screen Open returns 1, then Guru 80000004 during Aga Screen Close, after step 05 and before step 06. Cross-AP20-segment BSR.w displacements are fragile because AMOS Compiler copies library routines independently. The first R44 candidate only repaired four of fourteen identified cross-segment branches. The close path also involves font-state cleanup (8 -> 48 -> 49).

## How C1 works

C1 retains every original R46 68000 instruction, GetP marker, state byte and intra/inter-routine displacement in its original position, but moves the entire 27,856-byte code block into ONE AP20 segment with a 32-byte dispatcher (27,888 bytes total, below 32 KiB). Stub entries for each original public API use Rbsr to call the dispatcher, with an embedded 16-bit offset into that original block. Register D0/A0 and return stack are intended to be preserved by the dispatcher, but this MUST be checked in actual 68000 execution.

The tradeoff is that AMOS Compiler will copy approximately 28 KiB even if only one AGA command is used; this is a compatibility experiment, not the final lean architecture.

## Candidate identity

- Artifact: dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib
- Size: 29,964 bytes
- SHA256: d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b
- Reproducible generator: tools/build_aga_compiler_bridge_r46.py
- Static check: tools/test_aga_compiler_bridge_r46.py
- Trace: tests/diagnostics/R44_COMPILER_STAGE_TRACE.asc (historical file name; tests the INSTALLED library)
- Baseline SHA is locked to the R46 0.12.1 archive. Original code block and the 50 public AMOS API definitions stay byte-for-byte identical.

## One focused WinUAE Gate C test, NO repetition of the old failing baseline

1. Backup the actually installed APSystem/AMOSPro_AGA.Lib and the interpreter configuration.
2. Copy the experimental C1 library under the exact configured APSystem filename AMOSPro_AGA.Lib. Do NOT replace the canonical GitHub binaries or LAST_GOOD.
3. Fully restart AMOS Professional and AMOS Compiler. Import the existing trace in a new blank project. **Recompile**: a previously compiled executable embeds the OLD library routines and will not test C1.
4. Execute under WinUAE. Pass criterion for this diagnostic is 06 AFTER AGA SCREEN CLOSE and clean program exit without Guru. If Guru returns, capture the true exception PC and preceding trace; a ROM STOP after reset is not the fault PC.
5. If the minimal compiler trace passes, verify mouse cursor cleanup, fonts, double buffer and Aga Image Draw in BOTH interpreted and compiled contexts before a promotion or closure.

**Static host tests PASS, CPU execution and WinUAE Gate C NOT TESTED.** Do not promote to LAST_GOOD based on static checks.
