#!/usr/bin/env python3
"""M6 R14 0.7.1 - add Aga Blit Fill on top of validated R13 Copy.

R13 must match its archived SHA256; no existing R13 code segment may change,
except the trailing AP20 GetP separator on entry 19. R14 introduces entry 20.
The candidate is dist/AMOSPro_AGA.Lib, with a versioned identical archive.
LAST_GOOD and the archived R13/R12 bases are never written.
"""
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m68k_emit import Code, D, A, M, POST, PRE, I

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib'
DEST = ROOT / 'dist/AMOSPro_AGA.Lib'
ARCHIVE = ROOT / 'dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib'
LAST_GOOD = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
BASE_SHA256 = 'c71cab88d2294ed70c019f546d6c60ac72c278c1b625ded07d0aa6603e50a0cf'
LAST_GOOD_SHA256 = '0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41'
VERSION = '0.7.1'
ENTRY = 20
AMOS_STATE_PTR = 0x01C8
SCREEN, GFX, WIDTH, HEIGHT, DEPTH, DBSTATE = 0, 8, 12, 16, 28, 32
LVO_BLTBITMAP, LVO_WAITBLIT = -30, -228


def emit_fill():
    """Aga Blit Fill(x,y,w,h,pen) -> 1 or 0, back buffer only.

    D3=pen; successive (A3)+ = h,w,y,x; A5=AMOS base.
    D3=result, D2=0; A3 advances by exactly 16, SP balances.
    All D0,D1,D4-D7/A0-A2/A4-A6 restored. No restricted waits.

    Destination bitmap depth=1..8. Validate coordinates, pen range, physical
    dimensions and ALL destination plane pointers before any graphics call.
    For each bitplane use BltBitMap with a *single-bit write mask* and
    the source-ignoring minterm $F0 (set) or $00 (clear). These are exactly
    the four-channel-safe minterms specified by the graphics.library autodoc.
    WaitBlit after every plane, since the next BltBitMap is order-dependent.
    """
    c = Code()
    c.raw('48e7efee')                 # proven R13/R9 preserve set, excludes A3
    c.move(POST(3), D(5))            # height
    c.move(POST(3), D(4))            # width
    c.move(POST(3), D(1))            # y
    c.move(POST(3), D(0))            # x

    c.move(M(5, AMOS_STATE_PTR), A(4))
    c.move(A(4), D(6)); c.tst(D(6)); c.branch(7,'bad')
    c.move(M(4, SCREEN), D(6)); c.tst(D(6)); c.branch(7,'bad')
    c.move(M(4, DBSTATE), A(2))
    c.move(A(2), D(6)); c.tst(D(6)); c.branch(7,'bad')
    c.move(M(4, GFX), A(6))
    c.move(A(6), D(6)); c.tst(D(6)); c.branch(7,'bad')

    # Signed bounds and all nonzero extents; no clipping and no overflow.
    for reg in (0,1,3):
        c.tst(D(reg)); c.branch(11,'bad')  # BMI (pen >=0)
    for reg in (4,5):
        c.tst(D(reg)); c.branch(15,'bad')  # BLE
    for off in (WIDTH,HEIGHT):
        c.move(M(4,off),D(6)); c.tst(D(6)); c.branch(15,'bad')
        c.imm('cmp',32767,D(6)); c.branch(14,'bad')
    c.move(M(4,WIDTH),D(6)); c.alu('sub',D(4),6)
    c.tst(D(6)); c.branch(11,'bad')
    c.alu('cmp',D(6),0); c.branch(14,'bad')
    c.move(M(4,HEIGHT),D(6)); c.alu('sub',D(5),6)
    c.tst(D(6)); c.branch(11,'bad')
    c.alu('cmp',D(6),1); c.branch(14,'bad')

    # DB front index (+8); use the inactive ScreenBuffer.sb_BitMap.
    c.tst(M(2,8)); c.branch(7,'front_zero')
    c.move(M(2,0),A(0)); c.branch(0,'have_sb')
    c.label('front_zero'); c.move(M(2,4),A(0))
    c.label('have_sb')
    c.move(A(0),D(6)); c.tst(D(6)); c.branch(7,'bad')
    c.move(M(0,0),A(0))
    c.move(A(0),D(6)); c.tst(D(6)); c.branch(7,'bad')

    # Verify bitmap stride/rows/depth before access. Clear destination
    # bitplanes cannot be NULL or 0xffffffff (AmigaOS permits those in SRC).
    c.move(I(0),D(6)); c.move(M(0,0),D(6),'w')
    c.shift(6,3,left=True)
    c.alu('cmp',M(4,WIDTH),6); c.branch(13,'bad')
    c.move(I(0),D(6)); c.move(M(0,2),D(6),'w')
    c.alu('cmp',M(4,HEIGHT),6); c.branch(13,'bad')
    c.move(I(0),D(6)); c.move(M(0,5),D(6),'b')
    c.alu('cmp',M(4,DEPTH),6); c.branch(6,'bad')
    c.tst(D(6)); c.branch(15,'bad')
    c.imm('cmp',8,D(6)); c.branch(14,'bad')

    # Check every destination pointer before modifying ANY bitplane.
    c.move(D(6),D(2))
    c.move(A(0),A(1)); c.quick(8,A(1))
    c.label('check_plane')
    c.move(POST(1),D(6))
    c.tst(D(6)); c.branch(7,'bad')
    c.imm('cmp',-1,D(6)); c.branch(7,'bad')
    c.quick(1,D(2),sub=True)
    c.branch(6,'check_plane')

    # Compute 1<<depth (1..256), reject pen >= this limit BEFORE drawing.
    c.move(I(0),D(2)); c.move(M(0,5),D(2),'b')
    c.move(I(1),D(6))
    c.label('compute_limit')
    c.shift(6,1,left=True)
    c.quick(1,D(2),sub=True)
    c.branch(6,'compute_limit')
    c.alu('cmp',D(6),3); c.branch(4,'bad')  # BCC: unsigned pen >= limit

    # Scratch after all pre-validation: [SP] limit, 4(SP) pen.
    # Save bitmap in preserved A4; restore D0/D1/A0/A1 for each OS call.
    c.move(D(3),PRE(7)); c.move(D(6),PRE(7))
    c.move(A(0),A(4))
    c.move(D(0),D(2)); c.move(D(1),D(3))
    c.move(I(1),D(7))
    c.label('plane_loop')
    c.move(M(7,4),D(6))
    c.alu('and',D(7),6)
    c.tst(D(6)); c.branch(7,'plane_clear')
    c.move(I(0xF0),D(6)); c.branch(0,'do_blit')
    c.label('plane_clear'); c.move(I(0),D(6))
    c.label('do_blit')
    c.move(D(2),D(0)); c.move(D(3),D(1))
    c.move(A(4),A(0)); c.move(A(4),A(1))
    c.move(I(0),A(2))                 # TempA=NULL
    c.call_os(LVO_BLTBITMAP)
    c.tst(D(0)); c.branch(7,'blit_failed')
    c.call_os(LVO_WAITBLIT)
    c.shift(7,1,left=True)
    c.alu('cmp',M(7),7)
    c.branch(6,'plane_loop')
    c.move(I(1),D(3)); c.branch(0,'leave_plane_loop')
    c.label('blit_failed'); c.move(I(0),D(3))
    c.label('leave_plane_loop')
    c.quick(8,A(7))                  # exactly discard 2 scratch LONGs
    c.branch(0,'finish')
    c.label('bad'); c.move(I(0),D(3))
    c.label('finish')
    c.raw('4cdf77f7')               # restore saved registers except A3
    c.raw('7400')                   # AMOS integer return D2=0
    c.raw('4e75')                   # RTS
    result=c.out()
    assert len(result)%2==0
    return result,c.labels


def build():
    raw=BASE.read_bytes()
    assert digest(raw)==BASE_SHA256, 'R13 archive missing or modified'
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256, 'LAST_GOOD changed'
    toks,old,_=split(raw)
    assert len(old)==20 and toks.endswith(bytes(6))
    assert old[19][-2:]==bytes.fromhex('4e75')
    code,labels=emit_fill()
    new=list(old)
    new[19]+=b'GetP'               # separator preceding parameterized entry 20
    new.append(code)
    assert new[:19]==old[:19] and new[19]==old[19]+b'GetP'
    new_tokens=toks[:-6]+token('aga blit fill',1,ENTRY,'00,0,0,0,0')+bytes(6)
    title=(b'AMOSPro AGA M6 Blit Fill R14 0.7.1\0'
           b'$VER: AMOSPro_AGA 0.7.1\0')
    if len(title)%2: title+=b'\0'
    binary=b''.join(new)
    payload=(pack('>4I',len(new)*2,len(new_tokens),len(binary),len(title))
             +b'\0\0AP20'+b''.join(pack('>H',len(seg)//2) for seg in new)
             +new_tokens+binary+title+b'\0\0')
    payload+=bytes(-len(payload)%4)
    words=len(payload)//4
    result=(raw[:20]+pack('>I',words)+raw[24:28]+pack('>I',words)
            +payload+raw[-4:])
    audit=inspect(parse(result))
    assert not audit['issues'],audit['issues']
    rows=[row for row in audit['tokens'] if row['name']=='aga blit fill']
    assert len(rows)==1 and (rows[0]['function'],rows[0]['signature'])==(ENTRY,'00,0,0,0,0')
    assert any(x['index']==ENTRY and x['getp'] for x in audit['parameter_checks'])
    tokens,segments,_=split(result)
    assert tokens==new_tokens and segments==new
    return result,dict(version=VERSION,size=len(result),sha256=digest(result),
                       entry=ENTRY,code_size=len(code),labels=labels,
                       runtime_validation='NOT_TESTED')


if __name__=='__main__':
    assert len({BASE.resolve(),DEST.resolve(),ARCHIVE.resolve(),LAST_GOOD.resolve()})==4
    candidate,info=build()
    assert build()[0]==candidate, 'non-reproducible build'
    ARCHIVE.parent.mkdir(parents=True,exist_ok=True)
    ARCHIVE.write_bytes(candidate)
    assert ARCHIVE.read_bytes()==candidate
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    print('M6 R14 historical archive only; active R15 candidate NOT overwritten:',info)
