#!/usr/bin/env python3
"""OPT020 P1b: real masked 1..8 plane 68EC020/68020 execution and RLE host path.

Musashi executes every native kernel call. Full image geometry, corrupted
stream rejection, crop/masks and clipping use the existing AGAPIC v1
parser with an independent per-pixel destination oracle.
NOT a full native RLE/AP20 renderer and NOT WinUAE or real Amiga timing.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from random import Random
from struct import pack

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from machine68k import CPUType, Machine, Register

from m16_agapic import pack_image, parse_payload
from opt020_p1b_multiplane_emit import emit_masked_multiplane_020
from opt020_p1b_region import draw_region_020
from test_m18_agapic_atlas_model import as_planar, reference

CODE = 0x1000
RETURN = 0x1800
SRC = 0x3000
TABLE = 0x3100
DEST = 0x4000
STACK = 0x1f000
BEFORE_GUARD = bytes([0xa5] * 8)
AFTER_GUARD = bytes([0x5a] * 8)
D5_VALUE = 0x13579bdf
A3_VALUE = 0x2468ace0


class Real020Writer:
    """Native callable with an independent emulated memory for each CPU."""

    def __init__(self, cpu_kind):
        self.machine = Machine(cpu_kind, 256)
        self.calls = 0
        self.cycles = 0
        self.cpu_kind = cpu_kind
        self.code = emit_masked_multiplane_020()
        m = self.machine
        m.mem.w32(0, STACK)
        m.mem.w32(4, CODE)
        m.cpu.execute(m.cpu.pulse_reset())
        self.token = m.create_execute_end("opt020-p1b-return")
        self.trap_id = m.traps.alloc(lambda op, pc: self.token)
        assert 0 <= self.trap_id <= 4095
        m.mem.w16(RETURN, 0xa000 | self.trap_id)
        m.mem.w_block(CODE, self.code)

    def close(self):
        self.machine.cleanup()

    def __call__(self, colour_words, mask, shift, planes, dst_offset):
        depth = len(colour_words)
        assert 1 <= depth <= 8
        assert 0 <= mask <= 65535 and 0 <= shift < 8
        assert len(planes) == depth
        required = 2 if shift == 0 else 3
        m, cpu = self.machine, self.machine.cpu
        src = pack(">" + "H" * depth, *colour_words)
        m.mem.w_block(SRC, src)
        windows = []
        for i, plane in enumerate(planes):
            assert dst_offset + required <= len(plane)
            original = bytes(plane[dst_offset:dst_offset + required])
            windows.append(original)
            # A guard on both sides makes 8-plane pointer overrun visible.
            location = DEST + i * 0x100
            m.mem.w_block(location, BEFORE_GUARD + original + AFTER_GUARD)
            m.mem.w32(TABLE + i * 4, location + len(BEFORE_GUARD))
        m.mem.w32(STACK, RETURN)
        cpu.w_pc(CODE)
        cpu.w_sp(STACK)
        cpu.w_reg(Register.A0, SRC)
        cpu.w_reg(Register.A1, TABLE)
        cpu.w_reg(Register.A3, A3_VALUE)
        cpu.w_reg(Register.D0, shift)
        cpu.w_reg(Register.D2, mask)
        cpu.w_reg(Register.D3, 0)
        cpu.w_reg(Register.D5, D5_VALUE)
        cpu.w_reg(Register.D6, depth)
        state = m.execute(20000)
        assert state.result is self.token, (
            "CPU did not return", self.cpu_kind, depth, shift, mask,
            cpu.r_pc(), state)
        assert cpu.r_sp() == STACK + 4
        assert cpu.r_reg(Register.D3) == 1
        assert cpu.r_reg(Register.A3) == A3_VALUE
        assert cpu.r_reg(Register.D5) == D5_VALUE
        assert cpu.r_reg(Register.D0) == shift
        assert cpu.r_reg(Register.D2) == mask
        assert cpu.r_reg(Register.D6) & 65535 == 0
        assert cpu.r_reg(Register.A0) == SRC + 2 * depth
        assert cpu.r_reg(Register.A1) == TABLE + 4 * depth
        assert m.mem.r_block(SRC, len(src)) == src, "source was changed"
        for i, plane in enumerate(planes):
            location = DEST + i * 0x100
            actual = m.mem.r_block(location, 8 + required + 8)
            assert actual[:8] == BEFORE_GUARD
            assert actual[8 + required:] == AFTER_GUARD
            plane[dst_offset:dst_offset + required] = actual[8:8 + required]
        self.calls += 1
        self.cycles += state.sum_cycles


def test_code() -> tuple[int, str]:
    code = emit_masked_multiplane_020()
    assert code == emit_masked_multiplane_020()
    items = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020).
                 disasm(code, CODE))
    names = [i.mnemonic.lower().split(".", 1)[0] for i in items]
    assert sum(i.size for i in items) == len(code), (code.hex(), names)
    assert names.count("bfextu") == 2, names
    assert names.count("bfins") == 1, names
    assert "bne" in names and "not" in names
    assert names[-2:] == ["moveq", "rts"], names
    return len(code), sha256(code).hexdigest()


def direct_native(kind) -> int:
    rng = Random(0x200202)
    writer = Real020Writer(kind)
    tested = 0
    try:
        for depth in (1, 2, 4, 8):
            for shift in range(8):
                for mask in (0, 0xffff, 0xa55a, 0x8001, 0x5555):
                    words = [rng.randrange(65536) for _ in range(depth)]
                    before = [bytearray(rng.randbytes(8)) for _ in range(depth)]
                    expected = [bytearray(p) for p in before]
                    for plane, word in enumerate(words):
                        for pixel in range(16):
                            bit = 0x8000 >> pixel
                            if mask & bit:
                                dstbit = shift + pixel
                                db = dstbit // 8
                                bm = 0x80 >> (dstbit & 7)
                                if word & bit:
                                    expected[plane][db] |= bm
                                else:
                                    expected[plane][db] &= 255 ^ bm
                    writer(words, mask, shift, before, 0)
                    assert before == expected, (kind, depth, shift, mask)
                    tested += 1
    finally:
        writer.close()
    return tested


def make_atlas(depth, masked):
    w, h = 65, 11
    pixels = bytearray(w * h)
    mask = bytearray(w * h)
    for y in range(h):
        for x in range(w):
            # Two first groups identical -> one repeat packet, later groups
            # differ -> literal packets. The last group has 15 padding bits.
            if x < 32:
                value = ((x % 16) * 3 + y * 7) % (1 << depth)
            elif x < 48:
                value = ((x % 16) * 7 + y * 5 + 1) % (1 << depth)
            else:
                value = ((x % 16) * 11 + y * 3 + 2) % (1 << depth)
            pixels[y * w + x] = value
            mask[y * w + x] = int(((x % 16) + y * 3) % 5 != 0)
    raw = pack_image(w, h, depth, bytes(pixels),
                     bytes(mask) if masked else None)
    return parse_payload(raw), bytes(pixels), bytes(mask) if masked else None


def test_full_region(kind) -> tuple[int, int, int, int, int]:
    rng = Random(0x68ec020)
    tests = native = fallback = repeats = literals = 0
    for depth in (1, 2, 4, 8):
        for masked in (False, True):
            img, colours, mask = make_atlas(depth, masked)
            for region in ((0, 0, 65, 11), (3, 1, 47, 8),
                           (16, 2, 32, 7)):
                for x, y in ((0, 0), (1, 3), (5, -2),
                             (-19, 1), (36, 8), (57, 22)):
                    for mode in ((0, 1) if masked else (0,)):
                        backdrop = bytes(rng.randrange(1 << depth)
                                         for _ in range(57 * 22))
                        dest, stride = as_planar(backdrop, 57, 22, depth)
                        expected_pixels, pixels_written = reference(
                            backdrop, 57, 22, colours, mask, img.width,
                            region, x, y, mode)
                        target, _ = as_planar(expected_pixels, 57, 22, depth)
                        runner = Real020Writer(kind)
                        try:
                            result = draw_region_020(
                                img, *region, x, y, dest, 57, 22, mode,
                                runner, stride)
                            assert result.pixels == pixels_written
                            assert result.native_groups == runner.calls
                            assert dest == target, (
                                "pixel mismatch", kind, depth, masked,
                                region, x, y, mode, result)
                            assert all(p[-12:] == bytes([0xa5] * 12)
                                       for p in dest)
                            native += runner.calls
                            fallback += result.fallback_pixels
                            repeats += result.repeat_packets
                            literals += result.literal_packets
                        finally:
                            runner.close()
                        tests += 1
    assert native > 0 and fallback > 0, (kind, native, fallback)
    assert repeats > 0 and literals > 0
    return tests, native, fallback, repeats, literals


def test_rejects() -> int:
    img, pixels, _ = make_atlas(8, False)
    planes, stride = as_planar(bytes([42] * (57 * 22)), 57, 22, 8)
    cases = [
        ("bad source X", replace(img), (-1, 0, 8, 4, 0, 0, 0)),
        ("source crop overrun", img, (64, 0, 2, 1, 0, 0, 0)),
        ("zero width", img, (0, 0, 0, 4, 0, 0, 0)),
        ("bad mode", img, (0, 0, 16, 4, 0, 0, 1)),
        ("bad origin", img, (0, 0, 16, 4, 32768, 0, 0)),
        ("invalid depth metadata", replace(img, depth=7),
         (0, 0, 16, 4, 0, 0, 0)),
        ("truncated final RLE", replace(img, raw=img.raw[:-1]),
         (0, 0, 16, 4, 0, 0, 0)),
        ("invalid RLE run size", replace(
            img, raw=(img.raw[:img.offsets[-2]] + bytes([0xff]) +
                      img.raw[img.offsets[-2] + 1:])),
         (0, 0, 16, 4, 0, 0, 0)),
    ]
    count = 0
    for name, image, args in cases:
        before = [bytes(p) for p in planes]
        invoked = []
        def forbidden_writer(*anything):
            invoked.append(anything)
        try:
            draw_region_020(image, *args[:6], planes, 57, 22,
                            args[6], forbidden_writer, stride)
        except ValueError:
            assert not invoked and [bytes(p) for p in planes] == before, name
            count += 1
        else:
            raise AssertionError("Invalid input accepted: " + name)
    return count


def main():
    size, digest = test_code()
    runs, native, fallback, repeats, literals = 0, 0, 0, 0, 0
    direct = 0
    for cpu in (CPUType.M68EC020, CPUType.M68020):
        direct += direct_native(cpu)
        a, b, c, d, e = test_full_region(cpu)
        runs += a
        native += b
        fallback += c
        repeats += d
        literals += e
    refused = test_rejects()
    print("OPT020/P1b REAL 68EC020+68020 native PASS:",
          direct, "direct 1/2/4/8-plane cases;",
          runs, "full AGAPIC RLE crop/mask/clip comparisons")
    print("Native groups executed", native, "fallback pixels", fallback,
          "RLE repeat/literal packets", repeats, literals)
    print("Preflight safe refusals", refused)
    print("Native kernel", size, "bytes SHA256", digest)
    print("NO AP20 integrated, no R69, no AMOS Compiler, "
          "no WinUAE Chip RAM/CPU speed claim")


if __name__ == "__main__":
    main()
