#!/usr/bin/env python3
"""M9/R24 0.9.0: reproducible pure builder for stateless Aga Hotspot Hit.

Generates a candidate IN MEMORY from the immutable R23 WinUAE-PASS archive.
No live Lib or archive is overwritten by this script. Produces base64 only
with --emit-base64, for explicit integrity-checked binary publication.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m9_hotspot_r24_emit import emit_hotspot_hit

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib"
BASE_SHA256 = "899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23"
LAST_GOOD_SHA256="ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539"
ENTRY = 34
GETP = b"GetP"
VERSION = "R24 0.9.0"
SIGNATURE = "00,0,0,0,0,0"

def build():
    raw = BASE.read_bytes()
    assert digest(raw) == BASE_SHA256, "R23 WinUAE archive changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "LAST_GOOD changed"
    tokens, old, _ = split(raw)
    assert len(old) == ENTRY and tokens.endswith(bytes(6))
    assert old[-1][-144:] == bytes(144), "R23 dispatcher/private state changed"
    before_tokens = inspect(parse(raw))["tokens"]
    assert not any(t["name"].lower() == "aga hotspot hit" for t in before_tokens)
    assert len([t for t in before_tokens if t["name"].startswith("aga ")]) == 28

    routine, labels = emit_hotspot_hit()
    parts = list(old)
    # AP20 GetP is a delimiter at the *preceding* segment end. The R23
    # dispatcher ends with 144 private state bytes, not executable code.
    # Append the delimiter AFTER that state: its address/offset is unchanged.
    parts[ENTRY-1] += GETP
    parts.append(routine)
    assert len(parts) == ENTRY+1 == 35
    assert parts[:ENTRY-1] == old[:ENTRY-1]
    assert parts[ENTRY-1] == old[ENTRY-1] + GETP
    assert parts[ENTRY] == routine
    assert parts[ENTRY-1][-148:-4] == bytes(144)
    new_tokens = tokens[:-6] + token("aga hotspot hit", 1, ENTRY, SIGNATURE) + bytes(6)
    title = b"AMOSPro AGA M9 Hotspot Hit R24 0.9.0\0$VER: AMOSPro_AGA 0.9.0\0"
    if len(title)&1:
        title += b"\0"

    code = b"".join(parts)
    payload = (pack(">4I", len(parts)*2, len(new_tokens), len(code), len(title))
               + b"\0\0AP20"
               + b"".join(pack(">H", len(s)//2) for s in parts)
               + new_tokens + code + title + b"\0\0")
    payload += bytes((-len(payload)) % 4)
    words = pack(">I", len(payload)//4)
    candidate = raw[:20] + words + raw[24:28] + words + payload + raw[-4:]

    audit = inspect(parse(candidate))
    assert audit["issues"] == [], audit["issues"]
    new_tok, after, _ = split(candidate)
    assert new_tok == new_tokens and after == parts
    rows = [t for t in audit["tokens"] if t["name"] == "aga hotspot hit"]
    assert len(rows) == 1
    assert (rows[0]["instruction"],rows[0]["function"],rows[0]["signature"]) == (
        1, ENTRY, SIGNATURE)
    assert any(x["index"] == ENTRY and x["getp"] and x["parameters"] == 6
               for x in audit["parameter_checks"])
    assert [i for i in range(ENTRY) if parts[i] != old[i]] == [ENTRY-1]
    return candidate, {
        "version": VERSION,
        "size": len(candidate),
        "sha256": digest(candidate),
        "new_entry": ENTRY,
        "old_entries_changed": [ENTRY-1],
        "old_entry_suffix": "GetP",
        "new_token": "Aga Hotspot Hit",
        "m68k_labels": labels,
        "AMOS_WinUAE": "NOT_TESTED",
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    candidate, info = build()
    assert build()[0] == candidate, "R24 output not deterministic"
    print("R24 pure builder preflight (R23 live Lib unchanged):", info, flush=True)
    if args.emit_base64:
        print("R24_BASE64_BEGIN", flush=True)
        print(base64.b64encode(candidate).decode("ascii"), flush=True)
        print("R24_BASE64_END", flush=True)
