#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e PRIVATE BOBS -> AGA object-table bridge, in actual MC68020 code.

SOURCE ONLY. Append a *small* bridge after the EXACT P0d BOBS source. No
public AMOS token, no change to P0d, no automatically installed .Lib.

The legacy native AGA Init itself stores AGA State in A5+$1c8; the state
lives at group offset $1c2, even when Compiler V2 places the AGA and BOBS
units at entirely unrelated addresses. The source-pinned AGA End prologue
at State-$168 is verified before any cross-group object call. The P0e
object_put prologue and both native endpoints are also checked before JSR.

Four PRIVATE BOBS entrypoints (the same ABI as P0e object-table entries):
  bridge_put:   D0=object ID, D1=source bank, D4=image, D5=X, D6=Y
  bridge_off:   D0=object ID
  bridge_read:  D0=object ID, A1=valid 24-byte destination
  bridge_reset: A5=AMOS owner
Additional entry bridge_put_selected: D0=object ID, D4=image, D5=X,
D6=Y. It reads the ACTUAL BOBS bank_active_state only AFTER the CPU and
A5 checks, then calls P0e object_put. The saved bank ID survives later
selection changes. This entry still requires a valid prior Aga Bob Bank.

Each preserves the usual AMOS D0/D1/D4-D7/A0-A2/A4-A6, A3, A5 and SP;
returns D2=0, D3=1/0. Do not call through raw absolute addresses or via
an unverified End callback pointer. No drawing, no Swap, no Chip allocation.

Future Draw can invoke bridge_read from BOBS and call its own verified P0d
Safe/Chip painter. No AGA -> BOBS absolute call is needed.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I
from m19_p0d_public_blit_emit import emit_public_blit
from m19_p0e_object_table_emit import emit_object_table
from m19_p0c_program_end_bridge_emit import END_SIGNATURE,AGA_STATE_OFF

AGA_P0D_GROUP_BYTES=56580     # verified by exact P0d builder / SHA
STATE_A5=0x1c8
END_DELTA=0x168
OBJ_RELATIVE=AGA_P0D_GROUP_BYTES-AGA_STATE_OFF
FRAME=32
F=dict(ident=0,bank=4,image=8,x=12,y=16,output=20,entry_offset=24)
assert OBJ_RELATIVE==56130


def emit_v2_object_bridge(*, aga_side: bool=False) -> tuple[bytes, dict[str,int]]:
    p0d,labels=emit_public_blit()
    objects,obj_labels=emit_object_table()
    assert len(objects)==2332 and obj_labels['object_put_entry']==0
    assert all(obj_labels['object_'+k+'_entry']%2==0
               for k in ('put','off','read','reset'))
    # Do not depend on a pointer fixed by the host process: use the source
    # prologue in the same relocated AGA unit to validate State ancestry.
    obj_signature=tuple(int.from_bytes(objects[i:i+4],'big')
                        for i in range(0,16,4))
    assert len(obj_signature)==4
    c=Code()
    c.raw(p0d.hex())
    c.labels.update(labels)
    B,L=c.branch,c.label

    # AGA-side relocation deliberately removes the BOBS bank-state entry:
    # only BOBS can read its own PC-relative bank_active_state.
    if not aga_side:
        L('object_bridge_put_selected_entry')
        c.raw('48e7efee')
        c.move(I(-1),D(7))
        B(0,'object_bridge_common')
    for key in ('put','off','read','reset'):
        L('object_bridge_'+key+'_entry')
        c.raw('48e7efee')         # preserve AMOS register set except D2/D3
        c.move(I(obj_labels['object_'+key+'_entry']),D(7))
        B(0,'object_bridge_common')

    L('object_bridge_common')
    c.raw('4fefffe0')             # LEA -32(SP),SP
    c.move(A(7),A(2))            # A2=frame
    for name,reg in (('ident',D(0)),('bank',D(1)),('image',D(4)),
                     ('x',D(5)),('y',D(6)),('output',A(1)),
                     ('entry_offset',D(7))):
        c.move(reg,M(2,F[name]))
    c.move(I(0),D(3))            # default refusal, D2=0 at exit

    # Every entry refuses a CPU below MC68020 before AMOS or AGA access.
    c.raw('20780004')           # MOVEA.L (4).W,A0, ExecBase
    c.move(A(0),D(0));c.tst(D(0));B(7,'object_bridge_return')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1)    # BTST #AFF_68020,D0
    B(7,'object_bridge_return')
    c.move(A(5),D(0));c.tst(D(0));B(7,'object_bridge_return')
    c.imm('and',1,D(0));B(6,'object_bridge_return')
    c.move(M(2,F['entry_offset']),D(0))
    c.imm('cmp',-1,D(0))
    if aga_side:
        B(7,'object_bridge_return')  # no PC-relative BOBS data in AGA unit
    else:
        B(6,'object_bridge_bank_ready')
        c.lea(0,'bank_active_state')
        c.move(M(0,0),D(1))
        c.move(D(1),M(2,F['bank']))
        c.move(I(0),M(2,F['entry_offset']))  # object_put native offset
        L('object_bridge_bank_ready')
    # Object management requires an OPEN AGA screen. The original AGA
    # State is executable-unit-local and State+0 is the live Screen ptr.
    c.move(M(5,STATE_A5),D(0))
    c.tst(D(0));B(7,'object_bridge_return')
    c.imm('and',1,D(0));B(6,'object_bridge_return')
    c.move(M(5,STATE_A5),A(1))
    c.raw('2c780004');c.call_os(-534)  # TypeOfMem(State), before dereference
    c.tst(D(0));B(7,'object_bridge_return')
    c.move(M(5,STATE_A5),A(0))
    c.tst(M(0,0));B(7,'object_bridge_return')

    # Resolve and verify original AGA callback from the AGA State anchor:
    # AGA End=State-$168. Signature is frozen with the original AGA group.
    c.move(M(5,STATE_A5),D(0))
    c.imm('cmp',END_DELTA,D(0));B(5,'object_bridge_return')
    c.imm('sub',END_DELTA,D(0))
    c.move(D(0),A(4))
    c.imm('and',1,D(0));B(6,'object_bridge_return')
    c.move(A(4),A(1))
    c.raw('2c780004');c.call_os(-534) # Exec TypeOfMem old End entry
    c.tst(D(0));B(7,'object_bridge_return')
    for i,word in enumerate(END_SIGNATURE):
        c.move(M(4,4*i),D(0))
        c.imm('cmp',word,D(0));B(6,'object_bridge_return')

    # AGA object_put is at AGA State+56130 in the SAME AGA native unit;
    # physical distance between the TWO V2 units is completely irrelevant.
    c.move(M(5,STATE_A5),D(0))
    c.imm('add',OBJ_RELATIVE,D(0))
    B(5,'object_bridge_return')  # 32-bit pointer arithmetic overflow
    c.imm('and',1,D(0))
    B(6,'object_bridge_return')
    c.move(M(5,STATE_A5),D(0))
    c.imm('add',OBJ_RELATIVE,D(0))
    c.move(D(0),A(4))
    c.move(A(4),A(1))
    c.raw('2c780004');c.call_os(-534)  # TypeOfMem object_put
    c.tst(D(0));B(7,'object_bridge_return')
    c.move(A(4),D(0))
    c.imm('add',len(objects)-1,D(0))
    B(5,'object_bridge_return')
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534) # TypeOfMem object table tail
    c.tst(D(0));B(7,'object_bridge_return')
    for i,word in enumerate(obj_signature):
        c.move(M(4,4*i),D(0))
        c.imm('cmp',word,D(0));B(6,'object_bridge_return')

    # Chosen P0e table entry must be one of four fixed native offsets, not
    # a caller-supplied address. Full 32-bit addition avoids PC16 truncation.
    c.move(A(4),D(0))
    c.move(M(2,F['entry_offset']),D(1))
    c.alu('add',D(1),0);B(5,'object_bridge_return')
    c.move(D(0),A(4))
    for name,reg in (('ident',D(0)),('bank',D(1)),('image',D(4)),
                     ('x',D(5)),('y',D(6)),('output',A(1))):
        c.move(M(2,F[name]),reg)
    # A4 still holds the checked object entry; D4 is a DIFFERENT register
    # (data/image), so forwarding D4 does not affect the A4 code pointer.
    c.raw('4e94')             # JSR (A4), actual relocated AGA object entry
    L('object_bridge_return')
    c.raw('4fef0020')          # LEA 32(SP),SP
    c.raw('4cdf77f7')          # restore AMOS registers
    c.raw('74004e75')          # D2=0; RTS

    result=c.out()
    assert result[:len(p0d)]==p0d
    if not aga_side:
        assert c.labels['object_bridge_put_selected_entry']==len(p0d)
    else:
        assert c.labels['object_bridge_put_entry']==len(p0d)
        assert 'object_bridge_put_selected_entry' not in c.labels
    assert result.startswith(p0d) and len(result)%2==0
    return result,c.labels


if __name__=='__main__':
    from hashlib import sha256
    src,labels=emit_v2_object_bridge()
    print('M19 P0e PRIVATE cross-unit bridge SOURCE-ONLY',
          len(src),sha256(src).hexdigest(),
          len(src)-labels['object_bridge_put_selected_entry'])
