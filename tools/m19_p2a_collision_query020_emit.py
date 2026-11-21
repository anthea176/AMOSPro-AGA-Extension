#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P2a ONE native Bob-vs-Bob collision query, PRIVATE MC68020.

Input D0=Bob A ID, D1=Bob B ID, D4=mode (0 rect / 1 mask).
A1 -> trusted 8-byte context [screen dimensions pointer, P1d table pointer].
A4 -> TRUSTED INTERNAL callback table, seven LONGs:
  0 P2a paired P0f+P0j-b3 120-byte Chip resolver,
  4 P0f identity_check, 8 P0j-b3 image resolver,
 12 P2a signed hotspot reader, 16 P0j-b1 explicit bank lookup,
 20 P2a signed-hotspot/P1d geometry builder,
 24 P2a pixel/rectangle collision kernel.
A5=owner AMOS. Output D2=0, D3=1 collision / 0 no hit /
-1 any invalid private input, source identity or callback failure.
All other AMOS registers, stack, Bob state, selected bank, Chip untouched.

No output allocation: internal 120+8+80B reside in a private 352B stack.
Source callbacks must point to source-pinned PRIVATE code, never supplied
by AMOS callers. P0j staged source Chip allocations and P1d screen context
must already exist, remain stable during this synchronous native call.
No AP20, new Lib, DMA, Swap, WinUAE or Compiler qualification.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code,D,A,M,I
from m19_p2a_pair_chip_resolve_emit import OUTPUT_BYTES as PAIR_BYTES
from m19_p2a_pair_hotspot020_emit import OUTPUT_BYTES as HOT_BYTES
from m19_p2a_pair_geometry020_emit import OUTPUT_BYTES as DESC_BYTES

FRAME=352
PAIR=48
HOT=176
DESC=192
CALLBACK_BYTES=28
CONTEXT_BYTES=8
assert (PAIR_BYTES,HOT_BYTES,DESC_BYTES)==(120,8,80)
assert DESC+DESC_BYTES<=FRAME and PAIR+PAIR_BYTES<=HOT
F=dict(id_a=0,id_b=4,mode=8,context=12,callback=16,result=20)

def emit_p2a_collision_query020()->tuple[bytes,dict[str,int]]:
    c=Code();B,L=c.branch,c.label
    def S(src,name):c.move(src,M(2,F[name]))
    def G(name,dst):c.move(M(2,F[name]),dst)
    def ptr(off,register):
        c.move(A(2),D(5));c.imm('add',off,D(5));c.move(D(5),A(register))
    def reject_if_null_odd(register):
        c.move(register,D(5));c.tst(D(5));B(7,'p2a_query_invalid')
        c.imm('and',1,D(5));B(6,'p2a_query_invalid')

    L('p2a_collision_query_entry')
    c.raw('48e7efee4feffea0') # MOVEM AMOS ABI, frame -352(SP)
    c.move(A(7),A(2))
    S(D(0),'id_a');S(D(1),'id_b')
    S(D(4),'mode');S(A(1),'context');S(A(4),'callback')
    S(I(-1),'result')
    G('mode',D(5))
    c.imm('cmp',1,D(5));B(2,'p2a_query_return')
    for name in ('context','callback'):
        G(name,D(5));c.tst(D(5));B(7,'p2a_query_return')
        c.imm('and',1,D(5));B(6,'p2a_query_return')
    G('context',A(1))
    for off in (0,4):
        c.move(M(1,off),D(5));c.tst(D(5))
        B(7,'p2a_query_return')
        c.imm('and',1,D(5));B(6,'p2a_query_return')
    G('callback',A(4))
    for off in range(0,CALLBACK_BYTES,4):
        c.move(M(4,off),D(5));c.tst(D(5))
        B(7,'p2a_query_return')
        c.imm('and',1,D(5));B(6,'p2a_query_return')

    # 1. Real P0f checks -> 2 real P0j-b3 Chip descriptors -> recheck.
    G('id_a',D(0));G('id_b',D(1));ptr(PAIR,1)
    G('callback',A(4))
    c.move(M(4,0),A(3)) # P2a pair Chip entry
    c.move(M(4,4),A(4)) # real P0f callback
    G('callback',A(6));c.move(M(6,8),A(6)) # P0j-b3 callback
    c.raw('4e93') # JSR (A3)
    c.tst(D(3));B(7,'p2a_query_return')

    # 2. Live P1b signed hotspot lookup from both SOURCE AGBO directories.
    ptr(PAIR,0);ptr(HOT,1)
    G('callback',A(4))
    c.move(M(4,12),A(3)) # hotspot routine
    c.move(M(4,16),A(4)) # P0j-b1 private lookup
    c.raw('4e93')
    c.tst(D(3));B(7,'p2a_query_return')

    # 3. Logical screen/P1d clipping -> two private 40-byte descriptors.
    G('id_a',D(0));G('id_b',D(1))
    ptr(PAIR,0)
    G('context',A(1));c.move(M(1,0),A(1))
    ptr(HOT,3)
    G('context',A(4));c.move(M(4,4),A(4))
    ptr(DESC,6)
    G('callback',A(2));c.move(M(2,20),A(2))
    c.raw('4e92')  # JSR (A2), preserves A2
    c.move(A(7),A(2))
    c.tst(D(3));B(7,'p2a_query_return')

    # 4. Execute real 764-byte pixel-exact MC68020 kernel.
    G('mode',D(0));ptr(DESC,0);ptr(DESC+40,1)
    G('callback',A(2));c.move(M(2,24),A(2))
    c.raw('4e92')
    c.move(A(7),A(2))
    S(D(3),'result')
    L('p2a_query_return')
    G('result',D(3))
    c.raw('4fef01604cdf77f774004e75')
    raw=c.out()
    if (len(raw)%2 or len(raw)>=32766 or
            c.labels['p2a_collision_query_entry']!=0):
        raise ValueError('P2a native collision query ABI/PC16 invalid')
    return raw,c.labels

if __name__=='__main__':
    raw,_=emit_p2a_collision_query020()
    print('P2A ONE-CALL private MC68020 collision query',len(raw),sha256(raw).hexdigest(),
          'SOURCE_ONLY')
