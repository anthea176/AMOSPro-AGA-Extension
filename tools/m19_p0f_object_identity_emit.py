#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0f PRIVATE per-object AGBO snapshot binding/check on native 68020.

AGA V2 layout: immutable P0d group, exact 64-slot P0e object table,
exact P0e AGA-local bridge, P0f bank stamp, THEN this private binder.

The binder captures a 16-byte bank stamp *first*, calls exact P0e object_put,
and commits the stamp only after object_put succeeds. Reject leaves both
the object and the old stamp unchanged. Check reads an ACTIVE object into
a private stack descriptor, verifies its bank against the independent AMOS
Bnk.GetAdr stamp, and copies 24 descriptor bytes to caller ONLY on success.
No bank selection is changed, no numbered bank is created/erased, no Chip
allocation, Blitter, or Swap is attempted. 64 fixed stamp slots live in AGA.

Private register ABI (all preserved except D2=0 and D3=1/0):
  identity_bind: D0=object ID (1..64), D1=bank, D4=image, D5=X, D6=Y.
  identity_check: D0=object ID, A1=caller-owned writable 24-byte record.
  identity_clear: A5=owner, clears shadow stamp table (Close/End later).

The checked object itself still resides in P0e's original 24-byte table;
the sixth long stays reserved and all original P0d/P0e bytes are unchanged.

NO public Draw/End token, installed .Lib, WinUAE or true AMOS Compiler claim.
Same-address SAME-generation ABA reuse is not proved impossible.
"""
from __future__ import annotations
from m68k_emit import Code,D,A,M,POST,I
from m19_p0f_bank_stamp_emit import emit_bank_stamp
from m19_p0e_object_table_emit import emit_object_table,MAX_OBJECTS,SLOT_BYTES
from m19_p0e_split_bridge_emit import AGA_CORE

FRAME=160
STAMP_BYTES=16
STAMP_TABLE_BYTES=MAX_OBJECTS*STAMP_BYTES
SCRATCH_OBJECT=64
SCRATCH_STAMP=96
F=dict(ident=0,bank=4,image=8,x=12,y=16,output=20,result=24,owner=28)
OBJ,OBJ_LABELS=emit_object_table()
STAMP,STAMP_LABELS=emit_bank_stamp()
OBJECT_REL=-len(AGA_CORE)-len(OBJ)
assert OBJECT_REL%2==0 and len(OBJ)==2332


def emit_object_identity() -> tuple[bytes,dict[str,int]]:
    c=Code();B,L=c.branch,c.label
    c.raw(STAMP.hex())
    c.labels.update(STAMP_LABELS)
    # This native suffix will be appended directly after OBJ+AGA_CORE.
    # The earlier P0e object entry is in the SAME relocated AGA V2 unit.
    c.labels['identity_old_object_put']=OBJECT_REL+OBJ_LABELS['object_put_entry']
    c.labels['identity_old_object_read']=OBJECT_REL+OBJ_LABELS['object_read_entry']

    def S(src,name):c.move(src,M(2,F[name]))
    def G(name,dst):c.move(M(2,F[name]),dst)
    def scratch(which,areg):
        c.move(A(2),D(0))
        c.imm('add',which,D(0))
        c.move(D(0),A(areg))
    def slot_ptr(reg):
        G('ident',D(0))
        c.quick(1,D(0),sub=True)
        c.word(0xc0fc);c.word(STAMP_BYTES) # MULU.W #16,D0
        c.lea(reg,'identity_stamp_table')
        # ADDA.L D0,An
        c.word(0xd1c0 | (reg<<9))
    def valid_id():
        G('ident',D(0))
        c.imm('cmp',1,D(0));B(5,'identity_return')
        c.imm('cmp',MAX_OBJECTS,D(0));B(2,'identity_return')
    def init():
        c.raw('48e7efee')
        c.raw('4fefff60')  # LEA -160(SP),SP
        c.move(A(7),A(2))
        S(D(0),'ident')
        S(A(5),'owner')
        S(I(0),'result')

    L('identity_bind_entry')
    init()
    S(D(1),'bank');S(D(4),'image');S(D(5),'x');S(D(6),'y')
    valid_id()
    scratch(SCRATCH_STAMP,1)  # scratch computes A1 through D0
    G('bank',D(0))             # restore bank AFTER scratch clobbers D0
    B(1,'stamp_capture_entry')
    c.tst(D(3));B(7,'identity_return')  # no stale transaction
    G('ident',D(0))
    G('bank',D(1));G('image',D(4));G('x',D(5));G('y',D(6))
    B(1,'identity_old_object_put')
    c.tst(D(3));B(7,'identity_return')
    # Object published: commit the same validated stamp, no allocation.
    slot_ptr(0)
    for off in range(0,STAMP_BYTES,4):
        c.move(M(2,SCRATCH_STAMP+off),D(1))
        c.move(D(1),M(0,off))
    S(I(1),'result')
    B(0,'identity_return')

    L('identity_check_entry')
    init()
    S(A(1),'output')
    valid_id()
    G('output',D(0));c.tst(D(0));B(7,'identity_return')
    c.imm('and',1,D(0));B(6,'identity_return')
    G('output',D(0))
    c.imm('add',SLOT_BYTES-1,D(0));B(5,'identity_return')
    S(D(0),'x')   # scratch high output, not source coordinate
    G('output',A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'identity_return')
    G('x',A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'identity_return')
    scratch(SCRATCH_OBJECT,1) # scratch computes A1 through D0
    G('ident',D(0))           # restore ID AFTER scratch clobbers D0
    B(1,'identity_old_object_read')
    c.tst(D(3));B(7,'identity_return')
    # Verify bank number from P0e checked ACTIVE object, not selected bank.
    slot_ptr(1)
    c.move(M(2,SCRATCH_OBJECT+0),D(0))  # source bank number
    B(1,'stamp_verify_entry')         # A1=shadow stamp record
    c.tst(D(3));B(7,'identity_return')
    G('output',A(1))
    for off in range(0,SLOT_BYTES,4):
        c.move(M(2,SCRATCH_OBJECT+off),D(0))
        c.move(D(0),POST(1))
    S(I(1),'result')
    B(0,'identity_return')

    L('identity_clear_entry')
    init()
    G('owner',D(0));c.tst(D(0));B(7,'identity_return')
    c.imm('and',1,D(0));B(6,'identity_return')
    # Caller MUST first succeed in P0e object_reset (which owner-guards).
    # This is private, never exposed to public AMOS as a free-standing clear.
    c.lea(0,'identity_stamp_table')
    c.move(I(0),D(0))
    c.move(I(STAMP_TABLE_BYTES//4),D(1))
    L('identity_clear_loop')
    c.move(D(0),POST(0))
    c.quick(1,D(1),sub=True)
    B(6,'identity_clear_loop')
    S(I(1),'result')

    L('identity_return')
    G('result',D(3))
    c.raw('4fef00a0')    # restore frame +160
    c.raw('4cdf77f7')    # preserve all except numeric result D2/D3
    c.raw('74004e75')

    L('identity_stamp_table')
    c.raw('00'*STAMP_TABLE_BYTES)
    out=c.out()
    assert out[:len(STAMP)]==STAMP
    assert c.labels['identity_bind_entry']==len(STAMP)
    assert c.labels['identity_stamp_table']+STAMP_TABLE_BYTES==len(out)
    assert out[c.labels['identity_stamp_table']:] == bytes(STAMP_TABLE_BYTES)
    assert len(out)%2==0 and len(out)<32766
    assert all(c.labels[x]%2==0 for x in (
        'identity_bind_entry','identity_check_entry','identity_clear_entry'))
    return out,c.labels


if __name__=='__main__':
    from hashlib import sha256
    data,labels=emit_object_identity()
    print('M19 P0f SOURCE-ONLY AGA native object stamp binder/check',
          len(data),sha256(data).hexdigest(),
          'native helpers', {k:v for k,v in labels.items() if k.startswith('identity_')})
