#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 SafePort: bounded VBL acquisition before retrying public Bob Clear.

APPEND-ONLY after the byte-exact M19 B8 first-Update native fifth unit.
No changes to B7/B8 predecessors. On a failed Clear, retry ONLY when
the *live* owner, screen, DB, snapshot pool and pending Safe flag agree.
Never retry a missing snapshot or a foreign/stale screen. At most three
graphics.library WaitTOF (-270) calls, checked against AmigaOS AutoDocs;
each subsequent attempt runs the UNCHANGED atomic B8 Clear validator.
No busy-spin, no WaitPort deadlock, no implicit Swap, no fake success.
A remaining failure stays DIRTY and prevents presentation.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b8_first_update_emit import emit_b8_first_update
from m19_b8_page_manager_emit import R as B8ROOT
from m19_b8_back_selector_emit import STATE_OFF

MAX_SAFE_VBLS = 3
F = dict(result=0, remaining=4, db=8, state=12, gfx=16)


def emit_b8_safe_retry() -> tuple[bytes,dict[str,int]]:
    old, labels = emit_b8_first_update()
    c = Code()
    c.raw(old.hex())
    c.labels.update(labels)
    B,L = c.branch,c.label

    L('b8_service_clear_wait_safe_entry')
    c.raw('48e7cfee4fefffc0')  # AMOS preserved, 64-byte local frame
    c.move(A(7),A(4))
    c.move(I(0),M(4,F['result']))
    c.move(I(MAX_SAFE_VBLS),M(4,F['remaining']))

    L('b8_clear_wait_try')
    B(1,'b8_service_clear_guard_entry')
    c.tst(D(3)); B(6,'b8_clear_wait_success')
    c.move(M(4,F['remaining']),D(0))
    c.tst(D(0)); B(7,'b8_clear_wait_return')

    # Clear may have marked the guard DIRTY. Do NOT wait/retry unless the
    # same current AMOS owner still owns a pool and a valid old snapshot.
    c.lea(2,'b8_service_root')
    c.move(M(2,B8ROOT['owner']),D(0))
    c.tst(D(0)); B(7,'b8_clear_wait_return')
    c.move(A(5),D(1));c.alu('cmp',D(1),0)
    B(6,'b8_clear_wait_return')
    c.tst(M(2,B8ROOT['valid']))
    B(7,'b8_clear_wait_return')

    c.move(M(2,B8ROOT['db']),D(0))
    c.tst(D(0)); B(7,'b8_clear_wait_return')
    c.move(D(0),M(4,F['db']))
    c.imm('and',1,D(0)); B(6,'b8_clear_wait_return')

    # Verify DB mapping (start/end) BEFORE reading the pending Safe flag.
    c.move(M(4,F['db']),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0)); B(7,'b8_clear_wait_return')
    c.move(M(4,F['db']),D(0))
    c.imm('add',23,D(0)); B(5,'b8_clear_wait_return')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0)); B(7,'b8_clear_wait_return')

    # Check the same live owner/State/Screen/DB still links to the pool.
    c.move(M(5,STATE_OFF),D(0))
    c.tst(D(0)); B(7,'b8_clear_wait_return')
    c.move(D(0),M(4,F['state']))
    c.imm('and',1,D(0)); B(6,'b8_clear_wait_return')
    c.move(M(4,F['state']),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0)); B(7,'b8_clear_wait_return')
    c.move(M(4,F['state']),D(0))
    c.imm('add',35,D(0)); B(5,'b8_clear_wait_return')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0)); B(7,'b8_clear_wait_return')
    c.move(M(4,F['state']),A(0))
    c.move(M(0,32),D(0))
    c.move(M(4,F['db']),D(1))
    c.alu('cmp',D(1),0); B(6,'b8_clear_wait_return')
    c.lea(2,'b8_service_root')
    c.move(M(2,B8ROOT['screen']),D(0))
    c.move(M(4,F['state']),A(0))
    c.move(M(0,0),D(1))
    c.alu('cmp',D(1),0); B(6,'b8_clear_wait_return')

    c.move(M(4,F['db']),A(0))
    c.move(M(0,20),D(0))
    c.imm('and',1,D(0))
    B(7,'b8_clear_wait_return')  # No pending Safe: another real failure.

    # Graphics library must be a mapped even pointer. The prior Clear
    # safely rejected this state; NEVER jump through an unchecked base.
    c.move(M(4,F['state']),A(0))
    c.move(M(0,8),D(0))
    c.tst(D(0)); B(7,'b8_clear_wait_return')
    c.move(D(0),M(4,F['gfx']))
    c.imm('and',1,D(0)); B(6,'b8_clear_wait_return')
    c.move(M(4,F['gfx']),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0)); B(7,'b8_clear_wait_return')

    # Verified NDK graphics.library LVO -270 = WaitTOF().
    # One vertical blank, not a CPU spin or an unbounded WaitPort call.
    c.move(M(4,F['gfx']),A(6))
    c.call_os(-270)
    c.move(M(4,F['remaining']),D(0))
    c.quick(1,D(0),sub=True)
    c.move(D(0),M(4,F['remaining']))
    B(0,'b8_clear_wait_try')

    L('b8_clear_wait_success')
    c.move(I(1),M(4,F['result']))
    L('b8_clear_wait_return')
    c.move(M(4,F['result']),D(3))
    c.raw('4fef00404cdf77f374004e75')  # restore, THEN D2=0
    new=c.out()
    assert new.startswith(old) and new[len(old):]
    assert c.labels['b8_service_clear_wait_safe_entry']==len(old)
    assert len(new)%2==0 and len(new)<32766
    return new,c.labels


if __name__=='__main__':
    from hashlib import sha256
    old,_=emit_b8_first_update()
    code,labs=emit_b8_safe_retry()
    print('M19 B8 bounded Safe retry MC68020 SOURCE ONLY',
          len(code),len(code)-len(old),sha256(code).hexdigest(),
          labs['b8_service_clear_wait_safe_entry'])
