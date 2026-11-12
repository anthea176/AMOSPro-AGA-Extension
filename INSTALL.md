# Installing AMOSPro AGA Extension

**Active candidate R54 0.12.9:** [AMOSPro_AGA.Lib](dist/AMOSPro_AGA.Lib), **32,364 bytes**, Gate A CPU/CI PASS; **R54 WinUAE B/C pending**. Adds bank-number draw/font convenience commands, without modifying the old calls. **R53 Image Capture already passed interpreted and freshly compiled WinUAE tests**. **R46 C1 remains [LAST_GOOD](dist/AMOSPro_AGA_LAST_GOOD.Lib)**. [R54 test and procedure](docs/M16_R54_BANK_NUMBER.md).


**English** | [Français](INSTALL.fr.md) · [Examples](examples/README.md)

This is an **unofficial** extension for AMOS Professional on AGA Amiga systems (A1200/A4000 or an appropriately configured WinUAE). You need AMOS Professional already installed.

## 1. Install the extension

1. **Make backups** of your current AMOS Professional configuration and any existing extension library. In particular, keep a copy of the interpreter configuration (typically `S:AMOSPro_Interpreter_Config`).
2. Copy the [R54 candidate](dist/AMOSPro_AGA.Lib) into **APSystem** as `AMOSPro_AGA.Lib` in the same slot, then **restart AMOS and Compiler**. Keep the previous library/configuration. Run the [active test](tests/current/M16_R54_BANK_NUMBER_01.asc) interpreted first; after success, compile a **new executable** and test it separately.
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

**R46 v0.12.1-C1 — official promoted library (12 Nov 2026):** [`LAST_GOOD` R46 C1](dist/AMOSPro_AGA_LAST_GOOD.Lib) = [validated C1 archive](dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib), **29,964 bytes**, SHA256 `d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b`, **50 commands / 57 entries AP20**. CPU Gate A, interpreted WinUAE Gate B and compiled WinUAE integrated Gate C PASS (`RESULT 1`, `CLOSE RETURNED`). Gate D physical Amiga not tested. Never install the older raw R46 archive for compiled programs.

**Code and source examples:** [MIT](LICENSE). **`demo.iff` and all other visual assets:** [separate artwork terms](ASSETS_LICENSE.md), **not MIT**. Fan art from outside the example pack is not necessary to run these demos.

Official AMOS reference: [Setting loaded extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
