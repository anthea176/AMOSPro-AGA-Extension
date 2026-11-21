#!/usr/bin/env python3
"""M19 P0a, R88-derived HOST FORMAT model for AMOS AGA multi-image Bobs.

This is a host-side specification and validation implementation, NOT an AP20
command, an AMOS interpreter test, a Compiler test, or a new installable Lib.
A complete in-memory payload is constructed before any bank can be replaced.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from struct import Struct, pack_into, unpack_from

MAGIC = b"AGBO"
BANK_NAME = b"AGABOBS "
VERSION = 1
FLAG_MASK = 1
HEADER = Struct(">4s4H5I")  # 32 bytes
ENTRY = Struct(">6H4I2h2I")  # 40 bytes
ABK = Struct(">4sHHI8s")  # 20-byte native AMOS DATA-file envelope
MAX_BANK_BYTES = 16 * 1024 * 1024
MAX_PIXELS = 4 * 1024 * 1024
MAX_SIDE = 4096
MAX_IMAGE_ID = 4096
assert HEADER.size == 32 and ENTRY.size == 40 and ABK.size == 20


def _int_range(value: int, low: int, high: int, name: str) -> None:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"invalid {name}")


def _geometry(width: int, height: int, depth: int) -> tuple[int, int]:
    _int_range(width, 1, MAX_SIDE, "width")
    _int_range(height, 1, MAX_SIDE, "height")
    _int_range(depth, 1, 8, "depth")
    if width * height > MAX_PIXELS:
        raise ValueError("too many source pixels")
    stride = 2 * ((width + 15) // 16)
    plane_bytes = stride * height
    return stride, plane_bytes


@dataclass(frozen=True)
class BobImage:
    image_id: int
    width: int
    height: int
    depth: int
    stride: int
    planes: bytes
    mask: bytes | None = None
    hotspot_x: int = 0
    hotspot_y: int = 0

    @property
    def plane_bytes(self) -> int:
        return self.stride * self.height

    def colour(self, x: int, y: int) -> int:
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise IndexError("pixel outside image")
        pos = y * self.stride + 2 * (x // 16)
        bit = 0x8000 >> (x % 16)
        return sum(1 << p for p in range(self.depth)
                   if unpack_from(">H", self.planes,
                                  p * self.plane_bytes + pos)[0] & bit)

    def visible(self, x: int, y: int) -> bool:
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise IndexError("pixel outside image")
        if self.mask is None:
            return True
        return bool(unpack_from(">H", self.mask,
                                y * self.stride + 2 * (x // 16))[0]
                    & (0x8000 >> (x % 16)))


@dataclass(frozen=True)
class BobBank:
    raw: bytes
    generation: int
    images: tuple[BobImage, ...]

    def image(self, image_id: int) -> BobImage:
        for item in self.images:
            if item.image_id == image_id:
                return item
        raise KeyError(image_id)


def _validate_padding(raw: bytes, width: int, height: int, stride: int,
                      plane_count: int) -> None:
    remainder = width & 15
    if not remainder:
        return
    unused = (1 << (16 - remainder)) - 1
    size = stride * height
    for p in range(plane_count):
        for y in range(height):
            if unpack_from(">H", raw, p * size + y * stride + stride - 2)[0] & unused:
                raise ValueError("nonzero padding outside image width")


def _validate_image(image: BobImage) -> None:
    _int_range(image.image_id, 1, MAX_IMAGE_ID, "image id")
    stride, size = _geometry(image.width, image.height, image.depth)
    if image.stride != stride or type(image.planes) is not bytes or len(image.planes) != size * image.depth:
        raise ValueError("invalid planar image dimensions")
    _validate_padding(image.planes, image.width, image.height, stride, image.depth)
    if image.mask is not None:
        if type(image.mask) is not bytes or len(image.mask) != size:
            raise ValueError("invalid independent mask")
        _validate_padding(image.mask, image.width, image.height, stride, 1)
    _int_range(image.hotspot_x, -32768, 32767, "hotspot x")
    _int_range(image.hotspot_y, -32768, 32767, "hotspot y")


def _build(images: tuple[BobImage, ...], generation: int) -> bytes:
    _int_range(generation, 1, 0xffffffff, "generation")
    if len(images) > MAX_IMAGE_ID:
        raise ValueError("too many images")
    if tuple(sorted(x.image_id for x in images)) != tuple(x.image_id for x in images) or len({x.image_id for x in images}) != len(images):
        raise ValueError("image IDs must be unique and increasing")
    data_start = HEADER.size + len(images) * ENTRY.size
    if data_start > MAX_BANK_BYTES:
        raise ValueError("directory too large")
    out = bytearray(data_start)
    cursor = data_start
    for index, img in enumerate(images):
        _validate_image(img)
        pixels_length = len(img.planes)
        mask_length = len(img.mask) if img.mask is not None else 0
        if cursor + pixels_length + mask_length > MAX_BANK_BYTES:
            raise ValueError("AMOS bank exceeds 16 MiB")
        mask_offset = cursor + pixels_length if mask_length else 0
        ENTRY.pack_into(out, HEADER.size + index * ENTRY.size,
                        img.image_id, img.width, img.height, img.depth,
                        img.stride, FLAG_MASK if mask_length else 0,
                        cursor, pixels_length, mask_offset, mask_length,
                        img.hotspot_x, img.hotspot_y, 0, 0)
        out.extend(img.planes)
        if img.mask is not None:
            out.extend(img.mask)
        cursor += pixels_length + mask_length
    HEADER.pack_into(out, 0, MAGIC, VERSION, 0, len(images), ENTRY.size,
                     HEADER.size, data_start, cursor, generation, 0)
    assert len(out) == cursor
    return bytes(out)


def empty_bank() -> bytes:
    """Canonical empty payload, not an allocated native AMOS bank."""
    return _build((), 1)


def parse_payload(data: bytes) -> BobBank:
    """Validate all offsets, masks, unused bits and image ranges before use."""
    if type(data) is not bytes or not HEADER.size <= len(data) <= MAX_BANK_BYTES:
        raise ValueError("invalid ABK payload length")
    magic, version, flags, count, stride, directory, data_start, total, generation, reserved = HEADER.unpack_from(data)
    if (magic != MAGIC or version != VERSION or flags or reserved or
            stride != ENTRY.size or directory != HEADER.size or
            count > MAX_IMAGE_ID or data_start != HEADER.size + count * ENTRY.size or
            total != len(data) or not generation):
        raise ValueError("invalid multi-image ABK header")
    result: list[BobImage] = []
    cursor = data_start
    last_id = 0
    for n in range(count):
        (image_id, w, h, depth, row_stride, image_flags,
         pixels_offset, pixels_length, mask_offset, mask_length,
         hot_x, hot_y, reserved1, reserved2) = ENTRY.unpack_from(data, directory + n * stride)
        expected_stride, plane_size = _geometry(w, h, depth)
        if (image_id <= last_id or image_id > MAX_IMAGE_ID or
            row_stride != expected_stride or image_flags & ~FLAG_MASK or
            reserved1 or reserved2 or pixels_offset != cursor or
            pixels_length != plane_size * depth):
            raise ValueError("invalid image directory entry")
        has_mask = bool(image_flags & FLAG_MASK)
        if (mask_offset != (cursor + pixels_length if has_mask else 0) or
            mask_length != (plane_size if has_mask else 0)):
            raise ValueError("invalid mask location")
        end = cursor + pixels_length + mask_length
        if end > total:
            raise ValueError("image data exceeds bank")
        image = BobImage(image_id, w, h, depth, row_stride,
                         data[cursor:cursor + pixels_length],
                         data[cursor + pixels_length:end] if has_mask else None,
                         hot_x, hot_y)
        _validate_image(image)
        result.append(image)
        last_id = image_id
        cursor = end
    if cursor != total:
        raise ValueError("unreferenced or trailing image bytes")
    return BobBank(data, generation, tuple(result))


def pack_pixels(image_id: int, width: int, height: int, depth: int,
                pixels: bytes, *, visibility: bytes | None = None) -> BobImage:
    """Convert indexed pixels to plane-major, word-aligned, non-RLE data."""
    _int_range(image_id, 1, MAX_IMAGE_ID, "image id")
    stride, plane_size = _geometry(width, height, depth)
    if type(pixels) is not bytes or len(pixels) != width * height or any(v >= (1 << depth) for v in pixels):
        raise ValueError("wrong indexed image pixels")
    if visibility is not None and (type(visibility) is not bytes or
                                   len(visibility) != len(pixels) or any(v not in (0, 1) for v in visibility)):
        raise ValueError("visibility must use independent 0/1 bits")
    plane_bytes = bytearray(plane_size * depth)
    mask_bytes = bytearray(plane_size) if visibility is not None else None
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            word_off = y * stride + 2 * (x // 16)
            bit = 0x8000 >> (x & 15)
            color = pixels[pos]
            for p in range(depth):
                if color & (1 << p):
                    off = p * plane_size + word_off
                    value = unpack_from(">H", plane_bytes, off)[0]
                    pack_into(">H", plane_bytes, off, value | bit)
            if mask_bytes is not None and visibility[pos]:
                value = unpack_from(">H", mask_bytes, word_off)[0]
                pack_into(">H", mask_bytes, word_off, value | bit)
    return BobImage(image_id, width, height, depth, stride,
                    bytes(plane_bytes), bytes(mask_bytes) if mask_bytes is not None else None)


def put_image(payload: bytes, image_id: int, width: int, height: int,
              depth: int, pixels: bytes, *, visibility: bytes | None = None) -> bytes:
    """Add or replace exactly one image; does not mutate the source payload."""
    current = parse_payload(payload)
    new = pack_pixels(image_id, width, height, depth, pixels, visibility=visibility)
    if current.generation == 0xffffffff:
        raise ValueError("generation exhausted")
    images = {image.image_id: image for image in current.images}
    images[image_id] = new
    return _build(tuple(images[k] for k in sorted(images)), current.generation + 1)


def delete_images(payload: bytes, first: int, last: int) -> bytes:
    """Repack an inclusive ID range without renumbering remaining images."""
    _int_range(first, 1, MAX_IMAGE_ID, "first image id")
    _int_range(last, first, MAX_IMAGE_ID, "last image id")
    bank = parse_payload(payload)
    remaining = tuple(image for image in bank.images
                      if not first <= image.image_id <= last)
    if len(remaining) == len(bank.images):
        raise ValueError("no image in interval")
    return _build(remaining, bank.generation + 1)


def insert_blank_image(payload: bytes, image_id: int, width: int,
                       height: int, depth: int) -> bytes:
    """Create a drawable, transparent placeholder at an unoccupied ID."""
    _int_range(image_id, 1, MAX_IMAGE_ID, "image id")
    stride, plane_size = _geometry(width, height, depth)
    bank = parse_payload(payload)
    if any(image.image_id == image_id for image in bank.images):
        raise ValueError("image id is already occupied")
    if len(payload) + ENTRY.size + plane_size * (depth + 1) > MAX_BANK_BYTES:
        raise ValueError("AMOS bank exceeds 16 MiB")
    image = BobImage(image_id, width, height, depth, stride,
                     bytes(plane_size * depth), bytes(plane_size))
    updated = tuple(sorted((*bank.images, image), key=lambda item: item.image_id))
    return _build(updated, bank.generation + 1)


def make_mask(payload: bytes, image_id: int, transparent_index: int) -> bytes:
    current = parse_payload(payload)
    img = current.image(image_id)
    _int_range(transparent_index, 0, (1 << img.depth) - 1, "transparency index")
    if current.generation == 0xffffffff:
        raise ValueError("generation exhausted")
    mask = bytearray(img.plane_bytes)
    for y in range(img.height):
        for x in range(img.width):
            if img.colour(x, y) != transparent_index:
                off = y * img.stride + 2 * (x // 16)
                pack_into(">H", mask, off,
                          unpack_from(">H", mask, off)[0] | (0x8000 >> (x & 15)))
    new_img = BobImage(img.image_id, img.width, img.height, img.depth,
                       img.stride, img.planes, bytes(mask), img.hotspot_x, img.hotspot_y)
    return _build(tuple(new_img if item.image_id == image_id else item
                        for item in current.images), current.generation + 1)


def no_mask(payload: bytes, image_id: int) -> bytes:
    current = parse_payload(payload)
    img = current.image(image_id)
    if img.mask is None:
        return payload
    if current.generation == 0xffffffff:
        raise ValueError("generation exhausted")
    new_img = BobImage(img.image_id, img.width, img.height, img.depth,
                       img.stride, img.planes, None, img.hotspot_x, img.hotspot_y)
    return _build(tuple(new_img if item.image_id == image_id else item
                        for item in current.images), current.generation + 1)



def set_hotspot(payload: bytes, image_id: int, x: int, y: int) -> bytes:
    """Change existing AGBO v1 per-image anchor; copy-on-write and atomic.

    HOST MODEL ONLY: not a public AMOS command or native rendering support.
    The existing 40-byte directory entry already contains signed hot_x/y.
    Changing metadata increments the generation to invalidate Chip staging.
    """
    _int_range(image_id, 1, MAX_IMAGE_ID, "image id")
    _int_range(x, -32768, 32767, "hotspot x")
    _int_range(y, -32768, 32767, "hotspot y")
    current = parse_payload(payload)
    selected = current.image(image_id)
    if (selected.hotspot_x, selected.hotspot_y) == (x, y):
        return payload
    if current.generation == 0xffffffff:
        raise ValueError("generation exhausted")
    updated = tuple(replace(image, hotspot_x=x, hotspot_y=y)
                    if image.image_id == image_id else image
                    for image in current.images)
    return _build(updated, current.generation + 1)


def make_abk(bank_number: int, payload: bytes, *, chip_preferred: bool = False) -> bytes:
    """Create an AMOS DATA file; the Chip flag is NOT proof of Chip residency."""
    _int_range(bank_number, 5, 65535, "AMOS bank number")
    parse_payload(payload)
    return ABK.pack(b"AmBk", bank_number, 3 if chip_preferred else 1,
                    len(payload) + 8, BANK_NAME) + payload


def parse_abk(raw: bytes) -> tuple[int, int, BobBank]:
    if type(raw) is not bytes or len(raw) < ABK.size:
        raise ValueError("invalid AMOS bank file")
    magic, number, flags, length, name = ABK.unpack_from(raw)
    # Native AMOS Save may set bit 31 of the length field (observed on
    # M19_P0A_68020_BOBS.ABK); the low 31 bits still equal file size - 12.
    # Keep the exact-length check: never accept truncated or trailing bytes.
    actual_length = length & 0x7FFFFFFF
    if (magic != b"AmBk" or not 5 <= number <= 65535 or
            flags not in (1, 3) or actual_length != len(raw) - 12 or
            name != BANK_NAME):
        raise ValueError("invalid AMOS DATA bank header")
    return number, flags, parse_payload(raw[ABK.size:])
