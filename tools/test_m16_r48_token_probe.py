#!/usr/bin/env python3
"""Host/68000 Gate A for diagnostic R48; NO claim of real AMOS token parsing."""
from __future__ import annotations
from build_m16_r48_token_probe import build,native_probe,GOOD,OFFICIAL,R47
from compiler_relocation import unpack_ap20,unwrap_native_parts
from test_m16_capture_r47_unicorn import CaptureMachine, NEW_CODE
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000

def run():
    probe=native_probe()
    c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instr=list(c.disasm(probe,0))
    assert sum(x.size for x in instr)==len(probe)
    for opts,want in [({},1),({"bank":12},0),({"x":10},0),
        ({"w":17},0),({"h":15},0),({"index":0},0)]:
        m=CaptureMachine()
        m.uc.mem_write(NEW_CODE,probe)
        got,_=m.run_capture(bank=opts.get("bank",11),x=opts.get("x",16),
          y=opts.get("y",16),w=opts.get("w",16),h=opts.get("h",16),
          index=opts.get("index",-1))
        assert got==want,(opts,got,want)
        assert m.alloc_count==m.free_count==m.reserve_count==0
        assert m.erase_count==m.change_count==0
        assert m.main_calls==[], "R48 probe touched AMOS bank internals"
        assert 11 not in m.banks, "R48 probe created bank"
    candidate,info=build()
    assert candidate==build()[0] and len(candidate)==len(R47.read_bytes())
    assert OFFICIAL.read_bytes()==GOOD.read_bytes()
    tok,parts,_=unpack_ap20(candidate)
    assert len(parts)==58 and tok==unpack_ap20(R47.read_bytes())[0]
    source=unwrap_native_parts(candidate)[1]
    assert source[-1].startswith(probe)
    assert all(source[-1][len(probe)+i:len(probe)+i+2]==b"\x4e\x71"
               for i in range(0,len(source[-1])-len(probe),2))
    print("R48 DIAGNOSTIC Gate A PASS: native ABI six-arg probe, "
          "AMOS registers/stack, NO BANK/SYSTEM accesses, 6 cases")
    print("Not WinUAE Gate B. Do not treat a diagnostic as an image capture fix.")

if __name__=="__main__":
    run()
