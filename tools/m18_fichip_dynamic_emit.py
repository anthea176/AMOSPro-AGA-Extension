"""M18/R66 native 68000 AP20 dynamic FICHIP8 cache lifecycle.

API #64: Aga F Chip Bank Create(CacheBank,Count) -> D3=1/0.
API #65: Aga F Chip Stage(SourceBank,CacheBank,IconID) -> D3=1/0.

AMOS-owned DATA bank FICHIP8  is allocated as Chip-preferred (D1=3), and
physical Chip residency is verified with Exec TypeOfMem MEMF_CHIP on BOTH
ends before the first write. Occupied numbers are rejected non-destructively.
Stage validates AMOS bank headers, both spans, canonical source slot and
physical destination Chip before setting ready=0, converting exactly 288
bytes and setting ready=1 only after the last planar word is stored.
Source FICON8 can be Fast/Chip, but never overlaps the cache. No DMA,
swap, palette, screen changes or implicit cache invalidation.
"""
from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr

ENTRY_CREATE=64
ENTRY_STAGE=65
MIN_BANK,MAX_BANK=5,65535
MIN_COUNT,MAX_COUNT=4,4096
HEADER,SLOT=12,288
CHIP_FLAG=2
LVO_TYPEOFMEM=-534
CACHE_NAME=b"FICHIP8 "
SOURCE_NAME=b"FICON8  "
GETADR_MARKER=rjsr(main_index("Bnk.GetAdr"))
RESERVE_MARKER=rjsr(main_index("Bnk.Reserve"))
CHANGE_MARKER=rjsr(main_index("Bnk.Change"))
EFF_MARKER=rjsr(main_index("Bnk.Eff"))

CREATE_F=dict(count=0,bank=4,total=8,pointer=12,last=16)
CREATE_FRAME=64

def emit_chip_bank_create():
    c=Code();B,L=c.branch,c.label
    def get(field,reg):c.move(M(2,CREATE_F[field]),reg)
    def put(reg,field):c.move(reg,M(2,CREATE_F[field]))
    def call(marker):c.raw(marker.hex())
    def must_chip(reg):
        c.move(reg,A(1))
        c.raw("2c780004")             # MOVEA.L 4.W,A6 = ExecBase
        c.call_os(LVO_TYPEOFMEM)
        c.imm("and",CHIP_FLAG,D(0));B(7,"erase_new")

    c.raw("48e7efee")                 # preserve all except D2/D3/A3
    c.raw("4fefffc0")                 # 64-byte frame
    c.move(A(7),A(2))
    put(D(3),"count")
    c.move(POST(3),D(7));put(D(7),"bank")
    c.move(I(0),D(3))
    for field,minimum,maximum in (("bank",MIN_BANK,MAX_BANK),
                                  ("count",MIN_COUNT,MAX_COUNT)):
        get(field,D(0));c.imm("cmp",minimum,D(0));B(5,"return")
        c.imm("cmp",maximum,D(0));B(2,"return")
    # Total payload: 12 + Count * (288 + 1)
    get("count",D(0))
    c.move(I(SLOT+1),D(1));c.word(0xc0c1) # MULU.W D1,D0
    c.imm("add",HEADER,D(0));put(D(0),"total")
    # Double collision guard before Bnk.Reserve (reserve is destructive).
    for _ in range(2):
        get("bank",D(0));call(GETADR_MARKER)
        c.move(A(0),D(0));c.tst(D(0));B(6,"return")
    get("bank",D(0));c.move(I(3),D(1))   # AMOS DATA + Chip preferred
    get("total",D(2));c.lea(0,"bank_name")
    call(RESERVE_MARKER)
    c.tst(D(0));B(7,"return")
    put(D(0),"pointer")
    c.imm("cmp",24,D(0));B(3,"erase_new")
    c.move(D(0),D(1));c.imm("and",1,D(1));B(6,"erase_new")
    get("pointer",D(0));get("total",D(1))
    c.alu("add",D(1),0);B(5,"erase_new")
    c.quick(1,D(0),sub=True);put(D(0),"last")
    get("pointer",D(0));must_chip(D(0))
    get("last",D(0));must_chip(D(0))

    # Header: total.l count.w 16.w 16.w 8.w
    get("pointer",A(1));get("total",D(0))
    c.move(D(0),POST(1))
    get("count",D(0));c.move(D(0),POST(1),"w")
    c.move(I(16,"w"),POST(1),"w")
    c.move(I(16,"w"),POST(1),"w")
    c.move(I(8,"w"),POST(1),"w")
    # Clear slot payload: Count*72 LONG writes = Count*288 bytes.
    get("count",D(6));c.move(I(72),D(1));c.word(0xccc1) # MULU.W D1,D6
    L("zero_slots")
    c.move(I(0),POST(1))
    c.quick(1,D(6),sub=True);B(6,"zero_slots")
    # Clear count validity markers, each one BYTE (Count may be odd).
    get("count",D(6))
    L("zero_ready")
    c.move(I(0,"w"),POST(1),"b")
    c.quick(1,D(6),sub=True);B(6,"zero_ready")
    call(CHANGE_MARKER)
    c.move(I(1),D(3));B(0,"return")
    L("erase_new")
    get("bank",D(0));call(EFF_MARKER)
    c.move(I(0),D(3))
    L("return")
    c.raw("4fef0040")                 # restore local frame
    c.raw("4cdf77f7")
    c.raw("74004e75")                 # D2=0 -> integer; RTS
    L("bank_name");c.raw(CACHE_NAME.hex())
    return c.out(),c.labels

STAGE_F=dict(icon=0,cache_bank=4,source_bank=8,
             source_base=12,source_len=16,source_end=20,source_count=24,
             cache_base=28,cache_len=32,cache_end=36,cache_count=40,
             source_slot=44,cache_slot=48,ready_ptr=52)
STAGE_FRAME=96

def emit_chip_stage():
    c=Code();B,L=c.branch,c.label
    def get(field,reg):c.move(M(2,STAGE_F[field]),reg)
    def put(reg,field):c.move(reg,M(2,STAGE_F[field]))
    def type_mem(reg,chip=False):
        c.move(reg,A(1));c.raw("2c780004");c.call_os(LVO_TYPEOFMEM)
        if chip:c.imm("and",CHIP_FLAG,D(0))
        c.tst(D(0));B(7,"fail")
    def bank_lookup(bank,base,length,end,chip=False):
        get(bank,D(0));c.raw(GETADR_MARKER.hex())
        c.move(A(0),D(5));c.imm("cmp",24,D(5));B(3,"fail")
        c.move(D(5),D(0));c.imm("and",1,D(0));B(6,"fail")
        put(D(5),base)
        type_mem(D(5),chip)
        get(base,D(0));c.imm("sub",24,D(0))
        type_mem(D(0),chip)
        get(base,A(0));c.move(M(0,-20),D(4))
        c.imm("cmp",28,D(4));B(5,"fail")
        c.imm("sub",16,D(4))
        c.imm("cmp",HEADER+MAX_COUNT*(SLOT+1),D(4));B(2,"fail")
        put(D(4),length)
        get(base,D(0));c.alu("add",D(4),0);B(5,"fail")
        put(D(0),end)
        c.quick(1,D(0),sub=True)
        type_mem(D(0),chip)
        get(base,A(0));c.move(M(0,-16),D(0))
        get(bank,D(1));c.alu("cmp",D(1),0);B(6,"fail")
        c.move(I(0),D(0));c.move(M(0,-12),D(0),"w")
        c.tst(D(0));B(7,"flags_ok_"+bank)
        c.imm("and",0xfffd,D(0),"w")
        c.imm("cmp",1,D(0),"w");B(6,"fail")
        L("flags_ok_"+bank)
    def check_payload(base,length,count,name,sized_slot):
        get(base,A(0))
        c.move(M(0,-8),D(0));c.imm("cmp",int.from_bytes(name[:4],"big"),D(0));B(6,"fail")
        c.move(M(0,-4),D(0));c.imm("cmp",int.from_bytes(name[4:],"big"),D(0));B(6,"fail")
        c.move(M(0),D(0));c.alu("cmp",M(2,STAGE_F[length]),0);B(6,"fail")
        c.move(I(0),D(0));c.move(M(0,4),D(0),"w")
        c.imm("cmp",MIN_COUNT,D(0));B(5,"fail")
        c.imm("cmp",MAX_COUNT,D(0));B(2,"fail")
        put(D(0),count)
        get("icon",D(1));c.alu("cmp",D(1),0);B(5,"fail")
        c.move(I(sized_slot),D(1));c.word(0xc0c1)
        c.imm("add",HEADER,D(0))
        c.alu("cmp",M(2,STAGE_F[length]),0);B(6,"fail")
        for o,v in ((6,16),(8,16),(10,8)):
            c.move(I(0),D(0));c.move(M(0,o),D(0),"w")
            c.imm("cmp",v,D(0));B(6,"fail")

    c.raw("48e7efee")
    c.raw("4fefffa0")              # local frame 96
    c.move(A(7),A(2))
    put(D(3),"icon")
    c.move(POST(3),D(7));put(D(7),"cache_bank")
    c.move(POST(3),D(7));put(D(7),"source_bank")
    c.move(I(0),D(3))
    for fld in ("cache_bank","source_bank"):
        get(fld,D(0));c.imm("cmp",MIN_BANK,D(0));B(5,"fail")
        c.imm("cmp",MAX_BANK,D(0));B(2,"fail")
    get("source_bank",D(0));get("cache_bank",D(1))
    c.alu("cmp",D(1),0);B(7,"fail") # BEQ -> same bank forbidden
    get("icon",D(0));c.tst(D(0));B(15,"fail")
    c.imm("cmp",MAX_COUNT,D(0));B(2,"fail")

    bank_lookup("source_bank","source_base","source_len","source_end")
    check_payload("source_base","source_len","source_count",SOURCE_NAME,SLOT)
    bank_lookup("cache_bank","cache_base","cache_len","cache_end",chip=True)
    check_payload("cache_base","cache_len","cache_count",CACHE_NAME,SLOT+1)

    # Refuse overlapping allocations even if malicious metadata declares
    # different bank numbers.
    get("source_base",D(0));c.alu("cmp",M(2,STAGE_F["cache_end"]),0)
    B(4,"no_overlap")            # source_start >= cache_end
    get("cache_base",D(0));c.alu("cmp",M(2,STAGE_F["source_end"]),0)
    B(4,"no_overlap")            # cache_start >= source_end
    B(0,"fail")
    L("no_overlap")

    # Capture source and destination slot pointers, plus cache marker.
    for bank,target in (("source_base","source_slot"),("cache_base","cache_slot")):
        get("icon",D(0));c.quick(1,D(0),sub=True)
        c.move(I(SLOT),D(1));c.word(0xc0c1)
        c.imm("add",HEADER,D(0))
        get(bank,D(5));c.alu("add",D(5),0);B(5,"fail")
        put(D(0),target)
        c.imm("add",SLOT-1,D(0));B(5,"fail")
        type_mem(D(0),bank=="cache_base")
    get("cache_count",D(0));c.move(I(SLOT),D(1))
    c.word(0xc0c1);c.imm("add",HEADER,D(0))
    get("icon",D(1));c.quick(1,D(1),sub=True)
    c.alu("add",D(1),0)
    get("cache_base",D(5));c.alu("add",D(5),0);B(5,"fail")
    put(D(0),"ready_ptr");type_mem(D(0),chip=True)
    get("ready_ptr",A(0))
    c.move(I(0),D(0));c.move(M(0),D(0),"b")
    c.imm("cmp",1,D(0));B(2,"fail") # marker 0 or 1 only

    # Full canonical validation of the source slot BEFORE invalidating cache.
    get("source_slot",A(0));c.move(I(16),D(6))
    L("check_row")
    c.move(POST(0),D(4),"w")
    c.move(I(0),D(7));c.move(I(8),D(5))
    L("check_plane")
    c.alu("or",POST(0),7,"w")
    c.quick(1,D(5),sub=True);B(6,"check_plane")
    c.word(0x4647)              # NOT.W D7 => preserve mask
    c.alu("cmp",D(4),7,"w");B(6,"fail")
    c.quick(1,D(6),sub=True);B(6,"check_row")

    # No failure path after this point; hold ready=0 until complete.
    get("ready_ptr",A(4))
    c.move(I(0,"w"),M(4),"b")
    get("source_slot",A(0));get("cache_slot",A(1))
    c.move(I(0),D(0));c.move(I(16),D(6))
    L("copy_row")
    c.move(A(1),A(4))
    c.word(0xd9c0)              # ADDA.L D0,A4; row offset
    c.move(POST(0),D(7),"w")
    c.word(0x4647)              # NOT.W D7 -> visible mask
    c.move(D(7),M(4),"w")
    c.raw("49ec0020")           # LEA 32(A4),A4; plane0
    c.move(I(8),D(5))
    L("copy_plane")
    c.move(POST(0),M(4),"w")
    c.raw("49ec0020")
    c.quick(1,D(5),sub=True);B(6,"copy_plane")
    c.quick(2,D(0))
    c.quick(1,D(6),sub=True);B(6,"copy_row")
    get("ready_ptr",A(4))
    c.move(I(1,"w"),M(4),"b")
    c.move(I(1),D(3))
    L("fail")
    c.raw("4fef0060")
    c.raw("4cdf77f7")
    c.raw("74004e75")
    return c.out(),c.labels
