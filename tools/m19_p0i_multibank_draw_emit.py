#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0i source-only private persistent Bob -> Chip -> Safe Blitter route.

Two PRIVATE entries, no public Draw, no new token, no implicit Swap:
 - routed_paint_one_entry: D0=1..64 object ID; called AFTER a successful
   frame preflight. Skips inactive entries; an active stale source REFUSES.
 - routed_paint_all_entry: a full P0h 64-object bank stamp preflight, then
   synchronous ID-ordered drawing to the AGA Safe back BitMap.

Each object retains its ORIGINAL AGBO bank independently of Aga Bob Bank.
The legacy P0c registry and Safe painter require BOBS bank_active_state;
the experiment temporarily projects a fully verified object bank into
that 12-byte *PRIVATE* shadow, then unconditionally restores the prior
triple on EVERY success/failure path. No AMOS bank selection API is called.

This scoped native state is NOT reentrant: only foreground synchronous
draw and no concurrent BOBS command is supported. This is an explicit
limitation BEFORE public API/real WinUAE. Staging still uses the exact P0c
allocation/End bridge. A failed middle paint can leave partial changes in
the hidden back buffer, but it NEVER presents/swaps it.
"""
from __future__ import annotations

from hashlib import sha256
from m68k_emit import Code,D,A,M,I
from amos_main_abi import main_index,rjsr
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5
from m19_p0h_frame_preflight_emit import emit_frame_preflight,MAX_BOBS

GETADR=rjsr(main_index('Bnk.GetAdr'))
FRAME=160
RECORD=96
F=dict(ident=0,result=4,bank=8,image=12,x=16,y=20,
       old_bank=24,old_ptr=28,old_head=32,switched=36,
       state=40,gfx=44,ptr=48,head=52)
assert RECORD+24 <= FRAME


def emit_multibank_paint() -> tuple[bytes,dict[str,int]]:
    old, old_labels=emit_frame_preflight()
    c=Code();c.raw(old.hex());c.labels.update(old_labels)
    B,L=c.branch,c.label
    def S(src,name):c.move(src,M(2,F[name]))
    def G(name,dst):c.move(M(2,F[name]),dst)
    def record_addr():
        c.move(A(2),D(0));c.imm('add',RECORD,D(0));c.move(D(0),A(1))

    L('routed_paint_one_entry')
    c.raw('48e7efee')               # AMOS preserved set
    c.raw('4fefff60')               # frame 160 bytes
    c.move(A(7),A(2))
    S(D(0),'ident')
    S(I(0),'result')
    S(I(0),'switched')

    # Explicit internal contract: ID 1..64; caller should preflight first.
    B(1,'registry_cpu_guard');c.tst(D(0));B(7,'route_return')
    G('ident',D(0))
    c.imm('cmp',1,D(0));B(5,'route_return')
    c.imm('cmp',MAX_BOBS,D(0));B(2,'route_return')

    record_addr()
    G('ident',D(0))
    B(1,'relay_read_entry')
    c.tst(D(3));B(7,'route_inactive')
    record_addr()
    G('ident',D(0))
    B(1,'relay_checked_read_entry')
    c.tst(D(3));B(7,'route_return')
    c.move(M(2,RECORD+0),D(0));S(D(0),'bank')
    c.move(M(2,RECORD+4),D(0));S(D(0),'image')
    c.move(M(2,RECORD+8),D(0));S(D(0),'x')
    c.move(M(2,RECORD+12),D(0));S(D(0),'y')

    # The checked relay verified the ORIGINAL AGA End prologue and owner.
    # Reuse P0c's graphics base, but never assume selected bank is our source.
    c.move(M(5,0x1c8),D(0));S(D(0),'state')
    c.tst(D(0));B(7,'route_return')
    G('state',A(0))
    c.move(M(0,8),D(0));S(D(0),'gfx')
    c.tst(D(0));B(7,'route_return')
    c.imm('and',1,D(0));B(6,'route_return')
    G('gfx',A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'route_return')

    # Independent AMOS Bnk.GetAdr + real Cur_Banks identity. This
    # never calls Aga Bob Bank and never allocates/replaces an AMOS bank.
    G('bank',D(0));c.raw(GETADR.hex())
    c.move(A(0),D(0));S(D(0),'ptr')
    c.imm('cmp',24,D(0));B(3,'route_return')
    c.imm('and',1,D(0));B(6,'route_return')
    G('ptr',A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'route_return')
    c.move(M(5,CUR_BANKS_A5),D(0));S(D(0),'head')
    c.tst(D(0));B(7,'route_return')
    c.imm('and',1,D(0));B(6,'route_return')

    # Save all three private selected-bank words before exposing ANY
    # temporary shadow. All subsequent paths converge on route_restore.
    c.lea(0,'bank_active_state')
    c.move(M(0,0),D(1));S(D(1),'old_bank')
    c.move(M(0,4),D(1));S(D(1),'old_ptr')
    c.move(M(0,8),D(1));S(D(1),'old_head')
    G('bank',D(1));c.move(D(1),M(0,0))
    G('ptr',D(1));c.move(D(1),M(0,4))
    G('head',D(1));c.move(D(1),M(0,8))
    S(I(1),'switched')

    # Once per bank, validate/stage the original AGBO payload in Chip.
    # The existing P0c registry caches per bank, so repeated Bobs reuse it.
    G('bank',D(3));B(1,'registry_lookup_entry')
    c.tst(D(3));B(6,'route_arm_end')
    G('bank',D(3));G('gfx',A(4))
    B(1,'registry_prepare_entry')
    c.tst(D(3));B(7,'route_restore')
    L('route_arm_end')
    B(1,'program_end_arm_entry')
    c.tst(D(3));B(7,'route_unwind')

    # Original Safe painter selects the NON-displayed bitmap and WaitBlit.
    G('bank',D(3));G('image',D(0))
    G('x',D(1));G('y',D(4))
    B(1,'safe_bank_blit_entry')
    c.tst(D(3));B(7,'route_restore')
    S(I(1),'result')
    B(0,'route_restore')

    L('route_unwind')
    G('bank',D(3));G('gfx',A(4))
    B(1,'registry_free_entry')
    B(0,'route_restore')

    L('route_inactive')
    S(I(1),'result')   # only valid after frame preflight
    B(0,'route_return')

    L('route_restore')
    G('switched',D(0));c.tst(D(0));B(7,'route_return')
    c.lea(0,'bank_active_state')
    G('old_bank',D(1));c.move(D(1),M(0,0))
    G('old_ptr',D(1));c.move(D(1),M(0,4))
    G('old_head',D(1));c.move(D(1),M(0,8))
    S(I(0),'switched')
    L('route_return')
    G('result',D(3))
    c.raw('4fef00a0')          # frame 160
    c.raw('4cdf77f7')
    c.raw('74004e75')

    # Public API is unchanged: this private entry first verifies ALL 64
    # bank stamps, then paints objects synchronously in ascending order.
    L('routed_paint_all_entry')
    c.raw('48e7efee')
    c.raw('4fefffe0')         # local frame 32 bytes
    c.move(A(7),A(2))
    c.move(I(0),M(2,0))      # result
    B(1,'frame_bank_preflight_entry')
    c.tst(D(3));B(7,'route_all_return')
    c.move(I(1),M(2,4))      # object ID
    L('route_all_next')
    c.move(M(2,4),D(0))
    B(1,'routed_paint_one_entry')
    c.tst(D(3));B(7,'route_all_return')
    c.move(M(2,4),D(0));c.quick(1,D(0))
    c.move(D(0),M(2,4))
    c.imm('cmp',MAX_BOBS,D(0))
    B(3,'route_all_next')   # BLS: 1..64 inclusive
    c.move(I(1),M(2,0))
    L('route_all_return')
    c.move(M(2,0),D(3))
    c.raw('4fef0020')
    c.raw('4cdf77f7')
    c.raw('74004e75')

    raw=c.out()
    if (not raw.startswith(old) or len(raw)>=32766 or len(raw)&1 or
            c.labels['routed_paint_one_entry']!=len(old)):
        raise ValueError('P0i renderer damaged P0h source or PC16')
    if raw.count(GETADR)!=old.count(GETADR)+1:
        raise ValueError('P0i lacks exact checked AMOS GetAdr marker')
    return raw,c.labels


if __name__=='__main__':
    out,labels=emit_multibank_paint()
    print('M19 P0i PRIVATE MULTIBANK BOB BLIT SOURCE ONLY',
          'bytes',len(out),'added',len(out)-labels['routed_paint_one_entry'],
          'SHA256',sha256(out).hexdigest(),
          'NO PUBLIC DRAW, NO INSTALLED LIB, NO SWAP')
