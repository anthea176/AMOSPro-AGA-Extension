#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 native private Clear / Update transaction stages, SOURCE ONLY.

This module extends (byte-exact) the 60-check B7/B8 cross-unit arm source.
It is NOT a usable AMOS Clear/Update public command: only a SERIALIZED
three-stage native protocol for an ALREADY-REGISTERED B7 End shim.

    clear  : restore previous snapshot on Safe back; reset B7 frame guard.
    prepare: restore old back (unless explicit Clear was already done),
             snapshot fresh background, and permit ONE B7 Draw.
    finish : verify actual B7 Draw reached READY on the same physical back.
    abort  : leave B7 DIRTY; explicit Clear or successful Close recovers.
    reset  : clear transaction state ONLY after B8 service Close freed pool.

The caller must execute prepare -> real B7 Draw -> finish atomically in its
own AMOS task, with no Swap or arbitrary other call in between. This is
an internal integration contract; a public Update wrapper will have to
guarantee that sequence. No implicit Swap or bank prevalidation is provided
by these stages; the existing B7 Draw still handles AGBO validation.

Frame guard status is derived ONLY from a source-pinned registered B7 shim
callback (A5+1CC/1D0), checked against B8RG and MC68020 prologue.
No guessed cross-unit BSR. If B8 is not registered, all private operations
fail closed: no memory or front/back pixels are changed.
"""
from __future__ import annotations

from m68k_emit import Code,A,D,I,M
from m19_b8_cross_unit_arm_emit import emit_b8_cross_unit_arm
from m19_b8_b7_hook_emit import emit_b8_b7_hooks,END1,END2
from m19_b8_page_manager_emit import R as B8ROOT
from m19_p0j_swap_barrier_emit import G as B7GUARD,DIRTY,READY
from m19_b8_back_selector_emit import STATE_OFF

FRAME=96
F=dict(result=0,guard=4,bit=8,epoch=12,db=16,front=20,
       screen=24,state=28,callback=32,valid=36)
R=dict(owner=0,screen=4,epoch=8,cleared=12,pending=16,txepoch=20)
ROOT_SIZE=24
MAGIC=0x42385247

def emit_b8_clear_update_tx() -> tuple[bytes,dict[str,int]]:
    old,labels=emit_b8_cross_unit_arm()
    _,b7=emit_b8_b7_hooks()
    end=b7['b8_b7_end_trampoline_entry']
    guard_delta=b7['frame_guard_state']-end
    magic_delta=b7['b8_b7_register_magic']-end
    assert guard_delta<0 and -guard_delta<32766 and magic_delta>0
    c=Code();c.raw(old.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,key):c.move(src,M(4,F[key]))
    def G(key,dst):c.move(M(4,F[key]),dst)
    def txroot():c.lea(2,'b8_tx_root')
    def service():c.lea(0,'b8_service_root')
    def prologue(name):
        L('b8_service_'+name+'_entry')
        c.raw('48e7cfee4fefffa0')
        c.move(A(7),A(4))
        S(I(0),'result')
    def successful():
        S(I(1),'result')
        B(0,'b8_tx_return')
    def guard_status(value):
        G('guard',A(0))
        c.move(I(value),M(0,B7GUARD['status']))
    def mark_dirty():
        guard_status(DIRTY)
    bit_sites=[0]
    def selected_bit():
        # Emitted multiple times: every branch MUST have unique code labels.
        bit_sites[0]+=1
        page1=f'b8_tx_page1_{bit_sites[0]}'
        ready=f'b8_tx_bit_ready_{bit_sites[0]}'
        G('front',D(0))
        c.tst(D(0));B(7,page1)
        S(I(1),'bit')
        B(0,ready)
        L(page1)
        S(I(2),'bit')
        L(ready)

    # Verify ownership / real AGA Screen / registered original B7 shim.
    # The B7 guard lies in the SAME relocated BOBS native unit as shim.
    L('b8_tx_validate')
    service()
    c.move(M(0,B8ROOT['owner']),D(0))
    c.move(A(5),D(1));c.alu('cmp',D(1),0)
    B(6,'b8_tx_validate_fail')
    c.tst(D(0));B(7,'b8_tx_validate_fail')
    c.move(M(0,B8ROOT['epoch']),D(0));c.tst(D(0))
    B(7,'b8_tx_validate_fail')
    S(D(0),'epoch')
    c.move(M(0,B8ROOT['screen']),D(0));c.tst(D(0))
    B(7,'b8_tx_validate_fail')
    S(D(0),'screen')
    c.move(M(0,B8ROOT['db']),D(0));c.tst(D(0))
    B(7,'b8_tx_validate_fail')
    S(D(0),'db')
    c.move(M(5,STATE_OFF),D(0));c.tst(D(0))
    B(7,'b8_tx_validate_fail')
    S(D(0),'state')
    c.move(D(0),A(0))
    c.move(M(0,0),D(0));G('screen',D(1))
    c.alu('cmp',D(1),0);B(6,'b8_tx_validate_fail')
    G('state',A(0))
    c.move(M(0,32),D(0));G('db',D(1))
    c.alu('cmp',D(1),0);B(6,'b8_tx_validate_fail')
    G('db',A(0))
    c.move(M(0,8),D(0))
    c.imm('cmp',1,D(0));B(2,'b8_tx_validate_fail')
    S(D(0),'front')
    # Same exact B7 shim callback pair: foreign callbacks are immutable.
    c.move(M(5,END1),D(0));c.move(M(5,END2),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_tx_validate_fail')
    c.tst(D(0));B(7,'b8_tx_validate_fail')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'b8_tx_validate_fail')
    S(D(0),'callback')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_tx_validate_fail')
    G('callback',A(0))
    c.move(M(0,0),D(0))
    c.imm('cmp',0x48e7fffe,D(0))
    B(6,'b8_tx_validate_fail')
    G('callback',D(0))
    c.imm('add',magic_delta,D(0))
    B(5,'b8_tx_validate_fail')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_tx_validate_fail')
    G('callback',D(0))
    c.imm('add',magic_delta+3,D(0))
    B(5,'b8_tx_validate_fail')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_tx_validate_fail')
    G('callback',D(0))
    c.imm('add',magic_delta,D(0))
    c.move(D(0),A(0))
    c.move(M(0,0),D(0))
    c.imm('cmp',MAGIC,D(0));B(6,'b8_tx_validate_fail')
    G('callback',D(0))
    c.imm('sub',-guard_delta,D(0))
    B(5,'b8_tx_validate_fail')
    S(D(0),'guard')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_tx_validate_fail')
    G('guard',D(0))
    c.imm('add',23,D(0));B(5,'b8_tx_validate_fail')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_tx_validate_fail')
    # Stale guard identities must not be silently reset or overwritten.
    G('guard',A(0))
    c.move(M(0,B7GUARD['status']),D(0))
    c.imm('cmp',READY,D(0));B(2,'b8_tx_validate_fail')
    c.tst(D(0));B(7,'b8_tx_guard_ok')
    for key,frame in (
        ('owner',None),('state','state'),('db','db'),
        ('front','front'),('screen','screen')):
        G('guard',A(0))
        c.move(M(0,B7GUARD[key]),D(0))
        if key=='owner':c.move(A(5),D(1))
        else:G(frame,D(1))
        c.alu('cmp',D(1),0);B(6,'b8_tx_validate_fail')
    L('b8_tx_guard_ok')
    txroot()
    c.move(M(2,R['owner']),D(0))
    c.tst(D(0));B(7,'b8_tx_new_epoch')
    c.move(A(5),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_tx_validate_fail')
    c.move(M(2,R['screen']),D(0));G('screen',D(1))
    c.alu('cmp',D(1),0);B(6,'b8_tx_validate_fail')
    c.move(M(2,R['epoch']),D(0));G('epoch',D(1))
    c.alu('cmp',D(1),0);B(6,'b8_tx_validate_fail')
    B(0,'b8_tx_valid')
    L('b8_tx_new_epoch')
    c.move(A(5),M(2,R['owner']))
    G('screen',D(0));c.move(D(0),M(2,R['screen']))
    G('epoch',D(0));c.move(D(0),M(2,R['epoch']))
    L('b8_tx_valid')
    c.move(I(1),D(3));c.raw('4e75')
    L('b8_tx_validate_fail')
    c.move(I(0),D(3));c.raw('4e75')

    # On Clear failure, B7 DIRTY remains latched; never Swap a partial page.
    prologue('clear_guard')
    B(1,'b8_tx_validate')
    c.tst(D(3));B(7,'b8_tx_return')
    selected_bit()
    mark_dirty()
    B(1,'b8_service_safe_restore_entry')
    c.tst(D(3));B(7,'b8_tx_return')
    # No old Bob pixels remain on the checked back physical page.
    G('guard',A(0))
    for off in range(0,24,4):c.move(I(0),M(0,off))
    txroot()
    c.move(M(2,R['cleared']),D(0))
    G('bit',D(1));c.alu('or',D(1),0)
    c.move(D(0),M(2,R['cleared']))
    c.move(I(0),M(2,R['pending']))
    c.move(I(0),M(2,R['txepoch']))
    successful()

    # PREPARE: existing B8 shim must be registered; caller guarantees that
    # B7 Draw/Finish follows synchronously without AMOS Swap in between.
    prologue('update_prepare')
    B(1,'b8_tx_validate');c.tst(D(3));B(7,'b8_tx_return')
    selected_bit()
    txroot()
    c.tst(M(2,R['pending']));B(7,'b8_prepare_status')
    mark_dirty()
    B(0,'b8_tx_return')
    L('b8_prepare_status')
    G('guard',A(0))
    c.move(M(0,B7GUARD['status']),D(0))
    c.imm('cmp',DIRTY,D(0));B(7,'b8_tx_return')
    mark_dirty()
    # Preserve a background explicitly drawn after Clear on this page.
    txroot()
    c.move(M(2,R['cleared']),D(0))
    G('bit',D(1));c.alu('and',D(1),0)
    c.tst(D(0));B(6,'b8_prepare_capture')
    service()
    c.move(M(0,B8ROOT['valid']),D(0))
    G('bit',D(1));c.alu('and',D(1),0)
    c.tst(D(0));B(7,'b8_prepare_capture')
    B(1,'b8_service_safe_restore_entry')
    c.tst(D(3));B(7,'b8_tx_return')
    L('b8_prepare_capture')
    B(1,'b8_service_safe_capture_entry')
    c.tst(D(3));B(7,'b8_tx_return')
    txroot()
    G('bit',D(0));c.move(D(0),M(2,R['pending']))
    G('epoch',D(0));c.move(D(0),M(2,R['txepoch']))
    # Reset DIRTY only at the hand-off to B7's *internal* Draw; never
    # expose this three-stage API as independent user-callable commands.
    guard_status(0)
    successful()

    # FINISH only if B7's actual Draw set READY for same owner/front.
    # Any refusal (after an authenticated prepare) locks B7 DIRTY.
    prologue('update_finish')
    B(1,'b8_tx_validate');c.tst(D(3));B(7,'b8_tx_return')
    selected_bit()
    txroot()
    c.move(M(2,R['pending']),D(0))
    G('bit',D(1));c.alu('cmp',D(1),0);B(6,'b8_finish_fail')
    c.tst(D(0));B(7,'b8_finish_fail')
    c.move(M(2,R['txepoch']),D(0));G('epoch',D(1))
    c.alu('cmp',D(1),0);B(6,'b8_finish_fail')
    G('guard',A(0))
    c.move(M(0,B7GUARD['status']),D(0))
    c.imm('cmp',READY,D(0));B(6,'b8_finish_fail')
    service()
    c.move(M(0,B8ROOT['valid']),D(0))
    G('bit',D(1));c.alu('and',D(1),0)
    c.tst(D(0));B(7,'b8_finish_fail')
    txroot()
    c.move(I(0),M(2,R['pending']))
    c.move(I(0),M(2,R['txepoch']))
    G('bit',D(0))
    c.imm('cmp',1,D(0));B(6,'b8_finish_second')
    c.imm('and',0xfffffffe,M(2,R['cleared']))
    B(0,'b8_finish_success')
    L('b8_finish_second')
    c.imm('and',0xfffffffd,M(2,R['cleared']))
    L('b8_finish_success')
    successful()
    L('b8_finish_fail')
    mark_dirty()
    B(0,'b8_tx_return')

    prologue('update_abort')
    B(1,'b8_tx_validate');c.tst(D(3));B(7,'b8_tx_return')
    mark_dirty()
    txroot()
    c.move(I(0),M(2,R['pending']))
    c.move(I(0),M(2,R['txepoch']))
    # Abort is a safe intentional invalidation, not a successful Update.
    B(0,'b8_tx_return')

    # Reset transaction state only after the service pool is actually freed.
    # The B7 Close/End shim already ensures post-Close is called once.
    prologue('tx_reset')
    service()
    c.tst(M(0,B8ROOT['owner']));B(6,'b8_tx_return')
    txroot()
    for off in range(0,ROOT_SIZE,4):c.move(I(0),M(2,off))
    successful()

    L('b8_tx_return')
    G('result',D(3))
    c.move(I(0),D(2))
    c.raw('4fef00604cdf77f34e75')
    L('b8_tx_root')
    c.raw('00'*ROOT_SIZE)
    code=c.out()
    assert code.startswith(old)
    assert c.labels['b8_service_clear_guard_entry'] > len(old)
    assert len(code)%2==0 and len(code)<32766
    assert c.labels['b8_tx_root']+ROOT_SIZE==len(code)
    return code,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_b8_clear_update_tx()
    print('M19 B8 Clear/Update private stages MC68020 SOURCE ONLY',
          len(raw),sha256(raw).hexdigest())
