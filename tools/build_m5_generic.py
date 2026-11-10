"""Generic ILBM candidate, based exclusively on runtime reference R5 0.4.6.

Shared helpers are emitted locally in both AP20 entries: no cross-entry BSR
dependency on compiler extraction. Their source and contracts are identical.
Every helper takes A5=context, returns D0 (1 success, 0 error), modifies CCR,
and preserves D1-D7/A0-A6 including A5. No other register survives by accident.
The decoder additionally reads context.WRITE; Inspect never writes a bitmap.
Public entries preserve the R5 integer ABI: D3=result, D2=0, GetP unchanged.
"""
from pathlib import Path
import argparse
import hashlib
import json
from audit_ap20 import parse, inspect as audit
from m68k_emit import Code,D,A,M,POST,I,w,l

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.6_M52R5.Lib'
BASE_SHA='33092d2affbc8fd1d74762cc56cb50d465b34ef71677bfaaa10b408a70cc3715'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.5.0_GENERIC_R1.Lib'
OUT_SHA='b9bcf0efc444edc6d284988feabebcc33cd7ad88b21f1231ff155380f1b5941a'
# Stack-owned context: no hidden persistent state or changes to the R5 state.
STATE,STR,FIELD,CSTR,DOS,FH,FORM,SIZE,BMHD,CMAP,NC,BODY,BS,MODE,W,H,DEPTH,MASK,COMP,RB,BITMAP,STRIDE,SCREEN,RAWMODE,HEADER,WRITE = range(0,104,4)
HEADER=104  # twelve bytes, disjoint from WRITE and every metadata long
PTABLE=96
CONTEXT_SIZE=128

def ctx(off): return M(5,off)
def zero(c,reg): c.move(I(0),D(reg))
def fail_if(c,cc): c.branch(cc,'fail_'+c.current)
def begin(c,name):
    c.current=name; c.label(name); c.raw('48e77ffa')
def end(c,name):
    c.move(I(1),D(0)); c.branch(0,'end_'+name)
    c.label('fail_'+name); zero(c,0)
    c.label('end_'+name); c.raw('4cdf5ffe'); c.tst(D(0)); c.raw('4e75')
def invoke(c,name): c.branch(1,name); c.tst(D(0)); c.branch(7,'failure')

def read_file(c):
    """Input STR; output owned CSTR/DOS/FH/FORM/SIZE; cleanup owns failures."""
    begin(c,'read_file')
    c.move(ctx(STR),A(2)); zero(c,4); c.move(POST(2),D(4),'w'); c.tst(D(4)); fail_if(c,7)
    c.move(D(4),D(0)); c.quick(1,D(0)); c.move(I(0x10001),D(1)); c.raw('2c780004'); c.call_os(-684)
    c.tst(D(0)); fail_if(c,7); c.move(D(0),ctx(CSTR)); c.move(D(0),A(1))
    c.label('name_loop'); c.move(POST(2),POST(1),'b'); c.quick(1,D(4),True); c.branch(6,'name_loop')
    c.lea(1,'dosname'); zero(c,0); c.raw('2c780004'); c.call_os(-552)
    c.tst(D(0)); fail_if(c,7); c.move(D(0),ctx(DOS)); c.move(D(0),A(6))
    c.move(ctx(CSTR),D(1)); c.move(I(1005),D(2)); c.call_os(-30)
    c.tst(D(0)); fail_if(c,7); c.move(D(0),ctx(FH))
    c.move(D(0),D(1)); c.move(A(5),D(2)); c.imm('add',HEADER,D(2)); c.move(I(12),D(3)); c.call_os(-42)
    c.imm('cmp',12,D(0)); fail_if(c,6)
    c.imm('cmp',0x464f524d,ctx(HEADER)); fail_if(c,6)
    c.imm('cmp',0x494c424d,ctx(HEADER+8)); fail_if(c,6)
    c.move(ctx(HEADER+4),D(4)); c.imm('cmp',4,D(4)); fail_if(c,5)
    # DOS Read length is signed LONG; reject overflow before allocation/read.
    c.imm('cmp',0x7ffffff7,D(4)); fail_if(c,2); c.quick(8,D(4)); c.move(D(4),ctx(SIZE))
    c.move(D(4),D(0)); c.move(I(0x10001),D(1)); c.raw('2c780004'); c.call_os(-684)
    c.tst(D(0)); fail_if(c,7); c.move(D(0),ctx(FORM)); c.move(D(0),A(2))
    for off in (0,4,8): c.move(ctx(HEADER+off),M(2,off))
    c.move(ctx(FH),D(1)); c.move(A(2),D(2)); c.imm('add',12,D(2)); c.move(D(4),D(3)); c.imm('sub',12,D(3))
    c.move(D(3),D(4)); c.move(ctx(DOS),A(6)); c.call_os(-42); c.alu('cmp',D(4),0); fail_if(c,6)
    end(c,'read_file')

def inspect_file(c):
    """Input FORM/SIZE; output validated metadata; no system calls or writes to image."""
    begin(c,'inspect')
    c.move(ctx(FORM),A(0)); c.move(ctx(SIZE),D(7)); c.imm('sub',12,D(7)); c.move(A(0),D(0)); c.imm('add',12,D(0)); c.move(D(0),A(0))
    c.label('scan'); c.tst(D(7)); c.branch(7,'scan_done'); c.imm('cmp',8,D(7)); fail_if(c,5)
    c.move(POST(0),D(3)); c.move(POST(0),D(2)); c.quick(8,D(7),True)
    c.alu('cmp',D(7),2); fail_if(c,2)
    c.move(D(2),D(1)); c.imm('and',1,D(1)); c.alu('add',D(2),1); c.alu('cmp',D(7),1); fail_if(c,2)
    c.alu('sub',D(1),7)
    for kind in ('BMHD','CMAP','CAMG','BODY'):
        c.imm('cmp',int.from_bytes(kind.encode(),'big'),D(3)); c.branch(7,'chunk_'+kind)
    c.branch(0,'advance')
    for kind,off,sz in (('BMHD',BMHD,20),('CMAP',CMAP,None),('BODY',BODY,None)):
        c.label('chunk_'+kind); c.tst(ctx(off)); fail_if(c,6)
        if sz: c.imm('cmp',sz,D(2)); fail_if(c,6)
        c.move(A(0),ctx(off))
        if kind=='CMAP': c.move(D(2),ctx(NC))
        if kind=='BODY': c.move(D(2),ctx(BS))
        c.branch(0,'advance')
    c.label('chunk_CAMG'); c.tst(ctx(MODE)); fail_if(c,6)
    c.imm('cmp',4,D(2)); fail_if(c,6)
    # MODE holds a presence flag until scan_done, including an explicit CAMG=0.
    c.move(I(1),ctx(MODE)); c.move(M(0),ctx(RAWMODE))
    c.label('advance'); c.move(A(0),D(0)); c.alu('add',D(1),0); c.move(D(0),A(0)); c.branch(0,'scan')
    c.label('scan_done')
    for off in (BMHD,CMAP,BODY,BS): c.tst(ctx(off)); fail_if(c,7)
    c.move(ctx(BMHD),A(0))
    for src,dst,size in ((0,W,'w'),(2,H,'w'),(8,DEPTH,'b'),(9,MASK,'b'),(10,COMP,'b')):
        zero(c,0); c.move(M(0,src),D(0),size); c.move(D(0),ctx(dst))
    for off in (W,H,DEPTH): c.tst(ctx(off)); fail_if(c,7)
    c.imm('cmp',8,ctx(DEPTH)); fail_if(c,2)
    c.imm('cmp',2,ctx(MASK)); fail_if(c,2)
    c.imm('cmp',1,ctx(COMP)); fail_if(c,2)
    c.move(ctx(NC),D(0)); c.tst(D(0)); fail_if(c,7); c.imm('cmp',768,D(0)); fail_if(c,2)
    c.raw('80fc0003'); c.move(D(0),D(1)); c.raw('4841'); c.tst(D(1),'w'); fail_if(c,6)
    c.imm('and',0xffff,D(0)); c.move(D(0),ctx(NC))
    c.move(ctx(W),D(0)); c.imm('add',15,D(0)); c.shift(0,4); c.shift(0,1,True); c.move(D(0),ctx(RB))
    c.move(ctx(RAWMODE),D(0)); c.move(D(0),D(1)); c.imm('and',0xffff0000,D(1)); c.branch(6,'extended_camg')
    c.imm('and',0x8efd,D(0)); c.branch(0,'mode_validated')
    c.label('extended_camg'); c.move(D(0),D(1)); c.imm('and',0x1000,D(1)); fail_if(c,7)
    c.label('mode_validated'); c.move(D(0),ctx(MODE))
    c.move(D(0),D(1)); c.imm('and',0x400,D(1)); fail_if(c,6) # dual playfield has distinct layout
    c.move(D(0),D(1)); c.imm('and',0x800,D(1)); c.branch(7,'not_ham')
    c.imm('and',0x80,D(0)); fail_if(c,6)
    c.imm('cmp',6,ctx(DEPTH)); c.branch(7,'ham_ok'); c.imm('cmp',8,ctx(DEPTH)); fail_if(c,6)
    c.label('ham_ok'); c.branch(0,'mode_done')
    c.label('not_ham'); c.imm('and',0x80,D(0)); c.branch(7,'mode_done')
    c.imm('cmp',6,ctx(DEPTH)); fail_if(c,6)
    c.label('mode_done'); end(c,'inspect')

def validate_screen(c):
    """Input STATE + metadata; output BITMAP/STRIDE/SCREEN, no writes to screen."""
    begin(c,'validate_screen')
    c.move(ctx(STATE),A(2)); c.move(A(2),D(0)); c.tst(D(0)); fail_if(c,7)
    c.move(M(2),D(0)); c.tst(D(0)); fail_if(c,7); c.move(D(0),ctx(SCREEN))
    c.tst(M(2,8)); fail_if(c,7)
    for stateoff,off in ((12,W),(16,H),(28,DEPTH)):
        c.move(M(2,stateoff),D(0)); c.alu('cmp',ctx(off),0); fail_if(c,6)
    c.move(M(2,24),D(0)); c.move(ctx(MODE),D(1))
    # Compare full monitor ID when supplied; default-monitor CAMG compares mode bits.
    c.move(D(1),D(2)); c.imm('and',0xffff0000,D(2)); c.branch(6,'compare_mode')
    c.imm('and',0x8efd,D(0))
    c.label('compare_mode'); c.alu('cmp',D(1),0); fail_if(c,6)
    c.move(M(2,32),A(3)); c.move(A(3),D(0)); c.tst(D(0)); fail_if(c,7)
    c.tst(M(3,8)); c.branch(7,'front_zero'); c.move(M(3),A(0)); c.branch(0,'have_sb')
    c.label('front_zero'); c.move(M(3,4),A(0))
    c.label('have_sb'); c.move(A(0),D(0)); c.tst(D(0)); fail_if(c,7)
    c.move(M(0),A(3)); c.move(A(3),D(0)); c.tst(D(0)); fail_if(c,7); c.move(D(0),ctx(BITMAP))
    zero(c,0); c.move(M(3),D(0),'w'); c.alu('cmp',ctx(RB),0); fail_if(c,5); c.move(D(0),ctx(STRIDE))
    zero(c,0); c.move(M(3,2),D(0),'w'); c.alu('cmp',ctx(H),0); fail_if(c,5)
    zero(c,0); c.move(M(3,5),D(0),'b'); c.alu('cmp',ctx(DEPTH),0); fail_if(c,6)
    c.move(A(3),D(0)); c.quick(8,D(0)); c.move(D(0),A(0)); c.move(ctx(DEPTH),D(1))
    c.label('validate_planes'); c.move(POST(0),D(0)); c.tst(D(0)); fail_if(c,7)
    c.imm('cmp',0xffffffff,D(0)); fail_if(c,7); c.quick(1,D(1),True); c.branch(6,'validate_planes')
    end(c,'validate_screen')

def decode_body(c):
    """Input BODY/BS, metadata, WRITE=0 preflight or 1 store to validated bitmap.
    Every input packet and output row is checked in both passes. Mask rows consumed.
    """
    begin(c,'decode')
    c.move(ctx(BODY),A(0)); c.move(A(0),D(0)); c.alu('add',ctx(BS),0); c.move(D(0),A(2))
    zero(c,4); zero(c,3)
    c.label('row'); zero(c,5)
    c.move(ctx(BITMAP),A(3)); c.move(A(3),D(0)); c.quick(8,D(0)); c.move(D(0),A(4))
    c.label('plane'); c.move(ctx(RB),D(6)); c.move(I(0),A(6))
    c.alu('cmp',ctx(DEPTH),5); c.branch(4,'packet'); c.tst(ctx(WRITE)); c.branch(7,'packet')
    c.move(POST(4),D(0)); c.alu('add',D(3),0); c.move(D(0),A(6))
    c.label('packet'); c.tst(ctx(COMP)); c.branch(7,'raw_row')
    c.move(A(0),D(0)); c.alu('cmp',A(2),0); fail_if(c,4)
    zero(c,1); c.move(POST(0),D(1),'b'); c.imm('cmp',128,D(1)); c.branch(7,'packet'); c.branch(2,'repeat')
    c.quick(1,D(1)); c.move(D(1),D(2)); c.branch(0,'literal')
    c.label('raw_row'); c.move(D(6),D(1)); c.move(D(1),D(2))
    c.label('literal'); c.alu('cmp',D(6),1); fail_if(c,2)
    c.move(A(2),D(0)); c.alu('sub',A(0),0); c.alu('cmp',D(1),0); fail_if(c,5)
    c.alu('sub',D(1),6)
    c.label('literal_loop'); c.move(POST(0),D(0),'b'); c.move(A(6),D(7)); c.tst(D(7)); c.branch(7,'literal_skip')
    c.move(D(0),POST(6),'b')
    c.label('literal_skip'); c.quick(1,D(2),True); c.branch(6,'literal_loop'); c.branch(0,'row_progress')
    c.label('repeat'); c.move(I(257),D(2)); c.alu('sub',D(1),2)
    c.alu('cmp',D(6),2); fail_if(c,2); c.alu('sub',D(2),6)
    c.move(A(0),D(0)); c.alu('cmp',A(2),0); fail_if(c,4); c.move(POST(0),D(0),'b')
    c.label('repeat_loop'); c.move(A(6),D(7)); c.tst(D(7)); c.branch(7,'repeat_skip'); c.move(D(0),POST(6),'b')
    c.label('repeat_skip'); c.quick(1,D(2),True); c.branch(6,'repeat_loop')
    c.label('row_progress'); c.tst(D(6)); c.branch(6,'packet')
    c.quick(1,D(5)); c.move(ctx(DEPTH),D(0)); c.imm('cmp',1,ctx(MASK)); c.branch(6,'no_mask'); c.quick(1,D(0))
    c.label('no_mask'); c.alu('cmp',D(0),5); c.branch(5,'plane')
    c.alu('add',ctx(STRIDE),3); c.quick(1,D(4)); c.alu('cmp',ctx(H),4); c.branch(5,'row')
    c.label('tail'); c.move(A(0),D(0)); c.alu('cmp',A(2),0); c.branch(7,'decoded')
    c.tst(ctx(COMP)); fail_if(c,7); c.imm('cmp',128,POST(0),'b'); fail_if(c,6); c.branch(0,'tail')
    c.label('decoded'); end(c,'decode')

def prepare_palette(c):
    """Input CMAP/NC; output owned PTABLE. Allocated before bitmap writes.
    RGB8 is replicated to RGB32; no large AMOS-stack allocation is assumed.
    """
    begin(c,'prepare_palette')
    c.move(ctx(NC),D(0)); c.move(D(0),D(1)); c.shift(0,1,True); c.alu('add',D(1),0); c.shift(0,2,True); c.quick(8,D(0))
    c.move(I(0x10001),D(1)); c.raw('2c780004'); c.call_os(-684); c.tst(D(0)); fail_if(c,7)
    c.move(D(0),ctx(PTABLE)); c.move(D(0),A(1)); c.move(ctx(NC),D(0)); c.raw('4840'); c.move(D(0),POST(1))
    c.move(ctx(CMAP),A(0)); c.move(ctx(NC),D(4)); c.move(D(4),D(0)); c.alu('add',D(4),0); c.alu('add',D(0),4)
    c.label('rgb_loop'); zero(c,0); c.move(POST(0),D(0),'b'); c.move(D(0),D(1)); c.shift(0,8,True); c.alu('or',D(1),0)
    c.move(D(0),D(1)); c.raw('4840'); c.alu('or',D(1),0); c.move(D(0),POST(1)); c.quick(1,D(4),True); c.branch(6,'rgb_loop')
    c.move(I(0),M(1)); end(c,'prepare_palette')

def palette(c):
    """Input PTABLE/SCREEN; output exact CMAP via LoadRGB32, then WaitTOF.
    All CMAP indices, including upper pens, are explicitly written.
    """
    begin(c,'palette')
    c.move(ctx(PTABLE),A(1)); c.move(ctx(SCREEN),D(0)); c.imm('add',44,D(0)); c.move(D(0),A(0))
    c.move(ctx(STATE),A(2)); c.move(M(2,8),A(6)); c.call_os(-882); c.call_os(-270)
    end(c,'palette')

def cleanup(c):
    """Input resource context; frees all acquired resources, including partial I/O."""
    begin(c,'cleanup')
    c.tst(ctx(FH)); c.branch(7,'no_file'); c.move(ctx(DOS),A(6)); c.move(ctx(FH),D(1)); c.call_os(-36)
    c.label('no_file')
    for field,name in ((PTABLE,'palette_table'),(FORM,'form'),(CSTR,'name')):
        c.tst(ctx(field)); c.branch(7,'no_'+name); c.move(ctx(field),A(1)); c.raw('2c780004'); c.call_os(-690); c.label('no_'+name)
    c.tst(ctx(DOS)); c.branch(7,'no_dos'); c.move(ctx(DOS),A(1)); c.raw('2c780004'); c.call_os(-414); c.label('no_dos')
    end(c,'cleanup')

def routine(info=False, synchronize=False):
    c=Code(); c.raw('48e7effe')
    c.move(M(5,456),A(0)); c.move(D(3),D(4))
    if info: c.move(POST(3),D(3))
    c.move(D(3),A(1)); c.raw('4fefff80'); c.move(A(7),A(5))
    for off in range(0,CONTEXT_SIZE,4): c.move(I(0),ctx(off))
    c.move(A(0),ctx(STATE)); c.move(A(1),ctx(STR)); c.move(D(4),ctx(FIELD))
    if info: c.imm('cmp',7,ctx(FIELD)); c.branch(2,'failure')
    invoke(c,'read_file'); invoke(c,'inspect')
    if info:
        for field,offset in enumerate((W,H,DEPTH,NC,COMP,RAWMODE,MODE)):
            c.imm('cmp',field,ctx(FIELD)); c.branch(7,'info_'+str(field))
        c.move(I(1),D(3)); c.move(ctx(DEPTH),D(0)); c.label('colors_loop'); c.shift(3,1,True); c.quick(1,D(0),True); c.branch(6,'colors_loop'); c.branch(0,'done')
        for field,offset in enumerate((W,H,DEPTH,NC,COMP,RAWMODE,MODE)):
            c.label('info_'+str(field)); c.move(ctx(offset),D(3)); c.branch(0,'done')
    else:
        invoke(c,'validate_screen'); invoke(c,'decode') # preflight before first bitmap/palette write
        invoke(c,'prepare_palette')
        if synchronize:
            # CPU writes must not race the last SB_COPY_BITMAP blit.
            # A5/context stays live. D0/D1/A0/A1/A2/A6 are scratch here;
            # D3's incoming value is no longer needed. No CCR is consumed.
            c.label('wait_before_cpu_write')
            c.move(ctx(STATE),A(2)); c.move(M(2,8),A(6)); c.call_os(-228)
        c.move(I(1),ctx(WRITE)); invoke(c,'decode'); invoke(c,'palette')
        c.move(I(1),D(3)); c.branch(0,'done')
    c.label('failure'); c.move(I(-1 if info else 0),D(3))
    c.label('done'); c.branch(1,'cleanup'); c.raw('4fef00804cdf7ff774004e75')
    read_file(c); inspect_file(c)
    if not info: validate_screen(c); decode_body(c); prepare_palette(c); palette(c)
    cleanup(c); c.label('dosname'); c.b.extend(b'dos.library\0')
    if len(c.b)&1: c.b.append(0)
    result=c.out()
    return result,c.labels

def patch_open(old):
    """Instruction-aligned patches; a local tag helper follows the old strings.
    Width/height are positive signed WORDs (Intuition NewScreen); planar rows
    need not be multiples of 16. EHB/HAM use their CAMG bits and depth.
    """
    b=bytearray(old)
    def patch(before,after):
        src=bytes.fromhex(before); dst=bytes.fromhex(after); assert len(src)==len(dst)
        assert b.count(src)==1,before; pos=b.index(src); assert pos%2==0; b[pos:pos+len(src)]=dst
    patch('0c84000000a0','0c8400000001')
    patch('0c8400000500','0c8400007fff')
    patch('200402800000000f6600011e','20040280000000004e714e71')
    patch('0c85000000a0','0c8500000001')
    patch('0c8500000200','0c8500007fff')
    # Keep dual-playfield rejection; allow EHB/HAM. PicInfo field 6 supplies
    # the normalized legacy mode; field 5 remains the original file CAMG.
    patch('2207028100000c80','2207028100000400') if bytes.fromhex('2207028100000c80') in b else patch('2007028000000c80','2007028000000400')
    patch('4fefffcc','4fefffc4') # 60-byte taglist includes SA_AutoScroll
    patch('4fef0034','4fef003c')
    # Local helper contract: A1=next tag; writes AutoScroll and TAG_DONE.
    # D0=0 on exit, A1 advanced; preserves D1-D7/A0/A2-A6; CCR Z=1.
    # Same effect on live registers as the replaced TAG_DONE sequence.
    assert b[-4:]==b'GetP'
    target=len(b)-4; pos=b.index(bytes.fromhex('700022c022c0'))
    b[pos:pos+6]=bytes.fromhex('6100')+w(target-(pos+2))+bytes.fromhex('4e71')
    b[-4:]=bytes.fromhex('22fc80000039700122c0700022c022c04e75')+b'GetP'
    return bytes(b)

def build(synchronize=False):
    raw=BASE.read_bytes(); assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw); assert not audit(base)['issues']
    segments=[base.code[s:s+2*n] for s,n in zip(base.starts,base.jumps)]
    original=segments.copy()
    segments[6]=patch_open(segments[6])
    loader,loader_labels=routine(synchronize=synchronize); info,info_labels=routine(True)
    segments[13]=loader+b'GetP'; segments[14]=info
    # Old hidden palette helper remains unchanged but unreachable.
    for i in range(len(segments)):
        if i not in (6,13,14): assert segments[i]==original[i],i
    jumps=[len(s)//2 for s in segments]; code=b''.join(segments)
    title=(b'AMOSPro AGA M5 Generic ILBM R2 0.5.1\0$VER: AMOSPro_AGA 0.5.1\0' if synchronize else
           b'AMOSPro AGA M5 Generic ILBM R1 0.5.0\0$VER: AMOSPro_AGA 0.5.0\0')
    if len(title)&1: title+=b'\0'
    payload=bytearray(l(len(jumps)*2)+l(len(base.tokens))+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(n) for n in jumps)+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload.append(0)
    count=len(payload)//4
    result=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]
    out=parse(result); report=audit(out); assert report['issues']==[]
    assert out.tokens==base.tokens and tuple(out.jumps)==tuple(jumps)
    assert out.code==code
    if not synchronize:
        assert len(result)==6436 and hashlib.sha256(result).hexdigest()==OUT_SHA
    return result,dict(base_sha256=BASE_SHA,sha256=hashlib.sha256(result).hexdigest(),size=len(result),
                      jumps=jumps,modified_segments=[6,13,14],unchanged_segments=[i for i in range(len(segments)) if i not in (6,13,14)],
                      loader_labels=loader_labels,info_labels=info_labels,ap20_issues=report['issues'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--promote',action='store_true'); args=parser.parse_args()
    if args.promote:
        parser.error('R1 rejected after runtime colour regression; keep current R5. See docs/GENERIC_R1_RUNTIME_REGRESSION.md')
    result,report=build(); assert build()[0]==result
    DEST.write_bytes(result)
    (ROOT/'docs/GENERIC_BUILD.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if args.promote:
        # Promotion is explicit and only after the executable validation suite.
        from test_m5_generic import run
        run()
        (ROOT/'dist/AMOSPro_AGA.Lib').write_bytes(result)
    print(DEST.name,len(result),report['sha256'])
