"""One current working binary in dist/ and independently frozen LAST_GOOD.

R60 v0.13.5 is the user-promoted LAST_GOOD, SHA-pinned and identical to
the active library. Historical R59 remains reconstructible from its builder.
No synthetic 40K padding is included.
"""
from hashlib import sha256
from pathlib import Path

C1_SHA="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
C1_ARCHIVE="dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
LAST_GOOD_SHA="00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8"  # User-promoted R60 0.13.5, A/B/C and full regression on a8b14bc
R55_SHA="97f48ccb946ced9bad0b661cbabff00440a4e5a07aeef49021b215b269fcf9ad"  # Historical R55 builder identity, no separate R55 binary
R56_SHA="df0bf2400eb9dc87e69e94f4472c05c8a7d57b496ef792a11125f7419d75ffef"  # R56 historical, compiler FAIL
R58_SHA="c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b"  # Historical user-tested R58 40K V2 probe
R59_SHA="00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d"  # Historical deterministic R59 0.13.4, former LAST_GOOD
R60_SHA="00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8"  # M18/R60 v0.13.5 AGAPIC region, promoted LAST_GOOD
R61_SHA="ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f"  # Gate A P4 candidate; B/C pending
R57_SHA="aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0"  # Historical reproducible R57 0.13.2, formerly LAST_GOOD
CANDIDATE_HASHES={
    "dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib": "f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.8_IMAGE_CAPTURE_LINK_FIX_R53.Lib": "4cc7d78998720748e70a1498ec28375b03a4f5b98e02b3510d253f797af7ae26",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.3_R48_TOKEN_ABI_PROBE.Lib":
        "c30cfcc33ee50bb1f18c36225ccd7a5a6df7860e11201608d1801a0095687028",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.4_R49_GETADR_PROBE.Lib":
        "c18a0992ee148beb437aecc2c1c865338630b40e34bc989c72dfb26313d5657e",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.5_R50_RJSR_FNONE_PROBE.Lib":
        "984cbd5f6485c9f1133eafe356d23c290b2e457902d4f518df3776ffbb5f5eef",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.6_R51_RJSR_RELOCATION_PROBE.Lib":
        "04808ea9c89afb171a2c82f1ab61efd8bc912a0449d13cb20e942ad655ba7aea",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.7_R52_FNONE_TARGET_PROBE.Lib":
        "09ec9797fdea8f1b4694b2c8a9052776ff5cdcf7b959f2f1533c0b41151ea82e",
}
def verify_active(root: Path):
    """Return (current bytes, LAST_GOOD bytes, version label). Fail closed."""
    from audit_ap20 import parse,inspect
    from compiler_relocation import is_compiler_wrapped
    root=Path(root)
    c1=(root/C1_ARCHIVE).read_bytes()
    assert sha256(c1).hexdigest()==C1_SHA,"Archived R46 C1 changed"
    good=(root/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(good).hexdigest()==LAST_GOOD_SHA,"LAST_GOOD protected hash mismatch"
    cur=(root/"dist/AMOSPro_AGA.Lib").read_bytes()
    current_sha=sha256(cur).hexdigest()
    if current_sha in (R58_SHA, R59_SHA, R60_SHA, R61_SHA):
        from compiler_bridge_v2_probe import is_v2_wrapped
        assert is_v2_wrapped(cur), "R58/R59/R60 must use audited V2 Compiler bridge"
    else:
        assert is_compiler_wrapped(cur), "Active library must be Compiler-safe"
    report=inspect(parse(cur))
    assert not report["issues"],report["issues"]
    if current_sha==R61_SHA:
        from build_m18_r61_ficon import build as build_r61
        candidate,meta=build_r61()
        assert candidate==cur and cur!=good, "R61 must be byte-exact to builder and separate from LAST_GOOD"
        return cur,good,"R61 0.13.6 M18 Fast Icon Gate A candidate; WinUAE B/C NOT TESTED"
    if current_sha==R60_SHA:
        assert cur==good, "Promoted R60 LAST_GOOD must match active byte-for-byte"
        return cur,good,"promoted R60 v0.13.5 image region A/B/C + full regression PASS"
    if current_sha==R59_SHA:
        assert cur!=good, "Historical R59 must not replace promoted R60"
        return cur,good,"historical R59 v0.13.4 compact V2"
    if current_sha==R58_SHA:
        assert cur!=good, "R58 must not overwrite promoted R59 LAST_GOOD"
        return cur,good,"R58 0.13.3 V2 Gate A candidate"
    if current_sha==R57_SHA:
        return cur,good,"historical R57 v0.13.2 (not current LAST_GOOD)"
    if sha256(cur).hexdigest()==R56_SHA:
        assert cur!=good,"R56 must not overwrite validated R57 LAST_GOOD"
        return cur,good,"R56 v0.13.1 current Gate A candidate"
    if sha256(cur).hexdigest()==R55_SHA:
        assert cur!=good,"R55 candidate must not overwrite R57 LAST_GOOD"
        return cur,good,"R55 v0.13.0 current Gate A candidate"
    if cur==good:
        r54=(root/"dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib").read_bytes()
        assert r54==cur,"Promoted R54 differs from immutable 0.12.9 archive"
        return cur,good,"promoted R54 v0.12.9"
    for path,digest in CANDIDATE_HASHES.items():
        p=root/path
        if p.is_file() and sha256(cur).hexdigest()==digest:
            assert p.read_bytes()==cur,("Candidate differs from its immutable archive",path)
            return cur,good,path
    raise AssertionError("Unrecognized active binary; require matching versioned/pinned candidate archive")
