#!/usr/bin/env python3
"""M11/R26 0.9.2: in-memory AGA back-buffer native text candidate.

Builds only from the immutable R25 WinUAE-PASS archive. NEVER overwrites
R25/R24, the live dist/AMOSPro_AGA.Lib or LAST_GOOD. Gate A only.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m11_text_r26_emit import emit_text

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M10_v0.9.1_RECT_OVERLAP_R25.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "4835473771629bea697d64c9213ff1064013597f7dabc519914f4ea013af6da6"
LAST_GOOD_SHA256 = "e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f"
ENTRY = 36
TOKEN = "aga text"
SIGNATURE = "00,0,0,2"
GETP = b"GetP"
VERSION = "R26 0.9.2"

def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, "Frozen WinUAE-PASS R25 changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "LAST_GOOD changed"
    tok_before, old, _ = split(frozen)
    assert len(old) == ENTRY == 36
    assert tok_before.endswith(bytes(6))
    assert old[-1].endswith(bytes.fromhex("74004e75")), "R25 AABB exit changed"
    assert not old[-1].endswith(GETP), "R25 GetP separator unexpected"
    named = [t for t in inspect(parse(frozen))["tokens"] if t["name"].startswith("aga ")]
    assert len(named) == 30 and not any(t["name"] == TOKEN for t in named)

    routine, labels = emit_text()
    assert routine and len(routine) % 2 == 0
    segments = list(old)
    segments[-1] += GETP
    segments.append(routine)
    assert len(segments) == ENTRY+1 == 37
    assert segments[:ENTRY-1] == old[:ENTRY-1]
    assert segments[ENTRY-1] == old[ENTRY-1]+GETP
    tokens = tok_before[:-6] + token(TOKEN, 1, ENTRY, SIGNATURE) + bytes(6)
    title = b"AMOSPro AGA M11 Text R26 0.9.2\0$VER: AMOSPro_AGA 0.9.2\0"
    if len(title) & 1:
        title += b"\0"
    code = b"".join(segments)
    payload = (pack(">4I", len(segments)*2, len(tokens), len(code), len(title))
               + b"\0\0AP20" + b"".join(pack(">H", len(x)//2) for x in segments)
               + tokens + code + title + b"\0\0")
    payload += bytes((-len(payload)) % 4)
    words = pack(">I", len(payload)//4)
    candidate = frozen[:20] + words + frozen[24:28] + words + payload + frozen[-4:]

    audit = inspect(parse(candidate))
    assert not audit["issues"], audit["issues"]
    ts, parts, _ = split(candidate)
    assert ts == tokens and parts == segments
    row = [t for t in audit["tokens"] if t["name"] == TOKEN]
    assert len(row) == 1
    assert (row[0]["instruction"], row[0]["function"], row[0]["signature"]) == (1, ENTRY, SIGNATURE)
    assert any(x["index"] == ENTRY and x["parameters"] == 4 and x["getp"]
               for x in audit["parameter_checks"])
    assert len([t for t in audit["tokens"] if t["name"].startswith("aga ")]) == 31
    return candidate, {
        "version": VERSION, "size": len(candidate), "sha256": digest(candidate),
        "segments": len(parts), "new_token": TOKEN, "signature": SIGNATURE,
        "unchanged_existing_entries": list(range(ENTRY-1)),
        "previous_segment_getp_only": ENTRY-1,
        "opcode_labels": labels,
        "Gate_A": "REQUIRES_NATIVE_CPU_CI",
        "Gate_B_WinUAE": "NOT_TESTED",
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true",
                        help="Print reproducible candidate only after Gate A passes")
    opt = parser.parse_args()
    raw, info = build()
    assert raw == build()[0], "R26 build not deterministic"
    print("M11/R26 in-memory candidate:", info, flush=True)
    if opt.emit_base64:
        print("R26_BASE64_BEGIN", flush=True)
        print(base64.b64encode(raw).decode("ascii"), flush=True)
        print("R26_BASE64_END", flush=True)
