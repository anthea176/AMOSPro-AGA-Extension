#!/usr/bin/env python3
"""S1-P1c combined MC68020 AGA capture -> AGSP DATA AMOS bank Gate A.

Real VASM binary executes five MC68020 modules in one 68k address space.
graphics.library, Exec and AMOS Main calls are simulated. This is NOT a
public AP20 command, WinUAE real IFF, Compiler or DMA Sprite validation.
"""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack,pack_into
import unittest

from unicorn.m68k_const import (
    UC_M68K_REG_SR,UC_M68K_REG_A0,UC_M68K_REG_A5,UC_M68K_REG_A7,
    UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_PC,
)
from m19_s1_agsp_bank import empty_bank,put_capture,parse_payload
from test_m19_s1p1_native_capture import planar
from test_m19_s1p1b_screen_rgb24 import make_screen,make_cmap
from test_m19_s1p1c_amos_bank_commit import (
    Machine,CODE,STOP,AMOS,STACK,REGS,
)

BIT0=0x146000
BIT1=0x147000
STATE,SCREEN,COLORMAP,DB=0x140000,0x141000,0x142000,0x143000
SB0,SB1=0x144000,0x145000
GFX=0x270000
RGB32,RGB24,DESC,PLANE,PAL=(0x1a0000,0x1a1000,0x1a2000,0x1a3000,0x1a4000)
CAPTURE=0x158000
REPACK_REQ,REPACK_STAGE,PUBLISH_REQ=0x1d0000,0x1c0000,0x1d1000
BPL_BASE=0x40000
W,H,DEPTH,STRIDE=320,256,8,40


class PipelineMachine(Machine):
    def __init__(self,screen=None,front=0,safe=1,old=None,
                 image_id=1,bank=10,alloc_fail=False,capacity=0x8000):
        super().__init__(old=old,alloc_fail=alloc_fail)
        self.code=Path(os.environ['AGSP_PIPELINE_BIN']).read_bytes()
        assert 25000<len(self.code)<60000
        self.uc.mem_write(CODE,self.code)
        self.calls_gfx=[]
        self.cmap=make_cmap()
        self.pixels=make_screen() if screen is None else screen
        self.front,self.safe=front,safe
        self.image_id=image_id
        self.put32(STATE,SCREEN)
        self.put32(STATE+8,GFX)
        self.put32(STATE+12,W)
        self.put32(STATE+16,H)
        self.put32(STATE+20,256)
        self.put32(STATE+28,DEPTH)
        self.put32(STATE+32,DB)
        self.put32(SCREEN+48,COLORMAP)
        self.put16(COLORMAP+2,256)
        self.put32(DB,SB0)
        self.put32(DB+4,SB1)
        self.put32(DB+8,front)
        self.put32(DB+20,safe)
        self.put32(SB0,BIT0)
        self.put32(SB1,BIT1)
        for page,bmp in enumerate((BIT0,BIT1)):
            raw=bytearray(40)
            pack_into('>HH',raw,0,STRIDE,H)
            raw[5]=DEPTH
            for plane in range(8):
                pack_into('>I',raw,8+4*plane,BPL_BASE+(page*8+plane)*0x10000)
            self.uc.mem_write(bmp,bytes(raw))
        self.load_pixels(0,self.pixels)
        self.load_pixels(1,self.pixels)
        self.uc.mem_write(GFX-900,b'\x4e\x75')
        self.uc.mem_write(GFX-228,b'\x4e\x75')
        self.uc.mem_write(RGB32,bytes([0x66])*3072)
        self.uc.mem_write(RGB24,bytes([0x5a])*768)
        self.uc.mem_write(DESC,bytes([0x5a])*64)
        self.uc.mem_write(PLANE,bytes([0x5a])*1024)
        self.uc.mem_write(PAL,bytes([0x5a])*48)
        self.uc.mem_write(REPACK_REQ,bytes([0x5a])*40)
        self.uc.mem_write(REPACK_STAGE,bytes([0x5a])*capacity)
        self.uc.mem_write(PUBLISH_REQ,bytes([0x5a])*16)
        self.prepare_request(bank,image_id,capacity)

    def load_pixels(self,page,pixels):
        for i,plane in enumerate(planar(pixels,W,H,DEPTH,STRIDE)):
            addr=BPL_BASE+(page*8+i)*0x10000
            self.uc.mem_write(addr,plane)

    def prepare_request(self,bank=10,image_id=1,capacity=0x8000):
        req=bytearray(72)
        pack_into('>6I4HI',req,0,STATE,RGB32,RGB24,DESC,PLANE,PAL,13,5,16,0,0)
        pack_into('>I',req,36,bank)
        pack_into('>4H',req,40,image_id,0,0,0)
        old_ptr=(self.old_node+24) if self.old_node is not None else 0
        old_len=len(self.initial_old) if self.initial_old is not None else 0
        pack_into('>6I',req,48,old_ptr,old_len,REPACK_REQ,REPACK_STAGE,
                  capacity,PUBLISH_REQ)
        self.uc.mem_write(CAPTURE,bytes(req))

    def on_code(self,uc,address,size,user):
        if address == GFX-228:
            self.calls_gfx.append('WaitBlit')
            return
        if address == GFX-900:
            self.calls_gfx.append('GetRGB32')
            assert uc.reg_read(UC_M68K_REG_A0)==COLORMAP
            from unicorn.m68k_const import UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_A1
            assert uc.reg_read(UC_M68K_REG_D0)==0
            assert uc.reg_read(UC_M68K_REG_D1)==256
            assert uc.reg_read(UC_M68K_REG_A1)==RGB32
            rgb32=b''.join(pack('>III',*(v*0x01010101 for v in self.cmap[p*3:p*3+3]))
                           for p in range(256))
            uc.mem_write(RGB32,rgb32)
            return
        return super().on_code(uc,address,size,user)

    def capture(self):
        uc=self.uc
        from unicorn.m68k_const import UC_M68K_REG_A1,UC_M68K_REG_D0,UC_M68K_REG_D1
        for i,r in enumerate(REGS):
            uc.reg_write(r,0x50001000+i)
        uc.reg_write(UC_M68K_REG_A0,CAPTURE)
        uc.reg_write(UC_M68K_REG_A5,AMOS)
        saved={r:uc.reg_read(r) for r in REGS}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        uc.mem_write(STACK,pack('>I',STOP))
        uc.emu_start(CODE,STOP,count=70_000_000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in saved.items()),'ABI clobber'
        assert uc.reg_read(UC_M68K_REG_D2)==0
        return uc.reg_read(UC_M68K_REG_D3)


@unittest.skipUnless(os.getenv('AGSP_PIPELINE_BIN') and os.getenv('AGSP_PUBLISH_BIN'),
                     'requires combined VASM MC68020 image')
class AGSPPipelineGateA(unittest.TestCase):
    def test_new_bank_from_full_aga_screen_capture(self):
        m=PipelineMachine()
        self.assertEqual(m.capture(),1)
        self.assertEqual(m.calls_gfx,['WaitBlit','GetRGB32'])
        expected=put_capture(empty_bank(),1,m.pixels,W,H,13,5,16,16,
                             m.cmap,0,mode='s1')
        self.assertEqual(m.bank(10),expected)
        self.assertEqual(parse_payload(m.bank(10)).image(1).opaque_count,3)
        self.assertEqual(len(m.notes),1)

    def test_repack_preserves_old_s2_image_and_adds_s1(self):
        pal=make_cmap()
        pixels=bytes([0,1,2,3,4,0,1,2,3,4,0,1,2,3,4,0])
        old=put_capture(empty_bank(),9,pixels,16,1,0,0,16,1,pal,0,mode='s2')
        m=PipelineMachine(old=old)
        self.assertEqual(m.capture(),1)
        expected=put_capture(old,1,m.pixels,W,H,13,5,16,16,m.cmap,0,mode='s1')
        self.assertEqual(m.bank(10),expected)
        self.assertEqual([s.image_id for s in parse_payload(m.bank(10)).images],[1,9])
        self.assertEqual(m.freed,[m.old_node])

    def test_four_colors_fails_without_list_or_bank_mutation(self):
        m=PipelineMachine(screen=make_screen(extra=True))
        self.assertEqual(m.capture(),0)
        self.assertIsNone(m.bank(10))
        self.assertEqual(m.notes,[])
        self.assertEqual(m.calls,[])
        self.assertEqual(m.calls_gfx,['WaitBlit','GetRGB32'])

    def test_unsafe_buffer_refuses_without_graphics_or_bank(self):
        m=PipelineMachine(safe=0)
        self.assertEqual(m.capture(),0)
        self.assertEqual(m.calls_gfx,[])
        self.assertEqual(m.calls,[])
        self.assertEqual(m.bank(10),None)

    def test_publisher_alloc_failure_leaves_existing_bank(self):
        old=put_capture(empty_bank(),7,
                        bytes([0]*256),16,16,0,0,16,16,make_cmap(),0)
        m=PipelineMachine(old=old,alloc_fail=True)
        self.assertEqual(m.capture(),0)
        self.assertEqual(m.bank(10),old)
        self.assertEqual(m.notes,[])

    def test_back_buffer_selected_after_front_switch(self):
        m=PipelineMachine(front=1)
        m.load_pixels(1,bytes(W*H))  # front is page1; back must be page0
        self.assertEqual(m.capture(),1)
        expected=put_capture(empty_bank(),1,m.pixels,W,H,13,5,16,16,m.cmap,0)
        self.assertEqual(m.bank(10),expected)

    def test_bad_image_id_and_bank_reject_before_graphics(self):
        for bank,ident in ((4,1),(65536,1),(10,0),(10,4097)):
            with self.subTest(bank=bank,ident=ident):
                m=PipelineMachine(bank=bank,image_id=ident)
                self.assertEqual(m.capture(),0)
                self.assertEqual(m.calls_gfx,[])
                self.assertEqual(m.notes,[])


if __name__=='__main__':
    unittest.main(verbosity=2)
