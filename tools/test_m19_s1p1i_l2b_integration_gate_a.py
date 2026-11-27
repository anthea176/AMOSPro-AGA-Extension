#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Full candidate and actual inherited L2b DB/IFF/Sprite chain.
Native code on Unicorn; OS screen and library calls are modeled.
Not a WinUAE, real Compiler, physical Amiga or Sprite DMA qualification.
"""
import argparse
import base64
import json
import os
from pathlib import Path
from struct import pack, unpack_from
import unittest
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from audit_ap20 import walk_tokens
from build_m19_s1p1i_l2b_contract_in_memory import build_s1p1i
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import unpack_ap20, RBSR
from test_m19_s1p1i_contract_gate_a import ContractMachine, read_fixture, SAFE, DISP, MSG
from test_m19_s1p1c_pipeline import STATE, SCREEN, DB, SB0, SB1, GFX, W, H, BPL_BASE
from test_m19_s1p1c_amos_bank_commit import EXEC
from test_m19_s1p1_native_capture import planar
from test_m19_p2d_l1_safeport_gate_a import run_cases
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases, verify_linked_source
import test_m19_p2d_l2_first_bind_gate_a as l2_gate
from m19_s1_agsp_bank import put_capture

ROOT=Path(__file__).resolve().parents[1]
GROUP,INTUI,DOS,NAME=0x50000,0x260000,0x290000,0x149400
INFO0,INFO1=0x149000,0x149100

class Integrated(ContractMachine):
    def __init__(self,image,layout):
        tok,parts,_=unpack_ap20(image)
        sg=unpack_from('>H',parts[204],2)[0]
        super().__init__(parts[sg][len(DISPATCH_V2):],parts,layout)
        self.raw=(ROOT/'tests/proto/agsp_capture/AGSP_CAPTURE_320X256.iff').read_bytes()
        self.fixture_pixels,self.fixture_cmap=read_fixture()
        self.cmap=bytes(768)
        self.load_pixels(0,bytes(W*H))
        self.load_pixels(1,bytes(W*H))
        self.put32(STATE+32,0)
        self.put32(STATE+4,INTUI)
        self.uc.mem_write(DB,bytes(48))
        self.put32(SB0+4,INFO0)
        self.put32(SB1+4,INFO1)
        self.uc.mem_write(GROUP,parts[142])
        self.uc.mem_write(NAME,b'\0\x08test.iff')
        self.phase='double'
        self.ports=0
        self.disp_ready=False
        self.lib_open=False
        self.file_open=False
        self.cursor=0
        self.palette_calls=0
        self.swap_calls=0
        self.writes=0
        self.iff_entries={}
        api={r['name']:r for r in walk_tokens(tok)}
        for n,name in enumerate(('aga double buffer','aga iff load')):
            entry=api[name]['function']
            stub=parts[entry]
            group,offset=unpack_from('>HH',stub,2)
            assert stub.startswith(RBSR) and group==142
            pc=GROUP-0x100+n*0x20
            if layout=='runtime':
                raw=pack('>Hh',0x6100,GROUP-(pc+2))+stub[4:]
            else:
                raw=pack('>HIH',0x4eb9,GROUP,offset)+b'\x4e\x75'
            self.uc.mem_write(pc,raw)
            self.iff_entries[name]=pc
        for base,offsets in ((EXEC,(-666,-552,-414)),(INTUI,(-768,-780)),
                             (DOS,(-30,-42,-36)),(GFX,(-882,-270))):
            for off in offsets:
                self.uc.mem_write(base+off,b'\x4e\x75')
        self.uc.hook_add(UC_HOOK_MEM_WRITE,self.plane_write,begin=BPL_BASE,end=BPL_BASE+0xfffff)

    def plane_write(self,uc,access,addr,size,value,user):
        assert self.phase=='iff' and not self.get(DB+20)&1
        page=1-self.get(DB+8)
        assert any(BPL_BASE+(page*8+p)*0x10000<=addr and
                   addr+size<=BPL_BASE+(page*8+p)*0x10000+40*H
                   for p in range(8)), 'IFF wrote the wrong page'
        self.writes+=1

    def on_code(self,uc,address,size,user):
        d0=uc.reg_read(UC_M68K_REG_D0)
        d1=uc.reg_read(UC_M68K_REG_D1)
        a0=uc.reg_read(UC_M68K_REG_A0)
        a1=uc.reg_read(UC_M68K_REG_A1)
        result=0
        if address==EXEC-684 and self.phase=='double':
            assert d0==48 and d1==0x10001
            result=DB
        elif address==EXEC-666:
            assert self.phase=='double' and self.ports<2
            result=(SAFE,DISP)[self.ports]
            self.ports+=1
        elif address==INTUI-768:
            assert self.phase=='double' and a0==SCREEN and a1==0 and d0 in (1,2)
            result=(SB0,SB1)[d0-1]
        elif address==INTUI-780:
            assert self.phase=='swap' and a0==SCREEN
            assert a1==(SB1 if self.get(DB+8)==0 else SB0)
            self.swap_calls+=1
            result=1
        elif address==EXEC-372 and a0==DISP:
            assert self.phase=='swap' and self.get(DB+20)&2
            result=MSG+4 if self.disp_ready else 0
            self.disp_ready=False
        elif address==EXEC-552:
            assert self.read(a1,12)==b'dos.library\0' and not self.lib_open
            self.lib_open=True
            result=DOS
        elif address==EXEC-414:
            assert a1==DOS and self.lib_open and not self.file_open
            self.lib_open=False
        elif address==DOS-30:
            assert self.lib_open and self.read(d1,9)==b'test.iff\0'
            assert uc.reg_read(UC_M68K_REG_D2)==1005 and not self.file_open
            self.file_open=True
            self.cursor=0
            result=7
        elif address==DOS-42:
            assert self.file_open and d1==7
            ptr=uc.reg_read(UC_M68K_REG_D2)
            count=uc.reg_read(UC_M68K_REG_D3)
            data=self.raw[self.cursor:self.cursor+count]
            uc.mem_write(ptr,data)
            self.cursor+=len(data)
            result=len(data)
        elif address==DOS-36:
            assert self.file_open and d1==7
            self.file_open=False
        elif address==GFX-882:
            assert not self.get(DB+20)&1 and a0==SCREEN+44
            assert self.get(a1)==256<<16 and self.get(a1+4+3072)==0
            self.cmap=bytes(self.get(a1+4+j*4)>>24 for j in range(768))
            self.palette_calls+=1
        elif address==GFX-270:
            pass
        else:
            return super().on_code(uc,address,size,user)
        self.volatile(uc,result)

    def double(self):
        assert self._invoke(self.iff_entries['aga double buffer'],0)==1
        assert self.get(STATE+32)==DB and self.get(DB+20)==0 and self.get(DB+8)==0
        assert (self.get(DB),self.get(DB+4),self.get(DB+12),self.get(DB+16))==(SB0,SB1,SAFE,DISP)
        for info in (INFO0,INFO1):
            assert self.get(info+22)==SAFE and self.get(info+54)==DISP
        self.phase='capture'

    def page(self,p):
        return tuple(self.read(BPL_BASE+(p*8+i)*0x10000,40*H) for i in range(8))

    def iff(self):
        self.phase='iff'
        front=self.get(DB+8)
        before=self.page(front)
        assert self._invoke(self.iff_entries['aga iff load'],NAME)==1
        assert self.page(front)==before
        assert self.page(1-front)==tuple(planar(self.fixture_pixels,W,H,8,40))
        assert self.cmap==self.fixture_cmap
        assert not self.file_open and not self.lib_open
        self.no_temps()
        self.phase='capture'

    def swap(self):
        self.phase='swap'
        before=self.get(DB+8)
        # Actual inherited native Swap core, source-owned unit 142 offset.
        assert self._invoke(GROUP+0x00BA2,0)==1
        assert self.get(DB+8)==1-before and self.get(DB+20)==3
        self.phase='capture'

def chain(image):
    for layout in ('runtime','compiled'):
        m=Integrated(image,layout)
        m.double()
        m.iff()
        assert m.select()==1 and m.get_sprite()==1
        want=m.expected()
        assert m.bank(29)==want and len(want)==192
        assert m.get_sprite(2,48,5,63,20)==0 and m.bank(29)==want
        m.swap()
        before=m.reads
        assert m.get_sprite(2)==0 and m.bank(29)==want
        assert m.reads==before and m.get(DB+20)==3
        m.ready=True
        assert m.get_sprite(2)==1 and m.get(DB+20)==2
        want=put_capture(want,2,bytes(W*H),W,H,13,5,16,16,m.cmap,0)
        assert m.bank(29)==want
        m.iff()
        m.disp_ready=True
        m.swap()
        m.ready=True
        assert m.get_sprite(3,80,5,95,20)==1 and m.get(DB+20)==2
        assert m.bank(29)==m.expected(want,3,80)
        assert m.unsafe_reads==0 and m.swap_calls==2 and m.palette_calls==2 and m.writes>0
        m.no_temps()
        print('P1I_ACTUAL_L2B_DB_IFF_SWAP_CAPTURE_PASS',layout,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',type=Path,required=True)
    p.add_argument('--historical',type=Path,required=True)
    p.add_argument('--tested-native',type=Path,required=True)
    a=p.parse_args()
    for key in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[key]=str(a.historical)
    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    image,meta=build_s1p1i(a.vasm)
    _,parts,_=unpack_ap20(image)
    native=parts[207][len(DISPATCH_V2):]
    assert native==a.tested_native.read_bytes()
    verify_linked_source(a.vasm,good)
    chain(image)
    prior,_=build_l2(a.vasm)
    assert run_pattern_cases(prior,image)==184
    assert run_cases(image,meta)==172
    l2_gate.IMAGE,l2_gate.META=image,meta
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
    assert result.wasSuccessful() and result.testsRun==10
    assert (ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()==active
    assert (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()==good
    print('S1P1I_FULL_GATE_A_PASS '+json.dumps(meta,sort_keys=True),flush=True)
    print('S1P1I_SOURCE_NATIVE_BASE64 '+base64.b64encode(native).decode('ascii'),flush=True)

if __name__=='__main__':
    main()
