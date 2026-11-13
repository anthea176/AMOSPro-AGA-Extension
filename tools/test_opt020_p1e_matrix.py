#!/usr/bin/env python3
"""OPT020/P1e expanded CPU Gate A: real R60+020 memory safety and corruption.

Runs native code on Musashi, including actual GetAdr/Safe/bitmap traversals;
this is NOT WinUAE or AMOS Compiler. No installable library is generated.
"""
from __future__ import annotations

from struct import pack_into, unpack_from

from machine68k import CPUType

from m16_agapic import pack_image
from m18_image_region_emit import emit_image_region
from test_opt020_p1e_region import (
    LiveRegionCPU, BANK, BITMAP0, BITMAP1, DB, STATE,
)


def execute(native, *, kind=CPUType.M68020, payload=None, depth=4,
            screen_width=64, screen_height=42, stride=12, front=0,
            bank_flag=1, pending=0, safe_ready=True, invalid_mem_at=0,
            mutation=None, expect_ok=True, bank=10,
            sx=3, sy=2, w=21, h=9, x=5, y=7, mode=0):
    if payload is None:
        pixel = bytes((xx * 5 + yy * 3) & ((1 << depth) - 1)
                      for yy in range(22) for xx in range(57))
        payload = pack_image(57, 22, depth, pixel)
    m = LiveRegionCPU(
        kind, native, payload, base=0x1c000, depth=depth, front=front,
        bank_flag=bank_flag, pending=pending, safe_ready=safe_ready,
        invalid_mem_at=invalid_mem_at, screen_width=screen_width,
        screen_height=screen_height, stride=stride,
    )
    try:
        if mutation:
            mutation(m)
        m.run(bank=bank, sx=sx, sy=sy, w=w, h=h, x=x, y=y,
              mode=mode, expect_ok=expect_ok)
        if not expect_ok and safe_ready and pending:
            assert m.getmsg_calls == 0
        return m.bank_calls, m.type_calls, m.getmsg_calls
    finally:
        m.close()


def altered(original, mutator):
    result = bytearray(original)
    mutator(result)
    assert result != original
    return bytes(result)


def main():
    native, labels = emit_image_region(opt020=True)
    assert len(native) == 2174
    cases = 0

    # 1/2/4/8 planes; physical stride equal to minimum *and* padded.
    # Exercise group/fragment writers at the last allocated bitmap byte.
    geometries = ((16, 18, 2), (17, 18, 4), (65, 18, 10),
                  (64, 42, 8), (64, 42, 12))
    for kind in (CPUType.M68EC020, CPUType.M68020):
        for depth in (1, 2, 4, 8):
            pixels = bytes(((xx * 13 + yy * 7) ^ (xx >> 2)) & ((1 << depth) - 1)
                           for yy in range(22) for xx in range(57))
            mask = bytes(int((xx + 3 * yy) % 7 != 0)
                         for yy in range(22) for xx in range(57))
            for masked in (False, True):
                image = pack_image(57, 22, depth, pixels,
                                   mask if masked else None)
                for sw, sh, stride in geometries:
                    # Fully visible, including a 16px write exactly at last row.
                    execute(native, kind=kind, payload=image, depth=depth,
                            screen_width=sw, screen_height=sh, stride=stride,
                            front=int(masked), pending=3,
                            sx=0, sy=0, w=16, h=6,
                            x=sw - 16, y=sh - 6, mode=int(masked))
                    cases += 1
                    # Clipped fragment at lower/right limits; no adjacent writes.
                    execute(native, kind=kind, payload=image, depth=depth,
                            screen_width=sw, screen_height=sh, stride=stride,
                            front=1-int(masked), pending=1,
                            sx=1, sy=1, w=17, h=7,
                            x=sw - 8, y=sh - 5, mode=int(masked))
                    cases += 1
                if masked:
                    # Stored mask must be ignored in mode 0.
                    execute(native, kind=kind, payload=image, depth=depth,
                            sx=4, sy=2, w=17, h=11, x=5, y=7, mode=0)
                    cases += 1
                for x, y in ((-100, 5), (100, 5), (5, -100), (5, 100)):
                    execute(native, kind=kind, payload=image, depth=depth,
                            pending=3, x=x, y=y, mode=int(masked))
                    cases += 1

    # DATA envelope 0/1/3 accepted, 2/4/0xffff rejected, always no corruption.
    pixels = bytes(((xx * 3 + yy * 5) ^ xx) & 15
                   for yy in range(3) for xx in range(17))
    image = pack_image(17, 3, 4, pixels)
    for flag in (0, 1, 3):
        execute(native, payload=image, bank_flag=flag, pending=3,
                sx=0, sy=0, w=17, h=3, x=7, y=8)
        cases += 1
    for flag in (2, 4, 0xffff):
        execute(native, payload=image, bank_flag=flag, pending=3,
                expect_ok=False, sx=0, sy=0, w=17, h=3)
        cases += 1
    for at in (1, 2):
        execute(native, payload=image, pending=3, invalid_mem_at=at,
                expect_ok=False, sx=0, sy=0, w=17, h=3)
        cases += 1

    # RLE/source corruptions: ALL rejected before Safe or any plane write.
    st = unpack_from(">I", image, 32)[0]
    group_bytes = 2 * 4
    # Image width17 makes the LAST 16-bit group contain 15 pad pixels.
    bad = (
        ("magic", lambda b: b.__setitem__(0, 0)),
        ("version", lambda b: pack_into(">H", b, 6, 2)),
        ("flags", lambda b: pack_into(">H", b, 8, 2)),
        ("codec", lambda b: pack_into(">H", b, 10, 2)),
        ("width", lambda b: pack_into(">H", b, 12, 0)),
        ("depth", lambda b: pack_into(">H", b, 16, 9)),
        ("groupbytes", lambda b: pack_into(">H", b, 18, 0)),
        ("rowtable", lambda b: pack_into(">I", b, 20, 0)),
        ("stream", lambda b: pack_into(">I", b, 24, 0)),
        ("length", lambda b: pack_into(">I", b, 28, len(b) + 8)),
        ("row-offset", lambda b: pack_into(">I", b, 36, st)),
        ("row-overrun", lambda b: b.__setitem__(st, 0x7f)),
        ("rle-broken", lambda b: b.__setitem__(st, 0x80)),
        ("last-group-pad", lambda b: b.__setitem__(
            st + 1 + group_bytes + 1, b[st + 1 + group_bytes + 1] | 1)),
    )
    for description, mutate in bad:
        corrupt = altered(image, mutate)
        execute(native, payload=corrupt, pending=3, expect_ok=False,
                sx=0, sy=0, w=17, h=3)
        cases += 1

    # Independent mask padding must likewise be rejected in PASS 0.
    masked = pack_image(17, 3, 4, pixels, bytes([1]) * len(pixels))
    mask_start = unpack_from(">I", masked, 32)[0]
    mask_group_bytes = 2 * 5
    wrong_mask_pad = altered(masked, lambda b: b.__setitem__(
        mask_start + 1 + mask_group_bytes + 1,
        b[mask_start + 1 + mask_group_bytes + 1] | 1))
    execute(native, payload=wrong_mask_pad, pending=1,
            sx=0, sy=0, w=17, h=3, mode=1, expect_ok=False)
    cases += 1

    # Failure in the real managed DATA header must never touch Safe.
    mutations = (
        lambda m: m.mem.w32(BANK - 20, len(image) + 15),
        lambda m: m.mem.w32(BANK - 16, 4),
        lambda m: m.mem.w32(BANK - 8, 0x58585858),
        lambda m: m.mem.w32(STATE + 32, 0),
        lambda m: m.mem.w32(STATE + 28, 8),
        lambda m: m.mem.w32(BITMAP1 + 8, 0),
        lambda m: m.mem.w16(BITMAP1, 0),
        lambda m: m.mem.w16(BITMAP1 + 2, 0),
        lambda m: m.mem.w_block(BITMAP1 + 5, bytes([8])),
        lambda m: m.mem.w32(DB + 4, 0),
    )
    for mutate in mutations:
        execute(native, payload=image, pending=1,
                expect_ok=False, mutation=mutate,
                sx=0, sy=0, w=17, h=3)
        cases += 1

    # Safe pending 1/3 unready is a refusal, without destruction or wait.
    for pending in (1, 3):
        execute(native, payload=image, pending=pending,
                safe_ready=False, expect_ok=False,
                sx=0, sy=0, w=17, h=3, mode=0)
        cases += 1
    # Safe bit clear means no GetMsg call even when the port is not ready.
    execute(native, payload=image, pending=0, safe_ready=False,
            sx=0, sy=0, w=17, h=3, mode=0)
    cases += 1

    # All-transparent mask with mode=0 is still an opaque sprite;
    # the same bank with mode=1 is a true no-op.
    transparent = pack_image(17, 3, 4, pixels, bytes(len(pixels)))
    for mode in (0, 1):
        execute(native, payload=transparent, mode=mode,
                sx=0, sy=0, w=17, h=3)
        cases += 1

    print("OPT020/P1e EXTENDED CPU/MUSASHI GATE A PASS:", cases,
          "mixed depths, exact stride, canaries, masked/opaque,")
    print("DATA flags, malformed RLE, bank/Bitmap/Safe refusal, 000 guard.")
    print("NO lib/ASC modified, no AMOS Compiler, no WinUAE Gate B/C.")


if __name__ == "__main__":
    main()
