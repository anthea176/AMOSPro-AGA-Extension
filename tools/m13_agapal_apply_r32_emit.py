"""R32 0.10.4: apply one validated AGAPAL RGB24 slot to the private AGA screen.

Approved AMOS API: _OK=Aga Palette Bank Apply(Start(bank),index).
D3 = 0-based palette index, (A3)+ = live AMOS DATA bank data pointer.
Return integer D3=1/0, D2=0; preserve remaining AMOS registers and consume
exactly one long on A3. A valid palette is applied immediately via
graphics.library/LoadRGB32, with NO implicit WaitTOF/VBL and NO pixel writes.

Read-only validation before any screen change:
* TypeOfMem on native bank header and final byte (not proof of ownership),
  exact AMOS DATA size and flags, bank identity and AGAPAL signature/version;
* capacity 1..256, selected index in range, matching indexed RGB offset,
  flags 0 and selected palette color count 1..256 (empty is invalid);
* live private AGA Intuition Screen, ColorMap, graphics.library base,
  supported depth and mode, and ColorMap/logical color capacity >= count;
* successful temporary MEMF_PUBLIC AllocVec of 8+12*count bytes.

Encode a LoadRGB32 table (WORD count, WORD firstPen=0, RGB32 triplets,
zero LONG terminator). Each RGB24 byte is replicated four times to a
32-bit fraction. Update only pens 0..count-1; higher pens stay unchanged.
FreeVec scratch on the success path. None of the source AGAPAL bytes or
bitmap planes change. The LoadRGB32 OS call has no failure result.

Only Start(bank) from a live DATA bank is safe; TypeOfMem is insufficient
to make stale or arbitrary caller addresses safe.
"""
from m68k_emit import Code,D,A,M,POST,I

ENTRY_APPLY=43
BASE_ENTRIES=43
GETP=b"GetP"
MAX_SLOTS=256
MAX_COLORS=256
STATE_PTR=456
UNSUPPORTED_MODE=0x0c80
LVO_TYPEOFMEM=-534
LVO_ALLOCVEC=-684
LVO_FREEVEC=-690
LVO_LOADRGB32=-882


def emit_apply():
    c=Code()
    c.raw("48e7efee")            # R30/R31 proven register save mask
    c.move(D(3),D(5))            # 0-based slot
    c.move(POST(3),D(4))         # real AMOS Start(bank)
    c.move(I(0),D(3))            # failure by default

    c.imm("cmp",MAX_SLOTS-1,D(5))
    c.branch(2,"exit")           # unsigned >255 (includes negative)
    c.move(D(4),D(0))
    c.imm("cmp",24,D(0))
    c.branch(3,"exit")           # BLS: null/short pointer
    c.imm("and",1,D(0))
    c.branch(6,"exit")           # odd pointer

    # Validate address of first native header byte before dereferencing.
    c.move(D(4),D(0))
    c.imm("sub",24,D(0))
    c.move(D(0),A(1))
    c.raw("2c780004")            # MOVEA.L 4.W,A6: ExecBase
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0))
    c.branch(7,"exit")

    c.move(D(4),A(0))
    c.move(I(0),D(6))
    c.move(M(0,8),D(6),"w")    # AGAPAL capacity
    c.tst(D(6))
    c.branch(7,"exit")
    c.imm("cmp",MAX_SLOTS,D(6))
    c.branch(2,"exit")
    c.alu("cmp",D(6),5)
    c.branch(4,"exit")          # index >= capacity
    c.move(D(6),D(7))
    c.raw("cefc0308")           # MULU.W #776,D7
    c.imm("add",16,D(7))        # exact payload capacity

    # Check final byte is mapped before dereferencing the bank metadata.
    c.move(D(4),D(0))
    c.alu("add",D(7),0)
    c.branch(5,"exit")          # BCS: address overflow
    c.quick(1,D(0),sub=True)
    c.move(D(0),A(1))
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0))
    c.branch(7,"exit")

    # Native AMOS DATA allocation header (24 bytes before Start(bank)).
    c.move(D(4),A(0))
    c.move(M(0,-20),D(0))
    c.move(D(7),D(1))
    c.imm("add",16,D(1))
    c.alu("cmp",D(1),0)
    c.branch(6,"exit")
    c.move(I(0),D(0))
    c.move(M(0,-12),D(0),"w")
    c.imm("and",0xfffd,D(0),"w")
    c.imm("cmp",1,D(0))
    c.branch(6,"exit")
    c.move(M(0,-16),D(0))
    c.imm("cmp",5,D(0))
    c.branch(5,"exit")
    c.imm("cmp",65535,D(0))
    c.branch(2,"exit")
    c.move(M(0,-8),D(0))
    c.imm("cmp",0x41474150,D(0))  # "AGAP"
    c.branch(6,"exit")
    c.move(M(0,-4),D(0))
    c.imm("cmp",0x414c2020,D(0))  # "AL  "
    c.branch(6,"exit")

    # AGAPAL version 1, exact magic and reserved fields.
    c.move(M(0),D(0))
    c.imm("cmp",0x41474150,D(0))
    c.branch(6,"exit")
    c.move(I(0),D(0))
    c.move(M(0,4),D(0),"w")
    c.imm("cmp",0x414c,D(0))
    c.branch(6,"exit")
    c.move(I(0),D(0))
    c.move(M(0,6),D(0),"w")
    c.imm("cmp",1,D(0))
    c.branch(6,"exit")
    c.tst(M(0,10),"w")
    c.branch(6,"exit")
    c.tst(M(0,12))
    c.branch(6,"exit")

    # Selected 8-byte index descriptor.
    c.move(D(5),D(1))
    c.shift(1,3,left=True)
    c.imm("add",16,D(1))
    c.alu("add",D(4),1)
    c.move(D(1),A(1))
    c.move(D(6),D(0))
    c.shift(0,3,left=True)
    c.imm("add",16,D(0))
    c.move(D(5),D(1))
    c.raw("c2fc0300")           # MULU.W #768,D1
    c.alu("add",D(1),0)
    c.alu("cmp",M(1),0)
    c.branch(6,"exit")
    c.move(I(0),D(7))
    c.move(M(1,4),D(7),"w")   # source RGB color count
    c.tst(D(7))
    c.branch(7,"exit")          # empty AGAPAL slot
    c.imm("cmp",MAX_COLORS,D(7))
    c.branch(2,"exit")
    c.tst(M(1,6),"w")
    c.branch(6,"exit")          # unsupported flags
    c.alu("add",D(4),0)
    c.move(D(0),A(2))           # selected RGB24 data, read-only

    # Private Intuition screen and ColorMap, no AMOS legacy screen.
    c.move(M(5,STATE_PTR),A(0))
    c.move(A(0),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.move(M(0,0),A(1))
    c.move(A(1),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.tst(M(0,8))               # graphics.library base
    c.branch(7,"exit")
    c.move(M(0,28),D(0))       # indexed screen depth 1..8
    c.tst(D(0))
    c.branch(15,"exit")
    c.imm("cmp",8,D(0))
    c.branch(2,"exit")
    c.move(M(0,24),D(0))
    c.imm("and",UNSUPPORTED_MODE,D(0))
    c.branch(6,"exit")
    c.move(M(0,20),D(0))       # logical indexed colors
    c.tst(D(0))
    c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(0))
    c.branch(2,"exit")
    c.alu("cmp",D(0),7)         # count - logical colors
    c.branch(2,"exit")         # do not silently truncate
    c.move(M(1,48),A(1))      # Screen.ViewPort.ColorMap
    c.move(A(1),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.move(I(0),D(0))
    c.move(M(1,2),D(0),"w")  # ColorMap.Count
    c.tst(D(0))
    c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(0))
    c.branch(2,"exit")
    c.alu("cmp",D(0),7)         # count - ColorMap.Count
    c.branch(2,"exit")

    # Allocate the complete LoadRGB32 table (header + RGB32 + terminator).
    c.move(D(7),D(0))
    c.raw("c0fc000c")           # MULU.W #12,D0
    c.imm("add",8,D(0))
    c.move(I(1),D(1))           # MEMF_PUBLIC (Fast permitted)
    c.raw("2c780004")           # ExecBase
    c.call_os(LVO_ALLOCVEC)
    c.tst(D(0))
    c.branch(7,"exit")          # no screen or bank changes
    c.move(D(0),A(4))           # own temporary table through FreeVec

    # RGB32 table first LONG = (count << 16) | firstPen(0).
    c.move(A(4),A(1))
    c.move(D(7),D(0))
    c.raw("4840")               # SWAP D0: count in high word
    c.move(D(0),POST(1))

    c.move(D(7),D(6))           # color loop bound
    c.label("color_loop")
    for _ in range(3):         # red, green, blue, in that order
        c.move(I(0),D(0))
        c.move(POST(2),D(0),"b")
        c.move(D(0),D(1))
        c.shift(0,8,left=True)
        c.alu("or",D(1),0)      # 0x0000bbbb
        c.move(D(0),D(1))
        c.raw("4840")           # 0xbbbb0000
        c.alu("or",D(1),0)      # 0xbbbbbbbb
        c.move(D(0),POST(1))
    c.quick(1,D(6),sub=True)
    c.branch(6,"color_loop")
    c.move(I(0),M(1))           # terminating longword

    # LoadRGB32(ViewPort*,table): NO implicit VBL, no bitmap writes.
    c.move(M(5,STATE_PTR),A(0))
    c.move(M(0,0),A(0))        # Intuition Screen*
    c.move(A(0),D(0))
    c.imm("add",44,D(0))
    c.move(D(0),A(0))           # Screen.ViewPort*
    c.move(A(4),A(1))           # table start
    c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6))        # graphics.library
    c.call_os(LVO_LOADRGB32)

    c.move(A(4),A(1))
    c.raw("2c780004")           # ExecBase
    c.call_os(LVO_FREEVEC)
    c.move(I(1),D(3))
    c.label("exit")
    c.raw("4cdf77f7")           # restore all except D2/D3 and A3
    c.raw("74004e75")           # D2=integer, RTS
    return c.out(),c.labels
