"""R84 P1 native read-only AGAPIC v1/v2 bank metadata.

API: _VALUE=Aga Bank Image Info(Bank,Field).
  Bank is a live AMOS DATA bank number (5..65535), NOT Start(Bank).
  Fields: 1=Width, 2=Height, 3=Depth, 4=embedded palette count,
          5=DisplayModeID. Fields 4/5 return 0 for v1 (absent).
  Returns -1 for invalid bank/format/field, including corrupt row offsets.
  A valid v2 ModeID must be 1..$FFFFFFFE and is returned bit-exact as a
  32-bit AMOS integer (therefore values >=$80000000 appear negative).

No pixel decoding, screen access, palette changes, allocations, writes or VBL.
The native validator checks row offsets but does not re-decode compressed
RLE streams; Draw/Region retain their own full RLE validation.
"""
from __future__ import annotations
from m68k_emit import Code,D,A,M,POST,I

BANK_LOOKUP=bytes.fromhex('fe11f700031d') # AMOS365 Rjsr Bnk.GetAdr #797
LVO_TYPEOFMEM=-534
MAX_PAYLOAD=0x01000000
F=dict(bank=0,field=4,start=8,length=12,version=16,flags=20,
       width=24,height=28,depth=32,colors=36,table=40,stream=44,
       modeid=48,masked=52)
FRAME=96

def emit_bank_image_info():
    c=Code()
    def b(condition,label): c.branch(condition,label)
    def l(label): c.label(label)
    def fs(reg,name): c.move(reg,M(2,F[name]))
    def fl(name,reg): c.move(M(2,F[name]),reg)
    def u16(off,dst=0):
        c.move(I(0),D(dst))
        c.move(M(0,off),D(dst),'w')
    def fail_if_zero(reg):
        c.move(reg,D(0));c.tst(D(0));b(7,'fail')
    c.raw('48e7efee')                  # AP20 save set (excluding D2/D3/A3)
    c.raw('4fefffa0')                  # -96 SP
    c.move(A(7),A(2))                  # A2 independent of OS/Rjsr stack
    fs(D(3),'field')
    c.move(POST(3),D(7));fs(D(7),'bank')
    c.move(I(-1),D(3))                 # invalid/unsupported sentinel
    fl('field',D(0)); c.imm('cmp',1,D(0)); b(5,'fail')
    c.imm('cmp',5,D(0)); b(2,'fail')
    fl('bank',D(0));c.imm('cmp',5,D(0));b(5,'fail')
    c.imm('cmp',65535,D(0));b(2,'fail')
    c.raw(BANK_LOOKUP.hex())
    fail_if_zero(A(0));fs(A(0),'start')
    c.move(A(0),D(0));c.imm('cmp',24,D(0));b(3,'fail')
    c.imm('and',1,D(0));b(6,'fail')
    fl('start',D(0));c.imm('sub',24,D(0));c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0));b(7,'fail')
    fl('start',A(0))
    c.move(M(0,-16),D(0)); fl('bank',D(1)); c.alu('cmp',D(1),0);b(6,'fail')
    u16(-12);c.tst(D(0));b(7,'native_flags_ok')
    c.imm('and',0xfffd,D(0),'w');c.imm('cmp',1,D(0));b(6,'fail')
    l('native_flags_ok')
    c.move(M(0,-8),D(0));c.imm('cmp',0x41474150,D(0));b(6,'fail')
    c.move(M(0,-4),D(0));c.imm('cmp',0x49432020,D(0));b(6,'fail')
    c.move(M(0,-20),D(0));c.imm('cmp',48,D(0));b(5,'fail')
    c.imm('sub',16,D(0));c.imm('cmp',MAX_PAYLOAD,D(0));b(2,'fail')
    fs(D(0),'length')
    fl('start',D(1));c.alu('add',D(1),0);b(5,'fail')
    c.quick(1,D(0),sub=True);c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0));b(7,'fail')
    fl('start',A(0))
    c.move(M(0),D(0));c.imm('cmp',0x41474150,D(0));b(6,'fail')
    u16(4);c.imm('cmp',0x4943,D(0));b(6,'fail')
    u16(6);c.imm('cmp',1,D(0));b(7,'version_v1')
    c.imm('cmp',2,D(0));b(6,'fail')
    fs(D(0),'version');b(0,'version_done')
    l('version_v1');fs(D(0),'version')
    l('version_done')
    u16(8);fs(D(0),'flags')
    fl('version',D(1));c.imm('cmp',2,D(1));b(7,'flags_v2')
    c.imm('cmp',1,D(0));b(2,'fail')
    b(0,'flags_ok')
    l('flags_v2');c.imm('cmp',2,D(0));b(5,'fail')
    c.imm('cmp',3,D(0));b(2,'fail')
    l('flags_ok')
    c.imm('and',1,D(0));fs(D(0),'masked')
    u16(10);c.imm('cmp',1,D(0));b(6,'fail')
    for off,name in ((12,'width'),(14,'height'),(16,'depth')):
        u16(off);c.tst(D(0));b(7,'fail')
        c.imm('cmp',8 if name=='depth' else 4096,D(0));b(2,'fail')
        fs(D(0),name)
    fl('width',D(0));fl('height',D(1))
    c.word(0xc0c1)                 # MULU.W D1,D0
    c.imm('cmp',0x00400000,D(0));b(2,'fail')
    fl('depth',D(0));fl('masked',D(1));c.alu('add',D(1),0)
    c.shift(0,1,left=True)
    u16(18,1);c.alu('cmp',D(1),0);b(6,'fail')
    c.move(M(0,28),D(0));fl('length',D(1));c.alu('cmp',D(1),0);b(6,'fail')
    fl('version',D(0));c.imm('cmp',2,D(0));b(7,'format_v2')
    c.move(I(0),M(2,F['colors']));c.move(I(0),M(2,F['modeid']))
    c.move(I(32),M(2,F['table']))
    b(0,'format_done')
    l('format_v2')
    fl('length',D(0));c.imm('cmp',64,D(0));b(5,'fail')
    c.move(M(0,32),D(0));c.tst(D(0));b(7,'fail')
    c.imm('cmp',-1,D(0));b(7,'fail');fs(D(0),'modeid')
    fl('depth',D(1));c.move(I(1),D(7))
    l('color_count');c.shift(7,1,left=True)
    c.quick(1,D(1),sub=True);b(6,'color_count')
    fs(D(7),'colors')
    u16(36);c.alu('cmp',D(7),0);b(6,'fail')
    u16(38);c.imm('cmp',1,D(0));b(6,'fail')
    for off in (40,48):
        c.move(M(0,off),D(0));c.imm('cmp',64,D(0));b(6,'fail')
    c.move(D(7),D(1));c.raw('c2fc0003') # MULU.W #3,D1
    c.move(M(0,44),D(0));c.alu('cmp',D(1),0);b(6,'fail')
    for off in (52,56,60): c.tst(M(0,off));b(6,'fail')
    c.imm('add',67,D(1));c.imm('and',0xfffffffc,D(1))
    fs(D(1),'table')
    fl('length',D(0));c.alu('cmp',D(0),1);b(2,'fail')
    # V2 exact RGB24/padding layout; at most three bytes between palette/table.
    c.move(D(1),D(6));c.move(D(7),D(0));c.raw('c0fc0003')
    c.imm('add',64,D(0));c.alu('sub',D(0),6)
    c.tst(D(6));b(7,'padding_done')
    c.move(D(0),D(1));fl('start',D(0))
    c.alu('add',D(0),1);c.move(D(1),A(4))
    l('padding_loop')
    c.tst(POST(4),'b');b(6,'fail')
    c.quick(1,D(6),sub=True);b(6,'padding_loop')
    l('padding_done')
    fl('start',A(0))
    l('format_done')
    fl('table',D(0));c.alu('cmp',M(0,20),0);b(6,'fail')
    fl('height',D(1));c.quick(1,D(1));c.shift(1,2,left=True)
    c.alu('add',D(1),0);b(5,'fail')
    fs(D(0),'stream')
    c.alu('cmp',M(0,24),0);b(6,'fail')
    fl('length',D(1));c.alu('cmp',D(1),0);b(2,'fail')
    # Read-only full offset monotonicity, no compressed pixel decoding.
    fl('start',D(0));fl('table',D(1));c.alu('add',D(1),0)
    c.move(D(0),A(4))
    c.move(POST(4),D(0));fl('stream',D(1));c.alu('cmp',D(1),0);b(6,'fail')
    fl('height',D(6))
    l('row_loop')
    c.move(POST(4),D(1));c.alu('cmp',D(0),1);b(3,'fail')
    fl('length',D(5));c.alu('cmp',D(5),1);b(2,'fail')
    c.move(D(1),D(0))
    c.quick(1,D(6),sub=True);b(6,'row_loop')
    fl('length',D(1));c.alu('cmp',D(1),0);b(6,'fail')
    fl('field',D(0));c.imm('cmp',1,D(0));b(7,'return_width')
    c.imm('cmp',2,D(0));b(7,'return_height')
    c.imm('cmp',3,D(0));b(7,'return_depth')
    c.imm('cmp',4,D(0));b(7,'return_colors')
    fl('modeid',D(3));b(0,'done')
    l('return_width');fl('width',D(3));b(0,'done')
    l('return_height');fl('height',D(3));b(0,'done')
    l('return_depth');fl('depth',D(3));b(0,'done')
    l('return_colors');fl('colors',D(3));b(0,'done')
    l('fail')
    c.move(I(-1),D(3))
    l('done')
    c.raw('4fef0060');c.raw('4cdf77f7');c.raw('74004e75')
    out=c.out()
    assert len(out)&1==0
    assert out.count(BANK_LOOKUP)==1
    return out,dict(c.labels,frame=FRAME,bank_lookup=797)
