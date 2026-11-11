#!/usr/bin/env python3
"""R23 0.8.7: event-driven mouse edges and a shared RAWKEY dispatcher.

Pure HUNK/AP20 builder from the immutable, WinUAE-tested R22 archive.
An IDCMP message is replied ONCE in the common 68000 pump. Key down
messages are held in a 16-item FIFO for the original Aga Key/Wait Key
parser (and its Ctrl+C Break path). There is no WaitPort or Exec Wait.
This candidate must pass native CPU CI and WinUAE before any PASS claim.
"""
import argparse
import base64
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from m8_idcmp_r23_emit import (
    emit_dispatcher, emit_mouse_reader, STATE_BYTES,
    MAX_MESSAGES_PER_CALL, KEY_CAP,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M8_v0.8.6_MOUSE_EDGES_R22.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "96e38d478bd97e7a65801e16e96ce08c0bbd4aaacb4a8a6644e4bc1289a0c997"
LAST_GOOD_SHA256 = "0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41"
GETP = b"GetP"
STATE_ANCHOR = 0x1A0
KEY_STUB = 0x30
KEY_REPLY = 0x4E
NEW_WINDOW_IDCMP = 0x1E6
ENTRY_SCREEN_OPEN = 6
ENTRY_KEY = 17
ENTRY_WAIT_KEY = 18
ENTRY_PRESSED = 31
ENTRY_RELEASED = 32
ENTRY_DISPATCH = 33


def w(x):
    return pack(">h", x)


def u16(x):
    return pack(">H", x)


def patch_bsr(routine, ext_pos, from_start, target):
    # PC-relative BSR.w displacement is relative to its 16-bit ext word.
    off = target - (from_start + ext_pos)
    assert -32768 <= off < 32768, (ext_pos, from_start, target)
    assert routine[ext_pos-2:ext_pos] == b"\x61\x00"
    return routine[:ext_pos] + w(off) + routine[ext_pos+2:]


def patch_key(routine):
    assert len(routine) > KEY_REPLY + 4  # No GetP required for zero-arg functions
    b = bytearray(routine)
    assert b[KEY_STUB:KEY_STUB+4] == bytes.fromhex("4eaefe8c"), "GetMsg changed"
    assert b[KEY_REPLY:KEY_REPLY+4] == bytes.fromhex("4eaefe86"), "ReplyMsg changed"
    b[KEY_STUB:KEY_STUB+4] = bytes.fromhex("61000000")
    # Synthetic, already-replied IntuiMessage: no double ReplyMsg.
    b[KEY_REPLY:KEY_REPLY+4] = bytes.fromhex("4e714e71")
    return bytes(b)


def patch_screen_open(entry, state_delta):
    assert entry.endswith(GETP)
    data = bytearray(entry)
    assert data[NEW_WINDOW_IDCMP:NEW_WINDOW_IDCMP+8] == bytes.fromhex(
        "2f7c00000400000a"
    ), "Window IDCMPFlags changed from R22"
    # RAWKEY | MOUSEBUTTONS | ACTIVEWINDOW | INACTIVEWINDOW
    data[NEW_WINDOW_IDCMP:NEW_WINDOW_IDCMP+8] = bytes.fromhex(
        "2f7c000c0408000a"
    )
    helper_pos = len(entry) - len(GETP) - 18
    old = data[helper_pos:helper_pos+18]
    assert old[:2] == bytes.fromhex("6100")
    assert old[4:6] == bytes.fromhex("41ea")
    assert old[8:16] == bytes.fromhex("4298429842984298")
    assert old[16:18] == bytes.fromhex("4e75")
    assert 0 < state_delta < 32767
    # BSR original R22 init; LEA eventState(A2),A0;
    # MOVEQ #35,D0; CLR.L (A0)+; DBRA D0,-4 ; RTS.
    # Exact 18-byte replacement, no relocation of earlier code.
    new = bytes(old[:4]) + bytes.fromhex("41ea") + u16(state_delta) + bytes.fromhex(
        "7023429851c8fffc4e75"
    )
    assert len(new) == 18
    data[helper_pos:helper_pos+18] = new
    assert bytes(data[0x1EE:0x1F6]) == entry[0x1EE:0x1F6], "RMBTRAP changed"
    return bytes(data)


def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, "R22 PASS archive modified"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    token_bytes, before, _ = split(frozen)
    assert len(before) == 33
    assert before[ENTRY_KEY][KEY_STUB:KEY_STUB+4] == bytes.fromhex("4eaefe8c")
    assert before[ENTRY_WAIT_KEY][KEY_STUB:KEY_STUB+4] == bytes.fromhex("4eaefe8c")
    assert before[ENTRY_RELEASED][-2:] == b"\x00\x00"  # old data tail
    assert before[ENTRY_PRESSED].endswith(GETP)

    # Program size and all external-call locations are fixed independent
    # of state_delta, so emit a first pass to determine absolute position.
    p, pext = emit_mouse_reader("pressed", 1)
    r, rext = emit_mouse_reader("released", 1)
    dispatcher, labels = emit_dispatcher(1)
    parts = list(before)
    parts[ENTRY_PRESSED] = p + GETP
    parts[ENTRY_RELEASED] = r + GETP
    parts.append(dispatcher)
    assert len(parts) == 34
    starts, run = [], 0
    for part in parts:
        starts.append(run)
        run += len(part)
    state_delta = starts[ENTRY_DISPATCH] + labels["runtime_state"] - STATE_ANCHOR
    assert 0 < state_delta < 32767
    p, pext2 = emit_mouse_reader("pressed", state_delta)
    r, rext2 = emit_mouse_reader("released", state_delta)
    dispatcher, labels2 = emit_dispatcher(state_delta)
    assert (pext, rext) == (pext2, rext2)
    assert labels == labels2
    assert len(parts[ENTRY_PRESSED]) == len(p) + len(GETP)
    assert len(parts[ENTRY_RELEASED]) == len(r) + len(GETP)
    assert len(parts[ENTRY_DISPATCH]) == len(dispatcher)
    parts[ENTRY_SCREEN_OPEN] = patch_screen_open(parts[ENTRY_SCREEN_OPEN], state_delta)
    parts[ENTRY_KEY] = patch_key(parts[ENTRY_KEY])
    parts[ENTRY_WAIT_KEY] = patch_key(parts[ENTRY_WAIT_KEY])
    parts[ENTRY_PRESSED] = p + GETP
    parts[ENTRY_RELEASED] = r + GETP
    parts[ENTRY_DISPATCH] = dispatcher
    for index, ext in ((ENTRY_PRESSED, pext), (ENTRY_RELEASED, rext)):
        parts[index] = patch_bsr(parts[index], ext, starts[index],
                                 starts[ENTRY_DISPATCH] + labels["pump"])
    for index in (ENTRY_KEY, ENTRY_WAIT_KEY):
        parts[index] = patch_bsr(parts[index], KEY_STUB+2, starts[index],
                                 starts[ENTRY_DISPATCH] + labels["key_next"])
    assert [i for i in range(33) if before[i] != parts[i]] == [6, 17, 18, 31, 32]
    assert all(len(part) % 2 == 0 for part in parts)
    assert parts[ENTRY_DISPATCH][-STATE_BYTES:] == bytes(STATE_BYTES)
    assert token_bytes.endswith(bytes(6)), "AP20 token terminator changed"
    assert token_bytes == split(frozen)[0], "No new API name in R23"
    title = b"AMOSPro AGA M8 IDCMP Mouse R23 0.8.7\0$VER: AMOSPro_AGA 0.8.7\0"
    if len(title) & 1:
        title += b"\0"
    code = b"".join(parts)
    payload = (pack(">4I", 2*len(parts), len(token_bytes), len(code), len(title))
               + b"\0\0AP20"
               + b"".join(pack(">H", len(part)//2) for part in parts)
               + token_bytes + code + title + b"\0\0")
    payload += bytes((-len(payload)) % 4)
    size = pack(">I", len(payload)//4)
    candidate = frozen[:20] + size + frozen[24:28] + size + payload + frozen[-4:]
    audit = inspect(parse(candidate))
    assert not audit["issues"], audit["issues"]
    tok2, after, _ = split(candidate)
    assert tok2 == token_bytes and after == parts
    assert build_info_safety(after, labels, state_delta)
    return candidate, {
        "release": "R23 0.8.7",
        "bytes": len(candidate),
        "sha256": digest(candidate),
        "state_delta": state_delta,
        "statesize": STATE_BYTES,
        "keys": KEY_CAP,
        "bounded_messages_per_call": MAX_MESSAGES_PER_CALL,
        "code_length": len(code),
        "dispatch_length": len(dispatcher),
        "runtime": "NOT_TESTED"
    }


def build_info_safety(parts, labels, state_delta):
    # Word displacement and shared-state size are checked by the emitter.
    # The screen-open trampoline resets exactly STATE_BYTES of private data.
    assert STATE_BYTES == 144
    assert labels["runtime_state"] + STATE_BYTES == len(parts[ENTRY_DISPATCH])
    assert parts[ENTRY_SCREEN_OPEN][-4:] == GETP
    assert parts[ENTRY_KEY][KEY_REPLY:KEY_REPLY+4] == bytes.fromhex("4e714e71")
    assert parts[ENTRY_WAIT_KEY][KEY_REPLY:KEY_REPLY+4] == bytes.fromhex("4e714e71")
    assert parts[ENTRY_SCREEN_OPEN][NEW_WINDOW_IDCMP:NEW_WINDOW_IDCMP+8] == bytes.fromhex(
        "2f7c000c0408000a"
    )
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true",
                        help="Print candidate as base64 for audited GitHub blob handoff")
    args = parser.parse_args()
    candidate, report = build()
    assert build()[0] == candidate, "R23 must be reproducible"
    print("R23 IDCMP preflight candidate; no files overwritten:", report, flush=True)
    if args.emit_base64:
        print("R23_BASE64_BEGIN", flush=True)
        print(base64.b64encode(candidate).decode("ascii"), flush=True)
        print("R23_BASE64_END", flush=True)
