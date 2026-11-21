#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2a native paired P0f checked reads, REAL 68020; no public token or Lib.

Two source-disjoint V2 placements. Calls the REAL P0f identity_check routine
with mocked Bnk.GetAdr / Exec services, verifies atomic 48-byte output and
no selection changes, reads after bank stamp mismatch and Bob Off, ABI and
canary protection. Does not resolve AGBO images/masks or invoke P2a kernel.
"""
from __future__ import annotations
from struct import unpack
from hashlib import sha256
import unittest
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from build_m19_p0c_screen_close_in_memory import build as build_p0c
from test_m19_p0f_public_bound_native import BoundMachine
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from m19_p2a_pair_checked_read_emit import emit_p2a_pair_checked_read,PAIR_BYTES
from m19_p0f_object_identity_emit import emit_object_identity

OUT=0x5c800
CANARY=bytes.fromhex('d0a5face')*(PAIR_BYTES//4)
GUARD=b'\xaa'*16
BASES={'interpreted':0x240000,'compiled':0x340000}


class PairReadMachine(BoundMachine):
    def __init__(self,layout):
        base,_=build_p0c()
        super().__init__(base,layout)
        self.pair_code,self.pair_labels=emit_p2a_pair_checked_read()
        self.pair_entry=BASES[layout]
        self.uc.mem_write(self.pair_entry,self.pair_code)
        self.checked_entry=self.identity_base+self.identity_labels['identity_check_entry']
        self.check_calls=0
        self.uc.hook_add(UC_HOOK_CODE,self._checked,begin=self.checked_entry,end=self.checked_entry)
        for n in (10,11):
            assert self.run_select(n)==1
            if n==10: assert self.run_get(1,4,5,20,8)==1
            else: assert self.run_get(1,7,8,16,15)==1
        assert self.run_select(10)==1
        self.activate_aga_state()
        assert self.public('bob',ident=1,x=103,y=72,image=1)==1
        assert self.run_select(11)==1
        assert self.public('bob',ident=2,x=-12,y=31,image=1)==1
        assert self.run_select(10)==1

    def selected_triple(self):
        # P0e/P0f BoundMachine predates the P0j helper selected_triple().
        # Inspect the existing 12-byte BOBS selected-bank shadow read-only.
        return bytes(self.uc.mem_read(self.entry+self.labels['bank_active_state'],12))

    def _checked(self,uc,address,size,user):
        self.check_calls+=1

    def pair_read(self,a=1,b=2,*,owner=AMOS,output=OUT,callback=None):
        if callback is None: callback=self.checked_entry
        uc=self.uc
        uc.mem_write(OUT-16,GUARD)
        uc.mem_write(OUT,CANARY)
        uc.mem_write(OUT+PAIR_BYTES,GUARD)
        for i,r in enumerate(DR):uc.reg_write(r,0x12300000+i)
        for i,r in enumerate(AR[:7]):uc.reg_write(r,0x30000+i*0x100)
        uc.reg_write(DR[0],a&0xffffffff)
        uc.reg_write(DR[1],b&0xffffffff)
        uc.reg_write(AR[1],output)
        uc.reg_write(AR[4],callback)
        uc.reg_write(AR[5],owner)
        old={r:uc.reg_read(r) for r in DR+AR[:7] if r not in (DR[2],DR[3])}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.check_calls=0
        self.uc.emu_start(self.pair_entry,STOP,count=10000000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0 and self.d(3) in (0,1)
        for reg,old_value in old.items():
            assert uc.reg_read(reg)==old_value,('pair adapter broke AMOS ABI',reg)
        assert bytes(uc.mem_read(OUT-16,16))==GUARD
        assert bytes(uc.mem_read(OUT+PAIR_BYTES,16))==GUARD
        return self.d(3),bytes(uc.mem_read(OUT,PAIR_BYTES)),self.check_calls


class PairCheckedReadNative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,cls.labels=emit_p2a_pair_checked_read()

    def test_01_emitter_and_original_p0f_callback(self):
        self.assertEqual(emit_p2a_pair_checked_read(),(self.source,self.labels))
        self.assertEqual(self.labels['p2a_pair_checked_read_entry'],0)
        decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        disassembled=list(decoder.disasm(self.source,0x240000))
        self.assertEqual(sum(i.size for i in disassembled),len(self.source))
        self.assertFalse(any(x.mnemonic.startswith('dc.') for x in disassembled))
        self.assertEqual(self.source.count(bytes.fromhex('4e94')),2)
        self.assertTrue(emit_object_identity()[0])
        print('P2A_PAIR_READ_MC68020',len(self.source),sha256(self.source).hexdigest(),flush=True)

    def test_02_two_bank_checked_pair_and_unmodified_state(self):
        for layout in BASES:
            m=PairReadMachine(layout)
            state=(m.table(),m.shadows(),m.selected_triple())
            result,data,calls=m.pair_read()
            self.assertEqual((result,calls),(1,2))
            self.assertEqual(unpack('>6I',data[:24]),(10,1,103,72,1,0))
            self.assertEqual(unpack('>6I',data[24:]),(11,1,(-12)&0xffffffff,31,1,0))
            self.assertEqual((m.table(),m.shadows(),m.selected_triple()),state)
            result,swap,calls=m.pair_read(2,1)
            self.assertEqual((result,calls),(1,2))
            self.assertEqual(swap,data[24:]+data[:24])
            self.assertEqual((m.table(),m.shadows(),m.selected_triple()),state)

    def test_03_second_bank_stale_does_not_publish_first(self):
        for layout in BASES:
            m=PairReadMachine(layout)
            node=m.find(11)
            gen=m.get(node+24+24)
            old_state=(m.table(),m.shadows())
            m.put(node+24+24,gen+1)
            result,data,calls=m.pair_read()
            self.assertEqual((result,data,calls),(0,CANARY,2))
            self.assertEqual((m.table(),m.shadows()),old_state)
            m.put(node+24+24,gen)
            self.assertEqual(m.pair_read()[0],1)

    def test_04_first_bank_stale_or_missing(self):
        for layout in BASES:
            m=PairReadMachine(layout)
            node=m.find(10)
            gen=m.get(node+24+24)
            m.put(node+24+24,gen+1)
            self.assertEqual(m.pair_read(),(0,CANARY,1))
            m.put(node+24+24,gen)
            head=m.get(HEAD)
            m.put(HEAD,0)
            self.assertEqual(m.pair_read(),(0,CANARY,1))
            m.put(HEAD,head)
            self.assertEqual(m.pair_read()[0],1)

    def test_05_off_bob_foreign_owner_and_recovery(self):
        for layout in BASES:
            m=PairReadMachine(layout)
            self.assertEqual(m.pair_read(owner=AMOS+0x1000),(0,CANARY,1))
            assert m.public('off',ident=2)==1
            self.assertEqual(m.pair_read(),(0,CANARY,2))
            assert m.public('bob',ident=2,x=-12,y=31,image=1)==1
            self.assertEqual(m.pair_read()[0],1)

    def test_06_invalid_id_pair_and_callback_rejected(self):
        m=PairReadMachine('interpreted')
        for a,b in ((0,2),(1,65),(1,1),(65,65),(-1,2)):
            self.assertEqual(m.pair_read(a,b),(0,CANARY,0))
        for cb in (0,1,3):
            self.assertEqual(m.pair_read(callback=cb),(0,CANARY,0))
        for out in (0,OUT+1):
            self.assertEqual(m.pair_read(output=out),(0,CANARY,0))

    def test_07_bad_exec_output_endpoint(self):
        for layout in BASES:
            m=PairReadMachine(layout)
            for bad in (OUT,OUT+PAIR_BYTES-1):
                m.reject_type=bad
                self.assertEqual(m.pair_read(),(0,CANARY,0))
                m.reject_type=None
            self.assertEqual(m.pair_read()[0],1)

    def test_08_real_cpu_020_guard_in_p0f(self):
        for layout in BASES:
            m=PairReadMachine(layout)
            m.uc.mem_write(EXEC+0x128,b'\0\0')
            self.assertEqual(m.pair_read(),(0,CANARY,1))
            m.uc.mem_write(EXEC+0x128,b'\0\x02')
            self.assertEqual(m.pair_read()[0],1)

    def test_09_repeated_native_reads_no_state_mutation(self):
        for layout in BASES:
            m=PairReadMachine(layout)
            state=(m.table(),m.shadows(),m.selected_triple())
            for _ in range(12):
                self.assertEqual(m.pair_read()[0],1)
            self.assertEqual((m.table(),m.shadows(),m.selected_triple()),state)


if __name__=='__main__':
    unittest.main(verbosity=2)
