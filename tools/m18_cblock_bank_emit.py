"""M18/R68 CBlock RAW temporary Chip bank, CPU8 / CPU16 / BLIT8.

PROVISIONAL UNTIL GATE A: new API explicit Method:
 Capture(Bank,X,Y,Width,Height,Method), Draw(Bank,X,Y,Method),
 Restore(Bank,Method). Method 0=CPU8, 1=CPU16, 2=Blitter.
No AMOS Compiler invocation. One AMOS-owned DATA bank, no RLE, no Fast DMA.

All 68000 wrappers own argument checks, bank collision/Chip checks,
inactive private back buffer, Safe/WaitBlit, and one standalone P0 core
embedded as BSR.W target. No persistent pointers between calls.
"""
from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr
from m18_cblock_copy_emit import emit_cblock_copy_core

ENTRY_CAPTURE=67
ENTRY_DRAW=68
ENTRY_RESTORE=69
STATE_PTR=0x1c8
LVO_TYPEOFMEM=-534
LVO_GETMSG=-372
LVO_WAITBLIT=-228
MEMF_CHIP=2
NAME=b"AGACBLK "
MAGIC=b"AGACBLK1"
HEADER=40
MAX_SIZE=1048576
FRAME=384
TEMP_BITMAP=256
GETADR=rjsr(main_index("Bnk.GetAdr"))
RESERVE=rjsr(main_index("Bnk.Reserve"))
CHANGE=rjsr(main_index("Bnk.Change"))
EFF=rjsr(main_index("Bnk.Eff"))
F=dict(method=0,h=4,w=8,y=12,x=16,bank=20,base=24,length=28,
       state=32,db=36,backbm=40,gfx=44,scrw=48,scrh=52,depth=56,
       rowstride=60,plane_bytes=64,total=68,newbank=72,
       bmstride=76,first=80,last=84)

def emit_cblock_bank_action(action):
    if action not in ("capture","draw","restore"):
        raise ValueError("invalid action")
    c=Code();B,L=c.branch,c.label
    def get(k,reg):c.move(M(2,F[k]),reg)
    def put(reg,k):c.move(reg,M(2,F[k]))
    def call(mark):c.raw(mark.hex())
    def ull(a,off,reg):
        c.move(I(0),reg);c.move(M(a,off),reg,"w")
    def check_chip(reg):
        c.move(reg,A(1))
        c.raw("2c780004") # A6=ExecBase; call TypeOfMem(A1)
        c.call_os(LVO_TYPEOFMEM)
        c.imm("and",MEMF_CHIP,D(0));B(7,"reject")
    def check_add(reg,src):
        c.alu("add",src,reg);B(5,"reject")
    def check_limits():
        for key in ("w","h"):
            get(key,D(0));c.tst(D(0));B(15,"reject")
            c.imm("cmp",4096,D(0));B(2,"reject")
        for key in ("x","y"):
            get(key,D(0));c.tst(D(0));B(11,"reject")
            c.imm("cmp",32767,D(0));B(2,"reject")
        get("method",D(1));c.imm("cmp",1,D(1));B(7,"word_align")
        c.move(I(7),D(1));B(0,"align_ready")
        L("word_align");c.move(I(15),D(1))
        L("align_ready")
        for key in ("x","w"):
            get(key,D(0));c.alu("and",D(1),0);B(6,"reject")
        # All rectangles fully inside the LOGICAL screen, no clipping.
        for key,ext,limit in (("x","w","scrw"),("y","h","scrh")):
            get(key,D(0));get(ext,D(1));check_add(0,D(1))
            c.alu("cmp",M(2,F[limit]),0);B(2,"reject")
    def layout():
        get("w",D(0));c.imm("add",15,D(0));B(5,"reject")
        c.shift(0,4);c.shift(0,1,left=True)
        put(D(0),"rowstride")
        get("h",D(1));c.word(0xc0c1)  # MULU.W D1,D0, up to 2MiB
        put(D(0),"plane_bytes")
        get("depth",D(5));c.move(I(HEADER),D(0))
        L("layout_loop")
        get("plane_bytes",D(1));check_add(0,D(1))
        c.quick(1,D(5),sub=True);B(6,"layout_loop")
        c.imm("cmp",MAX_SIZE,D(0));B(2,"reject")
        put(D(0),"total")
    def verify_bank():
        # Bnk.GetAdr bank base returned in A0; never dereference before Chip.
        get("base",D(5));c.imm("cmp",24,D(5));B(3,"reject")
        c.move(D(5),D(0));c.imm("and",1,D(0));B(6,"reject")
        check_chip(D(5))
        get("base",D(0));c.imm("sub",24,D(0));check_chip(D(0))
        get("base",A(0))
        c.move(M(0,-20),D(4));c.imm("cmp",HEADER+16,D(4));B(5,"reject")
        c.imm("sub",16,D(4));c.imm("cmp",MAX_SIZE,D(4));B(2,"reject")
        put(D(4),"length")
        get("base",D(0));check_add(0,D(4));c.quick(1,D(0),sub=True)
        check_chip(D(0))
        get("base",A(0))
        c.move(M(0,-16),D(0));get("bank",D(1));c.alu("cmp",D(1),0);B(6,"reject")
        ull(0,-12,D(0));c.tst(D(0));B(7,"bank_flags_ok")
        c.imm("and",0xfffd,D(0),"w");c.imm("cmp",1,D(0),"w");B(6,"reject")
        L("bank_flags_ok")
        for off,chunk in ((-8,NAME[:4]),(-4,NAME[4:]),
                          (0,MAGIC[:4]),(4,MAGIC[4:])):
            c.move(M(0,off),D(0));c.imm("cmp",int.from_bytes(chunk,"big"),D(0))
            B(6,"reject")
        for off,val in ((8,HEADER),(10,1),(14,0)):
            ull(0,off,D(0));c.imm("cmp",val,D(0));B(6,"reject")
        ull(0,12,D(0));c.alu("cmp",M(2,F["depth"]),0);B(6,"reject")
        for off,key in ((24,"w"),(28,"h"),(32,"rowstride"),(36,"plane_bytes")):
            get("base",A(0));c.move(M(0,off),D(0))
            c.alu("cmp",M(2,F[key]),0);B(6,"reject")
        get("length",D(0));c.alu("cmp",M(2,F["total"]),0);B(6,"reject")

    # Standard AMOS save D0,D1,D4-D7,A0-A2,A4-A6; A3 is the parameter stack.
    c.raw("48e7efee")
    c.raw("4feffe80")  # LEA -384(SP),SP
    c.move(A(7),A(2))
    put(D(3),"method")
    c.move(I(0),M(2,F["newbank"]))
    if action=="capture":
        order=("h","w","y","x","bank")
    elif action=="draw":
        order=("y","x","bank")
    else:
        order=("bank",)
    for k in order:
        c.move(POST(3),D(7));put(D(7),k)
    c.move(I(0),D(3))
    get("method",D(0));c.tst(D(0));B(11,"reject")
    c.imm("cmp",2,D(0));B(2,"reject")
    get("bank",D(0));c.imm("cmp",5,D(0));B(5,"reject")
    c.imm("cmp",65535,D(0));B(2,"reject")

    # Private AGA state and INACTIVE back bitmap, not AMOS/Workbench.
    c.move(M(5,STATE_PTR),A(4));c.move(A(4),D(0))
    c.tst(D(0));B(7,"reject");put(A(4),"state")
    for off in (0,8,32):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,"reject")
    c.move(M(4,8),D(0));put(D(0),"gfx")
    for off,key in ((12,"scrw"),(16,"scrh")):
        c.move(M(4,off),D(0));c.tst(D(0));B(15,"reject")
        c.imm("cmp",4096,D(0));B(2,"reject")
        put(D(0),key)
    c.move(M(4,28),D(0))
    c.tst(D(0));B(15,"reject")
    c.imm("cmp",8,D(0));B(2,"reject");put(D(0),"depth")
    c.move(M(4,32),A(4));put(A(4),"db")
    c.move(M(4,8),D(0));c.tst(D(0));B(7,"front_zero")
    c.imm("cmp",1,D(0));B(6,"reject")
    get("db",A(4));c.move(M(4),A(1));B(0,"selected_sb")
    L("front_zero")
    get("db",A(4));c.move(M(4,4),A(1))
    L("selected_sb")
    c.move(A(1),D(0));c.tst(D(0));B(7,"reject")
    c.move(M(1),A(0));c.move(A(0),D(0));c.tst(D(0));B(7,"reject")
    put(A(0),"backbm")
    ull(0,0,D(0));c.tst(D(0));B(15,"reject")
    c.move(D(0),D(1));c.imm("and",1,D(1));B(6,"reject")
    put(D(0),"bmstride");c.shift(0,3,left=True)
    c.alu("cmp",M(2,F["scrw"]),0);B(5,"reject")
    ull(0,2,D(0));c.alu("cmp",M(2,F["scrh"]),0);B(5,"reject")
    c.move(I(0),D(0));c.move(M(0,5),D(0),"b")
    c.alu("cmp",M(2,F["depth"]),0);B(6,"reject")

    # For drawing, inspect existing block before geometry; Capture already
    # receives a fresh rectangle and might need to create the bank.
    if action!="capture":
        get("bank",D(0));call(GETADR);put(A(0),"base")
        get("base",D(0));c.tst(D(0));B(7,"reject")
        check_chip(D(0))
        get("base",D(0));c.imm("add",39,D(0));B(5,"reject")
        check_chip(D(0))
        get("base",A(0))
        for off,key in ((24,"w"),(28,"h")):
            c.move(M(0,off),D(0));put(D(0),key)
        if action=="restore":
            c.move(M(0,16),D(0));put(D(0),"x")
            c.move(M(0,20),D(0));put(D(0),"y")
    check_limits()
    layout()
    if action=="capture":
        get("bank",D(0));call(GETADR)
        put(A(0),"base")
        get("base",D(0));c.tst(D(0));B(6,"existing_bank")
        # Second collision guard: Bnk.Reserve may erase if number occupied.
        get("bank",D(0));call(GETADR)
        c.move(A(0),D(0));c.tst(D(0));B(6,"reject")
        get("bank",D(0));c.move(I(3),D(1))
        get("total",D(2));c.lea(0,"bank_name")
        call(RESERVE)
        c.tst(D(0));B(7,"reject")
        put(D(0),"base")
        c.move(I(1),M(2,F["newbank"]))
        get("base",D(0));c.imm("cmp",24,D(0));B(3,"reject")
        c.move(D(0),D(1));c.imm("and",1,D(1));B(6,"reject")
        check_chip(D(0))
        get("base",D(0));c.imm("sub",24,D(0));check_chip(D(0))
        get("base",D(0));get("total",D(1));check_add(0,D(1))
        c.quick(1,D(0),sub=True);check_chip(D(0))
        # Set the complete canonical header (no valid new bank until done).
        get("base",A(0))
        c.move(I(int.from_bytes(MAGIC[:4],"big")),POST(0))
        c.move(I(int.from_bytes(MAGIC[4:],"big")),POST(0))
        c.move(I(HEADER,"w"),POST(0),"w")
        c.move(I(1,"w"),POST(0),"w")
        get("depth",D(0));c.move(D(0),POST(0),"w")
        c.move(I(0,"w"),POST(0),"w")
        get("x",D(0));c.move(D(0),POST(0))
        get("y",D(0));c.move(D(0),POST(0))
        for key in ("w","h","rowstride","plane_bytes"):
            get(key,D(0));c.move(D(0),POST(0))
        B(0,"bank_ready")
        L("existing_bank")
        verify_bank()
        L("bank_ready")
    else:
        verify_bank()

    # Check actual Chip allocations of all screen planes at FIRST/LAST
    # accessed bytes, using logical clip and physical BitMap pitch.
    get("y",D(0));get("bmstride",D(1));c.word(0xc0c1)
    get("x",D(1));c.shift(1,3);check_add(0,D(1));put(D(0),"first")
    get("y",D(0));get("h",D(1));check_add(0,D(1))
    c.quick(1,D(0),sub=True);get("bmstride",D(1));c.word(0xc0c1)
    get("x",D(1));get("w",D(4));check_add(1,D(4))
    c.quick(1,D(1),sub=True);c.shift(1,3)
    check_add(0,D(1));put(D(0),"last")
    get("backbm",A(4));c.quick(8,A(4))
    get("depth",D(5))
    L("check_planes")
    c.move(POST(4),D(7));c.tst(D(7));B(7,"reject")
    c.imm("cmp",-1,D(7));B(6,"reject")
    c.move(D(7),D(0));c.imm("and",1,D(0));B(6,"reject")
    get("first",D(0));check_add(0,D(7));check_chip(D(0))
    get("last",D(0));check_add(0,D(7));check_chip(D(0))
    c.quick(1,D(5),sub=True);B(6,"check_planes")

    # Temp BitMap lives on the wrapper's own stack, points into the
    # SINGLE AMOS-owned, physical-Chip AGACBLK bank. No separate cache.
    c.move(I(0),M(2,TEMP_BITMAP+4))  # Flags=0,Depth/pad set below
    for unused in range(8):
        c.move(I(0),M(2,TEMP_BITMAP+8+unused*4))
    get("rowstride",D(0));c.move(D(0),M(2,TEMP_BITMAP),"w")
    get("h",D(0));c.move(D(0),M(2,TEMP_BITMAP+2),"w")
    get("depth",D(0));c.move(D(0),M(2,TEMP_BITMAP+5),"b")
    c.raw("49ea0108")  # LEA 264(A2),A4 ; first Plane pointer
    get("base",D(6));c.imm("add",HEADER,D(6))
    get("plane_bytes",D(7));get("depth",D(5))
    L("fill_temp_planes")
    # Check both ends of EVERY physical Chip plane before any CPU/DMA copy.
    check_chip(D(6))
    c.move(D(6),D(0));check_add(0,D(7))
    c.quick(1,D(0),sub=True);check_chip(D(0))
    c.move(D(6),POST(4))
    c.alu("add",D(7),6);B(5,"reject")
    c.quick(1,D(5),sub=True);B(6,"fill_temp_planes")

    # Nonblocking Safe for inactive ScreenBuffer, then explicit WaitBlit.
    get("db",A(4));c.move(M(4,20),D(0))
    c.imm("and",1,D(0));B(7,"safe")
    get("db",A(4));c.move(M(4,12),A(0));c.move(A(0),D(0))
    c.tst(D(0));B(7,"reject")
    c.raw("2c780004");c.call_os(LVO_GETMSG)
    c.tst(D(0));B(7,"reject")
    get("db",A(4));c.move(M(4,20),D(0))
    c.imm("and",0xfffffffe,D(0));c.move(D(0),M(4,20))
    L("safe")
    get("gfx",A(6));c.call_os(LVO_WAITBLIT)

    if action=="capture":
        get("backbm",A(0));c.raw("43ea0100") # LEA 256(A2),A1
        get("x",D(0));get("y",D(1))
        c.move(I(0),D(2));c.move(I(0),D(3))
    else:
        c.raw("41ea0100") # LEA 256(A2),A0
        get("backbm",A(1))
        c.move(I(0),D(0));c.move(I(0),D(1))
        get("x",D(2));get("y",D(3))
    get("w",D(4));get("h",D(5))
    get("method",D(6));get("gfx",A(6))
    B(1,"copy_core")
    c.tst(D(3));B(7,"reject")
    if action=="capture":
        get("base",A(0))
        get("x",D(0));c.move(D(0),M(0,16))
        get("y",D(0));c.move(D(0),M(0,20))
        call(CHANGE)
    c.move(I(1),D(3));B(0,"leave")
    L("reject")
    if action=="capture":
        get("newbank",D(0));c.tst(D(0));B(7,"reject_no_erase")
        get("bank",D(0));call(EFF)
        L("reject_no_erase")
    c.move(I(0),D(3))
    L("leave")
    c.raw("4fef0180") # LEA +384(SP),SP
    c.raw("4cdf77f7")
    c.raw("74004e75")
    L("bank_name")
    c.raw(NAME.hex())
    L("copy_core")
    native,labels=emit_cblock_copy_core()
    c.raw(native.hex())
    return c.out(),c.labels


def emit_capture():
    return emit_cblock_bank_action("capture")
def emit_draw():
    return emit_cblock_bank_action("draw")
def emit_restore():
    return emit_cblock_bank_action("restore")


if __name__=="__main__":
    from hashlib import sha256
    for action in ("capture","draw","restore"):
        b,labels=emit_cblock_bank_action(action)
        print("M18 CBlock",action,len(b),len(labels),sha256(b).hexdigest())
