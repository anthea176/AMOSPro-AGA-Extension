"""M19 P0a (R88 source only): Aga Bob Bank N, preliminary native selection.

An AMOS DATA bank is created by the previously source-audited atomic list
transaction, or a compatible existing AGBO bank is selected. The selected
bank number, payload identity and Cur_Banks identity live in private per-code
unit data. The future Get AGA Bob wrapper must recheck all three before use.

LIMIT: this is metadata/bank preparation only. Chip DMA staging and full
per-entry directory validation are not yet implemented and MUST be provided
before the animated Blitter Bob API is enabled. No WinUAE claims.
"""
from __future__ import annotations

from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr
from m19_p0a_amos_bank_transaction_emit import (
    CUR_BANKS_A5, BANK_NAME, emit_transaction,
)
from m19_p0a_multi_bob_abk import empty_bank

IDX_GETADR=main_index('Bnk.GetAdr')
MARKER=rjsr(IDX_GETADR)
FRAME=64
F=dict(bank=0,oldptr=4,head=8)
STATE_SIZE=12


def emit_bank_select():
    """Return (self-contained machine-code unit, entry-offset labels)."""
    c=Code(); B,L=c.branch,c.label
    def get(name,reg): c.move(M(2,F[name]),reg)
    def put(reg,name): c.move(reg,M(2,F[name]))
    L('bank_select')
    c.raw('48e7efee')           # preserve AMOS AP20 registers
    c.raw('4fefffc0')           # LEA -64(SP),SP
    c.move(A(7),A(2))
    put(D(3),'bank')
    c.move(I(0),D(3))
    get('bank',D(0))
    c.imm('cmp',5,D(0));B(5,'done')
    c.imm('cmp',65535,D(0));B(2,'done')
    c.raw(MARKER.hex())
    c.move(A(0),D(0));c.tst(D(0));B(6,'existing')
    # Only a missing bank may be created; never call destructive Reserve.
    c.lea(0,'canonical_empty')
    c.move(I(len(empty_bank())),D(1))
    get('bank',D(3))
    B(1,'commit')
    c.tst(D(3));B(7,'done')
    get('bank',D(0));c.raw(MARKER.hex())
    c.move(A(0),D(0));c.tst(D(0));B(7,'done')
    L('existing')
    c.imm('cmp',24,D(0));B(3,'done')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'done')
    put(D(0),'oldptr')
    c.move(D(0),A(4))
    # Standard AMOS layout: size at payload-20, bank at -16, flags -12,
    # name at -8, AGBO payload begins at +0. The 365 +Lib.s is authoritative.
    c.move(M(4,-20),D(0))
    c.imm('cmp',48,D(0));B(5,'done')
    c.imm('cmp',0x1000010,D(0));B(2,'done')
    c.imm('sub',16,D(0));put(D(0),'head')   # temporary actual payload size
    c.move(M(4,-16),D(0));get('bank',D(1))
    c.alu('cmp',D(1),0);B(6,'done')
    c.move(I(0),D(0));c.move(M(4,-12),D(0),'w')
    c.tst(D(0));B(7,'flags_ok')    # AMOS Load can normalize DATA flags to zero
    c.imm('and',0xfffd,D(0),'w')
    c.imm('cmp',1,D(0),'w');B(6,'done')
    L('flags_ok')
    c.move(M(4,-8),D(0));c.imm('cmp',0x41474142,D(0));B(6,'done')
    c.move(M(4,-4),D(0));c.imm('cmp',0x4f425320,D(0));B(6,'done')
    c.move(M(4,0),D(0));c.imm('cmp',0x4147424f,D(0));B(6,'done')
    c.move(I(0),D(0));c.move(M(4,4),D(0),'w')
    c.imm('cmp',1,D(0));B(6,'done')
    c.tst(M(4,6),'w');B(6,'done')
    c.move(I(0),D(0));c.move(M(4,8),D(0),'w')
    c.imm('cmp',4096,D(0));B(2,'done')
    c.move(D(0),D(1));c.raw('c2fc0028') # MULU.W #40,D1
    c.imm('add',32,D(1))
    c.move(M(4,16),D(0));c.alu('cmp',D(1),0);B(6,'done')
    c.move(I(0),D(0));c.move(M(4,10),D(0),'w')
    c.imm('cmp',40,D(0));B(6,'done')
    c.move(M(4,12),D(0));c.imm('cmp',32,D(0));B(6,'done')
    c.move(M(4,20),D(0));get('head',D(1))
    c.alu('cmp',D(1),0);B(6,'done')
    c.move(M(4,24),D(0));c.tst(D(0));B(7,'done')
    c.tst(M(4,28));B(6,'done')
    # The *entire* directory must be validated by Get before capture;
    # this initial select intentionally does not expose rendering yet.
    c.move(M(5,CUR_BANKS_A5),D(0));c.tst(D(0));B(7,'done')
    c.lea(0,'active_state')
    get('bank',D(1));c.move(D(1),M(0))
    get('oldptr',D(1));c.move(D(1),M(0,4))
    c.move(D(0),M(0,8))
    c.move(I(1),D(3))
    L('done')
    c.raw('4fef0040')
    c.raw('4cdf77f7')
    c.raw('74004e75')
    # Local PC-relative branch into source-audited private atomic transaction.
    L('commit')
    raw,_=emit_transaction()
    c.raw(raw.hex())
    L('active_state')
    c.raw('000000000000000000000000')
    L('canonical_empty')
    c.raw(empty_bank().hex())
    out=c.out()
    assert len(out)%2==0 and out.count(MARKER)==4
    assert out[0:8]==bytes.fromhex('48e7efee4fefffc0')
    assert out[c.labels['canonical_empty']:] == empty_bank()
    return out,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_bank_select()
    print('M19 P0a private BANK SELECT source R88',len(raw),sha256(raw).hexdigest(),labels)
