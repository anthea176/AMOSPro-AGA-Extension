#!/usr/bin/env python3
"""M12/R27 CPU Gate A: real emitted 68000 Safe-aware Copy/Fill/Clear.

Run against the exact R27 in-memory HUNK under Unicorn (68000 model).
Exercise pending Safe bit0, Disp bit1, ready/unready/null SafePort,
BlitBitMap never reached while unsafe, repeated use, clear BSR relocation,
AMOS A3/SP/volatile-register preservation and frozen R26/R10 identity.
WinUAE, Compiler and hardware still NOT TESTED.
"""
from struct import unpack_from
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC

from ap20_utils import split, digest
from audit_ap20 import inspect, parse
from build_m12_blit_safe_r27 import (
    build, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256,
    COPY_ENTRY, FILL_ENTRY, CLEAR_ENTRY, TEXT_ENTRY, GETP,
)
from build_m6_blit_clear_r15 import emit_clear
from m12_blit_safe_r27_emit import emit_copy_safe, emit_fill_safe
from test_m6_blit_copy_r13 import CopyMachine
from test_m6_blit_fill_r14 import FillMachine
from test_m6_blit_clear_r15 import ClearMachine
from test_m5_generic import DR, AR, EXEC, GFX, DB, SB, BITMAP

SAFE_PORT=0x59000
SAFE_REPLY=0x59100

class SafeMixin:
    def __init__(self, raw, pending=0, safe_ready=False, port_valid=True,
                 **kwargs):
        super().__init__(raw, **kwargs)
        self.put(DB+12, SAFE_PORT if port_valid else 0)
        self.put(DB+16, SAFE_PORT+0x100)
        self.put(DB+20, pending)
        self.safe_ready=safe_ready
        self.safe_calls=0
        self.uc.mem_write(EXEC-372, bytes.fromhex("4e75"))

    def os_call(self,uc,address,size,user):
        if address==EXEC-372:
            self.safe_calls+=1
            assert self.a(0)==SAFE_PORT, "wrong SafePort"
            assert self.get(DB+20)&1, "polled Safe without pending flag"
            assert self.a(6)==EXEC, "GetMsg must use ExecBase"
            uc.reg_write(DR[0], SAFE_REPLY if self.safe_ready else 0)
            uc.reg_write(DR[1], 0xdeadbeef) # caller-clobbered registers
            uc.reg_write(AR[0], 0xbad000)
            uc.reg_write(AR[1], 0xbad100)
            pc=self.get(self.a(7))
            uc.reg_write(AR[7],self.a(7)+4)
            uc.reg_write(UC_M68K_REG_PC,pc)
            return
        return super().os_call(uc,address,size,user)

class SafeCopyMachine(SafeMixin,CopyMachine):
    pass
class SafeFillMachine(SafeMixin,FillMachine):
    pass
class SafeClearMachine(SafeMixin,ClearMachine):
    pass

SPECS=(
    (SafeCopyMachine,"Copy",(12,17,90,53,44,23)),
    (SafeFillMachine,"Fill",(14,19,46,31,3)),
    (SafeClearMachine,"Clear",(26,42,50,20)),
)

def invoke(machine,name,args):
    return (machine.run_copy(args) if name=="Copy"
            else machine.run_fill(*args) if name=="Fill"
            else machine.run_clear(*args))

def count_blits(machine,name):
    return len(machine.blits if name=="Copy" else machine.fill_calls)

def check_return(cpu,expected,ctx):
    assert cpu==expected,(ctx,cpu,expected)

def run():
    candidate,meta=build()
    assert build()[0]==candidate,"R27 build not deterministic"
    assert digest(BASE.read_bytes())==BASE_SHA256,"R26 archive changed"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD changed"
    previous_tokens,previous,_=split(BASE.read_bytes())
    tokens,parts,_=split(candidate)
    assert tokens==previous_tokens,"R27 must NOT add/remove tokens"
    assert len(previous)==len(parts)==37
    changed=[i for i,(a,b) in enumerate(zip(previous,parts)) if a!=b]
    assert changed==[COPY_ENTRY,FILL_ENTRY,CLEAR_ENTRY],changed
    copy,copy_labels=emit_copy_safe()
    fill,fill_labels=emit_fill_safe()
    clear,details=emit_clear(len(fill))
    assert parts[COPY_ENTRY]==copy+GETP
    assert parts[FILL_ENTRY]==fill+GETP
    assert parts[CLEAR_ENTRY]==clear
    assert parts[TEXT_ENTRY]==previous[TEXT_ENTRY],"Aga Text R26 changed"
    assert inspect(parse(candidate))["issues"]==[]
    m68k=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    for name,body,labels in (("Copy",copy,copy_labels),
                             ("Fill",fill,fill_labels)):
        ins=list(m68k.disasm(body,0))
        assert sum(i.size for i in ins)==len(body),(name,"bad 68000 code")
        boundaries={i.address for i in ins}
        assert all(v in boundaries for v in labels.values())
        assert all(i.mnemonic not in ("dc.w","illegal","trap") for i in ins)
        assert body.count(bytes.fromhex("4eae"))>=2
    dis=list(m68k.disasm(clear,0))
    assert sum(i.size for i in dis)==len(clear)
    assert sum(i.mnemonic.startswith("bsr") for i in dis)==1
    disp=unpack_from(">h",clear,details["call_at"]+2)[0]
    assert disp==details["bsr_displacement"]
    layout=parse(candidate)
    assert layout.starts[CLEAR_ENTRY]+details["call_at"]+2+disp==layout.starts[FILL_ENTRY], "Clear BSR points to wrong Fill"

    cases=0
    for klass,name,args in SPECS:
        for depth in (1,2,4,8):
            item_args=(args if name!="Fill" else args[:-1]+((1<<depth)-1,))
            for front in (0,1):
                for pending,ready,expected in (
                    (0,False,1),(1,False,0),(1,True,1),
                    (2,False,1),(3,False,0),(3,True,1),
                ):
                    m=klass(candidate,depth=depth,front=front,
                            pending=pending,safe_ready=ready)
                    before=m.snapshot()
                    out=invoke(m,name,item_args)
                    check_return(out,expected,(name,depth,front,pending,ready))
                    assert m.safe_calls==int(bool(pending&1))
                    if expected:
                        assert count_blits(m,name)==(1 if name=="Copy" else depth)
                        assert m.waits==(1 if name=="Copy" else depth)
                        assert m.get(DB+20)==(pending&~1)
                    else:
                        assert m.snapshot()==before,"unsafe bitmap write"
                        assert count_blits(m,name)==0 and m.waits==0
                        assert m.get(DB+20)==pending
                    cases+=1

        # When the port is missing, NO polling, NO DMA, flags unchanged.
        m=klass(candidate,depth=4,front=1,pending=3,
                safe_ready=True,port_valid=False)
        old=m.snapshot()
        assert invoke(m,name,args)==0
        assert not m.safe_calls and count_blits(m,name)==0
        assert m.snapshot()==old and m.get(DB+20)==3
        cases+=1

        # Reject malformed arguments BEFORE consuming a Safe reply.
        badargs=((-1,0,0,0,8,8) if name=="Copy" else
                 (0,0,10,10,256) if name=="Fill" else (0,0,0,10))
        m=klass(candidate,depth=8,front=0,pending=3,safe_ready=True)
        before=m.snapshot()
        assert invoke(m,name,badargs)==0
        assert not m.safe_calls and count_blits(m,name)==0
        assert m.snapshot()==before and m.get(DB+20)==3
        cases+=1

        # After one reply, the consumed Safe bit is not polled again.
        m=klass(candidate,depth=4,front=0,pending=3,safe_ready=True)
        assert invoke(m,name,args)==1 and m.safe_calls==1
        assert m.get(DB+20)==2
        assert invoke(m,name,args)==1 and m.safe_calls==1
        assert m.get(DB+20)==2
        cases+=2

    # Exercise 40 bounded-ready operations with alternated ScreenBuffers.
    for klass,name,args in SPECS:
        m=klass(candidate,depth=4,front=0,pending=0,safe_ready=False)
        for frame in range(40):
            front=frame&1
            m.put(DB+8,front)
            m.expected_bitmap=BITMAP+0x100 if front==0 else BITMAP
            m.put(DB+20,3)
            m.safe_ready=False
            prior=count_blits(m,name)
            assert invoke(m,name,args)==0,("not safe",name,frame)
            assert m.get(DB+20)==3 and count_blits(m,name)==prior
            m.safe_ready=True
            assert invoke(m,name,args)==1,("ready",name,frame)
            assert m.get(DB+20)==2
            cases+=2
        assert m.safe_calls==80

    print("M12 R27 native 68000 Gate A PASS:",cases,
          "Copy/Fill/Clear Safe/Disp, invalid-args, ABI, Clear BSR and 40-frame cases")
    print("M12 R27 in-memory candidate:",meta)
    print("Gate B WinUAE / Compiler / physical AGA: NOT TESTED")

if __name__=="__main__":
    run()
