#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0 Bank Free: fifth-group public bridge to source-pinned BOBS unit.

A new AP20 stub at index 184 cannot reach BOBS group 177 with signed PC16.
The B8 fifth native group at 181 is reachable; append ONLY a small bridge
whose input is D3=bank, A5=AMOS owner, output D3=1/0, D2=0.

Resolve the B7/B8 end callback from live A5+1CC/+1D0. Check both pointers,
MC68020, TypeOfMem, native prologue, and the unmodified B8RG registrar
marker. The marker has TWO known source-derived offsets: one from the
original B7 End callback (before Update), another from B8's registered
End trampoline (after Update). Resolve Bank Free entry within the SAME
relocated BOBS native group with a checked offset and signature. Never
use a fixed address or cross-group PC-relative BSR.

No recognized B7 callback: return 0 (fail closed). The original BOBS
Bank Free preflight remains responsible for current frame/owner checks.
"""
from __future__ import annotations

from m68k_emit import Code,A,D,I,M
from m19_b8_safe_retry_emit import emit_b8_safe_retry
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free

MAGIC=0x42385247
F=dict(result=0,bank=4,callback=8,target=12,marker=16)
FRAME=64


def emit_b8_s1_bank_free_bridge() -> tuple[bytes,dict[str,int]]:
    old,labels=emit_b8_safe_retry()
    bobs,bel=emit_b8_s1_bank_free()
    b7=bel['b7_end_entry']
    shim=bel['b8_b7_end_trampoline_entry']
    mark=bel['b8_b7_register_magic']
    free=bel['b8s1_bank_free_entry']
    for v in (b7,shim,mark,free):
        if v<0 or v>=32766 or v&1:
            raise ValueError('Unverified native B7/BOBS label/offset')
    pairs=((mark-b7,free-b7),(mark-shim,free-shim))
    if pairs[0]==pairs[1] or any(m<=0 or d<=0 for m,d in pairs):
        raise ValueError('B7/B8 callback provenance or delta changed')
    c=Code();c.raw(old.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,k):c.move(src,M(4,F[k]))
    def G(k,dst):c.move(M(4,F[k]),dst)
    def mapped(reg):
        c.move(reg,A(1))
        c.raw('2c780004');c.call_os(-534) # TypeOfMem
        c.tst(D(0));B(7,'b8_bank_free_bridge_return')

    L('b8_bank_free_bridge_entry')
    c.raw('48e7cfee4fefffc0')
    c.move(A(7),A(4))
    S(D(3),'bank');S(I(0),'result')
    # Reject CPU000/010 or malformed AMOS owner before callbacks.
    c.raw('20780004')
    c.move(A(0),D(0));c.tst(D(0));B(7,'b8_bank_free_bridge_return')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1);B(7,'b8_bank_free_bridge_return')
    c.move(A(5),D(0));c.tst(D(0));B(7,'b8_bank_free_bridge_return')
    c.imm('and',1,D(0));B(6,'b8_bank_free_bridge_return')
    mapped(A(5))
    G('bank',D(0));c.imm('cmp',5,D(0));B(5,'b8_bank_free_bridge_return')
    c.imm('cmp',65535,D(0));B(2,'b8_bank_free_bridge_return')
    c.move(M(5,0x1cc),D(0));c.tst(D(0));B(7,'b8_bank_free_bridge_return')
    c.move(M(5,0x1d0),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_bank_free_bridge_return')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'b8_bank_free_bridge_return')
    S(D(0),'callback')
    mapped(D(0))
    G('callback',D(0));c.imm('add',3,D(0))
    B(5,'b8_bank_free_bridge_return')
    mapped(D(0))
    G('callback',A(0));c.move(M(0,0),D(0))
    c.imm('cmp',0x48e7fffe,D(0))
    B(6,'b8_bank_free_bridge_return')

    # Try the exact source-pinned B7 End callback first.
    for i,(mark_delta,free_delta) in enumerate(pairs):
        next_label='b8_bank_free_bridge_try_shim' if i==0 else 'b8_bank_free_bridge_return'
        if i==1:L('b8_bank_free_bridge_try_shim')
        G('callback',D(0))
        c.imm('add',mark_delta,D(0))
        B(5,next_label)
        S(D(0),'marker')
        mapped(D(0))
        G('marker',D(0));c.imm('add',3,D(0))
        B(5,next_label)
        mapped(D(0))
        G('marker',A(0));c.move(M(0,0),D(0))
        c.imm('cmp',MAGIC,D(0));B(6,next_label)
        G('callback',D(0));c.imm('add',free_delta,D(0))
        B(5,'b8_bank_free_bridge_return')
        S(D(0),'target')
        mapped(D(0))
        G('target',D(0));c.imm('add',7,D(0))
        B(5,'b8_bank_free_bridge_return')
        mapped(D(0))
        G('target',A(0))
        c.move(M(0,0),D(0))
        c.imm('cmp',0x48e7efee,D(0));B(6,'b8_bank_free_bridge_return')
        c.move(M(0,4),D(0))
        c.imm('cmp',0x4fefffa0,D(0));B(6,'b8_bank_free_bridge_return')
        G('bank',D(3));G('target',A(0))
        c.raw('4e90') # JSR (A0), exact mapped BOBS Bank Free
        c.tst(D(3));B(7,'b8_bank_free_bridge_return')
        S(I(1),'result')
        B(0,'b8_bank_free_bridge_return')

    L('b8_bank_free_bridge_return')
    G('result',D(3))
    c.raw('4fef00404cdf77f374004e75')

    native=c.out()
    if not native.startswith(old) or len(native)&1 or len(native)>=32766:
        raise ValueError('B8 fifth-group bridge prefix or PC16 overflow')
    if c.labels['b8_bank_free_bridge_entry']!=len(old):
        raise ValueError('B8 bridge not strictly appended to frozen code')
    return native,c.labels


if __name__=='__main__':
    from hashlib import sha256
    blob,lab=emit_b8_s1_bank_free_bridge()
    print('M19 P0 BANK FREE FIFTH GROUP BRIDGE MC68020',
          len(blob),sha256(blob).hexdigest(),lab['b8_bank_free_bridge_entry'])
