"""R30 AGAPAL v1: reference byte layout, NOT an AMOS extension implementation.

Public design contract: AMOS DATA bank in Fast RAM when available; on
disk, AMOS Save writes its own native 20-byte AmBk header. AGAPAL is the
inner DATA payload, not a standalone alternative ABK format.
R30 initializes empty slots; R31 captures screen colors into one slot.
This is a format model only, not proof of real AMOS/WinUAE behavior.

All offsets are in bytes, big endian, relative to AMOS Start(bank).
The builder is a deterministic model for static tests and review, not proof
of AMOS bank allocation, memory flags or live ABK loading.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack, unpack_from

SIGNATURE = b"AGAPAL"
NAME = b"AGAPAL  "
VERSION = 1
HEADER = 16
INDEX_SIZE = 8
RGB_SIZE = 3 * 256
SLOT_SIZE = INDEX_SIZE + RGB_SIZE
ABK_HEADER = 20

@dataclass(frozen=True)
class AGAPAL:
    palettes: int
    entries: tuple[tuple[int, int, int], ...]
    payload: bytes

def payload_size(count: int) -> int:
    if not isinstance(count, int) or not 1 <= count <= 65535:
        raise ValueError("count must be 1..65535")
    size = HEADER + SLOT_SIZE * count
    if size > 0x7fffffff:
        raise ValueError("bank too large")
    return size

def init_payload(count: int) -> bytes:
    """Initialize N empty (unassigned) 256-entry RGB24 slots."""
    data = bytearray(payload_size(count))
    data[0:6] = SIGNATURE
    data[6:10] = pack(">HH", VERSION, count)
    # Flags (word @+10) and future field (long @+12) remain zero.
    first = HEADER + INDEX_SIZE * count
    for index in range(count):
        index_start = HEADER + index * INDEX_SIZE
        data[index_start:index_start+8] = pack(
            ">IHH", first + RGB_SIZE * index, 0, 0
        )
    return bytes(data)

def parse_payload(raw: bytes) -> AGAPAL:
    if len(raw) < HEADER or raw[:6] != SIGNATURE:
        raise ValueError("missing AGAPAL signature")
    version, count, flags, reserved = unpack_from(">HHHI", raw, 6)
    if version != VERSION or flags or reserved:
        raise ValueError("unsupported version/flags/reserved")
    if len(raw) != payload_size(count):
        raise ValueError("invalid bank length")
    slots = []
    first = HEADER + INDEX_SIZE * count
    for index in range(count):
        off, colors, entry_flags = unpack_from(">IHH", raw, HEADER + index * INDEX_SIZE)
        if off != first + RGB_SIZE * index:
            raise ValueError("invalid palette offset")
        if colors > 256 or entry_flags:
            raise ValueError("invalid palette descriptor")
        slots.append((off, colors, entry_flags))
    return AGAPAL(count, tuple(slots), bytes(raw))

def abk_model(bank_no: int, payload: bytes, chip: bool = False) -> bytes:
    """Reference external AmBk envelope ONLY, not an AMOS Save replacement."""
    if not isinstance(bank_no, int) or not 5 <= bank_no <= 65535:
        raise ValueError("bank number must be 5..65535")
    parse_payload(payload)
    # Standard AMOS DATA flag #0; bit #1 is CHIP. FAST DATA=1, CHIP DATA=3.
    return pack(">4sHHI8s", b"AmBk", bank_no, 3 if chip else 1,
                len(payload) + 8, NAME) + payload

def parse_abk(raw: bytes) -> tuple[int, int, AGAPAL]:
    if len(raw) < ABK_HEADER:
        raise ValueError("short ABK")
    magic, bank_no, flags, size_field, name = unpack_from(">4sHHI8s", raw, 0)
    if magic != b"AmBk" or bank_no < 5 or flags not in (1,3) or name != NAME:
        raise ValueError("invalid ABK header/type/name")
    if size_field != len(raw) - 12:
        raise ValueError("invalid ABK size field")
    return bank_no, flags, parse_payload(raw[ABK_HEADER:])
