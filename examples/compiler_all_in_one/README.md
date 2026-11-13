# AMOS Compiler — all-in-one AGA example

[Français](README.fr.md) · [All examples](../README.md) · [Installation](../../INSTALL.md)

This is a **publicly renamed** version of the historically validated **R46 C1** integrated Compiler demonstration. It combines AGAPIC image drawing (opaque, masked and shifted), source clipping, Plot/Draw/Box/Circle, AMCAF BankFonts, Topaz, double buffering, pointer visibility and cleanup.

## Files and setup

- [`COMPILER_ALL_IN_ONE.asc`](COMPILER_ALL_IN_ONE.asc) — plain ASCII source. **Only its AGAPIC resource filename was adapted** during the public naming cleanup.
- [`AGAPIC_SAMPLE_BANK10.abk`](AGAPIC_SAMPLE_BANK10.abk) — picture bank **10**.
- [`Hwarf1252S.abk`](Hwarf1252S.abk) and [licence](Hwarf-12xxS.licence) — BankFont bank **25**.

1. Copy this **entire folder** to an AmigaDOS-accessible location. The compiled executable must run with this folder as its **current AmigaDOS directory**, since `Load` uses relative paths.
2. Install the [promoted R68 library](../../dist/AMOSPro_AGA.Lib) in the configured `APSystem` extension slot, restart AMOS and the Compiler, then use **Project → Merge ASCII** in a blank program.
3. Compile a **new executable**, then run it from this folder with the two ABK files. For the older, **exactly validated R46 C1 environment**, use the original frozen ZIP below and the [historical Compiler-safe library](../../dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib) in a separate test installation.

The example overwrites existing AMOS banks **10 and 25**. Do not run it in a session that owns those banks. The historical output included `RESULT 1`, `CLOSE RETURNED`, `CUR 500 ERR 0`, `IMAGE O/M/S 1 1 1` and `CLIP L/R/T/B 1 1 1 1`. Those are **expected indicators**, not new measured results for this adapted public ASC.

## Exact historical evidence versus clean public names

The [**original, byte-exact R46 C1 source**](../../tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc) and [validation report](../../docs/GATE_C_R46_MONOLITH_CANDIDATE.md) document the successful integrated Compiler test on **12 November 2026**.

The outer filename of [`COMPILER_ALL_IN_ONE.zip`](../COMPILER_ALL_IN_ONE.zip) has been simplified, but the **ZIP bytes, folder structure and old version-labelled names inside remain unchanged** to preserve the verified archive. Extract it as supplied to repeat the exact historical test. The public `COMPILER_ALL_IN_ONE.asc` above instead loads `AGAPIC_SAMPLE_BANK10.abk` and **has not been separately recompiled/validated after renaming**.

The example checks return values and cleanup, but does not prove every possible command path or physical AGA hardware compatibility. Source is [MIT](../../LICENSE); the Hwarf font has its [own licence](Hwarf-12xxS.licence), and artwork has [separate terms](../../ASSETS_LICENSE.md).
