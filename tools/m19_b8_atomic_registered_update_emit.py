#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 atomic registered-Update native wrapper, SOURCE ONLY.

After a VALID existing B7/B8 registration, one private MC68020 call:
  - checks B7's Draw trampoline via source-relative End shim pointer,
  - preflights all 64 actual AGBO sources, restores old back if needed,
  - captures current decor on the Safe non-displayed physical back,
  - calls the EXACT native B7 Draw trampoline by verified indirect JSR,
  - commits only if B7 Draw and B8 Update Finish both return 1,
  - otherwise latches B7 DIRTY with transactional Abort and returns 0.

No intermediate exposure of Prepare/Draw/Finish to AMOS; NO implicit Swap.
Aga Bob Draw still executes the original B7 validated 64-Bob native engine.

IMPORTANT: NOT a complete public "Aga Bob Update". The first Update
requires a bootstrap that safely binds snapshots and registers B7's End
callback without drawing over a background that has not yet been captured.
This entry intentionally REFUSES when B7/B8 is not yet registered.
AMOS token ABI / Compiler Gates B/C are not implied or installed.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b8_clear_update_tx_emit import emit_b8_clear_update_tx, F
from m19_b8_b7_hook_emit import emit_b8_b7_hooks

DRAW_SLOT=44  # unused byte range of existing 96-byte B8 transaction frame
FRAME=96


def emit_b8_atomic_registered_update() -> tuple[bytes, dict[str,int]]:
    old, labels = emit_b8_clear_update_tx()
    _, b7 = emit_b8_b7_hooks()
    delta = b7['b8_b7_draw_trampoline_entry'] - b7['b8_b7_end_trampoline_entry']
    if delta >= 0 or delta <= -32766 or delta & 1:
        raise ValueError('B7 Draw is not a safe source-verified relative entry')
    c=Code();c.raw(old.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    L('b8_service_update_atomic_registered_entry')
    c.raw('48e7cfee4fefffa0')  # AMOS preserved set, 96-byte frame
    c.move(A(7),A(4))
    c.move(I(0),M(4,F['result']))

    # Refuse unregistered/foreign owners before accessing any B7 code.
    B(1,'b8_tx_validate')
    c.tst(D(3));B(7,'b8_atomic_return')

    # Cross-unit: B7's End shim is a checked, relocatable callback.
    # The Draw wrapper is in THAT SAME B7 native group: no inter-unit BSR.
    c.move(M(4,F['callback']),D(0))
    c.imm('sub',-delta,D(0))
    B(5,'b8_atomic_return')
    c.move(D(0),M(4,DRAW_SLOT))

    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534) # TypeOfMem start
    c.tst(D(0));B(7,'b8_atomic_return')
    c.move(M(4,DRAW_SLOT),D(0))
    c.imm('add',7,D(0));B(5,'b8_atomic_return')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534) # TypeOfMem prologue end
    c.tst(D(0));B(7,'b8_atomic_return')
    c.move(M(4,DRAW_SLOT),A(0))
    c.move(M(0,0),D(0))
    c.imm('cmp',0x48e7efee,D(0));B(6,'b8_atomic_return')
    c.move(M(0,4),D(0))
    c.imm('cmp',0x4fefffe0,D(0));B(6,'b8_atomic_return')

    # This is a single public-call-sized transaction. The validated
    # underlying B7 64-image preflight runs before the FIRST pixel copy.
    B(1,'b8_service_update_prepare_entry')
    c.tst(D(3));B(7,'b8_atomic_return')
    c.move(M(4,DRAW_SLOT),A(0))
    c.raw('4e90') # JSR (A0) exact B7 local Draw wrapper
    c.tst(D(3));B(7,'b8_atomic_abort')
    B(1,'b8_service_update_finish_entry')
    c.tst(D(3));B(7,'b8_atomic_abort')
    c.move(I(1),M(4,F['result']))
    B(0,'b8_atomic_return')

    L('b8_atomic_abort')
    B(1,'b8_service_update_abort_entry') # Leaves B7 DIRTY, no Swap
    L('b8_atomic_return')
    c.move(M(4,F['result']),D(3))
    c.move(I(0),D(2))
    c.raw('4fef00604cdf77f34e75')

    result=c.out()
    assert result.startswith(old) and c.labels['b8_service_update_atomic_registered_entry']==len(old)
    assert len(result)%2==0 and len(result)<32766
    return result,c.labels


if __name__=='__main__':
    from hashlib import sha256
    data,labels=emit_b8_atomic_registered_update()
    print('M19 B8 atomic REGISTERED Update source-only MC68020',
          len(data),sha256(data).hexdigest(),
          labels['b8_service_update_atomic_registered_entry'])
