#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0h PRIVATE two-step 64-object bank-identity preflight for Bob Draw.

SOURCE ONLY: no API, Chip staging, DMA, Blitter or implicit Swap.
Traverse object IDs 1..64 in ascending order. An inactive raw object is
skipped; an active object whose bank stamp is stale aborts the WHOLE frame
BEFORE any future graphics operation. Uses P0g's independent BOBS->AGA
relay_checked_read to validate the saved source bank, not current selection.

Entry: A5=AMOS owner (screen must be open); no external buffer required.
Result D3=1 all objects safe (including empty list), 0 global refusal;
D2=0. Save AMOS D0/D1/D4-D7/A0-A2/A4-A6 and SP. All read targets are
source-verified private BOBS helpers, not new public AP20 commands.
The exact object snapshot/pixel checks and Chip staging are future work.
"""
from __future__ import annotations

from hashlib import sha256
from m68k_emit import Code, D, A, M, I
from m19_p0g_checked_read_emit import emit_checked_read
from m19_p0e_v2_object_bridge_emit import END_DELTA, END_SIGNATURE

NATIVE_P0H_BYTES = 16762
NATIVE_P0H_SHA256 = '2d5a9e7a7f53696427786e4cdaffd0786b9cbcdfa5b9f2039cdef480dcd6cc8b'
MAX_BOBS = 64
FRAME_BYTES = 128
RECORD_OFFSET = 64
RECORD_BYTES = 24
FRAME = dict(ident=0, result=4, state=8, active_count=12)
STATE_A5 = 0x1c8
assert RECORD_OFFSET + RECORD_BYTES <= FRAME_BYTES


def emit_frame_preflight() -> tuple[bytes, dict[str, int]]:
    old, old_labels = emit_checked_read()
    c = Code()
    c.raw(old.hex())
    c.labels.update(old_labels)
    B, L = c.branch, c.label

    def S(src, key):
        c.move(src, M(2, FRAME[key]))

    def G(key, dst):
        c.move(M(2, FRAME[key]), dst)

    def record_address():
        c.move(A(2), D(0))
        c.imm('add', RECORD_OFFSET, D(0))
        c.move(D(0), A(1))

    L('frame_bank_preflight_entry')
    c.raw('48e7efee')                # MOVEM.L AMOS preserved set
    c.raw('4fefff80')                # LEA -128(SP),SP
    c.move(A(7), A(2))
    S(I(0), 'result')
    S(I(0), 'active_count')

    # Reject unsupported CPU before touching the object table or AMOS state.
    B(1, 'registry_cpu_guard')
    c.tst(D(0)); B(7, 'frame_preflight_return')
    c.move(A(5), D(0)); c.tst(D(0))
    B(7, 'frame_preflight_return')
    c.imm('and', 1, D(0)); B(6, 'frame_preflight_return')
    # Verify the program A5 region before dereferencing its AGA state slot.
    c.move(A(5), D(0))
    c.imm('add', STATE_A5, D(0))
    B(5, 'frame_preflight_return')  # unsigned pointer wrap
    c.move(D(0), A(1))
    c.raw('2c780004')               # ExecBase
    c.call_os(-534)                 # TypeOfMem(A5+AGA State pointer)
    c.tst(D(0)); B(7, 'frame_preflight_return')
    c.move(M(5, STATE_A5), D(0))
    S(D(0), 'state')
    c.tst(D(0)); B(7, 'frame_preflight_return')
    c.imm('and', 1, D(0)); B(6, 'frame_preflight_return')
    G('state', A(1))
    c.raw('2c780004')
    c.call_os(-534)
    c.tst(D(0)); B(7, 'frame_preflight_return')
    G('state', A(0))
    c.tst(M(0, 0)); B(7, 'frame_preflight_return')  # live AGA Screen

    # The P0c mock may have a plausible temporary screen pointer.
    # Only the *original* AGA unit's native End prologue proves that
    # A5+$1c8 comes from real AGA Init, even after Compiler relocation.
    G('state', D(0))
    c.imm('cmp', END_DELTA, D(0)); B(5, 'frame_preflight_return')
    c.imm('sub', END_DELTA, D(0))
    c.move(D(0), A(4))
    c.move(A(4), A(1))
    c.raw('2c780004'); c.call_os(-534)  # TypeOfMem(original AGA End)
    c.tst(D(0)); B(7, 'frame_preflight_return')
    for index, word in enumerate(END_SIGNATURE):
        c.move(M(4, index*4), D(0))
        c.imm('cmp', word, D(0)); B(6, 'frame_preflight_return')

    S(I(1), 'ident')
    L('frame_preflight_next')
    G('ident', D(0))
    c.imm('cmp', MAX_BOBS, D(0))
    B(2, 'frame_preflight_all_checked') # BHI when ID > 64
    record_address()
    G('ident', D(0))
    B(1, 'relay_read_entry')        # inactive OR unreadable: D3=0
    c.tst(D(3))
    B(7, 'frame_preflight_advance') # inactive: no source bank to check

    # Raw read succeeded, so an invalid stamp is a HARD frame failure.
    # Reuse same private stack record; no caller data is published.
    record_address()
    G('ident', D(0))
    B(1, 'relay_checked_read_entry')
    c.tst(D(3))
    B(7, 'frame_preflight_return')
    G('active_count', D(0))
    c.quick(1, D(0))
    S(D(0), 'active_count')
    L('frame_preflight_advance')
    G('ident', D(0))
    c.quick(1, D(0))
    S(D(0), 'ident')
    B(0, 'frame_preflight_next')

    L('frame_preflight_all_checked')
    S(I(1), 'result')
    L('frame_preflight_return')
    G('result', D(3))
    c.raw('4fef0080')             # release private 128-byte frame
    c.raw('4cdf77f7')             # preserved registers
    c.raw('74004e75')             # D2=0; RTS

    native = c.out()
    if (not native.startswith(old) or c.labels['frame_bank_preflight_entry'] != len(old)
            or len(native) & 1 or len(native) >= 32766):
        raise ValueError('P0h preflight changed a frozen BOBS entry or exceeded V2 size')
    if not native[len(old):].startswith(bytes.fromhex('48e7efee4fefff80')):
        raise ValueError('Missing P0h private frame/ABI prologue')
    if len(native) != NATIVE_P0H_BYTES or sha256(native).hexdigest() != NATIVE_P0H_SHA256:
        raise ValueError('P0h native MC68020 source byte-exact drift')
    return native, c.labels


if __name__ == '__main__':
    blob, labels = emit_frame_preflight()
    print('M19 P0h PRIVATE MC68020 FRAME BANK PREFLIGHT SOURCE ONLY',
          'native bytes',len(blob),'appended',len(blob)-labels['frame_bank_preflight_entry'],
          'SHA256',sha256(blob).hexdigest(),'NO Chip/Blitter/Swap/active Lib')
