#!/usr/bin/env python3
"""Pinned current/LAST_GOOD/R46 compiler-safe native export regression, read-only."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from active_library import C1_ARCHIVE, verify_active
from compiler_relocation import wrap_native_ap20
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
        native, ctx = exp.source_binary_from_input(wrapped)
        assert ctx and ctx["verified_extract_and_rewrap"]
        assert ctx["official_entries"] == ctx["native_entries"] + 1
        assert wrap_native_ap20(native, exp.parse_lib(wrapped)["title"]) == wrapped
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

    # A valid AP20 title mutation must never pass the provenance check.
    tampered = bytearray(current)
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
