#!/usr/bin/env python3
"""Gate A R57: exact replacement at proven R55 bridge offset + real 68000 CPU.

This tests native execution in Unicorn and all AP20/Compiler bridge bytes;
it CANNOT prove that AMOS Compiler re-links the resulting executable correctly.
"""
from __future__ import annotations
from struct import unpack_from

from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from audit_ap20 import inspect,parse
from compiler_relocation import (
    native_from_promoted,unwrap_native_parts,unpack_ap20,is_compiler_wrapped,DISPATCH,
)
from build_m17_r57_rastport import build,TITLE
from build_m17_blit_group_r55 import build as build_r55
from m17_r56_rastport_emit import emit_fill_r56
from m17_blit_group_r55_emit import emit_fill_grouped
from test_m17_r56_rastport import RastMachine,expected_fill
from test_m12_blit_safe_r27 import SafeCopyMachine
from test_m5_generic import DB,BITMAP


def run():
    binary,meta=build()
    assert binary==build()[0],"non deterministic R57"
    prev,_=build_r55()
    tok,parts=unwrap_native_parts(binary)
    tok55,p55=unwrap_native_parts(prev)
    assert tok==tok55 and len(parts)==len(p55)==59
    assert all(parts[i]==p55[i] for i in range(59) if i!=58)
    group,_=emit_fill_grouped()
    rast,labels=emit_fill_r56()
    assert len(group)==620 and len(rast)==580
    assert parts[58][-620:-40]==rast
    assert parts[58][-40:]==b"\x4e\x71"*20
    assert parts[58][:-620]==p55[58][:-620]
    starts=[]; off=0
    for p in parts:
        starts.append(off);off+=len(p)
    assert off==30748
    assert starts[20]+2+unpack_from(">h",parts[20],2)[0]==30128
    assert starts[21]+24+unpack_from(">h",parts[21],24)[0]==starts[20]
    assert parts[19]==p55[19] and parts[21]==p55[21]
    w=unpack_ap20(binary)[1]
    w55=unpack_ap20(prev)[1]
    assert w[:-1]==w55[:-1],"Compiler stubs changed"
    assert len(w[-1])==len(w55[-1])==30780
    assert w[-1][:32]==DISPATCH==w55[-1][:32]
    assert is_compiler_wrapped(binary)
    assert not inspect(parse(binary))["issues"]
    native=native_from_promoted(binary,TITLE)
    assert not inspect(parse(native))["issues"]
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    instr=list(dis.disasm(rast,0))
    assert sum(x.size for x in instr)==len(rast)
    assert all(x.address in {y.address for y in instr} for x in instr)
    assert set(labels.values()).issubset({x.address for x in instr})
    assert all(x.mnemonic not in ("dc.w","illegal","trap") for x in instr)

    cases=0
    for depth in range(1,9):
        for front in (0,1):
            full=(1<<depth)-1
            for pen in sorted({0,1,full//2,full}):
                m=RastMachine(native,depth=depth,front=front)
                before=m.snapshot()
                assert m.run_fill(11,17,9,5,pen)==1
                assert m.pixels_calls==[("rect",11,17,9,5,pen)]
                assert m.waits==1 and m.pending_pixels is None
                for plane in range(depth):
                    assert m.snapshot()[plane]==expected_fill(
                        before[plane],11,17,9,5,pen,plane,m.stride)
                cases+=1
            m=RastMachine(native,depth=depth,front=front)
            assert m.run_clear(7,13,6,4)==1
            assert m.pixels_calls==[("rect",7,13,6,4,0)] and m.waits==1
            cases+=1
            m=RastMachine(native,depth=depth,front=front,physical_exact=True)
            assert m.run_clear(0,0,320,256)==1
            assert m.pixels_calls==[("setrast",0,0,320,256,0)] and m.waits==1
            cases+=1

    # Important: a padded full logical screen is NOT SetRast.
    for depth in (1,5,8):
        m=RastMachine(native,depth=depth)
        assert m.run_clear(0,0,320,256)==1
        assert m.pixels_calls==[("rect",0,0,320,256,0)]
        cases+=1

    for depth in (1,5,8):
        for pending,ready,want in ((0,False,1),(1,False,0),
                                   (1,True,1),(3,False,0),(3,True,1)):
            m=RastMachine(native,depth=depth,pending=pending,safe_ready=ready)
            assert m.run_fill(11,17,9,5,(1<<depth)-1)==want
            assert len(m.pixels_calls)==want and m.waits==want
            assert m.safe_calls==int(bool(pending&1))
            cases+=1

    m=RastMachine(native,depth=8,pending=3,safe_ready=True)
    assert m.run_fill(0,0,10,10,256)==0
    assert not m.pixels_calls and not m.safe_calls
    cases+=1
    m=RastMachine(native,depth=5,pending=3,safe_ready=True)
    m.put(BITMAP+0x100+8+4,0)
    assert m.run_fill(0,0,10,10,1)==0
    assert not m.pixels_calls and not m.safe_calls
    cases+=1

    copy=SafeCopyMachine(native,depth=4,pending=0)
    assert copy.run_copy((2,3,40,50,16,10))==1
    assert len(copy.blits)==copy.waits==1
    cases+=1

    print("R57 Gate A CPU/ABI/AP20/geometry/Safe/Pixels PASS",cases,
          "cases; R55 monolith 30780 bytes; candidate",
          meta["size"],"sha256",meta["sha256"],flush=True)
    print("R57 B/C WinUAE: NOT TESTED (compiled Guru R56 unresolved)",flush=True)

if __name__=="__main__":
    run()
