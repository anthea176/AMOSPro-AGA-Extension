# Installing AMOSPro AGA Extension

**R82 v0.13.27 promoted `LAST_GOOD` (68020+) — native Gate A, WinUAE Runtime B and AMOS Compiler C PASS** on the documented 68030 AGAPIC test. Pure interpreted mode and physical Amiga D **NOT TESTED**. [Current R82 library](dist/AMOSPro_AGA.Lib) = [`LAST_GOOD`](dist/AMOSPro_AGA_LAST_GOOD.Lib), **64,112 bytes**, SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`, **74 commands / 81 AP20 entries**. [Historical R81](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/aed079ec05102c992d8440f86522e8b8875df8e7/dist/AMOSPro_AGA_LAST_GOOD.Lib) remains reproducible. `LIBS:c2p.library` remains required for C2P. [Promotion report](docs/AGAPIC_R82_LAST_GOOD_PROMOTION_2026-11-14.md).


**English** | [Français](INSTALL.fr.md) · [Examples](examples/README.md)

This is an **unofficial** extension for AMOS Professional on AGA Amiga systems (A1200/A4000 or an appropriately configured WinUAE). You need AMOS Professional already installed.

## 1. Install the extension

1. **Make backups** of your current AMOS Professional configuration and any existing extension library. In particular, keep a copy of the interpreter configuration (typically `S:AMOSPro_Interpreter_Config`).
2. Copy the [promoted R82 library](dist/AMOSPro_AGA_LAST_GOOD.Lib) into **APSystem** as `AMOSPro_AGA.Lib`, after backing up the previous library. The [active R82 binary](dist/AMOSPro_AGA.Lib) is byte-identical. **Keep the same extension slot** and restart AMOS Professional. To roll back to historical R81, use the library at its former Git commit.
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
| Something goes wrong during a demo | Check the output. The [all-in-one compiled R46 C1 test](examples/compiler_all_in_one/) has passed WinUAE; other examples have different test coverage. |

## Release and licence

**Status:** R68 v0.13.13 is the sole **working test candidate** (native Gate A and WinUAE interpreted B PASS); **R63 v0.13.8 remains the protected and separately promoted LAST_GOOD**. Historical [R46 C1 compiler-safe archive](dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib) remains immutable. R68 has not completed actual AMOS Compiler Gate C or physical Amiga Gate D.

**Code and source examples:** [MIT](LICENSE). **`demo.iff` and all other visual assets:** [separate artwork terms](ASSETS_LICENSE.md), **not MIT**. Fan art from outside the example pack is not necessary to run these demos.

Official AMOS reference: [Setting loaded extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
