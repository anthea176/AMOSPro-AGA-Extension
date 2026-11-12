#!/usr/bin/env python3
"""HISTORICAL NATIVE R46 v0.12.1 (56 segments), NOT THE OFFICIAL COMPILER BUILD.

Reproduce the original AMOS DATA flags=0 repair for CPU/strict-source tests.
Use tools/build_aga_current.py to generate/verify the installable C1 binary.

The R45 v0.12.0 candidate failed WinUAE Gate B because it rejected the
observed valid AMOS bank native metadata FLAGS=0. R46 allows only 0,1,3
while keeping all other safety checks intact. One existing AP20 function
is repaired; no tokens, command count or historical segment is changed.
R44 LAST_GOOD and frozen failed R45 archive are NEVER rewritten.
"""
from __future__ import annotations

import argparse
import base64
from pathlib import Path

from ap20_utils import split, rebuild, digest
from audit_ap20 import parse, inspect
from m16_image_draw_r45_emit import emit_image_draw
from build_m16_image_draw_r45 import API, ENTRY_INDEX, BASE, BASE_SHA256, ARCHIVE_R44

ROOT = Path(__file__).resolve().parents[1]
R45_FAILED = ROOT / "dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib"
R45_SHA256 = "0d780b4648214c36e8f291d9575390462d174cd8ba22cac2188324b75bd220d7"
CURRENT = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE_R46 = ROOT / "dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib"
VERSION = "R46 0.12.1"


def build():
    assert digest(BASE.read_bytes()) == BASE_SHA256, "R44 LAST_GOOD changed"
    assert ARCHIVE_R44.read_bytes() == BASE.read_bytes(), "R44 archive changed"
    frozen = R45_FAILED.read_bytes()
    assert digest(frozen) == R45_SHA256 and len(frozen) == 29280, "failed R45 archive mutated"
    old_tokens, old_parts, old_title = split(frozen)
    assert len(old_parts) == 56 and len(old_parts[55]) > 512, "wrong R45 base"
    assert b"M16 Image Draw R45 0.12.0" in old_title, "not failed R45"

    updated, labels = emit_image_draw(accept_loaded_flags_zero=True)
    assert len(updated) % 2 == 0 and updated[-2:] == bytes.fromhex("4e75")
    assert updated != old_parts[55], "R46 did not repair native bank flags"
    unchanged, _ = emit_image_draw()
    assert unchanged == old_parts[55], "R45 emitter regressed"

    parts = list(old_parts)
    parts[ENTRY_INDEX] = updated
    title = b"AMOSPro AGA M16 Image Draw R46 0.12.1\0$VER: AMOSPro_AGA 0.12.1\0"
    if len(title) % 2:
        title += b"\0"
    candidate = rebuild(frozen, parts, title)
    tokens, new_parts, current_title = split(candidate)
    assert tokens == old_tokens and new_parts == parts and current_title == title
    assert new_parts[:ENTRY_INDEX] == old_parts[:ENTRY_INDEX], "inherited AP20 segment altered"

    report = inspect(parse(candidate))
    assert not report["issues"], report["issues"]
    commands = [x for x in report["tokens"] if x["name"].startswith("aga ")]
    assert len(commands) == 50 and len(new_parts) == 56
    item = [x for x in commands if x["name"] == API[0][0]]
    assert len(item) == 1
    assert (item[0]["instruction"], item[0]["function"], item[0]["signature"]) == (1,ENTRY_INDEX,API[0][2])
    assert any(x["index"] == ENTRY_INDEX and x["parameters"] == 5 and x["getp"]
               for x in report["parameter_checks"])
    if ARCHIVE_R46.exists():
        assert ARCHIVE_R46.read_bytes() == candidate, "R46 published archive mismatch"
    return candidate, dict(version=VERSION, size=len(candidate),sha256=digest(candidate),
        commands=50,segments=56,changed_segments=[ENTRY_INDEX],labels=labels,
        Gate_A="CPU_CI_PASS",Gate_B="USER_WINUAE_PASS")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    candidate,info=build()
    assert candidate == build()[0], "R46 non-deterministic build"
    print("M16/R46 HISTORICAL RAW 56-SEGMENT SOURCE (NOT INSTALLABLE IN COMPILER)",
          {key:value for key,value in info.items() if key!="labels"},flush=True)
    if args.emit_base64:
        print("R46_BASE64_BEGIN",flush=True)
        s=base64.b64encode(candidate).decode("ascii")
        for i in range(0,len(s),76):
            print(s[i:i+76],flush=True)
        print("R46_BASE64_END",flush=True)
