#!/usr/bin/env python3
"""Host reference codec for proposed AGSP v1 multi-image AGA Sprite banks.

This is a reproducible DATA bank/pixel/palette model, NOT an AMOS command,
a native MC68020 routine, a DMA detach proof, or a WinUAE Gate A/B/C.
The source image is an indexed screen plus an RGB24 CMAP, e.g. from ILBM.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from struct import Struct

MAGIC = b"AGSP"
NAME = b"AGASPRT "
VERSION = 1
HEADER = Struct(">4s4H5I")    # 32 bytes; mirrors AGBO envelope layout
ENTRY = Struct(">6H4I2h2H3I")  # 48 bytes; distinct from AGBO's 40-byte entry
ABK = Struct(">4sHHI8s")       # generic AMOS DATA bank file, 20 bytes
PALETTE_BYTES = 16 * 3          # 16 slots, 24-bit RGB each, local per image
MAX_BANK_BYTES = 16 * 1024 * 1024
MAX_IMAGES = 4096
MAX_HEIGHT = 256
assert HEADER.size == 32 and ENTRY.size == 48 and ABK.size == 20
assert len(NAME) == 8


def _number(value: int, low: int, high: int, name: str) -> None:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"invalid {name}")


def _geometry(width: int, height: int, depth: int) -> tuple[int, int]:
    if type(width) is not int or width not in (16, 32, 64):
        raise ValueError("AGSP widths must be 16, 32 or 64")
    _number(height, 1, MAX_HEIGHT, "image height")
    if type(depth) is not int or depth not in (2, 4):
        raise ValueError("AGSP depth must be 2 or 4 planes")
    stride = width // 8  # always whole 16-bit words
    return stride, stride * height


@dataclass(frozen=True)
class SpriteImage:
    image_id: int
    width: int
    height: int
    depth: int
    stride: int
    planes: bytes              # plane-major, each row big-endian, no RLE
    palette: bytes             # exactly 16 RGB24 triples; zeroed unused slots
    opaque_count: int          # number of used, distinct opaque RGB values
    source_transparent_pen: int
    hotspot_x: int = 0
    hotspot_y: int = 0

    def index(self, x: int, y: int) -> int:
        if type(x) is not int or type(y) is not int or not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("pixel outside sprite image")
        word = 2 * (x // 16)
        mask = 1 << (7 - (x % 8))
        byte = word + ((x % 16) // 8)
        plane_bytes = self.stride * self.height
        return sum((1 << plane) for plane in range(self.depth)
                   if self.planes[plane * plane_bytes + y * self.stride + byte] & mask)

    def rgb(self, x: int, y: int) -> bytes | None:
        color = self.index(x, y)
        return None if color == 0 else self.palette[color * 3:color * 3 + 3]


@dataclass(frozen=True)
class SpriteBank:
    raw: bytes
    generation: int
    images: tuple[SpriteImage, ...]

    def image(self, image_id: int) -> SpriteImage:
        for image in self.images:
            if image.image_id == image_id:
                return image
        raise KeyError(image_id)


def _validate_image(image: SpriteImage) -> None:
    _number(image.image_id, 1, MAX_IMAGES, "image id")
    stride, plane_size = _geometry(image.width, image.height, image.depth)
    if image.stride != stride or type(image.planes) is not bytes or len(image.planes) != plane_size * image.depth:
        raise ValueError("invalid planar data")
    if type(image.palette) is not bytes or len(image.palette) != PALETTE_BYTES:
        raise ValueError("invalid local RGB24 palette")
    _number(image.opaque_count, 0, (1 << image.depth) - 1, "opaque color count")
    _number(image.source_transparent_pen, 0, 255, "transparent source pen")
    _number(image.hotspot_x, -32768, 32767, "hotspot x")
    _number(image.hotspot_y, -32768, 32767, "hotspot y")
    if image.palette[:3] != bytes(3) or any(image.palette[(image.opaque_count + 1) * 3:]):
        raise ValueError("AGSP transparency/unused palette entries must be zero")
    opaque_palette = [image.palette[i * 3:i * 3 + 3] for i in range(1, image.opaque_count + 1)]
    if len(set(opaque_palette)) != len(opaque_palette):
        raise ValueError("duplicate RGB24 palette slots should be remapped")
    observed: set[int] = set()
    first_seen: list[int] = []
    for y in range(image.height):
        for x in range(image.width):
            idx = image.index(x, y)
            if idx > image.opaque_count:
                raise ValueError("pixel refers to unused local pen")
            if idx and idx not in observed:
                observed.add(idx)
                first_seen.append(idx)
    if first_seen != list(range(1, image.opaque_count + 1)):
        raise ValueError("noncanonical color assignment: local pens must follow first appearance")


def _build(images: tuple[SpriteImage, ...], generation: int) -> bytes:
    _number(generation, 1, 0xffffffff, "generation")
    if len(images) > MAX_IMAGES:
        raise ValueError("AGSP bank image count exceeds limit")
    ids = [img.image_id for img in images]
    if ids != sorted(set(ids)):
        raise ValueError("image IDs must be unique and sorted")
    data_start = HEADER.size + ENTRY.size * len(images)
    out = bytearray(data_start)
    cursor = data_start
    for pos, img in enumerate(images):
        _validate_image(img)
        pixels_len = len(img.planes)
        palette_offset = cursor + pixels_len
        end = palette_offset + PALETTE_BYTES
        if end > MAX_BANK_BYTES:
            raise ValueError("AGSP bank exceeds 16 MiB")
        ENTRY.pack_into(out, HEADER.size + pos * ENTRY.size,
                        img.image_id, img.width, img.height, img.depth,
                        img.stride, 0,
                        cursor, pixels_len, palette_offset, PALETTE_BYTES,
                        img.hotspot_x, img.hotspot_y,
                        img.opaque_count, img.source_transparent_pen, 0, 0, 0)
        out.extend(img.planes)
        out.extend(img.palette)
        cursor = end
    HEADER.pack_into(out, 0, MAGIC, VERSION, 0, len(images), ENTRY.size,
                     HEADER.size, data_start, cursor, generation, 0)
    assert len(out) == cursor
    return bytes(out)


def empty_bank() -> bytes:
    """Canonical 32-byte AGSP v1 payload (not an allocated AMOS bank)."""
    return _build((), 1)


def parse_payload(data: bytes) -> SpriteBank:
    """Reject malformed offsets, palettes, pixels, sorting, version and junk."""
    if type(data) is not bytes or not HEADER.size <= len(data) <= MAX_BANK_BYTES:
        raise ValueError("invalid AGSP payload length")
    magic, version, flags, count, entry_size, directory, start, size, generation, reserved = HEADER.unpack_from(data)
    if (magic != MAGIC or version != VERSION or flags or count > MAX_IMAGES or
            entry_size != ENTRY.size or directory != HEADER.size or
            start != HEADER.size + count * ENTRY.size or start > len(data) or
            size != len(data) or generation == 0 or reserved != 0):
        raise ValueError("invalid AGSP v1 header")
    images = []
    cursor = start
    last_id = 0
    for n in range(count):
        (image_id, width, height, depth, stride, flags,
         pixels_offset, pixels_length, pal_offset, pal_length,
         hotspot_x, hotspot_y, opaque_count, source_pen,
         reserved_a, reserved_b, reserved_c) = ENTRY.unpack_from(data, directory + n * ENTRY.size)
        expected_stride, plane_size = _geometry(width, height, depth)
        if (image_id <= last_id or image_id > MAX_IMAGES or flags or
                stride != expected_stride or pixels_offset != cursor or
                pixels_length != plane_size * depth or
                pal_offset != cursor + pixels_length or pal_length != PALETTE_BYTES or
                reserved_a or reserved_b or reserved_c):
            raise ValueError("invalid AGSP image directory")
        end = pal_offset + pal_length
        if end > size:
            raise ValueError("AGSP image data beyond payload")
        image = SpriteImage(image_id, width, height, depth, stride,
                            data[cursor:pal_offset], data[pal_offset:end],
                            opaque_count, source_pen, hotspot_x, hotspot_y)
        _validate_image(image)
        images.append(image)
        last_id = image_id
        cursor = end
    if cursor != size:
        raise ValueError("unreferenced AGSP bytes at end of payload")
    return SpriteBank(data, generation, tuple(images))


def _pack_planes(pixels: bytes, width: int, height: int, depth: int) -> bytes:
    stride, size = _geometry(width, height, depth)
    if type(pixels) is not bytes or len(pixels) != width * height:
        raise ValueError("invalid local index length")
    result = bytearray(size * depth)
    for y in range(height):
        for x in range(width):
            v = pixels[y * width + x]
            if v >= (1 << depth):
                raise ValueError("local color does not fit depth")
            for plane in range(depth):
                if v & (1 << plane):
                    offset = plane * size + y * stride + x // 8
                    result[offset] |= 1 << (7 - (x % 8))
    return bytes(result)


def _image_from_screen(image_id: int, screen: bytes, screen_width: int,
                       screen_height: int, x: int, y: int, width: int,
                       height: int, cmap: bytes, transparent_pen: int,
                       *, mode: str, hotspot_x: int, hotspot_y: int) -> SpriteImage:
    _number(image_id, 1, MAX_IMAGES, "image id")
    _number(screen_width, 1, 65535, "screen width")
    _number(screen_height, 1, 65535, "screen height")
    _number(x, 0, screen_width - 1, "capture x")
    _number(y, 0, screen_height - 1, "capture y")
    _number(transparent_pen, 0, 255, "transparent source pen")
    _number(hotspot_x, -32768, 32767, "hotspot x")
    _number(hotspot_y, -32768, 32767, "hotspot y")
    if type(screen) is not bytes or len(screen) != screen_width * screen_height:
        raise ValueError("screen indexed pixel buffer size mismatch")
    if type(cmap) is not bytes or not 3 <= len(cmap) <= 768 or len(cmap) % 3:
        raise ValueError("CMAP must contain 1..256 RGB24 triples")
    if transparent_pen * 3 + 3 > len(cmap):
        raise ValueError("transparent source pen outside CMAP")
    if mode not in ("s1", "s2"):
        raise ValueError("unknown AGSP capture mode")
    _geometry(width, height, 2)
    if x + width > screen_width or y + height > screen_height:
        raise ValueError("capture rectangle outside source screen")
    if mode == "s1" and width != 16:
        raise ValueError("S1 supports 16px width only")
    colors: dict[bytes, int] = {}
    local = bytearray(width * height)
    for row in range(height):
        for col in range(width):
            pen = screen[(y + row) * screen_width + x + col]
            if pen == transparent_pen:
                continue
            if pen * 3 + 3 > len(cmap):
                raise ValueError("pixel index beyond loaded CMAP")
            rgb = cmap[pen * 3:pen * 3 + 3]
            if rgb not in colors:
                colors[rgb] = len(colors) + 1
                if len(colors) > (3 if mode == "s1" else 15):
                    raise ValueError("too many opaque colors for selected Sprite mode")
            local[row * width + col] = colors[rgb]
    depth = 2 if len(colors) <= 3 else 4
    palette = bytearray(PALETTE_BYTES)
    for rgb, index in colors.items():
        palette[index * 3:index * 3 + 3] = rgb
    return SpriteImage(image_id, width, height, depth, width // 8,
                       _pack_planes(bytes(local), width, height, depth),
                       bytes(palette), len(colors), transparent_pen,
                       hotspot_x, hotspot_y)


def put_capture(payload: bytes, image_id: int, screen: bytes,
                screen_width: int, screen_height: int,
                x: int, y: int, width: int, height: int,
                cmap: bytes, transparent_pen: int, *, mode: str = "s1",
                hotspot_x: int = 0, hotspot_y: int = 0) -> bytes:
    """Transactional image add/replace; input payload is never mutated."""
    bank = parse_payload(payload)
    image = _image_from_screen(image_id, screen, screen_width, screen_height,
                               x, y, width, height, cmap, transparent_pen,
                               mode=mode, hotspot_x=hotspot_x, hotspot_y=hotspot_y)
    if bank.generation == 0xffffffff:
        raise ValueError("AGSP bank generation exhausted")
    images = {old.image_id: old for old in bank.images}
    images[image_id] = image
    return _build(tuple(images[k] for k in sorted(images)), bank.generation + 1)


def delete_image(payload: bytes, image_id: int) -> bytes:
    """Delete an image without renumbering the remaining IDs."""
    _number(image_id, 1, MAX_IMAGES, "image id")
    bank = parse_payload(payload)
    if image_id not in {img.image_id for img in bank.images}:
        raise KeyError(image_id)
    if bank.generation == 0xffffffff:
        raise ValueError("AGSP bank generation exhausted")
    return _build(tuple(img for img in bank.images if img.image_id != image_id),
                  bank.generation + 1)


def set_hotspot(payload: bytes, image_id: int, x: int, y: int) -> bytes:
    """Update per-image hotspot without changing any pixels or RGB colors."""
    _number(x, -32768, 32767, "hotspot x")
    _number(y, -32768, 32767, "hotspot y")
    bank = parse_payload(payload)
    img = bank.image(image_id)
    if (img.hotspot_x, img.hotspot_y) == (x, y):
        return payload
    if bank.generation == 0xffffffff:
        raise ValueError("AGSP bank generation exhausted")
    return _build(tuple(replace(a, hotspot_x=x, hotspot_y=y) if a.image_id == image_id else a
                        for a in bank.images), bank.generation + 1)


def s0_interleaved_image(image: SpriteImage) -> bytes:
    """Host-only 16px, 2-plane OS ChangeSprite data (control/footer zeroed).

    NOT proof of a ready-to-display native DMA allocation or safe teardown.
    ChangeSprite/MoveSprite may rewrite control words and owns its OS channel.
    """
    _validate_image(image)
    if (image.width, image.depth) != (16, 2):
        raise ValueError("S0-compatible interleave requires 16px 2-plane image")
    length = image.stride * image.height
    body = bytearray(b"\x00\x00\x00\x00")
    for y in range(image.height):
        body.extend(image.planes[y * 2:y * 2 + 2])
        body.extend(image.planes[length + y * 2:length + y * 2 + 2])
    body.extend(bytes(4))
    return bytes(body)


def make_abk(bank_number: int, payload: bytes, *, chip_preferred: bool = False) -> bytes:
    """Wrap AGSP in a generic AmBk DATA bank file; NOT an OCS Sprite bank."""
    _number(bank_number, 5, 65535, "AMOS bank number")
    parse_payload(payload)
    return ABK.pack(b"AmBk", bank_number, 3 if chip_preferred else 1,
                    len(payload) + 8, NAME) + payload


def parse_abk(data: bytes) -> tuple[int, int, SpriteBank]:
    if type(data) is not bytes or len(data) < ABK.size:
        raise ValueError("invalid AMOS DATA bank file")
    magic, bank_number, flags, length, name = ABK.unpack_from(data)
    if (magic != b"AmBk" or not 5 <= bank_number <= 65535 or
            flags not in (1, 3) or name != NAME or
            (length & 0x7fffffff) != len(data) - 12):
        raise ValueError("invalid AGSP AMOS bank envelope")
    return bank_number, flags, parse_payload(data[ABK.size:])
