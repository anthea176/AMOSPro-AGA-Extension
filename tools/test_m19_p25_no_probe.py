#!/usr/bin/env python3
"""M19 P2.5 R87 native Gate A without diagnostic probe: MC68020, ABI, pixels, buffers.

This exercises the *actual* emitted 68k code via Unicorn and an independent
pixel oracle. AMOS/WinUAE Runtime B and Compiler C remain separately pending.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/experiments"))
from unicorn.m68k_const import UC_CPU_M68K_M68020, UC_M68K_REG_SR, UC_M68K_REG_PC
from audit_ap20 import inspect, parse
from compiler_relocation import unpack_ap20, RBSR, GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements, assert_reaches_entry_on_mc68020
from amos_link_test_support import relocate
from active_library import R84_SHA
from build_m19_p25_no_probe import (
    build, ACTIVE, PROTECTED, GROUP_C2P, GROUP_IFF, GROUP_BOBS, GROUP_AGA,
    BATCH_ENTRY, TITLE
)

from m19_bob_batch_emit import (
    emit_bob_batch, MAX_BOBS, STRIDE, MAGIC,
    GETADR, HEADER
)
from m16_agapic_v2_draw_emit import emit_image_draw_v2
from m18_ficon_ap20_emit import emit_ficon_ap20
from m18_ficon16_model import build_bank
from m16_agapic import pack_image
from m16_agapic_v2 import pack_image_v2
from test_m16_capture import CaptureMachine, NEW_CODE
from test_m16_image_draw_r45 import (
    BANK, ARGS, TYPEOFMEM, sample_pixels
)
from test_m5_generic import DR, AR, AMOS, EXEC, STACK, STOP, GFX, SCREEN

DESC = 0xE40000
CODE = 0x1C0000
SW, SH = 65, 43
ICON = bytes((0 if (x+y)%3 == 0 else (x+y*2)%256)
             for y in range(16) for x in range(16))
ICONS = (bytes([0]*256), ICON, bytes([14]*256), bytes([65]*256))
FICON_BANK = build_bank(ICONS)
PIC_PIXELS = bytes([5 if x%3 else 0 for y in range(8) for x in range(9)])
AGAPIC_BANK = pack_image(9,8,8,PIC_PIXELS,
                         bytes([1 if p else 0 for p in PIC_PIXELS]))
MODE_ID=0x00021000
AGAPIC_V2_BANK = pack_image_v2(9,8,8,PIC_PIXELS,
     bytes((i*7+3)&255 for i in range(768)),MODE_ID,
     bytes([1 if p else 0 for p in PIC_PIXELS]))


def descriptor(records):
    return (pack(">IHHII", MAGIC, 1, STRIDE, len(records), 0)
            + b"".join(pack(">iiIIHH", y, x, bank, icon, kind, mode)
                       for (x,y,bank,icon,kind,mode) in records))


def oracle(base,records,kind):
    out = bytearray(base)
    for x,y,bank,icon_id,_type,mode in records:
        if kind=="ficon":
            width, height, pixels = 16,16,ICONS[icon_id-1]
        else:
            width,height,pixels = 9,8,PIC_PIXELS
        for yy in range(height):
            for xx in range(width):
                dx,dy=x+xx,y+yy
                if 0<=dx<SW and 0<=dy<SH:
                    p = pixels[yy*width+xx]
                    if mode==0 or p:
                        out[dy*SW+dx]=p
    return bytes(out)


class BatchMachine(CaptureMachine):
    def os_call(self,uc,address,size,user):
        if address==GFX-792:  # GetVPModeID: real v2 path
            assert self.a(0)==SCREEN+44
            self.mode_calls+=1
            self._ret(MODE_ID)
            return
        if address==TYPEOFMEM and DESC-24<=self.a(1)<DESC+len(self.desc):
            self.type_calls+=1
            self.os_calls.append(("TypeOfMem descriptor",self.a(1),1))
            self._ret(1)
            return
        super().os_call(uc,address,size,user)

    def __init__(self, candidate, rows, *, kind="ficon", front=0,
                 pending=0, safe_ready=True, mutate=None):
        # Legacy Machine initializes Unicorn as CPU000. Select the 020
        # before its first memory map; switching models later is rejected.
        with patch("test_m5_generic.UC_CPU_M68K_M68000", UC_CPU_M68K_M68020):
            super().__init__(binary=candidate, width=SW, height=SH, depth=8,
                             front=front, pending=pending, safe_ready=safe_ready)
        self.uc.mem_write(EXEC+0x128,b"\x00\x02")
        self.desc = descriptor(rows)
        self.uc.mem_write(DESC,self.desc)
        self.uc.mem_write(DESC-24,pack(">IIIHH8s",
                0,len(self.desc)+16,20,1,0,b"BOB1    "))
        self.banks[20] = DESC
        self.install_bank(FICON_BANK if kind=="ficon" else
                          AGAPIC_V2_BANK if kind=="agapic_v2" else AGAPIC_BANK)
        self.mode_calls=0
        self.uc.mem_write(GFX-792,b"\x4e\x75")
        self.uc.mem_write(BANK-8,b"FICON8  " if kind=="ficon" else b"AGAPIC  ")
        self.uc.mem_write(BANK-12,b"\x00\x01")
        self.kind=kind
        _,parts,_=unpack_ap20(candidate)
        code=relocate(parts[GROUP_BOBS],CODE,{GROUP_BOBS:CODE},self.uc)
        self.uc.mem_write(CODE,code)
        self.entry=CODE+len(DISPATCH_V2)
        self.frontbuffer=[bytes(self.uc.mem_read(a,self.plane_size))
                          for a in self.frontplanes]
        if mutate:mutate(self)

    def run(self, count, bank=20):
        for i,reg in enumerate(DR):
            self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]):
            self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS,bank)
        self.uc.reg_write(DR[3],count&0xffffffff)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        initial=self.snapshot()
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.entry,STOP,count=10_000_000)
        except Exception as ex:
            raise AssertionError(("BOBS CPU exception",str(ex),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),
                list(self.trace), self.main_calls, self.os_calls)) from ex
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4 and self.a(3)==ARGS+4
        assert self.d(2)==0 and self.d(3) in (0,1)
        for reg,val in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==val,("AP20 register clobbered",reg)
        assert [bytes(self.uc.mem_read(a,self.plane_size))
                for a in self.frontplanes]==self.frontbuffer, "FRONT written"
        assert self.reserve_count==self.erase_count==0
        assert self.alloc_count==self.free_count==0
        return self.d(3),initial


class BatchGateA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate,cls.meta=build()
        cls.old=PROTECTED.read_bytes()
        cls.tokens,cls.parts,cls.title=unpack_ap20(cls.candidate)
        cls.old_tokens,cls.old_parts,_=unpack_ap20(cls.old)

    def test_r84_immutability_and_four_groups(self):
        self.assertEqual(sha256(self.old).hexdigest(),R84_SHA)
        self.assertEqual(len(self.old),67904)
        self.assertEqual(self.meta["commands"],77)
        self.assertEqual(len(self.parts),87)
        self.assertEqual(self.title,TITLE)
        self.assertEqual([len(self.parts[g]) for g in
            (GROUP_C2P,GROUP_IFF,GROUP_AGA)], [5558,2508,56580])
        self.assertEqual(self.parts[GROUP_C2P],self.old_parts[82])
        self.assertEqual(self.parts[GROUP_IFF],self.old_parts[83])
        self.assertEqual(self.parts[GROUP_AGA],self.old_parts[84])
        self.assertEqual(self.parts[GROUP_BOBS][:len(DISPATCH_V2)],DISPATCH_V2)
        self.assertEqual(self.parts[GROUP_BOBS][len(DISPATCH_V2):],emit_bob_batch()[0])
        self.assertEqual(self.meta["native_units"]["BOBS"],len(DISPATCH_V2)+len(emit_bob_batch()[0]))
        self.assertTrue(all(len(self.parts[g])<=65534 for g in
            (GROUP_C2P,GROUP_IFF,GROUP_BOBS,GROUP_AGA)))
        self.assertEqual(inspect(parse(self.candidate))["issues"],[])
        self.assertEqual(inspect(parse(self.candidate))["tokens"][:-1],
                         inspect(parse(self.old))["tokens"])

    def test_no_public_or_native_diagnostic_probe(self):
        report = inspect(parse(self.candidate))
        self.assertEqual(report["issues"], [])
        self.assertFalse(any(x["name"] == "aga bob probe" for x in report["tokens"]))
        self.assertEqual([x["name"] for x in report["tokens"] if
                          x["name"].startswith("aga bob ")], ["aga bob batch"])
        self.assertEqual(report["tokens"][-1]["function"], BATCH_ENTRY)
        self.assertEqual(report["tokens"][-1]["signature"], "00,0")
        self.assertEqual(len(self.parts),87)
        self.assertEqual(self.meta["ap20_entries"],87)
        self.assertEqual(self.meta["commands"],77)
        self.assertNotIn(b"aga bob probe", self.candidate.lower())
        # Batch begins immediately after Compiler V2 dispatcher, no PROBE_CODE.
        self.assertEqual(self.parts[GROUP_BOBS][len(DISPATCH_V2):],emit_bob_batch()[0])

    def test_native_source_and_relocations(self):
        new,labels=emit_bob_batch()
        self.assertEqual(self.parts[GROUP_BOBS][len(DISPATCH_V2):],new)
        self.assertEqual(self.meta["native_labels"],labels)
        self.assertEqual(new.count(GETADR),3)
        image,_=emit_image_draw_v2()
        ficon,_=emit_ficon_ap20(opt020=True)
        self.assertIn(image,new)
        self.assertIn(ficon,new)
        offset=labels["backend_agapic"]
        site=122
        self.assertEqual(unpack_from(">H",new,offset+site)[0],0x6100)
        self.assertEqual(offset+site+2+unpack_from(">h",new,offset+site+2)[0],
                         labels["backend_image"])
        links=interpreter_rbsr_displacements(self.parts)
        self.assertEqual(len(links),81)
        self.assertIn(BATCH_ENTRY,links)
        for i in (0,2,20,41,55,57,60,75,80,81,82):
            with self.subTest(entry=i):
                assert_reaches_entry_on_mc68020(self.candidate,i)

    def test_ficon_pixel_exact_modes_clip_order_and_front_safety(self):
        total=0
        for front in (0,1):
            for mode in (0,1):
                for x,y in ((0,0),(1,2),(-5,-7),(60,39),(65,20),
                            (-16,-16),(10,40)):
                    records=[(x,y,10,2,2,mode),
                             (4,4,10,3,2,1)]
                    m=BatchMachine(self.candidate, records,front=front)
                    result,before=m.run(len(records))
                    self.assertEqual(result,1,("FICON failed",front,mode,x,y))
                    old=sample_pixels(before,SW,SH,8,m.stride)
                    expected=oracle(old,records,"ficon")
                    actual=sample_pixels(m.snapshot(),SW,SH,8,m.stride)
                    self.assertEqual(actual,expected)
                    total+=1
        self.assertEqual(total,28)

    def test_agapic_v1_pixel_exact_modes_clipping(self):
        for mode in (0,1):
            records=[(-4,1,10,0,1,mode),
                     (15,10,10,0,1,1),
                     (18,12,10,0,1,mode)]
            m=BatchMachine(self.candidate,records,kind="agapic",front=1)
            result,before=m.run(len(records))
            self.assertEqual(result,1)
            old=sample_pixels(before,SW,SH,8,m.stride)
            self.assertEqual(sample_pixels(m.snapshot(),SW,SH,8,m.stride),
                             oracle(old,records,"agapic"))

    def test_agapic_v2_pixel_exact_and_modeid(self):
        records=[(-5,-3,10,0,1,1),(15,10,10,0,1,0)]
        m=BatchMachine(self.candidate, records, kind="agapic_v2", front=1)
        ok,before=m.run(2)
        self.assertEqual(ok,1)
        self.assertEqual(m.mode_calls,2)
        expected=oracle(sample_pixels(before,SW,SH,8,m.stride), records, "agapic")
        self.assertEqual(sample_pixels(m.snapshot(),SW,SH,8,m.stride),expected)

    def test_invalid_descriptor_preflight_does_not_mutate_back_or_front(self):
        valid=(2,2,10,2,2,1)
        bads=(
            ([],0),
            ([valid],0),
            ([valid],257),
            ([(2,2,4,2,2,1)],1),
            ([(2,2,10,0,2,1)],1),
            ([(2,2,10,4097,2,1)],1),
            ([(2,2,10,2,3,1)],1),
            ([(2,2,10,2,2,3)],1),
            ([(32768,1,10,2,2,1)],1),
            ([(-32769,1,10,2,2,1)],1),
            ([(2,2,10,1,1,1)],1),
        )
        for records,count in bads:
            with self.subTest(records=records,count=count):
                m=BatchMachine(self.candidate,records)
                result,before=m.run(count)
                self.assertEqual(result,0)
                self.assertEqual(m.snapshot(),before)
        # descriptor bank absent
        m=BatchMachine(self.candidate,[valid])
        result,before=m.run(1,bank=21)
        self.assertEqual(result,0)
        self.assertEqual(m.snapshot(),before)

    def test_missing_or_corrupt_source_and_safe_refuse(self):
        valid=(4,4,10,2,2,1)
        for case in ("bank_missing","bad_signature","safe_not_ready"):
            with self.subTest(case=case):
                m=BatchMachine(self.candidate,[valid],
                               pending=1 if case=="safe_not_ready" else 0,
                               safe_ready=(case!="safe_not_ready"))
                if case=="bank_missing":
                    m.banks.pop(10)
                if case=="bad_signature":
                    m.uc.mem_write(BANK-8,b"WRONG   ")
                result,before=m.run(1)
                self.assertEqual(result,0)
                self.assertEqual(m.snapshot(),before)
                self.assertEqual(m.getmsg_calls,
                                  1 if case=="safe_not_ready" else 0)

    def test_deterministic_immutable_and_candidate_path(self):
        binary,meta=build()
        self.assertEqual(self.candidate,binary)
        self.assertEqual(self.meta,meta)
        self.assertIn(sha256(ACTIVE.read_bytes()).hexdigest(),
                      (R84_SHA, __import__("active_library").R85_SHA,
                       __import__("active_library").R86_SHA,
                       sha256(binary).hexdigest(),
                       __import__("active_library").R88_SHA,
                       __import__("active_library").P0C_SHA,
                        __import__("active_library").P0D_SHA))
        self.assertEqual(PROTECTED.read_bytes(),self.old)


if __name__=="__main__":
    unittest.main(verbosity=2)
