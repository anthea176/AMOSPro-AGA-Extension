#!/usr/bin/env python3
"""R80 real 68000 CPU Gate A: ILBM bytes -> exact AMOS chunky destination.

The emitted bytes execute under Unicorn with mocked OS/DOS and official
AMOS Bnk.GetAdr call. Checks complete 81920 pixels and sentinel memory.
This is NOT a WinUAE/Compiler runtime Gate B/C.
"""
from __future__ import annotations
import struct
from pathlib import Path
from hashlib import sha256
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from test_m5_generic import Machine, CODE, EXEC, DOSLIB, AMOS, NAME, STOP, STACK, DR, AR
from c2p_r80_iff_chunky_emit import emit_iff_to_chunky, BANK, CHUNKY
from build_c2p_r80_iff_chunky import build, API
from build_c2p_r79_zoom import build as build_r79
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from compiler_relocation import GETP
from test_c2p_iff_showcase import decode_iff

ROOT = Path(__file__).resolve().parents[1]
REAL = ROOT / "iff-TEST/AGA_DEMO_320x256_256c.iff"
BANK_SERVICE = 0x2800
BANKPTR = 0xb00000
ARGUMENTS = 0x58000
CANARY = b"R80_CHUNKY_BANK_END"


def chunk(tag, data):
    return tag + struct.pack(">I", len(data)) + data + (b"\0" if len(data) & 1 else b"")


def synthetic(depth, compressed):
    """Exact, independent indexed 4..8-plane ILBM in RAW or ByteRun1."""
    width, height = 320, 256
    pixels = bytes(
        ((x * 3 + y * 5 + ((x // 11) * 7)) & ((1 << depth) - 1))
        for y in range(height) for x in range(width)
    )
    body = bytearray()
    for y in range(height):
        row = pixels[y*width:(y+1)*width]
        for plane in range(depth):
            bits = bytes(sum(((row[x*8+b] >> plane) & 1) << (7-b)
                             for b in range(8)) for x in range(40))
            if compressed:
                body.append(39)  # one literal ByteRun1 packet, exactly 40 bytes
            body.extend(bits)
    bmhd = struct.pack(">HHhhBBBBHBBhh",
                       width, height, 0, 0, depth, 0, int(compressed), 0,
                       0, 1, 1, width, height)
    cmap = bytes((i * 17) & 255 for i in range(3 * (1 << depth)))
    payload = b"ILBM" + chunk(b"BMHD", bmhd) + chunk(b"CMAP", cmap)
    payload += chunk(b"CAMG", struct.pack(">I", 0x21000))
    payload += chunk(b"BODY", bytes(body))
    return b"FORM" + struct.pack(">I", len(payload)) + payload, pixels


def invalidate(data, tag, start, replacement):
    changed = bytearray(data)
    pos = changed.index(tag) + 8 + start
    changed[pos:pos+len(replacement)] = replacement
    return bytes(changed)


class NativeMachine(Machine):
    def __init__(self, data, *, bank=12, flags=1, banklen=CHUNKY,
                 bank_present=True, alloc_fail=0):
        # Use a verified but unmodified existing AP20 image as emulator map.
        parent, _ = build_r79()
        super().__init__(parent, data, meta=None, allocation_failure=alloc_fail)
        self.bank = bank
        self.bank_present = bank_present
        self.banklen = banklen
        self.bank_calls = 0
        self.type_calls = 0
        self.uc.mem_write(BANKPTR-24,
                          struct.pack(">IIIHH8s", 0, banklen+16, bank,
                                      flags, 0, b"C2PRAW  "))
        self.uc.mem_write(BANKPTR, b"\x9e" * CHUNKY)
        self.uc.mem_write(BANKPTR+CHUNKY, CANARY)
        code, _ = emit_iff_to_chunky()
        assert code.count(BANK) == 1
        code = code.replace(BANK, b"\x4e\xb9" + struct.pack(">I", BANK_SERVICE))
        self.uc.mem_write(CODE, code)
        self.uc.mem_write(BANK_SERVICE, b"\x4e\x75")
        self.uc.hook_add(UC_HOOK_CODE, self.bank_lookup,
                         begin=BANK_SERVICE, end=BANK_SERVICE)

    def return_call(self, value, *, bankptr=None):
        pc = self.get(self.a(7))
        self.uc.reg_write(AR[7], self.a(7) + 4)
        self.uc.reg_write(UC_M68K_REG_PC, pc)
        self.uc.reg_write(DR[0], value & 0xffffffff)
        self.uc.reg_write(DR[1], 0xdeadbeef)
        self.uc.reg_write(AR[0], 0xbad000 if bankptr is None else bankptr)
        self.uc.reg_write(AR[1], 0xbad100)

    def bank_lookup(self, uc, address, size, user):
        self.bank_calls += 1
        assert self.a(5) == AMOS
        ptr = BANKPTR if self.bank_present and self.d(0) == self.bank else 0
        self.return_call(0, bankptr=ptr)

    def os_call(self, uc, address, size, user):
        if address == EXEC - 534:
            self.type_calls += 1
            ptr = self.a(1)
            valid = BANKPTR-24 <= ptr < BANKPTR+self.banklen
            self.return_call(1 if valid else 0)
            return
        super().os_call(uc, address, size, user)

    def run_chunky(self, requested=None):
        for i, r in enumerate(DR):
            self.uc.reg_write(r, 0x1200 + i)
        for i, r in enumerate(AR[:7]):
            self.uc.reg_write(r, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], ARGUMENTS)
        self.put(ARGUMENTS, NAME)
        self.uc.reg_write(DR[3], self.bank if requested is None else requested)
        before = {r: self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE, STOP, count=50_000_000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4
        assert self.a(3) == ARGUMENTS + 4, "one AMOS parameter must be popped"
        for r, v in before.items():
            if r in (DR[2], DR[3], AR[3]):
                continue
            assert self.uc.reg_read(r) == v, ("ABI register corruption", r)
        assert self.d(2) == 0
        assert not self.owned and self.open_files == 0
        assert self.open_libraries == 0
        assert self.uc.mem_read(BANKPTR+CHUNKY, len(CANARY)) == CANARY
        return self.d(3), bytes(self.uc.mem_read(BANKPTR, CHUNKY))


def assert_valid(name, data, expected):
    machine = NativeMachine(data)
    actual_result, actual_pixels = machine.run_chunky()
    assert actual_result == 1, (name, actual_result)
    assert actual_pixels == expected, (
        name, "bad pixel", next((i for i,(a,b) in
        enumerate(zip(actual_pixels,expected)) if a != b), None))
    assert machine.bank_calls == 1, name
    assert machine.type_calls >= 3, name


def assert_reject(name, data, **kwargs):
    machine = NativeMachine(data, **kwargs)
    result, pixels = machine.run_chunky()
    assert result == 0, (name, result)
    assert pixels == b"\x9e" * CHUNKY, (name, "failed input changed bank")


def main():
    candidate, metadata = build()
    assert candidate == build()[0]
    tokens, parts = unwrap_native_parts_v2(candidate)
    parent, _ = build_r79()
    _, prev = unwrap_native_parts_v2(parent)
    assert len(parts) == 76 and len(prev) == 75
    assert parts[:74] == prev[:74] and parts[74] == prev[74] + GETP
    assert parts[75] == emit_iff_to_chunky()[0]
    assert metadata["commands"] == 70 and metadata["ap20_entries"] == 77
    assert API == ("aga iff to chunky", 1, 75, "02,0")
    real = REAL.read_bytes()
    real_pixels, _ = decode_iff(real)
    assert_valid("genuine fantasy IFF", real, real_pixels)
    cases = 1
    for depth in range(4, 9):
        for compression in (0, 1):
            data, pixels = synthetic(depth, compression)
            assert_valid("depth-%s-compression-%s" % (depth,compression),
                         data, pixels)
            cases += 1
    valid, _ = synthetic(8, 1)
    assert_reject("missing file", None)
    assert_reject("no destination bank", valid, bank_present=False)
    machine = NativeMachine(valid)
    result, pixels = machine.run_chunky(requested=4)
    assert result == 0 and pixels == b"\x9e" * CHUNKY
    assert_reject("bank too short", valid, banklen=CHUNKY-1)
    assert_reject("non-DATA flags", valid, flags=4)
    assert_reject("bad width", invalidate(valid,b"BMHD",0,b"\x01\x3f"))
    assert_reject("bad depth", invalidate(valid,b"BMHD",8,b"\x09"))
    assert_reject("masked ILBM", invalidate(valid,b"BMHD",9,b"\x01"))
    assert_reject("bad compression", invalidate(valid,b"BMHD",10,b"\x02"))
    assert_reject("HAM ILBM", invalidate(valid,b"CAMG",0,b"\x00\x02\x18\x00"))
    assert_reject("bad first ByteRun1 packet",invalidate(valid,b"BODY",0,b"\x7f"))
    assert_reject("truncated file",valid[:-11])
    print("R80 IFF->CHUNKY native CPU 68000 Gate A PASS", cases,
          "full 81920-pixel frames, invalid cases, unchanged rejection bank",
          metadata["size"], metadata["sha256"])


if __name__ == "__main__":
    main()
