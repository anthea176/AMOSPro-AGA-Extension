#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e PRIVATE fixed-slot MC68020 persistent Bob object metadata table.

SOURCE ONLY, NOT AN INSTALLED AMOS TOKEN. No AP20, .Lib, ASC, or R84 change.
Independent relocatable native unit (separate from already-near-PC16-limit
P0d BOBS unit); executable metadata is scoped to its real AMOS owner A5.
No allocation/Chip copying/DMA, no implicit Swap, no pointers to AMOS banks.

Entry ABI (trusted PRIVATE callers only; return D2=0, D3=1/0):
  object_put:   D0=object ID 1..64, D1=AMOS bank 5..65535,
                D4=image ID 1..4096, D5=signed X, D6=signed Y, A5=owner
  object_off:   D0=object ID, A5=owner; idempotently deactivate an existing slot
  object_read:  D0=object ID, A1=valid private destination of 24 bytes,
                A5=owner; do not touch output on failure/inactive object
  object_reset: A5=owner, reset every slot and bind to new owner (no allocations)

Each 24-byte slot: bank, image, signed X, signed Y, active(0/1), reserved.
Stable rendering order is slot/object ID ascending. A selected bank change
never alters a stored bank ID; an update of a slot is all-or-nothing after
range/owner checks. A source bank must be revalidated separately at DRAW.

IMPORTANT: Before public API integration, wire reset to real AGA Close/End;
this private metadata stage must NOT be mistaken for a persistent draw system.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, POST, I

MAX_OBJECTS = 64
SLOT_BYTES = 24
FRAME_BYTES = 64
ROOT_BYTES = 8
FIELDS = dict(ident=0,bank=4,image=8,x=12,y=16,owner=20,output=24,result=28)
assert max(FIELDS.values()) + 4 <= FRAME_BYTES


def emit_object_table() -> tuple[bytes, dict[str,int]]:
    c = Code()
    B,L = c.branch,c.label

    def store(src,name):
        c.move(src,M(2,FIELDS[name]))

    def get(name,dst):
        c.move(M(2,FIELDS[name]),dst)

    def common(*,need_id=True):
        # Save AMOS registers, leaving only D2/D3 as function result.
        c.raw('48e7efee')
        c.raw('4fefffc0')         # LEA -64(SP),SP
        c.move(A(7),A(2))
        store(A(5),'owner')
        store(I(0),'result')
        if need_id:
            store(D(0),'ident')
        B(1,'object_cpu_guard')
        c.tst(D(0)); B(7,'object_return')
        get('owner',D(0))
        c.tst(D(0)); B(7,'object_return')
        c.imm('and',1,D(0)); B(6,'object_return')
        if need_id:
            get('ident',D(0))
            c.imm('cmp',1,D(0)); B(5,'object_return')
            c.imm('cmp',MAX_OBJECTS,D(0)); B(2,'object_return')

    def owner_guard(*,allow_empty=False):
        c.lea(0,'object_root')
        c.move(M(0,0),D(0))
        if allow_empty:
            c.tst(D(0)); B(7,'object_unbound_allowed')
        get('owner',D(1))
        c.alu('cmp',D(1),0)
        B(6,'object_return')
        if allow_empty:
            L('object_unbound_allowed')

    def slot_ptr():
        get('ident',D(0))
        c.quick(1,D(0),sub=True)
        c.word(0xc0fc);c.word(SLOT_BYTES)  # MULU.W #24,D0; 0..63 only
        c.lea(0,'object_table')
        c.raw('d1c0')                    # ADDA.L D0,A0

    L('object_put_entry')
    common()
    store(D(1),'bank')
    store(D(4),'image')
    store(D(5),'x')
    store(D(6),'y')
    owner_guard(allow_empty=True)
    for name,low,high in (('bank',5,65535),('image',1,4096)):
        get(name,D(0))
        c.imm('cmp',low,D(0));B(5,'object_return')
        c.imm('cmp',high,D(0));B(2,'object_return')
    for name in ('x','y'):
        get(name,D(0))
        c.imm('cmp',-32768,D(0));B(13,'object_return')  # BLT
        c.imm('cmp',32767,D(0));B(14,'object_return')   # BGT
    slot_ptr()
    for name,off in (('bank',0),('image',4),('x',8),('y',12)):
        get(name,D(0))
        c.move(D(0),M(0,off))
    c.move(I(1),M(0,16))
    c.move(I(0),M(0,20))
    c.lea(0,'object_root')
    get('owner',D(0))
    c.move(D(0),M(0,0))
    store(I(1),'result')
    B(0,'object_return')

    L('object_off_entry')
    common()
    owner_guard()
    slot_ptr()
    c.tst(M(0,0));B(7,'object_return')   # never-created object
    c.move(I(0),M(0,16))                 # idempotent off (retains binding)
    store(I(1),'result')
    B(0,'object_return')

    L('object_read_entry')
    common()
    store(A(1),'output')
    owner_guard()
    get('output',D(0));c.tst(D(0));B(7,'object_return')
    c.imm('and',1,D(0));B(6,'object_return')
    get('output',D(0));c.imm('add',SLOT_BYTES-1,D(0))
    B(5,'object_return')
    slot_ptr()
    c.tst(M(0,16));B(7,'object_return')
    get('output',A(1))
    for off in range(0,SLOT_BYTES,4):
        c.move(M(0,off),D(0))
        c.move(D(0),POST(1))
    store(I(1),'result')
    B(0,'object_return')

    L('object_reset_entry')
    common(need_id=False)
    c.lea(0,'object_table')
    c.move(I(0),D(0))
    c.move(I(MAX_OBJECTS*SLOT_BYTES//4),D(1))
    L('object_reset_loop')
    c.move(D(0),POST(0))
    c.quick(1,D(1),sub=True)
    B(6,'object_reset_loop')
    c.lea(0,'object_root')
    get('owner',D(0));c.move(D(0),M(0,0))
    c.move(I(0),M(0,4))
    store(I(1),'result')
    B(0,'object_return')

    L('object_cpu_guard')
    c.raw('20780004')                    # MOVEA.L 4.W,A0 ExecBase
    c.move(A(0),D(0));c.tst(D(0));B(7,'object_no_020')
    c.move(M(0,0x128),D(0),'w')         # AttnFlags
    c.word(0x0800);c.word(1)           # BTST #AFF_68020,D0
    B(7,'object_no_020')
    c.move(I(1),D(0));c.raw('4e75')
    L('object_no_020')
    c.move(I(0),D(0));c.raw('4e75')

    L('object_return')
    get('result',D(3))
    c.raw('4fef0040')                   # restore frame
    c.raw('4cdf77f7')                   # restore AMOS set
    c.raw('74004e75')                   # D2=0; RTS

    L('object_root')
    c.raw('00'*ROOT_BYTES)
    L('object_table')
    c.raw('00'*(MAX_OBJECTS*SLOT_BYTES))
    binary=c.out()
    assert c.labels['object_put_entry']==0
    assert c.labels['object_root']<c.labels['object_table']<len(binary)
    assert binary[c.labels['object_root']:] == bytes(ROOT_BYTES+MAX_OBJECTS*SLOT_BYTES)
    assert not len(binary)&1 and len(binary)<32766
    return binary,c.labels


if __name__=='__main__':
    from hashlib import sha256
    data,labels=emit_object_table()
    print('M19 P0e PRIVATE object metadata MC68020 SOURCE ONLY',len(data),
          sha256(data).hexdigest(),MAX_OBJECTS,'slots',
          'no AP20/Lib/WinUAE/Compiler claim')
