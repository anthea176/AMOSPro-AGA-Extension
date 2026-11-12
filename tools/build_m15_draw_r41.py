#!/usr/bin/env python3
"""M15/R41 v0.11.2: deterministic Aga Draw candidate from immutable R40.

The R40 LAST_GOOD and its archive are left untouched. R41 is NOT promoted
until explicit user-confirmed interpreted AMOS/WinUAE Gate B.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m15_draw_r41_emit import emit_draw, ENTRY_INDEX

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib"
BASE_SHA256 = "0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256 = BASE_SHA256
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib"
GETP = b"GetP"
API = (("aga draw", ENTRY_INDEX, "00,0,0,0,0"),)
VERSION = "R41 0.11.2"


def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, "R40 immutable archive changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "R40 LAST_GOOD changed"
    old_tokens, old_segments, _ = split(frozen)
    assert len(old_segments) == ENTRY_INDEX == 51
    assert not old_segments[-1].endswith(GETP)
    assert old_segments[-1].endswith(bytes.fromhex("4cdf77f774004e75"))
    audit40 = inspect(parse(frozen))
    assert not audit40["issues"], audit40["issues"]
    assert len([t for t in audit40["tokens"] if t["name"].startswith("aga ")]) == 45
    code, labels = emit_draw()
    assert code.endswith(bytes.fromhex("4fef00a04cdf77f774004e75"))

    parts = list(old_segments)
    parts[-1] = old_segments[-1] + GETP
    parts.append(code)
    assert parts[:-2] == old_segments[:-1], "earlier R40 AP20 segments changed"
    assert parts[-2] == old_segments[-1] + GETP

    new_tokens = old_tokens[:-6] + token(API[0][0], 1, ENTRY_INDEX, API[0][2]) + bytes(6)
    title = b"AMOSPro AGA M15 Draw R41 0.11.2\0$VER: AMOSPro_AGA 0.11.2\0"
    if len(title) & 1:
        title += b"\0"
    code_bytes = b"".join(parts)
    payload = (pack(">4I", len(parts)*2, len(new_tokens), len(code_bytes), len(title))
               + b"\0\0AP20"
               + b"".join(pack(">H", len(p)//2) for p in parts)
               + new_tokens + code_bytes + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    words = pack(">I", len(payload)//4)
    candidate = frozen[:20] + words + frozen[24:28] + words + payload + frozen[-4:]

    assert split(candidate)[:2] == (new_tokens, parts)
    audit = inspect(parse(candidate))
    assert not audit["issues"], audit["issues"]
    named = [t for t in audit["tokens"] if t["name"].startswith("aga ")]
    assert len(named) == 46
    got = [t for t in named if t["name"] == API[0][0]]
    assert len(got) == 1
    assert (got[0]["instruction"], got[0]["function"], got[0]["signature"]) == (1, ENTRY_INDEX, API[0][2])
    assert any(c["index"] == ENTRY_INDEX and c["parameters"] == 5 and c["getp"]
               for c in audit["parameter_checks"])
    return candidate, dict(version=VERSION, sha256=digest(candidate),
        size=len(candidate), named_commands=46, segments=52,
        new_command=API[0], changed_segments=[50, 51],
        labels=labels, Gate_A="CPU_CI_PENDING", Gate_B="NOT_TESTED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    candidate, info = build()
    assert candidate == build()[0], "R41 build is not deterministic"
    print("R41 in-memory candidate:", {k:v for k,v in info.items() if k != "labels"}, flush=True)
    if args.emit_base64:
        print("R41_BASE64_BEGIN", flush=True)
        b64 = base64.b64encode(candidate).decode("ascii")
        for pos in range(0, len(b64), 76):
            print(b64[pos:pos+76], flush=True)
        print("R41_BASE64_END", flush=True)
