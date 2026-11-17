#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P0j-b2: explicit AGBO-bank Chip staging via byte-exact P0c validators.

Two PRIVATE entries, no public Draw or global bank_active_state access:
  explicit_checked_stage_entry: D3=bank, A1=ctx, A4=GfxBase, A5=owner.
  explicit_registry_prepare_entry: D3=bank, A4=GfxBase, A5=owner.
They join the original P0c full AGBO validator and atomic node publish
at two ZERO-BYTE labels; all earlier native bytes remain unchanged.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code,D,A,M,I
from amos_main_abi import main_index,rjsr
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5
from m19_p0c_checked_bank_stage_emit import F as SF
from m19_p0c_bank_registry_emit import F as RF,NODE_SIZE,META_FLAGS
from m19_p0j_explicit_bank_lookup_emit import emit_explicit_bank_lookup

GETADR=rjsr(main_index('Bnk.GetAdr'))

def emit_explicit_bank_stage() -> tuple[bytes,dict[str,int]]:
    old,labels=emit_explicit_bank_lookup()
    for key in ('checked_stage_live_bank_valid','registry_prepare_after_stage'):
        if key not in labels:
            raise ValueError('Missing zero-byte P0c source anchor: '+key)
    c=Code();c.raw(old.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,k):c.move(src,M(2,SF[k]))
    def G(k,dst):c.move(M(2,SF[k]),dst)
    def RS(src,k):c.move(src,M(2,RF[k]))
    def RG(k,dst):c.move(M(2,RF[k]),dst)

    L('explicit_checked_stage_entry')
    c.raw('48e7efee4fefff50') # AMOS MOVEM + 176-byte checked frame
    c.move(A(7),A(2))
    S(D(3),'bank');S(A(1),'ctx');S(A(4),'gfx')
    S(I(0),'result');c.move(I(0),D(3))
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'checked_fail')
    G('ctx',D(0));c.tst(D(0));B(7,'checked_fail')
    c.imm('and',1,D(0));B(6,'checked_fail')
    G('bank',D(0))
    c.imm('cmp',5,D(0));B(5,'checked_fail')
    c.imm('cmp',65535,D(0));B(2,'checked_fail')
    c.move(A(5),D(0));c.tst(D(0));B(7,'checked_fail')
    c.imm('and',1,D(0));B(6,'checked_fail')
    c.move(M(5,CUR_BANKS_A5),D(0));S(D(0),'head')
    c.tst(D(0));B(7,'checked_fail')
    c.imm('and',1,D(0));B(6,'checked_fail')
    G('bank',D(0));c.raw(GETADR.hex())
    c.move(A(0),D(0));S(D(0),'bankptr')
    c.imm('cmp',24,D(0));B(3,'checked_fail')
    c.imm('and',1,D(0));B(6,'checked_fail')
    # Branch to ORIGINAL full AGBO validation, including all images,
    # mask bytes, padded planes and the real P0c Chip CopyMem/WaitBlit.
    B(0,'checked_stage_live_bank_valid')

    L('explicit_registry_prepare_entry')
    c.raw('48e7efee4fefffa0') # AMOS MOVEM + 96-byte registry frame
    c.move(A(7),A(2))
    RS(D(3),'bank');RS(A(5),'owner');RS(A(4),'gfx')
    RS(I(0),'result');RS(I(0),'newnode')
    c.lea(0,'registry_state');RS(A(0),'root')
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'registry_return')
    RG('owner',D(0));c.tst(D(0));B(7,'registry_return')
    B(1,'registry_owner_guard')
    c.tst(D(0));B(7,'registry_return')
    RG('bank',D(0))
    c.imm('cmp',5,D(0));B(5,'registry_return')
    c.imm('cmp',65535,D(0));B(2,'registry_return')
    # Persistent Bobs: use a live, identity-checked Chip cache directly.
    # The b1 lookup validates the exact bank/generation, Chip cookie,
    # ownership and MEMF_CHIP without reading bank_active_state.
    # Its 28-byte result lives in our unused frame tail (+64..+91).
    # An absent or stale cache falls through to the original full stage.
    RG('bank',D(3))
    c.move(A(2),D(0))
    c.imm('add',64,D(0))
    c.move(D(0),A(1))
    B(1,'explicit_bank_lookup_entry')
    c.tst(D(3));B(7,'explicit_prepare_cache_miss')
    RS(I(1),'result')
    B(0,'registry_return')
    L('explicit_prepare_cache_miss')
    B(1,'registry_find')
    RG('bad',D(0));c.tst(D(0));B(6,'registry_return')
    RG('node',D(0));c.tst(D(0))
    B(6,'explicit_prepare_existing')
    c.move(I(NODE_SIZE),D(0));c.move(I(META_FLAGS),D(1))
    c.raw('2c780004');c.call_os(-684) # AllocVec metadata
    c.tst(D(0));B(7,'registry_return')
    RS(D(0),'newnode')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'registry_prepare_free_new')
    c.move(D(0),A(0));RG('bank',D(1));c.move(D(1),M(0,4))
    RS(D(0),'node')
    L('explicit_prepare_existing')
    RG('node',D(0));c.imm('add',8,D(0))
    c.move(D(0),A(1))
    RG('bank',D(3));RG('gfx',A(4))
    B(1,'explicit_checked_stage_entry')
    c.tst(D(3));B(7,'registry_prepare_free_new')
    # Join the ORIGINAL registry's atomic detached-node publication.
    B(0,'registry_prepare_after_stage')

    data=c.out()
    if (not data.startswith(old) or
            c.labels['explicit_checked_stage_entry']!=len(old)
            or len(data)&1 or len(data)>=32766):
        raise ValueError('P0j-b2 native prefix/CPU/PC16 drift')
    if data.count(GETADR)!=old.count(GETADR)+1:
        raise ValueError('P0j-b2 explicit stage lacks source Bnk.GetAdr')
    return data,c.labels

if __name__=='__main__':
    data,labels=emit_explicit_bank_stage()
    print('M19 P0j-b2 MC68020 EXPLICIT CHIP STAGING SOURCE ONLY',
          len(data),sha256(data).hexdigest(),
          'entry',labels['explicit_registry_prepare_entry'],
          'NO selection shadow/installed Lib/public Draw')
