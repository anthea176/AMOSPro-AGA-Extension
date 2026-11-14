# R82 AGAPIC v2 — Gates A / WinUAE Runtime B / Compiler C PASS (14/11/2026)

**Only active AMOS test:** [AGAPIC_R82_V2_BANK_PALETTE_01.asc](AGAPIC_R82_V2_BANK_PALETTE_01.asc). **Promoted R82 v0.13.27 `LAST_GOOD`**: `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib`, **64,112 bytes**, SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`, **74 commands / 81 AP20 entries**, 4,562-byte Compiler V2 headroom. Gates **A native / WinUAE Runtime B / AMOS Compiler C PASS** on the documented CPU 68030 AGAPIC test. Pure interpreted `PRG_STATE 0` and physical D **NOT TESTED**.

**Historical R81 v0.13.26:** SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`, 59,972 bytes, previously promoted `LAST_GOOD`, now available [through Git history](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/aed079ec05102c992d8440f86522e8b8875df8e7/dist/AMOSPro_AGA_LAST_GOOD.Lib) and the unchanged deterministic `tools/build_c2p_r81_opt020.py` builder.

## WinUAE test and evidence

1. Install R82 into the existing AMOS Professional extension slot in a WinUAE AGA setup with CPU 68020 or newer; restart AMOS.
2. Copy `R82_AGAPIC_V2_BANK10.abk` and `R82_AGAPIC_V1_BANK12.abk` beside the ASC. The test loads DATA banks 10 and 12 and reserves bank 11; use a disposable AMOS session.
3. In a fresh AMOS program, use **Project → Merge ASCII** with the sole active ASC. Its indexed 320×256×256-colour PAL LowRes screen tests AGAPIC v2 and AGAPAL palettes, Init/Capture/Apply/Fade, image draw, masked regions, invalid inputs and Swap.
4. The author has **already tested Runtime and compiled modes** under WinUAE 68030. Both logs report `RESULT 1`, `VERDICT PASS`, all feature flags 1, `ERR 0`, `CLOSE_RETURNED 1`, and zero net Chip/Fast RAM differences. A screenshot confirms the displayed multicolour image atlas and cropped regions.
5. The captured source logs are [Runtime](../../docs/evidence/AGAPIC_R82_RUNTIME_2026-11-14.TXT) and [Compiled](../../docs/evidence/AGAPIC_R82_COMPILED_2026-11-14.TXT). **No `PRG_STATE 0` report or physical Amiga test** has been received. Do not interpret these as universal tests of all CPU/mode combinations.

[Promotion report](../../docs/AGAPIC_R82_LAST_GOOD_PROMOTION_2026-11-14.md) · [WinUAE report](../../docs/AGAPIC_R82_WINUAE_RUNTIME_COMPILER_2026-11-14.md) · [Native Gate A report](../../docs/AGAPIC_V2_R82_P1_GATE_A_2026-11-14.md).
