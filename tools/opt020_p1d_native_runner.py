"""OPT020 P1d native clipped-fragment support on the P1c single Musashi CPU.

All native writers/decoders share ONE Machine instance. Independent R60
bank/Safe preflight is still required before hardware integration.
"""
from __future__ import annotations
from struct import pack
from machine68k import Register
from opt020_p1c_native_runner import (
    RealNativeRLEClip, CODE_WRITER, SOURCE_WORDS, WRITER_TABLE,
    DEST_WORDS, ROW_GUARD, TABLE_GUARD, CANARY_D5)
from opt020_p1d_fragment_emit import emit_fragment_020

CODE_FRAGMENT = CODE_WRITER + 0x200
MASK_WORD = SOURCE_WORDS + 0x100


class RealNativeP1d(RealNativeRLEClip):
    def __init__(self, kind):
        super().__init__(kind)
        self.machine.mem.w_block(CODE_FRAGMENT, emit_fragment_020())
        self.fragment_calls = 0

    def write_fragment(self, source_words, mask, shift, left, width,
                       planes, offset):
        """REAL BFEXTU/BFINS field of width [1,16], preserving nonfield bits."""
        depth = len(source_words)
        assert 1 <= depth <= 8 and len(planes) == depth
        assert 0 <= mask <= 65535 and 0 <= shift < 8
        assert 0 <= left <= 15 and 1 <= width <= 16 - left
        needed = (shift + width + 7) // 8
        assert 1 <= needed <= 3
        m = self.machine
        src = pack(">" + "H" * depth, *source_words)
        m.mem.w_block(SOURCE_WORDS, src)
        m.mem.w16(MASK_WORD, mask)
        for i, plane in enumerate(planes):
            assert 0 <= offset <= len(plane) - needed
            start = DEST_WORDS + i * 0x100
            original = bytes(plane[offset:offset + needed])
            m.mem.w_block(start, ROW_GUARD + original + TABLE_GUARD)
            m.mem.w32(WRITER_TABLE + 4 * i, start + 8)
        cpu = self._run(CODE_FRAGMENT, {
            Register.A0: SOURCE_WORDS, Register.A1: MASK_WORD,
            Register.A2: WRITER_TABLE, Register.D0: shift,
            Register.D3: 0, Register.D4: left,
            Register.D5: CANARY_D5, Register.D6: width,
            Register.D7: depth,
        }, 20000)
        assert cpu.r_reg(Register.D3) == 1
        assert cpu.r_reg(Register.D0) == shift
        assert cpu.r_reg(Register.D4) == left
        assert cpu.r_reg(Register.D5) == CANARY_D5
        assert cpu.r_reg(Register.D6) == width
        assert (cpu.r_reg(Register.D7) & 0xffff) == 0
        assert cpu.r_reg(Register.A0) == SOURCE_WORDS + depth * 2
        assert cpu.r_reg(Register.A1) == MASK_WORD
        assert cpu.r_reg(Register.A2) == WRITER_TABLE + 4 * depth
        assert m.mem.r_block(SOURCE_WORDS, len(src)) == src
        assert m.mem.r16(MASK_WORD) == mask
        for i, plane in enumerate(planes):
            start = DEST_WORDS + i * 0x100
            buf = m.mem.r_block(start, 8 + needed + 8)
            assert buf[:8] == ROW_GUARD
            assert buf[8 + needed:] == TABLE_GUARD
            plane[offset:offset + needed] = buf[8:8 + needed]
        self.fragment_calls += 1
