#!/usr/bin/env python3
"""Deterministic ILBM -> chunky fixture for examples/c2p_iff_showcase.

No AMOS runtime IFF decoding is assumed. The original .iff remains the
authority. Verify existing .chk by default; --write explicitly regenerates it.
Checks both input/output SHA256 and the exact final Blit+Zoom pixel oracle.
Only Python stdlib is required for CI.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import zlib
from pathlib import Path
from struct import unpack

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "iff-TEST/AGA_DEMO_320x256_256c.iff"
CHUNKY = ROOT / "iff-TEST/AGA_DEMO_320x256_256c.chk"
AMOS = ROOT / "examples/c2p_iff_showcase/C2P_IFF_SHOWCASE_R79.asc"
PNG = ROOT / "examples/c2p_iff_showcase/EXPECTED_C2P_SHOWCASE.png"
PNG_SHA = "919b166c1c815df2fe08bb0d0d8c3fdbb6224bdd8b9c0bcb08e40ae3b8cedadb"
SOURCE_SHA = "1820df9bcd77ae111b55927981482ce90c67da06d74646f6b6d92082f00db2db"
CHUNKY_SHA = "3f4df7bc229d36ab5a2711913fa8798d1d11bfe82a6792a98e5be67ad470b694"
COMPOSITE_SHA = "57604d9abf991cc5fe17425e4247431048d4cdc3276083302bbf1359b484cd09"
WIDTH, HEIGHT, PLANES = 320, 256, 8

BLITS = (
    (20,90,52,52,70,170),
    (238,92,58,48,222,165),
    (237,3,76,26,122,225),
)
ZOOMS = (
    (145,10,56,56,10,14,84,84),
    (240,74,48,64,198,14,96,112),
    (234,176,64,64,132,176,32,32),
    (0,64,40,48,-16,115,64,96),
    (128,48,48,48,292,215,72,72),
    (231,0,60,32,124,-16,60,48),
    (82,145,49,33,79,108,77,49),
)
PIXELS = (
    (319,0,244), (0,250,246), (70,170,114), (224,168,58),
    (122,225,224), (10,14,68), (92,95,0), (198,14,123),
    (132,176,52), (0,115,155), (319,255,85), (124,0,221),
    (79,108,127), (150,151,155),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_iff(data: bytes) -> tuple[bytes, bytes]:
    if len(data) < 12 or data[:4] != b"FORM" or data[8:12] != b"ILBM":
        raise ValueError("not a FORM ILBM")
    if int.from_bytes(data[4:8], "big") + 8 != len(data):
        raise ValueError("FORM size mismatch")
    chunks: dict[bytes, bytes] = {}
    pos = 12
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("truncated chunk header")
        tag = data[pos:pos+4]
        n = int.from_bytes(data[pos+4:pos+8], "big")
        end = pos + 8 + n + (n & 1)
        if end > len(data) or tag in chunks:
            raise ValueError("invalid/duplicate chunk")
        chunks[tag] = data[pos+8:pos+8+n]
        pos = end
    if not all(key in chunks for key in (b"BMHD", b"CMAP", b"CAMG", b"BODY")):
        raise ValueError("required ILBM chunk missing")
    if len(chunks[b"BMHD"]) != 20:
        raise ValueError("wrong BMHD length")
    w, h, x, y, planes, mask, compression, pad, transparent, ax, ay, pw, ph = (
        unpack(">HHhhBBBBHBBhh", chunks[b"BMHD"])
    )
    if (w, h, planes, mask, compression) != (WIDTH, HEIGHT, PLANES, 0, 1):
        raise ValueError("fixture must be 320x256x8 ByteRun1 without mask")
    if len(chunks[b"CMAP"]) != 768 or int.from_bytes(chunks[b"CAMG"], "big") != 0x21000:
        raise ValueError("fixture must have 256 RGB entries and PAL LoRes mode")
    body = chunks[b"BODY"]
    row_bytes = ((w + 15) // 16) * 2
    off = 0

    def row() -> bytes:
        nonlocal off
        pixels = bytearray()
        while len(pixels) < row_bytes:
            if off >= len(body):
                raise ValueError("truncated ByteRun1 BODY")
            cmd = body[off]
            off += 1
            if cmd < 128:
                n = cmd + 1
                if off + n > len(body):
                    raise ValueError("truncated ByteRun1 literal")
                pixels.extend(body[off:off+n])
                off += n
            elif cmd > 128:
                n = 257 - cmd
                if off >= len(body):
                    raise ValueError("truncated ByteRun1 repeat")
                pixels.extend([body[off]] * n)
                off += 1
            if len(pixels) > row_bytes:
                raise ValueError("ByteRun1 packet crosses plane row")
        return bytes(pixels)

    chunky = bytearray(w * h)
    for yy in range(h):
        rows = [row() for _ in range(planes)]
        for xx in range(w):
            flag = 0x80 >> (xx & 7)
            chunky[yy * w + xx] = sum(
                (1 << plane) for plane in range(planes)
                if rows[plane][xx >> 3] & flag
            )
    if off != len(body):
        raise ValueError("BODY trailing bytes")
    return bytes(chunky), chunks[b"CMAP"]


def compose(base: bytes) -> bytes:
    """Independent pixel oracle; source is immutable, target starts as source."""
    dst = bytearray(base)
    for sx, sy, w, h, dx, dy in BLITS:
        for yy in range(max(0, dy), min(HEIGHT, dy + h)):
            for xx in range(max(0, dx), min(WIDTH, dx + w)):
                dst[yy * WIDTH + xx] = base[(sy + yy - dy) * WIDTH + sx + xx - dx]
    for sx, sy, sw, sh, dx, dy, dw, dh in ZOOMS:
        for yy in range(max(0, dy), min(HEIGHT, dy + dh)):
            source_y = sy + ((yy - dy) * sh) // dh
            for xx in range(max(0, dx), min(WIDTH, dx + dw)):
                source_x = sx + ((xx - dx) * sw) // dw
                dst[yy * WIDTH + xx] = base[source_y * WIDTH + source_x]
    return bytes(dst)


def verify_png(expected_pixels: bytes, palette: bytes) -> None:
    """Indexed PNG golden image must match the model, without relying on PIL."""
    blob = PNG.read_bytes()
    assert sha256(blob) == PNG_SHA, "expected PNG changed"
    assert blob.startswith(b"\x89PNG\r\n\x1a\n")
    pos = 8
    chunks = {}
    while pos < len(blob):
        length = int.from_bytes(blob[pos:pos+4], "big")
        kind = blob[pos+4:pos+8]
        data = blob[pos+8:pos+8+length]
        crc = int.from_bytes(blob[pos+8+length:pos+12+length], "big")
        assert zlib.crc32(kind+data) & 0xffffffff == crc
        assert kind not in chunks
        chunks[kind] = data
        pos += 12+length
    assert pos == len(blob)
    assert list(chunks) == [b"IHDR", b"PLTE", b"IDAT", b"IEND"]
    assert chunks[b"IHDR"] == bytes.fromhex("00000140000001000803000000")
    assert chunks[b"PLTE"] == palette
    scanlines = zlib.decompress(chunks[b"IDAT"])
    assert len(scanlines) == HEIGHT*(WIDTH+1)
    for y in range(HEIGHT):
        row = scanlines[y*(WIDTH+1):(y+1)*(WIDTH+1)]
        assert row[0] == 0
        assert row[1:] == expected_pixels[y*WIDTH:(y+1)*WIDTH], y


def verify_program(code: str) -> None:
    """Guard the AMOS source against silent picture geometry/test drift."""
    observed_blit = []
    observed_zoom = []
    for line in code.splitlines():
        m = re.match(r"\s*_B([123])=Aga C2P Blit\(([^)]*)\)", line)
        if m:
            values = tuple(int(q) for q in m.group(2).split(","))
            assert values[:2] == (13, 320) and len(values) == 8
            observed_blit.append(values[2:])
        m = re.match(r"\s*_Z([1-7])=Aga C2P Zoom\(([^)]*)\)", line)
        if m:
            values = tuple(int(q) for q in m.group(2).split(","))
            assert values[:2] == (13, 320) and len(values) == 10
            observed_zoom.append(values[2:])
    assert tuple(observed_blit) == BLITS, "AMOS Blit geometry drift"
    assert tuple(observed_zoom) == ZOOMS, "AMOS Zoom geometry drift"
    for xx, yy, index in PIXELS:
        offset = (f"{yy}*320+{xx}" if yy and xx else
                  f"{yy}*320" if yy else str(xx))
        assert f"Peek(_PTR+{offset})={index}" in code, (
            f"AMOS reference pixel missing ({xx},{yy})={index}")
    assert code.count("_PIXCOUNT=_PIXCOUNT+1") == len(PIXELS)
    assert 'If _PIXCOUNT<>14' in code
    assert 'Until _K=69' in code
    assert code.index("Amos To Back") < code.index("Until _K=69")
    assert code.index("Until _K=69") < code.index("Aga Screen Close")
    assert code.index("Aga Screen Close") < code.index("Amos To Front")
    assert code.count("CLEANUP:") == 1 and code.rstrip().endswith("End")
    assert "RAM:C2P_IFF_SHOWCASE.TXT" in code
    assert "Bload _RAW$,_PTR" in code and "Bload _RAW$,_SRC" in code


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="regenerate the .chk from original IFF explicitly")
    args = parser.parse_args()
    data = SOURCE.read_bytes()
    assert sha256(data) == SOURCE_SHA, "original IFF changed"
    decoded, palette = decode_iff(data)
    assert len(decoded) == 81920 and len(set(decoded)) == 256
    assert sha256(decoded) == CHUNKY_SHA, "offline chunky pixel hash drift"
    assert palette[:3] == bytes.fromhex("F6F2FA")
    if args.write:
        CHUNKY.write_bytes(decoded)
    assert CHUNKY.read_bytes() == decoded, "checked-in chunky differs from IFF"
    output = compose(decoded)
    assert sha256(output) == COMPOSITE_SHA, "composed visual frame changed"
    verify_png(output, palette)
    for x, y, expected in PIXELS:
        assert output[y * WIDTH + x] == expected, (x, y, expected)
    program = AMOS.read_text("ascii")
    verify_program(program)
    print("PASS C2P IFF SHOWCASE ASSET + ASC STATIC")
    print("IFF", SOURCE_SHA, "CHUNKY", CHUNKY_SHA)
    print("COMPOSITE", COMPOSITE_SHA, "PNG", PNG_SHA, "PIXELS", len(PIXELS),
          "BLITS", len(BLITS), "ZOOMS", len(ZOOMS))
    print("AMOS WinUAE runtime NOT TESTED by this script")


if __name__ == "__main__":
    main()
