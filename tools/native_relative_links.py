"""Fail-closed relocation of audited PC-relative branches in AP20 V2 native code.

A V2 monolith only protects the Compiler from *separate* routine relocation.
It does not update BRA.W/BSR.W when an earlier native entry grows.  R70
grew entry 55 by 222 bytes and left three dependent edges dangling.

All offsets below are source-audited *instruction* offsets (not byte scans).
If a future emitter moves one of these sites or targets, fail closed and
update this explicit manifest after a source/disassembly audit.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from
from typing import Sequence


@dataclass(frozen=True)
class NativeLink:
    name: str
    source_entry: int
    source_offset: int
    opcode: int
    target_entry: int
    target_offset: int = 0


# Source-backed locations: R57 Fill dispatch, R54 bank wrappers, R56/R57
# in-entry helper.  The helper is within entry 58 at offset 110, following
# the bank-font wrapper.  Each destination begins with MOVEM.L saves.
LINKS = (
    NativeLink("Fill -> RasterPort helper", 20, 0, 0x6000, 58, 110),
    NativeLink("Bank Image Draw -> Image Draw", 57, 122, 0x6100, 55),
    NativeLink("Bank Font Select -> Font Bank Select", 58, 80, 0x6100, 49),
)
PROLOGUE = bytes.fromhex("48e7efee")


def native_starts(parts: Sequence[bytes]) -> list[int]:
    if len(parts) != 70 or any(len(p) & 1 for p in parts):
        raise AssertionError("Expected 70 aligned native AP20 entries")
    starts: list[int] = []
    offset = 0
    for part in parts:
        starts.append(offset)
        offset += len(part)
    if offset >= 65534:
        raise AssertionError("Native monolith exceeds Compiler V2 capacity")
    return starts


def link_positions(parts: Sequence[bytes], link: NativeLink) -> tuple[int, int, int]:
    """Return (actual PC-relative target, expected target, displacement)."""
    starts = native_starts(parts)
    src = parts[link.source_entry]
    at = link.source_offset
    if at < 0 or at + 4 > len(src) or unpack_from(">H", src, at)[0] != link.opcode:
        raise AssertionError(f"{link.name}: missing expected BRA.W/BSR.W instruction")
    target = parts[link.target_entry]
    if target[link.target_offset:link.target_offset + 4] != PROLOGUE:
        raise AssertionError(f"{link.name}: target prologue moved or changed")
    disp = unpack_from(">h", src, at + 2)[0]
    origin = starts[link.source_entry] + at + 2  # extension-word PC, not +4
    return origin + disp, starts[link.target_entry] + link.target_offset, disp


def assert_native_links(parts: Sequence[bytes]) -> None:
    """Gate A: reject any branch landing inside a callee or beyond its start."""
    for link in LINKS:
        actual, expected, disp = link_positions(parts, link)
        if actual != expected:
            raise AssertionError(
                f"{link.name}: destination {actual} != {expected} "
                f"(displacement {disp:+d}); unsafe AP20 native relocation"
            )


def relink_native_parts(parts: Sequence[bytes]) -> list[bytes]:
    """Recompute only declared PC-relative displacements after layout changes.

    Safe to rerun (idempotent); refuses changed opcodes, targets, or out-of-range
    branches rather than searching for coincidental 0x6000/0x6100 data words.
    """
    source = list(parts)
    result = list(source)
    for link in LINKS:
        _actual, expected, _old_disp = link_positions(source, link)
        starts = native_starts(source)
        origin = starts[link.source_entry] + link.source_offset + 2
        displacement = expected - origin
        if not -32768 <= displacement <= 32767:
            raise AssertionError(f"{link.name}: Bxx.W displacement out of range")
        patched = bytearray(result[link.source_entry])
        pack_into(">h", patched, link.source_offset + 2, displacement)
        result[link.source_entry] = bytes(patched)
    assert_native_links(result)
    if any(len(a) != len(b) for a, b in zip(source, result)):
        raise AssertionError("Relocation changed native entry length")
    return result
