#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Independent Sprite contract regression, exact source-assembled MC68020.
AP20 relocation models are not real AMOS Runtime or Compiler.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import os
from pathlib import Path
from struct import pack, unpack_from
from unicorn.m68k_const import *
from unicorn import UC_HOOK_MEM_READ
from active_library import S1P1H_SHA, S1P1I_SHA, P2DL2B_SHA, verify_s1p1i, verify_s1p1h, S1P2I_SHA, S1P2J_SHA, S1P2K_SHA, frozen_s1p1i
from compiler_relocation import unpack_ap20, repack_ap20, RBSR
from compiler_bridge_v2_probe import DISPATCH_V2
from m19_s1_agsp_bank import empty_bank, put_capture
from test_m19_s1p1e_get_sprite_cpu import GetMachine
from test_m19_s1p1c_amos_bank_commit import CODE, EXEC, CUR_BANKS, HEAD, ALT_HEAD
from test_m19_s1p1c_pipeline import DB, GFX, W, H, BPL_BASE

ROOT=Path(__file__).resolve().parents[1]
SAFE, DISP, MSG=0x148000,0x148100,0x148200
IFF_SHA='b39aa201dddd878405c828687973b3b874ae5d0f8cc1f09d1617dda7ff0628b9'

def read_fixture():
    """Decode the checked-in ByteRun1 ILBM independently of its generator."""
    raw=(ROOT/'tests/proto/agsp_capture/AGSP_CAPTURE_320X256.iff').read_bytes()
    assert sha256(raw).hexdigest()==IFF_SHA and raw[:4]==b'FORM' and raw[8:12]==b'ILBM'
    chunks={}
    at=12
    while at<len(raw):
        tag,size=unpack_from('>4sI',raw,at)
        at+=8
        chunks[tag]=raw[at:at+size]
        at+=size+(size&1)
    w,h,_,_,depth,mask,compression=unpack_from('>HHhhBBB',chunks[b'BMHD'])
    assert (w,h,depth,mask,compression)==(W,H,8,0,1)
    body=chunks[b'BODY']
    at=0
    pixels=bytearray(w*h)
    for y in range(h):
        for p in range(depth):
            row=bytearray()
            while len(row)<40:
                n=body[at];at+=1
                if n<128:
                    count=n+1
                    row.extend(body[at:at+count]);at+=count
                elif n>128:
                    row.extend(bytes([body[at]])*(257-n));at+=1
            assert len(row)==40
            for x in range(w):
                if row[x//8]&(128>>(x%8)):
                    pixels[y*w+x]|=1<<p
    assert at==len(body) and len(chunks[b'CMAP'])==768
    return bytes(pixels),chunks[b'CMAP']

class ContractMachine(GetMachine):
    def __init__(self,native,parts,layout,flags=0,ready=False,port=True,front=0):
        pixels,cmap=read_fixture()
        super().__init__(screen=pixels,safe=flags,front=front)
        self.cmap=cmap
        self.load_pixels(front,bytes(W*H))
        self.put32(DB+12,SAFE if port else 0)
        self.put32(DB+16,DISP)
        self.ready=ready
        self.safe_polls=0
        self.unsafe_reads=0
        self.reads=0
        self.mutate_on_alloc=None
        self.mutate_on_publish=None
        self.list_alloc_flags=[]
        self.uc.mem_write(EXEC-372,b'\x4e\x75')
        self.code=DISPATCH_V2+native
        self.uc.mem_write(CODE,self.code)
        self.entries={}
        for n,entry in enumerate((204,206)):
            stub=parts[entry]
            group,offset=unpack_from('>HH',stub,2)
            assert stub[:2]==RBSR and stub[6:8]==b'\x4e\x75' and group==207
            if layout=='runtime':
                pc=CODE-sum(map(len,parts[entry:207]))
                self.uc.mem_write(pc,pack('>Hh',0x6100,CODE-(pc+2))+stub[4:])
            else:
                assert layout=='compiled'
                pc=CODE-0x100+n*0x20
                self.uc.mem_write(pc,pack('>HIH',0x4eb9,CODE,offset)+b'\x4e\x75')
            self.entries[entry]=pc
        self.uc.hook_add(UC_HOOK_MEM_READ,self.plane_read,begin=BPL_BASE,end=BPL_BASE+0xfffff)

    def plane_read(self,uc,access,address,size,value,user):
        self.reads+=1
        if self.get(DB+20)&1:self.unsafe_reads+=1

    def select(self,bank=29):
        return self._invoke(self.entries[204],bank)

    def get_sprite(self,ident=1,x1=13,y1=5,x2=28,y2=20,pen=0):
        return self._invoke(self.entries[206],pen,(y2,x2,y1,x1,ident))

    def volatile(self,uc,result=0):
        uc.reg_write(UC_M68K_REG_D0,result)
        uc.reg_write(UC_M68K_REG_D1,0xdead1001)
        uc.reg_write(UC_M68K_REG_A0,0xdead2000)
        uc.reg_write(UC_M68K_REG_A1,0xdead3000)

    def on_code(self,uc,address,size,user):
        # L2b: bit0 pending, GetMsg once, do NOT consume Disp.
        if address==EXEC-372:
            assert uc.reg_read(UC_M68K_REG_A0)==SAFE and self.get(DB+20)&1
            self.safe_polls+=1
            result=MSG if self.ready else 0
            self.ready=False
            self.volatile(uc,result)
            return
        if address==EXEC-684 and self.mutate_on_alloc:
            change=self.mutate_on_alloc
            self.mutate_on_alloc=None
            change(self)
        if address in (EXEC-534,EXEC-684,EXEC-690,GFX-228,GFX-900):
            super().on_code(uc,address,size,user)
            result=uc.reg_read(UC_M68K_REG_D0) if address in (EXEC-534,EXEC-684) else 0
            self.volatile(uc,result)
            return
        if CODE<=address<CODE+len(self.code) and self.read(address,2)==b'\xfe\x11':
            site=self.read(address,6)
            assert site[:4]==b'\xfe\x11\xf7\x00'
            ident=unpack_from('>H',site,4)[0]
            self.calls.append(ident)
            # Independent AMOS365 +Lib.s/+B.s/+CLib.s bank ABI model.
            if ident==797:
                self.last_lookup=uc.reg_read(UC_M68K_REG_D0)
                node=self.bynum(self.last_lookup)
                ptr=node+24 if node else 0
                uc.reg_write(UC_M68K_REG_A0,ptr)
                uc.reg_write(UC_M68K_REG_A1,ptr)
                uc.reg_write(UC_M68K_REG_D1,node)
                if node:uc.reg_write(UC_M68K_REG_D0,self.word(node+12))
            elif ident==91:
                if self.mutate_on_publish:
                    change=self.mutate_on_publish
                    self.mutate_on_publish=None
                    change(self)
                cell=uc.reg_read(UC_M68K_REG_A0)
                length=uc.reg_read(UC_M68K_REG_D0)
                flags=uc.reg_read(UC_M68K_REG_D1)
                assert flags in (0x10001,0x10003)
                self.list_alloc_flags.append(flags)
                node=0
                if not self.alloc_fail:
                    node=self.allocate(length+8)
                    self.put32(node,self.get(cell))
                    self.put32(node+4,length)
                    self.put32(cell,node)
                uc.reg_write(UC_M68K_REG_A1,node)
                uc.reg_write(UC_M68K_REG_D0,node)
                uc.reg_write(UC_M68K_REG_D1,length)
            elif ident==819:
                node=self.bynum(self.last_lookup)
                assert node
                self.notes.append(node)
            elif ident==93:
                cell=uc.reg_read(UC_M68K_REG_A0)
                node=uc.reg_read(UC_M68K_REG_A1)
                assert self.get(cell)==node and node in self.allocations
                self.put32(cell,self.get(node))
                del self.allocations[node]
                self.freed.append(node)
            else:raise AssertionError(('unknown AMOS Main call',ident))
            uc.reg_write(UC_M68K_REG_PC,address+6)
            return
        return super().on_code(uc,address,size,user)

    def expected(self,old=None,ident=1,x=13):
        return put_capture(empty_bank() if old is None else old,ident,self.pixels,W,H,x,5,16,16,self.cmap,0)

def verify_frozen(native):
    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    if sha256(active).hexdigest() in (S1P2I_SHA,S1P2J_SHA,S1P2K_SHA):
        active=frozen_s1p1i(active,good)
    digest=sha256(active).hexdigest()
    assert digest in (S1P1H_SHA,S1P1I_SHA)
    assert sha256(good).hexdigest()==P2DL2B_SHA
    tok,parts,title=unpack_ap20(active)
    if digest==S1P1I_SHA:
        verify_s1p1i(active,good)
        # Recover the historical negative oracle using exact assembled P1h source.
        parts=parts[:207]+[DISPATCH_V2+native]
        historical=repack_ap20(active,tok,parts,title.replace(b'S1-P1i',b'S1-P1h'))
    else:
        historical=active
    verify_s1p1h(historical,good)
    assert len(parts)==208 and parts[207]==DISPATCH_V2+native
    assert parts[:203]==unpack_ap20(good)[1]
    return parts

def switch_owner(m):
    m.put32(ALT_HEAD,m.get(HEAD))
    m.put32(CUR_BANKS,ALT_HEAD)

def bump_generation(m):
    old=m.bynum(29)+24
    m.put32(old+24,m.get(old+24)+1)

def historical(native,parts):
    for layout in ('runtime','compiled'):
        m=ContractMachine(native,parts,layout,flags=0)
        assert m.select()==1 and m.get_sprite()==0 and m.bank(29)==empty_bank()
        m.no_temps()
        m=ContractMachine(native,parts,layout,flags=3)
        assert m.select()==1 and m.get_sprite()==1 and m.safe_polls==0 and m.unsafe_reads>0
        m.no_temps()
        m=ContractMachine(native,parts,layout,flags=1)
        assert m.select()==1 and m.select(4)==0 and m.get_sprite()==1
        m.no_temps()
        m=ContractMachine(native,parts,layout,flags=1)
        assert m.select()==1
        switch_owner(m)
        assert m.get_sprite()==1
        m.no_temps()
        m=ContractMachine(native,parts,layout,flags=1)
        assert m.select()==1
        m.mutate_on_publish=bump_generation
        assert m.get_sprite()==1
        m.no_temps()
        print('P1H_NEGATIVE_ORACLE_PASS',layout,
              'fresh-buffer refusal, pending-read, stale selection, owner drift, generation drift',flush=True)

def candidate(native,parts):
    cases=0
    for layout in ('runtime','compiled'):
        for flags,ready,port,success,polls,left in (
            (0,False,True,1,0,0),(2,False,True,1,0,2),
            (3,True,True,1,1,2),(3,False,True,0,1,3),
            (3,False,False,0,0,3)):
            for front in (0,1):
                m=ContractMachine(native,parts,layout,flags,ready,port,front)
                assert m.select()==1
                before=m.bank(29)
                assert m.get_sprite()==success,(layout,flags,ready,port,front)
                assert m.bank(29)==(m.expected() if success else before)
                assert m.safe_polls==polls and m.get(DB+20)==left
                assert m.unsafe_reads==0
                if not success:assert m.reads==0 and len(m.notes)==1
                m.no_temps()
                cases+=1
        m=ContractMachine(native,parts,layout)
        assert m.select()==1 and m.get_sprite()==1
        before=m.bank(29)
        assert m.get_sprite(2,48,5,63,20)==0 and m.bank(29)==before
        want=m.expected(before,2,80)
        assert m.get_sprite(2,80,5,95,20)==1 and m.bank(29)==want
        want=m.expected(want,1,80)
        assert m.get_sprite(1,80,5,95,20)==1 and m.bank(29)==want
        assert m.select(4)==0 and m.get_sprite()==0 and m.bank(29)==want
        m.no_temps()
        cases+=1
        m=ContractMachine(native,parts,layout)
        assert m.select()==1
        switch_owner(m)
        assert m.get_sprite()==0 and m.bank(29)==empty_bank()
        m.no_temps()
        cases+=1
        for attr in ('mutate_on_alloc','mutate_on_publish'):
            for drift in (switch_owner,bump_generation):
                m=ContractMachine(native,parts,layout)
                assert m.select()==1
                setattr(m,attr,drift)
                assert m.get_sprite()==0 and len(m.notes)==1,(attr,drift.__name__)
                assert len(m.bank(29))==32
                m.no_temps()
                cases+=1
        for fail_at in (1,2):
            m=ContractMachine(native,parts,layout)
            assert m.select()==1
            m.fail_temp_at=fail_at
            assert m.get_sprite()==0 and m.bank(29)==empty_bank()
            m.no_temps()
            cases+=1
        m=ContractMachine(native,parts,layout)
        assert m.select()==1
        m.put16(m.bynum(29)+12,3)
        assert m.get_sprite()==1 and m.word(m.bynum(29)+12)==3
        assert m.list_alloc_flags[-1]==0x10003
        m.no_temps()
        cases+=1
    print('P1I_CONTRACT_GATE_A_PASS',cases,'full AP20 models, fixture, safe, ownership, drift, allocations',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--historical',type=Path,required=True)
    p.add_argument('--candidate',type=Path)
    a=p.parse_args()
    raw=a.historical.read_bytes()
    os.environ['AGSP_GET_BIN']=str(a.historical)
    os.environ['AGSP_PUBLISH_BIN']=str(a.historical)
    os.environ['AGSP_PIPELINE_BIN']=str(a.historical)
    parts=verify_frozen(raw)
    historical(raw,parts)
    if a.candidate:candidate(a.candidate.read_bytes(),parts)

if __name__=='__main__':
    main()
