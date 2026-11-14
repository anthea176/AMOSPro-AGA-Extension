# R82 AGAPIC v2 — WinUAE interpreted Gate B (NOT YET EXECUTED)

**Only active AMOS test:** [AGAPIC_R82_V2_BANK_PALETTE_01.asc](AGAPIC_R82_V2_BANK_PALETTE_01.asc). **Current R82 v0.13.27 candidate**: `dist/AMOSPro_AGA.Lib`, 64,112 bytes, SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`; 74 commands / 81 AP20 entries; native Gate A PASS. WinUAE B / Compiler C / real Amiga D NOT TESTED.

**R81 v0.13.26 remains the protected `LAST_GOOD`** in `dist/AMOSPro_AGA_LAST_GOOD.Lib`, SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`, fully separate from the working R82 candidate. Existing historical R81 tests remain in Git history; do not run R82 with an old extension loaded.

## WinUAE interpreted procedure

1. In WinUAE AGA with CPU 68020+ install the **R82 candidate** into the existing AMOS Professional extension slot (historically slot 14 if available). Restart AMOS and check the loaded extension.
2. Copy `R82_AGAPIC_V2_BANK10.abk` and `R82_AGAPIC_V1_BANK12.abk` beside the ASC. They overwrite AMOS DATA banks 10 and 12; the test also reserves bank 11. **Use a disposable AMOS session.**
3. Open an empty AMOS program; **Project → Merge ASCII** the sole active ASC. Run **interpreted first**. It opens a 320×256×256-colour PAL LowRes double-buffered screen, applies AGAPIC v2 / AGAPAL palettes, tests Init/Capture/Apply/Fade, draws v1/v2 images and regions and validates rejection paths.
4. The image remains visible for a bounded 100 VBL before normal cleanup. The program restores the AMOS screen, erases banks 10/11/12 and returns with `End`.
5. Copy **`RAM:AGAPIC_R82_INTERPRETED.TXT`** outside RAM: before reset. Expected, **not yet observed**: `RESULT 1`, `VERDICT PASS`, `INVALID_OK 1`, `DRAW_V1_OK 1`, `DRAW_V2_OK 1`, `REGION_V1_OK 1`, `REGION_V2_OK 1`, `ERR 0`, `CLOSE_RETURNED 1`.
6. Report any Guru, graphical discrepancy, missing logs or failure with the displayed error code. **Do not compile before Gate B is accepted**; Gate C is a separate final step.

[Gate A report](../../docs/AGAPIC_V2_R82_P1_GATE_A_2026-11-14.md).
