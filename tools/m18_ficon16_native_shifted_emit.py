"""M18/P3 — native 68000 pixel-exact Fast Icon CPU kernel for arbitrary X.

INTERNAL core (no AP20): one validated Unity AGA F Icon slot (288 bytes,
16 rows of preserve-word + eight planar words) in Fast or Chip memory.
A0=slot, A1=array of eight validated Chip back-plane pointers;
D0=signed X, D1=signed Y, D2=positive even row stride, D3=mode 0/1,
D4=screen pixel width, D5=screen height.  X,Y are signed 16-bit.
D3 returns 1 success/no-op or 0 invalid; D2 cleared.
All other standard AMOS registers and A3 preserved, stack balanced.

Two masked 16-bit destination words PER plane/row at most, never pixel
loops; X can be unaligned and negative. Clip vertical, horizontal and the
last partial word to preserve pixels outside the rectangle and screen.
Mode 0 replaces zero with colour zero; mode 1 uses Unity's colour-zero
transparency (preserve bits). No DMA, allocation, ScreenBuffer, Safe,
palette, Swap or VBL. Caller must validate actual ownership, bank/header,
canonical mask, allocations, depth=8, back buffer and Safe BEFORE call.
"""
from m68k_emit import Code, D, A, M, POST, I

F = dict(x=0,y=4,stride=8,width=12,height=16,mode=20,
         shift=24,backshift=28,baseword=32,lastword=36,lastmask=40,
         offset0=44,offset1=48,mask0=52,mask1=56)
FRAME = 96

def _lsrw(count_reg, dest_reg):
    """LSR.W Dcount,Ddest, register count (Motorola 68000)."""
    return 0xe068 | (count_reg << 9) | dest_reg

def _lslw(count_reg, dest_reg):
    """LSL.W Dcount,Ddest, register count (Motorola 68000)."""
    return 0xe168 | (count_reg << 9) | dest_reg

def emit_ficon16_shifted_cpu():
    c = Code()
    B, L = c.branch, c.label
    c.raw('48e7efee')                  # Save D0/D1,D4..D7,A0..A2/A4..A6.
    c.raw('4fefffa0')                  # LEA -96(SP),SP
    c.move(A(7),A(2))
    for key,reg in [('x',0),('y',1),('stride',2),('width',4),
                    ('height',5),('mode',3)]:
        c.move(D(reg),M(2,F[key]))
    # Reject all malformed geometric and pointer metadata before painting.
    for addr in (0,1):
        c.move(A(addr),D(6));c.tst(D(6));B(7,'invalid')
        c.imm('and',1,D(6));B(6,'invalid')
    for reg in (0,1):
        c.imm('cmp',-32768,D(reg));B(13,'invalid')
        c.imm('cmp',32767,D(reg));B(14,'invalid')
    c.imm('cmp',1,D(3));B(14,'invalid') # 0/1 only
    c.tst(D(3));B(11,'invalid')
    for reg in (4,5):
        c.tst(D(reg));B(15,'invalid')
        c.imm('cmp',4096,D(reg));B(14,'invalid')
    c.tst(D(2));B(15,'invalid')
    c.imm('cmp',65535,D(2));B(14,'invalid')
    c.move(D(2),D(6));c.imm('and',1,D(6));B(6,'invalid')
    c.move(D(4),D(6));c.imm('add',15,D(6))
    c.shift(6,4)
    c.shift(6,1,left=True)
    c.alu('cmp',D(6),2);B(5,'invalid') # stride < ceil(width/16)*2
    c.move(A(1),A(4));c.move(I(8),D(6))
    L('check_planes')
    c.move(POST(4),D(7));c.tst(D(7));B(7,'invalid')
    c.imm('cmp',-1,D(7));B(7,'invalid')
    c.imm('and',1,D(7));B(6,'invalid')
    c.quick(1,D(6),sub=True);B(6,'check_planes')

    # Entire image outside the visible X range? Valid no-op.
    c.move(D(0),D(6));c.imm('add',16,D(6))
    c.tst(D(6));B(15,'success')    # x+16 <= 0
    c.alu('cmp',D(4),0);B(12,'success') # x >= width

    # Divmod signed X by 16. Arithmetic shift is essential for negative X.
    c.move(D(0),D(6))
    c.word(0xe886)                 # ASR.L #4,D6: floor(x/16)
    c.move(D(6),M(2,F['baseword']))
    c.move(D(0),D(6));c.imm('and',15,D(6))
    c.move(D(6),M(2,F['shift']))
    c.move(I(16),D(7));c.alu('sub',D(6),7)
    c.move(D(7),M(2,F['backshift']))

    c.move(D(4),D(6));c.quick(1,D(6),sub=True)
    c.shift(6,4)                  # (width-1)//16
    c.move(D(6),M(2,F['lastword']))
    c.move(I(0xffff),D(6))
    c.move(D(4),D(7));c.imm('and',15,D(7))
    c.tst(D(7));B(7,'lastmask_done')
    c.move(I(16),D(0));c.alu('sub',D(7),0)
    L('mask_shift')
    c.word(0xe34e)                # LSL.W #1,D6
    c.quick(1,D(0),sub=True);B(6,'mask_shift')
    L('lastmask_done')
    c.move(D(6),M(2,F['lastmask']))

    c.move(A(0),A(6))            # Source 18-byte rows
    c.move(I(0),D(2))            # Row index 0..15
    L('row')
    c.move(M(2,F['y']),D(7));c.alu('add',D(2),7)
    c.tst(D(7));B(11,'skip_row')
    c.alu('cmp',M(2,F['height']),7);B(12,'skip_row')
    c.move(M(2,F['stride']),D(6))
    c.word(0xcec6)                # MULU.W D6,D7 -> y*stride
    c.move(M(2,F['baseword']),D(6))
    c.shift(6,1,left=True)       # word index to byte offset
    c.alu('add',D(6),7)
    c.move(D(7),M(2,F['offset0']))
    c.quick(2,D(7))
    c.move(D(7),M(2,F['offset1']))

    # Prepare visible mask. For opaque, all 16 source bits replace pixels.
    c.move(POST(6),D(4),'w')      # Unity preserve mask
    c.tst(M(2,F['mode']));B(7,'opaque_mask')
    c.word(0x4644)               # NOT.W D4 => source visible bits
    B(0,'have_visible')
    L('opaque_mask')
    c.move(I(0xffff,'w'),D(4),'w')
    L('have_visible')
    c.move(D(4),D(5),'w')
    c.move(M(2,F['shift']),D(7))
    c.word(_lsrw(7,5))
    c.move(D(5),M(2,F['mask0']),'w')
    c.move(D(4),D(5),'w')
    c.move(M(2,F['backshift']),D(7))
    c.word(_lslw(7,5))
    c.move(D(5),M(2,F['mask1']),'w')

    # Restrict first and second halves to valid physical screen words.
    c.move(M(2,F['baseword']),D(6))
    c.tst(D(6));B(11,'drop_mask0')
    c.alu('cmp',M(2,F['lastword']),6);B(14,'drop_mask0')
    B(6,'mask0_clipped')          # if index != last word
    c.move(M(2,F['mask0']),D(7),'w')
    c.alu('and',M(2,F['lastmask']),7,'w')
    c.move(D(7),M(2,F['mask0']),'w')
    B(0,'mask0_clipped')
    L('drop_mask0')
    c.move(I(0),M(2,F['mask0']))
    L('mask0_clipped')
    c.quick(1,D(6))
    c.tst(D(6));B(11,'drop_mask1')
    c.alu('cmp',M(2,F['lastword']),6);B(14,'drop_mask1')
    B(6,'mask1_clipped')
    c.move(M(2,F['mask1']),D(7),'w')
    c.alu('and',M(2,F['lastmask']),7,'w')
    c.move(D(7),M(2,F['mask1']),'w')
    B(0,'mask1_clipped')
    L('drop_mask1')
    c.move(I(0),M(2,F['mask1']))
    L('mask1_clipped')
    c.move(M(2,F['mask0']),D(6),'w')
    c.alu('or',M(2,F['mask1']),6,'w')
    c.tst(D(6),'w');B(7,'skip_planes')

    c.move(A(1),A(5))            # eight Chip plane pointers
    c.move(I(8),D(1))
    L('plane')
    c.move(POST(6),D(5),'w')      # 16 source pixels of this bitplane
    c.move(POST(5),A(0))          # Chip plane base (not modified)
    c.move(M(2,F['mask0']),D(6),'w')
    c.tst(D(6),'w');B(7,'half1')
    c.move(D(5),D(0),'w')
    c.move(M(2,F['shift']),D(7))
    c.word(_lsrw(7,0))
    c.alu('and',D(6),0,'w')
    c.word(0x4646)               # NOT.W D6 => preserve unmasked bits
    c.move(A(0),A(4))
    c.move(M(2,F['offset0']),D(7))
    c.word(0xd9c7)               # ADDA.L D7,A4
    c.move(M(4),D(4),'w')
    c.alu('and',D(6),4,'w')
    c.alu('or',D(0),4,'w')
    c.move(D(4),M(4),'w')
    L('half1')
    c.move(M(2,F['mask1']),D(6),'w')
    c.tst(D(6),'w');B(7,'next_plane')
    c.move(D(5),D(0),'w')
    c.move(M(2,F['backshift']),D(7))
    c.word(_lslw(7,0))
    c.alu('and',D(6),0,'w')
    c.word(0x4646)
    c.move(A(0),A(4))
    c.move(M(2,F['offset1']),D(7))
    c.word(0xd9c7)
    c.move(M(4),D(4),'w')
    c.alu('and',D(6),4,'w')
    c.alu('or',D(0),4,'w')
    c.move(D(4),M(4),'w')
    L('next_plane')
    c.quick(1,D(1),sub=True);B(6,'plane')
    B(0,'next_row')
    L('skip_planes')
    c.raw('4dee0010')           # LEA 16(A6),A6
    B(0,'next_row')
    L('skip_row')
    c.raw('4dee0012')           # LEA 18(A6),A6
    L('next_row')
    c.quick(1,D(2))
    c.imm('cmp',16,D(2));B(6,'row')
    L('success')
    c.move(I(1),D(3));B(0,'done')
    L('invalid')
    c.move(I(0),D(3))
    L('done')
    c.raw('4fef0060')           # LEA 96(SP),SP
    c.raw('4cdf77f7')           # Restore all except D2/D3, A3 untouched
    c.raw('74004e75')           # D2=0, RTS
    raw=c.out()
    assert raw[:2]==bytes.fromhex('48e7') and raw[-2:]==b'\x4e\x75'
    assert len(raw)%2==0 and len(raw)<2200
    return raw,c.labels

if __name__=='__main__':
    from hashlib import sha256
    native, labels=emit_ficon16_shifted_cpu()
    print('M18/P3 SHIFTED 68000 CORE (NO AP20/WinUAE)',
          len(native),sha256(native).hexdigest(),len(labels),'labels')
