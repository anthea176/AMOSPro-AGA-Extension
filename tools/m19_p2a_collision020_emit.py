#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P2a private 68020 Bob-pair collision kernel, source-only.

No public AP20 token, no bank lookup, no installer, no DMA/Swap.
Inputs are TRUSTED, prevalidated/owned per-Bob descriptors in readable memory:
    A0 -> Bob A, A1 -> Bob B, D0 -> mode 0 rectangle / 1 pixel mask.
Descriptor (40 bytes, big-endian LONGs, aligned):
    +0,+4,+8,+12 = clipped left,top,right,bottom (signed, exclusive ends)
    +16,+20      = logical origin X,Y after signed hotspot subtraction
    +24,+28      = original width,height, 1..4096 pixels
    +32          = native AGBO row stride = 2*ceil(width/16), bytes
    +36          = validated mask address, 0 means all opaque including pen 0
Output: D2=0, D3=1 collision / 0 no collision / -1 malformed descriptor.
Preserves D0,D1,D4-D7,A0-A6 and stack. No writes beyond private stack.

CRITICAL: caller must revalidate A5 ownership, P0f stamps, source AGBO,
physical mask address/span and P1d clipping BEFORE invoking this kernel.
It is NOT safe to call with untrusted raw AMOS pointers. Identical-memory
ABA cannot be excluded by the host stamp format. Neither P1e nor LAST_GOOD
is modified by building/testing this independent source unit.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code, D, A, M, I

DESCRIPTOR_BYTES = 40
FRAME_BYTES = 64
MAX_SIDE = 4096
F = dict(mode=0, first=4, second=8, left=12, top=16,
         right=20, bottom=24, x=28, y=32)
assert max(F.values())+4 <= FRAME_BYTES


def emit_collision020():
    c=Code()
    B,L=c.branch,c.label
    def setv(reg,key): c.move(reg,M(2,F[key]))
    def getv(key,reg): c.move(M(2,F[key]),reg)

    L('p2a_pair_entry')
    c.raw('48e7efee')   # Known P1e/AMOS preserved register set, excluding D2/D3.
    c.raw('4fefffc0')   # LEA -64(SP),SP.
    c.move(A(7),A(2))
    setv(D(0),'mode');setv(A(0),'first');setv(A(1),'second')
    c.imm('cmp',1,D(0));B(2,'p2a_invalid')   # unsigned >1 rejects also negative
    for which in ('first','second'):
        getv(which,D(4))
        c.tst(D(4));B(7,'p2a_invalid')
        c.imm('and',1,D(4));B(6,'p2a_invalid') # odd descriptor pointer

    # Validate host-provided visible footprint against source image geometry.
    # For no-overlap cases an empty rectangle is legal and reports no hit.
    for index,which in enumerate(('first','second')):
        getv(which,A(4))
        prefix=f'p2a_v{index}_'
        for off in (0,4):
            c.move(M(4,off),D(4))
            c.alu('cmp',M(4,off+8),4)
            B(12,'p2a_no_hit')  # left>=right or top>=bottom
        for off in (24,28):
            c.move(M(4,off),D(4))
            c.imm('cmp',1,D(4));B(13,'p2a_invalid')
            c.imm('cmp',MAX_SIDE,D(4));B(14,'p2a_invalid')
        c.move(M(4,24),D(4))
        c.imm('add',15,D(4))
        c.shift(4,4,left=False)
        c.shift(4,1,left=True)  # Exact AGBO 16-pixel word stride.
        c.alu('cmp',M(4,32),4);B(6,'p2a_invalid')
        c.move(M(4,36),D(4))
        c.imm('and',1,D(4));B(6,'p2a_invalid') # 0 or even mask pointer
        for offset,origin,extent in ((0,16,24),(4,20,28)):
            c.move(M(4,offset),D(4))
            c.alu('cmp',M(4,origin),4)
            B(13,'p2a_invalid')       # clipped left is before image origin
            c.move(M(4,origin),D(4))
            c.alu('add',M(4,extent),4)
            c.alu('cmp',M(4,offset+8),4)
            B(13,'p2a_invalid')       # clipped right exceeds image extent
        L(prefix+'validated')

    for offset,key,kind in ((0,'left','max'),(4,'top','max'),
                            (8,'right','min'),(12,'bottom','min')):
        getv('first',A(0));getv('second',A(1))
        c.move(M(0,offset),D(4));c.move(M(1,offset),D(5))
        c.alu('cmp',D(5),4)
        label=f'p2a_keep_{key}'
        B(12 if kind=='max' else 15,label)  # BGE for max / BLE for min
        c.move(D(5),D(4))
        L(label)
        setv(D(4),key)
    for lower,upper in (('left','right'),('top','bottom')):
        getv(upper,D(4));c.alu('cmp',M(2,F[lower]),4)
        B(15,'p2a_no_hit')   # empty clipped intersection

    getv('mode',D(4));c.tst(D(4));B(7,'p2a_hit')
    getv('top',D(4));setv(D(4),'y')
    L('p2a_row')
    getv('left',D(4));setv(D(4),'x')
    L('p2a_pixel')
    for index,which in enumerate(('first','second')):
        getv(which,A(4))
        c.move(M(4,36),D(4));c.tst(D(4))
        B(7,f'p2a_opaque_{index}')  # no mask => fully opaque
        getv('x',D(5));c.alu('sub',M(4,16),5)
        getv('y',D(6));c.alu('sub',M(4,20),6)
        c.move(M(4,32),D(7))
        c.word(0xccc7)   # MULU.W D7,D6: local_y * native AGBO stride
        c.move(D(5),D(7));c.shift(7,3,left=False) # local_x // 8
        c.alu('add',D(7),6)
        c.move(D(4),A(3));c.word(0xd7c6)  # ADDA.L D6,A3
        c.imm('and',7,D(5))
        c.move(I(7),D(7));c.alu('sub',D(5),7)
        c.word(0x0f13)             # BTST D7,(A3): MSB-first mask bit
        B(7,'p2a_next_pixel')     # clear bit in either image => no hit
        L(f'p2a_opaque_{index}')
    B(0,'p2a_hit')
    L('p2a_next_pixel')
    getv('x',D(4));c.quick(1,D(4));setv(D(4),'x')
    c.alu('cmp',M(2,F['right']),4);B(13,'p2a_pixel')
    getv('y',D(4));c.quick(1,D(4));setv(D(4),'y')
    c.alu('cmp',M(2,F['bottom']),4);B(13,'p2a_row')

    L('p2a_no_hit');c.move(I(0),D(3));B(0,'p2a_return')
    L('p2a_hit');c.move(I(1),D(3));B(0,'p2a_return')
    L('p2a_invalid');c.move(I(-1),D(3))
    L('p2a_return')
    c.raw('4fef0040')          # Release 64-byte frame.
    c.raw('4cdf77f7')          # Restore ABI-preserved registers.
    c.raw('74004e75')          # MOVEQ #0,D2; RTS.
    code=c.out()
    if len(code)&1 or len(code)>=32766 or c.labels['p2a_pair_entry']!=0:
        raise ValueError('invalid P2a source PC16 or entry')
    return code, c.labels


if __name__=='__main__':
    source,labels=emit_collision020()
    print('M19 P2a private MC68020 pair collision',len(source),sha256(source).hexdigest(),
          'MODE 0/1; SOURCE_ONLY; NO AP20/Lib/WinUAE')
