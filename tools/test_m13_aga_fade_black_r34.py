#!/usr/bin/env python3
"""R34 Gate A — execute the real 68000 Fade To Black AP20 segment.

Unicorn/Capstone validation of ABI, ColorMap, RGB32/DDA exactness,
one WaitTOF+LoadRGB32 per frame, memory, rejects and unchanged pixels.
This is NOT an interpreted AMOS/WinUAE, Compiler or real hardware test.
"""
import struct
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from ap20_utils import split,digest
from audit_ap20 import parse,inspect as audit
from build_m13_aga_fade_black_r34 import (
    build,BASE,BASE_SHA256,LAST_GOOD,LAST_GOOD_SHA256,
    ENTRY_BLACK,BASE_ENTRIES,GETP,API
)
from m13_aga_fade_black_r34_emit import emit_black
from test_m13_agapal_fade_r33 import FadeMachine,expected_frame
from test_m13_palette_r28 import COLORMAP
from test_m5_generic import CODE,STOP,STACK,DR,AR,AMOS,STATE,SCREEN,GFX,EXEC
from test_m13_agapal_r30 import ARGS


class BlackMachine(FadeMachine):
    """R33's proven mock graphics.library and screen, but NO bank operand."""
    def os_call(self,uc,address,size,user):
        if address==EXEC-684:
            assert self.d(0)==8+42*self.logical,("AllocVec scratch size",self.d(0),self.logical)
            assert self.d(1)==1,"MEMF_PUBLIC expected, not forced Chip"
        return super().os_call(uc,address,size,user)

    def fade_black(self,vbl=3):
        for i,r in enumerate(DR):
            self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.uc.reg_write(DR[3],vbl&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_BLACK],STOP,count=10000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,"routine did not return"
        assert self.a(7)==STACK+4,"stack leak"
        assert self.a(3)==ARGS,"Fade To Black has NO A3 operands"
        for r,v in saved.items():
            if r in (DR[2],DR[3]):continue
            assert self.uc.reg_read(r)==v,(r,hex(v),hex(self.uc.reg_read(r)))
        assert self.d(2)==0,"function result D2=0"
        assert not self.owned and not self.open_libraries and not self.open_files
        assert self.plane_writes==0 and not self.writes,"bank/bitmap changed"
        return self.d(3)


def check_black(machine,duration):
    count=machine.logical
    initial=machine.original_screen
    bank_before=machine.get_native()+machine.get_payload()
    assert machine.fade_black(vbl=duration)==1
    assert machine.wait_calls==duration and machine.load_calls==duration
    assert machine.alloc_calls==1 and machine.type_calls==0,"must not touch AGAPAL header"
    assert machine.rgb_calls==(0 if duration==1 else 1)
    assert machine.get_native()+machine.get_payload()==bank_before
    assert len(machine.frames)==duration
    for t,palette in enumerate(machine.frames,1):
        assert palette[count:]==initial[count:],"pen outside logical range modified"
        expected=tuple(tuple(expected_frame(initial[i][k],0,t,duration,t)
                             for k in range(3)) for i in range(count))
        assert palette[:count]==expected,("bad fade",count,duration,t,
                            palette[:min(3,count)],expected[:min(3,count)])
    assert machine.frames[-1][:count]==((0,0,0),)*count,"last frame not exact black"
    assert machine.last_load[0]==count and machine.last_load[1]==0


def run():
    binary,meta=build()
    assert binary==build()[0],"non-deterministic R34 builder"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    oldtok,old,_=split(BASE.read_bytes())
    tok,segments,_=split(binary)
    assert len(old)==BASE_ENTRIES and len(segments)==BASE_ENTRIES+1
    assert segments[:ENTRY_BLACK-1]==old[:ENTRY_BLACK-1]
    assert segments[ENTRY_BLACK-1]==old[ENTRY_BLACK-1]+GETP
    code,labels=emit_black()
    assert segments[ENTRY_BLACK]==code
    assert tok.startswith(oldtok[:-6])
    report=audit(parse(binary))
    assert not report["issues"],report["issues"]
    named=[t for t in report["tokens"] if t["name"].startswith("aga ")]
    assert len(named)==40
    hit=[t for t in named if t["name"]=="aga fade to black"]
    assert len(hit)==1 and (hit[0]["instruction"],hit[0]["function"],hit[0]["signature"])==(1,ENTRY_BLACK,"00")
    assert any(t["index"]==ENTRY_BLACK and t["parameters"]==1 and t["getp"]
               for t in report["parameter_checks"])
    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions=list(md.disasm(code,0))
    assert sum(ins.size for ins in instructions)==len(code),"invalid 68000 opcode"
    boundaries={ins.address for ins in instructions}
    assert all(pos in boundaries for pos in labels.values()),labels
    assert not any(ins.mnemonic in ("dc.w","illegal","trap") for ins in instructions)
    assert any(ins.mnemonic.startswith("divs") for ins in instructions)
    assert bytes.fromhex("4eaefef2") in code,"WaitTOF -270 not found"
    assert bytes.fromhex("4eaefc7c") in code,"GetRGB32 -900 not found"
    assert bytes.fromhex("4eaefc8e") in code,"LoadRGB32 -882 not found"
    assert b"GetP" not in code,"GetP is only the previous AP20 segment trailer"

    count=0
    scenarios=(
        (1,2,2,1),(1,2,2,255),(2,4,4,2),(4,16,16,3),
        (8,256,256,1),(8,256,256,2),(8,256,256,4),
        (8,255,256,3),(8,17,256,16),(8,1,256,2),
        (8,5,5,7),(8,5,256,11)
    )
    for depth,logical,colors,duration in scenarios:
        for flags in (1,3):
            m=BlackMachine(binary,depth=depth,logical=logical,colors=colors,flags=flags)
            check_black(m,duration)
            count+=1
    # Repeating the fade when already black must still succeed.
    m=BlackMachine(binary,depth=8,logical=16,colors=256)
    assert m.fade_black(vbl=3)==1
    assert m.screen_palette[:16]==[(0,0,0)]*16
    before=m.get_native()+m.get_payload()
    # Reinitialise mock counters only, retaining the already-black ColorMap.
    # R33's GetRGB32 mock expects the first sample before a local VBL.
    m.wait_calls=m.load_calls=m.rgb_calls=m.alloc_calls=0
    m.frames=[]
    assert m.fade_black(vbl=5)==1
    assert m.wait_calls==5 and m.load_calls==5
    assert m.rgb_calls==1 and m.alloc_calls==1
    assert m.screen_palette[:16]==[(0,0,0)]*16
    assert m.get_native()+m.get_payload()==before
    count+=2

    # No WaitTOF, GetRGB32 or LoadRGB32 on invalid duration.
    for duration in (0,256,-1,-255,65536,0x7fffffff,0xffffffff):
        m=BlackMachine(binary)
        initial=tuple(m.screen_palette)
        before=m.get_native()+m.get_payload()
        assert m.fade_black(duration)==0,("bad duration",duration)
        assert m.wait_calls==m.load_calls==m.rgb_calls==m.alloc_calls==0
        assert tuple(m.screen_palette)==initial
        assert m.get_native()+m.get_payload()==before
        count+=1

    invalid_screens=[
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
    for damage in invalid_screens:
        m=BlackMachine(binary,depth=8,logical=16,colors=16)
        damage(m)
        initial=tuple(m.screen_palette)
        before=m.get_native()+m.get_payload()
        assert m.fade_black(vbl=3)==0
        assert m.wait_calls==m.load_calls==m.rgb_calls==m.alloc_calls==0
        assert tuple(m.screen_palette)==initial
        assert m.get_native()+m.get_payload()==before
        count+=1
    m=BlackMachine(binary,depth=8,logical=16,colors=16)
    m.allocation_failure=1
    before=m.get_native()+m.get_payload()
    assert m.fade_black(vbl=25)==0
    assert m.alloc_calls==1
    assert m.rgb_calls==m.wait_calls==m.load_calls==0
    assert m.get_native()+m.get_payload()==before
    count+=1

    print("M13 R34 Fade To Black native 68000 Gate A PASS:",count,"scenarios",flush=True)
    print("R34 deterministic in-memory candidate:",
          {k:v for k,v in meta.items() if k!="labels"},flush=True)
    print("R34 Gates B WinUAE, C Compiler, D physical AGA: NOT TESTED")


if __name__=="__main__":
    run()
