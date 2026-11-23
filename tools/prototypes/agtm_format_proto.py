#!/usr/bin/env python3
"""AGTM v1 host-only reference codec and chunky pixel oracle.

Exploratory specification prototype for RPG Engine / AGA M20.
Not an AMOS bank implementation, MC68020 renderer, or WinUAE test.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct


MAGIC = b"AGTM"
VERSION = 1
HEADER_BYTES = 64
TILE_EDGE = 16
MAX_DIM = 256
MAX_LAYERS = 4
MAX_TILES = 256
_HEADER = struct.Struct(">4sHHHHBBBBHHIIII")
assert _HEADER.size == 36


class AGTMError(ValueError):
    """Invalid AGTM data or an out-of-contract operation."""


@dataclass(frozen=True)
class AGTMMap:
    cols: int
    rows: int
    tile_count: int
    layers: tuple[bytes, ...]

    def __post_init__(self) -> None:
        if not (1 <= self.cols <= MAX_DIM and 1 <= self.rows <= MAX_DIM):
            raise AGTMError("MAP_DIMENSIONS")
        if not 1 <= self.tile_count <= MAX_TILES:
            raise AGTMError("TILE_COUNT")
        if not isinstance(self.layers, tuple) or not 1 <= len(self.layers) <= MAX_LAYERS:
            raise AGTMError("LAYER_COUNT")
        size = self.cols * self.rows
        for index, layer in enumerate(self.layers):
            if not isinstance(layer, bytes) or len(layer) != size:
                raise AGTMError(f"LAYER_LENGTH:{index}")
            if layer and max(layer) >= self.tile_count:
                raise AGTMError(f"TILE_OUT_OF_RANGE:{index}")

    def cell(self, layer: int, x: int, y: int) -> int:
        if not (0 <= layer < len(self.layers) and
                0 <= x < self.cols and 0 <= y < self.rows):
            raise AGTMError("CELL_RANGE")
        return self.layers[layer][y * self.cols + x]

    def with_cell(self, layer: int, x: int, y: int, tile_id: int) -> "AGTMMap":
        if not 0 <= tile_id < self.tile_count:
            raise AGTMError("TILE_OUT_OF_RANGE")
        self.cell(layer, x, y)  # validates coordinates and layer
        offset = y * self.cols + x
        if self.layers[layer][offset] == tile_id:
            return self
        edited = bytearray(self.layers[layer])
        edited[offset] = tile_id
        layers = list(self.layers)
        layers[layer] = bytes(edited)
        return AGTMMap(self.cols, self.rows, self.tile_count, tuple(layers))


def encode_agtm(tilemap: AGTMMap) -> bytes:
    """Serialize the canonical AGTM DATA payload (not an AmBk file)."""
    if not isinstance(tilemap, AGTMMap):
        raise AGTMError("EXPECTED_AGTM_MAP")
    layer_stride = tilemap.cols * tilemap.rows
    data_bytes = layer_stride * len(tilemap.layers)
    header = _HEADER.pack(
        MAGIC, VERSION, HEADER_BYTES,
        tilemap.cols, tilemap.rows,
        TILE_EDGE, TILE_EDGE, len(tilemap.layers), 1,
        tilemap.tile_count, 0,
        tilemap.cols, layer_stride, HEADER_BYTES, data_bytes,
    )
    return header + bytes(HEADER_BYTES - _HEADER.size) + b"".join(tilemap.layers)


def decode_agtm(payload: bytes) -> AGTMMap:
    """Reject noncanonical, truncated, or corrupt AGTM v1 payloads."""
    if not isinstance(payload, bytes) or len(payload) < HEADER_BYTES:
        raise AGTMError("HEADER_LENGTH")
    (magic, version, header_size, cols, rows, tile_w, tile_h,
     layer_count, index_bytes, tile_count, flags, row_stride,
     layer_stride, data_offset, data_bytes) = _HEADER.unpack_from(payload)
    if magic != MAGIC:
        raise AGTMError("MAGIC")
    if version != VERSION:
        raise AGTMError("VERSION")
    if header_size != HEADER_BYTES or data_offset != HEADER_BYTES:
        raise AGTMError("HEADER_OFFSETS")
    if tile_w != TILE_EDGE or tile_h != TILE_EDGE or index_bytes != 1:
        raise AGTMError("TILE_GEOMETRY_OR_INDEX")
    if flags != 0 or any(payload[_HEADER.size:HEADER_BYTES]):
        raise AGTMError("RESERVED_NOT_ZERO")
    if not (1 <= cols <= MAX_DIM and 1 <= rows <= MAX_DIM and
            1 <= layer_count <= MAX_LAYERS and 1 <= tile_count <= MAX_TILES):
        raise AGTMError("LIMITS")
    expected_layer_stride = cols * rows
    if (row_stride != cols or layer_stride != expected_layer_stride or
            data_bytes != expected_layer_stride * layer_count):
        raise AGTMError("STRIDES_OR_LENGTH")
    if len(payload) != HEADER_BYTES + data_bytes:
        raise AGTMError("PAYLOAD_LENGTH")
    layers = tuple(
        payload[HEADER_BYTES + i * layer_stride:
                HEADER_BYTES + (i + 1) * layer_stride]
        for i in range(layer_count)
    )
    return AGTMMap(cols, rows, tile_count, layers)


def render_reference(
    tilemap: AGTMMap,
    tileset: tuple[bytes, ...],
    camera_x: int,
    camera_y: int,
    width: int,
    height: int,
) -> bytes:
    """Slow reference compositor; no AGA bitplanes, timing, or DMA.

    Ground layer is opaque, including palette index 0. Overlay tile ID 0
    is absent; palette index 0 is transparent only on overlay layers.
    """
    if (len(tileset) < tilemap.tile_count or
            any(len(tile) != TILE_EDGE * TILE_EDGE for tile in tileset)):
        raise AGTMError("TILESET_LENGTH")
    if (width <= 0 or height <= 0 or camera_x < 0 or camera_y < 0 or
            camera_x + width > tilemap.cols * TILE_EDGE or
            camera_y + height > tilemap.rows * TILE_EDGE):
        raise AGTMError("VIEWPORT_RANGE")
    screen = bytearray(width * height)
    for y in range(height):
        world_y = camera_y + y
        cell_y = world_y >> 4
        tile_pixel_y = (world_y & 15) * TILE_EDGE
        for x in range(width):
            world_x = camera_x + x
            cell_x = world_x >> 4
            src_offset = tile_pixel_y + (world_x & 15)
            cell_offset = cell_y * tilemap.cols + cell_x
            for layer_number, cells in enumerate(tilemap.layers):
                tile_id = cells[cell_offset]
                if layer_number and tile_id == 0:
                    continue
                pen = tileset[tile_id][src_offset]
                if layer_number and pen == 0:
                    continue
                screen[y * width + x] = pen
    return bytes(screen)
