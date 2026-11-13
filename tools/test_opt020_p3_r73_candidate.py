#!/usr/bin/env python3
"""R73 exact in-memory release candidate vs independent P3 structural probe.

Not WinUAE and not Compiler. Fail-closed on unexpected bytes, moved links,
R70-style bad displacements, missing GetP, damaged protected R68 or R72.
"""
from hashlib import sha256
from pathlib import Path

from build_opt020_p3_r73 import build as build_r73
from build_opt020_p2_r72 import build as build_r72
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from compiler_relocation import GETP, unpack_ap20
from native_relative_links import LINKS,assert_native_links

ROOT=Path(__file__).resolve().parents[1]
R68="ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
R72="fdb98db259618fbdc3802843e2d6e836cb64acf2d68dc50bbe1133d46d36e67b"


def main():
    protected_path=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
    active_path=ROOT/"dist/AMOSPro_AGA.Lib"
    original_good=protected_path.read_bytes()
    original_active=active_path.read_bytes()
    assert sha256(original_good).hexdigest()==R68
    previous,_=build_r72()
    assert sha256(previous).hexdigest()==R72
    old_tokens,old_parts=unwrap_native_parts_v2(previous)
    candidate,meta=build_r73()
    assert candidate==build_r73()[0],"Non-deterministic R73 builder"
    assert meta["sha256"]==sha256(candidate).hexdigest()
    tokens,parts=unwrap_native_parts_v2(candidate)
    assert tokens==old_tokens
    assert len(parts)==len(old_parts)==70
    assert {i for i,(a,b) in enumerate(zip(old_parts,parts)) if a!=b}=={60,66}
    assert all(parts[i]==old_parts[i] for i in range(70) if i not in (60,66))
    for i in (55,59,60,66):
        assert parts[i].endswith(GETP),f"GetP lost from {i}"
    assert_native_links(parts)
    for edge in LINKS:
        mutated=list(parts)
        data=bytearray(mutated[edge.source_entry])
        data[edge.source_offset+3] ^= 1
        mutated[edge.source_entry]=bytes(data)
        try:
            assert_native_links(mutated)
        except AssertionError:
            pass
        else:
            raise AssertionError(f"Undetected R70-style link corruption: {edge.name}")
    t1,e1,title1=unpack_ap20(candidate)
    t0,e0,title0=unpack_ap20(previous)
    assert t1==t0 and len(e1)==len(e0)==71
    assert b"0.13.18" in title1 and b"0.13.17" in title0
    assert len(candidate)<65536,"unexpected binary expansion"
    # A new R73 candidate may be installed only in a separate later commit.
    current_sha=sha256(original_active).hexdigest()
    assert current_sha==R72,("R73 test initial run expects the validated R72 active",current_sha)
    assert active_path.read_bytes()==original_active
    assert protected_path.read_bytes()==original_good
    print("R73 EXACT IN-MEMORY RELEASE CANDIDATE GATE A PASS",meta,flush=True)
    print("3 negative relative link corruption cases rejected; R72/R68 bytes unchanged",flush=True)
    print("NO R73 active Lib and NO AMOS Compiler or WinUAE tests performed",flush=True)

if __name__=="__main__":
    main()
