#!/usr/bin/env python3
"""REJECTED R11 0.6.2: preserve historical candidate for static diagnostics.

R10 opens Jeff by retrying NTSC CAMG as physical PAL without cropping.
R11 changes ONLY the second OpenScreenTagList call within that existing
fallback: BSR.W into a 44-byte local helper that performs the same open,
then ScreenToFront and a conditional MoveScreen(-TopEdge). Native PAL
and NTSC paths are byte-for-byte unchanged from R10. No loader changes.
"""
from pathlib import Path
from struct import pack
from ap20_utils import Asm, split, rebuild, digest
from audit_ap20 import parse, inspect

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib"
BASE_SHA256 = "e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.6.2_JEFF_POSITION_R11.Lib"
R11_SHA256 = "0e2419965f411c4e9419b1c7c8d07debdde525f13f7b8da80e2ed9d3ee30ea7b"
RETRY_CALL = bytes.fromhex("4eaefd9c")   # OpenScreenTagList -612(A6)
PRESENT_CALL = bytes.fromhex("61000008") # BSR.W from offset 722 to 732
RETRY_CALL_OFFSET = 722
R10_OPEN_SIZE = 736
HELPER_SIZE = 44


def fallback_position_helper():
    """Called with A6=intuition, A4=IntuitionBase, D0=Screen* or zero.

    The helper calls OpenScreenTagList exactly once. If successful it
    saves the pointer, calls ScreenToFront(-252), and if Screen.TopEdge
    (+10) is positive calls MoveScreen(-162) with dx=0, dy=-TopEdge.
    AmigaOS can clobber D0/D1/A0/A1. The original Screen* is restored
    from CPU stack into D0 before returning to the existing Open code.
    """
    a = Asm()
    a.emit("4eaefd9c")         # JSR -612(A6) OpenScreenTagList, same as R10
    a.emit("4a80")             # TST.L D0
    a.branch(0x6700, "done")   # no Screen -> no positioning, D0 stays 0
    a.emit("2f00")             # MOVE.L D0,-(SP)
    a.emit("2040")             # MOVEA.L D0,A0, Screen*
    a.emit("2c4c")             # MOVEA.L A4,A6 IntuitionBase
    a.emit("4eaeff04")         # JSR -252(A6) ScreenToFront(Screen)
    a.emit("2057")             # MOVEA.L (SP),A0 recover Screen*
    a.emit("3228000a")         # MOVE.W 10(A0),D1, signed Screen.TopEdge
    a.emit("4a41")             # TST.W D1
    a.branch(0x6f00, "restore") # BLE.W: keep zero or negative TopEdge
    a.emit("4441")             # NEG.W D1 => dy=-TopEdge
    a.emit("7000")             # MOVEQ #0,D0 => dx=0
    a.emit("4eaeff5e")         # JSR -162(A6) MoveScreen(Screen,0,-TopEdge)
    a.label("restore")
    a.emit("201f")             # MOVE.L (SP)+,D0 recover public Screen*
    a.label("done")
    a.emit("4e75")             # RTS
    result = a.out()
    assert len(result) == HELPER_SIZE
    assert result.hex() == (
        "4eaefd9c4a80670000222f0020402c4c4eaeff0420573228000a"
        "4a416f00000a444170004eaeff5e201f4e75")
    return result


def build():
    r10 = BASE.read_bytes()
    assert digest(r10) == BASE_SHA256, "R10 reference changed"
    tokens, segments, title = split(r10)
    assert len(segments) == 19 and len(segments[6]) == R10_OPEN_SIZE
    assert title.startswith(b"AMOSPro AGA M5 NTSC-PAL R10 0.6.1")
    original = segments[6]
    assert original[-4:] == b"GetP"
    assert original[RETRY_CALL_OFFSET:RETRY_CALL_OFFSET + 10] == bytes.fromhex(
        "4eaefd9c4e7570004e75")
    assert original[RETRY_CALL_OFFSET - 4:RETRY_CALL_OFFSET] == bytes.fromhex("2341001c")

    helper = fallback_position_helper()
    start = len(original) - 4
    displacement = start - (RETRY_CALL_OFFSET + 2)
    assert displacement == 8
    modified = bytearray(original[:-4])
    modified[RETRY_CALL_OFFSET:RETRY_CALL_OFFSET + 4] = pack(
        ">Hh", 0x6100, displacement)
    modified += helper + b"GetP"

    updated = list(segments)
    updated[6] = bytes(modified)
    assert [i for i in range(19) if segments[i] != updated[i]] == [6]
    assert all(updated[i] == segments[i] for i in range(19) if i != 6)

    new_title = (b"AMOSPro AGA M5 POS R11 0.6.2\0"
                 b"$VER: AMOSPro_AGA 0.6.2\0").ljust(len(title), b"\0")
    out = rebuild(r10, updated, new_title)
    assert len(out) == 8896
    assert digest(out) == R11_SHA256
    assert inspect(parse(out))["issues"] == []
    toks2, parts2, title2 = split(out)
    assert toks2 == tokens and parts2 == updated and title2 == new_title
    return out, {
        "version": "0.6.2", "size": len(out), "sha256": R11_SHA256,
        "source_sha256": BASE_SHA256, "changed_ap20_segments": [6],
        "helper_bytes": HELPER_SIZE,
        "only_successful_ntsc_pal_retry_is_positioned": True,
        "native_screen_open_path_unchanged": True,
        "loader_picinfo_db_swap_keyboard_unchanged": True,
        "last_good_untouched": True,
        "runtime_status": "REJECTED_GREY_SCREEN_WINUAE"
    }


if __name__ == "__main__":
    result, report = build()
    assert build()[0] == result, "Non-deterministic R11"
    ARCHIVE.write_bytes(result)
    assert ARCHIVE.read_bytes() == result
    # R11 failed WinUAE (grey screen). Never overwrite the active R10.
    assert (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes() == BASE.read_bytes(), "Protected R10 changed"
    print("R11 rejected candidate archived only", report)
