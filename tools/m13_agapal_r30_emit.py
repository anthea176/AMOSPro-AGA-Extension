"""R30 / 0.10.2: initialize one existing, correctly sized AMOS DATA bank.

Only public operation: _OK=Aga Palette Bank Init(Start(bank), paletteCount).
D3=paletteCount, (A3)+ = pointer returned by AMOS Start(bank).
Returns integer D3=1 for a successful initialization, 0 on rejection.
The caller MUST pass a live Start(bank) from an AMOS DATA bank created
with Reserve As Data. This is NOT a general arbitrary-pointer validator.

Preflight before ANY write:
- aligned pointer, 1..256 slots, nonzero TypeOfMem for bank header/end;
- native bank length at Start-20 = (16+776*N)+16;
- permanent DATA flags = 1 (fast) or 3 (chip), not object/work;
- native bank number at Start-16 in [5,65535].
TypeOfMem identifies OS-managed memory, NOT allocation ownership; callers
must never pass forged, freed or stale addresses.

On success writes only Start-8..Start-1 (eight-byte AMOS bank name) and
Start..Start+(16+776*N)-1. Does not modify other native AMOS header fields,
does not allocate memory, does not change palettes/screens, does not create
persistent pointers. 68000-compatible CPU instructions only.
"""
from m68k_emit import Code, D, A, M, POST, I

MAX_SLOTS=256
ENTRY_INDEX=41
BASE_ENTRIES=41
NAME=b"AGAPAL  "
HEAD=b"AGAPAL"
SIZE_PER_SLOT=776
LVO_TYPEOFMEM=-534

def emit_init():
    c=Code()
    c.raw("48e7efee")               # preserve all non-result/non-A3 AMOS registers
    c.move(D(3),D(5))              # D5 = requested number of palettes
    c.move(POST(3),D(4))           # D4 = Start(bank), consume one stacked arg
    c.move(I(0),D(3))              # default result 0 (no operation performed)

    # Validate requested number BEFORE using word multiply.
    c.tst(D(5))
    c.branch(7,"return")
    c.imm("cmp",MAX_SLOTS,D(5))
    c.branch(2,"return")           # unsigned higher includes negative values

    # Reject null, odd and unreasonably small pointers before the header read.
    c.move(D(4),D(0))
    c.imm("cmp",24,D(0))
    c.branch(3,"return")           # BLS
    c.imm("and",1,D(0))
    c.branch(6,"return")           # BNE

    c.move(D(5),D(6))
    c.raw("ccfc0308")             # MULU.W #776,D6 -> 32-bit N*776
    c.imm("add",16,D(6))          # D6 = exact AGAPAL data size

    # TypeOfMem for both the AMOS header and last data byte. This is an
    # early invalid-RAM filter; it does not certify a genuine AMOS allocation.
    c.move(D(4),D(0))
    c.imm("sub",24,D(0))
    c.move(D(0),A(1))
    c.raw("2c780004")              # MOVEA.L 4.W,A6 = ExecBase
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0))
    c.branch(7,"return")

    c.move(D(4),D(0))
    c.alu("add",D(6),0)
    c.branch(5,"return")           # BCS on address overflow
    c.quick(1,D(0),sub=True)
    c.move(D(0),A(1))
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0))
    c.branch(7,"return")

    c.move(D(4),A(0))
    c.move(M(0,-20),D(0))         # native AMOS length = data size + 16
    c.move(D(6),D(7))
    c.imm("add",16,D(7))
    c.alu("cmp",D(7),0)
    c.branch(6,"return")

    c.move(I(0),D(0))
    c.move(M(0,-12),D(0),"w")    # flags WORD: 1=Fast Data, 3=Chip Data
    c.imm("and",0xfffd,D(0),"w")# ignore only CHIP bit
    c.imm("cmp",1,D(0))
    c.branch(6,"return")

    c.move(M(0,-16),D(0))        # bank number LONG, 5..65535
    c.imm("cmp",5,D(0))
    c.branch(5,"return")          # BCS: <5
    c.imm("cmp",65535,D(0))
    c.branch(2,"return")          # BHI: >65535

    # Validated bank: the first modification is the eight-byte name.
    c.move(I(0x41474150),M(0,-8))# AGAP
    c.move(I(0x414c2020),M(0,-4))# AL[space][space]

    # Internal 16-byte AGAPAL v1 header, all big-endian.
    c.move(I(0x41474150),M(0,0))
    c.move(I(0x414c,"w"),M(0,4),"w")
    c.move(I(1,"w"),M(0,6),"w")
    c.move(D(5),M(0,8),"w")
    c.move(I(0,"w"),M(0,10),"w")
    c.move(I(0),M(0,12))

    # Offset of first 768-byte palette. Header + all 8-byte descriptors.
    c.move(D(5),D(7))
    c.shift(7,3,left=True)
    c.imm("add",16,D(7))
    c.move(D(4),D(0))
    c.imm("add",16,D(0))
    c.move(D(0),A(1))
    c.label("indices")
    c.move(D(7),POST(1))
    c.move(I(0,"w"),POST(1),"w")   # empty palette: count 0
    c.move(I(0,"w"),POST(1),"w")   # flags reserved 0
    c.imm("add",768,D(7))
    c.quick(1,D(5),sub=True)
    c.branch(6,"indices")

    # Clear exactly 192 LONGs per palette (768 bytes); A1 is now
    # positioned at the first palette color after the index table.
    c.move(I(0),D(5))
    c.move(M(0,8),D(5),"w")
    c.raw("cafc00c0")             # MULU.W #192,D5 -> number of LONGs
    c.label("clear_rgb")
    c.move(I(0),POST(1))
    c.quick(1,D(5),sub=True)
    c.branch(6,"clear_rgb")
    c.move(I(1),D(3))

    c.label("return")
    c.raw("4cdf77f7")             # restore registers except D3/A3
    c.raw("74004e75")             # D2=0 (integer) and RTS
    return c.out(),c.labels
