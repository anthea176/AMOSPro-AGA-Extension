"""R34 0.10.6. Blocking indexed RGB24 Fade To Black.

API: _OK=Aga Fade To Black(vbl), vbl 1..255, D3 in/out, D2=0.
No A3 operands, no AGAPAL bank dependency or pixel writes. Input
ColorMap is captured once with GetRGB32 (N>1); R33's common helper
replicates 8-bit RGB into RGB32 fractions for LoadRGB32. Signed 8.8
DDA interpolates each channel toward black across one WaitTOF and one
LoadRGB32 per requested VBL. Final VBL forces exactly 0x00000000.
One AllocVec public scratch block 8+42*pens (max 10760 bytes)
holds LoadRGB32 table, source snapshot, and component DDA states.
All validation and allocation precede first VBL. Unsupported HAM,
EHB, dual PF, closed screens, invalid logical/ColorMap counts,
durations 0, negatives or >255 fail without screen changes.
VBL waits alone do not guarantee a strict elapsed duration on 68000.
"""
from m68k_emit import Code,D,A,M,POST,PRE,I
from m13_agapal_fade_r33_emit import expand_rgb

ENTRY_BLACK=45
BASE_ENTRIES=45
GETP=b"GetP"
MAX_COLORS=256
STATE_PTR=456
UNSUPPORTED_MODE=0x0c80
LVO_ALLOCVEC=-684
LVO_FREEVEC=-690
LVO_GETRGB32=-900
LVO_LOADRGB32=-882
LVO_WAITTOF=-270

def emit_black():
    c=Code()
    c.raw("48e7efee")              # R33 MOVEM register contract
    c.move(D(3),PRE(7))            # save duration for all exit paths
    c.move(I(0),D(3))              # failure by default
    c.move(M(7),D(0))
    c.tst(D(0))
    c.branch(7,"exit")             # vbl=0 rejected
    c.imm("cmp",255,D(0))
    c.branch(2,"exit")             # >255, negatives rejected

    # Private indexed screen and ColorMap, same checks as R33.
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
    c.move(M(0,20),D(7))          # all logical indexed pens
    c.tst(D(7))
    c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(7))
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

    # One VBL: skip GetRGB32/DIVS, black exact.
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

    # A0 = captured RGB32; A1 = (accum LONG, step WORD)*3*N
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
    c.move(POST(0),D(0),"b")      # first byte (0..255) of source RGB32
    c.quick(3,A(0))               # next RGB32 component
    c.shift(0,8,left=True)
    c.move(D(0),POST(1))          # DDA accumulator source*256 (LONG)
    c.move(D(0),D(1))
    c.move(I(0),D(0))
    c.alu("sub",D(1),0)            # black target: negative delta
    c.raw("81c6")                 # DIVS.W D6,D0; duration>=2
    c.move(D(0),POST(1),"w")      # truncated signed 8.8 step
    c.quick(1,D(5),sub=True)
    c.branch(6,"component_init")

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
    # Final frame is an exact black RGB32 table regardless of rounding.
    c.move(D(7),D(5))
    c.raw("cafc0003")              # MULU.W #3,D5
    c.label("component_exact")
    c.move(I(0),POST(1))          # zero LONG component to (A1)+
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

    # Free scratch; return 1. No fallible operations after first VBL.
    c.move(A(4),A(1))
    c.raw("2c780004")              # ExecBase
    c.call_os(LVO_FREEVEC)
    c.move(I(1),D(3))
    c.label("exit")
    c.quick(4,A(7))               # discard saved duration on ALL paths
    c.raw("4cdf77f7")              # AMOS ABI restore
    c.raw("74004e75")              # D2=integer result; RTS
    return c.out(),c.labels
