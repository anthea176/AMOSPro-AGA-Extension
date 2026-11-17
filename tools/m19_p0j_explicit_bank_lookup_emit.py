#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b1: explicit-bank Chip cache lookup, WITHOUT bank_active_state.

Append-only to the SHA-pinned P0j-a 020 code; no public token/Lib/ASC.
Private input: D3=AMOS AGBO bank number [5..65535],
               A1=caller-owned 28-byte output (even, mapped), A5=AMOS.
Result: D3=1 only if the CURRENT original bank AGBO payload/generation
and a previously staged Chip context match the per-bank P0c registry.
On D3=0 the entire caller output is unchanged. D2=0; AMOS ABI preserved.

Successful 28-byte output, seven big-endian longs:
  +0 original AGBO payload pointer (not selected-bank shadow)
  +4 current AGBO generation
  +8 Chip pixels allocation base
  +12 Chip allocation size
  +16 P0c Chip context pointer (node+8)
  +20 bank number
  +24 source list head (Cur_Banks)
The pointer is usable only for synchronous foreground rendering and must
be rechecked after any Erase/Load/Reserve. No Chip allocation or Blit here.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code,D,A,M,I
from amos_main_abi import main_index,rjsr
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5
from m19_p0j_frame_image_preflight_emit import emit_image_preflight

GETADR=rjsr(main_index('Bnk.GetAdr'))
MAX_NODES=256
COOKIE=0x43484950
MEMF_CHIP=2
FRAME=128
F=dict(bank=0,out=4,head=8,payload=12,generation=16,
       node=20,ctx=24,chip=28,chiplen=32,result=36,limit=40)
OUTPUT_BYTES=28

def emit_explicit_bank_lookup() -> tuple[bytes,dict[str,int]]:
    previous,old_labels=emit_image_preflight()
    c=Code()
    c.raw(previous.hex());c.labels.update(old_labels)
    B,L=c.branch,c.label
    def S(src,key):c.move(src,M(2,F[key]))
    def G(key,dst):c.move(M(2,F[key]),dst)
    def osbase():c.raw('2c780004')
    def mapped(key):
        G(key,A(1));osbase();c.call_os(-534)
        c.tst(D(0));B(7,'explicit_lookup_return')
    L('explicit_bank_lookup_entry')
    c.raw('48e7efee')                   # MOVEM.L ABI
    c.raw('4fefff80')                   # LEA -128(SP),SP
    c.move(A(7),A(2))
    S(D(3),'bank')
    S(A(1),'out')
    S(I(0),'result')

    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'explicit_lookup_return')
    G('bank',D(0))
    c.imm('cmp',5,D(0));B(5,'explicit_lookup_return')
    c.imm('cmp',65535,D(0));B(2,'explicit_lookup_return')
    c.move(A(5),D(0));c.tst(D(0))
    B(7,'explicit_lookup_return')
    c.imm('and',1,D(0));B(6,'explicit_lookup_return')
    c.lea(0,'registry_state')
    c.move(M(0,0),D(0))
    c.move(A(5),D(1))
    c.alu('cmp',D(1),0);B(6,'explicit_lookup_return')
    c.move(M(5,CUR_BANKS_A5),D(0));S(D(0),'head')
    c.tst(D(0));B(7,'explicit_lookup_return')
    c.imm('and',1,D(0));B(6,'explicit_lookup_return')

    # Bnk.GetAdr resolves the requested original bank; no global bank
    # selector is consulted, and no AMOS selection command is invoked.
    G('bank',D(0))
    c.raw(GETADR.hex())
    c.move(A(0),D(0));S(D(0),'payload')
    c.imm('cmp',24,D(0));B(3,'explicit_lookup_return')
    c.imm('and',1,D(0));B(6,'explicit_lookup_return')
    mapped('payload')
    G('payload',A(0))
    c.move(M(0,0),D(0))
    c.imm('cmp',0x4147424f,D(0));B(6,'explicit_lookup_return')
    c.move(M(0,24),D(0));S(D(0),'generation')
    c.tst(D(0));B(7,'explicit_lookup_return')

    # The P0c registry owner is verified above. Every node is bounded,
    # tested as memory and matched by bank ID, never by current selection.
    c.lea(0,'registry_state')
    c.move(M(0,4),D(0));S(D(0),'node')
    S(I(MAX_NODES),'limit')
    L('explicit_lookup_node')
    G('node',D(0));c.tst(D(0));B(7,'explicit_lookup_return')
    c.imm('and',1,D(0));B(6,'explicit_lookup_return')
    G('limit',D(1));c.tst(D(1));B(7,'explicit_lookup_return')
    c.quick(1,D(1),sub=True);S(D(1),'limit')
    mapped('node')
    G('node',A(0))
    c.move(M(0,4),D(0));G('bank',D(1))
    c.alu('cmp',D(1),0)
    B(7,'explicit_lookup_found')
    G('node',A(0));c.move(M(0,0),D(0));S(D(0),'node')
    B(0,'explicit_lookup_node')

    L('explicit_lookup_found')
    G('node',D(0));c.imm('add',8,D(0))
    B(5,'explicit_lookup_return')
    S(D(0),'ctx')
    G('ctx',A(0))
    c.move(M(0,0),D(0));S(D(0),'chip')
    c.tst(D(0));B(7,'explicit_lookup_return')
    c.imm('and',1,D(0));B(6,'explicit_lookup_return')
    c.move(M(0,4),D(0));S(D(0),'chiplen')
    c.imm('cmp',1,D(0));B(5,'explicit_lookup_return')
    c.imm('cmp',0x01000000,D(0));B(2,'explicit_lookup_return')
    c.move(M(0,16),D(0))
    c.imm('cmp',COOKIE,D(0));B(6,'explicit_lookup_return')

    # Reuse P0c's existing exact Chip-cookie+identity+generation check.
    G('payload',D(0));G('generation',D(1));G('ctx',A(1))
    B(1,'chip_lookup_entry')
    c.tst(D(3));B(7,'explicit_lookup_return')

    # Stage time already verified MEMF_CHIP, but recheck first/last byte.
    G('chip',A(1));osbase();c.call_os(-534)
    c.imm('and',MEMF_CHIP,D(0))
    c.imm('cmp',MEMF_CHIP,D(0));B(6,'explicit_lookup_return')
    G('chip',D(0));G('chiplen',D(1))
    c.alu('add',D(1),0);B(5,'explicit_lookup_return')
    c.quick(1,D(0),sub=True)
    c.move(D(0),A(1))
    osbase();c.call_os(-534)
    c.imm('and',MEMF_CHIP,D(0))
    c.imm('cmp',MEMF_CHIP,D(0));B(6,'explicit_lookup_return')

    # Writable output is validated at BOTH endpoints before publishing.
    G('out',D(0));c.tst(D(0));B(7,'explicit_lookup_return')
    c.imm('and',1,D(0));B(6,'explicit_lookup_return')
    G('out',A(1));osbase();c.call_os(-534)
    c.tst(D(0));B(7,'explicit_lookup_return')
    G('out',D(0));c.imm('add',OUTPUT_BYTES-1,D(0))
    B(5,'explicit_lookup_return')
    c.move(D(0),A(1));osbase();c.call_os(-534)
    c.tst(D(0));B(7,'explicit_lookup_return')

    # Output commit AFTER all checks: a failure never changes caller memory.
    G('out',A(0))
    for key in ('payload','generation','chip','chiplen','ctx','bank','head'):
        G(key,D(0));c.move(D(0),M(0))
        c.quick(4,A(0))
    S(I(1),'result')
    L('explicit_lookup_return')
    G('result',D(3))
    c.raw('4fef0080')                # restore frame
    c.raw('4cdf77f7')                # preserve caller AMOS ABI
    c.raw('74004e75')                # D2=0, RTS

    native=c.out()
    if (not native.startswith(previous) or
            c.labels['explicit_bank_lookup_entry']!=len(previous) or
            len(native)&1 or len(native)>=32766):
        raise ValueError('P0j-b1 changed historical native prefix or PC16')
    if native.count(GETADR)!=previous.count(GETADR)+1:
        raise ValueError('P0j-b1 explicit native branch lacks AMOS GetAdr')
    return native,c.labels

if __name__=='__main__':
    blob,labels=emit_explicit_bank_lookup()
    print('M19 P0j-b1 MC68020 EXPLICIT-BANK CHIP LOOKUP SOURCE ONLY',
          len(blob), sha256(blob).hexdigest(),
          'entry',labels['explicit_bank_lookup_entry'],
          'NO bank_active_state / NO public Draw / NO Lib switch')
