# R54 v0.12.9 — bank-number helpers (AMOS / WinUAE)

This is the **exact R54 regression source confirmed by the user** in interpreted AMOS and in a newly compiled executable under WinUAE. [Original archived test](../../tests/passed/M16_R54_BANK_NUMBER_01.asc). It compares the new `Aga Bank Image Draw(10,X,Y,Mode)` and `Aga Bank Font Select(25)` with the existing pointer/length commands. The legacy signatures remain available.

Copy this whole folder into the same AmigaDOS-accessible drawer. It contains `M16_R54_BANK_NUMBER_01.asc`, `M16_AGAPIC_SAMPLE_BANK10.abk`, `Hwarf1252S.abk`, and the separate Hwarf font license. Install the [current validated R54](../../dist/AMOSPro_AGA.Lib) as `APSystem/AMOSPro_AGA.Lib`, keep its configured extension slot and restart AMOS. Use **Project → Merge ASCII** into a blank program, run interpreted, then compile a **fresh executable** if desired.

**Warning:** the test issues `Load ... ,10` and `Load ... ,25`, overwriting any existing banks 10 and 25. Use a disposable WinUAE environment or back up those banks.

Expected: `DRAW NEW O/M OLD 1 1 1`, `FONT NEW/OLD/TEXT 1 1 1 1 1`, `INVALID IMG/FONT 0 0 NOS 0`, `RESULT 1`, `CLOSE RETURNED`, and a correct rendering of three images and text. Gates A/B/C have passed on this scenario; **real AGA hardware Gate D is untested**. The script is versioned as a regression/advanced example, not a general-purpose intro.

Source code: [MIT](../../LICENSE). Font artwork: [Hwarf separate license](Hwarf-12xxS.licence). Other visual assets: [separate license](../../ASSETS_LICENSE.md).
