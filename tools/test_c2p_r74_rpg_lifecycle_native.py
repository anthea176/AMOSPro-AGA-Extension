#!/usr/bin/env python3
"""RPG M0 regression gate: run the actual legacy Screen Close + AMOS exit
callbacks from byte-pinned R73/R74/R75 native AP20 bodies under machine68k.

The R74 Open Gate A had exercised *cleanup_core* directly, not either hook.
This test executes the real entry08+0 and entry00+0x38 in the complete
contiguous native monolith. All C2P state is deliberately zero, as in the
user's M0_R73_INPUT_DIAG_01.asc and M0_R73_MENU_01.asc (no C2P calls).

Machine68k/OS traps do NOT replace a real WinUAE Gate B.
"""
from __future__ import annotations

from machine68k import Machine, CPUType, Register

from build_opt020_p3_r73 import build as build_r73
from build_c2p_r74_open import build as build_r74
from build_c2p_r75_convert import build as build_r75
from compiler_bridge_v2_probe import unwrap_native_parts_v2

CODE=0x160000
STOP=0x1800
EXEC=0x8000
GFX=0x9000
INTUITION=0xa000
AMOS=0x32000
STATE=0x34000
DB=0x34200
SB0=0x34400
SB1=0x34500
SCREEN=0x35000
ARGS=0xf0000
STACK=0xe0000

SAVED={
    Register.D0:0x12345678, Register.D1:0x23456789,
    Register.D2:0x3456789a, Register.D3:0x56789abc,
    Register.D4:0x456789ab, Register.D5:0x6789abcd,
    Register.D6:0x789abcde, Register.D7:0x13572468,
    Register.A0:0x30000, Register.A1:0x30200,
    Register.A2:0x30400, Register.A3:ARGS,
    Register.A4:0x30600, Register.A5:AMOS,
    Register.A6:0x30800,
}

class Runtime:
    def __init__(self,parts,*,with_screen,with_db=True,has_open_context=False):
        self.m=Machine(CPUType.M68020,4096)
        self.mem=self.m.mem
        self.cpu=self.m.cpu
        self.mem.w32(0,STACK);self.mem.w32(4,CODE)
        self.cpu.execute(self.cpu.pulse_reset())
        self.start=[]
        offset=0
        for part in parts:
            self.start.append(offset)
            offset+=len(part)
        assert offset<65000
        self.mem.w_block(CODE,b"".join(parts))
        self.events=[]
        self.stop=self.m.create_execute_end("rpg-legacy-exit")
        self.trap(STOP,lambda _op,_pc:self.stop)
        for addr,name,value in (
            (GFX-228,"waitblit",0),
            (GFX-270,"waittof",0),
            (EXEC-690,"freevec",0),
            (EXEC-672,"deletemsgport",0),
            (EXEC-414,"closelibrary",0),
            (EXEC-372,"getmsg",0),
            (EXEC-378,"replymsg",0),
            (INTUITION-66,"closescreen",1),
            (INTUITION-774,"freescreenbuffer",0),
        ):
            self.trap(addr,self.make_trap(name,value))
        self.mem.w32(4,EXEC)
        self.mem.w32(AMOS+0x1c8,STATE)
        self.with_screen=with_screen
        self.with_db=with_db
        self.has_open_context=has_open_context
        self.mem.w_block(STATE,bytes(48))
        if with_screen:
            self.mem.w32(STATE+0,SCREEN)
            self.mem.w32(STATE+4,INTUITION)
            self.mem.w32(STATE+8,GFX)
        if with_db:
            self.mem.w32(STATE+32,DB)
        self.mem.w_block(DB,bytes(80))
        self.mem.w32(DB,SB0);self.mem.w32(DB+4,SB1)
        self.mem.w32(DB+20,0)  # Safe and Disp both acknowledged
        self.mem.w_block(DB+56,b"DB_SENTINEL____")
        if has_open_context:
            raise AssertionError("This test deliberately exercises NO C2P context")
        self.mem.w_block(SB0,bytes(16));self.mem.w_block(SB1,bytes(16))

    def trap(self,addr,callback):
        self.mem.w16(addr,0xa000|self.m.traps.alloc(callback))

    def make_trap(self,name,value):
        def callback(_op,_pc):
            self.events.append(name)
            if name=="freevec":
                assert self.cpu.r_reg(Register.A1)==DB, "unexpected FreeVec address"
            elif name=="freescreenbuffer":
                assert self.cpu.r_reg(Register.A0)==SCREEN
                assert self.cpu.r_reg(Register.A1) in (SB0,SB1)
            elif name=="closescreen":
                assert self.cpu.r_reg(Register.A0)==SCREEN
            sp=self.cpu.r_sp()
            pc=self.mem.r32(sp)
            self.cpu.w_sp(sp+4)
            self.cpu.w_pc(pc)
            self.cpu.w_reg(Register.D0,value&0xffffffff)
        return callback

    def run(self,entry,offset=0):
        self.cpu.w_sp(STACK)
        self.mem.w32(STACK,STOP)
        for reg,val in SAVED.items():
            self.cpu.w_reg(reg,val)
        self.cpu.w_pc(CODE+self.start[entry]+offset)
        result=self.m.execute(2000000)
        assert result.result is self.stop,(result,self.cpu.r_pc(),self.events)
        assert self.cpu.r_sp()==STACK+4,("stack corruption",entry,self.cpu.r_sp())
        assert all(self.cpu.r_reg(reg)==val for reg,val in SAVED.items()),(
            "AMOS register corruption",entry,
            [(str(reg),val,self.cpu.r_reg(reg)) for reg,val in SAVED.items() if self.cpu.r_reg(reg)!=val])
        assert self.mem.r_block(DB+56,15)==b"DB_SENTINEL____"

    def close(self):self.m.cleanup()


def test_close_and_exit(label,parts,*,with_screen):
    h=Runtime(parts,with_screen=with_screen,with_db=True)
    try:
        h.run(8,0) # Aga Screen Close (actual public entry)
        assert h.mem.r32(STATE+32)==0, "DoubleBuffer not detached"
        assert h.events.count("freevec")==1, h.events
        assert (h.events.count("freescreenbuffer")==2)==with_screen,h.events
        assert (h.events.count("closescreen")==1)==with_screen,h.events
        assert h.mem.r32(STATE+0)==0, "screen still attached"
        h.events=[]
        h.run(0,0x38) # AMOS extension program-exit callback
        assert not h.events,("unexpected double cleanup after Screen Close",h.events)
        return 1
    finally:h.close()


def test_direct_exit(label,parts,*,with_screen):
    h=Runtime(parts,with_screen=with_screen,with_db=True)
    try:
        h.run(0,0x38) # AMOS may exit without explicit Screen Close
        assert h.mem.r32(STATE+32)==0
        assert h.events.count("freevec")==1,h.events
        assert (h.events.count("closescreen")==1)==with_screen,h.events
        h.events=[]
        h.run(0,0x38) # re-entrant cleanup must be harmless
        assert not h.events
        return 1
    finally:h.close()


def main():
    results=[]
    for label,build in (("R73",build_r73),("R74",build_r74),("R75",build_r75)):
        _,parts=unwrap_native_parts_v2(build()[0])
        for screen in (False,True):
            results.append((label,"ScreenClose+End",screen,test_close_and_exit(label,parts,with_screen=screen)))
            results.append((label,"End directly twice",screen,test_direct_exit(label,parts,with_screen=screen)))
    assert len(results)==12
    print("RPG M0 NATIVE LIFECYCLE GATE A PASS",len(results),"actual paths; not WinUAE")
    for row in results:print(*row)

if __name__=="__main__":main()
