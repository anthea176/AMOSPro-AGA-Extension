#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
# AGA_NATIVE_PURPOSE: AUDIT_ONLY
"""Read-only provenance/vasm preview for the P1c/P1d suffix of UNIT142."""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from active_library import P2D_SHA
from build_m19_p1c_bob_priority_in_memory import build_p1c
from build_m19_p1d_limit_bob_in_memory import build_p1d
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import unpack_ap20
from generate_aga_multiunit_source import native_unit_source
from m19_p1c_bob_priority_emit import emit_priority_open
from m19_p1d_limit_bob_emit import TABLE_BYTES, emit_limit_open

ROOT = Path(__file__).resolve().parents[1]
UNIT_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"


def check(vasm: Path, dump: bool = False) -> None:
    official = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert len(official) == 136020 and sha256(official).hexdigest() == P2D_SHA
    _t, units, _title = unpack_ap20(official)
    unit = units[142]
    assert len(unit) == 62740 and sha256(unit).hexdigest() == UNIT_SHA

    p1c, cmeta = build_p1c()
    p1d, dmeta = build_p1d()
    _t, cp, _title = unpack_ap20(p1c)
    _t, dp, _title = unpack_ap20(p1d)
    assert dp[142] == unit, "P1d group differs from official P2d group"
    assert cp[142] == unit[:len(cp[142])], "P1c group prefix not preserved"

    origin = len(DISPATCH_V2) + cmeta["open_offset"]
    priority, context = emit_priority_open(1102, cmeta["open_offset"])
    assert origin == 0x0F0A4 and len(priority) == 46
    assert cp[142][origin:] == priority and unit[origin:origin+46] == priority
    assert context + len(DISPATCH_V2) == 0x0F0CA and priority[-8:] == bytes(8)
    print("UNIT142_P1C_SOURCE_EXACT_PASS",hex(origin),len(priority),
          "code",len(priority)-8,"state",8)

    table_start = len(cp[142])
    limit = emit_limit_open(cmeta["open_offset"], table_start-len(DISPATCH_V2))
    assert table_start == 0x0F0D2 and TABLE_BYTES == 1040
    assert len(limit) == 1090 and limit[:TABLE_BYTES] == bytes(TABLE_BYTES)
    assert unit[table_start:] == limit
    assert dmeta["open_offset"] == table_start-len(DISPATCH_V2)+TABLE_BYTES
    print("UNIT142_P1D_SOURCE_EXACT_PASS",hex(table_start),len(limit),
          "data",TABLE_BYTES,"code",len(limit)-TABLE_BYTES)

    for name, code in (("P1C_PRIORITY_OPEN",priority[:-8]),
                       ("P1D_LIMIT_OPEN",limit[TABLE_BYTES:])):
        preview, report = native_unit_source(name, code, [(0,0)])
        assert report["bytes"] == len(code)
        assert report["mnemonic_bytes"] + report["raw_dc_bytes"] == len(code)
        print("UNIT142_"+name+"_COVERAGE",
              report["mnemonic_bytes"], report["raw_dc_bytes"])
        text = "; AGA_NATIVE_MIN_CPU: MC68020\n; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n" + preview
        with TemporaryDirectory(prefix="unit142_p1cd_") as temp:
            folder = Path(temp)
            asm = folder / (name+".s")
            obj = folder / (name+".bin")
            asm.write_text(text, encoding="ascii", newline="\n")
            cmd = [str(vasm.resolve()),"-Fbin","-m68020","-no-opt","-quiet",
                   "-o",str(obj),asm.name]
            run = subprocess.run(cmd,cwd=folder,text=True,capture_output=True,check=False)
            if run.returncode:
                raise AssertionError(name+" vasm preview failed: "+run.stderr)
            assert obj.read_bytes() == code, name+" bytes differ from historical emitter"
        print("UNIT142_"+name+"_VASM_EXACT_PASS",len(code),sha256(code).hexdigest())
        if dump:
            print("UNIT142_"+name+"_ASM_B64_BEGIN")
            print(base64.b64encode(text.encode("ascii")).decode("ascii"))
            print("UNIT142_"+name+"_ASM_B64_END")


    # The first genuine 68020 JSR uses a full (d32,PC) extension, which the
    # conservative decoder does not trace. Preserve those eight bytes as
    # source-emitted data and start the trace at the next instruction only.
    for name, complete, start in (
        ("P1C_PRIORITY_SPLIT", priority, 8),
        ("P1D_LIMIT_SPLIT", limit, TABLE_BYTES + 8),
    ):
        source, report = native_unit_source(name, complete, [(0, start)])
        assert report["bytes"] == len(complete)
        assert report["mnemonic_bytes"] + report["raw_dc_bytes"] == len(complete)
        assert report["mnemonic_bytes"] > 0, name+" failed to decode code after full-extension JSR"
        print("UNIT142_"+name+"_COVERAGE", report["mnemonic_bytes"],
              "mnemonics", report["raw_dc_bytes"], "raw including data")
        text = "; AGA_NATIVE_MIN_CPU: MC68020\n; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n" + source
        with TemporaryDirectory(prefix="unit142_"+name+"_") as temp:
            folder=Path(temp)
            asm=folder/(name+".s")
            output=folder/(name+".bin")
            asm.write_text(text, encoding="ascii", newline="\n")
            cmd=[str(vasm.resolve()),"-Fbin","-m68020","-no-opt","-quiet",
                 "-o",str(output),asm.name]
            result=subprocess.run(cmd,cwd=folder,text=True,capture_output=True,check=False)
            if result.returncode:
                raise AssertionError(name+" vasm split failed: "+result.stderr)
            assert output.read_bytes() == complete, name+" split source differs"
        print("UNIT142_"+name+"_VASM_SPLIT_EXACT_PASS",
              len(complete), sha256(complete).hexdigest())
        if dump:
            print("UNIT142_"+name+"_ASM_B64_BEGIN")
            print(base64.b64encode(text.encode("ascii")).decode("ascii"))
            print("UNIT142_"+name+"_ASM_B64_END")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vasm",required=True,type=Path)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    check(args.vasm,args.emit_base64)
