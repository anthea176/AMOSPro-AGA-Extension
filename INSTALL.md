# Installing AMOSPro AGA Extension

**Active test candidate M19 P0c:** [`dist/AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib), **87,020 bytes**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`, 82 commands / 92 AP20 entries. Native MC68020 Gate A PASS; WinUAE Runtime B and Compiler C **PASS according to author-supplied logs**, with [documented evidence limitations](docs/M19_P0C_GATES_BC_2026-11-16.md). R84 `LAST_GOOD` remains independently protected in [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](dist/AMOSPro_AGA_LAST_GOOD.Lib), 67,904 bytes, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`. **Do not mistake the active candidate for promoted LAST_GOOD.** [Active WinUAE test](tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc).

**English** | [Français](INSTALL.fr.md) · [Examples](examples/README.md)

This is an **unofficial** extension for AMOS Professional on AGA Amiga systems (A1200/A4000 or an appropriately configured WinUAE). You need AMOS Professional already installed.

## 1. Install the extension

1. **Make backups** of your current AMOS Professional configuration and any existing extension library. In particular, keep a copy of the interpreter configuration (typically `S:AMOSPro_Interpreter_Config`).
2. For **M19 P0c testing**, copy **the active candidate** [`dist/AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) to **APSystem** as `AMOSPro_AGA.Lib`, after backing up your previously installed library outside the repository. The `LAST_GOOD` R84 file is deliberately **different** and must not be renamed/replaced. Keep the same slot, check the installed SHA256 and restart AMOS.
3. Start **AMOS Professional**. Choose **Config → Set Interpreter**, load your existing interpreter configuration, then select **Set Loaded Extensions**.
4. Register `AMOSPro_AGA.Lib` in **extension slot 14 if it is free** (the project's historical AMOS tests use slot 14). If slot 14 is occupied, do not overwrite someone else's extension; choose a free slot and remember that tokenized AMOS programs depend on their original slot. Enter the exact library filename or its full AmigaDOS path if your setup requires one.
5. **Save the interpreter configuration** (not only the editor preferences), exit AMOS Professional, and restart it. Under **AMOS → About Loaded Extensions**, confirm that the AGA extension is loaded.

**Existing users:** when replacing an older `AMOSPro_AGA.Lib`, keep the same extension slot and restart AMOS. Back up the old file and configuration first.

## 2. Requirements and C2P dependency

**Requirements for the active P0c test candidate:** an **AGA** Amiga (e.g. A1200/A4000, or WinUAE configured for AGA), **Motorola 68020/68EC020 or later** (not a 68000-only machine), AMOS Professional installed, and sufficient **Chip RAM** for the private AGA screen and buffers.

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

**Release status:** **M19 P0c is an unpromoted test candidate (B/C pending); R84 v0.13.29 remains `LAST_GOOD`.** Historical note: **R82 v0.13.27 was previously promoted** (74 commands / 81 AP20 entries). **Gates A native/CI, B WinUAE Runtime and C AMOS Compiler PASS** on the documented 68030/AGAPIC v1/v2 indexed 320×256×8 test. Pure interpreted `PRG_STATE 0` and physical Amiga Gate D have **not** been tested. [R82 promotion evidence](docs/AGAPIC_R82_LAST_GOOD_PROMOTION_2026-11-14.md). Previous R81 remains accessible [in Git history](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/aed079ec05102c992d8440f86522e8b8875df8e7/dist/AMOSPro_AGA_LAST_GOOD.Lib). Promotion does not imply an Aminet upload.

**Code and source examples:** [MIT](LICENSE). **`demo.iff` and all other visual assets:** [separate artwork terms](ASSETS_LICENSE.md), **not MIT**. Fan art from outside the example pack is not necessary to run these demos.

Official AMOS reference: [Setting loaded extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
