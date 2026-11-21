#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2a private native P1b signed hotspot pairs from REAL AGBO bank directory.

Input A0 = P0f/P0j-validated 120-byte Bob+Chip pairs, A1 = trusted
8-byte output, A4 = PRIVATE P0j-b1 explicit_bank_lookup_entry, A5=owner.
D3=1 only if both real bank identities, images and P0j staged Chip
descriptors still agree. Output [Ax WORD][Ay WORD][Bx WORD][By WORD] signed,
D2=0, all other AMOS regs and stack preserved. D3=0 leaves output intact.

The P0j-b1 lookup revalidates the ORIGINAL bank payload/generation and
staged Chip allocation without touching selected-bank shadow. AGBO
directory walking follows source-verified P1b +28/+30, word aligned.
After both scans, redo BOTH lookups and compare all seven identity LONGs
before publishing. Bank edits/reentrant memory changes must still be
forbidden during this synchronous operation. No public AP20 or Lib.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code,A,D,M,I,POST
from m19_p1b_hotspot_origin_emit import HOT_X,HOT_Y
from m19_p0j_explicit_bank_lookup_emit import OUTPUT_BYTES as LOOKUP_BYTES

FRAME=192
PAIR_BYTES=120
OUTPUT_BYTES=8
LOOKUP=(48,80)
VERIFY=112
HOT=144
assert LOOKUP_BYTES==28 and HOT+OUTPUT_BYTES<FRAME and (HOT_X,HOT_Y)==(28,30)
F=dict(pair=0,out=4,callback=8,result=12,count=16,image=20)

def emit_p2a_pair_hotspot020()->tuple[bytes,dict[str,int]]:
    c=Code();B,L=c.branch,c.label
    def S(src,name):c.move(src,M(2,F[name]))
    def G(name,dst):c.move(M(2,F[name]),dst)
    def ptr(off,reg=1):
        c.move(A(2),D(4));c.imm('add',off,D(4));c.move(D(4),A(reg))
    def lookup(i,slot):
        G('pair',A(0))
        c.move(M(0,60*i),D(3))
        ptr(slot)
        G('callback',A(4))
        c.raw('4e94') # JSR (A4), real P0j-b1 source
        c.tst(D(3));B(7,'p2a_hot_refuse')

    L('p2a_pair_hotspot_entry')
    c.raw('48e7efee4fefff40') # save AMOS regs, 192B stack
    c.move(A(7),A(2))
    S(A(0),'pair');S(A(1),'out');S(A(4),'callback')
    S(I(0),'result')
    for key in ('pair','out','callback'):
        G(key,D(4));c.tst(D(4));B(7,'p2a_hot_refuse')
        c.imm('and',1,D(4));B(6,'p2a_hot_refuse')
    # Obtain the two *current source* AGBO directories by exact P0j-b1
    # code and compare image dimensions/stride/depth to 36B Chip records.
    for i in (0,1):
        lookup(i,LOOKUP[i])
        G('pair',A(1))
        c.move(M(1,60*i+4),D(1));S(D(1),'image')
        c.imm('cmp',1,D(1));B(5,'p2a_hot_refuse')
        c.imm('cmp',4096,D(1));B(2,'p2a_hot_refuse')
        c.move(M(2,LOOKUP[i]),D(4));c.tst(D(4))
        B(7,'p2a_hot_refuse')
        c.move(D(4),A(0))
        c.move(I(0),D(4));c.move(M(0,8),D(4),'w')
        c.imm('cmp',1,D(4));B(5,'p2a_hot_refuse')
        c.imm('cmp',4096,D(4));B(2,'p2a_hot_refuse')
        S(D(4),'count')
        c.move(A(0),D(4));c.imm('add',32,D(4))
        B(5,'p2a_hot_refuse')
        c.move(D(4),A(0))
        tag=f'p2a_h{i}'
        L(tag+'_scan')
        c.move(I(0),D(4));c.move(M(0,0),D(4),'w')
        G('image',D(5));c.alu('cmp',D(5),4)
        B(7,tag+'_found')
        c.move(A(0),D(4));c.imm('add',40,D(4))
        B(5,'p2a_hot_refuse')
        c.move(D(4),A(0))
        G('count',D(4));c.quick(1,D(4),sub=True);S(D(4),'count')
        B(6,tag+'_scan')
        B(0,'p2a_hot_refuse')
        L(tag+'_found')
        # Host has already validated the whole AGBO via P0j-b3. Recheck
        # directory entry dimensions vs the staged Chip snapshot.
        G('pair',A(1))
        for entryoff,chipoff in ((2,60*i+24+8),(4,60*i+24+12),
                                 (6,60*i+24+20),(8,60*i+24+16)):
            c.move(I(0),D(4));c.move(M(0,entryoff),D(4),'w')
            c.alu('cmp',M(1,chipoff),4)
            B(6,'p2a_hot_refuse')
        for wordoff,dst in ((HOT_X,HOT+i*4),(HOT_Y,HOT+i*4+2)):
            c.move(M(0,wordoff),D(4),'w')
            c.move(D(4),M(2,dst),'w')

    # Recheck all seven LONGs of both lookups after both directories scanned.
    for i in (0,1):
        lookup(i,VERIFY)
        for off in range(0,LOOKUP_BYTES,4):
            c.move(M(2,VERIFY+off),D(4))
            c.alu('cmp',M(2,LOOKUP[i]+off),4)
            B(6,'p2a_hot_refuse')

    G('out',A(0))
    for off in (0,2,4,6):
        c.move(M(2,HOT+off),D(4),'w')
        c.move(D(4),POST(0),'w')
    S(I(1),'result')
    L('p2a_hot_refuse')
    G('result',D(3))
    c.raw('4fef00c04cdf77f774004e75')
    raw=c.out()
    if len(raw)%2 or len(raw)>=32766 or c.labels['p2a_pair_hotspot_entry']!=0:
        raise ValueError('P2a AGBO hotspot source/ABI/PC16 drift')
    return raw,c.labels

if __name__=='__main__':
    raw,_=emit_p2a_pair_hotspot020()
    print('P2A source-only P0j/P1b verified AGBO hotspot MC68020',len(raw),sha256(raw).hexdigest())
