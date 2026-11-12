#!/usr/bin/env python3
"""M16/R45 (0.12.0) EXPERIMENTAL candidate builder; R44 LAST_GOOD frozen.

Consumes exact R44 0.11.5 LAST_GOOD as read-only base. Appends one AP20
function and one 68000 segment. Never modifies R44 archives or binaries.
Gate A (native CPU/CI) and Gate B (AMOS/WinUAE) must pass separately.
"""
from __future__ import annotations

import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import digest, split
from audit_ap20 import parse, inspect, token
from m16_image_draw_r45_emit import emit_image_draw, ENTRY_INDEX, GETP

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc"
CURRENT = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE_R44 = ROOT / "dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"
VERSION = "R45 0.12.0"
API = (("aga image draw", ENTRY_INDEX, "00,0,0,0,0"),)


def build():
    original = BASE.read_bytes()
    assert digest(original) == BASE_SHA256, "R44 LAST_GOOD unexpectedly changed"
    assert CURRENT.read_bytes() == original, "R44 current binary changed"
    assert ARCHIVE_R44.read_bytes() == original, "R44 historical archive changed"
    tok, parts, _ = split(original)
    assert len(parts) == ENTRY_INDEX == 55, "R44 segment count changed"
    audited = inspect(parse(original))
    assert not audited["issues"], audited["issues"]
    named = [x for x in audited["tokens"] if x["name"].startswith("aga ")]
    assert len(named) == 49, "R44 named API changed"

    raw, labels = emit_image_draw()
    assert len(raw) % 2 == 0 and raw[-2:] == bytes.fromhex("4e75")
    new_parts = list(parts)
    new_parts[-1] = parts[-1] + GETP
    new_parts.append(raw)
    new_tokens = tok[:-6] + token(API[0][0], 1, ENTRY_INDEX, API[0][2]) + bytes(6)
    title = b"AMOSPro AGA M16 Image Draw R45 0.12.0\0$VER: AMOSPro_AGA 0.12.0\0"
    if len(title) % 2:
        title += b"\0"
    code = b"".join(new_parts)
    body = (pack(">4I", len(new_parts)*2, len(new_tokens), len(code), len(title))
            + b"\0\0AP20" + b"".join(pack(">H", len(p)//2) for p in new_parts)
            + new_tokens + code + title + b"\0\0")
    body += bytes(-len(body) % 4)
    words = pack(">I", len(body)//4)
    candidate = original[:20] + words + original[24:28] + words + body + original[-4:]
    assert split(candidate)[:2] == (new_tokens, new_parts)
    report = inspect(parse(candidate))
    assert not report["issues"], report["issues"]
    api = [x for x in report["tokens"] if x["name"].startswith("aga ")]
    assert len(api) == 50
    got = [x for x in api if x["name"] == API[0][0]]
    assert len(got) == 1
    assert (got[0]["instruction"], got[0]["function"],
            got[0]["signature"]) == (1,ENTRY_INDEX,API[0][2])
    assert any(x["index"] == ENTRY_INDEX and x["parameters"] == 5 and x["getp"]
               for x in report["parameter_checks"]), "AP20 GetP chain broken"
    assert new_parts[:54] == parts[:54], "historical R44 entries modified"
    assert new_parts[54] == parts[54] + GETP
    assert new_parts[55] == raw
    return candidate, dict(version=VERSION, size=len(candidate),
        sha256=digest(candidate), commands=50, segments=56,
        changed_segments=[54,55], labels=labels,
        Gate_A="CPU_CI_PASS",Gate_B="NOT_TESTED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    raw, info = build()
    assert raw == build()[0], "non deterministic R45"
    print("M16/R45 in-memory candidate", {k:v for k,v in info.items() if k!="labels"},flush=True)
    if args.emit_base64:
        print("R45_BASE64_BEGIN",flush=True)
        encoded = base64.b64encode(raw).decode("ascii")
        for i in range(0,len(encoded),76):
            print(encoded[i:i+76],flush=True)
        print("R45_BASE64_END",flush=True)
