#!/usr/bin/env python3
"""S1-P1e real MC68020 public Get AGA Sprite API with simulated AMOS/Exec.

The tests run assembled Motorola bytecode and verify AMOS A3 arguments,
bank selection, private owned AllocVec/FreeVec memory, and all AGSP pixels.
NOT an installed Lib, WinUAE, Compiler, DMA or physical Amiga Gate.
"""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack
import unittest

from unicorn.m68k_const import (
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A3,UC_M68K_REG_A5,
    UC_M68K_REG_A7,UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,
    UC_M68K_REG_D3,UC_M68K_REG_PC,UC_M68K_REG_SR
)
from m19_s1_agsp_bank import empty_bank,put_capture,parse_payload
from test_m19_s1p1c_amos_bank_commit import (
    CODE,STOP,AMOS,STACK,EXEC,REGS,fixture,CUR_BANKS,HEAD
)
from test_m19_s1p1c_pipeline import (
    PipelineMachine,GFX,COLORMAP,W,H
)
from test_m19_s1p1b_screen_rgb24 import make_screen

PARAMS=0x1e0000


class GetMachine(PipelineMachine):
    def __init__(self,old=None,screen=None,safe=1,front=0,foreign=False):
        super().__init__(old=old,screen=screen,safe=safe,front=front)
        self.code=Path(os.environ['AGSP_GET_BIN']).read_bytes()
        assert 5000<len(self.code)<65000
        self.uc.mem_write(CODE,self.code)
        self.uc.mem_write(EXEC-684,b'\x4e\x75')  # AllocVec
        self.uc.mem_write(EXEC-690,b'\x4e\x75')  # FreeVec
        self.put32(AMOS+0x1c8,self.put_screen_state)
        self.temp_allocs=[]
        self.temp_frees=[]
        self.temp_live=set()
        self.fail_temp_at=0
        self.temp_tries=0
        if foreign and self.old_node is not None:
            self.uc.mem_write(self.old_node+16,b'FOREIGN ')

    @property
    def put_screen_state(self):
        from test_m19_s1p1c_pipeline import STATE
        return STATE

    def on_code(self,uc,address,size,user):
        if address==EXEC-684:
            self.temp_tries+=1
            if self.fail_temp_at==self.temp_tries:
                uc.reg_write(UC_M68K_REG_D0,0)
                return
            size=uc.reg_read(UC_M68K_REG_D0)
            assert 0<size<=0x1000000
            assert uc.reg_read(UC_M68K_REG_D1)==0x00010001
            ptr=self.allocate(size)
            self.temp_live.add(ptr)
            self.temp_allocs.append((ptr,size))
            uc.reg_write(UC_M68K_REG_D0,ptr)
            return
        if address==EXEC-690:
            ptr=uc.reg_read(UC_M68K_REG_A1)
            assert ptr in self.temp_live
            self.temp_live.remove(ptr)
            self.temp_frees.append(ptr)
            del self.allocations[ptr]
            return
        if address==GFX-900:
            assert uc.reg_read(UC_M68K_REG_A0)==COLORMAP
            assert (uc.reg_read(UC_M68K_REG_D0),uc.reg_read(UC_M68K_REG_D1))==(0,256)
            dst=uc.reg_read(UC_M68K_REG_A1)
            assert dst in self.temp_live or any(
                p<=dst<p+length for p,length in self.temp_allocs)
            rgb32=b''.join(pack('>III',*(v*0x01010101 for v in self.cmap[p*3:p*3+3]))
                           for p in range(256))
            uc.mem_write(dst,rgb32)
            self.calls_gfx.append('GetRGB32')
            return
        return super().on_code(uc,address,size,user)

    def _invoke(self,pc,bank_or_pen,rest=()):
        uc=self.uc
        for i,r in enumerate(REGS):
            uc.reg_write(r,0x55004000+i)
        uc.reg_write(UC_M68K_REG_A5,AMOS)
        uc.reg_write(UC_M68K_REG_A0,0x1f0000)
        saved={r:uc.reg_read(r) for r in REGS}
        uc.reg_write(UC_M68K_REG_D3,bank_or_pen&0xffffffff)
        uc.reg_write(UC_M68K_REG_A3,PARAMS)
        if rest:
            assert len(rest)==5
            uc.mem_write(PARAMS,pack('>5I',*(x&0xffffffff for x in rest)))
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        uc.mem_write(STACK,pack('>I',STOP))
        try:
            uc.emu_start(pc,STOP,count=80_000_000)
        except Exception as exc:
            raise AssertionError(
                f'PC={uc.reg_read(UC_M68K_REG_PC):08x} '
                f'SP={uc.reg_read(UC_M68K_REG_A7):08x} '
                f'D3={uc.reg_read(UC_M68K_REG_D3):08x} '
                f'entry=0x{pc:08x}') from exc
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in saved.items()),'AMOS preserved register changed'
        assert uc.reg_read(UC_M68K_REG_A3)==PARAMS+4*len(rest),'AMOS arguments not all consumed'
        assert uc.reg_read(UC_M68K_REG_D2)==0
        return uc.reg_read(UC_M68K_REG_D3)

    def select(self,bank=10):
        return self._invoke(CODE,bank)

    def get_sprite(self,ident=1,x1=13,y1=5,x2=28,y2=20,pen=0):
        # From AMOS D3=last, pop Y2, X2, Y1, X1, ImageId.
        return self._invoke(CODE+8,pen,(y2,x2,y1,x1,ident))

    def no_temps(self):
        assert not self.temp_live, 'temporary AllocVec allocation survived'
        assert len(self.temp_allocs)==len(self.temp_frees)
        for ptr,_ in self.temp_allocs:
            assert ptr not in self.allocations


@unittest.skipUnless(os.getenv('AGSP_GET_BIN') and os.getenv('AGSP_PUBLISH_BIN'),
                     'requires combined VASM MC68020 Get entry')
class AGSPPublicGetGateA(unittest.TestCase):
    def test_select_then_capture_into_existing_empty_agsp_bank(self):
        m=GetMachine()
        self.assertEqual(m.select(10),1)
        self.assertEqual(m.bank(10),empty_bank())
        self.assertEqual(m.get_sprite(),1)
        want=put_capture(empty_bank(),1,m.pixels,W,H,13,5,16,16,m.cmap,0)
        self.assertEqual(m.bank(10),want)
        self.assertEqual(parse_payload(m.bank(10)).image(1).opaque_count,3)
        self.assertEqual(m.calls_gfx,['WaitBlit','GetRGB32'])
        m.no_temps()

    def test_runtime_bank_29_capture_and_replace(self):
        pixels=bytes(a|b for a,b in zip(make_screen(),make_screen(x=80)))
        m=GetMachine(screen=pixels)
        self.assertEqual(m.select(29),1)
        self.assertEqual(m.bank(29),empty_bank())
        self.assertEqual(m.get_sprite(),1)
        first=m.bank(29)
        self.assertEqual(len(first),192)
        self.assertEqual(m.get_sprite(2,x1=80,x2=95),1)
        self.assertEqual(len(m.bank(29)),352)
        self.assertEqual(m.get_sprite(1,x1=80,x2=95),1)
        self.assertEqual(len(m.bank(29)),352)
        self.assertEqual(m.get(CUR_BANKS),HEAD)
        self.assertIsNone(m.bank(10))
        self.assertFalse(m.temp_live)

    def test_get_without_bank_selection_is_refused(self):
        m=GetMachine()
        self.assertEqual(m.get_sprite(),0)
        self.assertIsNone(m.bank(10))
        self.assertEqual(m.temp_tries,0)
        self.assertEqual(m.calls_gfx,[])
        m.no_temps()

    def test_get_preserves_loaded_agsp_bank_with_flags_normalized_to_zero(self):
        original=fixture()
        m=GetMachine(old=original)
        m.put16(m.old_node+12,0)
        self.assertEqual(m.select(),1)
        self.assertEqual(m.get_sprite(2),1)
        new=m.bank(10)
        self.assertEqual([x.image_id for x in parse_payload(new).images],[1,2])
        self.assertEqual(parse_payload(new).image(1),parse_payload(original).image(1))
        m.no_temps()

    def test_capture_two_images_and_replace_one(self):
        m=GetMachine()
        self.assertEqual(m.select(),1)
        self.assertEqual(m.get_sprite(6),1)
        previous=m.bank(10)
        self.assertEqual(m.get_sprite(1),1)
        two=parse_payload(m.bank(10))
        self.assertEqual([s.image_id for s in two.images],[1,6])
        self.assertEqual(two.generation,3)
        self.assertEqual(m.get_sprite(6,y1=6,y2=21),1)
        final=parse_payload(m.bank(10))
        self.assertEqual(final.generation,4)
        self.assertEqual([s.image_id for s in final.images],[1,6])
        self.assertEqual(final.image(1),two.image(1))
        self.assertNotEqual(final.image(6),parse_payload(previous).image(6))
        self.assertEqual(len(m.notes),4)  # first bank create + 3 captures
        m.no_temps()

    def test_invalid_coordinates_or_image_never_modify_bank(self):
        cases=((1,13,5,27,20,0),(1,13,5,29,20,0),
               (1,13,5,28,260,0),(1,-1,5,14,20,0),
               (1,13,-1,28,14,0),(0,13,5,28,20,0),
               (4097,13,5,28,20,0),(1,13,5,28,20,256))
        for args in cases:
            with self.subTest(args=args):
                m=GetMachine()
                self.assertEqual(m.select(),1)
                old=m.bank(10)
                self.assertEqual(m.get_sprite(*args),0)
                self.assertEqual(m.bank(10),old)
                self.assertEqual(m.temp_tries,0)
                m.no_temps()

    def test_unsafe_back_buffer_refuses_and_frees_both_allocations(self):
        m=GetMachine(safe=0)
        self.assertEqual(m.select(),1)
        original=m.bank(10)
        self.assertEqual(m.get_sprite(),0)
        self.assertEqual(m.bank(10),original)
        self.assertEqual(m.calls_gfx,[])
        m.no_temps()

    def test_four_opaque_colors_refuse_without_bank_publication(self):
        m=GetMachine(screen=make_screen(extra=True))
        self.assertEqual(m.select(),1)
        original=m.bank(10)
        self.assertEqual(m.get_sprite(),0)
        self.assertEqual(m.bank(10),original)
        self.assertEqual(m.notes[-1][0],m.bynum(10))
        self.assertEqual(len(m.notes),1)
        m.no_temps()

    def test_first_and_second_allocvec_fail_without_leaks(self):
        for failat in (1,2):
            with self.subTest(at=failat):
                m=GetMachine()
                self.assertEqual(m.select(),1)
                before=m.bank(10)
                m.fail_temp_at=failat
                self.assertEqual(m.get_sprite(),0)
                self.assertEqual(m.bank(10),before)
                self.assertEqual(len(m.notes),1)
                m.no_temps()

    def test_amos_bank_alloc_failure_does_not_publish(self):
        m=GetMachine()
        self.assertEqual(m.select(),1)
        before=m.bank(10)
        m.alloc_fail=True
        self.assertEqual(m.get_sprite(),0)
        self.assertEqual(m.bank(10),before)
        self.assertEqual(len(m.notes),1)
        m.no_temps()

    def test_foreign_bank_and_corrupt_old_payload_refused(self):
        for foreign in (True,False):
            with self.subTest(foreign=foreign):
                m=GetMachine(old=fixture(),foreign=foreign)
                if not foreign:
                    m.uc.mem_write(m.old_node+24,b'AGBO')
                self.assertEqual(m.select(),0)
                self.assertEqual(m.get_sprite(),0)
                self.assertEqual(len(m.notes),0)
                m.no_temps()

    def test_changed_front_selector_uses_safe_back_buffer(self):
        m=GetMachine(front=1)
        m.load_pixels(1,bytes(W*H))
        self.assertEqual(m.select(),1)
        self.assertEqual(m.get_sprite(),1)
        want=put_capture(empty_bank(),1,m.pixels,W,H,13,5,16,16,m.cmap,0)
        self.assertEqual(m.bank(10),want)
        m.no_temps()


if __name__=='__main__':
    unittest.main(verbosity=2)
