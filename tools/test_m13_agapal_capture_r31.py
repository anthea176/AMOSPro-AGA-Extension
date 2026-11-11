#!/usr/bin/env python3
"""M13/R31 palette capture: actual AP20 68000 code under Unicorn/Capstone.

Static/CPU/ABI tests only. No AMOS/WinUAE (Gate B), Compiler or physical
Amiga validation, and no evidence of display changes (the API is read-only
on the private screen). Screen and Exec functions are instrumented mocks.
"""
import struct
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from build_m13_agapal_capture_r31 import (
    build,BASE,BASE_SHA256,LAST_GOOD,LAST_GOOD_SHA256,
    ENTRY_CAPTURE,BASE_ENTRIES,API,GETP,
)
from m13_agapal_capture_r31_emit import emit_capture
from agapal_r30_layout import init_payload,parse_payload,abk_model,parse_abk,payload_size
from test_m13_agapal_r30 import BankMachine,BANK,ARGS
from test_m13_palette_r28 import COLORMAP
from test_m5_generic import STATE,SCREEN,GFX,CODE,STOP,STACK,DR,AR,AMOS
from ap20_utils import digest,split
from audit_ap20 import inspect as audit, parse

class CaptureMachine(BankMachine):
    def __init__(self,binary,slots=8,slot=0,depth=8,colors=None,
                 logical=None,flags=1,**kwargs):
        super().__init__(binary,count=slots,flags=flags,name=b"AGAPAL  ",
                         **kwargs)
        self.uc.mem_write(BANK,init_payload(slots))
        self.uc.mem_write(GFX-900,b"\x4e\x75")
        self.depth=depth
        self.slot=slot
        self.colormap_count=(1<<depth) if colors is None else colors
        self.logical=(1<<depth) if logical is None else logical
        self.screen_before=None
        for off,v in ((0,SCREEN),(8,GFX),(12,320),(16,256),
                      (20,self.logical),(24,0),(28,depth)):
            self.put(STATE+off,v)
        self.put(SCREEN+48,COLORMAP)
        self.uc.mem_write(COLORMAP+2,struct.pack(">H",self.colormap_count))
        self.palette_rgb=[
            tuple((((i*(k+3)*7+31+k*17)&255)*0x01010101) for k in range(3))
            for i in range(256)
        ]
        self.rgb_calls=0
        self.last_count=None
        self.getrgb_dest=None

    def os_call(self,uc,address,size,user):
        if address==GFX-900:
            self.rgb_calls+=1
            assert self.a(0)==COLORMAP,"GetRGB32 must read private AGA ColorMap"
            assert self.d(0)==0,"GetRGB32 must start at first pen"
            expected=min(self.logical,self.colormap_count)
            assert 1<=expected<=256 and self.d(1)==expected,(
                self.d(1),expected)
            self.last_count=expected
            dst=self.a(1)
            assert dst in self.owned, "RGB32 temp must be Exec AllocVec-owned"
            assert self.owned[dst]>=expected*12
            rgb=[x for triple in self.palette_rgb[:expected] for x in triple]
            uc.mem_write(dst,struct.pack(">"+("I"*len(rgb)),*rgb))
            self.getrgb_dest=dst
            self.uc.reg_write(DR[0],0)
            self.uc.reg_write(DR[1],0xdeadbeef)
            self.uc.reg_write(AR[0],0xbad000)
            self.uc.reg_write(AR[1],0xbad100)
            pc=self.get(self.a(7))
            self.uc.reg_write(AR[7],self.a(7)+4)
            self.uc.reg_write(UC_M68K_REG_PC,pc)
            return
        return super().os_call(uc,address,size,user)

    def capture(self,index=None,ptr=BANK):
        value=self.slot if index is None else index
        for i,r in enumerate(DR):
            self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS,ptr)
        self.uc.reg_write(DR[3],value&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_CAPTURE],STOP,count=1000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4, "hardware stack leak"
        assert self.a(3)==ARGS+4, "one long parameter expected via (A3)+"
        for r,old in saved.items():
            if r in (DR[2],DR[3],AR[3]):continue
            assert self.uc.reg_read(r)==old,(r,old,self.uc.reg_read(r))
        assert self.d(2)==0, "must return AMOS integer type D2=0"
        assert not self.owned and not self.open_libraries and not self.open_files
        assert self.plane_writes==0
        return self.d(3)

    def slot_payload(self,index):
        start=16+8*self.count+768*index
        return bytes(self.uc.mem_read(BANK+start,768))

    def descriptor(self,index):
        return struct.unpack(">IHH",self.uc.mem_read(BANK+16+index*8,8))

    def expected_rgb(self,count):
        return bytes((v>>24)&255 for triplet in self.palette_rgb[:count]
                     for v in triplet)

def run():
    candidate,meta=build()
    assert candidate==build()[0],"non-deterministic candidate"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    oldtok,old,_=split(BASE.read_bytes())
    tok,parts,_=split(candidate)
    assert len(old)==BASE_ENTRIES and len(parts)==BASE_ENTRIES+1
    assert parts[:41]==old[:41]
    assert parts[41]==old[41]+GETP
    assert tok.startswith(oldtok[:-6])
    assert audit(parse(candidate))["issues"]==[]
    named=[x for x in audit(parse(candidate))["tokens"]
           if x["name"].startswith("aga ")]
    assert len(named)==37
    assert any(x["name"]=="aga palette bank capture" and
               (x["instruction"],x["function"],x["signature"])==(1,42,"00,0")
               for x in named)
    code,labels=emit_capture()
    assert parts[ENTRY_CAPTURE]==code
    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    dis=list(md.disasm(code,0))
    assert sum(x.size for x in dis)==len(code)
    boundaries={x.address for x in dis}
    assert all(x in boundaries for x in labels.values()),labels
    assert not any(x.mnemonic in ("dc.w","illegal","trap") for x in dis)
    assert any("mulu.w" in x.mnemonic for x in dis)

    tests=0
    # Various palette capacities/depths, first/last indexes, Chip/Fast DATA.
    for slots in (1,2,8,16,256):
        for depth in (1,4,8):
            for index in (0,slots-1):
                for flags in (1,3):
                    m=CaptureMachine(candidate,slots=slots,slot=index,
                                     depth=depth,flags=flags)
                    # Other slots must be preserved bit for bit.
                    untouched=m.get_payload()
                    before_name=m.get_native()
                    result=m.capture()
                    assert result==1,(slots,index,depth,flags,result)
                    assert m.type_calls==2 and m.rgb_calls==1 and m.alloc_calls==1
                    assert m.last_count==(1<<depth)
                    assert m.get_native()==before_name,"native ABK header changed"
                    start=16+8*slots+768*index
                    expect=m.expected_rgb(1<<depth)
                    got=m.get_payload()
                    assert got[start:start+len(expect)]==expect
                    assert got[start+len(expect):start+768]==bytes(768-len(expect))
                    assert m.descriptor(index)==(start,1<<depth,0)
                    assert got[:16+8*slots]==(
                        untouched[:16+8*index+4] +
                        struct.pack(">H",1<<depth) +
                        untouched[16+8*index+6:16+8*slots]
                    )
                    # Only target descriptor COUNT word and target RGB bytes differ.
                    for n in range(slots):
                        if n!=index:
                            assert m.descriptor(n)==(
                                16+slots*8+768*n,0,0)
                            assert m.slot_payload(n)==bytes(768)
                    assert parse_payload(got).entries[index][1]==1<<depth
                    bank,bankflags,parsed=parse_abk(abk_model(10,got,
                                                               chip=(flags==3)))
                    assert bank==10 and bankflags==flags
                    assert parsed.palettes==slots
                    tests+=1

    # A deliberately smaller logical screen or ColorMap must cap the count.
    for depth,logical,colors in ((8,17,256),(8,256,5),(4,16,3),
                                 (8,1,256),(8,256,255)):
        m=CaptureMachine(candidate,depth=depth,logical=logical,colors=colors)
        assert m.capture()==1
        n=min(logical,colors)
        assert m.last_count==n
        assert m.descriptor(0)[1]==n
        expect=m.expected_rgb(n)
        assert m.slot_payload(0)==expect+bytes(768-len(expect))
        tests+=1

    # Existing slot contents are overwritten, remainder deterministically 0.
    m=CaptureMachine(candidate,slots=8,depth=8,slot=3)
    start=16+8*8+3*768
    m.uc.mem_write(BANK+start,b"\xff"*768)
    m.uc.mem_write(BANK+16+3*8+4,struct.pack(">H",256))
    assert m.capture()==1
    assert m.slot_payload(3)==m.expected_rgb(256)
    m.type_calls=0
    m.logical=4
    m.put(STATE+20,4)
    m.palette_rgb=[(0x21212121,0x40404040,0xfefefefe)]*256
    assert m.capture()==1
    assert m.descriptor(3)[1]==4
    assert m.slot_payload(3)==m.expected_rgb(4)+bytes(756)
    assert m.rgb_calls==2
    tests+=2

    # On every rejection, bank (including name and unrelated slots) is identical.
    failures=[
        ("negative_index",dict(index=-1)),
        ("index_equals_capacity",dict(index=8)),
        ("index_huge",dict(index=0x10000)),
        ("null_ptr",dict(ptr=0)),
        ("odd_ptr",dict(ptr=BANK+1)),
        ("small_ptr",dict(ptr=23)),
        ("flag_zero",dict(flags=0)),
        ("flag_work",dict(flags=4)),
        ("flag_reserved",dict(flags=5)),
        ("banknum_low",dict(bankno=4)),
        ("banknum_high",dict(bankno=65536)),
        ("short_bank",dict(declared=16+7*776)),
        ("long_bank",dict(declared=16+9*776)),
        ("header_ram_invalid",dict(type_header=False)),
        ("end_ram_invalid",dict(type_end=False)),
    ]
    for name,args in failures:
        index=args.get("index",0)
        ptr=args.get("ptr",BANK)
        kw={k:v for k,v in args.items() if k not in ("index","ptr")}
        m=CaptureMachine(candidate,**kw)
        before=m.get_native()+m.get_payload()
        assert m.capture(index,ptr)==0,name
        assert before==m.get_native()+m.get_payload(),name
        assert not m.writes and m.rgb_calls==0 and m.alloc_calls==0,name
        tests+=1

    # Corrupt AGAPAL header/descriptor is rejected, without bank writes.
    patches=[
        (BANK-8,b"x"),(BANK-4,b"\xff"),
        (BANK,b"bad!"),(BANK+4,b"XX"),(BANK+6,b"\0\x02"),
        (BANK+8,b"\0\0"),(BANK+8,b"\x01\x01"),
        (BANK+10,b"\0\x01"),(BANK+12,b"\x01"),
        (BANK+16,b"\xff"),(BANK+20,b"\x01\x01"),
        (BANK+22,b"\x00\x01"),
    ]
    for addr,part in patches:
        m=CaptureMachine(candidate)
        m.uc.mem_write(addr,part)
        before=m.get_native()+m.get_payload()
        assert m.capture()==0,(addr,part)
        assert before==m.get_native()+m.get_payload()
        assert not m.writes and m.rgb_calls==0 and m.alloc_calls==0
        tests+=1

    # Screen validation before AllocVec and before a single persistent write.
    invalid=[
        ("screen",lambda m:m.put(STATE,0)),
        ("gfx",lambda m:m.put(STATE+8,0)),
        ("depth_zero",lambda m:m.put(STATE+28,0)),
        ("depth_over",lambda m:m.put(STATE+28,9)),
        ("ham",lambda m:m.put(STATE+24,0x800)),
        ("ehb",lambda m:m.put(STATE+24,0x80)),
        ("dual",lambda m:m.put(STATE+24,0x400)),
        ("logical_zero",lambda m:m.put(STATE+20,0)),
        ("logical_large",lambda m:m.put(STATE+20,257)),
        ("colormap_ptr",lambda m:m.put(SCREEN+48,0)),
        ("colormap_zero",lambda m:m.uc.mem_write(COLORMAP+2,b"\0\0")),
        ("colormap_large",lambda m:m.uc.mem_write(COLORMAP+2,b"\x01\x01")),
    ]
    for name,damage in invalid:
        m=CaptureMachine(candidate)
        damage(m)
        before=m.get_native()+m.get_payload()
        assert m.capture()==0,name
        assert before==m.get_native()+m.get_payload(),name
        assert not m.writes and m.alloc_calls==0 and m.rgb_calls==0,name
        tests+=1

    m=CaptureMachine(candidate)
    m.allocation_failure=1
    before=m.get_native()+m.get_payload()
    assert m.capture()==0
    assert not m.writes and not m.owned and m.rgb_calls==0
    assert before==m.get_native()+m.get_payload()
    tests+=1

    print("M13 R31 AGAPAL capture native 68000 Gate A PASS:",tests,
          "scenarios",flush=True)
    print("R31 candidate:",{k:v for k,v in meta.items() if k!="labels"},
          flush=True)
    print("Gate B WinUAE / Gate C Compiler / Gate D hardware: NOT TESTED")


if __name__=="__main__":
    run()
