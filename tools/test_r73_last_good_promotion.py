#!/usr/bin/env python3
"""Read-only proof of promoted R84 LAST_GOOD and preserved R68/R73/R81/R82/R83 sources.

Retains the historical filename for existing CI invocations. R68 and R73
are immutable deterministic build sources, independent of moving LAST_GOOD.
No AMOS Compiler, WinUAE, benchmarks or binary writes.
"""
from hashlib import sha256
from pathlib import Path

from active_library import LAST_GOOD_SHA, R68_SHA, R73_SHA, R74_SHA, R75_SHA, R76_SHA, R77_SHA, R78_SHA, R79_SHA, R80_SHA, R81_SHA, R82_SHA, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, verify_active
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
    assert LAST_GOOD_SHA==R84_SHA
    assert sha256(baseline).hexdigest()==R68_SHA, "Historical R68 source drift"
    assert len(baseline)==51064 and baseline!=cur
    assert len(validated)==51608 and sha256(validated).hexdigest()==R73_SHA, "Historical R73 builder drift"
    from build_c2p_r81_opt020 import build as build_r81
    historical_r81, historical_r81_meta=build_r81()
    assert len(historical_r81)==59972 and sha256(historical_r81).hexdigest()==R81_SHA
    assert historical_r81_meta["size"]==59972 and historical_r81_meta["commands"]==70
    assert historical_r81_meta["ap20_entries"]==77
    from build_agapic_v2_r82_full_preview import build as build_r82
    promoted, promoted_meta=build_r82()
    assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA, "Promoted R84 LAST_GOOD hash must be immutable"
    assert sha256(cur).hexdigest() in (R84_SHA,R85_SHA,R86_SHA,R87_SHA,R88_SHA,P0C_SHA,P0D_SHA), "Active candidate not pinned"
    assert len(promoted)==64112 and sha256(promoted).hexdigest()==R82_SHA
    assert good!=historical_r81 and good!=validated and good!=promoted
    from build_aga_r83_modular import build as build_r83
    former_r83,former_meta=build_r83()
    assert len(former_r83)==64188 and sha256(former_r83).hexdigest()==R83_SHA and former_meta["sha256"]==R83_SHA, "Historical R83 source changed"
    assert good!=former_r83
    assert promoted_meta["size"]==64112 and promoted_meta["commands"]==74
    assert promoted_meta["ap20_entries"]==81 and promoted_meta["compiler_margin"]==4562
    assert current.read_bytes()==cur and last_good.read_bytes()==good
    assert meta["commands"]==64 and meta["ap20_entries"]==71
    tokens,parts=unwrap_native_parts_v2(promoted)
    t,entries,title=unpack_ap20(promoted)
    assert tokens==t and len(parts)==80 and len(entries)==81
    assert_native_links(parts[:70])
    from c2p_r74_relink import check_cross_r74
    from build_c2p_r76_rpg_fix import state_offset, SITES
    check_cross_r74(parts[:70])
    assert state_offset(parts)==12070
    assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
               for i,pos,op in SITES), "R81 keyboard/mouse LEA drift"
    report=inspect(parse(good))
    assert not report["issues"]
    assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==76
    assert label.startswith(("R84 v0.13.29", "R85 v0.13.30", "R86 v0.13.31", "R87 v0.13.32","R88 v0.13.33","M19 P0c","M19 P0d"))
    if cur!=good:
        from c2p_r74_relink import check_cross_r74
        digest=sha256(cur).hexdigest()
        if digest==P0D_SHA:
            from build_m19_p0d_bob_blit_in_memory import build as build_p0d
            candidate,actual_meta=build_p0d()
            assert cur==candidate and actual_meta["sha256"]==P0D_SHA
            assert actual_meta["commands"]==83 and actual_meta["entries"]==93
            assert actual_meta["public_signature"]==("aga bob blit",1,88,"00,0,0")
            assert label.startswith("M19 P0d")
            _,parts,_=unpack_ap20(cur)
            _,historical_parts,_=unpack_ap20(good)
            assert (parts[89]==historical_parts[82] and
                    parts[90]==historical_parts[83] and
                    parts[92]==historical_parts[84]), "P0d changed frozen R84 native units"
            assert actual_meta["max_rbsr"]<32766
        elif digest==P0C_SHA:
            from build_m19_p0c_screen_close_in_memory import build as build_p0c
            candidate,actual_meta=build_p0c()
            assert cur==candidate and actual_meta["sha256"]==P0C_SHA
            assert actual_meta["public_commands"]==82 and actual_meta["ap20_entries"]==92
            assert actual_meta["screen_close_index"]==8 and actual_meta["bridge_group"]==90
            assert label.startswith("M19 P0c")
            _,parts,_=unpack_ap20(cur)
            _,historical_parts,_=unpack_ap20(good)
            assert (parts[88]==historical_parts[82] and
                    parts[89]==historical_parts[83] and
                    parts[91]==historical_parts[84]), "P0c altered frozen R84 native units"
            assert actual_meta["max_signed_rbsr"]<32768
        elif digest==R88_SHA:
            from build_m19_p28_r88_in_memory import build as build_r88
            candidate,actual_meta=build_r88()
            assert cur==candidate and actual_meta["sha256"]==R88_SHA
            assert actual_meta["commands"]==78 and actual_meta["entries"]==88
            assert label.startswith("R88 v0.13.33")
            _,current_parts,_=unpack_ap20(cur)
            _,historical_parts,_=unpack_ap20(good)
            assert (current_parts[84]==historical_parts[82] and
                    current_parts[85]==historical_parts[83] and
                    current_parts[87]==historical_parts[84]), "R88 changed frozen R84 native engines"
            assert len(current_parts[86])==7038
            assert sha256(good).hexdigest()==R84_SHA, "R84 LAST_GOOD changed"
        elif digest==R87_SHA:
            from build_m19_p25_no_probe import build as build_r87
            candidate, actual_meta = build_r87()
            assert cur==candidate and actual_meta["sha256"]==R87_SHA
            assert actual_meta["commands"]==77 and actual_meta["ap20_entries"]==87
            assert label.startswith("R87 v0.13.32")
            _, current_parts, _ = unpack_ap20(cur)
            _, historical_parts, _ = unpack_ap20(good)
            assert (current_parts[83]==historical_parts[82] and
                    current_parts[84]==historical_parts[83] and
                    current_parts[86]==historical_parts[84]), "R87 changed frozen R84 native engines"
            assert len(current_parts[85])==5220
            assert sha256(good).hexdigest()==R84_SHA, "LAST_GOOD modified"
        elif digest==R86_SHA:
            from build_m19_p23_bob_batch import build as build_r86
            candidate, actual_meta = build_r86()
            assert cur==candidate and actual_meta["sha256"]==R86_SHA
            assert actual_meta["commands"]==78 and actual_meta["ap20_entries"]==88
            assert label.startswith("R86 v0.13.31")
            _, current_parts, _ = unpack_ap20(cur)
            _, historical_parts, _ = unpack_ap20(good)
            assert (current_parts[84]==historical_parts[82] and
                    current_parts[85]==historical_parts[83] and
                    current_parts[87]==historical_parts[84]), "R86 altered frozen R84 native units"
            assert sha256(good).hexdigest()==R84_SHA, "LAST_GOOD overwritten"
        elif digest==R85_SHA:
            from build_m19_p22_fourth_unit_probe import build as build_r85
            candidate,actual_meta=build_r85()
            assert cur==candidate and actual_meta["sha256"]==R85_SHA
            assert actual_meta["commands"]==77 and actual_meta["ap20_entries"]==87
            assert label.startswith("R85 v0.13.30")
            _,current_parts,_=unpack_ap20(cur)
            _,historical_parts,_=unpack_ap20(good)
            assert (current_parts[83]==historical_parts[82] and
                    current_parts[84]==historical_parts[83] and
                    current_parts[86]==historical_parts[84]), "R85 altered old native groups"
            assert sha256(good).hexdigest()==R84_SHA, "LAST_GOOD overwritten"
        elif digest==R84_SHA:
            from build_aga_r84_agapic import build as build_r84
            candidate,actual_meta=build_r84()
            assert cur==candidate and actual_meta["sha256"]==R84_SHA
            assert actual_meta["commands"]==76 and actual_meta["ap20_entries"]==85
            assert label.startswith("R84 v0.13.29")
        elif digest==R83_SHA:
            from build_aga_r83_modular import build as build_r83
            candidate, actual_meta=build_r83()
            assert cur==candidate and actual_meta["sha256"]==R83_SHA
            assert actual_meta["commands"]==74 and actual_meta["ap20_entries"]==83
            assert label.startswith("R83 v0.13.28")
        elif digest==R82_SHA:
            from build_agapic_v2_r82_full_preview import build as build_r82
            candidate,actual_meta=build_r82()
            assert cur==candidate and actual_meta["sha256"]==R82_SHA
            assert actual_meta["size"]==64112
            assert actual_meta["commands"]==74 and actual_meta["ap20_entries"]==81
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==80 and state_offset(parts)==12070
            assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                       for i,pos,op in SITES),"R82 input-state LEA regression"
            assert label.startswith("R82 0.13.27")
        elif digest==R81_SHA:
            from build_c2p_r81_opt020 import build as build_r81
            from build_c2p_r76_rpg_fix import state_offset, SITES
            candidate,actual_meta=build_r81()
            assert cur==candidate and actual_meta["sha256"]==R81_SHA
            assert actual_meta["size"]==59972
            assert actual_meta["commands"]==70 and actual_meta["ap20_entries"]==77
            _,parts=unwrap_native_parts_v2(cur)
            assert len(parts)==76 and state_offset(parts)==12070
            assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                       for i,pos,op in SITES),"R81 input state LEA regression"
            assert label.startswith("R81 0.13.26")
        elif digest==R80_SHA:
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
        # P0c uses relocated AP20 V2 stubs, with cross-unit routing
        # independently checked by its exact source builder above.
        if digest not in (P0C_SHA,P0D_SHA):
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    asc=list((ROOT/"tests/current").glob("*.asc"))
    assert len(asc)==1, "Exactly one active ASC must exist, independent of the historical R73 test"
    assert sha256(good).hexdigest()==R84_SHA
    assert current.read_bytes()==cur and last_good.read_bytes()==good
    assert validated!=promoted and historical_r81!=promoted
    print("R84 LAST_GOOD FROZEN / ACTIVE SHA-PINNED CANDIDATE PASS",R84_SHA,len(good),
          "active bytes",len(cur),"R81 frozen parent",R81_SHA,"3 inherited links")
    print("Historical R68/R73 builders SHA pinned, one ASC active, no bytes written")

if __name__=="__main__":
    main()
