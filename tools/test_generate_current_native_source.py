#!/usr/bin/env python3
"""Pinned current/LAST_GOOD/R46 compiler-safe native export regression, read-only."""
from __future__ import annotations
from hashlib import sha256

import json
from pathlib import Path
import tempfile

from active_library import C1_ARCHIVE, R83_SHA, R84_SHA, verify_active
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
            assert sha256(original[1]).hexdigest()==R83_SHA
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
