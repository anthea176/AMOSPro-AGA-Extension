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
    assert active_sha in (R69_SHA, R70_SHA, R71_SHA, R72_SHA, R73_SHA, R74_SHA, R75_SHA, R76_SHA, R77_SHA, R78_SHA, R79_SHA)
    candidate, metadata = build()
    assert sha256(candidate).hexdigest() == R69_SHA
    if active_sha == R79_SHA:
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
    # The benchmark is NOT placed into tests/current, preserving the
    # single ACTIVE WinUAE Gate B ASC and all tests/passed archives.
    active_asc = list((ROOT / "tests/current").glob("*.asc"))
    assert len(active_asc) == 1 and active_asc[0].name in (
        "OPT020_P1E_R69_INTERPRETED_01.asc", "OPT020_P2_R70_INTERPRETED_01.asc",
        "OPT020_P2_R71_INTERPRETED_01.asc", "OPT020_P2_R72_INTERPRETED_01.asc",
        "OPT020_P3_R73_INTERPRETED_01.asc",
        "C2P_P2_R73_BITMAP_01.asc", "C2P_R74_OPEN_01.asc", "C2P_R75_CONVERT_01.asc", "C2P_R76_CONVERT_01.asc", "C2P_R77_CLOSE_01.asc", "C2P_R78_BLIT_01.asc", "C2P_R79_ZOOM_01.asc")
    print("OPT020/P1e R60-vs-R69 BENCHMARK STATIC PASS: 10 geometries,")
    print("3 trials x 240 calls, no waits/swaps inside timing, R68==R60 Region,")
    print("only native entry 59 differs in pinned R69 baseline; R70/R71/R72 preserve it.")
    print("STATIC ONLY: no AMOS execution, WinUAE timings, or AMOS Compiler.")


if __name__ == "__main__":
    main()
