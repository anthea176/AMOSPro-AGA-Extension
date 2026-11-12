#!/usr/bin/env python3
"""Reproducible R46 bridge plus verification of current R57/R56/R55 or R54.

New versions MUST derive native parts from the compiler-safe LAST_GOOD
with compiler_relocation.native_from_promoted(), modify the native parts,
and call compiler_relocation.wrap_native_ap20() as the FINAL production step.
Never publish the raw output of historical build_m16_image_draw_r46.py.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from ap20_utils import digest
from audit_ap20 import inspect, parse
from build_aga_compiler_bridge_r46 import build as bridge_r46, SOURCE, CANDIDATE, TITLE, CANDIDATE_SHA
from compiler_relocation import unwrap_native_parts, unpack_ap20, is_compiler_wrapped, native_from_promoted
from active_library import verify_active

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "dist/AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
C1_ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
HISTORICAL_RAW = SOURCE


def build() -> tuple[bytes, dict]:
    raw = HISTORICAL_RAW.read_bytes()
    promoted = bridge_r46(raw)
    assert promoted == CANDIDATE.read_bytes(), "C1 evidence archive changed"
    assert is_compiler_wrapped(promoted), "unwrapped R46 may not be promoted"
    raw_tokens, raw_parts, raw_title = unpack_ap20(raw)
    token, segments, title = unpack_ap20(promoted)
    assert token == raw_tokens and len(raw_parts) == 56 and len(segments) == 57
    assert title == TITLE and segments[-1][32:] == b"".join(raw_parts)
    assert unwrap_native_parts(promoted) == (raw_tokens, raw_parts)
    assert native_from_promoted(promoted, raw_title) == raw
    report = inspect(parse(promoted))
    assert not report["issues"] and len([t for t in report["tokens"] if t["name"].startswith("aga ")]) == 50
    assert len(promoted) == 29964 and digest(promoted) == CANDIDATE_SHA
    return promoted, dict(version="R46 v0.12.1-C1", segments=57,
                          commands=50, bytes=len(promoted), sha256=digest(promoted),
                          gates="A/B + Gate C integrated WinUAE PASS; D NOT TESTED")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", action="store_true",
                    help="verify reproducible historical C1 and current pinned Compiler-safe release")
    args = ap.parse_args()
    data, details = build()
    current,_,active=verify_active(ROOT)
    if active.startswith("R58 0.13.3"):
        from build_m17_r58_compiler_bridge import build as build_r58
        candidate,meta=build_r58()
        assert candidate==current, "R58 candidate not byte-exact to deterministic builder"
        print("CURRENT M17 R58 V2 40K BUILDER PASS",meta)
    elif active.startswith(("R57 v0.13.2", "promoted R57 v0.13.2")):
        from build_m17_r57_rastport import build as r57_build
        candidate,meta=r57_build()
        assert candidate==current,"Current R57 differs from deterministic builder"
        print("CURRENT M17 R57 IN-PLACE RASTPORT BUILDER PASS",
              {k:v for k,v in meta.items() if k!="labels"})
    elif active.startswith("R56 v0.13.1"):
        from build_m17_r56_rastport import build as r56_build
        candidate,meta = r56_build()
        assert candidate == current, "Current R56 differs from deterministic Compiler-safe build"
        print("CURRENT M17 R56 RASTPORT BUILDER PASS",
              {k:v for k,v in meta.items() if k!="labels"})
    elif active.startswith("R55 v0.13.0"):
        from build_m17_blit_group_r55 import build as r55_build
        candidate,meta = r55_build()
        assert candidate==current, "R55 current dist library differs from deterministic builder"
        print("CURRENT M17 R55 FILL/CLEAR BUILDER PASS",
              {k:v for k,v in meta.items() if k!="helper_labels"})
    elif active=="promoted R54 v0.12.9" or "BANK_NUMBER_R54" in active:
        from build_m16_bank_api_r54 import build as bank_build
        candidate,details_candidate=bank_build()
        assert candidate==current, "R54 candidate does not match its compiler-safe builder"
        print("ACTIVE R54 BANK NUMBER BUILDER PASS",
              {k:v for k,v in details_candidate.items() if not k.endswith("_labels")})
    elif "IMAGE_CAPTURE_LINK_FIX_R53" in active:
        from build_m16_capture import build as capture_build
        candidate,details_candidate=capture_build()
        assert candidate==current, "Active capture is not reproducible"
        print("ACTIVE CAPTURE BUILDER PASS",{k:v for k,v in details_candidate.items() if k!="labels"})
    assert C1_ARCHIVE.read_bytes() == data, "Archived compiler-safe R46 C1 diverged"
    # verify_active() separately checks the pinned LAST_GOOD release.
    print("HISTORICAL R46 C1 BRIDGE PASS", details)
    print("CURRENT INSTALLABLE LIBRARY PASS:", active)
    print("Next revision source: native_from_promoted(LAST_GOOD.read_bytes(), native_title)")
    print("Next revision final: wrap_native_ap20(native_candidate, release_title)")


if __name__ == "__main__":
    main()
