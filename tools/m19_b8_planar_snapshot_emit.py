#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""SOURCE ONLY: MC68020 private planar save/restore of a validated BitMap.

Independent native primitive, not an AMOS public command. The caller MUST
hold a Safe inactive AGA BitMap and own an isolated, sufficiently-sized
snapshot allocation. No screen acquisition, Swap, AllocMem or FreeMem here.

Input: A0=BitMap*, A1=private snapshot allocation, D0=allocated bytes,
       D1=0 copy BitMap -> snapshot, 1 snapshot -> BitMap.
Return: D2=0, D3=1 success, 0 refusal. Preserve all other AMOS registers.
Reject all bad pointers and geometry BEFORE the first plane write. Plane
arrays are validated against Exec TypeOfMem at start AND end (best-effort;
caller must have obtained and pinned the actual OS BitMap and allocation).

BitMap layout is the NDK classic planar struct: WORD BPR/Rows, BYTE Flags,
BYTE Depth, WORD pad, then Planes[8]. Stride is the *actual* BytesPerRow,
not the logical width rounded independently.
"""
from __future__ import annotations
from m68k_emit import Code, D, A, M, POST, I

FRAME=64
F=dict(bitmap=0,snapshot=4,capacity=8,mode=12,total=16,plane_bytes=20,depth=24,success=28,saved_a3=32)


def emit_planar_snapshot_core() -> tuple[bytes,dict[str,int]]:
    c=Code(); B,L=c.branch,c.label
    def S(src,key): c.move(src,M(2,F[key]))
    def G(key,dst): c.move(M(2,F[key]),dst)
    def checked_pointer(pointer, end_offset=None):
        # TypeOfMem(pointer) != 0, nonzero even, optionally last byte mapped.
        c.move(pointer,D(0))
        c.tst(D(0)); B(7,'b8_copy_return')
        c.imm('and',1,D(0)); B(6,'b8_copy_return')
        c.move(pointer,A(1))
        c.raw('2c780004');c.call_os(-534)
        c.tst(D(0)); B(7,'b8_copy_return')
        if end_offset is not None:
            c.move(pointer,D(0))
            c.alu('add',end_offset,0)
            B(5,'b8_copy_return')
            c.quick(1,D(0),sub=True)
            c.move(D(0),A(1))
            c.raw('2c780004');c.call_os(-534)
            c.tst(D(0)); B(7,'b8_copy_return')

    L('b8_planar_snapshot_core_entry')
    c.raw('48e7efee4fefffc0')  # AMOS saved set, local 64-byte frame
    c.move(A(7),A(2))
    S(A(0),'bitmap');S(A(1),'snapshot');S(D(0),'capacity');S(D(1),'mode')
    S(A(3),'saved_a3')
    S(I(0),'success')
    c.move(I(0),D(0))
    c.raw('20780004')     # ExecBase from 4.W: MC68020+ mandatory
    c.move(A(0),D(0));c.tst(D(0));B(7,'b8_copy_return')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1)  # BTST #AFF_68020,D0
    B(7,'b8_copy_return')
    G('mode',D(0))
    c.imm('cmp',1,D(0));B(2,'b8_copy_return') # mode >1
    G('bitmap',A(4))
    checked_pointer(A(4),I(40)) # full NDK BitMap metadata/pointers
    G('snapshot',A(3))
    checked_pointer(A(3))
    c.move(I(0),D(0));c.move(M(4,0),D(0),'w')
    c.imm('cmp',2,D(0));B(5,'b8_copy_return')
    c.move(D(0),D(2));c.imm('and',1,D(2));B(6,'b8_copy_return')
    c.move(I(0),D(1));c.move(M(4,2),D(1),'w')
    c.tst(D(1));B(7,'b8_copy_return')
    c.word(0xc0c1) # MULU.W D1,D0 -> unsigned bytes per plane
    c.tst(D(0));B(7,'b8_copy_return')
    S(D(0),'plane_bytes')
    c.move(I(0),D(5));c.move(M(4,5),D(5),'b')
    c.imm('cmp',1,D(5));B(5,'b8_copy_return')
    c.imm('cmp',8,D(5));B(2,'b8_copy_return')
    S(D(5),'depth')
    c.move(I(0),D(6))
    for n in range(1,9):
        c.imm('cmp',n,D(5));B(5,f'b8_total_done_{n}')
        G('plane_bytes',D(4))
        c.alu('add',D(4),6);B(5,'b8_copy_return')
        L(f'b8_total_done_{n}')
    S(D(6),'total')
    G('capacity',D(0));c.alu('cmp',D(6),0);B(5,'b8_copy_return')
    G('snapshot',A(3))
    checked_pointer(A(3),D(6))
    # Validate every destination/source plane before touching any pixels.
    for i in range(8):
        G('depth',D(5))
        c.imm('cmp',i+1,D(5));B(5,f'b8_validate_done_{i}')
        G('bitmap',A(4));c.move(M(4,8+4*i),A(3))
        G('plane_bytes',D(6))
        checked_pointer(A(3),D(6))
        L(f'b8_validate_done_{i}')
    G('snapshot',A(3))
    for i in range(8):
        G('depth',D(5))
        c.imm('cmp',i+1,D(5));B(5,f'b8_plane_done_{i}')
        G('bitmap',A(4));c.move(M(4,8+4*i),A(0))
        G('mode',D(6))
        c.tst(D(6));B(7,f'b8_capture_{i}')
        c.move(A(0),A(1)) # destination: screen plane
        c.move(A(3),A(0)) # source: snapshot
        B(0,f'b8_do_copy_{i}')
        L(f'b8_capture_{i}')
        c.move(A(3),A(1)) # destination: snapshot
        L(f'b8_do_copy_{i}')
        G('plane_bytes',D(7));c.shift(7,1)
        L(f'b8_copy_words_{i}')
        c.move(POST(0),POST(1),'w')
        c.quick(1,D(7),sub=True)
        B(6,f'b8_copy_words_{i}')
        G('mode',D(6))
        c.tst(D(6));B(7,f'b8_capture_done_{i}')
        c.move(A(0),A(3)) # snapshot cursor after restore
        B(0,f'b8_plane_done_{i}')
        L(f'b8_capture_done_{i}')
        c.move(A(1),A(3)) # snapshot cursor after capture
        L(f'b8_plane_done_{i}')
    S(I(1),'success')
    L('b8_copy_return')
    G('success',D(3))
    G('saved_a3',A(3))  # AMOS ABI: A3 omitted from MOVEM mask
    c.raw('4fef00404cdf77f774004e75')
    blob=c.out()
    assert len(blob)<32766 and len(blob)%2==0
    return blob,c.labels


if __name__=='__main__':
    from hashlib import sha256
    blob,labels=emit_planar_snapshot_core()
    print('M19 B8 MC68020 private snapshot copy, SOURCE ONLY',len(blob),
          sha256(blob).hexdigest(),labels['b8_planar_snapshot_core_entry'])
