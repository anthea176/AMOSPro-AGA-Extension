#!/usr/bin/env python3
"""R38 0.10.9: deterministic in-memory candidate, never edits LAST_GOOD.

Patches only Screen Close #8 (4-byte BSR hook), Aga Text #36 (R26
regenerated with opt-in font hook), prior GetP #47, and appends one AP20
function #48 + private helpers. All other AP20 routines are preserved.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m11_text_r26_emit import emit_text
from m14_font_select_r37_emit import (
    emit_font_select, ENTRY_FONT_SELECT, ENTRY_SCREEN_CLOSE, ENTRY_TEXT,
    BASE_ENTRIES, CLOSE_SCREEN_CALL_OFFSET, GETP,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225"
LAST_GOOD_SHA256 = "0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M14_v0.10.9_FONT_SELECT_R37.Lib"
API = (("aga font select", ENTRY_FONT_SELECT, "02,0"),)


def starts(segments):
    start, offsets = 0, []
    for part in segments:
        offsets.append(start)
        start += len(part)
    return offsets


def link_bsr(segment, operand, caller, callee):
    """Patch a 68000 BSR.W extension word (PC is its address)."""
    assert segment[operand - 2:operand] == b"\x61\x00", (operand, segment[operand - 2:operand])
    delta = callee - (caller + operand)
    assert -32768 <= delta <= 32767, (caller, callee, delta)
    return segment[:operand] + pack('>h', delta) + segment[operand + 2:]


def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, "R36 archive mutated"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "LAST_GOOD R38 changed"
    token_bytes, original, _ = split(frozen)
    assert len(original) == BASE_ENTRIES == ENTRY_FONT_SELECT == 48
    assert not original[-1].endswith(GETP)
    assert not inspect(parse(frozen))["issues"]
    assert len([x for x in inspect(parse(frozen))["tokens"] if x["name"].startswith("aga ")]) == 42

    original_text, _ = emit_text()
    assert original[ENTRY_TEXT] == original_text + GETP, "R26 text changed in frozen R36"
    upgraded_text, text_labels = emit_text(selected_font=True)
    assert "r37_query_operand" in text_labels
    assert upgraded_text != original_text and upgraded_text.endswith(b"\x74\x00\x4e\x75")

    close = original[ENTRY_SCREEN_CLOSE]
    assert close[CLOSE_SCREEN_CALL_OFFSET:CLOSE_SCREEN_CALL_OFFSET + 4] == bytes.fromhex("4eaeffbe"), "CloseScreen site changed"
    changed_close = bytearray(close)
    changed_close[CLOSE_SCREEN_CALL_OFFSET:CLOSE_SCREEN_CALL_OFFSET + 4] = b"\x61\x00\x00\x00"
    font_code, font_labels = emit_font_select()
    assert font_code[-8:] == bytes(8), "HUNK font state must start cleared"

    updated = list(original)
    updated[ENTRY_TEXT] = upgraded_text + GETP
    updated[ENTRY_SCREEN_CLOSE] = bytes(changed_close)
    updated[-1] += GETP
    updated.append(font_code)
    offsets = starts(updated)
    assert offsets[ENTRY_FONT_SELECT] < 32768
    target_query = offsets[ENTRY_FONT_SELECT] + font_labels["font_query"]
    target_close = offsets[ENTRY_FONT_SELECT] + font_labels["font_close"]

    text_ext = text_labels["r37_query_operand"]
    updated[ENTRY_TEXT] = link_bsr(
        updated[ENTRY_TEXT], text_ext, offsets[ENTRY_TEXT], target_query
    )
    updated[ENTRY_SCREEN_CLOSE] = link_bsr(
        updated[ENTRY_SCREEN_CLOSE], CLOSE_SCREEN_CALL_OFFSET + 2,
        offsets[ENTRY_SCREEN_CLOSE], target_close
    )
    assert all(updated[i] == original[i] for i in range(BASE_ENTRIES)
               if i not in (ENTRY_TEXT, ENTRY_SCREEN_CLOSE, BASE_ENTRIES-1))
    assert updated[ENTRY_SCREEN_CLOSE][:CLOSE_SCREEN_CALL_OFFSET] == close[:CLOSE_SCREEN_CALL_OFFSET]
    assert updated[ENTRY_SCREEN_CLOSE][CLOSE_SCREEN_CALL_OFFSET+4:] == close[CLOSE_SCREEN_CALL_OFFSET+4:]
    assert updated[BASE_ENTRIES-1] == original[-1] + GETP

    new_tokens = token_bytes[:-6] + token(API[0][0], 1, ENTRY_FONT_SELECT, API[0][2]) + bytes(6)
    # token() is given the exact R37 public name, numeric-result function,
    # two parameters (string$, numeric). Do not add public R38/R39 tokens.
    title = b"AMOSPro AGA M14 Font Select R37 0.10.9\0$VER: AMOSPro_AGA 0.10.9\0"
    if len(title) & 1:
        title += b"\0"
    code = b"".join(updated)
    payload = (pack(">4I", len(updated)*2, len(new_tokens), len(code), len(title))
               + b"\0\0AP20" + b"".join(pack(">H", len(s)//2) for s in updated)
               + new_tokens + code + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    words = pack(">I", len(payload)//4)
    candidate = frozen[:20] + words + frozen[24:28] + words + payload + frozen[-4:]
    assert split(candidate)[:2] == (new_tokens, updated)
    audited = inspect(parse(candidate))
    assert audited["issues"] == [], audited["issues"]
    named = [x for x in audited["tokens"] if x["name"].startswith("aga ")]
    assert len(named) == 43
    matches = [x for x in named if x["name"] == API[0][0]]
    assert len(matches) == 1
    assert (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"]) == (1,ENTRY_FONT_SELECT,"02,0")
    assert any(x["index"] == ENTRY_FONT_SELECT and x["parameters"] == 2 and x["getp"]
               for x in audited["parameter_checks"])
    return candidate, {
        "version": "R37 0.10.9", "sha256": digest(candidate), "size": len(candidate),
        "named_commands": len(named), "segments": len(updated),
        "new_token": API[0], "changed_segments": [8,36,47,48],
        "font_labels": font_labels, "text_labels": text_labels,
        "target_query": target_query, "target_close": target_close,
        "Gate_A": "REQUIRES_NATIVE_CPU_CI", "Gate_B": "NOT_TESTED",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    raw, report = build()
    assert raw == build()[0], "R37 candidate not deterministic"
    print("R37 0.10.9 in-memory candidate:", {k:v for k,v in report.items() if not k.endswith("labels")}, flush=True)
    if args.emit_base64:
        print("R37_BASE64_BEGIN", flush=True)
        value = base64.b64encode(raw).decode("ascii")
        for i in range(0,len(value),76):
            print(value[i:i+76], flush=True)
        print("R37_BASE64_END", flush=True)
