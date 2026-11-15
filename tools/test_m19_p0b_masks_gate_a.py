#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""MC68020 CPU/AP20 Gate A for Make/No AGA Bob Mask on R88-derived M19.

Services are isolated AMOS/Exec mocks, not a WinUAE or native Compiler Gate.
Exercises exact BOBS unit bytes in interpreter-like and compiled-like layouts,
identity/allocator rollback, AGBO header consistency, padding and pixel masks.
"""
from __future__ import annotations
from struct import pack

from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020

from test_m5_generic import DR,AR,AMOS,STACK,STOP
from amos_link_test_support import relocate
from test_m19_p0a_r88_get_gate_a import CaptureMachine,colour,ARGS,HEAD
from m19_p0b_masks_emit import emit_mask_commands
from m19_p0a_multi_bob_abk import parse_payload,make_mask,put_image
from build_m19_p0b_masks_in_memory import build
from compiler_relocation import unpack_ap20


class MaskMachine(CaptureMachine):
    def __init__(self,binary,layout='interpreted',depth=8,**kw):
        super().__init__(binary,layout=layout,depth=depth,**kw)
        self.native,self.labels=emit_mask_commands()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.make_entry=self.entry+self.labels['mask_make_entry']
        self.no_entry=self.entry+self.labels['mask_no_entry']
        self.get_entry=self.entry+self.labels['get_entry']

    def mask(self,make,image_id,colour_index=0,*,limit=9000000):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1230+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        if make:self.put(ARGS,image_id)
        self.uc.reg_write(DR[3],(colour_index if make else image_id)&0xffffffff)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.make_entry if make else self.no_entry,
                              STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('MASK CPU020 fault',str(exc),
                                  hex(self.uc.reg_read(UC_M68K_REG_PC)),
                                  make,image_id,colour_index,self.calls[-12:],
                                  self.stage_log[-4:])) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,'mask stack not restored'
        for r,v in before.items():
            if r in (DR[2],DR[3]):continue
            if r==AR[3]:
                assert self.uc.reg_read(r)==v+(4 if make else 0),'mask GetP consumed wrong arguments'
            else:
                assert self.uc.reg_read(r)==v,('mask caller register overwritten',r)
        assert self.d(2)==0,'AMOS integer status type'
        assert self.d(3) in (0,1),'unsupported mask native status'
        assert not self.scratch_live,'mask leaked temporary Exec allocation'
        assert self.plane_writes==0,'mask modified screen bitplanes'
        return self.d(3)


def verify_mask(bank,image_id,transparent):
    img=bank.image(image_id)
    assert img.mask is not None
    for y in range(img.height):
        for x in range(img.width):
            assert img.visible(x,y)==(img.colour(x,y)!=transparent),\
                ('mask pixel mismatch',image_id,x,y,transparent)


def main():
    binary,meta=build()
    assert binary==build()[0],'nonreproducible candidate'
    assert meta['commands']==82 and meta['entries']==92
    parts=unpack_ap20(binary)[1]
    native,labels=emit_mask_commands()
    assert parts[90].endswith(native)
    assert parts[91] and labels['mask_make_entry']<labels['mask_no_entry']
    c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
    d=list(c.disasm(native[labels['mask_make_entry']:labels['mask_kernel']],
                    0x10000+labels['mask_make_entry']))
    assert sum(x.size for x in d)==labels['mask_kernel']-labels['mask_make_entry']
    assert not any(x.mnemonic.startswith('dc.') for x in d)
    cases=0
    for layout in ('interpreted','compiled'):
        for depth in (1,4,8):
            m=MaskMachine(binary,layout=layout,depth=depth)
            assert m.run_select(10)==1
            for ident,rect in ((3,(20,6,56,9)),(1,(4,5,20,8)),(2,(6,3,36,10))):
                assert m.run_get(ident,*rect)==1,(layout,depth,ident,m.calls[-7:])
            original=parse_payload(m.bank_payload(10))
            assert [im.image_id for im in original.images]==[1,2,3]
            assert m.mask(True,1,0)==1,('make mask zero',layout,depth,m.calls[-10:],m.stage_log[-6:])
            after=parse_payload(m.bank_payload(10))
            assert after.generation==original.generation+1
            assert after.image(2)==original.image(2) and after.image(3)==original.image(3)
            verify_mask(after,1,0);cases+=1
            assert m.mask(True,2,(1<<depth)-1)==1
            after2=parse_payload(m.bank_payload(10))
            assert after2.image(1)==after.image(1) and after2.image(3)==after.image(3)
            verify_mask(after2,2,(1<<depth)-1);cases+=1
            assert m.mask(True,1,(1<<depth)-1)==1
            after3=parse_payload(m.bank_payload(10))
            verify_mask(after3,1,(1<<depth)-1)
            assert after3.image(2)==after2.image(2)
            assert len(after3.raw)==len(after2.raw)
            cases+=1
            assert m.mask(False,2)==1
            removed=parse_payload(m.bank_payload(10))
            assert removed.image(2).mask is None
            assert all(removed.image(2).visible(x,0)
                       for x in range(removed.image(2).width))
            assert removed.image(1)==after3.image(1)
            assert removed.image(3)==after3.image(3)
            assert len(removed.raw)==len(after3.raw)-after3.image(2).plane_bytes
            cases+=1
            frozen=m.bank_payload(10)
            allocs=m.allocations
            assert m.mask(False,2)==1
            assert m.bank_payload(10)==frozen
            assert m.allocations==allocs
            cases+=1
            for params in ((True,1,-1),(True,1,1<<depth),
                           (True,4097,0),(True,0,0),(False,999,0),
                           (False,0,0)):
                assert m.mask(*params)==0,('invalid param accepted',params)
                assert m.bank_payload(10)==frozen
                cases+=1
            assert m.mask(False,1)==1
            assert parse_payload(m.bank_payload(10)).image(1).mask is None
            cases+=1
            # A loaded bank may already contain a mask; preserve it when
            # mutating another image. Enforce mask==0/1 independently of color.
            p=m.bank_payload(10)
            p=make_mask(p,2,0)
            m.install_payload(10,p)
            assert m.run_select(10)==1
            assert m.mask(True,3,(1<<depth)-1)==1
            mixed=parse_payload(m.bank_payload(10))
            assert mixed.image(2)==parse_payload(p).image(2)
            verify_mask(mixed,3,(1<<depth)-1)
            cases+=1
        # Test geometry extremes within the AGA framebuffer depth8.
        for width in (1,7,17,31,32,37,65):
            m=MaskMachine(binary,layout=layout,depth=8)
            assert m.run_select(10)==1
            assert m.run_get(1,0,0,width-1,2)==1
            assert m.mask(True,1,0)==1
            verify_mask(parse_payload(m.bank_payload(10)),1,0)
            assert m.mask(False,1)==1
            assert parse_payload(m.bank_payload(10)).image(1).mask is None
            cases+=2
        for fault in ('scratch_fail','bank_alloc_fail'):
            m=MaskMachine(binary,layout=layout)
            assert m.run_select(10)==1
            assert m.run_get(1,7,4,23,7)==1
            prior=m.bank_payload(10)
            setattr(m,fault,True)
            assert m.mask(True,1,0)==0,('fault not rejected',fault,m.calls[-12:])
            assert m.bank_payload(10)==prior
            assert m.notifications==2  # Select + Get, no new notification
            cases+=1
        m=MaskMachine(binary,layout=layout)
        assert m.run_select(10)==1
        assert m.run_get(1,3,4,4,4)==1
        prior=m.bank_payload(10)
        m.put(HEAD,0)
        m.install_bank(10)
        assert m.mask(True,1,0)==0
        assert m.bank_payload(10)!=prior
        cases+=1
        m=MaskMachine(binary,layout=layout)
        assert m.run_select(10)==1
        assert m.run_get(1,1,1,17,1)==1
        # Corrupt the directory mask flag and verify complete rollback.
        old=m.bank_payload(10)
        node=m.find(10)
        m.uc.mem_write(node+24+32+10,b'\x00\x02')
        damaged=m.bank_payload(10)
        assert m.mask(True,1,0)==0
        assert m.bank_payload(10)==damaged
        assert old!=damaged
        cases+=1
        m=MaskMachine(binary,layout=layout)
        assert m.run_select(10)==1
        assert m.run_get(1,1,1,17,1)==1
        # AttnFlags AFF_68020 clear => clean, unchanged rejection.
        from test_m5_generic import EXEC
        m.uc.mem_write(EXEC+0x128,b'\x00\x00')
        prior=m.bank_payload(10)
        assert m.mask(True,1,0)==0
        assert m.bank_payload(10)==prior
        cases+=1
    print('M19 P0b Make/No Mask MC68020 AP20 Gate A PASS',cases,
          'CPU scenarios, interpreted and compiled-style relocations, SHA256',
          meta['sha256'],'candidate bytes',meta['size'],'NO WinUAE/real Compiler')


if __name__=='__main__': main()
