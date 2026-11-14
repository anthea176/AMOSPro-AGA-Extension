#!/usr/bin/env python3
"""OPT020/P1e Gate A: REAL R60 bank/GetAdr/Safe/Bitmap plus CPU020 paint.

Musashi executes the complete native R60 entry (not a synthetic fragment
descriptor) including both bounded RLE passes and actual planar writes.
AMOS bank lookup and Exec services are trap-backed mocks, NOT WinUAE.
Both CPU-code placements are exercised, then an in-memory R68 Compiler V2
re-envelope checks the unchanged public tokens, GetP and relocation unit.
No library, ASC or LAST_GOOD is ever written.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack, pack_into

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000, CS_MODE_M68K_020
from machine68k import CPUType, Machine, Register

from audit_ap20 import inspect, parse
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, unpack_ap20, repack_ap20
from m16_agapic import pack_image, parse_payload, unpack_image
from m18_image_region_emit import emit_image_region, GETADR_MARKER

ROOT = Path(__file__).resolve().parents[1]
R68_SHA = "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
EXEC = 0x8000
BANK_SERVICE = 0x2800
END_TRAP = 0x1800
AMOS = 0x32000
STATE = 0x34000
DB = 0x34200
SB0 = 0x34400
SB1 = 0x34500
BITMAP0 = 0x34600
BITMAP1 = 0x34700
SAFE_PORT = 0x34800
BACK = 0x40000
FRONT = 0x80000
BANK = 0xc0000
PARAMS = 0xd0000
STACK = 0xe0000
WIDTH, HEIGHT, STRIDE = 64, 42, 12


def expected_planes(original, payload, sx, sy, w, h, x, y, mode, *, screen_width=WIDTH, screen_height=HEIGHT, stride=STRIDE):
    image = parse_payload(payload)
    colours, mask = unpack_image(image)
    out = [bytearray(p) for p in original]
    for iy in range(h):
        dy = y + iy
        if not 0 <= dy < screen_height:
            continue
        for ix in range(w):
            dx = x + ix
            if not 0 <= dx < screen_width:
                continue
            at = (sy + iy) * image.width + sx + ix
            if mode and not mask[at]:
                continue
            colour = colours[at]
            offset = dy * stride + (dx >> 3)
            bit = 0x80 >> (dx & 7)
            for plane in range(image.depth):
                if colour & (1 << plane):
                    out[plane][offset] |= bit
                else:
                    out[plane][offset] &= 255 ^ bit
    return tuple(bytes(v) for v in out)


class LiveRegionCPU:
    def __init__(self, kind, native, payload, *, base, depth, front,
                 bank_flag=1, pending=0, safe_ready=True, attnflags=2,
                 screen_width=WIDTH, screen_height=HEIGHT, stride=STRIDE,
                 invalid_mem_at=0, draw_api=False):
        self.m = Machine(kind, 1024)
        self.cpu = self.m.cpu
        self.mem = self.m.mem
        self.bank_calls = self.type_calls = self.getmsg_calls = 0
        self.pending = pending
        self.safe_ready = safe_ready
        self.payload = payload
        self.depth = depth
        self.base = base
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.stride = stride
        self.invalid_mem_at = invalid_mem_at
        self.draw_api = draw_api
        assert 1 <= screen_width <= 320 and 1 <= screen_height <= 256
        assert stride >= ((screen_width + 15) // 16) * 2 and stride % 2 == 0
        m = self.m
        m.mem.w32(0, STACK)
        m.mem.w32(4, base)
        self.cpu.execute(self.cpu.pulse_reset())
        self.mem.w32(4, EXEC)
        self.mem.w16(EXEC + 0x128, attnflags)
        self.end = m.create_execute_end("p1e-return")
        self._trap(END_TRAP, lambda _opcode, _pc: self.end)
        self._trap(BANK_SERVICE, self.lookup_bank)
        self._trap(EXEC - 534, self.type_of_mem)
        self._trap(EXEC - 372, self.get_msg)

        if draw_api:
            # P2 Image Draw receives Start/Length directly; it must NEVER
            # perform R60's Bnk.GetAdr lookup or change the public ABI.
            assert native.count(GETADR_MARKER) == 0
            patched = native
        else:
            assert native.count(GETADR_MARKER) == 1
            patched = native.replace(GETADR_MARKER,
                                     bytes.fromhex("4eb9") + pack(">I", BANK_SERVICE))
        assert len(patched) == len(native)
        self.mem.w_block(base, patched)

        # The real R60 context in A5: private AGA screen and two
        # Intuition ScreenBuffers. Only the INACTIVE one may be written.
        for off, val in (
            (0, 0x34a00), (8, 0x34b00), (12, screen_width),
            (16, screen_height), (28, depth), (32, DB),
        ):
            self.mem.w32(STATE + off, val)
        self.mem.w32(AMOS + 0x1c8, STATE)
        self.mem.w32(DB, SB0)
        self.mem.w32(DB + 4, SB1)
        self.mem.w32(DB + 8, front)
        self.mem.w32(DB + 12, SAFE_PORT)
        self.mem.w32(DB + 20, pending)
        self.mem.w32(SB0, BITMAP0)
        self.mem.w32(SB1, BITMAP1)

        self.backplanes = []
        self.frontplanes = []
        for i in range(depth):
            bp = BACK + 0x3000 * i
            fp = FRONT + 0x3000 * i
            self.backplanes.append(bp)
            self.frontplanes.append(fp)
            self.mem.w_block(bp, bytes((i * 29 + j * 17 + 0xa5) & 255
                                       for j in range(stride * screen_height)))
            self.mem.w_block(fp, bytes([0x33]) * (stride * screen_height))
            # 16-byte canaries outside each real planar allocation.
            for addr in (bp, fp):
                self.mem.w_block(addr - 16, bytes([0xc3]) * 16)
                self.mem.w_block(addr + stride * screen_height,
                                 bytes([0x5c]) * 16)
        # front=0 means SB0 is the displayed bitmap, SB1 the inactive;
        # front=1 reverses them.
        for bitmap, addresses in (
            (BITMAP0, self.frontplanes if front == 0 else self.backplanes),
            (BITMAP1, self.backplanes if front == 0 else self.frontplanes),
        ):
            self.mem.w_block(bitmap, pack(">HHBBH", stride, screen_height, 0, depth, 0))
            for i, ptr in enumerate(addresses):
                self.mem.w32(bitmap + 8 + 4 * i, ptr)

        self.mem.w_block(BANK, payload)
        self.mem.w_block(BANK - 24,
                         pack(">IIIHH8s", 0, len(payload) + 16, 10,
                              bank_flag, 0, b"AGAPIC  "))
        self.before = self.snapshot()
        self.front_before = tuple(self.mem.r_block(p, stride * screen_height)
                                  for p in self.frontplanes)

    def _trap(self, address, callback):
        ident = self.m.traps.alloc(callback)
        assert 0 <= ident <= 4095
        self.mem.w16(address, 0xa000 | ident)

    def return_to_caller(self, d0, *, a0=None):
        cpu = self.cpu
        sp = cpu.r_sp()
        address = self.mem.r32(sp)
        cpu.w_sp(sp + 4)
        cpu.w_pc(address)
        cpu.w_reg(Register.D0, d0 & 0xffffffff)
        cpu.w_reg(Register.D1, 0xdeadbeef)
        if a0 is not None:
            cpu.w_reg(Register.A0, a0)
            cpu.w_reg(Register.A1, a0)
        else:
            cpu.w_reg(Register.A0, 0xbad000)
            cpu.w_reg(Register.A1, 0xbad100)

    def lookup_bank(self, _opcode, _pc):
        self.bank_calls += 1
        assert self.cpu.r_reg(Register.A5) == AMOS
        found = BANK if self.cpu.r_reg(Register.D0) == 10 else 0
        self.return_to_caller(1 if found else 0, a0=found)

    def type_of_mem(self, _opcode, _pc):
        self.type_calls += 1
        address = self.cpu.r_reg(Register.A1)
        ok = int(BANK - 24 <= address < BANK + len(self.payload))
        if self.invalid_mem_at == self.type_calls:
            ok = 0
        self.return_to_caller(ok)

    def get_msg(self, _opcode, _pc):
        self.getmsg_calls += 1
        assert self.cpu.r_reg(Register.A0) == SAFE_PORT
        self.return_to_caller(0x34900 if self.safe_ready else 0)

    def snapshot(self):
        return tuple(self.mem.r_block(p, self.stride * self.screen_height)
                     for p in self.backplanes)

    def guard_ok(self):
        for addr in self.backplanes + self.frontplanes:
            assert self.mem.r_block(addr - 16, 16) == bytes([0xc3]) * 16
            assert self.mem.r_block(addr + self.stride * self.screen_height, 16) == bytes([0x5c]) * 16

    def run(self, *, bank=10, sx=3, sy=2, w=21, h=9, x=5, y=7,
            mode=0, expect_ok=True, source_len=None, source_start=None):
        if self.draw_api:
            # R46 current public API: Start(bank), Length(bank), X, Y, Mode.
            args = (y, x, len(self.payload) if source_len is None else source_len,
                    BANK if source_start is None else source_start)
        else:
            args = (y, x, h, w, sy, sx, bank)
        for i, value in enumerate(args):
            self.mem.w32(PARAMS + 4 * i, value & 0xffffffff)
        self.mem.w32(STACK, END_TRAP)
        cpu = self.cpu
        cpu.w_sp(STACK)
        cpu.w_pc(self.base)
        preserved = {
            Register.D0: 0x11223344,
            Register.D1: 0x22334455,
            Register.D4: 0x44556677,
            Register.D5: 0x55667788,
            Register.D6: 0x66778899,
            Register.D7: 0x778899aa,
            Register.A0: 0x41000,
            Register.A1: 0x42000,
            Register.A2: 0x43000,
            Register.A4: 0x44000,
            Register.A5: AMOS,
            Register.A6: 0x46000,
        }
        for reg, val in preserved.items():
            cpu.w_reg(reg, val)
        cpu.w_reg(Register.A3, PARAMS)
        cpu.w_reg(Register.D2, 0xfeed1234)
        cpu.w_reg(Register.D3, mode & 0xffffffff)
        result = self.m.execute(4_000_000)
        assert result.result is self.end, (self.base, cpu.r_pc(), result)
        assert cpu.r_sp() == STACK + 4, ("unbalanced A7", hex(cpu.r_sp()))
        assert cpu.r_reg(Register.A3) == PARAMS + len(args) * 4
        assert cpu.r_reg(Register.D2) == 0
        if cpu.r_reg(Register.D3) != int(expect_ok):
            print("P1e first-failure diagnostic", {
                "cpu": str(self.cpu), "base": hex(self.base),
                "bank_calls": self.bank_calls,
                "type_calls": self.type_calls,
                "getmsg_calls": self.getmsg_calls,
                "back_changed": self.snapshot() != self.before,
                "pending": self.mem.r32(DB + 20),
                "pc": hex(cpu.r_pc()),
                "A0": hex(cpu.r_reg(Register.A0)),
                "D0": hex(cpu.r_reg(Register.D0)),
                "D3": cpu.r_reg(Register.D3),
                "AttnFlags": self.mem.r16(EXEC + 0x128),
                "frame": {
                    key: hex(self.mem.r32(STACK - 4 * (0xefee).bit_count()
                                         - 192 + off))
                    for key, off in {
                        "row": 88, "pass": 92, "current": 96,
                        "end": 100, "decoded": 104, "left": 108,
                        "repeat": 112, "group": 116, "groups": 60,
                        "srcbit": 144, "visible_width": 184,
                    }.items()
                },
            }, flush=True)
        assert cpu.r_reg(Register.D3) == int(expect_ok), (
            "D3", self.base, cpu.r_reg(Register.D3), expect_ok)
        for reg, val in preserved.items():
            assert cpu.r_reg(reg) == val, ("preserved AP20 register", reg)
        assert self.snapshot() == (
            expected_planes(self.before, self.payload, sx, sy, w, h, x, y, mode,
                            screen_width=self.screen_width,
                            screen_height=self.screen_height, stride=self.stride)
            if expect_ok else self.before
        ), ("pixel or padding mismatch", self.base, mode, sx, sy, w, h, x, y)
        assert tuple(self.mem.r_block(p, self.stride * self.screen_height)
                     for p in self.frontplanes) == self.front_before
        # "Safe" must not be consumed for invalid or fully invisible regions.
        visible = (x < self.screen_width and y < self.screen_height and
                   x + w > 0 and y + h > 0)
        should_poll = bool((self.pending & 1) and visible and
                           (expect_ok or not self.safe_ready))
        if not expect_ok and self.safe_ready:
            should_poll = False
        assert self.getmsg_calls == int(should_poll), (
            "Safe polling", self.getmsg_calls, should_poll, x, y, w, h)
        expected_pending = self.pending & ~1 if expect_ok and visible else self.pending
        assert self.mem.r32(DB + 20) == expected_pending, (
            "Safe pending changed", self.mem.r32(DB + 20), expected_pending)
        self.guard_ok()
        return self.cpu.r_reg(Register.D3)

    def close(self):
        self.m.cleanup()


def v2_structure(native):
    from build_m18_r68_cblock import build as build_r68
    old = build_r68()[0]  # Historic R68 baseline, not moving LAST_GOOD.
    current = (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes()
    assert sha256(old).hexdigest() == R68_SHA, "historical R68 builder changed"
    if current != old:
        from build_opt020_p1e_r69 import build as build_r69
        from build_opt020_p2_r70 import build as build_r70
        from build_opt020_p2_r71 import build as build_r71, R71_SHA
        from build_opt020_p2_r72 import build as build_r72
        from build_opt020_p3_r73 import build as build_r73
        from build_c2p_r74_open import build as build_r74
        from build_c2p_r75_convert import build as build_r75
        from build_c2p_r76_rpg_fix import build as build_r76
        from build_c2p_r77_close import build as build_r77
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        r69, r69meta = build_r69()
        r70, r70meta = build_r70()
        r71, r71meta = build_r71()
        r72, r72meta = build_r72()
        r73, r73meta = build_r73()
        r74, r74meta = build_r74()
        r75, r75meta = build_r75()
        r76, r76meta = build_r76()
        r77, r77meta = build_r77()
        assert current in (r69, r70, r71, r72, r73, r74, r75, r76, r77), (
            "current must be an EXACT SHA-pinned R69..R77 deterministic build")
        assert r69meta["sha256"] == "9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"
        assert r70meta["sha256"] == "fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"
        assert r71meta["sha256"] == R71_SHA
        assert r72meta["sha256"] == "fdb98db259618fbdc3802843e2d6e836cb64acf2d68dc50bbe1133d46d36e67b"
        assert r73meta["sha256"] == "c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        assert r74meta["sha256"] == "887f29c0350f47af9d93d1ebf64fc405c8542e897ff0e7d9d95eda6f814c2a23"
        assert r75meta["sha256"] == "c5a5a0e45e5b07012247937bf1af0371836f0d119577c102d62a28f4ca1ad3af"
        assert r76meta["sha256"]=="9e0a77f3e69c06cfcc96b00b8dc1f23122d559f617beac8762310c5f4bb53897" and r76meta["leas_patched"]==7
        assert r77meta["sha256"]=="81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11"
        assert r77meta["commands"]==67 and r77meta["ap20_entries"]==74
        if current==r77:
            # Historical 68020 Region implementation must remain bit-identical.
            r69_parts=unwrap_native_parts_v2(r69)[1]
            r77_parts=unwrap_native_parts_v2(r77)[1]
            assert r77_parts[59]==r69_parts[59], "R77 altered historical Region bytes"
        if current in (r71, r72, r73, r74, r75, r76, r77):
            parts_current=unwrap_native_parts_v2(current)[1]
            assert_native_links(parts_current[:70])
            if current in (r74, r75, r76, r77):
                check_cross_r74(parts_current[:70])
    tokens, parts = unwrap_native_parts_v2(old)
    _, installed, title = unpack_ap20(old)
    assert len(parts) == 70 and len(installed) == 71
    assert parts[59].endswith(GETP)
    trial = list(parts)
    trial[59] = native + GETP
    source = repack_ap20(old, tokens, trial, title)
    wrapped = wrap_native_ap20_v2(source, title)
    assert unwrap_native_parts_v2(wrapped) == (tokens, trial)
    tt, entries, nt = unpack_ap20(wrapped)
    assert tt == tokens and nt == title and len(entries) == 71
    report = inspect(parse(wrapped))
    assert not report["issues"], report["issues"]
    assert len(entries[-1]) < 65534
    assert sha256((ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()).hexdigest() == "c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
    return len(wrapped), len(entries[-1])


def main():
    old, _ = emit_image_region()
    native, labels = emit_image_region(opt020=True)
    assert len(old) == 2012, "historical R60 emitter changed"
    assert old != native and native.count(GETADR_MARKER) == 1
    assert {"decode_rows", "paint_group", "p1e_full_16",
            "p1e_fragment", "p1e_clip_x", "safe", "reject"} <= set(labels)
    disasm = native.replace(GETADR_MARKER, bytes.fromhex("4eb900040000"))
    ins = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020).
               disasm(disasm, 0))
    assert sum(i.size for i in ins) == len(native)
    starts = {i.address for i in ins}
    assert all(v in starts for v in labels.values())
    # Every instruction before the first 020-only painter is still 68000 legal.
    prefix = disasm[:labels["paint_group"]]
    original_000 = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000).
                        disasm(prefix, 0))
    assert sum(i.size for i in original_000) == len(prefix)
    wrapper = v2_structure(native)

    pix = bytes((x * 3 + y * 5) % 16 for y in range(22) for x in range(57))
    mask = bytes(int((x * 7 + y) % 5 != 0) for y in range(22) for x in range(57))
    cases = 0
    for cpu in (CPUType.M68EC020, CPUType.M68020):
        for placement in (0x10000, 0x1c000):
            for masked in (False, True):
                payload = pack_image(57, 22, 4, pix, mask if masked else None)
                for front, rect in (
                    (0, (0, 0, 32, 10, 0, 0)),
                    (1, (3, 2, 21, 9, 5, 7)),
                    (0, (19, 5, 31, 12, -9, -4)),
                    (1, (1, 1, 17, 8, 59, 39)),
                    (0, (0, 0, 57, 22, 80, 60)),
                ):
                    sx, sy, w, h, x, y = rect
                    m = LiveRegionCPU(cpu, native, payload, base=placement,
                                      depth=4, front=front)
                    try:
                        m.run(sx=sx, sy=sy, w=w, h=h, x=x, y=y,
                              mode=int(masked))
                        cases += 1
                    finally:
                        m.close()
    payload = pack_image(57, 22, 4, pix, mask)
    malformed = bytearray(payload)
    pack_into(">I", malformed, 28, len(malformed) + 8)
    for opts in (
        dict(bank=4),
        dict(sx=-1),
        dict(w=0),
        dict(sx=56, w=2),
        dict(mode=2),
        dict(x=32768),
    ):
        m = LiveRegionCPU(CPUType.M68020, native, payload,
                          base=0x10000, depth=4, front=0, pending=1)
        try:
            m.run(expect_ok=False, **opts)
            assert m.getmsg_calls == 0
            cases += 1
        finally:
            m.close()
    for kw in (
        dict(bank_flag=2, payload=payload, pending=1, safe_ready=True),
        dict(bank_flag=1, payload=bytes(malformed), pending=1, safe_ready=True),
        dict(bank_flag=1, payload=payload, pending=1, safe_ready=False),
    ):
        m = LiveRegionCPU(CPUType.M68020, native, kw.pop("payload"),
                          base=0x10000, depth=4, front=0, **kw)
        try:
            m.run(expect_ok=False)
            cases += 1
        finally:
            m.close()
    for kind in (CPUType.M68000, CPUType.M68020):
        m = LiveRegionCPU(kind, native, payload, base=0x10000,
                          depth=4, front=0, attnflags=0)
        try:
            m.run(expect_ok=False)
            assert m.bank_calls == m.getmsg_calls == 0
            cases += 1
        finally:
            m.close()
    print("OPT020/P1e REAL R60 native 020 CPU Gate A PASS:", cases,
          "bank/GetAdr, strict RLE passes, Safe, Intuition bitmap, ABI")
    print("R60 unchanged:", len(old), "bytes; 020 native:",
          len(native), "SHA256", sha256(native).hexdigest())
    print("R68 Compiler V2 in-memory structure PASS:", wrapper,
          "no .Lib, LAST_GOOD, ASC or archive changed; no WinUAE gate")


if __name__ == "__main__":
    main()
