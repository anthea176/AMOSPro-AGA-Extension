#!/usr/bin/env python3
"""M15/R42 v0.11.3: deterministic Aga Box candidate from frozen WinUAE-PASS R41.

This builder does not modify the candidate or LAST_GOOD on disk. R42 was
promoted after explicit user-confirmed WinUAE Gate B.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m15_box_r42_emit import emit_box, ENTRY_INDEX

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib"
BASE_SHA256 = "0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc"
LAST_GOOD = ROOT / "dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"  # historical R44 anchor, not moving LAST_GOOD
LAST_GOOD_SHA256 = "0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib"
GETP = b"GetP"
API = (("aga box", ENTRY_INDEX, "00,0,0,0,0"),)
VERSION = "R42 0.11.3"


def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, "immutable R41 archive changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "R41 LAST_GOOD changed"
    old_tokens, old_segments, _ = split(frozen)
    assert len(old_segments) == ENTRY_INDEX == 52
    assert not old_segments[-1].endswith(GETP)
    assert old_segments[-1].endswith(bytes.fromhex("4fef00a04cdf77f774004e75"))
    audit41 = inspect(parse(frozen))
    assert not audit41["issues"], audit41["issues"]
    assert len([t for t in audit41["tokens"] if t["name"].startswith("aga ")]) == 46

    code, labels = emit_box()
    assert code.endswith(bytes.fromhex("4fef00a04cdf77f774004e75"))

    parts = list(old_segments)
    parts[-1] = old_segments[-1] + GETP
    parts.append(code)
    assert parts[:-2] == old_segments[:-1], "historical R41 entries modified"
    assert parts[-2] == old_segments[-1] + GETP

    new_tokens = old_tokens[:-6] + token(API[0][0], 1, ENTRY_INDEX, API[0][2]) + bytes(6)
    title = b"AMOSPro AGA M15 Box R42 0.11.3\0$VER: AMOSPro_AGA 0.11.3\0"
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
    assert len(named) == 47
    got = [t for t in named if t["name"] == API[0][0]]
    assert len(got) == 1
    assert (got[0]["instruction"], got[0]["function"], got[0]["signature"]) == (1, ENTRY_INDEX, API[0][2])
    assert any(c["index"] == ENTRY_INDEX and c["parameters"] == 5 and c["getp"]
               for c in audit["parameter_checks"])
    return candidate, dict(version=VERSION, sha256=digest(candidate),
        size=len(candidate), named_commands=47, segments=53,
        new_command=API[0], changed_segments=[51, 52],
        labels=labels, Gate_A="CPU_CI_PASS", Gate_B="USER_WINUAE_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    candidate, info = build()
    assert candidate == build()[0], "R42 builder not deterministic"
    print("R42 in-memory candidate:", {k:v for k,v in info.items() if k!="labels"}, flush=True)
    if args.emit_base64:
        print("R42_BASE64_BEGIN", flush=True)
        encoded = base64.b64encode(candidate).decode("ascii")
        for i in range(0, len(encoded), 76):
            print(encoded[i:i+76], flush=True)
        print("R42_BASE64_END", flush=True)
