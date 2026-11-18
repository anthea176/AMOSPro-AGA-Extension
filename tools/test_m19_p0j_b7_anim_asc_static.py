#!/usr/bin/env python3
"""B7-m1 procedural tiled scene: static AMOS and two-page pixel oracle.

Never substitute these host-side pixels for WinUAE or real Amiga DMA proof.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import sys

NAME = "M19_P0J_B7_ANIM_RUNTIME_03.asc"
SIZE = 9624
SHA = "8a3aa82a637334558d918ea0626c9ca661d5f78a1e67ed40ad99ed5a3b1f1904"
LIB_SHA = "838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403"
W, H, TILE = 320, 256, 64
BOBS = ((17, 15, 4), (37, 8, 5), (17, 15, 4), (37, 8, 5))


def paint(buf: bytearray, x: int, y: int, width: int, height: int,
          pen: int, stride: int = W) -> None:
    assert x >= 0 and y >= 0 and width > 0 and height > 0
    assert x + width <= stride and y + height <= len(buf) // stride
    for yy in range(y, y + height):
        buf[yy * stride + x: yy * stride + x + width] = bytes([pen]) * width


def master() -> bytearray:
    tile = bytearray(W * TILE)
    paint(tile, 0, 0, 320, 64, 1)
    paint(tile, 0, 0, 320, 4, 2)
    paint(tile, 0, 32, 320, 4, 2)
    for i in range(10):
        x = i * 32
        paint(tile, x + 2, 8, 28, 18, 3)
        paint(tile, x + 4, 10, 20, 4, 7)
        paint(tile, x + 8, 19, 15, 3, 6)
        paint(tile, x + 2, 40, 28, 14, 8)
        paint(tile, x + 5, 42, 7, 7, 9)
        paint(tile, x + 22, 48, 6, 3, 7)
    assert len(set(tile)) >= 7, "background must not be a flat fill"
    return tile


def copy_rect(page: bytearray, x: int, y: int, width: int,
              height: int) -> tuple[int, int, bool]:
    """Copy x-aligned wallpaper from y%64, split across tile boundaries."""
    if x < 0:
        width += x
        x = 0
    if y < 64:
        height += y - 64
        y = 64
    if x + width > W:
        width = W - x
    if y + height > H:
        height = H - y
    if width <= 0 or height <= 0:
        return 0, 0, False
    calls = area = 0
    crossed = False
    if y % TILE + height > TILE:
        crossed = True
    remaining = height
    while remaining:
        sy = y % TILE
        n = min(remaining, TILE - sy)
        assert 0 <= sy <= 63 and 1 <= n <= 64 - sy
        assert y >= 64 and y + n <= 256
        for j in range(n):
            src, dst = (sy + j) * W + x, (y + j) * W + x
            page[dst:dst + width] = page[src:src + width]
        calls += 1
        area += width * n
        y += n
        remaining -= n
    return calls, area, crossed


def frame_positions(frame: int) -> tuple[tuple[int, int], ...]:
    p = frame if frame <= 60 else 120 - frame
    return ((-10 + p * 5, 72), (315 - p * 5, 110),
            (-5 + p * 2, 170 - p), (315 - p * 3, 200 - p))


def draw_bobs(page: bytearray, positions: tuple[tuple[int, int], ...]) -> None:
    for idx, ((x, y), (w, h, pen)) in enumerate(zip(positions, BOBS)):
        assert y >= 64, "Bobs cannot touch the immutable master band"
        for dy in range(h):
            py = y + dy
            if not 64 <= py < H:
                continue
            for dx in range(w):
                px = x + dx
                if not 0 <= px < W:
                    continue
                # Masked red Bobs: the 5x5 pen-0 hole stays transparent.
                if idx in (0, 2) and 5 <= dx < 10 and 5 <= dy < 10:
                    continue
                page[py * W + px] = pen


def pixel_oracle() -> tuple[int, int, int]:
    tile = master()
    base = tile * 4
    pages = [bytearray(base), bytearray(base)]
    scenes = total_copies = splits = 0
    for case in (1, 2, 3, 3, 2, 1):
        page_index = 0
        previous = [None, None]
        for frame in range(1, 121):
            page = pages[page_index]
            pos = frame_positions(frame)
            if case in (1, 2) or frame <= 2:
                # First two frames of C fully prime each physical page.
                for row in range(1, 4):
                    n, area, crossed = copy_rect(page, 0, row * 64, 320, 64)
                    assert n == 1 and area == 320 * 64 and not crossed
                    total_copies += n
            else:
                assert case == 3 and previous[page_index] is not None
                for (x, y), (w, h, unused) in zip(previous[page_index], BOBS):
                    n, unused_area, crossed = copy_rect(page, x, y, w, h)
                    total_copies += n
                    splits += int(crossed)
            if case != 2:
                draw_bobs(page, pos)
            expected = bytearray(base)
            if case != 2:
                draw_bobs(expected, pos)
            assert page == expected, (case, frame, page_index, 'stale image or tile corruption')
            assert page[:W * TILE] == tile, (case, frame, 'master overwritten')
            if case == 3:
                previous[page_index] = pos
            page_index ^= 1  # only after a successful simulated Swap
            scenes += 1
        assert page_index == 0  # even run length preserves physical parity
    assert scenes == 720 and splits > 0 and total_copies > 1500
    return scenes, splits, total_copies


def verify(path: Path) -> None:
    data = path.read_bytes()
    assert len(data) == SIZE and sha256(data).hexdigest() == SHA, 'ASC SHA drift'
    src = data.decode('ascii')
    lines = src.splitlines()
    assert lines and max(map(len, lines)) <= 200
    assert LIB_SHA in src and 'NO COMPILER TEST' in src
    assert src.rstrip().endswith('Return') and '\nEnd\n' in src
    assert len(re.findall(r'(?m)^\s*If\b', src)) == len(
        re.findall(r'(?m)^\s*End If\b', src))
    assert len(re.findall(r'(?m)^\s*For\b', src)) == len(
        re.findall(r'(?m)^\s*Next\b', src))
    assert len(re.findall(r'(?m)^\s*Repeat\b', src)) == len(
        re.findall(r'(?m)^\s*Until\b', src))
    assert not re.search(r'\bElseIf\b|\bExit\s+For\b|\bThen\b', src, re.I)
    required = ('Aga Screen Open(320,256,256,$00021000)', 'Aga Double Buffer',
                'Aga Screen Close', 'Amos To Front', 'Aga Bob Draw',
                'Make AGA Bob Mask 1,0', 'No AGA Bob Mask 1',
                'Aga Blit Copy(_DX,_SY,_DX,_DY,_DW,_SLICE)',
                'Aga Blit Fill(_PX,_PY,_PW,_PH,_COL)',
                'Gosub _BUILD_TILE', 'Gosub _RESTORE_FULL',
                'Gosub _COPY_TILE_RECT', 'Gosub _DO_SWAP',
                '_PAGE=1-_PAGE', '_SY=_SY-64', 'If _SLICE>64-_SY',
                'If _CASE=3 and _FRAME>2', 'If _ERR=0 and _CASE<>2',
                'For _RUN=1 To 6', 'For _FRAME=1 To 120',
                '_T0=Timer', '_TICKS(_RUN)=Timer-_T0',
                '_WAITS(_RUN)=_RETRY_VBL-_WAIT0',
                'Trap Open Out 1,_LOG$', 'Trap Close 1',
                'Erase _BANK1', 'Erase _BANK2', 'PRG_STATE',
                'RUN_COPIES', 'RUN_COPY_PIXELS', 'RUN_WAITS',
                'VERDICT', 'CLOSE_CALLED', 'TILE_MASTER_HEIGHT 64')
    for term in required:
        assert term in src, ('missing', term)
    assert src.count('Aga Blit Copy(') == 1
    assert src.count('Aga Bob Draw') == 1
    assert src.count('Aga Swap') == 1
    assert src.count('Make AGA Bob Mask 1,0') == 1
    assert src.count('No AGA Bob Mask 1') == 1
    assert 'Erase All' not in '\n'.join(l.split("'", 1)[0] for l in lines)
    assert src.index('\n_CLEANUP:\n') < src.index('\n   Aga Screen Close\n')
    assert src.index('\n   Aga Screen Close\n') < src.index('\n   Erase _BANK1\n')
    assert src.index('\n   Erase _BANK1\n') < src.index('\n   Erase _BANK2\n')
    assert src.index('For _WARM=1 To 2') < src.index('Amos To Back')
    assert src.index('Amos To Back') < src.index('For _RUN=1 To 6')
    # The backing pattern is built outside measured loops, never recopied
    # from a page containing the moving Bobs.
    assert src.index('_BUILD_TILE:') > src.index('\nEnd\n')
    assert src.count('Gosub _BUILD_TILE') == 1
    assert src.count('Gosub _RESTORE_FULL') == 2
    for bob in ('Aga Bob 1,_X1,_Y1,1', 'Aga Bob 2,_X2,_Y2,1',
                'Aga Bob 3,_X3,_Y3,1', 'Aga Bob 4,_X4,_Y4,1'):
        assert src.count(bob) == 1
    assert 'If _ERR=0 and _FR_OK=720 and _DB=1 and _CLOSE_CALLED=1' in src
    scenes, splits, copies = pixel_oracle()
    print(f'M19 B7-m1 DECOR BENCH STATIC PASS: {scenes} exact two-page scenes, '
          f'{splits} tile-boundary splits, {copies} copy calls simulated; '
          'NO WinUAE or Compiler validation')


if __name__ == '__main__':
    verify(Path(sys.argv[1]) if len(sys.argv) > 1
           else Path('tests/current') / NAME)
