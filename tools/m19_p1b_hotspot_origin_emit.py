#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1b, source-only native Bob hotspot -> private Safe-Blit origin.

Trusted PRIVATE call AFTER P0 checked AGBO staging and per-image resolution:
    A0 -> validated 40-byte AGBO v1 image directory entry
    A3 -> validated two longs (logical screen width, logical screen height)
    D1 = persistent logical Bob X, D4 = persistent logical Bob Y
Result:
    D3 = 1 when the shifted image intersects the logical screen,
         D1/D4 = adjusted top-left X/Y for the EXISTING Safe Blitter;
    D3 = 0 when fully clipped, D1/D4 UNCHANGED (successful no-op for caller).
    D2 = 0; D0, D5-D7 and A0-A6 preserved, stack balanced.

The helper is NOT yet called by P1a's native frame path; it is a
source-only building block. No public AMOS token and no installed .Lib.
The parent must validate both pointers, owner, bank generation and DMA
safety before entering. No direct rendering, allocation or Swap here.
"""
from __future__ import annotations
from m68k_emit import Code, A, D, I, M

AGBO_ENTRY_SIZE = 40
HOT_X = 28
HOT_Y = 30
MAX_SIDE = 4096
assert HOT_Y + 2 <= AGBO_ENTRY_SIZE


def emit_hotspot_origin() -> tuple[bytes,dict[str,int]]:
    c=Code()
    B,L=c.branch,c.label
    L('p1b_hotspot_origin_entry')
    c.raw('2f00')                  # MOVE.L D0,-(SP), preserve AMOS D0
    c.move(D(1),D(2))             # prospective top-left X
    c.move(M(0,HOT_X),D(0),'w')
    c.word(0x48c0)               # EXT.L D0, signed hotspot_x
    c.alu('sub',D(0),2)
    c.move(D(4),D(3))             # prospective top-left Y
    c.move(M(0,HOT_Y),D(0),'w')
    c.word(0x48c0)               # EXT.L D0, signed hotspot_y
    c.alu('sub',D(0),3)

    # The P0d private painter only accepts signed 16-bit draw origins.
    # An origin outside this bound cannot overlap a <=4096-pixel image
    # against a <=4096 logical screen, so it is a successful NO-DMA skip.
    for reg in (2,3):
        c.imm('cmp',-32768,D(reg));B(13,'p1b_no_overlap')
        c.imm('cmp',32767,D(reg));B(14,'p1b_no_overlap')

    # Screen logical width/height are prevalidated by the Safe path.
    c.alu('cmp',M(3,0),2);B(12,'p1b_no_overlap')
    c.alu('cmp',M(3,4),3);B(12,'p1b_no_overlap')

    # image source sizes are verified AGBO unsigned words at +2/+4.
    # Reject malformed 0 or >4096 values even for this private helper.
    c.move(I(0),D(0));c.move(M(0,2),D(0),'w')
    c.tst(D(0));B(15,'p1b_no_overlap')
    c.imm('cmp',MAX_SIDE,D(0));B(14,'p1b_no_overlap')
    c.alu('add',D(2),0)
    c.tst(D(0));B(15,'p1b_no_overlap')
    c.move(I(0),D(0));c.move(M(0,4),D(0),'w')
    c.tst(D(0));B(15,'p1b_no_overlap')
    c.imm('cmp',MAX_SIDE,D(0));B(14,'p1b_no_overlap')
    c.alu('add',D(3),0)
    c.tst(D(0));B(15,'p1b_no_overlap')

    c.move(D(2),D(1))            # only commit offsets after ALL checks
    c.move(D(3),D(4))
    c.move(I(1),D(3))
    B(0,'p1b_hotspot_return')
    L('p1b_no_overlap')
    c.move(I(0),D(3))
    L('p1b_hotspot_return')
    c.raw('201f')                # MOVE.L (SP)+,D0
    c.move(I(0),D(2))            # AMOS numeric return convention
    c.raw('4e75')                # RTS
    raw=c.out()
    if len(raw)&1 or len(raw)>256 or c.labels['p1b_hotspot_origin_entry']!=0:
        raise ValueError('P1b MC68020 helper ABI/PC16 guard failed')
    return raw,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_hotspot_origin()
    print('M19 P1b AGBO hotspot native ORIGIN ONLY',len(raw),
          sha256(raw).hexdigest(),'SOURCE ONLY; NOT WIRED TO RENDERER')
