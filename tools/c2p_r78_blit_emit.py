"""R78 M68000-safe chunky 8-bit rectangle blitter, AP20 integer function.

Aga C2P Blit(SrcBank,SrcPitch,SrcX,SrcY,W,H,DstX,DstY).
D3=DstY; (A3)+ pops DstX,H,W,SrcY,SrcX,SrcPitch,SrcBank.
D3=1 if pixels copied, 0 on any rejection; D2=0 on return.
No c2p.library/Blitter/Convert/Swap calls and no screen/palette writes.
Validate BOTH live DATA/WORK AMOS banks and complete source bounds before
one CPU pixel write; reject physical bank overlaps even with different ids.
No extra local allocation, all former R77/native sections remain untouched.
"""
from __future__ import annotations
from m68k_emit import Code,D,A,M,I,POST
from amos_main_abi import main_index,rjsr
from c2p_r74_open_emit import MAGIC,CHUNKY,LVO_TYPEOFMEM

BANK=rjsr(main_index("Bnk.GetAdr"))
STATE=0x1c8
FRAME=160
F=dict(
    dsty=0,dstx=4,h=8,w=12,srcy=16,srcx=20,pitch=24,srcbank=28,
    state=32,db=36,dstbank=40,srcbase=44,srclen=48,srcend=52,
    dstbase=56,dstlen=60,dstend=64,srcptr=68,dstptr=72,
    srcskip=76,dstskip=80,
)

def emit_blit():
    c=Code();B,L=c.branch,c.label
    def get(field,reg):c.move(M(2,F[field]),reg)
    def put(reg,field):c.move(reg,M(2,F[field]))
    def dbra(reg,where):
        c.word(0x51c8|reg)  # DBF Dn, signed 16-bit PC relative
        c.fix.append((len(c.b),where));c.word(0)
    def type_mem_from(reg):
        c.move(reg,A(1))
        c.raw("2c780004")  # ExecBase from absolute.W 4
        c.call_os(LVO_TYPEOFMEM)
        c.tst(D(0));B(7,"reject")
    def validate_bank(number,base,length,end,minimum):
        get(number,D(0));c.raw(BANK.hex())
        c.move(A(0),D(5))
        c.imm("cmp",24,D(5));B(3,"reject")
        c.move(D(5),D(0));c.imm("and",1,D(0));B(6,"reject")
        put(D(5),base)
        type_mem_from(D(5))
        get(base,D(0));c.imm("sub",24,D(0));type_mem_from(D(0))
        get(base,A(4))
        c.move(M(4,-16),D(0));get(number,D(1))
        c.alu("cmp",D(1),0);B(6,"reject")
        c.move(I(0),D(0));c.move(M(4,-12),D(0),"w")
        c.tst(D(0));B(7,"bankflags_"+base)
        c.imm("and",0xfffd,D(0),"w")
        c.imm("cmp",1,D(0),"w");B(6,"reject")
        L("bankflags_"+base)
        get(base,A(4));c.move(M(4,-20),D(0))
        c.imm("cmp",16+minimum,D(0));B(5,"reject")
        c.imm("sub",16,D(0))
        c.tst(D(0));B(13,"reject")   # fail closed if length >= 2GiB
        put(D(0),length)
        get(base,D(0));get(length,D(1))
        c.alu("add",D(1),0);B(5,"reject")
        put(D(0),end)
        c.quick(1,D(0),sub=True);type_mem_from(D(0))
    # Standard AP20 saved register convention, D3 result and A3 consumed.
    c.raw("48e7efee")
    c.raw("4fefff60")             # LEA -160(SP),SP
    c.move(A(7),A(2))
    put(D(3),"dsty")
    for field in ("dstx","h","w","srcy","srcx","pitch","srcbank"):
        c.move(POST(3),D(7));put(D(7),field)
    c.move(I(0),D(3))
    # Reject CPU 000 before invoking the 020-only c2p screen machinery.
    c.raw("20780004")            # ExecBase at 4.W
    c.move(A(0),D(0));c.tst(D(0));B(7,"reject")
    c.move(I(0),D(0));c.move(M(0,0x128),D(0),"w")
    c.word(0x0800);c.word(1)     # BTST #AFF_68020,D0
    B(7,"reject")
    # All AMOS integer arguments are signed. Reject invalid / overflow-prone
    # geometry before any bank lookup or write.
    get("srcbank",D(0));c.imm("cmp",5,D(0));B(5,"reject")
    c.imm("cmp",65535,D(0));B(2,"reject")
    for field,upper in (("pitch",0x7fffffff),("srcx",0x7fffffff),("srcy",0x7fffffff)):
        get(field,D(0));c.tst(D(0))
        B(13,"reject")
        if field=="pitch":B(7,"reject")
    for field,maximum in (("w",320),("h",256)):
        get(field,D(0));c.tst(D(0));B(3,"reject")
        c.imm("cmp",maximum,D(0));B(2,"reject")
    for field,negative,positive in (("dstx",-320,320),("dsty",-256,256)):
        get(field,D(0));c.imm("cmp",negative,D(0));B(13,"reject")
        c.imm("cmp",positive,D(0));B(12,"reject")
    # The full original source rectangle must fit one pitch even when
    # the destination is partially clipped.
    get("srcx",D(0));get("w",D(1))
    c.alu("add",D(1),0);B(5,"reject");B(9,"reject")
    get("pitch",D(1));c.alu("cmp",D(1),0);B(2,"reject")
    # The 48-byte DBState is owned by the screen. No cached bank pointer.
    c.move(M(5,STATE),A(4));c.move(A(4),D(0));c.tst(D(0));B(7,"reject")
    put(A(4),"state")
    get("state",A(4));c.move(M(4,0),D(0));c.tst(D(0));B(7,"reject")
    for off,required in ((12,320),(16,256)):
        get("state",A(4));c.move(M(4,off),D(0))
        c.imm("cmp",required,D(0));B(6,"reject")
    get("state",A(4));c.move(M(4,28),D(0))
    c.imm("cmp",4,D(0));B(5,"reject")
    c.imm("cmp",8,D(0));B(2,"reject")
    get("state",A(4));c.move(M(4,32),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,"reject");put(A(4),"db")
    get("db",A(4));c.move(M(4,40),D(0))
    c.imm("cmp",MAGIC,D(0));B(6,"reject")
    for off in (24,28):
        get("db",A(4));c.move(M(4,off),D(0));c.tst(D(0));B(7,"reject")
    get("db",A(4));c.move(M(4,32),D(0))
    c.imm("cmp",5,D(0));B(5,"reject")
    c.imm("cmp",65535,D(0));B(2,"reject")
    put(D(0),"dstbank")
    get("srcbank",D(1));c.alu("cmp",D(1),0);B(7,"reject")
    # Two independent Bnk.GetAdr calls. Reject missing, stale, malformed,
    # unaligned or overlapping whole-bank storage before pixel writes.
    validate_bank("srcbank","srcbase","srclen","srcend",1)
    validate_bank("dstbank","dstbase","dstlen","dstend",CHUNKY)
    get("srcbase",D(0));get("dstend",D(1))
    c.alu("cmp",D(1),0);B(4,"distinct")
    get("dstbase",D(0));get("srcend",D(1))
    c.alu("cmp",D(1),0);B(4,"distinct")
    B(0,"reject")
    L("distinct")
    # Checked multiplication (SrcY+H-1)*SrcPitch, full positive 32-bit,
    # software shift/add with carry rejection rather than MULU.W truncation.
    get("srcy",D(4));get("h",D(0))
    c.quick(1,D(0),sub=True)
    c.alu("add",D(0),4);B(9,"reject")
    get("pitch",D(5));B(1,"mul32")
    c.tst(D(1));B(7,"reject")
    get("srcx",D(1));c.alu("add",D(1),0);B(5,"reject")
    get("w",D(1));c.alu("add",D(1),0);B(5,"reject")
    get("srclen",D(1));c.alu("cmp",D(1),0);B(2,"reject")
    # Clip LEFT, adjusting source origin and width.
    get("dstx",D(0));c.tst(D(0));B(10,"clip_right")
    c.move(I(0),D(1));c.alu("sub",D(0),1) # -DstX, safe because >= -320
    get("w",D(0));c.alu("cmp",D(1),0);B(3,"reject")
    get("srcx",D(0));c.alu("add",D(1),0);put(D(0),"srcx")
    get("w",D(0));c.alu("sub",D(1),0);put(D(0),"w")
    c.move(I(0),D(0));put(D(0),"dstx")
    L("clip_right")
    get("dstx",D(0));get("w",D(1));c.alu("add",D(0),1)
    c.imm("cmp",320,D(1));B(3,"clip_top")
    c.move(I(320),D(1));c.alu("sub",D(0),1);put(D(1),"w")
    L("clip_top")
    get("dsty",D(0));c.tst(D(0));B(10,"clip_bottom")
    c.move(I(0),D(1));c.alu("sub",D(0),1)
    get("h",D(0));c.alu("cmp",D(1),0);B(3,"reject")
    get("srcy",D(0));c.alu("add",D(1),0);put(D(0),"srcy")
    get("h",D(0));c.alu("sub",D(1),0);put(D(0),"h")
    c.move(I(0),D(0));put(D(0),"dsty")
    L("clip_bottom")
    get("dsty",D(0));get("h",D(1));c.alu("add",D(0),1)
    c.imm("cmp",256,D(1));B(3,"clip_done")
    c.move(I(256),D(1));c.alu("sub",D(0),1);put(D(1),"h")
    L("clip_done")
    # The source bounds were checked for the larger original rectangle,
    # and each clipped rectangle is contained in it.
    get("srcy",D(4));get("pitch",D(5));B(1,"mul32")
    c.tst(D(1));B(7,"reject")
    get("srcx",D(1));c.alu("add",D(1),0);B(5,"reject")
    get("srcbase",D(1));c.alu("add",D(1),0);B(5,"reject")
    put(D(0),"srcptr")
    get("dsty",D(0));c.move(I(320),D(1))
    c.word(0xc0c1)               # MULU.W D1,D0, safe 0..255*320
    get("dstx",D(1));c.alu("add",D(1),0);B(5,"reject")
    get("dstbase",D(1));c.alu("add",D(1),0);B(5,"reject")
    put(D(0),"dstptr")
    get("pitch",D(0));get("w",D(1));c.alu("sub",D(1),0);put(D(0),"srcskip")
    c.move(I(320),D(0));c.alu("sub",D(1),0);put(D(0),"dstskip")
    # ALL validation is complete. CPU byte copy (zero is opaque).
    get("srcptr",A(0));get("dstptr",A(1))
    get("h",D(7));c.quick(1,D(7),sub=True)
    L("copy_row")
    get("w",D(6));c.quick(1,D(6),sub=True)
    L("copy_pixel")
    c.move(POST(0),POST(1),"b")
    dbra(6,"copy_pixel")
    get("srcskip",D(0));c.move(A(0),D(5));c.alu("add",D(0),5);c.move(D(5),A(0))
    get("dstskip",D(0));c.move(A(1),D(5));c.alu("add",D(0),5);c.move(D(5),A(1))
    dbra(7,"copy_row")
    c.move(I(1),D(3));B(0,"finish")
    L("reject")
    c.move(I(0),D(3))
    L("finish")
    c.raw("4fef00a0")              # LEA +160(SP),SP
    c.raw("4cdf77f7")              # MOVEM preserved restore
    c.raw("74004e75")              # MOVEQ #0,D2 ; RTS
    # Safe checked 32x32 multiplication subroutine. D4 rows, D5 pitch;
    # result D0 and D1 success. No long-multiply 020 opcode needed.
    L("mul32")
    c.move(I(0),D(0))
    L("mul_loop")
    c.tst(D(4));B(7,"mul_ok")
    c.word(0x0804);c.word(0)      # BTST #0,D4
    B(7,"mul_skip")
    c.alu("add",D(5),0);B(5,"mul_fail")
    L("mul_skip")
    c.shift(4,1)                  # LSR.L #1,D4
    B(7,"mul_ok")
    c.shift(5,1,left=True)        # LSL.L #1,D5
    B(5,"mul_fail")
    B(0,"mul_loop")
    L("mul_ok")
    c.move(I(1),D(1))
    c.raw("4e75")                 # RTS
    L("mul_fail")
    c.move(I(0),D(1))
    c.raw("4e75")                 # RTS
    out=c.out()
    assert len(out)%2==0 and out.count(BANK)==2
    assert out[:8]==bytes.fromhex("48e7efee4fefff60")
    assert out.count(bytes.fromhex("4cdf77f774004e75"))==1
    return out,c.labels

if __name__=="__main__":
    from hashlib import sha256
    blob,labels=emit_blit()
    print("R78 C2P BLIT",len(blob),"bytes",sha256(blob).hexdigest(),labels)
