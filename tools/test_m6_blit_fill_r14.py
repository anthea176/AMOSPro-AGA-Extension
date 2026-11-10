#!/usr/bin/env python3
"""M6/R14: deterministic CPU 68000 and bitmap bitplane-fill checks.

Unicorn/graphics.library call hooks are simulation, never WinUAE validation.
Run from the repository root after installing capstone/unicorn versions from CI.
"""
from struct import pack
from unicorn.m68k_const import *
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000

from ap20_utils import split,digest
from audit_ap20 import inspect,parse
from build_m6_blit_fill_r14 import (build,emit_fill,BASE,BASE_SHA256,
                                    LAST_GOOD,LAST_GOOD_SHA256,ENTRY)
from test_m6_blit_copy_r13 import CopyMachine
from test_m5_generic import (Machine,CODE,GFX,STATE,AMOS,DB,SB,BITMAP,
                             STACK,STOP,DR,AR)


class FillMachine(CopyMachine):
    def __init__(self,raw,width=320,height=256,depth=8,front=0,fail_plane=None):
        super().__init__(raw,width,height,depth,front)
        self.fill_calls=[]
        self.fail_plane=fail_plane

    def perform_pending(self):
        if self.pending is None:
            return
        plane,x,y,w,h,value=self.pending
        after=bytearray(self.uc.mem_read(self.planes[plane],self.plane_size))
        for py in range(y,y+h):
            for px in range(x,x+w):
                byte_index=py*self.stride+(px>>3)
                bit=1<<(7-(px&7))
                if value: after[byte_index] |= bit
                else: after[byte_index] &= 255^bit
        self.uc.mem_write(self.planes[plane],bytes(after))
        self.pending=None

    def os_call(self,uc,address,size,user):
        if address==GFX-30:
            assert self.a(0)==self.a(1)==self.expected_bitmap
            assert self.a(2)==0,'TempA must be NULL'
            x,y,dx,dy,w,h=[self.d(i) for i in range(6)]
            assert x==dx and y==dy,(x,y,dx,dy)
            assert 0<=x and 0<=y and w>0 and h>0
            assert x+w<=self.meta['width'] and y+h<=self.meta['height']
            minterm=self.d(6)&255; mask=self.d(7)&255
            assert minterm in (0x00,0xF0),hex(minterm)
            assert mask and mask&(mask-1)==0,hex(mask)
            plane=mask.bit_length()-1
            assert plane<self.meta['depth']
            assert self.pending is None,'Missing WaitBlit between bitplanes'
            self.fill_calls.append((plane,x,y,w,h,minterm))
            if plane==self.fail_plane:
                result=0
            else:
                self.pending=(plane,x,y,w,h,minterm==0xF0)
                result=1
            uc.reg_write(DR[0],result)
            uc.reg_write(DR[1],0xDEADBEEF)
            uc.reg_write(AR[0],0xBAD000)
            uc.reg_write(AR[1],0xBAD100)
            pc=self.get(self.a(7))
            uc.reg_write(AR[7],self.a(7)+4)
            uc.reg_write(UC_M68K_REG_PC,pc)
            return
        if address==GFX-228:
            assert self.pending is not None,'WaitBlit with no pending bitmap op'
            self.waits+=1
            self.perform_pending()
        Machine.os_call(self,uc,address,size,user)

    def run_fill(self,x,y,w,h,pen):
        for i,reg in enumerate(DR):self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]):self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],0x58000)
        for i,value in enumerate((h,w,y,x)):self.put(0x58000+4*i,value)
        self.uc.reg_write(DR[3],pen&0xFFFFFFFF)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY],STOP,count=250000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,'CPU SP unbalanced'
        for reg,old in saved.items():
            if reg in (DR[2],DR[3],AR[3]):continue
            assert self.uc.reg_read(reg)==old,(reg,old,self.uc.reg_read(reg))
        assert self.d(2)==0,'AMOS integer-result type must be zero'
        assert self.a(3)==0x58000+16,'GetP stack must consume 4 longs'
        assert self.pending is None
        return self.d(3)


def expected_fill(before,x,y,w,h,pen,plane,stride):
    after=bytearray(before)
    for py in range(y,y+h):
        for px in range(x,x+w):
            bi=py*stride+(px>>3); bit=1<<(7-(px&7))
            if pen & (1<<plane):after[bi] |= bit
            else:after[bi] &= 255^bit
    return bytes(after)


def run():
    raw,report=build()
    assert build()[0]==raw,'builder not reproducible'
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    t13,seg13,_=split(BASE.read_bytes())
    t14,seg14,_=split(raw)
    assert len(seg13)==20 and len(seg14)==21
    assert seg14[:19]==seg13[:19],'R13 AP20 entries 0..18 changed'
    assert seg14[19]==seg13[19]+b'GetP','R13 Copy must be byte-identical'
    assert seg14[20]==emit_fill()[0]
    audit=inspect(parse(raw));assert not audit['issues']
    rows=[r for r in audit['tokens'] if r['name']=='aga blit fill']
    assert len(rows)==1 and rows[0]['function']==ENTRY
    assert rows[0]['signature']=='00,0,0,0,0'
    assert any(x['index']==ENTRY and x['getp'] for x in audit['parameter_checks'])
    asm,labels=emit_fill()
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    decoded=list(dis.disasm(asm,0))
    assert sum(x.size for x in decoded)==len(asm)
    boundaries={i.address for i in decoded}
    assert all(offset in boundaries for offset in labels.values())
    assert all(i.mnemonic not in ('dc.w','illegal') for i in decoded)
    assert b'WaitBlit' not in asm

    count=0
    for depth in (1,2,4,8):
        pens=sorted({0,1,(1<<depth)//2,(1<<depth)-1})
        for front in (0,1):
            for pen in pens:
                x,y,w,h=(11,7,67,31) if front==0 else (129,151,79,23)
                m=FillMachine(raw,depth=depth,front=front)
                before=m.snapshot()
                assert m.run_fill(x,y,w,h,pen)==1,(depth,front,pen)
                assert len(m.fill_calls)==m.waits==depth
                assert [record[0] for record in m.fill_calls]==list(range(depth))
                assert [record[-1] for record in m.fill_calls]==[
                    0xF0 if (pen>>p)&1 else 0 for p in range(depth)]
                for plane in range(depth):
                    assert m.snapshot()[plane]==expected_fill(before[plane],x,y,w,h,
                                                              pen,plane,m.stride)
                count+=1

    for args in ((-1,0,10,10,1),(0,-1,10,10,1),
                 (0,0,0,10,1),(0,0,10,0,1),
                 (315,10,10,10,1),(10,250,10,10,1),
                 (0,0,-1,10,1),(0,0,10,-1,1),
                 (0,0,10,10,-1),(0,0,10,10,256),
                 (0,0,10,10,0x7fffffff),
                 (0x7fffffff,0,10,10,1)):
        m=FillMachine(raw,depth=8);before=m.snapshot()
        assert m.run_fill(*args)==0,args
        assert not m.fill_calls and m.waits==0 and m.snapshot()==before
        count+=1
    for depth in (1,2,4):
        m=FillMachine(raw,depth=depth)
        before=m.snapshot()
        assert m.run_fill(10,10,21,15,1<<depth)==0
        assert not m.fill_calls and before==m.snapshot()
        count+=1

    for case in ('screen','gfx','dbstate','width','height','depth',
                 'short_stride','short_rows','bad_plane_null','bad_plane_minus1',
                 'no_sb','no_bitmap'):
        m=FillMachine(raw,depth=4)
        bm=BITMAP+0x100
        if case=='screen':m.put(STATE+0,0)
        elif case=='gfx':m.put(STATE+8,0)
        elif case=='dbstate':m.put(STATE+32,0)
        elif case=='width':m.put(STATE+12,0x10000)
        elif case=='height':m.put(STATE+16,0)
        elif case=='depth':m.put(STATE+28,9)
        elif case=='short_stride':m.uc.mem_write(bm,pack('>H',2))
        elif case=='short_rows':m.uc.mem_write(bm+2,pack('>H',1))
        elif case=='bad_plane_null':m.put(bm+8+4*2,0)
        elif case=='bad_plane_minus1':m.put(bm+8+4*2,0xffffffff)
        elif case=='no_sb':m.put(DB+4,0)
        else:m.put(SB+0x100,0)
        before=m.snapshot()
        assert m.run_fill(12,20,25,20,5)==0,case
        assert not m.fill_calls and m.waits==0 and m.snapshot()==before
        count+=1

    m=FillMachine(raw,depth=8,fail_plane=3)
    assert m.run_fill(10,10,19,11,55)==0
    assert len(m.fill_calls)==4 and m.waits==3
    count+=1
    print('M6 R14 CPU PASS: 68000 GetP +16, SP, ABI, exact fill pixels, '
          'bitplane masks, zero/1 minterms, %d positive/negative scenarios'%count)
    print('M6 R14 candidate',report['size'],'bytes SHA256',report['sha256'])
    print('WinUAE, Compiler, physical AGA: NOT TESTED')


if __name__=='__main__':run()
