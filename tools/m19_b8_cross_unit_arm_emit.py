#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 SOURCE ONLY: discover B7-local registration via live End pointer.

No cross-unit BSR, no guessed load address, and no absolute code pointer
built from AP20 section concatenation. The verified B7-m2 callback A5+1cc
is the address of B7's b7_end_entry in its relocated native unit. The
local registrar is reachable by its source-verified POSITIVE label delta.
Check B7 End prologue, live mapping and B8RG marker before an indirect
JSR; the B7-side registrar independently checks original End callback
slots, A5 owner and valid B8 post-Close pointer.

This single-shot arm must occur after an actual successful B7 Draw, and
before an eventual user-visible B8 Update returns. If Draw never succeeds,
no registration is attempted; the orchestrator must roll back any pool
allocation on failure. The API/token/Close hook is NOT installed.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b8_safe_lifecycle_emit import emit_b8_safe_lifecycle
from m19_b8_b7_hook_emit import emit_b8_b7_hooks, END1, END2
from m19_b8_page_manager_emit import R as ROOT

FRAME=64
F=dict(result=0,callback=4,regaddr=8)
MAGIC=0x42385247


def emit_b8_cross_unit_arm() -> tuple[bytes,dict[str,int]]:
    old,labels=emit_b8_safe_lifecycle()
    _,b7_labels=emit_b8_b7_hooks()
    diff=b7_labels['b8_b7_register_entry']-b7_labels['b7_end_entry']
    assert diff>4 and diff<32766 and diff%2==0
    c=Code(); c.raw(old.hex()); c.labels.update(labels)
    B,L=c.branch,c.label

    L('b8_service_arm_b7_entry')
    c.raw('48e7cfee4fefffc0')
    c.move(A(7),A(2))
    c.move(I(0),M(2,F['result']))
    c.raw('20780004') # ExecBase
    c.move(A(0),D(0));c.tst(D(0));B(7,'b8_arm_return')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1) # 020 min CPU
    B(7,'b8_arm_return')
    c.lea(4,'b8_service_root')
    c.move(M(4,ROOT['owner']),D(0))
    c.move(A(5),D(1));c.alu('cmp',D(1),0);B(6,'b8_arm_return')
    c.tst(D(0));B(7,'b8_arm_return')
    c.tst(M(4,ROOT['screen']));B(7,'b8_arm_return')
    # Both B7 callbacks must be the same, source-pinned B7 End entry.
    c.move(M(5,END1),D(0))
    c.move(M(5,END2),D(1))
    c.alu('cmp',D(1),0);B(6,'b8_arm_return')
    c.tst(D(0));B(7,'b8_arm_return')
    c.move(D(0),D(1));c.imm('and',1,D(1))
    B(6,'b8_arm_return')
    c.move(D(0),M(2,F['callback']))
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534) # TypeOfMem(B7 End)
    c.tst(D(0));B(7,'b8_arm_return')
    c.move(M(2,F['callback']),D(0))
    c.imm('add',3,D(0));B(5,'b8_arm_return')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_arm_return')
    c.move(M(2,F['callback']),A(4))
    c.move(M(4,0),D(0))
    c.imm('cmp',0x48e7fffe,D(0))
    B(6,'b8_arm_return')
    # The registrar is reached by an offset WITHIN THE SAME B7 code unit.
    c.move(M(2,F['callback']),D(0))
    c.imm('add',diff,D(0));B(5,'b8_arm_return')
    c.move(D(0),M(2,F['regaddr']))
    c.imm('sub',4,D(0));B(5,'b8_arm_return')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_arm_return')
    c.move(M(2,F['regaddr']),D(0))
    c.imm('add',3,D(0));B(5,'b8_arm_return')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'b8_arm_return')
    c.move(M(2,F['regaddr']),A(4))
    c.move(M(4,-4),D(0))
    c.imm('cmp',MAGIC,D(0));B(6,'b8_arm_return')
    c.lea(0,'b8_service_postclose_entry')
    c.raw('4e94') # JSR (A4) verified native B7 local registrar
    c.tst(D(3));B(7,'b8_arm_return')
    c.move(I(1),M(2,F['result']))
    L('b8_arm_return')
    c.move(M(2,F['result']),D(3))
    c.raw('4fef00404cdf77f374004e75')
    code=c.out()
    assert code.startswith(old)
    assert c.labels['b8_service_arm_b7_entry']==len(old)
    assert len(code)<32766 and len(code)%2==0
    return code,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_b8_cross_unit_arm()
    print('M19 B8 MC68020 cross-unit callback-derived registrar SOURCE ONLY',
          len(raw),sha256(raw).hexdigest(),
          'arm',labels['b8_service_arm_b7_entry'])
