# AMOSPro AGA Extension

**English** | [Français](README.fr.md)

**AMOSPro AGA Extension** extends **AMOS Professional** on AGA-equipped Commodore Amiga computers, adding screen and palette support, IFF/ILBM loading, double buffering, Blitter and Copper operations, and keyboard and mouse input.

Designed and developed by **HWARF**, with assistance from **ChatGPT (OpenAI)** for programming, testing and documentation.

<img src="assets/Hwarf%20Logo.png" alt="HWARF logo" width="160">

![AMOSPro AGA Extension presentation illustration](assets/banniere.png)

*Presentation illustration generated with ChatGPT. This is not an actual extension screenshot.*

**Separate licenses:** source code and technical documentation are under [MIT](LICENSE). **Artwork, logos, drawings and scans are not covered by MIT**, and are not freely reusable. See the [visual assets license](ASSETS_LICENSE.md).

**Get started:** [Installation guide](INSTALL.md) · [Six simple AMOS examples](examples/README.md).

**Historical R27 correction:** An initial 0.9.3 candidate was withdrawn **before WinUAE** because Blitter growth invalidated R23 keyboard/mouse cross-entry BSR offsets and their private-state anchor. The candidate below is the **relinked replacement**; both native 68000 CPU and strict source export now pass. [Incident and fix](docs/M12_SAFE_BLITTER_R27.md).

## Libraries and tests

- **Current library (validated):** [`dist/AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) = **R29 0.10.1 M13**, 17,472 bytes, SHA-256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`. Native 68000 Gate A **49 scenarios PASS**, full CI **30/30 PASS** ([run](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43016176793)), **Gate B AMOS interpreted/WinUAE PASS** on the archived save → overwrite → load test. Personal Paint successfully imported the resulting 256-color IFF palette (without BODY). Gate C Compiler / Gate D physical AGA are untested. No palette bank, native fades or cycling added.
- **Latest WinUAE-PASS version:** [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](dist/AMOSPro_AGA_LAST_GOOD.Lib) = **R29 0.10.1**, 17,472 bytes, SHA-256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, byte-identical to [R29 archive](dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib) and `dist/AMOSPro_AGA.Lib`. R28 remains archived as the previous validated version. Promotion occurred only after the user confirmed the Gate B test.
- **Historical archives:** [R10](dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib), [R27](dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib), and [R28](dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib) remain unchanged; latest `LAST_GOOD` is R29 after WinUAE/PPaint validation.
- **Validated R29 WinUAE test:** [`M13_R29_PALETTE_SAVE_01.asc`](tests/passed/M13_R29_PALETTE_SAVE_01.asc), byte-identical to original test (Git blob `b80baabe5533288cac3285a78c232827cce94085`): `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1` and `CLOSE RETURNED`. Personal Paint successfully imported the saved 256-color CMAP. No active `.asc` test.
- **Validated R28 palette test:** [`M13_R28_PALETTE_01.asc`](tests/passed/M13_R28_PALETTE_01.asc), `RESULT 1`, `FADEERR 0`, palette IFF load, RGB Set/Get and normal return to AMOS. The selected IFF file is not identifiable in the screenshot; standalone PPaint export and full visual fade remain to verify. **Gate C/D untested.**
- **Validated M6 Blitter tests:** [R13 Copy](tests/passed/M6_R13_BLIT_COPY_01.asc), [R14 Fill](tests/passed/M6_R14_BLIT_FILL_01.asc) and [R15 Clear](tests/passed/M6_R15_BLIT_CLEAR_01.asc). **Validated M7 Copper tests:** [R16 Clear](tests/passed/M7_R16_COPPER_CLEAR_01.asc), [R17 On/Off](tests/passed/M7_R17_COPPER_ON_OFF_01.asc) and [R18 raster](tests/passed/M7_R18_COPPER_RASTER_01.asc).
- **R27 WinUAE test validated and archived byte-exact:** [`M12_R27_SAFE_BLIT_01.asc`](tests/passed/M12_R27_SAFE_BLIT_01.asc), original Git blob `3b3a6d8c120b1ec066669231d382eae6e0e4bd82`. **40 completed swaps**, Clear/Fill/Copy first-draw successes **14/13/13**, temporary rejections **13/13/13**, `SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, normal AMOS return **line 167**. User saw rectangles blinking. **R28 and R29 tests are archived in `tests/passed/`; no active WinUAE test remains in `tests/current/`.** See [M12 report](docs/M12_SAFE_BLITTER_R27.md); no 50 FPS measurement, exhaustive stress, Compiler or physical AGA validation.
- **Earlier binaries:** `dist/experimental/`; historical stable versions: `archive/`.

Install the library version that matches the test you intend to run. Files on GitHub do not automatically replace libraries installed in AMOS/WinUAE.

## Main AMOS commands

**Current library API R29 0.10.1** — **all 35 named AP20 commands**, R28's 34 plus `Aga Palette Save`. The R29 Save function passed **Gate B AMOS/WinUAE**; previous R28 palette scenarios remain validated. AMOS Compiler and physical AGA remain untested.

| Command | Exact syntax | Parameters and behaviour |
|---|---|---|
| `Aga Probe` | `Aga Probe` | Legacy no-argument diagnostic instruction. Not recommended as a gameplay API. |
| `Aga Detect` | `_AGA=Aga Detect` | No arguments. Returns a nonzero value when AGA is available; do not assume TRUE is always exactly 1. |
| `Aga Demo` | `_D=Aga Demo` | Legacy no-argument diagnostic function; no stable gameplay return-value contract. |
| `Aga Screen Open` | `_OK=Aga Screen Open(largeur,hauteur,nbCouleurs,modeID)` | Pixel dimensions; `nbCouleurs` is a **colour count**, not a bitplane count (indexed modes: 2, 4, 8, 16, 32, 64, 128 or 256). Pass an AmigaOS ModeID, e.g. `$00021000` for PAL LowRes. Returns 1 on success, 0 on failure. |
| `Aga Screen Close` | `Aga Screen Close` | No arguments. Closes the AGA screen and releases the associated resources. |
| `Aga Screen Pattern` | `Aga Screen Pattern` | No arguments. Draws the built-in diagnostic pattern. |
| `Aga Double Buffer` | `_DB=Aga Double Buffer` | No arguments. Enables double buffering. Returns 1 on success or 0 on failure. |
| `Aga Swap` | `_SW=Aga Swap` | No arguments. Presents the prepared back buffer. Returns 1 on success or 0 on failure. |
| `Aga Back Fill` | `Aga Back Fill couleur` | **One argument:** palette colour index used to fill the **entire** back buffer; e.g. 255 on an 8-bitplane indexed screen. |
| `Aga Pic Info` | `_V=Aga Pic Info(fichier$,champ)` | ILBM file path and field index 0..7 (see reference table below). Returns the selected value, or -1 on error. |
| `Aga Iff Load` | `_OK=Aga Iff Load(fichier$)` | IFF/ILBM file path. Loads pixels and palette onto a compatible AGA screen/buffer. Returns 1 or 0. |
| `Aga Palette Load` (M13 R28) | `_OK=Aga Palette Load(_FILE$)` | Read **standard IFF FORM ILBM** palette `CMAP` only, including palette-only PPaint/DPaint files without `BODY`/`BMHD`. Never copy pixels. Return 1 success or 0 invalid IFF/screen. **R28 Gate A CPU PASS and Gate B WinUAE PASS on M13 scenario.** |
| `Aga Palette Set` (M13 R28) | `_OK=Aga Palette Set(_PEN,_R,_G,_B)` | Set one indexed palette entry of the private AGA Intuition screen using 8-bit R/G/B components (`0..255`), through `LoadRGB32`. Returns 1 or 0. No VBL wait. HAM/EHB/dual playfield not supported in R28. |
| `Aga Palette Get` (M13 R28) | `_RGB=Aga Palette Get(_PEN)` | Read active `ColorMap` via `GetRGB32`. Packed RGB24 `$00RRGGBB`, or -1 when invalid; black = 0. No change to bitmap. |
| `Aga Palette Save` (M13 R29) | `_OK=Aga Palette Save(_FILE$)` | Save the current indexed AGA screen `ColorMap` to an IFF `FORM ILBM` containing `BMHD`+`CMAP`, no `BODY`. Filename: AMOS string (1–255 bytes), ordinary AmigaDOS path. **Overwrites an existing file** (`MODE_NEWFILE`). Returns integer **1** on complete write/close, **0** for invalid screen/file/allocation/write. Reads 1–256 colors, RGB24, no bitmap changes; no HAM/EHB/dual playfield. A write error after overwrite may destroy the old file. **Gate A CPU and Gate B WinUAE PASS on the archived scenario; PPaint palette import confirmed.** |
| `Aga Key` | `_K=Aga Key` | No arguments; nonblocking keyboard read. **R23:** preserves RAWKEY key-down events in a 16-item FIFO shared with the IDCMP mouse dispatcher. |
| `Aga Wait Key` | `_K=Aga Wait Key` | No arguments. Waits for an Intuition-window key and returns a **raw key code**, which need not be ASCII. **R23:** uses the shared dispatcher/FIFO; Ctrl+C break handling returned cleanly to AMOS with the Intuition screen closed under WinUAE. |
| `Aga Wait Vbl` | `Aga Wait Vbl` | No arguments. Waits for one vertical blank using `WaitTOF`. Does nothing if no AGA screen is open. |
| `Aga Blit Copy` (R13+, Safe in R27) | `_OK=Aga Blit Copy(sourceX,sourceY,destX,destY,largeur,hauteur)` | Copies a rectangle within the **same back buffer**. **R27:** automatically checks `Safe` before DMA; returns **0 without copying** when the previous front buffer is not yet writable (or arguments/state are invalid), **1** after success. Single nonblocking `GetMsg`, no `ReplyMsg`. **R27 Gate A CPU and Gate B WinUAE PASS for M12's archived 40 swaps.** |
| `Aga Blit Fill` (R14+, Safe in R27) | `_OK=Aga Blit Fill(x,y,largeur,hauteur,indexCouleur)` | Fills the back-buffer rectangle with the fifth-argument palette index. **R27:** same nonblocking `Safe` check before the first bitmap DMA; returns **0 without drawing** if not ready or invalid. **R27 Gate A CPU and Gate B WinUAE PASS for M12's archived scenario.** |
| `Aga Blit Clear` (R15+, Safe in R27) | `_OK=Aga Blit Clear(x,y,largeur,hauteur)` | Sets a back-buffer rectangle to palette index **0** (not necessarily RGB black). **R27:** inherits Fill's nonblocking `Safe` guard through its native wrapper; returns **0 without clearing** when unsafe/invalid. **R27 Gate A CPU and Gate B WinUAE PASS for M12's archived scenario.** |
| **`Aga Copper Clear`** (R16+) | `_OK=Aga Copper Clear` | No arguments. Creates an empty, terminated Copper list owned by the private AGA screen. Returns 1 or 0. |
| **`Aga Copper Wait`** (R18+) | `_OK=Aga Copper Wait(v,h)` | First argument `v`: vertical position (0..255). Second argument `h`: horizontal position (0..222). Consecutive WAIT positions must strictly increase. Returns 1 or 0. |
| **`Aga Copper Move`** (R18+) | `_OK=Aga Copper Move(registre,rgb4)` | First argument: even colour-register offset `$180..$1BE` (`COLOR00..COLOR31`). Second argument: **12-bit RGB4** value `$000..$FFF`, e.g. `$F00` = red. This is **not** a palette index. Returns 1 or 0. |
| **`Aga Copper End`** (R18+) | `_OK=Aga Copper End` | No arguments. Seals a nonempty Copper list. Calling End twice, or appending after End, fails. Returns 1 or 0. |
| **`Aga Copper On`** (R17+) | `_OK=Aga Copper On` | No arguments. Installs the list through Intuition. A nonempty list must have been finalized with End. Returns 1 or 0. |
| **`Aga Copper Off`** (R17+) | `_OK=Aga Copper Off` | No arguments. Removes the list, restores the display and frees resources owned by the extension. Repeated calls are accepted. Returns 1 or 0. |
| **`Aga Mouse X`** (R19+) | `_MX=Aga Mouse X` | No arguments. Horizontal position in logical screen pixels (0..width-1), or -1 if outside the screen / closed. Nonblocking. |
| **`Aga Mouse Y`** (R19+) | `_MY=Aga Mouse Y` | No arguments. Vertical position in logical screen pixels (0..height-1), or -1 if outside the screen / closed. Nonblocking. |
| **`Aga Mouse Buttons`** (R20+, fixed in R21) | `_B=Aga Mouse Buttons` | No arguments. **Integer bitmask 0..7:** 1=left, 2=right, 4=middle; bits can be combined (3=left+right), 0=none. Returns -1 if the screen/window or `input.device` is unavailable. Nonblocking snapshot. |
| **`Aga Mouse Pressed`** (R22+, IDCMP since R23) | `_P=Aga Mouse Pressed` | No-argument integer function; bitmask 1=left, 2=right, 4=middle, combinable. **R23:** stores `IDCMP_MOUSEBUTTONS` press events between reads; 0 if none, -1 for an invalid screen/focus. Each call consumes the pending presses, even after the button was released. |
| **`Aga Mouse Released`** (R22+, IDCMP since R23) | `_R=Aga Mouse Released` | No-argument integer function; combinable 1/2/4 bitmask. **R23:** release events remain stored independently of Pressed. Even a complete click between polls can yield both Pressed=1 and Released=1. |
| **`Aga Hotspot Hit`** (M9 R24) | `_HIT=Aga Hotspot Hit(_PX,_PY,_X,_Y,_W,_H)` | **Point-in-rectangle test (6 integer arguments)**: `PX,PY` = point to test (e.g. mouse position); `X,Y` = rectangle **top-left corner**; `W,H` = **width and height in pixels, NOT right/bottom coordinates**. Returns **1 inside**, **0 outside**, with the right and bottom edges excluded. Does **not** detect a click or draw/store a hotspot; combine with `Aga Mouse Pressed` for buttons. [Detailed example below](#rectangular-hotspots-m9-r24). |
| **`Aga Rect Overlap`** (M10 R25) | `_C=Aga Rect Overlap(_AX,_AY,_AW,_AH,_BX,_BY,_BW,_BH)` | Stateless **8-argument integer function**: two rectangles, each with origin (X,Y) and width/height (W,H) in logical pixels. Returns **1** for positive-area overlap (even 1 pixel), **0** for disjoint rectangles, touching edges/corners, or nonpositive dimensions. Negative origins allowed; signed 32-bit overflow is rejected safely. No screen, physics or input state required. **R25 WinUAE PASS on the archived scenario.** |
| **`Aga Text`** (M11 R26, unchanged in R27) | `_OK=Aga Text(_X,_BASELINE_Y,_PEN,_TEXT$)` | Four arguments: X pixels, baseline Y, indexed pen, AMOS string (1..128 characters). Draws one line into the AGA Intuition back buffer with temporary RastPort, system font and transparent `JAM1`. Return 1 if rendered, 0 on invalid state/geometry/string or not-`Safe` buffer. **R26 Gate A+B PASS for text and 40-swap archived scenarios.** R27 preserves the entire Text 68000 segment byte-for-byte; its new guards are implemented in Blit Copy/Fill/Clear only. [R26 contract](docs/M11_TEXT_R26.md) · [R27 contract](docs/M12_SAFE_BLITTER_R27.md). |

**Example: save the current AGA palette**, after opening the private AGA screen:

```amos
_OK=Aga Palette Save("RAM:MENU_PALETTE.IFF")
If _OK=0
   Print "PALETTE SAVE FAILED"
End If
```

Use [the archived R29 test](tests/passed/M13_R29_PALETTE_SAVE_01.asc) for save → overwrite → reload. The IFF contains colors but no pixels. Personal Paint 256-color palette import was confirmed by the user; Deluxe Paint remains untested; [R29 contract](docs/M13_PALETTE_R29.md).

**Copper RGB4** has been available since R18, **Mouse X/Y** since R19, **Mouse Buttons** since R20 (with RMBTRAP in R21), and **Mouse Pressed/Released** since R22. **R23 uses IDCMP events to capture button transitions and protect RAWKEY input**. The quick-click, keyboard FIFO and Ctrl+C WinUAE scenarios passed; focus-switch and stress scenarios remain untested. Sprites, a `Aga Set Colour` command, and comprehensive input-stress validation are outside the current scope.

### Safe Blitters (M12 R27 — CPU/CI and WinUAE scenario PASS)

The three existing functions `Aga Blit Clear`, `Aga Blit Fill`, and `Aga Blit Copy` now check `Safe` independently. A return value of 0 can mean `Safe` has not arrived **or** another argument/state error; retry only with a bounded VBL wait. A dedicated [archived WinUAE test](tests/passed/M12_R27_SAFE_BLIT_01.asc) exercises **40 swaps with rotating first operations** and no `Aga Text` probe. The legacy `Aga Back Fill` instruction is **not covered** by the R27 protection. [Technical contract](docs/M12_SAFE_BLITTER_R27.md).

### AGA Text (M11 R26 — WinUAE validated on its visual scenario)

With the R26 library installed and the AGA screen/double buffer already open, the function draws on the **inactive AGA BitMap**, not on a native AMOS screen. Here Y=96 denotes the **font baseline**; the palette index 28 must already have been defined (e.g. by loading `examples/demo.iff`):

```amos
_TX=Aga Text(40,96,28,"HELLO AGA")
If _TX=1
   _SW=Aga Swap
End If
```

A result of 0 can mean that the previous front buffer has not yet received its `Safe` notification. Do not spin indefinitely. This R26 safety check does **not** automatically secure pre-existing Blitter commands. [WinUAE test](tests/passed/M11_R26_AGA_TEXT_01.asc) · [technical limits](docs/M11_TEXT_R26.md).

### Rectangular hotspots (M9 R24)

`Aga Hotspot Hit(PX,PY,X,Y,W,H)` checks **one point against one rectangle**, not a collision between two rectangles. It returns an **integer** assigned to a variable, never a hotspot ID. The first two values are the **point coordinates**; the remaining four describe the rectangle.

| Argument | Meaning | Example |
|---|---|---|
| `PX`, `PY` | X/Y of the tested point (for instance, `Aga Mouse X/Y`) | `60,50` |
| `X`, `Y` | X/Y of the rectangle's **top-left corner** | `40,30` |
| `W`, `H` | **Width and height**, not the opposite corner | `80,40` |
| Result (`_HIT`) | `1` = point inside; `0` = outside/invalid | `1` |

For a rectangle `(X=40,Y=30,W=80,H=40)`, the included pixels are **X=40..119** and **Y=30..69**. X=120 or Y=70 is **outside** (the right and bottom boundaries are excluded). The top and left boundaries are included.

```amos
_INSIDE=Aga Hotspot Hit(60,50,40,30,80,40)
_OUTSIDE=Aga Hotspot Hit(120,50,40,30,80,40)
' _INSIDE=1, _OUTSIDE=0
```

**Example: trigger a menu action only when the left mouse button is pressed over this rectangle** (run while the AGA screen is open):

```amos
_SELECTED=0
_PX=Aga Mouse X
_PY=Aga Mouse Y
_HIT=Aga Hotspot Hit(_PX,_PY,40,30,80,40)
_P=Aga Mouse Pressed
If _P>=0
   _LEFT=_P And 1
   If _LEFT<>0 and _HIT=1
      _SELECTED=10
   End If
End If
```

Here, `10` is an **application-defined button ID**, not a value returned by `Aga Hotspot Hit`. To test several overlapping buttons, call the function for each rectangle and set the ID in the order you want: the **last matching assignment wins**, as in the [validated R24 test](tests/passed/M9_R24_HOTSPOT_HIT_01.asc).

**Limits:** negative mouse-point coordinates (including the `-1` sentinel from `Aga Mouse X/Y`) and nonpositive `W/H` return 0. Negative rectangle `X/Y` are allowed. The function does not read the mouse, consume input, draw a rectangle or need an open AGA screen. `Aga Mouse Pressed` is a separate event function; the coordinates read with `Aga Mouse X/Y` are their **current sampled values**, not a position saved at the exact click time. See the [technical contract](docs/M9_HOTSPOT_R24.md).

### AGA mouse details (R19–R23)

All five mouse APIs — `Aga Mouse X`, `Aga Mouse Y`, `Aga Mouse Buttons`, `Aga Mouse Pressed` and `Aga Mouse Released` — are **no-argument integer functions**. Use their results in assignments or expressions. **Do not write an integer-returning function on a line by itself** in AMOS Professional.

```amos
_X=Aga Mouse X
_Y=Aga Mouse Y
_B=Aga Mouse Buttons
_P=Aga Mouse Pressed
_R=Aga Mouse Released

If _X>=0 and _Y>=0 and _B>=0
   _LEFT=_B And 1
   _RIGHT=_B And 2
End If
```

- **X/Y coordinates:** origin at top left; X ranges from 0 to width-1, Y from 0 to height-1. The return value is -1 for a closed, invalid or out-of-bounds window. Check **both** coordinates.
- **Buttons:** 0=none, 1=left, 2=right, 4=middle; combine bits (3=left+right). A -1 result means input is unavailable: verify `_B>=0` **before** applying binary operators.
- **Right mouse button (R21):** `Aga Screen Open` enables `WFLG_RMBTRAP` so the right button does not open Intuition menus over the AGA window. This behaviour was tested under WinUAE.
- **Instantaneous state:** `Aga Mouse Buttons` reads a global `input.device/PeekQualifier()` snapshot. It does not dequeue keyboard messages or track clicks per window; extremely short clicks may be missed.
- **R23 edge capture:** `Aga Mouse Pressed` and `Aga Mouse Released` consume separate pending bitmasks populated from `IDCMP_MOUSEBUTTONS` by the shared dispatcher. A complete DOWN+UP click received before the poll can set **both** masks. Reading one does not clear the other. A 16-entry RAWKEY FIFO preserves keyboard input for `Aga Key` and `Aga Wait Key`; when full, the dispatcher temporarily stops dequeuing messages. **Repeated clicks of the same button within one interval collapse into one bit**; these functions are not click counters.

Legacy R21 approach for calculating transitions from consecutive snapshots:

```amos
_OLD=Aga Mouse Buttons
_NOW=Aga Mouse Buttons
If _OLD>=0 and _NOW>=0
   _PRESSED=_NOW And (7-_OLD)
   _RELEASED=_OLD And (7-_NOW)
End If
```

**R23 WinUAE tests:** the [exact archived R23 example](tests/passed/M8_R23_IDCMP_QUICK_01.asc) using an original 320×256×8 ILBM test card passed with `RESULT=1`, including `PRESSED=RELEASED=3`, `KEYS=64,64,-1` and `WAIT=16` (A on French AZERTY). A separate `Ctrl+C` test interrupted the program at `_WAITK=Aga Wait Key` and closed the Intuition screen cleanly (user confirmation). [R22's previous test](tests/passed/M8_R22_MOUSE_EDGES_01.asc) remains archived.

### AGA Copper details (R16–R18)

**All `Aga Copper` commands above are integer-returning functions**, so assign or use the result. `_OK=Aga Copper Off` is valid; **`Aga Copper Off` alone is an AMOS syntax error**, even in an `If` branch that is never executed. Return values: 1=success, 0=rejected/failure.

| Function | Parameter 1 | Parameter 2 | Notes |
|---|---|---|---|
| `Clear` | — | — | Initializes a Copper list owned by the AGA screen. Call it before appending operations. |
| `Wait(v,h)` | `v`: line 0..255 | `h`: position 0..222 | Positions must increase; invalid or backward positions return 0. |
| `Move(register,rgb4)` | Even register offset `$180..$1BE` | RGB4 value `$000..$FFF` | `$180`=`COLOR00`, `$182`=`COLOR01` … `$1BE`=`COLOR31`. No arbitrary DMA, BPLCON or bitplane-pointer register access. |
| `End` | — | — | Seals a nonempty list. Nothing may be appended afterward. |
| `On` | — | — | Activates a finalized list; editing while active is rejected. |
| `Off` | — | — | Detaches and frees the list; repeated Off calls are accepted. |

`Move` uses **12-bit RGB4**, not indexed palette numbers: `$F00`=red, `$0F0`=green, `$00F`=blue, `$000`=black. For example, `Aga Copper Move($180,$F00)` changes the value of **COLOR00** at the raster point defined by the most recent Wait.

The following sequence is to be run after a successful `Aga Screen Open` and `Aga Double Buffer`, optionally with a compatible image loaded. It follows the [validated R18 raster example](tests/passed/M7_R18_COPPER_RASTER_01.asc):

```amos
_C=Aga Copper Clear
_W1=Aga Copper Wait(20,0)
_M1=Aga Copper Move($180,$F00)
_W2=Aga Copper Wait(80,0)
_M2=Aga Copper Move($180,$0F0)
_W3=Aga Copper Wait(140,0)
_M3=Aga Copper Move($180,$00F)
_W4=Aga Copper Wait(200,0)
_M4=Aga Copper Move($180,$000)
_E=Aga Copper End
_ON=Aga Copper On
_SW=Aga Swap
_K=Aga Wait Key
_OFF=Aga Copper Off
```

**Required order:** Clear → Wait/Move pairs → End → On → display/wait → Off → Screen Close. A COLOR00 raster effect is most visible wherever the image uses palette index 0; those pixels may also change colour. The first RGB4 implementation is limited to **62 useful operations plus CEND**, with reserved capacity and no free-form AGA register programming.

**Validation scope:** R16, R17 and R18 passed their specific AMOS interpreted/WinUAE scenarios, including the R18 raster, rejected calls, Off and screen reopening. These tests **do not prove** AMOS Compiler compatibility, real Amiga hardware behaviour, long-running stability or complete 24-bit AGA palette support. See [R18 Copper details](docs/M7_COPPER_R18.md) and [M7 status](docs/M7_STATUS.md).

### Blitter: Aga Blit Fill, Aga Blit Copy and Aga Blit Clear

These functions require a successful `Aga Screen Open` followed by `Aga Double Buffer`. They operate on the **back buffer only**; call `Aga Swap` to make the drawing visible.

```amos
_OK=Aga Blit Fill(18,24,86,48,15)
```

| Argument | Meaning | Example value |
|---:|---|---|
| 1 | `x` — left coordinate | `18` |
| 2 | `y` — top coordinate | `24` |
| 3 | `width` | `86` pixels |
| 4 | `height` | `48` pixels |
| 5 | `colourIndex` | `15` — **palette entry index** |

This rectangle covers `x=18..103` and `y=24..71` (inclusive): the call **does not take x1,y1,x2,y2,colour**. The colour index is **not RGB**. Valid indexed ranges are 0..15 for four bitplanes and 0..255 for eight bitplanes, or more generally 0..(2^depth-1). Special HAM/EHB modes cannot be treated as ordinary indexed RGB palettes.

```amos
_OK=Aga Blit Copy(18,24,150,24,86,48)
_OK=Aga Blit Clear(32,40,36,16)
```

- **Copy:** source (18,24), destination (150,24), size 86×48. `graphics.library/BltBitMap` handles overlapping rectangles.
- **Clear:** sets the 36×16 rectangle at (32,40) to index 0, equivalent to `Aga Blit Fill(32,40,36,16,0)`.
- **No clipping:** negative coordinates, zero/negative dimensions, out-of-bounds rectangles or an invalid colour index return 0; 1 indicates success.
- Blits are synchronized using `WaitBlit`. A failure after writing a bitplane does **not** guarantee that the attempted operation was atomic.
- `Aga Back Fill colour` fills the **entire** back buffer, unlike `Aga Blit Fill(...)`.

### Typical use

Check the return values from `Aga Screen Open` and `Aga Double Buffer`; optionally load an IFF compatible with that screen using `Aga Iff Load`, perform Blitter operations, then call `Aga Swap`. For complete runnable AMOS programs with error handling and cleanup, see the validated [R13 Copy](tests/passed/M6_R13_BLIT_COPY_01.asc), [R14 Fill](tests/passed/M6_R14_BLIT_FILL_01.asc) and [R15 Clear](tests/passed/M6_R15_BLIT_CLEAR_01.asc) tests.

These M6 scenarios passed under interpreted AMOS/WinUAE. **AMOS Compiler and real AGA hardware remain untested** for M6.

### Reading ILBM image metadata

`Aga Pic Info(filename$,field)` exposes the following fields:

| Field | Return value |
|---:|---|
| 0 | Width |
| 1 | Height |
| 2 | Number of bitplanes |
| 3 | Number of CMAP palette entries |
| 4 | Compression: 0=RAW, 1=ByteRun1 |
| 5 | Original CAMG value |
| 6 | ModeID suitable for opening a screen |
| 7 | Number of screen colours to request |

The reference image inventory is in [`docs/ILBM_INVENTORY.md`](docs/ILBM_INVENTORY.md). Before calling `Aga Iff Load`, you must first open a compatible AGA screen.

### Recommended test sequence

M6 R13 Copy, R14 Fill and R15 Clear have passed WinUAE and were moved into [`tests/passed/`](tests/passed/). The R12 [`R12_JEFF_A0_RETRY.asc`](tests/passed/R12_JEFF_A0_RETRY.asc) remains archived. Its historical sequence was:

```text
Aga Pic Info → Aga Screen Open → Aga Double Buffer
→ Aga Iff Load → Aga Swap → Aga Wait Key
→ Aga Screen Close → Amos To Front
```

AMOS Professional uses `If condition` / `End If` (**without `Then`**). Close the AGA screen before leaving the program.

## Development and integrity

The [`tools/`](tools/README.md) directory contains the active builders, dependencies, CPU tests and integrity utilities. Retired tools are kept in `tools/obsolete/`.

- **Current R23 builder:** [`build_m8_idcmp_r23.py`](tools/build_m8_idcmp_r23.py), using the immutable R22 archive. The [CPU preflight](tools/test_m8_idcmp_r23_preflight.py) passed 15 scenarios; CPU/CI evidence and live WinUAE validation remain separate.
- **R30 AGAPAL design preview (NOT a released command):** [Format and native-AMOS ABK preview](docs/M13_AGAPAL_R30_PREVIEW.md) · [AMOS script](tests/design/R30_AGAPAL_ABK_PREVIEW_01.asc). Indexed 0-based palettes, 16-byte header, 8-byte entries, fixed 768-byte RGB24 slots. A Python reference model is statically tested; actual AMOS Save/Load and the future `Aga Palette Bank Init` token are **not yet WinUAE-tested or implemented**. R29 remains the only active library version.
- **R30 source prototype (NOT in the installable R29 library):** the approved future call is `_OK=Aga Palette Bank Init(Start(bank),count)`, using a native AMOS DATA bank, no hidden bank search. Its 68000 builder/CPU tests are staged for Gate A; no R30 candidate or runtime validation yet. [Design and safety limits](docs/M13_AGAPAL_R30_PREVIEW.md).
- **Earlier M8 documentation:** [R20 mouse buttons](docs/M8_MOUSE_BUTTONS_R20.md), [R19 mouse X/Y](docs/M8_MOUSE_R19.md) and [R21 RMBTRAP](docs/M8_RMBTRAP_R21.md).
- **Binary integrity:** [`verify_artifacts.py`](tools/verify_artifacts.py), HUNK/AP20 auditing, SHA-256, reproducibility and [GitHub Actions CI](.github/workflows/artifact-integrity.yml).
- **API/README parity:** [`test_readme_api_coverage.py`](tools/test_readme_api_coverage.py) checks the command table and active library version in **both English and French**. Adding or changing an AMOS instruction/function requires both README versions to be updated in the same candidate/code commit (exact AP20 token, syntax, parameters, return, limits, example and actual Gate status). Every subsequent validation or failure must update both README statuses with evidence; Gate B PASS documentation must be committed together with LAST_GOOD promotion and exact test archival. R30 `AGAPAL` bank functions are still design-only and must not appear as available R29 API.
- **Engineering rules:** [`EXTENSION_SOURCE_RULES.md`](EXTENSION_SOURCE_RULES.md). State and recovery notes: [`docs/NEXT_SESSION.md`](docs/NEXT_SESSION.md), [M8 status](docs/M8_STATUS.md), [architecture](docs/ARCHITECTURE.md) and [roadmap](docs/ROADMAP.md).

**Historical checkpoint (before R29):** R28 0.10.0 was in [`dist/AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib), Gate A CPU PASS, Gate B WinUAE pending ([single active test](tests/current/M13_R28_PALETTE_01.asc)). R27 0.9.3 is the latest user-confirmed WinUAE PASS, promoted to [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](dist/AMOSPro_AGA_LAST_GOOD.Lib) ([40-swap test archived](tests/passed/M12_R27_SAFE_BLIT_01.asc)). Future user-confirmed Gate B PASS automatically updates LAST_GOOD. R10 stays version-archived. Compiler and physical AGA remain untested.
