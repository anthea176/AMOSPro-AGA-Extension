#!/usr/bin/env python3
"""Read-only Gate A probe for the experimental 34-byte unsigned-offset bridge.

Default: execute the actual 68000 dispatcher with Unicorn, including the
compiler-simulated BSR.W and JSR absolute linkage. --static-only runs just
format, boundary and provenance checks (NOT a CPU Gate A result).
No candidate library, AP20 test artifact, or .asc file is written.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from

from active_library import LAST_GOOD_SHA, R69_SHA, R70_SHA, R71_SHA, R72_SHA, R73_SHA, R74_SHA, R75_SHA, R76_SHA, R77_SHA, R78_SHA, R79_SHA, R80_SHA, R81_SHA, R82_SHA, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, verify_active  # SHA-pinned releases.

from compiler_bridge_v2_probe import (
    DISPATCH_V2, MAX_UNIT_BYTES, is_v2_wrapped,
    unwrap_native_parts_v2, wrap_native_ap20_v2,
)
from compiler_relocation import (
    DISPATCH, GETP, is_compiler_wrapped, repack_ap20,
    unpack_ap20, unwrap_native_parts,
)

ROOT = Path(__file__).resolve().parents[1]
R57_SHA256 = 'aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0'  # Historical deterministic native reference
R58_SHA256 = 'c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b'
R59_SHA256 = '00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d'
R60_SHA256 = '00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8'
LAST_GOOD_SHA256 = LAST_GOOD_SHA  # Active promoted identity; historical R63_SHA256 stays immutable below.
R61_SHA256 = 'ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f'
R62_SHA256 = '9fede9f8899ff8ec3c4d978a354e30d16b7e40006c854ac96f547098d786d6f6'
R63_SHA256 = 'fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba'
R64_SHA256 = '4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c'
R65_SHA256 = '6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2'
R66_SHA256 = 'e57840e0c4f1379840e1254f1fb9ab800ce1ad712556efbd872047ea8822c7ca'
R67_SHA256 = 'ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5'
R68_SHA256 = 'ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed'
R69_SHA256 = R69_SHA  # Historical OPT020/P1e R69.
R70_SHA256 = R70_SHA  # Historical R70, failed WinUAE; cannot be active.
R71_SHA256 = R71_SHA  # R71 corrected relative links, WinUAE interpreted PASS.
R72_SHA256 = R72_SHA  # R72 P2 D3 reset, WinUAE Gate B PASS.
R73_SHA256 = R73_SHA  # Fast Icon capture/draw CPU020, Gates A/B/C PASS, promoted.
R74_SHA256 = R74_SHA  # C2P Open only, native Gate A; B/C NOT TESTED.
R75_SHA256 = R75_SHA  # Historical C2P Open+Convert RPG input regression.
R76_SHA256 = R76_SHA  # C2P input-state fix, native Gate A PASS, B/C pending.
R77_SHA256 = R77_SHA  # C2P Close appended to R76, Gate A/B functional PASS.
R78_SHA256 = R78_SHA  # C2P Blit appended to R77, Gates A/B PASS.
R79_SHA256 = R79_SHA  # C2P Zoom appended to R78, Gate A native PASS; B/C pending.
R80_SHA256 = R80_SHA  # Historical C2P IFF->chunky, R80 Gate A/B Runtime 8-plane PASS.
R81_SHA256 = R81_SHA  # Historical MC68020 C2P predecessor, Gates A/B/C PASS.
R82_SHA256 = R82_SHA  # Historical AGAPIC v2
R83_SHA256 = R83_SHA  # Former three-unit LAST_GOOD
R84_SHA256 = R84_SHA  # Promoted AGAPIC native v1/v2
TITLE = b'AP20 bridge V2 probe\0'
TITLE += bytes(len(TITLE) & 1)
TOKENS = b'\0' * 6  # Valid minimal terminated AP20 token table.
TARGET = bytes.fromhex('76634e75')  # MOVEQ #99,D3 ; RTS (valid 68000).


def template() -> bytes:
    return (pack('>5I', 0x3f3, 0, 1, 0, 0) + pack('>I', 0)
            + pack('>I', 0x3e9) + pack('>I', 0) + pack('>I', 0x3f2))


def native_at(offset: int) -> bytes:
    assert offset % 2 == 0 and 0 <= offset <= 65498
    # Synthetic first routine is NOP padding, target is the second routine.
    return repack_ap20(template(), TOKENS,
                       [bytes.fromhex('4e71') * (offset // 2), TARGET], TITLE)


def reject(call, what: str) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError('Expected ValueError: ' + what)


def static_checks() -> tuple[list[tuple[int, bytes]], bytes | None]:
    # 65534 is the maximum WORD-count-derived byte size supported by the
    # unchanged AMOS 365 +APComp.s LSL.W loader. 65536 would wrap to zero.
    assert len(DISPATCH) == 32 and len(DISPATCH_V2) == 34
    assert MAX_UNIT_BYTES == 65534
    tests = []
    offsets = [0, 30000, 32766, 32768, 40000, 65496]
    for off in offsets:
        source = native_at(off)
        v2 = wrap_native_ap20_v2(source, TITLE)
        assert v2 == wrap_native_ap20_v2(source, TITLE)
        assert is_v2_wrapped(v2) and not is_compiler_wrapped(v2)
        tok, native_parts, old_title = unpack_ap20(source)
        vt, entries, title = unpack_ap20(v2)
        assert vt == tok and title == old_title
        assert len(entries) == len(native_parts) + 1 == 3
        assert len(entries[-1]) == len(DISPATCH_V2) + off + len(TARGET)
        assert len(entries[-1]) <= MAX_UNIT_BYTES
        assert entries[1][:4] == b'\xfe\x31' + pack('>H', 2)
        assert unpack_from('>H', entries[1], 4)[0] == off
        assert entries[1][6:8] == b'\x4e\x75'
        assert unwrap_native_parts_v2(v2) == (tok, native_parts)
        reject(lambda: wrap_native_ap20_v2(v2, TITLE), 'V2 double wrap')
        tests.append((off, entries[-1]))
    reject(lambda: wrap_native_ap20_v2(native_at(65498), TITLE), '65536-byte V2 blob')
    # Never silently accept the old C1 bridge into V2 as if it were native.
    from compiler_relocation import wrap_native_ap20
    v1 = wrap_native_ap20(native_at(30000), TITLE)
    reject(lambda: wrap_native_ap20_v2(v1, TITLE), 'V1 double wrap')
    reject(lambda: unwrap_native_parts_v2(v1), 'V1 masquerades as V2')
    # Marker-only entries remain unmodified through the V2 roundtrip.
    marker = repack_ap20(template(), TOKENS, [b'', GETP, TARGET], TITLE)
    check = wrap_native_ap20_v2(marker, TITLE)
    assert unpack_ap20(check)[1][:2] == [b'', GETP]
    assert unwrap_native_parts_v2(check) == (TOKENS, [b'', GETP, TARGET])
    # Force wrong word offset into a V2 stub; strict reverse mapping must fail.
    token, entries, name = unpack_ap20(wrap_native_ap20_v2(native_at(40000), TITLE))
    damaged = list(entries)
    damaged[1] = damaged[1][:4] + pack('>H', 40001) + damaged[1][6:]
    bad = repack_ap20(template(), token, damaged, name)
    reject(lambda: unwrap_native_parts_v2(bad), 'corrupted offset')

    # Rebuild exact historical R57 without treating the newly promoted
    # R59 LAST_GOOD as the old V1 source. All 59 native routines and
    # already validated R57 public stubs must be byte-identical.
    active = ROOT / 'dist/AMOSPro_AGA.Lib'
    last_good = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
    realistic = None
    if active.is_file() or last_good.is_file():
        assert active.is_file() and last_good.is_file(), 'incomplete current/LAST_GOOD fixture'
        current_bytes, protected_bytes = active.read_bytes(), last_good.read_bytes()
        active_hash=sha256(current_bytes).hexdigest()
        assert active_hash in (R60_SHA256,R61_SHA256,R62_SHA256,R63_SHA256,R64_SHA256,R65_SHA256,R66_SHA256,R67_SHA256,R68_SHA256,R69_SHA256,R70_SHA256,R71_SHA256,R72_SHA256,R73_SHA256,R74_SHA256,R75_SHA256,R76_SHA256,R77_SHA256,R78_SHA256,R79_SHA256,R80_SHA256,R81_SHA256,R82_SHA256,R83_SHA256,R84_SHA256,R85_SHA,R86_SHA,R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA), "Current must be an exact SHA-pinned V2 library"
        from build_m17_r59_compact_v2 import build as build_r59
        assert sha256(build_r59()[0]).hexdigest() == R59_SHA256, "Historical R59 builder changed"
        from build_m18_r60_image_region import build as build_r60
        assert sha256(build_r60()[0]).hexdigest() == R60_SHA256, "Historical R60 deterministic builder mismatch"
        assert sha256(protected_bytes).hexdigest() == LAST_GOOD_SHA256
        if active_hash in (R85_SHA,R86_SHA,R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA):
            # Post-R84 candidates are AP20 multi-unit V2, not the historical
            # single-dispatcher probe format. Independently pin the installed
            # candidate and frozen R84 before testing the unchanged R57 bridge.
            verified, frozen, _ = verify_active(ROOT)
            assert verified == current_bytes and frozen == protected_bytes
            assert current_bytes != protected_bytes
            if active_hash == P0_FREE_SHA:
                from build_m19_b8_s1_bank_free_in_memory import build_bank_free
                rebuilt,meta=build_bank_free()
                assert rebuilt==current_bytes and meta['sha256']==P0_FREE_SHA
                assert len(current_bytes)==117896
                assert meta['public_commands']==89 and meta['ap20_entries']==185
                assert meta['native_groups']==[142,153,156,177,181]
                assert meta['pc16_max']==31092
            elif active_hash == B8S1_SHA:
                from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
                rebuilt,meta=build_b8_safe_retry()
                assert rebuilt==current_bytes and meta['sha256']==B8S1_SHA
                assert len(current_bytes)==116104
                assert meta['public_commands']==88 and meta['ap20_entries']==184
                assert meta['native_groups']==[142,153,156,177,181] and meta['pc16_max']==29962
                assert meta['wait_tof_max']==3 and meta['new_native_bytes']==360
            elif active_hash == B8_SHA:
                from build_m19_b8_first_update_in_memory import build_b8_first_update
                rebuilt,meta=build_b8_first_update()
                assert rebuilt==current_bytes and meta['sha256']==B8_SHA
                assert len(current_bytes)==115744
                assert meta['public_commands']==88 and meta['ap20_entries']==184
                assert meta['native_groups']==[142,153,156,177,181] and meta['pc16_max']==29962
            elif active_hash in (B7_SHA,B7M1_SHA,B7M2_SHA):
                from build_m19_p0j_end_lifecycle_in_memory import build as build_b7, build_multiframe
                if active_hash==B7M2_SHA:
                    from build_m19_b7m2_close_reset_in_memory import build_close_reset
                    rebuilt,meta=build_close_reset()
                    assert len(rebuilt)==102400 and meta["predecessor_sha"]==B7M1_SHA
                    assert meta["close_stub"]==179 and meta["appended_bytes"]==34
                else:
                    rebuilt,meta=(build_multiframe() if active_hash==B7M1_SHA else build_b7())
                    assert len(rebuilt)==(102360 if active_hash==B7M1_SHA else 102072)
                assert current_bytes==rebuilt
                assert meta["sha256"]==active_hash and meta["public_commands"]==86
                assert meta["ap20_entries"]==181 and meta["pc16_max"]<32766
                _,groups,_=unpack_ap20(current_bytes)
                assert len(groups)==181 and meta["native_groups"]==[142,153,156,177]
            elif active_hash == AP20_ISLANDS_SHA:
                from build_m19_ap20_islands_in_memory import build as build_islands
                rebuilt,meta=build_islands()
                assert current_bytes==rebuilt and len(current_bytes)==96908
                assert meta["sha256"]==AP20_ISLANDS_SHA and meta["new_pc16"]==854
                assert meta["ap20_entries"]==178
            elif active_hash == P0D_SHA:
                from build_m19_p0d_bob_blit_in_memory import build as build_p0d
                rebuilt, meta = build_p0d()
                assert current_bytes == rebuilt and meta["sha256"] == P0D_SHA
                assert meta["commands"] == 83 and meta["entries"] == 93
                assert meta["public_signature"] == ("aga bob blit",1,88,"00,0,0")
                _, groups, _ = unpack_ap20(current_bytes)
                _, promoted, _ = unpack_ap20(protected_bytes)
                assert len(groups) == 93 and (groups[89],groups[90],groups[92]) == (
                    promoted[82], promoted[83], promoted[84]), (
                    "P0d changed protected R84 native units")
            elif active_hash == P0C_SHA:
                from build_m19_p0c_screen_close_in_memory import build as build_p0c
                # unpack_ap20 is already imported at module scope; do not
                # shadow it locally (earlier V2 static checks also call it).
                rebuilt, meta = build_p0c()
                assert current_bytes == rebuilt and meta["sha256"] == P0C_SHA
                assert meta["public_commands"] == 82 and meta["ap20_entries"] == 92
                assert (meta["bridge_group"],meta["old_aga_group"],
                        meta["screen_close_index"]) == (90,91,8)
                assert meta["program_end_hook"].startswith("PRIVATE")
                _, groups, _ = unpack_ap20(current_bytes)
                _, promoted, _ = unpack_ap20(protected_bytes)
                assert len(groups) == 92 and groups[91] == promoted[84], (
                    "P0c changed the protected AGA native unit")
        elif active_hash == R84_SHA256:
            from build_aga_r84_agapic import build as build_r84
            candidate,meta=build_r84()
            assert current_bytes==protected_bytes==candidate, "R84 active/LAST_GOOD/pinned builder differ"
            assert meta["sha256"]==R84_SHA256 and meta["bytes"]==67904
            assert meta["commands"]==76 and meta["ap20_entries"]==85
        elif active_hash == R83_SHA256:
            from build_aga_r83_modular import build as build_r83
            candidate,meta=build_r83()
            assert current_bytes==candidate and meta["sha256"]==R83_SHA256
            assert sha256(protected_bytes).hexdigest()==LAST_GOOD_SHA256
        elif active_hash == R82_SHA256:
            from build_agapic_v2_r82_full_preview import build as build_r82
            from build_c2p_r76_rpg_fix import SITES, state_offset
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate, meta = build_r82()
            assert current_bytes == candidate == protected_bytes, (
                "Promoted R82 must equal LAST_GOOD and exact native builder")
            assert meta["size"] == 64112 and meta["commands"] == 74
            assert meta["ap20_entries"] == 81 and meta["compiler_margin"] == 4562
            parts = unwrap_native_parts_v2(current_bytes)[1]
            assert len(parts) == 80 and state_offset(parts) == 12070
            assert all(parts[i][off+2:off+4] == bytes.fromhex("2f26")
                       for i,off,_ in SITES), "R82 RPG input-state LEA regression"
            assert_native_links(parts[:70]); check_cross_r74(parts[:70])
        elif active_hash == R81_SHA256:
            from build_c2p_r81_opt020 import build as build_r81
            from build_c2p_r76_rpg_fix import SITES, state_offset
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate,meta=build_r81()
            assert current_bytes==candidate, "Historical R81 must equal its SHA-pinned builder"
            assert meta["size"]==59972 and meta["commands"]==70 and meta["ap20_entries"]==77
            parts=unwrap_native_parts_v2(current_bytes)[1]
            assert len(parts)==76 and state_offset(parts)==12070
            assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        elif active_hash == R80_SHA256:
            from build_c2p_r80_iff_chunky import build as build_r80
            from build_c2p_r76_rpg_fix import SITES, state_offset
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate,meta=build_r80()
            assert current_bytes==candidate and current_bytes!=protected_bytes
            assert meta["size"]==59708 and meta["commands"]==70 and meta["ap20_entries"]==77
            parts=unwrap_native_parts_v2(current_bytes)[1]
            assert len(parts)==76 and state_offset(parts)==12070
            assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        elif active_hash == R79_SHA256:
            from build_c2p_r79_zoom import build as build_r79
            from build_c2p_r76_rpg_fix import state_offset, SITES
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate,meta=build_r79()
            assert current_bytes==candidate and current_bytes!=protected_bytes
            assert meta["size"]==57344 and meta["commands"]==69 and meta["ap20_entries"]==76
            parts=unwrap_native_parts_v2(current_bytes)[1]
            assert len(parts)==75 and state_offset(parts)==12070
            assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        elif active_hash == R78_SHA256:
            from build_c2p_r78_blit import build as build_r78
            from build_c2p_r76_rpg_fix import state_offset, SITES
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate,meta=build_r78()
            assert current_bytes==candidate and current_bytes!=protected_bytes
            assert meta["size"]==55772 and meta["commands"]==68 and meta["ap20_entries"]==75
            parts=unwrap_native_parts_v2(current_bytes)[1]
            assert len(parts)==74 and state_offset(parts)==12070
            assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        elif active_hash == R77_SHA256:
            from build_c2p_r77_close import build as build_r77
            from build_c2p_r76_rpg_fix import state_offset, SITES
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate,meta=build_r77()
            assert current_bytes==candidate and current_bytes!=protected_bytes
            assert meta["size"]==54360 and meta["commands"]==67 and meta["ap20_entries"]==74
            parts=unwrap_native_parts_v2(current_bytes)[1]
            assert len(parts)==73 and state_offset(parts)==12070
            assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        elif active_hash == R76_SHA256:
            from build_c2p_r76_rpg_fix import build as build_r76, state_offset, SITES
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate,meta=build_r76()
            assert current_bytes==candidate and current_bytes!=protected_bytes
            assert meta["size"]==54144 and meta["commands"]==66 and meta["ap20_entries"]==73
            parts=unwrap_native_parts_v2(current_bytes)[1]
            assert len(parts)==72 and state_offset(parts)==12070
            assert all(parts[i][off+2:off+4]==bytes.fromhex("2f26") for i,off,_ in SITES)
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        elif active_hash == R75_SHA256:
            from build_c2p_r75_convert import build as build_r75
            from c2p_r75_convert_emit import emit_convert
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate,meta=build_r75()
            assert current_bytes==candidate and current_bytes!=protected_bytes
            assert meta["size"]==54144 and meta["commands"]==66 and meta["ap20_entries"]==73
            parts=unwrap_native_parts_v2(current_bytes)[1]
            assert len(parts)==72 and parts[-1]==emit_convert()[0]
            assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        elif active_hash == R74_SHA256:
            from build_c2p_r74_open import build as build_r74
            from native_relative_links import assert_native_links
            from c2p_r74_relink import check_cross_r74
            candidate, meta = build_r74()
            assert current_bytes == candidate and current_bytes != protected_bytes, (
                "R74 working candidate must match the exact source and protect R73 LAST_GOOD")
            assert meta["size"] == 52612 and meta["commands"] == 65 and meta["ap20_entries"] == 72
            r74_parts = unwrap_native_parts_v2(current_bytes)[1]
            assert len(r74_parts) == 71
            assert_native_links(r74_parts[:70])
            check_cross_r74(r74_parts)
        elif active_hash == R73_SHA256:
            from build_opt020_p3_r73 import build as build_r73
            from native_relative_links import assert_native_links
            candidate, meta = build_r73()
            assert current_bytes == candidate == protected_bytes, "Promoted R73 deterministic source/LAST_GOOD mismatch"
            assert meta["size"] == 51608 and meta["commands"] == 64 and meta["ap20_entries"] == 71
            assert meta["changed_native"] == [60,66]
            assert_native_links(unwrap_native_parts_v2(current_bytes)[1])
        elif active_hash == R72_SHA256:
            from build_opt020_p2_r72 import build as build_r72
            from native_relative_links import assert_native_links
            candidate, meta = build_r72()
            assert current_bytes == candidate and current_bytes != protected_bytes, "R72 deterministic source mismatch"
            assert meta["size"] == 51468 and meta["commands"] == 64 and meta["ap20_entries"] == 71
            assert_native_links(unwrap_native_parts_v2(current_bytes)[1])
        elif active_hash == R71_SHA256:
            from build_opt020_p2_r71 import build as build_r71
            from native_relative_links import assert_native_links
            candidate, meta = build_r71()
            assert current_bytes == candidate and current_bytes != protected_bytes, "R71 deterministic source mismatch"
            assert meta["size"] == 51460 and meta["commands"] == 64 and meta["ap20_entries"] == 71
            assert_native_links(unwrap_native_parts_v2(current_bytes)[1])
        elif active_hash == R70_SHA256:
            from build_opt020_p2_r70 import build as build_r70
            candidate, meta = build_r70()
            assert current_bytes == candidate and current_bytes != protected_bytes, (
                "R70 must match exact native builder and preserve R68 LAST_GOOD")
            assert meta["size"] == 51460 and meta["commands"] == 64 and meta["ap20_entries"] == 71
        elif active_hash == R69_SHA256:
            from build_opt020_p1e_r69 import build as build_r69
            candidate, meta = build_r69()
            assert current_bytes == candidate and current_bytes != protected_bytes, (
                "R69 must match exact native builder and preserve R68 LAST_GOOD")
            assert meta["size"] == 51240 and meta["commands"] == 64 and meta["ap20_entries"] == 71
        elif active_hash == R68_SHA256:
            from build_m18_r68_cblock import build as build_r68
            candidate,meta=build_r68()
            assert current_bytes==candidate==protected_bytes, (
                "Promoted R68 must match both deterministic CBlock builder and LAST_GOOD")
            assert meta["bytes"]==51064 and meta["commands"]==64 and meta["ap20_entries"]==71, (
                "R68 V2 bridge size/commands/entry count differs")
        elif active_hash == R67_SHA256:
            from build_m18_r67_ficon_capture import build as build_r67
            assert current_bytes == build_r67()[0] and current_bytes != protected_bytes, (
                "R67 must match SHA-pinned native builder; R63 LAST_GOOD protected")
        elif active_hash == R66_SHA256:
            from build_m18_r66_fichip_dynamic import build as build_r66
            assert current_bytes == build_r66()[0] and current_bytes != protected_bytes, (
                "R66 working candidate must match exact native builder and preserve R63")
        elif active_hash == R65_SHA256:
            from build_m18_r65_ficon_bank_put import build as build_r65
            assert current_bytes == build_r65()[0] and current_bytes != protected_bytes, (
                "R65 candidate must match pinned builder and preserve R63 LAST_GOOD")
        elif active_hash == R64_SHA256:
            from build_m18_r64_ficon_bank_create import build as build_r64
            assert current_bytes == build_r64()[0] and current_bytes != protected_bytes, (
                "R64 candidate must differ from R63 LAST_GOOD")
        elif active_hash == R63_SHA256:
            from build_m18_r63_chip_blit import build as build_r63
            assert current_bytes == build_r63()[0] and current_bytes == protected_bytes, "Promoted R63 candidate/LAST_GOOD mismatch"
        elif active_hash == R62_SHA256:
            from build_m18_r62_chip_blit import build as build_r62
            assert current_bytes == build_r62()[0] and current_bytes != protected_bytes, "R62 pinned candidate mismatch"
        elif active_hash == R61_SHA256:
            from build_m18_r61_ficon import build as build_r61
            assert current_bytes == build_r61()[0] and current_bytes != protected_bytes, "R61 pinned candidate mismatch"
        else:
            assert current_bytes == protected_bytes, "R60 current mismatch"
        from build_m17_r57_rastport import build as build_r57
        source_bytes, _ = build_r57()
        assert sha256(source_bytes).hexdigest() == R57_SHA256, "R57 historical source changed"
        tokens, original = unwrap_native_parts(source_bytes)
        assert len(original) == 59 and len(tokens) > 6
        old_parts = unpack_ap20(source_bytes)[1]
        original_title = unpack_ap20(source_bytes)[2]
        native = repack_ap20(source_bytes, tokens, original, original_title)
        v2 = wrap_native_ap20_v2(native, original_title)
        vt, entries, title = unpack_ap20(v2)
        assert vt == tokens and title == original_title
        assert entries[:-1] == old_parts[:-1], 'All original public stubs must remain exact'
        assert entries[-1][34:] == old_parts[-1][32:], 'Original native code must remain exact'
        assert len(entries[-1]) == 30782, 'R57 V2 candidate must be only 2 bytes larger'
        assert unwrap_native_parts_v2(v2) == (tokens, original)
        # Real R57 layout plus a synthetic far-away helper, entirely in RAM.
        size = sum(map(len, original))
        assert size == 30748
        pad = 40000 - size
        assert pad > 0 and not pad & 1
        extended = original + [bytes.fromhex('4e71') * (pad // 2), TARGET]
        extended_native = repack_ap20(source_bytes, tokens, extended, original_title)
        extended_v2 = wrap_native_ap20_v2(extended_native, original_title)
        far_segments = unpack_ap20(extended_v2)[1]
        assert unpack_from('>H', far_segments[-2], 4)[0] == 40000
        assert len(far_segments[-1]) == 40038
        assert unwrap_native_parts_v2(extended_v2) == (tokens, extended)
        realistic = far_segments[-1]
        # No generated AP20 is written to disk.
        assert active.read_bytes() == current_bytes and sha256(current_bytes).hexdigest()==active_hash
        assert last_good.read_bytes() == protected_bytes
        assert sha256(protected_bytes).hexdigest() == LAST_GOOD_SHA256
    print('STATIC PASS: V2 AP20 offsets', offsets, 'MAX', MAX_UNIT_BYTES,
          'R57', 'REPACK PASS' if realistic is not None else 'not mounted', flush=True)
    return tests, realistic


def emulate(link: bytes, bridge: bytes, target_offset: int, *, absolute: bool, expected_d3: int = 99) -> None:
    """Run original M68000 instructions, not a Python approximation."""
    from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
    from unicorn.m68k_const import (
        UC_CPU_M68K_M68000, UC_M68K_REG_PC, UC_M68K_REG_SR,
        UC_M68K_REG_A7, UC_M68K_REG_A0, UC_M68K_REG_D0,
        UC_M68K_REG_D2, UC_M68K_REG_D3,
    )
    STUB = 0x80000
    BRIDGE = (0x100000 if absolute else STUB + 8)
    STOP = 0x10000
    STACK = 0x3F0000
    uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    uc.mem_map(0, 0x400000)
    uc.mem_write(STUB, link)
    uc.mem_write(BRIDGE, bridge)
    uc.mem_write(STOP, b'\x4e\x71')
    uc.mem_write(STACK, pack('>I', STOP))
    uc.reg_write(UC_M68K_REG_SR, 0x2000)
    uc.reg_write(UC_M68K_REG_A7, STACK)
    uc.reg_write(UC_M68K_REG_A0, 0x1F00C0)
    uc.reg_write(UC_M68K_REG_D0, 0xA5A51234)
    uc.reg_write(UC_M68K_REG_D2, 0x20313233)
    uc.reg_write(UC_M68K_REG_D3, 0)
    visits = []
    far_pc = BRIDGE + len(DISPATCH_V2) + target_offset
    def trace(_uc, address, size, _user):
        if address == far_pc:
            visits.append(address)
    uc.hook_add(UC_HOOK_CODE, trace)
    uc.emu_start(STUB, STOP, count=200)
    assert visits == [far_pc], '68000 did not reach the requested far native entry'
    assert uc.reg_read(UC_M68K_REG_PC) == STOP, '68000 failed to return normally'
    assert uc.reg_read(UC_M68K_REG_A7) == STACK + 4, 'stack imbalance'
    assert uc.reg_read(UC_M68K_REG_A0) == 0x1F00C0, 'A0 destroyed'
    assert uc.reg_read(UC_M68K_REG_D0) == 0xA5A51234, 'D0 destroyed'
    assert uc.reg_read(UC_M68K_REG_D2) == 0x20313233, 'D2 destroyed'
    assert uc.reg_read(UC_M68K_REG_D3) == expected_d3, 'target result/ABI mismatch'


def cpu_checks(tests: list[tuple[int, bytes]], realistic: bytes | None) -> None:
    try:
        from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
        from unicorn import Uc  # noqa: F401
    except ImportError as exc:
        raise SystemExit('Install capstone==5.0.9 and unicorn==2.1.4 for actual 68000 Gate A') from exc
    dis = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    code = list(dis.disasm(DISPATCH_V2, 0))
    assert sum(x.size for x in code) == 34, 'cannot decode whole M68000 bridge'
    assert any(x.mnemonic.lower().startswith('adda') for x in code)
    assert any(x.mnemonic.lower().startswith('moveq') for x in code)
    assert not any(x.mnemonic.lower() in ('illegal', 'dc.w') for x in code)
    for off, bridge in tests:
        # Compiler's Rbsr marker $FE31 becomes a BSR.W when close.
        rel = bytes.fromhex('61000006') + pack('>H', off) + b'\x4e\x75\x4e\x71'
        emulate(rel, bridge, off, absolute=False)
        # The compiler can also emit a long absolute JSR after relocation.
        abs_link = b'\x4e\xb9' + pack('>I', 0x100000) + pack('>H', off) + b'\x4e\x75'
        emulate(abs_link, bridge, off, absolute=True)
    if realistic is not None:
        off = 40000
        rel = bytes.fromhex('61000006') + pack('>H', off) + b'\x4e\x75\x4e\x71'
        emulate(rel, realistic, off, absolute=False)
        abs_link = b'\x4e\xb9' + pack('>I', 0x100000) + pack('>H', off) + b'\x4e\x75'
        emulate(abs_link, realistic, off, absolute=True)
    print('M68000 CPU PASS:', 2 * len(tests) + (2 if realistic is not None else 0),
          '68k ABI/stack/call tests, real R57 preserved, no generated files', flush=True)
    print('NO new AMOS Compiler/WinUAE Gate C claimed; CPU test only', flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-only', action='store_true', help='NO CPU Gate A; skip Unicorn')
    args = parser.parse_args()
    cases, realistic = static_checks()
    if not args.static_only:
        cpu_checks(cases, realistic)
    else:
        print('STATIC ONLY: not a real CPU nor a WinUAE result', flush=True)


if __name__ == '__main__':
    main()
