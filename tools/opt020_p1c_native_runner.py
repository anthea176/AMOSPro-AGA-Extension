"""OPT020 P1c REAL native RLE + clipping runner on Musashi 68EC020/68020.

The Motorola instructions decode AGAPIC v1 row packets and decide both
horizontal and vertical visibility. The independent P1b native BFINS
routine paints full visible groups; the scalar remainder stays bounded.

NO AP20 ABI, Chip RAM ownership, executable Compiler, or hardware timing.
"""
from __future__ import annotations

from struct import pack
from machine68k import Machine, Register
from opt020_p1b_multiplane_emit import emit_masked_multiplane_020

from opt020_p1c_rle_clip_emit import (
    emit_rle_row_020, emit_clip_x_020, emit_clip_y_020
)

CODE_RLE = 0x1000
CODE_X = 0x1300
CODE_Y = 0x1600
TRAP = 0x1800
CODE_WRITER = 0x1a00
ROW = 0x4000
TABLE = 0x9000
SOURCE_WORDS = 0xa000
WRITER_TABLE = 0xb000
DEST_WORDS = 0xc000
STACK = 0x1f000
ROW_GUARD = bytes([0xa5] * 8)
TABLE_GUARD = bytes([0x5a] * 8)
CANARY_A3 = 0x2468ace0
CANARY_A5 = 0x719756eb
CANARY_D5 = 0x13579bdf


def _u32(n):
    return n & 0xffffffff


class RealNativeRLEClip:
    """Native subroutines, independent CPU execution for each call."""

    def __init__(self, kind):
        self.kind = kind
        self.machine = Machine(kind, 256)
        self.row_calls = 0
        self.row_rejections = 0
        self.clip_x_calls = 0
        self.clip_y_calls = 0
        self.write_calls = 0
        self.cycles = 0
        m = self.machine
        m.mem.w32(0, STACK)
        m.mem.w32(4, CODE_RLE)
        m.cpu.execute(m.cpu.pulse_reset())
        self.end = m.create_execute_end("opt020-p1c-return")
        trap = m.traps.alloc(lambda op, pc: self.end)
        assert 0 <= trap <= 4095
        m.mem.w16(TRAP, 0xa000 | trap)
        code = (
            (CODE_RLE, emit_rle_row_020()),
            (CODE_X, emit_clip_x_020()),
            (CODE_Y, emit_clip_y_020()),
            (CODE_WRITER, emit_masked_multiplane_020()),
        )
        for at, binary in code:
            assert len(binary) < 0x250
            m.mem.w_block(at, binary)

    def close(self):
        self.machine.cleanup()

    def _run(self, address, registers, budget=50000):
        m, cpu = self.machine, self.machine.cpu
        m.mem.w32(STACK, TRAP)
        cpu.w_sp(STACK)
        cpu.w_pc(address)
        cpu.w_reg(Register.A3, CANARY_A3)
        cpu.w_reg(Register.A5, CANARY_A5)
        for reg, value in registers.items():
            cpu.w_reg(reg, _u32(value))
        result = m.execute(budget)
        assert result.result is self.end, (
            "CPU did not return", self.kind, hex(address), cpu.r_pc(), result
        )
        assert cpu.r_sp() == STACK + 4, ("stack unbalanced", hex(address))
        assert cpu.r_reg(Register.A3) == CANARY_A3
        assert cpu.r_reg(Register.A5) == CANARY_A5
        self.cycles += result.sum_cycles
        return cpu

    def decode_row(self, row, group_bytes, group_count, *, expect_valid=True):
        """Read real native pointer table; do not interpret RLE in Python."""
        assert isinstance(row, bytes)
        assert 0 <= len(row) < TABLE - ROW - 16
        assert 0 <= group_count <= 1000
        m = self.machine
        table_bytes = 4 * min(group_count, 256)
        m.mem.w_block(ROW - 8, ROW_GUARD)
        m.mem.w_block(ROW, row + TABLE_GUARD)
        m.mem.w_block(TABLE - 8, ROW_GUARD)
        m.mem.w_block(TABLE, bytes([0xcc] * table_bytes) + TABLE_GUARD)
        regs = {
            Register.A0: ROW,
            Register.A1: ROW + len(row),
            Register.A2: TABLE,
            Register.D0: group_count,
            Register.D1: group_bytes,
            Register.D3: 0xabcd,
            Register.D5: CANARY_D5,
        }
        cpu = self._run(CODE_RLE, regs)
        assert cpu.r_reg(Register.D5) == CANARY_D5
        assert m.mem.r_block(ROW - 8, 8) == ROW_GUARD
        assert m.mem.r_block(ROW, len(row) + 8) == row + TABLE_GUARD
        assert m.mem.r_block(TABLE - 8, 8) == ROW_GUARD
        assert m.mem.r_block(TABLE + table_bytes, 8) == TABLE_GUARD
        valid = cpu.r_reg(Register.D3) == 1
        if not valid:
            assert cpu.r_reg(Register.D3) == 0
            self.row_rejections += 1
            if expect_valid:
                raise ValueError("Native 68020 RLE rejected validated row")
            return None
        assert expect_valid, "Native RLE accepted malformed source"
        assert cpu.r_reg(Register.A0) == ROW + len(row)
        assert cpu.r_reg(Register.A2) == TABLE + 4 * group_count
        self.row_calls += 1
        groups = []
        for index in range(group_count):
            pointer = m.mem.r32(TABLE + 4 * index)
            assert ROW <= pointer and pointer + group_bytes <= ROW + len(row), (
                "decoded group pointer out of row bounds", pointer, index)
            groups.append(m.mem.r_block(pointer, group_bytes))
        return tuple(groups)

    def clip_x(self, gx, sx, right, dx, dst_w, src_w):
        regs = {
            Register.D0: gx, Register.D1: sx, Register.D2: right,
            Register.D3: dx, Register.D4: dst_w, Register.D5: src_w,
        }
        cpu = self._run(CODE_X, regs)
        assert all(cpu.r_reg(reg) == _u32(val) for reg, val in (
            (Register.D0, gx), (Register.D1, sx), (Register.D2, right),
            (Register.D3, dx), (Register.D4, dst_w),
        ))
        lo, hi = cpu.r_reg(Register.D6), cpu.r_reg(Register.D7)
        assert 0 <= lo <= hi <= 16, (gx, sx, right, dx, dst_w, lo, hi)
        self.clip_x_calls += 1
        return lo, hi

    def clip_y(self, source_row, sy, dy, dst_h):
        regs = {
            Register.D0: source_row, Register.D1: sy,
            Register.D2: dy, Register.D3: dst_h,
        }
        cpu = self._run(CODE_Y, regs)
        assert all(cpu.r_reg(reg) == _u32(val) for reg, val in (
            (Register.D0, source_row), (Register.D1, sy),
            (Register.D2, dy), (Register.D3, dst_h)
        ))
        flag = cpu.r_reg(Register.D6)
        assert flag in (0, 1)
        got_y = cpu.r_reg(Register.D7)
        if flag:
            assert 0 <= got_y < dst_h
        self.clip_y_calls += 1
        return bool(flag), got_y

    def write_group(self, source_words, mask, shift, planes, offset):
        """Paint masked full group using the SAME Musashi machine and trap."""
        depth = len(source_words)
        assert 1 <= depth <= 8 and len(planes) == depth
        assert 0 <= mask <= 65535 and 0 <= shift < 8
        needed = 2 if shift == 0 else 3
        m = self.machine
        source = pack(">" + "H" * depth, *source_words)
        m.mem.w_block(SOURCE_WORDS, source)
        for i, plane in enumerate(planes):
            assert 0 <= offset <= len(plane) - needed
            payload = bytes(plane[offset:offset + needed])
            start = DEST_WORDS + i * 0x100
            m.mem.w_block(start, ROW_GUARD + payload + TABLE_GUARD)
            m.mem.w32(WRITER_TABLE + i * 4, start + 8)
        cpu = self._run(CODE_WRITER, {
            Register.A0: SOURCE_WORDS,
            Register.A1: WRITER_TABLE,
            Register.D0: shift,
            Register.D2: mask,
            Register.D3: 0,
            Register.D5: CANARY_D5,
            Register.D6: depth,
        }, 20000)
        assert cpu.r_reg(Register.D3) == 1
        assert cpu.r_reg(Register.D5) == CANARY_D5
        assert cpu.r_reg(Register.D0) == shift
        assert cpu.r_reg(Register.D2) == mask
        assert (cpu.r_reg(Register.D6) & 0xffff) == 0
        assert cpu.r_reg(Register.A0) == SOURCE_WORDS + 2 * depth
        assert cpu.r_reg(Register.A1) == WRITER_TABLE + 4 * depth
        assert m.mem.r_block(SOURCE_WORDS, len(source)) == source
        for i, plane in enumerate(planes):
            start = DEST_WORDS + i * 0x100
            payload = m.mem.r_block(start, 8 + needed + 8)
            assert payload[:8] == ROW_GUARD
            assert payload[8 + needed:] == TABLE_GUARD
            plane[offset:offset + needed] = payload[8:8 + needed]
        self.write_calls += 1
