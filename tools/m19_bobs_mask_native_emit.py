"""Native independent 1-bit Bob mask commands for the R90 AGA engine.

Make AGA Bob Mask I,C: D3=C, A3 pops image ID I.
No AGA Bob Mask I: D3=I, no stack parameters.
Mask pixels are 1=visible, 0=transparent. Pen zero is opaque unless
explicitly chosen as transparent C. Only bank-owned planar data is written.
"""
from __future__ import annotations
from m68k_emit import Code,D,A,M,POST,PRE,I
from amos_main_abi import main_index,rjsr

GETADR=rjsr(main_index('Bnk.GetAdr'))
CHANGE=rjsr(main_index('Bnk.Change'))
MAX_BANK_BYTES=131072
DIR_START=40
DIR_BYTES=24
DATA_START=40+128*24

F=dict(color=0,img=4,bank=8,base=12,desc=16,w=20,h=24,depth=28,
       stride=32,pixoff=36,maskoff=40,maskbytes=44,used=48,
       row=52,col=56,srcrow=60,transparent=64,bufptr=68,
       srcbyte=72,shift=76,candidate=80,oldmask=84)
FRAME=112


def emit_masks():
    c=Code()
    B,L=c.branch,c.label
    def ld(k,r):c.move(M(2,F[k]),r)
    def st(r,k):c.move(r,M(2,F[k]))
    def bump():
        c.move(A(6),PRE(7));c.raw('2c780004');c.call_os(-534)
        c.move(POST(7),A(6));c.tst(D(0));B(7,'reject')
    def selected(label):
        L(label)
        c.lea(4,'unlinked_selected')
        c.move(I(0),D(0));c.move(M(4),D(0),'w')
        c.imm('cmp',5,D(0));B(5,'reject')
        c.imm('cmp',65535,D(0));B(2,'reject')
        st(D(0),'bank')
    def setup_bank():
        ld('bank',D(0));c.raw(GETADR.hex())
        c.move(A(0),D(0));c.imm('cmp',24,D(0));B(3,'reject')
        c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'reject')
        st(A(0),'base')
        ld('base',D(0));c.imm('sub',24,D(0));c.move(D(0),A(1));bump()
        ld('base',D(0));c.imm('add',MAX_BANK_BYTES-1,D(0));B(5,'reject')
        c.move(D(0),A(1));bump()
        ld('base',A(0))
        c.move(M(0,-20),D(0));c.imm('cmp',MAX_BANK_BYTES+16,D(0));B(6,'reject')
        c.move(M(0,-16),D(0));ld('bank',D(1))
        c.alu('cmp',D(1),0);B(6,'reject')
        for off,x in ((-8,0x41474142),(-4,0x4f422020),
                      (0,0x41474142),(4,0x4f423031),
                      (8,0x00010080),(16,MAX_BANK_BYTES),
                      (24,40),(28,24),(32,DATA_START),(36,0)):
            ld('base',A(0));c.move(M(0,off),D(0))
            c.imm('cmp',x,D(0));B(6,'reject')
        ld('base',A(0));c.move(M(0,20),D(0))
        c.imm('cmp',DATA_START,D(0));B(5,'reject')
        c.imm('cmp',MAX_BANK_BYTES,D(0));B(2,'reject')
        st(D(0),'used')
        ld('img',D(0))
        c.imm('cmp',1,D(0));B(5,'reject')
        c.imm('cmp',128,D(0));B(2,'reject')
        c.quick(1,D(0),sub=True)
        c.move(I(DIR_BYTES),D(1));c.word(0xc0c1)
        c.imm('add',DIR_START,D(0));ld('base',D(1))
        c.alu('add',D(1),0);B(5,'reject')
        st(D(0),'desc')
        c.move(D(0),A(0));c.move(M(0),D(0))
        c.imm('cmp',1,D(0));B(6,'reject')
        # Read all fields after a fixed size/valid envelope check.
        ld('desc',A(0))
        for off,key in ((4,'w'),(6,'h'),(8,'depth'),(10,'stride')):
            c.move(I(0),D(0));c.move(M(0,off),D(0),'w')
            st(D(0),key)
        for off,key in ((12,'pixoff'),(16,'oldmask')):
            c.move(M(0,off),D(0));st(D(0),key)
        for key,maxval in (('w',4096),('h',4096),('depth',8)):
            ld(key,D(0));c.imm('cmp',1,D(0));B(5,'reject')
            c.imm('cmp',maxval,D(0));B(2,'reject')
        ld('w',D(0));c.imm('add',15,D(0))
        c.imm('and',0xfffffff0,D(0));c.shift(0,3,left=False)
        ld('stride',D(1));c.alu('cmp',D(1),0);B(6,'reject')
        ld('pixoff',D(0));c.imm('cmp',DATA_START,D(0));B(5,'reject')
        ld('depth',D(1));ld('stride',D(0));c.word(0xc0c1)
        ld('h',D(1));c.word(0xc0c1)
        ld('pixoff',D(1));c.alu('add',D(1),0);B(5,'reject')
        ld('used',D(1));c.alu('cmp',D(1),0);B(2,'reject')

    # entry 0: Make AGA Bob Mask I,C
    L('make_mask')
    c.raw('48e7efee');c.raw('4fefff90');c.move(A(7),A(2))
    st(D(3),'color')
    c.move(POST(3),D(7));st(D(7),'img')
    c.move(I(0),D(3))
    ld('color',D(0));c.tst(D(0));B(11,'reject')
    c.imm('cmp',255,D(0));B(2,'reject')
    selected('mask_bank_reference')
    setup_bank()

    # For depth<8, an out-of-palette transparent index is rejected.
    ld('depth',D(0));c.move(I(1),D(1))
    L('color_depth')
    c.shift(1,1,left=True)
    c.quick(1,D(0),sub=True);B(6,'color_depth')
    ld('color',D(0));c.alu('cmp',D(1),0);B(4,'reject')

    ld('stride',D(0));ld('h',D(1));c.word(0xc0c1)
    st(D(0),'maskbytes')
    c.imm('add',3,D(0));c.imm('and',0xfffffffc,D(0))
    ld('used',D(1));c.alu('add',D(1),0);B(5,'reject')
    c.imm('cmp',MAX_BANK_BYTES,D(0));B(2,'reject')
    st(D(0),'candidate')
    ld('used',D(0));st(D(0),'maskoff')
    ld('base',D(1));c.alu('add',D(1),0);B(5,'reject')
    st(D(0),'bufptr')

    # Zero candidate mask first, preserving all previously stored images.
    ld('bufptr',A(1));ld('maskbytes',D(6))
    c.imm('add',3,D(6));c.imm('and',0xfffffffc,D(6))
    c.shift(6,1,left=False)
    L('clear_mask')
    c.raw('4259')  # CLR.W (A1)+
    c.quick(1,D(6),sub=True);B(6,'clear_mask')

    c.move(I(0),D(0));st(D(0),'row')
    L('mask_row')
    c.move(I(0),D(0));st(D(0),'col')
    L('mask_col')
    # For a pixel, read its index across 1..8 planar source bytes.
    ld('row',D(0));ld('depth',D(1));c.word(0xc0c1)
    ld('stride',D(1));c.word(0xc0c1)
    ld('col',D(1));c.shift(1,3,left=False)
    c.alu('add',D(1),0)
    ld('pixoff',D(1));c.alu('add',D(1),0)
    ld('base',D(1));c.alu('add',D(1),0)
    c.move(D(0),A(4))
    ld('col',D(1));c.imm('and',7,D(1))
    c.move(I(7),D(2));c.alu('sub',D(1),2)
    c.move(I(0),D(5))   # reconstructed index
    c.move(I(1),D(7))   # plane weight
    ld('depth',D(6))
    L('mask_plane')
    c.move(I(0),D(0));c.move(M(4),D(0),'b')
    c.word(0x0500)    # BTST D2,D0 (bit position 7-(X&7))
    B(7,'mask_bit_clear')
    c.alu('or',D(7),5)
    L('mask_bit_clear')
    ld('stride',D(0));c.word(0xd9c0)  # ADDA.L D0,A4
    c.shift(7,1,left=True)
    c.quick(1,D(6),sub=True);B(6,'mask_plane')
    ld('color',D(0));c.alu('cmp',D(0),5)
    B(7,'mask_transparent')  # skip if index==transparent
    ld('row',D(0));ld('stride',D(1));c.word(0xc0c1)
    ld('col',D(1));c.shift(1,3,left=False);c.alu('add',D(1),0)
    ld('bufptr',D(1));c.alu('add',D(1),0)
    c.move(D(0),A(1))
    ld('col',D(2));c.imm('and',7,D(2))
    c.move(I(7),D(1));c.alu('sub',D(2),1)
    c.word(0x03d1) # BSET D1,(A1)
    L('mask_transparent')
    ld('col',D(0));c.quick(1,D(0));st(D(0),'col')
    ld('w',D(1));c.alu('cmp',D(1),0);B(5,'mask_col')
    ld('row',D(0));c.quick(1,D(0));st(D(0),'row')
    ld('h',D(1));c.alu('cmp',D(1),0);B(5,'mask_row')
    # All data ready: publish used, descriptor.maskoff.
    ld('base',A(0));ld('candidate',D(0));c.move(D(0),M(0,20))
    ld('desc',A(0));ld('maskoff',D(0));c.move(D(0),M(0,16))
    c.raw(CHANGE.hex())
    c.move(I(1),D(3))
    B(0,'leave')

    # entry 1: No AGA Bob Mask I
    L('no_mask')
    c.raw('48e7efee');c.raw('4fefff90');c.move(A(7),A(2))
    st(D(3),'img')
    c.move(I(0),D(3))
    selected('no_mask_bank_reference')
    setup_bank()
    ld('desc',A(0));c.move(I(0),M(0,16))
    c.raw(CHANGE.hex())
    c.move(I(1),D(3))
    B(0,'leave')

    L('reject')
    c.move(I(0),D(3))
    L('leave')
    c.raw('4fef0070');c.raw('4cdf77f7');c.raw('74004e75')
    L('unlinked_selected')
    c.word(0)
    raw=c.out()
    return raw,c.labels
