# Installing AMOSPro AGA Extension

**Current test candidate R40 v0.11.1: 68000 CPU/CI Gate A PASS (221 cases), WinUAE Gate B pending.** New `Aga Plot(X,Y,Pen)`; **45 named AP20 commands**. [R40 candidate](dist/AMOSPro_AGA.Lib) (23,840 bytes; SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`). [WinUAE-validated R38](dist/AMOSPro_AGA_LAST_GOOD.Lib) (23,380 bytes; SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`) remains in `LAST_GOOD`. R39 deferred; Compiler Gate C and physical AGA Gate D untested.


**English** | [Français](INSTALL.fr.md) · [Examples](examples/README.md)

This is an **unofficial** extension for AMOS Professional on AGA Amiga systems (A1200/A4000 or an appropriately configured WinUAE). You need AMOS Professional already installed.

## 1. Install the extension

1. **Make backups** of your current AMOS Professional configuration and any existing extension library. In particular, keep a copy of the interpreter configuration (typically `S:AMOSPro_Interpreter_Config`).
2. Copy the [R40 v0.11.1 candidate](dist/AMOSPro_AGA.Lib) (**45 commands, CPU/CI Gate A PASS, WinUAE Gate B pending**) to **`APSystem`** as `AMOSPro_AGA.Lib`. Keep the same extension slot as R38 and **restart AMOS**. Back up the previously installed Lib; [R38 `LAST_GOOD`](dist/AMOSPro_AGA_LAST_GOOD.Lib) remains available for rollback. The [R40 test](tests/current/M15_R40_PLOT_01.asc) needs no external assets.
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

**R40 candidate — Gate A PASS, Gate B not tested:** [`dist/AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) is identical to the [R40 archive](dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib), **23,840 bytes**, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`. [Active WinUAE test](tests/current/M15_R40_PLOT_01.asc). **Latest `LAST_GOOD`: R38 v0.11.0**, [file](dist/AMOSPro_AGA_LAST_GOOD.Lib) and [archive](dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib), SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`, unchanged.

**Code and source examples:** [MIT](LICENSE). **`demo.iff` and all other visual assets:** [separate artwork terms](ASSETS_LICENSE.md), **not MIT**. Fan art from outside the example pack is not necessary to run these demos.

Official AMOS reference: [Setting loaded extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
