#!/usr/bin/env python3
"""OPT020/P3 in-memory AP20 probe (not an installable candidate).

R72 is the single active known-good working binary. Build a temporary AP20
V2 image in RAM with ONLY native entry 60 (F Icon Draw) and entry 66
(F Icon Capture) replaced by opt-in 68020 emitters. The rebuilt monolith
must preserve the exact R72 entry 55/59, tokens, and inter-entry branch
destinations. Never write to dist/, archives or tests/current/.

This is a STRUCTURAL preflight, not a proof of 68020 CPU functionality.
"""
from hashlib import sha256
from pathlib import Path
from audit_ap20 import parse,inspect
from build_opt020_p2_r72 import build as build_r72
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from m18_ficon_ap20_emit import emit_ficon_ap20
from m18_ficon_capture_emit import emit_ficon_capture
from native_relative_links import assert_native_links,relink_native_parts,LINKS,link_positions

ROOT=Path(__file__).resolve().parents[1]
ACTIVE_SHA="fdb98db259618fbdc3802843e2d6e836cb64acf2d68dc50bbe1133d46d36e67b"
GOOD_SHA="ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
R73_SHA="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
DRAW=60
CAPTURE=66

def build():
    active=(ROOT/"dist/AMOSPro_AGA.Lib").read_bytes()
    last_good=(ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    active_sha=sha256(active).hexdigest()
    assert active_sha in (ACTIVE_SHA,R73_SHA),"Unrecognized P3 active library"
    assert sha256(last_good).hexdigest()==GOOD_SHA,"LAST_GOOD modified"
    source,_=build_r72()
    if active_sha==ACTIVE_SHA:
        assert source==active,"R72 builder differs from installed binary"
    else:
        from build_opt020_p3_r73 import build as build_r73
        assert active==build_r73()[0],"R73 builder differs from active binary"
    tokens,original=unwrap_native_parts_v2(source)
    assert len(original)==70 and original[59].endswith(GETP)
    assert original[DRAW]==emit_ficon_ap20()[0]+GETP
    assert original[CAPTURE]==emit_ficon_capture()[0]+GETP
    assert_native_links(original)
    modified=list(original)
    draw,draw_labels=emit_ficon_ap20(opt020=True)
    capture,capture_labels=emit_ficon_capture(opt020=True)
    assert "p3_fallback" in draw_labels or "core" in draw_labels
    assert "check_plane" in capture_labels and "pixel" not in capture_labels
    modified[DRAW]=draw+GETP
    modified[CAPTURE]=capture+GETP
    # Mandatory even if the known historical R70 links do not move.
    modified=relink_native_parts(modified)
    assert_native_links(modified)
    changed={i for i,(a,b) in enumerate(zip(original,modified)) if a!=b}
    assert changed=={DRAW,CAPTURE},f"Unexpected native entry changes {changed}"
    assert original[55]==modified[55] and original[59]==modified[59]
    for link in LINKS:
        after_target, expected, _=link_positions(modified,link)
        assert after_target==expected,link.name
    _t,_e,old_title=unpack_ap20(source)
    title=(b"AMOSPro AGA OPT020 P3 FIcon CAP+DRAW CPU020 IN-MEMORY PROBE\0"
           b"$VER: AMOSPro_AGA 0.13.17\0")
    title+=bytes(len(title)&1)
    native=repack_ap20(source,tokens,modified,title)
    probe=wrap_native_ap20_v2(native,title)
    assert unwrap_native_parts_v2(probe)==(tokens,modified)
    t,sections,got_title=unpack_ap20(probe)
    assert t==tokens and got_title==title and len(sections)==71
    report=inspect(parse(probe))
    assert not report["issues"],report["issues"]
    assert len(sections[-1])<65534
    assert sha256((ROOT/"dist/AMOSPro_AGA.Lib").read_bytes()).hexdigest()==active_sha
    assert sha256((ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()).hexdigest()==GOOD_SHA
    return probe,dict(
        status="STRUCTURAL PROBE ONLY; 68020 CPU/WinUAE NOT YET TESTED",
        bytes=len(probe),sha256=sha256(probe).hexdigest(),
        changed_native_indices=sorted(changed),
        draw_native_bytes=len(draw),capture_native_bytes=len(capture),
        draw_core_label=draw_labels["core"],capture_row_label=capture_labels["row"]
    )

if __name__=="__main__":
    probe,meta=build()
    assert build()[0]==probe,"Non-deterministic P3 probe"
    print("OPT020/P3 IN-MEMORY AP20 V2 STRUCTURAL PASS",meta)
    print("No new Lib or ASC written. No CPU / WinUAE Gate A/B claim.")
