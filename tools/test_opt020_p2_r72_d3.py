#!/usr/bin/env python3
"""R72 OPT020/P2 late-rejection regression (native Musashi, not WinUAE).

A DATA bank can change *after* PASS 0's full RLE validation but *before*
PASS 1 starts painting. Simulate this exact race inside a nonblocking GetMsg
call. The last row is made invalid, after prior rows have used CPU020 bitfield
painters and left D3=1. R71 then incorrectly returns 1; R72 must return 0.

Prior writes cannot be rolled back when a caller concurrently changes the
source; the invariant tested here is only the D3 status + AP20 return ABI,
memory bounds and lack of writes in the invalid last row.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import unpack_from

from machine68k import CPUType, Register

from build_opt020_p2_r71 import R71_SHA, build as build_r71
from build_opt020_p2_r72 import build as build_r72
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from m16_agapic import pack_image
from m16_image_draw_r45_emit import emit_image_draw
from native_relative_links import assert_native_links
from test_opt020_p1e_region import (
    AMOS, BANK, DB, END_TRAP, PARAMS, STACK, LiveRegionCPU,
)
from test_opt020_p2_image_draw import check

ROOT = Path(__file__).resolve().parents[1]
R68_SHA = "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
PRESERVED = {
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


class MutateLastRowOnSafe(LiveRegionCPU):
    def __init__(self, native: bytes, payload: bytes, *, depth=4, front=0):
        super().__init__(
            CPUType.M68020, native, payload, base=0x1c000,
            depth=depth, front=front, pending=1, safe_ready=True,
            attnflags=2, draw_api=True, bank_flag=0
        )
        # BE row offset table starts at byte 32. Exactly two groups (17 px)
        # per row, so control=0x7F requests 128 groups -> reject.
        row_count = unpack_from(">H", payload, 14)[0]  # HEIGHT field
        self.last_row = row_count - 1
        self.last_row_offset = unpack_from(">I", payload, 32 + 4 * self.last_row)[0]
        assert self.last_row_offset < len(payload)
        assert self.mem.r_block(BANK + self.last_row_offset, 1) != b"\x7f"
        self.mutations = 0

    def get_msg(self, opcode, pc):
        # Called only after preflight PASS 0 is successful.
        # The base handler consumes the Safe message and returns to the
        # CPU with a nonzero pointer; we now change the still-resident bank.
        super().get_msg(opcode, pc)
        self.mem.w_block(BANK + self.last_row_offset, b"\x7f")
        self.mutations += 1


def late_failure(native: bytes, payload: bytes, *, expect_d3: int, mode=0) -> None:
    m = MutateLastRowOnSafe(native, payload)
    try:
        args = (7, 3, len(payload), BANK)
        for i, item in enumerate(args):
            m.mem.w32(PARAMS + 4 * i, item)
        m.mem.w32(STACK, END_TRAP)
        cpu = m.cpu
        cpu.w_sp(STACK)
        cpu.w_pc(m.base)
        for reg, value in PRESERVED.items():
            cpu.w_reg(reg, value)
        cpu.w_reg(Register.A3, PARAMS)
        cpu.w_reg(Register.D2, 0xfeed1234)
        cpu.w_reg(Register.D3, mode)

        result = m.m.execute(4_000_000)
        assert result.result is m.end, ("unexpected CPU exit", cpu.r_pc(), result)
        assert cpu.r_sp() == STACK + 4, "A7 not balanced"
        assert cpu.r_reg(Register.A3) == PARAMS + len(args) * 4, "AMOS A3 not consumed"
        assert cpu.r_reg(Register.D2) == 0, "AP20 D2 must be zero"
        assert cpu.r_reg(Register.D3) == expect_d3, (
            "late rejection status", cpu.r_reg(Register.D3), expect_d3
        )
        for reg, value in PRESERVED.items():
            assert cpu.r_reg(reg) == value, ("preserved register damaged", reg)
        assert m.mutations == m.getmsg_calls == 1
        assert m.mem.r32(DB + 20) == 0, "Safe pending not consumed"
        assert m.bank_calls == 0, "P2 never calls Bnk.GetAdr"

        after = m.snapshot()
        assert after != m.before, "PASS 1 never painted early rows; test is ineffective"
        for n, (initial, final) in enumerate(zip(m.before, after)):
            off = (7 + m.last_row) * m.stride
            assert initial[off:off + m.stride] == final[off:off + m.stride], (
                "corrupt last row was painted", n
            )
        assert tuple(
            m.mem.r_block(ptr, m.stride * m.screen_height)
            for ptr in m.frontplanes
        ) == m.front_before, "front buffer modified"
        m.guard_ok()
    finally:
        m.close()


def main() -> None:
    active = (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes()
    protected = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(protected).hexdigest() == "9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4"
    r71, _ = build_r71()
    assert sha256(r71).hexdigest() == R71_SHA
    r72, info = build_r72()
    assert r72 == build_r72()[0]
    tokens71, parts71 = unwrap_native_parts_v2(r71)
    tokens72, parts72 = unwrap_native_parts_v2(r72)
    assert tokens71 == tokens72 and len(parts71) == len(parts72) == 70
    assert_native_links(parts72)
    assert parts71[59] == parts72[59], "P1e Region baseline modified"
    assert {i for i, (a, b) in enumerate(zip(parts71, parts72)) if a != b} == (
        {20, 55, 57, 58}
    )
    old, _ = emit_image_draw(accept_loaded_flags_zero=True, opt020=True)
    new, _ = emit_image_draw(
        accept_loaded_flags_zero=True, opt020=True, reset_failure_d3=True
    )
    assert parts71[55].startswith(old)
    assert parts72[55].startswith(new)

    pixels = bytes(((i * 3 + j * 5) ^ (i >> 1)) & 15
                   for j in range(7) for i in range(17))
    # All pixels are enabled to ensure that the first rows paint and
    # leave D3=1 before the corrupted final row is decoded.
    payload = pack_image(17, 7, 4, pixels)

    # Demonstrates the previous bug and verifies the fix on real CPU flow.
    late_failure(old, payload, expect_d3=1)
    late_failure(new, payload, expect_d3=0)
    # Masked P2 must also preserve an explicit false result.
    masked_payload = pack_image(17, 7, 4, pixels, bytes([1]) * len(pixels))
    late_failure(new, masked_payload, expect_d3=0, mode=1)

    # Normal caller-visible P2 behavior is unchanged.
    for x, y, mode, expected in (
        (3, 7, 0, True), (-11, 3, 0, True),
        (64, 0, 0, True), (2, 1, 2, False)
    ):
        check(new, payload, 4, x=x, y=y, mode=mode,
              expect_ok=expected, w=17, h=7)

    assert (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes() == active, (
        "R72 CPU test may not modify the active library"
    )
    assert (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes() == protected
    print("R72 LATE PASS-1 REJECTION CPU GATE A PASS", info, flush=True)
    print("Historical R71 reproduced wrong D3=1; R72 returns D3=0.")
    print("No WinUAE or AMOS Compiler test performed.")


if __name__ == "__main__":
    main()
