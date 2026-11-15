"""P2.8 experimental AP20 wrapper for an owned AGPC cache bank (not installed).

Proposed signature (function): Aga Cache Blit(CacheBank,X,Y,Mode)
D3=Mode (0 opaque, 1 independent 1-bit alpha); A3->[Y,X,CacheBank].
Only 16x16x8 AGPC **masked** snapshots are supported by the native M18
core: 72-byte AGPC header + 32 alpha bytes + 8*32 colour bytes.

Rejects bad bank/flags/geometry, missing chip storage, wrong v2 ModeID,
unsafe inactive ScreenBuffer, invalid clipping or pointer. Uses the
EXISTING 68000-tested M18/P5 masked Blitter core, no reinterpretation of
mask==OR(colour). This wrapper is not part of R87 and not WinUAE-tested.
"""
from __future__ import annotations

from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr
from m18_ficon16_chip_blit_emit import emit_chip_cache_blit

ENTRY_INDEX=83
GETADR_MARKER=rjsr(main_index('Bnk.GetAdr'))
assert main_index('Bnk.GetAdr')==797
STATE_PTR=0x1c8
LVO_TYPEOFMEM=-534
LVO_GETMSG=-372
LVO_GETVPMODEID=-792
HEADER=72
SLOT=288
TOTAL=HEADER+SLOT
AGPC_MAGIC=0x41475043
AGPC_NAME_SUFFIX=0x41434845
F=dict(mode=0,y=4,x=8,bank=12,base=16,length=20,
       slot=24,scrw=28,scrh=32,bitmap=36)
FRAME=96


def emit_agpc_ap20():
    c=Code()
    B,L=c.branch,c.label
    def ld(key,dest):c.move(M(2,F[key]),dest)
    def st(src,key):c.move(src,M(2,F[key]))
    def uw(reg,offset):
        c.move(I(0),D(reg));c.move(M(0,offset),D(reg),'w')
    def testbank(addr):
        c.move(addr,A(1));c.raw('2c780004') # ExecBase
        c.call_os(LVO_TYPEOFMEM)
        c.tst(D(0));B(7,'reject')

    # Original R87 AP20 preserved register set, D2/D3 result and consumed A3.
    c.raw('48e7efee')
    c.raw('4fefffa0')               # LEA -96(SP),SP
    c.move(A(7),A(2))
    st(D(3),'mode')
    for key in ('y','x','bank'):
        c.move(POST(3),D(7));st(D(7),key)
    c.move(I(0),D(3))
    ld('mode',D(0));c.tst(D(0));B(11,'reject')
    c.imm('cmp',1,D(0));B(14,'reject')
    for key in ('x','y'):
        ld(key,D(0))
        c.imm('cmp',-32768,D(0));B(13,'reject')
        c.imm('cmp',32767,D(0));B(14,'reject')
    ld('bank',D(0))
    c.imm('cmp',5,D(0));B(5,'reject')
    c.imm('cmp',65535,D(0));B(2,'reject')
    c.raw(GETADR_MARKER.hex())
    c.move(A(0),D(5));c.imm('cmp',24,D(5));B(3,'reject')
    c.move(D(5),D(0));c.imm('and',1,D(0));B(6,'reject')
    st(D(5),'base')
    testbank(D(5))
    ld('base',D(5));c.move(D(5),D(0));c.imm('sub',24,D(0))
    testbank(D(0))

    # The entire AGPC snapshot must be exactly 360 bytes, bank-owned.
    c.move(D(5),A(0))
    c.move(M(0,-20),D(4))
    c.imm('cmp',TOTAL+16,D(4));B(6,'reject')
    c.imm('sub',16,D(4))
    st(D(4),'length')
    c.move(D(5),D(0));c.alu('add',D(4),0);B(5,'reject')
    c.quick(1,D(0),sub=True)
    testbank(D(0))
    ld('base',D(5));c.move(D(5),A(0))
    c.move(M(0,-16),D(0))
    ld('bank',D(1));c.alu('cmp',D(1),0);B(6,'reject')
    uw(0,-12)
    # WinUAE can normalize reloaded AMOS DATA bank header flags to zero.
    c.tst(D(0));B(7,'native_bank_flags_ok')
    c.imm('and',0xfffd,D(0),'w')
    c.imm('cmp',1,D(0),'w');B(6,'reject')
    L('native_bank_flags_ok')
    c.move(M(0,-8),D(0));c.imm('cmp',AGPC_MAGIC,D(0));B(6,'reject')
    c.move(M(0,-4),D(0));c.imm('cmp',AGPC_NAME_SUFFIX,D(0));B(6,'reject')

    # Snapshot header strict: AGPC v1, explicitly independent alpha,
    # ready, 16x16x8 stride=2, mask at +72, planes at +104, total=360.
    c.move(M(0,0),D(0));c.imm('cmp',AGPC_MAGIC,D(0));B(6,'reject')
    uw(0,4);c.imm('cmp',1,D(0));B(6,'reject')
    uw(0,6);c.imm('cmp',3,D(0));B(6,'reject')
    uw(0,8);c.imm('cmp',16,D(0));B(6,'reject')
    uw(0,10);c.imm('cmp',16,D(0));B(6,'reject')
    uw(0,12);c.imm('cmp',8,D(0));B(6,'reject')
    uw(0,14);c.imm('cmp',2,D(0));B(6,'reject')
    c.move(M(0,20),D(0));c.imm('cmp',72,D(0));B(6,'reject')
    c.move(M(0,24),D(0));c.imm('cmp',104,D(0));B(6,'reject')
    c.move(M(0,28),D(0));c.imm('cmp',TOTAL,D(0));B(6,'reject')
    c.move(M(0,32),D(0));c.tst(D(0));B(7,'reject')
    c.tst(M(0,36));B(6,'reject')
    # SHA256 in +40..+71 is authoritative only from the host stage model,
    # not re-computed on every native draw. The bank is a snapshot value.
    c.move(D(5),D(0));c.imm('add',HEADER,D(0));B(5,'reject')
    st(D(0),'slot')

    # Validate private inactive AGA ScreenBuffer before touching Safe or DMA.
    c.move(M(5,STATE_PTR),A(4))
    c.move(A(4),D(0));c.tst(D(0));B(7,'reject')
    for off in (0,8,32):
        c.move(M(4,off),D(0));c.tst(D(0));B(7,'reject')
    for off,key in ((12,'scrw'),(16,'scrh')):
        c.move(M(4,off),D(0));c.tst(D(0));B(15,'reject')
        c.imm('cmp',32767,D(0));B(14,'reject');st(D(0),key)
    c.move(M(4,28),D(0));c.imm('cmp',8,D(0));B(6,'reject')

    # Screen.ViewPort ModeID must match cached AGAPIC v2 metadata.
    ld('base',A(0));c.move(M(0,16),D(6))
    c.imm('cmp',-1,D(6));B(6,'check_modeid')
    B(0,'modeid_ok')
    L('check_modeid')
    c.move(M(4,0),D(0));c.imm('add',44,D(0));c.move(D(0),A(0))
    c.move(M(4,8),A(6));c.call_os(LVO_GETVPMODEID)
    c.imm('cmp',-1,D(0));B(7,'reject')
    ld('base',A(0));c.alu('cmp',M(0,16),0);B(6,'reject')
    L('modeid_ok')

    c.move(M(4,32),A(0));c.move(M(0,8),D(0))
    c.tst(D(0));B(7,'front_zero')
    c.imm('cmp',1,D(0));B(6,'reject')
    c.move(M(4,32),A(0));c.move(M(0),A(1));B(0,'have_sb')
    L('front_zero')
    c.move(M(4,32),A(0));c.move(M(0,4),A(1))
    L('have_sb')
    c.move(A(1),D(0));c.tst(D(0));B(7,'reject')
    c.move(M(1),A(0))
    c.move(A(0),D(0));c.tst(D(0));B(7,'reject')
    st(A(0),'bitmap')
    uw(1,0);c.tst(D(1));B(7,'reject')
    c.shift(1,3,left=True)
    c.alu('cmp',M(2,F['scrw']),1);B(13,'reject')
    uw(1,2);c.alu('cmp',M(2,F['scrh']),1);B(13,'reject')
    c.move(I(0),D(1));c.move(M(0,5),D(1),'b')
    c.imm('cmp',8,D(1));B(6,'reject')
    c.move(A(0),A(1));c.quick(8,A(1))
    c.move(I(8),D(0))
    L('check_pointers')
    c.move(POST(1),D(1));c.tst(D(1));B(7,'reject')
    c.imm('cmp',-1,D(1));B(7,'reject')
    c.move(D(1),D(5));c.imm('and',1,D(5));B(6,'reject')
    c.quick(1,D(0),sub=True);B(6,'check_pointers')
    ld('x',D(0));c.alu('cmp',M(2,F['scrw']),0);B(12,'noop')
    c.imm('add',16,D(0));c.tst(D(0));B(15,'noop')
    ld('y',D(0));c.alu('cmp',M(2,F['scrh']),0);B(12,'noop')
    c.imm('add',16,D(0));c.tst(D(0));B(15,'noop')

    # Existing nonblocking Safe pattern, inherited from M18/R63.
    c.move(M(4,32),A(0));c.move(M(0,20),D(0));c.imm('and',1,D(0))
    B(7,'safe')
    c.move(M(0,12),A(0));c.move(A(0),D(0));c.tst(D(0));B(7,'reject')
    c.raw('2c780004');c.call_os(LVO_GETMSG)
    c.tst(D(0));B(7,'reject')
    c.move(M(4,32),A(0));c.move(M(0,20),D(0))
    c.imm('and',0xfffffffe,D(0));c.move(D(0),M(0,20))
    L('safe')
    ld('x',D(0));ld('y',D(1));ld('mode',D(3))
    ld('scrw',D(4));ld('scrh',D(5))
    ld('slot',A(0));ld('bitmap',A(1))
    c.move(M(4,8),A(6))
    B(1,'core')
    B(0,'leave')
    L('noop')
    c.move(I(1),D(3));B(0,'leave')
    L('reject')
    c.move(I(0),D(3))
    L('leave')
    c.raw('4fef0060')
    c.raw('4cdf77f7')
    c.raw('74004e75')
    L('core')
    raw,oldlabels=emit_chip_cache_blit()
    c.raw(raw.hex())
    binary=c.out()
    assert binary.count(GETADR_MARKER)==1
    assert binary[-len(raw):]==raw
    assert len(binary)%2==0 and len(binary)<65534
    return binary,dict(c.labels,core_bytes=len(raw),native_labels=oldlabels)

if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_agpc_ap20()
    print('P2.8 AGPC 16x16x8 IN-MEMORY AP20 WRAPPER',len(raw),sha256(raw).hexdigest(),len(labels))
