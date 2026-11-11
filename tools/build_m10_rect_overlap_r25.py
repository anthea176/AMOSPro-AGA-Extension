#!/usr/bin/env python3
"""M10/R25 0.9.1: reproducible in-memory candidate from frozen R24.

No files overwritten, no branch creation, no runtime PASS claims.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m10_rect_overlap_r25_emit import emit_rect_overlap

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M10_v0.9.1_RECT_OVERLAP_R25.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "cc8776e7303c529492fe6761544f4b2be1180063f3787fa840f44129766e3671"
LAST_GOOD_SHA256="ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539"
ENTRY = 35
GETP = b"GetP"
TOKEN = "aga rect overlap"
SIGNATURE = "00,0,0,0,0,0,0,0"
VERSION = "R25 0.9.1"


def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, "Frozen WinUAE-PASS R24 changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    tok_before, old, _ = split(frozen)
    assert len(old) == ENTRY == 35
    assert tok_before.endswith(bytes(6))
    assert old[-1].endswith(bytes.fromhex("74004e75")), "R24 hotspot exit changed"
    assert not old[-1].endswith(GETP)
    original_tokens = inspect(parse(frozen))["tokens"]
    assert len([t for t in original_tokens if t["name"].startswith("aga ")]) == 29
    assert not any(t["name"] == TOKEN for t in original_tokens)

    routine, labels = emit_rect_overlap()
    assert routine and len(routine) % 2 == 0
    parts = list(old)
    parts[-1] += GETP
    parts.append(routine)
    assert len(parts) == ENTRY+1 == 36
    assert parts[:ENTRY-1] == old[:ENTRY-1]
    assert parts[ENTRY-1] == old[ENTRY-1] + GETP

    tokens = tok_before[:-6] + token(TOKEN, 1, ENTRY, SIGNATURE) + bytes(6)
    title = b"AMOSPro AGA M10 Rect Overlap R25 0.9.1\0$VER: AMOSPro_AGA 0.9.1\0"
    if len(title) & 1:
        title += b"\0"
    code = b"".join(parts)
    payload = (pack(">4I", len(parts)*2, len(tokens), len(code), len(title))
               + b"\0\0AP20"
               + b"".join(pack(">H", len(s)//2) for s in parts)
               + tokens + code + title + b"\0\0")
    payload += bytes((-len(payload)) % 4)
    words = pack(">I", len(payload)//4)
    candidate = frozen[:20] + words + frozen[24:28] + words + payload + frozen[-4:]

    audit = inspect(parse(candidate))
    assert not audit["issues"], audit["issues"]
    tok_check, chk, _ = split(candidate)
    assert tok_check == tokens and chk == parts
    row = [t for t in audit["tokens"] if t["name"] == TOKEN]
    assert len(row) == 1 and (row[0]["instruction"], row[0]["function"],
                              row[0]["signature"]) == (1, ENTRY, SIGNATURE)
    assert any(x["index"] == ENTRY and x["getp"] and x["parameters"] == 8
               for x in audit["parameter_checks"])
    assert [i for i in range(ENTRY) if old[i] != parts[i]] == [ENTRY-1]
    return candidate, {
        "version": VERSION,
        "size": len(candidate),
        "sha256": digest(candidate),
        "segments": len(parts),
        "new_token": TOKEN,
        "signature": SIGNATURE,
        "previous_segments_changed": [ENTRY-1],
        "opcode_labels": labels,
        "WinUAE": "NOT_TESTED",
    }


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--emit-base64", action="store_true",
                   help="Output reproducible binary candidate for audited publication")
    args = a.parse_args()
    raw, info = build()
    assert raw == build()[0], "R25 reproducibility failure"
    print("M10 R25 in-memory builder:", info, flush=True)
    if args.emit_base64:
        print("R25_BASE64_BEGIN", flush=True)
        print(base64.b64encode(raw).decode("ascii"), flush=True)
        print("R25_BASE64_END", flush=True)
