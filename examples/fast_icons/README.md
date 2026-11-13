# Fast Icon Lab — AMOSPro AGA visual showcase

[Français](README.fr.md) | [All examples](../README.md) | [Fast Icon contract](../../docs/M18_FICON8_CAPTURE_DESIGN.md)

A **self-contained interactive demonstration** of the full `Aga F` workflow: generate 8-bit indexed pixels, create AMOS banks, fill `FICON8` slots, convert them into a Chip RAM `FICHIP8` cache, explicitly re-stage a modified icon, capture an icon from the screen and render through both CPU and Blitter.

**Source:** [FAST_ICON_LAB.asc](FAST_ICON_LAB.asc). **Requires the Fast Icon commands introduced in R67 (available in the currently promoted R68 v0.13.13 LAST_GOOD).** The R67 API passed its own native and interpreted WinUAE regressions; **the author confirmed this showcase in interpreted WinUAE on 13 November 2026** (without a separate screenshot or console readout). R68 has now passed its integrated Compiler Gate C, but **this specific showcase has not been separately compiled**.

## What to expect on screen

The display is **320×256, 256 indexed colours, PAL LowRes**. It has a dark-blue interface, five rows of 16×16 icons, four rendering modes, alternating panels, and a small moving accent in the header.

| Column | Function | Index zero |
|---|---|---|
| **CPU T** (X109) | `Aga F Icon(12,ID,X,Y,1)` | Masked: row background remains visible |
| **CPU O** (X164) | `Aga F Icon(12,ID,X,Y,0)` | Opaque: index zero draws black |
| **BLIT T** (X219) | `Aga F Blit(11,ID,X,Y,1)` | Masked, from real Chip RAM |
| **BLIT O** (X274) | `Aga F Blit(11,ID,X,Y,0)` | Opaque, using the Blitter |

Five rows: **CROSS** (red/green X with white border), **GEM** (recoloured and re-staged gemstone), **ELIXIR** (potion), **SPARK** (star) and **CAPTURE** (snapshot of GEM captured directly from the back buffer at **unaligned X31,Y45**). CROSS uses pen **255**, exercising all eight planes.

GEM and CAPTURE should be visually identical. All four drawing modes preserve the same coloured shapes, with only the index-zero interior turning black in opaque mode.

## Setup

1. Install [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) in the normal APSystem extension location, **without touching `LAST_GOOD`**; restart AMOS Professional.
2. Ensure **bank numbers 11, 12 and 13 are free**. This demo creates source `FICON8` bank 12 (8 slots), Chip cache `FICHIP8` bank 11 (8 slots), and a 256-byte chunky DATA bank 13. Native Reserve As Data 13,256 **can overwrite bank 13**; start from a clean, disposable AMOS session.
3. Open a **new empty AMOS program** and use **Project → Merge ASCII** to import [FAST_ICON_LAB.asc](FAST_ICON_LAB.asc). Do not use the ordinary AMOS program Load command for an ASCII source file.
4. Run **interpreted only**. Press any key or click to exit. The loop has a **1,200-frame upper bound**; `Safe`/`Swap` failures have bounded retry loops.
5. Upon return to AMOS, expect `ERROR 0`, `RESULT 1`, then `CLOSE RETURNED`. Chip/Fast free-memory counters are informative, **not** timing results.

**No external assets and no file I/O**: no IFF, ABK, separate font bank or AMCAF dependency. All pixel patterns are produced by `Poke` in memory.

## Full Fast Icon pipeline

```amos
_OK=Aga F Icon Bank Create(12,8)    ' Source: FICON8
_OK=Aga F Chip Bank Create(11,8)    ' Real Chip RAM FICHIP8 cache
Reserve As Data 13,256              ' Fill with Poke: 16x16 chunky pixels

_OK=Aga F Icon Bank Put(12,1,13,0)  ' Convert selected source slot
_OK=Aga F Chip Stage(12,11,1)       ' Prepare Blitter-friendly cache slot

_OK=Aga F Icon(12,1,31,45,0)        ' Opaque draw into the AGA back buffer
_OK=Aga F Icon Capture(12,5,31,45)  ' Capture 16x16 to FICON8 slot 5
_OK=Aga F Chip Stage(12,11,5)       ' EXPLICIT restaging of captured slot

_OK=Aga F Icon(12,5,109,90,1)       ' CPU masked draw
_OK=Aga F Blit(11,5,219,90,1)       ' Blitter masked draw
```

This snippet is **illustrative**: actual row Y coordinates are calculated by the full program and the AGA private screen must be opened before drawing. Moving `FICON8` into Chip RAM is not sufficient: `FICHIP8` uses a different Blitter-oriented storage format.

The demo checks that the captured icon's **288 bytes** exactly match the GEM source slot (mask plus eight planes). **Changing `FICON8` does not automatically update a staged `FICHIP8` slot**; invoke `Aga F Chip Stage` again after a Put or Capture.

## Results and limits

- Expect BANK PUT 4 / 4, INITIAL CHIP STAGES 4 / 4, GEM REPUT / RESTAGE 1 1, CAPTURE X31 / EQ288 / STAGE 1 1 1.
- `ERROR 0` and `RESULT 1` mean the code's own checks passed in that execution. **The author confirmed the showcase works in interpreted WinUAE**, without screenshot or numerical log. This showcase has not been tested under AMOS Compiler independently; R68's separate integrated Compiler Gate C is already PASS.
- No CPU-vs-Blitter benchmark is attempted. Frame rate depends on CPU/Chip RAM and WinUAE settings.
- No ABK Save/Load is performed in this zero-file demo; see the [R67 validation record](../../docs/M18_R67_FICON8_CAPTURE_WINUAE_GATE_B_2026-11-13.md) for the separate populated-bank persistence test.
- Example source and generated patterns are original, under [MIT](../../LICENSE). No external artwork to redistribute.
