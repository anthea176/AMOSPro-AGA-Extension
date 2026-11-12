# AMOSPro AGA Extension - Aminet publication preparation

Prepared 12 November 2026. **Draft only - nothing uploaded or modified on GitHub.**

## Recommended release baseline

- **Aminet category:** `dev/amos`
- **LHA filename:** `AMOSProAGA.lha`
- **Companion metadata:** `AMOSProAGA.readme` (this draft has `Short:` of 35 characters)
- **Version in draft:** `R54 / v0.12.9`, current officially promoted `LAST_GOOD`
- **Author:** HWARF
- **Uploader:** reproduced from the supplied `Oracle-src.readme`; check the address before sending
- **Architecture:** `m68k-amigaos`

**Important:** at the time of preparation, `dist/AMOSPro_AGA.Lib` on `main` is the newer **R57 / v0.13.2 development binary**, not the R54 stable binary. **Do not package that file by mistake.** Use `dist/AMOSPro_AGA_LAST_GOOD.Lib` (R54), copy it inside the distribution archive under the install name **`AMOSPro_AGA.Lib`**.

Expected R54 library:

- Length: **32,364 bytes**
- SHA-256: `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`
- 53 named AMOS instructions/functions, 60 AP20 entries
- Gate A automated CPU/CI PASS, Gate B AMOS interpreted/WinUAE PASS and Gate C newly compiled executable/WinUAE PASS on the documented scenario
- Gate D on a physical AGA machine **not yet tested**

Sources: `README.md`, `docs/ROADMAP.md`, `docs/M16_R54_BANK_NUMBER.md`, `docs/LIBRARY_TEST_HISTORY.md` from the GitHub `main` branch (12 November 2026).

## Recommended contents of AMOSProAGA.lha

```text
AMOSProAGA/
  AMOSPro_AGA.Lib        <- copy of R54 LAST_GOOD, with install filename
  README.md             <- release-specific readme (remove stale R57 references)
  INSTALL.md            <- release-specific instructions (repair stale links)
  LICENSE               <- code and technical documentation: MIT
  ASSETS_LICENSE.md     <- if any visual assets are included
  examples/
    README.md
    screen.asc
    picture.asc
    blitter.asc
    copper.asc
    mouse.asc
    m15_2d_cursor.asc
    demo.iff             <- include only with the author's authorization
    bank_number_r54/    <- R54 validated scenario and required assets/licences
```

This layout is a **recommendation**, not an existing archive. Include only examples whose required assets are present; do not imply the stand-alone examples have all passed end-to-end testing. If shipping additional ABK fonts, include their original attribution/licence files and check redistribution permission (including Pix3M CC BY terms).

Avoid bundling `tests/current/`, `dist/experimental/`, stale libraries, development-only benchmarks, copyrighted/fan-art illustrations, or the complete working repository into the beginner package.

## Before submission

- [ ] Decide whether to publish **R54** now or to promote **R57** after completing release validation. If the latter, update all version references and rebuild the draft metadata.
- [ ] Check the exact library SHA-256 and byte size **inside the final `.lha`**.
- [ ] Check that `Short:` is at most **40 characters**: `AGA graphics extension for AMOS Pro` = **35**.
- [ ] Keep the `.lha` and `.readme` basenames **identical**.
- [ ] Check that **INSTALL.md and README.md refer to the packaged library**, not the current `dist/AMOSPro_AGA.Lib` development build. GitHub INSTALL.md still has outdated R54 wording/links while the current installable file is R57.
- [ ] Check extension registration (default historical slot 14 only if free), restart and ASCII merge instructions on an actual clean AMOS setup.
- [ ] Check the included samples do not refer to external files missing from the archive.
- [ ] Confirm code MIT licence and separate artwork/font terms; exclude assets without redistribution permission.
- [ ] Verify LHA archive integrity and inspect its contents before uploading.
- [ ] Upload `AMOSProAGA.lha` with `AMOSProAGA.readme` to Aminet under `dev/amos`.

No release archive has been created or uploaded as part of this preparation.
