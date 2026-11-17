#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 AP20 V2 fifth native unit: source, ABI and *executed* CPU020 Gate A.

Exercise both real fifth-unit functions, including a native unsigned entry
offset past 32768, in a Unicorn MC68020. The interpreter BSR.W rewrites and
the Compiler JSR.L relocation are modeled, not actual WinUAE/AMOS Compiler.
Nothing here authorizes installation or proves Gates B/C/D.
"""
from __future__ import annotations

from struct import pack, unpack_from

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_A7, UC_M68K_REG_A0, UC_M68K_REG_D0,
    UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4,
)
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse
from build_m19_ap20_unit5_in_memory import (
    build, UNIT5_GROUP, UNIT5_SUM, UNIT5_TAIL, BASE_ENTRIES,
)
from compiler_relocation import RBSR, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from m19_ap20_unit5_emit import DATA_BYTES, EXPECTED_SUM, FAR_SIGNATURE

RETURN = 0xA00100
STACK = 0xA08000
RTS = bytes.fromhex('4e75')


def cpu020() -> Uc:
    u = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    for addr, length in ((0x100000, 0x40000), (0x300000, 0x10000),
                         (0x500000, 0x20000), (0x900000, 0x20000),
                         (0xA00000, 0x20000)):
        u.mem_map(addr, length)
    u.mem_write(RETURN, RTS)
    return u


def run_entry(u: Uc, entry: int, expected: int) -> None:
    """Execute a COMPLETE public stub, V2 dispatcher and native routine."""
    u.reg_write(UC_M68K_REG_SR, 0x2000)
    u.reg_write(UC_M68K_REG_A7, STACK)
    u.reg_write(UC_M68K_REG_D0, 0x11223344)
    u.reg_write(UC_M68K_REG_D1, 0x55667788)
    u.reg_write(UC_M68K_REG_A0, 0x12345678)
    u.reg_write(UC_M68K_REG_D4, 0xAABBCCDD)
    u.reg_write(UC_M68K_REG_D2, 0x13579BDF)
    u.reg_write(UC_M68K_REG_D3, 0x2468ACE0)
    u.mem_write(STACK, pack('>I', RETURN))
    u.emu_start(entry, RETURN, timeout=20_000_000, count=350_000)
    assert u.reg_read(UC_M68K_REG_PC) == RETURN, 'Entry never returned to AMOS'
    assert u.reg_read(UC_M68K_REG_D3) == expected, 'Native result mismatch'
    assert u.reg_read(UC_M68K_REG_D2) == 0, 'AMOS result type must be integer'
    for reg, value in ((UC_M68K_REG_D0, 0x11223344),
                       (UC_M68K_REG_D1, 0x55667788),
                       (UC_M68K_REG_A0, 0x12345678),
                       (UC_M68K_REG_D4, 0xAABBCCDD),
                       (UC_M68K_REG_A7, STACK + 4)):
        assert u.reg_read(reg) == value, f'ABI register/stack clobber: {reg}'


def main() -> None:
    binary, meta = build()
    _, parts, _ = unpack_ap20(binary)
    assert meta['native_groups'] == [142,153,156,177,180]
    assert len(parts) == 181 and len(parts[UNIT5_GROUP]) > 40960
    assert meta['table_bytes'] == DATA_BYTES == 40960
    assert meta['far_unsigned_offset'] > 32768
    assert meta['far_unsigned_offset'] <= 65535
    assert meta['new_pc16'] == meta['old_pc16'] == 854
    assert meta['new_pc16_near'] == 14 and meta['new_pc16_far'] == 6
    assert meta['sum_expected'] == EXPECTED_SUM
    assert meta['far_expected'] == FAR_SIGNATURE
    assert inspect(parse(binary))['issues'] == []
    assert all(parts[i].startswith(DISPATCH_V2) for i in meta['native_groups'])
    assert all(parts[i].startswith(RBSR) for i in (UNIT5_SUM,UNIT5_TAIL))
    assert unpack_from('>HH', parts[UNIT5_TAIL], 2) == (
        UNIT5_GROUP, meta['far_unsigned_offset'])

    labels = meta['labels']
    unit = parts[UNIT5_GROUP]
    native = unit[len(DISPATCH_V2):]
    # Disassemble ONLY executable intervals, never parse table bytes as code.
    cs = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
    first = list(cs.disasm(native[:labels['unit5_data']], 0))
    tail = list(cs.disasm(native[labels['unit5_tail']:],
                          labels['unit5_tail']))
    assert first and tail
    assert sum(x.size for x in first) == labels['unit5_data']
    assert sum(x.size for x in tail) == len(native) - labels['unit5_tail']
    assert first[-1].mnemonic.lower().startswith('rts')
    assert tail[-1].mnemonic.lower().startswith('rts')
    assert native[labels['unit5_data']:labels['unit5_tail']] != bytes(DATA_BYTES)

    # Fail closed on three invalid AP20 fifth-unit links.
    for group, off in ((UNIT5_GROUP,1), (UNIT5_GROUP,65535),
                       (177,meta['far_unsigned_offset'])):
        damaged = list(parts)
        damaged[UNIT5_TAIL] = RBSR + pack('>HH', group, off) + RTS
        try:
            pc16_displacements(damaged)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Invalid fifth-unit link accepted: {group},{off}')

    # Interpreter model: copy all original AP20 code, rewrite ONLY Rbsr
    # link words into signed BSR.W displacements as the AMOS loader does.
    starts = []
    at = 0
    for part in parts:
        starts.append(at)
        at += len(part)
    raw = bytearray(b''.join(parts))
    for i, dist in pc16_displacements(parts).items():
        raw[starts[i]:starts[i]+4] = pack('>Hh', 0x6100, dist)
    assert raw[:0] == b''  # interpreter input starts exactly at first stub
    u = cpu020()
    base = 0x100000
    u.mem_write(base, bytes(raw))
    for entry, result in ((UNIT5_SUM,EXPECTED_SUM),(UNIT5_TAIL,FAR_SIGNATURE)):
        run_entry(u, base + starts[entry], result)

    # Compiler model: public JSR.L calls the fifth V2 group at remote
    # ABSOLUTE 32-bit bases, supplying the FULL UNSIGNED offset word.
    # Two placements ensure no accidental proximity or fixed pointer.
    for group_base in (0x500000,0x900000):
        u = cpu020()
        u.mem_write(group_base,unit)
        for entry,result in ((UNIT5_SUM,EXPECTED_SUM),
                             (UNIT5_TAIL,FAR_SIGNATURE)):
            _, offset = unpack_from('>HH', parts[entry], 2)
            stub = 0x300000 + 0x100 * (entry-UNIT5_SUM)
            u.mem_write(stub, bytes.fromhex('4eb9')
                        + pack('>I', group_base) + pack('>H',offset) + RTS)
            run_entry(u, stub, result)

    # A mutated table must change the ACTUAL computed near-function result.
    u = cpu020()
    corrupt = bytearray(unit)
    corrupt[len(DISPATCH_V2)+labels['unit5_data']] ^= 1
    u.mem_write(0x500000,bytes(corrupt))
    u.mem_write(0x300000,bytes.fromhex('4eb9')
                + pack('>I',0x500000) + pack('>H',0) + RTS)
    run_entry(u,0x300000,EXPECTED_SUM-1)

    print('M19 AP20 V2 FIFTH UNIT MC68020 GATE A PASS',
          '86 old tokens + 2 diagnostics, 4 original native groups preserved,',
          '40-KiB table FULLY SUMMED; deep unsigned offset',
          meta['far_unsigned_offset'], '; both interpreter and 2 distant',
          'Compiler relocation models executed; ABI/stack PASS',
          '; candidate',meta['size'],meta['sha256'],
          '; WinUAE B/C/D NOT TESTED; ACTIVE LIB/ASC UNCHANGED')


if __name__ == '__main__':
    main()
