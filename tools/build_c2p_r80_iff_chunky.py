#!/usr/bin/env python3
"""R80 candidate in memory: append Aga Iff To Chunky(File$,Bank) to R79.

No binary writes, no LAST_GOOD change and no synthetic Gate B claim.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
from audit_ap20 import inspect, parse, token
from build_c2p_r79_zoom import build as build_r79
from build_c2p_r76_rpg_fix import SITES, state_offset
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from c2p_r80_iff_chunky_emit import emit_iff_to_chunky, BANK

R79_SHA = "ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab"
API = ("aga iff to chunky", 1, 75, "02,0")
TITLE = b"AMOSPro AGA IFF Chunky R80 0.13.25 candidate\0$VER: AMOSPro_AGA 0.13.25\0"
TITLE += bytes(len(TITLE) & 1)


def build():
    parent, _ = build_r79()
    assert sha256(parent).hexdigest() == R79_SHA
    tokens, original = unwrap_native_parts_v2(parent)
    assert len(original) == 75 and not original[-1].endswith(GETP)
    assert state_offset(original) == 12070
    for entry, pos, opcode in SITES:
        assert original[entry][pos:pos+4] == opcode.to_bytes(2, "big") + bytes.fromhex("2f26")
    assert_native_links(original[:70])
    check_cross_r74(original[:70])
    emitted, labels = emit_iff_to_chunky()
    assert 0 < len(emitted) < 12000 and emitted.count(BANK) == 1
    parts = list(original)
    parts[-1] += GETP
    parts.append(emitted)
    assert parts[:74] == original[:74]
    assert parts[74] == original[74] + GETP
    assert state_offset(parts) == 12070
    next_tokens = tokens[:-6] + token(*API) + bytes(6)
    native = repack_ap20(parent, next_tokens, parts, TITLE)
    candidate = wrap_native_ap20_v2(native, TITLE)
    got_tokens, got_parts = unwrap_native_parts_v2(candidate)
    assert got_tokens == next_tokens and got_parts == parts
    _, segments, title = unpack_ap20(candidate)
    assert title == TITLE and len(segments) == 77
    assert_native_links(got_parts[:70])
    check_cross_r74(got_parts[:70])
    assert state_offset(got_parts) == 12070
    audit = inspect(parse(candidate))
    assert audit["issues"] == [], audit["issues"]
    public = [x for x in audit["tokens"] if x["name"].startswith("aga ")]
    assert len(public) == 70
    assert (public[-1]["name"], public[-1]["function"], public[-1]["signature"]) == (
        API[0], API[2], API[3])
    return candidate, {
        "version": "R80 v0.13.25 IFF to Chunky",
        "sha256": sha256(candidate).hexdigest(),
        "size": len(candidate),
        "commands": len(public),
        "ap20_entries": len(segments),
        "native_entry": 75,
        "code_bytes": len(emitted),
        "base_sha": R79_SHA,
        "gate_a": "PENDING native CPU tests",
        "gate_b": "NOT TESTED",
        "gate_c": "NOT TESTED",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    candidate, meta = build()
    assert build()[0] == candidate
    print("R80 IFF TO CHUNKY IN-MEMORY BUILDER", meta, flush=True)
    if args.emit_base64:
        print("R80_B64_BEGIN", flush=True)
        b64 = base64.b64encode(candidate).decode("ascii")
        for i in range(0, len(b64), 120):
            print("R80_B64", b64[i:i+120], flush=True)
        print("R80_B64_END", flush=True)
