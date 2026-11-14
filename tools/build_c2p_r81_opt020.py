#!/usr/bin/env python3
"""R81 OPT020 candidate reconstructed in memory from the exact R80 SHA.

Three existing AP20 entries (Blit / Zoom / IFF-to-Chunky) are replaced by
separately checked MC68020 native variants. Historical builders, the active
dist binary, LAST_GOOD and the sole current ASC are never modified here.
No release, compiled AMOS test, or promotion is implied by this builder.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256

from audit_ap20 import inspect, parse
from build_c2p_r76_rpg_fix import SITES, state_offset
from build_c2p_r80_iff_chunky import build as build_r80
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from c2p_r78_blit_emit import emit_blit, BANK as BLIT_BANK
from c2p_r79_zoom_emit import emit_zoom, BANK as ZOOM_BANK
from c2p_r80_iff_chunky_emit import emit_iff_to_chunky, BANK as IFF_BANK
from c2p_opt020_variants import (
    emit_blit_opt020, emit_zoom_opt020, emit_iff_chunky_opt020,
)

R80_SHA = "24e05f7403c07d23db1ff65c9499a032b413fd7d0d140ce8a55e2fd6778b18c6"
TITLE = b"AMOSPro AGA C2P OPT020 R81 0.13.26 candidate\0$VER: AMOSPro_AGA 0.13.26\0"
TITLE += bytes(len(TITLE) & 1)


def build():
    parent, _ = build_r80()
    assert sha256(parent).hexdigest() == R80_SHA, "R80 base drift"
    tokens, old = unwrap_native_parts_v2(parent)
    assert len(old) == 76 and not old[-1].endswith(GETP)
    assert state_offset(old) == 12070
    originals = (emit_blit()[0], emit_zoom()[0], emit_iff_to_chunky()[0])
    assert old[73] == originals[0] + GETP, "R78 historical entry modified"
    assert old[74] == originals[1] + GETP, "R79 historical entry modified"
    assert old[75] == originals[2], "R80 historical entry modified"

    replacements = (
        emit_blit_opt020()[0],
        emit_zoom_opt020()[0],
        emit_iff_chunky_opt020()[0],
    )
    assert 0 < len(replacements[0]) < 10000
    assert 0 < len(replacements[1]) < 10000
    assert 0 < len(replacements[2]) < 14000
    for blob, marker, count in zip(
        replacements, (BLIT_BANK, ZOOM_BANK, IFF_BANK), (2, 2, 1)
    ):
        assert blob.count(marker) == count, "AMOS Bnk.GetAdr markers changed"

    parts = list(old)
    parts[73] = replacements[0] + GETP
    parts[74] = replacements[1] + GETP
    parts[75] = replacements[2]
    assert parts[:73] == old[:73], "Earlier AP20 entry modified"
    assert state_offset(parts) == 12070, "Keyboard/mouse state relocated"
    assert_native_links(parts[:70])
    check_cross_r74(parts[:70])
    for entry, pos, opcode in SITES:
        assert parts[entry][pos:pos + 4] == (
            opcode.to_bytes(2, "big") + bytes.fromhex("2f26")
        ), "Keyboard/mouse LEA changed"

    native = repack_ap20(parent, tokens, parts, TITLE)
    candidate = wrap_native_ap20_v2(native, TITLE)
    actual_tokens, actual_parts = unwrap_native_parts_v2(candidate)
    assert actual_tokens == tokens and actual_parts == parts
    _, entries, title = unpack_ap20(candidate)
    assert title == TITLE and len(entries) == 77
    audit = inspect(parse(candidate))
    assert not audit["issues"], audit["issues"]
    public = [x for x in audit["tokens"] if x["name"].startswith("aga ")]
    assert len(public) == 70
    assert [public[i]["name"] for i in (-3, -2, -1)] == [
        "aga c2p blit", "aga c2p zoom", "aga iff to chunky"
    ]
    return candidate, {
        "version": "R81 v0.13.26 OPT020",
        "sha256": sha256(candidate).hexdigest(),
        "size": len(candidate),
        "commands": len(public),
        "ap20_entries": len(entries),
        "native_changed_from_r80": [73, 74, 75],
        "r80_base_sha": R80_SHA,
        "native_gate_a": "PASS run 43615716395 (22 Blit, 14 Zoom, 15 IFF rows, CPU000 refusal)",
        "winuae_gate_b": "NOT TESTED",
        "compiled_gate_c": "NOT REQUESTED",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    image, meta = build()
    assert build()[0] == image, "R81 builder is not deterministic"
    print("R81 OPT020 IN-MEMORY BUILDER", meta, flush=True)
    if args.emit_base64:
        print("R81_B64_BEGIN", flush=True)
        data = base64.b64encode(image).decode("ascii")
        for index in range(0, len(data), 120):
            print("R81_B64", data[index:index + 120], flush=True)
        print("R81_B64_END", flush=True)


if __name__ == "__main__":
    main()
