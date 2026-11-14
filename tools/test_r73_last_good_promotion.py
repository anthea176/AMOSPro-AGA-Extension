#!/usr/bin/env python3
"""Read-only proof that R73 LAST_GOOD remains byte-exact when later C2P candidates are current.

R68 remains a pinned historical source independent from the moving LAST_GOOD.
No AMOS Compiler, WinUAE, benchmarks or binary writes.
"""
from hashlib import sha256
from pathlib import Path

from active_library import LAST_GOOD_SHA, R68_SHA, R73_SHA, R74_SHA, R75_SHA, R76_SHA, R77_SHA, R78_SHA, R79_SHA, R80_SHA, verify_active
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
        from c2p_r74_relink import check_cross_r74
        digest=sha256(cur).hexdigest()
        if digest==R80_SHA:
            from build_c2p_r80_iff_chunky import build as build_r80
            from build_c2p_r76_rpg_fix import state_offset, SITES
            candidate,actual_meta=build_r80()
            assert cur==candidate and actual_meta["sha256"]==R80_SHA
            assert actual_meta["size"]==59708
            assert actual_meta["commands"]==70 and actual_meta["ap20_entries"]==77
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==76 and state_offset(parts)==12070
            assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                       for i,pos,op in SITES),"R80 input state LEA regression"
            assert label.startswith("R80 0.13.25")
        elif digest==R79_SHA:
            from build_c2p_r79_zoom import build as build_r79
            from build_c2p_r76_rpg_fix import state_offset
            candidate,actual_meta=build_r79()
            assert cur==candidate and actual_meta["sha256"]=="ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab"
            assert actual_meta["commands"]==69 and actual_meta["ap20_entries"]==76
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==75 and state_offset(parts)==12070 and label.startswith("R79 0.13.24")
        elif digest==R78_SHA:
            from build_c2p_r78_blit import build as build_r78
            from build_c2p_r76_rpg_fix import state_offset
            candidate,actual_meta=build_r78()
            assert cur==candidate
            assert actual_meta["commands"]==68 and actual_meta["ap20_entries"]==75
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==74 and state_offset(parts)==12070 and label.startswith("R78 0.13.23")
        elif digest==R77_SHA:
            from build_c2p_r77_close import build as build_r77
            from build_c2p_r76_rpg_fix import state_offset
            candidate,actual_meta=build_r77()
            assert cur==candidate
            assert actual_meta["commands"]==67 and actual_meta["ap20_entries"]==74
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==73 and state_offset(parts)==12070 and label.startswith("R77 0.13.22")
        elif digest==R76_SHA:
            from build_c2p_r76_rpg_fix import build as build_r76, state_offset
            candidate,actual_meta=build_r76()
            assert cur==candidate
            assert actual_meta["commands"]==66 and actual_meta["ap20_entries"]==73
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==72 and state_offset(parts)==12070 and label.startswith("R76 0.13.21")
        elif digest==R75_SHA:
            from build_c2p_r75_convert import build as build_r75
            candidate,actual_meta=build_r75()
            assert cur==candidate
            assert actual_meta["commands"]==66 and actual_meta["ap20_entries"]==73
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==72 and label.startswith("R75 0.13.20")
        else:
            from build_c2p_r74_open import build as build_r74
            candidate,actual_meta=build_r74()
            assert cur==candidate and digest==R74_SHA
            assert actual_meta["commands"]==65 and actual_meta["ap20_entries"]==72
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==71 and label.startswith("R74 0.13.19")
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    asc=list((ROOT/"tests/current").glob("*.asc"))
    assert len(asc)==1, "Exactly one active ASC must exist, independent of the historical R73 test"
    assert good==validated
    print("R73 LAST_GOOD PROMOTION BYTE-EXACT PASS",R73_SHA,len(cur),
          "64 commands / 71 AP20 / 3 native links")
    print("Historical R68 source SHA pinned, one ASC active, no bytes written")

if __name__=="__main__":
    main()
