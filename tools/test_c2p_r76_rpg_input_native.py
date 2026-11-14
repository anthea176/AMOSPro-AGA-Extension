#!/usr/bin/env python3
"""Reproduce the actual R74/R75 RPG crash and prove the R76 correction.

All tested bytes are from deterministic native AP20 binaries, not mock
instruction models. The public Aga Screen Open native path (+$02E2)
initializes 144 bytes of keyboard/mouse state using State+displacement.
R74 added 138 bytes to entry08 but failed to rebase seven LEA offsets:
screen open then CLEARS REAL NATIVE CODE in entry33 before any C2P call.

For all R73/R74/R75/R76 binaries, run the actual clear loop and real
Aga Mouse Pressed / Released entry bodies under machine68k on CPU000/020.
R74/R75 MUST be observed corrupting code; R73 and R76 MUST not.

This Gate A proves the memory relocation defect and repair, not WinUAE B.
"""
from __future__ import annotations

from machine68k import CPUType,Machine,Register

from build_opt020_p3_r73 import build as build_r73
from build_c2p_r74_open import build as build_r74
from build_c2p_r75_convert import build as build_r75
from build_c2p_r76_rpg_fix import (
    SITES,STATE_ENTRY0_OFFSET,R73_MOUSE_STATE_DELTA,
    INSERTION_BYTES,MOUSE_STATE_SIZE,build as build_r76,
    state_offset,
)
from compiler_bridge_v2_probe import unwrap_native_parts_v2

CODE=0x160000
STOP=0x1800
EXEC=0x8000
AMOS=0x32000
INPUTCTX=0x34000
STACK=0xe0000
ARGS=0xf0000
MOUSE_RET=0xffffffff

class Runner:
    def __init__(self,parts,*,cpu_type):
        self.m=Machine(cpu_type,4096)
        self.mem=self.m.mem
        self.cpu=self.m.cpu
        self.mem.w32(0,STACK);self.mem.w32(4,CODE)
        self.cpu.execute(self.cpu.pulse_reset())
        self.stop=self.m.create_execute_end("rpg-state-return")
        self.mem.w16(STOP,0xa000|self.m.traps.alloc(lambda _op,_pc:self.stop))
        self.offset=[]
        x=0
        for p in parts:
            self.offset.append(x)
            x+=len(p)
        self.length=x
        self.mem.w_block(CODE,b"".join(parts))
        self.mem.w32(4,EXEC)
        self.state=CODE+STATE_ENTRY0_OFFSET
        assert self.mem.r_block(self.state,40)==bytes(40)
        self.mem.w32(AMOS+0x1c8,self.state)
        self.actual=self.state+state_offset(parts)
        self.legacy=self.state+R73_MOUSE_STATE_DELTA
        self.mem.w_block(INPUTCTX,bytes(64))
        self.mem.w32(self.state+36,INPUTCTX)
        assert self.actual==CODE+self.offset[33]+len(parts[33])-4-MOUSE_STATE_SIZE

    def run(self,entry,offset=0,*,a2_state=False):
        self.cpu.w_sp(STACK)
        self.mem.w32(STACK,STOP)
        self.cpu.w_reg(Register.A5,AMOS)
        self.cpu.w_reg(Register.A3,ARGS)
        if a2_state:self.cpu.w_reg(Register.A2,self.state)
        self.cpu.w_pc(CODE+self.offset[entry]+offset)
        result=self.m.execute(1000000)
        assert result.result is self.stop,(result,self.cpu.r_pc(),entry,offset)
        assert self.cpu.r_sp()==STACK+4,("stack corruption",entry,offset)
        assert self.cpu.r_reg(Register.A5)==AMOS
        assert self.cpu.r_reg(Register.A3)==ARGS
        return self.cpu.r_reg(Register.D3)

    def capture(self):
        return self.mem.r_block(CODE,self.length)

    def close(self):
        self.m.cleanup()


def validate_screen_open_clear(label,parts,*,cpu_type,broken):
    m=Runner(parts,cpu_type=cpu_type)
    try:
        # All 144 input state bytes need resetting on any new AGA screen.
        m.mem.w_block(m.actual,b"\x5a"*MOUSE_STATE_SIZE)
        before=m.capture()
        # Execute the real native LEA+MOVEQ+CLR.L/DBRA/RTS sequence from
        # Aga Screen Open, bypassing only unrelated OS opening calls.
        m.run(6,0x02e2,a2_state=True)
        after=m.capture()
        edits=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
        assert edits,"actual screen initialization performed no writes"
        data_start=m.actual-CODE
        data_end=data_start+MOUSE_STATE_SIZE
        wrong_start=m.legacy-CODE
        if broken:
            assert m.mem.r_block(m.actual+8,40)==b"\x5a"*40,(
                "old buggy build unexpectedly reset the actual mouse data")
            assert any(i<data_start for i in edits),(
                "expected old R74/R75 code overwrite not reproduced")
            assert all(wrong_start<=i<wrong_start+MOUSE_STATE_SIZE for i in edits)
        else:
            assert m.mem.r_block(m.actual,MOUSE_STATE_SIZE)==bytes(MOUSE_STATE_SIZE),(
                "fixed routine failed to reset 144 bytes")
            assert all(data_start<=i<data_end for i in edits),(
                "native executable code was overwritten",label,edits[:12])
        return len(edits)
    finally:
        m.close()


def validate_mouse_poll(label,parts,*,cpu_type,broken,entry):
    m=Runner(parts,cpu_type=cpu_type)
    try:
        # When the mouse context is present but not active, the public
        # mouse function clears four longs in its shared input state.
        m.mem.w32(INPUTCTX+24,0)
        for i in (4,8,12,28):
            m.mem.w32(m.actual+i,0x55667788)
        before=m.capture()
        assert m.run(entry)==MOUSE_RET
        assert m.cpu.r_reg(Register.D2)==0
        after=m.capture()
        edits=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
        data_start=m.actual-CODE
        if broken:
            assert any(i<data_start for i in edits),(
                "old R74/R75 must corrupt executable code",label,entry)
            assert m.mem.r32(m.actual+8)==0x55667788
        else:
            assert all(m.mem.r32(m.actual+i)==0 for i in (4,8,12,28))
            assert all(data_start<=i<data_start+MOUSE_STATE_SIZE for i in edits),(
                "executable mutation from fixed mouse polling",label,entry)
        return len(edits)
    finally:
        m.close()


def main():
    reports=[]
    for label,build in (("R73",build_r73),("R74",build_r74),
                        ("R75",build_r75),("R76",build_r76)):
        _,parts=unwrap_native_parts_v2(build()[0])
        broken=label in ("R74","R75")
        target=state_offset(parts)
        assert target==(R73_MOUSE_STATE_DELTA+(
            INSERTION_BYTES if label!="R73" else 0))
        # Assert the exact seven source locations, not a blind find/replace.
        for idx,pos,op in SITES:
            expected_disp=target if label=="R76" else R73_MOUSE_STATE_DELTA
            assert parts[idx][pos:pos+4]==op.to_bytes(2,"big")+expected_disp.to_bytes(2,"big"),(
                "native relocation signature drift",label,idx,pos)
        for cpu in (CPUType.M68000,CPUType.M68020):
            n=validate_screen_open_clear(label,parts,cpu_type=cpu,broken=broken)
            reports.append((label,str(cpu),"ScreenOpen 144 bytes",n,
                "REPRODUCED corruption" if broken else "SAFE"))
            for entry in (31,32):
                n=validate_mouse_poll(label,parts,cpu_type=cpu,broken=broken,entry=entry)
                reports.append((label,str(cpu),"Mouse"+str(entry),n,
                    "REPRODUCED corruption" if broken else "SAFE"))
    assert len(reports)==24
    print("R76 RPG INPUT STATIC-STATE 68K GATE A PASS",len(reports),
          "native CPU000/020 scenarios; R74/R75 corruption REPRODUCED")
    for line in reports:print(*line)


if __name__=="__main__":
    main()
