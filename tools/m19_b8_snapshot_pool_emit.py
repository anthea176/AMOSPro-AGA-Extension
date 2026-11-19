#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 PRIVATE two-page snapshot allocation pool, MC68020 SOURCE-ONLY.

No public AMOS API/Lib integration; no screen lifecycle hooks here.
The verified caller must pass exact physical Bitmap identities and actual
BytesPerRow*Rows*Depth after validating a live Safe AGA screen. Pool allows
one A5 owner and one screen at a time; all-or-nothing two-page allocation.

Inputs:
  b8_pool_bind_entry:  A5 owner, A0 Screen*, A1 BitMap0*, A2 BitMap1*,
                       D0 size per page (2..2097152, even).
  b8_pool_get_entry:   A5 owner, A0 Screen*, A1 current physical BitMap*.
  b8_pool_close_entry: A5 owner, A0 Screen* (idempotent if unbound).
Outputs: D3 status (1 success, 0 refusal), D2 snapshot pointer for GET,
         D2=0 for BIND/CLOSE; all other AMOS regs preserved.
Exec MEMF_PUBLIC|MEMF_CLEAR allocations are CPU-only backing stores.
Never DMA from these snapshots. NO implicit Swap, no hidden OS wait.
Binding mismatch is fail-closed; closing must be wired before Screen Close
and End to prevent leaks. This module is NOT installed.
"""
from __future__ import annotations
from m68k_emit import Code, D, A, M, I

MEMF_PUBLIC_CLEAR=0x00010001
MAX_PAGE_BYTES=0x00200000
FRAME=96
F=dict(owner=0,screen=4,bitmap0=8,bitmap1=12,bytes=16,
       ptr0=20,ptr1=24,output=28,status=32)
R=dict(owner=0,screen=4,bitmap0=8,ptr0=12,bytes0=16,
       bitmap1=20,ptr1=24,bytes1=28)
ROOT_BYTES=32


def emit_b8_snapshot_pool() -> tuple[bytes,dict[str,int]]:
    c=Code();B,L=c.branch,c.label
    def S(src,key):c.move(src,M(4,F[key]))
    def G(key,dst):c.move(M(4,F[key]),dst)
    def root():c.lea(0,'b8_pool_root')
    def prologue(name):
        L(name)
        c.raw('48e7cfee4fefffa0') # preserves all AMOS regs except D2/D3
        c.move(A(7),A(4))
        S(A(5),'owner');S(A(0),'screen')
        # D0 is an input byte count; preserve it BEFORE CPU guard returns D0=1.
        S(A(1),'bitmap0');S(A(2),'bitmap1');S(D(0),'bytes')
        S(I(0),'output');S(I(0),'status')
        B(1,'b8_pool_cpu_guard')
        c.tst(D(0));B(7,'b8_pool_return')
        for field in ('owner','screen'):
            G(field,D(0));c.tst(D(0));B(7,'b8_pool_return')
            c.imm('and',1,D(0));B(6,'b8_pool_return')
    def compare_root(key,frame,refuse='b8_pool_return'):
        root();c.move(M(0,R[key]),D(0))
        G(frame,D(1));c.alu('cmp',D(1),0);B(6,refuse)
    def check_ptr(field):
        G(field,D(0));c.tst(D(0));B(7,'b8_pool_return')
        c.imm('and',1,D(0));B(6,'b8_pool_return')
        G(field,A(1))
        c.raw('2c780004');c.call_os(-534) # Exec TypeOfMem
        c.tst(D(0));B(7,'b8_pool_return')

    # Bind is transactional: both buffers are allocated or neither.
    prologue('b8_pool_bind_entry')
    G('bytes',D(0));c.imm('cmp',2,D(0));B(5,'b8_pool_return')
    c.imm('cmp',MAX_PAGE_BYTES,D(0));B(2,'b8_pool_return')
    c.imm('and',1,D(0));B(6,'b8_pool_return')
    G('bitmap0',D(0));G('bitmap1',D(1))
    c.alu('cmp',D(1),0);B(7,'b8_pool_return')
    for k in ('owner','screen','bitmap0','bitmap1'):
        check_ptr(k)
    root()
    c.tst(M(0,R['owner']));B(7,'b8_pool_new')
    for key,frame in (('owner','owner'),('screen','screen'),
                      ('bitmap0','bitmap0'),('bitmap1','bitmap1'),
                      ('bytes0','bytes'),('bytes1','bytes')):
        compare_root(key,frame)
    S(I(1),'status') # repeated bind is idempotent; no new allocations
    B(0,'b8_pool_return')
    L('b8_pool_new')
    G('bytes',D(0));c.move(I(MEMF_PUBLIC_CLEAR),D(1))
    c.raw('2c780004');c.call_os(-198) # AllocMem
    c.tst(D(0));B(7,'b8_pool_return')
    S(D(0),'ptr0')
    G('bytes',D(0));c.move(I(MEMF_PUBLIC_CLEAR),D(1))
    c.raw('2c780004');c.call_os(-198)
    c.tst(D(0));B(7,'b8_pool_rollback')
    S(D(0),'ptr1')
    G('ptr0',D(1));c.alu('cmp',D(1),0);B(7,'b8_pool_rollback')
    # Commit only after both AllocMem calls have succeeded.
    root()
    for key,frame in (('owner','owner'),('screen','screen'),
                      ('bitmap0','bitmap0'),('ptr0','ptr0'),
                      ('bytes0','bytes'),('bitmap1','bitmap1'),
                      ('ptr1','ptr1'),('bytes1','bytes')):
        G(frame,D(0));c.move(D(0),M(0,R[key]))
    S(I(1),'status')
    B(0,'b8_pool_return')
    L('b8_pool_rollback')
    G('ptr0',A(1));G('bytes',D(0))
    B(1,'b8_pool_free_mem')
    B(0,'b8_pool_return')

    prologue('b8_pool_get_entry')
    S(A(1),'bitmap0') # lookup key, not a newly chosen source
    compare_root('owner','owner')
    compare_root('screen','screen')
    root();c.tst(M(0,R['ptr0']));B(7,'b8_pool_return')
    c.tst(M(0,R['ptr1']));B(7,'b8_pool_return')
    compare_root('bitmap0','bitmap0','b8_pool_get_second')
    root();c.move(M(0,R['ptr0']),D(0));S(D(0),'output')
    S(I(1),'status');B(0,'b8_pool_return')
    L('b8_pool_get_second')
    compare_root('bitmap1','bitmap0')
    root();c.move(M(0,R['ptr1']),D(0));S(D(0),'output')
    S(I(1),'status');B(0,'b8_pool_return')

    prologue('b8_pool_close_entry')
    root();c.tst(M(0,R['owner']));B(7,'b8_pool_close_empty')
    compare_root('owner','owner')
    compare_root('screen','screen')
    root();c.move(M(0,R['ptr0']),D(0));c.tst(D(0));B(7,'b8_pool_return')
    c.move(M(0,R['ptr1']),D(0));c.tst(D(0));B(7,'b8_pool_return')
    root();c.move(M(0,R['ptr0']),A(1))
    c.move(M(0,R['bytes0']),D(0));B(1,'b8_pool_free_mem')
    root();c.move(M(0,R['ptr1']),A(1))
    c.move(M(0,R['bytes1']),D(0));B(1,'b8_pool_free_mem')
    root()
    for offset in range(0,ROOT_BYTES,4):c.move(I(0),M(0,offset))
    L('b8_pool_close_empty')
    S(I(1),'status')
    B(0,'b8_pool_return')

    L('b8_pool_cpu_guard')
    c.raw('20780004') # MOVEA.L 4.W,A0 ExecBase
    c.move(A(0),D(0));c.tst(D(0));B(7,'b8_pool_cpu_missing')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1) # BTST #AFF_68020,D0
    B(7,'b8_pool_cpu_missing')
    c.move(I(1),D(0));c.raw('4e75')
    L('b8_pool_cpu_missing')
    c.move(I(0),D(0));c.raw('4e75')
    L('b8_pool_free_mem')
    c.raw('2c780004')
    c.call_os(-210) # Exec FreeMem(A1,D0)
    c.raw('4e75')
    L('b8_pool_return')
    G('output',D(2));G('status',D(3))
    c.raw('4fef00604cdf77f34e75')
    L('b8_pool_root')
    c.raw('00'*ROOT_BYTES)
    native=c.out()
    assert c.labels['b8_pool_bind_entry']==0
    assert c.labels['b8_pool_get_entry']<c.labels['b8_pool_close_entry']
    assert c.labels['b8_pool_root']+ROOT_BYTES==len(native)
    assert len(native)<32766 and len(native)%2==0
    return native,c.labels


if __name__=='__main__':
    from hashlib import sha256
    data,labels=emit_b8_snapshot_pool()
    print('M19 B8 private two-page pool MC68020 SOURCE ONLY',
          len(data),sha256(data).hexdigest())
