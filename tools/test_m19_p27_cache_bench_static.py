#!/usr/bin/env python3
"""M19 P2.7 R87: read-only source, asset and parity model preflight.

Does NOT simulate AmigaOS Safe, DMA or AMOS Compiler, and does not
measure speed. The WinUAE logs are the only authority for speed or B/C.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
from pathlib import Path
from struct import pack, unpack_from

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = "M19_P27_R87_CACHE_CPU_BLITTER_01.asc"
ACTIVE_BLOB = "e1062818abdfeb2d7e699d8c1dc9e9696250af65"
P26_BLOB = "c6c03b24bb273027492776ba24e53193ec52198b"
R84_SHA = "46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d"
R87_SHA = "02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302"


def git_blob(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def source_from_rectangles() -> bytes:
    pixels = bytearray(256)
    for y in range(4, 12):
        for x in range(4, 12):
            pixels[y * 16 + x] = 5
    for y in range(2, 6):
        for x in range(8, 12):
            pixels[y * 16 + x] = 6
    return bytes(pixels)


def pixel_bank() -> bytes:
    return bytes(
        6 if 8 <= x < 12 and 2 <= y < 6 else
        5 if 4 <= x < 12 and 4 <= y < 12 else 0
        for y in range(16) for x in range(16)
    )


def unity_slot(pixels: bytes) -> bytes:
    assert len(pixels) == 256
    out = bytearray()
    for y in range(16):
        preserve = 0
        planes = [0] * 8
        for x in range(16):
            col = pixels[y * 16 + x]
            bit = 0x8000 >> x
            if col == 0:
                preserve |= bit
            for p in range(8):
                if col & (1 << p):
                    planes[p] |= bit
        out.extend(pack('>9H', preserve, *planes))
    assert len(out) == 288
    return bytes(out)


def draw_rle_reference(canvas: list[bytearray], x: int, y: int,
                       mode: int, pixels: bytes) -> None:
    for sy in range(16):
        dy = y + sy
        if not 0 <= dy < 256:
            continue
        for sx in range(16):
            dx = x + sx
            if not 0 <= dx < 320:
                continue
            col = pixels[sy * 16 + sx]
            if mode == 0 or col:
                canvas[dy][dx] = col


def draw_ficon_planar(canvas: list[bytearray], x: int, y: int,
                       mode: int, slot: bytes) -> None:
    for sy in range(16):
        dy = y + sy
        if not 0 <= dy < 256:
            continue
        preserve, *planes = unpack_from('>9H', slot, sy * 18)
        for sx in range(16):
            dx = x + sx
            if not 0 <= dx < 320:
                continue
            bit = 0x8000 >> sx
            if mode and preserve & bit:
                continue
            canvas[dy][dx] = sum((1 << k) for k, word in enumerate(planes)
                                 if word & bit)


def scenes() -> list[tuple[int, int, int, int, int]]:
    # x, y, mode, ROI-X, ROI-Y; same positioning rules as the ASC.
    return [
        (32, 40, 0, 24, 32), (33, 40, 0, 24, 32),
        (32, 40, 1, 24, 32), (33, 40, 1, 24, 32),
        (-3, 40, 1, 0, 32), (312, 244, 1, 288, 224),
        (32, -3, 1, 24, 0), (32, 252, 1, 24, 224),
    ]


def test_parity_model() -> None:
    pixels = pixel_bank()
    assert source_from_rectangles() == pixels
    assert {p for p in pixels} == {0, 5, 6}
    assert pixels[0] == 0 and pixels[4 * 16 + 4] == 5
    assert pixels[2 * 16 + 8] == 6 and pixels[5 * 16 + 8] == 6
    slot = unity_slot(pixels)
    for x, y, mode, rx, ry in scenes():
        a = [bytearray([1] * 320) for _ in range(256)]
        b = [bytearray([1] * 320) for _ in range(256)]
        draw_rle_reference(a, x, y, mode, pixels)
        draw_ficon_planar(b, x, y, mode, slot)
        assert bytes().join(bytes(row[rx:rx+32]) for row in a[ry:ry+32]) == ( 
            bytes().join(bytes(row[rx:rx+32]) for row in b[ry:ry+32]))
    # Blit Copy staged source in the same inactive back buffer, opaque mode.
    a = [bytearray([1] * 320) for _ in range(256)]
    b = [bytearray([1] * 320) for _ in range(256)]
    draw_rle_reference(a, 240, 200, 0, pixels)
    for sy in range(16):
        a[40+sy][33:49] = a[200+sy][240:256]
    draw_ficon_planar(b, 33, 40, 0, slot)
    for sy in range(16):
        assert a[40+sy][33:49] == b[40+sy][33:49]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-only', action='store_true',
                        help='Run local source/model checks without mounted GitHub binary files')
    args = parser.parse_args()
    path = ROOT / 'tests/passed' / ACTIVE
    raw = path.read_bytes()
    assert len(list((ROOT/'tests/current').glob('*.asc'))) == 1
    assert next((ROOT/'tests/current').glob('*.asc')).is_file()
    assert git_blob(raw) == ACTIVE_BLOB, 'P2.7 ASC changed without source review'
    previous = (ROOT / 'tests/passed/M19_P26_R87_DRAW_BENCH_01.asc').read_bytes()
    assert git_blob(previous) == P26_BLOB, 'P2.6 PASS source was modified'
    if not args.source_only:
        candidate = (ROOT / 'dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib').read_bytes()
        active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
        assert len(active)==102400 and sha256(active).hexdigest()=='242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'
        lastgood = (ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
        assert len(candidate) == 73184 and sha256(candidate).hexdigest() == R87_SHA
        assert len(lastgood) == 67904 and sha256(lastgood).hexdigest() == R84_SHA
    s = raw.decode('latin-1')
    assert not any(x in s for x in ('Aga Bob Probe', 'ElseIf', 'Pop Proc'))
    assert 'Aga Bank Image Capture(12,0,0,16,16,0,1)' in s
    assert 'Aga Bank Image Capture(13,0,0,16,16,0,2)' in s
    assert 'Aga F Icon Bank Put(11,2,10,0)' in s
    assert 'Aga Blit Copy(240,200,_OX(_I),_OY(_I),16,16)' in s
    assert 'If _BANKS_SAFE=1\n   For _B=10 To 21' in s
    assert 'PARITY_OK ' in s and 'PARITY_BAD ' in s
    assert 'RAM:M19_P27_RUNTIME.TXT' in s and 'RAM:M19_P27_COMPILED.TXT' in s
    assert 'CLOSE_RETURNED ' in s and 'Trap Close 1' in s
    assert 'For _PASS=0 To 1' in s and '_METHOD=1-_ORDER' in s
    assert 'For _CASE=0 To 2' in s and 'For _REP=1 To _REPS' in s
    assert '_RUNS<>12 or _RLE_CALLS<>3584 or _ICON_CALLS<>3584' in s
    assert '_BLIT_RUNS<>4 or _STAGES<>4' in s
    assert '_BLIT_CALLS<>1024 or _OPAQUE_ICON_CALLS<>1024' in s
    assert 'PARITY_OK<>9' in s
    assert 'Aga Swap' not in '\n'.join(line for line in s.splitlines()
                                      if not line.lstrip().startswith("'"))
    assert 'Wait Vbl' not in '\n'.join(line for line in s.splitlines()
                                       if not line.lstrip().startswith("'"))
    # All fill, staging, capture and Erase operations occur before/after timing.
    for section in s.split('_T0=Timer')[1:]:
        timed = section.split('=Timer-_T0', 1)[0]
        assert 'Aga Blit Fill(' not in timed
        assert 'Aga Bank Image Capture(' not in timed
        assert 'Erase ' not in timed
        assert 'Aga Bank Image Draw(12,240,200,0)' not in timed
    assert max(map(len, s.splitlines())) < 200
    test_parity_model()
    print('M19 P2.7 STATIC PASS: R87 read-only target, P2.6 archived unchanged,')
    print('  9 independent 32x32 reference scenarios; 12 masked runs and 4 opaque runs')
    print('  4/8/16, 64 reps, AB/BA, 3584 AGAPIC and 3584 FICON calls')
    print('  Opaque BlitCopy 1024 calls + 4 out-of-chrono stage drawings')
    print('P2.7 WinUAE Runtime and Compiled PASS documented in benchmarks; this script checks static sources only, not FPS')


if __name__ == '__main__':
    main()
