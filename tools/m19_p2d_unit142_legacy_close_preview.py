#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
# AGA_NATIVE_PURPOSE: AUDIT_ONLY
"""Read-only historical provenance of AGA cold/end/close region in UNIT142.

Compare byte-exact R83 emitter output with current P2d, preserving the
verified 40-byte AGA Screen state as data. CFG candidates and vasm previews
do not by themselves authorize a new production ASM module.
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
from m19_p0c_screen_close_bridge_emit import AGA_STATE_OFFSET

ROOT = Path(__file__).resolve().parents[1]
UNIT_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"
LO, HI = 0x0005A, 0x002A2
STATE_SIZE = 40


def probe(vasm: Path, emit_base64: bool = False) -> None:
    official = (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes()
    assert len(official) == 136020 and sha256(official).hexdigest() == P2D_SHA
    _tokens, groups, _title = unpack_ap20(official)
    unit = groups[142]
    assert len(unit) == 62740 and sha256(unit).hexdigest() == UNIT_SHA

    old, info = build_r83()
    assert info["sha256"] == R83_SHA and sha256(old).hexdigest() == R83_SHA
    _tok, parts, _title = unpack_ap20(old)
    assert len(parts[82]) == 52974
    source = parts[82][LO:HI]
    candidate = unit[LO:HI]
    assert len(source) == len(candidate) == HI-LO == 584
    if source != candidate:
        diffs = [i for i, (a,b) in enumerate(zip(source,candidate)) if a!=b]
        print("UNIT142_LEGACY_CLOSE_R83_DIFFERS",len(diffs),
              "first at","%05X"%(LO+diffs[0]),"no migration")
        return
    print("UNIT142_LEGACY_CLOSE_R83_SOURCE_EXACT_PASS",len(candidate),
          sha256(candidate).hexdigest())
    assert AGA_STATE_OFFSET == 0x001C2
    state_lo = AGA_STATE_OFFSET - LO
    assert candidate[state_lo:state_lo+STATE_SIZE] == bytes(STATE_SIZE)
    print("UNIT142_LEGACY_CLOSE_STATE_PRESERVED",STATE_SIZE,
          "bytes at",f"{AGA_STATE_OFFSET:05X}")

    entries = [(0,0),(1,0x001EA-LO)]
    preview, report = native_unit_source("LEGACY_CLOSE_CORE", candidate, entries)
    assert report["bytes"] == 584
    assert report["mnemonic_bytes"] + report["raw_dc_bytes"] == 584
    print("UNIT142_LEGACY_CLOSE_PREVIEW",
          report["mnemonic_bytes"],"candidate code bytes,",
          report["raw_dc_bytes"],"raw/data bytes")
    text = ("; AGA_NATIVE_MIN_CPU: MC68020\n"
            "; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n" + preview)
    with TemporaryDirectory(prefix="unit142_r83_close_") as tmp:
        folder = Path(tmp)
        asm = folder / "LEGACY_CLOSE.s"
        obj = folder / "LEGACY_CLOSE.bin"
        asm.write_text(text,encoding="ascii",newline="\n")
        command = [str(vasm.resolve()),"-Fbin","-m68020","-no-opt","-quiet",
                   "-o",str(obj),asm.name]
        result = subprocess.run(command,cwd=folder,text=True,capture_output=True,check=False)
        if result.returncode:
            print("UNIT142_LEGACY_CLOSE_PREVIEW_NOT_ASSEMBLABLE",result.stderr[:1100])
            return
        if obj.read_bytes() != candidate:
            print("UNIT142_LEGACY_CLOSE_PREVIEW_BYTE_DRIFT; no migration")
            return
    print("UNIT142_LEGACY_CLOSE_PREVIEW_VASM_EXACT_PASS",len(candidate))
    if emit_base64:
        print("UNIT142_LEGACY_CLOSE_ASM_B64_BEGIN")
        print(base64.b64encode(text.encode("ascii")).decode("ascii"))
        print("UNIT142_LEGACY_CLOSE_ASM_B64_END")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vasm",required=True,type=Path)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    probe(args.vasm,args.emit_base64)
