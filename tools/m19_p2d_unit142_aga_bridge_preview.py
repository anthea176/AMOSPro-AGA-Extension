#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
# AGA_NATIVE_PURPOSE: AUDIT_ONLY
"""Source-backed direct-vasm preview of 470-byte P0e AGA object bridge.

This check is not a native source promotion and does not modify any Lib.
The historical M19 P0e emitter supplies the bytes and actual entrypoints.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from active_library import P2D_SHA
from compiler_relocation import unpack_ap20
from generate_aga_multiunit_source import native_unit_source
from m19_p0e_split_bridge_emit import AGA_CORE, AGA_OFFSETS

ROOT = Path(__file__).resolve().parents[1]
UNIT142_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"
BRIDGE_START = 0x0E620
BRIDGE_END = 0x0E7F6


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vasm", type=Path, required=True)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()

    official = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert len(official) == 136020 and sha256(official).hexdigest() == P2D_SHA
    _tokens, units, _title = unpack_ap20(official)
    unit = units[142]
    assert len(unit) == 62740 and sha256(unit).hexdigest() == UNIT142_SHA
    assert len(AGA_CORE) == BRIDGE_END - BRIDGE_START == 470
    assert unit[BRIDGE_START:BRIDGE_END] == AGA_CORE
    assert all(v % 2 == 0 and 0 <= v < len(AGA_CORE) for v in AGA_OFFSETS.values())
    print("UNIT142_P0E_AGA_BRIDGE_EMITTER_EXACT_PASS",
          hex(BRIDGE_START), len(AGA_CORE), sha256(AGA_CORE).hexdigest())
    entries = [(i, AGA_OFFSETS[name]) for i, name in enumerate(("put", "off", "read", "reset"))]
    source, coverage = native_unit_source("P0E_AGA_BRIDGE", AGA_CORE, entries)
    assert coverage["bytes"] == len(AGA_CORE)
    assert coverage["mnemonic_bytes"] + coverage["raw_dc_bytes"] == 470
    print("UNIT142_P0E_AGA_BRIDGE_MNEMONIC_COVERAGE",
          coverage["mnemonic_bytes"], coverage["raw_dc_bytes"])
    if coverage["raw_dc_bytes"]:
        print("UNIT142_P0E_AGA_BRIDGE_INCOMPLETE: no raw bytes promoted as executable")
        return

    candidate = ("; AGA_NATIVE_MIN_CPU: MC68020\n"
                 "; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n" + source)
    with TemporaryDirectory(prefix="unit142_p0e_bridge_") as temporary:
        folder = Path(temporary)
        src = folder / "P0E_AGA_BRIDGE_PREVIEW.s"
        out = folder / "P0E_AGA_BRIDGE_PREVIEW.bin"
        src.write_text(candidate, encoding="ascii", newline="\n")
        cmd = [str(args.vasm.resolve()), "-Fbin", "-m68020", "-no-opt",
               "-quiet", "-o", out.name, src.name]
        result = subprocess.run(cmd, cwd=folder, capture_output=True,
                                text=True, check=False)
        if result.returncode != 0:
            print("UNIT142_P0E_AGA_BRIDGE_ASM_INCOMPLETE", result.stderr[:1000])
            return
        if out.read_bytes() != AGA_CORE:
            print("UNIT142_P0E_AGA_BRIDGE_ASM_MISMATCH: no module promoted")
            return
    print("UNIT142_P0E_AGA_BRIDGE_PREVIEW_VASM_EXACT_PASS",
          len(AGA_CORE), sha256(AGA_CORE).hexdigest())
    if args.emit_base64:
        print("UNIT142_P0E_AGA_BRIDGE_B64_BEGIN")
        print(base64.b64encode(candidate.encode("ascii")).decode("ascii"))
        print("UNIT142_P0E_AGA_BRIDGE_B64_END")


if __name__ == "__main__":
    main()
