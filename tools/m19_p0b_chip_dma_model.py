#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0: HOST-ONLY AGBO -> DMA layout reference. Not Chip allocation or AP20.

The output is ordinary host bytes, NEVER a DMA pointer. A future native
implementation must allocate real MEMF_CHIP, verify every complete source and
mask range with TypeOfMem, respect Safe/Blitter completion and invalidate all
consumers before freeing memory. Nothing here edits the AMOS DATA bank.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from m19_p0a_multi_bob_abk import parse_payload

MAX_STAGE = 16 * 1024 * 1024


@dataclass(frozen=True)
class ImageSpan:
    image_id: int
    width: int
    height: int
    depth: int
    stride: int
    plane_size: int
    pixel_offset: int
    pixel_length: int
    mask_offset: int | None
    mask_length: int
    hotspot_x: int
    hotspot_y: int

    def dma_ranges(self) -> tuple[tuple[int, int], ...]:
        planes = tuple((self.pixel_offset + n * self.plane_size, self.plane_size)
                       for n in range(self.depth))
        return planes + (((self.mask_offset, self.mask_length),)
                         if self.mask_offset is not None else ())


@dataclass(frozen=True)
class Stage:
    bank_number: int
    bank_identity: int
    payload_sha256: str
    payload_size: int
    generation: int
    data: bytes
    images: tuple[ImageSpan, ...]

    def is_current(self, identity: int, payload: bytes) -> bool:
        return (identity == self.bank_identity and len(payload) == self.payload_size
                and sha256(payload).hexdigest() == self.payload_sha256)

    def validate(self) -> None:
        cursor = 0
        for img in self.images:
            if img.pixel_offset != cursor or (cursor & 1):
                raise ValueError("noncontiguous/unaligned colour data")
            if img.stride != 2 * ((img.width + 15) // 16):
                raise ValueError("unexpected planar stride")
            if img.plane_size != img.stride * img.height:
                raise ValueError("incorrect plane size")
            if img.pixel_length != img.plane_size * img.depth:
                raise ValueError("incorrect total pixel length")
            for begin, count in img.dma_ranges():
                if (begin < 0 or count <= 0 or (begin & 1) or (count & 1)
                        or count > len(self.data) or begin > len(self.data) - count):
                    raise ValueError("DMA range outside aligned staged allocation")
            cursor += img.pixel_length
            if img.mask_offset is not None:
                if img.mask_offset != cursor or img.mask_length != img.plane_size:
                    raise ValueError("incorrect independent mask")
                cursor += img.mask_length
            elif img.mask_length != 0:
                raise ValueError("maskless image claims mask bytes")
        if cursor != len(self.data) or cursor > MAX_STAGE:
            raise ValueError("unreferenced bytes or stage too large")


def stage_agbo(bank_number: int, identity: int, payload: bytes,
               *, budget: int = MAX_STAGE) -> Stage:
    """Validate whole AGBO first; build private planar copy or reject atomically.

    budget simulates an available-byte limit for HOST tests only. It does not
    represent real free Chip RAM and the returned bytes are NOT in Chip.
    """
    if type(bank_number) is not int or not 5 <= bank_number <= 65535:
        raise ValueError("invalid bank")
    if type(identity) is not int or identity <= 0 or identity & 1:
        raise ValueError("invalid bank identity")
    if type(budget) is not int or not 0 <= budget <= MAX_STAGE:
        raise ValueError("invalid synthetic budget")
    parsed = parse_payload(payload)
    out = bytearray()
    entries = []
    for img in parsed.images:
        plane_size = img.stride * img.height
        pixel_length = len(img.planes)
        mask_length = len(img.mask) if img.mask is not None else 0
        needed = pixel_length + mask_length
        if needed > budget - len(out):
            raise MemoryError("insufficient synthetic staging budget")
        pixel_offset = len(out)
        out.extend(img.planes)
        mask_offset = len(out) if img.mask is not None else None
        if img.mask is not None:
            out.extend(img.mask)
        entries.append(ImageSpan(img.image_id, img.width, img.height, img.depth,
                                 img.stride, plane_size, pixel_offset, pixel_length,
                                 mask_offset, mask_length, img.hotspot_x,
                                 img.hotspot_y))
    result = Stage(bank_number, identity, sha256(payload).hexdigest(),
                   len(payload), parsed.generation, bytes(out), tuple(entries))
    result.validate()
    return result


class StageRegistry:
    """Host reference: atomic replacement and stale-identity refusal."""

    def __init__(self) -> None:
        self._entries: dict[int, Stage] = {}

    def prepare(self, number: int, identity: int, payload: bytes,
                *, budget: int = MAX_STAGE) -> Stage:
        next_stage = stage_agbo(number, identity, payload, budget=budget)
        self._entries[number] = next_stage
        return next_stage

    def resolve(self, number: int, identity: int, payload: bytes) -> Stage | None:
        current = self._entries.get(number)
        return current if current is not None and current.is_current(identity, payload) else None

    def free(self, number: int) -> None:
        self._entries.pop(number, None)
