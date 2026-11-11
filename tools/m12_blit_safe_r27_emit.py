"""R27/0.9.3: protect legacy Blit Copy and Fill against pending Safe.

Keep exact historical argument validation/DMA algorithm from R13 and R14;
insert one shared nonblocking Safe guard immediately BEFORE the first DMA.
Aga Blit Clear is the R15 wrapper calling Fill and inherits this guard.
Aga Text (R26), Swap, older binaries and legacy Aga Back Fill unchanged.

R27 is only a candidate until actual Gate A CPU and Gate B WinUAE pass.
"""
from m68k_emit import Code, D, A, M, POST, PRE, I

AMOS_STATE_PTR=0x01C8
SCREEN, GFX, WIDTH, HEIGHT, DEPTH, DBSTATE=0,8,12,16,28,32
LVO_BLTBITMAP,LVO_WAITBLIT=-30,-228
LVO_GETMSG=-372

def _emit_safe_guard(c):
    """On entry: A2=DBState, A4=State, A6=GfxBase; D0/D1/A0/A1/D6 live.

    DBState+20 bit0: old front not safe to write. GetMsg(SafePort) once.
    On missing port/message, RESTORE registers/stack then jump to 'bad',
    which returns 0 before any graphics.library BltBitMap operation.
    On success clear Safe bit only, preserving Disp bit. Never ReplyMsg,
    WaitPort or wait indefinitely. The same guard serves Copy and Fill.
    """
    c.move(D(6), PRE(7))               # D6 may be Fill's colour limit
    c.move(M(2, 20), D(6))              # pending flags
    c.imm("and", 1, D(6))
    c.branch(7, "r27_safe_done")        # BEQ: already safe; pop D6
    c.move(D(0), PRE(7))               # preserve live copy/fill arguments
    c.move(D(1), PRE(7))
    c.move(A(0), PRE(7))               # back BitMap
    c.move(A(1), PRE(7))               # validated plane cursor / scratch
    c.move(M(2, 12), A(0))             # SafePort (NOT DispPort)
    c.move(A(0), D(6))
    c.tst(D(6)); c.branch(7, "r27_safe_failed")
    c.raw("2c780004")                  # MOVEA.L 4.w,A6 (ExecBase)
    c.call_os(LVO_GETMSG)
    c.tst(D(0)); c.branch(7, "r27_safe_failed")
    c.move(M(2, 20), D(6))
    c.imm("and", 0xfffffffe, D(6))     # clear only bit0, preserve Disp bit1
    c.move(D(6), M(2, 20))
    c.move(M(4, GFX), A(6))            # restore GfxBase (Exec -> graphics)
    c.move(POST(7), A(1))
    c.move(POST(7), A(0))
    c.move(POST(7), D(1))
    c.move(POST(7), D(0))
    c.branch(0, "r27_safe_done")       # pop original D6, proceed with DMA
    c.label("r27_safe_failed")
    c.move(M(4, GFX), A(6))
    c.move(POST(7), A(1))
    c.move(POST(7), A(0))
    c.move(POST(7), D(1))
    c.move(POST(7), D(0))
    c.move(POST(7), D(6))
    c.branch(0, "bad")                 # no DMA; D3=0 via existing return
    c.label("r27_safe_done")
    c.move(POST(7), D(6))              # preserve Fill's pen limit

def emit_copy_safe():
    """AMOS function: Aga Blit Copy(sx,sy,dx,dy,w,h) -> 1 or 0.

    In: D3=h, (A3)+=w,dy,dx,sy,sx; A5=AMOS base.
    Out: D3=result, D2=0, A3 advanced by 20 bytes, SP balanced.
    Preserves D0,D1,D4-D7/A0-A2/A4-A6 (including A5).
    Modifies D2,D3,A3,CCR. Does not use WaitPort or Exec Wait.

    All coordinates and extents are checked BEFORE calling BltBitMap,
    which performs no clipping/sanity checks. Destination/source refer
    to the same validated back BitMap. BltBitMap handles overlaps,
    pixel shifts and modulos. WaitBlit makes the result synchronous.
    """
    c = Code()
    # Same proven R9 save/restore pair; A3 deliberately NOT saved.
    c.raw("48e7efee")
    c.move(D(3), D(5))          # h
    for reg in (4, 3, 2, 1, 0):
        c.move(POST(3), D(reg)) # w,dy,dx,sy,sx

    c.move(M(5, AMOS_STATE_PTR), A(4))
    c.move(A(4), D(6))
    c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, SCREEN), D(6))
    c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, DBSTATE), A(2))
    c.move(A(2), D(6))
    c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, GFX), A(6))
    c.move(A(6), D(6))
    c.tst(D(6)); c.branch(7, "bad")

    # Reject negative coordinates and nonpositive rectangle dimensions.
    for reg in (0, 1, 2, 3):
        c.tst(D(reg)); c.branch(11, "bad")  # BMI
    for reg in (4, 5):
        c.tst(D(reg)); c.branch(15, "bad")  # BLE

    # Signed 16-bit geometry is an AmigaOS BltBitMap requirement.
    for off in (WIDTH, HEIGHT):
        c.move(M(4, off), D(6))
        c.tst(D(6)); c.branch(15, "bad")
        c.imm("cmp", 32767, D(6)); c.branch(14, "bad")

    # Subtract before comparing: avoids overflow of (coordinate+extent).
    c.move(M(4, WIDTH), D(6))
    c.alu("sub", D(4), 6)
    c.tst(D(6)); c.branch(11, "bad")
    for reg in (0, 2):
        c.alu("cmp", D(6), reg); c.branch(14, "bad")
    c.move(M(4, HEIGHT), D(6))
    c.alu("sub", D(5), 6)
    c.tst(D(6)); c.branch(11, "bad")
    for reg in (1, 3):
        c.alu("cmp", D(6), reg); c.branch(14, "bad")

    # DBState: front index +8, original ScreenBuffer +0, alt +4.
    c.tst(M(2, 8))
    c.branch(7, "front_zero")
    c.move(M(2, 0), A(0))
    c.branch(0, "have_sb")
    c.label("front_zero")
    c.move(M(2, 4), A(0))
    c.label("have_sb")
    c.move(A(0), D(6)); c.tst(D(6)); c.branch(7, "bad")
    c.move(M(0, 0), A(0))      # ScreenBuffer.sb_BitMap
    c.move(A(0), D(6)); c.tst(D(6)); c.branch(7, "bad")

    # Guard the real BitMap geometry before any DMA. 68000 only.
    c.move(I(0), D(6))
    c.move(M(0, 0), D(6), "w") # BytesPerRow
    c.shift(6, 3, left=True)   # >= logical width in bits
    c.alu("cmp", M(4, WIDTH), 6)
    c.branch(13, "bad")       # BLT
    c.move(I(0), D(6))
    c.move(M(0, 2), D(6), "w") # Rows
    c.alu("cmp", M(4, HEIGHT), 6)
    c.branch(13, "bad")
    c.move(I(0), D(6))
    c.move(M(0, 5), D(6), "b") # Depth
    c.alu("cmp", M(4, DEPTH), 6)
    c.branch(6, "bad")
    c.tst(D(6)); c.branch(15, "bad")
    c.imm("cmp", 8, D(6)); c.branch(14, "bad")

    _emit_safe_guard(c)          # reject before ANY BltBitMap if not Safe
    c.move(A(0), A(1))        # source and dest BitMap are identical
    c.move(I(0), A(2))        # TempA: graphics.library owns overlap scratch
    c.move(I(0xC0), D(6))     # copy minterm
    c.move(I(0xFF), D(7))     # all available bitplanes
    c.call_os(LVO_BLTBITMAP)
    c.tst(D(0)); c.branch(7, "bad")
    c.call_os(LVO_WAITBLIT)
    c.move(I(1), D(3))
    c.branch(0, "finish")
    c.label("bad")
    c.move(I(0), D(3))
    c.label("finish")
    c.raw("4cdf77f7")        # exact counterpart to 48e7efee; not A3
    c.raw("7400")            # AMOS integer result: D2=0
    c.raw("4e75")
    result = c.out()
    assert len(result) % 2 == 0
    return result, c.labels



def emit_fill_safe():
    """Aga Blit Fill(x,y,w,h,pen) -> 1 or 0, back buffer only.

    D3=pen; successive (A3)+ = h,w,y,x; A5=AMOS base.
    D3=result, D2=0; A3 advances by exactly 16, SP balances.
    All D0,D1,D4-D7/A0-A2/A4-A6 restored. No restricted waits.

    Destination bitmap depth=1..8. Validate coordinates, pen range, physical
    dimensions and ALL destination plane pointers before any graphics call.
    For each bitplane use BltBitMap with a *single-bit write mask* and
    the source-ignoring minterm $F0 (set) or $00 (clear). These are exactly
    the four-channel-safe minterms specified by the graphics.library autodoc.
    WaitBlit after every plane, since the next BltBitMap is order-dependent.
    """
    c = Code()
    c.raw('48e7efee')                 # proven R13/R9 preserve set, excludes A3
    c.move(POST(3), D(5))            # height
    c.move(POST(3), D(4))            # width
    c.move(POST(3), D(1))            # y
    c.move(POST(3), D(0))            # x

    c.move(M(5, AMOS_STATE_PTR), A(4))
    c.move(A(4), D(6)); c.tst(D(6)); c.branch(7,'bad')
    c.move(M(4, SCREEN), D(6)); c.tst(D(6)); c.branch(7,'bad')
    c.move(M(4, DBSTATE), A(2))
    c.move(A(2), D(6)); c.tst(D(6)); c.branch(7,'bad')
    c.move(M(4, GFX), A(6))
    c.move(A(6), D(6)); c.tst(D(6)); c.branch(7,'bad')

    # Signed bounds and all nonzero extents; no clipping and no overflow.
    for reg in (0,1,3):
        c.tst(D(reg)); c.branch(11,'bad')  # BMI (pen >=0)
    for reg in (4,5):
        c.tst(D(reg)); c.branch(15,'bad')  # BLE
    for off in (WIDTH,HEIGHT):
        c.move(M(4,off),D(6)); c.tst(D(6)); c.branch(15,'bad')
        c.imm('cmp',32767,D(6)); c.branch(14,'bad')
    c.move(M(4,WIDTH),D(6)); c.alu('sub',D(4),6)
    c.tst(D(6)); c.branch(11,'bad')
    c.alu('cmp',D(6),0); c.branch(14,'bad')
    c.move(M(4,HEIGHT),D(6)); c.alu('sub',D(5),6)
    c.tst(D(6)); c.branch(11,'bad')
    c.alu('cmp',D(6),1); c.branch(14,'bad')

    # DB front index (+8); use the inactive ScreenBuffer.sb_BitMap.
    c.tst(M(2,8)); c.branch(7,'front_zero')
    c.move(M(2,0),A(0)); c.branch(0,'have_sb')
    c.label('front_zero'); c.move(M(2,4),A(0))
    c.label('have_sb')
    c.move(A(0),D(6)); c.tst(D(6)); c.branch(7,'bad')
    c.move(M(0,0),A(0))
    c.move(A(0),D(6)); c.tst(D(6)); c.branch(7,'bad')

    # Verify bitmap stride/rows/depth before access. Clear destination
    # bitplanes cannot be NULL or 0xffffffff (AmigaOS permits those in SRC).
    c.move(I(0),D(6)); c.move(M(0,0),D(6),'w')
    c.shift(6,3,left=True)
    c.alu('cmp',M(4,WIDTH),6); c.branch(13,'bad')
    c.move(I(0),D(6)); c.move(M(0,2),D(6),'w')
    c.alu('cmp',M(4,HEIGHT),6); c.branch(13,'bad')
    c.move(I(0),D(6)); c.move(M(0,5),D(6),'b')
    c.alu('cmp',M(4,DEPTH),6); c.branch(6,'bad')
    c.tst(D(6)); c.branch(15,'bad')
    c.imm('cmp',8,D(6)); c.branch(14,'bad')

    # Check every destination pointer before modifying ANY bitplane.
    c.move(D(6),D(2))
    c.move(A(0),A(1)); c.quick(8,A(1))
    c.label('check_plane')
    c.move(POST(1),D(6))
    c.tst(D(6)); c.branch(7,'bad')
    c.imm('cmp',-1,D(6)); c.branch(7,'bad')
    c.quick(1,D(2),sub=True)
    c.branch(6,'check_plane')

    # Compute 1<<depth (1..256), reject pen >= this limit BEFORE drawing.
    c.move(I(0),D(2)); c.move(M(0,5),D(2),'b')
    c.move(I(1),D(6))
    c.label('compute_limit')
    c.shift(6,1,left=True)
    c.quick(1,D(2),sub=True)
    c.branch(6,'compute_limit')
    c.alu('cmp',D(6),3); c.branch(4,'bad')  # BCC: unsigned pen >= limit

    _emit_safe_guard(c)          # also covers Aga Blit Clear via wrapper
    # Scratch after all pre-validation: [SP] limit, 4(SP) pen.
    # Save bitmap in preserved A4; restore D0/D1/A0/A1 for each OS call.
    c.move(D(3),PRE(7)); c.move(D(6),PRE(7))
    c.move(A(0),A(4))
    c.move(D(0),D(2)); c.move(D(1),D(3))
    c.move(I(1),D(7))
    c.label('plane_loop')
    c.move(M(7,4),D(6))
    c.alu('and',D(7),6)
    c.tst(D(6)); c.branch(7,'plane_clear')
    c.move(I(0xF0),D(6)); c.branch(0,'do_blit')
    c.label('plane_clear'); c.move(I(0),D(6))
    c.label('do_blit')
    c.move(D(2),D(0)); c.move(D(3),D(1))
    c.move(A(4),A(0)); c.move(A(4),A(1))
    c.move(I(0),A(2))                 # TempA=NULL
    c.call_os(LVO_BLTBITMAP)
    c.tst(D(0)); c.branch(7,'blit_failed')
    c.call_os(LVO_WAITBLIT)
    c.shift(7,1,left=True)
    c.alu('cmp',M(7),7)
    c.branch(6,'plane_loop')
    c.move(I(1),D(3)); c.branch(0,'leave_plane_loop')
    c.label('blit_failed'); c.move(I(0),D(3))
    c.label('leave_plane_loop')
    c.quick(8,A(7))                  # exactly discard 2 scratch LONGs
    c.branch(0,'finish')
    c.label('bad'); c.move(I(0),D(3))
    c.label('finish')
    c.raw('4cdf77f7')               # restore saved registers except A3
    c.raw('7400')                   # AMOS integer return D2=0
    c.raw('4e75')                   # RTS
    result=c.out()
    assert len(result)%2==0
    return result,c.labels


