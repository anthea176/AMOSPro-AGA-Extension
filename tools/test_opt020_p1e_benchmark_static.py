#!/usr/bin/env python3
"""Static preflight for the OPT020/P1e R60-vs-R69 WinUAE bench.

This does NOT execute AMOS, change a library, run AMOS Compiler,
or claim any timing result. R68's native Region is the R60 baseline.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from compiler_bridge_v2_probe import unwrap_native_parts_v2
from compiler_relocation import GETP
from m18_image_region_emit import emit_image_region
from test_current_amos_blocks import scan
from build_opt020_p1e_r69 import build, IMAGE_REGION_INDEX, R68_SHA
from build_m18_r68_cblock import build as build_r68
from active_library import P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, P2D_SHA, S1P1E_SHA

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmarks/opt020_p1e_r60_vs_r69.asc"
CURRENT = ROOT / "dist/AMOSPro_AGA.Lib"
BANK = ROOT / "tests/current/M16_AGAPIC_SAMPLE_BANK10.abk"
R69_SHA = "9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"
R70_SHA = "fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"
R71_SHA = "1f4cdaabcc0e4ec641b1a60aec06e780187d66b7aaef172131fc7a7011ec85b0"
R72_SHA = "fdb98db259618fbdc3802843e2d6e836cb64acf2d68dc50bbe1133d46d36e67b"
R73_SHA = "c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
R74_SHA = "887f29c0350f47af9d93d1ebf64fc405c8542e897ff0e7d9d95eda6f814c2a23"
R75_SHA = "c5a5a0e45e5b07012247937bf1af0371836f0d119577c102d62a28f4ca1ad3af"
R76_SHA = "9e0a77f3e69c06cfcc96b00b8dc1f23122d559f617beac8762310c5f4bb53897"
R77_SHA = "81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11"
R78_SHA = "9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c"
R79_SHA = "ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab"
R80_SHA = "24e05f7403c07d23db1ff65c9499a032b413fd7d0d140ce8a55e2fd6778b18c6"
R81_SHA = "9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4"
R82_SHA = "b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36"
R83_SHA = "01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb"
R84_SHA = "46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d"
R85_SHA = "4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f"
R86_SHA = "63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f"
R87_SHA = "02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302"
R88_SHA = "69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc"


def main() -> None:
    raw = SOURCE.read_bytes()
    assert raw and all(c < 128 for c in raw), "ASCII source required"
    assert b"\r" not in raw and raw.endswith(b"Loop\n"), "LF / final Loop required"
    assert BANK.is_file(), "AGAPIC sample must be available"
    assert not scan(SOURCE), "AMOS blocks are unbalanced or invalid"
    src = raw.decode("ascii")

    # Historical benchmark baseline comes from pinned R68 builder, not moving LAST_GOOD.
    assert sha256(build_r68()[0]).hexdigest() == R68_SHA
    active = CURRENT.read_bytes()
    active_sha = sha256(active).hexdigest()
    assert active_sha in (R69_SHA, R70_SHA, R71_SHA, R72_SHA, R73_SHA, R74_SHA, R75_SHA, R76_SHA, R77_SHA, R78_SHA, R79_SHA, R80_SHA, R81_SHA, R82_SHA, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, P2D_SHA, S1P1E_SHA)
    candidate, metadata = build()
    assert sha256(candidate).hexdigest() == R69_SHA
    # Post-R82 candidates inherit the historical Region contract; the
    # active P0d / AP20-islands images must not be compared to the R69 Lib.
    if active_sha in (R82_SHA, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, P2D_SHA, S1P1E_SHA):
        # R83 inherits this audited R82 v2 Region, not the old R69 Region.
        # The current AGAPIC v2 Region is intentionally upgraded from the
        # R69 benchmark engine. Rebuild R82 rather than claiming byte
        # identity with an obsolete v1 Region routine.
        from build_agapic_v2_r82_full_preview import build as build_r82
        from build_c2p_r76_rpg_fix import state_offset, SITES
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        latest, meta = build_r82()
        assert meta["sha256"] == R82_SHA
        if active_sha in (P2D_SHA, S1P1E_SHA):
            # The current promoted P2d is proven by its source builder, not
            # accepted solely because its SHA is in the historical allowlist.
            from active_library import verify_active
            from compiler_relocation import unpack_ap20
            verified_current, verified_good, _ = verify_active(ROOT)
            assert verified_current == active and sha256(verified_good).hexdigest()==P2D_SHA
            _, current_units, _ = unpack_ap20(active)
            assert len(current_units) == (208 if active_sha == S1P1E_SHA else 203), "P2d-derived AP20 entry count changed"
            # The P2d groups evolved since the historical four-island image.
            # Pin the source-backed P2d units, not the obsolete predecessor.
            pinned_groups = {
                153: (5558, "6eda5283af42617aa13ad81e24d9130abedc4528ed05b469de2d765d20b4d700"),
                156: (2508, "4e14633eea1ed1fd906ee9f4691e3a0bfc3c6086aaea858f8d2fc1a88ea8f31b"),
            }
            assert all(len(current_units[i]) == size and
                       sha256(current_units[i]).hexdigest() == digest
                       for i, (size, digest) in pinned_groups.items()), (
                "P2d source-backed UNIT153/UNIT156 SHA mismatch")
        elif active_sha in (B8_SHA,B8S1_SHA,P0_FREE_SHA):
            from compiler_relocation import unpack_ap20
            from build_m19_ap20_islands_in_memory import build as build_islands
            if active_sha==P0_FREE_SHA:
                # Keep historical R69/R82 region checks, and verify the
                # installed M19 Bank Free image against its exact builder.
                from build_m19_b8_s1_bank_free_in_memory import build_bank_free
                tested,details=build_bank_free()
                assert len(tested)==117896
                assert details['public_commands']==89 and details['ap20_entries']==185
                assert details['native_groups']==[142,153,156,177,181]
                assert details['pc16_max']==31092 and details['bank_free_index']==184
            elif active_sha==B8S1_SHA:
                from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
                tested,details=build_b8_safe_retry()
                assert len(tested)==116104 and details['predecessor_sha']==B8_SHA
            else:
                from build_m19_b8_first_update_in_memory import build_b8_first_update
                tested,details=build_b8_first_update()
                assert len(tested)==115744
            assert active==tested and details['sha256']==active_sha
            if active_sha!=P0_FREE_SHA:
                assert details['public_commands']==88 and details['ap20_entries']==184
                assert details['native_groups']==[142,153,156,177,181]
                assert details['pc16_max']==29962
            _,native_units,_=unpack_ap20(tested)
            older,oldermeta=build_islands()
            assert oldermeta['sha256']==AP20_ISLANDS_SHA
            _,frozen_units,_=unpack_ap20(older)
            assert all(native_units[n]==frozen_units[n] for n in (142,153,156)), (
                'B8/S1/P0 modified R84-inherited AGAPIC/Region unit')
            if active_sha==P0_FREE_SHA:
                # Appended Bank Free must preserve both B8 S1 Bob units.
                from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
                s1,s1meta=build_b8_safe_retry()
                assert s1meta['sha256']==B8S1_SHA
                _,s1_units,_=unpack_ap20(s1)
                assert native_units[177].startswith(s1_units[177])
                assert native_units[181].startswith(s1_units[181])
        elif active_sha in (B7_SHA,B7M1_SHA,B7M2_SHA):
            from build_m19_p0j_end_lifecycle_in_memory import build as build_b7, build_multiframe
            from build_m19_b7m2_close_reset_in_memory import build_close_reset
            from build_m19_ap20_islands_in_memory import build as build_islands
            from compiler_relocation import unpack_ap20
            if active_sha == B7M2_SHA:
                image, image_meta = build_close_reset()
                expected_size = 102400
                assert image_meta["predecessor_sha"] == B7M1_SHA
            elif active_sha == B7M1_SHA:
                image, image_meta = build_multiframe()
                expected_size = 102360
            else:
                image, image_meta = build_b7()
                expected_size = 102072
            assert active == image and len(image) == expected_size
            assert image_meta["sha256"] == active_sha
            assert (image_meta["public_commands"], image_meta["ap20_entries"],
                    image_meta["native_groups"]) == (86,181,[142,153,156,177])
            previous, previous_meta = build_islands()
            assert previous_meta["sha256"] == AP20_ISLANDS_SHA
            _, current_parts, _ = unpack_ap20(image)
            _, old_parts, _ = unpack_ap20(previous)
            assert all(current_parts[i] == old_parts[i] for i in (142,153,156)), (
                "B7 changed the historical AGA/Region native islands")
        elif active_sha == AP20_ISLANDS_SHA:
            from build_m19_ap20_islands_in_memory import build as build_islands
            from compiler_relocation import unpack_ap20
            candidate_current,meta_current=build_islands()
            assert active==candidate_current and meta_current["sha256"]==AP20_ISLANDS_SHA
            assert meta_current["ap20_entries"]==178 and meta_current["new_pc16"]==854
            _,units,_=unpack_ap20(active)
            _,frozen_units,_=unpack_ap20((ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes())
            assert len(units)==178
            assert units[meta_current["native_groups"][94]].startswith(frozen_units[84])
        elif active_sha == P0D_SHA:
            from build_m19_p0d_bob_blit_in_memory import build as build_p0d
            candidate_current,meta_current=build_p0d()
            assert active==candidate_current and meta_current["sha256"]==P0D_SHA
        elif active_sha == P0C_SHA:
            # P0c retains R88's inherited R84 AGA/state group unchanged.
            # Its public Close stub now routes to a separate BOBS V2 group.
            from build_m19_p0c_screen_close_in_memory import build as build_p0c
            from compiler_relocation import unpack_ap20
            from compiler_bridge_v2_probe import DISPATCH_V2
            candidate_current, meta_current = build_p0c()
            assert active == candidate_current and meta_current["sha256"] == P0C_SHA
            assert meta_current["public_commands"] == 82 and meta_current["ap20_entries"] == 92
            _, units, _ = unpack_ap20(active)
            frozen = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
            assert sha256(frozen.read_bytes()).hexdigest() == R84_SHA
            _, frozen_units, _ = unpack_ap20(frozen.read_bytes())
            assert len(units) == 92 and units[91] == frozen_units[84], (
                "P0c modified inherited R84 AGA native state")
            assert units[90].startswith(DISPATCH_V2), "P0c BOBS V2 dispatcher changed"
            assert meta_current["old_aga_group"] == 91 and meta_current["bridge_group"] == 90
        elif active_sha == R88_SHA:
            from build_m19_p28_r88_in_memory import build as build_r88
            from compiler_relocation import unpack_ap20
            candidate_current, meta_current=build_r88()
            assert active==candidate_current and meta_current["sha256"]==R88_SHA
            _,units,_=unpack_ap20(active)
            from active_library import R84_SHA as FROZEN_R84
            frozen=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
            assert sha256(frozen.read_bytes()).hexdigest()==FROZEN_R84
            _,frozen_units,_=unpack_ap20(frozen.read_bytes())
            assert len(units)==88 and units[87]==frozen_units[84], "R88 modified inherited R84 native state"
        elif active_sha == R87_SHA:
            from build_m19_p25_no_probe import build as build_r87
            from compiler_relocation import unpack_ap20
            candidate_current,meta_current=build_r87()
            assert active==candidate_current and meta_current["sha256"]==R87_SHA
            _,units,_=unpack_ap20(active)
            _,frozen_units,_=unpack_ap20((ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes())
            assert len(units)==87 and units[86]==frozen_units[84]
        elif active_sha == R86_SHA:
            from build_m19_p23_bob_batch import build as build_r86
            candidate_current,meta_current=build_r86()
            assert active==candidate_current and meta_current["sha256"]==R86_SHA
        elif active_sha == R85_SHA:
            from build_m19_p22_fourth_unit_probe import build as build_r85
            actual, actual_meta=build_r85()
            assert active==actual and actual_meta["sha256"]==R85_SHA
            assert actual_meta["ap20_entries"]==87
        elif active_sha == R84_SHA:
            from build_aga_r84_agapic import build as build_r84
            actual, actual_meta=build_r84()
            assert active==actual and actual_meta["sha256"]==R84_SHA
            assert actual_meta["ap20_entries"]==85
        elif active_sha == R83_SHA:
            from build_aga_r83_modular import build as build_r83
            actual, actual_meta = build_r83()
            assert active == actual and actual_meta["sha256"] == R83_SHA
            assert actual_meta["ap20_entries"] == 83
        else:
            assert active == latest
        assert meta["commands"] == 74 and meta["ap20_entries"] == 81
        assert meta["monolith_bytes"] == 60972 and meta["compiler_margin"] == 4562
        parts = unwrap_native_parts_v2(latest)[1]
        assert len(parts) == 80 and state_offset(parts) == 12070
        assert all(parts[i][off+2:off+4] == bytes.fromhex("2f26")
                   for i,off,_ in SITES), "R82 RPG keyboard/mouse LEA regression"
        assert_native_links(parts[:70]); check_cross_r74(parts[:70])
        assert parts[IMAGE_REGION_INDEX] != unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX], (
            "R82 v2 Region unexpectedly identical to the historical R69 Region")
    elif active_sha == R81_SHA:
        from build_c2p_r81_opt020 import build as build_r81
        from build_c2p_r76_rpg_fix import SITES,state_offset
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        assert active==build_r81()[0],"Current R81 differs from exact OPT020 builder"
        parts=unwrap_native_parts_v2(active)[1]
        assert len(parts)==76 and state_offset(parts)==12070
        assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert parts[IMAGE_REGION_INDEX]==unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX],(
            "R81 changed historical optimized Image Region code")
    elif active_sha == R80_SHA:
        from build_c2p_r80_iff_chunky import build as build_r80
        from build_c2p_r76_rpg_fix import SITES,state_offset
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        assert active==build_r80()[0],"Current R80 does not match pinned builder"
        parts=unwrap_native_parts_v2(active)[1]
        assert len(parts)==76 and state_offset(parts)==12070
        assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert parts[IMAGE_REGION_INDEX]==unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX],(
            "R80 changed historical optimized Image Region code")
    elif active_sha == R79_SHA:
        from build_c2p_r79_zoom import build as build_r79
        from build_c2p_r76_rpg_fix import SITES,state_offset
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        assert active==build_r79()[0], "R79 Zoom differs from exact deterministic builder"
        parts=unwrap_native_parts_v2(active)[1]
        assert len(parts)==75 and state_offset(parts)==12070
        assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert parts[IMAGE_REGION_INDEX]==unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX],(
            "R79 changed historical optimized Image Region code")
    elif active_sha == R78_SHA:
        from build_c2p_r78_blit import build as build_r78
        from build_c2p_r76_rpg_fix import SITES,state_offset
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        assert active==build_r78()[0], "R78 Blit differs from exact deterministic builder"
        parts=unwrap_native_parts_v2(active)[1]
        assert len(parts)==74 and state_offset(parts)==12070
        assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert parts[IMAGE_REGION_INDEX]==unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX], (
            "R78 modified the historical optimized Image Region code")
    elif active_sha == R77_SHA:
        from build_c2p_r77_close import build as build_r77
        from build_c2p_r76_rpg_fix import SITES,state_offset
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        assert active==build_r77()[0], "Current R77 C2P Close source drift"
        parts=unwrap_native_parts_v2(active)[1]
        assert len(parts)==73 and state_offset(parts)==12070
        assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert parts[IMAGE_REGION_INDEX]==unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX], (
            "R77 changed the historical optimized Image Region code")
    elif active_sha == R76_SHA:
        from build_c2p_r76_rpg_fix import build as build_r76, SITES, state_offset
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        assert active==build_r76()[0], "Current R76 RPG input fix source drift"
        parts=unwrap_native_parts_v2(active)[1]
        assert len(parts)==72 and state_offset(parts)==12070
        assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert parts[IMAGE_REGION_INDEX]==unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX], (
            "R76 changed the historical optimized Image Region code")
    elif active_sha == R75_SHA:
        from build_c2p_r75_convert import build as build_r75
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        assert active==build_r75()[0], "Current R75 C2P candidate source drift"
        parts=unwrap_native_parts_v2(active)[1]
        assert len(parts)==72
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert parts[IMAGE_REGION_INDEX]==unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX], (
            "R75 changed the historical optimized Image Region code")
    elif active_sha == R74_SHA:
        from build_c2p_r74_open import build as build_r74
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        assert active == build_r74()[0], "Current R74 differs from exact C2P builder"
        native_parts = unwrap_native_parts_v2(active)[1]
        assert len(native_parts) == 71
        assert_native_links(native_parts[:70])
        check_cross_r74(native_parts)
        assert native_parts[IMAGE_REGION_INDEX] == unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX], (
            "R74 modified the historical P1e optimized Region implementation")
    elif active_sha == R73_SHA:
        from build_opt020_p3_r73 import build as build_r73
        from native_relative_links import assert_native_links
        assert active==build_r73()[0],"Current R73 not reproducible"
        assert_native_links(unwrap_native_parts_v2(active)[1])
        assert unwrap_native_parts_v2(active)[1][IMAGE_REGION_INDEX]==unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX]
    elif active_sha == R72_SHA:
        from build_opt020_p2_r72 import build as build_r72
        from native_relative_links import assert_native_links
        assert active == build_r72()[0], "Current R72 changed"
        assert_native_links(unwrap_native_parts_v2(active)[1])
        assert unwrap_native_parts_v2(active)[1][IMAGE_REGION_INDEX] == unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX]
    elif active_sha == R71_SHA:
        from build_opt020_p2_r71 import build as build_r71
        from native_relative_links import assert_native_links
        assert active == build_r71()[0], "Current R71 changed"
        assert_native_links(unwrap_native_parts_v2(active)[1])
        assert unwrap_native_parts_v2(active)[1][IMAGE_REGION_INDEX] == unwrap_native_parts_v2(candidate)[1][IMAGE_REGION_INDEX]
    elif active_sha == R70_SHA:
        from build_opt020_p2_r70 import build as build_r70
        assert active == build_r70()[0], "Historical R70 changed"
    else:
        assert candidate == active
    assert metadata["native_region_index"] == IMAGE_REGION_INDEX
    old_tokens, old_parts = unwrap_native_parts_v2(build_r68()[0])
    new_tokens, new_parts = unwrap_native_parts_v2(candidate)
    old_region, _ = emit_image_region()
    new_region, _ = emit_image_region(opt020=True)
    assert old_tokens == new_tokens and len(old_parts) == len(new_parts) == 70
    assert old_parts[IMAGE_REGION_INDEX] == old_region + GETP
    assert new_parts[IMAGE_REGION_INDEX] == new_region + GETP
    assert all(a == b for i, (a, b) in enumerate(zip(old_parts, new_parts))
               if i != IMAGE_REGION_INDEX), "Benchmark libraries differ outside Region"

    assert 'Load "M16_AGAPIC_SAMPLE_BANK10.abk",10' in src
    assert "Aga Screen Open(320,256,16,$00021000)" in src
    assert "For _CASE=0 To 9" in src and "For _TR=0 To 2" in src
    assert "For _I=1 To _N" in src and "_N=240" in src
    assert "Dim _TM(9,2)" in src and "_TM(_CASE,_TR)=Timer-_T0" in src
    assert "_SUM=_SUM+_OK" in src and "If _SUM<>_N" in src
    assert 'Print "RESULT ";_RESULT' in src and "CLOSE RETURNED" in src
    assert 'Print "CHIP BEFORE/END ";_CF0;" ";_CF1' in src
    for case in range(10):
        assert f"If _CASE={case}\n" in src, f"Missing geometry for case {case}"
    for label in ("OFF16", "ONEPX", "OPA16", "MSK16", "OPA+1", "MSK+1",
                  "CLIP17", "OPA32", "MSK32", "FRG17"):
        assert f'Print "{label}' in src, f"Missing timing report {label}"
    assert "_SX=24 : _SY=12 : _W=16 : _H=16" in src, "Masked test must use central pixels"
    assert "_X=320" in src and "_X=313" in src and "_X=161" in src
    assert "_X=163 : _Y=160 : _MODE=1" in src
    begin = src.index("      For _I=1 To _N\n")
    end = src.index("      Next _I\n", begin)
    loop = src[begin:end]
    assert loop.count("Aga Image Region(") == 1
    assert "_SUM=_SUM+_OK" in loop
    assert not any(x in loop for x in ("Wait Vbl", "Aga Swap", "Blitter Wait",
                                      "Aga Blit Clear", "Print ", "Timer",
                                      "Aga Screen Close", "Aga Bank Image Draw"))
    # The benchmark must remain outside tests/current. The *one* active
    # WinUAE ASC changes as milestones advance (M19 and later): do not
    # freeze its name to an R69..R84 list. Syntax and RAM logging are
    # separately checked by test_current_amos_blocks / test_current_ram_log.
    active_asc = sorted((ROOT / "tests/current").glob("*.asc"))
    assert len(active_asc) == 1, "Exactly one active WinUAE ASC is required"
    assert active_asc[0].name != SOURCE.name, (
        "Historical benchmark must stay under benchmarks/")
    assert sha256(active_asc[0].read_bytes()).digest() != sha256(raw).digest(), (
        "Historical benchmark must not replace active WinUAE ASC")
    print("OPT020/P1e R60-vs-R69 BENCHMARK STATIC PASS: 10 geometries,")
    print("3 trials x 240 calls, no waits/swaps inside timing, R68==R60 Region,")
    print("only native entry 59 differs in pinned R69 baseline; R70/R71/R72 preserve it.")
    print("STATIC ONLY: no AMOS execution, WinUAE timings, or AMOS Compiler.")


if __name__ == "__main__":
    main()
