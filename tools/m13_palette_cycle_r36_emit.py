"""R36 0.10.8 — single-call indexed AGA ColorMap RGB32 palette cycling.

Approved AMOS call: _OK=Aga Palette Cycle(First,Last,Direction).
AMOS numeric ABI: D3=Direction (+1/-1); (A3)+=Last; (A3)+=First.
One rotation per call; NO implicit WaitTOF and NO persistent task/state.
+1: colour of Last -> First, all others shift toward greater indices.
-1: colour of First -> Last, all others shift toward smaller indices.
Accept First>=0, Last>First and Last<logical pens and ColorMap.Count;
both First and Last must be within [0,255]. Reject invalid screen,
HAM/EHB/dual playfield, invalid ColorMap or allocation failure atomically.

Single Exec AllocVec(MEMF_PUBLIC) scratch of 8+12*N bytes, N=Last-
First+1 (2..256, at most 3080 bytes), with LoadRGB32 table header,
GetRGB32 exact RGB32 triplets and zero terminator. Rotate 3 LONG
components in the temporary slab using D4/D5/D6; one GetRGB32
and one LoadRGB32 per success, NO colour precision loss, no bank,
pixel, Copper, file, or unrelated pen changes. FreeVec after use.
D3 return integer 1 success or 0 failure, D2=0, rest ABI preserved.
No visual timing guarantee: caller controls VBL cadence (Aga Wait Vbl).
"""
from m68k_emit import Code,D,A,M,POST,PRE,I

ENTRY_CYCLE=47
BASE_ENTRIES=47
GETP=b"GetP"
STATE_PTR=456
UNSUPPORTED_MODE=0x0c80
MAX_COLORS=256
LVO_ALLOCVEC=-684
LVO_FREEVEC=-690
LVO_GETRGB32=-900
LVO_LOADRGB32=-882


def emit_cycle():
    c=Code()
    c.raw("48e7efee")                # R35-tested AMOS ABI MOVEM preservation
    c.move(D(3),PRE(7))              # saved direction on stack for all exits
    c.move(POST(3),D(5))             # Last
    c.move(POST(3),D(4))             # First
    c.move(I(0),D(3))                # failure default

    # Direction must be exactly +1 or -1, no 0 or arbitrary step.
    c.move(M(7),D(0))
    c.imm("cmp",1,D(0))
    c.branch(7,"valid_direction")
    c.imm("cmp",-1,D(0))
    c.branch(6,"exit")
    c.label("valid_direction")

    # unsigned validation also rejects all negative and overflowed values.
    c.imm("cmp",255,D(5))
    c.branch(2,"exit")               # Last > 255
    c.alu("cmp",D(5),4)
    c.branch(4,"exit")               # First >= Last (unsigned)

    # Validate private Intuition screen & colour map as in R35.
    c.move(M(5,STATE_PTR),A(0))
    c.move(A(0),D(0))
    c.tst(D(0));c.branch(7,"exit")
    c.move(M(0,0),A(1))              # Screen*
    c.move(A(1),D(0))
    c.tst(D(0));c.branch(7,"exit")
    c.tst(M(0,8));c.branch(7,"exit") # GfxBase
    c.move(M(0,28),D(0))
    c.tst(D(0));c.branch(15,"exit")  # depth <=0
    c.imm("cmp",8,D(0));c.branch(2,"exit")
    c.move(M(0,24),D(0))
    c.imm("and",UNSUPPORTED_MODE,D(0))
    c.branch(6,"exit")
    c.move(M(0,20),D(7))             # logical pen count
    c.tst(D(7));c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(7));c.branch(2,"exit")
    c.alu("cmp",D(7),5)
    c.branch(4,"exit")               # Last >= logical count
    c.move(M(1,48),A(1))             # ColorMap*
    c.move(A(1),D(0))
    c.tst(D(0));c.branch(7,"exit")
    c.move(I(0),D(0))
    c.move(M(1,2),D(0),"w")          # ColorMap.Count
    c.tst(D(0));c.branch(7,"exit")
    c.imm("cmp",MAX_COLORS,D(0));c.branch(2,"exit")
    c.alu("cmp",D(0),7)
    c.branch(2,"exit")               # ColorMap count < logical
    c.alu("cmp",D(0),5)
    c.branch(4,"exit")               # Last >= ColorMap.Count

    # N = Last - First + 1, guaranteed 2..256.
    c.move(D(5),D(7))
    c.alu("sub",D(4),7)
    c.quick(1,D(7))
    # Scratch header 4B + 12*N exact RGB32 bytes + 4B terminator.
    c.move(D(7),D(0))
    c.raw("c0fc000c")                # MULU.W #12,D0 (max 3072)
    c.imm("add",8,D(0))
    c.move(I(1),D(1))                # MEMF_PUBLIC, Fast RAM allowed
    c.raw("2c780004")                # ExecBase
    c.call_os(LVO_ALLOCVEC)
    c.tst(D(0));c.branch(7,"exit")
    c.move(D(0),A(4))                # scratch owner across graphics calls

    # Header = (N<<16) | First. GetRGB32 writes exact triplets at +4.
    c.move(D(7),D(0))
    c.raw("4840")                    # SWAP D0 -> count in high word
    c.alu("or",D(4),0)                # First in low word
    c.move(D(0),M(4))
    c.move(A(4),A(1))
    c.quick(4,A(1))
    c.move(M(5,STATE_PTR),A(0))
    c.move(M(0,0),A(0))
    c.move(M(0,48),A(0))             # ColorMap
    c.move(D(4),D(0))                # First
    c.move(D(7),D(1))                # count N
    c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6))              # GfxBase
    c.call_os(LVO_GETRGB32)          # exactly one read, before any write

    # A2 = terminator at scratch+4+N*12, also end of colour records.
    c.move(D(7),D(0))
    c.raw("c0fc000c")                # MULU.W #12,D0
    c.imm("add",4,D(0))
    c.move(A(4),D(1))
    c.alu("add",D(1),0)
    c.move(D(0),A(2))
    c.move(I(0),M(2))                # LoadRGB32 terminator
    c.move(M(7),D(0))                # saved Direction
    c.imm("cmp",1,D(0))
    c.branch(7,"forward")

    # -1: shift left. Save first RGB32 in D4,D5,D6 and copy next -> prev.
    c.label("backward")
    c.move(A(4),A(0))
    c.quick(4,A(0))                 # A0 = first record
    c.move(A(0),D(0))
    c.imm("add",12,D(0))
    c.move(D(0),A(1))                # A1 = second record
    c.move(M(0),D(4))
    c.move(M(0,4),D(5))
    c.move(M(0,8),D(6))
    c.quick(1,D(7),sub=True)         # N-1 records to shift
    c.label("backward_loop")
    c.move(M(1),M(0))
    c.move(M(1,4),M(0,4))
    c.move(M(1,8),M(0,8))
    c.move(A(1),A(0))                # advance destination
    c.move(A(1),D(0))
    c.imm("add",12,D(0))
    c.move(D(0),A(1))                # advance source
    c.quick(1,D(7),sub=True)
    c.branch(6,"backward_loop")
    c.move(D(4),M(0))                # original first to last
    c.move(D(5),M(0,4))
    c.move(D(6),M(0,8))
    c.branch(0,"apply")

    # +1: shift right. Save last RGB32 in D4,D5,D6 and copy prev -> next.
    c.label("forward")
    c.move(A(2),D(0))
    c.imm("sub",12,D(0))
    c.move(D(0),A(1))                # A1 = last record
    c.move(M(1),D(4))
    c.move(M(1,4),D(5))
    c.move(M(1,8),D(6))
    c.quick(1,D(7),sub=True)
    c.label("forward_loop")
    c.move(A(1),D(0))
    c.imm("sub",12,D(0))
    c.move(D(0),A(0))                # A0 = previous record
    c.move(M(0),M(1))
    c.move(M(0,4),M(1,4))
    c.move(M(0,8),M(1,8))
    c.move(A(0),A(1))
    c.quick(1,D(7),sub=True)
    c.branch(6,"forward_loop")
    c.move(D(4),M(1))                # original last to first
    c.move(D(5),M(1,4))
    c.move(D(6),M(1,8))

    c.label("apply")
    # Exactly one LoadRGB32 on the *private* ViewPort; no implicit WaitTOF.
    c.move(M(5,STATE_PTR),A(0))
    c.move(M(0,0),A(0))              # Screen*
    c.move(A(0),D(0))
    c.imm("add",44,D(0))
    c.move(D(0),A(0))                # &Screen.ViewPort
    c.move(A(4),A(1))                # table of exact RGB32 longs
    c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6))
    c.call_os(LVO_LOADRGB32)
    c.move(A(4),A(1))
    c.raw("2c780004")                # ExecBase
    c.call_os(LVO_FREEVEC)
    c.move(I(1),D(3))

    c.label("exit")
    c.quick(4,A(7))                 # discard saved direction
    c.raw("4cdf77f7")                # restore R35 ABI (except result D3)
    c.raw("74004e75")                # D2=integer result; RTS
    return c.out(),c.labels
