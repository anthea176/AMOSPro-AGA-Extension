#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""L1 Gate A: execute actual assembled Back Fill and IFF Load on MC68020.

Two physical pages; real source IFF parsing, both BODY passes and cleanup.
Exec/DOS/graphics calls are modeled (including volatile register clobber).
AP20 BSR.W and absolute JSR represent Runtime/Compiler relocation models,
not real AMOS, WinUAE, Blitter hardware or DMA validation.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from struct import pack, unpack_from

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from audit_ap20 import walk_tokens
from build_m19_p2d_in_memory import build_p2d
from build_m19_p2d_l1_safeport_in_memory import build_l1
from compiler_relocation import RBSR, unpack_ap20

DR=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7]
AR=[UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
EXEC,DOS,GFX=0x20000,0x22000,0x24000
STATE,AMOS,NAME,DB,SB,BM,SCREEN=0x50000,0x51000,0x52000,0x53000,0x54000,0x55000,0x56000
SAFE,DISP,REPLY=0x59000,0x59100,0x59200
CODE,GROUP,STOP,STACK=0x100000,0x400000,0x10000,0xF00000
WIDTH,HEIGHT,ROW_BYTES,STRIDE=17,2,4,6
SIZE=HEIGHT*STRIDE
PEN=0x105


def chunk(tag,payload):
    return tag+pack('>I',len(payload))+payload+(b'\0' if len(payload)&1 else b'')


def fixture(depth,compressed=False,malformed=False):
    rows=[bytes((y*37+p*19+j*11+3)&255 for j in range(ROW_BYTES))
          for y in range(HEIGHT) for p in range(depth)]
    body=b''.join((bytes([ROW_BYTES-1])+row if compressed else row) for row in rows)
    if malformed:
        body=body[:-1]
    bmhd=pack('>HHhhBBBBHBBhh',WIDTH,HEIGHT,0,0,depth,0,int(compressed),0,0,1,1,WIDTH,HEIGHT)
    cmap=bytes((j*17)&255 for j in range(3*(1<<depth)))
    payload=b'ILBM'+chunk(b'BMHD',bmhd)+chunk(b'CAMG',pack('>I',0))+chunk(b'CMAP',cmap)+chunk(b'BODY',body)
    expected=[b''.join(rows[y*depth+p]+b'\xa5'*(STRIDE-ROW_BYTES)
                       for y in range(HEIGHT)) for p in range(depth)]
    return b'FORM'+pack('>I',len(payload))+payload,expected,[v*0x01010101 for v in cmap]


class Machine:
    def __init__(self,image,layout,front,depth,pending,ready_at=None,
                 port_valid=True,compressed=False,malformed=False,fail_alloc=0):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x1000000)
        self.u.mem_write(STOP,b'\x4e\x71')
        tok,parts,_=unpack_ap20(image)
        api={r['name']:r for r in walk_tokens(tok)}
        entries={'back':api['aga back fill']['instruction'],'iff':api['aga iff load']['function']}
        assert entries=={'back':22,'iff':24}
        starts=[]
        at=0
        for p in parts:
            starts.append(at)
            at+=len(p)
        self.entries={}
        if layout=='runtime':
            self.u.mem_write(CODE,b''.join(parts))
        else:
            assert layout=='compiled'
            self.u.mem_write(GROUP,parts[142])
        for n,(name,entry) in enumerate(entries.items()):
            stub=parts[entry]
            assert stub.startswith(RBSR) and stub[6:8]==b'\x4e\x75'
            group,offset=unpack_from('>HH',stub,2)
            assert group==142
            if layout=='runtime':
                address=CODE+starts[entry]
                disp=starts[group]-(starts[entry]+2)
                self.u.mem_write(address,pack('>Hh',0x6100,disp))
            else:
                address=CODE+n*0x100
                self.u.mem_write(address,pack('>HIH',0x4EB9,GROUP,offset)+b'\x4e\x75')
            self.entries[name]=address
        self.front=front
        self.back=1-front
        self.depth=depth
        self.data,self.iff_expected,self.rgb_expected=fixture(depth,compressed,malformed)
        self.ready_at=ready_at
        self.consumed=False
        self.port_valid=port_valid
        self.fail_alloc=fail_alloc
        self.events=[]
        self.safe_calls=0
        self.safe_waits=0
        self.alloc_calls=0
        self.owned={}
        self.heap=0x300000
        self.file_open=False
        self.lib_open=False
        self.cursor=0
        self.palette=None
        self.pending_fill=None
        self.put(4,EXEC)
        self.put(AMOS+456,STATE)
        self.u.mem_write(NAME,b'\0\x08test.iff')
        for off,v in ((0,SCREEN),(8,GFX),(12,WIDTH),(16,HEIGHT),
                      (20,1<<depth),(24,0),(28,depth),(32,DB)):
            self.put(STATE+off,v)
        for off,v in ((0,SB),(4,SB+0x100),(8,front),
                      (12,SAFE if port_valid else 0),(16,DISP),(20,pending)):
            self.put(DB+off,v)
        self.planes=[]
        for page in (0,1):
            bm=BM+page*0x100
            self.put(SB+page*0x100,bm)
            self.u.mem_write(bm,pack('>HHBBH',STRIDE,HEIGHT,0,depth,0))
            addresses=[]
            for p in range(depth):
                addr=0x600000+page*0x10000+p*0x1000+0x10
                addresses.append(addr)
                self.put(bm+8+4*p,addr)
                self.u.mem_write(addr-4,b'PRE!'+b'\xa5'*SIZE+b'END!')
            self.planes.append(addresses)
        for base,offsets in ((EXEC,(-372,-684,-690,-552,-414)),
                             (DOS,(-30,-42,-36)),
                             (GFX,(-198,-234,-228,-882,-270))):
            for off in offsets:
                self.u.mem_write(base+off,b'\x4e\x75')
        self.u.hook_add(UC_HOOK_CODE,self.os_call,begin=0x1f000,end=0x24fff)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.check_write,begin=0x600000,end=0x61ffff)

    def put(self,addr,value):
        self.u.mem_write(addr,pack('>I',value&0xffffffff))

    def get(self,addr):
        return int.from_bytes(self.u.mem_read(addr,4),'big')

    def d(self,i):
        return self.u.reg_read(DR[i])

    def a(self,i):
        return self.u.reg_read(AR[i])

    def safe(self):
        return not self.get(DB+20)&1

    def snapshot(self):
        return tuple(tuple(bytes(self.u.mem_read(p,SIZE)) for p in page) for page in self.planes)

    def check_write(self,uc,access,addr,size,value,ctx):
        assert self.safe(),'UNSAFE CPU bitmap write'
        assert any(p<=addr and addr+size<=p+SIZE for p in self.planes[self.back]),('wrong page/canary',hex(addr))
        assert 'waitblit' in self.events,'CPU bitmap write before WaitBlit'

    def os_call(self,uc,addr,size,ctx):
        result=0
        assert self.a(6) in (EXEC,DOS,GFX)
        if addr==EXEC-372:
            assert self.a(6)==EXEC and self.a(0)==SAFE and self.port_valid and not self.safe()
            self.safe_calls+=1
            self.events.append('getmsg')
            if not self.consumed and self.ready_at is not None and self.safe_waits>=self.ready_at:
                result=REPLY
                self.consumed=True
        elif addr==EXEC-684:
            self.alloc_calls+=1
            if self.alloc_calls!=self.fail_alloc:
                n=self.d(0)
                assert 0<n<0x10000
                result=self.heap
                self.heap+=(n+15)&~15
                self.owned[result]=n
                uc.mem_write(result,bytes(n))
        elif addr==EXEC-690:
            assert self.a(1) in self.owned,'invalid/double FreeVec'
            del self.owned[self.a(1)]
        elif addr==EXEC-552:
            assert bytes(uc.mem_read(self.a(1),12))==b'dos.library\0'
            assert not self.lib_open
            self.lib_open=True
            result=DOS
        elif addr==EXEC-414:
            assert self.a(1)==DOS and self.lib_open
            self.lib_open=False
        elif addr==DOS-30:
            assert self.a(6)==DOS and self.lib_open and self.d(2)==1005
            assert bytes(uc.mem_read(self.d(1),9))==b'test.iff\0'
            self.file_open=True
            self.cursor=0
            result=7
        elif addr==DOS-42:
            assert self.file_open and self.d(1)==7
            data=self.data[self.cursor:self.cursor+self.d(3)]
            uc.mem_write(self.d(2),data)
            self.cursor+=len(data)
            result=len(data)
        elif addr==DOS-36:
            assert self.file_open and self.d(1)==7
            self.file_open=False
        elif addr==GFX-198:
            assert self.a(1) in self.owned
            self.events.append('initrast')
        elif addr==GFX-234:
            assert self.safe(),'UNSAFE SetRast'
            assert self.a(6)==GFX and self.a(1) in self.owned
            assert self.get(self.a(1)+4)==BM+self.back*0x100,'wrong bitmap'
            assert self.pending_fill is None
            self.events.append('setrast')
            self.pending_fill=self.d(0)&255
        elif addr==GFX-228:
            self.events.append('waitblit')
            if self.pending_fill is not None:
                for p,a in enumerate(self.planes[self.back]):
                    uc.mem_write(a,bytes([255 if self.pending_fill&(1<<p) else 0])*SIZE)
                self.pending_fill=None
        elif addr==GFX-882:
            assert self.safe(),'palette changed on refused Safe'
            assert self.a(0)==SCREEN+44 and self.a(1) in self.owned
            ptr=self.a(1)
            assert self.get(ptr)==(1<<self.depth)<<16
            self.palette=[self.get(ptr+4+j*4) for j in range(3*(1<<self.depth))]
            assert self.get(ptr+4+12*(1<<self.depth))==0
            self.events.append('loadrgb')
        elif addr==GFX-270:
            if not self.safe():
                self.safe_waits+=1
                self.events.append('waitsafe')
            else:
                self.events.append('waittof')
        else:
            raise AssertionError(('unexpected OS vector',hex(addr)))
        ret=self.get(self.a(7))
        uc.reg_write(AR[7],self.a(7)+4)
        uc.reg_write(DR[0],result)
        uc.reg_write(DR[1],0xdeadbeef)
        uc.reg_write(AR[0],0xbad000)
        uc.reg_write(AR[1],0xbad100)
        uc.reg_write(UC_M68K_REG_PC,ret)

    def run(self,name):
        for i,r in enumerate(DR):
            self.u.reg_write(r,0x12340000+i)
        for i,r in enumerate(AR[:7]):
            self.u.reg_write(r,0x40000+i*0x100)
        self.u.reg_write(AR[5],AMOS)
        self.u.reg_write(DR[3],NAME if name=='iff' else PEN)
        saved={r:self.u.reg_read(r) for r in DR+AR[:7]}
        self.u.reg_write(UC_M68K_REG_SR,0x2000)
        self.u.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.u.emu_start(self.entries[name],STOP,count=2000000)
        assert self.u.reg_read(UC_M68K_REG_PC)==STOP,'instruction budget / bad return'
        assert self.a(7)==STACK+4,'stack imbalance'
        for r,v in saved.items():
            if name=='iff' and r in (DR[2],DR[3]):
                continue
            assert self.u.reg_read(r)==v,('ABI',name,r,hex(v))
        assert not self.owned and not self.file_open and not self.lib_open,'resource leak'
        assert self.pending_fill is None
        for page in self.planes:
            for p in page:
                assert bytes(self.u.mem_read(p-4,4))==b'PRE!'
                assert bytes(self.u.mem_read(p+SIZE,4))==b'END!'
        if name=='iff':
            assert self.d(2)==0
            return self.d(3)
        # Back Fill has no public numeric result.
        return None

    def expected(self,name):
        if name=='iff':
            return tuple(self.iff_expected)
        return tuple(bytes([255 if PEN&(1<<p) else 0])*SIZE for p in range(self.depth))


def check(m,name,pending,success,calls,waits,*,alloc_fail=False):
    before=m.snapshot()
    returned=m.run(name)
    if name=='iff':
        assert returned==int(success)
    assert m.snapshot()[m.front]==before[m.front],'front corrupted'
    after=m.snapshot()[m.back]
    assert after==(m.expected(name) if success else before[m.back]),('back',name,pending,success)
    assert m.safe_calls==calls and m.safe_waits==waits,(name,m.events)
    expected_flags=pending&~1 if (success or alloc_fail) else pending
    assert m.get(DB+20)==expected_flags,'Safe/Disp changed incorrectly'
    assert m.get(DB+16)==DISP and m.get(DB+8)==m.front
    if name=='iff':
        assert m.palette==(m.rgb_expected if success else None)
    else:
        assert m.events.count('setrast')==int(success)
    if success:
        assert 'waitblit' in m.events
        if pending&1:
            draw='setrast' if name=='back' else 'waitblit'
            assert m.events.index('getmsg')<m.events.index(draw)
    return 1


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',type=Path,required=True)
    image,meta=build_l1(p.parse_args().vasm)
    base,_=build_p2d()
    n=0
    for layout in ('runtime','compiled'):
        for front in (0,1):
            for depth in (2,8):
                for name in ('back','iff'):
                    # Safe clear/Disp-only, ready Safe, permanent timeout, no port.
                    for flags,ready,port,ok,calls,waits in (
                        (0,None,True,True,0,0),(2,None,True,True,0,0),
                        (1,0,True,True,1,0),(3,0,True,True,1,0),
                        (3,None,True,False,4 if name=='back' else 1,3 if name=='back' else 0),
                        (3,0,False,False,0,0)):
                        m=Machine(image,layout,front,depth,flags,ready,port,
                                  compressed=bool(front))
                        n+=check(m,name,flags,ok,calls,waits)
                    # Existing unguarded behavior preserved byte/pixel exact
                    # when no Safe acquisition is required.
                    original=Machine(base,layout,front,depth,0,compressed=bool(front))
                    n+=check(original,name,0,True,0,0)
                for latency in (1,2,3):
                    m=Machine(image,layout,front,depth,3,latency)
                    n+=check(m,'back',3,True,latency+1,latency)
                # Preflight rejection must not acquire Safe or touch planes/RGB.
                bad=Machine(image,layout,front,depth,3,0,malformed=True,compressed=True)
                n+=check(bad,'iff',3,False,0,0)
                alloc=Machine(image,layout,front,depth,3,0,fail_alloc=3)
                n+=check(alloc,'iff',3,False,0,0)
                alloc=Machine(image,layout,front,depth,3,0,fail_alloc=1)
                n+=check(alloc,'back',3,False,1,0,alloc_fail=True)
            # A first refused IFF can be retried when Safe arrives. Then a
            # Back Fill on the same page needs no second GetMsg.
            m=Machine(image,layout,front,2,3,None)
            n+=check(m,'iff',3,False,1,0)
            m.ready_at=0
            before=m.snapshot()
            assert m.run('iff')==1 and m.safe_calls==2 and m.get(DB+20)==2
            assert m.snapshot()[m.front]==before[m.front]
            assert m.snapshot()[m.back]==m.expected('iff')
            m.run('back')
            assert m.safe_calls==2 and m.snapshot()[m.back]==m.expected('back')
            n+=2
    print('P2D L1 MC68020 Gate A PASS',n,'cases including both AP20 relocation models',meta)
    print('OS services simulated; WinUAE B, real Compiler C and physical D NOT TESTED')


if __name__=='__main__':
    main()
