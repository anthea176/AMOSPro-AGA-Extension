#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0f PRIVATE source-only snapshot/match of a live AMOS AGBO DATA bank.

The SOURCE-PINNED Bnk.GetAdr service is called each time, independently of
BOBS bank_active_state, so objects bound to different banks can later be
checked without changing the program's selected bank or creating anything.

ABI: D0=AMOS bank 5..65535; A1=valid 16-byte writable record on capture
     or read-only 16-byte expected record on verify; A5=current AMOS owner.
     D3=1/0, D2=0; preserve all other AMOS registers and A7.
     capture writes four LONGs ONLY after validation, with no writes on fail;
     verify NEVER mutates its input, even on success.
     record = [payload_ptr, AGBO_generation, Cur_Banks_list_ptr, payload_size].

Validates 020 CPU, A5/bank/output alignment and both output endpoints,
AMOS Bnk.GetAdr, bank header size/number/type, AGBO v1 magic/version,
image count, directory size, payload length/generation and mapped payload
endpoints, using Exec TypeOfMem before reading a bank pointer.

This matches the stable identity implemented by the verified P0c stage.
It is not an allocation-epoch guarantee against ABA reuse of EXACT same
payload address with SAME generation and matching data. Further lifecycle
controls remain required before a persistent public Draw can claim that.
NO Chip allocation, Blitter, Swap, token or installed .Lib.
"""
from __future__ import annotations
from m68k_emit import Code,D,A,M,I
from amos_main_abi import main_index,rjsr
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5

GETADR=rjsr(main_index('Bnk.GetAdr'))
FRAME=96
FIELDS={name:4*i for i,name in enumerate((
    'bank record mode owner head pointer size generation result end'
).split())}


def emit_bank_stamp() -> tuple[bytes,dict[str,int]]:
    c=Code();B,L=c.branch,c.label
    def S(src,key):c.move(src,M(2,FIELDS[key]))
    def G(key,dst):c.move(M(2,FIELDS[key]),dst)
    def mapped(key):
        G(key,A(1))
        c.raw('2c780004')
        c.call_os(-534) # Exec TypeOfMem
        c.tst(D(0));B(7,'stamp_return')

    L('stamp_capture_entry')
    c.raw('48e7efee')
    c.move(I(0),D(7))
    B(0,'stamp_common')
    L('stamp_verify_entry')
    c.raw('48e7efee')
    c.move(I(1),D(7))
    B(0,'stamp_common')
    L('stamp_common')
    c.raw('4fefffa0')          # frame -96
    c.move(A(7),A(2))
    S(D(0),'bank')
    S(A(1),'record')
    S(D(7),'mode')
    S(A(5),'owner')
    S(I(0),'result')
    c.raw('20780004')         # MOVEA.L 4.W,A0
    c.move(A(0),D(0));c.tst(D(0));B(7,'stamp_return')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1) # AFF_68020
    B(7,'stamp_return')
    G('owner',D(0));c.tst(D(0));B(7,'stamp_return')
    c.imm('and',1,D(0));B(6,'stamp_return')
    G('bank',D(0))
    c.imm('cmp',5,D(0));B(5,'stamp_return')
    c.imm('cmp',65535,D(0));B(2,'stamp_return')
    G('record',D(0));c.tst(D(0));B(7,'stamp_return')
    c.imm('and',1,D(0));B(6,'stamp_return')
    mapped('record')
    G('record',D(0));c.imm('add',15,D(0));B(5,'stamp_return')
    S(D(0),'end')
    mapped('end')
    # Verified AMOS 365 Cur_Banks is a list-head identity, not a bank number.
    G('owner',A(0))
    c.move(M(0,CUR_BANKS_A5),D(0));S(D(0),'head')
    c.tst(D(0));B(7,'stamp_return')
    c.imm('and',1,D(0));B(6,'stamp_return')
    # Do not use the stale selected-bank shadow. Bnk.GetAdr is the authority.
    G('bank',D(0));c.raw(GETADR.hex())
    c.move(A(0),D(0));S(D(0),'pointer')
    c.imm('cmp',24,D(0));B(3,'stamp_return')
    c.imm('and',1,D(0));B(6,'stamp_return')
    G('pointer',D(0));c.imm('sub',24,D(0));S(D(0),'end')
    mapped('end')
    G('pointer',A(4))
    c.move(M(4,-20),D(0))
    c.imm('cmp',48,D(0));B(5,'stamp_return')
    c.imm('cmp',0x01000010,D(0));B(2,'stamp_return')
    c.imm('sub',16,D(0));S(D(0),'size')
    G('pointer',D(0));G('size',D(1))
    c.alu('add',D(1),0);B(5,'stamp_return')
    c.quick(1,D(0),sub=True);S(D(0),'end')
    mapped('end')
    G('pointer',A(4))
    c.move(M(4,-16),D(0));G('bank',D(1))
    c.alu('cmp',D(1),0);B(6,'stamp_return')
    c.move(I(0),D(0));c.move(M(4,-12),D(0),'w')
    c.tst(D(0));B(7,'stamp_flags_ok')
    c.imm('and',0xfffd,D(0),'w')
    c.imm('cmp',1,D(0),'w');B(6,'stamp_return')
    L('stamp_flags_ok')
    for offset,value in ((-8,0x41474142),(-4,0x4f425320),
                         (0,0x4147424f)):
        c.move(M(4,offset),D(0))
        c.imm('cmp',value,D(0));B(6,'stamp_return')
    c.move(I(0),D(0));c.move(M(4,4),D(0),'w')
    c.imm('cmp',1,D(0));B(6,'stamp_return')
    c.tst(M(4,6),'w');B(6,'stamp_return')
    c.move(I(0),D(0));c.move(M(4,8),D(0),'w')
    c.imm('cmp',1,D(0));B(5,'stamp_return')
    c.imm('cmp',4096,D(0));B(2,'stamp_return')
    c.word(0xc0fc);c.word(40) # MULU.W #40,D0
    c.imm('add',32,D(0))
    c.alu('cmp',M(4,16),0);B(6,'stamp_return')
    G('size',D(1));c.alu('cmp',D(1),0);B(2,'stamp_return')
    c.move(M(4,20),D(0));G('size',D(1))
    c.alu('cmp',D(1),0);B(6,'stamp_return')
    c.move(M(4,24),D(0));c.tst(D(0));B(7,'stamp_return')
    S(D(0),'generation')
    c.tst(M(4,28));B(6,'stamp_return')
    # All checked; publish or compare exactly four full longwords.
    G('record',A(1))
    G('mode',D(0));c.tst(D(0));B(6,'stamp_compare')
    for key in ('pointer','generation','head','size'):
        G(key,D(0));c.move(D(0),M(1,0))
        c.quick(4,A(1))
    S(I(1),'result')
    B(0,'stamp_return')
    L('stamp_compare')
    for key in ('pointer','generation','head','size'):
        G(key,D(0));c.move(M(1,0),D(1))
        c.alu('cmp',D(1),0);B(6,'stamp_return')
        c.quick(4,A(1))
    S(I(1),'result')
    L('stamp_return')
    G('result',D(3))
    c.raw('4fef0060')
    c.raw('4cdf77f7')
    c.raw('74004e75')
    binary=c.out()
    assert binary[:4]==bytes.fromhex('48e7efee')
    assert len(binary)%2==0 and len(binary)<32766
    assert binary.count(GETADR)==1
    return binary,c.labels


if __name__=='__main__':
    from hashlib import sha256
    binary,labels=emit_bank_stamp()
    print('M19 P0f SOURCE-ONLY native 020 bank stamp',len(binary),
          sha256(binary).hexdigest(),labels,
          'NO persistent Draw / actual WinUAE / Compiler')
