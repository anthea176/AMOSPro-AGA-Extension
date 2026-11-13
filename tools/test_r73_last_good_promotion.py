#!/usr/bin/env python3
"""Read-only promotion gate: R73 LAST_GOOD and current are the exact validated V2 binary.

R68 remains a pinned historical source independent from the moving LAST_GOOD.
No AMOS Compiler, WinUAE, benchmarks or binary writes.
"""
from hashlib import sha256
from pathlib import Path

from active_library import LAST_GOOD_SHA, R68_SHA, R73_SHA, verify_active
from audit_ap20 import inspect, parse
from build_m18_r68_cblock import build as build_r68
from build_opt020_p3_r73 import build as build_r73
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from compiler_relocation import unpack_ap20
from native_relative_links import assert_native_links

ROOT=Path(__file__).resolve().parents[1]

def main():
    current=ROOT/"dist/AMOSPro_AGA.Lib"
    last_good=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
    cur,good,label=verify_active(ROOT)
    baseline,_=build_r68()
    validated,meta=build_r73()
    assert LAST_GOOD_SHA==R73_SHA
    assert sha256(baseline).hexdigest()==R68_SHA, "Historical R68 source drift"
    assert len(baseline)==51064 and baseline!=cur
    assert cur==good==validated,"R73 current and LAST_GOOD must be identical to deterministic source"
    assert len(cur)==51608 and sha256(cur).hexdigest()==R73_SHA
    assert current.read_bytes()==cur and last_good.read_bytes()==good
    assert meta["commands"]==64 and meta["ap20_entries"]==71
    tokens,parts=unwrap_native_parts_v2(cur)
    t,entries,title=unpack_ap20(cur)
    assert tokens==t and len(parts)==70 and len(entries)==71
    assert_native_links(parts)
    report=inspect(parse(cur))
    assert not report["issues"]
    assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==64
    asc=list((ROOT/"tests/current").glob("*.asc"))
    assert len(asc)==1 and asc[0].name=="OPT020_P3_R73_INTERPRETED_01.asc"
    assert "PROMOTED LAST_GOOD" in label
    print("R73 LAST_GOOD PROMOTION BYTE-EXACT PASS",R73_SHA,len(cur),
          "64 commands / 71 AP20 / 3 native links")
    print("Historical R68 source SHA pinned, one ASC active, no bytes written")

if __name__=="__main__":
    main()
