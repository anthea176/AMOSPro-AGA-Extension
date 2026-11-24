#!/usr/bin/env python3
"""Pinned current/LAST_GOOD/R46 compiler-safe native export regression, read-only."""
from __future__ import annotations
from hashlib import sha256

import json
from pathlib import Path
import tempfile

from active_library import C1_ARCHIVE, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, P1E_SHA, P2D_SHA, S1P1E_SHA, P2DL2_SHA, verify_active
from compiler_relocation import wrap_native_ap20
from compiler_bridge_v2_probe import is_v2_wrapped, wrap_native_ap20_v2
from build_m17_r58_compiler_bridge import build as build_r58
from build_m17_r59_compact_v2 import build as build_r59
from build_m18_r60_image_region import build as build_r60
import generate_aga_native_source as exp

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    current, last_good, label = verify_active(ROOT)
    paths = (ROOT / "dist/AMOSPro_AGA.Lib",
             ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib",
             ROOT / C1_ARCHIVE)
    original = tuple(p.read_bytes() for p in paths)
    assert original[:2] == (current, last_good)
    for path, wrapped in zip(paths, original):
        if exp.sha(wrapped) in (P2D_SHA, S1P1E_SHA, P2DL2_SHA):
            # P2d has multiple Compiler V2 native islands. The old strict
            # single-unit exporter must reject it, but the maintained
            # source builder must reproduce the official image exactly.
            from build_m19_p2d_in_memory import build_p2d
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect, parse
            candidate, meta = build_p2d()
            assert original[1] == candidate and len(candidate) == 136020
            assert meta['sha256'] == P2D_SHA
            assert meta['commands'] == 100 and meta['entries'] == 203
            _, groups, title = unpack_ap20(wrapped)
            _, reference, _ = unpack_ap20(candidate)
            if exp.sha(wrapped) == S1P1E_SHA:
                assert wrapped == current and len(wrapped) == 142000
                assert len(groups) == 208 and groups[:203] == reference
                assert b'AGSP S1-P1e' in title
            elif exp.sha(wrapped) == P2DL2_SHA:
                from active_library import verify_p2d_l2
                assert wrapped == current
                verify_p2d_l2(wrapped, candidate)
            else:
                assert wrapped == candidate and len(groups) == 203
                assert b'M19 P2d' in title
            assert not inspect(parse(wrapped))['issues']
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert 'Unsupported V2 compiler wrapper' in str(exc)
            else:
                raise AssertionError('P2d/S1 multi-unit V2 exported as false monolithic ASM')
            print('STRICT P2d/S1 SOURCE PROVENANCE / V2 MONOLITH REFUSAL PASS', exp.sha(wrapped))
            continue
        if exp.sha(wrapped)==P1E_SHA:
            # P1e is a five-native-unit V2 Lib. Rebuild exactly from source;
            # the historical single-dispatcher ASM audit must reject it.
            from build_m19_p1e_bank_edit_in_memory import build_p1e
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            candidate,meta=build_p1e()
            assert wrapped==candidate and len(candidate)==124444
            assert meta['sha256']==P1E_SHA and meta['commands']==96
            assert meta['entries']==196 and meta['pc16_max']==14130
            _,parts,title=unpack_ap20(wrapped)
            assert len(parts)==196 and not inspect(parse(wrapped))['issues']
            assert original[0]==original[1], "Promoted P1e must be byte-identical"
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert ('Rbsr entry without audited compiler dispatcher' in str(exc)
                        or 'Unsupported V2 compiler wrapper' in str(exc))
            else:
                raise AssertionError('P1e five-unit V2 AP20 exported as fake monolithic ASM')
            print('STRICT M19 P1e SOURCE BUILDER / V2 EXPORT REFUSAL PASS',P1E_SHA)
            continue
        if exp.sha(wrapped)==P0_FREE_SHA:
            from build_m19_b8_s1_bank_free_in_memory import build_bank_free
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            candidate,meta=build_bank_free()
            assert wrapped==candidate and len(candidate)==117896
            assert meta['sha256']==P0_FREE_SHA
            assert meta['public_commands']==89 and meta['ap20_entries']==185
            assert meta['native_groups']==[142,153,156,177,181] and meta['pc16_max']==31092
            _,parts,title=unpack_ap20(wrapped)
            assert len(parts)==185 and b'M19 P0 Bank Chip Select+Free' in title
            assert not inspect(parse(wrapped))['issues']
            assert sha256(original[1]).hexdigest()==P0_FREE_SHA and original[0]==original[1]
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert ('Rbsr entry without audited compiler dispatcher' in str(exc)
                        or 'Unsupported V2 compiler wrapper' in str(exc))
            else:
                raise AssertionError('P0 5-unit V2 AP20 exported as fake monolithic ASM')
            print('STRICT M19 P0 BANK FREE SOURCE BUILDER / V2 EXPORT REFUSAL PASS',P0_FREE_SHA)
            continue
        if exp.sha(wrapped)==B8S1_SHA:
            from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            candidate,meta=build_b8_safe_retry()
            assert wrapped==candidate and meta['sha256']==B8S1_SHA
            assert meta['predecessor_sha']==B8_SHA and len(candidate)==116104
            assert meta['public_commands']==88 and meta['ap20_entries']==184
            assert meta['native_groups']==[142,153,156,177,181] and meta['pc16_max']==29962
            _,parts,title=unpack_ap20(wrapped)
            assert len(parts)==184 and b'M19 B8 S1' in title
            assert not inspect(parse(wrapped))['issues']
            assert sha256(original[1]).hexdigest()==R84_SHA
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert ('Rbsr entry without audited compiler dispatcher' in str(exc)
                        or 'Unsupported V2 compiler wrapper' in str(exc))
            else:
                raise AssertionError('B8 S1 V2 islands exported as fake monolith')
            print('STRICT M19 B8 S1 SOURCE BUILDER AND OLD EXPORT REFUSAL PASS',B8S1_SHA)
            continue
        if exp.sha(wrapped)==B8_SHA:
            from build_m19_b8_first_update_in_memory import build_b8_first_update
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            candidate,meta=build_b8_first_update()
            assert wrapped==candidate and meta["sha256"]==B8_SHA
            assert meta["public_commands"]==88 and meta["ap20_entries"]==184
            assert meta["native_groups"]==[142,153,156,177,181] and meta["pc16_max"]==29962
            _,parts,title=unpack_ap20(wrapped)
            assert len(parts)==184 and b"M19 B8 candidate" in title
            assert not inspect(parse(wrapped))["issues"]
            assert sha256(original[1]).hexdigest()==R84_SHA
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert ("Rbsr entry without audited compiler dispatcher" in str(exc)
                        or "Unsupported V2 compiler wrapper" in str(exc))
            else:
                raise AssertionError("B8 V2 islands exported as fake monolith")
            print("STRICT M19 B8 BUILDER AND REFUSED MONOLITH EXPORT PASS",B8_SHA)
            continue
        if exp.sha(wrapped) in (B7_SHA,B7M1_SHA,B7M2_SHA):
            # Four relocated Compiler V2 AP20 native islands: maintain
            # strict source-provenance verification and REFUSE the old
            # monolithic exporter. Never decode RBSR stubs as 68000.
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            from build_m19_p0j_end_lifecycle_in_memory import build as build_b7, build_multiframe
            current_sha=exp.sha(wrapped)
            if current_sha==B7M2_SHA:
                from build_m19_b7m2_close_reset_in_memory import build_close_reset
                candidate,meta=build_close_reset()
                assert len(candidate)==102400 and meta["predecessor_sha"]==B7M1_SHA
                assert meta["close_stub"]==179 and meta["appended_bytes"]==34
            else:
                candidate,meta=(build_multiframe() if current_sha==B7M1_SHA else build_b7())
                assert len(candidate)==(102360 if current_sha==B7M1_SHA else 102072)
            assert wrapped==candidate and meta["sha256"]==current_sha
            assert meta["public_commands"]==86 and meta["ap20_entries"]==181
            assert meta["native_groups"]==[142,153,156,177] and meta["pc16_max"]<32766
            tokens,groups,title=unpack_ap20(wrapped)
            assert len(groups)==181
            assert (b"M19 B7-m2" in title if current_sha==B7M2_SHA
                    else b"M19 P0j-b7" in title)
            assert not inspect(parse(wrapped))["issues"]
            assert sha256(original[1]).hexdigest()==R84_SHA
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert ("Rbsr entry without audited compiler dispatcher" in str(exc)
                        or "Unsupported V2 compiler wrapper" in str(exc))
            else:
                raise AssertionError("B7 four-island wrapper exported as untrusted monolith")
            print("STRICT B7 SOURCE BUILDER AND MULTIUNIT EXPORT REFUSAL PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==AP20_ISLANDS_SHA:
            # The active AP20 islands are interleaved multi-unit V2, not an
            # accepted monolithic wrapper for historical ASM export.
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            from build_m19_ap20_islands_in_memory import build as build_islands
            from build_m19_p0d_bob_blit_in_memory import build as build_p0d
            candidate,meta=build_islands()
            predecessor,p0d_meta=build_p0d()
            assert wrapped==candidate and len(candidate)==96908
            assert meta["sha256"]==AP20_ISLANDS_SHA
            assert meta["ap20_entries"]==178 and meta["new_pc16"]==854
            assert len(predecessor)==91300 and p0d_meta["sha256"]==P0D_SHA
            assert len(unpack_ap20(wrapped)[1])==178
            assert not inspect(parse(wrapped))["issues"]
            assert sha256(original[1]).hexdigest()==R84_SHA
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert "Unsupported V2 compiler wrapper" in str(exc)
            else:
                raise AssertionError("Interleaved V2 units exported as a false monolith")
            print("STRICT AP20 ISLANDS SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==P0D_SHA:
            # P0d consists of multiple independently relocated Compiler V2
            # groups. The historical monolithic ASM exporter MUST reject it;
            # verify source-backed MC68020 builder + exact full AP20 bytes.
            from build_m19_p0d_bob_blit_in_memory import build as build_p0d
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            candidate,meta=build_p0d()
            assert wrapped==candidate and len(candidate)==91300
            assert meta["sha256"]==P0D_SHA and meta["commands"]==83
            assert meta["entries"]==93 and meta["previous_sha"]==P0C_SHA
            assert meta["public_signature"]==("aga bob blit",1,88,"00,0,0")
            _,groups,title=unpack_ap20(wrapped)
            assert len(groups)==93 and meta["group"]==91 and meta["entry"]==22688
            assert b"M19 P0d" in title
            assert not inspect(parse(wrapped))["issues"]
            assert sha256(original[1]).hexdigest()==R84_SHA
            # Preserve strict refusal of unsupported multiunit disassembly:
            # only the maintained source constructor is production authority.
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert "Unsupported V2 compiler wrapper" in str(exc)
            else:
                raise AssertionError("P0d V2 multiunit wrapper was exported as a false monolith")
            print("STRICT P0d MULTI-UNIT SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==P0C_SHA:
            # M19 P0c is a true FOUR-unit Compiler V2 layout. The strict
            # source export intentionally rejects this non-monolithic format.
            # Validate the exact maintained source builder and AP20 contracts
            # instead; never pass desassembly off as production source.
            from build_m19_p0c_screen_close_in_memory import build as build_p0c
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            candidate,meta=build_p0c()
            assert wrapped==candidate and len(candidate)==87020
            assert meta["sha256"]==P0C_SHA and meta["public_commands"]==82
            assert meta["ap20_entries"]==92 and meta["program_end_hook"].startswith("PRIVATE")
            _,groups,title=unpack_ap20(wrapped)
            assert len(groups)==92 and meta["screen_close_index"]==8
            assert (meta["bridge_group"],meta["old_aga_group"],
                    meta["old_aga_offset"])==(90,91,2008)
            assert b"Screen Close bridge EXPERIMENT UNINSTALLED" in title
            assert not inspect(parse(wrapped))["issues"]
            assert sha256(original[1]).hexdigest()==R84_SHA
            print("STRICT P0c FOUR-UNIT SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==R88_SHA:
            # R88 consists of four relocated V2 native groups; verify exact
            # deterministic provenance rather than exporting a false monolith.
            from build_m19_p28_r88_in_memory import build as build_r88
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            candidate,meta=build_r88()
            assert wrapped==candidate and meta["sha256"]==R88_SHA
            _,groups,title=unpack_ap20(wrapped)
            assert len(groups)==88 and tuple(map(len,groups[84:]))==(5558,2508,7038,56580)
            assert b"R88 v0.13.33" in title
            report=inspect(parse(wrapped))
            assert not report["issues"] and len([x for x in report["tokens"] if x["name"].startswith("aga ")])==78
            assert sha256(original[1]).hexdigest()==R84_SHA
            print("STRICT R88 FOUR-UNIT SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==R87_SHA:
            # Four independently relocated native groups. Byte-exact
            # deterministic provenance is stronger than falsely exporting
            # an unsupported single-unit ASM view.
            from build_m19_p25_no_probe import build as build_r87
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect, parse
            candidate,meta=build_r87()
            assert wrapped==candidate and meta["sha256"]==R87_SHA
            _, groups, title=unpack_ap20(wrapped)
            assert len(groups)==87 and tuple(map(len,groups[83:]))==(5558,2508,5220,56580)
            assert b"R87 v0.13.32" in title and b"CANDIDATE" in title
            report=inspect(parse(wrapped))
            assert not report["issues"]
            names=[x["name"] for x in report["tokens"]]
            assert "aga bob probe" not in names and "aga bob batch" in names
            assert sha256(original[1]).hexdigest()==R84_SHA
            print("STRICT R87 FOUR-UNIT SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==R86_SHA:
            # Four independent R86 Compiler V2 groups. The strict ASM
            # exporter still supports only the older single V2 monolith;
            # verify byte-exact provenance instead of claiming an export.
            from build_m19_p23_bob_batch import build as build_r86
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect, parse
            candidate, meta=build_r86()
            assert wrapped==candidate and meta["sha256"]==R86_SHA
            _, groups, title=unpack_ap20(wrapped)
            assert len(groups)==88 and tuple(map(len,groups[84:]))==(5558,2508,5226,56580)
            assert b"R86 v0.13.31" in title and b"CANDIDATE" in title
            assert not inspect(parse(wrapped))["issues"]
            assert sha256(original[1]).hexdigest()==R84_SHA
            print("STRICT R86 FOUR-UNIT SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==R85_SHA:
            # Four independent native groups, not a monolithic emitter.
            from build_m19_p22_fourth_unit_probe import build as build_r85
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect, parse
            candidate, meta=build_r85()
            assert wrapped==candidate and meta["sha256"]==R85_SHA
            _, groups, title=unpack_ap20(wrapped)
            assert len(groups)==87 and tuple(map(len,groups[83:]))==(5558,2508,40,56580)
            assert b"R85 v0.13.30" in title and b"TEST ONLY" in title
            assert not inspect(parse(wrapped))["issues"]
            assert sha256(original[1]).hexdigest()==R84_SHA
            print("STRICT R85 FOUR-UNIT SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==R84_SHA:
            # Three-module R84 is not a single-unit strict ASM export.
            # Deterministically reconstruct all units and verify provenance.
            from build_aga_r84_agapic import build as build_r84
            from compiler_relocation import unpack_ap20
            candidate,meta=build_r84()
            assert wrapped==candidate and meta["sha256"]==R84_SHA
            _, native_units, title=unpack_ap20(wrapped)
            assert len(native_units)==85 and tuple(map(len,native_units[82:]))==meta["units"]
            assert b"R84 v0.13.29" in title
            assert sha256(original[1]).hexdigest()==R84_SHA and wrapped==original[1]
            print("STRICT R84 THREE-UNIT SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        if exp.sha(wrapped)==R83_SHA:
            # The legacy strict ASM exporter expects ONE Compiler V2 unit.
            # Fail closed rather than pretending R83's three units are a
            # monolith. Its deterministic builder separately audits all 3.
            from build_aga_r83_modular import build as build_r83
            from compiler_relocation import unpack_ap20
            candidate, meta=build_r83()
            assert wrapped==candidate and meta["sha256"]==R83_SHA
            _, native_units, title=unpack_ap20(wrapped)
            assert [len(native_units[i]) for i in (80,81,82)]==[5558,2508,52974]
            assert b"R83 v0.13.28" in title
            print("STRICT R83 THREE-UNIT SOURCE PROVENANCE PASS",meta["sha256"])
            continue
        native, ctx = exp.source_binary_from_input(wrapped)
        assert ctx and ctx["verified_extract_and_rewrap"]
        assert ctx["official_entries"] == ctx["native_entries"] + 1
        rewrap = wrap_native_ap20_v2 if is_v2_wrapped(wrapped) else wrap_native_ap20
        assert rewrap(native, exp.parse_lib(wrapped)["title"]) == wrapped
        with tempfile.TemporaryDirectory(prefix="aga-native-source-") as tmp:
            assert exp.main(["--lib", str(path), "--out", tmp,
                             "--baseline", "auto", "--strict"]) == 0
            reports = list(Path(tmp).glob("AMOSPro_AGA_*_NATIVE.json"))
            asm = list(Path(tmp).glob("AMOSPro_AGA_*_NATIVE.s"))
            assert len(reports) == len(asm) == 1
            report = json.loads(reports[0].read_text(encoding="utf-8"))
            assert report["input_sha256"] == exp.sha(wrapped)
            assert report["compiler_wrapper"]["verified_extract_and_rewrap"]
            assert not report["unclassified_regions"]
            assert not report["native_reassembly_verified"]
            assert "NOT an installable" in asm[0].read_text(encoding="ascii")
        print("STRICT SOURCE EXPORT PASS:", path.relative_to(ROOT),
              ctx["official_entries"], "->", ctx["native_entries"],
              "entries;", ctx["provenance"])

    # Check future R58's strict source extraction directly in memory while
    # keeping only one installable .Lib and one active AMOS test in the repo.
    candidate, meta = build_r58()
    native58, ctx58 = exp.source_binary_from_input(candidate)
    assert ctx58 and ctx58["verified_extract_and_rewrap"]
    assert ctx58["official_entries"] == 62 and ctx58["native_entries"] == 61
    assert wrap_native_ap20_v2(native58, exp.parse_lib(candidate)["title"]) == candidate
    parsed58 = exp.parse_lib(native58)
    assert not exp.unclassified_gaps(parsed58), "R58 strict native source has untrusted gaps"
    print("R58 V2 STRICT NATIVE EXPORT PASS (in memory): 62 -> 61 AP20 entries")

    # R59 compact V2 must also round-trip through the SHA-pinned strict
    # exporter without inheriting any R58 synthetic padding.
    compact, meta59 = build_r59()
    native59, ctx59 = exp.source_binary_from_input(compact)
    assert ctx59 and ctx59["verified_extract_and_rewrap"]
    assert ctx59["official_entries"] == 60 and ctx59["native_entries"] == 59
    assert wrap_native_ap20_v2(native59, exp.parse_lib(compact)["title"]) == compact
    assert not exp.unclassified_gaps(exp.parse_lib(native59)), "R59 untrusted native gaps"
    assert meta59["padding_bytes"] == 0 and meta59["compiler_unit_bytes"] == 30782
    print("R59 V2 STRICT NATIVE EXPORT PASS (in memory): 60 -> 59 AP20 entries")

    # R60 SHA-pinned new native region must also round-trip strict,
    # without accepting arbitrary FE31 or FE11 markers.
    region, meta60 = build_r60()
    native60, ctx60 = exp.source_binary_from_input(region)
    assert ctx60 and ctx60["verified_extract_and_rewrap"]
    assert ctx60["official_entries"] == 61 and ctx60["native_entries"] == 60
    assert wrap_native_ap20_v2(native60, exp.parse_lib(region)["title"]) == region
    assert not exp.unclassified_gaps(exp.parse_lib(native60)), "R60 native untrusted gaps"
    assert meta60["public_commands"] == 54 and meta60["compiler_v2_bytes"] > 32768
    print("R60 V2 STRICT NATIVE EXPORT PASS (in memory): 61 -> 60 AP20 entries")

    # A valid AP20 title mutation must never pass the provenance check.
    tampered = bytearray(last_good)
    at = tampered.find(b"AMOSPro AGA")
    assert at > 0
    tampered[at] ^= 1
    changed = bytes(tampered)
    exp.parse_lib(changed)
    try:
        exp.source_binary_from_input(changed)
    except exp.ExportError as exc:
        # The promoted P0 multi-unit wrapper can fail even earlier at
        # the native-linker format guard; either rejection is fail-closed.
        assert str(exc), "Unpinned compiler-wrapped binary refused without diagnostic"
    else:
        raise AssertionError("Unpinned compiler-wrapped binary accepted")

    assert tuple(p.read_bytes() for p in paths) == original
    print("UNPINNED WRAPPER REJECTED; original Lib files unchanged")
    print("ACTIVE:", label)


if __name__ == "__main__":
    main()
