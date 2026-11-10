#!/usr/bin/env python3
"""R7 / 0.5.8: fix ScreenBuffer -> DBufInfo pointer reads in Aga Double Buffer.

The R6 allocator emitted "MOVEA.L $4A80(A0),A0" twice by accidentally
omitting both the +4 displacement and the TST.L D0 instruction word.
This reads far past a ScreenBuffer, then may write reply ports into a
bogus address before the first ChangeScreenBuffer.

This builder reassembles only AP20 entry 10 from the validated R6B-R1
labelled source, with BOTH pointer reads fixed. Branch displacements
are recalculated by the assembler, not patched by hand.

R6 archive, R6 working keyboard, screen Close, Generic ILBM R2,
PicInfo and ALL other AP20 entries are byte-for-byte unchanged.
IMPORTANT: R7 does NOT solve in-flight Swap Safe/Disp teardown.
"""
from pathlib import Path
import hashlib
import json

from audit_ap20 import parse, inspect as audit
from build_intuition_input_r6 import build as build_r6, ROOT
from build_intuition_input_r4 import split, u16, u32
from build_m4b_r6b_r1 import A, double_buffer as old_double_buffer

BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.7_INTUITION_INPUT_R6.Lib"
BASE_SHA = "729fc13efbaa710a371048353368ffe3dd5af0a23d0043d1e6ee3bcf2e5330d9"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE_DEST = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.8_DB_POINTER_R7.Lib"
REPORT = ROOT / "docs/DB_POINTER_R7_BUILD.json"

BAD0 = bytes.fromhex("205420684a80")
BAD1 = bytes.fromhex("206c000420684a80")
GOOD0 = bytes.fromhex("20542068000420084a80")
GOOD1 = bytes.fromhex("206c00042068000420084a80")


def double_buffer_fixed():
    """Identical to the R6B-R1 allocator except two DBufInfo dereferences."""
    a = A()
    a.e("48e7effe7600246d01c84a92"); a.br(0x6700, "done")
    a.e("286a0020200c4a80"); a.br(0x6600, "already")
    a.e("7018223c000100012c7800044eaefd544a80"); a.br(0x6700, "done")
    a.e("2840")
    a.e("2c7800044eaefd664a80"); a.br(0x6700, "fail_vec")
    a.e("2940000c")
    a.e("2c7800044eaefd664a80"); a.br(0x6700, "fail_ports")
    a.e("29400010")
    a.e("205293c970012c6a00044eaefd004a80"); a.br(0x6700, "fail_ports")
    a.e("2880")
    a.e("205293c970022c6a00044eaefd004a80"); a.br(0x6700, "fail_sb0")
    a.e("29400004")

    # ORIGINAL (BROKEN): 2054 2068 4a80
    #   movea.l (a4),a0
    #   movea.l $4A80(a0),a0   <-- OOB read; 4a80 was meant as TST.L D0
    # CORRECT: load ScreenBuffer.sb_DBufInfo at +4, then test that pointer.
    a.e(GOOD0.hex()); a.br(0x6700, "fail_both")
    a.e("202c000c21400016202c001021400036")

    # Repeat for SB1. SafeMessage.mn_ReplyPort is DBufInfo+22,
    # DispMessage.mn_ReplyPort is DBufInfo+54.
    a.e(GOOD1.hex()); a.br(0x6700, "fail_both")
    a.e("202c000c21400016202c001021400036")
    a.e("254c0020")
    a.label("already"); a.e("7601"); a.br(0x6000, "done")

    a.label("fail_both")
    a.e("2052226c00042c6a00044eaefcfa")
    a.label("fail_sb0")
    a.e("205222542c6a00044eaefcfa")
    a.label("fail_ports")
    a.e("2c780004206c001020084a80"); a.br(0x6700, "skip_disp")
    a.e("4eaefd60")
    a.label("skip_disp")
    a.e("206c000c20084a80"); a.br(0x6700, "fail_vec")
    a.e("4eaefd60")
    a.label("fail_vec")
    a.e("224c2c7800044eaefd4e")
    a.label("done"); a.e("4cdf7ff774004e75")

    code = a.out()
    assert len(code) == len(old_double_buffer()) + 8
    assert code.count(GOOD0) == code.count(GOOD1) == 1
    assert BAD0 not in code and BAD1 not in code
    # All local branches were resolved by A.out from their symbolic labels.
    assert len(a.fix) >= 12
    for extension, label in a.fix:
        displacement = int.from_bytes(code[extension:extension+2], "big", signed=True)
        assert extension + displacement == a.labels[label], (extension, label)
    return code


def build():
    raw, _ = build_r6()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA
    assert BASE.read_bytes() == raw, "R6 immutable archive changed"
    tokens, previous, title = split(raw)
    assert len(previous) == 19
    assert b"Intuition Input R6 0.5.7" in title
    assert previous[10] == old_double_buffer() + b"GetP", "R6 allocator changed unexpectedly"
    assert previous[10].count(BAD0) == previous[10].count(BAD1) == 1

    updated = list(previous)
    updated[10] = double_buffer_fixed() + b"GetP"
    assert len(updated[10]) == len(previous[10]) + 8
    assert all(updated[i] == previous[i] for i in range(19) if i != 10)

    title = (title.replace(b"Intuition Input R6 0.5.7", b"Intuition Input R7 0.5.8")
                  .replace(b"AMOSPro_AGA 0.5.7", b"AMOSPro_AGA 0.5.8"))
    assert len(title) == 64
    jumps = [len(s) // 2 for s in updated]
    code = b"".join(updated)
    payload = (u32(len(jumps)*2) + u32(len(tokens)) + u32(len(code))
               + u32(len(title)) + bytes.fromhex("000041503230")
               + b"".join(u16(w) for w in jumps)
               + tokens + code + title + bytes(2))
    payload += bytes(-len(payload) % 4)
    words = len(payload) // 4
    result = (raw[:20] + u32(words) + raw[24:28] + u32(words)
              + payload + raw[-4:])

    assert len(result) == 7956
    check_tokens, check_segments, check_title = split(result)
    assert check_tokens == tokens and check_title == title
    assert check_segments == updated
    assert audit(parse(result))["issues"] == []

    report = {
        "version": "0.5.8",
        "source": str(BASE.relative_to(ROOT)),
        "source_sha256": BASE_SHA,
        "size": len(result),
        "sha256": hashlib.sha256(result).hexdigest(),
        "modified_ap20_segments": [10],
        "byte_identical_except_db": list(range(0,10)) + list(range(11,19)),
        "bad_pointer_encoded": "2068 4a80 (MOVEA.L $4A80(A0),A0)",
        "corrected_pointer_encoded": "2068 0004 2008 4a80 (MOVEA.L 4(A0),A0; MOVE.L A0,D0; TST.L D0)",
        "screenbuffer_struct_offset": 4,
        "safe_replyport_offset_from_dbufinfo": 22,
        "disp_replyport_offset_from_dbufinfo": 54,
        "generic_ilbm_r2_unchanged": True,
        "picinfo_unchanged": True,
        "ctrl_c_and_close_unchanged": True,
        "warning": "R7 does NOT fix pending Safe/Disp notifications after Aga Swap. Do not run Swap/Close tests until a separate fix.",
        "runtime": "NOT VALIDATED",
    }
    return result, report


if __name__ == "__main__":
    raw, report = build()
    assert build()[0] == raw, "Non-deterministic builder"
    DEST.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(raw)
    ARCHIVE_DEST.write_bytes(raw)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(DEST.name, len(raw), report["sha256"])
