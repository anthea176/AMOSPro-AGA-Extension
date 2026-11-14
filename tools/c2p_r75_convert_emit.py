"""R75 C2P full-frame Convert, 320x256, 4..8 bitplanes; native M68000 opcodes.

Aga C2P Convert -> D3=1/0; D2=0; never flips a screen. Revalidates
AMOS BANK, both Intuition ScreenBuffers, SafePort and every Chip plane.
BltBitMap from an SDK-owned intermediate chip BitMap, WaitBlit before return.
A5, A3 and all AMOS caller register invariants are preserved.
"""
from m68k_emit import Code,D,A,M,I,POST
from amos_main_abi import main_index,rjsr
from c2p_r74_open_emit import MAGIC,CHUNKY,LVO_TYPEOFMEM

BANK=rjsr(main_index('Bnk.GetAdr'))
LVO_GETMSG=-372
LVO_WAITBLIT=-228
LVO_BLTBITMAP=-30
LVO_C2P_GET=-66
LVO_C2P_SET=-72
LVO_C2P_CONVERT=-90
MEMF_CHIP=2
STATE_OFFSET=0x1c8
FRAME=192
F=dict(state=0,db=4,lib=8,ctx=12,bank=16,depth=20,gfx=24,bankptr=28,
       front=32,sb0=36,sb1=40,backsb=44,backbm=48,frontbm=52,
       srcbm=56,bm=60,bpr=64,planehead=68,planecnt=72,planeend=76,
       blitcount=80)


def emit_convert():
    """Returns native bytes and symbol offsets, no AP20 GetP delimiter."""
    c=Code();B,L=c.branch,c.label
    def get(k,d):c.move(M(2,F[k]),d)
    def put(v,k):c.move(v,M(2,F[k]))
    def typemem(value, chip=False):
        c.move(value,A(1));c.raw('2c780004');c.call_os(LVO_TYPEOFMEM)
        if chip:c.imm('and',MEMF_CHIP,D(0))
        c.tst(D(0));B(7,'reject')
    def verify_bitmap(field):
        # Returns with all required planes confirmed Chip, no direct writes.
        get(field,D(5));c.tst(D(5));B(7,'reject')
        c.move(D(5),D(0));c.imm('and',1,D(0));B(6,'reject')
        typemem(D(5))
        get(field,D(5));c.move(D(5),D(0));c.imm('add',39,D(0));B(5,'reject');typemem(D(0))
        get(field,A(4))
        c.move(I(0),D(0));c.move(M(4,0),D(0),'w')
        c.imm('cmp',40,D(0));B(5,'reject')
        c.move(D(0),D(5));c.imm('and',1,D(5));B(6,'reject')
        put(D(0),'bpr')
        c.move(I(0),D(0));c.move(M(4,2),D(0),'w')
        c.imm('cmp',256,D(0));B(5,'reject')
        c.move(I(0),D(0));c.move(M(4,5),D(0),'b')
        get('depth',D(1));c.alu('cmp',D(1),0);B(6,'reject')
        # Validate CHIP residency at *both* ends of each physical plane.
        get('bpr',D(1));c.move(I(255),D(0));c.word(0xc0c1) # MULU.W D1,D0
        c.imm('add',39,D(0));B(5,'reject');put(D(0),'planeend')
        get(field,A(4));c.quick(8,A(4));put(A(4),'planehead')
        get('depth',D(7));put(D(7),'planecnt')
        L('plane_'+field)
        get('planehead',A(4));c.move(POST(4),D(5));put(A(4),'planehead')
        c.tst(D(5));B(7,'reject');c.imm('cmp',-1,D(5));B(7,'reject')
        c.move(D(5),D(0));c.imm('and',1,D(0));B(6,'reject')
        typemem(D(5),chip=True)
        get('planeend',D(0));c.alu('add',D(5),0);B(5,'reject')
        typemem(D(0),chip=True)
        get('planecnt',D(7));c.quick(1,D(7),sub=True);put(D(7),'planecnt');B(6,'plane_'+field)

    c.raw('48e7efee')                 # preserve D0/D1/D4-D7/A0-A2/A4-A6
    c.raw('4fefff40')                 # LEA -192(SP),SP
    c.move(A(7),A(2))
    c.move(I(0),D(3))
    # Fail-closed CPU feature guard before calling c2p.library.
    c.raw('20780004');c.move(A(0),D(0));c.tst(D(0));B(7,'reject')
    c.move(I(0),D(0));c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1);B(7,'reject')
    c.move(M(5,STATE_OFFSET),A(4));c.move(A(4),D(0));c.tst(D(0));B(7,'reject')
    put(A(4),'state')
    for off in (0,8,32):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,'reject')
    for off,required in ((12,320),(16,256)):
        c.move(M(4,off),D(0));c.imm('cmp',required,D(0));B(6,'reject')
    c.move(M(4,28),D(0));c.imm('cmp',4,D(0));B(5,'reject')
    c.imm('cmp',8,D(0));B(2,'reject');put(D(0),'depth')
    c.move(M(4,8),D(0));put(D(0),'gfx')
    c.move(M(4,32),A(4));put(A(4),'db')
    c.move(M(4,40),D(0));c.imm('cmp',MAGIC,D(0));B(6,'reject')
    for off,key in ((24,'lib'),(28,'ctx'),(32,'bank')):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,'reject');put(D(0),key)
    c.move(M(4,36),D(0));get('depth',D(1));c.alu('cmp',D(1),0);B(6,'reject')
    get('bank',D(0));c.imm('cmp',5,D(0));B(5,'reject');c.imm('cmp',65535,D(0));B(2,'reject')
    # Selected back SB must never be the displayed front SB.
    get('db',A(4))
    for off,key in ((0,'sb0'),(4,'sb1')):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,'reject');put(D(0),key)
        typemem(D(0))
        get('db',A(4))
    get('sb0',D(0));get('sb1',D(1));c.alu('cmp',D(1),0);B(7,'reject')
    get('db',A(4));c.move(M(4,8),D(0));c.imm('cmp',1,D(0));B(2,'reject');put(D(0),'front')
    c.tst(D(0));B(6,'front_one')
    get('sb1',D(0));put(D(0),'backsb')
    get('sb0',A(4));c.move(M(4,0),D(0));put(D(0),'frontbm')
    B(0,'selected')
    L('front_one')
    get('sb0',D(0));put(D(0),'backsb')
    get('sb1',A(4));c.move(M(4,0),D(0));put(D(0),'frontbm')
    L('selected')
    get('frontbm',D(0));c.tst(D(0));B(7,'reject')
    get('backsb',A(4));c.move(M(4,0),D(0));c.tst(D(0));B(7,'reject')
    put(D(0),'backbm')
    get('frontbm',D(1));c.alu('cmp',D(1),0);B(7,'reject')
    # Re-fetch bank address, never hold the old pointer through Erase/Load.
    get('bank',D(0));c.raw(BANK.hex());c.move(A(0),D(5))
    c.imm('cmp',24,D(5));B(3,'reject')
    c.move(D(5),D(0));c.imm('and',1,D(0));B(6,'reject')
    put(D(5),'bankptr')
    typemem(D(5))
    get('bankptr',D(0));c.imm('sub',24,D(0));typemem(D(0))
    get('bankptr',A(4));c.move(M(4,-16),D(0));get('bank',D(1));c.alu('cmp',D(1),0);B(6,'reject')
    get('bankptr',A(4));c.move(I(0),D(0));c.move(M(4,-12),D(0),'w')
    c.imm('and',0xfffd,D(0),'w');c.imm('cmp',1,D(0),'w');B(6,'reject')
    get('bankptr',A(4));c.move(M(4,-20),D(0));c.imm('cmp',CHUNKY+16,D(0));B(5,'reject')
    get('bankptr',D(0));c.imm('add',CHUNKY-1,D(0));B(5,'reject');typemem(D(0))
    # Query SDK bitmap, then validate source+destination fully before conversion.
    get('ctx',A(0));c.move(I(5),D(0));get('lib',A(6));c.call_os(LVO_C2P_GET)
    c.tst(D(0));B(7,'reject');put(D(0),'srcbm')
    verify_bitmap('srcbm')
    verify_bitmap('backbm')
    # Nonblocking consumption of Safe reply. No ReplyMsg, never touch Disp.
    get('db',A(4));c.move(M(4,20),D(0));c.imm('and',1,D(0));B(7,'safe')
    get('db',A(4));c.move(M(4,12),A(0));c.move(A(0),D(0));c.tst(D(0));B(7,'reject')
    c.raw('2c780004');c.call_os(LVO_GETMSG);c.tst(D(0));B(7,'reject')
    get('db',A(4));c.move(M(4,20),D(0));c.imm('and',0xfffffffe,D(0));c.move(D(0),M(4,20))
    L('safe')
    # If bank was reallocated with the same id, update the external SDK source.
    get('ctx',A(0));c.move(I(4),D(0));get('bankptr',D(1));get('lib',A(6));c.call_os(LVO_C2P_SET)
    c.tst(D(0));B(6,'reject')
    get('ctx',A(0));get('lib',A(6));c.call_os(LVO_C2P_CONVERT)
    c.tst(D(0));B(6,'reject')
    # Enforce prior-blitter completion, then copy all planes into back, never front.
    get('gfx',A(6));c.call_os(LVO_WAITBLIT)
    get('srcbm',A(0));get('backbm',A(1))
    for reg in range(6):c.move(I(0),D(reg))
    c.move(I(320),D(4));c.move(I(256),D(5))
    c.move(I(0xc0),D(6));c.move(I(0xff),D(7))
    c.move(I(0),A(2))  # TempA must be NULL (not our stack frame)
    # GraphicsBase was loaded into A6 immediately before the pre-blit WaitBlit.
    c.call_os(LVO_BLTBITMAP)
    c.move(A(7),A(2))
    put(D(0),'blitcount')
    get('gfx',A(6));c.call_os(LVO_WAITBLIT)
    get('blitcount',D(0));get('depth',D(1));c.alu('cmp',D(1),0);B(6,'reject')
    c.move(I(1),D(3));B(0,'finish')
    L('reject');c.move(I(0),D(3))
    L('finish')
    c.raw('4fef00c0')
    c.raw('4cdf77f7')
    c.raw('74004e75')
    out=c.out()
    assert len(out)%2==0 and out.count(BANK)==1
    return out,c.labels

if __name__=='__main__':
    from hashlib import sha256
    blob,labels=emit_convert()
    print('R75 C2P Convert',len(blob),'bytes',len(labels),'labels',sha256(blob).hexdigest())
