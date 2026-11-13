# CBlock Chip Lab — R68 v0.13.13

[Français](README.fr.md) · [All examples](../README.md) · [Technical contract](../../docs/M18_CBLOCK_DESIGN.md)

A small, **self-contained AMOS interpreted-mode example** for temporary **Chip RAM RAW planar background saves** using `Aga C Block Capture`, `Draw`, and `Restore`. **No image, IFF, ABK, palette file or AMCAF dependency**.

**Source:** [CBLOCK_CHIP_LAB.asc](CBLOCK_CHIP_LAB.asc). Requires [current R68 candidate](../../dist/AMOSPro_AGA.Lib) v0.13.13 (or compatible later version). The **API passed native Gate A and WinUAE interpreted Gate B** on separate archived tests ([Gate B](../../docs/M18_R68_CBLOCK_WINUAE_GATE_B_2026-11-13.md), [6-size PERF-02](../../docs/M18_R68_CBLOCK_PERF_02_WINUAE_2026-11-13.md)). **This new shorter public example has not been independently run in WinUAE**; do not claim it is a passed runtime regression or a Compiler Gate C result.

## Method is the programmer's choice — no automatic selection

| Value | Path | Horizontal alignment |
|---:|---|---|
| `0` | CPU8, one byte of each bitplane | X and Width multiples of **8 pixels** |
| `1` | CPU16, one word of each bitplane | X and Width multiples of **16 pixels** |
| `2` | Amiga Blitter, Chip-to-Chip DMA | X and Width multiples of **8 pixels** |

The `Method` parameter is mandatory for **every call**, including `Restore`. The extension does **not** benchmark, autodetect the CPU or override the chosen method. Unaligned coordinates, invalid bank/dimensions or a rectangle extending beyond the private AGA screen return `0`, without clipping. On the confirmed JIT-OFF benchmarks, performance differs by CPU and size; **no single winner** is enforced.

## Run

1. Ensure **AMOS bank 11 is FREE**. This demo creates one temporary `AGACBLK ` DATA bank in *physical Chip RAM* and releases it with `Erase 11` after closing the AGA screen. Do not use it in a program that already owns bank 11.
2. Install the current `dist/AMOSPro_AGA.Lib` as `AMOSPro_AGA.Lib` in `APSystem` with the **same extension slot**; restart AMOS.
3. In AMOS, open a **new empty program → Project → Merge ASCII** → `CBLOCK_CHIP_LAB.asc`. Run **interpreted only**. The actual AMOS Compiler Gate C is reserved for the **end of M18**.
4. The 320×256×256-colour AGA screen shows one **white square with a black centre** near the top, then three identical copies on a dark blue background: **CPU8 at X8**, **Blitter at X96**, **CPU16 at X176** (Y144). It remains visible for ~180 PAL VBL; then closes.
5. On the AMOS console, expect `DRAW CPU8/BLIT/CPU16 1 1 1`, `RECAP/SAME 1 1`, `BANK LEN 1064`, equal Chip Free before/after, `ERROR 0`, `RESULT 1` and `CLOSE RETURNED`. Those values are **expected**, not claimed observed for this new example.

## Key operations

```amos
_CAPMODE=2
_OK=Aga C Block Capture(11,16,48,32,32,_CAPMODE)

' Restore the saved original background at its capture coordinates:
_RESTMODE=1
_OK=Aga C Block Restore(11,_RESTMODE)

' Draw at three different destinations using the same Chip bank:
_OK=Aga C Block Draw(11,8,144,0)
_OK=Aga C Block Draw(11,96,144,2)
_OK=Aga C Block Draw(11,176,144,1)

' Recapture in place, without reallocation:
_OK=Aga C Block Capture(11,16,48,32,32,0)
Erase 11
```

This is a simplified excerpt: first open the private AGA screen, double buffer, wait for the inactive buffer to be Safe, then draw; synchronize, close the AGA screen and release the temporary bank. The full ASC implements that order. **Bit 0 of palette index 0 is not a transparency mask: restoration is opaque**.

The source is under [MIT](../../LICENSE). No external graphics assets are bundled.
