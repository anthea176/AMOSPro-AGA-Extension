"""Build Intuition Input R5 (0.5.6) from the archived, immutable R4 binary.

R5 only changes the Ctrl+C branch in the two public keyboard entries:
  * BITCONTROL | BITVBL in the native AMOS T_Actualise word;
  * jump to a self-contained, append-only return path that restores the
    input routine's public registers, then uses official AP20 Rjsr
    L_Test_PaSaut (main AMOS Professional library entry #140).

The AMOS loader/compiler resolves Rjsr markers during library linking.
Do not execute the raw marker as a CPU instruction. The mock CPU tests
substitute the documented linked JSR before running.

In particular R5 leaves R3's confirmed CloseWindow/CloseScreen fix, the
R4 Ctrl-only filter, Generic ILBM R2, PicInfo, and every other segment
byte-for-byte identical.
"""
from pathlib import Path
import hashlib
import json

from audit_ap20 import parse, inspect as audit
from build_intuition_input_r4 import (
    build as build_r4, split, u16, u32, branch, ROOT,
)

BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.5_INTUITION_INPUT_R4.Lib"
BASE_SHA = "fbcaec00f30e6a7c03abc692225dac1f95dbbdb537353674fa6939c1087de9f2"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE_DEST = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.6_INTUITION_INPUT_R5.Lib"
REPORT = ROOT / "docs/INTUITION_INPUT_BUILD.json"

# Verified in AOZ-Studio/AMOS-Professional-Official:
# +CEqu.s Rjsr: FE 11 F7 00 index.w ; +lequ.s L_Test_PaSaut=140.
# +ILib.s: Test_PaSaut -> Test_Normal -> Test_Force (if BitVBL set).
RJSR_TEST_PASAUT = bytes.fromhex("fe11f700008c")
CTRL_OR = bytes.fromhex("006d0100ff58")  # ORI.W #$0100,T_Actualise(a5)
CTRL_OR_FORCED = bytes.fromhex("006d8100ff58")  # BitVBL | BitControl
RESTORE = bytes.fromhex("4cdf5ff3")
D2_INT = bytes.fromhex("7400")
RTS = bytes.fromhex("4e75")
MOVE_D5_D3 = bytes.fromhex("2605")


def build():
    raw, report_r4 = build_r4()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA
    assert BASE.read_bytes() == raw
    tokens, old, title = split(raw)
    assert len(old) == 19
    assert b"Intuition Input R4 0.5.5" in title
    result = list(old)

    # Both Aka Key (17) and Aka Wait Key (18) must allow Ctrl+C to
    # interrupt, independent of whether the caller polls or waits.
    for entry in (17, 18):
        body = bytearray(old[entry])
        assert body.count(CTRL_OR) == 1, entry
        pos = body.index(CTRL_OR)
        assert pos == 130, (entry, pos)
        branch_pos = pos + 6
        assert body[branch_pos:branch_pos + 2] == bytes.fromhex("6000")
        assert RESTORE + D2_INT + RTS in body
        target = len(body)

        body[pos:pos + 6] = CTRL_OR_FORCED
        body[branch_pos:branch_pos + 4] = branch(0x6000, branch_pos, target)
        stub = MOVE_D5_D3 + RESTORE + D2_INT + RJSR_TEST_PASAUT + RTS
        assert len(stub) == 16
        body += stub

        # Every prior instruction/relative offset except this Ctrl path
        # remains unchanged, including the Ctrl-only filter in entry 18.
        assert body[:pos] == old[entry][:pos]
        assert body[branch_pos + 4:len(old[entry])] == old[entry][branch_pos + 4:]
        assert body.endswith(stub)
        result[entry] = bytes(body)

    for entry in range(17):
        assert result[entry] == old[entry], ("Unexpected segment delta", entry)

    title = (title.replace(b"Intuition Input R4 0.5.5", b"Intuition Input R5 0.5.6")
                  .replace(b"AMOSPro_AGA 0.5.5", b"AMOSPro_AGA 0.5.6"))
    assert len(title) == 64
    jumps = [len(s) // 2 for s in result]
    code = b"".join(result)
    payload = (u32(len(jumps) * 2) + u32(len(tokens))
               + u32(len(code)) + u32(len(title))
               + b"\0\0AP20"
               + b"".join(u16(n) for n in jumps)
               + tokens + code + title + bytes(2))
    payload += bytes(-len(payload) % 4)
    count = len(payload) // 4
    candidate = (raw[:20] + u32(count) + raw[24:28] + u32(count)
                 + payload + raw[-4:])

    assert len(candidate) == 7928
    assert candidate[-4:] == u32(0x3F2)
    new_tokens, new_segments, new_title = split(candidate)
    assert new_tokens == tokens and new_title == title
    assert new_segments == result
    assert candidate.count(RJSR_TEST_PASAUT) == 2
    assert audit(parse(candidate))["issues"] == []

    report = dict(report_r4)
    report.update({
        "base": str(BASE.relative_to(ROOT)),
        "base_sha256": BASE_SHA,
        "sha256": hashlib.sha256(candidate).hexdigest(),
        "size": len(candidate),
        "version": "0.5.6",
        "r5_delta": {
            "modified_r4_segments": [17, 18],
            "remaining_segments_identical": True,
            "control_break_flags": "BitControl ($0100) | BitVBL ($8000)",
            "amos_native_dispatch": "AP20 Rjsr L_Test_PaSaut (entry 140)",
            "amos_break_on_off": "Delegated to native AMOS Test_Force",
            "ctrl_qualifier": "IEQUALIFIER_CONTROL on RAWKEY C",
            "runtime_validation": "REQUIRED: interpreter and compiled",
        },
    })
    return candidate, report


if __name__ == "__main__":
    data, report = build()
    assert build()[0] == data
    DEST.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(data)
    ARCHIVE_DEST.write_bytes(data)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(DEST.name, len(data), report["sha256"])
