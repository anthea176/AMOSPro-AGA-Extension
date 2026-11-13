"""OPT020/P1e: attach validated P1b/P1c/P1d bitfield kernels to R60.

This emits only the PASS-1 painter into the SAME AP20 relocation unit as
R60's original bank/GetAdr, double-pass RLE, Safe and Intuition preflight.
All geometry is bounded by the original R60 pass-0 checks. No CPU bitmap
writes are performed during pass 0. The caller guards AFF_68020 before use.

R60 local frame: 192 bytes; the previously free final 44 bytes hold an
opaque mask word, eight plane pointers and the visible fragment width.
Every BSR target is local to the single native R60 routine.
"""
from __future__ import annotations

from m68k_emit import A, D, I, M, POST
from opt020_p1b_multiplane_emit import emit_masked_multiplane_020
from opt020_p1c_rle_clip_emit import emit_clip_x_020
from opt020_p1d_fragment_emit import emit_fragment_020

FULL_MASK = 148
PLANE_PTRS = 152
VISIBLE_WIDTH = 184
assert PLANE_PTRS + 8 * 4 <= VISIBLE_WIDTH and VISIBLE_WIDTH + 4 <= 192


def emit_paint_group_020(c, f):
    """Append R60-compatible clipping, native full/partial paint, and RTS."""
    def ld(name, reg):
        c.move(M(2, f[name]), reg)
    def st(reg, name):
        c.move(reg, M(2, f[name]))
    def b(cond, name):
        c.branch(cond, name)
    def l(name):
        c.label(name)

    # Original R60 signed row crop and destination height intersection.
    ld("row", D(0))
    c.alu("sub", M(2, f["srcy"]), 0)
    c.tst(D(0))
    b(11, "paint_done")
    c.alu("cmp", M(2, f["regionh"]), 0)
    b(12, "paint_done")
    c.alu("add", M(2, f["y"]), 0)
    c.tst(D(0))
    b(11, "paint_done")
    c.alu("cmp", M(2, f["scrh"]), 0)
    b(12, "paint_done")
    st(D(0), "dy")

    # Native P1c clip_x sees group_x, crop, bitmap bounds. It only
    # returns source bit offsets; it does not touch the bitmap.
    ld("decoded", D(0))
    c.shift(0, 4, left=True)
    ld("srcx", D(1))
    ld("regionw", D(2))
    c.alu("add", D(1), 2)
    ld("x", D(3))
    ld("scrw", D(4))
    ld("width", D(5))
    b(1, "p1e_clip_x")
    c.alu("cmp", D(6), 7)
    b(15, "paint_done")
    st(D(6), "srcbit")
    c.alu("sub", D(6), 7)
    c.move(D(7), M(2, VISIBLE_WIDTH))
    c.alu("add", D(6), 0)
    c.alu("sub", M(2, f["srcx"]), 0)
    c.alu("add", M(2, f["x"]), 0)
    st(D(0), "dx")

    # Destination byte address is exact; R60 has already checked the
    # inactive Bitmap, bitplane count, real stride, screen bounds, Safe.
    ld("dy", D(0))
    ld("stride", D(1))
    c.word(0xc0c1)                 # MULU.W D1,D0 (row*BytesPerRow)
    ld("dx", D(1))
    c.shift(1, 3, left=False)
    c.alu("add", D(1), 0)
    st(D(0), "destoff")

    # Build exactly Depth BE LONG pointers in the unused local frame;
    # no dynamically allocated scratch bank and no Chip-RAM source copy.
    ld("bitmap", A(6))
    c.quick(8, A(6))              # BitMap.Planes[0]
    c.raw("41ea0098")             # LEA 152(A2),A0 = pointer table
    ld("depth", D(7))
    l("p1e_plane_ptr_loop")
    c.move(POST(6), A(1))
    c.move(A(1), D(1))
    c.alu("add", M(2, f["destoff"]), 1)
    c.move(D(1), POST(0))
    c.quick(1, D(7), sub=True, size="w")
    b(6, "p1e_plane_ptr_loop")

    # Data groups include a leading mask WORD only when flags=1.
    # Mode=0 is always opaque, even if the stored image is masked.
    ld("group", A(0))
    ld("flags", D(5))
    c.tst(D(5))
    b(7, "p1e_source_ready")
    c.quick(2, A(0))
    l("p1e_source_ready")
    ld("mode", D(2))
    c.tst(D(2))
    b(6, "p1e_mask_from_image")
    c.move(I(0xffff), D(2))
    c.move(I(-1), M(2, FULL_MASK))
    c.raw("43ea0094")             # LEA 148(A2),A1 = BE 0xffff mask
    b(0, "p1e_mask_ready")
    l("p1e_mask_from_image")
    ld("group", A(1))
    c.move(I(0), D(2))
    c.move(M(1), D(2), "w")
    l("p1e_mask_ready")
    c.tst(D(2))
    b(7, "paint_done")            # all-transparent group: no writes

    ld("srcbit", D(4))
    c.move(M(2, VISIBLE_WIDTH), D(6))
    ld("dx", D(0))
    c.imm("and", 7, D(0))
    ld("depth", D(7))
    c.tst(D(4))
    b(6, "p1e_fragment_call")
    c.imm("cmp", 16, D(6))
    b(6, "p1e_fragment_call")
    c.raw("43ea0098")             # LEA 152(A2),A1 = plane table
    b(1, "p1e_full_16")
    b(0, "p1e_restore_frame")
    l("p1e_fragment_call")
    c.raw("45ea0098")             # LEA 152(A2),A2 = plane table
    b(1, "p1e_fragment")
    l("p1e_restore_frame")
    c.move(A(7), A(2))            # restore R60 frame pointer after P1d
    l("paint_done")
    c.word(0x4e75)                # RTS to R60 group loop

    # All BSR targets inside ONE AP20 unit: Compiler V2 relocation safe.
    l("p1e_clip_x")
    c.raw(emit_clip_x_020().hex())
    l("p1e_full_16")
    c.raw(emit_masked_multiplane_020().hex())
    l("p1e_fragment")
    c.raw(emit_fragment_020().hex())
