#!/usr/bin/env python3
"""R52 CPU regression, including TypeOfMem guards before ANY target load.

Unicorn simulates only the memory-map query; it DOES NOT model the real
AMOS link table or prove WinUAE runtime compatibility (Gate B pending).
"""
from __future__ import annotations
from struct import pack
from unicorn.m68k_const import UC_M68K_REG_D3
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from test_m5_generic import EXEC
from test_m16_capture_r47_unicorn import CaptureMachine,NEW_CODE,MAIN_BASE
from build_m16_r52_target_probe import emit_probe,build,MARKER,TARGET_CODE
TYPEOFMEM=EXEC-534
class ProbeMachine(CaptureMachine):
    def __init__(self,allowed=()):
        super().__init__()
        self.allowed=set(allowed)
        self.checked=[]
    def os_call(self,uc,address,size,user):
        if address==TYPEOFMEM:
            adr=self.a(1)
            self.checked.append(adr)
            self._ret(1 if adr in self.allowed else 0)
            return
        super().os_call(uc,address,size,user)
def run_case(target,code_at_target=None,expected=1,valid=True,allowed=True):
    source,labels=emit_probe()
    marker= b"\x4e\xb9"+pack(">I",target) if target is not None else MARKER
    image=source.replace(MARKER,marker)
    m=ProbeMachine(allowed=(target,target+5) if allowed and target is not None else ())
    m.uc.mem_write(NEW_CODE,image)
    if code_at_target is not None:
        m.uc.mem_write(target,code_at_target)
    original=dict(m.banks)
    try:
        result,_=m.run_capture(bank=11,x=16 if valid else 14,y=16,
                     w=16,h=16,index=-1)
        assert result==expected,(expected,result)
    except AssertionError as exc:
        if expected in (0,1):
            raise
        assert m.d(3)==expected,(expected,m.d(3),exc)
        assert not (exc.args and isinstance(exc.args[0],tuple)),exc
    assert m.main_calls==[]
    assert m.banks==original
    assert not m.reserve_count and not m.erase_count and not m.change_count
    assert not m.alloc_count and not m.free_count
    expected_checks=([] if expected in (0,4) else
             [target] if expected==3 else [target,target+5])
    assert m.checked==expected_checks,(expected,m.checked,expected_checks)
def run():
    raw,labels=emit_probe()
    assert raw[labels["marker"]:labels["marker"]+6]==MARKER
    assert raw[labels["marker"]-4:labels["marker"]-2]==b"\x60\x00"
    # Only actually executed instruction path is disassembled for a safe JSR.
    linked=raw.replace(MARKER,b"\x4e\xb9"+pack(">I",MAIN_BASE))
    cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    assert sum(i.size for i in cs.disasm(linked,0))==len(linked)
    run_case(MAIN_BASE,TARGET_CODE,1)
    run_case(MAIN_BASE,b"\x70\x00\x74\x00\x4e\x75",2)
    run_case(MAIN_BASE,TARGET_CODE,3,allowed=False)
    run_case(None,expected=4)
    run_case(MAIN_BASE,TARGET_CODE,0,valid=False)
    run_case(MAIN_BASE+1,expected=4)
    binary,meta=build()
    assert (binary,meta)==build()
    print("R52 CPU GATE A PASS: six variants, 2 TypeOfMem guards, NO Rjsr execution")
    print("Gate B real AMOS/WinUAE NOT TESTED")
if __name__=="__main__":
    run()
