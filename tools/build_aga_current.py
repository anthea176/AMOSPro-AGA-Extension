#!/usr/bin/env python3
"""Authoritative current builder: R46 v0.12.1-C1 (AMOS Compiler Gate C PASS).

Future versions MUST derive native parts from the compiler-safe LAST_GOOD
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
                    help="verify exact current/LAST_GOOD bytes against the reproducible C1 (default)")
    args = ap.parse_args()
    data, details = build()
    current,_,active=verify_active(ROOT)
    if "IMAGE_CAPTURE_LINK_FIX_R53" in active:
        from build_m16_capture import build as capture_build
        candidate,details_candidate=capture_build()
        assert candidate==current, "Active capture is not reproducible"
        print("ACTIVE CAPTURE BUILDER PASS",{k:v for k,v in details_candidate.items() if k!="labels"})
    assert LAST_GOOD.read_bytes() == data, "LAST_GOOD not identical to promoted compiler-safe R46"
    print("CURRENT BUILDER PASS", details)
    print("Next revision source: native_from_promoted(LAST_GOOD.read_bytes(), native_title)")
    print("Next revision final: wrap_native_ap20(native_candidate, release_title)")


if __name__ == "__main__":
    main()
