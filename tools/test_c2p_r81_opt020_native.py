#!/usr/bin/env python3
"""R81: execute optimized C2P loops on real Musashi MC68020 CPU.

Reuses the pixel-exact and ABI-checked R78/R79 native harnesses; additionally
executes the actual R80 optimized nibble expansion on 68020 (4..8 planes,
odd bit patterns and canaries) and checks CPU000 rejection before 020 opcodes.
This is *native Gate A only*; no AMOS Compiler/WinUAE Gate B claim.
"""
from __future__ import annotations

from struct import unpack_from
from unittest.mock import patch

from machine68k import CPUType, Machine, Register
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

import test_c2p_r78_blit_gate_a as r78
import test_c2p_r79_zoom_gate_a as r79
from c2p_opt020_variants import (
    emit_blit_opt020, emit_zoom_opt020, emit_iff_chunky_opt020,
)
from c2p_r80_iff_chunky_emit import emit_iff_to_chunky
from build_c2p_r81_opt020 import build
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from compiler_relocation import GETP

CODE = 0x160000
EXEC = 0x8000
SOURCE = 0x90000
DEST = 0xa0000
CTX = 0xb0000
STACK = 0xd0000
STOP = 0x1800
CANARY = b"OPT020_R81_BANK_END"


def native_machine(cpu_type=CPUType.M68020):
    machine = Machine(cpu_type, 4096)
    mem, cpu = machine.mem, machine.cpu
    mem.w32(0, STACK)
    mem.w32(4, CODE)
    cpu.execute(cpu.pulse_reset())
    mem.w32(4, EXEC)
    mem.w16(EXEC + 0x128, 2 if cpu_type == CPUType.M68020 else 0)
    end = machine.create_execute_end("r81-020-end")
    mem.w16(STOP, 0xA000 | machine.traps.alloc(lambda _op, _pc: end))
    return machine, mem, cpu, end


def test_blit():
    # The original CPU harness checks exact pixels, clipping and AP20 ABI.
    cases = 0
    with patch.object(r78, "emit_blit", emit_blit_opt020):
        for depth in (4, 6, 8):
            cases += r78.run_valid(depth=depth, w=16, h=16)
        for width in (1, 2, 3, 4, 5, 7, 15, 17, 31, 32):
            cases += r78.run_valid(
                pitch=32, sx=0, sy=1, w=width, h=9, dx=17, dy=20
            )
        for geo in (
            dict(dx=-5, dy=-6), dict(dx=315, dy=251),
            dict(sx=7, sy=2, w=21, h=11, dx=41, dy=51),
            dict(w=32, h=32, dx=0, dy=0),
        ):
            cases += r78.run_valid(**geo)
        for label, args in (
            ("zero pitch", dict(pitch=0)),
            ("same bank", dict(bank=12)),
            ("outside screen", dict(dx=320)),
            ("source overflow", dict(sy=0x70000000, pitch=16)),
        ):
            cases += r78.run_reject(label, **args)
        cases += r78.cpu_000()
    return cases


def test_zoom():
    cases = 0
    with patch.object(r79, "emit_zoom", emit_zoom_opt020):
        for depth in (4, 5, 6, 7, 8):
            cases += r79.valid_case("zoom x2", depth=depth)
        for name, geo in (
            ("identity", dict(sw=32, sh=32, dw=32, dh=32)),
            ("shrink", dict(sw=32, sh=32, dw=13, dh=9)),
            ("noninteger", dict(sw=17, sh=13, dw=31, dh=27)),
            ("clip left", dict(sw=32, sh=32, dx=-8, dy=30, dw=64, dh=64)),
            ("clip top", dict(sw=32, sh=32, dx=30, dy=-9, dw=64, dh=64)),
            ("full destination", dict(sw=32, sh=32, dx=0, dy=0, dw=320, dh=256)),
        ):
            cases += r79.valid_case(name, **geo)
        for label, args in (
            ("bad pitch", dict(pitch=0)),
            ("same bank", dict(bank=12)),
        ):
            cases += r79.reject_case(label, **args)
        cases += r79.cpu_000()
    return cases


def planar_row(pixels, plane):
    return bytes(
        sum(((pixels[base + bit] >> plane) & 1) << (7 - bit)
            for bit in range(8))
        for base in range(0, 320, 8)
    )


def test_iff_expansion():
    code, labels = emit_iff_chunky_opt020()
    baseline, original_labels = emit_iff_to_chunky()
    assert len(code) > len(baseline)
    assert labels["byte_start"] == original_labels["byte_start"]
    assert labels["plane_done"] == original_labels["plane_done"]
    machine, mem, cpu, end = native_machine()
    mem.w_block(CODE, code)
    # Only in this isolated core harness: return when loop branches to the
    # original plane_done continuation. Never patch production output.
    mem.w16(CODE + labels["plane_done"], 0x4E75)
    total = 0
    for depth in range(4, 9):
        for seed in (1, 11, 69):
            pixels = bytes(
                ((x * 37 + (x >> 1) * 5 + seed * 19) ^ (x * x >> 2))
                & ((1 << depth) - 1)
                for x in range(320)
            )
            mem.w_block(DEST, bytes(320))
            mem.w_block(DEST + 320, CANARY)
            for plane in range(depth):
                src = planar_row(pixels, plane)
                mem.w_block(SOURCE, src)
                cpu.w_sp(STACK)
                mem.w32(STACK, STOP)
                cpu.w_reg(Register.A3, SOURCE)
                cpu.w_reg(Register.A4, DEST)
                cpu.w_reg(Register.D2, 39)
                cpu.w_reg(Register.D6, plane)
                cpu.w_pc(CODE + labels["byte_start"])
                run = machine.execute(150000)
                assert run.result is end, ("IFF optimized loop did not return", run)
                assert cpu.r_reg(Register.A3) == SOURCE + 40
                assert cpu.r_reg(Register.A4) == DEST + 320
                assert mem.r_block(DEST + 320, len(CANARY)) == CANARY
            assert mem.r_block(DEST, 320) == pixels, (
                "IFF pixel expansion differs", depth, seed
            )
            total += 1
    return total


def test_iff_cpu_000():
    # Startup guard must refuse CPU000 before reaching the indexed 020 LUT.
    code, labels = emit_iff_chunky_opt020()
    machine, mem, cpu, end = native_machine(CPUType.M68000)
    mem.w_block(CODE, code)
    mem.w_block(DEST, b"\xA5" * 320)
    cpu.w_reg(Register.A5, CTX)
    cpu.w_sp(STACK)
    mem.w32(STACK, STOP)
    cpu.w_pc(CODE + labels["chunky_decode"])
    run = machine.execute(10000)
    assert run.result is end, ("CPU000 guard did not return", run)
    assert cpu.r_reg(Register.D0) == 0
    assert mem.r_block(DEST, 320) == b"\xA5" * 320
    return 1


def main():
    image, meta = build()
    _, parts = unwrap_native_parts_v2(image)
    assert len(parts) == 76 and meta["commands"] == 70
    emitters = (
        emit_blit_opt020(), emit_zoom_opt020(), emit_iff_chunky_opt020()
    )
    for index, (code, labels) in zip((73, 74, 75), emitters):
        assert parts[index] == code + (GETP if index != 75 else b"")
        # Disassemble the full native entry, including appended 68020 code.
        ins = list(Cs(
            CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020
        ).disasm(code, 0))
        assert sum(i.size for i in ins) == len(code), (
            "Malformed 020 native instruction", index,
            [(x.address, x.mnemonic, x.op_str) for x in ins[-5:]]
        )
    b = test_blit()
    z = test_zoom()
    i = test_iff_expansion()
    guard = test_iff_cpu_000()
    assert image == build()[0], "R81 deterministic build failed"
    print("R81 OPT020 REAL 68020 GATE A PASS", b, "Blit",
          z, "Zoom", i, "IFF planar rows", guard, "CPU000 guard",
          "all 70 APIs/77 AP20 unchanged, SHA256", meta["sha256"],
          "WinUAE R81 / AMOS Compiler NOT TESTED")


if __name__ == "__main__":
    main()
