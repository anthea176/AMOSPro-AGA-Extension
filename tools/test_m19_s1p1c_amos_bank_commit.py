#!/usr/bin/env python3
"""S1-P1c MC68020 bank publication, real vasm bytes and AMOS Main mock.

Executes FE11 F700 AMOS_MAIN pseudo-call sites through emulated callbacks.
The same P2d constants/structures are used; this is a CPU Gate A
component test, NOT a real AP20 token, DOS Save, WinUAE or Compiler.
"""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack, pack_into, unpack_from
import unittest

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2,
    UC_M68K_REG_A3, UC_M68K_REG_A4, UC_M68K_REG_A5,
    UC_M68K_REG_A6, UC_M68K_REG_A7, UC_M68K_REG_D0,
    UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
)
from m19_s1_agsp_bank import empty_bank, put_capture, parse_payload

CODE=0x20000
STOP=0x30000
AMOS=0x90000
REQUEST=0x140000
SOURCE=0x150000
EXEC=0x280000
STACK=0x2c0000
HEAD=AMOS+0x5ea
MAX_ALLOC=0x270000
REGS=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D4,
      UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
      UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,
      UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)
PSEUDO={91:'Lst.Cree',93:'Lst.Del',797:'Bnk.GetAdr',819:'Bnk.Change'}


def fixture(seed=0, bank=10):
    img=bytes((0,25,67,128)[(x+y+seed)%4] for y in range(16) for x in range(16))
    cm=bytearray(256*3)
    for i,color in ((25,(255,80,56)),(67,(237,198,66)),(128,(61,199,182))):
        cm[i*3:i*3+3]=bytes(color)
    return put_capture(empty_bank(),1,img,16,16,0,0,16,16,bytes(cm),0,mode='s1')


class Machine:
    def __init__(self, old=None, other=False, foreign=False,
                 alloc_fail=False, race=False):
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x400000)
        self.code=Path(os.environ['AGSP_PUBLISH_BIN']).read_bytes()
        assert 100 < len(self.code) < 20000
        self.uc.mem_write(CODE,self.code)
        self.uc.mem_write(EXEC-534,b'\x4e\x75')
        self.uc.hook_add(UC_HOOK_CODE,self.on_code)
        self.allocations={}
        self.freed=[]
        self.created=[]
        self.notes=[]
        self.calls=[]
        self.newptr=0x210000
        self.alloc_fail=alloc_fail
        self.race=race
        self.race_done=False
        self.initial_old=old
        self.old_node=None
        self.other_node=None
        self.put32(HEAD,0)
        if other:
            self.other_node=self.make_bank(11,b"DATA    ",bytes(range(32)))
        if old is not None:
            self.old_node=self.make_bank(10,b"FOREIGN " if foreign else b"AGASPRT ",old)

    def get(self,a):return unpack_from('>I',self.uc.mem_read(a,4))[0]
    def word(self,a):return unpack_from('>H',self.uc.mem_read(a,2))[0]
    def put32(self,a,v):self.uc.mem_write(a,pack('>I',v))
    def put16(self,a,v):self.uc.mem_write(a,pack('>H',v))
    def read(self,a,n):return bytes(self.uc.mem_read(a,n))

    def allocate(self,size):
        a=self.newptr
        self.newptr+=((size+15)//16)*16+0x100
        assert self.newptr<MAX_ALLOC
        self.uc.mem_write(a,bytes(size))
        self.allocations[a]=size
        self.created.append(a)
        return a

    def make_bank(self,num,name,payload,flags=1):
        addr=self.allocate(24+len(payload))
        self.put32(addr,self.get(HEAD))
        self.put32(addr+4,len(payload)+16)
        self.put32(addr+8,num)
        self.put16(addr+12,flags)
        self.put16(addr+14,0)
        self.uc.mem_write(addr+16,name)
        self.uc.mem_write(addr+24,payload)
        self.put32(HEAD,addr)
        return addr

    def nodes(self):
        out=[];p=self.get(HEAD)
        for _ in range(100):
            if p==0:return out
            assert p not in out,'loop in AMOS bank list'
            out.append(p)
            p=self.get(p)
        raise AssertionError('AMOS list scanning exceeded 100')

    def bynum(self,num):
        for p in self.nodes():
            if self.get(p+8)==num:return p
        return 0

    def on_code(self,uc,address,size,user):
        if address==EXEC-534:
            a=uc.reg_read(UC_M68K_REG_A1)
            uc.reg_write(UC_M68K_REG_D0,1 if (0<a<0x3FFFFF) else 0)
            return
        if not CODE<=address<CODE+len(self.code):return
        op=self.read(address,2)
        if op != b'\xfe\x11':return
        site=self.read(address,6)
        assert site[:4]==b'\xfe\x11\xf7\x00',f'unknown pseudo {site.hex()}'
        ident=unpack_from('>H',site,4)[0]
        assert ident in PSEUDO,f'not recognized pseudo-call {ident}'
        self.calls.append(ident)
        if ident==797:
            num=uc.reg_read(UC_M68K_REG_D0)
            p=self.bynum(num)
            if self.race and self.calls.count(797)==2 and not self.race_done:
                # Simulate an externally replaced bank-list head during alloc.
                self.race_done=True
                self.put32(HEAD,0)
                p=0
            uc.reg_write(UC_M68K_REG_A0,p+24 if p else 0)
        elif ident==91:
            if self.alloc_fail:
                uc.reg_write(UC_M68K_REG_D0,0)
                uc.reg_write(UC_M68K_REG_A1,0)
            else:
                list_head=uc.reg_read(UC_M68K_REG_A0)
                length=uc.reg_read(UC_M68K_REG_D0)
                assert uc.reg_read(UC_M68K_REG_D1)==0x00010001
                addr=self.allocate(length+8)
                self.put32(addr,self.get(list_head))
                self.put32(addr+4,length)
                self.put32(list_head,addr)
                uc.reg_write(UC_M68K_REG_D0,addr)
                uc.reg_write(UC_M68K_REG_A1,addr)
        elif ident==819:
            self.notes.append((self.bynum(10),self.old_node in self.allocations))
            assert self.bynum(10),'notify must happen only after publish'
            assert self.old_node is None or self.old_node in self.allocations
        elif ident==93:
            list_head=uc.reg_read(UC_M68K_REG_A0)
            node=uc.reg_read(UC_M68K_REG_A1)
            assert self.get(list_head)==node
            self.put32(list_head,self.get(node))
            assert node in self.allocations
            del self.allocations[node]
            self.freed.append(node)
        uc.reg_write(UC_M68K_REG_PC,address+6)

    def execute(self,payload,bank=10,size=None,request_bad=None):
        uc=self.uc
        self.uc.mem_write(SOURCE,payload)
        req=bytearray(pack('>4I',SOURCE,len(payload) if size is None else size,bank,0))
        for off,value in (request_bad or {}).items():pack_into('>I',req,off,value)
        uc.mem_write(REQUEST,bytes(req))
        before_src=self.read(SOURCE,len(payload))
        for n,reg in enumerate(REGS):uc.reg_write(reg,0x55008000+n)
        saved={reg:uc.reg_read(reg) for reg in REGS}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A0,REQUEST)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        uc.mem_write(STACK,pack('>I',STOP))
        uc.emu_start(CODE,STOP,count=3_000_000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in saved.items()),'AMOS ABI register clobber'
        assert uc.reg_read(UC_M68K_REG_D2)==0
        assert self.read(SOURCE,len(payload))==before_src,'input overwritten'
        return uc.reg_read(UC_M68K_REG_D3)

    def bank(self,num):
        p=self.bynum(num)
        if p==0:return None
        count=self.get(p+4)-16
        return self.read(p+24,count)


@unittest.skipUnless(os.getenv('AGSP_PUBLISH_BIN'), 'requires VASM MC68020 raw binary')
class AGSPPublisherCPU(unittest.TestCase):
    def test_insert_first_canonical_amos_data_node(self):
        m=Machine()
        data=fixture()
        self.assertEqual(m.execute(data),1)
        self.assertEqual(m.bank(10),data)
        p=m.bynum(10)
        self.assertEqual(m.get(p+4),len(data)+16)
        self.assertEqual(m.word(p+12),1)
        self.assertEqual(m.read(p+16,8),b'AGASPRT ')
        self.assertEqual(m.notes,[(p,False)])
        self.assertEqual(m.freed,[])
        self.assertEqual(m.calls,[797,91,797,819])

    def test_insert_before_unrelated_bank_preserves_list(self):
        m=Machine(other=True)
        before=m.bank(11)
        self.assertEqual(m.execute(fixture()),1)
        self.assertEqual([m.get(p+8) for p in m.nodes()],[10,11])
        self.assertEqual(m.bank(11),before)
        self.assertEqual(len(m.notes),1)

    def test_replace_old_bank_callback_before_free_and_other_untouched(self):
        old=fixture()
        new=fixture(seed=1)
        m=Machine(old=old,other=True)
        self.assertEqual(m.execute(new),1)
        self.assertEqual(m.bank(10),new)
        self.assertEqual(m.bank(11),bytes(range(32)))
        self.assertEqual(m.freed,[m.old_node])
        self.assertNotIn(m.old_node,m.allocations)
        self.assertEqual(len(m.notes),1)
        self.assertEqual(m.notes[0][1],True)
        self.assertEqual(m.calls,[797,91,797,819,93])

    def test_foreign_data_bank_is_refused_without_allocating(self):
        m=Machine(old=fixture(),foreign=True)
        before=m.bank(10)
        self.assertEqual(m.execute(fixture(seed=1)),0)
        self.assertEqual(m.bank(10),before)
        self.assertEqual(m.notes,[])
        self.assertEqual(m.freed,[])
        self.assertEqual(m.calls,[797])

    def test_alloc_failure_retains_existing_bank_and_no_notification(self):
        m=Machine(old=fixture(),alloc_fail=True)
        before=m.bank(10)
        self.assertEqual(m.execute(fixture(seed=1)),0)
        self.assertEqual(m.bank(10),before)
        self.assertEqual(m.notes,[])
        self.assertEqual(m.calls,[797,91])

    def test_head_race_rejects_and_cleans_only_staged_node(self):
        m=Machine(old=fixture(),race=True)
        old=m.bank(10)
        self.assertEqual(m.execute(fixture(seed=1)),0)
        self.assertEqual(m.notes,[])
        self.assertEqual(len(m.freed),1)
        self.assertNotEqual(m.freed[0],m.old_node)
        self.assertIn(m.old_node,m.allocations)
        self.assertEqual(m.calls,[797,91,797,93])

    def test_bad_payloads_never_allocate(self):
        good=fixture()
        cases=[
            (b'AGBO'+good[4:],None,None),
            (good[:4]+b'\x00\x02'+good[6:],None,None),
            (good,None,{8:4}),
            (good,None,{8:65536}),
            (good,None,{12:1}),
            (good[:-2],None,None),
        ]
        for raw,size,bad in cases:
            with self.subTest(case=(len(raw),size,bad)):
                m=Machine(old=fixture())
                original=m.bank(10)
                self.assertEqual(m.execute(raw,size=size,request_bad=bad),0)
                self.assertEqual(m.bank(10),original)
                self.assertEqual(m.notes,[])
                self.assertEqual(m.freed,[])

    def test_no_phantom_missing_bank_races(self):
        m=Machine(race=True)
        self.assertEqual(m.execute(fixture()),0)
        self.assertEqual(m.notes,[])
        self.assertEqual(len(m.freed),1)
        self.assertNotIn(m.freed[0],m.allocations)

if __name__=='__main__':
    unittest.main(verbosity=2)
