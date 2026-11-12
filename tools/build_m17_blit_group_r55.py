#!/usr/bin/env python3
"""R55: deterministic historical candidate, based on immutable R54 archive.

The ONLY working binary lives at dist/AMOSPro_AGA.Lib; build() is read-only.
A forward BRA.W at native Fill entry 20 delegates to a new native helper
APPENDED to existing last entry 58. This preserves ALL old native offsets,
existing Clear BSR.W (-572), dispatcher/state links and public tokens.
The final binary uses wrap_native_ap20, not an unwrapped native output.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from

from audit_ap20 import inspect, parse
from build_m6_blit_clear_r15 import emit_clear
from compiler_relocation import (
    unpack_ap20, unwrap_native_parts, repack_ap20,
    wrap_native_ap20, is_compiler_wrapped,
)
from m12_blit_safe_r27_emit import emit_fill_safe
from m17_blit_group_r55_emit import emit_fill_grouped

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib"
CURRENT = ROOT / "dist/AMOSPro_AGA.Lib"
R54_ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib"
BASE_SHA = "f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0"
FILL_ENTRY, CLEAR_ENTRY, LAST_ENTRY = 20, 21, 58
GETP = b"GetP"
VERSION = "R55 0.13.0 unpromoted in-memory candidate"
TITLE = b"AMOSPro AGA M17 grouped Blitter R55 0.13.0 candidate\0$VER: AMOSPro_AGA 0.13.0\0"
TITLE += bytes(len(TITLE) % 2)


def build():
    stable = BASE.read_bytes()
    assert len(stable) == 32364 and sha256(stable).hexdigest() == BASE_SHA
    assert R54_ARCHIVE.read_bytes() == stable, "Frozen R54 source archive drift"
    assert is_compiler_wrapped(stable)
    tokens, original = unwrap_native_parts(stable)
    assert len(original) == 59
    old_fill, _ = emit_fill_safe()
    assert original[FILL_ENTRY] == old_fill + GETP, "R54 Fill differs from R27"
    old_clear, _ = emit_clear(len(old_fill))
    assert original[CLEAR_ENTRY] == old_clear, "R54 Clear differs from R27"
    assert original[LAST_ENTRY].endswith(bytes.fromhex("74004e75"))

    grouped, labels = emit_fill_grouped()
    fill_native_start = sum(len(p) for p in original[:FILL_ENTRY])
    helper_native_start = sum(len(p) for p in original)
    displacement = helper_native_start - (fill_native_start + 2)
    # BRA.W branch displacement is relative to the extension word address.
    assert 0 < displacement < 32768 and not (displacement & 1)
    assert original[FILL_ENTRY][:4] == bytes.fromhex("48e7efee")

    parts = list(original)
    parts[FILL_ENTRY] = bytes.fromhex("6000") + pack(">h", displacement) + original[FILL_ENTRY][4:]
    parts[LAST_ENTRY] = original[LAST_ENTRY] + grouped
    assert len(parts) == len(original) == 59
    assert all(parts[i] == original[i] for i in range(59)
               if i not in (FILL_ENTRY, LAST_ENTRY))
    assert parts[FILL_ENTRY][4:] == original[FILL_ENTRY][4:]
    assert parts[LAST_ENTRY].startswith(original[LAST_ENTRY])
    assert parts[CLEAR_ENTRY] == old_clear  # unchanged BSR to Fill entry
    assert unpack_from(">h", parts[CLEAR_ENTRY], 24)[0] == -572

    native = repack_ap20(stable, tokens, parts, TITLE)
    result = wrap_native_ap20(native, TITLE)
    tok_new, new_parts = unwrap_native_parts(result)
    assert tok_new == tokens and new_parts == parts
    wrapped_old = unpack_ap20(stable)[1]
    wrapped_new = unpack_ap20(result)[1]
    assert len(wrapped_new) == len(wrapped_old) == 60
    assert wrapped_new[:-1] == wrapped_old[:-1], "AP20 stubs/offsets changed"
    monolith_size = len(wrapped_new[-1])
    assert monolith_size < 32768, "Compiler-safe monolith > signed 16-bit range"
    assert not inspect(parse(result))["issues"]
    before = [x for x in inspect(parse(stable))["tokens"] if x["name"].startswith("aga ")]
    after = [x for x in inspect(parse(result))["tokens"] if x["name"].startswith("aga ")]
    assert before == after and len(after) == 53
    # Active version selection/integrity is checked by active_library.py;
    # historical R55 builder must remain reproducible with an R56 in dist/.
    return result, {
        "version": VERSION, "size": len(result),
        "sha256": sha256(result).hexdigest(),
        "commands": 53, "ap20_entries": 60,
        "monolith_size": monolith_size,
        "native_fill_start": fill_native_start,
        "native_helper_start": helper_native_start,
        "fill_bra_displacement": displacement,
        "original_fill_size": len(old_fill), "grouped_fill_size": len(grouped),
        "helper_labels": labels,
        "gate_a": "CPU/CI tests required",
        "gate_b": "NOT TESTED", "gate_c": "NOT TESTED",
        "gate_d": "NOT TESTED", "last_good": "UNTOUCHED R54",
    }


if __name__ == "__main__":
    raw, info = build()
    assert raw == build()[0], "R55 builder not deterministic"
    print("R55 current dist/ candidate verified in memory:",
          {k:v for k,v in info.items() if k != "helper_labels"}, flush=True)
