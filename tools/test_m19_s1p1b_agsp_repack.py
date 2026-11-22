#!/usr/bin/env python3
"""MC68020 AGSP v1 payload repacker vs independent AGSP reference model.

No OS/AMOS service is touched. CPU Gate A for the private stage, not
an AP20 integration, an AMOS Save/Load or WinUAE runtime validation.
"""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack, pack_into
import unittest

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020,UC_M68K_REG_PC,UC_M68K_REG_SR,
    UC_M68K_REG_A0,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
)
from m19_s1_agsp_bank import empty_bank, put_capture, parse_payload

PC,STOP,OLD,PLANES,PALETTE,DEST,REQUEST,STACK=(
    0x20000,0x30000,0x50000,0x140000,0x150000,0x180000,0x120000,0x2c0000)
REGS=(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,
      UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A2,UC_M68K_REG_A3,
      UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)


def cmap():
    return b''.join(bytes((p,(p*13+7)&255,(p*17+11)&255)) for p in range(256))


def img_source(height=16, pattern=(0,25,67,128)):
    return bytes(pattern[(x+y)%len(pattern)] for y in range(height) for x in range(16))


def put_image(payload,ident,height=16,pattern=(0,25,67,128),pen=0,mode='s1'):
    return put_capture(payload,ident,img_source(height,pattern),16,height,
                       0,0,16,height,cmap(),pen,mode=mode)


class RepackRunner:
    def __init__(self):
        self.uc=Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x400000)
        binary=Path(os.environ['AGSP_REPACK_BIN']).read_bytes()
        assert 300 < len(binary) < 16000
        self.uc.mem_write(PC,binary)

    def put(self,addr,data): self.uc.mem_write(addr,bytes(data))
    def read(self,addr,n): return bytes(self.uc.mem_read(addr,n))

    def run(self,old,new_payload,new_id,capacity=0x100000,corrupt=None):
        uc=self.uc
        new=parse_payload(new_payload).image(new_id)
        self.put(PLANES,new.planes)
        self.put(PALETTE,new.palette)
        self.put(OLD,old if old is not None else bytes(32))
        self.put(DEST-16,bytes([0xa5])*16)
        self.put(DEST,bytes([0x5a])*max(0x5000,len(old or b'')+len(new.planes)+1024))
        self.put(DEST+0x5000,bytes([0xc3])*16)
        params=bytearray(pack('>6I4H2hI',OLD if old is not None else 0,
                              len(old) if old is not None else 0,
                              PLANES,PALETTE,DEST,capacity,
                              new_id,new.height,new.opaque_count,
                              new.source_transparent_pen,
                              new.hotspot_x,new.hotspot_y,0))
        assert len(params)==40
        for offset,value in (corrupt or {}).items():
            if offset in (0,4,8,12,16,20,36):pack_into('>I',params,offset,value)
            else:pack_into('>H',params,offset,value)
        self.put(REQUEST,params)
        source=old if old is not None else bytes(32)
        planes=new.planes
        palette=new.palette
        for i,r in enumerate(REGS):uc.reg_write(r,0x45001100+i)
        saved={r:uc.reg_read(r) for r in REGS}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A0,REQUEST)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        self.put(STACK,pack('>I',STOP))
        uc.emu_start(PC,STOP,count=5000000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in saved.items()),'ABI register clobber'
        assert self.read(OLD,len(source))==source
        assert self.read(PLANES,len(planes))==planes
        assert self.read(PALETTE,len(palette))==palette
        assert self.read(DEST-16,16)==bytes([0xa5])*16
        assert self.read(DEST+0x5000,16)==bytes([0xc3])*16
        return uc.reg_read(UC_M68K_REG_D0),uc.reg_read(UC_M68K_REG_D1)


@unittest.skipUnless(os.environ.get('AGSP_REPACK_BIN'), 'requires real MC68020 assembled binary')
class AGSPRepackGateA(unittest.TestCase):
    def setUp(self):
        self.m=RepackRunner()

    def verify(self,old,ident,height=16,pattern=(0,25,67,128),pen=0):
        model=put_image(old if old is not None else empty_bank(),ident,height,pattern,pen)
        temp=put_image(empty_bank(),ident,height,pattern,pen)
        size,status=self.m.run(old,temp,ident)
        self.assertEqual((size,status),(len(model),1))
        self.assertEqual(self.m.read(DEST,size),model)
        self.assertEqual(parse_payload(self.m.read(DEST,size)).image(ident),
                         parse_payload(model).image(ident))
        return model

    def test_new_bank_from_null_is_canonical(self):
        got=self.verify(None,1)
        self.assertEqual(parse_payload(got).generation,2)
        self.assertEqual(len(got),32+48+64+48)

    def test_inserting_before_middle_and_after_keeps_ids(self):
        bank=self.verify(None,10)
        bank=self.verify(bank,1,height=5)
        bank=self.verify(bank,6,height=10)
        bank=self.verify(bank,20,height=3)
        self.assertEqual([i.image_id for i in parse_payload(bank).images],[1,6,10,20])
        self.assertEqual(parse_payload(bank).generation,5)

    def test_replace_existing_image_changes_byte_count_and_palette(self):
        bank=self.verify(None,3,height=16)
        bank=self.verify(bank,9,height=32)
        bank=self.verify(bank,3,height=9,pattern=(0,25),pen=0)
        self.assertEqual(parse_payload(bank).image(3).height,9)
        self.assertEqual(parse_payload(bank).image(9).height,32)

    def test_max_height_256_and_opaque_black(self):
        self.verify(None,4096,height=256,pattern=(0,255))

    def test_retain_s2_old_image_4_planes(self):
        old=put_capture(empty_bank(),20,
                        bytes([0,1,2,3,4]*3+[0]),16,1,0,0,16,1,cmap(),0,mode='s2')
        self.assertEqual(parse_payload(old).image(20).depth,4)
        got=self.verify(old,1)
        self.assertEqual(parse_payload(got).image(20),parse_payload(old).image(20))

    def test_capacity_failure_never_writes(self):
        temp=put_image(empty_bank(),2)
        size,status=self.m.run(None,temp,2,capacity=100)
        self.assertEqual((size,status),(0,0))
        self.assertEqual(self.m.read(DEST,512),bytes([0x5a])*512)

    def test_bad_request_refuses_before_mutating_stage(self):
        temp=put_image(empty_bank(),2)
        cases=({24:0},{24:4097},{26:0},{28:4},{30:256},{36:1},
               {8:0},{12:0},{16:0},{20:2})
        for changes in cases:
            with self.subTest(changes=changes):
                m=RepackRunner()
                self.assertEqual(m.run(None,temp,2,corrupt=changes),(0,0))
                self.assertEqual(m.read(DEST,512),bytes([0x5a])*512)

    def test_bad_old_header_and_directory_refused(self):
        original=put_image(empty_bank(),6)
        temp=put_image(empty_bank(),3)
        for offset,value,width in ((0,0,4),(4,2,2),(8,4097,2),
                                   (10,40,2),(12,0,4),(16,0,4),
                                   (20,0,4),(28,1,4),(32,0,2),
                                   (44,0,4),(56,0,4),(64,4,2)):
            bad=bytearray(original)
            pack_into('>I' if width==4 else '>H',bad,offset,value)
            with self.subTest(offset=offset):
                m=RepackRunner()
                self.assertEqual(m.run(bytes(bad),temp,3),(0,0))
                self.assertEqual(m.read(DEST,512),bytes([0x5a])*512)


if __name__=='__main__':unittest.main(verbosity=2)
