#!/usr/bin/env python3
"""M4b v0.0.6 R4: preserve D3 function return in Double Buffer and Swap.

R3 fixed the AP20 loader. R4 changes only the MOVEM masks of the two
zero-argument functions so D3 is not restored over the function result.
No code size, jump span, token, Cold or title change.
"""
from pathlib import Path
import hashlib
from audit_ap20 import parse, inspect

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist" / "experimental" / "AMOSPro_AGA_M4b_v0.0.6_R3.Lib"
DEST = ROOT / "dist" / "experimental" / "AMOSPro_AGA_M4b_v0.0.6_R4.Lib"

BASE_SHA = "036bd744c57f6206d40c5ab8eb1088dc58fc322b6e108e619b14d4e86a3d8c4b"
R4_SHA = "1f982aea0ffb29112a1a4c8b28d71810bf0e8dad2391da3c95dd6902ca9a2da1"

def build():
    raw = bytearray(BASE.read_bytes())
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA
    lib = parse(raw)
    assert len(lib.jumps) == 14

    code_file = 32 + 22 + lib.lengths[0] + lib.lengths[1]

    for index in (10, 11):
        start = code_file + lib.starts[index]
        end = start + lib.jumps[index] * 2

        # Each function segment ends with the 4-byte GetP dispatcher belonging
        # to the following parameterized entry.
        assert raw[start:start+4] == bytes.fromhex("48e7ffee")
        assert raw[end-12:end-4] == bytes.fromhex("4cdf77ff74004e75")
        assert raw[end-4:end] == b"GetP"

        # MOVEM predecrement/postincrement masks excluding D3.
        raw[start:start+4] = bytes.fromhex("48e7efee")
        raw[end-12:end-8] = bytes.fromhex("4cdf77f7")

    out = bytes(raw)
    assert len(out) == 2136
    assert hashlib.sha256(out).hexdigest() == R4_SHA

    before, after = parse(BASE.read_bytes()), parse(out)
    assert before.tokens == after.tokens
    assert before.jumps == after.jumps
    assert before.title == after.title
    assert before.lengths == after.lengths
    assert inspect(after)["issues"] == []
    return out

if __name__ == "__main__":
    DEST.write_bytes(build())
    print("Generated", DEST)
    print("SHA256", R4_SHA)
