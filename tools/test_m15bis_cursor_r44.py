#!/usr/bin/env python3
"""M15bis/R44 provisional native 68000 CPU Gate A.

Executes true machine-code AP20 entry and shared window-close helper in
Unicorn, with strict ABI checking and OS-call mocks. This does NOT establish
AMOS/WinUAE runtime correctness, Compiler, or physical Amiga validation.
"""
from struct import pack, unpack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import *

from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from m15bis_cursor_r44_emit import (
    emit_cursor, ENTRY_INDEX, SPRITE_SIZE, MEMF_CHIP_CLEAR,
    LVO_SET_POINTER, LVO_CLEAR_POINTER, LVO_CLOSE_WINDOW,
    LVO_ALLOC_MEM, LVO_FREE_MEM)
from build_m15bis_cursor_r44 import (
    build, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256,
    OWNED_CLOSES, BSR_W, CLOSE_LVO)

CODE = 0x100000
EXEC = 0x20000
INTUI = 0x26000
AMOS = 0x51000
STATE = 0x50000
SCREEN = 0x56000
WINDOW = 0x58000
WINDOW2 = 0x59000
ARGS = 0x5a000
CHIP = 0x310000
STACK = 0xf00000
STOP = 0x10000
DR = [UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
      UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7]
AR = [UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
      UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7]
LVO = (EXEC+LVO_ALLOC_MEM, EXEC+LVO_FREE_MEM,
       INTUI+LVO_SET_POINTER, INTUI+LVO_CLEAR_POINTER, INTUI+LVO_CLOSE_WINDOW)


class CursorMachine:
    def __init__(self, binary, fail_alloc=False):
        self.binary=binary
        self.p=parse(binary)
        self.code, self.labels=emit_cursor()
        self.state_data=CODE+self.p.starts[ENTRY_INDEX]+self.labels["cursor_state"]
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        self.uc.mem_map(0,0x1000000)
        self.uc.mem_write(CODE,self.p.code)
        self.uc.mem_write(STOP,b"\x4e\x71")
        self.put(4,EXEC)
        self.put(AMOS+456,STATE)
        self.put(STATE+0,SCREEN)
        self.put(STATE+4,INTUI)
        self.put(STATE+36,WINDOW)
        self.put(WINDOW+46,SCREEN)
        self.put(WINDOW2+46,SCREEN)
        self.history=[]
        self.fail_alloc=fail_alloc
        self.alloc_count=0
        self.free_count=0
        self.allocations={}
        self.active_pointer=None
        self.closed=[]
        for addr in LVO:self.uc.mem_write(addr,b"\x4e\x75")
        self.uc.hook_add(UC_HOOK_CODE,self.os_hook,begin=0x1f000,end=0x26fff)

    def put(self,addr,v):
        self.uc.mem_write(addr,pack(">I",v&0xffffffff))

    def get(self,addr):
        return unpack(">I",self.uc.mem_read(addr,4))[0]

    def d(self,n):
        return self.uc.reg_read(DR[n])

    def a(self,n):
        return self.uc.reg_read(AR[n])

    def os_hook(self,uc,address,size,userdata):
        assert address in LVO, ("unexpected OS call",hex(address))
        ret=0
        if address==EXEC+LVO_ALLOC_MEM:
            assert self.d(0)==72 and self.d(1)==MEMF_CHIP_CLEAR
            self.alloc_count+=1
            self.history.append(("AllocMem",72,MEMF_CHIP_CLEAR))
            if not self.fail_alloc:
                ret=CHIP+(self.alloc_count-1)*0x1000
                assert ret not in self.allocations
                self.allocations[ret]=72
                uc.mem_write(ret,bytes([0])*72)
        elif address==EXEC+LVO_FREE_MEM:
            assert self.d(0)==72 and self.a(1) in self.allocations
            assert self.active_pointer is None, "FreeMem while pointer attached"
            ptr=self.a(1)
            self.history.append(("FreeMem",ptr,72))
            del self.allocations[ptr]
            self.free_count+=1
        elif address==INTUI+LVO_SET_POINTER:
            assert (self.d(0),self.d(1),self.d(2),self.d(3))==(16,16,0,0)
            assert self.a(0)==self.get(STATE+36)
            ptr=self.a(1)
            assert ptr in self.allocations and self.allocations[ptr]==72
            assert bytes(uc.mem_read(ptr,72))==bytes(72),"sprite must be fully transparent"
            self.active_pointer=self.a(0)
            self.history.append(("SetPointer",self.a(0),ptr))
        elif address==INTUI+LVO_CLEAR_POINTER:
            assert self.a(0) in (WINDOW,WINDOW2)
            self.history.append(("ClearPointer",self.a(0)))
            if self.active_pointer==self.a(0):self.active_pointer=None
        elif address==INTUI+LVO_CLOSE_WINDOW:
            assert self.a(0) in (WINDOW,WINDOW2)
            assert self.active_pointer!=self.a(0),"CloseWindow before ClearPointer"
            self.history.append(("CloseWindow",self.a(0)))
            self.closed.append(self.a(0))
        else: raise AssertionError(("unknown OS call",hex(address)))
        uc.reg_write(DR[0],ret)
        uc.reg_write(DR[1],0xdeadbeef)
        uc.reg_write(AR[0],0xbad000)
        uc.reg_write(AR[1],0xbad100)
        sp=self.a(7)
        uc.reg_write(AR[7],sp+4)
        uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def run_entry(self,visible,addr=None):
        for i,reg in enumerate(DR):
            self.uc.reg_write(reg,0x1100+i)
        for i,reg in enumerate(AR[:7]):
            self.uc.reg_write(reg,0x44000+i*32)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.uc.reg_write(DR[3],visible&0xffffffff)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        entry=CODE+self.p.starts[ENTRY_INDEX] if addr is None else addr
        self.uc.emu_start(entry,STOP,count=30000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP, "entry no RTS"
        assert self.a(7)==STACK+4, "entry unbalanced stack"
        assert self.a(3)==ARGS, "entry consumed unexpected AMOS stacked parameter"
        for reg,v in saved.items():
            if reg not in (DR[2],DR[3]):
                assert self.uc.reg_read(reg)==v, ("entry register ABI",reg)
        assert self.d(2)==0
        assert self.d(3) in (0,1)
        return self.d(3)

    def close_window(self,window=WINDOW):
        for i,r in enumerate(DR): self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x44000+i*32)
        self.uc.reg_write(AR[0],window)
        self.uc.reg_write(AR[6],INTUI)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_INDEX]+self.labels["close_window_hook"],
                          STOP,count=30000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4, "CloseWindow wrapper unbalanced"
        for reg,v in saved.items():
            assert self.uc.reg_read(reg)==v, ("wrapper clobbered",reg)


def run():
    candidate,info=build()
    assert candidate==build()[0],"R44 non-deterministic"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    tok43,old,_=split(BASE.read_bytes())
    tok44,segments,_=split(candidate)
    assert len(old)==54 and len(segments)==55
    assert tok44.startswith(tok43[:-6]) and len(tok44)>len(tok43)
    for i in range(53):
        if i not in OWNED_CLOSES:assert segments[i]==old[i], ("unrelated entry changed",i)
    assert segments[53]==old[53]+b"GetP"
    for i,p in OWNED_CLOSES.items():
        assert segments[i][:p]==old[i][:p] and segments[i][p+4:]==old[i][p+4:]
        assert old[i][p:p+4]==CLOSE_LVO and segments[i][p:p+2]==BSR_W
        disp=unpack(">h",segments[i][p+2:p+4])[0]
        actual=sum(len(x) for x in segments[:i])+p+2+disp
        expected=sum(len(x) for x in segments[:ENTRY_INDEX])+info["labels"]["close_window_hook"]
        assert actual==expected,(i,actual,expected)
    assert segments[40]==old[40] and old[40].count(CLOSE_LVO)==1
    assert not inspect(parse(candidate))["issues"]
    assert len([t for t in inspect(parse(candidate))["tokens"] if t["name"].startswith("aga ")])==49
    code,labels=emit_cursor()
    assert segments[-1]==code and code[-8:]==bytes(8)
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions=list(dis.disasm(code[:labels["cursor_state"]],0))
    assert sum(x.size for x in instructions)==labels["cursor_state"]
    assert all(v in {x.address for x in instructions} for k,v in labels.items() if k!="cursor_state")
    assert all(x.mnemonic not in ("dc.w","illegal") for x in instructions)
    cases=0

    # Normal idempotence and single allocation after 500 hide/show cycles.
    m=CursorMachine(candidate)
    assert m.run_entry(1)==1
    assert m.alloc_count==0 and m.active_pointer is None
    for i in range(500):
        assert m.run_entry(0)==1 and m.active_pointer==WINDOW
        assert m.run_entry(0)==1 and m.active_pointer==WINDOW
        assert m.run_entry(1)==1 and m.active_pointer is None
        cases+=1
    assert m.alloc_count==1 and len(m.allocations)==1
    assert m.get(m.state_data)==CHIP and m.get(m.state_data+4)==WINDOW
    assert m.run_entry(0)==1
    m.close_window()
    assert m.history[-3:]==[("ClearPointer",WINDOW),("CloseWindow",WINDOW),("FreeMem",CHIP,72)]
    assert m.free_count==1 and m.allocations=={}
    assert m.get(m.state_data)==0 and m.get(m.state_data+4)==0
    cases+=1

    # Cold show/normal close must never allocate or free.
    m=CursorMachine(candidate)
    assert m.run_entry(1)==1
    m.close_window()
    assert m.history==[("ClearPointer",WINDOW),("CloseWindow",WINDOW)]
    assert m.alloc_count==m.free_count==0
    cases+=1

    # OOM leaves normal pointer visible and state unmodified.
    m=CursorMachine(candidate,fail_alloc=True)
    assert m.run_entry(0)==0 and m.history==[("AllocMem",72,MEMF_CHIP_CLEAR)]
    assert m.get(m.state_data)==0 and m.active_pointer is None
    cases+=1

    # Invalid arguments and lost/mismatched runtime must do NOTHING.
    for v in (-2147483648,-2,-1,2,3,32767,2147483647):
        m=CursorMachine(candidate)
        assert m.run_entry(v)==0 and m.history==[]
        assert m.allocations=={} and m.get(m.state_data)==0
        cases+=1
    for field,offset,val in (
        ("state",AMOS+456,0),("screen",STATE+0,0),
        ("intuition",STATE+4,0),("window",STATE+36,0),
        ("other_window_screen",WINDOW+46,0)):
        m=CursorMachine(candidate)
        m.put(offset,val)
        assert m.run_entry(0)==0 and m.history==[],field
        cases+=1

    # New Window or reopen: prior state cannot affect a different Window.
    m=CursorMachine(candidate)
    assert m.run_entry(0)==1
    m.put(STATE+36,WINDOW2)
    assert m.run_entry(0)==0
    assert m.run_entry(1)==0
    m.close_window(WINDOW2)  # A different window never clears the pointer.
    assert m.alloc_count==1 and m.free_count==0
    m.put(STATE+36,WINDOW)
    m.close_window(WINDOW)
    assert m.free_count==1 and m.allocations=={}
    m.put(STATE+36,WINDOW2)
    assert m.run_entry(0)==1
    assert m.get(m.state_data+4)==WINDOW2
    m.close_window(WINDOW2)
    assert m.alloc_count==2 and m.free_count==2 and not m.allocations
    cases+=1

    print("M15bis/R44 68000 native CPU preliminary Gate A PASS:",cases,"cases")
    print("49 AP20 commands / 55 segments, four window-close hooks and")
    print("single Chip allocation, SetPointer/ClearPointer, OOM, 500 toggles,")
    print("close-order, state/ABI, unchanged unrelated Palette Save and R43")
    print("R44 in-memory",info["sha256"],"bytes",info["size"])
    print("Gates B AMOS/WinUAE, C Compiler, D Amiga AGA hardware: NOT TESTED")


if __name__=="__main__":
    run()
