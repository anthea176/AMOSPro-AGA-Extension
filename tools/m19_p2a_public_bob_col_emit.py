#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2a public Bob–Bob collision native source, built ONLY from P1e emitters.

The existing BOBS native P1e source remains a byte-exact prefix. The P2a
private units are appended in the SAME relocatable V2 AP20 BOBS group.
No absolute pointers into a compiler-relocated HUNK: all seven callbacks
are filled at run time with MC68020 PC-relative LONG displacement LEAs.

Public function GETP signature: Aga Bob Col(A,B,Mode)
 D3=Mode, A3 points to B then A (two 32-bit arguments).
 Result D3=1 hit / 0 no hit / -1 invalid, D2=0.
 P1c verifies actual live screen context at A5+0x1c8; dimensions are
 read from live AGA state offsets 12/16 and P1d table from context+8.
 Cache Chip for BOTH Bob banks must already have been staged via Update.
"""
from __future__ import annotations
from struct import pack
from hashlib import sha256
from m68k_emit import A, D, I, M, POST, Code
from m19_p1e_bank_edit_emit import emit_bank_edit
from m19_p1c_bob_priority_emit import STATE_A5
from m19_p1d_limit_bob_emit import TABLE_FROM_CONTEXT
from m19_p2a_pair_chip_resolve_emit import emit_p2a_pair_chip_resolve
from m19_p2a_pair_hotspot020_emit import emit_p2a_pair_hotspot020
from m19_p2a_pair_geometry020_emit import emit_p2a_pair_geometry020
from m19_p2a_collision020_emit import emit_collision020
from m19_p2a_collision_query020_emit import emit_p2a_collision_query020

FRAME=256
F=dict(mode=0,bob_b=4,bob_a=8,result=12,context=16)
SCREEN=64
CALLBACKS=80
PRIVATE_CONTEXT=112
assert PRIVATE_CONTEXT+8 <= FRAME
ENTRIES=(
    'p2a_pair_chip_resolve_entry',
    'identity_check_entry',
    'explicit_image_resolve_entry',
    'p2a_pair_hotspot_entry',
    'explicit_bank_lookup_entry',
    'p2a_pair_geometry_entry',
    'p2a_pair_entry',
)

def emit_p2a_public_col(context_delta: int) -> tuple[bytes,dict[str,int]]:
    old, old_labels=emit_bank_edit(context_delta)
    c=Code(); c.raw(old.hex());c.labels.update(old_labels)
    for producer in (emit_p2a_pair_chip_resolve,emit_p2a_pair_hotspot020,
                     emit_p2a_pair_geometry020,emit_collision020,
                     emit_p2a_collision_query020):
        fragment, labels = producer()
        offset=len(c.b)
        for name,pos in labels.items():
            if name in c.labels:
                raise ValueError('duplicate P2a native label: '+name)
            c.labels[name]=offset+pos
        c.b.extend(fragment)
    B,L=c.branch,c.label
    def S(src,key):c.move(src,M(2,F[key]))
    def G(key,dst):c.move(M(2,F[key]),dst)
    def frame_ptr(off,areg):
        c.move(A(2),D(5));c.imm('add',off,D(5));c.move(D(5),A(areg))
    def lea_pc_long(reg,target):
        # LEA (bd.L,PC),An, MC68020 FULL extension 0170, index suppressed.
        # PC base = address of the extension word (instruction start+2).
        pos=len(c.b)
        c.word(0x41fb | (reg<<9))
        c.word(0x0170)
        displacement=c.labels[target]-(pos+2)
        if not -0x80000000<=displacement<=0x7fffffff:
            raise ValueError('invalid MC68020 PC32 reference')
        c.b.extend(pack('>i',displacement))

    L('p2a_public_bob_col')
    c.raw('48e7efee4fefff00') # Preserve public AMOS regs except D2/D3, 256B frame.
    c.move(A(7),A(2))
    S(D(3),'mode')
    S(POST(3),'bob_b')          # GETP: B preceding A on A3.
    S(POST(3),'bob_a')
    S(I(-1),'result')            # error by default, never uninitialized.
    lea_pc_long(6,'p1c_context')
    c.raw('4e96')               # Existing source-verifiable CPU/owner/screen context
    c.move(A(0),D(5));c.tst(D(5));B(7,'p2a_public_col_done')
    c.imm('and',1,D(5));B(6,'p2a_public_col_done')
    S(A(0),'context')
    c.move(M(5,STATE_A5),A(0))  # Real AGA state, already owner-checked by P1c
    c.move(M(0,12),D(5));c.move(D(5),M(2,SCREEN))
    c.move(M(0,16),D(5));c.move(D(5),M(2,SCREEN+4))
    # Context { &screen[2], &limits[65] } is private to this call.
    frame_ptr(SCREEN,0);c.move(A(0),M(2,PRIVATE_CONTEXT))
    G('context',D(5));c.imm('add',TABLE_FROM_CONTEXT,D(5))
    c.move(D(5),M(2,PRIVATE_CONTEXT+4))
    # Runtime addresses are PC-relative in ONE relocatable V2 BOBS unit;
    # never store addresses captured before relocation or supplied by AMOS.
    for i,label in enumerate(ENTRIES):
        lea_pc_long(0,label)
        c.move(A(0),M(2,CALLBACKS+4*i))
    G('bob_a',D(0));G('bob_b',D(1));G('mode',D(4))
    frame_ptr(PRIVATE_CONTEXT,1)
    frame_ptr(CALLBACKS,4)
    B(1,'p2a_collision_query_entry')
    S(D(3),'result')
    L('p2a_public_col_done')
    G('result',D(3))
    c.raw('4fef01004cdf77f774004e75')
    native=c.out()
    if (native[:len(old)]!=old or len(native)%2 or len(native)>65500
        or c.labels['p2a_public_bob_col']<len(old)
        or any(label not in c.labels for label in ENTRIES)):
        raise ValueError('P2a source ancestry/group length ABI drift')
    return native,c.labels

if __name__=='__main__':
    from build_m19_p1e_bank_edit_in_memory import build_p1e
    _, meta = build_p1e()
    b, labels=emit_p2a_public_col(meta['context_delta'])
    print('P2A PUBLIC SOURCE 020',len(b),sha256(b).hexdigest(),
          'ENTRY',labels['p2a_public_bob_col'])
