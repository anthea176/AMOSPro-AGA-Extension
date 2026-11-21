#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P2a: PRIVATE 68020 pair checked-read adapter (source-only).

Use REAL existing P0f identity_check, not P0e raw object_read.
Input: D0=Bob A ID, D1=Bob B ID, A1=caller-owned 48-byte output,
       A4=TRUSTED PRIVATE identity_check entry, A5=AMOS owner.
Output: D3=1 only if both distinct active Bob IDs 1..64 pass native P0f
        source-bank/stamp revalidation. Otherwise D3=0 and all 48 output
        bytes stay untouched. D2=0; other AMOS registers + SP preserved.
Output consists of two consecutive unmodified 24-byte native P0e records.

Caller MUST use a source-verified A4 callback, not a public-provided pointer.
Exec TypeOfMem checks output endpoints; this does not prove the entire 48-byte
region contiguous or guarantee lifetime, so caller MUST provide valid owned
writable scratch. A5/CPU/Bnk.GetAdr/generation are checked by the REAL P0f
callback. A synchronous query is required: no concurrent mutation/reentrancy.
This adapter does NOT resolve image IDs, read mask bytes, build 40-byte P2a
collision descriptors, call the collision kernel, or publish an AP20 token.
No selection, allocation, render, DMA, WaitBlit, Swap or .Lib modification.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code, A, D, I, M, POST

FRAME=128
OBJECT_BYTES=24
PAIR_BYTES=OBJECT_BYTES*2
OFF=dict(id_a=0,id_b=4,output=8,callback=12,result=16)
SCRATCH_A=32
SCRATCH_B=SCRATCH_A+OBJECT_BYTES
assert SCRATCH_B+OBJECT_BYTES<=FRAME


def emit_p2a_pair_checked_read() -> tuple[bytes,dict[str,int]]:
    c=Code();B,L=c.branch,c.label
    def keep(src,key):c.move(src,M(2,OFF[key]))
    def read(key,dst):c.move(M(2,OFF[key]),dst)
    L('p2a_pair_checked_read_entry')
    c.raw('48e7efee')        # Preserve AMOS regs except D2 and D3
    c.raw('4fefff80')        # LEA -128(SP),SP
    c.move(A(7),A(2))      # Private stack frame
    keep(D(0),'id_a')
    keep(D(1),'id_b')
    keep(A(1),'output')
    keep(A(4),'callback')
    keep(I(0),'result')
    for key in ('id_a','id_b'):
        read(key,D(0))
        c.imm('cmp',1,D(0));B(5,'p2a_pair_fail')  # below 1
        c.imm('cmp',64,D(0));B(2,'p2a_pair_fail') # above 64
    read('id_a',D(0))
    c.alu('cmp',M(2,OFF['id_b']),0);B(7,'p2a_pair_fail')
    for key in ('callback','output'):
        read(key,D(0));c.tst(D(0));B(7,'p2a_pair_fail')
        c.imm('and',1,D(0));B(6,'p2a_pair_fail')
    # Check the owned 48-byte output's two endpoints via Exec TypeOfMem.
    # The destination MUST be a trusted contiguous caller scratch buffer.
    for end in (0,PAIR_BYTES-1):
        read('output',D(0))
        if end:
            c.imm('add',end,D(0));B(5,'p2a_pair_fail')
        c.move(D(0),A(1))
        c.raw('2c780004')  # MOVEA.L 4.W,A6: ExecBase
        c.call_os(-534)    # Exec TypeOfMem(A1)
        c.tst(D(0));B(7,'p2a_pair_fail')
    # Reuse source-exact P0f's *checked* read, not the unsafe raw object read.
    # PRIVATE trusted A4 callback address is relocated by the caller.
    for key,scratch in (('id_a',SCRATCH_A),('id_b',SCRATCH_B)):
        read(key,D(0))
        c.move(A(2),D(1))
        c.imm('add',scratch,D(1))
        c.move(D(1),A(1))
        read('callback',A(4))
        c.raw('4e94')       # JSR (A4) identity_check
        c.tst(D(3));B(7,'p2a_pair_fail')
    # Only now publish the pair: failure after either check cannot leak one.
    read('output',A(0))
    for scratch in (SCRATCH_A,SCRATCH_B):
        for offset in range(0,OBJECT_BYTES,4):
            c.move(M(2,scratch+offset),D(1))
            c.move(D(1),POST(0))
    keep(I(1),'result')
    L('p2a_pair_fail')
    read('result',D(3))
    c.raw('4fef0080')       # LEA +128(SP),SP
    c.raw('4cdf77f7')       # MOVEM.L preserved regs,(SP)+
    c.raw('74004e75')       # MOVEQ #0,D2 / RTS
    raw=c.out()
    if (not raw.startswith(bytes.fromhex('48e7efee4fefff80')) or
            c.labels['p2a_pair_checked_read_entry'] != 0 or
            len(raw)&1 or len(raw)>=32766):
        raise ValueError('P2a MC68020 private pair read ABI/PC16 violated')
    return raw,c.labels


if __name__=='__main__':
    raw,labels=emit_p2a_pair_checked_read()
    print('M19 P2a PRIVATE MC68020 P0f PAIR CHECK',len(raw),sha256(raw).hexdigest(),
          'SOURCE ONLY; no AGBO image resolver, token, Lib or WinUAE')
