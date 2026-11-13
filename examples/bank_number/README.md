# Bank-number helpers — AMOSPro AGA

[Français](README.fr.md) · [All examples](../README.md) · [Installation](../../INSTALL.md)

This example compares `Aga Bank Image Draw(Bank,X,Y,Mode)` and `Aga Bank Font Select(Bank)` with the original image/font functions that take an address and length. These commands first appeared in **R54** and are available in the [currently promoted R68 `LAST_GOOD`](../../dist/AMOSPro_AGA.Lib).

## Folder contents

- [`BANK_NUMBER_HELPERS.asc`](BANK_NUMBER_HELPERS.asc) — AMOS ASCII demonstration.
- [`AGAPIC_SAMPLE_BANK10.abk`](AGAPIC_SAMPLE_BANK10.abk) — AGAPIC picture loaded into bank **10**.
- [`Hwarf1252S.abk`](Hwarf1252S.abk) and [font licence](Hwarf-12xxS.licence) — bitmap font loaded into bank **25**.

Copy this entire folder to an AmigaDOS-accessible drawer and **run with that drawer as the current directory**. In a new, empty AMOS program, use **Project → Merge ASCII** to import `BANK_NUMBER_HELPERS.asc`. Run interpreted. If compiling, create a **fresh executable** using the installed library.

**Warning:** the source uses `Load ...,10` and `Load ...,25`. Existing banks 10 and 25 are overwritten. Work with a disposable session or back up the banks.

## Expected result and validation

The script checks `DRAW NEW O/M OLD 1 1 1`, `FONT NEW/OLD/TEXT 1 1 1 1 1`, `INVALID IMG/FONT 0 0 NOS 0`, `RESULT 1`, `CLOSE RETURNED`, and the correct images and text.

**Historical evidence:** the [original R54 ASC](../../tests/passed/M16_R54_BANK_NUMBER_01.asc) passed interpreted AMOS and a freshly compiled WinUAE executable. The public program here has **only one text change** to load the cleaner resource filename `AGAPIC_SAMPLE_BANK10.abk`; it is not byte-identical to that archived test and has **not been independently rerun** after the rename. Physical Amiga Gate D remains untested.

Code is [MIT](../../LICENSE). The Hwarf bitmap font carries its [separate licence](Hwarf-12xxS.licence); other artwork has [separate terms](../../ASSETS_LICENSE.md).
