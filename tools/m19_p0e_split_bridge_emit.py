#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e AP20 PC16 recovery: small BOBS relay, full private AGA bridge.

SOURCE ONLY, no installed .Lib. Preserves every byte of P0d BOBS/AGA code.
- Place immutable P0e 64-slot table immediately after original AGA unit.
- Append an AGA-LOCAL generic version of the verified 020 object bridge.
- Append only a short CPU/TypeOfMem/entry-signature relay to BOBS.
- Put_selected reads its own BOBS bank_active_state BEFORE forwarding bank
  to AGA; no PC-relative reference from AGA to an unrelated V2 unit.
- Public Aga Bob / Aga Bob Off wrappers use exactly the original GetP ABI.

The target is derived from A5+$1c8, i.e. native AGA State at offset $1c2,
then from source-pinned AGA unit sizes/entry offsets, NOT an absolute
Runtime/Compiler address. An AGA screen must be open. End/Close reset and
Draw are NOT yet implemented here.
"""
from __future__ import annotations

from m68k_emit import Code,D,A,M,I,POST
from m19_p0d_public_blit_emit import emit_public_blit
from m19_p0e_v2_object_bridge_emit import emit_v2_object_bridge, STATE_A5
from m19_p0e_object_table_emit import emit_object_table

AGA_OLD_GROUP=56580
AGA_STATE_OFFSET=0x1c2
FRAME=32
F=dict(ident=0,bank=4,image=8,x=12,y=16,output=20,entry_offset=24)
ENTRY_NAMES=('put','off','read','reset')
P0D, P0D_LABELS = emit_public_blit()
AGA_CORE_ALL, AGA_CORE_LABELS = emit_v2_object_bridge(aga_side=True)
assert AGA_CORE_ALL.startswith(P0D)
AGA_CORE_BASE = AGA_CORE_LABELS['object_bridge_put_entry']
AGA_CORE = AGA_CORE_ALL[AGA_CORE_BASE:]
OBJ, OBJ_LABELS=emit_object_table()
AGA_BRIDGE_DELTA=AGA_OLD_GROUP+len(OBJ)-AGA_STATE_OFFSET
assert AGA_BRIDGE_DELTA==58462
AGA_OFFSETS={kind:AGA_CORE_LABELS['object_bridge_'+kind+'_entry']-AGA_CORE_BASE
             for kind in ENTRY_NAMES}
assert AGA_OFFSETS['put']==0 and all(o%2==0 for o in AGA_OFFSETS.values())


def emit_split_bobs_public() -> tuple[bytes,dict[str,int]]:
    c=Code(); B,L=c.branch,c.label
    c.raw(P0D.hex())
    c.labels.update(P0D_LABELS)

    # Every entry preserves the AMOS register set; the common frame protects
    # input registers across Exec TypeOfMem, which clobbers D0/D1/A0/A1.
    L('relay_put_selected_entry')
    c.raw('48e7efee')
    c.lea(0,'bank_active_state')
    c.move(M(0,0),D(1))
    c.move(I(AGA_OFFSETS['put']),D(7))
    B(0,'relay_common')
    for kind in ('put','off','read','reset'):
        L('relay_'+kind+'_entry')
        c.raw('48e7efee')
        c.move(I(AGA_OFFSETS[kind]),D(7))
        B(0,'relay_common')

    L('relay_common')
    c.raw('4fefffe0')       # 32-byte local frame
    c.move(A(7),A(2))
    for key,reg in (('ident',D(0)),('bank',D(1)),('image',D(4)),
                    ('x',D(5)),('y',D(6)),('output',A(1)),
                    ('entry_offset',D(7))):
        c.move(reg,M(2,F[key]))
    c.move(I(0),D(3))      # fail closed until AGA target returns success
    c.raw('20780004')      # MOVEA.L 4.W,A0 ExecBase
    c.move(A(0),D(0));c.tst(D(0));B(7,'relay_return')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1)   # BTST #AFF_68020,D0
    B(7,'relay_return')
    c.move(A(5),D(0));c.tst(D(0));B(7,'relay_return')
    c.imm('and',1,D(0));B(6,'relay_return')
    c.move(M(5,STATE_A5),D(0))
    c.tst(D(0));B(7,'relay_return')
    c.imm('and',1,D(0));B(6,'relay_return')
    c.move(M(5,STATE_A5),A(1))
    c.raw('2c780004');c.call_os(-534) # TypeOfMem(AGA State)
    c.tst(D(0));B(7,'relay_return')
    c.move(M(5,STATE_A5),D(0))
    c.imm('add',AGA_BRIDGE_DELTA,D(0))
    B(5,'relay_return')   # carry: 32-bit pointer wrap
    c.move(M(2,F['entry_offset']),D(1))
    c.alu('add',D(1),0)
    B(5,'relay_return')
    c.move(D(0),A(4))
    c.imm('and',1,D(0));B(6,'relay_return')
    c.move(A(4),A(1))
    c.raw('2c780004');c.call_os(-534) # TypeOfMem(target entry)
    c.tst(D(0));B(7,'relay_return')
    c.move(M(4,0),D(0))
    c.imm('cmp',0x48e7efee,D(0)) # every AGA-side bridge entry starts MOVEM
    B(6,'relay_return')
    for key,reg in (('ident',D(0)),('bank',D(1)),('image',D(4)),
                    ('x',D(5)),('y',D(6)),('output',A(1))):
        c.move(M(2,F[key]),reg)
    c.raw('4e94')          # JSR (A4) into verified AGA private unit
    L('relay_return')
    c.raw('4fef0020')      # release 32-byte frame
    c.raw('4cdf77f7')      # restore AMOS registers (exclude D2/D3)
    c.raw('74004e75')      # D2=0, RTS (D3 success/failure)

    L('public_aga_bob_entry')
    c.raw('48e7efee')
    c.move(D(3),D(4))       # image from last argument
    c.move(POST(3),D(6))    # Y
    c.move(POST(3),D(5))    # X
    c.move(POST(3),D(0))    # N
    B(1,'relay_put_selected_entry')
    c.raw('4cdf77f7')
    c.raw('74004e75')

    L('public_aga_bob_off_entry')
    c.raw('2f00')
    c.move(D(3),D(0))
    B(1,'relay_off_entry')
    c.raw('201f')
    c.raw('74004e75')

    blob=c.out()
    assert blob.startswith(P0D)
    assert all(c.labels[x]&1==0 for x in (
        'relay_put_selected_entry','relay_put_entry','relay_off_entry',
        'relay_read_entry','relay_reset_entry',
        'public_aga_bob_entry','public_aga_bob_off_entry'))
    assert len(blob)%2==0 and len(blob)<32766
    return blob,c.labels


if __name__=='__main__':
    from hashlib import sha256
    binary,labels=emit_split_bobs_public()
    print('M19 P0e SPLIT PRIVATE AGA CORE',len(AGA_CORE),
          'BOBS relay+Set/Off',len(binary)-len(P0D),
          'AGA bridge delta',AGA_BRIDGE_DELTA,
          'source SHA256',sha256(binary).hexdigest())
