"""M19 AGA Bob bank ABK v1: independent planar pixels and 1-bit masks.

Host-side deterministic reference codec only. It DOES NOT register AP20 tokens,
allocate real Chip RAM, run WinUAE, or substitute for native Get AGA Bob.
The fixed-size DATA payload permits in-place updates by a future AMOS native
writer without destructive Bnk.Reserve on each captured image.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from struct import Struct
from typing import Iterable

ABK = Struct('>4sHHI8s')
HEADER = Struct('>8sHHHHIIIIII')
ENTRY = Struct('>HHHHHHIII')
ABK_NAME = b'AGABOB  '
MAGIC = b'AGABOB01'
VERSION = 1
MAX_IMAGES = 128
CAPACITY = 131072
DATA_OFFSET = HEADER.size + MAX_IMAGES * ENTRY.size
MASK_FLAG = 1


class BobFormatError(ValueError):
    """Invalid geometry, bank, payload, capacity, or mask."""


def _valid_bank(number: int) -> None:
    if type(number) is not int or not 5 <= number <= 65535:
        raise BobFormatError('AMOS DATA bank must be in 5..65535')


def _valid_image(image_id: int) -> None:
    if type(image_id) is not int or not 1 <= image_id <= MAX_IMAGES:
        raise BobFormatError('image ID outside 1..128')


def stride_for(width: int) -> int:
    if type(width) is not int or not 1 <= width <= 4096:
        raise BobFormatError('invalid image width')
    return ((width + 15) // 16) * 2


def _geometry(width: int, height: int, depth: int) -> int:
    if type(height) is not int or not 1 <= height <= 4096:
        raise BobFormatError('invalid image height')
    if type(depth) is not int or not 1 <= depth <= 8:
        raise BobFormatError('invalid bitplane depth')
    return stride_for(width) * height


def _check_padding(raw: bytes, width: int, height: int) -> None:
    """Each scanline's unused bits must be zero (plane or mask)."""
    stride = stride_for(width)
    trailing = stride * 8 - width
    if not trailing:
        return
    keep = (1 << trailing) - 1
    for row in range(height):
        if int.from_bytes(raw[(row + 1) * stride - 2:(row + 1) * stride], 'big') & keep:
            raise BobFormatError('nonzero planar padding bits')


def planar_from_indices(width: int, height: int, depth: int,
                        indices: Iterable[int]) -> bytes:
    plane_len = _geometry(width, height, depth)
    data = list(indices)
    if len(data) != width * height or any(
        type(c) is not int or c < 0 or c >= 1 << depth for c in data
    ):
        raise BobFormatError('colour indices/length invalid for depth')
    stride = stride_for(width)
    buf = bytearray(plane_len * depth)
    for y in range(height):
        for x in range(width):
            value = data[y * width + x]
            addr = y * stride + (x >> 3)
            bit = 0x80 >> (x & 7)
            for plane in range(depth):
                if value & (1 << plane):
                    buf[plane * plane_len + addr] |= bit
    return bytes(buf)


def indices_from_planar(width: int, height: int, depth: int,
                        planar: bytes) -> bytes:
    plane_len = _geometry(width, height, depth)
    if len(planar) != plane_len * depth:
        raise BobFormatError('bad planar length')
    stride = stride_for(width)
    out = bytearray(width * height)
    for plane in range(depth):
        src = planar[plane * plane_len:(plane + 1) * plane_len]
        _check_padding(src, width, height)
        for y in range(height):
            for x in range(width):
                if src[y * stride + (x >> 3)] & (0x80 >> (x & 7)):
                    out[y * width + x] |= 1 << plane
    return bytes(out)


def mask_from_visible(width: int, height: int, visible: Iterable[bool]) -> bytes:
    _geometry(width, height, 1)
    v = list(visible)
    if len(v) != width * height or any(type(c) not in (int, bool) or c not in (0, 1) for c in v):
        raise BobFormatError('invalid visibility map')
    stride = stride_for(width)
    result = bytearray(stride * height)
    for y in range(height):
        for x in range(width):
            if v[y * width + x]:
                result[y * stride + (x >> 3)] |= 0x80 >> (x & 7)
    return bytes(result)


@dataclass(frozen=True)
class BobImage:
    width: int
    height: int
    depth: int
    pixels: bytes
    mask: bytes | None = None

    def __post_init__(self) -> None:
        row_bytes = _geometry(self.width, self.height, self.depth)
        if len(self.pixels) != row_bytes * self.depth:
            raise BobFormatError('pixel bytes mismatch')
        indices_from_planar(self.width, self.height, self.depth, self.pixels)
        if self.mask is not None:
            if len(self.mask) != row_bytes:
                raise BobFormatError('mask bytes mismatch')
            _check_padding(self.mask, self.width, self.height)

    @classmethod
    def from_pixels(cls, width: int, height: int, depth: int,
                    indices: Iterable[int]) -> BobImage:
        return cls(width, height, depth,
                   planar_from_indices(width, height, depth, indices))

    def colours(self) -> bytes:
        return indices_from_planar(self.width, self.height, self.depth, self.pixels)

    def with_transparency(self, colour: int) -> BobImage:
        if type(colour) is not int or not 0 <= colour < 1 << self.depth:
            raise BobFormatError('transparent colour outside palette')
        return BobImage(self.width, self.height, self.depth, self.pixels,
                        mask_from_visible(self.width, self.height,
                                          (index != colour for index in self.colours())))

    def without_mask(self) -> BobImage:
        return BobImage(self.width, self.height, self.depth, self.pixels)


@dataclass
class BobBank:
    number: int
    images: dict[int, BobImage] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _valid_bank(self.number)
        for ident, image in self.images.items():
            _valid_image(ident)
            if not isinstance(image, BobImage):
                raise BobFormatError('image is not BobImage')
        self._encode_payload()  # verify capacity before publishing

    def put(self, image_id: int, image: BobImage) -> None:
        _valid_image(image_id)
        if not isinstance(image, BobImage):
            raise BobFormatError('image is not BobImage')
        new = dict(self.images)
        new[image_id] = image
        self._encode_payload(new)  # transactional validation
        self.images = new

    def capture(self, image_id: int, screen_width: int, screen_height: int,
                depth: int, indices: Iterable[int],
                x1: int, y1: int, x2: int, y2: int) -> None:
        """Host pixel oracle for Get AGA Bob's INCLUSIVE rectangle."""
        _valid_image(image_id)
        _geometry(screen_width, screen_height, depth)
        if any(type(n) is not int for n in (x1, y1, x2, y2)) or not (
            0 <= x1 <= x2 < screen_width and 0 <= y1 <= y2 < screen_height
        ):
            raise BobFormatError('capture rectangle outside AGA screen')
        source = bytes(indices)
        if len(source) != screen_width * screen_height:
            raise BobFormatError('screen pixel buffer length invalid')
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        selected = (source[y * screen_width + x]
                    for y in range(y1, y2 + 1)
                    for x in range(x1, x2 + 1))
        self.put(image_id, BobImage.from_pixels(width, height, depth, selected))

    def capture_planar(self, image_id: int, screen_width: int,
                       screen_height: int, depth: int, planes: Iterable[bytes],
                       source_stride: int, x1: int, y1: int,
                       x2: int, y2: int) -> None:
        """Reference capture from physical plane-major AGA back-buffer bytes.

        The planes are the source BitMap plane buffers, NOT a chunky image.
        The caller must choose the inactive/safe buffer; this model cannot
        interrogate Intuition, TypeOfMem or WaitBlit.
        """
        _valid_image(image_id)
        source = list(planes)
        _geometry(screen_width, screen_height, depth)
        if len(source) != depth:
            raise BobFormatError('source BitMap depth does not match planes')
        if (type(source_stride) is not int or source_stride % 2 or
            not stride_for(screen_width) <= source_stride <= 65534):
            raise BobFormatError('invalid physical BitMap stride')
        if any(len(p) < source_stride * screen_height for p in source):
            raise BobFormatError('source plane memory too short')
        if any(type(n) is not int for n in (x1, y1, x2, y2)) or not (
            0 <= x1 <= x2 < screen_width and 0 <= y1 <= y2 < screen_height
        ):
            raise BobFormatError('capture rectangle outside AGA screen')
        width, height = x2 - x1 + 1, y2 - y1 + 1
        stride = stride_for(width)
        dst_plane_bytes = stride * height
        dst = bytearray(dst_plane_bytes * depth)
        for plane, input_plane in enumerate(source):
            for row in range(height):
                for col in range(width):
                    source_offset = (y1 + row) * source_stride + ((x1 + col) >> 3)
                    if input_plane[source_offset] & (0x80 >> ((x1 + col) & 7)):
                        dst[plane * dst_plane_bytes + row * stride + (col >> 3)] |= (
                            0x80 >> (col & 7))
        self.put(image_id, BobImage(width, height, depth, bytes(dst)))

    def make_mask(self, image_id: int, colour: int) -> None:
        _valid_image(image_id)
        if image_id not in self.images:
            raise BobFormatError('mask references missing image')
        self.put(image_id, self.images[image_id].with_transparency(colour))

    def no_mask(self, image_id: int) -> None:
        _valid_image(image_id)
        if image_id not in self.images:
            raise BobFormatError('mask references missing image')
        self.put(image_id, self.images[image_id].without_mask())

    def _encode_payload(self, images: dict[int, BobImage] | None = None) -> bytes:
        images = self.images if images is None else images
        out = bytearray(CAPACITY)
        used = DATA_OFFSET
        for image_id, image in sorted(images.items()):
            _valid_image(image_id)
            pixel_length = len(image.pixels)
            mask_length = len(image.mask) if image.mask is not None else 0
            end = used + pixel_length + mask_length
            if end > CAPACITY:
                raise BobFormatError('bank capacity exceeded; original images preserved')
            out[used:used + pixel_length] = image.pixels
            mask_offset = used + pixel_length if mask_length else 0
            if mask_length:
                out[mask_offset:end] = image.mask
            ENTRY.pack_into(out, HEADER.size + (image_id - 1) * ENTRY.size,
                            image_id, image.width, image.height, image.depth,
                            stride_for(image.width), MASK_FLAG if mask_length else 0,
                            used, mask_offset, end - used)
            used = end
        HEADER.pack_into(out, 0, MAGIC, VERSION, MAX_IMAGES, len(images), 0,
                         CAPACITY, used, HEADER.size, ENTRY.size, DATA_OFFSET, 0)
        return bytes(out)

    def to_abk(self, *, flags: int = 1) -> bytes:
        if flags not in (1, 3):
            raise BobFormatError('invalid AMOS DATA flags')
        data = self._encode_payload()
        return ABK.pack(b'AmBk', self.number, flags, len(data) + 8, ABK_NAME) + data

    @classmethod
    def from_abk(cls, raw: bytes, *, expected_bank: int | None = None) -> BobBank:
        if len(raw) < ABK.size + HEADER.size:
            raise BobFormatError('truncated ABK')
        magic, bank, flags, length, name = ABK.unpack_from(raw)
        _valid_bank(bank)
        if (magic, name) != (b'AmBk', ABK_NAME) or flags not in (0, 1, 3):
            raise BobFormatError('not an AGA Bob AMOS DATA bank')
        if expected_bank is not None and bank != expected_bank:
            raise BobFormatError('wrong AMOS bank number')
        if length != len(raw) - ABK.size + 8:
            raise BobFormatError('ABK length mismatch')
        payload = raw[ABK.size:]
        (ident, version, slots, count, hdr_flags, capacity, used,
         dir_offset, entry_size, data_offset, reserved) = HEADER.unpack_from(payload)
        if (ident, version, slots, hdr_flags, capacity, dir_offset,
            entry_size, data_offset, reserved) != (
            MAGIC, VERSION, MAX_IMAGES, 0, CAPACITY,
            HEADER.size, ENTRY.size, DATA_OFFSET, 0
        ) or len(payload) != CAPACITY or not DATA_OFFSET <= used <= CAPACITY:
            raise BobFormatError('unsupported/corrupt AGA Bob header')
        images = {}
        cursor = DATA_OFFSET
        for image_id in range(1, MAX_IMAGES + 1):
            (num, w, h, depth, stride, flags, pixel_at,
             mask_at, extent) = ENTRY.unpack_from(payload,
                                                  HEADER.size + (image_id - 1) * ENTRY.size)
            if not any((num, w, h, depth, stride, flags, pixel_at, mask_at, extent)):
                continue
            if num != image_id or flags not in (0, MASK_FLAG):
                raise BobFormatError('corrupt Bob directory')
            size = _geometry(w, h, depth)
            pixel_length = size * depth
            mask_length = size if flags & MASK_FLAG else 0
            if (stride != stride_for(w) or pixel_at != cursor or
                extent != pixel_length + mask_length or
                mask_at != (cursor + pixel_length if mask_length else 0) or
                cursor + extent > used):
                raise BobFormatError('invalid Bob image offsets')
            pixels = payload[cursor:cursor + pixel_length]
            mask = payload[mask_at:mask_at + mask_length] if mask_length else None
            images[image_id] = BobImage(w, h, depth, pixels, mask)
            cursor += extent
        if count != len(images) or cursor != used or any(payload[used:]):
            raise BobFormatError('noncanonical Bob bank payload')
        return cls(bank, images)
