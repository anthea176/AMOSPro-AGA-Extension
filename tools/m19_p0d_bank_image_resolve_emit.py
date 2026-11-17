#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0d: PRIVATE checked AGBO image -> staged Chip descriptor, SOURCE ONLY.

Append-only to the exact P0c native BOBS source. No AP20 token, no Lib build.
The selected AGBO bank must ALREADY have passed registry_prepare_entry and
program_end_arm_entry; this resolver never stages or frees memory itself.

Private call: A5=AMOS owner, D3=bank number, D0=1-based image ID,
              A1=caller-owned VALID writable 36-byte descriptor.
Result: D3=1 success / 0 refusal, D2=0. No bytes of the caller descriptor
are modified on failure. A3/A5/AMOS preserved registers and A7 unchanged.

Descriptor (nine big-endian longs):
    +0  Chip plane-0 address
    +4  independent 1-bit Chip mask address, or 0 for opaque
    +8  width pixels
    +12 height pixels
    +16 bytes-per-row (2*ceil(width/16))
    +20 depth (1..8)
    +24 bytes per plane (stride*height)
    +28 owner Chip allocation start
    +32 owner Chip allocation byte count

The P0c registry_lookup_entry revalidates live AMOS selection, actual bank
pointer, AGBO generation and staged identity. The new code independently
bounds the requested image's colour and mask ranges INSIDE the verified
contiguous private Chip allocation; never returns an address into Fast.
It does not support arbitrary in-place AGBO Poke, nor a foreign owner A5.
The caller owns the descriptor lifetime and must not release/re-stage Chip
until the synchronous Bob paint/WaitBlit has completed.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I
from m19_p0c_program_end_bridge_emit import emit_program_end_bridge

COOKIE = 0x43484950
FRAME = 192
K = (
    'bank image output payload count data_start entry cursor remain node '
    'chip_ptr chip_len generation pix_off pix_len mask_off mask_len flags '
    'width height depth stride plane_bytes total_bytes relative '
    'pixel_ptr mask_ptr result'
).split()
F = {name: 4*i for i, name in enumerate(K)}
assert 4*len(F) <= FRAME

def emit_bank_image_resolve() -> tuple[bytes, dict[str,int]]:
    old, labels = emit_program_end_bridge()
    c = Code()
    c.raw(old.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label

    def S(src, name):
        c.move(src, M(2, F[name]))

    def G(name, dst):
        c.move(M(2, F[name]), dst)

    def bounded_span(offset_name, len_name, result_name):
        # Result = chip allocation base + (AGBO offset - data_start).
        # Reject unsigned underflow/overflow or a span past the allocation.
        G(offset_name, D(0))
        G('data_start', D(1))
        c.alu('cmp', D(1), 0)
        B(5, 'resolve_fail')           # BCS: offset before data start
        c.alu('sub', D(1), 0)
        S(D(0), 'relative')
        G('chip_len', D(1))
        G(len_name, D(7))
        c.alu('sub', D(7), 1)
        B(5, 'resolve_fail')           # len > chip_len
        c.alu('cmp', D(1), 0)
        B(2, 'resolve_fail')           # rel > chip_len - len
        G('chip_ptr', D(1))
        c.alu('add', D(1), 0)
        B(5, 'resolve_fail')           # address wraps
        S(D(0), result_name)

    L('bank_image_resolve_entry')
    c.raw('48e7efee')                 # save AMOS-preserved regs, not D2/D3/A3
    c.raw('4fefff40')                 # LEA -192(SP),SP
    c.move(A(7), A(2))
    S(D(3), 'bank')
    S(D(0), 'image')
    S(A(1), 'output')
    S(I(0), 'result')
    S(I(0), 'mask_ptr')

    # No bank-state access on CPUs below the declared MC68020 minimum.
    B(1, 'registry_cpu_guard')
    c.tst(D(0)); B(7, 'resolve_fail')
    G('image', D(0))
    c.imm('cmp', 1, D(0)); B(5, 'resolve_fail')
    c.imm('cmp', 4096, D(0)); B(2, 'resolve_fail')
    G('output', D(0))
    c.tst(D(0)); B(7, 'resolve_fail')
    c.imm('and', 1, D(0)); B(6, 'resolve_fail')

    # Lookup MUST confirm that the selected AMOS bank, its pointer and its
    # AGBO generation still match the staged per-bank Chip context.
    G('bank', D(3))
    B(1, 'registry_lookup_entry')
    c.tst(D(3)); B(7, 'resolve_fail')

    c.lea(0, 'bank_active_state')
    c.move(M(0, 4), D(0)); S(D(0), 'payload')
    c.tst(D(0)); B(7, 'resolve_fail')
    # Zero-byte anchor: P0j-b3 can supply a verified payload directly
    # without changing historical P0d resolver machine-code bytes.
    L('resolve_live_payload')
    c.move(D(0), A(0))
    c.move(I(0), D(0))
    c.move(M(0, 8), D(0), 'w')
    c.imm('cmp', 1, D(0)); B(5, 'resolve_fail')
    c.imm('cmp', 4096, D(0)); B(2, 'resolve_fail')
    S(D(0), 'count')
    c.word(0xc0fc); c.word(40)        # MULU.W #40,D0
    c.imm('add', 32, D(0))
    S(D(0), 'data_start')
    G('payload', D(0))
    c.imm('add', 32, D(0)); B(5, 'resolve_fail')
    S(D(0), 'entry')
    S(I(0), 'cursor')

    # Directory is guaranteed well formed by checked_stage, and the live
    # generation/payload identity was revalidated above. Still bound each
    # individual lookup; image IDs are NOT directory indices.
    L('resolve_image_loop')
    G('cursor', D(0)); G('count', D(1))
    c.alu('cmp', D(1), 0); B(12, 'resolve_fail')
    G('entry', A(0))
    c.move(I(0), D(0))
    c.move(M(0, 0), D(0), 'w')
    G('image', D(1))
    c.alu('cmp', D(1), 0)
    B(7, 'resolve_image_found')
    G('entry', D(0))
    c.imm('add', 40, D(0)); B(5, 'resolve_fail')
    S(D(0), 'entry')
    G('cursor', D(0)); c.quick(1, D(0))
    S(D(0), 'cursor')
    B(0, 'resolve_image_loop')

    L('resolve_image_found')
    c.lea(0, 'registry_state')
    c.move(M(0, 0), D(0))
    c.move(A(5), D(1))
    c.alu('cmp', D(1), 0); B(6, 'resolve_fail')
    c.lea(0, 'registry_state')
    c.move(M(0, 4), D(0)); S(D(0), 'node')
    S(I(256), 'remain')

    L('resolve_node_loop')
    G('node', D(0)); c.tst(D(0)); B(7, 'resolve_fail')
    G('remain', D(1)); c.tst(D(1)); B(7, 'resolve_fail')
    c.quick(1, D(1), sub=True); S(D(1), 'remain')
    G('node', A(0))
    c.move(M(0, 4), D(0))
    G('bank', D(1))
    c.alu('cmp', D(1), 0)
    B(7, 'resolve_node_found')
    G('node', A(0)); c.move(M(0, 0), D(0))
    S(D(0), 'node')
    B(0, 'resolve_node_loop')

    L('resolve_node_found')
    G('node', A(0))
    c.move(M(0, 8), D(0)); S(D(0), 'chip_ptr')
    c.move(M(0, 12), D(0)); S(D(0), 'chip_len')
    c.move(M(0, 24), D(0))
    c.imm('cmp', COOKIE, D(0)); B(6, 'resolve_fail')
    c.move(M(0, 16), D(0))
    G('payload', D(1)); c.alu('cmp', D(1), 0)
    B(6, 'resolve_fail')
    c.move(M(0, 20), D(0)); S(D(0), 'generation')
    G('payload', A(0))
    c.move(M(0, 24), D(1))
    c.alu('cmp', D(1), 0); B(6, 'resolve_fail')
    G('chip_ptr', D(0))
    c.tst(D(0)); B(7, 'resolve_fail')
    c.imm('and', 1, D(0)); B(6, 'resolve_fail')

    G('entry', A(0))
    for name, off, upper in (('width',2,4096), ('height',4,4096),
                             ('depth',6,8), ('stride',8,512)):
        c.move(I(0), D(0)); c.move(M(0, off), D(0), 'w')
        c.imm('cmp', 1, D(0)); B(5, 'resolve_fail')
        c.imm('cmp', upper, D(0)); B(2, 'resolve_fail')
        S(D(0), name)
    G('width', D(0)); c.imm('add',15,D(0))
    c.shift(0,4); c.shift(0,1,left=True)
    G('stride', D(1)); c.alu('cmp', D(1), 0)
    B(6, 'resolve_fail')
    G('stride', D(0)); G('height', D(1))
    c.word(0xc0c1)                   # MULU.W D1,D0
    S(D(0), 'plane_bytes')

    G('entry', A(0))
    c.move(I(0), D(0)); c.move(M(0,10), D(0), 'w')
    c.imm('cmp',1,D(0)); B(2,'resolve_fail')
    S(D(0),'flags')
    c.move(M(0,12),D(0)); S(D(0),'pix_off')
    c.move(M(0,16),D(0)); S(D(0),'pix_len')
    c.move(M(0,20),D(0)); S(D(0),'mask_off')
    c.move(M(0,24),D(0)); S(D(0),'mask_len')

    # Expected pixel length = plane_bytes * depth, in 32-bit arithmetic;
    # never use 16-bit MULU with a potentially >65535 plane size.
    S(I(0), 'total_bytes')
    G('depth', D(7))
    L('resolve_depth_loop')
    G('total_bytes', D(0))
    G('plane_bytes', D(1))
    c.alu('add', D(1), 0)
    B(5, 'resolve_fail')
    S(D(0), 'total_bytes')
    c.quick(1, D(7), sub=True)
    B(6, 'resolve_depth_loop')
    G('pix_len', D(0)); G('total_bytes', D(1))
    c.alu('cmp', D(1), 0); B(6, 'resolve_fail')
    bounded_span('pix_off','pix_len','pixel_ptr')

    G('flags', D(0)); c.tst(D(0))
    B(7, 'resolve_no_mask')
    G('mask_len', D(0)); G('plane_bytes', D(1))
    c.alu('cmp', D(1), 0); B(6, 'resolve_fail')
    bounded_span('mask_off','mask_len','mask_ptr')
    B(0, 'resolve_write')
    L('resolve_no_mask')
    G('mask_len', D(0)); c.tst(D(0)); B(6, 'resolve_fail')
    G('mask_off', D(0)); c.tst(D(0)); B(6, 'resolve_fail')

    # All checks passed; now and ONLY now publish the 9-long descriptor.
    L('resolve_write')
    G('output', A(0))
    for field in ('pixel_ptr', 'mask_ptr','width','height','stride',
                  'depth','plane_bytes','chip_ptr','chip_len'):
        G(field, D(0))
        c.move(D(0), M(0))
        c.quick(4, A(0))
    S(I(1),'result')

    L('resolve_fail')
    G('result',D(3))
    c.raw('4fef00c0')            # LEA +192(SP),SP
    c.raw('4cdf77f7')            # restore preserved AMOS caller registers
    c.raw('74004e75')            # D2=0; RTS
    raw = c.out()
    assert raw[:len(old)] == old, 'never patch installed P0c source'
    assert c.labels['bank_image_resolve_entry'] == len(old)
    assert len(raw) < 32766 and not (len(raw)&1)
    return raw, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    raw, labels = emit_bank_image_resolve()
    print('M19 P0d private MC68020 image descriptor SOURCE ONLY',
          len(raw), sha256(raw).hexdigest(),
          labels['bank_image_resolve_entry'],
          'no AP20/Lib/WinUAE claim')
