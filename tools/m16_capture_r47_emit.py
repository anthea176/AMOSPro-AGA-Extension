"""EXPERIMENTAL M16 R47: Aga Image Capture native 68000 entry and bank bridge.

Public *candidate* API: _OK=Aga Image Capture(Bank,X,Y,Width,Height,TransparentIndex).
D3 = TransparentIndex; A3 stack arguments, in pop order: H,W,Y,X,Bank.
Produces exact AGAPIC v1 DATA payload from inactive AGA back buffer, with
Fast-preferred/Chip-fallback AMOS reservation and non-destructive collision
precheck. A temporary one-row buffer is used to compute exact compressed
length, then the output is regenerated directly into the reserved bank.

AMOS main-library Rjsr numeric IDs 297/300/316/319 were derived by counting
Lib_Def/Lib_Par in marc365/AMOS-Professional-365/+Lib.s (main v2 source).
They MUST be confirmed on the target AMOS runtime and under Compiler BEFORE
this candidate can be promoted or considered safe to install. These are
AP20 relocator pseudo-instructions, NOT executable 68k until linked by AMOS.
Bnk.Reserve deletes any preexisting bank: do not call without checking.
The emitted native segment appends the already Unicorn-tested row core.
No binary or public API is changed by importing this module.
"""
from m68k_emit import Code, D, A, M, POST, I
from m16_capture_r47_core_emit import emit_scanline_rle

LVO_ALLOCVEC, LVO_FREEVEC, LVO_GETMSG = -684, -690, -372
STATE_PTR = 0x1C8
IDX_GETADR, IDX_EFF, IDX_RESERVE, IDX_CHANGE = 297, 300, 316, 319
NAME = b"AGAPIC  "
MAX_PAYLOAD, MAX_PIXELS = 0x1000000, 0x400000

F = dict(bank=0,x=4,y=8,width=12,height=16,transparent=20,
         state=24,db=28,bitmap=32,stride=36,depth=40,
         screenw=44,screenh=48,temp=52,rowcap=56,total=60,
         bankptr=64,row=68,tableptr=72,streamptr=76,
         bankend=80,masked=84,result=88,streamoffset=92)
FRAME = 224


def emit_capture():
    c=Code()
    def L(n): c.label(n)
    def B(cond,name): c.branch(cond,name)
    def S(reg,name): c.move(reg,M(2,F[name]))
    def G(name,reg): c.move(M(2,F[name]),reg)
    def RJ(index):  # Compiler/interpreter relocation, NOT a raw JSR.
        c.raw("fe11f700")
        c.word(index)
    def nonzero(reg,to="fail"):
        c.move(reg,D(0)); c.tst(D(0)); B(7,to)
    def osbase(): c.raw("2c780004")  # MOVEA.L 4.W,A6

    # AP20 ABI: preserve all except D2 integer type, D3 result and A3 consumed args.
    c.raw("48e7efee")                 # MOVEM.L standard AGA preserved set
    c.raw("4fefff20")                 # LEA -224(SP),SP
    c.move(A(7),A(2))                 # frame pointer
    S(D(3),"transparent")
    for field in ("height","width","y","x","bank"):
        c.move(POST(3),D(7)); S(D(7),field)
    for field in ("temp","bankptr","result"):
        c.move(I(0),M(2,F[field]))
    c.move(I(0),D(3))

    # Validate bank number before touching another AMOS bank or screen.
    G("bank",D(0))
    c.imm("cmp",5,D(0)); B(5,"fail")
    c.imm("cmp",65535,D(0)); B(2,"fail")
    # AMOS private AGA Intuition screen and dimension/depth state.
    c.move(M(5,STATE_PTR),A(4)); nonzero(A(4))
    S(A(4),"state")
    for off in (0,8,32):
        c.move(M(4,off),D(0)); c.tst(D(0)); B(7,"fail")
    c.move(M(4,32),A(0)); S(A(0),"db")
    for off,field in ((12,"screenw"),(16,"screenh"),(28,"depth")):
        c.move(M(4,off),D(0))
        c.tst(D(0)); B(15,"fail")
        c.imm("cmp",8 if field=="depth" else 4096,D(0)); B(2,"fail")
        S(D(0),field)

    # Entire source rectangle must fit; never clip.
    for field in ("x","y"):
        G(field,D(0)); c.tst(D(0)); B(11,"fail")
    for field in ("width","height"):
        G(field,D(0)); c.tst(D(0)); B(15,"fail")
        c.imm("cmp",4096,D(0)); B(2,"fail")
    for field,screen_field,origin in (
        ("width","screenw","x"),("height","screenh","y")):
        G(screen_field,D(0)); c.alu("sub",M(2,F[field]),0)
        B(11,"fail")
        G(origin,D(1)); c.alu("cmp",D(0),1); B(14,"fail")
    G("width",D(0)); G("height",D(1))
    c.word(0xc0c1)                 # MULU.W D1,D0 -> LONG
    c.imm("cmp",MAX_PIXELS,D(0)); B(2,"fail")

    # Optional transparency index -1, or exact 0..(2^depth-1).
    G("transparent",D(1))
    c.imm("cmp",-1,D(1)); B(7,"transparent_none")
    c.tst(D(1)); B(11,"fail")
    G("depth",D(0)); c.move(I(1),D(7))
    L("transparent_max")
    c.shift(7,1,left=True)
    c.quick(1,D(0),sub=True); B(6,"transparent_max")
    c.alu("cmp",D(7),1); B(4,"fail")
    c.move(I(1),M(2,F["masked"]))
    B(0,"transparent_ok")
    L("transparent_none")
    c.move(I(0),M(2,F["masked"]))
    L("transparent_ok")

    # Resolve currently inactive ScreenBuffer BitMap precisely as R46 Draw.
    G("db",A(0))
    c.move(M(0,8),D(0))
    c.tst(D(0)); B(7,"db_zero")
    c.imm("cmp",1,D(0)); B(6,"fail")
    c.move(M(0),A(1))
    B(0,"db_found")
    L("db_zero")
    c.move(M(0,4),A(1))
    L("db_found")
    nonzero(A(1))
    c.move(M(1),A(0)); nonzero(A(0))
    S(A(0),"bitmap")
    c.move(I(0),D(0)); c.move(M(0),D(0),"w")
    c.imm("cmp",2,D(0)); B(5,"fail")
    c.imm("cmp",65534,D(0)); B(2,"fail")
    c.move(D(0),D(1)); c.imm("and",1,D(1)); B(6,"fail")
    S(D(0),"stride")
    c.shift(0,3,left=True)
    c.alu("cmp",M(2,F["screenw"]),0); B(13,"fail")
    c.move(I(0),D(0)); c.move(M(0,2),D(0),"w")
    c.alu("cmp",M(2,F["screenh"]),0); B(13,"fail")
    c.move(I(0),D(0)); c.move(M(0,5),D(0),"b")
    c.alu("cmp",M(2,F["depth"]),0); B(6,"fail")
    c.move(A(0),A(1)); c.quick(8,A(1))
    G("depth",D(0))
    L("check_planes")
    c.move(POST(1),D(1)); c.tst(D(1)); B(7,"fail")
    c.imm("cmp",-1,D(1)); B(7,"fail")
    c.quick(1,D(0),sub=True); B(6,"check_planes")

    # Refuse any occupied AMOS bank, no matter what it contains.
    G("bank",D(0)); RJ(IDX_GETADR)
    c.move(A(0),D(0)); c.tst(D(0)); B(6,"fail")

    # Non-blocking Safe before touching back buffer, same gate as Draw R46.
    G("db",A(4))
    c.move(M(4,20),D(0)); c.imm("and",1,D(0)); B(7,"safe_ok")
    c.move(M(4,12),A(0)); nonzero(A(0))
    osbase(); c.call_os(LVO_GETMSG)
    c.tst(D(0)); B(7,"fail")
    G("db",A(4))
    c.move(M(4,20),D(0))
    c.imm("and",0xfffffffe,D(0))
    c.move(D(0),M(4,20))
    L("safe_ok")

    # Max possible size of a 1-row literal-only stream = groups*(groupbytes+1).
    G("width",D(0)); c.imm("add",15,D(0))
    c.shift(0,4,left=False)
    G("depth",D(1)); c.alu("add",M(2,F["masked"]),1)
    c.shift(1,1,left=True); c.quick(1,D(1))
    c.word(0xc0c1)                 # MULU.W D1,D0
    S(D(0),"rowcap")
    c.move(D(0),D(6))
    c.move(I(1),D(1))              # MEMF_PUBLIC | unspecified type
    osbase(); c.call_os(LVO_ALLOCVEC)
    c.tst(D(0)); B(7,"fail")
    S(D(0),"temp")

    # Table size (h+1)*4 + 32. Count exact encoded row byte lengths.
    G("height",D(0)); c.quick(1,D(0))
    c.shift(0,2,left=True)
    c.imm("add",32,D(0)); S(D(0),"streamoffset"); S(D(0),"total")
    c.move(I(0),M(2,F["row"]))
    L("count_loop")
    G("row",D(0)); c.alu("cmp",M(2,F["height"]),0); B(12,"count_done")
    G("temp",A(1)); G("rowcap",D(6))
    # Core arguments shared by count and output pass.
    c.branch(1,"core_args")
    c.tst(D(0)); B(7,"fail")
    G("total",D(1)); c.alu("add",D(0),1); B(5,"fail")
    c.imm("cmp",MAX_PAYLOAD,D(1)); B(2,"fail")
    S(D(1),"total")
    G("row",D(0)); c.quick(1,D(0)); S(D(0),"row")
    B(0,"count_loop")
    L("count_done")

    # Recheck collision immediately before calling destructive Reserve.
    G("bank",D(0)); RJ(IDX_GETADR)
    c.move(A(0),D(0)); c.tst(D(0)); B(6,"fail")
    G("bank",D(0))
    c.move(I(1),D(1))             # DATA/Fast preferred, may fall back Chip
    G("total",D(2))
    c.lea(0,"bank_name")
    RJ(IDX_RESERVE)
    c.tst(D(0)); B(7,"fail")
    S(D(0),"bankptr")
    # Check pointer arithmetic before committing image data.
    G("total",D(1)); c.alu("add",D(1),0); B(5,"erase_bank")
    S(D(0),"bankend")
    G("bankptr",A(0))
    c.move(I(0x41474150),M(0))            # AGAP
    c.move(I(0x4943,"w"),M(0,4),"w")     # IC
    c.move(I(1,"w"),M(0,6),"w")          # v1
    G("masked",D(0)); c.move(D(0),M(0,8),"w")
    c.move(I(1,"w"),M(0,10),"w")         # codec row RLE
    for name,off in (("width",12),("height",14),("depth",16)):
        G(name,D(0)); c.move(D(0),M(0,off),"w")
    G("depth",D(0)); c.alu("add",M(2,F["masked"]),0)
    c.shift(0,1,left=True); c.move(D(0),M(0,18),"w")
    c.move(I(32),M(0,20))
    G("streamoffset",D(0)); c.move(D(0),M(0,24))
    G("total",D(0)); c.move(D(0),M(0,28))
    G("bankptr",D(0)); c.imm("add",32,D(0)); S(D(0),"tableptr")
    G("bankptr",D(0)); c.alu("add",M(2,F["streamoffset"]),0)
    S(D(0),"streamptr")
    c.move(I(0),M(2,F["row"]))

    L("write_loop")
    G("row",D(0)); c.alu("cmp",M(2,F["height"]),0); B(12,"write_done")
    G("streamptr",D(0)); c.alu("sub",M(2,F["bankptr"]),0)
    G("tableptr",A(4)); c.move(D(0),POST(4)); S(A(4),"tableptr")
    G("streamptr",A(1))
    G("bankend",D(6)); c.alu("sub",A(1),6)
    c.branch(1,"core_args")
    c.tst(D(0)); B(7,"erase_bank")
    G("streamptr",D(1)); c.alu("add",D(0),1); B(5,"erase_bank")
    c.alu("cmp",M(2,F["bankend"]),1); B(2,"erase_bank")
    S(D(1),"streamptr")
    G("row",D(0)); c.quick(1,D(0)); S(D(0),"row")
    B(0,"write_loop")
    L("write_done")
    G("streamptr",D(0)); c.alu("cmp",M(2,F["bankend"]),0)
    B(6,"erase_bank")
    G("tableptr",A(4)); G("total",D(0)); c.move(D(0),M(4))
    # Notify other extensions of the newly complete bank.
    RJ(IDX_CHANGE)
    c.move(I(1),M(2,F["result"]))
    B(0,"cleanup")

    # Erase ONLY the newly created bank on any failed second pass.
    L("erase_bank")
    G("bank",D(0)); RJ(IDX_EFF)
    c.move(I(0),M(2,F["bankptr"]))
    B(0,"cleanup")
    L("fail")
    L("cleanup")
    G("temp",A(1))
    c.move(A(1),D(0)); c.tst(D(0)); B(7,"return")
    osbase(); c.call_os(LVO_FREEVEC)
    L("return")
    G("result",D(3))
    c.raw("4fef00e0")                  # LEA +224(SP),SP
    c.raw("4cdf77f7")                  # restore established AP20 preserved set
    c.raw("74004e75")                  # D2=0 (integer), RTS

    # Internal helper: load CPU core calling convention and BSR core.
    L("core_args")
    G("bitmap",A(0)); c.quick(8,A(0))
    G("x",D(0)); G("y",D(1)); c.alu("add",M(2,F["row"]),1)
    G("width",D(2)); G("depth",D(3))
    G("stride",D(4)); G("transparent",D(5))
    c.branch(1,"core")
    c.raw("4e75")                     # return bytes D0 to caller
    L("core")
    core,_ = emit_scanline_rle()
    c.raw(core.hex())
    L("bank_name")
    c.raw(NAME.hex())
    raw=c.out()
    assert len(raw)%2==0
    return raw,c.labels
