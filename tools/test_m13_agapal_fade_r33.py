#!/usr/bin/env python3
"""R33 Gate A: execute the actual new 68000 AP20 Fade To Bank routine.

Unicorn/Capstone with instrumented Exec/graphics.library. This is NOT
WinUAE, AMOS Compiler, visual timing proof or physical AGA validation.
"""
import struct
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from ap20_utils import split,digest
from audit_ap20 import parse,inspect as audit
from build_m13_agapal_fade_r33 import (
    build,BASE,BASE_SHA256,LAST_GOOD,LAST_GOOD_SHA256,
    ENTRY_FADE,BASE_ENTRIES,GETP,
)
from m13_agapal_fade_r33_emit import emit_fade
from test_m13_agapal_apply_r32 import ApplyMachine
from test_m13_agapal_r30 import BANK,ARGS
from test_m5_generic import STATE,GFX,CODE,STOP,STACK,DR,AR,AMOS


class FadeMachine(ApplyMachine):
    def __init__(self,binary,**kwargs):
        super().__init__(binary,**kwargs)
        self.uc.mem_write(GFX-270,b"\x4e\x75")
        self.wait_calls=0
        self.frames=[]
        self.rgb_calls=0
        # An explicitly different starting screen palette for all 256 pens.
        self.screen_palette=[
            tuple(((i*(k*11+19)+k*53+127)&255)*0x01010101
                  for k in range(3))
            for i in range(256)
        ]
        self.original_screen=tuple(self.screen_palette)

    def _os_return(self):
        self.uc.reg_write(DR[0],0)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000)
        self.uc.reg_write(AR[1],0xbad100)
        pc=self.get(self.a(7))
        self.uc.reg_write(AR[7],self.a(7)+4)
        self.uc.reg_write(UC_M68K_REG_PC,pc)

    def os_call(self,uc,address,size,user):
        if address==GFX-270:
            self.wait_calls+=1
            self._os_return()
            return
        if address==GFX-900:
            self.rgb_calls+=1
            assert self.wait_calls==0,"GetRGB32 must happen before first VBL"
            assert self.a(0)!=0 and self.d(0)==0
            count=self.d(1)
            assert 1<=count<=self.logical and count<=self.colormap_count
            pointer=self.a(1)
            assert any(start<=pointer and pointer+12*count<=start+length
                       for start,length in self.owned.items())
            self.uc.mem_write(pointer,struct.pack(">"+("I"*(count*3)),
                *(v for rgb in self.screen_palette[:count] for v in rgb)))
            self._os_return()
            return
        if address==GFX-882:
            assert self.wait_calls==self.load_calls+1,"one VBL before each frame"
            super().os_call(uc,address,size,user)
            self.frames.append(tuple(self.screen_palette))
            return
        super().os_call(uc,address,size,user)

    def fade(self,index=None,ptr=BANK,vbl=3):
        index=self.index if index is None else index
        for i,r in enumerate(DR):
            self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS,index)
        self.put(ARGS+4,ptr)
        self.uc.reg_write(DR[3],vbl&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_FADE],STOP,count=10000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,"routine did not return"
        assert self.a(7)==STACK+4,"stack leak"
        assert self.a(3)==ARGS+8,"three args: D3 duration, two A3 longs"
        for r,v in saved.items():
            if r in (DR[2],DR[3],AR[3]):continue
            assert self.uc.reg_read(r)==v,(r,hex(v),hex(self.uc.reg_read(r)))
        assert self.d(2)==0,"integer return D2"
        assert not self.owned and not self.open_libraries and not self.open_files
        assert self.plane_writes==0 and not self.writes,"bank/bitplane changed"
        return self.d(3)


def expected_frame(source,target,step,duration,frame):
    if frame==duration:
        return target
    src=source>>24
    dst=target>>24
    delta=int((dst-src)*256/duration)       # signed DIVS truncates toward 0
    now=(src*256+delta*frame)>>8
    assert 0<=now<=255,(source,target,duration,frame,now)
    return now*0x01010101


def check_fade(m,retval,duration):
    before_bank=m.get_native()+m.get_payload()
    initial=m.original_screen
    target=m.expected_colors(m.index)
    count=len(target)
    assert retval==1,("fade rejected",duration,count,retval)
    assert m.wait_calls==duration and m.load_calls==duration,(m.wait_calls,m.load_calls,duration)
    assert m.alloc_calls==1 and m.type_calls==2
    assert m.rgb_calls==(0 if duration==1 else 1)
    assert m.get_native()+m.get_payload()==before_bank
    assert len(m.frames)==duration
    for step,frame in enumerate(m.frames,1):
        assert frame[count:]==initial[count:],"upper pens changed"
        expected=tuple(tuple(expected_frame(initial[i][k],target[i][k],
                                step,duration,step) for k in range(3))
                       for i in range(count))
        assert frame[:count]==expected,(duration,step,frame[:min(count,3)],expected[:min(count,3)])
    assert m.frames[-1][:count]==target
    assert m.last_load[0]==count


def run():
    binary,metadata=build()
    assert binary==build()[0],"non-deterministic candidate"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    bt,base,_=split(BASE.read_bytes())
    tok,segments,_=split(binary)
    assert len(base)==BASE_ENTRIES and len(segments)==BASE_ENTRIES+1
    assert segments[:ENTRY_FADE-1]==base[:ENTRY_FADE-1]
    assert segments[ENTRY_FADE-1]==base[ENTRY_FADE-1]+GETP
    code,labels=emit_fade()
    assert segments[ENTRY_FADE]==code
    assert tok.startswith(bt[:-6])
    report=audit(parse(binary))
    assert not report["issues"]
    matches=[t for t in report["tokens"] if t["name"]=="aga fade to bank"]
    assert len(matches)==1 and (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,ENTRY_FADE,"00,0,0")
    assert len([t for t in report["tokens"] if t["name"].startswith("aga ")])==39
    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions=list(md.disasm(code,0))
    assert sum(ins.size for ins in instructions)==len(code),"malformed opcode"
    boundaries={ins.address for ins in instructions}
    assert all(pos in boundaries for pos in labels.values()),labels
    assert not any(ins.mnemonic in ("dc.w","illegal","trap") for ins in instructions)
    assert any(ins.mnemonic.startswith("divs") for ins in instructions)
    assert any(ins.mnemonic.startswith("jsr") and "$fffffef2" in ins.op_str.lower()
               for ins in instructions) or bytes.fromhex("4eaefef2") in code,"WaitTOF LVO missing"

    trials=0
    for depth,duration in ((1,1),(1,2),(4,3),(4,7),(8,1),(8,2),(8,3),(8,11)):
        for flags in (1,3):
            m=FadeMachine(binary,depth=depth,flags=flags)
            bank_before=m.get_native()+m.get_payload()
            result=m.fade(vbl=duration)
            check_fade(m,result,duration)
            assert m.get_native()+m.get_payload()==bank_before
            trials+=1
    # Partial 3/4/17/255 colors, exact color upper bound and long fade.
    for count,duration in ((3,255),(4,16),(17,8),(255,3),(256,4)):
        m=FadeMachine(binary,depth=8,filled=count)
        result=m.fade(vbl=duration)
        check_fade(m,result,duration)
        trials+=1
    # Arbitrary valid index in an 8-slot ABK.
    for index,duration in ((0,4),(7,2)):
        m=FadeMachine(binary,index=index,slots=8,depth=8,filled=4)
        result=m.fade(vbl=duration)
        check_fade(m,result,duration)
        trials+=1
    # Failure before waiting or changing the screen/bank, including allocation.
    failures=[
        (0,0,{},BANK),(256,0,{},BANK),(-1,0,{},BANK),
        (65536,0,{},BANK),(3,-1,{},BANK),(3,8,{},BANK),
        (3,0,{},0),(3,0,{},BANK+1),(3,0,{},23),
        (3,0,{"flags":4},BANK),
        (3,0,{"bankno":4},BANK),(3,0,{"declared":16+7*776},BANK),
        (3,0,{"type_header":False},BANK),(3,0,{"type_end":False},BANK),
    ]
    for duration,index,kwargs,ptr in failures:
        m=FadeMachine(binary,**kwargs)
        before=m.get_native()+m.get_payload()
        screen=tuple(m.screen_palette)
        assert m.fade(index=index,ptr=ptr,vbl=duration)==0,(duration,index,kwargs,ptr)
        assert m.wait_calls==0 and m.load_calls==0 and m.alloc_calls==0
        assert m.rgb_calls==0 and not m.frames
        assert m.get_native()+m.get_payload()==before
        assert tuple(m.screen_palette)==screen
        trials+=1
    for corruption in [
        (BANK-8,b"x"),(BANK,b"bad!"),(BANK+8,b"\0\0"),
        (BANK+20,b"\x01\x01"),(BANK+22,b"\x00\x01")
    ]:
        m=FadeMachine(binary)
        m.uc.mem_write(*corruption)
        before=m.get_native()+m.get_payload()
        assert m.fade(vbl=7)==0
        assert m.get_native()+m.get_payload()==before
        assert m.wait_calls==m.load_calls==m.rgb_calls==0
        trials+=1
    invalid_screens=[
        lambda m:m.put(AMOS+456,0),
        lambda m:m.put(STATE,0),
        lambda m:m.put(STATE+8,0),
        lambda m:m.put(STATE+28,9),
        lambda m:m.put(STATE+24,0x800),
        lambda m:m.put(STATE+24,0x80),
        lambda m:m.put(STATE+24,0x400),
        lambda m:m.put(STATE+20,3),
    ]
    for damage in invalid_screens:
        m=FadeMachine(binary,filled=4)
        damage(m)
        assert m.fade(vbl=3)==0
        assert m.wait_calls==m.rgb_calls==m.load_calls==0
        trials+=1
    m=FadeMachine(binary)
    m.allocation_failure=1
    assert m.fade(vbl=3)==0
    assert m.alloc_calls==1 and m.rgb_calls==0 and m.wait_calls==0 and m.load_calls==0
    trials+=1
    print("M13 R33 AGAPAL Fade To Bank native 68000 Gate A PASS:",
          trials,"scenarios",flush=True)
    print("R33 in-memory candidate:",
          {k:v for k,v in metadata.items() if k!="labels"},flush=True)
    print("Gate B WinUAE, Gate C Compiler, Gate D physical AGA: NOT TESTED")


if __name__=="__main__":
    run()
