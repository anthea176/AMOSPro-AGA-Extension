#!/usr/bin/env python3
"""HISTORICAL INCOMPLETE R44/R45 AP20 CloseWindow experiment (NOT FOR PRODUCTION).

Only four legacy CloseWindow branches are repaired; remaining cross-segment
calls make this unsuitable for future versions. Use compiler_relocation.py and
build_aga_current.py for the official user-validated R46 C1 bridge.

Only emits in memory by default. R44 / R45 baselines are SHA256 pinned.
No canonical library, archive or LAST_GOOD is rewritten.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from struct import pack, unpack_from

from ap20_utils import digest, split
from audit_ap20 import parse, inspect
from m15bis_cursor_r44_emit import emit_cursor
from build_m15bis_cursor_r44 import OWNED_CLOSES

ROOT = Path(__file__).resolve().parents[1]
BASELINES = {
    "r44": (
        ROOT / "dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib",
        "0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc",
        55,
    ),
    "r45": (
        ROOT / "dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib",
        "0d780b4648214c36e8f291d9575390462d174cd8ba22cac2188324b75bd220d7",
        56,
    ),
}
CURSOR = 54
RBSR_OPCODE = b"\xfe\x31"  # AMOS Compiler Rbsr index (CEqu.s)
STATE_GETTER = bytes.fromhex("45fa00044e750000000000000000")


def rbsr(index: int) -> bytes:
    assert 0 < index < 65536
    return RBSR_OPCODE + pack(">H", index)


def offset_of_cursor_state_lea(cursor: bytes, state_offset: int, close_offset: int) -> int:
    """Only matches LEA d16(PC),A2 whose effective target is the known state."""
    locations = []
    for pos in range(0, close_offset, 2):
        if cursor[pos:pos + 2] != b"\x45\xfa":
            continue
        disp = unpack_from(">h", cursor, pos + 2)[0]
        if pos + 2 + disp == state_offset:
            locations.append(pos)
    assert len(locations) == 1, locations
    return locations[0]


def rebuild_with_added_entries(base: bytes, tokens: bytes, parts: list[bytes], title: bytes) -> bytes:
    assert all(len(part) % 2 == 0 and 0 < len(part) <= 131070 for part in parts)
    code = b"".join(parts)
    payload = (pack(">4I", len(parts) * 2, len(tokens), len(code), len(title))
        + b"\0\0AP20" + b"".join(pack(">H", len(part) // 2) for part in parts)
        + tokens + code + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    words = pack(">I", len(payload) // 4)
    candidate = base[:20] + words + base[24:28] + words + payload + base[-4:]
    assert split(candidate) == (tokens, parts, title)
    return candidate


def patch(base: bytes, target: str) -> tuple[bytes, dict]:
    assert target in BASELINES
    _, expected_digest, expected_count = BASELINES[target]
    assert digest(base) == expected_digest, f"{target} source SHA256 mismatch"
    tokens, old, title = split(base)
    assert len(old) == expected_count
    orig_cursor, labels = emit_cursor()
    assert old[CURSOR] == orig_cursor + (b"GetP" if target == "r45" else b"")
    state_index = len(old)
    close_index = state_index + 1
    close_pos = labels["close_window_hook"]
    state_pos = labels["cursor_state"]
    assert orig_cursor[state_pos:] == b"\0" * 8

    cursor_lea = offset_of_cursor_state_lea(orig_cursor, state_pos, close_pos)
    parts = list(old)
    updated_cursor = bytearray(parts[CURSOR])
    updated_cursor[cursor_lea:cursor_lea+4] = rbsr(state_index)
    parts[CURSOR] = bytes(updated_cursor)

    # Original close hook saves every D/A register and uses A4 for state.
    # Replace its LEA A4,state with Rbsr STATE_GETTER (returns A2), then
    # MOVEA.L A2,A4. The inserted 2-byte move precedes every local branch,
    # so displacements among the remaining instructions stay unchanged.
    hook = orig_cursor[close_pos:state_pos]
    assert hook[:6] == bytes.fromhex("48e7fffe2648")
    assert hook[6:8] == b"\x49\xfa"
    old_delta = unpack_from(">h", hook, 8)[0]
    assert close_pos + 8 + old_delta == state_pos
    close_hook = hook[:6] + rbsr(state_index) + bytes.fromhex("284a") + hook[10:]
    assert len(close_hook) == len(hook) + 2
    assert close_hook[-6:] == bytes.fromhex("4cdf7fff4e75")

    starts = [sum(len(p) for p in old[:i]) for i in range(len(old))]
    for segment, pos in OWNED_CLOSES.items():
        content = bytearray(parts[segment])
        opcode, disp = content[pos:pos+2], unpack_from(">h", content, pos+2)[0]
        assert opcode == b"\x61\x00", (segment, pos, opcode)
        expected = starts[CURSOR] + close_pos
        assert starts[segment] + pos + 2 + disp == expected
        content[pos:pos+4] = rbsr(close_index)
        parts[segment] = bytes(content)

    parts.extend((STATE_GETTER, close_hook))
    binary = rebuild_with_added_entries(base, tokens, parts, title)
    before, after = inspect(parse(base)), inspect(parse(binary))
    assert not before["issues"] and not after["issues"]
    assert before["tokens"] == after["tokens"] and before["parameter_checks"] == after["parameter_checks"]
    assert all(parts[i] == old[i] for i in range(len(old)) if i not in (*OWNED_CLOSES, CURSOR))
    assert parts[state_index] == STATE_GETTER and parts[close_index] == close_hook
    return binary, dict(target=target, state_index=state_index, close_index=close_index,
                        cursor_lea=cursor_lea, close_sites=dict(OWNED_CLOSES),
                        source_sha256=expected_digest, candidate_sha256=digest(binary),
                        size=len(binary), entries=len(parts), tokens=len(after["tokens"]))


def build(target: str) -> tuple[bytes, dict]:
    path, expected, _ = BASELINES[target]
    raw = path.read_bytes()
    assert digest(raw) == expected
    return patch(raw, target)


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--target", choices=tuple(BASELINES), default="r44")
    cli.add_argument("--output", type=Path, default=None,
                     help="explicit experimental destination; default is in-memory only")
    args = cli.parse_args()
    binary, metadata = build(args.target)
    assert build(args.target)[0] == binary, "not deterministic"
    print(metadata)
    if args.output is not None:
        assert args.output.name.startswith("AMOSPro_AGA_COMPILER_GATE_C_")
        assert args.output.parent.resolve() == (ROOT / "dist/experimental").resolve()
        assert not args.output.exists(), "never overwrite a pre-existing candidate"
        args.output.write_bytes(binary)
        print("Wrote experimental candidate:", args.output)


if __name__ == "__main__":
    main()
