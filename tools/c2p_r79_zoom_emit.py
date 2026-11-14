"""R79 68000-safe opaque nearest-neighbour C2P Zoom, native AP20 integer.

Aga C2P Zoom(SrcBank,SrcPitch,SrcX,SrcY,SrcW,SrcH,DstX,DstY,DstW,DstH)
D3=DstH; (A3)+ pops DstW,DstY,DstX,SrcH,SrcW,SrcY,SrcX,SrcPitch,SrcBank.
Returns D3=1 if pixels written, 0 otherwise, D2=0. No SDK/Blitter/Swap.
Uses full original destination rectangle (even with clipping) to map
source pixels: floor((screenX-DstX)*SrcW/DstW), likewise for Y.
Source and destination bank addresses are resolved and validated per call.
"""
from __future__ import annotations
from m68k_emit import Code,D,A,M,I,POST
from amos_main_abi import main_index,rjsr
from c2p_r74_open_emit import MAGIC,CHUNKY,LVO_TYPEOFMEM

BANK=rjsr(main_index("Bnk.GetAdr"))
STATE=0x1c8
FRAME=192
F=dict(
    dsth=0,dstw=4,dsty=8,dstx=12,srch=16,srcw=20,srcy=24,
    srcx=28,pitch=32,srcbank=36,state=40,db=44,dstbank=48,
    srcbase=52,srclen=56,srcend=60,dstbase=64,dstlen=68,dstend=72,
    visx=76,visy=80,visw=84,vish=88,xstart=92,ystart=96,
    xquot=100,xrem=104,xfirst=108,xerr=112,dstrow=116,rowoff=120
)

def emit_zoom():
    c=Code();B,L=c.branch,c.label
    def get(field,reg):c.move(M(2,F[field]),reg)
    def put(reg,field):c.move(reg,M(2,F[field]))
    def dbra(reg,target):
        c.word(0x51c8|reg)
        c.fix.append((len(c.b),target));c.word(0)
    def require_mem(reg):
        c.move(reg,A(1))
        c.raw("2c780004")                # ExecBase from absolute.W 4
        c.call_os(LVO_TYPEOFMEM)
        c.tst(D(0));B(7,"reject")
    def validate_bank(number,base,length,end,minimum):
        get(number,D(0));c.raw(BANK.hex())
        c.move(A(0),D(5))
        c.imm("cmp",24,D(5));B(3,"reject")
        c.move(D(5),D(0));c.imm("and",1,D(0));B(6,"reject")
        put(D(5),base)
        require_mem(D(5))
        get(base,D(0));c.imm("sub",24,D(0));require_mem(D(0))
        get(base,A(4))
        c.move(M(4,-16),D(0));get(number,D(1))
        c.alu("cmp",D(1),0);B(6,"reject")
        c.move(I(0),D(0));c.move(M(4,-12),D(0),"w")
        c.tst(D(0));B(7,"bank_flags_"+base)
        c.imm("and",0xfffd,D(0),"w")
        c.imm("cmp",1,D(0),"w");B(6,"reject")
        L("bank_flags_"+base)
        get(base,A(4));c.move(M(4,-20),D(0))
        c.imm("cmp",16+minimum,D(0));B(5,"reject")
        c.imm("sub",16,D(0))
        c.tst(D(0));B(13,"reject")
        put(D(0),length)
        get(base,D(0));get(length,D(1))
        c.alu("add",D(1),0);B(5,"reject")
        put(D(0),end)
        c.quick(1,D(0),sub=True);require_mem(D(0))

    # ABI: standard saved registers, D3 is last argument and return.
    c.raw("48e7efee")
    c.raw("4fefff40")                 # LEA -192(SP),SP
    c.move(A(7),A(2))
    put(D(3),"dsth")
    for key in ("dstw","dsty","dstx","srch","srcw","srcy","srcx","pitch","srcbank"):
        c.move(POST(3),D(7));put(D(7),key)
    c.move(I(0),D(3))

    # Fail closed on CPU000/010. Every opcode in this routine is 68000-safe.
    c.raw("20780004")
    c.move(A(0),D(0));c.tst(D(0));B(7,"reject")
    c.move(I(0),D(0));c.move(M(0,0x128),D(0),"w")
    c.word(0x0800);c.word(1)        # BTST #AFF_68020,D0
    B(7,"reject")

    get("srcbank",D(0));c.imm("cmp",5,D(0));B(5,"reject")
    c.imm("cmp",65535,D(0));B(2,"reject")
    for key in ("pitch","srcx","srcy"):
        get(key,D(0));c.tst(D(0));B(13,"reject")
        if key=="pitch":B(7,"reject")
    for key,limit in (("srcw",320),("srch",256),
                      ("dstw",320),("dsth",256)):
        get(key,D(0));c.tst(D(0));B(15,"reject")
        c.imm("cmp",limit,D(0));B(2,"reject")
    for key,minimum,upper_exclusive in (("dstx",-319,320),("dsty",-255,256)):
        get(key,D(0))
        c.imm("cmp",minimum,D(0));B(13,"reject")
        c.imm("cmp",upper_exclusive,D(0));B(12,"reject")

    # Validate complete original source rectangle before writing any pixel.
    get("srcx",D(0));get("srcw",D(1))
    c.alu("add",D(1),0);B(5,"reject");B(9,"reject")
    get("pitch",D(1));c.alu("cmp",D(1),0);B(2,"reject")

    # Verify active 320x256 C2P screen and full DBState ownership.
    c.move(M(5,STATE),A(4));c.move(A(4),D(0));c.tst(D(0));B(7,"reject")
    put(A(4),"state")
    get("state",A(4));c.move(M(4,0),D(0));c.tst(D(0));B(7,"reject")
    for offset,expected in ((12,320),(16,256)):
        get("state",A(4));c.move(M(4,offset),D(0))
        c.imm("cmp",expected,D(0));B(6,"reject")
    get("state",A(4));c.move(M(4,28),D(0))
    c.imm("cmp",4,D(0));B(5,"reject")
    c.imm("cmp",8,D(0));B(2,"reject")
    get("state",A(4));c.move(M(4,32),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,"reject");put(A(4),"db")
    get("db",A(4));c.move(M(4,40),D(0))
    c.imm("cmp",MAGIC,D(0));B(6,"reject")
    for offset in (24,28):
        get("db",A(4));c.move(M(4,offset),D(0));c.tst(D(0));B(7,"reject")
    get("db",A(4));c.move(M(4,32),D(0))
    c.imm("cmp",5,D(0));B(5,"reject")
    c.imm("cmp",65535,D(0));B(2,"reject")
    put(D(0),"dstbank")
    get("srcbank",D(1));c.alu("cmp",D(1),0);B(7,"reject")
    validate_bank("srcbank","srcbase","srclen","srcend",1)
    validate_bank("dstbank","dstbase","dstlen","dstend",CHUNKY)
    get("srcbase",D(0));get("dstend",D(1))
    c.alu("cmp",D(1),0);B(4,"separate")
    get("dstbase",D(0));get("srcend",D(1))
    c.alu("cmp",D(1),0);B(4,"separate")
    B(0,"reject")
    L("separate")

    get("srcy",D(4));get("srch",D(0))
    c.quick(1,D(0),sub=True)
    c.alu("add",D(0),4);B(5,"reject");B(9,"reject")
    get("pitch",D(5));B(1,"mul32")
    c.tst(D(1));B(7,"reject")
    get("srcx",D(1));c.alu("add",D(1),0);B(5,"reject")
    get("srcw",D(1));c.alu("add",D(1),0);B(5,"reject")
    get("srclen",D(1));c.alu("cmp",D(1),0);B(2,"reject")

    # Clip original destination rectangle, without changing the scale.
    get("dstx",D(0));get("dstw",D(1))
    c.alu("add",D(0),1)
    c.tst(D(1));B(15,"reject")   # end <= 0
    c.imm("cmp",320,D(1));B(15,"x_end_ready")
    c.move(I(320),D(1))
    L("x_end_ready")
    get("dstx",D(0));c.tst(D(0));B(10,"x_nonnegative")
    c.move(I(0),D(4));c.alu("sub",D(0),4);put(D(4),"xstart")
    c.move(I(0),D(0));B(0,"x_start_ready")
    L("x_nonnegative")
    c.move(I(0),D(4));put(D(4),"xstart")
    L("x_start_ready")
    put(D(0),"visx")
    c.alu("sub",D(0),1);c.tst(D(1));B(15,"reject")
    put(D(1),"visw")

    get("dsty",D(0));get("dsth",D(1))
    c.alu("add",D(0),1)
    c.tst(D(1));B(15,"reject")
    c.imm("cmp",256,D(1));B(15,"y_end_ready")
    c.move(I(256),D(1))
    L("y_end_ready")
    get("dsty",D(0));c.tst(D(0));B(10,"y_nonnegative")
    c.move(I(0),D(4));c.alu("sub",D(0),4);put(D(4),"ystart")
    c.move(I(0),D(0));B(0,"y_start_ready")
    L("y_nonnegative")
    c.move(I(0),D(4));put(D(4),"ystart")
    L("y_start_ready")
    put(D(0),"visy")
    c.alu("sub",D(0),1);c.tst(D(1));B(15,"reject")
    put(D(1),"vish")

    # First visible chunky destination pixel: (visibleY*320+visibleX).
    get("visy",D(0));c.move(I(320),D(1))
    c.word(0xc0c1)             # MULU.W D1,D0 (320*255)
    get("visx",D(1));c.alu("add",D(1),0)
    get("dstbase",D(1));c.alu("add",D(1),0)
    put(D(0),"dstrow")

    # Horizontal DDA: quotient+remainder of SrcW/DstW, no DIVU per pixel.
    get("srcw",D(0));get("dstw",D(1))
    c.word(0x80c1)             # DIVU.W D1,D0
    c.move(D(0),D(4));c.imm("and",0xffff,D(0));put(D(0),"xquot")
    c.word(0x4844)             # SWAP D4, remainder in low word
    c.imm("and",0xffff,D(4));put(D(4),"xrem")

    # First visible pixel may be clipped LEFT; account for original X.
    get("xstart",D(0));get("srcw",D(1))
    c.word(0xc0c1)             # MULU.W D1,D0
    get("dstw",D(1));c.word(0x80c1)  # DIVU.W D1,D0
    c.move(D(0),D(4));c.imm("and",0xffff,D(0));put(D(0),"xfirst")
    c.word(0x4844);c.imm("and",0xffff,D(4));put(D(4),"xerr")
    get("ystart",D(0));put(D(0),"rowoff")

    # All potentially rejecting validation is complete. No error path
    # occurs after the first pixel is written.
    get("vish",D(7));c.quick(1,D(7),sub=True)
    L("row")
    get("rowoff",D(0));get("srch",D(1))
    c.word(0xc0c1)             # MULU.W D1,D0; < 256*256
    get("dsth",D(1));c.word(0x80c1)  # DIVU.W D1,D0
    c.imm("and",0xffff,D(0))
    get("srcy",D(4));c.alu("add",D(0),4)
    get("pitch",D(5));B(1,"mul32")
    get("srcx",D(1));c.alu("add",D(1),0)
    get("xfirst",D(1));c.alu("add",D(1),0)
    get("srcbase",D(1));c.alu("add",D(1),0)
    c.move(D(0),A(0))
    get("dstrow",A(1))
    get("xerr",D(4))
    get("visw",D(6));c.quick(1,D(6),sub=True)
    L("pixel")
    c.move(M(0),M(1),"b")      # opaque: index 0 is written too
    c.quick(1,A(1))            # next destination pixel
    get("xquot",D(0))
    c.move(A(0),D(1));c.alu("add",D(0),1);c.move(D(1),A(0))
    get("xrem",D(0));c.alu("add",D(0),4)
    get("dstw",D(0));c.alu("cmp",D(0),4)
    B(5,"x_no_carry")          # X error < DstW, no extra source step
    c.alu("sub",D(0),4)
    c.quick(1,A(0))
    L("x_no_carry")
    dbra(6,"pixel")
    get("rowoff",D(0));c.quick(1,D(0));put(D(0),"rowoff")
    get("dstrow",D(0));c.imm("add",320,D(0));put(D(0),"dstrow")
    dbra(7,"row")
    c.move(I(1),D(3));B(0,"finish")

    L("reject")
    c.move(I(0),D(3))
    L("finish")
    c.raw("4fef00c0")          # LEA +192(SP),SP
    c.raw("4cdf77f7")          # restore original register set
    c.raw("74004e75")          # MOVEQ #0,D2 ; RTS

    # Checked unsigned 32x32 multiply without MULU.L (68020-only).
    # Called only with nonnegative factors; D4 rows, D5 pitch.
    L("mul32")
    c.move(I(0),D(0))
    L("mul_loop")
    c.tst(D(4));B(7,"mul_ok")
    c.word(0x0804);c.word(0)  # BTST #0,D4
    B(7,"mul_skip")
    c.alu("add",D(5),0);B(5,"mul_fail")
    L("mul_skip")
    c.shift(4,1)
    B(7,"mul_ok")
    c.shift(5,1,left=True)
    B(5,"mul_fail")
    B(0,"mul_loop")
    L("mul_ok")
    c.move(I(1),D(1));c.raw("4e75")
    L("mul_fail")
    c.move(I(0),D(1));c.raw("4e75")
    blob=c.out()
    assert len(blob)%2==0 and blob.count(BANK)==2
    assert blob[:8]==bytes.fromhex("48e7efee4fefff40")
    assert blob.count(bytes.fromhex("4cdf77f774004e75"))==1
    return blob,c.labels

if __name__=="__main__":
    from hashlib import sha256
    b,lbl=emit_zoom()
    print("R79 ZOOM CODE",len(b),"SHA256",sha256(b).hexdigest(),lbl)
