#!/usr/bin/env python3
"""P2.8 R88 experimental AP20 test, real 68k CPU, OS/DMA hooks only.

Both interpreter Rbsr and separately relocated Compiler V2 paths execute
M19 P2.8 independent-alpha AGPC AP20 wrapper + M18 Blitter native core.
NO WinUAE/AMOS Compiler execution, no installed library, no real DMA/FPS.
"""
from __future__ import annotations

from random import Random
from struct import pack,unpack_from

from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR,UC_CPU_M68K_M68020
from unittest.mock import patch

from compiler_relocation import unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from amos_link_test_support import relocate
from m16_agapic import pack_image
from m16_agapic_v2 import pack_image_v2
from m19_p28_agapic_planar_cache import (
    cache_from_agapic,parse_cache,FLAG_HAS_MASK,FLAG_READY,
)
from m19_p28_agpc_ap20_emit import emit_agpc_ap20,GETADR_MARKER
from build_m19_p28_r88_in_memory import build,CACHE_PUBLIC,GROUP_BOBS
from test_m16_capture import CaptureMachine,NEW_CODE
from test_m16_image_draw_r45 import BANK,ARGS
from test_m5_generic import GFX,EXEC,AMOS,AR,DR,STACK,STOP,SCREEN

WIDTH,HEIGHT=65,43
MODE_ID=0x00021000
RNG=Random(0x88A62026)
PIXELS=bytes(0 if (x+y)%7==0 else ((x*7+y*13)&255)
             for y in range(16) for x in range(16))
ALPHA=bytes(0 if (x+y)%13==0 or (x*3+y*5)%11==0 else 1
            for y in range(16) for x in range(16))
assert any(p==0 and a for p,a in zip(PIXELS,ALPHA))
assert any(p!=0 and not a for p,a in zip(PIXELS,ALPHA))
V1=pack_image(16,16,8,PIXELS,ALPHA)
PAL=bytes((3*i+7)&255 for i in range(768))
V2=pack_image_v2(16,16,8,PIXELS,PAL,MODE_ID,ALPHA)
CACHES=[cache_from_agapic(V1),cache_from_agapic(V2)]


class AgpcMachine(CaptureMachine):
    def __init__(self,binary,*,cache=CACHES[0],front=0,pending=0,
                 safe_ready=True,chip=True,screen_mode_id=MODE_ID):
        with patch('test_m5_generic.UC_CPU_M68K_M68000',UC_CPU_M68K_M68020):
            super().__init__(binary=binary,width=WIDTH,height=HEIGHT,depth=8,
                             front=front,pending=pending,safe_ready=safe_ready)
        self.payload=cache
        self.uc.mem_write(BANK,cache)
        self.put(BANK-20,len(cache)+16)
        self.put(BANK-16,11)
        self.uc.mem_write(BANK-12,b'\x00\x03')
        self.uc.mem_write(BANK-8,b'AGPCACHE')
        self.banks={11:BANK}
        self.is_chip=chip
        self.screen_mode_id=screen_mode_id
        self.gfx_calls=[]
        for disp in (-198,-606,-636,-228,-792):
            self.uc.mem_write(GFX+disp,b'\x4e\x75')

    def os_call(self,uc,address,size,user):
        if address==EXEC-534:
            loc=self.a(1)
            inside=BANK-24<=loc<BANK+len(self.payload)
            kind=(3 if self.is_chip else 1) if inside else 0
            self.type_calls+=1
            self.os_calls.append(('TypeOfMem',loc,kind))
            self._ret(kind)
            return
        if address==GFX-792:
            assert self.a(0)==SCREEN+44
            self.gfx_calls.append(('GetVPModeID',self.screen_mode_id))
            self._ret(self.screen_mode_id)
            return
        if address==GFX-198:
            rp=self.a(1)
            uc.mem_write(rp,bytes(128))
            self.gfx_calls.append(('InitRastPort',rp))
            self._ret(0)
            return
        if address in (GFX-606,GFX-636):
            masked=address==GFX-636
            bmp=self.a(0);rp=self.a(1)
            assert self.get(rp+4)==self.expected_bitmap,'front accidentally selected'
            assert unpack_from('>HH',bytes(uc.mem_read(bmp,4)))==(2,16)
            assert bytes(uc.mem_read(bmp+5,1))==bytes([8])
            srcplanes=[self.get(bmp+8+4*i) for i in range(8)]
            slot=srcplanes[0]-32
            assert slot==BANK+72,(hex(slot),'wrong cache alpha pointer')
            assert srcplanes==[slot+32+32*i for i in range(8)]
            sx,sy,dx,dy,w,h,minterm=(self.d(i) for i in range(7))
            assert 0<=sx<16 and 0<=sy<16 and sx+w<=16 and sy+h<=16
            assert 0<=dx<WIDTH and 0<=dy<HEIGHT and 1<=w<=16 and 1<=h<=16
            assert dx+w<=WIDTH and dy+h<=HEIGHT
            assert minterm==(0xe0 if masked else 0xc0)
            if masked: assert self.a(2)==slot
            self.gfx_calls.append(('masked' if masked else 'opaque',sx,sy,dx,dy,w,h))
            for row in range(h):
                for col in range(w):
                    px=sx+col;py=sy+row
                    bit=0x80>>(px&7)
                    if masked:
                        vis=unpack_from('>H',bytes(uc.mem_read(slot+2*py,2)))[0]
                        if not(vis&(0x8000>>px)):continue
                    for plane in range(8):
                        v=bytes(uc.mem_read(srcplanes[plane]+2*py+(px>>3),1))[0]
                        target=self.planes[plane]+(dy+row)*self.stride+((dx+col)>>3)
                        dbit=0x80>>((dx+col)&7)
                        current=bytes(uc.mem_read(target,1))[0]
                        uc.mem_write(target,bytes(((current|dbit) if v&bit else (current&(~dbit&255)),)))
            self._ret(0)
            return
        if address==GFX-228:
            assert self.gfx_calls and self.gfx_calls[-1][0] in ('masked','opaque')
            self.gfx_calls.append(('WaitBlit',))
            self._ret(0)
            return
        super().os_call(uc,address,size,user)


def oracle(before,x,y,mode):
    out=[bytearray(p) for p in before]
    stride=((WIDTH+15)//16)*2
    for sy in range(16):
        ty=y+sy
        if not 0<=ty<HEIGHT:continue
        for sx in range(16):
            tx=x+sx
            if not 0<=tx<WIDTH:continue
            index=sy*16+sx
            if mode==1 and ALPHA[index]==0:continue
            value=PIXELS[index]
            pos=ty*stride+(tx>>3)
            bit=0x80>>(tx&7)
            for p in range(8):
                if value&(1<<p):out[p][pos]|=bit
                else:out[p][pos]&=~bit&255
    return out


def one_case(binary,*,layout='interpreted',cache=CACHES[0],front=0,
             pending=0,safe_ready=True,chip=True,screen_mode_id=MODE_ID,
             bank=11,x=1,y=2,mode=1,expect_ok=True,mutation=None):
    m=AgpcMachine(binary,cache=cache,front=front,pending=pending,
                  safe_ready=safe_ready,chip=chip,screen_mode_id=screen_mode_id)
    if mutation:mutation(m)
    src_before=bytes(m.uc.mem_read(BANK,len(cache)))
    _,parts,_=unpack_ap20(binary)
    assert len(parts)==88
    if layout=='interpreted':
        entry=NEW_CODE+sum(len(v) for v in parts[:CACHE_PUBLIC])
    elif layout=='compiled':
        code_base=0x1b8000
        entry=0x1b7000
        m.uc.mem_write(code_base,relocate(parts[GROUP_BOBS],code_base,
                                          {GROUP_BOBS:code_base},m.uc))
        m.uc.mem_write(entry,relocate(parts[CACHE_PUBLIC],entry,
                                      {GROUP_BOBS:code_base},m.uc))
    else:
        raise ValueError('bad layout')
    before=m.snapshot()
    for k,reg in enumerate(DR):m.uc.reg_write(reg,0x1200+k)
    for k,reg in enumerate(AR[:7]):m.uc.reg_write(reg,0x40000+k*256)
    m.uc.reg_write(AR[5],AMOS)
    m.uc.reg_write(AR[3],ARGS)
    for k,v in enumerate((y,x,bank)):
        m.put(ARGS+k*4,v&0xffffffff)
    m.uc.reg_write(DR[3],mode&0xffffffff)
    saved={r:m.uc.reg_read(r) for r in DR+AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR,0x2000)
    m.uc.reg_write(AR[7],STACK)
    m.put(STACK,STOP)
    try:m.uc.emu_start(entry,STOP,count=2000000)
    except Exception as exc:
        raise AssertionError(('R88 AGPC wrapper CPU exception',layout,x,y,mode,
                              repr(exc),hex(m.uc.reg_read(UC_M68K_REG_PC)),
                              m.main_calls,m.os_calls[-7:],m.gfx_calls[-6:])) from exc
    assert m.uc.reg_read(UC_M68K_REG_PC)==STOP,'no RTS'
    assert m.a(7)==STACK+4 and m.a(3)==ARGS+12,'AP20 stack/A3 mismatch'
    assert (m.d(2),m.d(3))==(0,int(expect_ok)),('wrong result',layout,x,y,mode,m.d(2),m.d(3),m.gfx_calls[-5:])
    for reg,value in saved.items():
        if reg not in (DR[2],DR[3],AR[3]):
            assert m.uc.reg_read(reg)==value,('register clobbered',reg)
    assert all(bytes(m.uc.mem_read(p,m.plane_size))==v
               for p,v in zip(m.frontplanes,m.front_before)),'front modified'
    assert m.alloc_count==m.free_count==m.reserve_count==m.erase_count==0
    assert bytes(m.uc.mem_read(BANK,len(cache)))==src_before,'source cache mutated'
    if expect_ok:
        expected=oracle(before,x,y,mode)
        assert [bytearray(v) for v in m.snapshot()]==expected,('pixels differ',layout,x,y,mode)
        visible=-16<x<WIDTH and -16<y<HEIGHT
        assert sum(z[0]=='WaitBlit' for z in m.gfx_calls)==int(visible)
        assert sum(z[0]=='InitRastPort' for z in m.gfx_calls)==int(visible)
        if cache==CACHES[1] and visible:
            assert sum(z[0]=='GetVPModeID' for z in m.gfx_calls)==1
    else:
        assert before==m.snapshot(),'invalid operation wrote pixels'
        assert not any(z[0] in ('masked','opaque') for z in m.gfx_calls)
    return 1


def main():
    binary,info=build()
    assert build()[0]==binary,'not deterministic'
    assert info['entries']==88 and info['commands']==78
    _,parts,_=unpack_ap20(binary)
    new,_=emit_agpc_ap20()
    assert parts[GROUP_BOBS].endswith(new)
    assert len(parts[GROUP_BOBS])-len(new)==5220, 'R87 BOBS unit not retained'
    assert new.count(GETADR_MARKER)==1
    readable=new.replace(GETADR_MARKER,bytes.fromhex('4eb900030000'))
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(readable,0))
    assert sum(i.size for i in ins)==len(new),'invalid 68k instructions'
    cases=0
    for layout in ('interpreted','compiled'):
        for cache in CACHES:
            for mode in (0,1):
                for x,y in ((0,0),(1,7),(7,3),(15,0),(16,16),(-15,-1),
                            (-1,2),(49,7),(64,42),(65,1),(-16,5),(17,42)):
                    cases+=one_case(binary,layout=layout,cache=cache,
                                    mode=mode,x=x,y=y,front=(x&1))
        for config in (
            dict(bank=4),dict(bank=10),dict(mode=2),dict(mode=-1),
            dict(x=32768),dict(y=-32769),dict(chip=False),
            dict(cache=cache_from_agapic(pack_image(16,16,8,PIXELS))),
            dict(cache=cache_from_agapic(pack_image(17,16,8,PIXELS+b'\x00'*16,ALPHA+b'\x00'*16))),
            dict(cache=CACHES[1],screen_mode_id=MODE_ID+1),
            dict(pending=1,safe_ready=False),
            dict(mutation=lambda m:m.uc.mem_write(BANK-8,b'FICHIP8 ')),
            dict(mutation=lambda m:m.put(BANK-20,len(m.payload)+17)),
            dict(mutation=lambda m:m.uc.mem_write(BANK+6,b'\x00\x02')),
            dict(mutation=lambda m:m.uc.mem_write(BANK+32,bytes(4))),
        ):
            cases+=one_case(binary,layout=layout,expect_ok=False,**config)
        cases+=one_case(binary,layout=layout,pending=3,safe_ready=True)
        cases+=one_case(binary,layout=layout,x=65,y=0,pending=1,
                        safe_ready=False,expect_ok=True)
    print('P2.8 R88 IN-MEMORY AP20 NATIVE GATE A PASS:',cases,
          '68020 interpreter+Compiler V2 emulation; independent zero-alpha; Safe/TypeOfMem/WaitBlit')
    print('R87 candidate, R84 LAST_GOOD, WinUAE Runtime/Compiled NOT CHANGED OR TESTED FOR R88')

if __name__=='__main__':
    main()
