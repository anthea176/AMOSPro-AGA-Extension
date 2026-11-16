#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0c PRIVATE checked AGBO bank -> Chip staging; NO AP20 token or Lib.

This is source assembled from the frozen, CPU-tested P0b BOBS emitter and
the independently CPU-tested private Chip lifecycle emitter. It appends
one PRIVATE entry to the SAME native unit, reusing the checked P0a planar
padding helper and P0b selected-bank identity contract; neither existing
entry point nor its bytes are modified.

Entry: A5 = current AMOS program context, D3 = selected AMOS bank number,
       A1 = caller-owned 20-byte stage context (one per bank), A4 = valid
       graphics.library base for replacement. Output: D3 = 1/0, D2 = 0.
First validate complete live AGBO data: bank identity/header, all image
IDs, dimension/stride/depth/offset/order/size/padding/mask entries. Then
pass ONLY the validated contiguous planar data to stage_entry.

WARNING: source-only private experiment, no integrated per-bank registry
or Bob objects, no new .Lib, no WinUAE/Compiler or physical DMA proof.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I
from amos_main_abi import main_index, rjsr
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5
from m19_p0b_masks_emit import emit_mask_commands
from m19_p0c_chip_stage_emit import emit_chip_stage

GETADR = rjsr(main_index('Bnk.GetAdr'))
FRAME = 176
K = ('bank ctx gfx bankptr head payload_size count data_start generation '
     'cursor entry index prev_id width height depth stride plane_size '
     'pixels_len mask_len flags result source data_size').split()
F = {name: n * 4 for n, name in enumerate(K)}
assert len(K)*4 <= FRAME


def emit_checked_bank_stage() -> tuple[bytes, dict[str, int]]:
    prefix, previous_labels = emit_mask_commands()
    chip, chip_labels = emit_chip_stage()
    c = Code()
    c.raw(prefix.hex())
    c.labels.update(previous_labels)
    B, L = c.branch, c.label

    def S(src, name):
        c.move(src, M(2, F[name]))

    def G(name, dst):
        c.move(M(2, F[name]), dst)

    def reject():
        B(0, 'checked_fail')

    def add(dst, src):
        c.alu('add', src, dst)
        B(5, 'checked_fail')  # BCS: size/address overflow

    def osbase():
        c.raw('2c780004')  # MOVEA.L (4).W,A6

    def typeof(name):
        G(name, A(1))
        osbase()
        c.call_os(-534)
        c.tst(D(0))
        B(7, 'checked_fail')

    L('checked_stage_entry')
    c.raw('48e7efee')       # AMOS ABI preserved set
    c.raw('4fefff50')       # LEA -176(SP),SP
    c.move(A(7), A(2))
    S(D(3), 'bank')
    S(A(1), 'ctx')
    S(A(4), 'gfx')
    S(I(0), 'result')
    c.move(I(0), D(3))

    # Reject <020 BEFORE dereferencing any AMOS bank data.
    c.raw('20780004')       # MOVEA.L (4).W,A0
    c.move(A(0), D(0))
    c.tst(D(0)); B(7, 'checked_fail')
    c.move(M(0, 0x128), D(0), 'w')
    c.word(0x0800); c.word(1)     # BTST #AFF_68020,D0
    B(7, 'checked_fail')
    G('ctx', D(0))
    c.tst(D(0)); B(7, 'checked_fail')
    c.imm('and', 1, D(0)); B(6, 'checked_fail')
    G('bank', D(0))
    c.imm('cmp', 5, D(0)); B(5, 'checked_fail')
    c.imm('cmp', 65535, D(0)); B(2, 'checked_fail')

    # The active Bob bank selection must match the live AMOS list and pointer.
    c.lea(0, 'bank_active_state')
    c.move(M(0, 0), D(1))
    G('bank', D(0))
    c.alu('cmp', D(1), 0); B(6, 'checked_fail')
    c.move(M(0, 4), D(0)); S(D(0), 'bankptr')
    c.tst(D(0)); B(7, 'checked_fail')
    c.move(M(0, 8), D(0)); S(D(0), 'head')
    c.tst(D(0)); B(7, 'checked_fail')
    c.move(M(5, CUR_BANKS_A5), D(0))
    G('head', D(1))
    c.alu('cmp', D(1), 0); B(6, 'checked_fail')
    G('bank', D(0)); c.raw(GETADR.hex())
    c.move(A(0), D(0))
    G('bankptr', D(1))
    c.alu('cmp', D(1), 0); B(6, 'checked_fail')
    c.imm('cmp', 24, D(0)); B(3, 'checked_fail')
    c.move(D(0), D(1)); c.imm('and', 1, D(1)); B(6, 'checked_fail')

    # Probe AMOS bank header region through Exec before reading its size.
    G('bankptr', D(0))
    c.imm('sub', 24, D(0))
    S(D(0), 'source')
    typeof('source')
    G('bankptr', A(4))
    c.move(M(4, -20), D(0))
    c.imm('cmp', 48, D(0)); B(5, 'checked_fail')
    c.imm('cmp', 0x01000010, D(0)); B(2, 'checked_fail')
    c.imm('sub', 16, D(0))
    S(D(0), 'payload_size')
    G('bankptr', D(0))
    G('payload_size', D(1))
    add(0, D(1))
    c.quick(1, D(0), sub=True)
    S(D(0), 'source')
    typeof('source')

    G('bankptr', A(4))
    c.move(M(4, -16), D(0))
    G('bank', D(1))
    c.alu('cmp', D(1), 0); B(6, 'checked_fail')
    c.move(I(0), D(0))
    c.move(M(4, -12), D(0), 'w')
    c.tst(D(0)); B(7, 'checked_flags_ok')
    c.imm('and', 0xfffd, D(0), 'w')
    c.imm('cmp', 1, D(0), 'w'); B(6, 'checked_fail')
    L('checked_flags_ok')
    c.move(M(4, -8), D(0))
    c.imm('cmp', 0x41474142, D(0)); B(6, 'checked_fail')
    c.move(M(4, -4), D(0))
    c.imm('cmp', 0x4f425320, D(0)); B(6, 'checked_fail')
    c.move(M(4, 0), D(0))
    c.imm('cmp', 0x4147424f, D(0)); B(6, 'checked_fail')
    c.move(I(0), D(0))
    c.move(M(4, 4), D(0), 'w')
    c.imm('cmp', 1, D(0)); B(6, 'checked_fail')
    c.tst(M(4, 6), 'w'); B(6, 'checked_fail')
    c.move(I(0), D(0))
    c.move(M(4, 8), D(0), 'w')
    # Staging needs at least one actual image; empty banks are valid but empty.
    c.imm('cmp', 1, D(0)); B(5, 'checked_fail')
    c.imm('cmp', 4096, D(0)); B(2, 'checked_fail')
    S(D(0), 'count')
    c.move(I(0), D(0))
    c.move(M(4, 10), D(0), 'w')
    c.imm('cmp', 40, D(0)); B(6, 'checked_fail')
    c.move(M(4, 12), D(0))
    c.imm('cmp', 32, D(0)); B(6, 'checked_fail')
    G('count', D(0))
    c.raw('c0fc0028')     # MULU.W #40,D0
    c.imm('add', 32, D(0))
    S(D(0), 'data_start')
    G('bankptr', A(4))
    c.alu('cmp', M(4, 16), 0); B(6, 'checked_fail')
    G('payload_size', D(1))
    c.alu('cmp', D(1), 0); B(2, 'checked_fail')
    c.move(M(4, 20), D(0))
    G('payload_size', D(1))
    c.alu('cmp', D(1), 0); B(6, 'checked_fail')
    c.move(M(4, 24), D(0))
    c.tst(D(0)); B(7, 'checked_fail')
    S(D(0), 'generation')
    c.tst(M(4, 28)); B(6, 'checked_fail')
    G('data_start', D(0))
    S(D(0), 'cursor')
    G('bankptr', D(0))
    c.imm('add', 32, D(0))
    S(D(0), 'entry')
    for field in ('index', 'prev_id'):
        S(I(0), field)

    # Strict validation of EVERY image, including mask, all planar padding,
    # offset contiguity, duplicate/unsorted ID and reserved bytes.
    L('checked_loop')
    G('index', D(0))
    G('count', D(1))
    c.alu('cmp', D(1), 0)
    B(12, 'checked_all_entries')

    G('entry', A(4))
    c.move(I(0), D(0))
    c.move(M(4, 0), D(0), 'w')
    G('prev_id', D(1))
    c.alu('cmp', D(1), 0); B(3, 'checked_fail')
    c.imm('cmp', 4096, D(0)); B(2, 'checked_fail')
    S(D(0), 'prev_id')
    for off, field, upper in ((2, 'width', 4096), (4, 'height', 4096),
                              (6, 'depth', 8)):
        c.move(I(0), D(0))
        c.move(M(4, off), D(0), 'w')
        c.imm('cmp', 1, D(0)); B(5, 'checked_fail')
        c.imm('cmp', upper, D(0)); B(2, 'checked_fail')
        S(D(0), field)
    G('width', D(0))
    G('height', D(1))
    c.word(0xc0c1)         # MULU.W D1,D0
    c.imm('cmp', 0x400000, D(0)); B(2, 'checked_fail')

    G('width', D(0))
    c.imm('add', 15, D(0))
    c.shift(0, 4, left=False)
    c.shift(0, 1, left=True)
    G('entry', A(4))
    c.move(I(0), D(1))
    c.move(M(4, 8), D(1), 'w')
    c.alu('cmp', D(1), 0); B(6, 'checked_fail')
    S(D(0), 'stride')
    G('stride', D(0))
    G('height', D(1))
    c.word(0xc0c1)         # MULU.W D1,D0
    S(D(0), 'plane_size')
    c.move(D(0), D(6))
    G('depth', D(5))
    c.move(I(0), D(7))
    L('checked_sum_planes')
    c.alu('add', D(6), 7); B(5, 'checked_fail')
    c.quick(1, D(5), sub=True)
    B(6, 'checked_sum_planes')
    G('entry', A(4))
    c.move(M(4, 16), D(0))
    c.alu('cmp', D(7), 0); B(6, 'checked_fail')
    S(D(0), 'pixels_len')
    G('cursor', D(0))
    c.alu('cmp', M(4, 12), 0); B(6, 'checked_fail')

    c.move(I(0), D(0))
    c.move(M(4, 10), D(0), 'w')
    c.imm('cmp', 1, D(0)); B(2, 'checked_fail')
    S(D(0), 'flags')
    G('flags', D(0)); c.tst(D(0))
    B(7, 'checked_no_mask')
    G('plane_size', D(1))
    G('entry', A(4))
    c.move(M(4, 24), D(0))
    c.alu('cmp', D(1), 0); B(6, 'checked_fail')
    G('cursor', D(0))
    G('pixels_len', D(1))
    add(0, D(1))
    c.alu('cmp', M(4, 20), 0); B(6, 'checked_fail')
    G('plane_size', D(0))
    S(D(0), 'mask_len')
    B(0, 'checked_mask_done')
    L('checked_no_mask')
    G('entry', A(4))
    c.tst(M(4, 20)); B(6, 'checked_fail')
    c.tst(M(4, 24)); B(6, 'checked_fail')
    S(I(0), 'mask_len')
    L('checked_mask_done')
    G('cursor', D(0))
    G('pixels_len', D(1))
    add(0, D(1))
    G('mask_len', D(1))
    add(0, D(1))
    G('payload_size', D(1))
    c.alu('cmp', D(1), 0); B(2, 'checked_fail')
    S(D(0), 'cursor')
    G('entry', A(4))
    c.tst(M(4, 32)); B(6, 'checked_fail')
    c.tst(M(4, 36)); B(6, 'checked_fail')

    # Reuse the existing CPU020/P0a checked planar padding helper.
    G('bankptr', D(0))
    G('entry', A(4))
    add(0, M(4, 12))
    c.move(D(0), A(0))
    G('width', D(0)); G('stride', D(1))
    G('height', D(2)); G('depth', D(3))
    B(1, 'check_padding')
    c.tst(D(0)); B(7, 'checked_fail')
    G('mask_len', D(0)); c.tst(D(0))
    B(7, 'checked_padding_ok')
    G('bankptr', D(0))
    G('entry', A(4))
    add(0, M(4, 20))
    c.move(D(0), A(0))
    G('width', D(0)); G('stride', D(1))
    G('height', D(2))
    c.move(I(1), D(3))
    B(1, 'check_padding')
    c.tst(D(0)); B(7, 'checked_fail')
    L('checked_padding_ok')

    G('entry', D(0))
    c.imm('add', 40, D(0))
    S(D(0), 'entry')
    G('index', D(0))
    c.quick(1, D(0))
    S(D(0), 'index')
    B(0, 'checked_loop')

    L('checked_all_entries')
    G('cursor', D(0))
    G('payload_size', D(1))
    c.alu('cmp', D(1), 0); B(6, 'checked_fail')
    G('payload_size', D(0))
    G('data_start', D(1))
    c.alu('sub', D(1), 0)
    S(D(0), 'data_size')
    G('bankptr', D(0))
    G('data_start', D(1))
    add(0, D(1))
    c.move(D(0), A(0))
    G('data_size', D(0))
    G('ctx', A(1))
    G('bankptr', D(1))
    G('generation', D(4))
    G('gfx', A(4))
    B(1, 'checked_chip_stage')
    c.tst(D(3)); B(7, 'checked_fail')
    S(I(1), 'result')
    L('checked_fail')
    G('result', D(3))
    c.raw('4fef00b0')       # LEA 176(SP),SP
    c.raw('4cdf77f7')       # restore AMOS ABI
    c.raw('74004e75')       # D2=0, RTS

    # LOOKUP: the bank still must be selected and its current AMOS payload
    # address must match the staged identity; no stale DMA pointer after Erase.
    L('checked_lookup_entry')
    c.raw('48e7efee')       # preserve caller registers, MC68020
    c.raw('4fefff50')       # local 176-byte frame
    c.move(A(7), A(2))
    S(D(3), 'bank')
    S(A(1), 'ctx')
    S(I(0), 'result')
    c.raw('20780004')
    c.move(A(0), D(0))
    c.tst(D(0)); B(7, 'checked_lookup_fail')
    c.move(M(0, 0x128), D(0), 'w')
    c.word(0x0800); c.word(1)
    B(7, 'checked_lookup_fail')
    G('ctx', D(0)); c.tst(D(0)); B(7, 'checked_lookup_fail')
    c.imm('and', 1, D(0)); B(6, 'checked_lookup_fail')
    G('bank', D(0))
    c.imm('cmp', 5, D(0)); B(5, 'checked_lookup_fail')
    c.imm('cmp', 65535, D(0)); B(2, 'checked_lookup_fail')
    c.lea(0, 'bank_active_state')
    c.move(M(0, 0), D(0))
    G('bank', D(1))
    c.alu('cmp', D(1), 0); B(6, 'checked_lookup_fail')
    c.lea(0, 'bank_active_state')
    c.move(M(0, 4), D(0)); S(D(0), 'bankptr')
    c.tst(D(0)); B(7, 'checked_lookup_fail')
    c.move(M(0, 8), D(0)); S(D(0), 'head')
    c.move(M(5, CUR_BANKS_A5), D(0))
    G('head', D(1))
    c.alu('cmp', D(1), 0); B(6, 'checked_lookup_fail')
    G('bank', D(0))
    c.raw(GETADR.hex())
    c.move(A(0), D(0))
    G('bankptr', D(1))
    c.alu('cmp', D(1), 0); B(6, 'checked_lookup_fail')
    c.imm('cmp', 24, D(0)); B(3, 'checked_lookup_fail')
    c.move(D(0), D(1)); c.imm('and', 1, D(1))
    B(6, 'checked_lookup_fail')
    G('bankptr', A(1))
    osbase(); c.call_os(-534)
    c.tst(D(0)); B(7, 'checked_lookup_fail')
    G('bankptr', A(4))
    c.move(M(4, 0), D(0))
    c.imm('cmp', 0x4147424f, D(0))
    B(6, 'checked_lookup_fail')
    c.move(M(4, 24), D(1))
    c.tst(D(1)); B(7, 'checked_lookup_fail')
    G('bankptr', D(0))
    G('ctx', A(1))
    B(1, 'checked_chip_lookup_entry')
    c.tst(D(3)); B(7, 'checked_lookup_fail')
    S(I(1), 'result')
    L('checked_lookup_fail')
    G('result', D(3))
    c.raw('4fef00b0')
    c.raw('4cdf77f7')
    c.raw('74004e75')

    # RELEASE is valid even if Erase/Load removed the original bank.
    # Context belongs to the private calling registry; the helper validates
    # its ownership cookie and performs WaitBlit before FreeVec.
    L('checked_release_entry')
    B(0, 'checked_chip_release_entry')

    L('checked_chip_stage')
    c.raw(chip.hex())
    for key, off in chip_labels.items():
        c.labels['chip_' + key] = c.labels['checked_chip_stage'] + off
    out = c.out()
    assert out[:len(prefix)] == prefix
    assert len(out) % 2 == 0
    assert len(out) < 32766
    assert c.labels['checked_stage_entry'] > previous_labels['mask_kernel']
    assert c.labels['checked_chip_stage'] > c.labels['checked_stage_entry']
    return out, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    native, labels = emit_checked_bank_stage()
    print('M19 P0c PRIVATE live AGBO bank validation + Chip stage',
          len(native), sha256(native).hexdigest(),
          'wrapper offset', labels['checked_stage_entry'],
          'no AP20, no WinUAE or Compiler claim')
