#!/usr/bin/env python3
"""R51 static/Unicorn: marker must be inspected but NEVER executed."""
from __future__ import annotations
from struct import pack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from test_m16_capture_r47_unicorn import CaptureMachine,NEW_CODE,MAIN_BASE
from build_m16_r51_relocation_probe import emit_probe,build,MARKER
def test_variant(source,expected,valid_args=True):
    m=CaptureMachine()
    m.uc.mem_write(NEW_CODE,source)
    prev=dict(m.banks)
    try:
        result,_=m.run_capture(x=16 if valid_args else 15,y=16,
                                w=16,h=16,bank=11,index=-1)
        assert result==expected,(result,expected)
    except AssertionError as e:
        if expected in (0,1):
            raise
        assert not str(e),("unexpected Unicorn assertion",str(e))
        assert m.d(3)==expected,(m.d(3),expected)
    assert m.main_calls==[]
    assert m.banks==prev
    assert m.reserve_count==m.erase_count==m.change_count==0
    assert m.alloc_count==m.free_count==0
def run():
    raw,labels=emit_probe()
    assert raw[labels["marker"]:labels["marker"]+6]==MARKER
    assert raw[labels["marker"]-4:labels["marker"]-2]==b"\x60\x00"
    variants=[
      (raw,2,True),   # actual FE11 is never executed, despite being present
      (raw.replace(MARKER,b"\x4e\xb9"+pack(">I",MAIN_BASE)),1,True),
      (raw.replace(MARKER,b"\x4e\xb9"+pack(">I",0)),3,True),
      (raw.replace(MARKER,b"\x4e\xb9"+pack(">I",MAIN_BASE+1)),3,True),
      (raw.replace(MARKER,b"\x4e\x71"+pack(">I",MAIN_BASE)),3,True),
      (raw,0,False),
    ]
    for code,value,ok in variants:
        # Disassemble the patched variant without executing Rjsr, proving
        # no invalid opcode in the actually executed (skipping) path.
        if code!=raw:
            d=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
            assert sum(inst.size for inst in d.disasm(code,0))==len(code)
        test_variant(code,value,ok)
    a,info=build()
    assert (a,info)==build() and len(a)==32012
    print("R51 CPU GATE A PASS: 6 safe relocation recognition cases")
    print("WinUAE interpreted B NOT TESTED; marker NEVER executed")
if __name__=="__main__":
    run()
