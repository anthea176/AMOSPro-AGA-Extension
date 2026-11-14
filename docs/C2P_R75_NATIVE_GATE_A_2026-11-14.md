# C2P R75 — native Convert Gate A (14/11/2026)

**Statut : R75 Convert source built in memory and native Gate A PASS; NOT YET INSTALLED as active library.** The current R74 v0.13.19 binary remains the sole active `dist/AMOSPro_AGA.Lib`, and R73 v0.13.18 remains the byte-protected `LAST_GOOD`.

## Authorized API

`_OK=Aga C2P Convert` is an integer **no-argument function**. It uses the AMOS bank configured by the already validated `Aga C2P Open(Bank)`, revalidates the bank at every call, updates the SDK chunky pointer, performs `C2P_Chunky2Planar` into its own dedicated Chip bitmap, and copies into the actual **inactive** Intuition AGA back bitmap using `graphics.library/BltBitMap` followed by `WaitBlit`. **No automatic `Aga Swap` or palette writes.** Supported: 320x256, **4..8 bitplanes**, 68020+.

## Native checks

- Native emitter: `tools/c2p_r75_convert_emit.py`, **1,492 bytes**, native byte SHA256 `447c6579f308ee59c0a60a1ba72c0221152a4379d27856d1adc89d9282e944c6` (emitter checked locally).
- Deterministic AP20 V2 wrapper: `tools/build_c2p_r75_convert.py` starts from pinned R74 SHA256 `887f29c0350f47af9d93d1ebf64fc405c8542e897ff0e7d9d95eda6f814c2a23`, adding one public function at native entry 71. The preexisting native entries 0..69 and the R74 Open entry 70 are preserved except the required `GetP` delimiter.
- Native CPU validation: `tools/test_c2p_r75_convert_gate_a.py`, **22 test scenarios PASS** under machine68k, with Capstone M68000 instruction check, AP20 entry count and historical branch links.
- Coverage includes 4/5/6/7/8 planes, separate and interleaved back layouts, front never modified, no implicit swap, two WaitBlit calls, unavailable SafePort (one nonblocking GetMsg), Safe/Disp bit preservation, flipped front index, erased/too short/reallocated bank, invalid source Chip plane, invalid destination plane, missing context, invalid depth, CPU feature rejection, SDK errors, partial BltBitMap and cleanup.
- The emulated C2P/Blitter functions are **mock OS/SDK calls**; Gate A is not a real pixel-level c2p.library or WinUAE test.
- `ScreenBuffer.sb_BitMap` is read at **+0**; `ScreenBuffer+4` is DBufInfo. No GDB/Powershell diagnostic is needed.

## Gates and next steps

- **Gate A Native CPU/ABI: PASS** on GitHub Actions run [43589098566](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43589098566), step `R75 C2P Convert (in-memory) 68k Gate A`.
- **Gate B AMOS/WinUAE: NOT TESTED** until an R75 binary is installed and the unique active ASC runs.
- **Gate C Compiler: NOT TESTED**; one combined C2P Compiler Gate C at the final milestone only, not one per function.
- **Gate D hardware: NOT TESTED**.
- R75 `Aga C2P Close` is **not implemented or approved**.
- **No promotion**: R73 LAST_GOOD remains protected.

[Contract](C2P_R75_CONVERT_CONTRACT_2026-11-14.md) · [R74 Open Gate B](C2P_R74_WINUAE_GATE_B_2026-11-14.md).
