#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 private Safe AGA BACK BitMap selector, source-only MC68020.

Validated native state layout from P0d/B5: A5+$1c8 -> AGA state;
state+0=Screen, state+32=DBState; DB+0/+4=ScreenBuffer0/1,
DB+8=front index, DB+20 bit0=Safe pending; ScreenBuffer+0=BitMap.

A5 is the true AMOS owner. No use of AMOS/OCS Screen Copy or Swap.
The selector REFUSES a pending Safe: it does not poll, GetMsg or WaitVbl.
Caller can retry later (or use the verified P0d SafePort protocol).
It never touches the front bitmap or modifies DBState, and never draws.

Input: A5=AMOS owner.
Output: D2=non-displayed BitMap pointer (0 on refusal), D3=1/0.
All other AMOS registers (including A3) preserved.
Exec TypeOfMem calls check only allocation membership, not full object
lifetime or contiguity: the real caller must guarantee stable AGA state.
"""
from __future__ import annotations
from m68k_emit import Code, D, A, M, I
from m19_b8_planar_snapshot_emit import emit_planar_snapshot_core

STATE_OFF=0x1c8
FRAME=96
F=dict(result=0,output=4,state=8,db=12,back_sb=16,front_sb=20,
       bitmap=24,front_bitmap=28)


def emit_b8_back_selector() -> tuple[bytes,dict[str,int]]:
    previous,labels=emit_planar_snapshot_core()
    c=Code()
    c.raw(previous.hex())
    c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,key):c.move(src,M(2,F[key]))
    def G(key,dst):c.move(M(2,F[key]),dst)
    def mapped(reg,*,size=1):
        # Private checker: nonzero aligned pointer; TypeOfMem at start/end.
        c.move(reg,D(0))
        c.tst(D(0));B(7,'b8_select_return')
        c.imm('and',1,D(0));B(6,'b8_select_return')
        c.move(reg,A(1))
        c.raw('2c780004');c.call_os(-534)
        c.tst(D(0));B(7,'b8_select_return')
        if size>1:
            c.move(reg,D(0))
            c.imm('add',size-1,D(0));B(5,'b8_select_return')
            c.move(D(0),A(1))
            c.raw('2c780004');c.call_os(-534)
            c.tst(D(0));B(7,'b8_select_return')

    L('b8_checked_back_selector_entry')
    c.raw('48e7efee4fefffa0') # Save AMOS ABI, 96-byte frame.
    c.move(A(7),A(2))
    S(I(0),'result');S(I(0),'output')
    # Execute only if ExecBase and an actual 68020+ are present.
    c.raw('20780004')
    c.move(A(0),D(0));c.tst(D(0));B(7,'b8_select_return')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1)     # BTST #AFF_68020,D0
    B(7,'b8_select_return')
    mapped(A(5),size=STATE_OFF+4)
    c.move(M(5,STATE_OFF),A(4))
    mapped(A(4),size=36)
    c.move(M(4,0),D(0));c.tst(D(0));B(7,'b8_select_return')
    c.move(M(4,32),A(4));S(A(4),'db')
    mapped(A(4),size=24)
    G('db',A(4))
    c.move(M(4,20),D(0));c.imm('and',1,D(0))
    B(6,'b8_select_return')      # Safe still pending; NEVER touch DMA page.
    c.move(M(4,8),D(0))
    c.tst(D(0));B(7,'b8_front_zero')
    c.imm('cmp',1,D(0));B(6,'b8_select_return')
    c.move(M(4,0),D(1));S(D(1),'back_sb')
    c.move(M(4,4),D(1));S(D(1),'front_sb')
    B(0,'b8_buffers_ready')
    L('b8_front_zero')
    c.move(M(4,4),D(1));S(D(1),'back_sb')
    c.move(M(4,0),D(1));S(D(1),'front_sb')
    L('b8_buffers_ready')
    G('back_sb',D(0));G('front_sb',D(1))
    c.alu('cmp',D(1),0);B(7,'b8_select_return') # same buffer
    G('back_sb',A(4));mapped(A(4),size=4)
    G('front_sb',A(4));mapped(A(4),size=4)
    G('back_sb',A(4));c.move(M(4,0),D(0));S(D(0),'bitmap')
    G('front_sb',A(4));c.move(M(4,0),D(0));S(D(0),'front_bitmap')
    G('bitmap',D(0));G('front_bitmap',D(1))
    c.alu('cmp',D(1),0);B(7,'b8_select_return') # same Bitmap
    G('bitmap',A(4));mapped(A(4),size=40) # Planes[8] metadata
    G('bitmap',D(0));S(D(0),'output')
    S(I(1),'result')
    L('b8_select_return')
    G('output',D(2))
    G('result',D(3))
    c.raw('4fef00604cdf77f74e75') # D2/D3 private return, not public GetP.
    native=c.out()
    assert native.startswith(previous)
    assert c.labels['b8_checked_back_selector_entry']==len(previous)
    assert len(native)<32766 and len(native)%2==0
    return native,labels|{'b8_checked_back_selector_entry':len(previous)}


if __name__=='__main__':
    from hashlib import sha256
    data,labels=emit_b8_back_selector()
    print('M19 B8 checked back selector SOURCE ONLY',len(data),
          sha256(data).hexdigest(),labels['b8_checked_back_selector_entry'])
