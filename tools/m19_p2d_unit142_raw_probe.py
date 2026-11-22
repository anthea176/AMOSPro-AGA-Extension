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

from active_library import P2D_SHA, R83_SHA
from compiler_relocation import GETP, unpack_ap20
from m19_p2d_unit142_source import expected_sources, SPANS, CBLOCK_SPANS, GROUP_SHA

ROOT = Path(__file__).resolve().parents[1]
TAIL_START, TAIL_END = 0x0DCFC, 0x0F514
PUBLIC_P1D_ENTRY = 0x0F4E2


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
    assert reconstructed == group and len(modules) == 156
    clean = sum(hi - lo for lo, hi, _name, _source in modules)
    assert sum(hi - lo for (_file, _start, _stop, lo, hi, *_rest) in SPANS) == 50442
    assert sum(hi - lo - 12 for lo, hi in CBLOCK_SPANS) == 2616
    assert clean == 58080 and len(group) - clean == 4660

    # Source-owned code vs. original state/header/pseudo data, byte exact.
    mask = bytearray(len(group))
    for lo, hi, filename, _source in modules:
        assert 0 <= lo < hi <= len(group), filename
        assert mask[lo:hi] == bytes(hi-lo), "Source overlap: " + filename
        mask[lo:hi] = b"\x01"*(hi-lo)
    assert mask.count(1) == clean and mask.count(0) == len(group)-clean

    from m19_p0c_screen_close_bridge_emit import AGA_STATE_OFFSET
    from m19_p0e_object_table_emit import emit_object_table
    from m19_p0f_object_identity_emit import emit_object_identity
    from m19_p1c_bob_priority_emit import emit_priority_open
    from m19_p1d_limit_bob_emit import TABLE_BYTES, emit_limit_open
    p0e, labels = emit_object_table()
    p0f, flabels = emit_object_identity()
    p1c, _ = emit_priority_open(1102, 0x0F0A4-34)
    p1d = emit_limit_open(0x0F0A4-34, 0x0F0D2-34)
    assert AGA_STATE_OFFSET == 0x001C2
    data = (
        (AGA_STATE_OFFSET, AGA_STATE_OFFSET+40, bytes(40), "AGA Screen state"),
        # Proven by the exact SHA-pinned R83 native Screen Open source.
        (0x005D4, 0x005E6, b"intuition.library\x00", "R83 Intuition name"),
        (0x005E6, 0x005F8, b"graphics.library\x00\x00", "R83 graphics name"),
        (0x0E018, 0x0E620, p0e[labels["object_root"]:], "P0e objects"),
        (0x0ECA4, 0x0F0A4, p0f[flabels["identity_stamp_table"]:], "P0f stamps"),
        (0x0F0CA, 0x0F0D2, p1c[-8:], "P1c context"),
        (0x0F0D2, 0x0F4E2, p1d[:TABLE_BYTES], "P1d limit table"),
    )
    confirmed = 0
    for lo,hi,original,label in data:
        assert len(original) == hi-lo and group[lo:hi] == original, label
        assert mask[lo:hi] == bytes(hi-lo), label+" already in source code"
        confirmed += hi-lo
        print("UNIT142_SOURCE_DATA_CONFIRMED", label, "%05X..%05X"%(lo,hi),hi-lo)
    assert confirmed == 3692

    # R83 carries a second group of literal AmigaOS library/driver names,
    # AMOS GetP delimiters and signature headers. These are source-proven
    # DATA, not candidate Motorola instructions. Do not treat zero runs
    # or unrelated opaque code as padding.
    from build_aga_r83_modular import build as build_r83
    from build_c2p_r76_rpg_fix import MOUSE_STATE_SIZE
    historical, r83_info = build_r83()
    assert r83_info["sha256"] == R83_SHA
    assert sha256(historical).hexdigest() == R83_SHA
    _r83_tokens, r83_parts, _r83_title = unpack_ap20(historical)
    assert len(r83_parts[82]) == 52974
    assert MOUSE_STATE_SIZE == 144 and AGA_STATE_OFFSET + 12070 == 0x030E8
    r83_literals = (
        (0x00448, b"intuition.library\x00graphics.library\x00\x00GetP", "Intuition/graphics names"),
        (0x0030C, b"graphics.library\x00\x00GetP", "graphics name/GetP"),
        (0x02D7E, b"input.device\x00\x00GetP", "input.device name/GetP"),
        (0x015C8, b"dos.library\x00GetP", "DOS name/GetP IFF"),
        (0x03A14, b"dos.library\x00GetP", "DOS name/GetP load"),
        (0x0410A, b"dos.library\x00GetP", "DOS name/GetP save"),
        (0x01BD2, b"dos.library\x00", "DOS name before pseudo-op"),
        (0x077D0, b"AGAPIC  GetP", "AGA picture signature/GetP"),
        (0x09558, b"FICON8  GetP", "FICON8 signature/GetP"),
        (0x09A92, b"FICHIP8 GetP", "FICHIP8 signature/GetP"),
        (0x05702, b"GetP", "AMOS GetP after opaque zeros A"),
        (0x06674, b"GetP", "AMOS GetP after opaque zeros B"),
        (0x030E8, bytes(MOUSE_STATE_SIZE) + GETP, "144-byte keyboard/mouse state + GetP"),
        (0x05302, bytes(8) + GETP, "R83 helper zero state + GetP"),
    )
    r83_noncode = 0
    for lo, literal, name in r83_literals:
        hi = lo + len(literal)
        assert group[lo:hi] == literal == r83_parts[82][lo:hi], name
        assert mask[lo:hi] == bytes(hi-lo), name + " overlaps code"
        r83_noncode += hi-lo
        print("UNIT142_R83_LITERAL_DATA_CONFIRMED", name,
              "%05X..%05X" % (lo,hi), hi-lo)
    assert r83_noncode == 344

    headers = 0
    for lo,hi in CBLOCK_SPANS:
        for start,end,literal in ((lo,lo+8,b"AGACBLK "),(hi-4,hi,b"GetP")):
            assert group[start:end] == literal and mask[start:end] == bytes(end-start)
            headers += end-start
    assert headers == 36
    assert group[TAIL_START:TAIL_START+8] == b"AGAPIC  "
    assert mask[TAIL_START:TAIL_START+8] == bytes(8)
    assert group[0x0E8D8:0x0E8DE] == bytes.fromhex("FE11F700031D")
    assert mask[0x0E8D8:0x0E8DE] == bytes(6)
    # Linker grammar is authoritative: FE11/F700 is AMOS Main Rjsr,
    # and literal "GetP" delimits Compiler parameters. Decode neither
    # as Motorola instructions, and count only complete isolated islands.
    from amos_main_abi import rjsr
    gaps = []
    pos = 0
    while pos < len(mask):
        if mask[pos]:
            pos += 1
            continue
        lo = pos
        while pos < len(mask) and not mask[pos]:
            pos += 1
        gaps.append((lo, pos))
    pseudo = [(lo, hi) for lo, hi in gaps
              if hi-lo == 6 and group[lo:lo+4] == bytes.fromhex("FE11F700")]
    getp = [(lo, hi) for lo, hi in gaps
            if hi-lo == 4 and group[lo:hi] == GETP]
    assert len(pseudo) == 45 and len(getp) == 54, (len(pseudo),len(getp))
    for lo, hi in pseudo:
        index = int.from_bytes(group[lo+4:hi], "big")
        assert index in (0x008C,0x031D,0x0320,0x0330,0x0333)
        assert group[lo:hi] == rjsr(index), "Unproven AMOS Main pseudo-op"
    for lo, hi in getp:
        assert group[lo:hi] == GETP
    assert any(lo == 0x0E8D8 for lo, _ in pseudo)
    assert all(any(lo == end-4 for lo, _ in getp)
               for _begin, end in CBLOCK_SPANS)
    extra_markers = (len(pseudo)-1)*6 + (len(getp)-3)*4
    assert any(lo == 0x00760 for lo, _ in getp)
    assert extra_markers == 468
    print("UNIT142_LINKER_MARKERS_PASS", len(pseudo), "AMOS Main 6-byte records,",
          len(getp), "GetP 4-byte records;", extra_markers,
          "additional non-code bytes after previously counted records")
    known_noncode = confirmed + headers + 8 + 6
    known_noncode += extra_markers + r83_noncode
    assert known_noncode == 4554
    unknown = len(group) - clean - known_noncode
    assert unknown == 106
    print("UNIT142_RESIDUAL_CLASSIFIED_PASS", known_noncode,
          "proven non-code bytes;",unknown,"unclassified preserved bytes")

    # Keep a reproducible source-only map of the genuinely UNCLASSIFIED
    # gaps. Observed bytes do not imply executable code or spare padding.
    classified = bytearray(mask)
    def mark_noncode(lo, hi, tag):
        assert 0 <= lo <= hi <= len(group), tag
        for pos in range(lo, hi):
            assert classified[pos] in (0, 2), (tag, pos)
            classified[pos] = 2

    for lo, hi, _original, label in data:
        mark_noncode(lo, hi, label)
    for lo, literal, label in r83_literals:
        mark_noncode(lo, lo + len(literal), label)
    for lo, hi in CBLOCK_SPANS:
        mark_noncode(lo, lo + 8, "AGACBLK")
        mark_noncode(hi - 4, hi, "CBlock GetP")
    mark_noncode(TAIL_START, TAIL_START+8, "AGAPIC")
    for lo, hi in pseudo:
        mark_noncode(lo, hi, "AMOS Main pseudo-call")
    for lo, hi in getp:
        mark_noncode(lo, hi, "AMOS GetP")
    assert classified.count(1) == clean
    assert classified.count(2) == known_noncode
    assert classified.count(0) == unknown
    undecided = []
    at = 0
    while at < len(group):
        if classified[at]:
            at += 1
            continue
        end = at
        while end < len(group) and not classified[end]:
            end += 1
        undecided.append((at, end))
        at = end
    assert sum(hi - lo for lo, hi in undecided) == unknown
    for lo, hi in sorted(undecided, key=lambda pair: pair[1] - pair[0],
                         reverse=True)[:30]:
        print("UNIT142_UNCLASSIFIED_ISLAND", "%05X..%05X" % (lo, hi),
              hi-lo, "bytes", "hex", group[lo:min(hi,lo+16)].hex().upper())


    tail = group[TAIL_START:TAIL_END]
    assert len(tail) == 6168 and tail.startswith(b"AGAPIC  ")
    assert group[PUBLIC_P1D_ENTRY:PUBLIC_P1D_ENTRY + 4] == bytes.fromhex("4EBB0170")
    assert any(lo == PUBLIC_P1D_ENTRY and hi == TAIL_END and "P1D_LIMIT_OPEN" in name
               for lo, hi, name, _code in modules), "P1d public wrapper source missing"
    print("UNIT142_RAW_REMAINDER_PASS", len(group), "native bytes",
          clean, "source-owned", len(group) - clean, "raw preserved")
    print("RAW_TAIL", "%05X..%05X" % (TAIL_START, TAIL_END),
          len(tail), "bytes; AGAPIC ASCII header = 8")
    print("SOURCE_PINNED_PUBLIC_ENTRY", "%05X" % PUBLIC_P1D_ENTRY)

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
        print("ZERO_RUN_OBSERVED", "%05X..%05X" % (lo, hi),
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
