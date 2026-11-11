#!/usr/bin/env python3
"""R10 0.6.1: preserve ILBM dimensions, retry unavailable NTSC as PAL.

Only Open AP20 entry 6 changes. A single JSR OpenScreenTagList is
replaced by BSR.W to a same-entry appended helper. No loader/keyboard/DB
changes, and no resampling/clipping. R9 remains the immutable base.

If opening NTSC fails, and the equivalent PAL ModeID is available per
graphics.library/ModeNotAvailable, retry with that PAL monitor ID while
retaining the original logical ModeID in D7 and STATE_MODE. The ILBM
loader checks this logical ModeID against the original image's CAMG.
"""
from pathlib import Path
from struct import pack
from ap20_utils import Asm, split, rebuild, digest
from audit_ap20 import parse, inspect

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib"
BASE_SHA256 = "58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
R10_SHA256 = "e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3"

OPENSCREEN_CALL = bytes.fromhex("4eaefd9c")  # intuition.library -612
MODE_NOT_AVAILABLE = bytes.fromhex("4eaefce2")  # graphics.library -798
OPEN_CALL_OFFSET = 0x116
EXPECTED_OLD_OPEN_SIZE = 656
EXPECTED_HELPER_SIZE = 80


def open_retry_stub():
    """A1=live stack-owned SA_* tags; A4=intuition, A5=graphics, D7=request.

    D2 caches taglist A1 across AmigaOS calls (D2 is OS call-preserved);
    public Open restores its D2=0 result at exit. OpenScreenTagList may
    clobber D0/D1/A0/A1. We recompute D1 after ModeNotAvailable.
    The fourth tag, SA_DisplayID, has its value at 28(A1).
    """
    a = Asm()
    a.label("retry")
    a.emit("2409")              # MOVE.L A1,D2  (save taglist pointer)
    a.emit("4eaefd9c")          # JSR OpenScreenTagList(A6=Intuition)
    a.emit("4a80")              # TST.L D0
    a.branch(0x6600, "done")    # BNE success -> no changes
    a.emit("2207")              # MOVE.L D7,D1 (requested ModeID)
    a.emit("0281ffff0000")      # ANDI.L #$FFFF0000,D1
    a.emit("0c8100010000")      # CMPI.L #NTSC_MONITOR_ID ($10000),D1
    a.branch(0x6600, "done")    # not NTSC -> fail as R9
    a.emit("2207")              # D7 -> D1
    a.emit("068100010000")      # ADDI.L #$00010000,D1 (NTSC->PAL)
    a.emit("2f0e")              # MOVE.L A6,-(SP) preserve IntuitionBase
    a.emit("2c4d")              # MOVEA.L A5,A6 (graphics.library)
    a.emit("2001")              # MOVE.L D1,D0 (PAL ModeID)
    a.emit("4eaefce2")          # JSR ModeNotAvailable(-798,A6)
    a.emit("2c5f")              # MOVEA.L (SP)+,A6 restore IntuitionBase
    a.emit("4a80")              # TST.L D0
    a.branch(0x6600, "failed")  # unavailable PAL: no retry
    a.emit("2207")              # recompute D1 (OS may clobber it)
    a.emit("068100010000")      # ADDI.L #$00010000,D1
    a.emit("2242")              # MOVEA.L D2,A1 (restore original tags)
    a.emit("2341001c")          # MOVE.L D1,28(A1) only SA_DisplayID
    a.emit("4eaefd9c")          # retry with unchanged W/H/depth/colors
    a.label("done")
    a.emit("4e75")              # RTS, D0=Screen* or NULL
    a.label("failed")
    a.emit("70004e75")          # MOVEQ #0,D0 / RTS (never fake success)
    return a.out()


def build():
    r9 = BASE.read_bytes()
    assert digest(r9) == BASE_SHA256, "R9 reference changed"
    tokens, old, title = split(r9)
    assert len(old) == 19 and len(old[6]) == EXPECTED_OLD_OPEN_SIZE
    assert title.startswith(b"AMOSPro AGA M5 PicInfo A3 R9 0.6.0")
    assert old[6].endswith(b"GetP")
    original = old[6]
    assert original.count(OPENSCREEN_CALL) == 1
    assert original[OPEN_CALL_OFFSET:OPEN_CALL_OFFSET + 4] == OPENSCREEN_CALL
    assert original[OPEN_CALL_OFFSET - 4:OPEN_CALL_OFFSET] == bytes.fromhex("224f2c4c")
    assert original[OPEN_CALL_OFFSET + 4:OPEN_CALL_OFFSET + 8] == bytes.fromhex("4fef003c")

    helper = open_retry_stub()
    assert len(helper) == EXPECTED_HELPER_SIZE
    assert helper.count(OPENSCREEN_CALL) == 2
    assert helper.count(MODE_NOT_AVAILABLE) == 1
    target = len(original) - 4  # append BEFORE the AP20 GetP marker
    displacement = target - (OPEN_CALL_OFFSET + 2)
    assert 0 < displacement < 32768
    modified = bytearray(original[:-4])
    modified[OPEN_CALL_OFFSET:OPEN_CALL_OFFSET + 4] = pack(">Hh", 0x6100, displacement)
    modified += helper + b"GetP"
    assert len(modified) == EXPECTED_OLD_OPEN_SIZE + EXPECTED_HELPER_SIZE

    updated = list(old)
    updated[6] = bytes(modified)
    assert [i for i in range(19) if old[i] != updated[i]] == [6]
    assert old[13] == updated[13] and old[14] == updated[14]

    new_title = (b"AMOSPro AGA M5 NTSC-PAL R10 0.6.1\0"
                 b"$VER: AMOSPro_AGA 0.6.1\0").ljust(len(title), b"\0")
    output = rebuild(r9, updated, new_title)
    assert len(output) == 8852
    assert digest(output) == R10_SHA256
    assert inspect(parse(output))["issues"] == []
    result_tokens, result_parts, result_title = split(output)
    assert result_tokens == tokens and result_parts == updated
    assert result_title == new_title
    return output, {
        "version": "0.6.1",
        "size": len(output),
        "sha256": R10_SHA256,
        "source_sha256": BASE_SHA256,
        "changed_ap20_segments": [6],
        "original_modeid_retained_for_ilbm": True,
        "native_ntsc_tried_first": True,
        "pal_retry_only_after_ntsc_open_failure": True,
        "pal_checked_by_ModeNotAvailable": True,
        "no_truncate_or_rescale": True,
        "loader_picinfo_db_swap_keyboard_unchanged": True,
        "winuae_status": "NOT TESTED",
    }


if __name__ == "__main__":
    output, info = build()
    assert build()[0] == output, "Non-deterministic R10"
    ARCHIVE.write_bytes(output)
    assert ARCHIVE.read_bytes() == output
    # R10 is preserved by its immutable archive; LAST_GOOD advances after WinUAE PASS.
    assert ARCHIVE.read_bytes() == output
    print("R10 archive only", info)
