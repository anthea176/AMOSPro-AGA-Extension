#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
# AGA_NATIVE_PURPOSE: AUDIT_ONLY
"""Audit-only vasm preview of the historical P0f native stamp/binder.

The exact original M19 P0f emitter supplies all input bytes. The 1,024-byte
stamp table is DATA and excluded from mnemonic coverage. AMOS Main pseudo
operations and any code not proven decodable stay raw; never install a Lib.
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
from m19_p0f_object_identity_emit import emit_object_identity, STAMP_TABLE_BYTES

ROOT = Path(__file__).resolve().parents[1]
UNIT_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"
OFFSET = 0xE7F6


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vasm", required=True, type=Path)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()

    binary = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert len(binary) == 136020 and sha256(binary).hexdigest() == P2D_SHA
    _tokens, parts, _title = unpack_ap20(binary)
    unit = parts[142]
    assert len(unit) == 62740 and sha256(unit).hexdigest() == UNIT_SHA

    original, labels = emit_object_identity()
    core_end = labels["identity_stamp_table"]
    assert core_end == 1198 and len(original) - core_end == STAMP_TABLE_BYTES == 1024
    assert original[core_end:] == bytes(STAMP_TABLE_BYTES)
    assert unit[OFFSET:OFFSET + len(original)] == original
    print("UNIT142_P0F_IDENTITY_EMITTER_EXACT_PASS", hex(OFFSET),
          len(original), "code-and-markers", core_end,
          "zero stamp-table", STAMP_TABLE_BYTES)

    seeds = [(i, labels[name]) for i, name in enumerate((
        "stamp_capture_entry", "stamp_verify_entry",
        "identity_bind_entry", "identity_check_entry", "identity_clear_entry"
    ))]
    source, coverage = native_unit_source("P0F_IDENTITY_CODE", original[:core_end], seeds)
    assert coverage["bytes"] == core_end
    assert coverage["mnemonic_bytes"] + coverage["raw_dc_bytes"] == core_end
    print("UNIT142_P0F_IDENTITY_MNEMONIC_COVERAGE",
          coverage["mnemonic_bytes"], coverage["raw_dc_bytes"],
          "unresolved", coverage["unresolved_instruction_encodings"])
    candidate = ("; AGA_NATIVE_MIN_CPU: MC68020\n"
                 "; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n" + source)

    with TemporaryDirectory(prefix="unit142_p0f_preview_") as tmp:
        folder = Path(tmp)
        input_file = folder / "P0F_IDENTITY_PREVIEW.s"
        output_file = folder / "P0F_IDENTITY_PREVIEW.bin"
        input_file.write_text(candidate, encoding="ascii", newline="\n")
        proc = subprocess.run(
            [str(args.vasm.resolve()), "-Fbin", "-m68020", "-no-opt",
             "-quiet", "-o", output_file.name, input_file.name],
            cwd=folder, capture_output=True, text=True, check=False,
        )
        if proc.returncode:
            print("UNIT142_P0F_IDENTITY_PREVIEW_ASM_INCOMPLETE",
                  proc.stderr[:1000])
            return
        if output_file.read_bytes() != original[:core_end]:
            print("UNIT142_P0F_IDENTITY_PREVIEW_NOT_BYTE_EXACT")
            return

    print("UNIT142_P0F_IDENTITY_PREVIEW_VASM_EXACT_PASS", core_end,
          sha256(original[:core_end]).hexdigest(),
          "raw preserved", coverage["raw_dc_bytes"])
    if args.emit_base64:
        print("UNIT142_P0F_IDENTITY_B64_BEGIN")
        print(base64.b64encode(candidate.encode("ascii")).decode("ascii"))
        print("UNIT142_P0F_IDENTITY_B64_END")


if __name__ == "__main__":
    main()
