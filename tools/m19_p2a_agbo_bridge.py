#!/usr/bin/env python3
"""M19 P2a host-only adapter: P1e object/stamp/limit snapshots and AGBO v1.

These inputs are COPIES supplied by a trusted native snapshot mechanism. This
module cannot verify A5 ownership, Bnk.GetAdr, TypeOfMem or live memory; its
stamp comparison only detects inconsistencies within supplied snapshots.
No AP20 tokens, native memory access, DMA, painting or Swap.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import Struct
from typing import Mapping

from m19_p0a_multi_bob_abk import BobBank, BobImage, parse_payload
from m19_p2a_bob_collision_model import Bob, Image, Rect, collision_pairs

# From m19_p0e_object_table_emit.py: 64 slots of 24 bytes, six big-endian LONGs.
# bank(+0), image(+4), signed x(+8), signed y(+12), active(+16), reserved(+20).
OBJECT = Struct(">IIiiII")
OBJECT_COUNT = 64
# From m19_p0f_bank_stamp_emit.py: pointer, generation, Cur_Banks head, size.
STAMP = Struct(">IIII")
# From m19_p1d_limit_bob_emit.py: 65 slots, four signed LONGs each.
LIMIT = Struct(">iiii")
LIMIT_COUNT = 65
assert OBJECT.size == 24 and STAMP.size == 16 and LIMIT.size == 16


@dataclass(frozen=True)
class BankSnapshot:
    """Trusted snapshot of one AMOS DATA bank and its external identity.

    Pointers are compared as opaque host integers, never dereferenced. Equal
    same-address/same-generation ABA reuse cannot be detected by this format.
    """
    payload: bytes
    payload_ptr: int
    bank_list_head: int

    def __post_init__(self) -> None:
        if type(self.payload) is not bytes:
            raise ValueError("bank payload must be immutable bytes")
        for name in ("payload_ptr", "bank_list_head"):
            value = getattr(self, name)
            if type(value) is not int or not 0 < value <= 0xffffffff or value & 1:
                raise ValueError(f"invalid {name}")


def host_image(source: BobImage) -> Image:
    """Translate REAL AGBO 16-bit-aligned planar visibility to host 8-bit rows.

    AGBO has a 16-pixel-rounded stride; the existing collision model uses
    8-pixel-rounded rows. Both are MSB-first. Colour planes are not consulted:
    mask absence makes every pixel opaque, including palette index 0.
    """
    if source.mask is None:
        return Image(source.width, source.height)
    dst_stride = (source.width + 7) // 8
    rows = (source.mask[y * source.stride:y * source.stride + dst_stride]
            for y in range(source.height))
    return Image(source.width, source.height, b"".join(rows))


def decode_objects(table: bytes, stamps: bytes,
                   banks: Mapping[int, BankSnapshot], *, screen_depth: int = 8
                   ) -> tuple[Bob, ...]:
    """Validate a P0e/P0f offline snapshot; fail on stale active bindings.

    Object ID is the 1-based slot index. OFF entries retain old bindings and
    stamps natively; their data are ignored, but their active/reserved fields
    must still be valid. Missing/invalid source image is an error, not an
    invented hit/miss or a silently recycled image after P1e Del Bob.
    """
    if (type(table) is not bytes or len(table) != OBJECT_COUNT * OBJECT.size or
            type(stamps) is not bytes or len(stamps) != OBJECT_COUNT * STAMP.size):
        raise ValueError("expected exact 64 P0e object slots and P0f stamps")
    if type(screen_depth) is not int or not 1 <= screen_depth <= 8:
        raise ValueError("invalid AGA screen depth")
    if not isinstance(banks, Mapping):
        raise ValueError("banks must map numeric AMOS IDs to BankSnapshot")
    parsed: dict[int, BobBank] = {}
    host_images: dict[tuple[int, int], Image] = {}
    result: list[Bob] = []
    for slot in range(OBJECT_COUNT):
        bank_id, image_id, x, y, active, reserved = OBJECT.unpack_from(table, slot * OBJECT.size)
        if reserved != 0 or active not in (0, 1):
            raise ValueError(f"corrupt P0e object slot {slot + 1}")
        if active == 0:
            continue  # Bob Off keeps bank/image/coords/stamp from prior binding.
        if (not 5 <= bank_id <= 65535 or not 1 <= image_id <= 4096 or
                not -32768 <= x <= 32767 or not -32768 <= y <= 32767):
            raise ValueError(f"invalid active P0e object slot {slot + 1}")
        snapshot = banks.get(bank_id)
        if not isinstance(snapshot, BankSnapshot):
            raise ValueError(f"missing validated AGBO snapshot for bank {bank_id}")
        if bank_id not in parsed:
            parsed[bank_id] = parse_payload(snapshot.payload)
        source_bank = parsed[bank_id]
        expected = (snapshot.payload_ptr, source_bank.generation,
                    snapshot.bank_list_head, len(snapshot.payload))
        if STAMP.unpack_from(stamps, slot * STAMP.size) != expected:
            raise ValueError(f"stale P0f stamp for Bob {slot + 1}")
        try:
            source_image = source_bank.image(image_id)
        except KeyError as exc:
            raise ValueError(f"missing AGBO image {image_id} for Bob {slot + 1}") from exc
        if source_image.depth > screen_depth:
            raise ValueError(f"Bob {slot + 1} exceeds screen depth")
        key = (bank_id, image_id)
        if key not in host_images:
            host_images[key] = host_image(source_image)
        result.append(Bob(slot + 1, bank_id, image_id, x, y, host_images[key],
                          source_image.hotspot_x, source_image.hotspot_y))
    return tuple(result)


def decode_limits(table: bytes) -> tuple[Rect | None, dict[int, Rect]]:
    """Decode canonical P1d stored rectangle slots, ends exclusive.

    A zero slot means no limit. Noncanonical zero-area slots are rejected,
    rather than silently assuming a policy that the public API disallows.
    """
    if type(table) is not bytes or len(table) != LIMIT_COUNT * LIMIT.size:
        raise ValueError("expected exactly 65 P1d limit slots")
    local: dict[int, Rect] = {}
    global_limit = None
    for index in range(LIMIT_COUNT):
        left, top, right, bottom = LIMIT.unpack_from(table, index * LIMIT.size)
        if (left, top, right, bottom) == (0, 0, 0, 0):
            continue
        if right <= left or bottom <= top:
            raise ValueError(f"noncanonical P1d limit slot {index}")
        rect = Rect(left, top, right - left, bottom - top)
        if index == 0:
            global_limit = rect
        else:
            local[index] = rect
    return global_limit, local


def collisions_from_snapshots(objects: bytes, stamps: bytes,
                              banks: Mapping[int, BankSnapshot], *,
                              screen: Rect, mode: str = "mask",
                              limits: bytes | None = None,
                              screen_depth: int = 8) -> list[tuple[int, int]]:
    """Pure host query for offline P1e-consistent, identity-checked snapshots."""
    if screen.x != 0 or screen.y != 0 or not 1 <= screen.w <= 4096 or not 1 <= screen.h <= 4096:
        raise ValueError("invalid logical AGA screen")
    bobs = decode_objects(objects, stamps, banks, screen_depth=screen_depth)
    global_limit, local_limits = (decode_limits(limits) if limits is not None else (None, {}))
    return collision_pairs(bobs, screen=screen, mode=mode,
                           global_limit=global_limit, local_limits=local_limits)
