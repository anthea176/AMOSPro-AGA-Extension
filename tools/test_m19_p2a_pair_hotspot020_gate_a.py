#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2a source-verified P1b hotspot reads, REAL MC68020 P0j-b1 callback.

The signed hotspot data is read from original AGBO directories, NOT
host fabricated. Chains existing native P0f+P0j Chip pair, this native
hotspot scanner, native P1d 2x40 geometry and real MC68020 collision
kernel. Orchestration is Python harness, not a published AMOS opcode.
"""
from __future__ import annotations
from hashlib import sha256
from struct import pack,unpack,pack_into
import unittest
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_PC
from test_m5_generic import AR,DR,AMOS,STACK,STOP
from test_m19_p2a_pair_geometry020_gate_a import GeometryMachine,expect_geometry,SCREEN,PAIR,W,H
from m19_p2a_bob_collision_model import Rect,collision
from m19_p0a_multi_bob_abk import set_hotspot,parse_payload
from m19_p2a_pair_hotspot020_emit import emit_p2a_pair_hotspot020,OUTPUT_BYTES
from m19_p2a_pair_chip_resolve_emit import OUTPUT_BYTES as PAIR_BYTES

BASES={'interpreted':0x3e0000,'compiled':0x4e0000}
OUT=0x61000
GUARD=b'\xa8'*12
CANARY=b'\xd3'*OUTPUT_BYTES

class HotNativeMachine(GeometryMachine):
    def __init__(self,layout,hot10=(0,0),hot11=(0,0)):
        self.wanted={10:hot10,11:hot11}
        self._edited=set()
        super().__init__(layout)
        self.source,self.source_labels=emit_p2a_pair_hotspot020()
        self.source_base=BASES[layout]
        self.uc.mem_write(self.source_base,self.source)
        self.lookup_entry=self.entry+self.labels['explicit_bank_lookup_entry']
        self.lookup_calls=0
        self.mutate_after_first=False
        self._modified=None
        self.uc.hook_add(UC_HOOK_CODE,self._lookup_seen,begin=self.lookup_entry,end=self.lookup_entry)

    def stage(self,bank,owner=AMOS):
        # Called during parent initializer, *before* the native Chip stage.
        # Replace AGBO transactionally, update P0f binding to new generation,
        # then stage real Chip source via the parent P0j-b2 routine.
        if bank in self.wanted and bank not in self._edited:
            desired=self.wanted[bank]
            if desired != (0,0):
                old=self.bank_payload(bank)
                changed=set_hotspot(old,1,*desired)
                assert len(old)==len(changed)
                self.uc.mem_write(self.find(bank)+24,changed)
                assert self.run_select(bank)==1
                ident=1 if bank==10 else 2
                x,y=(27,41) if ident==1 else (33,43)
                assert self.public('bob',ident=ident,image=1,x=x,y=y)==1
            self._edited.add(bank)
        return super().stage(bank,owner=owner)

    def _lookup_seen(self,uc,address,size,user):
        self.lookup_calls+=1
        if self.mutate_after_first and self.lookup_calls==3:
            # A bank changed *after both scans*, just before revalidation.
            addr=self.find(10)+24+24
            self._modified=(addr,self.get(addr))
            self.put(addr,self.get(addr)+1)

    def restore_late(self):
        if self._modified:
            addr,value=self._modified
            self.put(addr,value)
            self._modified=None
        self.mutate_after_first=False

    def hotread(self,*,pair=None,owner=AMOS,callback=None,output=OUT):
        if pair is None:pair=self.pair
        if callback is None:callback=self.lookup_entry
        uc=self.uc
        uc.mem_write(PAIR,pair)
        uc.mem_write(OUT-12,GUARD)
        uc.mem_write(OUT,CANARY)
        uc.mem_write(OUT+OUTPUT_BYTES,GUARD)
        for i,r in enumerate(DR):uc.reg_write(r,0x9b000000+i)
        for i,r in enumerate(AR[:7]):uc.reg_write(r,0x35000+i*0x100)
        uc.reg_write(AR[0],PAIR);uc.reg_write(AR[1],output)
        uc.reg_write(AR[4],callback);uc.reg_write(AR[5],owner)
        saved={r:uc.reg_read(r) for r in DR+AR[:7] if r not in (DR[2],DR[3])}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.lookup_calls=0
        self.explicit_shadow_writes=[]
        self.in_explicit_lookup=True
        try:
            uc.emu_start(self.source_base,STOP,count=12000000)
        finally:
            self.in_explicit_lookup=False
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0 and self.d(3) in (0,1)
        for reg,value in saved.items():
            assert uc.reg_read(reg)==value,('hotspot MC68020 ABI',reg)
        assert bytes(uc.mem_read(OUT-12,12))==GUARD
        assert bytes(uc.mem_read(OUT+OUTPUT_BYTES,12))==GUARD
        assert not self.explicit_shadow_writes
        return self.d(3),bytes(uc.mem_read(OUT,OUTPUT_BYTES)),self.lookup_calls


class NativeHotspotP2a(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.labels=emit_p2a_pair_hotspot020()

    def test_01_source_deterministic_and_full_68020_disassembly(self):
        self.assertEqual((self.raw,self.labels),emit_p2a_pair_hotspot020())
        cap=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        ins=list(cap.disasm(self.raw,BASES['interpreted']))
        self.assertEqual(sum(op.size for op in ins),len(self.raw))
        self.assertFalse(any(x.mnemonic.startswith('dc.') for x in ins))
        self.assertEqual(self.raw.count(bytes.fromhex('4e94')),4)
        print('P2A_HOTSPOT_MC68020',len(self.raw),sha256(self.raw).hexdigest(),flush=True)

    def test_02_two_real_bank_hotspots_byte_exact(self):
        for layout in BASES:
            for hot10,hot11 in (((0,0),(0,0)),((4,-3),(-2,5)),
                                ((-32768,32767),(32767,-32768))):
                m=HotNativeMachine(layout,hot10,hot11)
                status,payload,calls=m.hotread()
                self.assertEqual((status,calls),(1,4))
                self.assertEqual(payload,pack('>4h',*hot10,*hot11))
                for bank,expected in ((10,hot10),(11,hot11)):
                    img=parse_payload(m.bank_payload(bank)).image(1)
                    self.assertEqual((img.hotspot_x,img.hotspot_y),expected)

    def test_03_real_native_hotspot_to_p1d_geometry_to_collision(self):
        for layout in BASES:
            m=HotNativeMachine(layout,(4,-3),(-2,5))
            status,hots,calls=m.hotread()
            self.assertEqual((status,calls),(1,4))
            h=unpack('>4h',hots)
            global_limit=Rect(0,0,64,64)
            local={1:Rect(0,20,64,30),2:Rect(12,25,60,50)}
            got=m.geom(hotspots=h,global_limit=global_limit,local_limits=local)
            expected,bobs=expect_geometry(m.pair,m.src,hotspots=h,
                                          global_limit=global_limit,local_limits=local)
            self.assertEqual(got,expected)
            for mode in (0,1):
                result=m.collide(mode)
                reference=int(collision(*bobs,screen=Rect(0,0,W,H),
                     mode='rect' if mode==0 else 'mask',
                     global_limit=global_limit,local_limits=local))
                self.assertEqual(result,reference)

    def test_04_original_selected_bank_never_changed(self):
        for layout in BASES:
            m=HotNativeMachine(layout,(3,2),(-1,4))
            state=(m.table(),m.shadows(),m.selected_triple(),dict(m.chip_live))
            for _ in range(4):
                self.assertEqual(m.hotread()[0],1)
            self.assertEqual((m.table(),m.shadows(),m.selected_triple(),
                              dict(m.chip_live)),state)

    def test_05_refuse_missing_or_stale_source_bank(self):
        for layout in BASES:
            m=HotNativeMachine(layout,(2,1),(-3,0))
            for bank in (10,11):
                node=m.find(bank)
                addr=node+24+24
                value=m.get(addr)
                m.put(addr,value+1)
                self.assertEqual(m.hotread()[0:2],(0,CANARY))
                m.put(addr,value)
            self.assertEqual(m.hotread()[0],1)

    def test_06_refuse_invalid_image_or_chip_descriptor(self):
        m=HotNativeMachine('interpreted')
        for offset,value in ((4,4096),(60+4,0),(24+8,0),
                             (60+24+16,99)):
            changed=bytearray(m.pair)
            pack_into('>I',changed,offset,value)
            self.assertEqual(m.hotread(pair=bytes(changed))[0:2],(0,CANARY))

    def test_07_recheck_detects_late_generation_mutation(self):
        for layout in BASES:
            m=HotNativeMachine(layout,(1,2),(-1,3))
            m.mutate_after_first=True
            self.assertEqual(m.hotread()[0:2],(0,CANARY))
            self.assertEqual(m.lookup_calls,3)
            m.restore_late()
            self.assertEqual(m.hotread()[0],1)

    def test_08_reject_bad_callbacks_owner_and_output(self):
        m=HotNativeMachine('compiled')
        for cb in (0,1,3):
            self.assertEqual(m.hotread(callback=cb)[0:2],(0,CANARY))
        self.assertEqual(m.hotread(owner=AMOS+0x1000)[0:2],(0,CANARY))
        for out in (0,OUT+1):
            self.assertEqual(m.hotread(output=out)[0:2],(0,CANARY))


if __name__=='__main__':
    unittest.main(verbosity=2)
