#!/usr/bin/env python3
"""R36 Gate A — execute actual 68000 Aga Palette Cycle AP20 bytes.

Check signed direction, exact RGB32 permutation, untouched screen/bank,
proper GetRGB32 and LoadRGB32 ranges, no WaitTOF, AMOS ABI, allocation,
atomic rejection, full 256 pens and repeated/reversed operations.
This is not an AMOS interpreted/WinUAE, Compiler, or hardware test.
"""
import struct
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from ap20_utils import split,digest
from audit_ap20 import parse,inspect as audit
from build_m13_palette_cycle_r36 import (
    build,BASE,BASE_SHA256,LAST_GOOD,LAST_GOOD_SHA256,
    ENTRY_CYCLE,BASE_ENTRIES,GETP,API
)
from m13_palette_cycle_r36_emit import emit_cycle
from test_m13_agapal_fade_r33 import FadeMachine
from test_m13_palette_r28 import COLORMAP
from test_m5_generic import CODE,STOP,STACK,DR,AR,AMOS,STATE,SCREEN,GFX,EXEC
from test_m13_agapal_r30 import ARGS


class CycleMachine(FadeMachine):
    """R33/R35 proven native screen fixture; R36 uses no bank operand."""
    def __init__(self,binary,**kwargs):
        super().__init__(binary,**kwargs)
        self.get_calls=0
        self.expected_first=0
        self.expected_last=1
        self.read_range=None

    def os_call(self,uc,address,size,user):
        if address==GFX-270:
            raise AssertionError("R36 MUST NOT call WaitTOF")
        if address==EXEC-684:
            assert self.d(0)==8+12*(self.expected_last-self.expected_first+1),(
                   "AllocVec size",self.d(0),self.expected_first,self.expected_last)
            assert self.d(1)==1,"MEMF_PUBLIC required; Chip not forced"
            return super().os_call(uc,address,size,user)
        if address==GFX-900:
            self.get_calls+=1
            assert self.get_calls==1,"one GetRGB32 per rotation"
            assert self.load_calls==0,"read entire range before writing"
            assert self.a(0)==COLORMAP,"GetRGB32 must use private ColorMap"
            first,count=self.d(0),self.d(1)
            assert (first,count)==(self.expected_first,
                self.expected_last-self.expected_first+1),(first,count)
            assert first+count<=self.logical and first+count<=self.colormap_count
            pointer=self.a(1)
            assert any(start+4==pointer and n>=8+12*count
                       for start,n in self.owned.items()),"exact scratch payload"
            rgb=self.screen_palette[first:first+count]
            self.read_range=tuple(rgb)
            uc.mem_write(pointer,struct.pack(">"+("I"*count*3),
                              *(v for triplet in rgb for v in triplet)))
            self._os_return()
            return
        if address==GFX-882:
            self.load_calls+=1
            assert self.load_calls==1,"one LoadRGB32 per rotation"
            assert self.get_calls==1,"LoadRGB32 before GetRGB32"
            assert self.a(0)==SCREEN+44,"private ViewPort only"
            ptr=self.a(1)
            assert ptr in self.owned,"table must be AllocVec-owned"
            header=self.get(ptr)
            count,first=header>>16,header&65535
            assert (first,count)==(self.expected_first,
                     self.expected_last-self.expected_first+1),(first,count)
            assert self.owned[ptr]==8+12*count
            assert self.get(ptr+4+12*count)==0,"LoadRGB32 terminator"
            colors=[tuple(self.get(ptr+4+12*i+4*j) for j in range(3))
                    for i in range(count)]
            # 32-bit GetRGB32 values must be preserved bit for bit, not
            # truncated to RGB8 then expanded and lose fractions.
            assert sorted(colors)==sorted(self.read_range),("RGB32 lost",colors)
            self.last_load=(count,first,tuple(colors))
            self.screen_palette[first:first+count]=colors
            self._os_return()
            return
        super().os_call(uc,address,size,user)

    def cycle(self,first=28,last=31,direction=1):
        self.expected_first=first
        self.expected_last=last
        for i,r in enumerate(DR):
            self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS,last)
        self.put(ARGS+4,first)
        self.uc.reg_write(DR[3],direction&0xffffffff)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_CYCLE],STOP,count=5000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,"no RTS"
        assert self.a(7)==STACK+4,"stack imbalance"
        assert self.a(3)==ARGS+8,"A3 must consume Last then First"
        for reg,val in saved.items():
            if reg in (DR[2],DR[3],AR[3]):continue
            assert self.uc.reg_read(reg)==val,(reg,hex(val),hex(self.uc.reg_read(reg)))
        assert self.d(2)==0,"AMOS integer result requires D2=0"
        assert not self.owned and not self.open_libraries and not self.open_files
        assert self.plane_writes==0 and not self.writes,"bank/bitmap changed"
        assert self.wait_calls==0,"no WaitTOF allowed in R36"
        return self.d(3)


def expected_colors(before,first,last,direction):
    original=tuple(before)
    selected=list(original[first:last+1])
    if direction==1:
        selected=selected[-1:]+selected[:-1]
    elif direction==-1:
        selected=selected[1:]+selected[:1]
    else:
        raise AssertionError("test expected only +/-1")
    return original[:first]+tuple(selected)+original[last+1:]


def run():
    raw,meta=build()
    assert raw==build()[0],"nondeterministic R36"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    old_tok,old,_=split(BASE.read_bytes())
    tokens,parts,_=split(raw)
    assert len(old)==BASE_ENTRIES and len(parts)==BASE_ENTRIES+1
    assert parts[:ENTRY_CYCLE-1]==old[:ENTRY_CYCLE-1]
    assert parts[ENTRY_CYCLE-1]==old[ENTRY_CYCLE-1]+GETP
    code,labels=emit_cycle()
    assert parts[ENTRY_CYCLE]==code
    assert tokens.startswith(old_tok[:-6])
    audit_result=audit(parse(raw))
    assert audit_result["issues"]==[],audit_result["issues"]
    named=[t for t in audit_result["tokens"] if t["name"].startswith("aga ")]
    assert len(named)==42
    hit=[t for t in named if t["name"]=="aga palette cycle"]
    assert len(hit)==1
    assert (hit[0]["instruction"],hit[0]["function"],hit[0]["signature"])==(
        1,ENTRY_CYCLE,"00,0,0")
    assert any(t["index"]==ENTRY_CYCLE and t["parameters"]==3 and t["getp"]
               for t in audit_result["parameter_checks"])
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instr=list(dis.disasm(code,0))
    assert sum(i.size for i in instr)==len(code),"bad 68000 opcode"
    bounds={i.address for i in instr}
    assert all(i in bounds for i in labels.values()),labels
    assert not any(i.mnemonic in ("dc.w","illegal","trap") for i in instr)
    assert bytes.fromhex("4eaefc7c") in code,"GetRGB32 missing"
    assert bytes.fromhex("4eaefc8e") in code,"LoadRGB32 missing"
    assert bytes.fromhex("4eae fef2".replace(" ","")) not in code,"WaitTOF forbidden"
    assert b"GetP" not in code
    scenarios=[
      (1,2,2,0,1),
      (2,4,4,0,3),(2,4,4,1,2),
      (4,16,16,0,15),(4,16,16,3,7),
      (8,256,256,0,255),(8,256,256,0,1),
      (8,256,256,1,255),(8,256,256,28,31),
      (8,256,256,224,255),(8,256,256,254,255),
      (8,255,256,0,254),(8,17,256,5,16),
      (8,5,5,0,4),(8,5,256,1,4),(8,256,256,0,224)
    ]
    cases=0
    for depth,logical,cmcount,first,last in scenarios:
        for direction in (1,-1):
            for flags in (1,3):
                m=CycleMachine(raw,depth=depth,logical=logical,
                               colors=cmcount,flags=flags)
                prior=tuple(m.screen_palette)
                bank=m.get_native()+m.get_payload()
                expected=expected_colors(prior,first,last,direction)
                assert m.cycle(first,last,direction)==1,(
                       depth,logical,first,last,direction)
                assert tuple(m.screen_palette)==expected,(
                       "wrong rotation",first,last,direction,
                       m.screen_palette[first:last+1],expected[first:last+1])
                assert m.get_calls==m.load_calls==m.alloc_calls==1
                assert m.rgb_calls==0 and m.type_calls==0
                assert m.get_native()+m.get_payload()==bank
                assert m.last_load==(last-first+1,first,expected[first:last+1])
                cases+=1

    # Repeating a rotation N times must restore the exact RGB32 source.
    # Opposite-direction single rotation must also reverse it.
    for first,last in ((0,1),(28,31),(224,255),(0,255)):
        for direction in (1,-1):
            m=CycleMachine(raw,logical=256,colors=256)
            initial=tuple(m.screen_palette)
            count=last-first+1
            for i in range(count):
                assert m.cycle(first,last,direction)==1
                m.get_calls=m.load_calls=m.alloc_calls=0
            assert tuple(m.screen_palette)==initial,"cycle N repeats did not restore"
            assert m.cycle(first,last,direction)==1
            m.get_calls=m.load_calls=m.alloc_calls=0
            assert m.cycle(first,last,-direction)==1
            assert tuple(m.screen_palette)==initial,"inverse did not restore"
            cases+=1

    # Atomic invalids: no calls or any palette/bank/pixel change.
    invalid=[
      (-1,2,1),(0,-1,1),(1,1,1),(2,1,1),
      (0,256,1),(0,65536,1),(256,257,1),
      (0,1,0),(0,1,2),(0,1,-2),(0,1,65536),
      (0,1,0x7fffffff),(0,1,0xffffffff-1),
      (-255,0,-1),(0,0,1),(255,255,-1),(254,256,-1),
      (0,0x7fffffff,1),(0,0xffffffff,1)
    ]
    for first,last,direction in invalid:
        m=CycleMachine(raw)
        original=tuple(m.screen_palette)
        bank=m.get_native()+m.get_payload()
        assert m.cycle(first,last,direction)==0,(first,last,direction)
        assert m.get_calls==m.load_calls==m.alloc_calls==0
        assert m.get_native()+m.get_payload()==bank
        assert tuple(m.screen_palette)==original
        cases+=1

    badscreens=[
       lambda m:m.put(AMOS+456,0),
       lambda m:m.put(STATE,0),
       lambda m:m.put(STATE+8,0),
       lambda m:m.put(STATE+28,0),
       lambda m:m.put(STATE+28,9),
       lambda m:m.put(STATE+24,0x800),
       lambda m:m.put(STATE+24,0x80),
       lambda m:m.put(STATE+24,0x400),
       lambda m:m.put(STATE+20,0),
       lambda m:m.put(STATE+20,257),
       lambda m:m.put(SCREEN+48,0),
       lambda m:m.uc.mem_write(COLORMAP+2,b"\0\0"),
       lambda m:m.uc.mem_write(COLORMAP+2,b"\x01\x01"),
       lambda m:m.uc.mem_write(COLORMAP+2,b"\0\x0f"),
    ]
    for damage in badscreens:
        m=CycleMachine(raw,depth=8,logical=16,colors=16)
        damage(m)
        palette=tuple(m.screen_palette)
        before=m.get_native()+m.get_payload()
        assert m.cycle(1,2,1)==0
        assert m.get_calls==m.load_calls==m.alloc_calls==0
        assert tuple(m.screen_palette)==palette
        assert m.get_native()+m.get_payload()==before
        cases+=1

    m=CycleMachine(raw,logical=256,colors=256)
    m.allocation_failure=1
    original=tuple(m.screen_palette)
    bank=m.get_native()+m.get_payload()
    assert m.cycle(28,31,1)==0
    assert m.alloc_calls==1 and m.get_calls==m.load_calls==0
    assert tuple(m.screen_palette)==original
    assert m.get_native()+m.get_payload()==bank
    cases+=1

    print("M13 R36 AGA Palette Cycle native 68000 Gate A PASS:",
          cases,"scenarios",flush=True)
    print("R36 deterministic in-memory candidate:",
          {k:v for k,v in meta.items() if k!="labels"},flush=True)
    print("R36 Gate B interpreted AMOS/WinUAE: USER PASS 2026-11-11 (exact test archived); Gate C Compiler and D physical AGA: NOT TESTED")


if __name__=="__main__":
    run()
