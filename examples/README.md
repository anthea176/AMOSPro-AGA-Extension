# AMOSPro AGA — examples

[Français](README.fr.md) · [Installation](../INSTALL.md) · [Promoted R73 library](../dist/AMOSPro_AGA_LAST_GOOD.Lib)

**Promoted reference: R73 v0.13.18 `LAST_GOOD`** (Gates A/B/C). The current working `dist/AMOSPro_AGA.Lib` is the **R79 v0.13.24 development candidate** (Zoom native CPU Gate A PASS; **this integrated IFF demonstration has not yet been run under WinUAE**). Older examples can use R73, but **the C2P IFF showcase requires R79 and `LIBS:c2p.library` v1.9**. Hardware Gate D is untested. Passing library tests does not automatically validate each standalone demo.

## Run an example

1. Install `AMOSPro_AGA.Lib` in the appropriate AMOS `APSystem` extension slot, then restart AMOS Professional.
2. Use a **new empty program → Project → Merge ASCII** to import a `.asc` file. The files are ASCII source, not tokenized AMOS programs.
3. Keep any required `.abk` and `.iff` resources in the directory expected by the source, and check that the AMOS bank numbers used by the demo are free.
4. For IFF-based demos, select [`demo.iff`](demo.iff) from AmigaOS. Close the AGA screen and return to AMOS before trying another example.

## Self-contained graphics demonstrations

| Source | What it shows | Requirements / validation |
|---|---|---|
| [`screen.asc`](screen.asc) | Opens and closes a 320×256, 256-colour AGA screen | No external image |
| [`picture.asc`](picture.asc) | IFF metadata, image loading, double buffering | Select `demo.iff` |
| [`blitter.asc`](blitter.asc) | Blitter fill, clear and copy | Select `demo.iff` |
| [`copper.asc`](copper.asc) | RGB4 Copper raster bands | No assets |
| [`mouse.asc`](mouse.asc) | Pointer position, buttons and keyboard | Click / press a key |
| [`collide.asc`](collide.asc) | AABB overlap, mouse and animated back buffer | `demo.iff` provides the PAL mode/palette; left-click to exit |
| [`show.asc`](show.asc) | Animated HUD, text, drawing, collision and safe swaps | `demo.iff` supplies the mode/palette; click/key to exit |
| [`fade_to_bank.asc`](fade_to_bank.asc) | Three coloured bars and RGB24 palette transitions | Replaces bank **12**; **visible fade user-confirmed in interpreted WinUAE** |
| [`font_bank.asc`](font_bank.asc) | AMCAF BankFonts: Hwarf and Pix3M | Run from `examples/` with [`Amcaf Fonts/`](Amcaf%20Fonts/), replaces bank **25**; user-confirmed interpreted WinUAE |
| [`2d_cursor.asc`](2d_cursor.asc) | Plot, Draw, Box, Circle, moving reticle and local pointer visibility | No external files; right-click toggles pointer, left-click/key exits; **user-confirmed WinUAE** |

The basic graphics demos are statically checked. Only the specific user-confirmed scenarios above have direct WinUAE evidence; other standalone programs have not all been validated end-to-end.

## Extended examples

| Example | Description | Bank use / validation |
|---|---|---|
| [**C2P IFF golden showcase**](c2p_iff_showcase/README.md) · [ASC](c2p_iff_showcase/C2P_IFF_SHOWCASE.asc) · [expected PNG](c2p_iff_showcase/EXPECTED_C2P_SHOWCASE.png) | End-to-end real **320×256×256 colour fantasy AGA IFF**: IFF/Palette → C2P Convert/Swap → 3 Blit + 7 Zoom (enlarge/reduce/clip) → Close/ReOpen; 14 golden indices and RAM report | **Requires R79 candidate** plus `LIBS:c2p.library`; original IFF and `.chk` companion together in `iff-TEST/`; **overwrites banks 12/13**; offline oracle verified, **WinUAE runtime pending** |
| [**IFF to ABK converter**](iff_to_abk/README.md) · [ASC](iff_to_abk/IFF_TO_ABK.asc) | Select IFF via `Fsel$`, capture AGAPIC, save **ABK + palette-only IFF**, clear, reload, display **CHARGEMENT ABK**, reconstruct and `Aga Wait Key` | **Erase 11** at startup overwrites existing bank 11; output `RAM:IFF_TO_ABK.abk` and matching `.iff`. WinUAE execution pending |
| [**ABK viewer**](iff_to_abk/README.md) · [ASC](iff_to_abk/ABK_VIEWER.asc) | Select ABK, automatically load matching palette-only `.iff` in its directory; display on PAL 320×256 until `Aga Wait Key` | Destructive **Erase 11**; requires AGAPIC v1 and companion palette; WinUAE execution pending |
| [**CBlock Chip Lab**](cblock_chip/README.md) · [ASC](cblock_chip/CBLOCK_CHIP_LAB.asc) | Temporary planar Chip background capture, draw and restore. **Method is mandatory:** `0` CPU8, `1` CPU16, `2` Blitter; **no AUTO** | Requires free bank **11** and R68+; **this standalone showcase is only statically checked**. The R68 API passed separate WinUAE/Compiler tests |
| [**Fast Icon Lab**](fast_icons/README.md) · [ASC](fast_icons/FAST_ICON_LAB.asc) | `FICON8` source, `FICHIP8` staging, unaligned capture, CPU/Blitter masked/opaque rendering | Requires free banks **11, 12, 13**, R67+ commands (included in R68); **user-confirmed interpreted WinUAE**; showcase not separately compiled |
| [**Bank-number helpers**](bank_number/README.md) · [ASC](bank_number/BANK_NUMBER_HELPERS.asc) | Draw AGAPIC and select font by bank number, versus address/length calls | Replaces banks **10/25**, requires bundled ABK files. Original R54 regression passed interpreted + freshly compiled WinUAE; public copy has a renamed asset path and has not been rerun independently |
| [**Compiler all-in-one**](compiler_all_in_one/README.md) · [ASC](compiler_all_in_one/COMPILER_ALL_IN_ONE.asc) | Historical R46 C1 integrated image, 2D, fonts, cursor and cleanup showcase | Replaces banks **10/25**. Original compiled WinUAE test passed; renamed public ASC has an adapted resource filename and has **not** been recompiled |

**Historical ZIP:** [`COMPILER_ALL_IN_ONE.zip`](COMPILER_ALL_IN_ONE.zip) is **byte-for-byte the original R46 C1 validated archive**, with its **original versioned internal filenames**. Its outer name is simplified, but the ZIP contents are intentionally not rewritten. To reproduce the exact old Compiler validation, extract the ZIP and use its original names. For clean public filenames, use [`compiler_all_in_one/`](compiler_all_in_one/) instead; the modified public copy needs a new Compiler run to claim separate runtime validation.

## Resources and safety

- The included [`demo.iff`](demo.iff) is a 320×256×256-colour PAL test card. In `collide.asc` and `show.asc` it primarily establishes the video mode and palette; the drawing is generated by AGA commands.
- **Bank numbers matter.** `Reserve As Data` and `Load` may overwrite an existing AMOS bank. Start from a fresh, disposable program or back up your banks.
- For `font_bank.asc`, use the exact relative paths `Amcaf Fonts/Hwarf1252S.abk` and `Amcaf Fonts/Pix3M-1252L.abk`. **No separate AMCAF extension is needed** to display these bank fonts through the AGA extension.
- `.asc` sources should be imported with **Merge ASCII**, not the normal AMOS `Load` command.
- The original, version-labelled regression sources live in [`tests/passed/`](../tests/passed/), not in these cleaned-up public example names. Renaming a bundled asset does **not** retroactively validate the adapted ASC.

**Licensing:** example source is [MIT](../LICENSE). Hwarf and Pix3M fonts retain their [Hwarf](Amcaf%20Fonts/Hwarf-12xxS.licence) and [Pix3M](Amcaf%20Fonts/Pix3M-12xxL.licence) licences. The IFF/art assets have [separate terms](../ASSETS_LICENSE.md). 
