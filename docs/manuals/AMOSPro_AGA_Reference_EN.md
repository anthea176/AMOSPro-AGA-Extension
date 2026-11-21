---
title: "AMOSPro AGA Extension — 100-command reference manual"
subtitle: "AMOS Professional reference • M19 P2d • 68020+"
author: "AMOSPro-AGA-Extension — API reference"
date: "21 November 2026"
lang: en-GB
colorlinks: true
linkcolor: NavyBlue
urlcolor: NavyBlue
toc-title: "Contents"
---

> **Document revision :** 2026-11-21 • **Library :** `M19 P2d` • **API :** `100` commands / `203` AP20 entries • **Minimum CPU :** `MC68020 / 68EC020` • **Chipset :** `AGA`.
> **Library SHA256 :**  
> `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`  
> **Verified repository revision :** [`a2b4a8a9a5a8`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/a2b4a8a9a5a86a789817bab92e49f1a480b1e816) (`main`).

This manual documents the **API actually exposed by M19 P2d**. It adds no proposed commands. It is not a replacement for the AMOS Professional manual: `Aga` calls manage a private Intuition screen and are not aliases of native AMOS instructions.

## How to use this manual
Every entry specifies the **exact token name**, **AMOS form** (function or statement), **parameters**, **behaviour and limits**, **an isolated call** and **preconditions**. Individual snippets assume the screen, banks and resources are ready. Only the full appendix listings are complete programs.
Listings use **AMOS Professional** syntax, not generic BASIC: block `If … End If` has no `Then`, and procedures return via `End Proc[...]`. Import `.asc` using `Project → Merge ASCII` into a blank program.

### Validation scope
P2d was **promoted to LAST_GOOD** after the integrated P2a–P2e Bob test passed under WinUAE **Runtime (Gate B)** and the **real AMOS Compiler (Gate C)**. The test logged **121 initial `Aga Swap` refusals, all recovered by a VBL retry**, in each mode. This evidence covers that scenario, **not** 100 individual API requalification tests. Strict interpreted mode (Prg State 0) and physical AGA hardware (Gate D) are untested for that scenario. Entries were not rerun for this edition.
[P2d promotion report](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/docs/M19_P2D_LAST_GOOD_PROMOTION_2026-11-21.md) · [Integrated Bob test](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples/bob_p2_all_in_one/README.md).

## Installation and runtime environment
1. Use an **AGA A1200/A4000** or WinUAE configured for AGA and a **68020/68EC020 or later**. AMOS Professional must already be installed. Check free Chip RAM.
2. Install the sole `dist/AMOSPro_AGA.Lib` into `APSystem` as `AMOSPro_AGA.Lib`; back up the prior version, then register it in a free AMOS extension slot (**14** was used by historical tests, only if free). Keep the slot stable across upgrades; save configuration and restart AMOS.
3. Confirm the installed version, `About Loaded Extensions` and SHA256. Do not install `LAST_GOOD` as a second extension or change the slot casually: already-tokenised AMOS programs depend on it.
4. **C2P only:** install AmigaOS `c2p.library` separately in `LIBS:`; it is **not** an AMOS extension. Standalone `Aga Iff To Chunky` does not require it. AMCAF-format BankFonts are supported without necessarily installing the entire AMCAF extension.
[Full installation guide](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/INSTALL.md).

## Execution model and common traps
| Topic | Rule |
|---|---|
| **Private screen** | `Aga Screen Open` owns one Intuition AGA screen; it is not native `Screen Open`. Close before changing modes. |
| **Buffer state** | Draw to a Safe back buffer; return `0` may require bounded VBL retries before `Aga Swap`. Never present a partial frame. |
| **Synchronization** | `Aga Swap` is a **status function**, not native `Screen Swap`. `Aga Wait Vbl` is a **statement**. |
| **Rectangles** | Blit, Hotspot and Capture use width/height; `Aga Box` and `Get AGA Bob` use inclusive corners. |
| **Colours** | Palette pen 0 need not be black or transparent. `Aga Copper Move` expects RGB4, not a colour index. |
| **AMOS banks** | Check existence using `Length(n)` before `Start(n)`; never assume banks 10, 24, 27 or 28 are available. |
| **Compiler** | Runtime PASS does not prove Compiler. Use the same ASC and identify the loaded binary in both runs. |
| **Hardware sprites** | There is no `Aga Sprite` command in P2d; hardware sprites were still in S0 audit. |

## Bank-format quick reference
| Format | Contents and notes |
|---|---|
| `AGAPAL v1` | RGB24 palettes: 16-byte header plus 776 bytes per slot; zero-based slot indices. |
| `AGAPIC v1/v2` | Packed images; v1 has no embedded palette; v2 may include RGB24 + ModeID. API compatibility differs. |
| `AGBO v1` | DATA image bank for software Bobs, selected by `Aga Bob Bank`; image and transparency mask differ. |
| `FICON8` | 16×16×8-plane icons in an AMOS bank (Fast/Chip as appropriate), IDs starting at 1. |
| `FICHIP8` | Icon cache physically staged in Chip RAM for the Blitter. |
| `AGACBLK` | Temporary planar background capture in Chip RAM, with saved restore coordinates. |
| `C2P chunky` | DATA/WORK bank of linear 8-bit pixels: at least 320×256 = 81,920 bytes. |

## Index of all 100 commands
Numbers below are **reference-entry numbers**, not AP20 token IDs.

### Screen, display modes and IFF files (001–007)
[001 Aga Detect](#cmd-001) · [002 Aga Screen Open](#cmd-002)
[003 Aga Screen Close](#cmd-003) · [004 Aga Double Buffer](#cmd-004)
[005 Aga Swap](#cmd-005) · [006 Aga Pic Info](#cmd-006)
[007 Aga Iff Load](#cmd-007)

### Palettes, fades and palette banks (008–018)
[008 Aga Palette Load](#cmd-008) · [009 Aga Palette Set](#cmd-009)
[010 Aga Palette Get](#cmd-010) · [011 Aga Palette Save](#cmd-011)
[012 Aga Bank Palette Init](#cmd-012) · [013 Aga Bank Palette Capture](#cmd-013)
[014 Aga Bank Palette Apply](#cmd-014) · [015 Aga Bank Palette Fade](#cmd-015)
[016 Aga Fade To Black](#cmd-016) · [017 Aga Fade To White](#cmd-017)
[018 Aga Palette Cycle](#cmd-018)

### Keyboard and timing (019–021)
[019 Aga Key](#cmd-019) · [020 Aga Wait Key](#cmd-020)
[021 Aga Wait Vbl](#cmd-021)

### Blitter and rectangles (022–024)
[022 Aga Blit Copy](#cmd-022) · [023 Aga Blit Fill](#cmd-023)
[024 Aga Blit Clear](#cmd-024)

### Copper raster effects (025–030)
[025 Aga Copper Clear](#cmd-025) · [026 Aga Copper Wait](#cmd-026)
[027 Aga Copper Move](#cmd-027) · [028 Aga Copper End](#cmd-028)
[029 Aga Copper On](#cmd-029) · [030 Aga Copper Off](#cmd-030)

### Mouse, hit testing and rectangle collisions (031–037)
[031 Aga Mouse X](#cmd-031) · [032 Aga Mouse Y](#cmd-032)
[033 Aga Mouse Buttons](#cmd-033) · [034 Aga Mouse Pressed](#cmd-034)
[035 Aga Mouse Released](#cmd-035) · [036 Aga Hotspot Hit](#cmd-036)
[037 Aga Rect Overlap](#cmd-037)

### Text, fonts and 2D primitives (038–045)
[038 Aga Text](#cmd-038) · [039 Aga Font Select](#cmd-039)
[040 Aga Bank Font Select](#cmd-040) · [041 Aga Plot](#cmd-041)
[042 Aga Draw](#cmd-042) · [043 Aga Box](#cmd-043)
[044 Aga Circle](#cmd-044) · [045 Aga Mouse Cursor](#cmd-045)

### Images, icons, captures and caches (046–061)
[046 Aga Bank Image Draw](#cmd-046) · [047 Aga Image Region](#cmd-047)
[048 Aga F Icon](#cmd-048) · [049 Aga F Blit](#cmd-049)
[050 Aga F Icon Bank Create](#cmd-050) · [051 Aga F Icon Bank Put](#cmd-051)
[052 Aga F Chip Bank Create](#cmd-052) · [053 Aga F Chip Stage](#cmd-053)
[054 Aga F Icon Capture](#cmd-054) · [055 Aga C Block Capture](#cmd-055)
[056 Aga C Block Draw](#cmd-056) · [057 Aga C Block Restore](#cmd-057)
[058 Aga Bank Image Info](#cmd-058) · [059 Aga Bank Image Capture](#cmd-059)
[060 Aga Bob Batch](#cmd-060) · [061 Aga Cache Blit](#cmd-061)

### AGA software Bobs (062–083)
[062 Aga Bob Bank](#cmd-062) · [063 Aga Bob Bank Free](#cmd-063)
[064 Get AGA Bob](#cmd-064) · [065 Make AGA Bob Mask](#cmd-065)
[066 No AGA Bob Mask](#cmd-066) · [067 Aga Bob Blit](#cmd-067)
[068 Aga Bob](#cmd-068) · [069 Aga Bob Off](#cmd-069)
[070 Aga Bob Draw](#cmd-070) · [071 Aga Bob Clear](#cmd-071)
[072 Aga Bob Update](#cmd-072) · [073 Aga Bob Priority](#cmd-073)
[074 Aga Limit Bob](#cmd-074) · [075 Aga Del Bob](#cmd-075)
[076 Aga Ins Bob](#cmd-076) · [077 Aga Bob Col](#cmd-077)
[078 Aga Bob Flip](#cmd-078) · [079 Aga Bob Planes](#cmd-079)
[080 Aga Bob Auto Update](#cmd-080) · [081 Aga X Bob](#cmd-081)
[082 Aga Y Bob](#cmd-082) · [083 Aga I Bob](#cmd-083)

### Chunky-to-planar (C2P) (084–089)
[084 Aga Iff To Chunky](#cmd-084) · [085 Aga C2P Open](#cmd-085)
[086 Aga C2P Blit](#cmd-086) · [087 Aga C2P Zoom](#cmd-087)
[088 Aga C2P Convert](#cmd-088) · [089 Aga C2P Close](#cmd-089)

### Diagnostics and full-buffer filling (090–093)
[090 Aga Probe](#cmd-090) · [091 Aga Demo](#cmd-091)
[092 Aga Screen Pattern](#cmd-092) · [093 Aga Back Fill](#cmd-093)

### Low-level pointer forms (094–100)
[094 Aga Palette Bank Init](#cmd-094) · [095 Aga Palette Bank Capture](#cmd-095)
[096 Aga Palette Bank Apply](#cmd-096) · [097 Aga Fade To Bank](#cmd-097)
[098 Aga Image Draw](#cmd-098) · [099 Aga Image Capture](#cmd-099)
[100 Aga Font Bank Select](#cmd-100)

# Command dictionary

## Screen, display modes and IFF files

The extension owns a private Intuition AGA screen. Check each opening result and close it before returning to AMOS.

### 001. Aga Detect {#cmd-001}

**AMOS form :** Numeric function (assign result)

```amos
_AGA=Aga Detect
```

**Purpose and behaviour —** Detects an AGA chipset. A nonzero result means available; do not assume true is always 1.

**Return / effect —** nonzero = AGA detected; 0 = absent.

**Sample call :**
```amos
_AGA=Aga Detect
```

### 002. Aga Screen Open {#cmd-002}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Screen Open(largeur,hauteur,nbCouleurs,modeID)
```

**Purpose and behaviour —** Opens the extension's private Intuition screen, separate from native AMOS screens. The colour argument is a number of entries (2–256, powers of two), not bitplanes. Requires an AmigaOS ModeID; returns 1/0.

**Parameters :**
- `largeur` — screen width in pixels.
- `hauteur` — screen height in pixels.
- `nbCouleurs` — number of indexed colours, not bitplanes.
- `modeID` — AmigaOS display ModeID (`$00021000` = PAL LowRes).

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Dimensions in pixels

**Sample call :**
```amos
_OK=Aga Screen Open(320,256,256,$00021000)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 003. Aga Screen Close {#cmd-003}

**AMOS form :** Statement (no assignment)

```amos
Aga Screen Close
```

**Purpose and behaviour —** Closes the private AGA screen after Safe/Disp handling. Statement without a return value; not native AMOS Screen Close.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Screen Close
```

### 004. Aga Double Buffer {#cmd-004}

**AMOS form :** Numeric function (assign result)

```amos
_DB=Aga Double Buffer
```

**Purpose and behaviour —** Enables double buffering for the private screen; returns 1 on success, 0 on failure.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_DB=Aga Double Buffer
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 005. Aga Swap {#cmd-005}

**AMOS form :** Numeric function (assign result)

```amos
_SW=Aga Swap
```

**Purpose and behaviour —** Presents the prepared back buffer. Returns 1 on success, 0 when buffer state forbids presentation; an unvalidated DIRTY frame may be rejected.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_SW=Aga Swap
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 006. Aga Pic Info {#cmd-006}

**AMOS form :** Numeric function (assign result)

```amos
_V=Aga Pic Info(fichier$,champ)
```

**Purpose and behaviour —** Reads an IFF/ILBM metadata field by index 0–7; returns its value or -1 on error.

**Parameters :**
- `fichier$` — AmigaDOS file path, AMOS string.
- `champ` — field index: see metadata table.

**Return / effect —** requested field value; −1 on error.

**Sample call :**
```amos
_W=Aga Pic Info(_FILE$,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 007. Aga Iff Load {#cmd-007}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Iff Load(fichier$)
```

**Purpose and behaviour —** Loads pixels and palette from a compatible IFF/ILBM into the active AGA screen. Returns 1/0; first open a screen of matching dimensions and mode.

**Parameters :**
- `fichier$` — AmigaDOS file path, AMOS string.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Iff Load(_FILE$)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

## Palettes, fades and palette banks

Palette entries are logical indices. 24-bit colours and Copper RGB4 values are not interchangeable.

### 008. Aga Palette Load {#cmd-008}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Palette Load(_FILE$)
```

**Purpose and behaviour —** Imports only the CMAP from an IFF FORM ILBM, including palette-only files without BODY or BMHD. Does not write pixels; returns 1/0.

**Parameters :**
- `_FILE$` — AmigaDOS path, AMOS string.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Palette Load(_FILE$)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 009. Aga Palette Set {#cmd-009}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Palette Set(_PEN,_R,_G,_B)
```

**Purpose and behaviour —** Sets one indexed ColorMap entry with 8-bit RGB components (0–255), using LoadRGB32. No implicit VBL wait. HAM, EHB and dual-playfield modes are unsupported; returns 1/0.

**Parameters :**
- `_PEN` — private-screen palette index.
- `_R` — 8-bit red channel (0..255).
- `_G` — 8-bit green channel (0..255).
- `_B` — 8-bit blue channel (0..255).

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Palette Set(1,255,0,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 010. Aga Palette Get {#cmd-010}

**AMOS form :** Numeric function (assign result)

```amos
_RGB=Aga Palette Get(_PEN)
```

**Purpose and behaviour —** Reads a palette entry using GetRGB32. Returns packed $00RRGGBB or -1 on failure; black is 0 and is not an error.

**Parameters :**
- `_PEN` — private-screen palette index.

**Return / effect —** packed RGB24 `$00RRGGBB`; −1 on error.

**Sample call :**
```amos
_RGB=Aga Palette Get(1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 011. Aga Palette Save {#cmd-011}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Palette Save(_FILE$)
```

**Purpose and behaviour —** Writes the ColorMap as IFF FORM ILBM containing BMHD and CMAP without BODY. AmigaDOS path length is 1–255 bytes. Overwrites an existing file even if a later write fails; returns 1/0.

**Parameters :**
- `_FILE$` — AmigaDOS path, AMOS string.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Warning: existing file is overwritten.

**Sample call :**
```amos
_OK=Aga Palette Save("RAM:aga_palette.iff")
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 012. Aga Bank Palette Init {#cmd-012}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bank Palette Init(_B,_N)
```

**Purpose and behaviour —** Initializes an existing AMOS DATA bank as AGAPAL v1 with N slots (1–256), exact size 16+776×N bytes. Bank number 5–65535; returns 1/0.

**Parameters :**
- `_B` — number of an existing AMOS DATA bank.
- `_N` — number of palette slots, 1–256.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** AGAPAL bank must already exist, exactly `16 + 776 × N` bytes.

**Sample call :**
```amos
_OK=Aga Bank Palette Init(10,2)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 013. Aga Bank Palette Capture {#cmd-013}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bank Palette Capture(_B,_INDEX)
```

**Purpose and behaviour —** Copies current screen colours to a zero-based slot in an AGAPAL v1 DATA bank. Does not modify the screen; returns 1/0.

**Parameters :**
- `_B` — number of an existing AMOS DATA bank.
- `_INDEX` — zero-based slot index.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bank Palette Capture(10,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 014. Aga Bank Palette Apply {#cmd-014}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bank Palette Apply(_B,_INDEX)
```

**Purpose and behaviour —** Immediately applies a populated AGAPAL v1 slot, or an AGAPIC v2 palette at index 0. AGAPIC v2 requires a matching ModeID; no drawing or VBL wait; returns 1/0.

**Parameters :**
- `_B` — number of an existing AMOS DATA bank.
- `_INDEX` — zero-based slot index.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bank Palette Apply(10,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 015. Aga Bank Palette Fade {#cmd-015}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bank Palette Fade(_B,_INDEX,_VBL)
```

**Purpose and behaviour —** Blocking fade to AGAPAL v1 or AGAPIC v2 (index 0), lasting 1–255 VBL. The last step produces the exact target palette. Returns 1/0.

**Parameters :**
- `_B` — number of an existing AMOS DATA bank.
- `_INDEX` — zero-based slot index.
- `_VBL` — blocking duration of 1–255 VBL.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bank Palette Fade(10,0,32)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 016. Aga Fade To Black {#cmd-016}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Fade To Black(_VBL)
```

**Purpose and behaviour —** Blocking fade of every logical palette entry to exact black over 1–255 VBL. Pixels remain unchanged; returns 1/0.

**Parameters :**
- `_VBL` — blocking duration of 1–255 VBL.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Fade To Black(32)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 017. Aga Fade To White {#cmd-017}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Fade To White(_VBL)
```

**Purpose and behaviour —** Blocking fade of all logical palette entries to exact white over 1–255 VBL. Pixels remain unchanged; returns 1/0.

**Parameters :**
- `_VBL` — blocking duration of 1–255 VBL.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Fade To White(32)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 018. Aga Palette Cycle {#cmd-018}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Palette Cycle(First,Last,Direction)
```

**Purpose and behaviour —** Rotates an inclusive colour range once: 0 ≤ First < Last < 256. Direction 1 moves the last entry to First, -1 reverses. Preserves full RGB32 values; no automatic VBL; returns 1/0.

**Parameters :**
- `First` — inclusive first palette index.
- `Last` — inclusive last palette index.
- `Direction` — rotation direction: 1 or −1.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** One rotation per call; no implicit VBL wait.

**Sample call :**
```amos
_OK=Aga Palette Cycle(1,15,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

## Keyboard and timing

Keyboard events use RAWKEY codes, which are not necessarily ASCII. `Aga Wait Vbl` waits for vertical retrace.

### 019. Aga Key {#cmd-019}

**AMOS form :** Numeric function (assign result)

```amos
_K=Aga Key
```

**Purpose and behaviour —** Non-blocking keyboard read from a 16-entry RAWKEY FIFO shared with the mouse-event dispatcher. The code is not ASCII.

**Return / effect —** available RAWKEY code / status sentinel.

**Sample call :**
```amos
_K=Aga Key
```

### 020. Aga Wait Key {#cmd-020}

**AMOS form :** Numeric function (assign result)

```amos
_K=Aga Wait Key
```

**Purpose and behaviour —** Waits for a keyboard event from the AGA Intuition window and returns its RAWKEY code, not an ASCII character.

**Return / effect —** RAWKEY code; ASCII not guaranteed.

**Sample call :**
```amos
_K=Aga Wait Key
```

### 021. Aga Wait Vbl {#cmd-021}

**AMOS form :** Statement (no assignment)

```amos
Aga Wait Vbl
```

**Purpose and behaviour —** Waits for one vertical blank using WaitTOF; does nothing if no AGA screen is open.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Wait Vbl
```

## Blitter and rectangles

The final arguments specify width and height, not the opposite corner. Drawing depends on the back buffer Safe state.

### 022. Aga Blit Copy {#cmd-022}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Blit Copy(sourceX,sourceY,destX,destY,largeur,hauteur)
```

**Purpose and behaviour —** Copies a rectangle within the same back buffer. Width and height are dimensions, not ending coordinates. Non-blocking Safe check before DMA; returns 1/0.

**Parameters :**
- `sourceX` — pixel coordinate (source/destination per its name).
- `sourceY` — pixel coordinate (source/destination per its name).
- `destX` — pixel coordinate (source/destination per its name).
- `destY` — pixel coordinate (source/destination per its name).
- `largeur` — screen width in pixels.
- `hauteur` — screen height in pixels.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Both rectangles are in the same back buffer; width/height, not ending corners.

**Sample call :**
```amos
_OK=Aga Blit Copy(16,24,152,24,104,68)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 023. Aga Blit Fill {#cmd-023}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Blit Fill(x,y,largeur,hauteur,indexCouleur)
```

**Purpose and behaviour —** Fills a rectangle of the back buffer with a palette index. Non-blocking Safe check before DMA; returns 1/0 and draws nothing if the buffer is unavailable.

**Parameters :**
- `x` — integer or address according to the description below.
- `y` — integer or address according to the description below.
- `largeur` — screen width in pixels.
- `hauteur` — screen height in pixels.
- `indexCouleur` — integer or address according to the description below.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Final argument is a colour index, not RGB24.

**Sample call :**
```amos
_OK=Aga Blit Fill(16,24,104,68,63)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 024. Aga Blit Clear {#cmd-024}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Blit Clear(x,y,largeur,hauteur)
```

**Purpose and behaviour —** Fills a back-buffer rectangle with palette index 0 (not necessarily black). Safe-guarded; returns 1/0.

**Parameters :**
- `x` — integer or address according to the description below.
- `y` — integer or address according to the description below.
- `largeur` — screen width in pixels.
- `hauteur` — screen height in pixels.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Clearing writes palette index 0, which need not be black.

**Sample call :**
```amos
_OK=Aga Blit Clear(32,40,72,36)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

## Copper raster effects

All six Copper calls are functions and need a result assignment. Only the colour registers exposed by this API are permitted.

### 025. Aga Copper Clear {#cmd-025}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Copper Clear
```

**Purpose and behaviour —** Creates an empty Copper list for the private screen. Call before appending WAIT or MOVE. Returns 1/0.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Copper Clear
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 026. Aga Copper Wait {#cmd-026}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Copper Wait(v,h)
```

**Purpose and behaviour —** Appends a WAIT at raster position v (0–255) and h (0–222). Consecutive WAIT positions must increase strictly; returns 1/0.

**Parameters :**
- `v` — raster vertical line 0..255.
- `h` — horizontal position 0..222.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Copper Wait(20,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 027. Aga Copper Move {#cmd-027}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Copper Move(registre,rgb4)
```

**Purpose and behaviour —** Appends a colour-register write: even offset $180–$1BE for COLOR00–COLOR31 and 12-bit RGB4 $000–$FFF. This is not a palette index; returns 1/0.

**Parameters :**
- `registre` — even colour register from `$180` to `$1BE`.
- `rgb4` — 12-bit RGB4 value, not a palette index.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** `$180` selects COLOR00; `$F00` is RGB4 red.

**Sample call :**
```amos
_OK=Aga Copper Move($180,$F00)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 028. Aga Copper End {#cmd-028}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Copper End
```

**Purpose and behaviour —** Seals a non-empty Copper list. A second End or an append after End is rejected; returns 1/0.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Copper End
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 029. Aga Copper On {#cmd-029}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Copper On
```

**Purpose and behaviour —** Installs a prepared and finalized Copper list into the private ViewPort's Intuition display; returns 1/0.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Copper On
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 030. Aga Copper Off {#cmd-030}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Copper Off
```

**Purpose and behaviour —** Removes the Copper list, restores the display and frees extension-owned resources. Repeated calls are accepted; returns 1/0.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Copper Off
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

## Mouse, hit testing and rectangle collisions

Button reads return bitmasks; rectangle helpers use pixel dimensions.

### 031. Aga Mouse X {#cmd-031}

**AMOS form :** Numeric function (assign result)

```amos
_MX=Aga Mouse X
```

**Purpose and behaviour —** Reads the pointer's horizontal position in logical screen pixels; returns -1 if outside the screen or the screen is closed.

**Return / effect —** pixel position; −1 when unavailable.

**Sample call :**
```amos
_MX=Aga Mouse X
```

### 032. Aga Mouse Y {#cmd-032}

**AMOS form :** Numeric function (assign result)

```amos
_MY=Aga Mouse Y
```

**Purpose and behaviour —** Reads the pointer's vertical position in logical screen pixels; returns -1 if outside the screen or the screen is closed.

**Return / effect —** pixel position; −1 when unavailable.

**Sample call :**
```amos
_MY=Aga Mouse Y
```

### 033. Aga Mouse Buttons {#cmd-033}

**AMOS form :** Numeric function (assign result)

```amos
_B=Aga Mouse Buttons
```

**Purpose and behaviour —** Returns current button state: bit 1 left, bit 2 right, bit 4 middle (combinable 0–7); -1 if the device/window is unavailable.

**Return / effect —** bitmask 0..7; −1 when unavailable.

**Sample call :**
```amos
_B=Aga Mouse Buttons
```

### 034. Aga Mouse Pressed {#cmd-034}

**AMOS form :** Numeric function (assign result)

```amos
_P=Aga Mouse Pressed
```

**Purpose and behaviour —** Returns press edges accumulated since the previous read, using bits 1/2/4. Different from the held-button state returned by Buttons.

**Return / effect —** pressed-edge bitmask 0..7.

**Sample call :**
```amos
_P=Aga Mouse Pressed
```

### 035. Aga Mouse Released {#cmd-035}

**AMOS form :** Numeric function (assign result)

```amos
_R=Aga Mouse Released
```

**Purpose and behaviour —** Returns release edges accumulated since the previous read, using bits 1/2/4, independently of Pressed.

**Return / effect —** released-edge bitmask 0..7.

**Sample call :**
```amos
_R=Aga Mouse Released
```

### 036. Aga Hotspot Hit {#cmd-036}

**AMOS form :** Numeric function (assign result)

```amos
_HIT=Aga Hotspot Hit(_PX,_PY,_X,_Y,_W,_H)
```

**Purpose and behaviour —** Checks whether a point lies inside a rectangle defined by X/Y origin and W/H dimensions. Returns integer 1 inside, 0 outside.

**Parameters :**
- `_PX` — test point X.
- `_PY` — test point Y.
- `_X` — region origin X.
- `_Y` — region origin Y.
- `_W` — region width in pixels.
- `_H` — region height in pixels.

**Return / effect —** 1 = inside rectangle, 0 = outside.

**Sample call :**
```amos
_HIT=Aga Hotspot Hit(20,30,10,10,64,40)
```

### 037. Aga Rect Overlap {#cmd-037}

**AMOS form :** Numeric function (assign result)

```amos
_C=Aga Rect Overlap(_AX,_AY,_AW,_AH,_BX,_BY,_BW,_BH)
```

**Purpose and behaviour —** Tests whether two rectangles (each with origin and dimensions) have overlapping area. Returns 1 for overlap, 0 otherwise.

**Parameters :**
- `_AX` — rectangle A origin X.
- `_AY` — rectangle A origin Y.
- `_AW` — rectangle A width.
- `_AH` — rectangle A height.
- `_BX` — rectangle B origin X.
- `_BY` — rectangle B origin Y.
- `_BW` — rectangle B width.
- `_BH` — rectangle B height.

**Return / effect —** 1 = overlap, 0 = no overlap.

**Sample call :**
```amos
_C=Aga Rect Overlap(0,0,32,32,16,16,32,32)
```

## Text, fonts and 2D primitives

Drawing targets the back buffer. AmigaOS disk fonts and AMCAF BankFonts are different mechanisms.

### 038. Aga Text {#cmd-038}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Text(_X,_BASELINE_Y,_PEN,_TEXT$)
```

**Purpose and behaviour —** Draws one transparent JAM1 text line into the back buffer: X, baseline Y, colour index and AMOS string. Returns 1/0.

**Parameters :**
- `_X` — horizontal pixel position.
- `_BASELINE_Y` — text baseline Y coordinate.
- `_PEN` — text palette index.
- `_TEXT$` — AMOS text string to draw.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Text(16,32,1,"AGA TEXT")
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 039. Aga Font Select {#cmd-039}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Font Select(_FONT$,_YSIZE)
```

**Purpose and behaviour —** Loads an AmigaOS .font through diskfont.library and selects its vertical size (1–255). Returns 1/0.

**Parameters :**
- `_FONT$` — AmigaOS `.font` name.
- `_YSIZE` — requested font pixel height, 1–255.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Font Select("topaz.font",8)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 040. Aga Bank Font Select {#cmd-040}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bank Font Select(Bank)
```

**Purpose and behaviour —** Selects an AMCAF BankFont using its existing DATA bank number; address and length are resolved automatically. Returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Consumes an AMCAF-format BankFont; the AMCAF extension itself is not automatically required.

**Sample call :**
```amos
_OK=Aga Bank Font Select(10)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 041. Aga Plot {#cmd-041}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Plot(X,Y,Pen)
```

**Purpose and behaviour —** Plots one pixel in the back buffer at X/Y using a palette index supported by the active depth. Returns 1/0.

**Parameters :**
- `X` — pixel X coordinate.
- `Y` — pixel Y coordinate.
- `Pen` — current indexed palette entry.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Plot(24,40,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 042. Aga Draw {#cmd-042}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Draw(X1,Y1,X2,Y2,Pen)
```

**Purpose and behaviour —** Draws a one-pixel-wide line between two endpoints (both included), with clipping for partially off-screen lines. Returns 1/0.

**Parameters :**
- `X1` — pixel coordinate (source/destination per its name).
- `Y1` — pixel coordinate (source/destination per its name).
- `X2` — pixel coordinate (source/destination per its name).
- `Y2` — pixel coordinate (source/destination per its name).
- `Pen` — current indexed palette entry.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Draw(10,20,80,100,2)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 043. Aga Box {#cmd-043}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Box(X1,Y1,X2,Y2,Pen)
```

**Purpose and behaviour —** Draws a rectangle outline from two inclusive corners. The four coordinates are not width/height parameters; returns 1/0.

**Parameters :**
- `X1` — pixel coordinate (source/destination per its name).
- `Y1` — pixel coordinate (source/destination per its name).
- `X2` — pixel coordinate (source/destination per its name).
- `Y2` — pixel coordinate (source/destination per its name).
- `Pen` — current indexed palette entry.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Both corners are inclusive; do not confuse with Blitter dimensions.

**Sample call :**
```amos
_OK=Aga Box(10,20,90,90,3)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 044. Aga Circle {#cmd-044}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Circle(CX,CY,Radius,Pen)
```

**Purpose and behaviour —** Draws an outline circle centred at CX/CY with integer radius 0–32767 and a palette index. Radius zero means one pixel; returns 1/0.

**Parameters :**
- `CX` — circle centre X.
- `CY` — circle centre Y.
- `Radius` — nonnegative integer radius (0..32767).
- `Pen` — current indexed palette entry.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Circle(80,80,24,4)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 045. Aga Mouse Cursor {#cmd-045}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Mouse Cursor(Visible)
```

**Purpose and behaviour —** Shows (1) or hides (0) only the Intuition cursor of the private AGA window. Does not reserve a hardware Sprite channel; returns 1/0.

**Parameters :**
- `Visible` — 0 = hide; 1 = show.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Mouse Cursor(0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

## Images, icons, captures and caches

AGAPIC, FICON8, FICHIP8 and AGACBLK are different formats. Respect Chip/Fast requirements and live bank identity.

### 046. Aga Bank Image Draw {#cmd-046}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bank Image Draw(Bank,X,Y,Mode)
```

**Purpose and behaviour —** Draws an AGAPIC v1/RLE image from an existing DATA bank, resolved by bank number. Destination is the back buffer; returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Mode` — command-specific integer mode.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bank Image Draw(10,32,32,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 047. Aga Image Region {#cmd-047}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Image Region(Bank,SrcX,SrcY,Width,Height,X,Y,Mode)
```

**Purpose and behaviour —** Draws a source region of dimensions Width/Height from an AGAPIC image in a DATA bank. Source SrcX/SrcY and destination X/Y are separate; returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `SrcX` — pixel coordinate (source/destination per its name).
- `SrcY` — pixel coordinate (source/destination per its name).
- `Width` — positive pixel width.
- `Height` — positive pixel height.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Mode` — command-specific integer mode.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Image Region(10,0,0,16,16,64,32,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 048. Aga F Icon {#cmd-048}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga F Icon(Bank,IconID,X,Y,Mode)
```

**Purpose and behaviour —** CPU-renders a FICON8 icon of 16×16 pixels and 8 planes, one-based icon ID, from a DATA bank into the back buffer; returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `IconID` — icon ID starting at 1.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Mode` — command-specific integer mode.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga F Icon(11,1,32,32,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 049. Aga F Blit {#cmd-049}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga F Blit(CacheBank,IconID,X,Y,Mode)
```

**Purpose and behaviour —** Blitter-renders a 16×16×8 icon from a FICHIP8 cache physically resident in Chip RAM. Mode 0 is opaque, mode 1 transparent; returns 1/0.

**Parameters :**
- `CacheBank` — AMOS bank number of the required format.
- `IconID` — icon ID starting at 1.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Mode` — command-specific integer mode.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga F Blit(12,1,32,32,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 050. Aga F Icon Bank Create {#cmd-050}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga F Icon Bank Create(Bank,Count)
```

**Purpose and behaviour —** Creates a FICON8 DATA bank with 4–4096 empty 16×16×8 icon slots. Requires a free bank number 5–65535; prefers Fast RAM; returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `Count` — element count limited by the format.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga F Icon Bank Create(11,16)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 051. Aga F Icon Bank Put {#cmd-051}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga F Icon Bank Put(DestBank,IconID,PixelBank,ByteOffset)
```

**Purpose and behaviour —** Converts 256 chunky 8-bit indices from a source DATA bank starting at ByteOffset into an existing FICON8 slot. Icon IDs start at 1; returns 1/0.

**Parameters :**
- `DestBank` — AMOS bank number of the required format.
- `IconID` — icon ID starting at 1.
- `PixelBank` — AMOS bank number of the required format.
- `ByteOffset` — integer or address according to the description below.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga F Icon Bank Put(11,1,13,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 052. Aga F Chip Bank Create {#cmd-052}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga F Chip Bank Create(CacheBank,Count)
```

**Purpose and behaviour —** Creates a FICHIP8 cache bank of 4–4096 16×16×8 icons in genuine Chip RAM for Blitter transfers. Returns 1/0.

**Parameters :**
- `CacheBank` — AMOS bank number of the required format.
- `Count` — element count limited by the format.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga F Chip Bank Create(12,16)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 053. Aga F Chip Stage {#cmd-053}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga F Chip Stage(SourceBank,CacheBank,IconID)
```

**Purpose and behaviour —** Stages the selected FICON8 icon into the same-ID slot of an already allocated FICHIP8 Chip cache. Returns 1/0.

**Parameters :**
- `SourceBank` — AMOS bank number of the required format.
- `CacheBank` — AMOS bank number of the required format.
- `IconID` — icon ID starting at 1.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga F Chip Stage(11,12,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 054. Aga F Icon Capture {#cmd-054}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga F Icon Capture(Bank,IconID,X,Y)
```

**Purpose and behaviour —** Captures a 16×16 square from the eight-plane back buffer into an existing FICON8 icon slot; rectangle must lie entirely on screen. Returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `IconID` — destination ID of an existing icon, starting at 1.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga F Icon Capture(11,1,32,32)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 055. Aga C Block Capture {#cmd-055}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga C Block Capture(Bank,X,Y,Width,Height,Method)
```

**Purpose and behaviour —** Captures uncompressed planar data into an AGACBLK bank physically resident in Chip RAM. Method selects the CPU/Blitter path under its contract; returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Width` — positive pixel width.
- `Height` — positive pixel height.
- `Method` — transfer method: 0 CPU8, 1 CPU16, 2 Blitter for CBlock.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** The AGACBLK destination bank must reside in actual Chip RAM.

**Sample call :**
```amos
_OK=Aga C Block Capture(14,32,32,16,16,2)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 056. Aga C Block Draw {#cmd-056}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga C Block Draw(Bank,X,Y,Method)
```

**Purpose and behaviour —** Restores an opaque AGACBLK CBlock at X/Y, including palette index zero. Method 0 CPU8, 1 CPU16, 2 Blitter; respect 8/16-pixel X alignment; returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Method` — transfer method: 0 CPU8, 1 CPU16, 2 Blitter for CBlock.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga C Block Draw(14,64,64,2)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 057. Aga C Block Restore {#cmd-057}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga C Block Restore(Bank,Method)
```

**Purpose and behaviour —** Restores a Chip CBlock at its recorded capture position. Method 0 CPU8, 1 CPU16, 2 Blitter; release the bank with Erase Bank; returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `Method` — transfer method: 0 CPU8, 1 CPU16, 2 Blitter for CBlock.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga C Block Restore(14,2)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 058. Aga Bank Image Info {#cmd-058}

**AMOS form :** Numeric function (assign result)

```amos
_VALEUR=Aga Bank Image Info(Bank,Champ)
```

**Purpose and behaviour —** Reads metadata from an AGAPIC DATA bank without changing bank or pixels. Documented fields include 1 width, 2 height, 3 depth, 4 colour count; additional fields depend on format.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `Champ` — metadata field selector.

**Return / effect —** requested metadata field; see the AGAPIC field contract.

**Sample call :**
```amos
_W=Aga Bank Image Info(10,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 059. Aga Bank Image Capture {#cmd-059}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)
```

**Purpose and behaviour —** Captures a back-buffer rectangle into a new, free AGAPIC bank. Version 1 or 2; v2 embeds an RGB24 palette and the ModeID. Returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Width` — positive pixel width.
- `Height` — positive pixel height.
- `TransparentIndex` — integer or address according to the description below.
- `Version` — integer or address according to the description below.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bank Image Capture(10,0,0,32,32,0,2)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 060. Aga Bob Batch {#cmd-060}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Batch(DescriptorBank,Count)
```

**Purpose and behaviour —** Draws 1–256 BOB1 descriptors from a DATA bank in sequence into the inactive, Safe back buffer. Not the persistent-Bob manager; returns 1/0.

**Parameters :**
- `DescriptorBank` — DATA bank containing BOB1 descriptors.
- `Count` — batch size, up to 256 Bobs.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bob Batch(15,4)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 061. Aga Cache Blit {#cmd-061}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Cache Blit(CacheBank,X,Y,Mode)
```

**Purpose and behaviour —** Blitter-renders a planar AGPC 16×16×8 cache in real Chip RAM. Its visibility mask is independent of colour zero; returns 1/0.

**Parameters :**
- `CacheBank` — AMOS bank number of the required format.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Mode` — command-specific integer mode.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Cache Blit(16,32,32,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

## AGA software Bobs

AGBO banks, persistent objects, their images and physical pages have separate lifecycles. Never present an unprepared page.

### 062. Aga Bob Bank {#cmd-062}

**AMOS form :** Statement (no assignment)

```amos
Aga Bob Bank _BANK
```

**Purpose and behaviour —** Selects or prepares an AGBO v1 bank by number (5–65535). The bank may be empty; this statement has no function return.

**Parameters :**
- `_BANK` — AGBO DATA bank number.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Bob Bank 24
```
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 063. Aga Bob Bank Free {#cmd-063}

**AMOS form :** Statement (no assignment)

```amos
Aga Bob Bank Free _BANK
```

**Purpose and behaviour —** Releases the Chip cache tied to an AGBO bank and disables its dependent Bobs when the frame is CLEAN. Does not arbitrarily destroy other banks; no return value.

**Parameters :**
- `_BANK` — AGBO DATA bank number.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Bob Bank Free 24
```

### 064. Get AGA Bob {#cmd-064}

**AMOS form :** Statement (no assignment)

```amos
Get AGA Bob _I,_X1,_Y1,_X2,_Y2
```

**Purpose and behaviour —** Captures image ID 1–4096 into the selected AGBO bank using inclusive back-buffer corners. Example: (0,0) to (31,31) yields 32×32. Statement without a return value.

**Parameters :**
- `_I` — target AGBO image ID, 1..4096.
- `_X1` — inclusive rectangle left X.
- `_Y1` — inclusive rectangle top Y.
- `_X2` — inclusive rectangle right X.
- `_Y2` — inclusive rectangle bottom Y.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Important note —** `X1,Y1,X2,Y2` are inclusive; (0,0)–(31,31) gives 32×32.

**Sample call :**
```amos
Get AGA Bob 1,0,0,31,31
```
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 065. Make AGA Bob Mask {#cmd-065}

**AMOS form :** Statement (no assignment)

```amos
Make AGA Bob Mask _I,_C
```

**Purpose and behaviour —** Builds or replaces the transparency mask of an existing AGBO image: pixels of palette index C become transparent. Statement without a return value.

**Parameters :**
- `_I` — existing AGBO image ID, 1..4096.
- `_C` — palette index to make transparent.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Make AGA Bob Mask 1,0
```

### 066. No AGA Bob Mask {#cmd-066}

**AMOS form :** Statement (no assignment)

```amos
No AGA Bob Mask _I
```

**Purpose and behaviour —** Removes an AGBO image's transparency mask so all pixels become opaque, including palette index zero. Statement without a return value.

**Parameters :**
- `_I` — AGBO image ID whose mask is removed.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Important note —** Without a mask, palette-index-0 pixels become opaque.

**Sample call :**
```amos
No AGA Bob Mask 1
```

### 067. Aga Bob Blit {#cmd-067}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Blit(_I,_X,_Y)
```

**Purpose and behaviour —** Immediately draws selected AGBO image I at signed X/Y into the back buffer, without registering a persistent Bob. Returns 1/0.

**Parameters :**
- `_I` — AGBO image ID to display.
- `_X` — signed draw position X.
- `_Y` — signed draw position Y.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bob Blit(1,32,32)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 068. Aga Bob {#cmd-068}

**AMOS form :** Statement (no assignment)

```amos
Aga Bob _N,_X,_Y,_I
```

**Purpose and behaviour —** Declares or moves a persistent Bob ID 1–64 with image I from an identified AGBO bank. X/Y coordinates are signed. Statement without a return value.

**Parameters :**
- `_N` — persistent Bob ID, 1..64.
- `_X` — signed Bob X position.
- `_Y` — signed Bob Y position.
- `_I` — AGBO image ID, 1..4096.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Bob 1,32,32,1
```
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 069. Aga Bob Off {#cmd-069}

**AMOS form :** Statement (no assignment)

```amos
Aga Bob Off _N
```

**Purpose and behaviour —** Disables persistent Bob N (1–64), without immediate clearing, drawing or Swap. Statement without a return value.

**Parameters :**
- `_N` — persistent Bob ID to deactivate, 1..64.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Bob Off 1
```

### 070. Aga Bob Draw {#cmd-070}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Draw
```

**Purpose and behaviour —** Draws active persistent Bobs into the Safe back buffer in priority order. Does not implicitly present the frame; returns 1/0.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bob Draw
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 071. Aga Bob Clear {#cmd-071}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Clear
```

**Purpose and behaviour —** Restores the saved background of the physical Safe back page. Does not assume the two pages share one background; returns 1/0.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bob Clear
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 072. Aga Bob Update {#cmd-072}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Update
```

**Purpose and behaviour —** Prevalidates images, restores the relevant backgrounds and draws active Bobs on the physical back page. Returns 1/0; presentation is not implicit.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Bob Update
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 073. Aga Bob Priority {#cmd-073}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Priority(Mode)
```

**Purpose and behaviour —** Sets drawing order: 0 ascending ID, 1 ascending Y then ID, 2 descending ID, 3 descending Y then ID. Returns 1/0.

**Parameters :**
- `Mode` — 0 ascending ID; 1 ascending Y/ID; 2 descending ID; 3 descending Y/ID.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Priority: 0 ascending ID; 1 ascending Y then ID; 2 descending ID; 3 descending Y then ID.

**Sample call :**
```amos
_OK=Aga Bob Priority(1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 074. Aga Limit Bob {#cmd-074}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Limit Bob(N,X,Y,W,H)
```

**Purpose and behaviour —** Sets a global limit (N=0) or a per-Bob limit (N=1–64), using signed origin and positive dimensions. Half-open region [X,X+W) × [Y,Y+H). Returns 1/0.

**Parameters :**
- `N` — 0 for global limit; 1–64 for per-Bob limit.
- `X` — limit rectangle X origin.
- `Y` — limit rectangle Y origin.
- `W` — positive width of limit rectangle.
- `H` — positive height of limit rectangle.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Limit rectangle: `[X,X+W) × [Y,Y+H)`; N=0 global, N=1..64 individual.

**Sample call :**
```amos
_OK=Aga Limit Bob(0,0,0,320,256)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 075. Aga Del Bob {#cmd-075}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Del Bob(Bank,First,Last)
```

**Purpose and behaviour —** Deletes AGBO images with IDs from First through Last inclusive. Remaining IDs stay stable; editing is disallowed during an engaged frame. Returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `First` — first image ID to delete, inclusive.
- `Last` — last image ID to delete, inclusive.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Del Bob(24,2,4)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 076. Aga Ins Bob {#cmd-076}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Ins Bob(Bank,Image,W,H,Depth)
```

**Purpose and behaviour —** Inserts a transparent AGBO image slot at an available image ID, with dimensions W/H and depth of 1–8 bitplanes. Returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `Image` — free image ID to create.
- `W` — image width in pixels.
- `H` — image height in pixels.
- `Depth` — image bitplane depth, 1–8.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Ins Bob(24,2,16,16,8)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 077. Aga Bob Col {#cmd-077}

**AMOS form :** Numeric function (assign result)

```amos
_C=Aga Bob Col(_A,_B,_MODE)
```

**Purpose and behaviour —** Tests two distinct active persistent Bobs: mode 0 visible rectangles, mode 1 visible pixel masks. Returns 1 collision, 0 no collision, -1 invalid request.

**Parameters :**
- `_A` — first active persistent Bob ID, 1–64.
- `_B` — distinct second active persistent Bob ID, 1–64.
- `_MODE` — 0 visible rectangle; 1 visible masks.

**Return / effect —** 1 = collision; 0 = none; −1 = rejected.

**Important note —** Mode 0 = visible boxes; 1 = visible pixel masks; unlike `Aga Rect Overlap`.

**Sample call :**
```amos
_C=Aga Bob Col(1,2,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 078. Aga Bob Flip {#cmd-078}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Flip(_N,_MODE)
```

**Purpose and behaviour —** Changes Bob N orientation: 0 normal, 1 horizontal mirror, 2 vertical mirror, 3 both axes. Keeps X/Y anchor; returns 1/0.

**Parameters :**
- `_N` — active persistent Bob, 1–64.
- `_MODE` — 0 normal; 1 horizontal; 2 vertical; 3 H+V.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Mode 0 normal, 1 horizontal, 2 vertical, 3 both; mind the hotspot.

**Sample call :**
```amos
_OK=Aga Bob Flip(1,1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 079. Aga Bob Planes {#cmd-079}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Planes(_N,_MASK)
```

**Purpose and behaviour —** Selects destination planes written by Bob N using an 8-bit mask (0–255). Plane selection differs from the AGBO transparency mask. Returns 1/0.

**Parameters :**
- `_N` — active persistent Bob, 1–64.
- `_MASK` — destination bitplane mask, 0–255.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Bits 0..7 select destination planes; 255 = all planes.

**Sample call :**
```amos
_OK=Aga Bob Planes(1,255)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 080. Aga Bob Auto Update {#cmd-080}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Bob Auto Update(_MODE)
```

**Purpose and behaviour —** Mode 1 updates/prepares Bobs on each Aga Swap; mode 0 restores manual operation. Changing mode requires a clean frame; returns 1/0.

**Parameters :**
- `_MODE` — 0: manual (default); 1: automatic before Swap.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Automatic mode prepares Bobs just before `Aga Swap`; do not blindly issue an extra manual Update.

**Sample call :**
```amos
_OK=Aga Bob Auto Update(1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 081. Aga X Bob {#cmd-081}

**AMOS form :** Numeric function (assign result)

```amos
_X=Aga X Bob(_N)
```

**Purpose and behaviour —** Reads signed X position of active persistent Bob N. Returns -32769 when missing, disabled or unavailable; no drawing side effect.

**Parameters :**
- `_N` — active Bob ID, 1–64.

**Return / effect —** X coordinate; −32769 = unavailable Bob.

**Sample call :**
```amos
_X=Aga X Bob(1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 082. Aga Y Bob {#cmd-082}

**AMOS form :** Numeric function (assign result)

```amos
_Y=Aga Y Bob(_N)
```

**Purpose and behaviour —** Reads signed Y position of active persistent Bob N. Returns -32769 when missing, disabled or unavailable; no drawing side effect.

**Parameters :**
- `_N` — active Bob ID, 1–64.

**Return / effect —** Y coordinate; −32769 = unavailable Bob.

**Sample call :**
```amos
_Y=Aga Y Bob(1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 083. Aga I Bob {#cmd-083}

**AMOS form :** Numeric function (assign result)

```amos
_I=Aga I Bob(_N)
```

**Purpose and behaviour —** Reads image ID (1–4096) of active Bob N. Returns -32769 if missing, OFF or unavailable; no drawing side effect.

**Parameters :**
- `_N` — active Bob ID, 1–64.

**Return / effect —** image ID; −32769 = unavailable Bob.

**Sample call :**
```amos
_I=Aga I Bob(1)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

## Chunky-to-planar (C2P)

The C2P group needs `LIBS:c2p.library` in addition to this extension, except for standalone IFF-to-chunky decoding.

### 084. Aga Iff To Chunky {#cmd-084}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Iff To Chunky(File$,Bank)
```

**Purpose and behaviour —** Decodes an indexed 320×256 4–8-plane RAW or ByteRun1 IFF/ILBM into an existing DATA/WORK bank of at least 81,920 bytes. Rejects HAM/EHB, dual playfield and masks; returns 1/0.

**Parameters :**
- `File$` — AmigaDOS path to the ILBM image.
- `Bank` — live AMOS bank number unless pointer form is specified.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Indexed ILBM decoder: 320×256, 4–8 bitplanes, RAW/ByteRun1; standalone call needs no `c2p.library`.

**Sample call :**
```amos
_OK=Aga Iff To Chunky(_FILE$,10)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 085. Aga C2P Open {#cmd-085}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga C2P Open(Bank)
```

**Purpose and behaviour —** Binds a chunky DATA/WORK bank ≥81,920 bytes and allocates the C2P context/Chip bitmap. Requires c2p.library in LIBS:, a private 320×256 screen and double buffer. A second Open fails; returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Requires `LIBS:c2p.library`, a chunky DATA/WORK bank of at least 81,920 bytes, compatible screen and double buffering.

**Sample call :**
```amos
_OK=Aga C2P Open(10)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 086. Aga C2P Blit {#cmd-086}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga C2P Blit(SrcBank,SrcPitch,SrcX,SrcY,W,H,DstX,DstY)
```

**Purpose and behaviour —** Copies an opaque 8-bit chunky rectangle from a source bank into the active C2P chunky bank. SrcPitch is a stride in bytes. Returns 1/0, without presentation.

**Parameters :**
- `SrcBank` — source bank number.
- `SrcPitch` — actual byte pitch between source rows.
- `SrcX` — pixel coordinate (source/destination per its name).
- `SrcY` — pixel coordinate (source/destination per its name).
- `W` — pixel size according to parameter role.
- `H` — pixel size according to parameter role.
- `DstX` — pixel coordinate (source/destination per its name).
- `DstY` — pixel coordinate (source/destination per its name).

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga C2P Blit(11,320,0,0,32,32,64,64)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 087. Aga C2P Zoom {#cmd-087}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga C2P Zoom(SrcBank,SrcPitch,SrcX,SrcY,SrcW,SrcH,DstX,DstY,DstW,DstH)
```

**Purpose and behaviour —** Scales an 8-bit chunky rectangle into the C2P context using nearest-neighbour sampling, with explicit source and destination dimensions. Returns 1/0.

**Parameters :**
- `SrcBank` — source bank number.
- `SrcPitch` — actual byte pitch between source rows.
- `SrcX` — pixel coordinate (source/destination per its name).
- `SrcY` — pixel coordinate (source/destination per its name).
- `SrcW` — pixel size according to parameter role.
- `SrcH` — pixel size according to parameter role.
- `DstX` — pixel coordinate (source/destination per its name).
- `DstY` — pixel coordinate (source/destination per its name).
- `DstW` — pixel size according to parameter role.
- `DstH` — pixel size according to parameter role.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga C2P Zoom(11,320,0,0,32,32,64,64,64,64)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 088. Aga C2P Convert {#cmd-088}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga C2P Convert
```

**Purpose and behaviour —** Converts the bound chunky bank to planar via c2p.library and copies into the Safe back buffer. Does not change palette or display; explicit Aga Swap is needed; returns 1/0.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Conversion does not call `Aga Swap`; palette management is separate.

**Sample call :**
```amos
_OK=Aga C2P Convert
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 089. Aga C2P Close {#cmd-089}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga C2P Close
```

**Purpose and behaviour —** Releases the C2P context and its Chip bitmap after Blitter synchronization. Returns 1 if a context was closed, 0 if none existed (including a second Close).

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga C2P Close
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

## Diagnostics and full-buffer filling

Some commands are diagnostics; their presence among the 100 tokens does not make them a stable game-programming API.

### 090. Aga Probe {#cmd-090}

**AMOS form :** Statement (no assignment)

```amos
Aga Probe
```

**Purpose and behaviour —** Internal diagnostic statement without arguments, not designed as a game API. Do not build application logic on it.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Probe
```

### 091. Aga Demo {#cmd-091}

**AMOS form :** Numeric function (assign result)

```amos
_D=Aga Demo
```

**Purpose and behaviour —** Internal diagnostic function whose return contract is not stable for games. Use only for designated tests.

**Return / effect —** diagnostic: no stable result value guaranteed.

**Sample call :**
```amos
_D=Aga Demo
```

### 092. Aga Screen Pattern {#cmd-092}

**AMOS form :** Statement (no assignment)

```amos
Aga Screen Pattern
```

**Purpose and behaviour —** Draws a diagnostic pattern on the open AGA screen. Statement without a return value, useful for visual display checks.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Screen Pattern
```

### 093. Aga Back Fill {#cmd-093}

**AMOS form :** Statement (no assignment)

```amos
Aga Back Fill couleur
```

**Purpose and behaviour —** Fills the entire back buffer with a palette index (for example 255 in eight-plane mode). Statement without a return value.

**Parameters :**
- `couleur` — colour index written to the entire back buffer.

**Return / effect —** Statement with no result; do not assign it to a variable.

**Sample call :**
```amos
Aga Back Fill 0
```

## Low-level pointer forms

These calls expect a valid bank pointer from `Start(bank)`; check bank existence with `Length(bank)` before calling `Start`.

### 094. Aga Palette Bank Init {#cmd-094}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Palette Bank Init(Start(_B),_N)
```

**Purpose and behaviour —** Low-level AGAPAL form: Start address of an already reserved DATA bank of exact size 16+776×N (N=1–256). Returns 1/0; check bank existence before Start.

**Parameters :**
- `Start(_B)` — existing DATA bank address (`Start`), never requested from a missing bank.
- `_N` — object ID or count as defined by the command.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Palette Bank Init(Start(10),2)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 095. Aga Palette Bank Capture {#cmd-095}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Palette Bank Capture(Start(_B),_INDEX)
```

**Purpose and behaviour —** Low-level pointer form: captures ColorMap into a zero-based AGAPAL slot of an allocated bank. Returns 1/0.

**Parameters :**
- `Start(_B)` — existing DATA bank address (`Start`), never requested from a missing bank.
- `_INDEX` — zero-based slot index.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Palette Bank Capture(Start(10),0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 096. Aga Palette Bank Apply {#cmd-096}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Palette Bank Apply(Start(_B),_INDEX)
```

**Purpose and behaviour —** Low-level pointer form: applies a populated AGAPAL slot to the private palette. Does not write pixels; returns 1/0.

**Parameters :**
- `Start(_B)` — existing DATA bank address (`Start`), never requested from a missing bank.
- `_INDEX` — zero-based slot index.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Palette Bank Apply(Start(10),0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 097. Aga Fade To Bank {#cmd-097}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Fade To Bank(Start(_B),_INDEX,_VBL)
```

**Purpose and behaviour —** Blocking fade to an AGAPAL slot referenced by Start(_B), lasting 1–255 VBL with exact final colours. Returns 1/0.

**Parameters :**
- `Start(_B)` — existing DATA bank address (`Start`), never requested from a missing bank.
- `_INDEX` — zero-based slot index.
- `_VBL` — blocking duration of 1–255 VBL.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Fade To Bank(Start(10),0,32)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 098. Aga Image Draw {#cmd-098}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Image Draw(Start(_B),Length(_B),_X,_Y,_MODE)
```

**Purpose and behaviour —** Low-level pointer-and-length form for an AGAPIC v1/RLE image in a live DATA bank. Draws into the back buffer; returns 1/0.

**Parameters :**
- `Start(_B)` — existing DATA bank address (`Start`), never requested from a missing bank.
- `Length(_B)` — byte length of the existing bank.
- `_X` — pixel coordinate (source/destination per its name).
- `_Y` — pixel coordinate (source/destination per its name).
- `_MODE` — command-specific mode.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Sample call :**
```amos
_OK=Aga Image Draw(Start(10),Length(10),32,32,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

### 099. Aga Image Capture {#cmd-099}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Image Capture(Bank,X,Y,Width,Height,TransparentIndex)
```

**Purpose and behaviour —** Creates a free AGAPIC v1 bank by capturing a wholly contained back-buffer rectangle with a transparency index. Returns 1/0.

**Parameters :**
- `Bank` — live AMOS bank number unless pointer form is specified.
- `X` — pixel coordinate (source/destination per its name).
- `Y` — pixel coordinate (source/destination per its name).
- `Width` — positive pixel width.
- `Height` — positive pixel height.
- `TransparentIndex` — integer or address according to the description below.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Capture produces AGAPIC v1; use the bank-number versioned variant to request v2.

**Sample call :**
```amos
_OK=Aga Image Capture(10,0,0,32,32,0)
```
*Isolated fragment: create the required screen/bank and check status before continuing.*

### 100. Aga Font Bank Select {#cmd-100}

**AMOS form :** Numeric function (assign result)

```amos
_OK=Aga Font Bank Select(_START,_LENGTH)
```

**Purpose and behaviour —** Low-level AMCAF BankFont selection by address and length of an existing bank (Start/Length). Returns 1/0; does not automatically require the AMCAF extension itself.

**Parameters :**
- `_START` — pointer to a live AMOS bank.
- `_LENGTH` — bank length in bytes.

**Return / effect —** Numeric function. For status commands, `1` indicates success and `0` a failed/rejected call; use the description for data getters and special cases.

**Important note —** Check `Length(_B)` on the target bank before `Start(_B)` to avoid Bank not reserved.

**Sample call :**
```amos
_OK=Aga Font Bank Select(Start(10),Length(10))
```
*Isolated fragment: create the required screen/bank and check status before continuing.*
[Public contract and further details](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md).

# Examples and usage patterns

## Example A — safe screen open and close
Complete source adapted from `examples/screen.asc`, omitting its opening comments. No external image needed. `Aga Screen Pattern` is deliberately diagnostic.
```amos
Cls
Print "AGA SCREEN - 320 X 256"
If Aga Detect=0
   Print "AGA CHIPSET NOT DETECTED"
   End
End If
_OK=Aga Screen Open(320,256,256,$00021000)
If _OK<>1
   Print "SCREEN OPEN FAILED"
   End
End If
Aga Screen Pattern
Amos To Back
For _I=1 To 150
   Aga Wait Vbl
Next _I
Aga Screen Close
Amos To Front
Print "SCREEN CLOSED - BACK IN AMOS"
End
```
[Original source](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples/screen.asc).

## Example B — IFF, Blitter and return checking
Complete program taken from `examples/blitter.asc`. Choose a compatible **320×256×8-plane** ILBM such as `examples/demo.iff`; the path **must be visible in AmigaOS**. This listing was not rerun for this manual.
```amos
Cls
Print "AGA BLITTER - SELECT demo.iff"
_FILE$=Fsel$("**")
If _FILE$=""
   Print "CANCELLED"
   End
End If
_W=Aga Pic Info(_FILE$,0)
_H=Aga Pic Info(_FILE$,1)
_D=Aga Pic Info(_FILE$,2)
_C=Aga Pic Info(_FILE$,7)
_MODE=Aga Pic Info(_FILE$,6)
If _W<>320 or _H<>256 or _D<>8 or _C<>256
   Print "PLEASE SELECT A 320X256X8 IFF"
   End
End If
_OPEN=Aga Screen Open(_W,_H,_C,_MODE)
If _OPEN<>1
   Print "SCREEN OPEN FAILED"
   End
End If
_DB=Aga Double Buffer
If _DB<>1
   Aga Screen Close
   Amos To Front
   Print "DOUBLE BUFFER FAILED"
   End
End If
_LOAD=Aga Iff Load(_FILE$)
If _LOAD<>1
   Aga Screen Close
   Amos To Front
   Print "IFF LOAD FAILED"
   End
End If
_F=Aga Blit Fill(16,24,104,68,63)
_C=Aga Blit Clear(32,40,72,36)
_B=Aga Blit Copy(16,24,152,24,104,68)
If _F<>1 or _C<>1 or _B<>1
   Aga Screen Close
   Amos To Front
   Print "BLITTER ERROR ";_F;" ";_C;" ";_B
   End
End If
_SW=Aga Swap
If _SW<>1
   Aga Screen Close
   Amos To Front
   Print "SWAP FAILED"
   End
End If
Amos To Back
_K=Aga Wait Key
Aga Screen Close
Amos To Front
Print "FILL ";_F;" CLEAR ";_C;" COPY ";_B
Print "BLITTER CLOSED - KEY ";_K
End
```
[Original source](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples/blitter.asc).

## Example C — Copper raster effect (fragment)
Once the screen and double buffering are successfully open, these calls build the colour raster. This **fragment is not standalone**: error exits and screen closure belong to its caller.
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

## Recommended render lifecycle
```text
Detect AGA -> Open -> Double Buffer
  -> create/load resources -> wait for a Safe back buffer
  -> draw complete frame -> check results
  -> Swap (bounded VBL retry on refusal)
  -> release resources -> Screen Close -> Amos To Front
```

## Manual versus automatic Bobs
**Manual mode:** `Aga Bob Bank` selects an image bank, `Get AGA Bob` captures images and `Aga Bob` registers persistent objects. The loop invokes `Aga Bob Clear`, `Aga Bob Update`/`Aga Bob Draw`, then `Aga Swap` as required, checking Safe state. **P2d automatic mode:** enable `Aga Bob Auto Update(1)` on a CLEAN page; preparation occurs before Swap. Do not call another manual Update during retry of a rejected `Swap`.
**Validated B/C reference:** use `examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc` unchanged; it uses banks 24, 27 and 28 (ensure they are free before importing) and employs native AMAL channels alongside AGA commands. The original logs are retained in the repository.
[Complete Bob example](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc).

# Appendices and verification

## Aga Pic Info field index
| Field | Returned value |
|---:|---|
| 0 | Width |
| 1 | Height |
| 2 | Bitplane count |
| 3 | CMAP colour count |
| 4 | Compression (0 RAW; 1 ByteRun1) |
| 5 | Original CAMG |
| 6 | Display ModeID suitable for Open |
| 7 | Screen colour count for Open |

## Confusing return values and errors
| Case | Convention |
|---|---|
| `Aga Detect` | nonzero = present; `−1` can represent true on WinUAE |
| `Aga Screen Open` / `Aga Double Buffer` | `1` = success; `0` = failure |
| `Aga Palette Get` | `$00RRGGBB` = valid value; `−1` = error |
| `Aga Pic Info` | `−1` = error; field indices `0..7` |
| `Aga Mouse Buttons` | `1/2/4`: left/right/middle; `−1` invalid |
| `Aga Bob Col` | `1` collision, `0` none, `−1` rejected |
| `Aga X/Y/I Bob` | `−32769` = invalid/unavailable Bob |
| `Aga Swap` | return `0` possible when not ready; bounded and checked VBL retry |

## Pre-release checklist for an AMOS program
- Identify the exact installed binary, AMOS slot and SHA256; a program title does not prove which binary was loaded.
- Check dependencies: `LIBS:c2p.library`, available banks and sizes, IFF/ABK visible to AmigaOS, and sufficient Chip RAM.
- Check rectangle boundaries, transparency masks and colour indices; check returns after drawing and Swap.
- Record WinUAE Runtime and actual AMOS Compiler results separately; do not claim Gate C based on a simulation.
- Check `Aga Screen Close`, return to `Amos To Front`, Ctrl+C, repeat runs for leaks, and document remaining untested cases.

## Sources and references
- [README API FR](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md)
- [README API EN](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md)
- [EXTENSION_SOURCE_RULES](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/EXTENSION_SOURCE_RULES.md)
- [INSTALL FR](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/INSTALL.fr.md)
- [INSTALL EN](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/INSTALL.md)
- [Bob P2d promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/docs/M19_P2D_LAST_GOOD_PROMOTION_2026-11-21.md)
- [Bob P2 integrated tests](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/docs/M19_P2_ALL_IN_ONE_2026-11-21.md)
- [AMOS examples](https://github.com/anthea176/AMOSPro-AGA-Extension/tree/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples)
- [Original AMOS Pro manual](https://amospromanual.dev/)

---

**Method note:** syntax and signatures cross-checked against both public READMEs at a pinned commit. Short examples illustrate calls but were **not independently run under AMOS**. This documentation makes no repository or source-code changes.
