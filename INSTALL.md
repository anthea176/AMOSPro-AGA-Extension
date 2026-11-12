# Installing AMOSPro AGA Extension

**Promoted R54 v0.12.9 `LAST_GOOD`:** [AMOSPro_AGA.Lib](dist/AMOSPro_AGA.Lib) = [`AMOSPro_AGA_LAST_GOOD.Lib`](dist/AMOSPro_AGA_LAST_GOOD.Lib), 32,364 bytes, 53 commands. **Gate A CPU/CI PASS; Gates B/C interpreted/new compiled WinUAE PASS on tested scenario; Gate D physical hardware not tested.** Adds bank-number image and font convenience calls while preserving legacy signatures. [R54 report](docs/M16_R54_BANK_NUMBER.md) · [original test](tests/passed/M16_R54_BANK_NUMBER_01.asc).


**English** | [Français](INSTALL.fr.md) · [Examples](examples/README.md)

This is an **unofficial** extension for AMOS Professional on AGA Amiga systems (A1200/A4000 or an appropriately configured WinUAE). You need AMOS Professional already installed.

## 1. Install the extension

1. **Make backups** of your current AMOS Professional configuration and any existing extension library. In particular, keep a copy of the interpreter configuration (typically `S:AMOSPro_Interpreter_Config`).
2. Copy the [R54 validated library](dist/AMOSPro_AGA.Lib) into **APSystem** as `AMOSPro_AGA.Lib` in the same slot, then **restart AMOS and Compiler**. Keep the previous library/configuration. To reproduce the release, run the [archived validated test](tests/passed/M16_R54_BANK_NUMBER_01.asc) interpreted first; after success, compile a **new executable** and test it separately.
3. Start **AMOS Professional**. Choose **Config → Set Interpreter**, load your existing interpreter configuration, then select **Set Loaded Extensions**.
4. Register `AMOSPro_AGA.Lib` in **extension slot 14 if it is free** (the project's historical AMOS tests use slot 14). If slot 14 is occupied, do not overwrite someone else's extension; choose a free slot and remember that tokenized AMOS programs depend on their original slot. Enter the exact library filename or its full AmigaDOS path if your setup requires one.
5. **Save the interpreter configuration** (not only the editor preferences), exit AMOS Professional, and restart it. Under **AMOS → About Loaded Extensions**, confirm that the AGA extension is loaded.

**Existing users:** when replacing an older `AMOSPro_AGA.Lib`, keep the same extension slot and restart AMOS. Back up the old file and configuration first.

## 2. Run a first example

1. Copy selected `.asc` examples and `demo.iff` from [`examples/`](examples/) into a directory accessible to your Amiga or WinUAE (an Amiga hard disk, mapped host directory or mounted disk image). The script files are **plain ASCII text**, not tokenized `.AMOS` programs.
2. In the AMOS editor, start with an **empty program** (**New**) and select **Project → Merge ASCII** (shortcut **Amiga + Shift + M**). Import `examples/screen.asc`.
3. Run the program **in the interpreter**. The AGA test pattern should appear briefly and then close, returning to the AMOS editor.
4. Next import `examples/picture.asc` using a fresh empty editor. When the file selector opens (`Fsel$("**")`), pick `examples/demo.iff`. Press any key once the image is displayed to return to AMOS.
5. Try `blitter.asc`, `copper.asc` and `mouse.asc` in that order. Consult [`examples/README.md`](examples/README.md) for what each does.

**Important:** `Merge ASCII` **adds** source to the current editor buffer. Start a new/empty program each time; do not repeatedly merge the examples into one program. Once imported, you may save an example in AMOS's native `.AMOS` format.

## 3. Troubleshooting

| Problem | First checks |
|---|---|
| `Aga ...` commands unrecognized | The correct `.Lib` must be in `APSystem`, registered in the interpreter's loaded extensions, and AMOS restarted. Check the slot and the exact filename. |
| Cannot find `demo.iff` | The file selector needs the **Amiga-visible** path. Move `demo.iff` into a mounted drive/drawer and browse to it. |
| Screen does not open | Confirm that the emulator/Amiga has **AGA**, that PAL 320×256 is available, and that the screen can use 256 colours. |
| `.asc` is not recognized by Load | Use **Project → Merge ASCII**, not the normal native-AMOS Load command. |
| Something goes wrong during a demo | Check the output. The [all-in-one compiled R46 C1 test](examples/compiler_r46_all_in_one/) has passed WinUAE; other examples have different test coverage. |

## Release and licence

**R54 v0.12.9 — currently promoted and Compiler-safe (12 Nov 2026):** [installable](dist/AMOSPro_AGA.Lib) = [LAST_GOOD](dist/AMOSPro_AGA_LAST_GOOD.Lib) = [frozen R54 archive](dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib), SHA256 `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`, **32,364 bytes / 53 commands / 60 AP20 entries**. Gates A/B/C PASS on the user-tested scenario; real AGA hardware Gate D untested. The former validated [R46 C1 Compiler-safe archive](dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib) remains frozen for reproducibility and regression.

**Code and source examples:** [MIT](LICENSE). **`demo.iff` and all other visual assets:** [separate artwork terms](ASSETS_LICENSE.md), **not MIT**. Fan art from outside the example pack is not necessary to run these demos.

Official AMOS reference: [Setting loaded extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
