# OPT020/P2 R70 v0.13.15 — unique active WinUAE Gate B program

**Active library:** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), R70 (51,460 bytes). SHA256 `fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad`. **R70 is a working candidate only**, not the promoted reference; R68 [`LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) remains SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`.

**Only active ASC:** [`OPT020_P2_R70_INTERPRETED_01.asc`](OPT020_P2_R70_INTERPRETED_01.asc). Supersedes the P1e R69 ASC in `tests/current/` (the old revision stays accessible in Git history). This is **Gate B interpreted-only**. No new executable may be compiled for this check.

## Run under WinUAE

1. WinUAE: AGA, **68020 or 68030, JIT OFF**, record CPU/RAM. Install the active R70 library in the existing AGA extension slot in `APSystem`, restart AMOS completely.
2. In a disposable test environment, place [`M16_AGAPIC_SAMPLE_BANK10.abk`](M16_AGAPIC_SAMPLE_BANK10.abk) alongside the ASC; `Load` replaces bank 10. Open a **blank** AMOS program then **Project → Merge ASCII** the one current ASC.
3. Run using **AMOS interpreted mode only**. Do not launch AMOS Compiler. Photograph the AGA graphics and the final console. The program shows the screen for 125 VBL before closing.

## Expected results (not a claimed WinUAE PASS)

- `P2 O/M/SHIFT 1 1 1`; `P2 CLIP L/R/T/B 1 1 1 1`; `P2 OUT/BAD P/L/M/X/NOS 1 0 0 0 0 0`.
- P1e regression: `FRAMES 1 1 1 1 SHIFT 1`, `CLIP 1 1 1 1 OUT 1`, `EDGE/PART/MASK OPAQUE 1 1 1`, invalid bank/coords/size/mode all `0`.
- `LEGACY 1`, `CLOSE -1`, `NOS 0`, `RESULT 1`, `CLOSE RETURNED`.
- `CHIP BEFORE/END` must show **the same value** within the session; no freeze, Guru or obvious stray drawing.

The native CPU Gate A covers 248 real P2 scenarios (Musashi M68EC020/M68020), malformed RLE, pixel-accurate compare, canaries, front/back, DATA flags, Safe and 68000 refusal. [Technical details](../../docs/OPT020_P2_IMAGE_DRAW_68020_2026-11-13.md). **This does not establish R70's WinUAE Gate B/C or a speedup for Image Draw.** Those require the actual captures and later benchmark.
