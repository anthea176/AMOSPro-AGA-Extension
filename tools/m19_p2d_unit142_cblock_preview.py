#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
# AGA_NATIVE_PURPOSE: AUDIT_ONLY
"""Preview embedded M18 CBlock as MC68020 ASM, without modifying any P2d file.

Proof source: the pinned historical m18_cblock_copy_emit Python emitter,
not a reverse-engineered library. This preview is NOT a production module.
The generated mnemonic candidate is accepted only after direct vasm compares
all its bytes with the exact emitter core.
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
from m18_cblock_copy_emit import emit_cblock_copy_core

ROOT = Path(__file__).resolve().parents[1]
GROUP = 142
GROUP_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"
CBLOCK_SPANS = ((0x0ABC6, 0x0AF3A), (0x0B58A, 0x0B8FE), (0x0BF52, 0x0C2C6))


def check(vasm: Path, emit_base64: bool = False) -> None:
    binary = (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes()
    assert len(binary) == 136020 and sha256(binary).hexdigest() == P2D_SHA
    _tokens, units, _title = unpack_ap20(binary)
    unit = units[GROUP]
    assert len(unit) == 62740 and sha256(unit).hexdigest() == GROUP_SHA
    core, labels = emit_cblock_copy_core()
    expected = b"AGACBLK " + core + b"GetP"
    print("CBLOCK_SOURCE_SIZE", len(core), len(expected), "source-labels", len(labels))
    assert len(expected) == 884, "Historical CBlock source does not match the 884-byte raw envelope"
    for lo, hi in CBLOCK_SPANS:
        assert unit[lo:hi] == expected, f"CBlock emitter mismatch {lo:05X}..{hi:05X}"
    print("UNIT142_TRIPLE_CBLOCK_ORIGIN_PASS", len(core), "bytes", sha256(core).hexdigest())

    preview, coverage = native_unit_source("CBLOCK_CORE", core, [(0, 0)])
    source = "; AGA_NATIVE_MIN_CPU: MC68020\n; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n" + preview
    assert coverage["bytes"] == len(core)
    assert coverage["mnemonic_bytes"] + coverage["raw_dc_bytes"] == len(core)

    with TemporaryDirectory(prefix="unit142_cblock_preview_") as directory:
        folder = Path(directory)
        source_path = folder / "CBLOCK_CORE_PREVIEW.s"
        output = folder / "CBLOCK_CORE_PREVIEW.bin"
        source_path.write_text(source, encoding="ascii", newline="\n")
        command = [str(vasm.resolve()), "-Fbin", "-m68020", "-no-opt",
                   "-quiet", "-o", str(output), source_path.name]
        result = subprocess.run(command, cwd=folder, text=True,
                                capture_output=True, check=False)
        if result.returncode:
            raise AssertionError("CBlock preview is not yet ASM verified: " + result.stderr)
        assert output.read_bytes() == core, "CBlock decoded mnemonic preview differs from emitter"

    print("UNIT142_CBLOCK_PREVIEW_VASM_EXACT_PASS",
          coverage["mnemonic_bytes"], "mnemonic bytes;",
          coverage["raw_dc_bytes"], "raw bytes")
    if emit_base64:
        print("UNIT142_CBLOCK_ASM_B64_BEGIN")
        print(base64.b64encode(source.encode("ascii")).decode("ascii"))
        print("UNIT142_CBLOCK_ASM_B64_END")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vasm", type=Path, required=True)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    check(args.vasm, args.emit_base64)


if __name__ == "__main__":
    main()
