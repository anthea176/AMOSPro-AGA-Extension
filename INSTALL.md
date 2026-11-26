# Installing AMOSPro AGA Extension


**Active TEST candidate S1-P2m (MC68020+):** [dist/AMOSPro_AGA.Lib](dist/AMOSPro_AGA.Lib), 149,400 bytes, SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`, 105 commands / 214 AP20 entries, [native MC68020 Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45891037257), B functional PASS, C functional 2/2 (strict 1/2), D pending. For the 0.14.1 protected base use [P2d-L2b LAST_GOOD](dist/AMOSPro_AGA_LAST_GOOD.Lib), 136,708 bytes, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, renamed AMOSPro_AGA.Lib in APSystem. 0.14.1 not released.

**English** | [Français](INSTALL.fr.md) · [Examples](examples/README.md)

This is an **unofficial** extension for AMOS Professional on AGA Amiga systems (A1200/A4000 or an appropriately configured WinUAE). You need AMOS Professional already installed.

## 1. Install the extension

1. **Make backups** of your current AMOS Professional configuration and any existing extension library. In particular, keep a copy of the interpreter configuration (typically `S:AMOSPro_Interpreter_Config`).
2. For S1-P2m testing, back up the installed Lib and copy [dist/AMOSPro_AGA.Lib](dist/AMOSPro_AGA.Lib) into APSystem in the same extension slot. Verify SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`, restart WinUAE completely without restoring a save state, start AMOS and follow the [Runtime protocol](tests/current/README.md). WinUAE 68030, JIT ON, AGA PAL.
3. Start **AMOS Professional**. Choose **Config → Set Interpreter**, load your existing interpreter configuration, then select **Set Loaded Extensions**.
4. Register `AMOSPro_AGA.Lib` in **extension slot 14 if it is free** (the project's historical AMOS tests use slot 14). If slot 14 is occupied, do not overwrite someone else's extension; choose a free slot and remember that tokenized AMOS programs depend on their original slot. Enter the exact library filename or its full AmigaDOS path if your setup requires one.
5. **Save the interpreter configuration** (not only the editor preferences), exit AMOS Professional, and restart it. Under **AMOS → About Loaded Extensions**, confirm that the AGA extension is loaded.

**Existing users:** when replacing an older `AMOSPro_AGA.Lib`, keep the same extension slot and restart AMOS. Back up the old file and configuration first.

## 2. Requirements and C2P dependency

**Requirements for the active S1-P1i test candidate (same minimum CPU as P2d):** an **AGA** Amiga (e.g. A1200/A4000, or WinUAE configured for AGA), **Motorola 68020/68EC020 or later** (not a 68000-only machine), AMOS Professional installed, and sufficient **Chip RAM** for the private AGA screen and buffers.

**Additional library for C2P:** [**c2p.library v1.9 by Alimede Informatica, on Aminet**](https://aminet.net/package/dev/misc/c2plib) ([upstream source](https://github.com/alimede/c2p.library)). This is a standard AmigaOS shared library, **not** an AMOS extension and **not** part of `AMOSPro_AGA.Lib`.

1. Download **`c2plib.lha`** from Aminet and extract it with an LhA-compatible archiver.
2. Locate the runtime **`c2p.library`** file (normally in the package's **`libs/`** directory). Copy **that file** to **`LIBS:c2p.library`** on the Amiga (usually **`SYS:Libs/c2p.library`**). With WinUAE, the destination must be **AmigaOS-visible**, not just a Windows folder.
3. Keep **`AMOSPro_AGA.Lib` in `APSystem`** and **`c2p.library` in `LIBS:`**. **Do not register** `c2p.library` under *Set Loaded Extensions*. If it was missing during a previous attempt, relaunch AMOS and try again.

**Scope:** the five `Aga C2P` commands (`Open`, `Convert`, `Close`, `Blit`, `Zoom`) need a C2P context using that shared library. Other extension commands, **including `Aga Iff To Chunky` on its own**, do not need it. If `c2p.library` is absent, `Aga C2P Open` returns **0**; the AMOS AGA extension itself can still load.

**C2P prerequisites:** open a private AGA screen **320×256** with **16/32/64/128/256 indexed colours (4–8 bitplanes)**; enable **`Aga Double Buffer`**; provide a valid existing AMOS **DATA/WORK chunky bank** (bank number **5..65535**, at least **81,920 bytes**). Optionally fill the bank from a compatible ILBM with `Aga Iff To Chunky(File$,Bank)`. Render with **Open → optional Blit/Zoom → Convert → explicit `Aga Swap` → Close**. Palette loading is separate; no implicit palette update or Swap.

## 3. Run a first example

1. Copy selected `.asc` examples and `demo.iff` from [`examples/`](examples/) into a directory accessible to your Amiga or WinUAE (an Amiga hard disk, mapped host directory or mounted disk image). The script files are **plain ASCII text**, not tokenized `.AMOS` programs.
2. In the AMOS editor, start with an **empty program** (**New**) and select **Project → Merge ASCII** (shortcut **Amiga + Shift + M**). Import `examples/screen.asc`.
3. Run the program **in the interpreter**. The AGA test pattern should appear briefly and then close, returning to the AMOS editor.
4. Next import `examples/picture.asc` using a fresh empty editor. When the file selector opens (`Fsel$("**")`), pick `examples/demo.iff`. Press any key once the image is displayed to return to AMOS.
5. Try `blitter.asc`, `copper.asc` and `mouse.asc` in that order. Consult [`examples/README.md`](examples/README.md) for what each does.

**Important:** `Merge ASCII` **adds** source to the current editor buffer. Start a new/empty program each time; do not repeatedly merge the examples into one program. Once imported, you may save an example in AMOS's native `.AMOS` format.

## 4. Troubleshooting

| Problem | First checks |
|---|---|
| `Aga ...` commands unrecognized | The correct `.Lib` must be in `APSystem`, registered in the interpreter's loaded extensions, and AMOS restarted. Check the slot and the exact filename. |
| Cannot find `demo.iff` | The file selector needs the **Amiga-visible** path. Move `demo.iff` into a mounted drive/drawer and browse to it. |
| Screen does not open | Confirm that the emulator/Amiga has **AGA**, that PAL 320×256 is available, and that the screen can use 256 colours. |
| `.asc` is not recognized by Load | Use **Project → Merge ASCII**, not the normal native-AMOS Load command. |
| `Aga C2P Open(Bank)` returns 0 | Check `LIBS:c2p.library`, CPU 68020+, a private 320×256 AGA screen in 4–8 planes, successful `Aga Double Buffer`, and an existing chunky DATA/WORK bank of at least 81,920 bytes. Opening twice also returns 0. |
| `Aga C2P Convert` fails or shows no picture | Check that Open succeeded and the bank still exists; the back buffer must be `Safe`. After Convert, explicitly call `Aga Swap` and load the palette if needed. |
| `Aga Iff To Chunky` rejects a picture | The supported source is indexed 320×256 ILBM, 4–8 planes, RAW or ByteRun1, without HAM/EHB, masking or dual playfield. |
| Something goes wrong during a demo | Check the output. The [all-in-one compiled R46 C1 test](examples/compiler_all_in_one/) has passed WinUAE; other examples have different test coverage. |

## Release and licence

**Current status:** S1-P1i native MC68020 Gate A PASS, B/C/D pending; P2d-L2b protected, previous evidence unchanged. [Qualification](docs/releases/0.14.1_QUALIFICATION.md).

**Code and source examples:** [MIT](LICENSE). **`demo.iff` and all other visual assets:** [separate artwork terms](ASSETS_LICENSE.md), **not MIT**. Fan art from outside the example pack is not necessary to run these demos.

Official AMOS reference: [Setting loaded extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
