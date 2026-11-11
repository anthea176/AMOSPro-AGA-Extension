"""R31 0.10.3: capture active private AGA ColorMap into one AGAPAL slot.

Approved AMOS API: _OK=Aga Palette Bank Capture(Start(bank),slot).
D3=slot (0-based), (A3)+=live AMOS DATA bank address. Returns D3=1/0,
D2=0; A3 consumes one long, all other AMOS registers preserved.

Reads GetRGB32 once into a temporary Exec AllocVec buffer, converts the
most significant byte of each of its RGB32 values to RGB24, and clears
unused destination color bytes. Only the selected 8-byte descriptor's
color count and its 768-byte RGB24 slot may change. No palette/screen
updates, file I/O, persistent allocations, or automatic VBL waits.

Preflight is entirely read-only on the bank: check live pointer alignment,
TypeOfMem header and end, permanent DATA flags, valid AMOS bank number,
exact native length, AGAPAL external/internal signatures and version,
slots 1..256, requested index and selected descriptor offset/flags.
Then check private AGA Intuition screen/graphics library/ColorMap, reject
HAM/EHB/dual playfield and invalid counts/depth, and allocate scratch.
Rejected operations do not modify the bank. TypeOfMem is not an
ownership proof: callers MUST supply an actual Start(bank) from a live
AMOS DATA bank, never a stale/arbitrary pointer.
"""
from m68k_emit import Code, D, A, M, POST, I

ENTRY_CAPTURE=42
BASE_ENTRIES=42
GETP=b"GetP"
MAX_SLOTS=256
MAX_COLORS=256
STATE_PTR=456
UNSUPPORTED_MODE=0x0c80
LVO_TYPEOFMEM=-534
LVO_ALLOCVEC=-684
LVO_FREEVEC=-690
LVO_GETRGB32=-900


def emit_capture():
    c=Code()
    c.raw("48e7efee")            # established R30 return-preserving ABI
    c.move(D(3),D(5))            # requested zero-based slot
    c.move(POST(3),D(4))         # actual Start(bank), consume one argument
    c.move(I(0),D(3))            # fail by default

    c.imm("cmp",MAX_SLOTS-1,D(5))
    c.branch(2,"exit")           # BHI also rejects negative index
    c.move(D(4),D(0))
    c.imm("cmp",24,D(0))
    c.branch(3,"exit")           # BLS, includes null/short pointers
    c.imm("and",1,D(0))
    c.branch(6,"exit")           # odd address

    # Check first AMOS header byte is system-managed before dereferencing.
    c.move(D(4),D(0))
    c.imm("sub",24,D(0))
    c.move(D(0),A(1))
    c.raw("2c780004")            # MOVEA.L 4.W,A6 -> ExecBase
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0))
    c.branch(7,"exit")

    c.move(D(4),A(0))
    c.move(I(0),D(6))
    c.move(M(0,8),D(6),"w")   # bank-internal palette capacity
    c.tst(D(6))
    c.branch(7,"exit")
    c.imm("cmp",MAX_SLOTS,D(6))
    c.branch(2,"exit")
    c.alu("cmp",D(6),5)       # slot - capacity
    c.branch(4,"exit")        # BCC: slot >= capacity
    c.move(D(6),D(7))
    c.raw("cefc0308")            # MULU.W #776,D7
    c.imm("add",16,D(7))       # exact AGAPAL data size

    # Check bank's final byte before accessing its native header/descriptors.
    c.move(D(4),D(0))
    c.alu("add",D(7),0)
    c.branch(5,"exit")        # BCS: address overflow
    c.quick(1,D(0),sub=True)
    c.move(D(0),A(1))
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0))
    c.branch(7,"exit")

    # Native AMOS DATA header, identical conventions to R30 Init.
    c.move(D(4),A(0))
    c.move(M(0,-20),D(0))    # header length = payload length + 16
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

    # Validate AGAPAL v1 header, including reserved fields.
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
    c.move(M(0,10),D(0),"w")
    c.tst(D(0),"w")
    c.branch(6,"exit")
    c.tst(M(0,12))
    c.branch(6,"exit")

    # Descriptor address = bank + 16 + index*8.
    c.move(D(5),D(1))
    c.shift(1,3,left=True)
    c.imm("add",16,D(1))
    c.alu("add",D(4),1)
    c.move(D(1),A(1))
    # Expected relative RGB slot = 16 + capacity*8 + index*768.
    c.move(D(6),D(0))
    c.shift(0,3,left=True)
    c.imm("add",16,D(0))
    c.move(D(5),D(1))
    c.raw("c2fc0300")            # MULU.W #768,D1
    c.alu("add",D(1),0)
    c.alu("cmp",M(1),0)
    c.branch(6,"exit")
    c.move(I(0),D(0))
    c.move(M(1,4),D(0),"w")
    c.imm("cmp",MAX_COLORS,D(0))
    c.branch(2,"exit")           # corrupted color count
    c.tst(M(1,6),"w")
    c.branch(6,"exit")           # unknown descriptor flags

    # Private AGA Intuition screen only, same source as R29 Palette Save.
    c.move(M(5,STATE_PTR),A(0))
    c.move(A(0),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.move(M(0,0),A(1))
    c.move(A(1),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.tst(M(0,8))                # graphics.library base
    c.branch(7,"exit")
    c.move(M(0,28),D(0))        # logical planar depth
    c.tst(D(0))
    c.branch(15,"exit")         # BLE 0
    c.imm("cmp",8,D(0))
    c.branch(2,"exit")
    c.move(M(0,24),D(0))
    c.imm("and",UNSUPPORTED_MODE,D(0))
    c.branch(6,"exit")
    c.move(M(0,20),D(7))       # logical colors
    c.tst(D(7))
    c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(7))
    c.branch(2,"exit")
    c.move(M(1,48),A(2))       # Screen.ViewPort.ColorMap
    c.move(A(2),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.move(I(0),D(0))
    c.move(M(2,2),D(0),"w")   # ColorMap.Count
    c.tst(D(0))
    c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(0))
    c.branch(2,"exit")
    c.alu("cmp",D(0),7)
    c.branch(3,"count_ready")    # logical <= colormap
    c.move(D(0),D(7))
    c.label("count_ready")

    # Scratch allocation is completely independent of persistent AGAPAL.
    c.move(D(7),D(0))
    c.raw("c0fc000c")            # MULU.W #12,D0 (RGB32 words)
    c.move(I(1),D(1))            # MEMF_PUBLIC, no CHIP requirement
    c.raw("2c780004")
    c.call_os(LVO_ALLOCVEC)
    c.tst(D(0))
    c.branch(7,"exit")           # allocation failed; bank untouched
    c.move(D(0),A(4))            # keep allocation for FreeVec

    # graphics.library GetRGB32(ColorMap,first=0,count,RGB32*).
    c.move(A(2),A(0))
    c.move(A(4),A(1))
    c.move(I(0),D(0))
    c.move(D(7),D(1))
    c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6))
    c.call_os(LVO_GETRGB32)

    # From here no fallible operations remain before completing the slot.
    c.move(D(6),D(0))
    c.shift(0,3,left=True)
    c.imm("add",16,D(0))
    c.move(D(5),D(1))
    c.raw("c2fc0300")            # MULU.W #768,D1
    c.alu("add",D(1),0)
    c.alu("add",D(4),0)
    c.move(D(0),A(1))            # selected slot only
    c.move(I(192),D(6))         # 192 LONGs = 768 bytes
    c.label("clear_slot")
    c.move(I(0),POST(1))
    c.quick(1,D(6),sub=True)
    c.branch(6,"clear_slot")

    c.move(D(0),A(1))            # start of selected slot again
    c.move(A(4),A(2))            # RGB32 source
    c.move(D(7),D(6))
    c.label("copy_rgb")
    for _ in range(3):
        c.move(M(2),POST(1),"b")
        c.quick(4,A(2))          # skip low three bytes of RGB32 fraction
    c.quick(1,D(6),sub=True)
    c.branch(6,"copy_rgb")

    # Commit the new color count only after RGB bytes are fully populated.
    c.move(D(5),D(0))
    c.shift(0,3,left=True)
    c.imm("add",20,D(0))
    c.alu("add",D(4),0)
    c.move(D(0),A(0))
    c.move(D(7),M(0),"w")

    c.move(A(4),A(1))
    c.raw("2c780004")
    c.call_os(LVO_FREEVEC)
    c.move(I(1),D(3))
    c.label("exit")
    c.raw("4cdf77f7")            # restore all except result D2/D3 and A3
    c.raw("74004e75")            # D2=0 integer result; RTS
    return c.out(),c.labels
