"""M16/R45 experimental 68000 CPU AGAPIC image decoder and planar writer.

One AP20 integer function: Aga Image Draw(Start(bank),Length(bank),X,Y,Mode).
D3=mode; (A3)+: Y, X, Length, Start. D3=1 on success, D2=0.
No allocation, no Blitter, no automatic swap or VBL; writes only inactive
private AGA Intuition ScreenBuffer AFTER nonblocking Safe. Strict two-pass
RLE validation: every row and packet checked before the first pixel write.

This is a native 68000 candidate requiring CPU/Unicorn Gate A and
interpreted AMOS/WinUAE Gate B; R44 LAST_GOOD is not changed.
"""
from m68k_emit import Code, D, A, M, POST, I

ENTRY_INDEX = 55
GETP = b"GetP"
STATE_PTR = 0x1C8
LVO_TYPEOFMEM = -534
LVO_GETMSG = -372
MAX_BYTES = 0x01000000
MAX_PIXELS = 0x00400000

# Stack temporary 192 bytes, AFTER the register-save MOVEM.
# Storage is used for locals only, never for a decoded image.
F = dict(mode=0, y=4, x=8, length=12, base=16,
         width=20, height=24, depth=28, flags=32,
         groupbytes=36, groups=40, pad=44, stream=48,
         scrw=52, scrh=56, stride=60, bitmap=64,
         row=68, passno=72, current=76, end=80,
         decoded=84, left=88, repeat=92, group=96,
         bit=100, dx=104, dy=108, destoff=112,
         bytebit=116, planesleft=120, srcbit=124)

# P2 only: share the *tested* P1e 020 painter with the historical R46
# decoder, which has no source crop. The free end of the existing 192-byte
# frame holds zero source offsets and full-image extents. P1e reserves
# offset 148 for the mask, 152..183 for 8 bitplane pointers and 184 for
# the visible width. The historical emit_image_draw() remains byte-identical.
F020 = dict(F, srcx=128, srcy=132, regionw=136, regionh=140)
assert max(F.values()) == 124 and F020["regionh"] + 4 <= 148


def emit_image_draw(*, accept_loaded_flags_zero=False, opt020=False,
                    reset_failure_d3=False):
    if reset_failure_d3 and not opt020:
        raise ValueError("D3 rejection hardening is only defined for OPT020/P2")
    c = Code()
    def L(name): c.label(name)
    def B(cond,name): c.branch(cond,name)
    def ld(name,reg): c.move(M(2,F[name]),reg)
    def st(reg,name): c.move(reg,M(2,F[name]))
    def fail_if_zero(reg,where):
        c.move(reg,D(0)); c.tst(D(0)); B(7,where)
    def uword(off,dreg=0):
        c.move(I(0),D(dreg))
        c.move(M(0,off),D(dreg),"w")
    def invalid_if_memory_missing():
        c.tst(D(0)); B(7,"reject")

    # Full standard AP20 preserved set, minus D3, D2, and consumed A3.
    c.raw("48e7efee")
    c.raw("4fefff40")             # LEA -192(SP),SP
    c.move(A(7),A(2))            # FRAME POINTER: BSR changes SP
    st(D(3),"mode")
    c.move(POST(3),D(7)); st(D(7),"y")
    c.move(POST(3),D(6)); st(D(6),"x")
    c.move(POST(3),D(4)); st(D(4),"length")
    c.move(POST(3),D(5)); st(D(5),"base")
    c.move(I(0),D(3))             # default failure
    if opt020:
        # Entire check uses 68000-safe opcodes. Reject 68000 before 020
        # instructions, Safe acquisition or any pixel write.
        c.raw("20780004")          # MOVEA.L 4.W,A0: ExecBase
        c.move(A(0),D(0)); c.tst(D(0)); B(7,"reject")
        c.move(M(0,0x128),D(0),"w")  # ExecBase.AttnFlags
        c.word(0x0800); c.word(1)  # BTST #AFF_68020,D0
        B(7,"reject")
    ld("mode",D(0))
    c.imm("cmp",1,D(0)); B(2,"reject")  # unsigned: includes negative
    c.imm("cmp",32,D(4)); B(5,"reject")
    c.imm("cmp",MAX_BYTES,D(4)); B(2,"reject")
    c.imm("cmp",24,D(5)); B(3,"reject")
    c.move(D(5),D(0)); c.imm("and",1,D(0)); B(6,"reject")
    # API coordinates are bounded signed16, as established by M15.
    for reg in (6,7):
        c.imm("cmp",-32768,D(reg)); B(13,"reject")
        c.imm("cmp",32767,D(reg)); B(14,"reject")
    # Check address wrap and managed memory at bank header/last byte.
    c.move(D(5),D(0)); c.alu("add",D(4),0); B(5,"reject")
    c.quick(1,D(0),sub=True); c.move(D(0),A(1))
    c.raw("2c780004")             # ExecBase
    c.call_os(LVO_TYPEOFMEM)
    invalid_if_memory_missing()
    c.move(D(5),D(0)); c.imm("sub",24,D(0))
    c.move(D(0),A(1))
    c.call_os(LVO_TYPEOFMEM)
    invalid_if_memory_missing()
    # AMOS-native DATA bank envelope: Start-20 length=DATA+16;
    # Start-16 number in 5..65535; -12 class=1/3; -8 name.
    c.move(D(5),A(0))
    c.move(M(0,-20),D(0))
    c.move(D(4),D(1)); c.imm("add",16,D(1))
    c.alu("cmp",D(1),0); B(6,"reject")
    c.move(M(0,-16),D(0))
    c.imm("cmp",5,D(0)); B(5,"reject")
    c.imm("cmp",65535,D(0)); B(2,"reject")
    uword(-12)
    # R45 intentionally accepts only DATA/FAST=1 or DATA/CHIP=3.
    # WinUAE's genuine, reloaded AGAPIC bank reports FLAGS=0;
    # R46 permits this observed case, while preserving the exact R45
    # binary, its failing archive and its original unit-test semantics.
    if accept_loaded_flags_zero:
        c.tst(D(0)); B(7,"native_bank_flags_ok")
    c.imm("and",0xfffd,D(0),"w")
    c.imm("cmp",1,D(0)); B(6,"reject")
    if accept_loaded_flags_zero:
        L("native_bank_flags_ok")
    c.move(M(0,-8),D(0))
    c.imm("cmp",0x41474150,D(0)); B(6,"reject")
    c.move(M(0,-4),D(0))
    c.imm("cmp",0x49432020,D(0)); B(6,"reject")

    # AGAPIC v1 header (big endian), strictly matches Length(bank).
    c.move(M(0),D(0))
    c.imm("cmp",0x41474150,D(0)); B(6,"reject")
    uword(4)
    c.imm("cmp",0x4943,D(0)); B(6,"reject")
    uword(6)
    c.imm("cmp",1,D(0)); B(6,"reject")
    uword(8); st(D(0),"flags")
    c.imm("cmp",1,D(0)); B(2,"reject")
    ld("mode",D(1))
    c.tst(D(1)); B(7,"mode_valid")
    c.tst(D(0)); B(7,"reject")   # mask required for mode=1
    L("mode_valid")
    uword(10)
    c.imm("cmp",1,D(0)); B(6,"reject")
    uword(12); st(D(0),"width")
    c.tst(D(0)); B(7,"reject")
    c.imm("cmp",4096,D(0)); B(2,"reject")
    uword(14); st(D(0),"height")
    c.tst(D(0)); B(7,"reject")
    c.imm("cmp",4096,D(0)); B(2,"reject")
    # At most 4 million indexed pixels; 4096x4096 is rejected.
    ld("width",D(1))
    c.word(0xc0c1)             # MULU.W D1,D0
    c.imm("cmp",MAX_PIXELS,D(0)); B(2,"reject")
    uword(16); st(D(0),"depth")
    c.tst(D(0)); B(7,"reject")
    c.imm("cmp",8,D(0)); B(2,"reject")
    c.move(D(0),D(1)); ld("flags",D(0))
    c.alu("add",D(1),0)
    c.shift(0,1,left=True)
    st(D(0),"groupbytes")
    c.move(I(0),D(1)); c.move(M(0,18),D(1),"w")
    c.alu("cmp",D(1),0); B(6,"reject")
    c.move(M(0,20),D(0))
    c.imm("cmp",32,D(0)); B(6,"reject")
    ld("height",D(0))
    c.quick(1,D(0)); c.shift(0,2,left=True)
    c.imm("add",32,D(0))
    st(D(0),"stream")
    c.move(M(0,24),D(1))
    c.alu("cmp",D(1),0); B(6,"reject")
    c.alu("cmp",D(4),0); B(2,"reject")  # stream <= length
    c.move(M(0,28),D(0))
    c.alu("cmp",D(4),0); B(6,"reject")
    ld("width",D(0)); c.imm("add",15,D(0))
    c.shift(0,4,left=False)
    st(D(0),"groups")
    # Last 16-pixel group must have zero bits beyond source width.
    # For width modulo 16 = rem, padmask = (1<<(16-rem))-1.
    ld("width",D(1)); c.imm("and",15,D(1))
    c.move(I(0),D(0))
    c.tst(D(1)); B(7,"pad_done")
    c.move(I(0xffff),D(0))
    L("pad_shift")
    c.word(0xe248)             # LSR.W #1,D0
    c.quick(1,D(1),sub=True)
    B(6,"pad_shift")
    L("pad_done")
    st(D(0),"pad")

    # Screen, DB, bitmap, physical dimensions and all planes exactly as
    # R40/R43, except no RastPort or graphics.library drawing is used.
    c.move(M(5,STATE_PTR),A(4))
    fail_if_zero(A(4),"reject")
    for offset in (0,8,32):
        c.move(M(4,offset),D(0)); c.tst(D(0)); B(7,"reject")
    for offset,target in ((12,"scrw"),(16,"scrh")):
        c.move(M(4,offset),D(0))
        c.tst(D(0)); B(15,"reject")
        c.imm("cmp",32767,D(0)); B(14,"reject")
        st(D(0),target)
    c.move(M(4,28),D(0))
    c.alu("cmp",M(2,F["depth"]),0); B(6,"reject")
    c.move(M(4,32),A(0))
    c.move(M(0,8),D(0))
    c.tst(D(0)); B(7,"front_zero")
    c.imm("cmp",1,D(0)); B(6,"reject")
    c.move(M(4,32),A(0))
    c.move(M(0),A(1))
    B(0,"have_sb")
    L("front_zero")
    c.move(M(4,32),A(0))
    c.move(M(0,4),A(1))
    L("have_sb")
    fail_if_zero(A(1),"reject")
    c.move(M(1),A(0))         # inactive ScreenBuffer.sb_BitMap
    fail_if_zero(A(0),"reject")
    st(A(0),"bitmap")
    c.move(I(0),D(1)); c.move(M(0,0),D(1),"w")
    c.tst(D(1)); B(7,"reject")
    st(D(1),"stride")
    c.shift(1,3,left=True)
    c.alu("cmp",M(2,F["scrw"]),1); B(13,"reject")
    c.move(I(0),D(1)); c.move(M(0,2),D(1),"w")
    c.alu("cmp",M(2,F["scrh"]),1); B(13,"reject")
    c.move(I(0),D(1)); c.move(M(0,5),D(1),"b")
    c.alu("cmp",M(2,F["depth"]),1); B(6,"reject")
    c.move(D(1),D(0))
    c.move(A(0),A(1)); c.quick(8,A(1))
    L("planes_check")
    c.move(POST(1),D(1))
    c.tst(D(1)); B(7,"reject")
    c.imm("cmp",-1,D(1)); B(7,"reject")
    c.quick(1,D(0),sub=True); B(6,"planes_check")

    # PASS 0 decodes and checks every RLE byte without touching any pixels.
    c.move(I(0),M(2,F["passno"]))
    B(1,"decode_rows")
    c.tst(D(0)); B(7,"reject")

    # A fully off-screen but structurally valid image is a no-op success.
    ld("x",D(0)); c.alu("cmp",M(2,F["scrw"]),0); B(12,"success")
    c.alu("add",M(2,F["width"]),0)
    c.tst(D(0)); B(15,"success")
    ld("y",D(0)); c.alu("cmp",M(2,F["scrh"]),0); B(12,"success")
    c.alu("add",M(2,F["height"]),0)
    c.tst(D(0)); B(15,"success")

    # R27 nonblocking Safe acquisition BEFORE the first direct CPU write.
    c.move(M(4,32),A(0))
    c.move(M(0,20),D(0))
    c.imm("and",1,D(0))
    B(7,"safe")
    c.move(M(0,12),A(0))
    fail_if_zero(A(0),"reject")
    c.raw("2c780004")            # ExecBase (GetMsg)
    c.call_os(LVO_GETMSG)
    c.tst(D(0)); B(7,"reject")
    c.move(M(4,32),A(0))
    c.move(M(0,20),D(0))
    c.imm("and",0xfffffffe,D(0))
    c.move(D(0),M(0,20))
    L("safe")
    if opt020:
        # P1e painter accepts a crop; Image Draw is the WHOLE AGAPIC.
        # All four words live in the previously unused local frame.
        c.move(I(0),D(0))
        c.move(D(0),M(2,F020["srcx"]))
        c.move(D(0),M(2,F020["srcy"]))
        ld("width",D(0)); c.move(D(0),M(2,F020["regionw"]))
        ld("height",D(0)); c.move(D(0),M(2,F020["regionh"]))
    c.move(I(1),M(2,F["passno"]))
    B(1,"decode_rows")
    c.tst(D(0)); B(7,"reject")  # impossible unless bank is modified in flight
    L("success")
    c.move(I(1),D(3))
    if reset_failure_d3:
        # P1e 020 paint kernels may leave D3=1 even when PASS 1 rejects
        # a bank modified *after* successful PASS 0.  Keep the validated
        # R46/R70/R71 emitters byte-for-byte identical unless explicitly
        # enabled by a new candidate. A successful return must skip reset.
        B(0,"p2_exit")
    L("reject")
    if reset_failure_d3:
        c.word(0x7600)  # MOVEQ #0,D3: all rejection paths return false
        L("p2_exit")
    c.raw("4fef00c0")           # LEA +192(SP),SP
    c.raw("4cdf77f7")           # restore all except result D3,D2 and cursor A3
    c.raw("74004e75")           # D2=0 ; RTS

    # The row decoder runs twice. One 16-pixel group is materialized as a
    # pointer into the original Fast-RAM bank, never into a Chip-RAM cache.
    L("decode_rows")
    c.move(I(0),M(2,F["row"]))
    L("row_begin")
    ld("row",D(0))
    c.alu("cmp",M(2,F["height"]),0)
    B(12,"rows_ok")
    c.shift(0,2,left=True)
    c.move(D(0),D(1)); ld("base",D(0))
    c.imm("add",32,D(0))
    c.alu("add",D(1),0)
    c.move(D(0),A(1))             # address of row offsets
    c.move(POST(1),D(0))          # first offset
    c.move(POST(1),D(1))          # next offset
    c.alu("cmp",D(1),0); B(4,"rows_bad")  # rowstart >= next
    c.alu("cmp",M(2,F["stream"]),0); B(5,"rows_bad")
    c.alu("cmp",M(2,F["length"]),1); B(2,"rows_bad")
    ld("row",D(2)); c.tst(D(2)); B(6,"not_first")
    c.alu("cmp",M(2,F["stream"]),0); B(6,"rows_bad")
    L("not_first")
    c.move(M(2,F["height"]),D(2)); c.quick(1,D(2),sub=True)
    c.alu("cmp",M(2,F["row"]),2); B(6,"not_last")
    c.alu("cmp",M(2,F["length"]),1); B(6,"rows_bad")
    L("not_last")
    ld("base",D(2))
    c.alu("add",D(2),0); st(D(0),"current")
    c.alu("add",D(2),1); st(D(1),"end")
    c.move(I(0),M(2,F["decoded"]))
    c.move(I(0),M(2,F["left"]))
    c.move(I(0),M(2,F["repeat"]))

    L("group_loop")
    ld("decoded",D(0))
    c.alu("cmp",M(2,F["groups"]),0); B(12,"row_done")
    ld("left",D(0)); c.tst(D(0)); B(6,"have_packet")
    # New RLE packet control. Every row has its own strict end pointer.
    ld("current",D(0)); c.alu("cmp",M(2,F["end"]),0)
    B(4,"rows_bad")
    c.move(D(0),A(0))
    c.move(I(0),D(0)); c.move(POST(0),D(0),"b") # unsigned control
    c.move(D(0),D(1)); c.imm("and",0x7f,D(1))
    c.quick(1,D(1)); st(D(1),"left")
    c.move(D(0),D(2)); c.imm("and",0x80,D(2))
    st(D(2),"repeat")
    ld("decoded",D(2))
    c.alu("add",D(1),2)
    c.alu("cmp",M(2,F["groups"]),2); B(14,"rows_bad")
    c.move(A(0),D(2)); st(D(2),"current")
    ld("repeat",D(2)); c.tst(D(2)); B(7,"literal_packet")
    st(A(0),"group")            # repeated group pointer
    ld("groupbytes",D(2))
    B(0,"packet_size")
    L("literal_packet")
    ld("groupbytes",D(2))
    c.word(0xc4c1)             # MULU.W D1,D2; packet literal bytes
    L("packet_size")
    c.move(A(0),D(0)); c.alu("add",D(2),0); B(5,"rows_bad")
    c.alu("cmp",M(2,F["end"]),0); B(14,"rows_bad")
    L("have_packet")
    ld("repeat",D(2)); c.tst(D(2)); B(6,"repeated_group")
    ld("current",D(0)); st(D(0),"group")
    c.alu("add",M(2,F["groupbytes"]),0)
    st(D(0),"current")
    B(0,"group_ready")
    L("repeated_group")
    # First repeated group must advance current pointer just once.
    ld("current",D(0))
    ld("group",D(1))
    c.alu("cmp",D(1),0)
    B(6,"group_ready")         # already advanced (for this packet)
    c.alu("add",M(2,F["groupbytes"]),0)
    st(D(0),"current")
    L("group_ready")
    # Pad check on the last group of EVERY scanline, in BOTH passes.
    ld("pad",D(0)); c.tst(D(0)); B(7,"group_pad_ok")
    ld("decoded",D(1)); c.quick(1,D(1))
    c.alu("cmp",M(2,F["groups"]),1); B(6,"group_pad_ok")
    ld("group",A(0))
    ld("groupbytes",D(1)); c.shift(1,1,left=False)
    L("pad_word")
    c.move(I(0),D(2)); c.move(POST(0),D(2),"w")
    c.alu("and",D(0),2,"w"); B(6,"rows_bad")
    c.quick(1,D(1),sub=True); B(6,"pad_word")
    L("group_pad_ok")
    ld("passno",D(0)); c.tst(D(0)); B(7,"dont_paint")
    B(1,"paint_group")
    L("dont_paint")
    ld("left",D(0)); c.quick(1,D(0),sub=True); st(D(0),"left")
    ld("decoded",D(0)); c.quick(1,D(0)); st(D(0),"decoded")
    B(0,"group_loop")

    L("row_done")
    ld("current",D(0))
    c.alu("cmp",M(2,F["end"]),0); B(6,"rows_bad")
    ld("row",D(0)); c.quick(1,D(0)); st(D(0),"row")
    B(0,"row_begin")
    L("rows_ok")
    c.move(I(1),D(0))
    c.raw("4e75")                # RTS to main
    L("rows_bad")
    c.move(I(0),D(0))
    c.raw("4e75")                # RTS to main

    # Direct planar CPU paint. Scan one group at a time, one pixel per bit.
    # All destination words/bytes are in the *inactive* Intuition bitmap,
    # and pixel/byte offsets are clipped before a memory write.
    L("paint_group")
    if opt020:
        from opt020_p1e_painter_emit import emit_paint_group_020
        emit_paint_group_020(c, F020)
    else:
        ld("row",D(0)); c.alu("add",M(2,F["y"]),0)
        c.tst(D(0)); B(11,"paint_done")
        c.alu("cmp",M(2,F["scrh"]),0); B(12,"paint_done")
        st(D(0),"dy")
        c.move(I(0),M(2,F["bit"]))
        L("pixel_loop")
        ld("bit",D(0)); c.imm("cmp",16,D(0))
        B(12,"paint_done")
        ld("decoded",D(1))
        c.shift(1,4,left=True)
        c.alu("add",D(0),1)          # source pixel index in scanline
        c.alu("cmp",M(2,F["width"]),1)
        B(12,"paint_done")         # padding in last group
        c.alu("add",M(2,F["x"]),1)
        c.tst(D(1)); B(11,"pixel_next")
        c.alu("cmp",M(2,F["scrw"]),1); B(12,"pixel_next")
        st(D(1),"dx")
        c.move(I(15),D(0))
        c.alu("sub",M(2,F["bit"]),0)
        st(D(0),"srcbit")
        ld("mode",D(2)); c.tst(D(2)); B(7,"pixel_opaque")
        ld("group",A(0))
        c.move(I(0),D(2)); c.move(M(0),D(2),"w")
        c.word(0x0102)             # BTST D0,D2 (mask bit)
        B(7,"pixel_next")
        L("pixel_opaque")
        # destoff = dy * BytesPerRow + (dx / 8); 68000 MULU.W.
        ld("dy",D(0)); ld("stride",D(1))
        c.word(0xc0c1)             # MULU.W D1,D0
        ld("dx",D(1)); c.shift(1,3,left=False)
        c.alu("add",D(1),0)
        st(D(0),"destoff")
        ld("dx",D(1)); c.imm("and",7,D(1))
        c.move(I(7),D(0)); c.alu("sub",D(1),0)
        st(D(0),"bytebit")
        ld("group",A(1))
        ld("flags",D(0)); c.tst(D(0)); B(7,"start_planes")
        c.quick(2,A(1))            # skip independent mask WORD
        L("start_planes")
        ld("bitmap",A(6))
        c.quick(8,A(6))            # pointer to Bitmap.Planes[0]
        ld("depth",D(0)); st(D(0),"planesleft")
        L("plane_loop")
        c.move(I(0),D(2)); c.move(POST(1),D(2),"w")
        c.move(POST(6),A(0))      # destination Plane*
        c.move(A(0),D(4))
        c.alu("add",M(2,F["destoff"]),4)
        c.move(D(4),A(0))
        ld("srcbit",D(0)); ld("bytebit",D(1))
        c.word(0x0102)            # BTST D0,D2
        B(7,"plane_clear")
        c.word(0x03d0)            # BSET D1,(A0), bit 7 = leftmost
        B(0,"plane_next")
        L("plane_clear")
        c.word(0x0390)            # BCLR D1,(A0), also writes colour 0
        L("plane_next")
        ld("planesleft",D(0)); c.quick(1,D(0),sub=True)
        st(D(0),"planesleft"); B(6,"plane_loop")
        L("pixel_next")
        ld("bit",D(0)); c.quick(1,D(0)); st(D(0),"bit")
        B(0,"pixel_loop")
        L("paint_done")
        c.raw("4e75")
    raw = c.out()
    assert len(raw)%2 == 0
    return raw,c.labels
