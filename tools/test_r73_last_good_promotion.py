#!/usr/bin/env python3
"""Read-only proof that R73 LAST_GOOD remains byte-exact when R74 is current.

R68 remains a pinned historical source independent from the moving LAST_GOOD.
No AMOS Compiler, WinUAE, benchmarks or binary writes.
"""
from hashlib import sha256
from pathlib import Path

from active_library import LAST_GOOD_SHA, R68_SHA, R73_SHA, R74_SHA, verify_active
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
    assert good==validated,"Protected R73 LAST_GOOD differs from deterministic source"
    assert len(good)==51608 and sha256(good).hexdigest()==R73_SHA
    assert current.read_bytes()==cur and last_good.read_bytes()==good
    assert meta["commands"]==64 and meta["ap20_entries"]==71
    tokens,parts=unwrap_native_parts_v2(good)
    t,entries,title=unpack_ap20(good)
    assert tokens==t and len(parts)==70 and len(entries)==71
    assert_native_links(parts)
    report=inspect(parse(good))
    assert not report["issues"]
    assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==64
    if cur!=good:
        from build_c2p_r74_open import build as build_r74
        from c2p_r74_relink import check_cross_r74
        candidate,actual_meta=build_r74()
        assert cur==candidate and sha256(cur).hexdigest()==R74_SHA
        assert actual_meta["commands"]==65 and actual_meta["ap20_entries"]==72
        _,r74parts=unwrap_native_parts_v2(cur)
        assert len(r74parts)==71
        assert_native_links(r74parts[:70]);check_cross_r74(r74parts)
        assert label.startswith("R74 0.13.19")
    asc=list((ROOT/"tests/current").glob("*.asc"))
    assert len(asc)==1, "Exactly one active ASC must exist, independent of the historical R73 test"
    assert good==validated
    print("R73 LAST_GOOD PROMOTION BYTE-EXACT PASS",R73_SHA,len(cur),
          "64 commands / 71 AP20 / 3 native links")
    print("Historical R68 source SHA pinned, one ASC active, no bytes written")

if __name__=="__main__":
    main()
