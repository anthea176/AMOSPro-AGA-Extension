"""M18/P2: real 68000 aligned Fast Icon CPU word-write CORE, not an AP20 command.

Input A0=trusted 288-byte icon slot (Fast or Chip), A1=array of 8 Chip
plane pointers, D0=X, D1=Y, D2=BytesPerRow, D3=Mode (0=opaque, 1=masked),
D4=screen width, D5=screen height. Coordinates signed int16.
Output D3=1 success/no-op, D3=0 reject; D2=0. A3 unchanged.
Preserve D0,D1,D4-D7/A0-A2/A4-A6 and balanced stack.
X not a multiple of 16 is rejected, NOT rounded. Y clips by pixel.
Caller must prevalidate source bank/header/canonical masks, screen and
screenbuffer, depth=8, valid Chip plane allocations, and Safe; this core
intentionally neither owns resources nor calls the OS, AP20 or Blitter.
"""
from m68k_emit import Code, D, A, M, POST, I

F = dict(x=0, y=4, stride=8, width=12, height=16, mode=20,
         mask_clip=24, x_byte=28, dy=32)

def emit_ficon16_aligned_cpu():
    c=Code()
    B=c.branch
    L=c.label
    c.raw('48e7efee')               # Existing AMOS-compatible save set
    c.raw('4fefffc0')               # LEA -64(SP),SP
    c.move(A(7),A(2))
    for name,reg in [('x',0),('y',1),('stride',2),('width',4),
                     ('height',5),('mode',3)]:
        c.move(D(reg),M(2,F[name]))
    c.move(A(0),D(6));c.tst(D(6));B(7,'bad')
    c.imm('and',1,D(6));B(6,'bad')
    c.move(A(1),D(6));c.tst(D(6));B(7,'bad')
    c.imm('and',1,D(6));B(6,'bad')
    for reg in (0,1):
        c.imm('cmp',-32768,D(reg));B(13,'bad')
        c.imm('cmp',32767,D(reg));B(14,'bad')
    c.imm('cmp',1,D(3));B(2,'bad')
    for reg in (4,5):
        c.tst(D(reg));B(15,'bad')
        c.imm('cmp',4096,D(reg));B(14,'bad')
    c.tst(D(2));B(15,'bad')
    c.imm('cmp',65535,D(2));B(14,'bad')
    c.move(D(2),D(6));c.imm('and',1,D(6));B(6,'bad')
    c.move(D(0),D(6));c.imm('and',15,D(6));B(6,'bad')
    c.move(D(4),D(6));c.imm('add',15,D(6));c.shift(6,4)
    c.shift(6,1,left=True)
    c.alu('cmp',D(6),2);B(5,'bad')
    # Validate every Chip plane pointer before any write.
    c.move(A(1),A(4));c.move(I(8),D(6))
    L('check_planes')
    c.move(POST(4),D(7));c.tst(D(7));B(7,'bad')
    c.imm('cmp',-1,D(7));B(7,'bad')
    c.imm('and',1,D(7));B(6,'bad')
    c.quick(1,D(6),sub=True);B(6,'check_planes')
    # A negative X aligned to 16 does not overlap the screen at all.
    c.tst(D(0));B(11,'ok')
    c.alu('cmp',D(4),0);B(12,'ok')
    c.move(D(0),D(6));c.shift(6,3)
    c.move(D(6),M(2,F['x_byte']))
    # Horizontal clipping of rightmost, partially filled destination word.
    c.move(I(0xffff),D(6))
    c.move(D(4),D(7));c.alu('sub',D(0),7)
    c.imm('cmp',16,D(7));B(12,'clip_ready')
    c.move(I(16),D(0));c.alu('sub',D(7),0)
    L('clip_loop')
    c.word(0xe34e)                  # LSL.W #1,D6
    c.quick(1,D(0),sub=True);B(6,'clip_loop')
    L('clip_ready')
    c.move(D(6),M(2,F['mask_clip']))
    c.move(A(0),A(6))
    c.move(I(0),D(2))
    L('row_loop')
    c.move(M(2,F['y']),D(7));c.alu('add',D(2),7)
    c.tst(D(7));B(11,'skip_row')
    c.alu('cmp',M(2,F['height']),7);B(12,'skip_row')
    c.move(D(7),M(2,F['dy']))
    c.move(M(2,F['stride']),D(6))
    c.word(0xcec6)                  # MULU.W D6,D7
    c.alu('add',M(2,F['x_byte']),7)
    c.move(POST(6),D(4),'w')        # 16-bit source preserve/zero mask
    c.move(M(2,F['mask_clip']),D(6))
    c.tst(M(2,F['mode']));B(7,'mask_ready')
    c.word(0x4644)                  # NOT.W D4 => visible mask
    c.alu('and',D(4),6,'w')
    L('mask_ready')
    c.tst(D(6),'w');B(7,'skip_planes')
    c.move(D(6),D(0),'w');c.word(0x4640) # D0.w=~visible
    c.move(A(1),A(5));c.move(I(8),D(1))
    L('plane_loop')
    c.move(POST(6),D(4),'w')         # source plane word
    c.move(POST(5),A(4))             # destination Chip plane
    c.word(0xd9c7)                  # ADDA.L D7,A4
    c.move(M(4),D(5),'w')
    c.alu('and',D(0),5,'w')          # preserve invisible pixels
    c.alu('and',D(6),4,'w')          # source visible pixels
    c.alu('or',D(4),5,'w')
    c.move(D(5),M(4),'w')
    c.quick(1,D(1),sub=True);B(6,'plane_loop')
    B(0,'next_row')
    L('skip_planes')
    c.raw('4dee0010')               # LEA 16(A6),A6
    B(0,'next_row')
    L('skip_row')
    c.raw('4dee0012')               # LEA 18(A6),A6
    L('next_row')
    c.quick(1,D(2))
    c.imm('cmp',16,D(2));B(6,'row_loop')
    L('ok')
    c.move(I(1),D(3));B(0,'leave')
    L('bad')
    c.move(I(0),D(3))
    L('leave')
    c.raw('4fef0040')               # LEA +64(SP),SP
    c.raw('4cdf77f7')               # restore all except D2/D3/A3
    c.raw('74004e75')               # D2=0; RTS
    raw=c.out()
    assert raw[:2]==bytes.fromhex('48e7') and raw[-2:]==b'\x4e\x75'
    assert len(raw)%2==0
    return raw,c.labels

if __name__=='__main__':
    from hashlib import sha256
    code,labels=emit_ficon16_aligned_cpu()
    print('M18 P2 ALIGNED CORE (NO AP20, NO WINUAE)',
          len(code),'bytes',sha256(code).hexdigest(),len(labels),'labels')
