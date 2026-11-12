#!/usr/bin/env python3
"""M16/R47 EXPERIMENTAL: real 68000 AGAPIC one-row RLE CPU Gate A.

Does NOT create AMOS banks or prove WinUAE/Compiler safety. Drives emitted
Motorola 68000 machine code through Unicorn and validates AGAPIC v1 output
using the existing strict decoder and independent host pixel reference.
"""
from __future__ import annotations

import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_MEM_WRITE, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_M68K_REG_PC, UC_M68K_REG_A7, UC_M68K_REG_SR, UC_CPU_M68K_M68000, UC_M68K_REG_D0,
    UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6,
    UC_M68K_REG_D7, UC_M68K_REG_A0, UC_M68K_REG_A1,
    UC_M68K_REG_A2, UC_M68K_REG_A3, UC_M68K_REG_A4,
    UC_M68K_REG_A5, UC_M68K_REG_A6,
)
from m16_capture_r47_core_emit import emit_scanline_rle
from m16_agapic import (
    HEADER, MAGIC, VERSION, FLAG_MASK, CODEC_ROW_RLE,
    parse_payload, unpack_image,
)

CODE = 0x10000
TABLE = 0x20000
PLANE = 0x30000
OUT = 0x60000
STACK = 0x80000
STOP = 0x90000
REGS = (
    UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6,
    UC_M68K_REG_D7, UC_M68K_REG_A0, UC_M68K_REG_A1,
    UC_M68K_REG_A2, UC_M68K_REG_A3, UC_M68K_REG_A4,
    UC_M68K_REG_A5, UC_M68K_REG_A6,
)


def screen(width=43, height=23, depth=4, solid=False):
    stride = ((width + 15) // 16) * 2
    planes = [bytearray(stride * height) for _ in range(depth)]
    pixels = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            colour = 0 if solid else (((x * 5 + y * 7) ^ (x >> 2)) % (1 << depth))
            pixels[y * width + x] = colour
            for p in range(depth):
                if colour & (1 << p):
                    planes[p][y * stride + (x >> 3)] |= 0x80 >> (x & 7)
    return planes, bytes(pixels), stride


def execute(code, planes, stride, x, y, width, depth, transparent=-1, capacity=8192):
    uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    uc.mem_map(0, 0x1000000)  # same 68000/exception vectors as established CPU harness
    uc.mem_write(CODE, code)
    uc.mem_write(STOP, bytes.fromhex('4e71'))
    uc.mem_write(STACK, struct.pack(">I", STOP))
    for p, plane in enumerate(planes):
        uc.mem_write(PLANE + p * 0x1000, bytes(plane))
    uc.mem_write(TABLE, b"".join(
        struct.pack(">I", PLANE + p * 0x1000) for p in range(depth)))
    uc.mem_write(OUT, bytes([0xA5]) * 8192)
    args = [
        (UC_M68K_REG_A0, TABLE), (UC_M68K_REG_A1, OUT),
        (UC_M68K_REG_D0, x), (UC_M68K_REG_D1, y),
        (UC_M68K_REG_D2, width), (UC_M68K_REG_D3, depth),
        (UC_M68K_REG_D4, stride),
        (UC_M68K_REG_D5, transparent & 0xffffffff),
        (UC_M68K_REG_D6, capacity),
    ]
    for reg, value in args:
        uc.reg_write(reg, value & 0xffffffff)
    for reg in (UC_M68K_REG_A2, UC_M68K_REG_A3, UC_M68K_REG_A4,
                UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_D7):
        uc.reg_write(reg, 0x50000 + reg * 2)
    before = {reg: uc.reg_read(reg) for reg in REGS}
    uc.reg_write(UC_M68K_REG_SR, 0x2000)
    uc.reg_write(UC_M68K_REG_A7, STACK)
    writes = []
    def memwrite(uc, access, address, size, value, user):
        if PLANE <= address < PLANE + depth * 0x1000:
            writes.append((address, size))
    uc.hook_add(UC_HOOK_MEM_WRITE, memwrite)
    trace = []
    def code_hook(uc, addr, size, user):
        trace.append((hex(addr),bytes(uc.mem_read(addr,min(size,8))).hex()))
        if len(trace)>24: trace.pop(0)
    uc.hook_add(UC_HOOK_CODE, code_hook)
    try:
        uc.emu_start(CODE, STOP, count=8000000)
    except Exception as error:
        raise AssertionError(('native exception',type(error).__name__,
            str(error), 'PC', hex(uc.reg_read(UC_M68K_REG_PC)),
            'trace', trace, 'stack', hex(uc.reg_read(UC_M68K_REG_A7)))) from error
    assert uc.reg_read(UC_M68K_REG_PC) == STOP, "did not RTS"
    assert uc.reg_read(UC_M68K_REG_A7) == STACK + 4, "stack mismatch"
    assert not writes, "source bitplane modified"
    for reg, value in before.items():
        assert uc.reg_read(reg) == value, ("register changed", reg,
                                          hex(uc.reg_read(reg)), hex(value))
    result = uc.reg_read(UC_M68K_REG_D0)
    assert result < 8192, result
    out = bytes(uc.mem_read(OUT, result))
    return result, out


def payload_from_rows(rows, width, depth, transparent):
    masked = transparent != -1
    stream = 32 + 4 * (len(rows) + 1)
    offsets = [stream]
    for row in rows:
        offsets.append(offsets[-1] + len(row))
    return (
        HEADER.pack(MAGIC, VERSION, FLAG_MASK if masked else 0,
                    CODEC_ROW_RLE, width, len(rows), depth,
                    2 * (depth + int(masked)), 32, stream, offsets[-1])
        + struct.pack(">" + "I" * len(offsets), *offsets)
        + b"".join(rows)
    )


def run():
    code, labels = emit_scanline_rle()
    assert len(code) < 4096 and len(code) % 2 == 0
    assert code[:4] == bytes.fromhex("48e77ffe")
    assert code[-10:] == bytes.fromhex("4fef00a04cdf7ffe4e75")
    cs = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    ins = list(cs.disasm(code, 0))
    assert sum(x.size for x in ins) == len(code), (
        "invalid CPU encoding", len(code), sum(x.size for x in ins),
        [hex(x.address) for x in ins[-5:]])
    boundary = {x.address for x in ins}
    assert all(addr in boundary for addr in labels.values()), labels
    assert not any(i.mnemonic in ("dc.w", "illegal", "trap", "bkpt")
                   for i in ins)
    count = 0
    for depth in (1, 2, 4, 8):
        planes, pixels, stride = screen(depth=depth)
        for x, y, w, h in ((0, 0, 1, 1), (1, 2, 17, 3),
                           (15, 4, 28, 7), (26, 9, 17, 11)):
            for transparent in (-1, 0, (1 << depth) - 1):
                rows = []
                for row in range(y, y + h):
                    n, encoded = execute(
                        code, planes, stride, x, row, w, depth,
                        transparent=transparent)
                    assert 0 < n == len(encoded) <= 8192
                    rows.append(encoded)
                    count += 1
                image = parse_payload(payload_from_rows(
                    rows, w, depth, transparent))
                actual, mask = unpack_image(image)
                expected = bytes(pixels[row * 43 + col]
                                 for row in range(y, y + h)
                                 for col in range(x, x + w))
                assert actual == expected, (
                    "pixel mismatch", depth, x, y, w, h, transparent)
                assert mask == (
                    None if transparent == -1 else
                    bytes(int(v != transparent) for v in expected))
                count += 1
    # RLE repeat packet on 4 identical adjacent groups (64 zero pixels).
    planes, _, stride = screen(width=64, height=2, depth=4, solid=True)
    for transparent, nbytes in ((-1, 9), (0, 11)):
        n, encoded = execute(code, planes, stride, 0, 0, 64, 4, transparent)
        assert (n, encoded[0]) == (nbytes, 0x83), (transparent, n, encoded)
        count += 1
        # One byte too short must fail rather than overflow output.
        bad, _ = execute(
            code, planes, stride, 0, 0, 64, 4, transparent, nbytes - 1)
        assert bad == 0
        count += 1
    # Strict invalid-value and geometry failures, no bank allocation exists.
    planes, _, stride = screen()
    for x, y, w, d, ix, cap in (
        (-1, 0, 10, 4, -1, 8192),
        (4096, 0, 1, 4, -1, 8192),
        (4000, 0, 150, 4, -1, 8192),
        (0, 0, 0, 4, -1, 8192),
        (0, 0, 10, 0, -1, 8192),
        (0, 0, 10, 9, -1, 8192),
        (0, 0, 10, 4, -2, 8192),
        (0, 0, 10, 4, 16, 8192),
        (0, 0, 10, 4, -1, 0),
    ):
        n, _ = execute(code, planes, stride, x, y, w, d, ix, cap)
        assert n == 0, (x, y, w, d, ix, cap)
        count += 1
    print("M16/R47 native 68000 AGAPIC scanline RLE PASS:", count,
          "cases; bytes", len(code))
    print("HOST/CPU Gate A ONLY: NO AMOS bank creation or WinUAE Gate B/C")


if __name__ == "__main__":
    run()
