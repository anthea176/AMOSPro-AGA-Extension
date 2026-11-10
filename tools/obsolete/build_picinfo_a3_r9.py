#!/usr/bin/env python3
"""R9 0.6.0: fix A3 parameter stack pop in Aga Pic Info only.

AMOS +ILib.s Ent_2 pushes the first argument on A3. PicInfo pops it
with MOVE.L (A3)+,D3, but R8 MOVEM restored A3 on return, undoing the
pop. AMOS's LGoto then treats leaked parameter values as loop frames.
Do not change Double Buffer, Swap, loader, or runtime R8.
"""
from pathlib import Path
from ap20_utils import split, rebuild, digest
from audit_ap20 import parse, inspect

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.9_DB_SYNC_R8.Lib"
BASE_SHA256 = "112dce3e7945a235430a0263e309126061639de0d8dcc0d9c319431b0f2f27a2"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
R9_SHA256 = "58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c"

# 68000 MOVEM masks. Keep the stack symmetric while allowing A3 to advance.
# Predecrement: bit 4 represents A3; postincrement: bit 11 represents A3.
R8_SAVE = bytes.fromhex("48e7effe")
R9_SAVE = bytes.fromhex("48e7efee")
R8_RESTORE = bytes.fromhex("4cdf7ff7")
R9_RESTORE = bytes.fromhex("4cdf77f7")
END_RESTORE_OFFSET = 492


def build():
    base = BASE.read_bytes()
    assert digest(base) == BASE_SHA256, "R8 archive hash mismatch"
    tokens, parts, old_title = split(base)
    assert len(parts) == 19 and len(old_title) == 64
    assert b"Intuition Input R8 0.5.9" in old_title

    info = bytearray(parts[14])
    assert info[:4] == R8_SAVE and info[10:12] == bytes.fromhex("261b")
    assert info[END_RESTORE_OFFSET:END_RESTORE_OFFSET + 4] == R8_RESTORE
    assert info.count(R8_SAVE) == 1
    assert info.count(R8_RESTORE) == 1

    # Mask substitution only: no instruction length, jump or branch changes.
    info[:4] = R9_SAVE
    info[END_RESTORE_OFFSET:END_RESTORE_OFFSET + 4] = R9_RESTORE
    updated = list(parts)
    updated[14] = bytes(info)
    assert [i for i in range(19) if parts[i] != updated[i]] == [14]

    new_title = (b"AMOSPro AGA M5 PicInfo A3 R9 0.6.0\0"
                 b"$VER: AMOSPro_AGA 0.6.0\0").ljust(len(old_title), b"\0")
    output = rebuild(base, updated, new_title)
    assert len(output) == len(base) == 8772
    assert digest(output) == R9_SHA256
    assert inspect(parse(output))["issues"] == []
    out_tokens, out_parts, out_title = split(output)
    assert out_tokens == tokens and out_parts == updated and out_title == new_title

    diff = [i for i, (a, b) in enumerate(zip(base, output)) if a != b]
    assert len(diff) == 50
    report = {
        "version": "0.6.0",
        "source_sha256": BASE_SHA256,
        "sha256": R9_SHA256,
        "size": len(output),
        "changed_ap20_segments": [14],
        "loader_and_double_buffer_byte_identical": True,
        "a3_pop_after_picinfo": 4,
        "r8_archive_preserved": True,
        "active_candidate": "R9 0.6.0",
        "winuae_status": "NOT TESTED",
    }
    return output, report


if __name__ == "__main__":
    result, manifest = build()
    assert build()[0] == result, "Non-deterministic candidate"
    ARCHIVE.write_bytes(result)
    assert ARCHIVE.read_bytes() == result
    # Historical R9: do not overwrite the active R12 or LAST_GOOD R10.
    print("R9 archive only", ARCHIVE.name, manifest)
