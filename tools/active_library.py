"""Active installable candidate (dist root) vs independently frozen LAST_GOOD.

Only versioned, pinned artifacts are permitted in the active distribution.
A candidate may be current WITHOUT being promoted; the prior official last
good is never overwritten by Gate A / CPU diagnostics.
"""
from hashlib import sha256
from pathlib import Path

LAST_GOOD_SHA="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
CANDIDATE_HASHES={
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
    good=(root/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(good).hexdigest()==LAST_GOOD_SHA,"LAST_GOOD R46 C1 changed"
    cur=(root/"dist/AMOSPro_AGA.Lib").read_bytes()
    assert is_compiler_wrapped(cur),"Active library must be Compiler-safe"
    report=inspect(parse(cur))
    assert not report["issues"],report["issues"]
    if cur==good:
        return cur,good,"promoted R46 C1"
    for path,digest in CANDIDATE_HASHES.items():
        p=root/path
        if p.is_file() and sha256(cur).hexdigest()==digest:
            assert p.read_bytes()==cur,("Candidate differs from its immutable archive",path)
            return cur,good,path
    raise AssertionError("Unrecognized active binary; require matching versioned/pinned candidate archive")
