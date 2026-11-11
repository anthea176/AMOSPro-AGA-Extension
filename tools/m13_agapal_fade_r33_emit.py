"""R33 0.10.5 - blocking RGB24 AGAPAL fade, one LoadRGB32 per WaitTOF.

Approved call: _OK=Aga Fade To Bank(Start(bank),index,vbl).
D3 = vbl (1..255), (A3)+ = index, (A3)+ = live DATA Start(bank).
Return D3=1/0 and D2=0; all other AMOS registers preserved.

For n=2..255, GetRGB32 once captures current pen values. A 8.8
signed fixed-point step is precomputed once per RGB component using
DIVS.W (difference*256 / vbl). Each intermediate VBL adds the step,
converts the byte to RGB32 and calls LoadRGB32 once. Last frame ALWAYS
reads the exact target RGB24 bytes, eliminating all cumulative rounding
error. For vbl=1, no GetRGB32 nor division is necessary.

Scratch, single AllocVec(MEMF_PUBLIC) allocation:
  0                   : LoadRGB32 header, triplets, terminator (8+12*N)
  8+12*N              : GetRGB32 source (12*N)
  8+24*N              : signed DDA states (3*N)*(LONG accum + WORD step)
  total               : 8+42*N bytes <= 10760
All scratch released, no bank or bitmap writes, no persistent state.

All validation/allocations precede the first VBL and LoadRGB32; invalid
banks, slots, color counts, screens, and durations fail atomically.
WaitTOF is graphics.library LVO -270 (A6=GfxBase); GetRGB32 -900,
LoadRGB32 -882. Long fades are blocking, with N explicit VBL waits.
At 68000/256 colors a frame can exceed a refresh period: exact
real-time duration/50 fps is not guaranteed.
Only Start(bank) from an actual live DATA AMOS bank is safe.
"""
from m68k_emit import Code,D,A,M,POST,PRE,I

ENTRY_FADE=44
BASE_ENTRIES=44
GETP=b"GetP"
MAX_SLOTS=256
MAX_COLORS=256
STATE_PTR=456
UNSUPPORTED_MODE=0x0c80
LVO_TYPEOFMEM=-534
LVO_ALLOCVEC=-684
LVO_FREEVEC=-690
LVO_GETRGB32=-900
LVO_LOADRGB32=-882
LVO_WAITTOF=-270


def expand_rgb(c):
    """D0 low byte (0..255) to replicated RGB32 in (A1)+; clobbers D1."""
    c.move(D(0),D(1))
    c.shift(0,8,left=True)
    c.alu("or",D(1),0)
    c.move(D(0),D(1))
    c.raw("4840")                  # SWAP D0
    c.alu("or",D(1),0)
    c.move(D(0),POST(1))


def emit_fade():
    c=Code()
    c.raw("48e7efee")              # prior R30..R32 ABI-safe MOVEM mask
    c.move(D(3),PRE(7))            # save duration on stack (all exits restore)
    c.move(POST(3),D(5))           # slot
    c.move(POST(3),D(4))           # Start(bank)
    c.move(I(0),D(3))              # default failure

    # Reject duration 0, negative and >255 BEFORE touching any bank memory.
    c.move(M(7),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.imm("cmp",255,D(0))
    c.branch(2,"exit")             # unsigned >255 also rejects negatives
    c.imm("cmp",MAX_SLOTS-1,D(5))
    c.branch(2,"exit")             # slot >=256 or negative
    c.move(D(4),D(0))
    c.imm("cmp",24,D(0))
    c.branch(3,"exit")             # pointer <=24
    c.imm("and",1,D(0))
    c.branch(6,"exit")             # odd pointer

    # Native bank header must be mapped before reading. No ownership proof.
    c.move(D(4),D(0))
    c.imm("sub",24,D(0))
    c.move(D(0),A(1))
    c.raw("2c780004")              # MOVEA.L 4.W,A6 (ExecBase)
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0))
    c.branch(7,"exit")
    c.move(D(4),A(0))
    c.move(I(0),D(6))
    c.move(M(0,8),D(6),"w")        # AGAPAL palette capacity
    c.tst(D(6))
    c.branch(7,"exit")
    c.imm("cmp",MAX_SLOTS,D(6))
    c.branch(2,"exit")
    c.alu("cmp",D(6),5)
    c.branch(4,"exit")             # index >= capacity
    c.move(D(6),D(7))
    c.raw("cefc0308")              # MULU.W #776,D7
    c.imm("add",16,D(7))

    # Verify final data byte mapped and exact native AMOS DATA metadata.
    c.move(D(4),D(0))
    c.alu("add",D(7),0)
    c.branch(5,"exit")
    c.quick(1,D(0),sub=True)
    c.move(D(0),A(1))
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0))
    c.branch(7,"exit")
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
    c.imm("cmp",0x41474150,D(0))
    c.branch(6,"exit")
    c.move(M(0,-4),D(0))
    c.imm("cmp",0x414c2020,D(0))
    c.branch(6,"exit")
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

    # Verify only the selected indexed RGB24 descriptor.
    c.move(D(5),D(1))
    c.shift(1,3,left=True)
    c.imm("add",16,D(1))
    c.alu("add",D(4),1)
    c.move(D(1),A(1))
    c.move(D(6),D(0))
    c.shift(0,3,left=True)
    c.imm("add",16,D(0))
    c.move(D(5),D(1))
    c.raw("c2fc0300")              # MULU.W #768,D1
    c.alu("add",D(1),0)
    c.alu("cmp",M(1),0)
    c.branch(6,"exit")
    c.move(I(0),D(7))
    c.move(M(1,4),D(7),"w")        # color count for selected palette
    c.tst(D(7))
    c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(7))
    c.branch(2,"exit")
    c.tst(M(1,6),"w")
    c.branch(6,"exit")
    c.alu("add",D(4),0)
    c.move(D(0),A(2))              # target RGB24 start (read-only)

    # Private indexed AGA Intuition screen and ColorMap as in R32 Apply.
    c.move(M(5,STATE_PTR),A(0))
    c.move(A(0),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.move(M(0,0),A(1))
    c.move(A(1),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.tst(M(0,8))
    c.branch(7,"exit")
    c.move(M(0,28),D(0))
    c.tst(D(0))
    c.branch(15,"exit")
    c.imm("cmp",8,D(0))
    c.branch(2,"exit")
    c.move(M(0,24),D(0))
    c.imm("and",UNSUPPORTED_MODE,D(0))
    c.branch(6,"exit")
    c.move(M(0,20),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(0))
    c.branch(2,"exit")
    c.alu("cmp",D(0),7)
    c.branch(2,"exit")
    c.move(M(1,48),A(1))           # Screen.ViewPort.ColorMap
    c.move(A(1),D(0))
    c.tst(D(0))
    c.branch(7,"exit")
    c.move(I(0),D(0))
    c.move(M(1,2),D(0),"w")
    c.tst(D(0))
    c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(0))
    c.branch(2,"exit")
    c.alu("cmp",D(0),7)
    c.branch(2,"exit")

    # Allocate one public scratch block before the first VBL.
    c.move(M(7),D(6))              # saved vbl duration
    c.move(D(7),D(0))
    c.raw("c0fc002a")              # MULU.W #42,D0
    c.imm("add",8,D(0))            # full RGB32+snapshot+DDA slab
    c.move(I(1),D(1))              # MEMF_PUBLIC
    c.raw("2c780004")              # ExecBase
    c.call_os(LVO_ALLOCVEC)
    c.tst(D(0))
    c.branch(7,"exit")
    c.move(D(0),A(4))              # slab owner for FreeVec

    # A single VBL requires only the final exact target, no GetRGB32/DIVS.
    c.imm("cmp",1,D(6))
    c.branch(7,"frames_setup")

    # Source snapshot from GetRGB32 into slab+8+12*N.
    c.move(D(7),D(0))
    c.raw("c0fc000c")              # MULU.W #12,D0
    c.imm("add",8,D(0))
    c.move(A(4),D(1))
    c.alu("add",D(1),0)
    c.move(D(0),A(1))
    c.move(M(5,STATE_PTR),A(0))
    c.move(M(0,0),A(0))
    c.move(M(0,48),A(0))           # ColorMap*
    c.move(I(0),D(0))              # first pen 0
    c.move(D(7),D(1))
    c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6))            # graphics.library base
    c.call_os(LVO_GETRGB32)

    # A0 = source RGB32; A1 = (accum LONG, step WORD)*3*N
    c.move(D(7),D(0))
    c.raw("c0fc000c")
    c.imm("add",8,D(0))
    c.move(A(4),D(1))
    c.alu("add",D(1),0)
    c.move(D(0),A(0))
    c.move(D(7),D(0))
    c.raw("c0fc0018")              # MULU.W #24,D0
    c.imm("add",8,D(0))
    c.move(A(4),D(1))
    c.alu("add",D(1),0)
    c.move(D(0),A(1))
    c.move(D(7),D(5))
    c.raw("cafc0003")              # MULU.W #3,D5
    c.label("component_init")
    c.move(I(0),D(0))
    c.move(POST(0),D(0),"b")      # high byte of source RGB32
    c.quick(3,A(0))               # next source RGB32 component
    c.shift(0,8,left=True)
    c.move(D(0),POST(1))          # 8.8 accumulator as LONG
    c.move(I(0),D(1))
    c.move(POST(2),D(1),"b")      # exact target byte
    c.shift(1,8,left=True)
    c.alu("sub",D(0),1)            # signed (target-start)*256
    c.raw("83c6")                  # DIVS.W D6,D1 ; n>=2 => fits WORD
    c.move(D(1),POST(1),"w")      # signed 8.8 step
    c.quick(1,D(5),sub=True)
    c.branch(6,"component_init")
    # Restore target A2 to the first RGB24 component (init advanced it).
    c.move(D(7),D(0))
    c.raw("c0fc0003")              # MULU.W #3,D0
    c.move(A(2),D(1))
    c.alu("sub",D(0),1)
    c.move(D(1),A(2))

    c.label("frames_setup")
    c.move(D(6),D(4))              # remaining explicit VBL waits
    c.label("frame_loop")
    c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6))
    c.call_os(LVO_WAITTOF)

    # Table header: (colorCount WORD <<16) | firstPen=0.
    c.move(A(4),A(1))
    c.move(D(7),D(0))
    c.raw("4840")                  # SWAP D0: color count high WORD
    c.move(D(0),POST(1))
    c.imm("cmp",1,D(4))
    c.branch(7,"exact_frame")

    # Intermediate frame: for 3*N components, accum += signed step.
    c.move(D(7),D(0))
    c.raw("c0fc0018")
    c.imm("add",8,D(0))
    c.move(A(4),D(1))
    c.alu("add",D(1),0)
    c.move(D(0),A(0))              # DDA states
    c.move(D(7),D(5))
    c.raw("cafc0003")
    c.move(A(4),A(1))
    c.quick(4,A(1))               # table color components start
    c.label("component_step")
    c.move(M(0),D(0))             # accumulator LONG
    c.move(I(0),D(1))
    c.move(M(0,4),D(1),"w")       # signed delta WORD
    c.raw("48c1")                  # EXT.L D1
    c.alu("add",D(1),0)
    c.move(D(0),M(0))             # write only scratch
    c.quick(6,A(0))
    c.shift(0,8)                  # byte in low word
    expand_rgb(c)
    c.quick(1,D(5),sub=True)
    c.branch(6,"component_step")
    c.branch(0,"load_frame")

    c.label("exact_frame")
    c.move(A(2),A(0))             # original AGAPAL slot RGB24
    c.move(D(7),D(5))
    c.raw("cafc0003")
    c.label("component_exact")
    c.move(I(0),D(0))
    c.move(POST(0),D(0),"b")
    expand_rgb(c)
    c.quick(1,D(5),sub=True)
    c.branch(6,"component_exact")

    c.label("load_frame")
    c.move(I(0),M(1))             # zero LONG terminator
    c.move(M(5,STATE_PTR),A(0))
    c.move(M(0),A(0))             # Screen*
    c.move(A(0),D(0))
    c.imm("add",44,D(0))
    c.move(D(0),A(0))             # ViewPort*
    c.move(A(4),A(1))             # table*
    c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6))
    c.call_os(LVO_LOADRGB32)
    c.quick(1,D(4),sub=True)
    c.branch(6,"frame_loop")

    # Finished: free scratch, return 1. No failure operations after first VBL.
    c.move(A(4),A(1))
    c.raw("2c780004")              # ExecBase
    c.call_os(LVO_FREEVEC)
    c.move(I(1),D(3))
    c.label("exit")
    c.quick(4,A(7))               # discard saved duration on ALL paths
    c.raw("4cdf77f7")              # AMOS ABI restore
    c.raw("74004e75")              # D2=integer result; RTS
    return c.out(),c.labels
