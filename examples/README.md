# AMOSPro AGA — 11 simple examples

**English** | [Français](README.fr.md) · [Installation](../INSTALL.md)

**Current release: R46 v0.12.1** is `LAST_GOOD` for interpreted AMOS/WinUAE (Gates A/B). The separate experimental **R46 C1** has passed compiled Open/Close, graphics and Image Draw tests; complete Compiler Gate C remains open. [Gate C progress](../docs/GATE_C_R46_MONOLITH_CANDIDATE.md).

**Chip RAM endurance:** a separate [500-switch WinUAE stress test](../tests/passed/M14_R38_CHIP_RAM_STRESS_01.asc) passed on 12 November 2026 with no measured loss of total or largest free Chip RAM.

These are **user-facing examples**, not historical regression tests. Most run in interpreted AMOS with the [current release](../dist/AMOSPro_AGA.Lib); the new all-in-one compiled test explicitly requires experimental **R46 C1**.

| File | Demonstrates | What to do |
|---|---|---|
| [`screen.asc`](screen.asc) | Open/close a 320×256×256-colour screen | Runs a pattern for about 3 seconds; no image required |
| [`picture.asc`](picture.asc) | Read IFF metadata, load image, swap buffers | Select the included [`demo.iff`](demo.iff), then press a key |
| [`blitter.asc`](blitter.asc) | `Aga Blit Fill`, `Clear`, `Copy` | Select `demo.iff`, look at the shapes, then press a key |
| [`copper.asc`](copper.asc) | RGB4 Copper raster via `Wait`/`Move` | Shows red/green/blue/black horizontal bands, then press a key |
| [`mouse.asc`](mouse.asc) | Coordinates, click edges, keyboard polling | Click left/right, then press a key or let the 5-second timer end |
| [`collide.asc`](collide.asc) | R25 `Aga Rect Overlap`, mouse, Blitter, double buffering and VBL | Select `demo.iff`, move into/out of the blue rectangle (green = free, red = overlap); left-click to exit, or wait 900 frames |
| [`show.asc`](show.asc) | **R27 animated showcase:** native AGA text, a neon-style HUD, safe double-buffered Blitter Fill/Clear/Copy, moving and mirrored rectangles, AABB collision and mouse position | Select `demo.iff`, watch the moving green/red blocks, move the cursor; **left-click or press a key** to exit (automatic stop after up to 600 frames) |
| [`fade_to_bank_r33.asc`](fade_to_bank_r33.asc) | **R33 visible RGB24 fade demo:** three large coloured strips, RED → GREEN → BLUE → RED, each transition 150 VBL | No IFF needed. **Overwrites bank 12**; `Aga Swap` and `Amos To Back` run **before** the fades. Pauses between transitions; results appear after the screen closes. **User-confirmed visible, working fade in WinUAE (11 Nov 2026); no FPS/timing measurement.** |
| [`font_bank_r38.asc`](font_bank_r38.asc) | **R38 AMCAF BankFont showcase:** draw text with `Hwarf1252S.abk` and `Pix3M-1252L.abk` on the same 320×256 AGA screen | Requires R38 v0.11.0; run from the `examples/` directory with `Amcaf Fonts/` present; **replaces AMOS bank 25**; press a key to exit. |
| [`m15_2d_cursor.asc`](m15_2d_cursor.asc) | **M15 + M15bis combined showcase (R44):** Plot stars, Draw axes and a moving crosshair, Box frames, Circle radar rings and custom reticle, plus window-local `Aga Mouse Cursor` visibility | **No IFF or font bank needed.** Move the mouse, **right-click** to show/hide the system cursor, **left-click or press a key** to exit (automatic stop at 600 frames). R44 v0.11.5 or later required; **user-confirmed WinUAE working (12 Nov 2026).** |
| [`compiler_r46_all_in_one/COMPILER_R46_ALL_IN_ONE.asc`](compiler_r46_all_in_one/COMPILER_R46_ALL_IN_ONE.asc) | **R46 C1 all-in-one Compiler test:** AGAPIC opaque/masked images, clipping, Plot/Draw/Box/Circle, double buffer, two fonts, 500 cursor toggles and full screen cleanup | **One ASC plus two included ABKs.** Keep the bundled directory together; compile with experimental R46 C1. Report `RESULT 1` and `CLOSE RETURNED`. **New example, not yet tested.** |

**R46 Compiler all-in-one test:** [open the self-contained folder](compiler_r46_all_in_one/) and follow its [setup instructions](compiler_r46_all_in_one/README.md). The single ASC uses two bundled ABKs; **run the compiled executable with that folder as the AmigaDOS current directory**. The test does not modify any official `LAST_GOOD` library.

**M15 + M15bis interactive demo — `m15_2d_cursor.asc`:** a self-contained 320×256 AGA scene with a 256-colour palette and safe double buffering. It draws 23 stars using Plot, axes and a moving crosshair with Draw, frames with Box, concentric radar rings and a moving reticle using Circle, and controls the R44 private-window cursor. The system pointer starts hidden; **right-click** toggles it, **left-click or any key** exits, or it stops after 600 frames. Closing the window automatically restores the system cursor. Bounded 12-attempt Safe/VBL retries protect `Aga Blit Clear` and `Aga Swap`. After return to AMOS, success prints `ERROR 0`, `RESULT 1`, `CLOSE RETURNED`. **Requires R44; user-confirmed rendering and interaction under WinUAE (12 Nov 2026), without a separate numerical result screenshot.** No IFF, ABK or other files.

**R38 font demo — `font_bank_r38.asc`:** load `Amcaf Fonts/Hwarf1252S.abk` and `Amcaf Fonts/Pix3M-1252L.abk` **one after the other** using `Load "...",25`, `Aga Font Bank Select(Start(25),Length(25))` and `Aga Text`. Both ABKs have bank number 25, which the demo overwrites. `Erase 25` is safe after a successful selection because R38 creates its own Chip RAM copy. The example resets the system font with `Aga Font Select("",0)` and closes the screen. Use `/` as the **AmigaDOS directory separator** (Windows paths may show `\\`); run with `examples/` as the current AmigaDOS directory, for example after copying the complete `examples/` folder to an Amiga volume. **No AMCAF extension is required at runtime.** **The R38 font demo was run successfully under interpreted AMOS/WinUAE (user-confirmed, 12 November 2026).** No long-duration Chip RAM stress test is claimed.

**Font attribution:** Hwarf BankFont: [Hwarf licence/attribution](Amcaf%20Fonts/Hwarf-12xxS.licence). Pix3M font: [Pix3M attribution (CC BY 3.0)](Amcaf%20Fonts/Pix3M-12xxL.licence). The ABK artwork is not covered by the source-code MIT licence.

The `.asc` files are plain ASCII source. In AMOS, select **New → Project / Merge ASCII** to import one file at a time. Do **not** use the normal `Load` command for these files. When asked to choose an image via `Fsel$("**")`, browse to `examples/demo.iff` **from AmigaOS**.

The bundled `demo.iff` is a 320×256, 8-bitplane, 256-colour original test card also kept in `iff-TEST/`. The ten earlier examples have static checks; the new compiler integration example is not yet verified under WinUAE. **The R33 fade demo was run successfully with visible transitions under WinUAE (user-confirmed); the other standalone examples have not all been validated end-to-end.** The separate R23 input/Ctrl+C and R25 collision regression scenarios passed interpreted AMOS/WinUAE; those results do not automatically certify these shortened examples.

**Why load an IFF for `collide.asc`?** `demo.iff` supplies the PAL video mode and the palette (index 3 = blue, 28 = green, 224 = red). The example clears the entire back buffer before every frame, so **the picture itself is not displayed and does not take part in collision detection**. An `Aga Rect Overlap` test needs no IFF or screen; the file is only needed here for predictable display colours.


**R27 showcase — `show.asc`:** the bundled IFF supplies the PAL mode and indexed colours only (0 = background, 3 = blue, 28 = green, 224 = red). The example **redraws every pixel through AGA functions**; the IFF image itself is not used as art. The first `Aga Blit Clear` of each frame has a **12-attempt VBL-bounded Safe retry**; `Aga Swap` is retried with the same bound. It illustrates the R27 automatic Safe protection, native `Aga Text`, `Aga Blit Copy`, `Aga Rect Overlap` and mouse/keyboard input. **This is an unverified example, not a WinUAE-PASS regression test and not an FPS benchmark.** See [the R27 validation test](../tests/passed/M12_R27_SAFE_BLIT_01.asc) for the separate 40-swap evidence.

Development/regression cases remain in [`tests/current/`](../tests/current/), [`tests/passed/`](../tests/passed/) and [`tests/historical/`](../tests/historical/). **Do not distribute those versioned test scripts as beginner examples.**

**Licensing:** example script source is [MIT](../LICENSE). The bundled font artwork has separate [Hwarf](Amcaf%20Fonts/Hwarf-12xxS.licence) and [Pix3M](Amcaf%20Fonts/Pix3M-12xxL.licence) attribution terms. The included image is **not MIT**: [visual asset terms](../ASSETS_LICENSE.md), local testing permitted; redistribution/reuse of the artwork separately requires permission.
