"""M17/R55: grouped bitplane Fill/Clear, 68000 only.

New emission is isolated from frozen R27. The validations and Safe guard
below are reproduced from emit_fill_safe(); only the DMA tail is changed.
BltBitMap minterms 0/$F0 ignore source, and Mask selects destination planes.
Each group is synchronous. The returned planecnt is checked exactly against
popcount(mask), including after partial-result WaitBlit.
"""
from m68k_emit import Code, D, A, M, POST, PRE, I
from m12_blit_safe_r27_emit import (
    AMOS_STATE_PTR, SCREEN, GFX, WIDTH, HEIGHT, DEPTH, DBSTATE,
    LVO_BLTBITMAP, LVO_WAITBLIT, _emit_safe_guard,
)


def emit_fill_grouped():
    """Return complete optimized Fill native body (without AP20 GetP).

    D3=pen, (A3)+ = h,w,y,x. Output D3=0/1, D2=0; SP balanced.
    All old geometry/bitplane/Safe validation occurs before the first DMA.
    """
    c = Code()
    c.raw("48e7efee")
    c.move(POST(3), D(5))
    c.move(POST(3), D(4))
    c.move(POST(3), D(1))
    c.move(POST(3), D(0))

    c.move(M(5, AMOS_STATE_PTR), A(4))
    c.move(A(4), D(6)); c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, SCREEN), D(6)); c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, DBSTATE), A(2))
    c.move(A(2), D(6)); c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, GFX), A(6))
    c.move(A(6), D(6)); c.tst(D(6)); c.branch(7, "bad")

    for reg in (0, 1, 3):
        c.tst(D(reg)); c.branch(11, "bad")
    for reg in (4, 5):
        c.tst(D(reg)); c.branch(15, "bad")
    for off in (WIDTH, HEIGHT):
        c.move(M(4, off), D(6)); c.tst(D(6)); c.branch(15, "bad")
        c.imm("cmp", 32767, D(6)); c.branch(14, "bad")
    c.move(M(4, WIDTH), D(6)); c.alu("sub", D(4), 6)
    c.tst(D(6)); c.branch(11, "bad")
    c.alu("cmp", D(6), 0); c.branch(14, "bad")
    c.move(M(4, HEIGHT), D(6)); c.alu("sub", D(5), 6)
    c.tst(D(6)); c.branch(11, "bad")
    c.alu("cmp", D(6), 1); c.branch(14, "bad")

    c.tst(M(2, 8)); c.branch(7, "front_zero")
    c.move(M(2, 0), A(0)); c.branch(0, "have_sb")
    c.label("front_zero"); c.move(M(2, 4), A(0))
    c.label("have_sb")
    c.move(A(0), D(6)); c.tst(D(6)); c.branch(7, "bad")
    c.move(M(0, 0), A(0))
    c.move(A(0), D(6)); c.tst(D(6)); c.branch(7, "bad")

    c.move(I(0), D(6)); c.move(M(0, 0), D(6), "w")
    c.shift(6, 3, left=True)
    c.alu("cmp", M(4, WIDTH), 6); c.branch(13, "bad")
    c.move(I(0), D(6)); c.move(M(0, 2), D(6), "w")
    c.alu("cmp", M(4, HEIGHT), 6); c.branch(13, "bad")
    c.move(I(0), D(6)); c.move(M(0, 5), D(6), "b")
    c.alu("cmp", M(4, DEPTH), 6); c.branch(6, "bad")
    c.tst(D(6)); c.branch(15, "bad")
    c.imm("cmp", 8, D(6)); c.branch(14, "bad")

    c.move(D(6), D(2))
    c.move(A(0), A(1)); c.quick(8, A(1))
    c.label("check_plane")
    c.move(POST(1), D(6))
    c.tst(D(6)); c.branch(7, "bad")
    c.imm("cmp", -1, D(6)); c.branch(7, "bad")
    c.quick(1, D(2), sub=True)
    c.branch(6, "check_plane")

    c.move(I(0), D(2)); c.move(M(0, 5), D(2), "b")
    c.move(I(1), D(6))
    c.label("compute_limit")
    c.shift(6, 1, left=True)
    c.quick(1, D(2), sub=True)
    c.branch(6, "compute_limit")
    c.alu("cmp", D(6), 3); c.branch(4, "bad")

    _emit_safe_guard(c)

    # 3 scratch longs: [setMask, 1<<Depth, pen].
    # The saved bitmap, width/height, x/y survive graphics.library calls.
    c.move(D(3), PRE(7)); c.move(D(6), PRE(7))
    c.move(A(0), A(4))
    c.move(D(0), D(2)); c.move(D(1), D(3))
    c.move(M(7), D(7))
    c.quick(1, D(7), sub=True)       # full depth mask
    c.move(M(7, 4), D(6))
    c.alu("and", D(7), 6)            # setMask = pen & fullMask
    c.move(D(6), PRE(7))
    c.alu("sub", D(6), 7)            # clearMask = fullMask - setMask

    c.tst(D(7)); c.branch(7, "set_group")
    c.move(I(0), D(6))              # first group clears selected planes
    c.branch(1, "group_blt")
    c.tst(D(0)); c.branch(7, "blit_failed")

    c.label("set_group")
    c.move(M(7), D(7))
    c.tst(D(7)); c.branch(7, "blit_succeeded")
    c.move(I(0xF0), D(6))           # second group sets selected planes
    c.branch(1, "group_blt")
    c.tst(D(0)); c.branch(7, "blit_failed")

    c.label("blit_succeeded")
    c.move(I(1), D(3)); c.branch(0, "leave_groups")
    c.label("blit_failed")
    c.move(I(0), D(3))
    c.label("leave_groups")
    c.quick(8, A(7)); c.quick(4, A(7))
    c.branch(0, "finish")

    # All early validation / Safe failures reach 'bad' without scratch.
    c.label("bad")
    c.move(I(0), D(3))
    c.label("finish")
    c.raw("4cdf77f7")
    c.raw("7400")
    c.raw("4e75")

    # Private helper in the same contiguous Compiler-copied monolith.
    # On entry: D7=nonzero group mask, D6=minterm, D2=x, D3=y,
    # D4=w, D5=h, A4=bitmap, A6=GfxBase.
    # Returns D0=1 iff BltBitMap planecnt == popcount(group mask).
    # WaitBlit is called EVEN for a zero or partial planecnt.
    c.label("group_blt")
    c.move(D(6), PRE(7))            # minterm before count loop
    c.move(D(7), D(0))
    c.move(I(0), D(1))
    c.label("popcount_loop")
    c.tst(D(0)); c.branch(7, "popcount_done")
    c.move(D(0), D(6))
    c.quick(1, D(6), sub=True)
    c.alu("and", D(6), 0)            # x &= x-1, counting its set bits
    c.quick(1, D(1))
    c.branch(0, "popcount_loop")
    c.label("popcount_done")
    c.move(D(1), PRE(7))            # expected count [SP], minterm [SP+4]
    c.move(M(7, 4), D(6))
    c.move(D(2), D(0)); c.move(D(3), D(1))
    c.move(A(4), A(0)); c.move(A(4), A(1))
    c.move(I(0), A(2))              # TempA=NULL
    c.call_os(LVO_BLTBITMAP)
    c.move(D(0), D(6))              # preserve actual count across WaitBlit
    c.call_os(LVO_WAITBLIT)
    c.alu("cmp", M(7), 6)
    c.branch(6, "group_failed")     # BNE: partial/zero count
    c.quick(8, A(7))
    c.move(I(1), D(0))
    c.raw("4e75")
    c.label("group_failed")
    c.quick(8, A(7))
    c.move(I(0), D(0))
    c.raw("4e75")

    code = c.out()
    assert len(code) % 2 == 0
    assert c.labels["group_blt"] > c.labels["finish"]
    return code, c.labels
