#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P0d private integrated AGBO -> staged Chip -> Safe AGA Blitter Gate A.

Native instructions run under Unicorn MC68020 with two distinct layouts.
AMOS/Exec/graphics/Intuition services and DMA are MOCKED. This is NOT
a real WinUAE Runtime or an AMOS Compiler executable.
"""
from __future__ import annotations

from struct import pack, unpack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from test_m5_generic import DR, AR, AMOS, EXEC, GFX, STACK, STOP
from test_m19_p0a_r88_get_gate_a import STRIDE, SCREEN_W, SCREEN_H
from test_m19_p0d_bank_image_resolve_native import prepared, ResolverMachine
from m19_p0d_safe_bank_blit_emit import emit_safe_bank_blit
from m19_p0d_bank_image_resolve_emit import emit_bank_image_resolve
from m19_p0d_private_blit_emit import emit_private_bob_blit
from m19_p0a_multi_bob_abk import parse_payload
from build_m19_p0c_screen_close_in_memory import build
from amos_link_test_support import relocate

SB0, SB1 = 0x54000, 0x54100
BM0, BM1 = 0x55000, 0x55100
BACK_PLANES = tuple(0x820000 + p*0x20000 for p in range(8))
SIZE = STRIDE*SCREEN_H
RP_SIZE = 128


class DrawMachine(ResolverMachine):
    def __init__(self, binary, layout='interpreted', depth=8):
        super().__init__(binary,layout=layout,depth=depth)
        self.native,self.labels=emit_safe_bank_blit()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.paint_blits=[]
        self.getmsg=[]
        self.uc.mem_write(GFX-198,b'\x4e\x75')
        self.uc.mem_write(GFX-606,b'\x4e\x75')
        self.uc.mem_write(GFX-636,b'\x4e\x75')
        self.uc.mem_write(EXEC-372,b'\x4e\x75')
        self.back_planes=list(BACK_PLANES[:depth])
        self.planes.extend(self.back_planes)
        self.uc.mem_write(BM1, pack('>HHBBH',STRIDE,SCREEN_H,0,depth,0)+
                          b''.join(pack('>I',p) for p in self.back_planes))
        self.put(SB0,BM0)
        self.put(SB1,BM1)
        for p,addr in enumerate(self.back_planes):
            self.uc.mem_write(addr,bytes(((p*37+13*y+x*11)&255
                            for y in range(SCREEN_H) for x in range(STRIDE))))

    def configure_real_state(self):
        self.put(self.real_state+12,SCREEN_W)
        self.put(self.real_state+16,SCREEN_H)
        self.put(self.real_state+28,self.depth)
        self.put(self.real_state+32,0x53000)
        self.put(0x53000+8,0)
        self.put(0x53000+20,0)

    def active_back_bitmap(self):
        return BM1 if self.get(0x53000+8)==0 else BM0

    def active_back_planes(self):
        return self.back_planes if self.get(0x53000+8)==0 else self.screen_planes

    def read_back(self):
        return [bytearray(self.uc.mem_read(addr,SIZE)) for addr in self.active_back_planes()]

    def os_call(self,uc,address,size,user):
        if address==EXEC-534:
            ptr=self.a(1)
            if any(p<=ptr<p+SIZE for p in self.back_planes):
                return self._os_return(3)
            return super().os_call(uc,address,size,user)

        if address==EXEC-372:
            ptr=self.a(0)
            self.getmsg.append(ptr)
            assert ptr==0x5b000,('wrong SafePort',hex(ptr))
            return self._os_return(0x5b100 if self.safe else 0)

        if address==GFX-198:
            rp=self.a(1)
            self.uc.mem_write(rp,bytes(RP_SIZE))
            self.paint_blits.append(('InitRastPort',rp))
            return self._os_return(0)

        if address in (GFX-606,GFX-636):
            masked=address==GFX-636
            source=self.a(0)
            rp=self.a(1)
            assert self.get(rp+4)==self.active_back_bitmap(),'not inactive BitMap'
            assert self.uc.mem_read(source+5,1)==bytes([self.depth])
            stride=unpack('>H',self.uc.mem_read(source,2))[0]
            rows=unpack('>H',self.uc.mem_read(source+2,2))[0]
            assert stride>0 and rows>0
            sx,sy,dx,dy,w,h,term=[self.d(i) for i in range(7)]
            assert term==(0xe0 if masked else 0xc0)
            assert 0<=sx and 0<=sy and 0<=dx and 0<=dy
            assert w>0 and h>0 and sx+w<=stride*8 and sy+h<=rows
            assert dx+w<=SCREEN_W and dy+h<=SCREEN_H
            maskptr=self.a(2) if masked else 0
            plane_ptrs=[self.get(source+8+4*p) for p in range(self.depth)]
            assert all(any(c<=ptr<c+n for c,n in self.chip_live.items())
                       for ptr in plane_ptrs), 'non-staged or Fast source'
            if masked:
                assert any(c<=maskptr<c+n for c,n in self.chip_live.items())
            dst=self.active_back_planes()
            for y in range(h):
                for x in range(w):
                    ix,iy,ox,oy=sx+x,sy+y,dx+x,dy+y
                    source_bit=0x80>>(ix&7)
                    if masked:
                        mask_byte=self.uc.mem_read(maskptr+iy*stride+ix//8,1)[0]
                        if not (mask_byte&source_bit):
                            continue
                    for p in range(self.depth):
                        at=plane_ptrs[p]+iy*stride+ix//8
                        source_byte=self.uc.mem_read(at,1)[0]
                        dst_at=dst[p]+oy*STRIDE+ox//8
                        before=self.uc.mem_read(dst_at,1)[0]
                        dest_bit=0x80>>(ox&7)
                        after=before|dest_bit if source_byte&source_bit else before & (255^dest_bit)
                        self.uc.mem_write(dst_at,bytes([after]))
            self.paint_blits.append(('BltMask' if masked else 'BltOpaque',
                                     sx,sy,dx,dy,w,h))
            return self._os_return(0)

        if address==GFX-228:
            self.paint_blits.append(('WaitBlit',))
            return super().os_call(uc,address,size,user)

        return super().os_call(uc,address,size,user)

    def paint(self,image=1,x=1,y=1,bank=10,*,limit=12000000):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1210+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(DR[0],image&0xffffffff)
        self.uc.reg_write(DR[1],x&0xffffffff)
        self.uc.reg_write(DR[3],bank&0xffffffff)
        self.uc.reg_write(DR[4],y&0xffffffff)
        original={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.entry+self.labels['safe_bank_blit_entry'],
                              STOP,count=limit)
        except Exception as exc:
            raise AssertionError((
                'M19 P0d full Safe->Blitter CPU020 fault',str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),image,x,y,bank,
                self.paint_blits[-5:],
                self.root(),self.nodes() if self.metadata else {})
            ) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,'SP clobbered'
        for r,v in original.items():
            if r not in (DR[2],DR[3]):
                assert self.uc.reg_read(r)==v,('ABI clobber',r)
        assert self.d(2)==0
        return self.d(3)


def ready(binary,layout,depth):
    m=DrawMachine(binary,layout=layout,depth=depth)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.run_get(2,20,6,56,9)==1
    assert m.run_get(3,6,3,36,10)==1
    assert m.mask(True,1,0)==1
    assert m.mask(True,2,(1<<depth)-1)==1
    m.activate_aga_state()
    m.configure_real_state()
    assert m.call('registry_prepare_entry')==1
    assert m.call('program_end_arm_entry')==1
    return m


def oracle(before,img,x,y):
    expected=[bytearray(p) for p in before]
    for sy in range(img.height):
        for sx in range(img.width):
            px,py=x+sx,y+sy
            if not 0<=px<SCREEN_W or not 0<=py<SCREEN_H or not img.visible(sx,sy):
                continue
            value=img.colour(sx,sy)
            off=py*STRIDE+px//8
            bit=0x80>>(px&7)
            for p in range(img.depth):
                expected[p][off]=(expected[p][off]|bit) if value&(1<<p) else (expected[p][off]&(255^bit))
    return expected


def main():
    lib,meta=build()
    assert meta['ap20_entries']==92
    raw,labels=emit_safe_bank_blit()
    old,old_labels=emit_bank_image_resolve()
    paint,_=emit_private_bob_blit()
    assert raw[:len(old)]==old
    assert all(labels[k]==v for k,v in old_labels.items())
    assert raw[labels['private_bob_blit_entry']:]==paint
    assert raw==emit_safe_bank_blit()[0]
    tail=raw[labels['safe_bank_blit_entry']:labels['private_bob_blit_entry']]
    decoded=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).disasm(tail,0x10000))
    assert sum(x.size for x in decoded)==len(tail)

    cases=0
    for layout in ('interpreted','compiled'):
        for depth in (1,4,8):
            m=ready(lib,layout,depth)
            bank=parse_payload(m.bank_payload(10))
            init_front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
            last_allocs=m.chip_allocs
            for image,x,y in (
                (1,1,1),(2,5,7),(3,-3,8),
                (1,64,11),(2,6,-2),(3,12,44),
                (2,-37,8),(3,SCREEN_W,4)):
                before=m.read_back()
                prev_blits=len(m.paint_blits)
                assert m.paint(image,x,y)==1,(layout,depth,image,x,y,m.paint_blits[-6:])
                want=oracle(before,bank.image(image),x,y)
                assert m.read_back()==want,(layout,depth,image,x,y,'pixel mismatch')
                visible=(-bank.image(image).width<x<SCREEN_W and
                         -bank.image(image).height<y<SCREEN_H)
                new=m.paint_blits[prev_blits:]
                assert sum(a[0] in ('BltOpaque','BltMask') for a in new)==int(visible)
                assert sum(a[0]=='WaitBlit' for a in new)==int(visible)
                assert m.get(0x53000+8)==0,'hidden swap'
                cases+=1
            assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==init_front
            assert m.chip_allocs==last_allocs,'paint recopied or allocated Chip'

            # SafePort pending once, Disp bit preserved on successful GetMsg.
            m.safe=True
            m.put(0x53000+12,0x5b000)
            m.put(0x53000+20,3)
            assert m.paint(1,7,8)==1
            assert m.get(0x53000+20)==2
            assert len(m.getmsg)==1
            cases+=1

            # Missing Safe notice: no DMA, no implicit Swap, pending unchanged.
            m.safe=False
            m.put(0x53000+20,3)
            old=m.read_back()
            blits=len(m.paint_blits)
            assert m.paint(1,7,8)==0
            assert m.read_back()==old and len(m.paint_blits)==blits
            assert m.get(0x53000+20)==3
            assert len(m.getmsg)==2
            cases+=1
            m.safe=True
            m.put(0x53000+20,0)

            # Change front index: painter must now use the original SB0 back,
            # while the previous SB1 front retains all of its contents.
            keep=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.back_planes)
            m.put(0x53000+8,1)
            before=m.read_back()
            assert m.paint(3,8,5)==1
            assert m.read_back()==oracle(before,bank.image(3),8,5)
            assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.back_planes)==keep
            cases+=1
            m.put(0x53000+8,0)

            # Invalidated AGBO generation must refuse before GetMsg/Blit.
            assert m.mask(True,1,(1<<depth)-1)==1
            before=m.read_back()
            blits=len(m.paint_blits)
            assert m.paint(1,3,3)==0
            assert len(m.paint_blits)==blits and m.read_back()==before
            assert m.call('registry_prepare_entry')==1
            assert m.paint(1,3,3)==1
            cases+=2

            # AGA Close must free the two owned P0c allocations after WaitBlit.
            m.invoke('bridge')
            assert not m.chip_live and not m.metadata and m.root()==(0,0)
            cases+=1

    print('M19 P0d PRIVATE MC68020 Safe AGBO->Blitter GATE A PASS',
          len(tail),'wrapper bytes;',cases,'native scenarios;',
          'OS/graphics mocked, NOT WinUAE or real AMOS Compiler')


if __name__=='__main__':
    main()
