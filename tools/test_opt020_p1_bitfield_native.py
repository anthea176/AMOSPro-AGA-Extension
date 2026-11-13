#!/usr/bin/env python3
"""OPT020 P1: execute real CPU000 and CPU020 instructions with Musashi.

No AP20 wrapper, whole RLE decoder, WinUAE, Compiler or hardware timing.
Requires machine68k==0.4.0 and capstone==5.0.9.
"""
from __future__ import annotations

from hashlib import sha256
from random import Random

from capstone import (Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN,
                      CS_MODE_M68K_000, CS_MODE_M68K_020)
from machine68k import CPUType, Machine, Register

from opt020_p1_bitfield_emit import reference_68000, candidate_68020

CODE = 0x1000
TRAP = 0x1800
SRC = 0x3000
DST = 0x5000
STACK = 0xf000
GUARD_A3 = 0x2468ace0
GUARD_D5 = 0x13579bdf


def oracle(word: int, before: bytes, offset: int) -> bytes:
    """Independent, per-pixel MSB-first source-to-destination reference."""
    assert 0 <= offset <= 7 and len(before) >= 5
    out = bytearray(before)
    for i in range(16):
        bitpos = offset + i
        byte = bitpos // 8
        mask = 1 << (7 - (bitpos % 8))
        if word & (1 << (15 - i)):
            out[byte] |= mask
        else:
            out[byte] &= (255 ^ mask)
    return bytes(out)


def check_decoding() -> None:
    ref, candidate = reference_68000(), candidate_68020()
    assert candidate == bytes.fromhex("e9d01010efd1181076014e75")
    for data, mode, needs in (
            (ref, CS_MODE_M68K_000, ("btst", "bset", "bclr")),
            (candidate, CS_MODE_M68K_020, ("bfextu", "bfins"))):
        ins = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | mode).disasm(data, CODE))
        names = [i.mnemonic.lower() for i in ins]
        assert sum(i.size for i in ins) == len(data), (data.hex(), names)
        assert names[-1] == "rts", names
        assert all(name in names for name in needs), names


def run_code(cpu_type: CPUType, code: bytes, word: int,
             initial: bytes, offset: int) -> tuple[bytes, int]:
    m = Machine(cpu_type, 64)
    try:
        mem, cpu = m.mem, m.cpu
        mem.w32(0, STACK)
        mem.w32(4, CODE)
        cpu.execute(cpu.pulse_reset())
        end = m.create_execute_end("opt020-return")
        trap_id = m.traps.alloc(lambda opcode, pc: end)
        assert 0 <= trap_id <= 4095
        mem.w16(TRAP, 0xa000 | trap_id)
        mem.w_block(CODE, code)
        mem.w16(SRC, word)
        mem.w_block(DST, initial)
        mem.w32(cpu.r_sp(), TRAP)
        cpu.w_reg(Register.A0, SRC)
        cpu.w_reg(Register.A1, DST)
        cpu.w_reg(Register.D0, offset)
        cpu.w_reg(Register.D3, 0)
        cpu.w_reg(Register.D5, GUARD_D5)
        cpu.w_reg(Register.A3, GUARD_A3)
        sp = cpu.r_sp()
        result = m.execute(30000)
        assert result.result is end, (cpu_type, word, offset, cpu.r_pc(), result)
        assert cpu.r_reg(Register.D3) == 1
        assert cpu.r_reg(Register.A3) == GUARD_A3
        assert cpu.r_reg(Register.D5) == GUARD_D5
        assert cpu.r_sp() == sp + 4, ("SP", cpu_type, offset)
        assert mem.r16(SRC) == word
        return mem.r_block(DST, len(initial)), result.sum_cycles
    finally:
        m.cleanup()


def main() -> None:
    check_decoding()
    rng = Random(0x202068)
    words = [0, 0xffff, 0xa55a, 0x5aa5, 0x8000, 1, 0x7fff, 0x5555]
    words += [rng.randrange(65536) for _ in range(24)]
    programs = (
        ("68000", CPUType.M68000, reference_68000()),
        ("68EC020", CPUType.M68EC020, candidate_68020()),
        ("68020", CPUType.M68020, candidate_68020()),
    )
    totals = {name: 0 for name, _, _ in programs}
    count = 0
    for offset in range(8):
        for word in words:
            before = bytes(rng.randrange(256) for _ in range(8))
            expected = oracle(word, before, offset)
            for name, cpu_type, code in programs:
                actual, cycles = run_code(cpu_type, code, word, before, offset)
                assert actual == expected, (name, offset, word,
                                            actual.hex(), expected.hex())
                totals[name] += cycles
                count += 1
    print("OPT020/P1 native Musashi PASS:", count,
          "CPU emulated calls, 0 pixel/canary/register/stack errors")
    for name, _, code in programs:
        print(name, "code", len(code), "bytes SHA256", sha256(code).hexdigest())
    print("Musashi estimated cycles (NOT WinUAE/Amiga speed):", totals)
    print("NO AP20, no complete AGAPIC RLE, no mask/clip, no B/C/D gates")


if __name__ == "__main__":
    main()
