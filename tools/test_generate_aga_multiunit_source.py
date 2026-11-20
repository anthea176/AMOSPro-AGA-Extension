#!/usr/bin/env python3
"""Read-only regression checks for SHA-pinned R88 four-unit native ASM export.

Run from repo root: py -3 tools/test_generate_aga_multiunit_source.py
No WinUAE, AMOS Compiler, assembler or .Lib modifications are performed.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack
import json
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from active_library import R84_SHA, R88_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, verify_active
from build_m19_p28_r88_in_memory import build as build_r88
from compiler_relocation import repack_ap20, unpack_ap20, RBSR
from export_aga_asm import decode_exact_asm
from decoder68k import Decoder
from generate_aga_multiunit_source import (
    digest, export, identify, native_unit_source, validate_wrapped, trace_unit_code,
)

def run() -> None:
    # AMOS Rjsr is a 6-byte linker word, and decoded CPU code resumes after it.
    fixture = bytes.fromhex("7001fe11f700031d70024e75")
    decoded, covered = trace_unit_code(fixture, {0})
    assert set(decoded) == {0, 8, 10}
    assert decoded[8].text == "moveq #2,d0"
    assert not any(covered[2:8])
    # Authentic MC68000 signed and unsigned integer DIV/MUL mnemonics.
    for opcode, expected in (
        ("80c1", "divu.w d1,d0"),
        ("81c1", "divs.w d1,d0"),
        ("c0c1", "mulu.w d1,d0"),
        ("c1c1", "muls.w d1,d0"),
    ):
        actual = Decoder(bytes.fromhex(opcode)).decode(0)
        assert actual is not None and actual.text == expected, (opcode, actual)
    current_file = ROOT / "dist/AMOSPro_AGA.Lib"
    good_file = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
    # R88 is historical now: rebuild the exact image from its pinned R87
    # predecessor; never make a second installable .Lib or replace P0c.
    active_before = current_file.read_bytes()
    good = good_file.read_bytes()
    assert digest(active_before) in (AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA), "Active AP20 islands/B7 differs from pinned SHA"
    assert digest(good) == R84_SHA, "Protected R84 LAST_GOOD changed"
    active, frozen, _ = verify_active(ROOT)
    assert active == active_before and frozen == good
    before, meta = build_r88()
    assert len(before) == 75040 and digest(before) == R88_SHA
    assert meta["sha256"] == R88_SHA and meta["entries"] == 88
    assert identify(before)[0] == "R88"
    segments, title, refs = validate_wrapped(
        before, 84, ("C2P", "IFF", "BOBS", "AGA")
    )
    assert len(segments) == 88
    assert tuple(map(len, segments[84:])) == (5558, 2508, 7038, 56580)
    assert all(group in refs for group in (84, 85, 86, 87))
    assert all(refs[group] for group in (84, 85, 86, 87))

    # Corrupt just the first live RBSR target without changing the AP20
    # container geometry. It MUST NOT be accepted as an audited V2 bridge.
    tok, parts, title = unpack_ap20(before)
    idx = next(i for i, s in enumerate(parts[:84]) if s.startswith(RBSR))
    invalid = list(parts)
    invalid[idx] = invalid[idx][:2] + pack(">HH", 98, 0) + invalid[idx][6:]
    corrupt = repack_ap20(before, tok, invalid, title)
    try:
        validate_wrapped(corrupt, 84, ("C2P", "IFF", "BOBS", "AGA"))
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid RBSR native-unit target accepted")

    with TemporaryDirectory(prefix="aga-r88-multiunit-") as tmp:
        output = Path(tmp) / "src/generated"
        paths = export(before, root=ROOT, target=output, strict=True)
        assert len(paths) == 7, [str(p) for p in paths]
        manifest = json.loads((output / "AMOSPro_AGA_R88_NATIVE.json").read_text())
        assert manifest["input_sha256"] == R88_SHA
        assert manifest["deterministic_builder_verified"] is True
        assert manifest["exact_ap20_binary_roundtrip_verified"] is True
        assert manifest["native_assembler_verified"] is False
        assert manifest["ap20_entries"] == 88
        assert len(manifest["groups"]) == 4
        linked = (output / "AMOSPro_AGA_R88_NATIVE.s").read_text()
        assert linked.count('    include "AMOSPro_AGA_R88_') == 4
        assert "HUNK_DATA_END:" in linked
        exact = (output / "AMOSPro_AGA_R88_AP20_EXACT.s").read_text()
        assert decode_exact_asm(exact) == before
        for i, name in enumerate(("C2P", "IFF", "BOBS", "AGA"), 84):
            entry = manifest["groups"][i - 84]
            assert entry["sha256"] == sha256(segments[i]).hexdigest()
            assert entry["mnemonic_bytes"] + entry["raw_dc_bytes"] == len(segments[i])
            asm = (output / f"AMOSPro_AGA_R88_{name}_NATIVE.s").read_text()
            assert "MC68020" in asm and "NOT" in asm
        try:
            export(before, root=ROOT, target=ROOT / "dist/forbidden",
                   strict=True)
        except ValueError:
            pass
        else:
            raise AssertionError("Export was allowed inside dist/")
    assert current_file.read_bytes() == active_before, "Active AP20 islands .Lib modified"
    assert good_file.read_bytes() == good, "LAST_GOOD modified"
    print("R88 HISTORICAL MULTI-UNIT GATE A EXPORT PASS: frozen builder, 4 groups, exact AP20 bytes, SHA, RBSR; active canonical B7/AP20 islands and LAST_GOOD protected")
    print("NOTE: native vasm reassembly, WinUAE B and Compiler C NOT RUN")

if __name__ == "__main__":
    run()
