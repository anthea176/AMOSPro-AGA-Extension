#!/usr/bin/env python3
"""Read-only proof of promoted M19 P2d-L2b LAST_GOOD and frozen historical sources.

Retains the historical filename for existing CI invocations. R68 and R73
are immutable deterministic build sources, independent of moving LAST_GOOD.
No AMOS Compiler, WinUAE, benchmarks or binary writes.
"""
from hashlib import sha256
from pathlib import Path

from active_library import LAST_GOOD_SHA, R68_SHA, R73_SHA, R74_SHA, R75_SHA, R76_SHA, R77_SHA, R78_SHA, R79_SHA, R80_SHA, R81_SHA, R82_SHA, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, P1E_SHA, P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, S1P1F_SHA, S1P1G_SHA, S1P1H_SHA, S1P1I_SHA, S1P2I_SHA, S1P2J_SHA, S1P2K_SHA, S1P2LB_SHA, S1P2LC_SHA, S1P2M_SHA, S2A_SHA, S2B_SHA, S2R_SHA, S2C_SHA, SPRITE_L2B_HISTORICAL_SHAS, verify_active, verify_p2d_l2, verify_p2d_l2b
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
    assert LAST_GOOD_SHA==P2DL2B_SHA
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
    assert len(good)==136708 and sha256(good).hexdigest()==P2DL2B_SHA, "Promoted L2b LAST_GOOD hash must be exact"
    from build_aga_r84_agapic import build as build_r84
    historical_r84,r84meta=build_r84()
    assert len(historical_r84)==67904 and r84meta['sha256']==R84_SHA
    assert sha256(historical_r84).hexdigest()==R84_SHA and historical_r84!=good
    assert sha256(cur).hexdigest() in (R84_SHA,R85_SHA,R86_SHA,R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA,P2D_SHA,S1P1E_SHA,P2DL2_SHA,P2DL2B_SHA, *SPRITE_L2B_HISTORICAL_SHAS), "Active candidate not pinned"
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
    report=inspect(parse(historical_r84))
    assert not report["issues"]
    assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==76
    promoted_report=inspect(parse(good))
    assert not promoted_report["issues"]
    named=[t for t in promoted_report['tokens'] if t['name'].startswith(('aga ','get aga ','make aga ','no aga '))]
    assert len(named)==100 and named[-1]['name']=='aga bob auto update'
    assert label.startswith(("R84 v0.13.29", "R85 v0.13.30", "R86 v0.13.31", "R87 v0.13.32","R88 v0.13.33","M19 P0c","M19 P0d","M19 AP20 V2 ISLANDS","M19 P0j-b7","M19 B7-m2","M19 B8 Clear/Update","M19 B8 S1","M19 P0 Bank Free","M19 P1e","M19 P2d","M19 S1-P1e","M19 S1-P1f","M19 S1-P1g","M19 S1-P1h","M19 S1-P1i", "M19 S1-P2i", "M19 S1-P2j", "M19 S1-P2k", "M19 S1-P2l-b", "M19 S1-P2l-c", "M19 S1-P2m", "M19 S2a-P1", "M19 S2b-P1", "M19 S2r-P1", "M19 S2c-P1c"))
    if cur!=good:
        from c2p_r74_relink import check_cross_r74
        digest=sha256(cur).hexdigest()
        if digest==S2C_SHA:
            from active_library import verify_s2c
            verify_s2c(cur,good)
            assert len(cur)==159844 and label.startswith('M19 S2c-P1c')
        elif digest==S2R_SHA:
            from active_library import verify_s2r
            verify_s2r(cur,good)
            assert len(cur)==154352 and label.startswith('M19 S2r-P1')
        elif digest==S2B_SHA:
            from active_library import verify_s2b
            verify_s2b(cur,good)
            assert len(cur)==152876 and label.startswith('M19 S2b-P1')
        elif digest==S2A_SHA:
            from active_library import verify_s2a
            verify_s2a(cur,good)
            assert len(cur)==151164 and label.startswith('M19 S2a-P1')
        elif digest==S1P2M_SHA:
            from active_library import verify_s1p2m
            verify_s1p2m(cur,good)
            assert len(cur)==149400 and label.startswith('M19 S1-P2m')
        elif digest==S1P2LC_SHA:
            from active_library import verify_s1p2lc
            verify_s1p2lc(cur,good)
            assert len(cur)==150056 and label.startswith('M19 S1-P2l-c')
        elif digest==S1P2LB_SHA:
            from active_library import verify_s1p2lb
            verify_s1p2lb(cur,good)
            assert len(cur)==149940 and label.startswith('M19 S1-P2l-b')
        elif digest==S1P2K_SHA:
            from active_library import verify_s1p2k
            verify_s1p2k(cur, good)
            assert len(cur)==149080 and label.startswith('M19 S1-P2k')
        elif digest==S1P2J_SHA:
            from active_library import verify_s1p2j
            verify_s1p2j(cur, good)
            assert len(cur)==148296 and label.startswith('M19 S1-P2j')
        elif digest==S1P2I_SHA:
            from active_library import verify_s1p2i
            verify_s1p2i(cur, good)
            assert len(cur)==149384 and label.startswith('M19 S1-P2i')
        elif digest==S1P1I_SHA:
            from active_library import verify_s1p1i
            verify_s1p1i(cur, good)
            assert len(cur)==142968 and label.startswith('M19 S1-P1i')
        elif digest==S1P1H_SHA:
            from active_library import verify_s1p1h
            verify_s1p1h(cur, good)
            assert len(cur)==142720 and label.startswith('M19 S1-P1h')
        elif digest==S1P1G_SHA:
            from active_library import verify_s1p1g
            verify_s1p1g(cur, good)
            assert len(cur)==142684 and label.startswith('M19 S1-P1g')
        elif digest==S1P1F_SHA:
            from active_library import verify_s1p1f
            verify_s1p1f(cur, good)
            assert len(cur)==142684 and label.startswith('M19 S1-P1f')
        elif digest==P2DL2B_SHA:
            verify_p2d_l2b(cur,good)
            assert len(cur)==136708 and label.startswith('M19 P2d-L2b')
        elif digest==P2DL2_SHA:
            verify_p2d_l2(cur, good)
            assert len(cur)==136332 and label.startswith('M19 P2d-L2')
        elif digest==S1P1E_SHA:
            _,parts,_=unpack_ap20(cur)
            _,oldparts,_=unpack_ap20(good)
            assert len(parts)==208 and len(oldparts)==203 and parts[:203]==oldparts
            assert len(cur)==142000 and label.startswith("M19 S1-P1e")
        elif digest==P0_FREE_SHA:
            from build_m19_b8_s1_bank_free_in_memory import build_bank_free
            candidate,actual_meta=build_bank_free()
            assert cur==candidate and len(cur)==117896 and actual_meta['sha256']==P0_FREE_SHA
            assert actual_meta['public_commands']==89 and actual_meta['ap20_entries']==185
            assert actual_meta['native_groups']==[142,153,156,177,181] and actual_meta['pc16_max']==31092
            assert label.startswith('M19 P0 Bank Free')
            _,current_parts,_=unpack_ap20(cur)
            from build_m19_ap20_islands_in_memory import build as build_islands
            islands,islands_meta=build_islands()
            assert islands_meta['sha256']==AP20_ISLANDS_SHA
            _,frozen_parts,_=unpack_ap20(islands)
            assert all(current_parts[i]==frozen_parts[i] for i in (142,153,156))
            assert sha256(good).hexdigest()==R84_SHA
        elif digest==B8S1_SHA:
            from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
            candidate,actual_meta=build_b8_safe_retry()
            assert cur==candidate and len(cur)==116104 and actual_meta['sha256']==B8S1_SHA
            assert actual_meta['public_commands']==88 and actual_meta['ap20_entries']==184
            assert actual_meta['native_groups']==[142,153,156,177,181] and actual_meta['pc16_max']==29962
            assert actual_meta['wait_tof_max']==3 and actual_meta['new_native_bytes']==360
            assert label.startswith('M19 B8 S1')
            _,current_parts,_=unpack_ap20(cur)
            from build_m19_ap20_islands_in_memory import build as build_islands
            islands,islands_meta=build_islands()
            assert islands_meta['sha256']==AP20_ISLANDS_SHA
            _,frozen_parts,_=unpack_ap20(islands)
            assert all(current_parts[i]==frozen_parts[i] for i in (142,153,156))
            assert sha256(good).hexdigest()==R84_SHA
        elif digest==B8_SHA:
            from build_m19_b8_first_update_in_memory import build_b8_first_update
            candidate,actual_meta=build_b8_first_update()
            assert cur==candidate and len(cur)==115744 and actual_meta['sha256']==B8_SHA
            assert actual_meta['public_commands']==88 and actual_meta['ap20_entries']==184
            assert actual_meta['native_groups']==[142,153,156,177,181]
            assert actual_meta['pc16_max']==29962
            assert label.startswith('M19 B8 Clear/Update')
            _,current_parts,_=unpack_ap20(cur)
            from build_m19_ap20_islands_in_memory import build as build_islands
            islands,islands_meta=build_islands()
            assert islands_meta['sha256']==AP20_ISLANDS_SHA
            _,frozen_parts,_=unpack_ap20(islands)
            assert all(current_parts[i]==frozen_parts[i] for i in (142,153,156))
            assert sha256(good).hexdigest()==R84_SHA
        elif digest in (B7_SHA,B7M1_SHA,B7M2_SHA):
            from build_m19_p0j_end_lifecycle_in_memory import build as build_b7, build_multiframe
            if digest==B7M2_SHA:
                from build_m19_b7m2_close_reset_in_memory import build_close_reset
                candidate,actual_meta=build_close_reset()
                assert len(candidate)==102400 and actual_meta["predecessor_sha"]==B7M1_SHA
                assert actual_meta["close_stub"]==179 and actual_meta["appended_bytes"]==34
                assert label.startswith("M19 B7-m2")
            else:
                candidate,actual_meta=(build_multiframe() if digest==B7M1_SHA else build_b7())
                assert len(candidate)==(102360 if digest==B7M1_SHA else 102072)
                assert label.startswith("M19 P0j-b7")
            assert cur==candidate and actual_meta["sha256"]==digest
            assert actual_meta["public_commands"]==86
            assert actual_meta["ap20_entries"]==181 and actual_meta["native_groups"]==[142,153,156,177]
            _,parts,_=unpack_ap20(cur)
            from build_m19_ap20_islands_in_memory import build as build_islands
            islands, islands_meta=build_islands()
            assert sha256(islands).hexdigest()==AP20_ISLANDS_SHA
            _,historical_islands,_=unpack_ap20(islands)
            assert (parts[142]==historical_islands[142] and
                    parts[153]==historical_islands[153] and
                    parts[156]==historical_islands[156]), "B7 changed frozen AP20/R84 native islands"
            assert sha256(good).hexdigest()==R84_SHA, "R84 LAST_GOOD changed"
        elif digest==AP20_ISLANDS_SHA:
            from build_m19_ap20_islands_in_memory import build as build_islands
            candidate,actual_meta=build_islands()
            assert cur==candidate and len(candidate)==96908
            assert actual_meta["sha256"]==AP20_ISLANDS_SHA
            assert actual_meta["ap20_entries"]==178 and actual_meta["new_pc16"]==854
            assert label.startswith("M19 AP20 V2 ISLANDS")
            _,current_parts,_=unpack_ap20(cur)
            _,historical_parts,_=unpack_ap20(good)
            group_map=actual_meta["native_groups"]
            assert current_parts[group_map[91]]==historical_parts[82]
            assert current_parts[group_map[92]]==historical_parts[83]
            assert current_parts[group_map[94]].startswith(historical_parts[84])
            assert sha256(good).hexdigest()==R84_SHA
        elif digest==P0D_SHA:
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
        if digest not in (P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,S1P1E_SHA,P2DL2_SHA,P2DL2B_SHA, *SPRITE_L2B_HISTORICAL_SHAS):
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    else:
        # Promoted L2b is byte-identical to the canonical working Lib.
        assert cur==good and sha256(cur).hexdigest()==P2DL2B_SHA
        assert label.startswith('M19 P2d-L2b PROMOTED LAST_GOOD')
        from build_m19_p2d_in_memory import build_p2d
        rebuilt,meta_p2d=build_p2d()
        assert meta_p2d['sha256']==P2D_SHA
        verify_p2d_l2b(cur, rebuilt)
        assert (meta_p2d['commands'],meta_p2d['entries'],meta_p2d['pc16_max'])==(100,203,854)
        from build_m19_b8_s1_bank_free_in_memory import build_bank_free
        historical_p0,p0meta=build_bank_free()
        assert len(historical_p0)==117896 and p0meta['sha256']==P0_FREE_SHA
        assert cur!=historical_p0
    asc=list((ROOT/"tests/current").glob("*.asc"))
    assert len(asc)==1, "Exactly one active ASC must exist, independent of the historical R73 test"
    assert sha256(good).hexdigest()==P2DL2B_SHA
    assert current.read_bytes()==cur and last_good.read_bytes()==good
    assert validated!=promoted and historical_r81!=promoted
    print("P2d-L2b LAST_GOOD PROMOTED / HISTORICAL R84 SOURCE PINNED PASS",P2DL2B_SHA,len(good),
          "active bytes",len(cur),"R81 frozen parent",R81_SHA,"3 inherited links")
    print("Historical R68/R73 builders SHA pinned, one ASC active, no bytes written")

if __name__=="__main__":
    main()
