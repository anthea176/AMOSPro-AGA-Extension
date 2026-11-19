#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 PRIVATE MC68020 page snapshot coordinator, source-only.

Preserves the existing planar copy, Safe back selector and transaction pool
byte-for-byte. Entry points (A5 is the AMOS owner):
  b8_service_bind_entry     reserve two CPU snapshot buffers for live screen
  b8_service_capture_entry  save only currently Safe non-displayed BitMap
  b8_service_restore_entry  restore only that BitMap if its snapshot is valid
  b8_service_close_entry    release both buffers once, owner-checked

Returns D2=0, D3=1/0. Preserves the other AMOS registers.
No DMA uses the snapshot (Exec MEMF_PUBLIC|MEMF_CLEAR). No implicit Swap.
The service root binds owner, Screen*, DBState*, both physical BitMap* and
physical BytesPerRow*Rows*Depth. Snapshot validity is tracked PER BitMap,
never just by front index. A local epoch increments on each new bind.
It is NOT an OS screen-generation token: Close/End integration is required
before exposing this API, including protection against same-address ABA.
No public tokens, no modifications to B7-m2 or existing Close/End hooks.
Safe pending is refused rather than waited on. TypeOfMem checking is only
best-effort: the caller must maintain OS object lifetime and serialized use.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b8_back_selector_emit import emit_b8_back_selector, STATE_OFF
from m19_b8_snapshot_pool_emit import emit_b8_snapshot_pool, MAX_PAGE_BYTES

FRAME = 96
F = dict(owner=0, screen=4, db=8, bitmap0=12, bitmap1=16,
         back=20, bytes=24, bit=28, snapshot=32, mode=36, status=40, plane_bytes=44)
R = dict(owner=0, screen=4, db=8, bitmap0=12, bitmap1=16,
         bytes=20, valid=24, epoch=28)
ROOT_SIZE = 32


def emit_b8_page_manager() -> tuple[bytes, dict[str, int]]:
    old, labels = emit_b8_back_selector()
    pool, pool_labels = emit_b8_snapshot_pool()
    c = Code()
    c.raw(old.hex())
    c.labels.update(labels)
    pool_start = len(old)
    c.raw(pool.hex())
    c.labels.update({k: pool_start + v for k, v in pool_labels.items()})
    prefix = bytes(c.b)
    B, L = c.branch, c.label

    def S(src, name):
        c.move(src, M(4, F[name]))

    def G(name, dst):
        c.move(M(4, F[name]), dst)

    def root():
        c.lea(2, 'b8_service_root')  # A2 is nonvolatile across Exec calls.

    def saved_entry(name):
        L(name)
        c.raw('48e7cfee4fefffa0')  # MOVEM saved; 96-byte local frame.
        c.move(A(7), A(4))
        S(I(0), 'status')

    def compare_identity():
        root()
        c.tst(M(2, R['owner']))
        B(7, 'b8_service_identity_fail')
        for field in ('owner', 'screen', 'db', 'bitmap0', 'bitmap1', 'bytes'):
            root()
            c.move(M(2, R[field]), D(0))
            G(field, D(1))
            c.alu('cmp', D(1), 0)
            B(6, 'b8_service_identity_fail')
        c.move(I(1), D(3))
        c.raw('4e75')
        L('b8_service_identity_fail')
        c.move(I(0), D(3))
        c.raw('4e75')

    def mapped_bitmap(key):
        G(key, D(0))
        c.tst(D(0))
        B(7, 'b8_service_fetch_fail')
        c.imm('and', 1, D(0))
        B(6, 'b8_service_fetch_fail')
        G(key, A(1))
        c.raw('2c780004')
        c.call_os(-534)  # TypeOfMem(pointer)
        c.tst(D(0))
        B(7, 'b8_service_fetch_fail')
        G(key, D(0))
        c.imm('add', 39, D(0))
        B(5, 'b8_service_fetch_fail')
        c.move(D(0), A(1))
        c.raw('2c780004')
        c.call_os(-534)  # TypeOfMem(pointer + sizeof(BitMap)-1)
        c.tst(D(0))
        B(7, 'b8_service_fetch_fail')

    # Resolve a *live* physical back, both physical BitMaps and exact geometry.
    # Never read or write pixel planes here. Caller owns the 96-byte frame.
    L('b8_service_fetch')
    S(A(5), 'owner')
    B(1, 'b8_checked_back_selector_entry')
    c.tst(D(3))
    B(7, 'b8_service_fetch_fail')
    S(D(2), 'back')
    c.move(M(5, STATE_OFF), A(0))
    c.move(M(0, 0), D(0))
    S(D(0), 'screen')
    c.move(M(0, 32), D(0))
    S(D(0), 'db')
    G('db', A(0))
    c.move(M(0, 0), A(1))
    c.move(M(0, 4), A(0))
    c.move(M(1, 0), D(0))
    S(D(0), 'bitmap0')
    G('db', A(0))
    c.move(M(0, 4), A(1))
    c.move(M(1, 0), D(0))
    S(D(0), 'bitmap1')
    G('bitmap0', D(0))
    G('bitmap1', D(1))
    c.alu('cmp', D(1), 0)
    B(7, 'b8_service_fetch_fail')
    mapped_bitmap('bitmap0')
    mapped_bitmap('bitmap1')

    # Equality of BPR, Rows and Depth across physical pages.
    G('bitmap0', A(0))
    G('bitmap1', A(1))
    c.move(M(0, 0), D(0))
    c.move(M(1, 0), D(1))
    c.alu('cmp', D(1), 0)
    B(6, 'b8_service_fetch_fail')
    c.move(I(0), D(0))
    c.move(M(0, 5), D(0), 'b')
    c.move(I(0), D(1))
    c.move(M(1, 5), D(1), 'b')
    c.alu('cmp', D(1), 0)
    B(6, 'b8_service_fetch_fail')
    c.imm('cmp', 1, D(0))
    B(5, 'b8_service_fetch_fail')
    c.imm('cmp', 8, D(0))
    B(2, 'b8_service_fetch_fail')
    c.move(D(0), D(5))  # Depth.
    G('bitmap0', A(0))
    c.move(I(0), D(0))
    c.move(M(0, 0), D(0), 'w')  # Real BytesPerRow.
    c.imm('cmp', 2, D(0))
    B(5, 'b8_service_fetch_fail')
    c.move(D(0), D(2))
    c.imm('and', 1, D(2))
    B(6, 'b8_service_fetch_fail')
    c.move(I(0), D(1))
    c.move(M(0, 2), D(1), 'w')  # Rows.
    c.tst(D(1))
    B(7, 'b8_service_fetch_fail')
    c.word(0xc0c1)  # MULU.W D1,D0 -> 32-bit bytes per plane.
    c.tst(D(0))
    B(7, 'b8_service_fetch_fail')
    S(D(0), 'plane_bytes')
    S(D(0), 'bytes')
    c.move(I(0), D(6))
    for n in range(1, 9):
        c.imm('cmp', n, D(5))
        B(5, f'b8_service_geometry_done_{n}')
        G('bytes', D(4))
        c.alu('add', D(4), 6)
        B(5, 'b8_service_fetch_fail')  # 32-bit overflow.
        L(f'b8_service_geometry_done_{n}')
    c.imm('cmp', MAX_PAGE_BYTES, D(6))
    B(2, 'b8_service_fetch_fail')
    S(D(6), 'bytes')
    # Never allow page-0 and page-1 plane memory to overlap. Distinct
    # BitMap pointers alone do NOT guarantee distinct DMA pages.
    for i in range(8):
        c.imm('cmp', i+1, D(5))
        B(5, f'b8_service_plane_outer_done_{i}')
        for j in range(8):
            c.imm('cmp', j+1, D(5))
            B(5, f'b8_service_plane_inner_done_{i}_{j}')
            G('bitmap0', A(0))
            c.move(M(0, 8+4*i), D(0))
            G('bitmap1', A(1))
            c.move(M(1, 8+4*j), D(1))
            c.move(D(0), D(2))
            G('plane_bytes', D(4))
            c.alu('add', D(4), 2)
            B(5, 'b8_service_fetch_fail')
            c.alu('cmp', D(1), 2)
            B(3, f'b8_service_plane_inner_done_{i}_{j}')
            c.move(D(1), D(2))
            c.alu('add', D(4), 2)
            B(5, 'b8_service_fetch_fail')
            c.alu('cmp', D(0), 2)
            B(3, f'b8_service_plane_inner_done_{i}_{j}')
            B(0, 'b8_service_fetch_fail')
            L(f'b8_service_plane_inner_done_{i}_{j}')
        L(f'b8_service_plane_outer_done_{i}')
    G('back', D(0))
    G('bitmap0', D(1))
    c.alu('cmp', D(1), 0)
    B(6, 'b8_service_back_one')
    S(I(1), 'bit')
    B(0, 'b8_service_fetch_success')
    L('b8_service_back_one')
    G('bitmap1', D(1))
    c.alu('cmp', D(1), 0)
    B(6, 'b8_service_fetch_fail')
    S(I(2), 'bit')
    L('b8_service_fetch_success')
    c.move(I(1), D(3))
    c.raw('4e75')
    L('b8_service_fetch_fail')
    c.move(I(0), D(3))
    c.raw('4e75')

    # Accept a bind only once the page selection and both geometries agree.
    saved_entry('b8_service_bind_entry')
    B(1, 'b8_service_fetch')
    c.tst(D(3))
    B(7, 'b8_service_return')
    root()
    c.tst(M(2, R['owner']))
    B(7, 'b8_service_bind_new')
    B(1, 'b8_service_identity')
    c.tst(D(3))
    B(7, 'b8_service_return')
    B(0, 'b8_service_bind_pool')
    L('b8_service_bind_new')
    # A failed second AllocMem cannot publish a service root.
    L('b8_service_bind_pool')
    G('screen', A(0))
    G('bitmap0', A(1))
    G('bitmap1', A(2))
    G('bytes', D(0))
    B(1, 'b8_pool_bind_entry')
    c.tst(D(3))
    B(7, 'b8_service_return')
    root()
    c.tst(M(2, R['owner']))
    B(6, 'b8_service_bind_ok')  # Repeated matching bind keeps valid flags.
    for field in ('owner', 'screen', 'db', 'bitmap0', 'bitmap1', 'bytes'):
        G(field, D(0))
        root()
        c.move(D(0), M(2, R[field]))
    root()
    c.move(I(0), M(2, R['valid']))
    c.move(M(2, R['epoch']), D(0))
    c.quick(1, D(0))
    c.tst(D(0))
    B(6, 'b8_service_epoch_ok')
    c.move(I(1), D(0))  # Avoid zero after wrap-around.
    L('b8_service_epoch_ok')
    c.move(D(0), M(2, R['epoch']))
    L('b8_service_bind_ok')
    S(I(1), 'status')
    B(0, 'b8_service_return')

    # Save/restore has no implicit swap; never copy before Safe and identity.
    saved_entry('b8_service_capture_entry')
    S(I(0), 'mode')
    B(0, 'b8_service_transfer')
    saved_entry('b8_service_restore_entry')
    S(I(1), 'mode')
    L('b8_service_transfer')
    B(1, 'b8_service_fetch')
    c.tst(D(3))
    B(7, 'b8_service_return')
    B(1, 'b8_service_identity')
    c.tst(D(3))
    B(7, 'b8_service_return')
    G('mode', D(0))
    c.tst(D(0))
    B(7, 'b8_service_capture_prepare')
    root()
    c.move(M(2, R['valid']), D(0))
    G('bit', D(1))
    c.alu('and', D(1), 0)
    c.tst(D(0))
    B(7, 'b8_service_return')  # Never restore a missing snapshot.
    B(0, 'b8_service_copy_prepare')
    L('b8_service_capture_prepare')
    B(1, 'b8_service_invalidate')  # Failure cannot leave old data valid.
    L('b8_service_copy_prepare')
    G('screen', A(0))
    G('back', A(1))
    B(1, 'b8_pool_get_entry')
    c.tst(D(3))
    B(7, 'b8_service_copy_fail')
    S(D(2), 'snapshot')
    G('back', A(0))
    G('snapshot', A(1))
    G('bytes', D(0))
    G('mode', D(1))
    B(1, 'b8_planar_snapshot_core_entry')
    c.tst(D(3))
    B(7, 'b8_service_copy_fail')
    G('mode', D(0))
    c.tst(D(0))
    B(6, 'b8_service_copy_ok')  # Restore keeps its valid snapshot.
    root()
    c.move(M(2, R['valid']), D(0))
    G('bit', D(1))
    c.alu('or', D(1), 0)
    c.move(D(0), M(2, R['valid']))
    L('b8_service_copy_ok')
    S(I(1), 'status')
    B(0, 'b8_service_return')
    L('b8_service_copy_fail')
    B(1, 'b8_service_invalidate')  # Fail closed even for a failed restore.
    B(0, 'b8_service_return')

    # Release CPU-only allocations; still private, NOT an Open/Close/End hook.
    saved_entry('b8_service_close_entry')
    root()
    c.tst(M(2, R['owner']))
    B(7, 'b8_service_close_empty')
    c.move(M(2, R['owner']), D(0))
    c.move(A(5), D(1))
    c.alu('cmp', D(1), 0)
    B(6, 'b8_service_return')  # Foreign owner must never FreeMem.
    c.move(M(2, R['screen']), A(0))
    B(1, 'b8_pool_close_entry')
    c.tst(D(3))
    B(7, 'b8_service_return')
    root()
    for off in range(0, R['epoch'], 4):
        c.move(I(0), M(2, off))  # Keep monotonic generation across Close.
    L('b8_service_close_empty')
    S(I(1), 'status')
    B(0, 'b8_service_return')

    L('b8_service_identity')
    compare_identity()

    L('b8_service_invalidate')
    root()
    c.move(M(2, R['valid']), D(0))
    G('bit', D(1))
    c.imm('cmp', 1, D(1))
    B(6, 'b8_service_invalidate_second')
    c.imm('and', 0xfffffffe, D(0))
    B(0, 'b8_service_invalidate_commit')
    L('b8_service_invalidate_second')
    c.imm('and', 0xfffffffd, D(0))
    L('b8_service_invalidate_commit')
    c.move(D(0), M(2, R['valid']))
    c.raw('4e75')

    L('b8_service_return')
    c.move(I(0), D(2))
    G('status', D(3))
    c.raw('4fef00604cdf77f34e75')
    L('b8_service_root')
    c.raw('00' * ROOT_SIZE)
    result = c.out()
    assert result.startswith(prefix)
    assert result[len(prefix):c.labels['b8_service_bind_entry']] == b''
    assert c.labels['b8_service_root'] + ROOT_SIZE == len(result)
    assert not len(result) & 1 and len(result) < 32766
    return result, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    raw, labels = emit_b8_page_manager()
    print('M19 B8 page manager MC68020 SOURCE ONLY', len(raw),
          sha256(raw).hexdigest(), labels['b8_service_bind_entry'])
