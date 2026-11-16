#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0d PRIVATE planar AGBO Chip -> AGA back BitMap Blitter painter.

Native SOURCE, independent private core, not a new public AP20 token and
NOT an installed Library. Caller must verify current AGBO bank+generation via
P0c registry, use the SAME staged AllocVec(MEMF_CHIP) source allocation,
obtain the inactive PRIVATE AGA BitMap only after a real Safe notification,
and prevent Erase/Load/re-stage until this call returns. Nothing here obtains
Safe, chooses a bank, creates an object, or calls Aga Swap.

Entry: A0 = image plane-0 ptr in verified *contiguous* private Chip allocation
       A1 = optional independent 1-bit mask ptr (0 means fully opaque)
       A2 = inactive SAFE AGA BitMap ptr (Intuition-owned)
       A3 = caller-owned pair of longs (logical width, logical height)
       A6 = valid graphics.library base from the live AGA State
       D0 = signed pixel X, D1 = signed pixel Y (both signed 16-bit range)
       D3 = planar bytes-per-row (even; 2*ceil(width/16))
       D4 = image width, D5 = image height (pixels, 1..4096)
       D6 = depth (1..8, must equal the active screen BitMap depth in P0d)
       D7 = bytes per whole image plane (=D3*D5)
Logical dimensions in A3 are mandatory: BytesPerRow*8 can include padding;
no Blitter write may cross the logical screen width or height.
Return D3=1 on success including completely off-screen no-op, D3=0 on refusal;
       D2=0; preserve A3, A5 and the project AMOS register set, balance A7.

Source image is planar plane-major as in AGBO v1; mask is a separate plane
with 1=visible. The paint path calls graphics.library BltBitMapRastPort for
opaque or BltMaskBitMapRastPort for masked, then WaitBlit. This first core
refuses mixed source/destination depths; no implicit palette/swap/clear.

These OS calls and source/destination pointers MUST be exercised via the
MC68020 CPU Gate A mock before integration, and then REAL WinUAE B/C. No
claim of hardware DMA, integration or live Bob rendering is made here.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, POST, I

MEMF_CHIP = 2
TYPEOFMEM = -534
INITRASTPORT = -198
BLT_BITMAP_RP = -606
BLT_MASK_BITMAP_RP = -636
WAITBLIT = -228
FRAME = 384
RP_OFFSET = 64
F = {name: 192 + 4*i for i, name in enumerate((
    'src mask dst gfx x y stride width height depth plane_bytes '
    'dst_stride dst_width dst_height dst_plane_bytes '
    'sx sy dx dy cw ch src_end mask_end dest_ptr dest_end result '
    'logical_ptr logical_w logical_h'
).split())}
assert max(F.values()) + 4 < FRAME


def emit_private_bob_blit() -> tuple[bytes, dict[str, int]]:
    c = Code()
    B, L = c.branch, c.label

    def S(src, name):
        c.move(src, M(4, F[name]))

    def G(name, dst):
        c.move(M(4, F[name]), dst)

    def cpu_guard():
        # All preceding instructions are legal on older CPUs. Refuse before
        # any new code or dereferencing an image/screen pointer.
        c.raw('20780004')  # MOVEA.L 4.W,A0, ExecBase
        c.move(A(0), D(0))
        c.tst(D(0)); B(7, 'reject')
        c.move(I(0), D(0))
        c.move(M(0, 0x128), D(0), 'w')
        c.word(0x0800); c.word(1)  # BTST #AFF_68020,D0
        B(7, 'reject')

    def check_nonzero_even(name):
        G(name, D(0)); c.tst(D(0)); B(7, 'reject')
        c.imm('and', 1, D(0)); B(6, 'reject')

    def check_chip(name):
        G(name, A(1))
        c.raw('2c780004')  # ExecBase, TypeOfMem(A1)
        c.call_os(TYPEOFMEM)
        c.imm('and', MEMF_CHIP, D(0))
        c.imm('cmp', MEMF_CHIP, D(0)); B(6, 'reject')

    def checked_end(ptr, length, result):
        G(ptr, D(0)); G(length, D(1))
        c.alu('add', D(1), 0); B(5, 'reject')
        c.quick(1, D(0), sub=True)
        S(D(0), result)

    def calc_clip(axis, source_size, limit, src, dst, extent):
        G(axis, D(0))
        c.tst(D(0)); B(11, 'neg_'+axis)
        S(I(0), src)
        S(D(0), dst)
        B(0, 'axis_'+axis)
        L('neg_'+axis)
        S(I(0), dst)
        c.move(I(0), D(1))
        c.alu('sub', D(0), 1)
        S(D(1), src)
        L('axis_'+axis)
        G(source_size, D(0)); G(src, D(1))
        c.alu('sub', D(1), 0)  # available source pixels
        G(limit, D(1)); G(dst, D(7))
        c.alu('sub', D(7), 1)  # available destination pixels
        c.alu('cmp', D(1), 0)
        B(13, 'axis_min_'+axis)  # signed BLT, source < dest
        c.move(D(1), D(0))
        L('axis_min_'+axis)
        c.tst(D(0)); B(15, 'ok')  # nonpositive: fully clipped, no DMA
        S(D(0), extent)

    L('private_bob_blit_entry')
    c.raw('48e7efee')        # AMOS ABI D0-D1/D4-D7/A0-A2/A4-A6 preserved
    c.raw('4feffe80')        # LEA -384(SP),SP
    c.move(A(7), A(4))      # frame base
    for reg, name in ((A(0),'src'), (A(1),'mask'), (A(2),'dst'),
                      (A(6),'gfx'), (A(3),'logical_ptr'),
                      (D(0),'x'), (D(1),'y'),
                      (D(3),'stride'), (D(4),'width'),
                      (D(5),'height'), (D(6),'depth'),
                      (D(7),'plane_bytes')):
        S(reg, name)
    S(I(0), 'result')
    cpu_guard()

    for name in ('src', 'dst', 'gfx', 'logical_ptr'):
        check_nonzero_even(name)
    # Explicit logical dimensions are passed by a private trusted caller.
    # Verify the second long is addressable before reading both values.
    G('logical_ptr', D(0))
    c.imm('add', 7, D(0)); B(5, 'reject')
    c.move(D(0), A(1))
    c.raw('2c780004'); c.call_os(TYPEOFMEM)
    c.tst(D(0)); B(7, 'reject')
    G('logical_ptr', A(0))
    for off, name in ((0, 'logical_w'), (4, 'logical_h')):
        c.move(M(0, off), D(0))
        c.imm('cmp', 1, D(0)); B(5, 'reject')
        c.imm('cmp', 4096, D(0)); B(2, 'reject')
        S(D(0), name)
    G('mask', D(0)); c.tst(D(0)); B(7, 'mask_ptr_valid')
    c.imm('and', 1, D(0)); B(6, 'reject')
    L('mask_ptr_valid')

    for name in ('x', 'y'):
        G(name, D(0))
        c.imm('cmp', -32768, D(0)); B(13, 'reject')
        c.imm('cmp', 32767, D(0)); B(14, 'reject')
    for name in ('width', 'height'):
        G(name, D(0)); c.imm('cmp', 1, D(0)); B(13, 'reject')
        c.imm('cmp', 4096, D(0)); B(14, 'reject')
    G('depth', D(0)); c.imm('cmp', 1, D(0)); B(13, 'reject')
    c.imm('cmp', 8, D(0)); B(14, 'reject')

    # Enforce AGBO v1 planar geometry, independently of the caller.
    G('width', D(0)); c.imm('add', 15, D(0))
    c.shift(0, 4); c.shift(0, 1, left=True)
    G('stride', D(1)); c.alu('cmp', D(1), 0); B(6, 'reject')
    G('stride', D(0)); G('height', D(1))
    c.word(0xc0c1)         # MULU.W D1,D0 => 32-bit stride*height
    G('plane_bytes', D(1)); c.alu('cmp', D(1), 0); B(6, 'reject')
    G('plane_bytes', D(0)); c.tst(D(0)); B(15, 'reject')
    c.imm('cmp', 0x01000000, D(0)); B(2, 'reject')

    # Validate the real inactive BitMap structure before trusting dimensions.
    G('dst', A(1)); c.raw('2c780004'); c.call_os(TYPEOFMEM)
    c.tst(D(0)); B(7, 'reject')
    G('dst', A(0))
    c.move(I(0), D(0)); c.move(M(0, 0), D(0), 'w')
    c.imm('cmp', 2, D(0)); B(5, 'reject')
    c.imm('cmp', 512, D(0)); B(2, 'reject')
    S(D(0), 'dst_stride')
    c.shift(0, 3, left=True)
    G('logical_w', D(1)); c.alu('cmp', D(1), 0); B(13, 'reject')
    S(D(1), 'dst_width')
    c.move(I(0), D(0)); c.move(M(0, 2), D(0), 'w')
    c.imm('cmp', 1, D(0)); B(5, 'reject')
    c.imm('cmp', 4096, D(0)); B(2, 'reject')
    G('logical_h', D(1)); c.alu('cmp', D(1), 0); B(13, 'reject')
    S(D(1), 'dst_height')
    c.move(I(0), D(0)); c.move(M(0, 5), D(0), 'b')
    G('depth', D(1)); c.alu('cmp', D(1), 0); B(6, 'reject')
    G('dst_stride', D(0)); G('dst_height', D(1))
    c.word(0xc0c1)         # MULU.W D1,D0
    S(D(0), 'dst_plane_bytes')

    calc_clip('x', 'width', 'dst_width', 'sx', 'dx', 'cw')
    calc_clip('y', 'height', 'dst_height', 'sy', 'dy', 'ch')

    # Make the exact source BitMap on stack. Its eight plane pointers are
    # exclusively derived from the single verified private Chip allocation.
    G('stride', D(0)); c.move(D(0), M(4, 0), 'w')
    G('height', D(0)); c.move(D(0), M(4, 2), 'w')
    c.move(I(0, 'w'), M(4, 4), 'b')  # bm_Flags
    G('depth', D(0)); c.move(D(0), M(4, 5), 'b')
    c.move(I(0, 'w'), M(4, 6), 'w')  # bm_Pad
    for i in range(8):
        c.move(I(0), M(4, 8+4*i))
    G('src', A(0))
    c.raw('43ec0008')       # LEA 8(A4),A1 (planes)
    G('depth', D(7))
    L('plane_build_loop')
    c.move(A(0), POST(1))
    c.move(A(0), D(0))
    G('plane_bytes', D(1)); c.alu('add', D(1), 0)
    B(5, 'reject')        # pointer wrap
    c.move(D(0), A(0))
    c.quick(1, D(7), sub=True)
    B(6, 'plane_build_loop')
    c.move(A(0), D(0)); c.quick(1, D(0), sub=True)
    S(D(0), 'src_end')
    check_chip('src'); check_chip('src_end')

    G('mask', D(0)); c.tst(D(0)); B(7, 'mask_checked')
    checked_end('mask', 'plane_bytes', 'mask_end')
    check_chip('mask'); check_chip('mask_end')
    L('mask_checked')

    # Real Intuition ScreenBuffer bitplanes are an OS-owned contiguous Chip
    # allocation. TypeOfMem endpoints are additional guards, not an arbitrary
    # malloc-contiguity proof. Check all participating destination planes.
    for i in range(8):
        skip = f'dest_plane_{i}_skip'
        G('depth', D(0)); c.imm('cmp', i+1, D(0)); B(5, skip)
        G('dst', A(0)); c.move(M(0, 8+4*i), D(0))
        c.tst(D(0)); B(7, 'reject')
        c.imm('cmp', -1, D(0)); B(7, 'reject')
        S(D(0), 'dest_ptr')
        c.imm('and', 1, D(0)); B(6, 'reject')
        checked_end('dest_ptr', 'dst_plane_bytes', 'dest_end')
        check_chip('dest_ptr'); check_chip('dest_end')
        L(skip)

    # InitRastPort initializes a complete 128-byte RP, then attach only
    # the already Safe AGA back BitMap (never the displayed front one).
    G('gfx', A(6))
    c.raw('43ec0040')       # LEA 64(A4),A1
    c.call_os(INITRASTPORT)
    c.raw('43ec0040')       # A1 = RastPort
    G('dst', D(0)); c.move(D(0), M(1, 4))  # rp_BitMap

    c.move(A(4), A(0))      # A0 = local source BitMap
    for reg, key in ((0,'sx'), (1,'sy'), (2,'dx'), (3,'dy'),
                     (4,'cw'), (5,'ch')):
        G(key, D(reg))
    G('mask', D(7)); c.tst(D(7)); B(7, 'draw_opaque')
    c.move(I(0xe0), D(6))
    G('mask', A(2))
    c.call_os(BLT_MASK_BITMAP_RP)
    B(0, 'blit_done')
    L('draw_opaque')
    c.move(I(0xc0), D(6))
    c.call_os(BLT_BITMAP_RP)
    L('blit_done')
    G('gfx', A(6))
    c.call_os(WAITBLIT)
    L('ok')
    S(I(1), 'result')
    B(0, 'return')
    L('reject')
    L('return')
    G('result', D(3))
    c.raw('4fef0180')       # LEA +384(SP),SP
    c.raw('4cdf77f7')       # MOVEM restore, D3 not restored
    c.raw('74004e75')       # MOVEQ #0,D2; RTS
    binary = c.out()
    assert binary[:4] == bytes.fromhex('48e7efee')
    assert binary[-4:] == bytes.fromhex('74004e75')
    assert len(binary)%2 == 0 and len(binary) < 32766
    return binary, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    raw, labels = emit_private_bob_blit()
    print('M19 P0d PRIVATE MC68020 AGBO Blitter SOURCE ONLY', len(raw),
          sha256(raw).hexdigest(), len(labels), 'labels; no AP20/Lib/WinUAE')
