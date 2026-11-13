# IFF to AGAPIC ABK — visual round trip

[Français](README.fr.md) · [All examples](../README.md)

Open [`IFF_TO_ABK.asc`](IFF_TO_ABK.asc) in AMOS Professional with **Project → Merge ASCII**. Use the **promoted R68 `AMOSPro_AGA_LAST_GOOD.Lib`**, installed under the standard name `AMOSPro_AGA.Lib` in the `APSystem` extension slot. The active R70 candidate has an unresolved WinUAE interpreted-mode issue and is **not recommended** for this showcase.

## What it does

1. Select an indexed **IFF/ILBM** using `Fsel$("**")`; read dimensions, colour count and display mode.
2. Open a matching AGA screen with double buffering; load the IFF image and its palette.
3. Before swapping, convert the entire **back buffer** into an opaque **AGAPIC v1 DATA bank 11** using `Aga Image Capture`.
4. Save the native AMOS bank to **`RAM:IFF_TO_ABK.abk`**; briefly show the original IFF image; **Erase bank 11**.
5. Clear the screen and display **CHARGEMENT ABK**.
6. Reload the saved ABK from disk with AMOS `Load`; clear the back buffer; reconstruct the picture pixels **only from the reloaded ABK** using `Aga Bank Image Draw(11,0,0,0)`.
7. Restore **only the IFF palette** via `Aga Palette Load`, swap the final picture to the screen, then wait for `Aga Wait Key`. Close the AGA screen and clean up the demo's bank 11.

**Important:** AGAPIC stores compressed indexed pixels but **does not contain the RGB colour palette**. The source IFF must remain accessible to restore colours. `Aga Palette Load` only reads the CMAP and never repaints the IFF's image pixels.

**Bank safety:** bank **11 must be empty**. This program refuses to start if it is occupied and only erases bank 11 after creating it itself. Do not work in a session where bank 11 is in use. AMOS `Save` and `Load` file errors may stop the interpreter.

**File storage:** `RAM:` is temporary and is lost at reboot. Change `_ABK$="RAM:IFF_TO_ABK.abk"` to a writable disk location such as `Work:IFF_TO_ABK.abk` for permanent storage. Repeated runs overwrite the output file.

Try [`examples/demo.iff`](../demo.iff) (PAL 320×256, 256 colours) first. Other indexed IFFs can be tried if `Aga Screen Open` and `Aga Iff Load` accept their mode and there is enough Chip/Fast memory.

**Validation status:** new public showcase based on existing API calls. Static source review only: **not yet executed under AMOS/WinUAE**. No Compiler Gate or real-Amiga validation is implied.
