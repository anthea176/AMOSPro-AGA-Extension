# IFF ↔ AGAPIC ABK — converter and viewer

[Français](README.fr.md) · [All examples](../README.md)

Two independent AMOS Professional examples are available. Import either **ASCII source** using **Project → Merge ASCII**. Use the promoted **R68 `AMOSPro_AGA_LAST_GOOD.Lib`**, installed as `AMOSPro_AGA.Lib` in the configured `APSystem` extension slot. Neither example has yet been executed independently under WinUAE.

## 1. Convert an IFF to ABK + palette

[**IFF_TO_ABK.asc**](IFF_TO_ABK.asc) selects an indexed IFF/ILBM via `Fsel$("**")`, opens an AGA screen, loads its pixels and captures the whole **back buffer** as an opaque AGAPIC DATA bank 11. It saves **two files together**:

| Output | Contents |
|---|---|
| `RAM:IFF_TO_ABK.abk` | Native AMOS ABK containing compressed indexed image pixels (AGAPIC v1) |
| `RAM:IFF_TO_ABK.iff` | Palette-only `FORM ILBM` with `BMHD` and `CMAP` from `Aga Palette Save`; **no image BODY** |

The demonstration briefly displays the original IFF, erases bank 11, clears the screen and shows **CHARGEMENT ABK**. It loads the **saved ABK**, clears the back buffer, redraws the image using `Aga Bank Image Draw`, restores the **saved companion palette only** with `Aga Palette Load`, then waits for `Aga Wait Key`.

The companion palette path is automatically derived from the ABK filename. Change only `_ABK$="RAM:IFF_TO_ABK.abk"` to choose a different writable directory or basename; the matching `.iff` file is saved alongside it. Files in `RAM:` disappear after reboot.

## 2. Display an ABK without its original IFF

[**ABK_VIEWER.asc**](ABK_VIEWER.asc) is a separate, minimal image viewer. Select the **`.abk`** with `Fsel$("**")`; it automatically looks for the palette-only **`.iff` with the same basename in the same directory**. It reads the AGAPIC header from the DATA bank to identify the image width, height and depth, opens an indexed PAL LowRes 320×256 AGA screen, clears its back buffer and draws the reloaded ABK. The viewer shows the picture until `Aga Wait Key`, without accessing the original source IFF.

**Viewer limits:** AGAPIC v1, depth 1–8 planes, width ≤ 320 and height ≤ 256 pixels; PAL LowRes mode `$00021000`. A palette-only companion `.iff` is required. The ABK does not contain a palette or display-mode identifier, so arbitrary video modes and larger images are not supported by this simple viewer.

## Warning / validation

**Both programs explicitly call `Erase 11` before creating/loading bank 11. Any existing bank 11 is destroyed.** Use a fresh AMOS session or save important banks first. Native AMOS `Save`/`Load` file errors may halt the interpreter. Both output files are overwritten when the converter runs again.

Try [`examples/demo.iff`](../demo.iff) (320×256, 256 colours) first. The code is statically checked, but **visual WinUAE/AMOS execution is still required**; no Compiler or physical Amiga validation is claimed.
