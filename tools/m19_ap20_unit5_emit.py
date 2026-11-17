#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 AP20 V2: fifth, independent MC68020 diagnostic native unit.

SOURCE ONLY; never an alternate installable Lib or an ASC. This module
contains a deterministic 40-KiB data table which the near native function
really checksums; the second native function lies ABOVE the 32-KiB unsigned
offset boundary within the same compiler-copied V2 unit.

The diagnostic functions are exclusively for proving the AP20 architecture.
They are not new production graphics APIs. All source is generated here;
no disassembly/reconstruction from a binary is used as source authority.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, PRE, POST, I

DATA_BYTES = 40 * 1024
FAR_SIGNATURE = 0x005A0205
DATA = bytes(((i * 37) ^ (i >> 5) ^ 0xA5) & 0xFF
             for i in range(DATA_BYTES))
EXPECTED_SUM = 0x004FB000
assert len(DATA) == 40960 and sum(DATA) == EXPECTED_SUM


def emit_fifth_native() -> tuple[bytes, dict[str, int]]:
    """Generate two real callable routines plus a used deterministic table.

    Public no-argument function results are D3=value, D2=0. D0/D1/A0,
    all other non-result registers and the caller's stack are preserved.
    All code has a declared MC68020 minimum; legacy-compatible opcodes
    within that target are intentional.
    """
    c = Code()
    c.label('unit5_sum')
    # Save exactly the AMOS registers this checksum implementation uses.
    c.move(D(0), PRE(7))
    c.move(D(1), PRE(7))
    c.move(A(0), PRE(7))
    c.lea(0, 'unit5_data')          # PC16 only INSIDE the new unit, short.
    c.move(I(DATA_BYTES), D(0))
    c.move(I(0), D(3))
    c.label('unit5_loop')
    c.move(I(0), D(1))             # unsigned zero-extend byte to 32 bits
    c.move(POST(0), D(1), 'b')
    c.alu('add', D(1), 3, 'l')     # sum of all 40960 table bytes
    c.quick(1, D(0), sub=True)
    c.branch(6, 'unit5_loop')     # BNE.W local loop, never across units
    c.move(I(0), D(2))
    c.move(POST(7), A(0))
    c.move(POST(7), D(1))
    c.move(POST(7), D(0))
    c.raw('4e75')
    c.label('unit5_data')
    c.b.extend(DATA)
    c.label('unit5_tail')
    c.move(I(FAR_SIGNATURE), D(3))
    c.move(I(0), D(2))
    c.raw('4e75')
    native = c.out()
    labels = c.labels
    assert labels['unit5_sum'] == 0
    assert 0 < labels['unit5_data'] < 32766
    assert labels['unit5_tail'] - labels['unit5_data'] == DATA_BYTES
    assert 32768 < labels['unit5_tail'] < 65536
    assert native[labels['unit5_data']:labels['unit5_tail']] == DATA
    assert native[labels['unit5_tail']:] == bytes.fromhex('263c005a0205243c000000004e75')
    assert len(native) < 65534 - 34 and len(native) % 2 == 0
    return native, dict(labels, bytes=len(native), table_bytes=DATA_BYTES,
                        sum_expected=EXPECTED_SUM, tail_expected=FAR_SIGNATURE)


if __name__ == '__main__':
    from hashlib import sha256
    native,meta=emit_fifth_native()
    print('M19 AP20 V2 UNIT FIVE SOURCE ONLY MC68020',meta,
          'sha256',sha256(native).hexdigest(),
          'NOT INSTALLED / NO WINUAE GATE')
