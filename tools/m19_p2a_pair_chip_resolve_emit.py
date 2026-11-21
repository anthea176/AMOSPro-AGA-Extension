#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P2a private MC68020 paired P0f+P0j-b3 Chip image resolution.

Prefix is the exact P2a P0f pair-checked reader (source-built, unmodified).
New entry resolves BOTH checked objects with the existing source-verifiable
P0j-b3 explicit_bank_image_resolve_entry. Only after both images resolve and
the objects are rechecked is the 120-byte result published atomically.

Input:  D0=Bob A ID, D1=Bob B ID, A1=TRUSTED 120-byte writable result,
        A4=TRUSTED P0f identity_check_entry, A6=TRUSTED P0j-b3
        explicit_image_resolve_entry, A5=AMOS owner.
Output: D3=1/0, D2=0, others and SP unchanged.
Output: A 24-byte P0e record, A 36-byte P0j image descriptor,
        B 24-byte P0e record, B 36-byte P0j image descriptor.

P0j Chip cache MUST ALREADY be staged for both bank IDs. This routine does
NOT prepare/freeze bank memory, choose selected bank, allocate Chip, draw,
Swap, inspect sprites, read hotspot metadata or apply P1d limits.
Callbacks are private source-resolved code pointers, never AMOS arguments.
Scratch/output spans must be supplied by trusted engine; TypeOfMem endpoint
checks do not prove full intermediate mapped extent. Synchronous use only.
No public AP20 token, Lib build, WinUAE/Compiler validation or promotion.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code, D, A, M, I, POST
from m19_p2a_pair_checked_read_emit import emit_p2a_pair_checked_read

FRAME=256
PAIR=64
IMAGE_A=120
IMAGE_B=156
RECHECK=200
OBJECT_BYTES=24
IMAGE_BYTES=36
OUTPUT_BYTES=2*(OBJECT_BYTES+IMAGE_BYTES)
assert RECHECK+2*OBJECT_BYTES<=FRAME
PREVIOUS,PREVIOUS_LABELS=emit_p2a_pair_checked_read()
F=dict(id_a=0,id_b=4,out=8,checked=12,resolver=16,result=20)


def emit_p2a_pair_chip_resolve() -> tuple[bytes,dict[str,int]]:
    c=Code()
    c.raw(PREVIOUS.hex())
    c.labels.update(PREVIOUS_LABELS)
    B,L=c.branch,c.label
    def S(src,key): c.move(src,M(2,F[key]))
    def G(key,dst): c.move(M(2,F[key]),dst)
    def ptr(offset,reg=1):
        c.move(A(2),D(4))
        c.imm('add',offset,D(4))
        c.move(D(4),A(reg))

    L('p2a_pair_chip_resolve_entry')
    c.raw('48e7efee')           # AMOS ABI, D2/D3 result only
    c.raw('4fefff00')           # LEA -256(SP),SP
    c.move(A(7),A(2))
    S(D(0),'id_a');S(D(1),'id_b')
    S(A(1),'out');S(A(4),'checked');S(A(6),'resolver')
    S(I(0),'result')
    # Validate callback/output pointers before first call or write.
    for name in ('checked','resolver','out'):
        G(name,D(0));c.tst(D(0));B(7,'p2a_pair_chip_return')
        c.imm('and',1,D(0));B(6,'p2a_pair_chip_return')
    # The output is trusted engine scratch. Check endpoint mappings.
    for delta in (0, OUTPUT_BYTES-1):
        G('out',D(0))
        if delta:
            c.imm('add',delta,D(0));B(5,'p2a_pair_chip_return')
        c.move(D(0),A(1))
        c.raw('2c780004')       # ExecBase -> A6
        c.call_os(-534)         # TypeOfMem
        c.tst(D(0));B(7,'p2a_pair_chip_return')
    # Capture two checked active P0e records at once; rejects stale stamps.
    G('id_a',D(0));G('id_b',D(1))
    ptr(PAIR)
    G('checked',A(4))
    B(1,'p2a_pair_checked_read_entry')
    c.tst(D(3));B(7,'p2a_pair_chip_return')

    # Resolve Chip image descriptors, by ORIGINAL bank, not selected shadow.
    for start,dst in ((PAIR,IMAGE_A),(PAIR+OBJECT_BYTES,IMAGE_B)):
        c.move(M(2,start+0),D(3)) # bank from P0e checked record
        c.move(M(2,start+4),D(0)) # image ID from P0e
        ptr(dst)
        G('resolver',A(6))
        c.raw('4e96')           # JSR (A6): source-pinned P0j-b3
        c.tst(D(3));B(7,'p2a_pair_chip_return')

    # Recheck both P0f stamps to protect a synchronous query from a late
    # bank-generation mutation inside either resolver/service callback.
    G('id_a',D(0));G('id_b',D(1))
    ptr(RECHECK)
    G('checked',A(4))
    B(1,'p2a_pair_checked_read_entry')
    c.tst(D(3));B(7,'p2a_pair_chip_return')
    for offset in range(0,2*OBJECT_BYTES,4):
        c.move(M(2,PAIR+offset),D(4))
        c.alu('cmp',M(2,RECHECK+offset),4)
        B(6,'p2a_pair_chip_return')

    # Atomic publication to caller: two immutable 60-byte (Bob,Image) pairs.
    G('out',A(0))
    for obj,img in ((PAIR,IMAGE_A),(PAIR+OBJECT_BYTES,IMAGE_B)):
        for off in range(0,OBJECT_BYTES,4):
            c.move(M(2,obj+off),D(4))
            c.move(D(4),POST(0))
        for off in range(0,IMAGE_BYTES,4):
            c.move(M(2,img+off),D(4))
            c.move(D(4),POST(0))
    S(I(1),'result')
    L('p2a_pair_chip_return')
    G('result',D(3))
    c.raw('4fef0100')          # Release 256-byte frame
    c.raw('4cdf77f7')          # Preserve D0,D1,D4..7,A0..A6
    c.raw('74004e75')          # D2=0, RTS
    raw=c.out()
    if not (raw.startswith(PREVIOUS) and
            c.labels['p2a_pair_chip_resolve_entry']==len(PREVIOUS) and
            c.labels['p2a_pair_checked_read_entry']==0 and
            len(raw)%2==0 and len(raw)<32766):
        raise ValueError('P2a pair Chip source/ABI/PC16 drift')
    return raw,c.labels


if __name__=='__main__':
    raw,labels=emit_p2a_pair_chip_resolve()
    print('M19 P2a P0f+P0j MC68020 CHIP PAIR SOURCE ONLY',
          len(raw),sha256(raw).hexdigest(),len(PREVIOUS))
