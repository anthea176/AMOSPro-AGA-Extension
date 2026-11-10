# AMOSPro AGA — 5 simple examples

**English** | [Français](README.fr.md) · [Installation](../INSTALL.md)

These are **user-facing examples**, not historical regression tests. Use the current [`AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) and run them as **interpreted AMOS Professional** programs.

| File | Demonstrates | What to do |
|---|---|---|
| [`screen.asc`](screen.asc) | Open/close a 320×256×256-colour screen | Runs a pattern for about 3 seconds; no image required |
| [`picture.asc`](picture.asc) | Read IFF metadata, load image, swap buffers | Select the included [`demo.iff`](demo.iff), then press a key |
| [`blitter.asc`](blitter.asc) | `Aga Blit Fill`, `Clear`, `Copy` | Select `demo.iff`, look at the shapes, then press a key |
| [`copper.asc`](copper.asc) | RGB4 Copper raster via `Wait`/`Move` | Shows red/green/blue/black horizontal bands, then press a key |
| [`mouse.asc`](mouse.asc) | Coordinates, click edges, keyboard polling | Click left/right, then press a key or let the 5-second timer end |

The `.asc` files are plain ASCII source. In AMOS, select **New → Project / Merge ASCII** to import one file at a time. Do **not** use the normal `Load` command for these files. When asked to choose an image via `Fsel$("**")`, browse to `examples/demo.iff` **from AmigaOS**.

The bundled `demo.iff` is a 320×256, 8-bitplane, 256-colour original test card also kept in `iff-TEST/`. The examples have static checks, **but their new end-to-end scripts have not yet been validated under WinUAE**. The R23 input dispatcher is still a candidate (Ctrl+C not tested).

Development/regression cases remain in [`tests/current/`](../tests/current/), [`tests/passed/`](../tests/passed/) and [`tests/historical/`](../tests/historical/). **Do not distribute those versioned test scripts as beginner examples.**

**Licensing:** script source is [MIT](../LICENSE). The included image is **not MIT**: [visual asset terms](../ASSETS_LICENSE.md), local testing permitted; redistribution/reuse of the artwork separately requires permission.
