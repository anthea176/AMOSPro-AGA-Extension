"""R77 native 68000-safe Aga C2P Close (no arguments), returns D3 1/0.

Uses the SAME 48-byte DBState ownership fields, cookie, and cleanup order
as R74's Screen Close / AMOS exit hooks, without changing those proven
legacy native entries or shifting the input-state block (R74/R75 regression).
The old automatic cleanup remains present; this explicit path clears ownership
first so a later Screen Close/End does not call DestroyContext twice.
"""
from __future__ import annotations
from m68k_emit import Code,D,A,M,I
from c2p_r74_open_emit import (
    MAGIC, STATE, LVO_WAITBLIT, LVO_C2P_DESTROY, LVO_CLOSELIBRARY,
)

F=dict(state=0, db=4, lib=8, ctx=12, gfx=16)
FRAME=48

def emit_close():
    """Return native bytes + symbols. No GetP marker, caller appends AP20."""
    c=Code(); B,L=c.branch,c.label
    def get(name,reg):c.move(M(2,F[name]),reg)
    def put(reg,name):c.move(reg,M(2,F[name]))

    # R74/R75 ABI: preserve D0,D1,D4-D7,A0-A2,A4-A6; do not touch A3/A5.
    c.raw('48e7efee')
    c.raw('4fefffd0')             # LEA -48(SP),SP
    c.move(A(7),A(2))
    c.move(I(0),D(3))             # Close without context -> 0
    c.move(M(5,STATE),A(4))       # A5 + $1C8 -> extension State
    c.move(A(4),D(0));c.tst(D(0));B(7,'finish')
    put(A(4),'state')
    c.move(M(4,32),A(4))         # State+32 -> existing 48-byte DBState
    c.move(A(4),D(0));c.tst(D(0));B(7,'finish')
    put(A(4),'db')
    c.move(M(4,40),D(0));c.imm('cmp',MAGIC,D(0));B(6,'finish')
    c.move(M(4,24),D(0));c.tst(D(0));B(7,'finish')
    put(D(0),'lib')
    c.move(M(4,28),D(0));c.tst(D(0));B(7,'finish')
    put(D(0),'ctx')
    get('state',A(4));c.move(M(4,8),D(0));put(D(0),'gfx')
    # Clear ALL C2P ownership fields before any OS/SDK call.
    # This is the same invariant as cleanup_core in R74.
    get('db',A(4))
    for off in (24,28,32,36,40):
        c.raw('42ac'+format(off,'04x')) # CLR.L offset(A4)
    get('gfx',A(6));c.move(A(6),D(0));c.tst(D(0));B(7,'destroy')
    c.call_os(LVO_WAITBLIT)
    L('destroy')
    get('ctx',A(0));get('lib',A(6));c.call_os(LVO_C2P_DESTROY)
    get('lib',A(1));c.raw('2c780004');c.call_os(LVO_CLOSELIBRARY)
    c.move(I(1),D(3))
    L('finish')
    c.raw('4fef0030')             # LEA 48(SP),SP
    c.raw('4cdf77f7')             # MOVEM restore
    c.raw('74004e75')             # MOVEQ #0,D2; RTS
    code=c.out()
    assert len(code)%2==0
    assert code[:8]==bytes.fromhex('48e7efee4fefffd0')
    assert code[-4:]==bytes.fromhex('74004e75')
    return code,c.labels

if __name__=="__main__":
    from hashlib import sha256
    code,labels=emit_close()
    print("R77 close native",len(code),"bytes",sha256(code).hexdigest(),labels)
