"""M5 Intuition Input R6 0.5.7: restore AMOS video BEFORE the proven R5 Break.

Source-backed AMOS Professional screen restoration:
  +WEqu.s: T_EcVect = -8 (Rl SyVect,1 ; Rl EcVect,1)
  +Equ.s:   AMOS_WB = 72, EcCalD AMOS_WB,1
  +W.s:     EcIn[72] -> TAMOSWb; D1=1 restores the AMOS display.

Only append 10 bytes to the existing R5 Ctrl+C stub of entries 17/18.
The Ctrl+C BRAW already points to the original stub start; placing the
video call at that exact address leaves all original branch offsets
unchanged. Window/Screen cleanup and normal input paths are untouched.
"""
import hashlib
import json
from build_intuition_input_r5 import (
    build as build_r5, ROOT, split, u16, u32, RJSR_TEST_PASAUT,
)
from audit_ap20 import parse, inspect as audit

BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.6_INTUITION_INPUT_R5.Lib"
BASE_SHA256 = "3de03160c458f5c6990e18e450ef9d0a34ada950b59d83dd8cc2fbac271f29c5"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE_DEST = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.7_INTUITION_INPUT_R6.Lib"
REPORT = ROOT / "docs/INTUITION_INPUT_BUILD.json"

# EcCalD AMOS_WB,1: moveq #1,d1 ; movea.l T_EcVect(a5),a0 ; jsr 72*4(a0)
# 68000 encodings validated from the authoritative AMOS macros/offsets.
AMOS_TO_FRONT = bytes.fromhex("7201206dfff84ea80120")
R5_BREAK_STUB = bytes.fromhex("26054cdf5ff37400") + RJSR_TEST_PASAUT + bytes.fromhex("4e75")
assert len(AMOS_TO_FRONT) == 10 and len(R5_BREAK_STUB) == 16


def build():
    raw, previous_report = build_r5()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA256
    assert BASE.read_bytes() == raw, "R5 archive must not be rewritten"
    tokens, before, title = split(raw)
    assert len(before) == 19
    assert b"Intuition Input R5 0.5.6" in title

    after = list(before)
    for index in (17, 18):
        old = before[index]
        assert old.endswith(R5_BREAK_STUB), ("Unexpected Ctrl+C stub", index)
        # Original R5 branches jump to start of the old 16-byte stub.
        # This address remains unchanged: R6 inserts AMOS_To_Front there.
        after[index] = (old[:-len(R5_BREAK_STUB)] +
                        AMOS_TO_FRONT + R5_BREAK_STUB)
        assert len(after[index]) == len(old) + 10
        assert after[index][:-26] == old[:-16]

    for index in range(17):
        assert after[index] == before[index], ("Non-keyboard code changed", index)

    title = (title.replace(b"Intuition Input R5 0.5.6", b"Intuition Input R6 0.5.7")
                  .replace(b"AMOSPro_AGA 0.5.6", b"AMOSPro_AGA 0.5.7"))
    assert len(title) == 64
    jump_words = [len(s) // 2 for s in after]
    code = b"".join(after)
    payload = (u32(len(jump_words) * 2) + u32(len(tokens))
               + u32(len(code)) + u32(len(title))
               + b"\0\0AP20" + b"".join(u16(n) for n in jump_words)
               + tokens + code + title + bytes(2))
    payload += bytes(-len(payload) % 4)
    word_count = len(payload) // 4
    data = (raw[:20] + u32(word_count) + raw[24:28] + u32(word_count)
            + payload + raw[-4:])

    assert len(data) == 7948
    t, segments, final_title = split(data)
    assert t == tokens and final_title == title and segments == after
    assert all(segments[i] == before[i] for i in range(17))
    assert data.count(RJSR_TEST_PASAUT) == 2
    assert audit(parse(data))["issues"] == []

    report = dict(previous_report)
    report.update({
        "base": str(BASE.relative_to(ROOT)),
        "base_sha256": BASE_SHA256,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "version": "0.5.7",
        "r6_delta": {
            "modified_r5_segments": [17, 18],
            "all_other_segments_byte_identical": True,
            "amos_front_source": "+WEqu.s T_EcVect=-8; +Equ.s AMOS_WB=72",
            "amos_front_encoding": AMOS_TO_FRONT.hex(),
            "ctrl_c_sequence": "ReplyMsg -> R3 cleanup -> native AMOS_WB(1) -> restore regs -> AMOS Test_PaSaut",
            "amos_break_runtime": "R5 user-confirmed PASS, Workbench remained front",
            "amos_front_runtime": "REQUIRES WinUAE confirmation",
        },
    })
    return data, report


if __name__ == "__main__":
    data, report = build()
    assert build()[0] == data, "Build is not deterministic"
    DEST.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(data)
    ARCHIVE_DEST.write_bytes(data)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(DEST.name, len(data), report["sha256"])
