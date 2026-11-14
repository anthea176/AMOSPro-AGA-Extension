"""R80: decode indexed FORM ILBM directly to an existing 320x256 chunky bank.

Aga Iff To Chunky(File$,Bank) -> 1/0.
The 68000-native AP20 entry performs strict ILBM preflight before it writes
one byte to the caller-owned DATA/WORK bank. No screen, palette, C2P context,
or external .chk file is involved.

Only indexed 4-8 plane 320x256 ILBM, compression RAW/ByteRun1, masking=0,
and non-HAM/non-EHB/non-dualpf is accepted. Palette remains independent.
"""
from __future__ import annotations
from m68k_emit import Code, D, A, M, POST, I
from amos_main_abi import main_index, rjsr
from build_m5_generic import (
    STR, FORM, SIZE, DEPTH, MASK, COMP, RAWMODE, W, H, BODY, BS, WRITE,
    ctx, begin, end, invoke, fail_if, read_file, inspect_file, cleanup,
)

BANK = rjsr(main_index("Bnk.GetAdr"))
CHUNKY = 320 * 256
BANKNO = 128
DEST = 132
DESTLEN = 136
ROWBUF = 160
FRAME = 224
MAX_FILE = 1024 * 1024
LVO_TYPEOFMEM = -534


def dbra(c, reg, label):
    c.word(0x51c8 | reg)
    c.fix.append((len(c.b), label))
    c.word(0)


def format_check(c):
    """No pixel destination writes during format validation."""
    begin(c, "format_check")
    for field, expected in ((W, 320), (H, 256), (MASK, 0)):
        c.imm("cmp", expected, ctx(field))
        fail_if(c, 6)
    c.move(ctx(DEPTH), D(0))
    c.imm("cmp", 4, D(0))
    fail_if(c, 13)
    c.imm("cmp", 8, D(0))
    fail_if(c, 14)
    c.move(ctx(RAWMODE), D(0))
    c.imm("and", 0x0c80, D(0))  # HAM / EHB / dual playfield
    fail_if(c, 6)
    c.move(ctx(SIZE), D(0))
    c.imm("cmp", MAX_FILE, D(0))
    fail_if(c, 14)
    end(c, "format_check")


def chunky_decode(c):
    """Two identical BODY passes: scan only, then materialize indices.

    ByteRun1 control 128 is a legal NOP. Every run is bounded to its own
    planar scanline; no packet can spill into the next plane. The second
    pass runs only once the entire first pass has accepted the BODY.
    """
    begin(c, "chunky_decode")
    c.move(ctx(BODY), A(0))
    c.move(A(0), D(0))
    c.alu("add", ctx(BS), 0)
    c.move(D(0), A(2))           # first byte beyond BODY
    c.move(ctx(DEST), A(1))     # first chunky destination pixel
    c.tst(ctx(WRITE))
    c.branch(7, "scan_start")
    # Clear the whole destination only after strict preflight succeeded.
    c.move(A(1), A(4))
    c.move(I((CHUNKY // 4) - 1), D(0))
    c.label("zero_loop")
    c.word(0x429c)              # CLR.L (A4)+
    dbra(c, 0, "zero_loop")
    c.label("scan_start")
    c.move(I(255), D(4))        # 256 rows
    c.label("row_start")
    c.move(I(0), D(6))          # bitplane 0..depth-1
    c.label("plane_start")
    c.move(I(40), D(7))         # row bytes remaining
    c.move(A(5), D(0))
    c.imm("add", ROWBUF, D(0))
    c.move(D(0), A(3))          # internal 40-byte row scratch

    c.label("packet_start")
    c.tst(ctx(COMP))
    c.branch(7, "raw_packet")
    # A0 must point before BODY end before reading ByteRun1 opcode.
    c.move(A(0), D(0))
    c.alu("cmp", A(2), 0)
    fail_if(c, 4)
    c.move(I(0), D(1))
    c.move(POST(0), D(1), "b")
    c.imm("cmp", 128, D(1))
    c.branch(7, "packet_start")    # -128 is a no-op
    c.branch(2, "repeat_packet")   # 129..255
    c.quick(1, D(1))
    c.move(D(1), D(2))            # literal count 1..128
    c.branch(0, "literal_packet")
    c.label("raw_packet")
    c.move(D(7), D(2))            # exact remaining RAW row
    c.label("literal_packet")
    c.alu("cmp", D(7), 2)
    fail_if(c, 2)                 # count > 40-row_remaining
    c.move(A(2), D(0))
    c.alu("sub", A(0), 0)
    c.alu("cmp", D(2), 0)
    fail_if(c, 5)                 # truncated source
    c.alu("sub", D(2), 7)
    c.label("literal_loop")
    c.move(POST(0), POST(3), "b")
    c.quick(1, D(2), sub=True)
    c.branch(6, "literal_loop")
    c.branch(0, "next_packet")

    c.label("repeat_packet")
    c.move(I(257), D(2))
    c.alu("sub", D(1), 2)
    c.alu("cmp", D(7), 2)
    fail_if(c, 2)
    c.move(A(0), D(0))
    c.alu("cmp", A(2), 0)
    fail_if(c, 4)
    c.alu("sub", D(2), 7)
    c.move(POST(0), D(0), "b")
    c.label("repeat_loop")
    c.move(D(0), POST(3), "b")
    c.quick(1, D(2), sub=True)
    c.branch(6, "repeat_loop")
    c.label("next_packet")
    c.tst(D(7))
    c.branch(6, "packet_start")

    c.tst(ctx(WRITE))
    c.branch(7, "plane_done")
    # Unpack MSB-first planar bytes into bank indices, plane p -> bit p.
    c.move(A(5), D(0))
    c.imm("add", ROWBUF, D(0))
    c.move(D(0), A(3))
    c.move(A(1), A(4))
    c.move(I(39), D(2))
    c.label("byte_start")
    c.move(POST(3), D(0), "b")
    for bit in range(7, -1, -1):
        next_label = "pixel_skip_" + str(bit)
        c.word(0x0800)           # BTST #bit,D0
        c.word(bit)
        c.branch(7, next_label)
        c.word(0x0dd4)           # BSET D6,(A4); sets current plane bit
        c.label(next_label)
        c.quick(1, A(4))
    dbra(c, 2, "byte_start")
    c.label("plane_done")
    c.quick(1, D(6))
    c.alu("cmp", ctx(DEPTH), 6)
    c.branch(5, "plane_start")
    c.move(A(1), D(0))
    c.imm("add", 320, D(0))
    c.move(D(0), A(1))
    dbra(c, 4, "row_start")

    # Accept exactly consumed BODY, with optional trailing ByteRun1 NOPs.
    c.label("tail_check")
    c.move(A(0), D(0))
    c.alu("cmp", A(2), 0)
    c.branch(7, "body_ok")
    c.tst(ctx(COMP))
    fail_if(c, 7)
    c.move(I(0), D(0))
    c.move(POST(0), D(0), "b")
    c.imm("cmp", 128, D(0))
    fail_if(c, 6)
    c.branch(0, "tail_check")
    c.label("body_ok")
    end(c, "chunky_decode")


def emit_iff_to_chunky():
    c = Code()
    B, L = c.branch, c.label

    def fail_if_early(cc):
        B(cc, "early_failure")

    def require_mem(reg):
        c.move(reg, A(1))
        c.raw("2c780004")       # ExecBase = *(ULONG *)4
        c.call_os(LVO_TYPEOFMEM)
        c.tst(D(0))
        fail_if_early(7)

    # Standard AP20 integer-function ABI: last param Bank arrives in D3,
    # File$ descriptor is popped ONCE from the AMOS A3 argument stack.
    c.raw("48e7effe")
    c.move(POST(3), A(1))
    c.raw("4fefff20")          # LEA -224(SP),SP
    c.move(A(7), A(2))
    for off in range(0, FRAME, 4):
        c.move(I(0), M(2, off))
    c.move(A(1), M(2, STR))
    c.move(D(3), M(2, BANKNO))
    c.move(I(0), D(3))

    # Resolve the caller-owned DATA/WORK bank while A5 is still AMOS Base.
    c.move(M(2, BANKNO), D(0))
    c.imm("cmp", 5, D(0))
    fail_if_early(5)
    c.imm("cmp", 65535, D(0))
    fail_if_early(2)
    c.raw(BANK.hex())
    c.move(A(0), D(5))
    c.imm("cmp", 24, D(5))
    fail_if_early(3)
    c.move(D(5), D(0))
    c.imm("and", 1, D(0))
    fail_if_early(6)
    c.move(D(5), M(2, DEST))
    require_mem(D(5))
    c.move(D(5), D(0))
    c.imm("sub", 24, D(0))
    require_mem(D(0))
    c.move(D(5), A(4))
    c.move(M(4, -16), D(0))
    c.alu("cmp", M(2, BANKNO), 0)
    fail_if_early(6)
    c.move(I(0), D(0))
    c.move(M(4, -12), D(0), "w")
    c.tst(D(0))
    B(7, "flags_ok")
    c.imm("and", 0xfffd, D(0), "w")
    c.imm("cmp", 1, D(0), "w")
    fail_if_early(6)
    L("flags_ok")
    c.move(M(4, -20), D(0))
    c.imm("cmp", CHUNKY + 16, D(0))
    fail_if_early(5)
    c.imm("sub", 16, D(0))
    c.tst(D(0))
    fail_if_early(13)           # reject negative capacity
    c.move(D(0), M(2, DESTLEN))
    c.alu("add", D(5), 0)
    fail_if_early(5)            # overflow pointer+capacity
    c.quick(1, D(0), sub=True)
    require_mem(D(0))          # destination final byte is allocated

    # Borrow validated generic M5 ILBM file parsing and resource cleanup.
    c.move(A(2), A(5))
    invoke(c, "read_file")
    invoke(c, "inspect")
    invoke(c, "format_check")
    invoke(c, "chunky_decode") # first pass: no caller bank writes
    c.move(I(1), ctx(WRITE))
    invoke(c, "chunky_decode") # second pass: write exactly 81920 indices
    c.move(I(1), D(3))
    B(0, "done")

    L("early_failure")
    c.move(A(2), A(5))         # context even for rejected bank input
    L("failure")
    c.move(I(0), D(3))
    L("done")
    B(1, "cleanup")
    c.raw("4fef00e04cdf7ff774004e75")

    read_file(c)
    inspect_file(c)
    format_check(c)
    chunky_decode(c)
    cleanup(c)
    L("dosname")
    c.b.extend(b"dos.library\0")
    if len(c.b) & 1:
        c.b.append(0)
    return c.out(), c.labels
