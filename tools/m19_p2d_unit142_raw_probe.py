#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
# AGA_NATIVE_PURPOSE: AUDIT_ONLY
"""UNIT142 historical raw-tail source provenance inventory.

Read-only. Compare pinned P2d UNIT142 against historical emitters, without
classifying an undecoded byte as CPU code or assuming zero RAM is padding.
This is neither a production-source generator nor an AMOS runtime test.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from active_library import P2D_SHA
from compiler_relocation import unpack_ap20
from m19_p2d_unit142_source import expected_sources, SPANS, CBLOCK_SPANS, GROUP_SHA

ROOT = Path(__file__).resolve().parents[1]
TAIL_START, TAIL_END = 0x0DCFC, 0x0F514
PUBLIC_RAW_ENTRY = 0x0F4E2


def compare(whole: bytes, tail: bytes, label: str, payload: bytes) -> None:
    """Report a source-emitter byte match, never invent its semantics."""
    if not payload or len(payload) % 2:
        raise ValueError(label + ": malformed emitted source")
    hits = []
    i = whole.find(payload)
    while i >= 0:
        hits.append(i)
        i = whole.find(payload, i + 1)
    if hits:
        print("EMITTER_FULL_MATCH", label, "size", len(payload),
              "offsets", ",".join("%05X" % x for x in hits))
        return
    best = None
    # A 32-byte nontrivial fingerprint is only a lead, NOT a provenance proof.
    for off in range(0, len(payload) - 31, 2):
        chunk = payload[off:off + 32]
        if len(set(chunk)) < 8 or chunk.count(0) > 12:
            continue
        index = tail.find(chunk)
        if index >= 0:
            best = (off, TAIL_START + index)
            break
    if best:
        print("EMITTER_FINGERPRINT_ONLY", label, "emitter+%05X" % best[0],
              "UNIT142+%05X" % best[1], "length 32; unproven")
    else:
        print("EMITTER_NOT_LOCATED", label, "bytes", len(payload))


def check() -> None:
    official = (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes()
    assert len(official) == 136020 and sha256(official).hexdigest() == P2D_SHA
    _token, groups, _title = unpack_ap20(official)
    group = groups[142]
    assert len(group) == 62740 and sha256(group).hexdigest() == GROUP_SHA
    reconstructed, _wrapper, modules = expected_sources()
    assert reconstructed == group and len(modules) == 127
    clean = sum(hi - lo for lo, hi, _name, _source in modules)
    assert sum(hi - lo for (_file, _start, _stop, lo, hi, *_rest) in SPANS) == 50442
    assert sum(hi - lo - 12 for lo, hi in CBLOCK_SPANS) == 2616
    assert clean == 54316 and len(group) - clean == 8424

    tail = group[TAIL_START:TAIL_END]
    assert len(tail) == 6168 and tail.startswith(b"AGAPIC  ")
    assert group[PUBLIC_RAW_ENTRY:PUBLIC_RAW_ENTRY + 4] == bytes.fromhex("4EBB0170")
    print("UNIT142_RAW_REMAINDER_PASS", len(group), "native bytes",
          clean, "source-owned", len(group) - clean, "raw preserved")
    print("RAW_TAIL", "%05X..%05X" % (TAIL_START, TAIL_END),
          len(tail), "bytes; AGAPIC ASCII header = 8")
    print("RAW_PUBLIC_ENTRY_UNCLASSIFIED", "%05X" % PUBLIC_RAW_ENTRY)

    # A zero byte is not automatically padding: record only factual ranges.
    runs = []
    at = 0
    while at < len(tail):
        if tail[at]:
            at += 1
            continue
        end = at
        while end < len(tail) and not tail[end]:
            end += 1
        if end - at >= 64:
            runs.append((TAIL_START + at, TAIL_START + end))
        at = end
    for lo, hi in sorted(runs, key=lambda x: x[1] - x[0], reverse=True)[:12]:
        print("ZERO_RUN_UNCLASSIFIED", "%05X..%05X" % (lo, hi),
              hi - lo, "bytes")
    assert runs, "Expected historical zero-region evidence missing"

    # These emitters are historical sources, not disassembled Lib bytes.
    from m16_agapic_capture_v2_emit import emit_capture_versioned
    from m16_agapic_info_emit import emit_bank_image_info
    from m16_capture_r47_core_emit import emit_scanline_rle
    from m16_capture_r47_emit import emit_capture as emit_capture_r47
    from m16_capture_emit import emit_capture as emit_capture_v1
    candidates = (
        ("capture_r84_v2", emit_capture_versioned),
        ("bank_info_r84", emit_bank_image_info),
        ("scanline_r47", emit_scanline_rle),
        ("capture_r47", emit_capture_r47),
        ("capture_r53", emit_capture_v1),
    )
    for label, emitter in candidates:
        payload, _labels = emitter()
        compare(group, tail, label, payload)
    print("UNIT142_RAW_PROVENANCE_AUDIT_PASS; candidates != migrated source")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")
    check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
