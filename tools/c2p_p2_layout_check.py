#!/usr/bin/env python3
"""Read-only C2P P2 checker for a real AMOSPro AGA ScreenBuffer snapshot.

This script NEVER touches Amiga memory. It validates an observation captured
under WinUAE, not the behavior of the C2P library or of an AMOS executable.
No runtime PASS should be inferred from synthetic unit tests.

Input: JSON with mode and buffers (see docs/C2P_P2_BITMAP_DIAGNOSTIC_2026-11-14.md).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MEMF_CHIP = 0x0002
BMF_INTERLEAVED = 0x0004
DEFAULT_WIDTH = 320
DEFAULT_HEIGHT = 256
DEFAULT_DEPTH = 8


def number(value: Any, field: str) -> int:
    """Parse an unsigned Amiga pointer or scalar; never coerce booleans."""
    if isinstance(value, bool):
        raise ValueError(f"{field}: boolean is not an address/number")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str):
        parsed = int(value, 0)
    else:
        raise ValueError(f"{field}: expected an integer or 0x-prefixed string")
    if parsed < 0 or parsed > 0xFFFFFFFF:
        raise ValueError(f"{field}: outside unsigned 32-bit range")
    return parsed


def check_document(doc: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    inspections: list[dict[str, Any]] = []
    if not isinstance(doc, dict):
        raise ValueError("document must be a JSON object")
    mode = doc.get("mode")
    if not isinstance(mode, dict):
        raise ValueError("mode must contain width, height and depth")
    width = number(mode.get("width"), "mode.width")
    height = number(mode.get("height"), "mode.height")
    depth = number(mode.get("depth"), "mode.depth")
    if (width, height, depth) != (DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_DEPTH):
        errors.append("P2 scope is strictly 320x256x8 (not a general C2P mode validator)")
    bytes_plane_row = width // 8 if width % 8 == 0 else 0
    if width % 32 != 0:
        errors.append("width must be a multiple of 32 pixels")
    bitmap_size = bytes_plane_row * height * depth
    # Optional conservative physical CHIP range established separately from
    # WinUAE's configured Chip size AND its GDB physical RAM map. This is
    # NOT a forged Exec TypeOfMem() return value.
    chip_ranges: list[tuple[int, int]] = []
    for entry in doc.get("chip_ranges", []):
        if not isinstance(entry, dict) or not entry.get("basis"):
            raise ValueError("chip_ranges requires an explicit evidence basis")
        start = number(entry.get("start"), "chip_ranges.start")
        end = number(entry.get("end"), "chip_ranges.end")
        if not start < end:
            raise ValueError("chip_ranges must be nonempty [start,end) intervals")
        chip_ranges.append((start, end))
    buffers = doc.get("buffers")
    if not isinstance(buffers, list) or len(buffers) != 2:
        raise ValueError("buffers must be exactly [SB0, SB1]")

    declared_sbs: set[int] = set()
    declared_bitmaps: set[int] = set()
    regions: list[tuple[int, int, str]] = []
    for index, buffer in enumerate(buffers):
        label = f"SB{index}"
        e: list[str] = []
        if not isinstance(buffer, dict):
            raise ValueError(f"{label}: expected an object")
        if buffer.get("name") != label:
            e.append(f"name must be {label}")
        sb = number(buffer.get("screen_buffer"), f"{label}.screen_buffer")
        bitmap = number(buffer.get("bitmap"), f"{label}.bitmap")
        if not sb or not bitmap or sb % 2 or bitmap % 2:
            e.append("screen_buffer and bitmap must be nonzero even addresses")
        if sb in declared_sbs or bitmap in declared_bitmaps:
            e.append("ScreenBuffer/BitMap pointer is duplicated")
        declared_sbs.add(sb)
        declared_bitmaps.add(bitmap)
        bpr = number(buffer.get("bytes_per_row"), f"{label}.bytes_per_row")
        rows = number(buffer.get("rows"), f"{label}.rows")
        dep = number(buffer.get("depth"), f"{label}.depth")
        flags = number(buffer.get("flags"), f"{label}.flags")
        if rows != height or dep != depth:
            e.append(f"unexpected Rows/Depth: {rows}/{dep}; expected {height}/{depth}")
        interleaved = bool(flags & BMF_INTERLEAVED)
        expected_bpr = bytes_plane_row * (depth if interleaved else 1)
        if bpr != expected_bpr:
            e.append(f"BytesPerRow {bpr} != {expected_bpr} for this geometry/layout")
        planes = buffer.get("planes")
        memfirst = buffer.get("type_of_mem_first")
        memlast = buffer.get("type_of_mem_last")
        if not isinstance(planes, list) or len(planes) != 8:
            raise ValueError(f"{label}: planes must have exactly eight pointers")
        p = [number(v, f"{label}.planes[{i}]") for i, v in enumerate(planes)]
        for i, address in enumerate(p):
            if not address or address % 4:
                e.append(f"Planes[{i}] must be a nonzero 4-byte aligned address")
            offset = i * bytes_plane_row * (1 if interleaved else height)
            expected = p[0] + offset
            if expected > 0xFFFFFFFF or address != expected:
                e.append(f"Planes[{i}]={address:#010x}, expected {expected:#010x}")
        full_end = p[0] + bitmap_size
        if full_end > 0x100000000:
            e.append("plane region overflows 32-bit address space")
        else:
            regions.append((p[0], full_end, label))
        chip_verified = True
        if memfirst is None and memlast is None and chip_ranges:
            # A complete interval check is stricter than just the first/last
            # byte, but depends on the reported WinUAE Chip RAM configuration.
            if not any(start <= p[0] and full_end <= end for start, end in chip_ranges):
                chip_verified = False
                e.append("buffer is not entirely inside a verified Chip RAM range")
        elif not isinstance(memfirst, list) or len(memfirst) != 8 or not isinstance(memlast, list) or len(memlast) != 8:
            chip_verified = False
            e.append("no physical Chip RAM evidence (TypeOfMem or confirmed WinUAE memory map)")
        else:
            for i in range(8):
                a = number(memfirst[i], f"{label}.type_of_mem_first[{i}]")
                b = number(memlast[i], f"{label}.type_of_mem_last[{i}]")
                if not (a & MEMF_CHIP and b & MEMF_CHIP):
                    chip_verified = False
                    e.append(f"plane {i}: first/last address not verified as MEMF_CHIP")
        if interleaved:
            e.append("BMF_INTERLEAVED: SDK has an interleaved mode, but custom-bitmap safety needs separate validation")
        inspections.append({
            "name": label,
            "layout": "interleaved" if interleaved else "contiguous_planar",
            "memory_chip_verified": chip_verified,
            "memory_chip_basis": ("WinUAE configured Chip range and RAM map"
                                  if memfirst is None and chip_ranges else "Exec TypeOfMem"),
            "base": f"0x{p[0]:08X}",
            "bytes_per_row": bpr,
            "rows": rows,
            "depth": dep,
            "errors": e,
            "direct_c2p_candidate": not e,
        })
    if len(regions) == 2:
        (a0, a1, al), (b0, b1, bl) = regions
        if max(a0, b0) < min(a1, b1):
            errors.append(f"{al} and {bl} memory allocations overlap")
    if any(b["errors"] for b in inspections):
        errors.append("at least one ScreenBuffer does not meet strict direct-C2P prerequisites")
    return {
        "scope": "AMOSPro AGA 320x256x8 - P2 only",
        "direct_custom_bitmap_candidate": not errors,
        "buffers": inspections,
        "errors": errors,
        "runtime_qualified": False,
        "note": "Requires observed WinUAE data. Passing this checker is NOT Gate B or proof C2P is safe.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="observed JSON with SB0 and SB1 bitmap fields")
    args = parser.parse_args()
    try:
        report = check_document(json.loads(args.snapshot.read_text(encoding="utf-8")))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"C2P P2 INVALID INPUT: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["direct_custom_bitmap_candidate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
