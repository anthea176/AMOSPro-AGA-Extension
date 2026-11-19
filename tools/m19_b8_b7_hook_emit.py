#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8: B7-m2-local Draw, Close and End trampoline, SOURCE ONLY.

Append-only to the exact native B7-m2 BOBS unit. No cross-unit BSR.
The new B8 fifth unit may register its post-Close function pointer only
AFTER B7 Draw has armed the exact source-pinned B7 End callback. Register
and all public wrappers live in B7's *same* relocated native unit.

Public Close/Draw AP20 stubs can be redirected IN MEMORY, never installed,
only after verifying the original RBSR indices and all B7 byte ancestry.
If no private B8 owner is registered, Draw/Close delegate to the existing
B7-m2 entries. A registered End shim temporarily restores B7's original
callback, invokes the exact B7 End chain, and re-arms only when Screen is
still live. No foreign or half-patched callback may be overwritten.

B8 callback registration must happen synchronously after the initial
B7 Draw, before returning from a future public B8 Update wrapper. Any
failed initialization before registration must release the B8 pool itself
to avoid an untracked End/Close memory leak. This condition is NOT YET
satisfied by a public token; therefore this module is not installed.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b7m2_close_reset_emit import emit_close_reset

END1=0x1cc
END2=0x1d0
ROOT_SIZE=8
R=dict(owner=0,callback=4)
FRAME=32
F=dict(result=0,postclose=4)


def emit_b8_b7_hooks() -> tuple[bytes,dict[str,int]]:
    old,labels=emit_close_reset()
    c=Code()
    c.raw(old.hex())
    c.labels.update(labels)
    B,L=c.branch,c.label

    def Rptr():
        c.lea(0,'b8_b7_hook_root')

    # Public numeric Draw wrapper. Default B7 behavior when B8 inactive.
    L('b8_b7_draw_trampoline_entry')
    c.raw('48e7efee4fefffe0') # AMOS numeric ABI, 32-byte local frame
    c.move(A(7),A(2))
    c.move(I(0),M(2,F['result']))
    Rptr()
    c.move(M(0,R['owner']),D(0))
    c.move(A(5),D(1))
    c.alu('cmp',D(1),0)
    B(6,'b8_b7_draw_call')  # no registered owner: preserve B7 behavior
    c.tst(D(0));B(7,'b8_b7_draw_call')
    c.lea(4,'b8_b7_end_trampoline_entry')
    c.move(M(5,END1),D(0))
    c.move(M(5,END2),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_draw_call')
    c.move(A(4),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_draw_call')
    c.lea(0,'b7_end_entry')
    c.move(A(0),M(5,END1))
    c.move(A(0),M(5,END2))
    L('b8_b7_draw_call')
    B(1,'b7_multiframe_draw_entry')
    c.move(D(3),M(2,F['result']))
    # Only a registered owner may replace the B7 End callbacks; this
    # is the same exact pair emitted by the unchanged B7 draw routine.
    Rptr()
    c.move(M(0,R['owner']),D(0))
    c.move(A(5),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_draw_return')
    c.tst(D(0));B(7,'b8_b7_draw_return')
    c.lea(4,'b7_end_entry')
    c.move(M(5,END1),D(0))
    c.move(M(5,END2),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_draw_return')
    c.move(A(4),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_draw_return')
    c.lea(0,'b8_b7_end_trampoline_entry')
    c.move(A(0),M(5,END1))
    c.move(A(0),M(5,END2))
    L('b8_b7_draw_return')
    c.move(M(2,F['result']),D(3))
    c.raw('4fef00204cdf77f774004e75')

    # Public Screen Close is an INSTRUCTION; preserve the entire ABI.
    L('b8_b7_close_trampoline_entry')
    c.raw('48e7fffe')
    B(1,'b7m2_close_reset_entry') # Original 64-slot reset -> B5 Close.
    Rptr()
    c.move(M(0,R['owner']),D(0))
    c.move(A(5),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_close_return')
    c.tst(D(0));B(7,'b8_b7_close_return')
    c.move(M(0,R['callback']),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,'b8_b7_close_return')
    c.raw('4e94')  # JSR (A4): registered fifth-unit B8 postclose.
    c.tst(D(3));B(7,'b8_b7_close_return') # Still live, never unbind.
    B(1,'b8_b7_clear_root')
    # After a successful explicit Close B7 keeps its native End callback
    # until End is invoked. Restore this baseline, not our stale B8 hook.
    c.lea(4,'b8_b7_end_trampoline_entry')
    c.move(M(5,END1),D(0))
    c.move(M(5,END2),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_close_return')
    c.move(A(4),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_close_return')
    c.lea(0,'b7_end_entry')
    c.move(A(0),M(5,END1))
    c.move(A(0),M(5,END2))
    L('b8_b7_close_return')
    c.raw('4cdf7fff4e75')

    # End callback: preserve all D0-D7/A0-A6 like existing B7 End.
    L('b8_b7_end_trampoline_entry')
    c.raw('48e7fffe')
    c.lea(4,'b8_b7_end_trampoline_entry')
    c.move(M(5,END1),D(0))
    c.move(M(5,END2),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_end_return')
    c.move(A(4),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_end_return')
    c.lea(0,'b7_end_entry')
    c.move(A(0),M(5,END1))
    c.move(A(0),M(5,END2))
    B(1,'b7_end_entry') # Checked B7 -> P0c -> original AGA End.
    Rptr()
    c.move(M(0,R['owner']),D(0))
    c.move(A(5),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_end_return')
    c.tst(D(0));B(7,'b8_b7_end_return')
    c.move(M(0,R['callback']),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,'b8_b7_end_return')
    c.raw('4e94')
    c.tst(D(3));B(7,'b8_b7_end_pending')
    B(1,'b8_b7_clear_root')
    B(0,'b8_b7_end_return')
    L('b8_b7_end_pending')
    # Reinstall only if B7 has deliberately left BOTH callbacks set to
    # its own End handler (timed-out native Safe/Disp close).
    c.lea(4,'b7_end_entry')
    c.move(M(5,END1),D(0))
    c.move(M(5,END2),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_end_return')
    c.move(A(4),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_end_return')
    c.lea(0,'b8_b7_end_trampoline_entry')
    c.move(A(0),M(5,END1))
    c.move(A(0),M(5,END2))
    L('b8_b7_end_return')
    c.raw('4cdf7fff4e75')

    # Private B8 fifth-unit callback registrar, no public token. A0 is
    # supplied by B8 source as LEA b8_service_postclose_entry(PC),A0.
    L('b8_b7_register_magic')
    c.raw('42385247')  # ASCII B8RG, must precede the registration entry.
    L('b8_b7_register_entry')
    c.raw('48e7cfee4fefffe0') # numeric 1/0, no clobber of AMOS A3
    c.move(A(7),A(2))
    c.move(A(0),M(2,F['postclose']))
    c.move(I(0),M(2,F['result']))
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'b8_b7_register_return')
    c.move(A(5),D(0));c.tst(D(0));B(7,'b8_b7_register_return')
    c.imm('and',1,D(0));B(6,'b8_b7_register_return')
    c.move(M(2,F['postclose']),D(0))
    c.tst(D(0));B(7,'b8_b7_register_return')
    c.imm('and',1,D(0));B(6,'b8_b7_register_return')
    c.move(M(2,F['postclose']),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_b7_register_return')
    # This must be a stable exact B7 End callback, or our own registered
    # shim on idempotent rearm. Any other callback pair is foreign.
    c.move(M(5,END1),D(0))
    c.move(M(5,END2),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_register_return')
    c.lea(4,'b7_end_entry')
    c.move(A(4),D(1))
    c.alu('cmp',D(1),0);B(7,'b8_b7_register_check_root')
    c.lea(4,'b8_b7_end_trampoline_entry')
    c.move(A(4),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_register_return')
    L('b8_b7_register_check_root')
    Rptr()
    c.move(M(0,R['owner']),D(0))
    c.tst(D(0));B(7,'b8_b7_register_commit')
    c.move(A(5),D(1));c.alu('cmp',D(1),0)
    B(6,'b8_b7_register_return')
    c.move(M(0,R['callback']),D(0))
    c.move(M(2,F['postclose']),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_b7_register_return')
    B(0,'b8_b7_register_arm')
    L('b8_b7_register_commit')
    c.move(A(5),M(0,R['owner']))
    c.move(M(2,F['postclose']),D(0))
    c.move(D(0),M(0,R['callback']))
    L('b8_b7_register_arm')
    c.lea(0,'b8_b7_end_trampoline_entry')
    c.move(A(0),M(5,END1))
    c.move(A(0),M(5,END2))
    c.move(I(1),M(2,F['result']))
    L('b8_b7_register_return')
    c.move(M(2,F['result']),D(3))
    c.raw('4fef00204cdf77f374004e75')

    # Shared native-owner root: zero after an actual successful Close/End.
    L('b8_b7_clear_root')
    Rptr()
    c.move(I(0),M(0,R['owner']))
    c.move(I(0),M(0,R['callback']))
    c.raw('4e75')
    L('b8_b7_hook_root')
    c.raw('00'*ROOT_SIZE)
    result=c.out()
    assert result.startswith(old)
    assert c.labels['b8_b7_draw_trampoline_entry']==len(old)
    assert c.labels['b8_b7_register_entry']==c.labels['b8_b7_register_magic']+4
    assert c.labels['b8_b7_hook_root']+ROOT_SIZE==len(result)
    assert len(result)%2==0 and len(result)<32766
    return result,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_b8_b7_hooks()
    print('M19 B8 B7-m2-local Draw/Close/End source-only',len(raw),
          sha256(raw).hexdigest(),
          'register',labels['b8_b7_register_entry'],
          'close',labels['b8_b7_close_trampoline_entry'],
          'end',labels['b8_b7_end_trampoline_entry'])
