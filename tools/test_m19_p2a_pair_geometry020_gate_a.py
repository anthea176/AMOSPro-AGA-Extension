#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A: execute the P2a 2x40 geometry packer on a REAL emulated 68020.

Source inputs: actual P0f+P0j-b3 120-byte pair from the native harness.
Hotspot words are deliberately supplied as trusted AGBO host snapshots
at this stage; they are NOT yet looked up by an integrated native helper.
Compare with independent host Rect/visible_footprint, then invoke the
real 764-byte MC68020 collision kernel on the generated descriptors.
"""
from __future__ import annotations
from hashlib import sha256
from random import Random
from struct import Struct,pack,pack_into,unpack
import unittest
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import AR,DR,AMOS,STACK,STOP
from test_m19_p2a_pair_chip_resolve_gate_a import PairChipMachine,BASES
from m19_p0a_multi_bob_abk import parse_payload
from m19_p2a_agbo_bridge import host_image
from m19_p2a_bob_collision_model import Bob,Rect,visible_footprint,collision
from m19_p2a_collision020_emit import emit_collision020
from m19_p2a_pair_geometry020_emit import emit_p2a_pair_geometry020,OUTPUT_BYTES

W,H=320,256
SCREEN=0x5f800
HOT=0x5f900
LIMITS=0x69000
RESULT=0x5fa00
PAIR=0x5cb00
GUARD=b'\xe1'*16
CANARY=b'\xc3'*OUTPUT_BYTES
DESCRIPTOR=Struct('>iiiiiiIIII')
SLOT=Struct('>iiii')
NATIVE_BASE={'interpreted':0x3c0000,'compiled':0x4c0000}
COL_BASE={'interpreted':0x3d0000,'compiled':0x4d0000}
assert DESCRIPTOR.size==40 and SLOT.size==16


def expect_geometry(data,imgs,ids=(1,2),hotspots=(0,0,0,0),
                    global_limit=None,local_limits=None):
    if local_limits is None:local_limits={}
    screen=Rect(0,0,W,H)
    expected=[]
    bobs=[]
    for i,img in enumerate(imgs):
        chunk=data[60*i:60*i+60]
        bank,im_id,x,y,active,reserved=unpack('>IIiiII',chunk[:24])
        nine=unpack('>9I',chunk[24:])
        hot_x,hot_y=hotspots[2*i:2*i+2]
        bob=Bob(ids[i],bank,im_id,x,y,host_image(img),hot_x,hot_y)
        bobs.append(bob)
        rect=visible_footprint(bob,screen,global_limit,local_limits)
        bound=(0,0,0,0) if rect is None else (
            rect.x,rect.y,rect.right,rect.bottom)
        expected.append(DESCRIPTOR.pack(*bound,bob.origin_x,bob.origin_y,
                           img.width,img.height,img.stride,nine[1]))
    return b''.join(expected),bobs


class GeometryMachine(PairChipMachine):
    def __init__(self,layout):
        super().__init__(layout)
        self.geo,self.geo_labels=emit_p2a_pair_geometry020()
        self.col,self.col_labels=emit_collision020()
        self.uc.mem_write(NATIVE_BASE[layout],self.geo)
        self.uc.mem_write(COL_BASE[layout],self.col)
        self.layout=layout
        pair_ok,pair,_,_=self.chip_pair()
        assert pair_ok==1
        self.pair=pair
        self.src=tuple(parse_payload(self.bank_payload(i)).image(1)
                       for i in (10,11))
        self.uc.mem_write(SCREEN,pack('>2I',W,H))
        self.uc.mem_write(LIMITS,bytes(65*SLOT.size))

    def geom(self,*,ids=(1,2),hotspots=(0,0,0,0),global_limit=None,
             local_limits=None,raw=None,screen=(W,H),expect=1,raw_limits=None):
        uc=self.uc
        if raw is None:raw=self.pair
        if local_limits is None: local_limits={}
        for where,payload in ((PAIR,raw),(SCREEN,pack('>2I',*screen)),
                              (HOT,pack('>4h',*hotspots))):
            uc.mem_write(where,payload)
        lim=bytearray(SLOT.size*65)
        if global_limit is not None:
            SLOT.pack_into(lim,0,global_limit.x,global_limit.y,
                           global_limit.right,global_limit.bottom)
        for bob_id,rect in local_limits.items():
            SLOT.pack_into(lim,bob_id*16,rect.x,rect.y,rect.right,rect.bottom)
        uc.mem_write(LIMITS,bytes(lim) if raw_limits is None else raw_limits)
        uc.mem_write(RESULT-16,GUARD)
        uc.mem_write(RESULT,CANARY)
        uc.mem_write(RESULT+OUTPUT_BYTES,GUARD)
        for i,r in enumerate(DR):uc.reg_write(r,0x7e000000+i)
        for i,r in enumerate(AR[:7]):uc.reg_write(r,0x30000+i*0x100)
        for r,v in ((DR[0],ids[0]&0xffffffff),(DR[1],ids[1]&0xffffffff),
                    (AR[0],PAIR),(AR[1],SCREEN),(AR[3],HOT),
                    (AR[4],LIMITS),(AR[5],AMOS),(AR[6],RESULT)):
            uc.reg_write(r,v)
        old={r:uc.reg_read(r) for r in DR+AR[:7] if r not in (DR[2],DR[3])}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        uc.emu_start(NATIVE_BASE[self.layout],STOP,count=800000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0
        for reg,value in old.items():
            assert uc.reg_read(reg)==value,('geometry ABI clobber',reg)
        assert bytes(uc.mem_read(RESULT-16,16))==GUARD
        assert bytes(uc.mem_read(RESULT+OUTPUT_BYTES,16))==GUARD
        got=bytes(uc.mem_read(RESULT,OUTPUT_BYTES))
        assert self.d(3)==expect,(self.d(3),expect)
        if not expect: assert got==CANARY
        return got

    def collide(self,mode):
        uc=self.uc
        for i,r in enumerate(DR):uc.reg_write(r,0x5c000000+i)
        for i,r in enumerate(AR[:7]):uc.reg_write(r,0x31000+i*0x100)
        uc.reg_write(DR[0],mode&0xffffffff)
        uc.reg_write(AR[0],RESULT)
        uc.reg_write(AR[1],RESULT+40)
        saved={r:uc.reg_read(r) for r in DR+AR[:7] if r not in (DR[2],DR[3])}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        uc.emu_start(COL_BASE[self.layout],STOP,count=2500000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP and self.a(7)==STACK+4
        assert self.d(2)==0
        for r,v in saved.items():assert uc.reg_read(r)==v,('collision ABI',r)
        return self.d(3) if self.d(3)<0x80000000 else self.d(3)-0x100000000


class P2aNativeGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native,cls.labels=emit_p2a_pair_geometry020()

    def test_01_deterministic_68020_opcode_abi(self):
        self.assertEqual((self.native,self.labels),emit_p2a_pair_geometry020())
        decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        ins=list(decoder.disasm(self.native,0x3c0000))
        self.assertEqual(sum(i.size for i in ins),len(self.native))
        self.assertFalse(any(x.mnemonic.startswith('dc.') for x in ins))
        self.assertEqual(self.labels['p2a_pair_geometry_entry'],0)
        print('P2A_GEOMETRY_MC68020',len(self.native),sha256(self.native).hexdigest(),flush=True)

    def test_02_real_chip_pair_matches_independent_geometry(self):
        for layout in BASES:
            m=GeometryMachine(layout)
            desc=m.geom()
            exp,bobs=expect_geometry(m.pair,m.src)
            self.assertEqual(desc,exp)
            for mode in (0,1):
                expect=int(collision(*bobs,screen=Rect(0,0,W,H),
                                     mode='rect' if mode==0 else 'mask'))
                self.assertEqual(m.collide(mode),expect)

    def test_03_signed_hotspots_and_touching_edges(self):
        cases=((4,3,-2,1),(0,0,0,0),(-8,4,7,-5),(32767,-32768,-32768,32767),
               (-32768,32767,32767,-32768))
        for layout in BASES:
            m=GeometryMachine(layout)
            for hot in cases:
                desc=m.geom(hotspots=hot)
                exp,bobs=expect_geometry(m.pair,m.src,hotspots=hot)
                self.assertEqual(desc,exp)
                for mode in (0,1):
                    expected=int(collision(*bobs,screen=Rect(0,0,W,H),
                                          mode='rect' if mode==0 else 'mask'))
                    self.assertEqual(m.collide(mode),expected)

    def test_04_p1d_global_and_two_local_limits(self):
        rng=Random(0x020120)
        for layout in BASES:
            m=GeometryMachine(layout)
            for _ in range(30):
                g=Rect(rng.randint(-4,30),rng.randint(-4,48),
                       rng.randint(1,72),rng.randint(1,40)) if rng.randrange(2) else None
                local={}
                for ident in (1,2):
                    if rng.randrange(3):
                        local[ident]=Rect(rng.randint(-5,50),rng.randint(-7,52),
                                          rng.randint(1,80),rng.randint(1,70))
                hot=tuple(rng.randint(-8,8) for _ in range(4))
                desc=m.geom(hotspots=hot,global_limit=g,local_limits=local)
                exp,bobs=expect_geometry(m.pair,m.src,hotspots=hot,
                                         global_limit=g,local_limits=local)
                self.assertEqual(desc,exp)
                for mode in (0,1):
                    expected=int(collision(*bobs,screen=Rect(0,0,W,H),
                                          global_limit=g,local_limits=local,
                                          mode='rect' if mode==0 else 'mask'))
                    self.assertEqual(m.collide(mode),expected)

    def test_05_clip_extreme_signed_positions(self):
        for layout in BASES:
            m=GeometryMachine(layout)
            for xy in ((-32768,-32768,32767,32767),
                       (32767,32767,-32768,-32768),
                       (-3,-1,0,0),(319,255,319,255)):
                data=bytearray(m.pair)
                for i in (0,1):
                    pack_into('>ii',data,60*i+8,*xy[i*2:i*2+2])
                desc=m.geom(raw=bytes(data))
                expected,bobs=expect_geometry(bytes(data),m.src)
                self.assertEqual(desc,expected)
                for mode in (0,1):
                    self.assertEqual(m.collide(mode),
                        int(collision(*bobs,screen=Rect(0,0,W,H),
                                      mode='rect' if mode==0 else 'mask')))

    def test_06_noncanonical_p1d_limit_refused(self):
        m=GeometryMachine('interpreted')
        # Degenerate global zone: encoded without host Rect (invalid API).
        raw=bytearray(SLOT.size*65)
        SLOT.pack_into(raw,0,1,2,1,3)
        self.assertEqual(m.geom(raw_limits=bytes(raw),expect=0),CANARY)
        # A noncanonical local slot also refuses before any publication.
        SLOT.pack_into(raw,0,0,0,0,0)
        SLOT.pack_into(raw,2*SLOT.size,4,5,1,6)
        self.assertEqual(m.geom(raw_limits=bytes(raw),expect=0),CANARY)
        for flag in (0,1):
            source=bytearray(m.pair)
            if flag==0: pack_into('>I',source,16,2) # active 2 invalid
            else:pack_into('>I',source,24+16,3)     # stride incorrect
            self.assertEqual(m.geom(raw=bytes(source),expect=0),CANARY)

    def test_07_invalid_inputs_leave_80_bytes_untouched(self):
        m=GeometryMachine('compiled')
        for ids in ((0,2),(1,65),(1,1),(-1,2)):
            self.assertEqual(m.geom(ids=ids,expect=0),CANARY)
        for sc in ((0,256),(320,0),(4097,256)):
            self.assertEqual(m.geom(screen=sc,expect=0),CANARY)

    def test_08_repeated_geometry_preserves_chip_and_selector(self):
        for layout in BASES:
            m=GeometryMachine(layout)
            before=(m.table(),m.shadows(),m.selected_triple(),dict(m.chip_live))
            for _ in range(5):
                m.geom(hotspots=(2,1,-1,2))
                m.collide(1)
            after=(m.table(),m.shadows(),m.selected_triple(),dict(m.chip_live))
            self.assertEqual(after,before)


if __name__=='__main__':
    unittest.main(verbosity=2)
