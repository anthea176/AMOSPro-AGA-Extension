"""Build M5 Intuition Input R1 from the promoted Generic ILBM R2 library.

Scope: Intuition RAWKEY input only. Generic ILBM R2/PicInfo segments are
asserted byte-for-byte identical to the promoted base.

Public 68000 contracts
----------------------
Aga Key (entry 17)
  in: none
  out: D3=-1 or raw key-down 0..127, D2=0
  preserves: D0,D1,D4-D7,A0-A6 (A5 untouched)
  modifies: D2,D3,CCR
  stack: balanced

Aga Wait Key (entry 18)
  in: none
  out: D3=raw key-down 0..127 (or -1 if the AGA input context vanished), D2=0
  preserves: D0,D1,D4-D7,A0-A6 (A5 untouched)
  modifies: D2,D3,CCR
  stack: balanced
  wait: cooperative graphics.library/WaitTOF only; never Exec Wait/WaitPort

Internal helpers are local to their AP20 entries; there is no cross-entry BSR.
"""
from pathlib import Path
import hashlib
import json
import struct

from audit_ap20 import parse, inspect as audit, token
from m68k_emit import Code, D, A, M, I, w, l

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.1_GENERIC_R2.Lib"
BASE_SHA = "18fdfd059bd6f15f5a0d42eeb9d628a71ee4110849d8bb781a67db9575f93803"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE_DEST = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.3_INTUITION_INPUT_R2.Lib"
REPORT = ROOT / "docs/INTUITION_INPUT_BUILD.json"

# Shared runtime state. Existing offsets are frozen.
STATE_SCREEN = 0
STATE_INTUITION = 4
STATE_GFX = 8
STATE_WIDTH = 12
STATE_HEIGHT = 16
STATE_COLORS = 20
STATE_MODE = 24
STATE_DEPTH = 28
STATE_DB = 32
STATE_WINDOW = 36
STATE_SIZE = 40
AMOS_STATE_PTR = 0x01C8

# NDK/AMOS constants, source-backed in AOZ-Studio/AMOS-Professional-Official.
IDCMP_RAWKEY = 0x00000400
IECODE_UP_PREFIX = 0x0080
IEQUALIFIER_CONTROL = 0x0008
RAWKEY_C = 0x0033
CUSTOMSCREEN = 0x000F
WINDOW_FLAGS = 0x00021900  # BACKDROP|BORDERLESS|ACTIVATE|NOCAREREFRESH
WINDOW_USERPORT = 86
IM_CLASS = 20
IM_CODE = 24
IM_QUALIFIER = 26

# AMOS graphics work area. +WEqu.s: BitControl=8, T_Actualise=-168(a5).
T_ACTUALISE = -168
BITCONTROL_WORD = 0x0100

# Library vectors.
LVO_CLOSESCREEN = -66
LVO_CLOSEWINDOW = -72
LVO_OPENWINDOW = -204
LVO_WAITTOF = -270
LVO_GETMSG = -372
LVO_REPLYMSG = -378
LVO_CLOSELIBRARY = -414
LVO_DELETEPORT = -672
LVO_FREEVEC = -690
LVO_FREESCREENBUFFER = -774
LVO_WAITBLIT = -228

EXEC_WAIT = bytes.fromhex("4eaefec2")      # jsr -318(a6)
EXEC_WAITPORT = bytes.fromhex("4eaefe80")  # jsr -384(a6)
GFX_WAITTOF = bytes.fromhex("4eaefef2")    # jsr -270(a6)
EXEC_GETMSG = bytes.fromhex("4eaefe8c")
EXEC_REPLYMSG = bytes.fromhex("4eaefe86")

REGISTER_CONTRACTS = {
    "Aga Key": {
        "inputs": "none",
        "outputs": "D3=-1 or raw key-down 0..127; D2=0",
        "preserved": "D0,D1,D4-D7,A0-A6 (A5 untouched)",
        "modified": "D2,D3,CCR",
        "stack": "balanced",
    },
    "Aga Wait Key": {
        "inputs": "none",
        "outputs": "D3=raw key-down 0..127; D2=0; -1 only if AGA input context vanished",
        "preserved": "D0,D1,D4-D7,A0-A6 (A5 untouched)",
        "modified": "D2,D3,CCR",
        "stack": "balanced",
    },
    "OpenWindow helper": {
        "inputs": "A2=runtime state; D7=ModeID",
        "outputs": "D3=1 success / 0 failure",
        "modified": "D3,CCR; all other D/A registers restored locally",
        "stack": "balanced; 48-byte NewWindow is stack-owned",
    },
    "CloseWindow helper": {
        "inputs": "A2=runtime state",
        "outputs": "none",
        "modified": "D0,A0,A1,A3,A4,A6,CCR (caller owns preservation)",
        "stack": "balanced",
    },
}


def s16(data, offset):
    return struct.unpack_from(">h", data, offset)[0]


def patch_once(buf, before, after):
    assert len(before) == len(after)
    assert bytes(buf).count(before) == 1, before.hex()
    pos = bytes(buf).index(before)
    assert not (pos & 1), pos
    buf[pos:pos + len(before)] = after
    return pos


def branch_word(opcode, source, target):
    """68000 word-displacement branch. PC base is the extension word."""
    disp = target - (source + 2)
    assert -32768 <= disp <= 32767
    return struct.pack(">Hh", opcode, disp)


def close_window_helper():
    """A2=state. Drain GetMsg/ReplyMsg exactly once, then CloseWindow."""
    c = Code()
    c.move(M(2, STATE_WINDOW), A(3))
    c.move(A(3), D(0))
    c.tst(D(0))
    c.branch(7, "done")
    c.move(M(3, WINDOW_USERPORT), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "close")
    c.label("drain")
    c.move(A(4), A(0))
    c.raw("2c780004")
    c.call_os(LVO_GETMSG)
    c.tst(D(0))
    c.branch(7, "close")
    c.move(D(0), A(1))
    c.call_os(LVO_REPLYMSG)
    c.branch(0, "drain")
    c.label("close")
    c.move(M(2, STATE_INTUITION), A(6))
    c.move(A(6), D(0))
    c.tst(D(0))
    c.branch(7, "clear")
    c.move(A(3), A(0))
    c.call_os(LVO_CLOSEWINDOW)
    c.label("clear")
    c.move(I(0), M(2, STATE_WINDOW))
    c.label("done")
    c.raw("4e75")
    return c.out()



def ctrl_c_cleanup_helper():
    """A2=state. Full nonblocking AGA teardown before handing Break to AMOS.

    Order:
      1. drain/reply IDCMP and CloseWindow;
      2. free DB ScreenBuffers/MsgPorts/DBState if present;
      3. CloseScreen;
      4. close graphics.library and intuition.library;
      5. zero the whole shared state.

    Caller preserves the public ABI registers around this helper.
    """
    c = Code()

    # Window first: no Intuition message may survive the screen.
    c.move(M(2, STATE_WINDOW), A(3))
    c.move(A(3), D(0))
    c.tst(D(0))
    c.branch(7, "db")
    c.move(M(3, WINDOW_USERPORT), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "close_window")
    c.label("drain_window")
    c.move(A(4), A(0))
    c.raw("2c780004")
    c.call_os(LVO_GETMSG)
    c.tst(D(0))
    c.branch(7, "close_window")
    c.move(D(0), A(1))
    c.call_os(LVO_REPLYMSG)
    c.branch(0, "drain_window")
    c.label("close_window")
    c.move(M(2, STATE_INTUITION), A(6))
    c.move(A(6), D(0))
    c.tst(D(0))
    c.branch(7, "clear_window")
    c.move(A(3), A(0))
    c.call_os(LVO_CLOSEWINDOW)
    c.label("clear_window")
    c.move(I(0), M(2, STATE_WINDOW))

    # Validated nonblocking DB teardown derived from R6B-R4.
    c.label("db")
    c.move(M(2, STATE_DB), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "close_screen")

    c.move(M(2, STATE_GFX), A(6))
    c.move(A(6), D(0))
    c.tst(D(0))
    c.branch(7, "free_sbs")
    c.call_os(LVO_WAITBLIT)

    c.label("free_sbs")
    c.move(M(2, STATE_SCREEN), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "delete_ports")
    c.move(M(2, STATE_INTUITION), A(6))

    c.move(M(4, 4), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "skip_sb1")
    c.call_os(LVO_FREESCREENBUFFER)
    c.label("skip_sb1")

    c.move(M(4, 0), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "delete_ports")
    c.move(M(2, STATE_SCREEN), A(0))
    c.call_os(LVO_FREESCREENBUFFER)

    c.label("delete_ports")
    c.raw("2c780004")
    c.move(M(4, 16), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "skip_disp")
    c.call_os(LVO_DELETEPORT)
    c.label("skip_disp")
    c.move(M(4, 12), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "free_db")
    c.call_os(LVO_DELETEPORT)

    c.label("free_db")
    c.move(A(4), A(1))
    c.raw("2c780004")
    c.call_os(LVO_FREEVEC)
    c.move(I(0), M(2, STATE_DB))

    c.label("close_screen")
    c.move(M(2, STATE_SCREEN), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "close_gfx")
    c.move(M(2, STATE_INTUITION), A(6))
    c.call_os(LVO_CLOSESCREEN)
    c.move(I(0), M(2, STATE_SCREEN))

    c.label("close_gfx")
    c.move(M(2, STATE_GFX), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "close_intuition")
    c.raw("2c780004")
    c.call_os(LVO_CLOSELIBRARY)
    c.move(I(0), M(2, STATE_GFX))

    c.label("close_intuition")
    c.move(M(2, STATE_INTUITION), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "clear_state")
    c.raw("2c780004")
    c.call_os(LVO_CLOSELIBRARY)
    c.move(I(0), M(2, STATE_INTUITION))

    c.label("clear_state")
    c.raw("7000")
    for off in range(0, STATE_SIZE, 4):
        c.move(D(0), M(2, off))
    c.raw("4e75")
    return c.out()


def open_window_helper():
    """A2=state, D7=ModeID. Open a borderless active RAWKEY Window."""
    c = Code()
    # The replaced caller sequence used to store ModeID here.
    c.move(D(7), M(2, STATE_MODE))
    # Preserve everything except D3, the public result register.
    c.raw("48e7effe")  # MOVEM.L D0-D2/D4-D7/A0-A6,-(SP)
    c.raw("4fefffd0")  # LEA -48(SP),SP : struct NewWindow
    c.raw("7000")      # MOVEQ #0,D0
    for off in range(0, 48, 4):
        c.move(D(0), M(7, off))
    # Runtime dimensions are LONGs; load the full value, then store NewWindow WORDs.
    c.move(M(2, STATE_WIDTH), D(0))
    c.move(D(0), M(7, 4), "w")
    c.move(M(2, STATE_HEIGHT), D(0))
    c.move(D(0), M(7, 6), "w")
    c.move(I(IDCMP_RAWKEY), M(7, 10))
    c.move(I(WINDOW_FLAGS), M(7, 14))
    c.move(M(2, STATE_SCREEN), D(0))
    c.move(D(0), M(7, 30))
    c.move(I(CUSTOMSCREEN, "w"), M(7, 46), "w")
    c.move(A(7), A(0))
    c.move(M(2, STATE_INTUITION), A(6))
    c.call_os(LVO_OPENWINDOW)
    c.move(D(0), D(1))
    c.raw("4fef0030")  # LEA 48(SP),SP
    c.tst(D(1))
    c.branch(7, "failure")
    c.move(D(1), M(2, STATE_WINDOW))
    c.raw("7601")      # MOVEQ #1,D3
    c.branch(0, "finish")

    c.label("failure")
    # Screen is already open at this point. Close it before the libraries.
    c.move(M(2, STATE_SCREEN), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "close_gfx")
    c.move(M(2, STATE_INTUITION), A(6))
    c.call_os(LVO_CLOSESCREEN)
    c.label("close_gfx")
    c.move(M(2, STATE_GFX), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "close_intuition")
    c.raw("2c780004")
    c.call_os(LVO_CLOSELIBRARY)
    c.label("close_intuition")
    c.move(M(2, STATE_INTUITION), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "clear_state")
    c.raw("2c780004")
    c.call_os(LVO_CLOSELIBRARY)
    c.label("clear_state")
    c.raw("7000")
    for off in range(0, STATE_SIZE, 4):
        c.move(D(0), M(2, off))
    c.raw("7600")      # MOVEQ #0,D3

    c.label("finish")
    c.raw("4cdf7ff7")  # MOVEM.L (SP)+,D0-D2/D4-D7/A0-A6
    c.raw("4e75")
    return c.out()


def input_routine(wait):
    """Emit one self-contained public AP20 entry; no cross-entry calls."""
    c = Code()
    c.raw("48e7cffa")  # save D0,D1,D4-D7,A0-A4,A6
    c.raw("76ff")      # D3=-1
    c.move(M(5, AMOS_STATE_PTR), A(2))
    c.move(A(2), D(0))
    c.tst(D(0))
    c.branch(7, "finish")
    c.move(M(2, STATE_WINDOW), A(3))
    c.move(A(3), D(0))
    c.tst(D(0))
    c.branch(7, "finish")
    c.move(M(3, WINDOW_USERPORT), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "finish")

    c.label("poll")
    c.move(A(4), A(0))
    c.raw("2c780004")
    c.call_os(LVO_GETMSG)
    c.tst(D(0))
    c.branch(7, "no_message")
    c.move(D(0), A(3))
    c.move(M(3, IM_CLASS), D(4))
    c.raw("7a00")
    c.move(M(3, IM_CODE), D(5), "w")
    c.raw("7c00")
    c.move(M(3, IM_QUALIFIER), D(6), "w")
    c.move(A(3), A(1))
    c.call_os(LVO_REPLYMSG)

    # Only RAWKEY key-down is externally visible.
    c.imm("cmp", IDCMP_RAWKEY, D(4))
    c.branch(6, "poll")
    c.move(D(5), D(0))
    c.imm("and", IECODE_UP_PREFIX, D(0))
    c.branch(6, "poll")

    # Native AMOS Ctrl+C propagation. Do not emulate a private Ctrl state:
    # IntuiMessage.Qualifier is authoritative. AMOS later applies BREAK ON/OFF.
    c.imm("cmp", RAWKEY_C, D(5))
    c.branch(6, "return_key")
    c.move(D(6), D(0))
    c.imm("and", IEQUALIFIER_CONTROL, D(0))
    c.branch(7, "return_key")

    # Ctrl+C must not strand the Intuition screen. Tear down AGA resources
    # first, then hand the native Break bit back to AMOS.
    c.branch(0, "ctrl_cleanup")
    c.label("after_ctrl_cleanup")
    c.imm("or", BITCONTROL_WORD, M(5, T_ACTUALISE), "w")
    c.branch(0, "return_key")

    c.label("ctrl_cleanup")
    cleanup_start = len(c.b)
    c.raw(ctrl_c_cleanup_helper().hex())
    # The helper ends in RTS; replace it with a branch back into this entry
    # so this remains a single self-contained AP20 routine.
    assert c.b[-2:] == bytes.fromhex("4e75")
    del c.b[-2:]
    c.branch(0, "after_ctrl_cleanup")

    c.label("return_key")
    c.move(D(5), D(3))
    c.branch(0, "finish")

    c.label("no_message")
    if wait:
        c.move(M(2, STATE_GFX), A(6))
        c.move(A(6), D(0))
        c.tst(D(0))
        c.branch(7, "finish")
        c.call_os(LVO_WAITTOF)
        c.branch(0, "poll")

    c.label("finish")
    c.raw("4cdf5ff3")  # restore D0,D1,D4-D7,A0-A4,A6
    c.raw("7400")      # ABI: D2=0
    c.raw("4e75")
    result = c.out()
    assert EXEC_WAIT not in result
    assert EXEC_WAITPORT not in result
    assert EXEC_GETMSG in result and EXEC_REPLYMSG in result
    if wait:
        assert GFX_WAITTOF in result
    else:
        assert GFX_WAITTOF not in result
    return result


def patch_init(old):
    assert old[-36:] == bytes(36)
    assert 12 + s16(old, 12) == len(old) - 36
    assert 32 + s16(old, 32) == len(old) - 36
    body = bytearray(old[:-36])
    patch_once(body, bytes.fromhex("7007429851c8fffc"),
               bytes.fromhex("7009429851c8fffc"))
    helper = close_window_helper()
    pos = bytes(body).index(bytes.fromhex("42aa0020"))
    assert bytes(body).count(bytes.fromhex("42aa0020")) == 1
    target = len(body)
    body[pos:pos + 4] = branch_word(0x6100, pos, target)
    state_start = len(body) + len(helper)
    struct.pack_into(">h", body, 12, state_start - 12)
    struct.pack_into(">h", body, 32, state_start - 32)
    result = bytes(body) + helper + bytes(STATE_SIZE)
    assert 12 + s16(result, 12) == len(result) - STATE_SIZE
    assert 32 + s16(result, 32) == len(result) - STATE_SIZE
    return result


def patch_open(old):
    assert old[-4:] == b"GetP"
    body = bytearray(old[:-4])
    before = bytes.fromhex("2547001876016000001a")
    assert bytes(body).count(before) == 1
    pos = bytes(body).index(before)
    old_done = pos + 8 + s16(body, pos + 8)
    helper = open_window_helper()
    target = len(body)
    replacement = (branch_word(0x6100, pos, target)
                   + branch_word(0x6000, pos + 4, old_done)
                   + bytes.fromhex("4e71"))
    assert len(replacement) == len(before)
    body[pos:pos + len(before)] = replacement
    return bytes(body) + helper + b"GetP"


def patch_close(old):
    assert old[-4:] == b"GetP"
    body = bytearray(old[:-4])
    needle = bytes.fromhex("42aa0020")
    assert bytes(body).count(needle) == 1
    pos = bytes(body).index(needle)
    helper = close_window_helper()
    target = len(body)
    body[pos:pos + 4] = branch_word(0x6100, pos, target)
    return bytes(body) + helper + b"GetP"


def build():
    raw = BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA
    base = parse(raw)
    assert not audit(base)["issues"]
    segments = [base.code[s:s + 2*n] for s, n in zip(base.starts, base.jumps)]
    original = segments.copy()
    assert len(segments) == 17

    segments[0] = patch_init(segments[0])
    segments[6] = patch_open(segments[6])
    segments[8] = patch_close(segments[8])
    segments.append(input_routine(False))
    segments.append(input_routine(True))

    # Generic ILBM R2 and PicInfo are frozen byte-for-byte.
    assert segments[13] == original[13]
    assert segments[14] == original[14]
    for i in list(range(1, 6)) + [7] + list(range(9, 17)):
        assert segments[i] == original[i], i

    assert base.tokens.endswith(bytes(6))
    tokens = (base.tokens[:-6]
              + token("aga key", 1, 17, "0")
              + token("aga wait key", 1, 18, "0")
              + bytes(6))
    jumps = [len(s)//2 for s in segments]
    assert all(len(s) % 2 == 0 for s in segments)
    code = b"".join(segments)
    title = (b"AMOSPro AGA M5 Intuition Input R2 0.5.3\0"
             b"$VER: AMOSPro_AGA 0.5.3\0")
    if len(title) & 1:
        title += b"\0"

    payload = bytearray(
        l(len(jumps)*2) + l(len(tokens)) + l(len(code)) + l(len(title))
        + b"\0\0AP20" + b"".join(w(n) for n in jumps)
        + tokens + code + title + b"\0\0"
    )
    while len(payload) & 3:
        payload.append(0)
    count = len(payload)//4
    result = raw[:20] + l(count) + raw[24:28] + l(count) + payload + raw[-4:]

    out = parse(result)
    audited = audit(out)
    assert audited["issues"] == []
    assert out.tokens == tokens
    assert tuple(out.jumps) == tuple(jumps)
    assert out.code == code

    out_segments = [out.code[s:s + 2*n] for s, n in zip(out.starts, out.jumps)]
    ilbm_proof = {}
    for index, name in ((13, "Generic ILBM R2"), (14, "PicInfo")):
        before_sha = hashlib.sha256(original[index]).hexdigest()
        after_sha = hashlib.sha256(out_segments[index]).hexdigest()
        assert before_sha == after_sha
        ilbm_proof[name] = {
            "segment": index,
            "base_sha256": before_sha,
            "candidate_sha256": after_sha,
            "byte_for_byte_identical": True,
        }

    report = {
        "base": str(BASE.relative_to(ROOT)),
        "base_sha256": BASE_SHA,
        "sha256": hashlib.sha256(result).hexdigest(),
        "size": len(result),
        "version": "0.5.3",
        "state_offsets": {
            "Screen*": STATE_SCREEN,
            "IntuitionBase": STATE_INTUITION,
            "GfxBase": STATE_GFX,
            "width": STATE_WIDTH,
            "height": STATE_HEIGHT,
            "colors": STATE_COLORS,
            "ModeID": STATE_MODE,
            "depth": STATE_DEPTH,
            "DBState*": STATE_DB,
            "Window*": STATE_WINDOW,
            "size": STATE_SIZE,
        },
        "commands": {
            "Aga Key": 17,
            "Aga Wait Key": 18,
        },
        "modified_existing_segments": [0, 6, 8],
        "new_segments": [17, 18],
        "generic_ilbm_integrity": ilbm_proof,
        "forbidden_waits": {
            "Exec Wait": False,
            "WaitPort": False,
            "Aga Wait Key uses WaitTOF": True,
        },
        "ctrl_c": {
            "rawkey_c": RAWKEY_C,
            "qualifier_control": IEQUALIFIER_CONTROL,
            "amos_T_Actualise_offset": T_ACTUALISE,
            "amos_BitControl": 8,
            "propagation": "full AGA teardown, then set native AMOS BitControl in T_Actualise; AMOS applies BREAK ON/OFF",
            "runtime_validation": "REQUIRED",
        },
        "register_contracts": REGISTER_CONTRACTS,
        "ap20_issues": audited["issues"],
    }
    return result, report


if __name__ == "__main__":
    result, report = build()
    result2, report2 = build()
    assert result2 == result and report2 == report
    DEST.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(result)
    ARCHIVE_DEST.write_bytes(result)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(DEST.name, len(result), report["sha256"])
