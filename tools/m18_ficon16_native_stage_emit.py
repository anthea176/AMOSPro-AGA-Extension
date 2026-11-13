"""M18/P2 real 68000 Fast->Chip staging core: 288-byte Unity icon slot.

Source: 16 rows of [preserveMask,plane0..plane7] (9 words per row).
Destination: VISIBLE mask (inverse of Unity preserve mask) 32 bytes,
followed by 8 contiguous 32-byte bitplanes. VISIBLE bit 1 means copy;
format matches graphics.library/BltMaskBitMapRastPort mask semantics.
Inputs A0=prevalidated 288-byte source, A1=288-byte Chip cache target.
Source and destination must be even, nonzero and NON-OVERLAPPING.
Reject 32-bit address wrapping. Output D3=1 success/0 refusal, D2=0,
balanced SP and other standard AMOS register preservation.
THIS IS INTERNAL ONLY: no AMOS Bank/ScreenBuffer/Safe or AP20 binding,
no allocator, no Blitter DMA, no claim about actual Fast allocation.
"""
from m68k_emit import Code,D,A,M,POST,I
SLOT=288

def emit_ficon16_stage_cpu():
    c=Code()
    B=c.branch
    L=c.label
    c.raw('48e7efee')
    c.move(A(0),D(0));c.tst(D(0));B(7,'bad')
    c.move(A(1),D(1));c.tst(D(1));B(7,'bad')
    c.move(D(0),D(4));c.imm('and',1,D(4));B(6,'bad')
    c.move(D(1),D(4));c.imm('and',1,D(4));B(6,'bad')
    c.move(D(0),D(2));c.imm('add',SLOT,D(2));B(5,'bad')
    c.move(D(1),D(3));c.imm('add',SLOT,D(3));B(5,'bad')
    c.alu('cmp',D(3),0);B(4,'valid')  # src >= dst_end
    c.alu('cmp',D(2),1);B(4,'valid')  # dst >= src_end
    B(0,'bad')
    L('valid')
    c.move(I(0),D(0))              # row offset: 0,2,...30
    c.move(I(16),D(1))
    L('row')
    c.move(A(1),A(4))
    c.word(0xd9c0)                # ADDA.L D0,A4
    # Unity stores PRESERVE=1 transparent; the OS masked blit uses VISIBLE=1.
    c.move(POST(0),D(6),'w')      # first row word: preserve mask
    c.word(0x4646)               # NOT.W D6 -> visible mask for DMA
    c.move(D(6),M(4),'w')
    c.raw('49ec0020')            # LEA 32(A4),A4: plane0
    c.move(I(8),D(5))
    L('word')
    c.move(POST(0),M(4),'w')      # source plane word
    c.raw('49ec0020')            # LEA 32(A4),A4: next staged plane
    c.quick(1,D(5),sub=True);B(6,'word')
    c.quick(2,D(0))
    c.quick(1,D(1),sub=True);B(6,'row')
    c.move(I(1),D(3));B(0,'finish')
    L('bad')
    c.move(I(0),D(3))
    L('finish')
    c.raw('4cdf77f7')
    c.raw('74004e75')
    raw=c.out()
    assert len(raw)%2==0
    return raw,c.labels

if __name__=='__main__':
    from hashlib import sha256
    code,labels=emit_ficon16_stage_cpu()
    print('M18 P2 NATIVE STAGE (NO AP20, NO WINUAE)',
          len(code),'bytes',sha256(code).hexdigest(),len(labels),'labels')
