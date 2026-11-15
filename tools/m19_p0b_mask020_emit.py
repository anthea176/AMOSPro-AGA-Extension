#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0b PRIVATE 68020 independent-mask generation kernel.

This is NOT an AMOS/AP20 command and cannot be called by an AMOS program.
The future public wrapper must validate the complete AGBO bank, stage a new
transactional payload, allocate exact destination bytes, and commit atomically.

INPUT (already strictly prevalidated by the future native wrapper):
    A0 = nonzero even address of plane-major image data
    A1 = nonzero even address of writable mask storage (>= stride*height)
    D0 = width [1,4096], D1 = height [1,4096], D2 = bitplanes [1,8]
    D3 = transparent color [0,2**depth-1], D4 = stride [ceil(width/16)*2]
OUTPUT: D3=1 success, D3=0 reject, D2=0 integer status.

This kernel performs a word-major scan (one pass over the mask) and combines
per-plane DIFFERENCES from the transparent index. Colour index 0 may remain
opaque; source pixels remain unmodified. The final word is masked by width.
The inner loop uses MC68020 BFEXTU for transparent-index bit extraction.
"""
from __future__ import annotations
from m68k_emit import Code, A, D, I, M, POST

FRAME=96
K=('src dst width height depth transparent stride plane_size words '
   'rows_left words_left tail').split()
F={k:4*i for i,k in enumerate(K)}
assert len(F)==12 and F['tail']+4<=FRAME


def emit_mask020() -> tuple[bytes, dict[str,int]]:
    c=Code(); B,L=c.branch,c.label
    def S(r,key): c.move(r,M(2,F[key]))
    def G(key,r): c.move(M(2,F[key]),r)

    L('mask_kernel')
    c.raw('48e7efee')      # preserved AMOS-style register subset
    c.raw('4fefffa0')      # LEA -96(SP),SP
    c.move(A(7),A(2))
    for reg,key in ((A(0),'src'),(A(1),'dst'),(D(0),'width'),
                    (D(1),'height'),(D(2),'depth'),
                    (D(3),'transparent'),(D(4),'stride')):
        S(reg,key)
    # All bounds and pointer checks BEFORE any destination store.
    for key,upper in (('width',4096),('height',4096),('depth',8)):
        G(key,D(0)); c.imm('cmp',1,D(0)); B(5,'reject') # BLT
        c.imm('cmp',upper,D(0)); B(2,'reject')        # BHI
    for key in ('src','dst'):
        G(key,D(0)); c.tst(D(0)); B(7,'reject')
        c.imm('and',1,D(0)); B(6,'reject')
    G('width',D(0)); G('height',D(1))
    c.word(0xc0c1) # MULU.W D1,D0, <=16M
    c.imm('cmp',0x400000,D(0)); B(2,'reject') # host 4Mi pixels limit
    # Row stride is exact ceil(width/16)*2.
    G('width',D(0)); c.imm('add',15,D(0))
    c.shift(0,4,left=False); c.shift(0,1,left=True)
    G('stride',D(1)); c.alu('cmp',D(1),0); B(6,'reject')
    c.shift(0,1,left=False); S(D(0),'words')
    G('stride',D(0)); G('height',D(1))
    c.word(0xc0c1)   # MULU.W D1,D0, exact bytes of ONE plane
    S(D(0),'plane_size')
    # 0 <= C < 2**depth, reject otherwise.
    G('transparent',D(1)); c.tst(D(1)); B(11,'reject')
    c.move(I(1),D(6)); G('depth',D(7))
    L('colour_limit')
    c.alu('add',D(6),6)
    c.quick(1,D(7),sub=True); B(6,'colour_limit')
    c.alu('cmp',D(6),1); B(4,'reject')
    # Tail-mask lookup by width modulo 16, 0 => FFFF.
    G('width',D(0)); c.imm('and',15,D(0))
    c.shift(0,1,left=True)
    c.lea(4,'tail_table')
    c.raw('d9c0')      # ADDA.L D0,A4
    c.move(I(0),D(0)); c.move(M(4),D(0),'w'); S(D(0),'tail')
    G('height',D(0)); S(D(0),'rows_left')
    G('src',A(0)); G('dst',A(1))

    L('row')
    G('words',D(0)); S(D(0),'words_left')
    L('word')
    c.move(A(0),A(4))
    G('plane_size',D(4)); G('depth',D(7))
    G('transparent',D(5)); c.move(I(0),D(6))
    L('plane')
    c.move(I(0),D(0)); c.move(M(4),D(0),'w')
    # BFEXTU D5{31:1},D1. MC68020 instruction -- NOT a 68000 fallback.
    c.word(0xe9c5); c.word(0x17c1)
    c.tst(D(1)); B(7,'colour_bit_zero')
    c.word(0x0a40); c.word(0xffff)  # EORI.W #$FFFF,D0
    L('colour_bit_zero')
    c.alu('or',D(0),6,'w')           # OR.W D0,D6 (opaque if any plane differs)
    c.raw('d9c4')                  # ADDA.L D4,A4, next plane's same word
    c.shift(5,1,left=False)        # LSR.L #1,D5
    c.quick(1,D(7),sub=True); B(6,'plane')
    G('words_left',D(0)); c.imm('cmp',1,D(0)); B(6,'full_word')
    G('tail',D(0)); c.alu('and',D(0),6,'w')
    L('full_word')
    c.move(D(6),POST(1),'w')       # exactly one 16-bit word of the mask
    c.quick(2,A(0))
    G('words_left',D(0)); c.quick(1,D(0),sub=True)
    S(D(0),'words_left'); B(6,'word')
    G('rows_left',D(0)); c.quick(1,D(0),sub=True)
    S(D(0),'rows_left'); B(6,'row')
    L('accept')
    c.raw('4fef0060')  # LEA +96(SP),SP
    c.raw('4cdf77f7')  # restore saved regs
    c.move(I(1),D(3)); c.raw('74004e75')  # D3=1, D2=0, RTS
    L('reject')
    c.raw('4fef0060');c.raw('4cdf77f7')
    c.move(I(0),D(3)); c.raw('74004e75')
    L('tail_table')
    for count in range(16):
        mask=0xffff if count==0 else (0xffff << (16-count)) & 0xffff
        c.word(mask)
    raw=c.out()
    assert len(raw)%2==0 and len(raw)<32766
    assert raw.count(bytes.fromhex('e9c517c1'))==1
    return raw,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_mask020()
    print('M19 P0b private MC68020 native mask kernel (NOT AP20)',len(raw),sha256(raw).hexdigest(),labels)
