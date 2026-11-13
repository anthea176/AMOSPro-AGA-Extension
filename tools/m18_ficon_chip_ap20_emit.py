"""M18/P5 experimental AP20 Aga F Blit(CacheBank,ID,X,Y,Mode) emitter.

Input cache bank: AMOS Chip DATA 'FICHIP8 ', 12-byte header,
count*288 staged mask+planar slots, and count ready markers.
No on-the-fly allocation or hidden staging. F Icon source must be
prepared into the cache in advance; cache survives Screen Swap and Close.
Before real DMA check actual Chip source, bank header/marker/selected
content, the private back bitmap, and nonblocking Safe. P5 Blitter core
calls InitRastPort, BltBitMapRastPort or BltMaskBitMapRastPort, WaitBlit.
No R61 modification, no published .Lib until native Gate A passes.
"""
from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr
from m18_ficon16_chip_blit_emit import emit_chip_cache_blit

ENTRY_INDEX=61
GETADR_MARKER=rjsr(main_index("Bnk.GetAdr"))
STATE_PTR=0x1c8
LVO_TYPEOFMEM=-534
LVO_GETMSG=-372
SLOT=288
HEADER=12
MAX_COUNT=4096
MAX_PAYLOAD=HEADER+MAX_COUNT*(SLOT+1)
F=dict(mode=0,y=4,x=8,icon=12,bank=16,base=20,length=24,count=28,
       slot=32,scrw=36,scrh=40,bitmap=44,marker=48)
FRAME=96

def emit_ficon_chip_ap20():
    c=Code()
    B,L=c.branch,c.label
    def ld(key,dest):c.move(M(2,F[key]),dest)
    def st(src,key):c.move(src,M(2,F[key]))
    def uw(reg,at):
        c.move(I(0),D(reg))
        c.move(M(0,at),D(reg),"w")

    c.raw("48e7efee")
    c.raw("4fefffa0")
    c.move(A(7),A(2))
    st(D(3),"mode")
    for key in ("y","x","icon","bank"):
        c.move(POST(3),D(7));st(D(7),key)
    c.move(I(0),D(3))
    ld("mode",D(0));c.tst(D(0));B(11,"reject")
    c.imm("cmp",1,D(0));B(14,"reject")
    for key in ("x","y"):
        ld(key,D(0))
        c.imm("cmp",-32768,D(0));B(13,"reject")
        c.imm("cmp",32767,D(0));B(14,"reject")
    ld("icon",D(0));c.tst(D(0));B(15,"reject")
    c.imm("cmp",MAX_COUNT,D(0));B(14,"reject")
    ld("bank",D(0))
    c.imm("cmp",5,D(0));B(5,"reject")
    c.imm("cmp",65535,D(0));B(2,"reject")
    c.raw(GETADR_MARKER.hex())
    c.move(A(0),D(5));c.imm("cmp",24,D(5));B(3,"reject")
    c.move(D(5),D(0));c.imm("and",1,D(0));B(6,"reject")
    st(D(5),"base")
    # Verify native AMOS bank envelope is addressable before dereference.
    c.move(D(5),A(1));c.raw("2c780004");c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0));B(7,"reject")
    ld("base",D(5));c.move(D(5),D(0));c.imm("sub",24,D(0))
    c.move(D(0),A(1));c.raw("2c780004");c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0));B(7,"reject")
    c.move(D(5),A(0))
    c.move(M(0,-20),D(4))
    c.imm("cmp",16+HEADER,D(4));B(5,"reject")
    c.imm("sub",16,D(4))
    c.imm("cmp",MAX_PAYLOAD,D(4));B(2,"reject")
    st(D(4),"length")
    c.move(D(5),D(0));c.alu("add",D(4),0);B(5,"reject")
    c.quick(1,D(0),sub=True)
    c.move(D(0),A(1));c.raw("2c780004");c.call_os(LVO_TYPEOFMEM)
    c.imm("and",2,D(0));B(7,"reject")  # FULL allocation end is Chip
    ld("base",D(5));c.move(D(5),A(0))
    c.move(M(0,-16),D(0))
    ld("bank",D(1));c.alu("cmp",D(1),0);B(6,"reject")
    uw(0,-12)
    c.imm("and",3,D(0),"w")
    c.imm("cmp",3,D(0),"w");B(6,"reject") # AmBk DATA+CHIP bank flags
    c.move(M(0,-8),D(0))
    c.imm("cmp",0x46494348,D(0));B(6,"reject") # "FICH"
    c.move(M(0,-4),D(0))
    c.imm("cmp",0x49503820,D(0));B(6,"reject") # "IP8 "
    c.move(M(0),D(0))
    c.alu("cmp",M(2,F["length"]),0);B(6,"reject")
    uw(0,4);st(D(0),"count")
    c.imm("cmp",4,D(0));B(5,"reject")
    c.imm("cmp",MAX_COUNT,D(0));B(14,"reject")
    ld("icon",D(1));c.alu("cmp",D(1),0);B(5,"reject")
    c.move(I(SLOT+1),D(1));c.word(0xc0c1) # MULU.W D1,D0 count*289
    c.imm("add",HEADER,D(0))
    c.alu("cmp",M(2,F["length"]),0);B(6,"reject")
    uw(0,6);c.imm("cmp",16,D(0));B(6,"reject")
    uw(0,8);c.imm("cmp",16,D(0));B(6,"reject")
    uw(0,10);c.imm("cmp",8,D(0));B(6,"reject")

    # Ready marker is placed AFTER all slots, never inside DMA payload.
    ld("count",D(0));c.move(I(SLOT),D(1));c.word(0xc0c1)
    c.imm("add",HEADER,D(0))
    ld("icon",D(1));c.quick(1,D(1),sub=True)
    c.alu("add",D(1),0);c.alu("add",D(5),0);B(5,"reject")
    st(D(0),"marker")
    c.move(D(0),A(0))
    c.move(I(0),D(0));c.move(M(0),D(0),"b")
    c.imm("cmp",1,D(0));B(6,"reject")  # reject any unstaged slot

    ld("icon",D(0));c.quick(1,D(0),sub=True)
    c.move(I(SLOT),D(1));c.word(0xc0c1)
    c.imm("add",HEADER,D(0));c.alu("add",D(5),0);B(5,"reject")
    st(D(0),"slot")

    # Verify staging mask == bitwise OR of the eight colour planes
    # for every row before consuming Safe or invoking DMA.
    c.move(D(0),A(0))
    c.move(D(0),A(1))
    c.raw("43e90020")               # LEA 32(A1),A1
    c.move(I(16),D(6))
    L("check_row")
    c.move(POST(0),D(4),"w")
    c.move(A(1),A(6))
    c.move(I(0),D(7))
    c.move(I(8),D(5))
    L("check_plane")
    c.alu("or",M(6),7,"w")
    c.raw("4dee0020")               # LEA 32(A6),A6 (source register A6, not A4)
    c.quick(1,D(5),sub=True);B(6,"check_plane")
    c.alu("cmp",D(4),7,"w");B(6,"reject")
    c.quick(2,A(1))
    c.quick(1,D(6),sub=True);B(6,"check_row")

    # Copy R61's private back buffer validation and nonblocking Safe rule.
    c.move(M(5,STATE_PTR),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,"reject")
    for off in (0,8,32):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,"reject")
    for off,key in ((12,"scrw"),(16,"scrh")):
        c.move(M(4,off),D(0))
        c.tst(D(0));B(15,"reject")
        c.imm("cmp",32767,D(0));B(14,"reject")
        st(D(0),key)
    c.move(M(4,28),D(0));c.imm("cmp",8,D(0));B(6,"reject")
    c.move(M(4,32),A(0))
    c.move(M(0,8),D(0))
    c.tst(D(0));B(7,"front_zero")
    c.imm("cmp",1,D(0));B(6,"reject")
    c.move(M(4,32),A(0));c.move(M(0),A(1));B(0,"have_sb")
    L("front_zero")
    c.move(M(4,32),A(0));c.move(M(0,4),A(1))
    L("have_sb")
    c.move(A(1),D(0));c.tst(D(0));B(7,"reject")
    c.move(M(1),A(0))
    c.move(A(0),D(0));c.tst(D(0));B(7,"reject")
    st(A(0),"bitmap")
    uw(1,0);c.tst(D(1));B(7,"reject")
    c.shift(1,3,left=True)
    c.alu("cmp",M(2,F["scrw"]),1);B(13,"reject")
    uw(1,2);c.alu("cmp",M(2,F["scrh"]),1);B(13,"reject")
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
    ld("x",D(0));c.alu("cmp",M(2,F["scrw"]),0);B(12,"noop")
    c.imm("add",16,D(0));c.tst(D(0));B(15,"noop")
    ld("y",D(0));c.alu("cmp",M(2,F["scrh"]),0);B(12,"noop")
    c.imm("add",16,D(0));c.tst(D(0));B(15,"noop")
    c.move(M(4,32),A(0))
    c.move(M(0,20),D(0));c.imm("and",1,D(0))
    B(7,"safe")
    c.move(M(0,12),A(0));c.move(A(0),D(0))
    c.tst(D(0));B(7,"reject")
    c.raw("2c780004");c.call_os(LVO_GETMSG)
    c.tst(D(0));B(7,"reject")
    c.move(M(4,32),A(0));c.move(M(0,20),D(0))
    c.imm("and",0xfffffffe,D(0));c.move(D(0),M(0,20))
    L("safe")
    ld("x",D(0));ld("y",D(1));ld("mode",D(3))
    ld("scrw",D(4));ld("scrh",D(5))
    ld("slot",A(0));ld("bitmap",A(1))
    c.move(M(4,8),A(6))          # private GfxBase, validated above
    B(1,"core")
    B(0,"leave")
    L("noop")
    c.move(I(1),D(3));B(0,"leave")
    L("reject")
    c.move(I(0),D(3))
    L("leave")
    c.raw("4fef0060")
    c.raw("4cdf77f7")
    c.raw("74004e75")
    L("core")
    native,labels=emit_chip_cache_blit()
    c.raw(native.hex())
    raw=c.out()
    assert raw.count(GETADR_MARKER)==1
    assert raw[-len(native):]==native
    assert len(raw)%2==0
    return raw,dict(c.labels,core_bytes=len(native))

if __name__=="__main__":
    from hashlib import sha256
    blob,labels=emit_ficon_chip_ap20()
    print("M18/P5 CHIP AP20 UNINSTALLED",len(blob),
          sha256(blob).hexdigest(),"core",labels["core"])
