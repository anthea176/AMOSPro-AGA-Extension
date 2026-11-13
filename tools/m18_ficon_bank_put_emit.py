"""M18/R65: Aga F Icon Bank Put(DestBank,ID,PixelBank,Offset) -> D3 1/0.

Bulk-convert 256 chunky 8-bit palette indices from a *different* AMOS DATA
bank at a byte offset into exactly one existing FICON8 16x16 slot (288 bytes).
Zero is transparent only when using Aga F Icon(...,Mode=1).
No colour quantisation, palette/screen modification, cache staging or DMA.
Every input & physical memory region is validated before any bank write.
"""
from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr
ENTRY_INDEX=63
LVO_TYPEOFMEM=-534
HEADER=12
SLOT=288
COUNT_MIN,COUNT_MAX=4,4096
FICON_NAME=b"FICON8  "
GETADR_MARKER=rjsr(main_index("Bnk.GetAdr"))
F=dict(offset=0,source_bank=4,icon=8,dest_bank=12,
       dest_base=16,dest_len=20,count=24,source_base=28,
       source_len=32,source_ptr=36,slot_ptr=40)
FRAME=96

def emit_ficon_bank_put():
    c=Code();B,L=c.branch,c.label
    def get(name,reg):c.move(M(2,F[name]),reg)
    def put(reg,name):c.move(reg,M(2,F[name]))
    def chk_memory_from(reg):
        c.move(reg,A(1))
        c.raw("2c780004")            # MOVEA.L ExecBase 4.W,A6
        c.call_os(LVO_TYPEOFMEM)
        c.tst(D(0));B(7,"fail")
    def bank_lookup(field,target):
        get(field,D(0));c.raw(GETADR_MARKER.hex())
        c.move(A(0),D(5))
        c.imm("cmp",24,D(5));B(3,"fail")
        c.move(D(5),D(0));c.imm("and",1,D(0));B(6,"fail")
        put(D(5),target)
        chk_memory_from(D(5))
        get(target,D(0));c.imm("sub",24,D(0))
        chk_memory_from(D(0))
    def bank_metadata(number_field,pointer_field):
        get(pointer_field,A(0))
        c.move(M(0,-16),D(0))
        get(number_field,D(1));c.alu("cmp",D(1),0);B(6,"fail")
        c.move(I(0),D(0))
        c.move(M(0,-12),D(0),"w")
        c.tst(D(0));B(7,"flags_ok_"+number_field)
        c.imm("and",0xfffd,D(0),"w")
        c.imm("cmp",1,D(0),"w");B(6,"fail")
        L("flags_ok_"+number_field)

    # Standard preservation ABI: D2 integer type, D3 value and A3 popped.
    c.raw("48e7efee")              # MOVEM.L D0-D7/A0-A2/A4-A6,-(SP)
    c.raw("4fefffa0")              # LEA -96(SP),SP
    c.move(A(7),A(2))
    put(D(3),"offset")
    for field in ("source_bank","icon","dest_bank"):
        c.move(POST(3),D(7));put(D(7),field)
    c.move(I(0),D(3))            # default failure

    for field in ("dest_bank","source_bank"):
        get(field,D(0));c.imm("cmp",5,D(0));B(5,"fail")
        c.imm("cmp",65535,D(0));B(2,"fail")
    get("dest_bank",D(0));get("source_bank",D(1))
    c.alu("cmp",D(1),0);B(7,"fail")  # BEQ: reject only same-bank source/dest
    get("icon",D(0));c.tst(D(0));B(15,"fail")
    c.imm("cmp",COUNT_MAX,D(0));B(14,"fail")
    get("offset",D(0));c.tst(D(0));B(11,"fail")

    # Destination bank must be a fully valid FICON8 AMOS DATA bank.
    bank_lookup("dest_bank","dest_base")
    get("dest_base",A(0))
    c.move(M(0,-20),D(4))
    c.imm("cmp",16+HEADER,D(4));B(5,"fail")
    c.imm("sub",16,D(4))
    c.imm("cmp",HEADER+COUNT_MAX*SLOT,D(4));B(2,"fail")
    put(D(4),"dest_len")
    get("dest_base",D(0));c.alu("add",D(4),0);B(5,"fail")
    c.quick(1,D(0),sub=True)
    chk_memory_from(D(0))
    bank_metadata("dest_bank","dest_base")
    get("dest_base",A(0))
    c.move(M(0,-8),D(0));c.imm("cmp",0x4649434f,D(0));B(6,"fail")
    c.move(M(0,-4),D(0));c.imm("cmp",0x4e382020,D(0));B(6,"fail")
    c.move(M(0),D(0))
    c.alu("cmp",M(2,F["dest_len"]),0);B(6,"fail")
    c.move(I(0),D(0));c.move(M(0,4),D(0),"w")
    c.imm("cmp",COUNT_MIN,D(0));B(5,"fail")
    c.imm("cmp",COUNT_MAX,D(0));B(14,"fail")
    put(D(0),"count")
    get("icon",D(1));c.alu("cmp",D(1),0);B(5,"fail")
    c.move(I(SLOT),D(1));c.word(0xc0c1) # MULU.W count*288
    c.imm("add",HEADER,D(0))
    c.alu("cmp",M(2,F["dest_len"]),0);B(6,"fail")
    for off,val in ((6,16),(8,16),(10,8)):
        c.move(I(0),D(0));c.move(M(0,off),D(0),"w")
        c.imm("cmp",val,D(0));B(6,"fail")
    get("icon",D(0));c.quick(1,D(0),sub=True)
    c.move(I(SLOT),D(1));c.word(0xc0c1)
    c.imm("add",HEADER,D(0))
    get("dest_base",D(5));c.alu("add",D(5),0);B(5,"fail")
    put(D(0),"slot_ptr")
    c.imm("add",SLOT-1,D(0));B(5,"fail")
    chk_memory_from(D(0))

    # Any AMOS DATA source bank, selected by bank number & byte offset.
    bank_lookup("source_bank","source_base")
    get("source_base",A(0))
    c.move(M(0,-20),D(4))
    c.imm("cmp",16+256,D(4));B(5,"fail")
    c.imm("sub",16,D(4))
    put(D(4),"source_len")
    get("source_base",D(0));c.alu("add",D(4),0);B(5,"fail")
    c.quick(1,D(0),sub=True)
    chk_memory_from(D(0))
    bank_metadata("source_bank","source_base")
    get("source_len",D(0));c.imm("sub",256,D(0))
    get("offset",D(1));c.alu("cmp",D(1),0);B(5,"fail")
    get("source_base",D(0));c.alu("add",D(1),0);B(5,"fail")
    put(D(0),"source_ptr")
    chk_memory_from(D(0))
    get("source_ptr",D(0));c.imm("add",255,D(0));B(5,"fail")
    chk_memory_from(D(0))

    # All pointer/header/size checks completed. Convert 16 rows in place.
    get("source_ptr",A(0));get("slot_ptr",A(1))
    c.move(I(16),D(6))            # Y counter
    L("row")
    c.move(I(0,"w"),M(1),"w")
    for off in (2,6,10,14):
        c.move(I(0),M(1,off))     # zero 8 planar words
    c.move(I(0),D(7))            # preservation mask for zero pixels
    c.move(I(0x8000,"w"),D(1),"w") # current source X bit
    c.move(I(16),D(2))           # X counter
    L("pixel")
    c.move(I(0),D(4))
    c.move(POST(0),D(4),"b")     # source 8-bit index
    c.tst(D(4),"b");B(6,"nonzero")
    c.alu("or",D(1),7,"w")
    B(0,"pixel_done")
    L("nonzero")
    c.move(A(1),A(4));c.quick(2,A(4))
    c.move(I(8),D(5))
    L("plane")
    c.move(D(4),D(0));c.imm("and",1,D(0),"w")
    c.tst(D(0),"w");B(7,"skip_bit")
    c.move(M(4),D(0),"w")
    c.alu("or",D(1),0,"w")
    c.move(D(0),M(4),"w")
    L("skip_bit")
    c.word(0xe24c)              # LSR.W #1,D4, colour next bit
    c.quick(2,A(4))
    c.quick(1,D(5),sub=True);B(6,"plane")
    L("pixel_done")
    c.word(0xe249)              # LSR.W #1,D1, next x position
    c.quick(1,D(2),sub=True);B(6,"pixel")
    c.move(D(7),M(1),"w")
    c.raw("43e90012")           # LEA 18(A1),A1
    c.quick(1,D(6),sub=True);B(6,"row")

    c.move(I(1),D(3))
    L("fail")
    c.raw("4fef0060")           # LEA +96(SP),SP
    c.raw("4cdf77f7")           # restore all preserved registers
    c.raw("74004e75")           # D2=0, RTS
    return c.out(),c.labels
