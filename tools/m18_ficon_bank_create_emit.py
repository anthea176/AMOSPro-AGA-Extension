"""M18/R64 native 68000 AP20: Aga F Icon Bank Create(Bank, Count) -> D3=1/0.

D3 receives Count; A3 supplies the stacked Bank LONG. Allocate an AMOS
permanent DATA bank using source-audited Bnk.GetAdr/Reserve/Change/Eff.
Reject occupied bank numbers BEFORE destructive Reserve, including a second
check immediately before reservation. No private screen, palette or DMA.

FICON8 payload: >IHHHH header (12 bytes), Count * 288 bytes, each 16x16x8
row = preserve.w ($ffff) + 8 plane words (zero). Fully canonical empty
icons: masked Aga F Icon draws nothing; opaque draws index zero.
No persistent private allocation; Erase/Save/Load remain owned by AMOS.
Gate A CPU/ABI and interpreted WinUAE B must be validated independently.
"""
from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr

ENTRY_INDEX=62
MIN_BANK,MAX_BANK=5,65535
MIN_COUNT,MAX_COUNT=4,4096
HEADER,SLOT,ROW=12,288,18
NAME=b"FICON8  "
IDX_GETADR=main_index("Bnk.GetAdr")
IDX_RESERVE=main_index("Bnk.Reserve")
IDX_CHANGE=main_index("Bnk.Change")
IDX_EFF=main_index("Bnk.Eff")
GETADR_MARKER=rjsr(IDX_GETADR)
RESERVE_MARKER=rjsr(IDX_RESERVE)
CHANGE_MARKER=rjsr(IDX_CHANGE)
EFF_MARKER=rjsr(IDX_EFF)
F=dict(count=0,bank=4,total=8,pointer=12)
FRAME=48

def emit_ficon_bank_create():
    c=Code()
    B,L=c.branch,c.label
    def ld(field,reg):c.move(M(2,F[field]),reg)
    def st(reg,field):c.move(reg,M(2,F[field]))
    def bank_call(index):c.raw(rjsr(index).hex())

    c.raw("48e7efee")              # AMOS preservation: D2/D3/A3 output only
    c.raw("4fefffd0")              # LEA -48(SP),SP
    c.move(A(7),A(2))
    st(D(3),"count")
    c.move(POST(3),D(7));st(D(7),"bank")
    c.move(I(0),D(3))            # default result 0

    # Reject signed negatives, truncation and out-of-range inputs.
    ld("count",D(0))
    c.imm("cmp",MIN_COUNT,D(0));B(5,"return")
    c.imm("cmp",MAX_COUNT,D(0));B(2,"return")
    ld("bank",D(0))
    c.imm("cmp",MIN_BANK,D(0));B(5,"return")
    c.imm("cmp",MAX_BANK,D(0));B(2,"return")

    # Size is full 32-bit: 12 + Count*288, maximum 1,179,660.
    ld("count",D(0))
    c.move(I(SLOT),D(1))
    c.word(0xc0c1)               # MULU.W D1,D0 (68000, LONG result)
    c.imm("add",HEADER,D(0))
    st(D(0),"total")

    # Bnk.Reserve overwrites an existing AMOS bank: never do it blindly.
    ld("bank",D(0));bank_call(IDX_GETADR)
    c.move(A(0),D(0));c.tst(D(0));B(6,"return")
    ld("bank",D(0));bank_call(IDX_GETADR)
    c.move(A(0),D(0));c.tst(D(0));B(6,"return")

    ld("bank",D(0))
    c.move(I(1),D(1))          # AMOS permanent DATA, Fast preferred
    ld("total",D(2))
    c.lea(0,"bank_name")
    bank_call(IDX_RESERVE)
    c.tst(D(0));B(7,"return")  # no allocation -> no cleanup
    st(D(0),"pointer")

    # Validate returned pointer and integer end BEFORE the first write.
    c.imm("cmp",24,D(0));B(3,"erase_new")  # <=24 is never valid
    c.move(D(0),D(1))
    c.imm("and",1,D(1))
    B(6,"erase_new")            # odd bank DATA pointer
    ld("pointer",D(0))
    ld("total",D(1))
    c.alu("add",D(1),0);B(5,"erase_new") # overflow

    # Exact Unity-compatible FICON8 header in native big endian.
    ld("pointer",A(1))
    ld("total",D(0));c.move(D(0),POST(1))
    ld("count",D(0));c.move(D(0),POST(1),"w")
    c.move(I(16,"w"),POST(1),"w")
    c.move(I(16,"w"),POST(1),"w")
    c.move(I(8,"w"),POST(1),"w")

    # 16 rows/icon * Count; 32-bit LONG counter handles Count=4096.
    ld("count",D(6));c.shift(6,4,left=True)
    L("empty_row")
    c.move(I(0xffff,"w"),POST(1),"w")
    for _ in range(4):
        c.move(I(0),POST(1))
    c.quick(1,D(6),sub=True)
    B(6,"empty_row")

    # All 288*N bytes are now canonical and stable. Notify AMOS.
    bank_call(IDX_CHANGE)
    c.move(I(1),D(3))
    B(0,"return")

    L("erase_new")
    ld("bank",D(0));bank_call(IDX_EFF)
    c.move(I(0),D(3))
    L("return")
    c.raw("4fef0030")         # restore original stack before MOVEM
    c.raw("4cdf77f7")
    c.raw("74004e75")         # D2=0 integer result; RTS

    L("bank_name")
    c.raw(NAME.hex())
    return c.out(),c.labels
