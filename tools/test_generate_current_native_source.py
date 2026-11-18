#!/usr/bin/env python3
"""Pinned current/LAST_GOOD/R46 compiler-safe native export regression, read-only."""
from __future__ import annotations
from hashlib import sha256

import json
from pathlib import Path
import tempfile

from active_library import C1_ARCHIVE, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, verify_active
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
        if exp.sha(wrapped) in (B7_SHA,B7M1_SHA):
            # The B7 candidate is a four-island Compiler V2 AP20 image.
            # Verify its SOURCE builder and reject the historical monolith
            # native exporter; treating AP20 RBSR stubs as opcodes is unsafe.
            from compiler_relocation import unpack_ap20
            from audit_ap20 import inspect,parse
            from build_m19_p0j_end_lifecycle_in_memory import build as build_b7, build_multiframe
            current_sha=exp.sha(wrapped)
            candidate,meta=(build_multiframe() if current_sha==B7M1_SHA else build_b7())
            assert wrapped==candidate and len(candidate)==(102360 if current_sha==B7M1_SHA else 102072)
            assert meta["sha256"]==current_sha and meta["public_commands"]==86
            assert meta["ap20_entries"]==181 and meta["native_groups"]==[142,153,156,177]
            assert meta["pc16_max"]<32766
            tokens,groups,title=unpack_ap20(wrapped)
            assert len(groups)==181 and b"M19 P0j-b7" in title
            assert not inspect(parse(wrapped))["issues"]
            assert sha256(original[1]).hexdigest()==R84_SHA
            try:
                exp.source_binary_from_input(wrapped)
            except exp.ExportError as exc:
                assert ("Rbsr entry without audited compiler dispatcher" in str(exc)
                        or "Unsupported V2 compiler wrapper" in str(exc))
            else:
                raise AssertionError("B7 four-island wrapper exported as untrusted monolith")
            print("STRICT P0j-b7 SOURCE BUILDER AND MULTIUNIT EXPORT REFUSAL PASS",meta["sha256"])
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
        assert "source audit required" in str(exc)
    else:
        raise AssertionError("Unpinned compiler-wrapped binary accepted")

    assert tuple(p.read_bytes() for p in paths) == original
    print("UNPINNED WRAPPER REJECTED; original Lib files unchanged")
    print("ACTIVE:", label)


if __name__ == "__main__":
    main()
