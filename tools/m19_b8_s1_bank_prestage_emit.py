#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0 Bank Select: pre-stage an existing populated AGBO bank in Chip.

APPEND-ONLY to the byte-exact B8 S1 BOBS native unit. This native function is
the proposed replacement for the *existing* public Aga Bob Bank N entry. Its
AP20 stub is redirected IN MEMORY by a separate source-pinned builder ONLY.

Selection of an empty newly created bank keeps the old behavior: no Chip
allocation. Selection of a populated bank uses the existing P0j-b2 fully
validated explicit-bank registry preparation and B7 checked End arming,
BEFORE returning to AMOS. Reusing a current cache makes no Chip allocation.

On stage or callback failure, restore the original bank selection. A newly
staged Chip cache is released with the source-verified WaitBlit/FreeVec path
when callback arming fails. The source AGBO bank is NEVER freed here.
No Bob painting, no implicit Swap, no new AP20 command, no installed Lib.
Only owner-synchronous AMOS calls; asynchronous Erase/Poke remains unsupported.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b8_first_update_emit import emit_b8_b7_first_update
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5

FRAME=64
STATE_A5=0x1c8
F=dict(bank=0,oldbank=4,oldptr=8,oldhead=12,ptr=16,
       state=20,gfx=24,cached=28,staged=32,result=36)


def emit_b8_s1_bank_prestage() -> tuple[bytes,dict[str,int]]:
    old,labels=emit_b8_b7_first_update()
    required=('bank_bank_select','bank_active_state',
              'explicit_registry_prepare_entry','registry_lookup_entry',
              'registry_free_entry','b8_b7_arm_end_nodraw_entry')
    if any(key not in labels for key in required):
        raise ValueError('Missing verified B8 S1 BOBS native entry or bank state')
    c=Code(); c.raw(old.hex()); c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,key):c.move(src,M(2,F[key]))
    def G(key,dst):c.move(M(2,F[key]),dst)
    def mapped(addr, fail):
        c.move(addr,A(1))
        c.raw('2c780004')  # ExecBase 4.w, A6
        c.call_os(-534)    # TypeOfMem
        c.tst(D(0));B(7,fail)

    L('b8s1_bank_prestage_entry')
    c.raw('48e7efee4fefffc0')  # AMOS registers + 64-byte local frame
    c.move(A(7),A(2))
    S(D(3),'bank')
    for k in ('cached','staged','result'):S(I(0),k)
    c.lea(0,'bank_active_state')
    for k,off in (('oldbank',0),('oldptr',4),('oldhead',8)):
        S(M(0,off),k)

    # Existing official instruction: validates/creates AGBO, updates selected
    # triple, and performs NO Chip allocation. Retain the original bytes.
    G('bank',D(3))
    B(1,'bank_bank_select')
    c.tst(D(3));B(7,'b8s1_bank_return')
    c.lea(0,'bank_active_state')
    c.move(M(0,0),D(0))
    G('bank',D(1));c.alu('cmp',D(1),0)
    B(6,'b8s1_bank_rollback')
    c.move(M(0,4),D(0))
    c.imm('cmp',24,D(0));B(3,'b8s1_bank_rollback')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'b8s1_bank_rollback')
    S(D(0),'ptr')
    c.move(M(0,8),D(0))
    c.move(M(5,CUR_BANKS_A5),D(1))
    c.alu('cmp',D(1),0)
    B(6,'b8s1_bank_rollback')

    # Existing Bank Select validates the AGBO header and directory length.
    # Probe the entire count field endpoints before examining it.
    G('ptr',D(0));c.imm('add',9,D(0))
    B(5,'b8s1_bank_rollback')
    mapped(D(0),'b8s1_bank_rollback')
    G('ptr',A(0))
    c.move(I(0),D(0))
    c.move(M(0,8),D(0),'w')
    c.tst(D(0));B(7,'b8s1_bank_success') # canonical empty AGBO: no Chip.

    # Real screen/GfxBase is needed by the checked allocator and eventual
    # WaitBlit on replacement/free. Non-empty bank before Open is refused,
    # restoring the previous selection and making no Chip allocation.
    c.move(M(5,STATE_A5),D(0))
    c.tst(D(0));B(7,'b8s1_bank_rollback')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'b8s1_bank_rollback')
    S(D(0),'state')
    mapped(D(0),'b8s1_bank_rollback')
    G('state',D(0));c.imm('add',32,D(0))
    B(5,'b8s1_bank_rollback')
    mapped(D(0),'b8s1_bank_rollback')
    G('state',A(0))
    c.tst(M(0,0));B(7,'b8s1_bank_rollback')  # live AGA Screen
    c.move(M(0,8),D(0))
    c.tst(D(0));B(7,'b8s1_bank_rollback')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'b8s1_bank_rollback')
    S(D(0),'gfx')
    mapped(D(0),'b8s1_bank_rollback')

    # A current, identity/generation-checked staged bank is a cache hit.
    # This determines if a later callback failure must free a newly staged
    # bank or preserve the earlier owned cache.
    G('bank',D(3));G('gfx',A(4))
    B(1,'registry_lookup_entry')
    c.tst(D(3));B(7,'b8s1_bank_cache_miss')
    S(I(1),'cached')
    L('b8s1_bank_cache_miss')
    G('bank',D(3));G('gfx',A(4))
    B(1,'explicit_registry_prepare_entry')
    c.tst(D(3));B(7,'b8s1_bank_rollback')
    S(I(1),'staged')

    # Unlike the older P0c-only End armer, this B7 hook accepts existing
    # B7/B8 callbacks and installs a verified whole-registry teardown.
    # No Bob SET, Draw or pixel write is performed by this path.
    B(1,'b8_b7_arm_end_nodraw_entry')
    c.tst(D(3));B(6,'b8s1_bank_success')

    # Failed hook: do NOT release a pre-existing valid shared bank cache.
    G('cached',D(0));c.tst(D(0));B(6,'b8s1_bank_rollback')
    G('bank',D(3));G('gfx',A(4))
    B(1,'registry_free_entry')
    # A failed release remains fail-closed; it cannot authorize Draw or Swap.

    L('b8s1_bank_rollback')
    c.lea(0,'bank_active_state')
    for k,off in (('oldbank',0),('oldptr',4),('oldhead',8)):
        G(k,D(0));c.move(D(0),M(0,off))
    B(0,'b8s1_bank_return')
    L('b8s1_bank_success')
    S(I(1),'result')
    L('b8s1_bank_return')
    G('result',D(3))
    c.raw('4fef00404cdf77f774004e75')

    native=c.out()
    if (not native.startswith(old)
            or c.labels['b8s1_bank_prestage_entry']!=len(old)
            or len(native)%2 or len(native)>=32766):
        raise ValueError('B8 S1 pre-stage altered frozen BOBS prefix or PC16 span')
    return native,c.labels


if __name__=='__main__':
    from hashlib import sha256
    code,labs=emit_b8_s1_bank_prestage()
    print('M19 P0 BANK SELECT PRESTAGE MC68020 SOURCE ONLY',
          len(code), sha256(code).hexdigest(),
          labs['b8s1_bank_prestage_entry'], 'NO INSTALLED LIB')
