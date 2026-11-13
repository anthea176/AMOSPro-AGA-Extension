#!/usr/bin/env python3
"""M18/P5 R62 in-memory AP20 68000 chip-bank/Safe/masked Gfx Gate A.

Runs the full real R62 native routine in both interpretation-dispatcher
and relocated Compiler V2 layouts. Only graphics/Exec services are mocked.
NOT a WinUAE or physical DMA test. No library binary is written/installed.
"""
from random import Random
from struct import pack,unpack_from
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m16_capture import CaptureMachine,NEW_CODE
from test_m16_image_draw_r45 import BANK,ARGS
from test_m5_generic import GFX,EXEC,AMOS,AR,DR,STACK,STOP,DB
from amos_link_test_support import relocate
from compiler_relocation import unpack_ap20
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from m18_ficon16_model import build_bank,parse_bank,draw_cpu
from m18_ficon_chip_cache import empty_payload,stage,parse_cache
from m18_ficon_chip_ap20_emit import (
    emit_ficon_chip_ap20,GETADR_MARKER,ENTRY_INDEX
)
from build_m18_r62_chip_blit import build

WIDTH,HEIGHT=65,43
RNG=Random(0xb11e2026)
ICONS=(
  bytes(256),bytes([255])*256,
  bytes((17*x+3*y)&255 for y in range(16) for x in range(16)),
  bytes(RNG.randrange(256) if (x+y)%3 else 0
        for y in range(16) for x in range(16)),
)
SOURCE=parse_bank(build_bank(ICONS))
CACHE=empty_payload(4)
for i in range(1,5):CACHE=stage(CACHE,SOURCE.raw,i)
assert parse_cache(CACHE).slot(1)

class CacheMachine(CaptureMachine):
    def __init__(self,binary,*,front=0,pending=0,safe_ready=True,
                 cache=CACHE,chip=True):
        super().__init__(binary=binary,width=WIDTH,height=HEIGHT,depth=8,
                         front=front,pending=pending,safe_ready=safe_ready)
        self.payload=cache
        self.uc.mem_write(BANK,cache)
        self.put(BANK-20,len(cache)+16)
        self.put(BANK-16,11)
        self.uc.mem_write(BANK-12,b"\0\3")
        self.uc.mem_write(BANK-8,b"FICHIP8 ")
        self.banks={11:BANK}
        self.is_chip=chip
        self.gfx_calls=[]
        for disp in (-198,-606,-636,-228):
            self.uc.mem_write(GFX+disp,b"\x4e\x75")

    def os_call(self,uc,address,size,user):
        if address==EXEC-534:
            loc=self.a(1)
            inside=BANK-24<=loc<BANK+len(self.payload)
            kind=(3 if self.is_chip else 1) if inside else 0
            self.type_calls+=1
            self.os_calls.append(("TypeOfMem",loc,kind))
            self._ret(kind)
            return
        if address==GFX-198:
            rp=self.a(1)
            self.uc.mem_write(rp,bytes(128))
            self.gfx_calls.append(("InitRastPort",rp))
            self._ret(0)
            return
        if address in (GFX-606,GFX-636):
            masked=address==GFX-636
            bmp=self.a(0)
            rp=self.a(1)
            assert self.get(rp+4)==self.expected_bitmap,"front got blitted"
            assert unpack_from(">HH",bytes(uc.mem_read(bmp,4)))==(2,16)
            assert bytes(uc.mem_read(bmp+5,1))==bytes([8])
            srcplanes=[self.get(bmp+8+4*i) for i in range(8)]
            slot=srcplanes[0]-32
            assert BANK+12<=slot<=BANK+12+3*288
            assert srcplanes==[slot+32+32*i for i in range(8)]
            sx,sy,dx,dy,w,h,mt=(self.d(i) for i in range(7))
            assert 0<=sx<16 and 0<=sy<16 and sx+w<=16 and sy+h<=16
            assert 0<=dx<WIDTH and 0<=dy<HEIGHT
            assert w>=1 and h>=1 and dx+w<=WIDTH and dy+h<=HEIGHT
            assert mt==(0xe0 if masked else 0xc0)
            if masked: assert self.a(2)==slot
            self.gfx_calls.append(("masked" if masked else "opaque",
                                   sx,sy,dx,dy,w,h))
            # Independent per-pixel transfer of *real* source bitmap words.
            for row in range(h):
                for col in range(w):
                    px=sx+col;py=sy+row
                    bit=0x80>>(px&7)
                    if masked:
                        vis=unpack_from(">H",bytes(uc.mem_read(slot+2*py,2)))[0]
                        if not(vis&(0x8000>>px)):continue
                    for plane in range(8):
                        b=bytes(uc.mem_read(srcplanes[plane]+2*py+(px>>3),1))[0]
                        daddr=self.planes[plane]+(dy+row)*self.stride+((dx+col)>>3)
                        dbit=0x80>>((dx+col)&7)
                        current=bytes(uc.mem_read(daddr,1))[0]
                        uc.mem_write(daddr,bytes(((current|dbit) if b&bit else (current&(~dbit&255)),)))
            self._ret(0)
            return
        if address==GFX-228:
            assert self.gfx_calls and self.gfx_calls[-1][0] in ("opaque","masked")
            self.gfx_calls.append(("WaitBlit",))
            self._ret(0)
            return
        super().os_call(uc,address,size,user)

def case(binary,*,layout="interpreted",index=4,x=1,y=1,mode=1,
         front=0,pending=0,safe_ready=True,cache=CACHE,chip=True,
         bank=11,expect_ok=True,mutation=None):
    m=CacheMachine(binary,front=front,pending=pending,safe_ready=safe_ready,
                   cache=cache,chip=chip)
    if mutation:mutation(m)
    cache_before=bytes(m.uc.mem_read(BANK,len(cache)))
    _,parts,_=unpack_ap20(binary)
    assert len(parts)==63
    if layout=="interpreted":
        entry=NEW_CODE+sum(len(v) for v in parts[:ENTRY_INDEX])
    elif layout=="compiled":
        monolith=0x1b8000
        entry=0x1b7000
        m.uc.mem_write(monolith,relocate(parts[-1],monolith,{62:monolith},m.uc))
        m.uc.mem_write(entry,relocate(parts[ENTRY_INDEX],entry,{62:monolith},m.uc))
    else:raise ValueError(layout)
    before=m.snapshot()
    for k,reg in enumerate(DR):m.uc.reg_write(reg,0x1200+k)
    for k,reg in enumerate(AR[:7]):m.uc.reg_write(reg,0x40000+k*256)
    m.uc.reg_write(AR[5],AMOS)
    m.uc.reg_write(AR[3],ARGS)
    for k,v in enumerate((y,x,index,bank)):
        m.put(ARGS+k*4,v&0xffffffff)
    m.uc.reg_write(DR[3],mode&0xffffffff)
    saved={r:m.uc.reg_read(r) for r in DR+AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR,0x2000)
    m.uc.reg_write(AR[7],STACK)
    m.put(STACK,STOP)
    try:m.uc.emu_start(entry,STOP,count=2500000)
    except Exception as exc:
        raise AssertionError(("R62 wrapper CPU fault",layout,index,x,y,mode,
                              repr(exc),hex(m.uc.reg_read(UC_M68K_REG_PC)),
                              m.main_calls,m.os_calls[-10:],m.gfx_calls[-5:])) from exc
    assert m.uc.reg_read(UC_M68K_REG_PC)==STOP,"no RTS"
    assert m.a(7)==STACK+4 and m.a(3)==ARGS+16,"AP20 stack/A3 mismatch"
    assert (m.d(2),m.d(3))==(0,int(expect_ok)),(
        "wrong result",layout,index,x,y,mode,m.d(2),m.d(3),m.gfx_calls[-3:])
    for reg,value in saved.items():
        if reg not in (DR[2],DR[3],AR[3]):
            assert m.uc.reg_read(reg)==value,("clobbered register",reg)
    assert all(bytes(m.uc.mem_read(p,m.plane_size))==v
               for p,v in zip(m.frontplanes,m.front_before)),"modified front"
    assert m.alloc_count==m.free_count==m.reserve_count==m.erase_count==0
    assert bytes(m.uc.mem_read(BANK,len(cache)))==cache_before,"cache source changed during call"
    if expect_ok:
        wanted=[bytearray(p) for p in before]
        draw_cpu(SOURCE,index,x,y,mode,wanted,WIDTH,HEIGHT,m.stride)
        assert [bytearray(p) for p in m.snapshot()]==wanted,(
            "different pixels",layout,index,x,y,mode)
        visible=-16<x<WIDTH and -16<y<HEIGHT
        assert sum(c[0]=="WaitBlit" for c in m.gfx_calls)==int(visible)
        assert sum(c[0]=="InitRastPort" for c in m.gfx_calls)==int(visible)
        assert m.getmsg_calls==int(bool(pending&1) and visible)
    else:
        assert before==m.snapshot(),"invalid call drew"
        assert not any(c[0] in ("opaque","masked") for c in m.gfx_calls)
    return 1

def main():
    binary,info=build()
    assert build()[0]==binary,"not deterministic"
    tok,parts=unwrap_native_parts_v2(binary)
    assert len(parts)==62 and len(tok)>0
    core,labels=emit_ficon_chip_ap20()
    assert parts[ENTRY_INDEX]==core and core.count(GETADR_MARKER)==1
    # Rjsr linker marker is data, not a CPU opcode.
    stripped=core.replace(GETADR_MARKER,bytes.fromhex("4eb900030000"))
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
             .disasm(stripped,0))
    assert sum(t.size for t in ins)==len(core),"invalid 68000 opcodes"
    assert "safe" in labels and "core" in labels and "check_plane" in labels
    assert info["commands"]==56 and info["ap20_entries"]==63

    tests=0
    for layout in ("interpreted","compiled"):
        for mode in (0,1):
            for index in (1,2,3,4):
                for x,y in ((0,0),(1,3),(15,0),(-7,21),(49,2),
                            (64,42),(65,1),(-16,0)):
                    tests+=case(binary,layout=layout,index=index,x=x,y=y,
                                mode=mode,front=index&1)
        for options in (dict(bank=4),dict(bank=10),dict(index=0),
                        dict(index=5),dict(mode=2),dict(mode=-1),
                        dict(x=32768),dict(y=-32769),
                        dict(cache=empty_payload(4)),
                        dict(chip=False),
                        dict(mutation=lambda m:m.uc.mem_write(BANK-8,b"AGAPIC  ")),
                        dict(mutation=lambda m:m.put(BANK-20,len(CACHE)+17)),
                        dict(mutation=lambda m:m.uc.mem_write(
                            BANK+12+3*288,
                            bytes([m.uc.mem_read(BANK+12+3*288,1)[0]^0x80]))),
                        dict(pending=1,safe_ready=False)):
            tests+=case(binary,layout=layout,expect_ok=False,**options)
        tests+=case(binary,layout=layout,pending=3,safe_ready=True)
        tests+=case(binary,layout=layout,x=65,y=0,pending=1,
                    safe_ready=False,expect_ok=True)
    print("M18/R62 CHIP BLIT AP20 GATE A PASS:",tests,
          "real 68000 bank/ABI/graphics OS-hook cases;"
          " interpreter & Compiler V2 relocation; no WinUAE B/C")
    print("R62 remains IN MEMORY only: no dist Lib, no new ASC, no promotion")
if __name__=="__main__":
    main()
