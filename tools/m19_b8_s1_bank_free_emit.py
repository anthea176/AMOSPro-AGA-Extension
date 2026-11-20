#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0 source-only Bank Free N: disable Bobs and release private Chip.

Append-only to the SHA-pinned B8 S1 + Bank Select Chip pre-stage BOBS group.
PRIVATE source is linked to an AP20 instruction only by the guarded builder.
Never touches the public AMOS AGBO/DATA bank; no implicit Swap or drawing.

PRECONDITIONS: MC68020, current AMOS A5, live AGA Screen/GfxBase, B7
frame-guard EMPTY (neither DIRTY nor READY), valid AGA P0e object table and
owner, and validated BOBS registry ownership. The 64-slot native P0e table
is located from the original verified AGA State offset, not an absolute
Runtime/Compiler address; TypeOfMem checks both extremes and the source
signature before reading it. Two passes: validate every slot first, then
deactivate only ACTIVE slots whose stored bank number equals N. The source
bank remains intact, including Save/Load data. Clear selected-bank shadow
when N is selected: any next Get/Put requires Aga Bob Bank N again.

Once references are disabled, the existing checked registry_free waits for
Blitter (WaitBlit) and releases only bank N's owned Chip and metadata. If
release refuses, references remain safely disabled; no unsafe rollback.
A stale/pending frame refuses without changing any resource.
"""
from __future__ import annotations

from m68k_emit import Code,A,D,I,M
from m19_b8_s1_bank_prestage_emit import emit_b8_s1_bank_prestage
from m19_p0e_object_table_emit import emit_object_table,MAX_OBJECTS,SLOT_BYTES
from m19_p0e_v2_object_bridge_emit import OBJ_RELATIVE
from m19_p0j_swap_barrier_emit import G as B7GUARD,DIRTY,READY

OBJECT, O=emit_object_table()
assert MAX_OBJECTS==64 and SLOT_BYTES==24 and OBJ_RELATIVE==56130
assert len(OBJECT)==2332
FRAME=96
STATE_A5=0x1c8
F=dict(bank=0,result=4,state=8,base=12,root=16,table=20,
       ptr=24,left=28,gfx=32,table_owner=36,selected=40)


def emit_b8_s1_bank_free() -> tuple[bytes,dict[str,int]]:
    old,labels=emit_b8_s1_bank_prestage()
    required=('frame_guard_state','registry_state','registry_free_entry',
              'registry_cpu_guard','bank_active_state')
    if any(k not in labels for k in required):
        raise ValueError('B8 S1 Bank Free requires source-pinned live BOBS helpers')
    c=Code()
    c.raw(old.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,k):c.move(src,M(2,F[k]))
    def G(k,dst):c.move(M(2,F[k]),dst)
    def mapped(ptr,failed='b8s1_bank_free_return'):
        c.move(ptr,A(1))
        c.raw('2c780004')  # ExecBase
        c.call_os(-534)    # Exec TypeOfMem
        c.tst(D(0));B(7,failed)
    def advance_and_loop(target):
        G('ptr',D(0))
        c.imm('add',SLOT_BYTES,D(0))
        B(5,'b8s1_bank_free_return')
        S(D(0),'ptr')
        G('left',D(0));c.quick(1,D(0),sub=True);S(D(0),'left')
        B(6,target)

    L('b8s1_bank_free_entry')
    c.raw('48e7efee4fefffa0') # preserve AMOS non-result + 96-byte local
    c.move(A(7),A(2))
    S(D(3),'bank')
    S(I(0),'result')
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'b8s1_bank_free_return')
    c.move(A(5),D(0));c.tst(D(0));B(7,'b8s1_bank_free_return')
    c.imm('and',1,D(0));B(6,'b8s1_bank_free_return')
    mapped(A(5))
    G('bank',D(0));c.imm('cmp',5,D(0));B(5,'b8s1_bank_free_return')
    c.imm('cmp',65535,D(0));B(2,'b8s1_bank_free_return')

    # Absolutely no Free / Bob Off while a B8 frame is being composed
    # (DIRTY) or has been completed but not presented (READY).
    c.lea(0,'frame_guard_state')
    c.tst(M(0,B7GUARD['status']))
    B(6,'b8s1_bank_free_return')

    # Refuse resources registered to another AMOS owner, even if a selected
    # bank number happens to match. Root (owner=0,head=0) is a valid empty.
    c.lea(0,'registry_state')
    c.move(M(0,0),D(0))
    c.tst(D(0));B(7,'b8s1_bank_free_registry_empty')
    c.move(A(5),D(1));c.alu('cmp',D(1),0)
    B(6,'b8s1_bank_free_return')
    c.tst(M(0,4));B(7,'b8s1_bank_free_return')
    B(0,'b8s1_bank_free_registry_ok')
    L('b8s1_bank_free_registry_empty')
    c.tst(M(0,4));B(6,'b8s1_bank_free_return')
    L('b8s1_bank_free_registry_ok')

    # Require actual AGA screen and mapped graphics.library for WaitBlit.
    c.move(M(5,STATE_A5),D(0));c.tst(D(0))
    B(7,'b8s1_bank_free_return')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'b8s1_bank_free_return')
    S(D(0),'state')
    mapped(D(0))
    G('state',D(0));c.imm('add',32,D(0))
    B(5,'b8s1_bank_free_return')
    mapped(D(0))
    G('state',A(0))
    c.tst(M(0,0));B(7,'b8s1_bank_free_return')
    c.move(M(0,8),D(0));c.tst(D(0))
    B(7,'b8s1_bank_free_return')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'b8s1_bank_free_return')
    S(D(0),'gfx')
    mapped(D(0))

    # P0e original AGA object_put is at State+56130, same relocated AGA
    # island as the 64-slot object array. Its prefix signature is frozen.
    G('state',D(0))
    c.imm('add',OBJ_RELATIVE,D(0));B(5,'b8s1_bank_free_return')
    S(D(0),'base')
    mapped(D(0))
    G('base',A(0))
    c.move(M(0,0),D(0))
    c.imm('cmp',0x48e7efee,D(0))
    B(6,'b8s1_bank_free_return')
    G('base',D(0))
    c.imm('add',O['object_root'],D(0))
    B(5,'b8s1_bank_free_return')
    S(D(0),'root')
    mapped(D(0))
    G('base',D(0))
    c.imm('add',O['object_table'],D(0))
    B(5,'b8s1_bank_free_return')
    S(D(0),'table')
    mapped(D(0))
    G('table',D(0))
    c.imm('add',MAX_OBJECTS*SLOT_BYTES-1,D(0))
    B(5,'b8s1_bank_free_return')
    mapped(D(0))

    G('root',A(0))
    c.move(M(0,0),D(0))
    S(D(0),'table_owner')
    c.tst(D(0));B(7,'b8s1_bank_free_scan_start')
    c.move(A(5),D(1));c.alu('cmp',D(1),0)
    B(6,'b8s1_bank_free_return')

    # First pass: structurally validate ALL 64 slots before changing any.
    L('b8s1_bank_free_scan_start')
    G('table',D(0));S(D(0),'ptr')
    S(I(MAX_OBJECTS),'left')
    L('b8s1_bank_free_scan')
    G('ptr',A(0))
    c.move(M(0,16),D(0))
    c.imm('cmp',1,D(0));B(2,'b8s1_bank_free_return')
    c.tst(D(0));B(7,'b8s1_bank_free_next_check')
    G('table_owner',D(1));c.tst(D(1))
    B(7,'b8s1_bank_free_return')
    G('ptr',A(0))
    c.move(M(0,0),D(0))
    c.imm('cmp',5,D(0));B(5,'b8s1_bank_free_return')
    c.imm('cmp',65535,D(0));B(2,'b8s1_bank_free_return')
    L('b8s1_bank_free_next_check')
    advance_and_loop('b8s1_bank_free_scan')

    # Second pass cannot reject: clear only active flags of bank N.
    G('table',D(0));S(D(0),'ptr')
    S(I(MAX_OBJECTS),'left')
    L('b8s1_bank_free_disable')
    G('ptr',A(0))
    c.tst(M(0,16));B(7,'b8s1_bank_free_next_off')
    c.move(M(0,0),D(0))
    G('bank',D(1));c.alu('cmp',D(1),0)
    B(6,'b8s1_bank_free_next_off')
    G('ptr',A(0));c.move(I(0),M(0,16))
    L('b8s1_bank_free_next_off')
    advance_and_loop('b8s1_bank_free_disable')

    # Drop the selected AGBO shadow for this bank so no new Bob may be SET
    # from freed/stale Chip without Aga Bob Bank N re-selection.
    c.lea(0,'bank_active_state')
    c.move(M(0,0),D(0))
    G('bank',D(1));c.alu('cmp',D(1),0)
    B(6,'b8s1_bank_free_release')
    for off in (0,4,8):
        c.move(I(0),M(0,off))

    # Existing source-verified registry_free performs checked WaitBlit before
    # freeing Chip, unlinks only after success, never Erase AMOS bank.
    L('b8s1_bank_free_release')
    G('bank',D(3));G('gfx',A(4))
    B(1,'registry_free_entry')
    c.tst(D(3));B(7,'b8s1_bank_free_return')
    S(I(1),'result')
    L('b8s1_bank_free_return')
    G('result',D(3))
    c.raw('4fef00604cdf77f774004e75')

    native=c.out()
    if (not native.startswith(old)
        or c.labels['b8s1_bank_free_entry']!=len(old)
        or len(native)%2 or len(native)>=32766):
        raise ValueError('M19 P0 Bank Free source/prefix/PC16 overflow')
    return native,c.labels


if __name__=='__main__':
    from hashlib import sha256
    blob,labels=emit_b8_s1_bank_free()
    print('M19 P0 BANK FREE MC68020 SOURCE ONLY',
          len(blob),sha256(blob).hexdigest(),
          'entry',labels['b8s1_bank_free_entry'])
