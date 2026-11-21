#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2a native geometric descriptor packer (private, independent MC68020).

Trusted PRIVATE sources:
 D0/D1 Bob IDs in 1..64; A0 checked P0f+P0j pair, 120 bytes;
 A1 logical screen two LONGs width,height (1..4096);
 A3 two AGBO hotspot pairs of signed WORDs in A,B order (8 bytes);
 A4 P1d canonical 65-slot limit table, 16 bytes/slot, zero means disabled;
 A6 owned contiguous writable 80-byte output.
 On D3=1 publish two 40-byte descriptors accepted by collision020, D2=0.
 On D3=0 leave 80 output bytes UNCHANGED. All other AMOS regs+SP preserved.

Input hotspot words MUST have been read from VERIFIED original AGBO
entries (P1b source contract offsets +28,+30); NOT read from Chip pixels.
Input pair MUST be atomically returned by P0f+P0j and both masks/allocations
must stay alive until the collision call. The P1d table MUST be owned by
the current validated screen and not mutate during this synchronous query.
No persistent source bank selection, AP20, DMA, Lib build, WinUAE or Compiler.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code, D, A, M, I, POST
from m19_p1b_hotspot_origin_emit import HOT_X, HOT_Y
from m19_p1d_limit_bob_emit import SLOT_BYTES, SLOTS
from m19_p2a_collision020_emit import DESCRIPTOR_BYTES

FRAME=256
PAIR_BYTES=120
OUTPUT_BYTES=80
TMP=(112,152)
F=dict(id_a=0,id_b=4,pair=8,screen=12,hot=16,limits=20,
       out=24,result=28,screen_w=32,screen_h=36)
assert (DESCRIPTOR_BYTES, HOT_X, HOT_Y, SLOT_BYTES, SLOTS) == (40,28,30,16,65)
assert TMP[1]+DESCRIPTOR_BYTES<=FRAME

def emit_p2a_pair_geometry020() -> tuple[bytes,dict[str,int]]:
    c=Code();B,L=c.branch,c.label
    def S(src,name):c.move(src,M(2,F[name]))
    def G(name,dst):c.move(M(2,F[name]),dst)
    def checked_id(name):
        G(name,D(4));c.imm('cmp',1,D(4));B(5,'p2a_geo_reject')
        c.imm('cmp',64,D(4));B(2,'p2a_geo_reject')
    def footprint(which):
        objoff=which*60;imgoff=objoff+24;hot_off=which*4;tmp=TMP[which]
        ident=('id_a','id_b')[which];tag=f'p2a_g{which}'
        # Validate records from P0f/P0j before touching any mask pointer.
        G('pair',A(0))
        c.move(M(0,objoff+16),D(4));c.imm('cmp',1,D(4));B(6,'p2a_geo_reject')
        c.move(M(0,objoff+20),D(4));c.tst(D(4));B(6,'p2a_geo_reject')
        for off in (imgoff+8,imgoff+12):
            c.move(M(0,off),D(4))
            c.imm('cmp',1,D(4));B(5,'p2a_geo_reject')
            c.imm('cmp',4096,D(4));B(2,'p2a_geo_reject')
        c.move(M(0,imgoff+8),D(4));c.imm('add',15,D(4))
        c.shift(4,4,left=False);c.shift(4,1,left=True)
        c.alu('cmp',M(0,imgoff+16),4);B(6,'p2a_geo_reject')
        # Plane size and mask stride were independently checked by P0j-b3.
        c.move(M(0,imgoff+16),D(4))
        c.move(M(0,imgoff+12),D(5))
        c.word(0xc8c5)  # MULU.W D5,D4 -> stride * height
        c.alu('cmp',M(0,imgoff+24),4);B(6,'p2a_geo_reject')
        c.move(M(0,imgoff+4),D(4));c.imm('and',1,D(4));B(6,'p2a_geo_reject')
        # Origin = logical Bob anchor - signed AGBO 16-bit hotspot.
        G('hot',A(3))
        for axis,coord,wordoff,origin in (
                ('x',objoff+8,hot_off+0,16),
                ('y',objoff+12,hot_off+2,20)):
            G('pair',A(0))
            c.move(M(0,coord),D(5))
            c.move(M(3,wordoff),D(4),'w')
            c.word(0x48c4) # EXT.L D4 (source P1b signed WORD)
            c.alu('sub',D(4),5)
            c.move(D(5),M(2,tmp+origin))
            c.move(D(5),M(2,tmp+(0 if axis=='x' else 4)))
        # Right/bottom exclusive, LONG maths (signed origin + positive size).
        for axis,wh,slot in (('x',imgoff+8,8),('y',imgoff+12,12)):
            c.move(M(2,tmp+(16 if axis=='x' else 20)),D(4))
            G('pair',A(0));c.alu('add',M(0,wh),4)
            c.move(D(4),M(2,tmp+slot))
        # Remaining geometry mirrors native collision020, original sizes.
        G('pair',A(0))
        for original,output in ((imgoff+8,24),(imgoff+12,28),
                                (imgoff+16,32),(imgoff+4,36)):
            c.move(M(0,original),D(4));c.move(D(4),M(2,tmp+output))
        # Intersect [0,screenWidth) and [0,screenHeight).
        for pos,maximum in ((0,'screen_w'),(4,'screen_h')):
            c.move(M(2,tmp+pos),D(4));c.tst(D(4))
            B(12,f'{tag}_left_ok_{pos}')
            c.move(I(0),M(2,tmp+pos))
            L(f'{tag}_left_ok_{pos}')
            c.move(M(2,tmp+pos+8),D(4));G(maximum,D(5))
            c.alu('cmp',D(5),4)
            B(15,f'{tag}_right_ok_{pos}')
            c.move(D(5),M(2,tmp+pos+8))
            L(f'{tag}_right_ok_{pos}')
        # Intersect stored P1d global slot 0 and local slot Bob ID.
        for zone in ('global','local'):
            G('limits',D(4))
            if zone=='local':
                G(ident,D(5));c.shift(5,4,left=True)
                c.alu('add',D(5),4)
            c.move(D(4),A(4))
            for off in (0,4,8,12):
                c.move(M(4,off),D(4));c.tst(D(4))
                B(6,f'{tag}_{zone}_set')
            B(0,f'{tag}_{zone}_done')
            L(f'{tag}_{zone}_set')
            # P1d only stores canonical positive-area rectangles.
            for start,end in ((0,8),(4,12)):
                c.move(M(4,end),D(4));c.alu('cmp',M(4,start),4)
                B(15,'p2a_geo_reject')
            for pos,zonepos,kind in ((0,0,'max'),(4,4,'max'),
                                     (8,8,'min'),(12,12,'min')):
                c.move(M(2,tmp+pos),D(4))
                c.move(M(4,zonepos),D(5));c.alu('cmp',D(5),4)
                label=f'{tag}_{zone}_clip_{pos}'
                B(12 if kind=='max' else 15,label)
                c.move(D(5),M(2,tmp+pos))
                L(label)
            L(f'{tag}_{zone}_done')
        # Canonical empty footprint [0,0,0,0] reports no hit, not refusal.
        for low,high in ((0,8),(4,12)):
            c.move(M(2,tmp+high),D(4));c.alu('cmp',M(2,tmp+low),4)
            B(15,f'{tag}_empty')
        B(0,f'{tag}_complete')
        L(f'{tag}_empty')
        for off in (0,4,8,12):c.move(I(0),M(2,tmp+off))
        L(f'{tag}_complete')

    L('p2a_pair_geometry_entry')
    c.raw('48e7efee4fefff00') # 256-byte private stack frame, AMOS ABI
    c.move(A(7),A(2))
    for name,reg in (('id_a',D(0)),('id_b',D(1)),('pair',A(0)),
                     ('screen',A(1)),('hot',A(3)),('limits',A(4)),
                     ('out',A(6))):S(reg,name)
    S(I(0),'result')
    checked_id('id_a');checked_id('id_b')
    G('id_a',D(4));c.alu('cmp',M(2,F['id_b']),4)
    B(7,'p2a_geo_reject')
    # All buffers trusted engine-owned; reject obvious invalid pointers.
    for name in ('pair','screen','hot','limits','out'):
        G(name,D(4));c.tst(D(4));B(7,'p2a_geo_reject')
        c.imm('and',1,D(4));B(6,'p2a_geo_reject')
    G('screen',A(1))
    for pos,name in ((0,'screen_w'),(4,'screen_h')):
        c.move(M(1,pos),D(4))
        c.imm('cmp',1,D(4));B(5,'p2a_geo_reject')
        c.imm('cmp',4096,D(4));B(2,'p2a_geo_reject')
        S(D(4),name)
    footprint(0);footprint(1)
    # Commit after both footprints pass. Never publish a partial descriptor.
    G('out',A(0))
    for temp in TMP:
        for off in range(0,DESCRIPTOR_BYTES,4):
            c.move(M(2,temp+off),D(4));c.move(D(4),POST(0))
    S(I(1),'result')
    L('p2a_geo_reject')
    G('result',D(3))
    c.raw('4fef01004cdf77f774004e75')
    raw=c.out()
    if not (len(raw)<32766 and len(raw)%2==0 and
            c.labels['p2a_pair_geometry_entry']==0):
        raise ValueError('P2a descriptor native PC16/ABI mismatch')
    return raw,c.labels

if __name__=='__main__':
    raw,_=emit_p2a_pair_geometry020()
    print('P2a native 2x40 geometry',len(raw),sha256(raw).hexdigest(),
          'SOURCE_ONLY; HOTSPOTS/LIMITS MUST BE SOURCE-VALIDATED')
