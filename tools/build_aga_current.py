#!/usr/bin/env python3
"""Verify the SHA-pinned promoted R68 V2 and frozen historical R46 C1.

Future revisions MUST unwrap the V2 LAST_GOOD via
compiler_bridge_v2_probe.unwrap_native_parts_v2(), change only audited
native parts and rewrap with wrap_native_ap20_v2(). The old V1 wrapper is
historical and must not be silently applied to the current R59 image.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
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
    if active.startswith("R71 0.13.16"):
        from build_opt020_p2_r71 import R71_SHA, build as build_r71
        candidate, meta = build_r71()
        assert candidate == current and meta["sha256"] == R71_SHA
        print("CURRENT R71 OPT020/P2 link repair Gate A; WinUAE B and Compiler C pending", meta)
    elif active.startswith("R70 0.13.15"):
        from build_opt020_p2_r70 import build as build_r70
        candidate, meta = build_r70()
        assert candidate == current and meta["sha256"] == "fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"
        assert sha256(LAST_GOOD.read_bytes()).hexdigest() == "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
        print("CURRENT R70 OPT020/P2 Gate A; WinUAE B and Compiler C pending", meta)
    elif active.startswith("R69 0.13.14"):
        from build_opt020_p1e_r69 import build as build_r69
        candidate,meta=build_r69()
        assert candidate == current and meta["sha256"] == "9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"
        assert sha256(LAST_GOOD.read_bytes()).hexdigest() == "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
        print("CURRENT R69 OPT020/P1e tested: WinUAE Gate B and interpreted/compiled Region benchmark PASS; P2/R70 Gate B failed",meta)
    elif active.startswith("R68 0.13.13"):
        from build_m18_r68_cblock import build as build_r68
        candidate,meta=build_r68()
        assert candidate==current and meta["sha256"]=="ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
        assert candidate == LAST_GOOD.read_bytes(), "Promoted R68 differs from LAST_GOOD"
        print("CURRENT R68 PROMOTED LAST_GOOD; Gates A/B/C PASS, D physical untested",meta)
    elif active.startswith("R67 0.13.12"):
        from build_m18_r67_ficon_capture import build as build_r67
        candidate,meta=build_r67()
        assert candidate==current,"R67 active differs from exact native builder"
        print("CURRENT R67 FICON8 SCREEN CAPTURE Gate A 240 PASS; WinUAE interpreted B pending",meta)
    elif active.startswith("R66 0.13.11"):
        from build_m18_r66_fichip_dynamic import build as build_r66
        candidate,meta=build_r66()
        assert candidate==current,"R66 current differs from deterministic native builder"
        print("CURRENT R66 CHIP CACHE CREATE+STAGE GATE A 122 PASS; WinUAE B pending",meta)
    elif active.startswith("R65 0.13.10"):
        from build_m18_r65_ficon_bank_put import build as build_r65
        candidate,meta=build_r65()
        assert candidate==current,"R65 must match exact deterministic source builder"
        print("CURRENT R65 FICON8 BANK PUT GATE A CPU PASS, B pending, C end M18",meta)
    elif active.startswith("R64 0.13.9"):
        from build_m18_r64_ficon_bank_create import build as build_r64
        candidate,meta=build_r64()
        assert candidate==current,"R64 current differs from deterministic source"
        print("CURRENT R64 FICON8 BANK CREATE A/B PASS (interpreted+visual); Compiler C end M18",meta)
    elif active.startswith("R63 0.13.8"):
        from build_m18_r63_chip_blit import build as build_r63
        candidate,meta=build_r63()
        assert candidate==current, "R63 candidate differs from exact deterministic source"
        print("CURRENT R63 CHIP BLIT PROMOTED LAST_GOOD A/B PASS (pixels pending, C end M18)",meta)
    elif active.startswith("R62 0.13.7"):
        from build_m18_r62_chip_blit import build as build_r62
        candidate,meta=build_r62()
        assert candidate==current, "R62 does not match pinned source builder"
        print("CURRENT R62 CHIP BLIT GATE A BUILDER PASS, B/C pending",meta)
    elif active.startswith("R61 0.13.6"):
        from build_m18_r61_ficon import build as build_r61
        candidate,meta=build_r61()
        assert candidate==current, "R61 candidate differs from deterministic builder"
        print("CURRENT M18 R61 FICON V2 GATE A BUILDER PASS (B/C pending)",
              {k:v for k,v in meta.items() if k!="labels"})
    elif active.startswith(("R60 0.13.5", "promoted R60 v0.13.5")):
        from build_m18_r60_image_region import build as build_r60
        candidate,meta = build_r60()
        assert candidate==current, "R60 candidate must be byte-exact to deterministic builder"
        print("CURRENT M18 R60 AGAPIC REGION V2 GATE A BUILDER PASS",
              {k:v for k,v in meta.items() if k!="labels"})
    elif active.startswith(("R59 0.13.4", "promoted R59 v0.13.4")):
        from build_m17_r59_compact_v2 import build as build_r59
        candidate,meta=build_r59()
        assert candidate==current, "R59 candidate not byte-exact to deterministic builder"
        print("CURRENT M17 R59 COMPACT V2 BUILDER PASS",meta)
    elif active.startswith("R58 0.13.3"):
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
    print("Next revision source: unwrap_native_parts_v2(LAST_GOOD.read_bytes()) (promoted R68)")
    print("Next revision final: wrap_native_ap20_v2(native_candidate, release_title)")


if __name__ == "__main__":
    main()
