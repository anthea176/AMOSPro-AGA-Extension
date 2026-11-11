"""R29 0.10.1: export the active indexed AGA ColorMap as IFF FORM ILBM.

Proposed/approved AMOS API: _OK=Aga Palette Save(filename$).
Writes BMHD(20) and CMAP(3*N + optional zero pad), NO BODY/pixel data.
The file is created with DOS MODE_NEWFILE (overwrite enabled).
Reads all colors in a single graphics.library/GetRGB32 call, then emits
RGB8 triplets from the high bytes of its RGB32 table. No Chip RAM needed.

Context is 128 stack bytes. Buffers use AllocVec(MEMF_PUBLIC|MEMF_CLEAR)
and are freed even on error. A partial file is deleted after write/close
failure. No persistent bank and no new Fade functionality in R29.
"""
from m68k_emit import Code, D, A, M, POST, I
from build_m5_generic import begin, end, invoke, fail_if, ctx

STATE, STR, CSTR, DOS, FH, SCREEN, COLORMAP, NC, W, H, DEPTH, BYTES, TOTAL, BUF, RGBPTR, FILE_OPENED, SUCCESS = range(0, 68, 4)
CONTEXT_SIZE=128
STATE_PTR=456
MAX_COLORS=256
MODE_UNSUPPORTED=0x0c80  # EHB, HAM, DUALPF

def validate_screen(c):
    """Check a private indexed screen, dimensions and accessible ColorMap."""
    begin(c,"validate_screen")
    c.move(ctx(STATE),A(2))
    c.move(A(2),D(0)); c.tst(D(0)); fail_if(c,7)
    c.move(M(2,0),D(0)); c.tst(D(0)); fail_if(c,7)
    c.move(D(0),ctx(SCREEN))
    c.tst(M(2,8)); fail_if(c,7) # graphics.library base
    c.move(M(2,28),D(0)); c.tst(D(0)); fail_if(c,7)
    c.imm("cmp",8,D(0)); fail_if(c,2)
    c.move(D(0),ctx(DEPTH))
    c.move(M(2,24),D(0)); c.imm("and",MODE_UNSUPPORTED,D(0)); fail_if(c,6)
    for field,off in ((W,12),(H,16)):
        c.move(M(2,off),D(0)); c.tst(D(0)); fail_if(c,15)
        c.imm("cmp",32767,D(0)); fail_if(c,2)
        c.move(D(0),ctx(field))
    c.move(M(2,20),D(4)); c.tst(D(4)); fail_if(c,15)
    c.imm("cmp",MAX_COLORS,D(4)); fail_if(c,2)
    c.move(ctx(SCREEN),A(0))
    c.move(M(0,48),A(1))
    c.move(A(1),D(0)); c.tst(D(0)); fail_if(c,7)
    c.move(D(0),ctx(COLORMAP))
    c.move(I(0),D(0))
    c.move(M(1,2),D(0),"w")  # ColorMap.Count UWORD
    c.tst(D(0)); fail_if(c,7)
    c.imm("cmp",MAX_COLORS,D(0)); fail_if(c,2)
    c.alu("cmp",D(0),4)        # D4 = min(State.Colours, ColorMap.Count)
    c.branch(3,"count_ok")    # BLS unsigned
    c.move(D(0),D(4))
    c.label("count_ok")
    c.move(D(4),ctx(NC))
    end(c,"validate_screen")

def prepare_name(c):
    """Convert AMOS length-prefixed filename to allocated NUL-terminated path."""
    begin(c,"prepare_name")
    c.move(ctx(STR),A(2))
    c.move(A(2),D(0)); c.tst(D(0)); fail_if(c,7)
    c.move(I(0),D(4))
    c.move(POST(2),D(4),"w")
    c.tst(D(4)); fail_if(c,7)
    c.imm("cmp",255,D(4)); fail_if(c,2)
    c.move(D(4),D(0)); c.quick(1,D(0))
    c.move(I(0x10001),D(1))
    c.raw("2c780004"); c.call_os(-684) # Exec AllocVec(MEMF_PUBLIC|CLEAR)
    c.tst(D(0)); fail_if(c,7)
    c.move(D(0),ctx(CSTR)); c.move(D(0),A(1))
    c.label("name_loop")
    c.move(POST(2),POST(1),"b")
    c.quick(1,D(4),sub=True)
    c.branch(6,"name_loop")
    end(c,"prepare_name")

def prepare_data(c):
    """Build a complete, padded palette-only ILBM in one temporary allocation."""
    begin(c,"prepare_data")
    c.move(ctx(NC),D(4))
    c.move(D(4),D(0)); c.alu("add",D(4),0); c.alu("add",D(4),0)
    c.move(D(0),ctx(BYTES))            # 3*N bytes, no pad
    c.move(D(0),D(1)); c.imm("and",1,D(1))
    c.alu("add",D(1),0); c.imm("add",48,D(0))
    c.move(D(0),ctx(TOTAL))            # 48+3*N+pad bytes
    c.move(ctx(BYTES),D(1)); c.shift(1,2,left=True)
    c.alu("add",D(1),0)               # file bytes + 12*N RGB32 scratch
    c.move(I(0x10001),D(1))
    c.raw("2c780004"); c.call_os(-684)
    c.tst(D(0)); fail_if(c,7)
    c.move(D(0),ctx(BUF))
    c.move(D(0),D(1)); c.alu("add",ctx(TOTAL),1)
    c.move(D(1),ctx(RGBPTR))
    # IFF header (all unused BMHD fields and CMAP odd pad are cleared)
    c.move(ctx(BUF),A(0))
    for off,val in ((0,0x464f524d),(8,0x494c424d),(12,0x424d4844),
                    (16,20),(40,0x434d4150)):
        c.move(I(val),M(0,off))
    c.move(ctx(TOTAL),D(0)); c.imm("sub",8,D(0)); c.move(D(0),M(0,4))
    for field,off1,off2 in ((W,20,36),(H,22,38)):
        c.move(ctx(field),D(0))
        c.move(D(0),M(0,off1),"w")
        c.move(D(0),M(0,off2),"w")
    c.move(ctx(DEPTH),D(0)); c.move(D(0),M(0,28),"b")
    c.move(I(0x0101,"w"),M(0,34),"w") # xAspect=1, yAspect=1
    c.move(ctx(BYTES),M(0,44))
    # RGB32 read from the private screen's ColorMap, never from a bitmap.
    c.move(ctx(COLORMAP),A(0))
    c.move(I(0),D(0)); c.move(ctx(NC),D(1))
    c.move(ctx(RGBPTR),A(1))
    c.move(ctx(STATE),A(2)); c.move(M(2,8),A(6))
    c.call_os(-900)                  # graphics.library/GetRGB32
    # Pack only the most significant byte of each RGB32 LONG.
    c.move(ctx(RGBPTR),A(0))
    c.move(ctx(BUF),D(0)); c.imm("add",48,D(0)); c.move(D(0),A(1))
    c.move(ctx(NC),D(4))
    c.label("rgb_loop")
    for _ in range(3):
        c.move(M(0),POST(1),"b")
        c.quick(4,A(0))
    c.quick(1,D(4),sub=True)
    c.branch(6,"rgb_loop")
    end(c,"prepare_data")

def write_iff(c):
    """Create/overwrite and write exactly the IFF length. Verify Close()."""
    begin(c,"write_iff")
    c.lea(1,"dosname")
    c.raw("2c780004"); c.call_os(-552) # Exec OpenLibrary
    c.tst(D(0)); fail_if(c,7)
    c.move(D(0),ctx(DOS)); c.move(D(0),A(6))
    c.move(ctx(CSTR),D(1))
    c.move(I(1006),D(2))             # MODE_NEWFILE: overwrite existing file
    c.call_os(-30)
    c.tst(D(0)); fail_if(c,7)
    c.move(D(0),ctx(FH)); c.move(I(1),ctx(FILE_OPENED))
    c.move(D(0),D(1))
    c.move(ctx(BUF),D(2)); c.move(ctx(TOTAL),D(3))
    c.call_os(-48)                   # DOS Write(fh,buffer,total)
    c.alu("cmp",ctx(TOTAL),0)
    fail_if(c,6)                     # short or failed writes rejected
    c.move(ctx(FH),D(1))
    c.move(ctx(DOS),A(6)); c.call_os(-36) # DOS Close may detect buffered error
    c.move(D(0),D(4))
    c.move(I(0),ctx(FH))             # handle is invalid even when Close fails
    c.tst(D(4)); fail_if(c,7)
    c.move(I(1),ctx(SUCCESS))
    end(c,"write_iff")

def cleanup_save(c):
    """Free every allocation, close open handles and remove partial files."""
    begin(c,"cleanup_save")
    c.tst(ctx(FH)); c.branch(7,"no_file")
    c.move(ctx(DOS),A(6))
    c.move(ctx(FH),D(1)); c.call_os(-36)
    c.label("no_file")
    c.tst(ctx(FILE_OPENED)); c.branch(7,"no_delete")
    c.tst(ctx(SUCCESS)); c.branch(6,"no_delete")
    c.move(ctx(DOS),A(6))
    c.move(ctx(CSTR),D(1)); c.call_os(-72) # DeleteFile partial output
    c.label("no_delete")
    for off,tag in ((BUF,"buf"),(CSTR,"name")):
        c.tst(ctx(off)); c.branch(7,"no_"+tag)
        c.move(ctx(off),A(1)); c.raw("2c780004"); c.call_os(-690)
        c.label("no_"+tag)
    c.tst(ctx(DOS)); c.branch(7,"no_dos")
    c.move(ctx(DOS),A(1)); c.raw("2c780004"); c.call_os(-414)
    c.label("no_dos")
    end(c,"cleanup_save")

def emit_save():
    """AMOS D3=filename$ descriptor; result D3=1/0, D2=0, A3 unchanged."""
    c=Code()
    c.raw("48e7effe")              # R28-compatible non-result register mask
    c.move(M(5,STATE_PTR),A(0))
    c.move(D(3),A(1))
    c.raw("4fefff80")              # LEA -128(SP),SP
    c.move(A(7),A(5))
    for off in range(0,CONTEXT_SIZE,4):
        c.move(I(0),ctx(off))
    c.move(A(0),ctx(STATE)); c.move(A(1),ctx(STR))
    invoke(c,"validate_screen")
    invoke(c,"prepare_name")
    invoke(c,"prepare_data")
    invoke(c,"write_iff")
    c.move(I(1),D(3)); c.branch(0,"done")
    c.label("failure"); c.move(I(0),D(3))
    c.label("done")
    c.branch(1,"cleanup_save")
    c.raw("4fef00804cdf7ff774004e75") # restore SP/registers; D2=0; RTS
    validate_screen(c)
    prepare_name(c)
    prepare_data(c)
    write_iff(c)
    cleanup_save(c)
    c.label("dosname"); c.b.extend(b"dos.library\0")
    if len(c.b)&1:c.b.append(0)
    return c.out(),c.labels
