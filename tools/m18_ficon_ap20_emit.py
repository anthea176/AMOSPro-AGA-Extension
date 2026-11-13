"""M18/R61 experimental public AMOS AP20 bank-based Fast Icon 16x16 renderer.

Aga F Icon(Bank,IconID,X,Y,Mode) -> D3=1/0, D2=0.
Mode is D3; A3 pops Y,X,IconID,Bank as four ULONG arguments.
BANK is AMOS DATA 5..65535 named b'FICON8  ' with payload
[total_size.l, count.w, width.w=16, height.w=16, depth.w=8,
 count * 288 bytes of Unity preserve-mask+8-plane 16x16 slots].
Selected icon must have a canonical zero-colour preserve mask per row.

Uses live Bnk.GetAdr, validates bank and all selected slot rows before any
pixel write or non-blocking Safe acquisition. Obtains the inactive private
ScreenBuffer/8-bitplane Bitmap, polls Safe message only if pending, then
calls the already Gate-A-qualified P3 68000 arbitrary-X word renderer.
No implicit Swap/VBL, allocation, DMA or Fast/Chip guessing. R60 is immutable.
This module emits code only; not an installed/released library.
"""
from m68k_emit import Code, D, A, M, POST, I
from amos_main_abi import main_index, rjsr
from m18_ficon16_native_shifted_emit import emit_ficon16_shifted_cpu

ENTRY_INDEX = 60
GETP = b"GetP"
STATE_PTR = 0x1c8
LVO_TYPEOFMEM = -534
LVO_GETMSG = -372
MAX_COUNT = 4096
SLOT_BYTES = 288
HEADER_BYTES = 12
MAX_PAYLOAD = HEADER_BYTES + MAX_COUNT * SLOT_BYTES
BANK_NAME = b"FICON8  "
assert len(BANK_NAME)==8
GETADR_MARKER = rjsr(main_index("Bnk.GetAdr"))
assert main_index("Bnk.GetAdr") == 797

# Temporary frame after MOVEM: valid across nested subroutine calls.
F = dict(mode=0,y=4,x=8,icon=12,bank=16,base=20,length=24,count=28,
         slot=32,scrw=36,scrh=40,stride=44,bitmap=48)
FRAME = 96

def emit_ficon_ap20(*, opt020=False):
    c=Code()
    B,L=c.branch,c.label
    def ld(field,reg):c.move(M(2,F[field]),reg)
    def st(reg,field):c.move(reg,M(2,F[field]))
    def uw(reg,offset):  # zero-extend 16-bit header field
        c.move(I(0),D(reg))
        c.move(M(0,offset),D(reg),"w")
    # Same preserved register set as the promoted R60 public entry.
    c.raw("48e7efee")
    c.raw("4fefffa0")                  # LEA -96(SP),SP
    c.move(A(7),A(2))                 # frame (A2)
    st(D(3),"mode")
    for field in ("y","x","icon","bank"):
        c.move(POST(3),D(7));st(D(7),field)
    c.move(I(0),D(3))                # default failure

    # Reject malformed AP20 arguments even when the bank is absent.
    ld("mode",D(0))
    c.imm("cmp",1,D(0));B(2,"reject")  # 0 or 1 (unsigned)
    for field in ("x","y"):
        ld(field,D(0))
        c.imm("cmp",-32768,D(0));B(13,"reject")
        c.imm("cmp",32767,D(0));B(14,"reject")
    ld("icon",D(0));c.tst(D(0));B(15,"reject")
    c.imm("cmp",MAX_COUNT,D(0));B(14,"reject")
    ld("bank",D(0))
    c.imm("cmp",5,D(0));B(5,"reject")
    c.imm("cmp",65535,D(0));B(2,"reject")
    c.raw(GETADR_MARKER.hex())        # source-derived AMOS Bnk.GetAdr
    c.move(A(0),D(5));c.imm("cmp",24,D(5));B(3,"reject")
    c.move(D(5),D(0));c.imm("and",1,D(0));B(6,"reject")
    st(D(5),"base")

    # Verify memory ownership BEFORE reading native AMOS bank header.
    c.move(D(5),A(1))
    c.raw("2c780004")                # A6=ExecBase
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0));B(7,"reject")
    ld("base",D(5));c.move(D(5),D(0))
    c.imm("sub",24,D(0));c.move(D(0),A(1))
    c.raw("2c780004")
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0));B(7,"reject")

    c.move(D(5),A(0))
    c.move(M(0,-20),D(4))           # real AMOS payload + 16
    c.imm("cmp",16+HEADER_BYTES,D(4));B(5,"reject")
    c.imm("sub",16,D(4))
    c.imm("cmp",MAX_PAYLOAD,D(4));B(2,"reject")
    st(D(4),"length")
    c.move(D(5),D(0));c.alu("add",D(4),0);B(5,"reject")
    c.quick(1,D(0),sub=True);c.move(D(0),A(1))
    c.raw("2c780004")
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0));B(7,"reject")
    ld("base",D(5));c.move(D(5),A(0))
    c.move(M(0,-16),D(0))
    ld("bank",D(1));c.alu("cmp",D(1),0);B(6,"reject")
    uw(0,-12)
    c.tst(D(0));B(7,"native_flags_ok")
    c.imm("and",0xfffd,D(0),"w")
    c.imm("cmp",1,D(0));B(6,"reject")
    L("native_flags_ok")
    c.move(M(0,-8),D(0))
    c.imm("cmp",0x4649434f,D(0));B(6,"reject") # "FICO"
    c.move(M(0,-4),D(0))
    c.imm("cmp",0x4e382020,D(0));B(6,"reject") # "N8  "

    # Strict 12-byte Unity payload header (no ambiguous AGAPIC overlap).
    c.move(M(0),D(0))
    c.alu("cmp",M(2,F["length"]),0);B(6,"reject")
    uw(0,4);st(D(0),"count")
    c.imm("cmp",4,D(0));B(5,"reject")
    c.imm("cmp",MAX_COUNT,D(0));B(14,"reject")
    ld("icon",D(1));c.alu("cmp",D(1),0);B(5,"reject")
    c.move(I(SLOT_BYTES),D(1))
    c.word(0xc0c1)                # MULU.W D1,D0 -> count*288
    c.imm("add",HEADER_BYTES,D(0))
    c.alu("cmp",M(2,F["length"]),0);B(6,"reject")
    uw(0,6);c.imm("cmp",16,D(0));B(6,"reject")
    uw(0,8);c.imm("cmp",16,D(0));B(6,"reject")
    uw(0,10);c.imm("cmp",8,D(0));B(6,"reject")
    ld("icon",D(0));c.quick(1,D(0),sub=True)
    c.move(I(SLOT_BYTES),D(1));c.word(0xc0c1)
    c.imm("add",HEADER_BYTES,D(0));c.alu("add",D(5),0);B(5,"reject")
    st(D(0),"slot")

    # Canonical mask: PRESERVE = NOT(OR(8 plane words)).
    # The 16 selected icon rows are checked before screen Safe/any pixels.
    c.move(D(0),A(0));c.move(I(16),D(6))
    L("check_row")
    c.move(POST(0),D(4),"w")
    c.move(I(0),D(7))
    c.move(I(8),D(5))
    L("check_plane")
    c.alu("or",POST(0),7,"w")
    c.quick(1,D(5),sub=True);B(6,"check_plane")
    c.word(0x4647)               # NOT.W D7
    c.alu("cmp",D(4),7,"w");B(6,"reject")
    c.quick(1,D(6),sub=True);B(6,"check_row")

    # ScreenBuffer is private to AGA extension, not AMOS main screen.
    c.move(M(5,STATE_PTR),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,"reject")
    for off in (0,8,32):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,"reject")
    for off,field in ((12,"scrw"),(16,"scrh")):
        c.move(M(4,off),D(0))
        c.tst(D(0));B(15,"reject")
        c.imm("cmp",32767,D(0));B(14,"reject")
        st(D(0),field)
    c.move(M(4,28),D(0));c.imm("cmp",8,D(0));B(6,"reject")

    c.move(M(4,32),A(0))
    c.move(M(0,8),D(0))
    c.tst(D(0));B(7,"front_zero")
    c.imm("cmp",1,D(0));B(6,"reject")
    c.move(M(4,32),A(0))
    c.move(M(0),A(1));B(0,"have_sb")
    L("front_zero")
    c.move(M(4,32),A(0));c.move(M(0,4),A(1))
    L("have_sb")
    c.move(A(1),D(0));c.tst(D(0));B(7,"reject")
    c.move(M(1),A(0))
    c.move(A(0),D(0));c.tst(D(0));B(7,"reject")
    st(A(0),"bitmap")
    uw(1,0);c.tst(D(1));B(7,"reject");st(D(1),"stride")
    c.shift(1,3,left=True)
    c.alu("cmp",M(2,F["scrw"]),1);B(13,"reject")
    uw(1,2)
    c.alu("cmp",M(2,F["scrh"]),1);B(13,"reject")
    c.move(I(0),D(1));c.move(M(0,5),D(1),"b")
    c.imm("cmp",8,D(1));B(6,"reject")
    c.move(A(0),A(1));c.quick(8,A(1))
    c.move(I(8),D(0))
    L("check_pointers")
    c.move(POST(1),D(1))
    c.tst(D(1));B(7,"reject")
    c.imm("cmp",-1,D(1));B(7,"reject")
    c.move(D(1),D(5));c.imm("and",1,D(5));B(6,"reject")
    c.quick(1,D(0),sub=True);B(6,"check_pointers")

    # Full off-screen is a success without Safe consumption.
    ld("x",D(0));c.alu("cmp",M(2,F["scrw"]),0);B(12,"noop")
    c.imm("add",16,D(0));c.tst(D(0));B(15,"noop")
    ld("y",D(0));c.alu("cmp",M(2,F["scrh"]),0);B(12,"noop")
    c.imm("add",16,D(0));c.tst(D(0));B(15,"noop")

    # Nonblocking Safe, exactly as R60. No WaitVbl, no WaitBlit.
    c.move(M(4,32),A(0))
    c.move(M(0,20),D(0));c.imm("and",1,D(0))
    B(7,"safe")
    c.move(M(0,12),A(0))
    c.move(A(0),D(0));c.tst(D(0));B(7,"reject")
    c.raw("2c780004");c.call_os(LVO_GETMSG)
    c.tst(D(0));B(7,"reject")
    c.move(M(4,32),A(0))
    c.move(M(0,20),D(0))
    c.imm("and",0xfffffffe,D(0));c.move(D(0),M(0,20))
    L("safe")
    # Internal, prevalidated CPU renderer. BSR.W keeps all relocations local.
    ld("x",D(0));ld("y",D(1));ld("stride",D(2))
    ld("mode",D(3));ld("scrw",D(4));ld("scrh",D(5))
    ld("slot",A(0));ld("bitmap",A(1));c.quick(8,A(1))
    B(1,"core")                  # BSR.W actual P3 68000 renderer
    B(0,"leave")
    L("noop")
    c.move(I(1),D(3));B(0,"leave")
    L("reject")
    c.move(I(0),D(3))
    L("leave")
    c.raw("4fef0060")           # Restore frame
    c.raw("4cdf77f7")           # MOVEM restores caller-safe registers
    c.raw("74004e75")           # MOVEQ #0,D2 ; RTS

    L("core")
    native,core_labels=emit_ficon16_shifted_cpu(opt020=opt020)
    c.raw(native.hex())
    result=c.out()
    assert result.count(GETADR_MARKER)==1
    assert result[-len(native):]==native
    assert len(result)%2==0
    return result,dict(c.labels,core_bytes=len(native),
                       core_labels=len(core_labels))

if __name__=="__main__":
    from hashlib import sha256
    code,labels=emit_ficon_ap20()
    print("M18/R61 FICON AP20 68000 UNINSTALLED",
          len(code),sha256(code).hexdigest(),
          {k:labels[k] for k in ("core","reject","safe","check_row")})
