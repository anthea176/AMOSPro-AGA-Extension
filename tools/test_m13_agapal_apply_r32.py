#!/usr/bin/env python3
"""M13/R32: native 68000 Gate A for AGAPAL Apply(Start(bank),index).

Execute the real new AP20 segment in Unicorn M68000. Mock Exec memory
management and graphics.library/LoadRGB32, checking actual RGB32 tables
and register ABI. This is NOT an AMOS/WinUAE, compiler or real AGA test.
"""
import struct
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from build_m13_agapal_apply_r32 import (
    build,BASE,BASE_SHA256,LAST_GOOD,LAST_GOOD_SHA256,
    ENTRY_APPLY,BASE_ENTRIES,API,GETP,
)
from m13_agapal_apply_r32_emit import emit_apply
from agapal_r30_layout import parse_payload,abk_model,parse_abk
from test_m13_agapal_capture_r31 import CaptureMachine,BANK,ARGS
from test_m13_palette_r28 import COLORMAP
from test_m5_generic import STATE,SCREEN,GFX,CODE,STOP,STACK,DR,AR,AMOS
from ap20_utils import digest,split
from audit_ap20 import inspect as audit,parse

class ApplyMachine(CaptureMachine):
    def __init__(self,binary,slots=8,index=0,depth=8,colors=None,
                 logical=None,filled=None,flags=1,**kwargs):
        super().__init__(binary,slots=slots,slot=index,depth=depth,
                         colors=colors,logical=logical,flags=flags,**kwargs)
        self.index=index
        self.load_calls=0
        self.last_load=None
        self.screen_palette=[(0xaaaaaaaa,0xbbbbbbbb,0xcccccccc)
                             for _ in range(256)]
        self.original_screen=tuple(self.screen_palette)
        self.slot_colors={}
        self.uc.mem_write(GFX-882,b"\x4e\x75")
        if filled is None:
            filled=min(self.logical,self.colormap_count,256)
        if 1<=filled<=256 and 0<=index<slots:
            self.populate(index,filled)

    def populate(self,index,count,seed=None):
        assert 0<=index<self.count and 0<=count<=256
        seed=index*47+13 if seed is None else seed
        rgb=bytes((i*(k*17+13)+seed+k*59)&255
                  for i in range(count) for k in range(3))
        off=16+self.count*8+768*index
        self.uc.mem_write(BANK+off,rgb+bytes([0xE7])*(768-len(rgb)))
        self.uc.mem_write(BANK+16+8*index+4,struct.pack(">H",count))
        self.slot_colors[index]=rgb

    def os_call(self,uc,address,size,user):
        if address==GFX-882:
            self.load_calls+=1
            assert self.a(0)==SCREEN+44,"LoadRGB32 must use private ViewPort"
            ptr=self.a(1)
            assert ptr in self.owned,"temporary table must be AllocVec-owned"
            word=self.get(ptr)
            count,first=word>>16,word&0xffff
            assert first==0 and 1<=count<=256,(first,count)
            assert self.owned[ptr]>=8+count*12
            assert count<=self.logical and count<=self.colormap_count
            colors=[]
            for i in range(count):
                rgb=tuple(self.get(ptr+4+i*12+j*4) for j in range(3))
                assert all(x == ((x>>24)*0x01010101) for x in rgb),(
                    "RGB32 fractions are not correctly replicated",i,rgb)
                colors.append(rgb)
            assert self.get(ptr+4+count*12)==0,"missing RGB32 terminator"
            self.last_load=(count,first,tuple(colors))
            self.screen_palette[:count]=colors
            self.palette=list(v for rgb in colors for v in rgb)
            # Amiga library ABI: D0/D1/A0/A1 volatile.
            uc.reg_write(DR[0],0)
            uc.reg_write(DR[1],0xdeadbeef)
            uc.reg_write(AR[0],0xbad000)
            uc.reg_write(AR[1],0xbad100)
            pc=self.get(self.a(7))
            uc.reg_write(AR[7],self.a(7)+4)
            uc.reg_write(UC_M68K_REG_PC,pc)
            return
        return super().os_call(uc,address,size,user)

    def apply(self,index=None,ptr=BANK):
        value=self.index if index is None else index
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
        self.uc.emu_start(CODE+self.p.starts[ENTRY_APPLY],STOP,count=1000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,"hardware stack leak"
        assert self.a(3)==ARGS+4,"must consume exactly one Start(bank) pointer"
        for r,v in saved.items():
            if r in (DR[2],DR[3],AR[3]):continue
            assert self.uc.reg_read(r)==v,(r,hex(v),hex(self.uc.reg_read(r)))
        assert self.d(2)==0,"AMOS integer return D2=0"
        assert not self.owned and not self.open_libraries and not self.open_files
        assert self.plane_writes==0
        assert not self.writes,"Apply must never write the AGAPAL bank"
        return self.d(3)

    def expected_colors(self,index):
        rgb=self.slot_colors[index]
        return tuple(tuple(c*0x01010101 for c in rgb[i*3:i*3+3])
                     for i in range(len(rgb)//3))


def run():
    raw,meta=build()
    assert raw==build()[0], "R32 builder nondeterministic"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    oldtok,old,_=split(BASE.read_bytes())
    tok,parts,_=split(raw)
    assert len(old)==BASE_ENTRIES and len(parts)==BASE_ENTRIES+1
    assert parts[:42]==old[:42] and parts[42]==old[42]+GETP
    assert parts[ENTRY_APPLY]==emit_apply()[0]
    assert tok.startswith(oldtok[:-6]) and audit(parse(raw))["issues"]==[]
    named=[t for t in audit(parse(raw))["tokens"] if t["name"].startswith("aga ")]
    assert len(named)==38
    assert any(t["name"]=="aga palette bank apply" and
               (t["instruction"],t["function"],t["signature"])==(1,43,"00,0")
               for t in named)
    code,labels=emit_apply()
    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    dis=list(md.disasm(code,0))
    assert sum(t.size for t in dis)==len(code),"invalid 68000 instruction boundary"
    boundaries={t.address for t in dis}
    assert all(t in boundaries for t in labels.values()),labels
    assert not any(t.mnemonic in ("dc.w","illegal","trap") for t in dis)
    assert any("mulu.w" in t.mnemonic for t in dis)
    assert any(t.mnemonic=="swap" for t in dis),"RGB24 to RGB32 requires SWAP"

    trials=0
    # First/last slot, 1/2/4/8 bitplanes, Fast/Chip DATA; bank must be read-only.
    for slots in (1,2,8,16,256):
        for depth in (1,2,4,8):
            for index in (0,slots-1):
                for flags in (1,3):
                    m=ApplyMachine(raw,slots=slots,index=index,depth=depth,flags=flags)
                    before=m.get_native()+m.get_payload()
                    old_screen=tuple(m.screen_palette)
                    count=1<<depth
                    expect=m.expected_colors(index)
                    result=m.apply()
                    assert result==1,(slots,depth,index,flags,result)
                    assert m.type_calls==2 and m.load_calls==1 and m.alloc_calls==1
                    assert m.last_load==(count,0,expect),m.last_load
                    assert m.screen_palette[:count]==list(expect)
                    assert m.screen_palette[count:]==list(old_screen[count:]),"higher pens changed"
                    assert m.get_native()+m.get_payload()==before,"bank modified"
                    assert parse_payload(m.get_payload()).entries[index][1]==count
                    assert parse_abk(abk_model(10,m.get_payload(),chip=flags==3))[0]==10
                    trials+=1

    # Palette with fewer colors: never changes higher indexed pens.
    for depth,count,cmcount,logical in (
        (8,1,256,256),(8,2,256,256),(8,3,256,256),
        (8,17,256,256),(8,255,256,256),(8,256,256,256),
        (4,1,16,16),(4,7,16,16),(8,5,5,5),(8,5,256,5)
    ):
        m=ApplyMachine(raw,depth=depth,filled=count,colors=cmcount,logical=logical)
        before=m.get_native()+m.get_payload()
        old_screen=tuple(m.screen_palette)
        assert m.apply()==1
        assert m.load_calls==1 and m.last_load[0]==count
        assert m.screen_palette[:count]==list(m.expected_colors(0))
        assert m.screen_palette[count:]==list(old_screen[count:])
        assert m.get_native()+m.get_payload()==before
        trials+=1

    # Two real stored palettes: successive applications replace the screen
    # but keep bank/index bytes exactly unchanged.
    m=ApplyMachine(raw,slots=8,index=0,filled=256)
    m.populate(1,256,seed=103)
    bank_before=m.get_native()+m.get_payload()
    assert m.apply(0)==1
    first=tuple(m.screen_palette)
    m.type_calls=0
    assert m.apply(1)==1
    assert tuple(m.screen_palette)==m.expected_colors(1)
    assert tuple(m.screen_palette)!=first
    assert m.get_native()+m.get_payload()==bank_before
    assert m.load_calls==2 and m.alloc_calls==2
    trials+=2

    failures=[
        ("negative_index",dict(index=-1)),
        ("index_eq_capacity",dict(index=8)),
        ("index_huge",dict(index=65536)),
        ("null_pointer",dict(ptr=0)),
        ("odd_pointer",dict(ptr=BANK+1)),
        ("short_pointer",dict(ptr=23)),
        ("flag_zero",dict(flags=0)),
        ("flag_nondata",dict(flags=4)),
        ("flag_reserved",dict(flags=5)),
        ("banknumber_low",dict(bankno=4)),
        ("banknumber_high",dict(bankno=65536)),
        ("bank_short",dict(declared=16+7*776)),
        ("bank_long",dict(declared=16+9*776)),
        ("unmapped_header",dict(type_header=False)),
        ("unmapped_end",dict(type_end=False)),
    ]
    for name,opts in failures:
        index=opts.get("index",0)
        ptr=opts.get("ptr",BANK)
        kw={k:v for k,v in opts.items() if k not in ("index","ptr")}
        m=ApplyMachine(raw,**kw)
        before=m.get_native()+m.get_payload()
        colors=tuple(m.screen_palette)
        assert m.apply(index,ptr)==0,name
        assert m.get_native()+m.get_payload()==before and tuple(m.screen_palette)==colors,name
        assert m.load_calls==0 and m.alloc_calls==0 and not m.writes,name
        trials+=1

    # Empty slot, corrupted count (>256), offset, flag, and header must
    # reject without screen changes and without even AllocVec.
    corruptions=[
        (BANK-8,b"x"),(BANK-4,b"\xff"),
        (BANK,b"bad!"),(BANK+4,b"XX"),(BANK+6,b"\0\x02"),
        (BANK+8,b"\0\0"),(BANK+8,b"\x01\x01"),
        (BANK+10,b"\0\x01"),(BANK+12,b"\x01"),
        (BANK+16,b"\xff"),
        (BANK+20,b"\x00\x00"),(BANK+20,b"\x01\x01"),
        (BANK+22,b"\x00\x01"),
    ]
    for addr,patch in corruptions:
        m=ApplyMachine(raw)
        m.uc.mem_write(addr,patch)
        bank_before=m.get_native()+m.get_payload()
        before=tuple(m.screen_palette)
        assert m.apply()==0,(hex(addr),patch)
        assert bank_before==m.get_native()+m.get_payload()
        assert tuple(m.screen_palette)==before
        assert not m.writes and m.alloc_calls==0 and m.load_calls==0
        trials+=1

    screen_invalid=[
        ("state",lambda m:m.put(AMOS+456,0)),
        ("screen",lambda m:m.put(STATE,0)),
        ("graphics",lambda m:m.put(STATE+8,0)),
        ("depth_zero",lambda m:m.put(STATE+28,0)),
        ("depth_over",lambda m:m.put(STATE+28,9)),
        ("ham",lambda m:m.put(STATE+24,0x800)),
        ("ehb",lambda m:m.put(STATE+24,0x80)),
        ("dual",lambda m:m.put(STATE+24,0x400)),
        ("logical_zero",lambda m:m.put(STATE+20,0)),
        ("logical_over",lambda m:m.put(STATE+20,257)),
        ("logical_too_short",lambda m:m.put(STATE+20,255)),
        ("colormap_ptr",lambda m:m.put(SCREEN+48,0)),
        ("colormap_zero",lambda m:m.uc.mem_write(COLORMAP+2,b"\0\0")),
        ("colormap_over",lambda m:m.uc.mem_write(COLORMAP+2,b"\x01\x01")),
        ("colormap_too_short",lambda m:m.uc.mem_write(COLORMAP+2,b"\0\xff")),
    ]
    for name,damage in screen_invalid:
        m=ApplyMachine(raw,filled=256)
        damage(m)
        bank_before=m.get_native()+m.get_payload()
        screen_before=tuple(m.screen_palette)
        assert m.apply()==0,name
        assert bank_before==m.get_native()+m.get_payload()
        assert tuple(m.screen_palette)==screen_before
        assert m.load_calls==0 and m.alloc_calls==0 and not m.writes
        trials+=1

    m=ApplyMachine(raw)
    m.allocation_failure=1
    bank_before=m.get_native()+m.get_payload()
    screen_before=tuple(m.screen_palette)
    assert m.apply()==0
    assert m.alloc_calls==1 and m.load_calls==0 and not m.owned
    assert m.get_native()+m.get_payload()==bank_before
    assert tuple(m.screen_palette)==screen_before
    trials+=1

    print("M13 R32 AGAPAL Apply native 68000 Gate A PASS:",trials,
          "scenarios",flush=True)
    print("R32 candidate:",{k:v for k,v in meta.items() if k!="labels"},flush=True)
    print("Gate B AMOS/WinUAE, Gate C Compiler, Gate D physical AGA: NOT TESTED")

if __name__=="__main__":
    run()
