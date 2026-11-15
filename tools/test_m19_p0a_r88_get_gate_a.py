#!/usr/bin/env python3
"""M19/P0a R88 native 68000/Get AGA Bob Gate A (OS and AMOS calls mocked).

Executes exactly the builder's BOBS code on Unicorn in two separately placed
layouts. Checks 1/4/8 planar capture, unaligned pixels, sorted insert, replace,
mask preservation, Safe, Chip flags, erase/load, allocator failure, ABI.
This is NOT a WinUAE Runtime or real AMOS Compiler test.
"""
from __future__ import annotations
from struct import pack

from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000

from test_m5_generic import DR,AR,AMOS,EXEC,GFX,STACK,STOP
from amos_link_test_support import relocate
from test_m19_p0a_r88_bank_gate_a import SelectMachine,HEAD
from m19_p0a_get_bob_emit import emit_get_bob
from m19_p0a_multi_bob_abk import parse_payload,make_mask,put_image
from build_m19_p0a_r88_get_in_memory import build
from compiler_relocation import unpack_ap20

STATE=0x52000
DB=0x53000
SB=0x54000
BITMAP=0x55000
ARGS=0x58000
STRIDE=12
SCREEN_W=65
SCREEN_H=45
PLANE_START=0x600000
PLANE_GAP=0x40000


def colour(x,y,depth):
    v=((x*17+y*29+(x//3)*5)^0xa7) & ((1<<depth)-1)
    if (x+y)%11==0: v=0
    return v


class CaptureMachine(SelectMachine):
    def __init__(self,binary,layout='interpreted',depth=8,safe=True,chip=True,
                 scratch_fail=False,bank_alloc_fail=False):
        super().__init__(binary,layout=layout)
        self.native,self.labels=emit_get_bob()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.get_entry=self.entry+self.labels['get_entry']
        self.depth=depth
        self.safe=safe
        self.chip=chip
        self.scratch_fail=scratch_fail
        self.bank_alloc_fail=bank_alloc_fail
        self.screen_planes=[PLANE_START+p*PLANE_GAP for p in range(depth)]
        self.planes=list(self.screen_planes)
        self.plane_size=STRIDE*SCREEN_H
        self.waits=0
        self.chip_calls=0
        self.scratch_allocs=0
        self.scratch_frees=0
        self.scratch_live={}
        self.next_scratch=0xa20000
        self.uc.mem_write(AMOS+0x1c8,pack('>I',STATE))
        self.put(STATE+0,0x5a000)
        self.put(STATE+8,GFX)
        self.put(STATE+12,SCREEN_W)
        self.put(STATE+16,SCREEN_H)
        self.put(STATE+28,depth)
        self.put(STATE+32,DB)
        self.put(DB,SB)
        self.put(DB+4,SB)
        self.put(DB+8,0)
        self.put(DB+12,0x5b000)
        self.put(DB+20,1 if safe else 0)
        self.put(SB,BITMAP)
        self.uc.mem_write(BITMAP,pack('>HHBBH',STRIDE,SCREEN_H,0,depth,0))
        for p,addr in enumerate(self.screen_planes):
            self.put(BITMAP+8+4*p,addr)
            data=bytearray([0x8e]*(STRIDE*SCREEN_H))
            for y in range(SCREEN_H):
                for x in range(SCREEN_W):
                    off=y*STRIDE+(x>>3)
                    bit=0x80>>(x&7)
                    if colour(x,y,depth)&(1<<p): data[off]|=bit
                    else:data[off]&=~bit
            self.uc.mem_write(addr,bytes(data))
        self.plane_writes=0
        self.uc.mem_write(GFX-228,b'\x4e\x75')
        for off in (-534,-684,-690,-372):
            self.uc.mem_write(EXEC+off,b'\x4e\x75')

    def _os_return(self,result):
        self.uc.reg_write(DR[0],result & 0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000)
        self.uc.reg_write(AR[1],0xbad100)
        self._rts()

    def os_call(self,uc,address,size,user):
        if address==EXEC-534:
            ptr=self.a(1)
            self.chip_calls+=1
            first=(PLANE_START<=ptr<PLANE_START+(self.depth-1)*PLANE_GAP+self.plane_size)
            return self._os_return(2 if first and self.chip else (1 if ptr>=0x50000 else 0))
        if address==EXEC-684:
            size=self.d(0)
            self.scratch_allocs+=1
            if self.scratch_fail:
                return self._os_return(0)
            assert size>=32 and size<=0x1000000
            ptr=self.next_scratch
            self.next_scratch+=(size+15)&~15
            assert self.next_scratch<0xb00000,'scratch overlaps AMOS bank heap'
            assert self.d(1)==0x10001
            self.uc.mem_write(ptr,bytes(size))
            self.scratch_live[ptr]=size
            return self._os_return(ptr)
        if address==EXEC-690:
            ptr=self.a(1)
            assert ptr in self.scratch_live,hex(ptr)
            del self.scratch_live[ptr]
            self.scratch_frees+=1
            return self._os_return(0)
        if address==EXEC-372:
            return self._os_return(0 if not self.safe else 0x5b100)
        if address==GFX-228:
            self.waits+=1
            return self._os_return(0)
        raise AssertionError('unexpected OS LVO '+hex(address))

    def service(self,uc,address,size,user):
        if self.bank_alloc_fail and self.targets.get(address)=='Lst.Cree':
            self.alloc_fail=True
        return super().service(uc,address,size,user)

    def run_get(self,image_id,x1,y1,x2,y2,*,limit=9000000):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,value in enumerate((x2,y1,x1,image_id)):
            self.put(ARGS+4*i,value)
        self.uc.reg_write(DR[3],y2&0xffffffff)
        old={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.get_entry,STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('68000 Get AGA Bob error',str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),
                (image_id,x1,y1,x2,y2),self.calls[-8:])) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,'stack not restored'
        for r,v in old.items():
            if r in (DR[2],DR[3]):continue
            if r==AR[3]:
                assert self.uc.reg_read(r)==v+16,'5-arg GetP stack consumption'
            else:assert self.uc.reg_read(r)==v,('bad ABI register',r)
        assert self.d(2)==0
        assert self.d(3) in (0,1)
        assert not self.scratch_live,'scratch leak'
        assert self.plane_writes==0,'Get wrote to screen Chip planes'
        return self.d(3)

    def bank_payload(self,n):
        node=self.find(n)
        if not node: return None
        size=self.get(node+4)-16
        return bytes(self.uc.mem_read(node+24,size))

    def install_payload(self,n,payload):
        node=self.install_bank(n)
        assert len(payload)<0x1000
        self.put(node+4,16+len(payload))
        self.uc.mem_write(node+24,payload)
        return node


def check_image(m,n,image_id,x1,y1,x2,y2):
    b=parse_payload(m.bank_payload(n))
    img=b.image(image_id)
    assert (img.width,img.height,img.depth)==(x2-x1+1,y2-y1+1,m.depth)
    assert img.mask is None
    for y in range(img.height):
        for x in range(img.width):
            assert img.colour(x,y)==colour(x+x1,y+y1,m.depth),\
                ('pixel mismatch',x,y,image_id,img.colour(x,y),colour(x+x1,y+y1,m.depth))
    return b


def main():
    binary,meta=build()
    assert binary==build()[0]
    assert meta['commands']==80 and meta['entries']==90
    parts=unpack_ap20(binary)[1]
    native,labels=emit_get_bob()
    assert parts[88].endswith(native) # R88 BOBS + Bank Select + Get Capture
    capture=native[labels['get_entry']:]
    m=CaptureMachine(binary)
    dis=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
             .disasm(m.uc.mem_read(m.get_entry,len(capture)),m.get_entry))
    assert sum(x.size for x in dis)==len(capture),'invalid 68000 capture opcodes'
    assert not any(x.mnemonic.startswith('dc.') for x in dis)
    cases=0
    for layout in ('interpreted','compiled'):
        for depth in (1,4,8):
            m=CaptureMachine(binary,layout,depth)
            assert m.run_select(10)==1
            for n,rect in ((1,(0,0,0,0)),(3,(3,5,19,19)),(2,(4,7,40,14))):
                assert m.run_get(n,*rect)==1,(depth,layout,n,
                    {'calls':m.calls[-9:],'chip_calls':m.chip_calls,
                     'waits':m.waits,'scratch_allocs':m.scratch_allocs,
                     'scratch_frees':m.scratch_frees,'state_ptr':m.get(AMOS+0x1c8),
                     'active_bank':m.get(m.entry+m.labels['bank_active_state']),
                     'active_ptr':m.get(m.entry+m.labels['bank_active_state']+4)})
                check_image(m,10,n,*rect)
                cases+=1
            imgs=parse_payload(m.bank_payload(10)).images
            assert tuple(x.image_id for x in imgs)==(1,2,3)
            original1=imgs[0].planes;original3=imgs[2].planes
            assert m.run_get(2,16,0,46,12)==1
            b=check_image(m,10,2,16,0,46,12)
            assert b.image(1).planes==original1 and b.image(3).planes==original3
            assert m.scratch_allocs==m.scratch_frees
            cases+=1
        # Existing independent mask, hotspot, and colour zero remain unchanged.
        m=CaptureMachine(binary,layout,4)
        pixels=bytes(colour(x,y,4) for y in range(8) for x in range(17))
        old=put_image(m.bank_payload(10) if m.find(10) else __import__('m19_p0a_multi_bob_abk').empty_bank(),
                      1,17,8,4,pixels)
        masked=make_mask(old,1,0)
        m.install_payload(10,masked)
        assert m.run_select(10)==1
        assert m.run_get(2,7,9,23,16)==1
        b=parse_payload(m.bank_payload(10))
        assert b.image(1).mask==parse_payload(masked).image(1).mask
        assert b.image(2).mask is None
        cases+=1
        for kwargs in ({'scratch_fail':True},{'bank_alloc_fail':True},
                       {'safe':False},{'chip':False}):
            m=CaptureMachine(binary,layout,8,**kwargs)
            assert m.run_select(10)==1
            before=m.bank_payload(10)
            assert m.run_get(1,2,2,18,7)==0,kwargs
            assert m.bank_payload(10)==before
            assert m.scratch_allocs==m.scratch_frees or kwargs.get('scratch_fail')
            cases+=1
        # Errors before reading native Chip buffer.
        for args in ((0,0,0,0,0),(4097,0,0,0,0),(1,0,0,65,1),
                     (1,0,0,1,45),(1,5,5,4,5),(1,0,7,3,6),
                     (1,-1,0,0,0)):
            m=CaptureMachine(binary,layout,8)
            assert m.run_select(10)==1
            before=m.bank_payload(10)
            assert m.run_get(*args)==0,args
            assert m.bank_payload(10)==before
            cases+=1
        # Erase/reload invalidates an old selected AMOS bank reference.
        m=CaptureMachine(binary,layout,8)
        assert m.run_select(10)==1
        original=m.find(10)
        m.put(HEAD,0)
        m.install_bank(10)
        assert m.find(10)!=original
        before=m.bank_payload(10)
        assert m.run_get(1,0,0,0,0)==0
        assert m.bank_payload(10)==before
        cases+=1
    print('M19 P0a GET AGA BOB Gate A 68000 PASS',cases,
          'scenarios, layouts interpreted & Compiler-style, SHA256',meta['sha256'],
          'size',meta['size'],'no dist/ WinUAE/ real Compiler writes')


if __name__=='__main__':main()
