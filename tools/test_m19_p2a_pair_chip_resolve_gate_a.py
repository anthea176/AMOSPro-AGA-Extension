#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2a real 68020 P0f+P0j Chip pair bridge, independent V2 layouts.

Uses source-emitted *actual* P0f checked Bobs AND P0j-b3 resolver
under Unicorn MC68020 with mocked AMOS/Exec services. This is NOT a
real WinUAE, AP20 integration or Compiler test.
"""
from __future__ import annotations
from hashlib import sha256
from struct import unpack
import unittest

from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m19_p0j_explicit_image_resolve_gate_a import ResolverMachine
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from m19_p0a_multi_bob_abk import parse_payload
from m19_p2a_pair_chip_resolve_emit import (
    emit_p2a_pair_chip_resolve,OUTPUT_BYTES,PREVIOUS)
from m19_p0j_explicit_image_resolve_emit import emit_explicit_bank_image_resolve
from m19_p0f_object_identity_emit import emit_object_identity

OUT=0x5cb00
CANARY=b'K'*OUTPUT_BYTES
GUARD=b'Q'*16
BASES={'interpreted':0x300000,'compiled':0x350000}


class PairChipMachine(ResolverMachine):
    def __init__(self,layout,*,stage_banks=(10,11),with_mask=True):
        source,_=build_p0c()
        super().__init__(source,layout)
        self.unit,self.pair_labels=emit_p2a_pair_chip_resolve()
        self.pair_base=BASES[layout]
        self.uc.mem_write(self.pair_base,self.unit)
        self.checked_entry=self.identity_base+self.identity_labels['identity_check_entry']
        self.resolve_entry=self.entry+self.labels['explicit_image_resolve_entry']
        self.check_calls=0
        self.resolve_calls=0
        self.mutate_late=False
        self._mutated_generation=None
        self.uc.hook_add(UC_HOOK_CODE,self._on_checked,
                         begin=self.checked_entry,end=self.checked_entry)
        self.uc.hook_add(UC_HOOK_CODE,self._on_resolve,
                         begin=self.resolve_entry,end=self.resolve_entry)
        assert self.run_select(10)==1
        assert self.run_get(1,4,5,20,8)==1
        assert self.run_select(11)==1
        assert self.run_get(1,7,8,16,15)==1
        assert self.run_select(10)==1
        if with_mask:
            assert self.mask(True,1,0)==1
        assert self.run_select(11)==1
        self.activate_aga_state()
        self.configure_real_state()
        assert self.run_select(10)==1
        assert self.public('bob',ident=1,image=1,x=27,y=41)==1
        assert self.run_select(11)==1
        assert self.public('bob',ident=2,image=1,x=33,y=43)==1
        for bank in stage_banks:
            assert self.stage(bank)==1
        self.baseline_selector=self.selected_triple()

    def _on_checked(self,uc,address,size,user):
        self.check_calls+=1

    def _on_resolve(self,uc,address,size,user):
        self.resolve_calls+=1
        if self.mutate_late and self.resolve_calls==2:
            genaddr=self.find(10)+24+24
            self._mutated_generation=(genaddr,self.get(genaddr))
            self.put(genaddr,self.get(genaddr)+1)

    def restore_mutation(self):
        if self._mutated_generation:
            addr,value=self._mutated_generation
            self.put(addr,value)
            self._mutated_generation=None
        self.mutate_late=False

    def chip_pair(self,a=1,b=2,*,owner=AMOS,output=OUT,
                  checked=None,resolver=None):
        if checked is None: checked=self.checked_entry
        if resolver is None: resolver=self.resolve_entry
        self.uc.mem_write(OUT-16,GUARD)
        self.uc.mem_write(OUT,CANARY)
        self.uc.mem_write(OUT+OUTPUT_BYTES,GUARD)
        for n,r in enumerate(DR):self.uc.reg_write(r,0x620000+n)
        for n,r in enumerate(AR[:7]):self.uc.reg_write(r,0x46000+n*256)
        self.uc.reg_write(DR[0],a&0xffffffff)
        self.uc.reg_write(DR[1],b&0xffffffff)
        self.uc.reg_write(AR[1],output)
        self.uc.reg_write(AR[4],checked)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[6],resolver)
        old={r:self.uc.reg_read(r) for r in DR+AR[:7] if r not in (DR[2],DR[3])}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.check_calls=0
        self.resolve_calls=0
        self.explicit_shadow_writes=[]
        self.in_explicit_lookup=True
        try:
            self.uc.emu_start(
                self.pair_base+self.pair_labels['p2a_pair_chip_resolve_entry'],
                STOP,count=30000000)
        finally:
            self.in_explicit_lookup=False
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0 and self.d(3) in (0,1)
        for reg,value in old.items():
            assert self.uc.reg_read(reg)==value,('P2a Chip pair ABI',reg)
        assert bytes(self.uc.mem_read(OUT-16,16))==GUARD
        assert bytes(self.uc.mem_read(OUT+OUTPUT_BYTES,16))==GUARD
        assert not self.explicit_shadow_writes,'P2a changed bank_active_state'
        return (self.d(3),bytes(self.uc.mem_read(OUT,OUTPUT_BYTES)),
                self.check_calls,self.resolve_calls)


class PairChipNative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native,cls.labels=emit_p2a_pair_chip_resolve()

    def test_01_emission_source_abi_and_pinned_callbacks(self):
        self.assertEqual((self.native,self.labels),emit_p2a_pair_chip_resolve())
        self.assertTrue(self.native.startswith(PREVIOUS))
        self.assertEqual(self.labels['p2a_pair_chip_resolve_entry'],len(PREVIOUS))
        self.assertEqual(self.native[len(PREVIOUS):].count(bytes.fromhex('4e96')),2)
        cap=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        part=self.native[len(PREVIOUS):]
        ins=list(cap.disasm(part,0x300000+len(PREVIOUS)))
        self.assertEqual(sum(i.size for i in ins),len(part))
        self.assertTrue(ins)
        self.assertFalse(any(i.mnemonic.startswith('dc.') for i in ins))
        self.assertTrue(emit_object_identity()[0])
        self.assertTrue(emit_explicit_bank_image_resolve()[0])
        print('P2A_CHIP_PAIR_MC68020',len(self.native),sha256(self.native).hexdigest(),flush=True)

    def test_02_two_banks_checked_and_chip_image_descriptors(self):
        for layout in BASES:
            m=PairChipMachine(layout)
            state=(m.table(),m.shadows(),m.baseline_selector,dict(m.chip_live))
            status,data,checks,resolves=m.chip_pair()
            self.assertEqual((status,checks,resolves),(1,4,2))
            for index,bank in enumerate((10,11)):
                ob,pl=data[index*60:index*60+24],data[index*60+24:index*60+60]
                meta=unpack('>6I',ob)
                self.assertEqual((meta[0],meta[1],meta[4],meta[5]),(bank,1,1,0))
                plane,mask,w,h,stride,depth,plane_bytes,chip,alloc=unpack('>9I',pl)
                source=parse_payload(m.bank_payload(bank)).image(1)
                self.assertEqual((w,h,stride,depth,plane_bytes),
                                 (source.width,source.height,source.stride,
                                  source.depth,source.stride*source.height))
                self.assertEqual(bool(mask),bool(source.mask))
                self.assertIn(chip,m.chip_live)
                self.assertEqual(m.chip_live[chip],alloc)
                self.assertTrue(chip<=plane<chip+alloc)
                self.assertEqual(bytes(m.uc.mem_read(plane,len(source.planes))),source.planes)
                if mask:
                    self.assertTrue(chip<=mask<chip+alloc)
                    self.assertEqual(bytes(m.uc.mem_read(mask,len(source.mask))),source.mask)
            self.assertEqual((m.table(),m.shadows(),m.selected_triple(),dict(m.chip_live)),state)
            status,swapped,checks,resolves=m.chip_pair(2,1)
            self.assertEqual((status,checks,resolves),(1,4,2))
            self.assertEqual(swapped,data[60:]+data[:60])

    def test_03_missing_second_chip_staging_atomic_refusal(self):
        for layout in BASES:
            m=PairChipMachine(layout,stage_banks=(10,))
            self.assertEqual(m.chip_pair(),(0,CANARY,2,2))
            self.assertEqual(m.selected_triple(),m.baseline_selector)
            self.assertEqual(m.stage(11),1)
            self.assertEqual(m.chip_pair()[0],1)

    def test_04_stale_first_second_generation_or_list(self):
        for layout in BASES:
            m=PairChipMachine(layout)
            for bank in (10,11):
                node=m.find(bank)
                offset=node+24+24
                gen=m.get(offset)
                m.put(offset,gen+1)
                status,data,checks,resolves=m.chip_pair()
                self.assertEqual((status,data),(0,CANARY))
                self.assertEqual(resolves,0)
                m.put(offset,gen)
            first=m.get(HEAD)
            m.put(HEAD,0)
            self.assertEqual(m.chip_pair()[0:2],(0,CANARY))
            m.put(HEAD,first)
            self.assertEqual(m.chip_pair()[0],1)

    def test_05_late_mutation_after_first_resolve_rejected_by_recheck(self):
        for layout in BASES:
            m=PairChipMachine(layout)
            m.mutate_late=True
            status,data,checks,resolves=m.chip_pair()
            self.assertEqual((status,data),(0,CANARY))
            self.assertEqual(resolves,2)
            self.assertGreaterEqual(checks,3)
            m.restore_mutation()
            self.assertEqual(m.chip_pair()[0],1)

    def test_06_inactive_wrong_owner_and_bad_pairs(self):
        m=PairChipMachine('interpreted')
        for a,b in ((0,2),(1,65),(1,1),(65,1),(-1,2)):
            self.assertEqual(m.chip_pair(a,b),(0,CANARY,0,0))
        self.assertEqual(m.chip_pair(owner=AMOS+0x1000)[0:2],(0,CANARY))
        assert m.public('off',ident=2)==1
        self.assertEqual(m.chip_pair()[0:2],(0,CANARY))
        assert m.public('bob',ident=2,image=1,x=33,y=43)==1
        self.assertEqual(m.chip_pair()[0],1)

    def test_07_invalid_private_callbacks_or_output(self):
        m=PairChipMachine('compiled')
        for checked,resolver in ((0,None),(1,None),(None,0),(None,3)):
            self.assertEqual(m.chip_pair(checked=checked,resolver=resolver),(0,CANARY,0,0))
        for bad in (0,OUT+1):
            self.assertEqual(m.chip_pair(output=bad),(0,CANARY,0,0))

    def test_08_68020_guard_and_repeat_no_mutation(self):
        for layout in BASES:
            m=PairChipMachine(layout)
            state=(m.table(),m.shadows(),m.baseline_selector,dict(m.chip_live))
            m.uc.mem_write(EXEC+0x128,b'\0\0')
            self.assertEqual(m.chip_pair()[0:2],(0,CANARY))
            m.uc.mem_write(EXEC+0x128,b'\0\x02')
            for _ in range(3):
                self.assertEqual(m.chip_pair()[0],1)
            self.assertEqual((m.table(),m.shadows(),m.selected_triple(),dict(m.chip_live)),state)


if __name__=='__main__':
    unittest.main(verbosity=2)
