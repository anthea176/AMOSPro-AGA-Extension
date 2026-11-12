# Installing AMOSPro AGA Extension

**R42 v0.11.3 — AMOS/WinUAE test candidate, native CPU/CI Gate A PASS (360 cases), Gate B not tested:** [`AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) = [R42 archive](dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib), **25,896 bytes**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`, **47 named AP20 commands**. New `Aga Box(X1,Y1,X2,Y2,Pen)` draws safely clipped 1-pixel rectangle outlines with unordered corners. [Active R42 test](tests/current/M15_R42_BOX_01.asc) requires no extra IFF/ABK. **Last `LAST_GOOD`: R41 v0.11.2**, 24,816 bytes; [R41 archive](dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib) remains unchanged. Compiler Gate C and physical AGA Gate D untested.


**English** | [Français](INSTALL.fr.md) · [Examples](examples/README.md)

This is an **unofficial** extension for AMOS Professional on AGA Amiga systems (A1200/A4000 or an appropriately configured WinUAE). You need AMOS Professional already installed.

## 1. Install the extension

1. **Make backups** of your current AMOS Professional configuration and any existing extension library. In particular, keep a copy of the interpreter configuration (typically `S:AMOSPro_Interpreter_Config`).
2. Copy the [R42 v0.11.3 candidate](dist/AMOSPro_AGA.Lib) into **`APSystem`** as `AMOSPro_AGA.Lib`, **keeping the same extension slot**, then **restart AMOS**. Back up the installed library; [R41 `LAST_GOOD`](dist/AMOSPro_AGA_LAST_GOOD.Lib) remains available for rollback. From an empty program import the [R42 test](tests/current/M15_R42_BOX_01.asc) using **Project → Merge ASCII**.
3. Start **AMOS Professional**. Choose **Config → Set Interpreter**, load your existing interpreter configuration, then select **Set Loaded Extensions**.
4. Register `AMOSPro_AGA.Lib` in **extension slot 14 if it is free** (the project's historical AMOS tests use slot 14). If slot 14 is occupied, do not overwrite someone else's extension; choose a free slot and remember that tokenized AMOS programs depend on their original slot. Enter the exact library filename or its full AmigaDOS path if your setup requires one.
5. **Save the interpreter configuration** (not only the editor preferences), exit AMOS Professional, and restart it. Under **AMOS → About Loaded Extensions**, confirm that the AGA extension is loaded.

**Existing users:** when replacing an older `AMOSPro_AGA.Lib`, keep the same extension slot and restart AMOS. Back up the old file and configuration first.

## 2. Run a first example

1. Copy the seven `.asc` files and `demo.iff` from [`examples/`](examples/) into a directory accessible to your Amiga or WinUAE (an Amiga hard disk, mapped host directory or mounted disk image). The script files are **plain ASCII text**, not tokenized `.AMOS` programs.
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
| Something goes wrong during a demo | Reopen AMOS and check the output. The examples are new distribution samples; their source has static checks but **has not yet been run in WinUAE**. |

## Release and licence

**R42 v0.11.3 — AMOS/WinUAE test candidate, native CPU/CI Gate A PASS (360 cases), Gate B not tested:** [`AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) = [R42 archive](dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib), **25,896 bytes**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`, **47 named AP20 commands**. New `Aga Box(X1,Y1,X2,Y2,Pen)` draws safely clipped 1-pixel rectangle outlines with unordered corners. [Active R42 test](tests/current/M15_R42_BOX_01.asc) requires no extra IFF/ABK. **Last `LAST_GOOD`: R41 v0.11.2**, 24,816 bytes; [R41 archive](dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib) remains unchanged. Compiler Gate C and physical AGA Gate D untested.

**Code and source examples:** [MIT](LICENSE). **`demo.iff` and all other visual assets:** [separate artwork terms](ASSETS_LICENSE.md), **not MIT**. Fan art from outside the example pack is not necessary to run these demos.

Official AMOS reference: [Setting loaded extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
