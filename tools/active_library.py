"""One current working binary in dist/ and independently frozen LAST_GOOD.

R68 v0.13.13 remains the protected promoted LAST_GOOD (A/B/C PASS).
R69 OPT020/P1e passed CPU/WinUAE and interpreted/compiled benchmarks.
R70 OPT020/P2 remains SHA-pinned in source only after WinUAE Gate B FAILED with Guru $80000004; R69 remains the active candidate.
R63 remains preserved in Git history; physical Gate D has not been tested.
R65 and R64 historical candidates passed Gates A/B interpreted and visual.
Historical R60 remains reconstructible and preserved in Git history.
No synthetic 40K padding is included.
"""
from hashlib import sha256
from pathlib import Path

C1_SHA="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
C1_ARCHIVE="dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
LAST_GOOD_SHA="ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"  # Promoted R68 v0.13.13, Gates A/B/C PASS; D physical untested
R55_SHA="97f48ccb946ced9bad0b661cbabff00440a4e5a07aeef49021b215b269fcf9ad"  # Historical R55 builder identity, no separate R55 binary
R56_SHA="df0bf2400eb9dc87e69e94f4472c05c8a7d57b496ef792a11125f7419d75ffef"  # R56 historical, compiler FAIL
R58_SHA="c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b"  # Historical user-tested R58 40K V2 probe
R59_SHA="00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d"  # Historical deterministic R59 0.13.4, former LAST_GOOD
R60_SHA="00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8"  # M18/R60 v0.13.5 AGAPIC region, promoted LAST_GOOD
R61_SHA="ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f"  # Historical R61, WinUAE A/B/C PASS
R62_SHA="9fede9f8899ff8ec3c4d978a354e30d16b7e40006c854ac96f547098d786d6f6"  # Historical R62 Gate A PASS, WinUAE interpreted RESULT 0
R63_SHA="fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba"  # Promoted R63 A/B PASS; visual pixels pending, C end M18
R64_SHA="4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c"  # R64 FICON8 Create Gates A/B interpreted + visual PASS, NOT PROMOTED; C end M18
R65_SHA="6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2"  # R65 FICON8 Bank Put Gates A/B interpreted + visual PASS; C end M18
R66_SHA="e57840e0c4f1379840e1254f1fb9ab800ce1ad712556efbd872047ea8822c7ca"  # R66 FICHIP8 Create+Stage Gates A/B interpreted+visual PASS
R67_SHA="ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5"  # R67 FICON8 Capture Gates A/B PASS
R68_SHA="ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"  # R68 Chip CBlock Gates A/B/C PASS, promoted LAST_GOOD
R69_SHA="9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"  # OPT020/P1e proven WinUAE interpreted and benchmark compiled (historical)
R70_SHA="fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"  # OPT020/P2 reproducible Image Draw CPU020 candidate, Gates B/C pending
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
    if current_sha in (R58_SHA, R59_SHA, R60_SHA, R61_SHA, R62_SHA, R63_SHA, R64_SHA, R65_SHA, R66_SHA, R67_SHA, R68_SHA, R69_SHA, R70_SHA):
        from compiler_bridge_v2_probe import is_v2_wrapped
        assert is_v2_wrapped(cur), "R58/R59/R60 must use audited V2 Compiler bridge"
    else:
        assert is_compiler_wrapped(cur), "Active library must be Compiler-safe"
    report=inspect(parse(cur))
    assert not report["issues"],report["issues"]
    if current_sha==R70_SHA:
        # Fail closed: exact SHA/structural CI cannot override a fatal WinUAE
        # illegal instruction. Keep the P2 builder in memory until fixed.
        raise AssertionError("R70 FAILED WinUAE Gate B (Guru $80000004); restore the pinned R69 working library")
    if current_sha==R69_SHA:
        from build_opt020_p1e_r69 import build as build_r69
        candidate,meta=build_r69()
        assert cur == candidate and cur != good, "R69 active differs from exact builder"
        assert sha256(good).hexdigest() == R68_SHA, "R68 LAST_GOOD protection lost"
        assert len(cur) == 51240 and meta["ap20_entries"] == 71 and meta["commands"] == 64
        return cur,good,"R69 0.13.14 OPT020/P1e tested candidate; Gate B and interpreted/compiled Region benchmarks PASS"
    if current_sha==R68_SHA:
        from build_m18_r68_cblock import build as build_r68
        candidate,meta=build_r68()
        assert candidate==cur==good and sha256(good).hexdigest()==R68_SHA
        assert len(cur)==51064 and meta["commands"]==64 and meta["ap20_entries"]==71
        return cur,good,"R68 0.13.13 Chip CBlock PROMOTED LAST_GOOD; Gates A/B/C PASS, D physical untested"
    if current_sha==R67_SHA:
        from build_m18_r67_ficon_capture import build as build_r67
        candidate,meta=build_r67()
        assert candidate==cur and cur!=good and sha256(good).hexdigest()==R63_SHA, (
            "R67 candidate differs from exact builder or R63 LAST_GOOD changed")
        return cur,good,"R67 0.13.12 FICON8 screen Capture Gate A 240 CPU PASS; WinUAE B pending, Compiler C end M18"
    if current_sha==R66_SHA:
        from build_m18_r66_fichip_dynamic import build as build_r66
        candidate,meta=build_r66()
        assert candidate==cur and cur!=good and sha256(good).hexdigest()==R63_SHA, (
            "R66 must match its deterministic builder and preserve R63 LAST_GOOD")
        return cur,good,"R66 0.13.11 Chip Cache Create+Stage Gate A 122 CPU PASS; WinUAE B pending, Compiler C end M18"
    if current_sha==R65_SHA:
        from build_m18_r65_ficon_bank_put import build as build_r65
        candidate,meta=build_r65()
        assert candidate==cur and cur!=good and sha256(good).hexdigest()==R63_SHA, (
            "R65 candidate must match pinned builder and preserve R63 LAST_GOOD")
        return cur,good,"R65 0.13.10 FICON8 Bank Put Gates A/B PASS (interpreted+visual), Compiler C end M18"
    if current_sha==R64_SHA:
        from build_m18_r64_ficon_bank_create import build as build_r64
        candidate,meta=build_r64()
        assert candidate==cur and cur!=good and sha256(good).hexdigest()==R63_SHA, (
            "R64 builder mismatch or protected R63 LAST_GOOD changed")
        return cur,good,"R64 0.13.9 FICON8 Create Gates A/B PASS (interpreted+visual), NOT PROMOTED; Compiler C end M18"
    if current_sha==R63_SHA:
        from build_m18_r63_chip_blit import build as build_r63
        candidate,meta=build_r63()
        assert candidate==cur and cur==good, "Promoted R63 must equal deterministic candidate and LAST_GOOD"
        return cur,good,"R63 0.13.8 M18 Chip masked Blitter PROMOTED LAST_GOOD; A/B PASS, visual pending, C end M18"
    if current_sha==R62_SHA:
        from build_m18_r62_chip_blit import build as build_r62
        candidate,meta=build_r62()
        assert candidate==cur and cur!=good, "R62 must match deterministic builder and preserve R60 LAST_GOOD"
        return cur,good,"R62 0.13.7 M18 masked Chip Blitter Gate A PASS; WinUAE B/C NOT TESTED"
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
