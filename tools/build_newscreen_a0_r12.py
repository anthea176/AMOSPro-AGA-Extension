#!/usr/bin/env python3
"""R12 0.6.3: reset A0 to NULL at the NTSC->PAL OpenScreenTagList retry.

R10 passed an uninitialized volatile A0 as the optional NewScreen*
on the second call, although its initial call used SUBA.L A0,A0.
Only the 68000 Open entry #6 changes. All other entries remain R10.
"""
from pathlib import Path
from struct import unpack_from, pack_into
from ap20_utils import split, rebuild, digest
from audit_ap20 import parse, inspect
from build_ntsc_pal_r10 import open_retry_stub

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib"
DEST = ARCHIVE  # R12 is frozen: never overwrite the active R13 candidate
BASE_SHA256 = "e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3"
LAST_GOOD_SHA256="09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366"
R12_SHA256 = "b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec"


def build():
    raw = BASE.read_bytes()
    assert digest(raw) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "LAST_GOOD changed (expected latest validated R38)"
    tokens, parts, title = split(raw)
    assert len(parts) == 19 and len(parts[6]) == 736
    assert title.startswith(b"AMOSPro AGA M5 NTSC-PAL R10 0.6.1")
    old = parts[6]
    assert old[0x110:0x112] == bytes.fromhex("91c8")  # Initial A0 clear
    assert old[-4:] == b"GetP"
    helper = open_retry_stub()
    assert len(helper) == 80 and old[-84:-4] == helper
    signature = bytes.fromhex("2341001c4eaefd9c")
    assert helper.count(signature) == 1
    insertion = helper.index(signature) + 4
    assert insertion == 70
    new = bytearray(helper[:insertion] + bytes.fromhex("91c8")
                    + helper[insertion:])
    assert len(new) == 82
    for offset, displacement in ((8,64), (26,46), (52,22)):
        assert helper[offset:offset+2] == bytes.fromhex("6600")
        assert unpack_from(">h", helper, offset+2)[0] == displacement
        assert offset+2+displacement >= insertion
        pack_into(">h", new, offset+2, displacement+2)
    assert new[insertion:insertion+6] == bytes.fromhex("91c84eaefd9c")
    assert new[-8:] == helper[-8:]
    updated = list(parts)
    updated[6] = old[:-84] + bytes(new) + b"GetP"
    assert len(updated[6]) == 738
    assert [i for i in range(19) if parts[i] != updated[i]] == [6]
    title_new = (b"AMOSPro AGA M5 A0 R12 0.6.3\0"
                 b"$VER: AMOSPro_AGA 0.6.3\0").ljust(len(title), b"\0")
    output = rebuild(raw, updated, title_new)
    assert len(output) == 8856 and digest(output) == R12_SHA256
    assert inspect(parse(output))["issues"] == []
    t, p, name = split(output)
    assert t == tokens and p == updated and name == title_new
    return output, {"version":"0.6.3", "size":8856,
                    "sha256":R12_SHA256, "changed_ap20":[6],
                    "historical_r10_archive_preserved":True, "winuae":"NOT_TESTED"}


if __name__ == "__main__":
    output, report = build()
    assert build()[0] == output
    ARCHIVE.write_bytes(output)
    assert ARCHIVE.read_bytes() == output
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print("R12 candidate", report)
