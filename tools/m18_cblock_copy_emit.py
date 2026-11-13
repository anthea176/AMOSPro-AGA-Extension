"""M18 CBlock standalone M68000 CPU/Blitter planar Chip-to-Chip copy core.

NOT an AP20 command / NOT installed / NOT WinUAE-qualified.

Inputs (prevalidated full logical-screen bounds, all memory genuinely Chip):
  A0=source BitMap, A1=destination BitMap, A6=graphics.library,
  D0=source X, D1=source Y, D2=dest X, D3=dest Y,
  D4=width pixels, D5=height pixels,
  D6=method: 0 CPU byte copy (8px), 1 CPU word copy (16px),
             2 BltBitMapRastPort (8px, horizontal blitter shift allowed).
Outputs: D3=1 success / D3=0 rejection, D2=0. A3 untouched.
Preserves D0,D1,D4-D7/A0-A2/A4-A6 and caller stack; no allocations.

Fast paths: 8px uses MOVE.B, 16px uses MOVE.W. Both copy each
bitplane's rows without changing bytes outside the rectangle. The Blitter
path calls documented graphics.library functions (InitRastPort,
BltBitMapRastPort with minterm 0xC0, WaitBlit); Safe/Chip residency and
real logical dimensions are validated by future enclosing AP20 wrappers.
"""
from m68k_emit import Code,D,A,M,POST,I

LVO_INITRASTPORT=-198
LVO_BLTBITMAPRASTPORT=-606
LVO_WAITBLIT=-228
FRAME=256
RASTPORT=128
F=dict(src=0,dst=4,sx=8,sy=12,dx=16,dy=20,w=24,h=28,
       method=32,gfx=36,src_bpr=40,dst_bpr=44,depth=48,
       byte_count=52,src_mod=56,dst_mod=60,plane_count=64,
       src_rows=68,dst_rows=72)

def emit_cblock_copy_core():
    c=Code();B,L=c.branch,c.label
    def get(k,reg):c.move(M(4,F[k]),reg)
    def put(reg,k):c.move(reg,M(4,F[k]))
    def unsigned_word(a,off,reg):
        c.move(I(0),reg);c.move(M(a,off),reg,'w')

    c.raw('48e7efee')                 # preserve AMOS regs except D2/D3
    c.raw('4fefff00')                 # LEA -256(SP),SP
    c.move(A(7),A(4))
    for key,reg in (('src',A(0)),('dst',A(1)),('gfx',A(6)),
                    ('sx',D(0)),('sy',D(1)),('dx',D(2)),('dy',D(3)),
                    ('w',D(4)),('h',D(5)),('method',D(6))):
        put(reg,key)
    c.move(I(0),D(3))

    # Strict geometrical prevalidation before any transfer or Blitter call.
    for key in ('src','dst'):
        get(key,D(0));c.tst(D(0));B(7,'bad')
        c.imm('and',1,D(0));B(6,'bad')
    get('method',D(0));c.imm('cmp',2,D(0));B(2,'bad')
    c.tst(D(0));B(11,'bad')
    for key in ('sx','sy','dx','dy'):
        get(key,D(0));c.tst(D(0));B(11,'bad')
        c.imm('cmp',32767,D(0));B(14,'bad')
    for key in ('w','h'):
        get(key,D(0));c.tst(D(0));B(15,'bad')
        c.imm('cmp',4096,D(0));B(14,'bad')
    # All methods require 8-pixel X positions/width. CPU-word requires 16.
    get('method',D(1));c.imm('cmp',1,D(1));B(7,'word_align')
    c.move(I(7),D(1));B(0,'align_test')
    L('word_align');c.move(I(15),D(1))
    L('align_test')
    for key in ('sx','dx','w'):
        get(key,D(0));c.alu('and',D(1),0);B(6,'bad')

    # Read source/destination canonical BitMap header.
    for bitmap,bpr,rows in (('src','src_bpr','src_rows'),
                            ('dst','dst_bpr','dst_rows')):
        get(bitmap,A(0));unsigned_word(0,0,D(0));put(D(0),bpr)
        c.tst(D(0));B(15,'bad')
        c.imm('and',1,D(0));B(6,'bad')
        unsigned_word(0,2,D(0));put(D(0),rows)
        c.tst(D(0));B(15,'bad')
        c.move(I(0),D(0));c.move(M(0,5),D(0),'b')
        c.tst(D(0));B(15,'bad')
        c.imm('cmp',8,D(0));B(14,'bad')
        if bitmap=='src':put(D(0),'depth')
        else:c.alu('cmp',M(4,F['depth']),0);B(6,'bad')
    # Source and destination rectangles must be within physical BitMap.
    for x,y,bpr,rows in (('sx','sy','src_bpr','src_rows'),
                         ('dx','dy','dst_bpr','dst_rows')):
        get(x,D(0));get('w',D(1));c.alu('add',D(1),0)
        get(bpr,D(1));c.shift(1,3,left=True)
        c.alu('cmp',D(1),0);B(2,'bad')
        get(y,D(0));get('h',D(1));c.alu('add',D(1),0)
        c.alu('cmp',M(4,F[rows]),0);B(2,'bad')
    # Verify nonzero word-aligned BitMap plane pointers before first write.
    get('src',A(5));c.quick(8,A(5))
    get('dst',A(6));c.quick(8,A(6))
    get('depth',D(7))
    L('check_planes')
    for ptr in (5,6):
        c.move(POST(ptr),D(0));c.tst(D(0));B(7,'bad')
        c.imm('and',1,D(0));B(6,'bad')
    c.quick(1,D(7),sub=True);B(6,'check_planes')
    get('method',D(0));c.imm('cmp',2,D(0));B(6,'cpu_copy')

    # Trusted private-screen back Bitmap -> temporary Chip Bitmap or reverse.
    # Initializing one RastPort avoids raw hardware registers and supports
    # the 8-pixel origin shift at the graphics.library level.
    get('gfx',D(0));c.tst(D(0));B(7,'bad')
    get('gfx',A(6))
    c.raw('43ec0080')               # LEA 128(A4),A1 (RastPort)
    c.call_os(LVO_INITRASTPORT)
    c.raw('43ec0080')
    get('dst',M(1,4))               # rp_BitMap pointer (offset +4)
    get('src',A(0));get('sx',D(0));get('sy',D(1))
    get('dx',D(2));get('dy',D(3));get('w',D(4));get('h',D(5))
    c.move(I(0xc0),D(6))
    c.call_os(LVO_BLTBITMAPRASTPORT)
    get('gfx',A(6));c.call_os(LVO_WAITBLIT)
    B(0,'ok')

    # Move.B pixel bytes or Move.W words along rows (no source shifts).
    L('cpu_copy')
    get('w',D(0));c.shift(0,3)
    put(D(0),'byte_count')
    get('src_bpr',D(1));c.alu('sub',D(0),1);put(D(1),'src_mod')
    get('dst_bpr',D(1));c.alu('sub',D(0),1);put(D(1),'dst_mod')
    get('src',A(5));c.quick(8,A(5))
    get('dst',A(6));c.quick(8,A(6))
    get('depth',D(7))
    L('copy_plane')
    c.move(POST(5),A(0));c.move(POST(6),A(1))
    # A0 += Sy*srcBpr + Sx/8
    get('sy',D(0));get('src_bpr',D(1));c.word(0xc0c1) # MULU.W D1,D0
    get('sx',D(1));c.shift(1,3);c.alu('add',D(1),0)
    c.word(0xd1c0)                  # ADDA.L D0,A0
    get('dy',D(0));get('dst_bpr',D(1));c.word(0xc0c1)
    get('dx',D(1));c.shift(1,3);c.alu('add',D(1),0)
    c.word(0xd3c0)                  # ADDA.L D0,A1
    get('h',D(4))
    L('copy_row')
    get('byte_count',D(6));get('method',D(0))
    c.imm('cmp',1,D(0));B(7,'words')
    L('byte_loop')
    c.move(POST(0),POST(1),'b')
    c.quick(1,D(6),sub=True);B(6,'byte_loop')
    B(0,'row_done')
    L('words')
    c.shift(6,1)                    # Width/8 -> Width/16
    L('word_loop')
    c.move(POST(0),POST(1),'w')
    c.quick(1,D(6),sub=True);B(6,'word_loop')
    L('row_done')
    get('src_mod',D(0));c.word(0xd1c0) # ADDA.L D0,A0
    get('dst_mod',D(0));c.word(0xd3c0) # ADDA.L D0,A1
    c.quick(1,D(4),sub=True);B(6,'copy_row')
    c.quick(1,D(7),sub=True);B(6,'copy_plane')
    L('ok');c.move(I(1),D(3));B(0,'return')
    L('bad');c.move(I(0),D(3))
    L('return')
    c.raw('4fef0100')               # LEA +256(SP),SP
    c.raw('4cdf77f7')
    c.raw('74004e75')               # D2=0; RTS
    data=c.out()
    assert data[:2]==bytes.fromhex('48e7') and data[-2:]==bytes.fromhex('4e75')
    assert len(data)%2==0
    return data,c.labels

if __name__=='__main__':
    from hashlib import sha256
    data,labels=emit_cblock_copy_core()
    print('M18 CBlock raw CPU/Blitter native core',len(data),'bytes',len(labels),
          'labels',sha256(data).hexdigest(),'(not installed)')
