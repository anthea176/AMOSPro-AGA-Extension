"""Reproducible Intuition Input R4: Ctrl-only must not exit Aga Wait Key.

R3 (0.5.4) is the verified source of every AP20 code segment.
R4 modifies only entry 18, Aga Wait Key. To avoid moving any existing
68000 PC-relative branches, the C comparison is replaced with a
word-branch to a 20-byte append-only Ctrl filter stub.

Entry 17 (Aga Key) retains fully raw keycodes, including Ctrl=99.
Segments 0/6/8 (init/open/close), loader, PicInfo, and every other
segment remain byte-for-byte identical to R3.
"""
from pathlib import Path
import hashlib
import json
import struct

from build_intuition_input_r3 import build as build_r3, ROOT
from audit_ap20 import parse, inspect as audit

R3_SOURCE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.4_INTUITION_INPUT_R3.Lib"
R3_SHA = "feb012b30b1adf89b3e0609e19e9a8e475be6fcd375b355c69f0d69b2d37a884"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE_DEST = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.5_INTUITION_INPUT_R4.Lib"
REPORT = ROOT / "docs/INTUITION_INPUT_BUILD.json"
RAWKEY_CONTROL = 0x63  # 99 decimal, observed under Intuition
RAWKEY_C = 0x33

CMP_C = bytes.fromhex("0c8500000033")       # CMPI.L #$33,D5
CMP_CTRL = bytes.fromhex("0c8500000063")    # CMPI.L #$63,D5


def u16(value):
    return struct.pack(">H", value)


def u32(value):
    return struct.pack(">I", value)


def branch(opcode, source, target):
    """68000 BRA.W / BEQ.W; displacement base at opcode+2."""
    distance = target - (source + 2)
    assert -32768 <= distance <= 32767
    return struct.pack(">Hh", opcode, distance)


def split(raw):
    """Decode AP20 HUNK code segments without guessing byte offsets."""
    assert raw[:4] == u32(0x3f3)
    assert raw[24:28] == u32(0x3e9)
    assert len(raw) == 36 + struct.unpack_from(">I", raw, 28)[0] * 4
    offset = 32
    jump_bytes, token_bytes, code_bytes, title_bytes = struct.unpack_from(">4I", raw, offset)
    assert raw[offset + 16:offset + 22] == bytes.fromhex("000041503230")
    assert jump_bytes == 38
    jumps = list(struct.unpack_from(">19H", raw, offset + 22))
    token_start = offset + 22 + jump_bytes
    tokens = raw[token_start:token_start + token_bytes]
    code_start = token_start + token_bytes
    code = raw[code_start:code_start + code_bytes]
    title = raw[code_start + code_bytes:code_start + code_bytes + title_bytes]
    assert sum(jumps) * 2 == len(code)
    segments, at = [], 0
    for words in jumps:
        segments.append(code[at:at + 2 * words])
        at += 2 * words
    assert len(segments) == 19
    return tokens, segments, title


def build():
    r3_binary, r3_report = build_r3()
    assert hashlib.sha256(r3_binary).hexdigest() == R3_SHA
    assert R3_SOURCE.read_bytes() == r3_binary
    tokens, before, title = split(r3_binary)
    assert b"Intuition Input R3 0.5.4" in title
    after = list(before)

    wait = bytearray(after[18])
    cmp_offset, poll_offset = 104, 42
    assert wait.count(CMP_C) == 1
    assert wait[cmp_offset:cmp_offset + 6] == CMP_C
    assert wait[poll_offset:poll_offset + 2] == bytes.fromhex("204c")
    assert wait[cmp_offset + 6:cmp_offset + 8] == bytes.fromhex("6600")
    assert wait[-2:] == bytes.fromhex("4e75")
    stub_offset = len(wait)

    # Original CMP.L #$33,D5 is six bytes. Keep those six bytes' footprint.
    # BRA.W points to the appended stub; NOP occupies the other word.
    wait[cmp_offset:cmp_offset + 6] = (
        branch(0x6000, cmp_offset, stub_offset) + bytes.fromhex("4e71")
    )
    stub = (
        CMP_CTRL
        + branch(0x6700, stub_offset + 6, poll_offset)  # Ctrl -> poll
        + CMP_C
        + branch(0x6000, stub_offset + 16, cmp_offset + 6)  # C test -> original BNE
    )
    assert len(stub) == 20
    wait += stub
    after[18] = bytes(wait)
    assert len(after[18]) == len(before[18]) + 20
    for i in range(18):
        assert after[i] == before[i], i

    title = (title.replace(b"Intuition Input R3 0.5.4", b"Intuition Input R4 0.5.5")
                  .replace(b"AMOSPro_AGA 0.5.4", b"AMOSPro_AGA 0.5.5"))
    assert len(title) == 64
    jumps = [len(s) // 2 for s in after]
    code = b"".join(after)
    payload = (u32(len(jumps) * 2) + u32(len(tokens))
               + u32(len(code)) + u32(len(title))
               + bytes.fromhex("000041503230")
               + b"".join(u16(x) for x in jumps)
               + tokens + code + title + bytes(2))
    payload += bytes(-len(payload) % 4)
    count = len(payload) // 4
    result = (r3_binary[:20] + u32(count) + r3_binary[24:28] + u32(count)
              + payload + r3_binary[-4:])

    assert len(result) == 7896
    out_tokens, out_segments, out_title = split(result)
    assert out_tokens == tokens and out_title == title
    assert out_segments == after
    for i in range(18):
        assert out_segments[i] == before[i]
    assert not audit(parse(result))["issues"]

    report = dict(r3_report)
    report["base"] = str(R3_SOURCE.relative_to(ROOT))
    report["base_sha256"] = R3_SHA
    report["sha256"] = hashlib.sha256(result).hexdigest()
    report["size"] = len(result)
    report["version"] = "0.5.5"
    report["r4_delta"] = {
        "modified_r3_segments": [18],
        "aga_key": "Unchanged; raw Ctrl key-down still returns 99",
        "aga_wait_key": "Ignores Ctrl-only RAWKEY $63; Ctrl+C uses existing native AMOS break path",
        "existing_pc_relative_offsets": "Unchanged: branch to append-only stub",
        "r3_other_segments_identical": True,
        "runtime_validation": "REQUIRED",
    }
    return result, report


if __name__ == "__main__":
    built, report = build()
    assert build()[0] == built
    DEST.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(built)
    ARCHIVE_DEST.write_bytes(built)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(DEST.name, len(built), report["sha256"])
