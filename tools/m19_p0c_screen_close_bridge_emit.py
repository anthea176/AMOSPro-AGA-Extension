#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0c experimental public Screen Close bridge in SOURCE-ONLY BOBS unit.

Do NOT install this as a library until the complete AP20 Gate A is proven.
Original AGA V2 unit is SHA-pinned and kept byte-for-byte intact; only the
public Close stub is redirected IN MEMORY by the separate experimental builder.

The AMOS extension initializer stores a pointer to native AGA State in
A5+456. That state is inside the SAME relocated V2 native unit as the old
public Screen Close body. A state-relative JSR therefore crosses BOBS -> AGA
without a signed PC16 cross-unit branch or an assumed absolute load address.

For the exact R88-derived P0b source only:
  AGA V2 dispatcher bytes: 34
  AGA state offset in V2 unit: 0x1c2 (confirmed by exact init LEA+store)
  old public Close native offset: 34 + AP20 RBSR offset 2008 == 0x7fa
  delta (Close - State): +0x638
The builder MUST reverify the original AP20 HUNK, AGA init LEA and old Close
prologue byte-exactly, and reject ALL changes to base/layout. The wrapper
also checks the legacy Close prologue at runtime before any Chip is freed.

Behavior: on CPU020, verify old Close entry, call private P0c preclose,
if it succeeds invoke actual legacy AGA Close by JSR (A4). If it fails,
abort without closing the screen. Preserve full original D0-D7/A0-A6
including input D2/D3 (legacy Screen Close is an INSTRUCTION), and A7.

The real AMOS End callback (A5+460/464) is NOT hooked here. No new token,
no invasive patch to any old native code. CPU020 Gate A only until tested.
"""
from __future__ import annotations

from m68k_emit import Code,D,A,M,I
from m19_p0c_screen_preclose_emit import emit_screen_preclose

AGA_STATE_OFFSET = 0x1c2
AGA_CLOSE_ENTRY_OFFSET = 0x7fa
CLOSE_STATE_DELTA = AGA_CLOSE_ENTRY_OFFSET-AGA_STATE_OFFSET
assert CLOSE_STATE_DELTA == 0x638
STATE_PTR_A5=0x1c8
# Exact frozen R88/P0b 12-byte native Screen Close entry, runtime signature.
CLOSE_SIGNATURE=(0x48e7fffe,0x246d01c8,0x600001d0)


def emit_screen_close_bridge() -> tuple[bytes,dict[str,int]]:
    previous,old_labels=emit_screen_preclose()
    c=Code()
    c.raw(previous.hex())
    c.labels.update(old_labels)
    B,L=c.branch,c.label

    L('screen_close_bridge_entry')
    c.raw('48e7fffe')   # MOVEM.L D0-D7/A0-A6,-(SP)
    # Explicit CPU gate, independent of the old AGA native CPU support.
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'bridge_return')
    c.move(A(5),D(0));c.tst(D(0));B(7,'bridge_return')
    c.imm('and',1,D(0));B(6,'bridge_return')
    # The AGA init pins State to a PC-relative address in its own native unit.
    c.move(M(5,STATE_PTR_A5),D(0))
    c.tst(D(0));B(7,'bridge_return')
    c.move(D(0),D(1))
    c.imm('and',1,D(1));B(6,'bridge_return')
    c.imm('add',CLOSE_STATE_DELTA,D(0))
    B(5,'bridge_return')
    c.move(D(0),A(4))   # owned old Close address (survives preclose helper)

    # Require a valid mapped native entry, NOT an assumed adjacent segment.
    c.move(A(4),A(1))
    c.raw('2c780004')   # ExecBase from 4.W
    c.call_os(-534)     # TypeOfMem(old native Close)
    c.tst(D(0));B(7,'bridge_return')
    for i,word in enumerate(CLOSE_SIGNATURE):
        c.move(M(4,i*4),D(0))
        c.imm('cmp',word,D(0))
        B(6,'bridge_return')

    # Preclose must complete BEFORE the old AGA Screen Close starts.
    B(1,'screen_preclose_entry')
    c.tst(D(3));B(7,'bridge_return')
    c.raw('4e94')        # JSR (A4), actual old Screen Close, AGA group
    L('bridge_return')
    c.raw('4cdf7fff')  # MOVEM.L (SP)+,D0-D7/A0-A6
    c.raw('4e75')      # RTS

    code=c.out()
    assert code[:len(previous)]==previous,'P0b/P0c verified prefix changed'
    assert c.labels['screen_close_bridge_entry']==len(previous)
    assert len(code)%2==0 and len(code)<32766
    return code,c.labels


if __name__=='__main__':
    from hashlib import sha256
    src,labels=emit_screen_close_bridge()
    print('M19 P0c IN MEMORY experimental Screen Close bridge SOURCE ONLY',
          len(src),sha256(src).hexdigest(),labels['screen_close_bridge_entry'],
          'NO AMOS End hook, NOT installed, no WinUAE/Compiler Gate')
