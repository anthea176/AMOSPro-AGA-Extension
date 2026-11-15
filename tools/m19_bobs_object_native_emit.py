"""Native persistent AGA Bobs: set, off, draw/update on private backbuffer.

32 independent objects share bank-owned planar images; each object retains
its bank number AND bank pointer identity, preventing stale Erase/Load reuse
in the ordinary replacement case. No implicit Aga Swap. Mask is independent,
index 0 opaque unless caller made an index-zero transparency mask.
Draw is a safety-checked CPU compositor, not a claimed Blitter fast path.
"""
from __future__ import annotations

from m68k_emit import Code,D,A,M,POST,PRE,I
from amos_main_abi import main_index,rjsr

GETADR=rjsr(main_index("Bnk.GetAdr"))
STATE_PTR=0x1c8
MAX_BOBS=32
RECORD=24
CAPACITY=131072
DATA_START=40+128*24
CHIP_FLAG=2

S=dict(img=0,y=4,x=8,obj=12,bank=16,base=20,slot=24,desc=28)
SF=48

F=dict(state=0,db=4,bmp=8,sw=12,sh=16,scdepth=20,bpr=24,
       table=28,left=32,base=36,x=40,y=44,img=48,
       desc=52,pixoff=56,maskoff=60,w=64,h=68,depth=72,
       stride=76,sx=80,sy=84,ex=88,ey=92,col=96,row=100,
       plane=104,dx=108,dy=112,srcaddr=116,dstaddr=120,
       used=124,bytes=128)
FRAME=160


def emit_objects():
    c=Code();B,L=c.branch,c.label
    def ld(k,reg):c.move(M(2,S[k]),reg)
    def st(reg,k):c.move(reg,M(2,S[k]))
    def df(k,reg):c.move(M(2,F[k]),reg)
    def ds(reg,k):c.move(reg,M(2,F[k]))

    # Public instruction: Aga Bob N,X,Y,I. D3=image, A3 pops Y,X,N.
    L('bob_set')
    c.raw('48e7efee');c.raw('4fefffd0');c.move(A(7),A(2))
    st(D(3),'img')
    for k in ('y','x','obj'):
        c.move(POST(3),D(7));st(D(7),k)
    c.move(I(0),D(3))
    ld('obj',D(0));c.imm('cmp',1,D(0));B(5,'set_reject')
    c.imm('cmp',MAX_BOBS,D(0));B(2,'set_reject')
    ld('img',D(0));c.imm('cmp',1,D(0));B(5,'set_reject')
    c.imm('cmp',128,D(0));B(2,'set_reject')
    for k in ('x','y'):
        ld(k,D(0));c.imm('cmp',-32768,D(0));B(13,'set_reject')
        c.imm('cmp',32767,D(0));B(14,'set_reject')
    L('set_bank_reference');c.lea(4,'unlinked_selected')
    c.move(I(0),D(0));c.move(M(4),D(0),'w')
    c.imm('cmp',5,D(0));B(5,'set_reject')
    c.imm('cmp',65535,D(0));B(2,'set_reject')
    st(D(0),'bank')
    c.raw(GETADR.hex())
    c.move(A(0),D(0));c.imm('cmp',24,D(0));B(3,'set_reject')
    st(A(0),'base')
    c.move(M(0,-20),D(0));c.imm('cmp',CAPACITY+16,D(0));B(6,'set_reject')
    c.move(M(0,-16),D(0));ld('bank',D(1))
    c.alu('cmp',D(1),0);B(6,'set_reject')
    ld('base',A(0))
    for off,word in ((-8,0x41474142),(-4,0x4f422020),
                     (0,0x41474142),(4,0x4f423031),
                     (8,0x00010080),(16,CAPACITY),
                     (24,40),(28,24),(32,DATA_START),(36,0)):
        c.move(M(0,off),D(0));c.imm('cmp',word,D(0));B(6,'set_reject')
    ld('img',D(0));c.quick(1,D(0),sub=True)
    c.move(I(24),D(1));c.word(0xc0c1)
    c.imm('add',40,D(0));ld('base',D(1));c.alu('add',D(1),0)
    c.move(D(0),A(0));c.move(M(0),D(0))
    c.imm('cmp',1,D(0));B(6,'set_reject')

    ld('obj',D(0));c.quick(1,D(0),sub=True)
    c.move(I(RECORD),D(1));c.word(0xc0c1)
    c.lea(4,'bob_table');c.word(0xd9c0)  # ADDA.L D0,A4
    ld('bank',D(0));c.move(D(0),M(4,4))
    ld('img',D(0));c.move(D(0),M(4,8))
    ld('x',D(0));c.move(D(0),M(4,12))
    ld('y',D(0));c.move(D(0),M(4,16))
    ld('base',D(0));c.move(D(0),M(4,20))
    c.move(I(1),M(4))
    c.move(I(1),D(3));B(0,'set_leave')
    L('set_reject');c.move(I(0),D(3))
    L('set_leave');c.raw('4fef0030');c.raw('4cdf77f7');c.raw('74004e75')

    # Public instruction: Aga Bob Off N.
    L('bob_off')
    c.raw('48e7efee')
    c.move(D(3),D(0));c.move(I(0),D(3))
    c.imm('cmp',1,D(0));B(5,'off_leave')
    c.imm('cmp',MAX_BOBS,D(0));B(2,'off_leave')
    c.quick(1,D(0),sub=True)
    c.move(I(RECORD),D(1));c.word(0xc0c1)
    c.lea(4,'bob_table');c.word(0xd9c0)
    c.move(I(0),M(4))
    c.move(I(1),D(3))
    L('off_leave');c.raw('4cdf77f7');c.raw('74004e75')

    # Public instruction: Aga Bob Draw or Aga Bob Update. No A3 args.
    L('bob_draw')
    c.raw('48e7efee');c.raw('4fefff60');c.move(A(7),A(2))
    c.move(I(0),D(3))
    c.move(M(5,STATE_PTR),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,'draw_leave')
    ds(A(4),'state')
    for off in (0,8,32):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,'draw_leave')
    for off,k in ((12,'sw'),(16,'sh'),(28,'scdepth')):
        c.move(M(4,off),D(0));c.imm('cmp',1,D(0));B(5,'draw_leave')
        c.imm('cmp',8 if k=='scdepth' else 4096,D(0))
        B(2,'draw_leave');ds(D(0),k)
    df('state',A(4));c.move(M(4,32),A(0));ds(A(0),'db')
    c.move(M(0,8),D(0));c.tst(D(0));B(7,'draw_back0')
    c.imm('cmp',1,D(0));B(6,'draw_leave')
    df('db',A(0));c.move(M(0),A(1));B(0,'draw_back_ready')
    L('draw_back0')
    df('db',A(0));c.move(M(0,4),A(1))
    L('draw_back_ready')
    c.move(A(1),D(0));c.tst(D(0));B(7,'draw_leave')
    c.move(M(1),A(0));c.move(A(0),D(0));c.tst(D(0))
    B(7,'draw_leave');ds(A(0),'bmp')
    c.move(I(0),D(0));c.move(M(0),D(0),'w')
    c.imm('cmp',2,D(0));B(5,'draw_leave')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'draw_leave')
    ds(D(0),'bpr')
    c.shift(0,3,left=True);df('sw',D(1))
    c.alu('cmp',D(1),0);B(5,'draw_leave')
    df('bmp',A(0));c.move(I(0),D(0));c.move(M(0,2),D(0),'w')
    df('sh',D(1));c.alu('cmp',D(1),0);B(5,'draw_leave')
    c.move(I(0),D(0));c.move(M(0,5),D(0),'b')
    df('scdepth',D(1));c.alu('cmp',D(1),0);B(6,'draw_leave')

    # Validate EACH physical back bitplane is real Chip memory.
    df('bmp',A(4));c.quick(8,A(4))
    df('scdepth',D(5))
    L('draw_plane_safety')
    c.move(POST(4),D(7));c.tst(D(7));B(7,'draw_leave')
    c.imm('cmp',-1,D(7));B(7,'draw_leave')
    c.move(D(7),D(0));c.imm('and',1,D(0));B(6,'draw_leave')
    c.move(D(7),A(1))
    c.move(A(6),PRE(7));c.raw('2c780004');c.call_os(-534)
    c.move(POST(7),A(6))
    c.imm('and',2,D(0));B(7,'draw_leave')
    c.move(D(7),D(0));df('bpr',D(1));df('sh',D(2))
    c.word(0xc2c2)  # MULU.W D2,D1, count bytes of physical plane
    c.alu('add',D(1),0);B(5,'draw_leave')
    c.quick(1,D(0),sub=True)
    c.move(D(0),A(1))
    c.move(A(6),PRE(7));c.raw('2c780004');c.call_os(-534)
    c.move(POST(7),A(6))
    c.imm('and',2,D(0));B(7,'draw_leave')
    c.quick(1,D(5),sub=True);B(6,'draw_plane_safety')

    # Complete older asynchronous Blitter updates before any CPU pixel writes.
    df('db',A(4));c.move(M(4,20),D(0))
    c.imm('and',1,D(0));B(7,'draw_safe')
    c.move(M(4,12),A(0));c.move(A(0),D(0))
    c.tst(D(0));B(7,'draw_leave')
    c.move(A(6),PRE(7));c.raw('2c780004');c.call_os(-372)
    c.move(POST(7),A(6))
    c.tst(D(0));B(7,'draw_leave')
    df('db',A(4));c.move(M(4,20),D(0));c.imm('and',0xfffffffe,D(0))
    c.move(D(0),M(4,20))
    L('draw_safe')
    df('state',A(4));c.move(A(6),PRE(7))
    c.move(M(4,8),A(6));c.call_os(-228)
    c.move(POST(7),A(6))

    c.lea(4,'bob_table');ds(A(4),'table')
    c.move(I(MAX_BOBS),D(0));ds(D(0),'left')
    L('draw_object')
    df('table',A(4))
    c.move(M(4),D(0));c.imm('cmp',1,D(0))
    B(6,'draw_next')
    c.move(M(4,4),D(0));c.imm('cmp',5,D(0));B(5,'draw_next')
    c.imm('cmp',65535,D(0));B(2,'draw_next')
    c.raw(GETADR.hex())
    c.move(A(0),D(0));c.imm('cmp',24,D(0));B(3,'draw_next')
    c.move(A(0),D(1));df('table',A(4))
    c.alu('cmp',M(4,20),1);B(6,'draw_next')
    ds(A(0),'base')
    c.move(M(0,-20),D(0));c.imm('cmp',CAPACITY+16,D(0));B(6,'draw_next')
    df('base',A(0))
    for off,word in ((-8,0x41474142),(-4,0x4f422020),
                     (0,0x41474142),(4,0x4f423031),
                     (8,0x00010080),(16,CAPACITY),
                     (24,40),(28,24),(32,DATA_START),(36,0)):
        c.move(M(0,off),D(0));c.imm('cmp',word,D(0));B(6,'draw_next')
    c.move(M(0,20),D(0));c.imm('cmp',DATA_START,D(0));B(5,'draw_next')
    c.imm('cmp',CAPACITY,D(0));B(2,'draw_next')
    ds(D(0),'used')
    df('table',A(4))
    for off,k in ((8,'img'),(12,'x'),(16,'y')):
        c.move(M(4,off),D(0));ds(D(0),k)
    df('img',D(0));c.imm('cmp',1,D(0));B(5,'draw_next')
    c.imm('cmp',128,D(0));B(2,'draw_next')
    c.quick(1,D(0),sub=True);c.move(I(24),D(1))
    c.word(0xc0c1);c.imm('add',40,D(0))
    df('base',D(1));c.alu('add',D(1),0)
    ds(D(0),'desc')
    c.move(D(0),A(0));c.move(M(0),D(0));c.imm('cmp',1,D(0))
    B(6,'draw_next')
    df('desc',A(0))
    for off,k in ((4,'w'),(6,'h'),(8,'depth'),(10,'stride')):
        c.move(I(0),D(0));c.move(M(0,off),D(0),'w');ds(D(0),k)
    for off,k in ((12,'pixoff'),(16,'maskoff'),(20,'bytes')):
        c.move(M(0,off),D(0));ds(D(0),k)
    for key,maxval in (('w',4096),('h',4096),('depth',8)):
        df(key,D(0));c.imm('cmp',1,D(0));B(5,'draw_next')
        c.imm('cmp',maxval,D(0));B(2,'draw_next')
    df('depth',D(0));df('scdepth',D(1))
    c.alu('cmp',D(1),0);B(2,'draw_next')
    df('w',D(0));c.imm('add',15,D(0))
    c.imm('and',0xfffffff0,D(0));c.shift(0,3,left=False)
    df('stride',D(1));c.alu('cmp',D(1),0);B(6,'draw_next')
    df('pixoff',D(0));c.imm('cmp',DATA_START,D(0));B(5,'draw_next')
    df('depth',D(1));df('stride',D(0));c.word(0xc0c1)
    df('h',D(1));c.word(0xc0c1)
    df('bytes',D(1));c.alu('cmp',D(1),0);B(6,'draw_next')
    df('pixoff',D(1));c.alu('add',D(1),0);B(5,'draw_next')
    df('used',D(1));c.alu('cmp',D(1),0);B(2,'draw_next')
    # Validate optional 1-bit mask extent separately.
    df('maskoff',D(0));c.tst(D(0));B(7,'draw_mask_ok')
    c.imm('cmp',DATA_START,D(0));B(5,'draw_next')
    df('stride',D(1));df('h',D(2));c.word(0xc2c2)
    c.alu('add',D(1),0);B(5,'draw_next')
    df('used',D(1));c.alu('cmp',D(1),0);B(2,'draw_next')
    L('draw_mask_ok')
    # Screen clip computed in signed longs before pixel loop.
    c.move(I(0),D(0));ds(D(0),'sx');ds(D(0),'sy')
    df('x',D(0));c.tst(D(0));B(10,'clip_x_ready')
    c.move(I(0),D(1));c.alu('sub',D(0),1);ds(D(1),'sx')
    L('clip_x_ready')
    df('y',D(0));c.tst(D(0));B(10,'clip_y_ready')
    c.move(I(0),D(1));c.alu('sub',D(0),1);ds(D(1),'sy')
    L('clip_y_ready')
    df('w',D(0));df('sw',D(1));df('x',D(2))
    c.alu('sub',D(2),1);c.alu('cmp',D(1),0)
    B(13,'clip_x_keep');c.move(D(1),D(0))
    L('clip_x_keep');ds(D(0),'ex')
    df('sx',D(1));c.alu('cmp',D(1),0);B(13,'draw_next')
    df('h',D(0));df('sh',D(1));df('y',D(2))
    c.alu('sub',D(2),1);c.alu('cmp',D(1),0)
    B(13,'clip_y_keep');c.move(D(1),D(0))
    L('clip_y_keep');ds(D(0),'ey')
    df('sy',D(1));c.alu('cmp',D(1),0);B(13,'draw_next')

    df('sy',D(0));ds(D(0),'row')
    L('draw_row')
    df('sx',D(0));ds(D(0),'col')
    L('draw_pixel')
    df('maskoff',D(0));c.tst(D(0));B(7,'draw_visible')
    # mask addr = base + mask offset + row*stride + (col>>3)
    df('row',D(0));df('stride',D(1));c.word(0xc0c1)
    df('col',D(1));c.shift(1,3,left=False);c.alu('add',D(1),0)
    df('maskoff',D(1));c.alu('add',D(1),0)
    df('base',D(1));c.alu('add',D(1),0)
    c.move(D(0),A(4))
    df('col',D(2));c.imm('and',7,D(2))
    c.move(I(7),D(1));c.alu('sub',D(2),1)
    c.move(I(0),D(0));c.move(M(4),D(0),'b')
    c.word(0x0300)         # BTST D1,D0
    B(7,'draw_skip_pixel')
    L('draw_visible')
    # Source & destination pixel coordinates, both now clipped.
    df('col',D(0));df('x',D(1));c.alu('add',D(1),0);ds(D(0),'dx')
    df('row',D(0));df('y',D(1));c.alu('add',D(1),0);ds(D(0),'dy')
    c.move(I(0),D(0));ds(D(0),'plane')
    L('draw_pixel_plane')
    # Source byte: base+off+(row*depth+plane)*stride+col//8.
    df('row',D(0));df('depth',D(1));c.word(0xc0c1)
    df('plane',D(1));c.alu('add',D(1),0)
    df('stride',D(1));c.word(0xc0c1)
    df('col',D(1));c.shift(1,3,left=False);c.alu('add',D(1),0)
    df('pixoff',D(1));c.alu('add',D(1),0)
    df('base',D(1));c.alu('add',D(1),0)
    c.move(D(0),A(4))
    df('col',D(2));c.imm('and',7,D(2))
    c.move(I(7),D(1));c.alu('sub',D(2),1)
    c.move(I(0),D(0));c.move(M(4),D(0),'b')
    c.word(0x0300)         # BTST D1,D0, Z flag retained
    # Need calculate target without clobbering flags => store source bit in frame.
    B(7,'source_zero')
    c.move(I(1),D(7));B(0,'source_ready')
    L('source_zero');c.move(I(0),D(7))
    L('source_ready')
    # Destination plane address from inactive physical BitMap + plane*4.
    df('plane',D(0));c.shift(0,2,left=True)
    c.imm('add',8,D(0));df('bmp',D(1));c.alu('add',D(1),0)
    c.move(D(0),A(0));c.move(M(0),D(0))
    df('dy',D(1));df('bpr',D(2));c.word(0xc2c2)
    c.alu('add',D(1),0)
    df('dx',D(1));c.shift(1,3,left=False);c.alu('add',D(1),0)
    c.move(D(0),A(1))
    df('dx',D(2));c.imm('and',7,D(2))
    c.move(I(7),D(4));c.alu('sub',D(2),4)
    c.tst(D(7));B(7,'dest_clear')
    c.word(0x09d1)         # BSET D4,(A1)
    B(0,'plane_next')
    L('dest_clear')
    c.word(0x0991)         # BCLR D4,(A1), index-zero truly opaque
    L('plane_next')
    df('plane',D(0));c.quick(1,D(0));ds(D(0),'plane')
    df('depth',D(1));c.alu('cmp',D(1),0);B(5,'draw_pixel_plane')
    L('draw_skip_pixel')
    df('col',D(0));c.quick(1,D(0));ds(D(0),'col')
    df('ex',D(1));c.alu('cmp',D(1),0);B(5,'draw_pixel')
    df('row',D(0));c.quick(1,D(0));ds(D(0),'row')
    df('ey',D(1));c.alu('cmp',D(1),0);B(5,'draw_row')
    L('draw_next')
    df('table',D(0));c.imm('add',RECORD,D(0));ds(D(0),'table')
    df('left',D(0));c.quick(1,D(0),sub=True);ds(D(0),'left')
    B(6,'draw_object')
    c.move(I(1),D(3))
    L('draw_leave')
    c.raw('4fef00a0');c.raw('4cdf77f7');c.raw('74004e75')

    L('unlinked_selected');c.word(0)
    L('bob_table')
    c.raw('00'*(MAX_BOBS*RECORD))
    raw=c.out()
    return raw,c.labels
