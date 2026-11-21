#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A: ONE native MC68020 query calls P0f/P0j/P1b/P1d/collision.

Use actual source-generated native units under Unicorn, REAL AGBO
banks/Chip staging and private P0f/P0j callbacks. Amiga OS/AMOS services
remain simulated; this does NOT run a real AMOS program, AP20, WinUAE
or the actual Compiler. No public token, no new Lib.
"""
from __future__ import annotations
from hashlib import sha256
from random import Random
from struct import pack,pack_into
import unittest
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from test_m19_p2a_pair_hotspot020_gate_a import HotNativeMachine
from test_m19_p2a_pair_geometry020_gate_a import (
    W,H,SCREEN,LIMITS,SLOT,expect_geometry,NATIVE_BASE,COL_BASE)
from m19_p2a_bob_collision_model import Rect,collision
from m19_p2a_collision_query020_emit import emit_p2a_collision_query020

CB=0xa10000
CONTEXT=0xa10200
BASES={'interpreted':0x3f0000,'compiled':0x4f0000}

class NativeFullQuery(HotNativeMachine):
    def __init__(self,layout,hot10=(0,0),hot11=(0,0)):
        super().__init__(layout,hot10,hot11)
        self.querycode,self.querylabels=emit_p2a_collision_query020()
        self.querybase=BASES[layout]
        self.uc.mem_write(self.querybase,self.querycode)
        self.callbacks=[
            self.pair_base+self.pair_labels['p2a_pair_chip_resolve_entry'],
            self.checked_entry,self.resolve_entry,
            self.source_base,self.lookup_entry,
            NATIVE_BASE[layout],COL_BASE[layout]
        ]
        self.uc.mem_write(CB,pack('>7I',*self.callbacks))
        self.uc.mem_write(CONTEXT,pack('>2I',SCREEN,LIMITS))
        self._last_limit=bytes(65*SLOT.size)

    def os_call(self,uc,address,size,user):
        # The original source-only host stub considers only a synthetic
        # PUBLIC address range. A real allocated native STACK is valid Exec
        # memory: make that specific verified frame range TypeOfMem=PUBLIC.
        if address==EXEC-534 and STACK-4096<=self.a(1)<=STACK:
            return self._os_return(1)
        return super().os_call(uc,address,size,user)

    def query(self,mode=1,*,ids=(1,2),global_limit=None,local_limits=None,
              owner=AMOS,screen=(W,H),rawlimits=None,callbacks=None,
              context=CONTEXT,cbptr=CB):
        uc=self.uc
        if local_limits is None:local_limits={}
        uc.mem_write(SCREEN,pack('>2I',*screen))
        limits=bytearray(65*SLOT.size)
        if global_limit is not None:
            SLOT.pack_into(limits,0,global_limit.x,global_limit.y,
                           global_limit.right,global_limit.bottom)
        for k,rect in local_limits.items():
            SLOT.pack_into(limits,k*16,rect.x,rect.y,rect.right,rect.bottom)
        if rawlimits is not None:limits[:]=rawlimits
        uc.mem_write(LIMITS,bytes(limits))
        uc.mem_write(CONTEXT,pack('>2I',SCREEN,LIMITS))
        uc.mem_write(CB,pack('>7I',*(self.callbacks if callbacks is None else callbacks)))
        for i,reg in enumerate(DR):uc.reg_write(reg,0x71000000+i)
        for i,reg in enumerate(AR[:7]):uc.reg_write(reg,0x730000+i*0x100)
        uc.reg_write(DR[0],ids[0]&0xffffffff)
        uc.reg_write(DR[1],ids[1]&0xffffffff)
        uc.reg_write(DR[4],mode&0xffffffff)
        uc.reg_write(AR[1],context)
        uc.reg_write(AR[4],cbptr)
        uc.reg_write(AR[5],owner)
        before={r:uc.reg_read(r) for r in DR+AR[:7] if r not in (DR[2],DR[3])}
        state=(self.table(),self.shadows(),self.selected_triple(),dict(self.chip_live))
        self.lookup_calls=0
        self.resolve_calls=0
        self.check_calls=0
        self.explicit_shadow_writes=[]
        self.in_explicit_lookup=True
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            uc.emu_start(self.querybase,STOP,count=40000000)
        finally:
            self.in_explicit_lookup=False
        assert uc.reg_read(UC_M68K_REG_PC)==STOP,hex(uc.reg_read(UC_M68K_REG_PC))
        assert self.a(7)==STACK+4
        assert self.d(2)==0
        for reg,value in before.items():
            assert uc.reg_read(reg)==value,('full query ABI',reg)
        assert not self.explicit_shadow_writes,'selected bank shadow mutated'
        if not self._modified:
            assert (self.table(),self.shadows(),self.selected_triple(),dict(self.chip_live))==state
        d3=self.d(3)
        return d3-0x100000000 if d3&0x80000000 else d3


class FullNativeP2aQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.labels=emit_p2a_collision_query020()

    def test_01_real_68020_disassembly_abi_stable(self):
        self.assertEqual((self.raw,self.labels),emit_p2a_collision_query020())
        cap=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        ins=list(cap.disasm(self.raw,BASES['interpreted']))
        self.assertEqual(sum(i.size for i in ins),len(self.raw))
        self.assertFalse(any(x.mnemonic.startswith('dc.') for x in ins))
        self.assertEqual(self.raw.count(bytes.fromhex('4e92')),2)
        print('P2A_ONE_CALL_QUERY_020',len(self.raw),sha256(self.raw).hexdigest(),flush=True)

    def test_02_one_call_sources_two_banks_signed_hotspots(self):
        for layout in BASES:
            for a,b in (((0,0),(0,0)),((4,-3),(-2,5))):
                m=NativeFullQuery(layout,a,b)
                h=(*a,*b)
                _,bobs=expect_geometry(m.pair,m.src,hotspots=h)
                for mode in (0,1):
                    wanted=int(collision(*bobs,screen=Rect(0,0,W,H),
                                         mode='rect' if mode==0 else 'mask'))
                    self.assertEqual(m.query(mode),wanted)
                    self.assertGreaterEqual(m.check_calls,4)
                    self.assertGreaterEqual(m.resolve_calls,2)
                    self.assertGreaterEqual(m.lookup_calls,4)

    def test_03_global_and_local_p1d_clipping(self):
        rng=Random(0x0A60120)
        for layout in BASES:
            a,b=(3,-2),(-1,4)
            m=NativeFullQuery(layout,a,b)
            _,bobs=expect_geometry(m.pair,m.src,hotspots=(*a,*b))
            for _ in range(14):
                global_limit=Rect(rng.randint(-6,40),rng.randint(-8,48),
                                  rng.randint(1,50),rng.randint(1,40)) if rng.randrange(2) else None
                loc={}
                if rng.randrange(2):loc[1]=Rect(10,10,rng.randint(1,60),rng.randint(1,40))
                if rng.randrange(2):loc[2]=Rect(15,22,rng.randint(1,60),rng.randint(1,35))
                for mode in (0,1):
                    wanted=int(collision(*bobs,screen=Rect(0,0,W,H),
                                         mode='rect' if mode==0 else 'mask',
                                         global_limit=global_limit,local_limits=loc))
                    self.assertEqual(m.query(mode,global_limit=global_limit,
                                             local_limits=loc),wanted)

    def test_04_bad_mode_ids_owner_refuse(self):
        m=NativeFullQuery('interpreted')
        for mode in (-1,2,99):
            self.assertEqual(m.query(mode),-1)
        for pair in ((0,1),(1,1),(1,65),(65,1),(-1,2)):
            self.assertEqual(m.query(ids=pair),-1)
        self.assertEqual(m.query(owner=AMOS+0x1000),-1)

    def test_05_source_generation_drift_fails_closed(self):
        for layout in BASES:
            m=NativeFullQuery(layout,(2,1),(-2,0))
            for bank in (10,11):
                addr=m.find(bank)+24+24
                old=m.get(addr)
                m.put(addr,old+1)
                self.assertEqual(m.query(),-1)
                m.put(addr,old)
            self.assertIn(m.query(),(0,1))

    def test_06_late_hotspot_source_mutation_fails_closed(self):
        for layout in BASES:
            m=NativeFullQuery(layout,(4,-1),(1,2))
            m.mutate_after_first=True
            self.assertEqual(m.query(),-1)
            self.assertIsNotNone(m._modified)
            m.restore_late()
            self.assertIn(m.query(),(0,1))

    def test_07_bad_screen_and_p1d_table_refuse(self):
        m=NativeFullQuery('compiled')
        for wh in ((0,256),(4097,256),(320,0)):
            self.assertEqual(m.query(screen=wh),-1)
        raw=bytearray(65*SLOT.size)
        SLOT.pack_into(raw,0,10,10,10,11)
        self.assertEqual(m.query(rawlimits=bytes(raw)),-1)
        SLOT.pack_into(raw,0,0,0,0,0)
        SLOT.pack_into(raw,2*16,5,5,1,6)
        self.assertEqual(m.query(rawlimits=bytes(raw)),-1)

    def test_08_reject_invalid_private_pointer_table(self):
        m=NativeFullQuery('interpreted')
        bad=list(m.callbacks);bad[3]=0
        self.assertEqual(m.query(callbacks=bad),-1)
        bad=list(m.callbacks);bad[6]=1
        self.assertEqual(m.query(callbacks=bad),-1)
        self.assertEqual(m.query(context=0),-1)
        self.assertEqual(m.query(cbptr=0),-1)

    def test_09_repeated_native_query_never_allocates_or_swaps(self):
        for layout in BASES:
            m=NativeFullQuery(layout,(-2,3),(0,-1))
            state=(m.table(),m.shadows(),m.selected_triple(),dict(m.chip_live))
            for _ in range(5):
                for mode in (0,1):
                    self.assertIn(m.query(mode),(0,1))
            self.assertEqual((m.table(),m.shadows(),m.selected_triple(),dict(m.chip_live)),state)


if __name__=='__main__':
    unittest.main(verbosity=2)
