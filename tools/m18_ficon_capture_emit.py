"""M18/R67 68000: capture an exact 16x16 8-plane AGA back-buffer patch.

Aga F Icon Capture(Bank,IconID,X,Y) -> D3=1/0, D2=0.
No AGAPIC, chunky scratch, bank allocation, Blitter writes, palette edits,
screen swap, VBL wait or implicit FICHIP8 staging. Source pixel index 0
produces PRESERVE=1 for masked draw and opaque index-zero in opaque mode.

The selected existing FICON8 slot is only touched after checking ALL bank
metadata, all eight physical screen bitplanes (first/last byte), full 16x16
screen rectangle, selected slot boundaries, safe ScreenBuffer and WaitBlit.
No error paths inside the 288-byte write loop. Bytes outside slot untouched.

AMOS ABI: D3=Y; A3 stacked X, IconID, Bank (in pop order).
"""
from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr

ENTRY_INDEX=66
STATE_PTR=0x1c8
LVO_TYPEOFMEM=-534
LVO_GETMSG=-372
LVO_WAITBLIT=-228
CHIP_FLAG=2
MIN_BANK,MAX_BANK=5,65535
MIN_COUNT,MAX_COUNT=4,4096
NAME=b"FICON8  "
HEADER=12
SLOT=288
GETADR_MARKER=rjsr(main_index("Bnk.GetAdr"))
F=dict(y=0,x=4,icon=8,bank=12,base=16,length=20,count=24,
       slot=28,state=32,db=36,bitmap=40,
       width=44,height=48,stride=52,xbyte=56,initbit=60,
       rowoff=64,firstoff=68,lastoff=72,rowptr=76)
FRAME=128

def emit_ficon_capture():
    c=Code();B,L=c.branch,c.label
    def get(k,reg):c.move(M(2,F[k]),reg)
    def put(reg,k):c.move(reg,M(2,F[k]))
    def ensure_mem(reg,chip=False):
        c.move(reg,A(1))
        c.raw("2c780004")    # MOVEA.L (4).W,A6 ExecBase
        c.call_os(LVO_TYPEOFMEM)
        if chip:c.imm("and",CHIP_FLAG,D(0))
        c.tst(D(0));B(7,"fail")
    def checked_add(a,b):
        c.alu("add",b,a);B(5,"fail")

    c.raw("48e7efee")      # standard AMOS preserves D0,D1,D4.. / A0..A6
    c.raw("4fefff80")      # LEA -128(SP),SP
    c.move(A(7),A(2))
    put(D(3),"y")
    for f in ("x","icon","bank"):
        c.move(POST(3),D(7));put(D(7),f)
    c.move(I(0),D(3))     # default result 0

    for k,mi,ma in (("bank",MIN_BANK,MAX_BANK),
                    ("icon",1,MAX_COUNT)):
        get(k,D(0));c.imm("cmp",mi,D(0));B(5,"fail")
        c.imm("cmp",ma,D(0));B(2,"fail")
    for k in ("x","y"):
        get(k,D(0));c.tst(D(0));B(11,"fail")
        c.imm("cmp",4096,D(0));B(2,"fail")

    # AMOS-owned FICON8 bank, strict header, size, selected slot, TypeOfMem.
    get("bank",D(0));c.raw(GETADR_MARKER.hex())
    c.move(A(0),D(5));c.imm("cmp",24,D(5));B(3,"fail")
    c.move(D(5),D(0));c.imm("and",1,D(0));B(6,"fail")
    put(D(5),"base")
    ensure_mem(D(5))
    get("base",D(0));c.imm("sub",24,D(0))
    ensure_mem(D(0))
    get("base",A(0))
    c.move(M(0,-20),D(4));c.imm("cmp",16+HEADER,D(4));B(5,"fail")
    c.imm("sub",16,D(4));c.imm("cmp",HEADER+MAX_COUNT*SLOT,D(4));B(2,"fail")
    put(D(4),"length")
    get("base",D(0));checked_add(0,D(4))
    c.quick(1,D(0),sub=True);ensure_mem(D(0))
    get("base",A(0))
    c.move(M(0,-16),D(0));get("bank",D(1))
    c.alu("cmp",D(1),0);B(6,"fail")
    c.move(I(0),D(0));c.move(M(0,-12),D(0),"w")
    c.tst(D(0));B(7,"flags_ok")
    c.imm("and",0xfffd,D(0),"w")
    c.imm("cmp",1,D(0),"w");B(6,"fail")
    L("flags_ok")
    c.move(M(0,-8),D(0));c.imm("cmp",0x4649434f,D(0));B(6,"fail")
    c.move(M(0,-4),D(0));c.imm("cmp",0x4e382020,D(0));B(6,"fail")
    c.move(M(0),D(0));c.alu("cmp",M(2,F["length"]),0);B(6,"fail")
    c.move(I(0),D(0));c.move(M(0,4),D(0),"w")
    c.imm("cmp",MIN_COUNT,D(0));B(5,"fail")
    c.imm("cmp",MAX_COUNT,D(0));B(2,"fail")
    put(D(0),"count")
    get("icon",D(1));c.alu("cmp",D(1),0);B(5,"fail")
    c.move(I(SLOT),D(1));c.word(0xc0c1) # MULU.W #288,D0 -> long
    c.imm("add",HEADER,D(0))
    c.alu("cmp",M(2,F["length"]),0);B(6,"fail")
    for off,expect in ((6,16),(8,16),(10,8)):
        c.move(I(0),D(0));c.move(M(0,off),D(0),"w")
        c.imm("cmp",expect,D(0));B(6,"fail")
    get("icon",D(0));c.quick(1,D(0),sub=True)
    c.move(I(SLOT),D(1));c.word(0xc0c1)
    c.imm("add",HEADER,D(0))
    get("base",D(5));checked_add(0,D(5));put(D(0),"slot")
    c.imm("add",SLOT-1,D(0));B(5,"fail")
    ensure_mem(D(0))

    # Independent private AGA screen + its inactive back ScreenBuffer.
    c.move(M(5,STATE_PTR),A(4));c.move(A(4),D(0))
    c.tst(D(0));B(7,"fail")
    put(A(4),"state")
    for off in (0,8,32):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,"fail")
    for off,k in ((12,"width"),(16,"height")):
        c.move(M(4,off),D(0))
        c.imm("cmp",16,D(0));B(5,"fail")
        c.imm("cmp",4096,D(0));B(2,"fail")
        put(D(0),k)
    c.move(M(4,28),D(0));c.imm("cmp",8,D(0));B(6,"fail")
    for k,limit in (("x","width"),("y","height")):
        get(limit,D(0));c.imm("sub",16,D(0))
        get(k,D(1));c.alu("cmp",D(0),1);B(2,"fail")

    get("state",A(4));c.move(M(4,32),A(0))
    put(A(0),"db")
    c.move(M(0,8),D(0));c.tst(D(0));B(7,"front_zero")
    c.imm("cmp",1,D(0));B(6,"fail")
    get("db",A(0));c.move(M(0),A(1));B(0,"have_sb")
    L("front_zero")
    get("db",A(0));c.move(M(0,4),A(1))
    L("have_sb")
    c.move(A(1),D(0));c.tst(D(0));B(7,"fail")
    c.move(M(1),A(0));c.move(A(0),D(0))
    c.tst(D(0));B(7,"fail");put(A(0),"bitmap")
    c.move(I(0),D(0));c.move(M(0),D(0),"w")
    c.imm("cmp",2,D(0));B(5,"fail")
    c.imm("cmp",65534,D(0));B(2,"fail")
    c.move(D(0),D(1));c.imm("and",1,D(1));B(6,"fail")
    put(D(0),"stride")
    c.shift(0,3,left=True);c.alu("cmp",M(2,F["width"]),0);B(5,"fail")
    get("bitmap",A(0))
    c.move(I(0),D(0));c.move(M(0,2),D(0),"w")
    c.alu("cmp",M(2,F["height"]),0);B(5,"fail")
    c.move(I(0),D(0));c.move(M(0,5),D(0),"b")
    c.imm("cmp",8,D(0));B(6,"fail")

    get("x",D(0));c.shift(0,3,left=False);put(D(0),"xbyte")
    get("x",D(0));c.imm("and",7,D(0))
    c.move(I(7),D(1));c.alu("sub",D(0),1);put(D(1),"initbit")
    get("y",D(0));get("stride",D(1))
    c.word(0xc0c1)          # MULU.W stride, y -> LONG row offset
    put(D(0),"rowoff")
    get("xbyte",D(1));checked_add(0,D(1));put(D(0),"firstoff")
    get("y",D(0));c.imm("add",15,D(0))
    get("stride",D(1));c.word(0xc0c1)
    get("x",D(1));c.imm("add",15,D(1))
    c.shift(1,3,left=False);checked_add(0,D(1));put(D(0),"lastoff")

    # All 8 planes must be valid physical Chip at first AND last used byte,
    # including X not aligned to an eight-pixel byte boundary.
    get("bitmap",A(4));c.quick(8,A(4));c.move(I(8),D(5))
    L("check_plane")
    c.move(POST(4),D(7))
    c.tst(D(7));B(7,"fail")
    c.imm("cmp",-1,D(7));B(7,"fail")
    c.move(D(7),D(0));c.imm("and",1,D(0));B(6,"fail")
    c.move(D(7),D(0));get("firstoff",D(1))
    checked_add(0,D(1));ensure_mem(D(0),chip=True)
    c.move(D(7),D(0));get("lastoff",D(1))
    checked_add(0,D(1));ensure_mem(D(0),chip=True)
    c.quick(1,D(5),sub=True);B(6,"check_plane")

    # Read only when the inactive ScreenBuffer is Safe.
    get("db",A(4));c.move(M(4,20),D(0))
    c.imm("and",1,D(0));B(7,"safe")
    c.move(M(4,12),A(0));c.move(A(0),D(0))
    c.tst(D(0));B(7,"fail")
    c.raw("2c780004");c.call_os(LVO_GETMSG)
    c.tst(D(0));B(7,"fail")
    get("db",A(4));c.move(M(4,20),D(0))
    c.imm("and",0xfffffffe,D(0));c.move(D(0),M(4,20))
    L("safe")
    # Ensure preceding async graphics Blitter writes have finished. No VBL.
    get("state",A(4));c.move(M(4,8),A(6))
    c.call_os(LVO_WAITBLIT)

    # No rejection branches in the copy region. Each row writes exactly
    # [preserve mask WORD, plane0..7 WORDS] = 18 bytes, 16 rows = 288.
    get("slot",D(0));put(D(0),"rowptr")
    c.move(I(16),D(6))
    L("row")
    get("bitmap",A(0));c.quick(8,A(0))
    get("rowptr",A(1));c.quick(2,A(1))
    c.move(I(8),D(5))
    c.move(I(0),D(7))         # OR of 8 planes (visible)
    L("plane")
    c.move(POST(0),A(4))       # next bitplane
    get("rowoff",D(0));c.word(0xd9c0) # ADDA.L D0,A4
    get("xbyte",D(0));c.word(0xd9c0)
    c.move(I(0),D(4))         # planar row output
    c.move(I(0x8000,"w"),D(2),"w")
    get("initbit",D(1))
    c.move(I(16),D(0))
    L("pixel")
    c.move(I(0),D(3))
    c.move(M(4),D(3),"b")     # read one source bitplane byte
    c.word(0x0303)           # BTST D1,D3 (1 if bit set)
    B(7,"no_pixel")
    c.alu("or",D(2),4,"w")
    L("no_pixel")
    c.word(0xe24a)           # LSR.W #1,D2 -> next destination bit
    c.quick(1,D(1),sub=True)
    B(10,"bit_pos_ok")        # BPL
    c.quick(1,A(4))
    c.move(I(7),D(1))
    L("bit_pos_ok")
    c.quick(1,D(0),sub=True);B(6,"pixel")
    c.move(D(4),POST(1),"w")
    c.alu("or",D(4),7,"w")
    c.quick(1,D(5),sub=True);B(6,"plane")
    c.word(0x4647)          # NOT.W D7; index-zero mask
    get("rowptr",A(1));c.move(D(7),M(1),"w")
    get("rowoff",D(0));get("stride",D(1))
    c.alu("add",D(1),0);put(D(0),"rowoff")
    get("rowptr",D(0));c.imm("add",18,D(0));put(D(0),"rowptr")
    c.quick(1,D(6),sub=True);B(6,"row")
    c.move(I(1),D(3))
    L("fail")
    c.raw("4fef0080")
    c.raw("4cdf77f7")
    c.raw("74004e75")
    return c.out(),c.labels
