"""M13/R28 (0.10.0): 68000 AGA palette primitives for a private Intuition screen.

Aga Palette Load(filename$) -> 1/0: read ILBM CMAP, apply only palette.
Aga Palette Set(pen,r,g,b) -> 1/0: 8-bit RGB for one indexed pen.
Aga Palette Get(pen) -> packed $00RRGGBB, or -1 for invalid state.

All commands operate on screen.ViewPort.ColorMap, never AMOS's own
Screen, custom-chip registers or the bitmap. HAM/EHB/DUALPF excluded
from this first indexed-colour contract. No persistent memory.
"""
from m68k_emit import Code, D, A, M, POST, I
from build_m5_generic import (
    STATE, STR, FORM, SIZE, CMAP, NC, SCREEN, CONTEXT_SIZE,
    ctx, begin, end, invoke, fail_if, read_file,
    prepare_palette, palette, cleanup,
)

STATE_PTR=456       # (AMOSBase A5)+$01C8 -> extension State
LVO_LOADRGB32=-882
LVO_GETRGB32=-900
GETP=b"GetP"
MAX_COLORS=256
MODE_UNSUPPORTED=0x0c80 # EHB (0x80), dualPF (0x400), HAM (0x800)
STACK_RGB5=20
STACK_RGB3=12

def _validate_viewport(c, pen_reg=None, num_reg=None):
    """Emit common private-screen and v39 ColorMap checks.

    Return with A2=State, A0=ViewPort, A1=ColorMap, A6=GfxBase;
    D0,D1 scratch, preserve incoming D3/D4-D7.
    The lookup checks colormap->Count at offset 2, not its RGB arrays.
    """
    c.move(M(5,STATE_PTR),A(2))
    c.move(A(2),D(0)); c.tst(D(0)); c.branch(7,"bad")
    c.move(M(2,0),D(0)); c.tst(D(0)); c.branch(7,"bad")
    c.move(M(2,8),D(0)); c.tst(D(0)); c.branch(7,"bad")
    c.move(M(2,28),D(0)); c.tst(D(0)); c.branch(15,"bad")
    c.imm("cmp",8,D(0)); c.branch(14,"bad")
    c.move(M(2,24),D(0))
    c.imm("and",MODE_UNSUPPORTED,D(0))
    c.branch(6,"bad")
    c.move(M(2,0),A(0))   # private Intuition Screen
    c.move(M(0,48),A(1))  # &(Screen.ViewPort)+4 : ViewPort.ColorMap
    c.move(A(1),D(0)); c.tst(D(0)); c.branch(7,"bad")
    c.move(I(0),D(0))
    c.move(M(1,2),D(0),"w") # ColorMap.Count
    c.tst(D(0)); c.branch(7,"bad")
    c.imm("cmp",MAX_COLORS,D(0)); c.branch(2,"bad")
    if pen_reg is not None:
        c.tst(D(pen_reg)); c.branch(11,"bad")
        c.alu("cmp",D(0),pen_reg)
        c.branch(4,"bad")   # pen >= Count
        c.alu("cmp",M(2,20),pen_reg)
        c.branch(4,"bad")   # pen >= screen logical colors
    if num_reg is not None:
        c.tst(D(num_reg)); c.branch(15,"bad")
        c.alu("cmp",D(0),num_reg)
        c.branch(2,"bad")   # CMAP count > ColorMap.Count
        c.alu("cmp",M(2,20),num_reg)
        c.branch(2,"bad")
    c.move(M(2,8),A(6))   # GfxBase after all pointer checks
    c.move(A(0),D(0))
    c.imm("add",44,D(0))
    c.move(D(0),A(0))     # ViewPort A0

def _rgb32(c,reg,offset):
    """Convert 8-bit component to LoadRGB32 32-bit fraction."""
    c.move(D(reg),D(0))
    c.move(D(0),D(1))
    c.shift(0,8,left=True)
    c.alu("or",D(1),0)   # 0x0000RRRR
    c.move(D(0),D(1))
    c.raw("4840")       # SWAP D0 -> 0xRRRR0000
    c.alu("or",D(1),0)   # 0xRRRRRRRR
    c.move(D(0),M(7,offset))

def emit_set():
    """D3=blue, (A3)+ green, red, index. D3 result; D2=0."""
    c=Code()
    c.raw("48e7efee")              # same R26 non-result register mask
    c.move(D(3),D(7))             # blue
    c.move(POST(3),D(6))         # green
    c.move(POST(3),D(5))         # red
    c.move(POST(3),D(4))         # pen
    c.move(I(0),D(3))
    for reg in (4,5,6,7):
        c.imm("cmp",255,D(reg))
        c.branch(2,"bad")         # unsigned >255, includes negative
    _validate_viewport(c,pen_reg=4)
    # Single LoadRGB32 record, no WaitTOF: caller can animate each VBL.
    c.raw("4fefffec")             # LEA -20(SP),SP
    c.move(A(7),A(1))
    c.move(D(4),D(0))
    c.imm("add",0x10000,D(0))     # count=1, firstPen=index
    c.move(D(0),M(1))
    _rgb32(c,5,4)
    _rgb32(c,6,8)
    _rgb32(c,7,12)
    c.move(I(0),M(7,16))         # LoadRGB32 terminating count=0
    c.move(A(7),A(1))
    c.call_os(LVO_LOADRGB32)
    c.raw("4fef0014")
    c.move(I(1),D(3))
    c.label("bad")
    c.raw("4cdf77f7")
    c.raw("74004e75")             # D2=integer result; RTS
    return c.out(),c.labels

def emit_get():
    """D3=pen. Return high 8-bit fractions as packed 00RRGGBB or -1."""
    c=Code()
    c.raw("48e7efee")
    c.move(D(3),D(4))
    c.move(I(-1),D(3))           # valid pure black returns zero
    c.imm("cmp",255,D(4))
    c.branch(2,"bad")
    _validate_viewport(c,pen_reg=4)
    c.raw("4feffff4")             # LEA -12(SP),SP
    c.move(D(4),D(0))            # first colour
    c.move(I(1),D(1))            # number of colours
    c.move(A(7),A(1))            # RGB32 table
    c.move(M(0,4),A(0))          # ViewPort.ColorMap -> A0
    c.call_os(LVO_GETRGB32)
    c.move(M(7,0),D(5))
    c.move(M(7,4),D(6))
    c.move(M(7,8),D(7))
    c.shift(5,8)                 # red high byte -> bits 23:16
    c.shift(6,8);c.shift(6,8)    # green high byte -> bits 15:8
    c.shift(7,8);c.shift(7,8);c.shift(7,8) # blue high byte -> bits 7:0
    c.alu("or",D(6),5)
    c.alu("or",D(7),5)
    c.move(D(5),D(3))
    c.raw("4fef000c")             # discard table (unconditional once allocated)
    c.label("bad")
    c.raw("4cdf77f7")
    c.raw("74004e75")
    return c.out(),c.labels

def inspect_palette(c):
    """Scan FORM ILBM with bounded chunk arithmetic; only CMAP required.

    Unlike the bitmap decoder, no BMHD dimensions/depth/BODY are inspected:
    the palette may come from an ILBM of another resolution or depth.
    FORM length is checked by the common DOS read_file helper.
    """
    begin(c,"inspect")
    c.move(ctx(FORM),A(0))
    c.move(ctx(SIZE),D(7))
    c.imm("sub",12,D(7))
    c.move(A(0),D(0))
    c.imm("add",12,D(0))
    c.move(D(0),A(0))
    c.label("pal_scan")
    c.tst(D(7))
    c.branch(7,"pal_scan_done")
    c.imm("cmp",8,D(7))
    fail_if(c,5)                # fewer than 8 bytes for a chunk header
    c.move(POST(0),D(3))       # chunk ID
    c.move(POST(0),D(2))       # payload length
    c.quick(8,D(7),sub=True)
    c.alu("cmp",D(7),2)
    fail_if(c,2)               # payload extends beyond FORM
    c.move(D(2),D(1))
    c.imm("and",1,D(1))
    c.alu("add",D(2),1)        # padded physical bytes
    c.alu("cmp",D(7),1)
    fail_if(c,2)
    c.alu("sub",D(1),7)
    c.imm("cmp",0x434d4150,D(3)) # "CMAP"
    c.branch(6,"pal_advance")
    c.tst(ctx(CMAP))
    fail_if(c,6)                # duplicate CMAP
    c.move(A(0),ctx(CMAP))
    c.move(D(2),ctx(NC))
    c.label("pal_advance")
    c.move(A(0),D(0))
    c.alu("add",D(1),0)
    c.move(D(0),A(0))
    c.branch(0,"pal_scan")
    c.label("pal_scan_done")
    c.tst(ctx(CMAP))
    fail_if(c,7)
    c.move(ctx(NC),D(0))
    c.tst(D(0))
    fail_if(c,7)
    c.imm("cmp",768,D(0))
    fail_if(c,2)
    c.raw("80fc0003")          # DIVU.W #3,D0 (hi WORD = remainder)
    c.move(D(0),D(1))
    c.raw("4841")              # SWAP D1
    c.tst(D(1),"w")
    fail_if(c,6)
    c.imm("and",0xffff,D(0))
    c.move(D(0),ctx(NC))      # actual color count
    end(c,"inspect")

def check_palette_screen(c):
    """Before any palette memory allocation or writes: verify private screen."""
    begin(c,"validate_palette")
    c.move(ctx(STATE),A(2))
    c.move(A(2),D(0));c.tst(D(0));fail_if(c,7)
    c.move(M(2,0),D(0));c.tst(D(0));fail_if(c,7)
    c.move(D(0),ctx(SCREEN))
    c.move(M(2,8),D(0));c.tst(D(0));fail_if(c,7)
    c.move(M(2,28),D(0));c.tst(D(0));fail_if(c,15)
    c.imm("cmp",8,D(0));fail_if(c,14)
    c.move(M(2,24),D(0))
    c.imm("and",MODE_UNSUPPORTED,D(0))
    fail_if(c,6)
    c.move(ctx(SCREEN),A(0))
    c.move(M(0,48),A(1))
    c.move(A(1),D(0));c.tst(D(0));fail_if(c,7)
    c.move(I(0),D(0))
    c.move(M(1,2),D(0),"w")
    c.tst(D(0));fail_if(c,7)
    c.imm("cmp",MAX_COLORS,D(0));fail_if(c,2)
    c.alu("cmp",ctx(NC),0)    # Count - file entries
    fail_if(c,5)              # file entries > ColorMap.Count
    c.move(M(2,20),D(0))
    c.alu("cmp",ctx(NC),0)
    fail_if(c,5)
    end(c,"validate_palette")

def emit_load():
    """D3=AMOS string descriptor filename, no remaining (A3)+ args."""
    c=Code()
    c.raw("48e7effe")              # proven M5 ILBM return/stack ABI
    c.move(M(5,STATE_PTR),A(0))
    c.move(D(3),A(1))
    c.raw("4fefff80")             # context 128 bytes on hardware SP
    c.move(A(7),A(5))
    for off in range(0,CONTEXT_SIZE,4):
        c.move(I(0),ctx(off))
    c.move(A(0),ctx(STATE))
    c.move(A(1),ctx(STR))
    invoke(c,"read_file")
    invoke(c,"inspect")
    invoke(c,"validate_palette")
    invoke(c,"prepare_palette")
    invoke(c,"palette")
    c.move(I(1),D(3))
    c.branch(0,"done")
    c.label("failure")
    c.move(I(0),D(3))
    c.label("done")
    c.branch(1,"cleanup")
    c.raw("4fef00804cdf7ff774004e75") # SP, MOVEM, D2=0, RTS
    read_file(c)
    inspect_palette(c)
    check_palette_screen(c)
    prepare_palette(c)
    palette(c)
    cleanup(c)
    c.label("dosname")
    c.b.extend(b"dos.library\0")
    if len(c.b)&1:c.b.append(0)
    return c.out(),c.labels
