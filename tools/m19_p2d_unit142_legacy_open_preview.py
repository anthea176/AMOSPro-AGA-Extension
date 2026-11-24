#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
# AGA_NATIVE_PURPOSE: AUDIT_ONLY
"""Explore legacy AGA Screen Open source, without installing or rewriting it.

The P1c emitter proves the executable entry $00470; the historical
R83 builder is independently SHA-pinned. Decoder output is only a
preview: it may include undecoded raw bytes and must pass vasm exactness.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from active_library import P2D_SHA, R83_SHA
from build_aga_r83_modular import build as build_r83
from compiler_relocation import unpack_ap20
from generate_aga_multiunit_source import native_unit_source
from m19_p1c_bob_priority_emit import emit_priority_open

ROOT = Path(__file__).resolve().parents[1]
UNIT_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"
OPEN_LO, OPEN_HI = 0x00470, 0x00764
P1C_AT = 0x0F0A4


def probe(vasm: Path, show: bool = False) -> None:
    official = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert len(official) == 136020 and sha256(official).hexdigest() == P2D_SHA
    _tokens, units, _title = unpack_ap20(official)
    group = units[142]
    assert len(group) == 62740 and sha256(group).hexdigest() == UNIT_SHA
    priority, _context = emit_priority_open(1102, P1C_AT-34)
    assert group[P1C_AT:P1C_AT+8] == priority[:8]
    assert priority[:4] == bytes.fromhex("4EBB0170")
    signed_disp = int.from_bytes(priority[4:8], "big", signed=True)
    assert P1C_AT + 2 + signed_disp == OPEN_LO
    print("UNIT142_LEGACY_OPEN_ENTRY_PROVEN", f"{OPEN_LO:05X}", "P1c forward call")

    old, meta = build_r83()
    assert meta["sha256"] == R83_SHA and sha256(old).hexdigest() == R83_SHA
    _tok, parts, _title = unpack_ap20(old)
    historic = parts[82]
    assert len(historic) == 52974
    current = group[OPEN_LO:OPEN_HI]
    source = historic[OPEN_LO:OPEN_HI]
    if current != source:
        mismatch = next(i for i,(a,b) in enumerate(zip(current,source)) if a!=b)
        print("UNIT142_LEGACY_OPEN_R83_DIFFERS",f"{OPEN_LO+mismatch:05X}",
              "requires distinct source provenance, no migration")
        return
    print("UNIT142_LEGACY_OPEN_R83_SOURCE_EXACT_PASS", len(source), sha256(source).hexdigest())

    preview, report = native_unit_source("LEGACY_SCREEN_OPEN", current, [(0,0)])
    assert report["bytes"] == OPEN_HI-OPEN_LO
    assert report["mnemonic_bytes"] + report["raw_dc_bytes"] == len(current)
    print("UNIT142_LEGACY_OPEN_PREVIEW",report["mnemonic_bytes"],
          "candidate instructions;",report["raw_dc_bytes"],"raw bytes")
    text = "; AGA_NATIVE_MIN_CPU: MC68020\n; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n" + preview
    with TemporaryDirectory(prefix="unit142_legacy_screen_") as dirname:
        folder=Path(dirname)
        src=folder/"LEGACY_SCREEN_OPEN.s"
        dst=folder/"LEGACY_SCREEN_OPEN.bin"
        src.write_text(text,encoding="ascii",newline="\n")
        cmd=[str(vasm.resolve()),"-Fbin","-m68020","-no-opt","-quiet",
             "-o",str(dst),src.name]
        run=subprocess.run(cmd,cwd=folder,capture_output=True,text=True,check=False)
        if run.returncode:
            print("UNIT142_LEGACY_OPEN_PREVIEW_NOT_ASSEMBLABLE",run.stderr[:900])
            return
        if dst.read_bytes()!=current:
            print("UNIT142_LEGACY_OPEN_PREVIEW_BYTE_DRIFT; no migration")
            return
    print("UNIT142_LEGACY_OPEN_PREVIEW_VASM_EXACT_PASS",len(current),
          "preview only; no production module")
    if show:
        print("UNIT142_LEGACY_OPEN_ASM_B64_BEGIN")
        print(base64.b64encode(text.encode("ascii")).decode("ascii"))
        print("UNIT142_LEGACY_OPEN_ASM_B64_END")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vasm",required=True,type=Path)
    parser.add_argument("--emit-base64",action="store_true")
    a=parser.parse_args()
    probe(a.vasm,a.emit_base64)
