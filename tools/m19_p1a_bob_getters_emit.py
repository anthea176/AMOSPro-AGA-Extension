#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1a: public numeric Bob X/Y/I getters in the REACHABLE fifth AP20 unit.

Exact P0 fifth native Bank Free bridge is a byte-identical prefix.
New private read bridge applies the same callback/marker/TypeOfMem guards
as P0 Bank Free, but targets the source-pinned P0 BOBS relay_read_entry.
No absolute inter-unit address and NO signed 16-bit jump across islands.
The BOBS source and object table are not modified.

AMOS input: D3=Bob number 1..64. Output: D2=0; D3=value or -32769.
A3, A5 and all other AMOS non-result registers are preserved.
Refusal is outside valid signed XY [-32768..32767] and image [1..4096].
"""
from __future__ import annotations

from struct import unpack_from
from m68k_emit import Code, A, D, I, M
from m19_b8_s1_bank_free_bridge_emit import (
    emit_b8_s1_bank_free_bridge, MAGIC,
)
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free

INVALID=-32769
FIELDS=dict(x=8,y=12,image=4)
FRAME=64
F=dict(result=0,ident=4,output=8,callback=12,target=16,marker=20)


def emit_m19_p1a_getters() -> tuple[bytes,dict[str,int]]:
    old,labels=emit_b8_s1_bank_free_bridge()
    bobs,bel=emit_b8_s1_bank_free()
    needed=('b7_end_entry','b8_b7_end_trampoline_entry',
            'b8_b7_register_magic','relay_read_entry')
    if any(k not in bel for k in needed):
        raise ValueError('Missing exact P0 split Bob relay or End callback')
    b7,shim,mark,read=(bel[k] for k in needed)
    if any(x<0 or x>=32766 or x&1 for x in (b7,shim,mark,read)):
        raise ValueError('BOBS native source offset/ABI invalid')
    sig=bobs[read:read+8]
    if len(sig)!=8 or sig[:4]!=bytes.fromhex('48e7efee'):
        raise ValueError('P0 relay_read source signature unexpectedly changed')
    signature=unpack_from('>II',sig)
    pairs=((mark-b7,read-b7),(mark-shim,read-shim))
    if (pairs[0]==pairs[1] or any(mark_delta<=0 for mark_delta,_ in pairs)
            or any(target_delta==0 for _,target_delta in pairs)):
        raise ValueError('P0 callback-derived BOBS read target invalid')
    c=Code()
    c.raw(old.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,key):c.move(src,M(4,F[key]))
    def G(key,dst):c.move(M(4,F[key]),dst)
    def mapped(reg,failed='p1a_read_bridge_return'):
        c.move(reg,A(1))
        c.raw('2c780004')          # MOVEA.L 4.W,A6 = ExecBase
        c.call_os(-534)           # Exec TypeOfMem
        c.tst(D(0));B(7,failed)

    L('p1a_read_bridge_entry')
    c.raw('48e7cfee4fefffc0')  # P0 fifth-group bridge ABI, 64-byte frame
    c.move(A(7),A(4))
    S(D(0),'ident');S(A(1),'output');S(I(0),'result')

    # Reject non-020, bad AMOS owner and invalid Bob ID before dereferencing.
    c.raw('20780004')
    c.move(A(0),D(0));c.tst(D(0));B(7,'p1a_read_bridge_return')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1);B(7,'p1a_read_bridge_return')
    c.move(A(5),D(0));c.tst(D(0));B(7,'p1a_read_bridge_return')
    c.imm('and',1,D(0));B(6,'p1a_read_bridge_return')
    mapped(A(5))
    G('ident',D(0));c.imm('cmp',1,D(0));B(5,'p1a_read_bridge_return')
    c.imm('cmp',64,D(0));B(2,'p1a_read_bridge_return')
    G('output',D(0));c.tst(D(0));B(7,'p1a_read_bridge_return')
    c.imm('and',1,D(0));B(6,'p1a_read_bridge_return')
    G('output',A(1));c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'p1a_read_bridge_return')
    G('output',D(0));c.imm('add',23,D(0))
    B(5,'p1a_read_bridge_return')
    mapped(D(0))

    # P0's original validated B7/B8 End callback is our relocation anchor.
    c.move(M(5,0x1cc),D(0));c.tst(D(0));B(7,'p1a_read_bridge_return')
    c.move(M(5,0x1d0),D(1));c.alu('cmp',D(1),0)
    B(6,'p1a_read_bridge_return')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'p1a_read_bridge_return')
    S(D(0),'callback')
    mapped(D(0))
    G('callback',D(0));c.imm('add',3,D(0))
    B(5,'p1a_read_bridge_return')
    mapped(D(0))
    G('callback',A(0));c.move(M(0,0),D(0))
    c.imm('cmp',0x48e7fffe,D(0));B(6,'p1a_read_bridge_return')

    # Only two exact P0 source-derived callback/marker layouts are trusted.
    for i,(mark_delta,read_delta) in enumerate(pairs):
        next_label=('p1a_read_bridge_try_shim' if i==0
                    else 'p1a_read_bridge_return')
        if i==1:L('p1a_read_bridge_try_shim')
        G('callback',D(0));c.imm('add',mark_delta,D(0))
        B(5,next_label)
        S(D(0),'marker')
        mapped(D(0),next_label)
        G('marker',D(0));c.imm('add',3,D(0))
        B(5,next_label)
        mapped(D(0),next_label)
        G('marker',A(0));c.move(M(0,0),D(0))
        c.imm('cmp',MAGIC,D(0));B(6,next_label)

        G('callback',D(0))
        if read_delta<0:
            c.imm('sub',-read_delta,D(0))
        else:
            c.imm('add',read_delta,D(0))
        B(5,'p1a_read_bridge_return')
        S(D(0),'target')
        mapped(D(0))
        G('target',D(0));c.imm('add',7,D(0))
        B(5,'p1a_read_bridge_return')
        mapped(D(0))
        G('target',A(0))
        for word,off in ((signature[0],0),(signature[1],4)):
            c.move(M(0,off),D(0))
            c.imm('cmp',word,D(0));B(6,'p1a_read_bridge_return')
        G('ident',D(0));G('output',A(1));G('target',A(0))
        c.raw('4e90')             # JSR (A0) into P0 BOBS relay_read_entry
        c.tst(D(3));B(7,'p1a_read_bridge_return')
        S(I(1),'result')
        B(0,'p1a_read_bridge_return')

    L('p1a_read_bridge_return')
    G('result',D(3))
    c.raw('4fef00404cdf77f374004e75')

    # The public getters never expose the private 24-byte scratch record.
    # They call the fifth-group bridge, not a PC16 BOBS branch.
    for name,offset in FIELDS.items():
        prefix='p1a_get_'+name
        L(prefix+'_entry')
        c.raw('48e7efee4fefffe0')
        c.move(D(3),D(0))
        c.move(A(7),A(1))
        B(1,'p1a_read_bridge_entry')
        c.tst(D(3));B(7,prefix+'_fail')
        c.move(M(7,offset),D(3))
        B(0,prefix+'_return')
        L(prefix+'_fail')
        c.move(I(INVALID),D(3))
        L(prefix+'_return')
        c.raw('4fef00204cdf77f774004e75')

    native=c.out()
    if (not native.startswith(old) or len(native)&1 or len(native)>=32766
            or c.labels['p1a_read_bridge_entry']!=len(old)
            or len(native)-len(old)>1800):
        raise ValueError('P1a fifth-group native layout/prefix/size invalid')
    return native,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_m19_p1a_getters()
    print('M19 P1a 020 FIFTH GROUP SOURCE ONLY',len(raw),sha256(raw).hexdigest(),
          {k:labels['p1a_get_'+k+'_entry'] for k in FIELDS},
          'NO installed Lib/Compiler claim')
