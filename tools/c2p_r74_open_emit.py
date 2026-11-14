"""R74 native 68000-safe entry: Aga C2P Open(Bank) -> D3=1/0.

Only accepts AGA private 320x256, depth 4..8, existing DoubleBuffer.
Passes an externally-owned live AMOS DATA bank to c2p.library v1.9.
All error paths clean up locally; successful context is stored in an
EXTENDED 48-byte DBState owned by the private screen's double buffering.

Close and AMOS-exit hooks, appended into the original Screen Close entry,
release the C2P context, bitmap and library before the DBState is freed.

This emitter is NOT itself an installed library, Gate A or a WinUAE result.
"""
from __future__ import annotations
from m68k_emit import Code, D, A, M, POST, I
from amos_main_abi import main_index, rjsr

ENTRY_OPEN=70
DB_ALLOC_OLD=24
DB_ALLOC_NEW=48
STATE=0x1c8
LVO_TYPEOFMEM=-534
LVO_OPENLIBRARY=-552
LVO_CLOSELIBRARY=-414
LVO_WAITBLIT=-228
LVO_C2P_CREATE=-48
LVO_C2P_INITIALIZE=-54
LVO_C2P_DESTROY=-60
LVO_C2P_GET=-66
LVO_C2P_SET=-72
BANK= rjsr(main_index('Bnk.GetAdr'))
MAGIC=0x43325031  # ASCII 'C2P1' (cookie DBState+40)
CHUNKY=320*256
F=dict(bank=0,state=4,db=8,base=12,banklen=16,depth=20,lib=24,ctx=28,bmp=32)
FRAME=64


def emit_open():
    """Return (native bytes, Code labels). No AP20 GetP marker."""
    c=Code();B,L=c.branch,c.label
    def get(k,d): c.move(M(2,F[k]),d)
    def put(s,k): c.move(s,M(2,F[k]))
    def ensure_type_mem(reg, fail='reject'):
        c.move(reg,A(1))
        c.raw('2c780004')
        c.call_os(LVO_TYPEOFMEM)
        c.tst(D(0));B(7,fail)
    def set_param(p, v):
        get('ctx',A(0))
        c.move(I(p),D(0))
        if isinstance(v,int): c.move(I(v),D(1))
        else: get(v,D(1))
        get('lib',A(6))
        c.call_os(LVO_C2P_SET)
        c.tst(D(0));B(6,'release')

    # Standard AP20 integer-function ABI: D3 is Bank; D2=0 on return.
    c.raw('48e7efee')             # MOVEM D0-D1/D4-D7/A0-A2/A4-A6
    c.raw('4fefffc0')             # LEA -64(SP),SP
    c.move(A(7),A(2))
    put(D(3),'bank')
    c.move(I(0),D(3))
    c.move(I(0),D(0));put(D(0),'lib');put(D(0),'ctx')

    # Guard using only plain 68000 instructions.  ExecBase.AttnFlags bit 1.
    c.raw('20780004')            # MOVEA.L 4.W,A0
    c.move(A(0),D(0));c.tst(D(0));B(7,'reject')
    c.move(I(0),D(0));c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1)     # BTST #AFF_68020,D0
    B(7,'reject')

    get('bank',D(0));c.imm('cmp',5,D(0));B(5,'reject')
    c.imm('cmp',65535,D(0));B(2,'reject')
    c.move(M(5,STATE),A(4));c.move(A(4),D(0));c.tst(D(0));B(7,'reject')
    put(A(4),'state')
    c.move(M(4),D(0));c.tst(D(0));B(7,'reject') # screen exists
    for offset,value in ((12,320),(16,256)):
        c.move(M(4,offset),D(0));c.imm('cmp',value,D(0));B(6,'reject')
    c.move(M(4,28),D(0))
    c.imm('cmp',4,D(0));B(5,'reject')
    c.imm('cmp',8,D(0));B(2,'reject')
    put(D(0),'depth')
    c.move(M(4,32),A(4));c.move(A(4),D(0));c.tst(D(0));B(7,'reject')
    put(A(4),'db')
    # Check that allocated 48-byte DBState is not already attached to C2P.
    for offset in (24,28,40):
        c.move(M(4,offset),D(0));c.tst(D(0));B(6,'reject')
    for offset in (0,4):
        c.move(M(4,offset),D(0));c.tst(D(0));B(7,'reject')

    # AMOS bank lookup and full native header validation. No raw bank number
    # may be interpreted as a memory pointer.  Only DATA/WORK accepted.
    get('bank',D(0));c.raw(BANK.hex())
    c.move(A(0),D(5))
    c.imm('cmp',24,D(5));B(3,'reject')
    c.move(D(5),D(0));c.imm('and',1,D(0));B(6,'reject')
    put(D(5),'base')
    ensure_type_mem(D(5))
    get('base',D(0));c.imm('sub',24,D(0));ensure_type_mem(D(0))
    get('base',A(0))
    c.move(M(0,-16),D(0));get('bank',D(1))
    c.alu('cmp',D(1),0);B(6,'reject')
    c.move(I(0),D(0));c.move(M(0,-12),D(0),'w')
    c.imm('and',0xfffd,D(0),'w')
    c.imm('cmp',1,D(0),'w');B(6,'reject')
    get('base',A(0));c.move(M(0,-20),D(0))
    c.imm('cmp',CHUNKY+16,D(0));B(5,'reject')
    c.imm('sub',16,D(0));put(D(0),'banklen')
    get('base',D(0));c.imm('add',CHUNKY-1,D(0));B(5,'reject')
    ensure_type_mem(D(0))

    # The SDK explicitly permits a user-provided chunky pointer at init.
    c.raw('2c780004');c.lea(1,'c2p_library_name')
    c.move(I(1),D(0));c.call_os(LVO_OPENLIBRARY)
    c.tst(D(0));B(7,'reject')
    put(D(0),'lib')
    get('lib',A(6));c.call_os(LVO_C2P_CREATE)
    c.tst(D(0));B(7,'release')
    put(D(0),'ctx')

    set_param(1,1)              # TYPE=BITMAP, SDK owns Chip bitmap
    set_param(2,320)            # WIDTH
    set_param(3,256)            # HEIGHT
    set_param(9,'depth')        # 4..8 planes
    set_param(4,'base')         # external AMOS chunky 81920 bytes
    get('ctx',A(0));get('lib',A(6))
    c.call_os(LVO_C2P_INITIALIZE)
    c.tst(D(0));B(6,'release')
    get('ctx',A(0));c.move(I(5),D(0));get('lib',A(6))
    c.call_os(LVO_C2P_GET)      # output bitmap from SDK
    c.tst(D(0));B(7,'release')
    put(D(0),'bmp')
    ensure_type_mem(D(0),'release')
    get('bmp',A(0))
    c.move(I(0),D(0));c.move(M(0,0),D(0),'w')
    c.imm('cmp',40,D(0));B(6,'release')
    c.move(I(0),D(0));c.move(M(0,2),D(0),'w')
    c.imm('cmp',256,D(0));B(5,'release')
    c.move(I(0),D(0));c.move(M(0,5),D(0),'b')
    get('depth',D(1));c.alu('cmp',D(1),0);B(6,'release')

    # Success: place pointers in the CLEAR-allocated 48-byte DBState.
    # The cookie is written LAST; Screen Close must never free partial data.
    get('db',A(4))
    get('lib',D(0));c.move(D(0),M(4,24))
    get('ctx',D(0));c.move(D(0),M(4,28))
    get('bank',D(0));c.move(D(0),M(4,32))
    get('depth',D(0));c.move(D(0),M(4,36))
    c.move(I(MAGIC),M(4,40))
    c.move(I(1),D(3))
    B(0,'finish')

    # All partial failures are transactionally cleaned.
    L('release')
    get('ctx',D(0));c.tst(D(0));B(7,'release_lib')
    get('ctx',A(0));get('lib',A(6));c.call_os(LVO_C2P_DESTROY)
    L('release_lib')
    get('lib',D(0));c.tst(D(0));B(7,'reject')
    get('lib',A(1));c.raw('2c780004');c.call_os(LVO_CLOSELIBRARY)
    L('reject')
    c.move(I(0),D(3))
    L('finish')
    c.raw('4fef0040')
    c.raw('4cdf77f7')
    c.raw('74004e75')
    L('c2p_library_name')
    c.raw(b'c2p.library\0'.hex())
    code=c.out()
    assert len(code)%2==0
    assert code.count(BANK)==1
    return code,c.labels


def emit_cleanup_hooks():
    """Two close paths and one shared idempotent DBState cleanup routine.

    The builder patches jmp_normal to original entry08 +0x126 and
    jmp_program_exit to original entry00 +0x1C8.
    """
    c=Code();B,L=c.branch,c.label
    L('screen_hook')
    B(1,'cleanup_core')
    L('jmp_normal')
    c.raw('60000000')              # patched absolute within monolith
    L('program_exit_hook')
    B(1,'cleanup_core')
    L('jmp_program_exit')
    c.raw('60000000')              # patched absolute within monolith
    L('cleanup_core')
    c.raw('48e7fffe')              # save all D0-D7/A0-A6
    c.move(A(2),D(0));c.tst(D(0));B(7,'done')
    c.move(M(2,32),A(4));c.move(A(4),D(0));c.tst(D(0));B(7,'done')
    c.move(M(4,40),D(0));c.imm('cmp',MAGIC,D(0));B(6,'done')
    c.move(M(4,28),D(5));c.move(M(4,24),D(6))
    # Clear ownership before calling any OS function (safe on reentrancy).
    for offset in (24,28,32,36,40):
        c.raw('42ac'+format(offset,'04x'))
    c.move(D(6),D(0));c.tst(D(0));B(7,'done')
    # Ensure future C2P Convert cannot leave a blit pending at destruction.
    c.move(M(2,8),A(6));c.move(A(6),D(0));c.tst(D(0));B(7,'destroy')
    c.call_os(LVO_WAITBLIT)
    L('destroy')
    c.move(D(5),D(0));c.tst(D(0));B(7,'close_library')
    c.move(D(5),A(0));c.move(D(6),A(6));c.call_os(LVO_C2P_DESTROY)
    L('close_library')
    c.move(D(6),A(1));c.raw('2c780004');c.call_os(LVO_CLOSELIBRARY)
    L('done')
    c.raw('4cdf7fff')
    c.raw('4e75')
    return c.out(),c.labels
