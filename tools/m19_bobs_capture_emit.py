"""M19 native Get AGA Bob I,X1,Y1,X2,Y2 (inclusive), MC68020-ready.

Captures 1..8 private AGA back-buffer planes into one AMOS-owned, planar,
uncompressed multi-image bank. No conversion on PC, no other bank numbers,
no implicit swap. Planar layout: for each row, plane0..plane(depth-1),
each plane row word-aligned. Zero mask offset means fully opaque.
This is an experimental command: real WinUAE and Compiler are separate gates.

Generated PC-relative selection-state reference is linked by the builder;
the caller must never execute this emitter without linking that reference.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, POST, PRE, I
from amos_main_abi import main_index, rjsr

GETADR = rjsr(main_index("Bnk.GetAdr"))
DATA_BYTES = 131072
DATA_START = 40 + 128 * 24
STATE_PTR = 0x1c8
CHIP_FLAG = 2
LVO_TYPEOFMEM = -534
LVO_GETMSG = -372
LVO_WAITBLIT = -228
MAX_W = 4096

F = dict(y2=0,x2=4,y1=8,x1=12,img=16,bank=20,base=24,
         state=28,db=32,bmp=36,sw=40,sh=44,depth=48,
         src_stride=52,dst_stride=56,w=60,h=64,bytes=68,
         padded=72,srcrow=76,xbyte=80,srcbit=84,
         dstptr=88,offset=92,end=96,dirptr=100,
         oldvalid=104,first=108,last=112)
FRAME = 160


def emit_get_bob() -> tuple[bytes, dict[str,int]]:
    c = Code()
    B, L = c.branch, c.label
    def ld(k, d): c.move(M(2, F[k]), d)
    def st(d, k): c.move(d, M(2, F[k]))
    def fail_nonzero(k): ld(k,D(0));c.tst(D(0));B(7,'reject')
    def memory_check(chip=False):
        # Exec.TypeOfMem(A1) -> D0, restoring AMOS A6 before further calls.
        c.move(A(6),PRE(7))
        c.raw('2c780004')
        c.call_os(LVO_TYPEOFMEM)
        c.move(POST(7),A(6))
        if chip: c.imm('and',CHIP_FLAG,D(0))
        c.tst(D(0))
        B(7,'reject')
    def checked_add(dst,src):
        c.alu('add',src,dst)
        B(5,'reject')
    def expect_long(off,expect):
        ld('base',A(0));c.move(M(0,off),D(0))
        c.imm('cmp',expect,D(0));B(6,'reject')

    c.raw('48e7efee')       # established AP20 preservation convention
    c.raw('4fefff60')       # local frame 160 bytes
    c.move(A(7),A(2))
    st(D(3),'y2')
    for k in ('x2','y1','x1','img'):
        c.move(POST(3),D(7));st(D(7),k)
    c.move(I(0),D(3))     # default fail

    # PC-relative bank-number state belongs to same compiler-copied BOBS unit.
    L('selection_reference')
    c.lea(4,'unlinked_selected_word')
    c.move(I(0),D(0))
    c.move(M(4),D(0),'w')
    st(D(0),'bank')
    c.imm('cmp',5,D(0));B(5,'reject')
    c.imm('cmp',65535,D(0));B(2,'reject')
    ld('img',D(0))
    c.imm('cmp',1,D(0));B(5,'reject')
    c.imm('cmp',128,D(0));B(2,'reject')

    # Reject rectangles with bad order/negative or impossible dimensions.
    for k in ('x1','y1','x2','y2'):
        ld(k,D(0));c.tst(D(0));B(11,'reject')
        c.imm('cmp',MAX_W,D(0));B(4,'reject')  # BCC >=4096
    for lo,hi in (('x1','x2'),('y1','y2')):
        ld(hi,D(0));ld(lo,D(1));c.alu('cmp',D(1),0);B(5,'reject')
    for lo,hi,dim in (('x1','x2','w'),('y1','y2','h')):
        ld(hi,D(0));ld(lo,D(1));c.alu('sub',D(1),0)
        c.quick(1,D(0));st(D(0),dim)

    # Re-resolve AMOS bank number EVERY call; Erase/Load may replace it.
    ld('bank',D(0));c.raw(GETADR.hex())
    c.move(A(0),D(0))
    c.imm('cmp',24,D(0));B(3,'reject')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'reject')
    st(A(0),'base')
    ld('base',D(0));c.imm('sub',24,D(0));c.move(D(0),A(1))
    memory_check()
    ld('base',D(0));c.imm('add',DATA_BYTES-1,D(0));B(5,'reject')
    c.move(D(0),A(1));memory_check()

    ld('base',A(0))
    c.move(M(0,-20),D(0));c.imm('cmp',DATA_BYTES+16,D(0));B(6,'reject')
    c.move(M(0,-16),D(0));ld('bank',D(1));c.alu('cmp',D(1),0);B(6,'reject')
    c.move(I(0),D(0));c.move(M(0,-12),D(0),'w')
    c.tst(D(0));B(7,'bankflags_ok')
    c.imm('and',0xfffd,D(0),'w');c.imm('cmp',1,D(0),'w');B(6,'reject')
    L('bankflags_ok')
    for off,ex in (
        (-8,0x41474142),(-4,0x4f422020),
        (0,0x41474142),(4,0x4f423031),
        (8,0x00010080),(16,DATA_BYTES),
        (24,40),(28,24),(32,DATA_START),(36,0)
    ):
        expect_long(off,ex)
    ld('base',A(0))
    c.move(M(0,20),D(0))
    c.imm('cmp',DATA_START,D(0));B(5,'reject')
    c.imm('cmp',DATA_BYTES,D(0));B(2,'reject')
    st(D(0),'offset')
    c.move(I(0),D(0));c.move(M(0,12),D(0),'w')
    c.tst(D(0));B(6,'reject')  # flags must be zero

    # Validate private AGA Screen state and inactive ScreenBuffer.
    c.move(M(5,STATE_PTR),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,'reject')
    st(A(4),'state')
    for off in (0,8,32):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,'reject')
    for off, k in ((12,'sw'),(16,'sh'),(28,'depth')):
        c.move(M(4,off),D(0))
        c.imm('cmp',1,D(0));B(5,'reject')
        c.imm('cmp',8 if k=='depth' else MAX_W,D(0));B(2,'reject')
        st(D(0),k)
    for dim,hi in (('sw','x2'),('sh','y2')):
        ld(hi,D(0));ld(dim,D(1));c.alu('cmp',D(1),0);B(4,'reject')

    ld('state',A(4));c.move(M(4,32),A(0));st(A(0),'db')
    c.move(M(0,8),D(0));c.tst(D(0));B(7,'front_zero')
    c.imm('cmp',1,D(0));B(6,'reject')
    ld('db',A(0));c.move(M(0),A(1));B(0,'back_ready')
    L('front_zero')
    ld('db',A(0));c.move(M(0,4),A(1))
    L('back_ready')
    c.move(A(1),D(0));c.tst(D(0));B(7,'reject')
    c.move(M(1),A(0))
    c.move(A(0),D(0));c.tst(D(0));B(7,'reject')
    st(A(0),'bmp')

    c.move(I(0),D(0));c.move(M(0),D(0),'w')
    c.imm('cmp',2,D(0));B(5,'reject')
    c.imm('cmp',65534,D(0));B(2,'reject')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'reject')
    st(D(0),'src_stride')
    c.shift(0,3,left=True)
    ld('sw',D(1));c.alu('cmp',D(1),0);B(5,'reject')
    ld('bmp',A(0))
    c.move(I(0),D(0));c.move(M(0,2),D(0),'w')
    ld('sh',D(1));c.alu('cmp',D(1),0);B(5,'reject')
    c.move(I(0),D(0));c.move(M(0,5),D(0),'b')
    ld('depth',D(1));c.alu('cmp',D(1),0);B(6,'reject')

    # Stride and data budget: planar rows word-aligned; never overflow bank.
    ld('w',D(0));c.imm('add',15,D(0))
    c.imm('and',0xfffffff0,D(0))
    c.shift(0,3,left=False)
    st(D(0),'dst_stride')
    ld('depth',D(1))
    c.word(0xc0c1)             # MULU.W depth,D0
    ld('h',D(1))
    c.word(0xc0c1)             # MULU.W height,D0
    st(D(0),'bytes')
    c.imm('add',3,D(0));B(5,'reject')
    c.imm('and',0xfffffffc,D(0))
    st(D(0),'padded')
    ld('offset',D(1));checked_add(0,D(1))
    c.imm('cmp',DATA_BYTES,D(0));B(2,'reject')
    st(D(0),'end')
    ld('base',D(0));ld('offset',D(1));checked_add(0,D(1))
    st(D(0),'dstptr')

    # Directory ID is 1-based; metadata is committed ONLY after full capture.
    ld('img',D(0));c.quick(1,D(0),sub=True)
    c.move(I(24),D(1));c.word(0xc0c1)
    c.imm('add',40,D(0));ld('base',D(1));checked_add(0,D(1))
    st(D(0),'dirptr')
    c.move(D(0),A(0));c.move(M(0),D(0))
    c.tst(D(0));B(7,'valid_new')
    c.imm('cmp',1,D(0));B(6,'reject')
    L('valid_new')
    st(D(0),'oldvalid')

    # Source row byte offsets. 68000 MULU is safe: Y<=4095, stride<=65534.
    ld('y1',D(0));ld('src_stride',D(1));c.word(0xc0c1)
    st(D(0),'srcrow')
    ld('x1',D(0));c.shift(0,3,left=False)
    st(D(0),'xbyte')
    ld('x1',D(0));c.imm('and',7,D(0))
    c.move(I(7),D(1));c.alu('sub',D(0),1)
    st(D(1),'srcbit')
    ld('srcrow',D(0));ld('xbyte',D(1));checked_add(0,D(1))
    st(D(0),'first')
    ld('y2',D(0));ld('src_stride',D(1));c.word(0xc0c1)
    ld('x2',D(1));c.shift(1,3,left=False);checked_add(0,D(1))
    st(D(0),'last')

    # Each actual source plane MUST be Chip at first and last used byte.
    ld('bmp',A(4));c.quick(8,A(4))
    ld('depth',D(5))
    L('check_source_plane')
    c.move(POST(4),D(7))
    c.tst(D(7));B(7,'reject')
    c.imm('cmp',-1,D(7));B(7,'reject')
    c.move(D(7),D(0));c.imm('and',1,D(0));B(6,'reject')
    c.move(D(7),D(0));ld('first',D(1));checked_add(0,D(1))
    c.move(D(0),A(1));memory_check(chip=True)
    c.move(D(7),D(0));ld('last',D(1));checked_add(0,D(1))
    c.move(D(0),A(1));memory_check(chip=True)
    c.quick(1,D(5),sub=True)
    B(6,'check_source_plane')

    # Wait for Safe and WaitBlit before reading screen pixels.
    ld('db',A(4));c.move(M(4,20),D(0))
    c.imm('and',1,D(0));B(7,'is_safe')
    c.move(M(4,12),A(0));c.move(A(0),D(0));c.tst(D(0));B(7,'reject')
    c.move(A(6),PRE(7));c.raw('2c780004');c.call_os(LVO_GETMSG)
    c.move(POST(7),A(6))
    c.tst(D(0));B(7,'reject')
    ld('db',A(4));c.move(M(4,20),D(0))
    c.imm('and',0xfffffffe,D(0));c.move(D(0),M(4,20))
    L('is_safe')
    ld('state',A(4));c.move(A(6),PRE(7))
    c.move(M(4,8),A(6));c.call_os(LVO_WAITBLIT)
    c.move(POST(7),A(6))

    # Zero only selected new payload, including word-aligned row padding.
    ld('dstptr',A(1));ld('padded',D(6));c.shift(6,1,left=False)
    L('zero_destination')
    c.raw('4259')            # CLR.W (A1)+
    c.quick(1,D(6),sub=True);B(6,'zero_destination')

    # Actual planar pixel extraction from private ScreenBuffer (no chunky).
    ld('h',D(6))
    L('row_start')
    ld('bmp',A(0));c.quick(8,A(0))
    ld('depth',D(5))
    L('plane_start')
    c.move(POST(0),A(4))
    ld('srcrow',D(0));c.word(0xd9c0)  # ADDA.L D0,A4
    ld('xbyte',D(0));c.word(0xd9c0)
    ld('dstptr',A(1))
    ld('w',D(2))
    ld('srcbit',D(1))
    c.move(I(7),D(4))
    L('pixel')
    c.move(I(0),D(0));c.move(M(4),D(0),'b')
    c.word(0x0300)           # BTST D1,D0
    B(7,'pixel_is_zero')
    c.word(0x09d1)           # BSET D4,(A1) in selected planar output
    L('pixel_is_zero')
    c.quick(1,D(1),sub=True);B(10,'source_bit_ready')
    c.quick(1,A(4));c.move(I(7),D(1))
    L('source_bit_ready')
    c.quick(1,D(4),sub=True);B(10,'dest_bit_ready')
    c.quick(1,A(1));c.move(I(7),D(4))
    L('dest_bit_ready')
    c.quick(1,D(2),sub=True);B(6,'pixel')
    ld('dstptr',D(0));ld('dst_stride',D(1));checked_add(0,D(1))
    st(D(0),'dstptr')
    c.quick(1,D(5),sub=True);B(6,'plane_start')
    ld('srcrow',D(0));ld('src_stride',D(1));checked_add(0,D(1))
    st(D(0),'srcrow')
    c.quick(1,D(6),sub=True);B(6,'row_start')

    # Publish directory, used pointer, count. Other image descriptors untouched.
    ld('dirptr',A(1))
    c.move(I(0),POST(1))     # valid=0 until the last store
    for k in ('w','h','depth','dst_stride'):
        ld(k,D(0));c.move(D(0),POST(1),'w')
    ld('offset',D(0));c.move(D(0),POST(1))
    c.move(I(0),POST(1))     # independent mask not yet allocated: opaque
    ld('bytes',D(0));c.move(D(0),POST(1))
    ld('base',A(0));ld('end',D(0));c.move(D(0),M(0,20))
    ld('oldvalid',D(0));c.tst(D(0));B(6,'count_same')
    c.move(I(0),D(0));c.move(M(0,12),D(0),'w')
    c.quick(1,D(0))        # low word is the image count
    c.move(D(0),M(0,12),'w')
    L('count_same')
    ld('dirptr',A(0));c.move(I(1),M(0))
    c.move(I(1),D(3))
    L('reject')
    c.raw('4fef00a0')
    c.raw('4cdf77f7')
    c.raw('74004e75')        # integer return type, no implicit swap
    L('unlinked_selected_word')
    c.word(0)                # placeholder to be PC-relatively re-linked
    result = c.out()
    if result.count(GETADR) != 1:
        raise ValueError('unexpected AMOS bank lookup calls')
    if result[c.labels['unlinked_selected_word']:][:2] != b'\x00\x00':
        raise ValueError('selection placeholder changed')
    return result, c.labels
