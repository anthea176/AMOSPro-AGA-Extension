#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
# AGA_NATIVE_PURPOSE: AUDIT_ONLY
"""Check provenance and vasm preview for the private P0e AGA object table.

Audit only: does not modify binary candidates, source, or AMOS tests.
The historical emitter, not the decoded official binary, is the source.
The compiler's AP20/CPU checks remain independent of this static probe.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from active_library import P2D_SHA, P2DL2B_SHA, frozen_p2d
from compiler_relocation import unpack_ap20
from generate_aga_multiunit_source import native_unit_source
from m19_p0e_object_table_emit import (
    MAX_OBJECTS, ROOT_BYTES, SLOT_BYTES, emit_object_table,
)
from m19_p0e_split_bridge_emit import AGA_CORE
from m19_p0f_bank_stamp_emit import emit_bank_stamp
from m19_p0f_object_identity_emit import emit_object_identity

ROOT = Path(__file__).resolve().parents[1]
GROUP_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"
TAIL_START = 0xDD04


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vasm", required=True, type=Path)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()

    protected = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(protected).hexdigest() in (P2D_SHA,P2DL2B_SHA)
    official = frozen_p2d(protected)
    assert len(official) == 136020
    assert sha256(official).hexdigest() == P2D_SHA
    _tokens, parts, _title = unpack_ap20(official)
    unit = parts[142]
    assert len(unit) == 62740 and sha256(unit).hexdigest() == GROUP_SHA
    assert unit[0xDCFC:TAIL_START] == b"AGAPIC  "

    original, labels = emit_object_table()
    assert len(original) == 2332
    assert labels["object_put_entry"] == 0
    assert labels["object_table"] == labels["object_root"] + ROOT_BYTES
    assert len(original) - labels["object_root"] == ROOT_BYTES + MAX_OBJECTS * SLOT_BYTES
    assert original[labels["object_root"]:] == bytes(ROOT_BYTES + MAX_OBJECTS * SLOT_BYTES)
    assert unit[TAIL_START:TAIL_START + len(original)] == original
    print("UNIT142_P0E_OBJECT_SOURCE_EXACT_PASS",
          hex(TAIL_START), len(original), labels["object_root"])

    bridge_at = TAIL_START + len(original)
    assert len(AGA_CORE) == 470
    assert unit[bridge_at:bridge_at + len(AGA_CORE)] == AGA_CORE
    print("UNIT142_P0E_AGA_BRIDGE_SOURCE_EXACT_PASS",
          hex(bridge_at), len(AGA_CORE))

    stamp, _stamp_labels = emit_bank_stamp()
    stamp_at = bridge_at + len(AGA_CORE)
    assert unit[stamp_at:stamp_at + len(stamp)] == stamp
    print("UNIT142_P0F_BANK_STAMP_SOURCE_EXACT_PASS",
          hex(stamp_at), len(stamp))

    identity, identity_labels = emit_object_identity()
    assert identity.startswith(stamp)
    binder = identity[len(stamp):]
    binder_at = stamp_at + len(stamp)
    assert unit[binder_at:binder_at + len(binder)] == binder
    print("UNIT142_P0F_BINDER_SOURCE_EXACT_PASS",
          hex(binder_at), len(binder),
          "end", hex(binder_at + len(binder)),
          "stamp-table", identity_labels["identity_stamp_table"])

    executable = original[:labels["object_root"]]
    entries = [
        (index, labels[name])
        for index, name in enumerate((
            "object_put_entry", "object_off_entry",
            "object_read_entry", "object_reset_entry",
        ))
    ]
    preview, coverage = native_unit_source("P0E_OBJECT_CODE", executable, entries)
    assert coverage["bytes"] == len(executable)
    assert coverage["mnemonic_bytes"] + coverage["raw_dc_bytes"] == len(executable)
    print("UNIT142_P0E_OBJECT_CODE_COVERAGE",
          coverage["mnemonic_bytes"], coverage["raw_dc_bytes"])
    assert coverage["raw_dc_bytes"] == 0, "Unverified object-code opcodes remain"

    candidate = ("; AGA_NATIVE_MIN_CPU: MC68020\n"
                 "; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n" + preview)
    with TemporaryDirectory(prefix="unit142_p0e_preview_") as temporary:
        folder = Path(temporary)
        input_file = folder / "P0E_OBJECT_PREVIEW.s"
        output_file = folder / "P0E_OBJECT_PREVIEW.bin"
        input_file.write_text(candidate, encoding="ascii", newline="\n")
        cmd = [str(args.vasm.resolve()), "-Fbin", "-m68020", "-no-opt",
               "-quiet", "-o", str(output_file), input_file.name]
        proc = subprocess.run(cmd, cwd=folder, text=True, capture_output=True, check=False)
        if proc.returncode:
            raise AssertionError("P0e vasm preview failed: " + proc.stderr)
        assert output_file.read_bytes() == executable, "P0e vasm code is not byte-exact"
    print("UNIT142_P0E_OBJECT_PREVIEW_VASM_EXACT_PASS",
          len(executable), sha256(executable).hexdigest())
    if args.emit_base64:
        print("UNIT142_P0E_ASM_B64_BEGIN")
        print(base64.b64encode(candidate.encode("ascii")).decode("ascii"))
        print("UNIT142_P0E_ASM_B64_END")


if __name__ == "__main__":
    main()
