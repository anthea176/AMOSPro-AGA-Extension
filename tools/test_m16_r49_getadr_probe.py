#!/usr/bin/env python3
"""M16 R49 native 68000 Gate A with a single mocked Bnk.GetAdr (index 297).

The actual interpreter/AMOS linker remains Gate B, which is NOT simulated.
"""
from __future__ import annotations
from struct import pack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from build_m16_r49_getadr_probe import build,native_probe,MARKER,R48
from test_m16_capture_r47_unicorn import CaptureMachine,NEW_CODE,MAIN_BASE,IDX_GETADR
def linked_code():
    core=native_probe()
    assert core.count(MARKER)==1
    return core.replace(MARKER,b"\x4e\xb9"+pack(">I",MAIN_BASE+16*IDX_GETADR))
def run():
    code=linked_code()
    cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    ins=list(cs.disasm(code,0))
    assert sum(x.size for x in ins)==len(code)
    cases=[({},1,[IDX_GETADR]),({"x":15},0,[]),
      ({"bank":12},0,[]),({"index":0},0,[]),
      ({"w":15},0,[]),({"h":17},0,[])]
    for cfg,expected,maincalls in cases:
        m=CaptureMachine()
        m.uc.mem_write(NEW_CODE,code)
        result,_=m.run_capture(bank=cfg.get("bank",11),x=cfg.get("x",16),
            y=cfg.get("y",16),w=cfg.get("w",16),h=cfg.get("h",16),
            index=cfg.get("index",-1))
        assert result==expected,(cfg,result)
        assert m.main_calls==maincalls,(cfg,m.main_calls)
        assert m.reserve_count==m.erase_count==m.change_count==0
        assert m.alloc_count==m.free_count==0
        assert m.banks=={10: m.banks[10]} and 11 not in m.banks
    # Bank 11 exists: run_capture's inherited 0/1 constraint correctly
    # detects return code 2 AFTER it verifies A7,A3,D2 and preserved registers.
    m=CaptureMachine(occupied=True)
    m.uc.mem_write(NEW_CODE,code)
    baseline=dict(m.banks)
    try:
        m.run_capture(bank=11,x=16,y=16,w=16,h=16,index=-1)
    except AssertionError:
        assert m.d(3)==2,"Existing bank branch did not return 2"
    else:
        raise AssertionError("Existing bank must return diagnostic status 2")
    assert m.main_calls==[IDX_GETADR] and m.banks==baseline
    assert m.reserve_count==m.erase_count==m.change_count==0
    candidate,meta=build()
    assert candidate==build()[0] and len(candidate)==len(R48.read_bytes())
    print("R49 Gate A PASS: 7 cases, AMOS ABI, read-only GetAdr, no bank mutation")
    print("Gate B (real AMOS interpreter/linker) NOT TESTED")
if __name__=="__main__":
    run()
