#!/usr/bin/env python3
"""M6 R15 0.7.2: Aga Blit Clear(x,y,w,h), reuse R14 Fill with pen 0.

The sole functional delta is a four-parameter AMOS adapter for the validated
five-parameter Fill entry. R14 entries 0..19 are byte-for-byte unchanged,
entry 20 only gains the mandatory GetP delimiter, and entry 21 is new.
Always build from the immutable R14 experimental archive, not the live Lib.
R13, R14 and LAST_GOOD archives must never be overwritten.
"""
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m68k_emit import Code, D, A, M, PRE, POST, I

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "a8c43c478efdb2ddcb3547a807a2dba60bd125fc0d7ab5bb791ef565aeb90e4f"
LAST_GOOD_SHA256 = "0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41"
VERSION = "0.7.2"
ENTRY = 21
FILL_ENTRY = 20
DELIMITER = b"GetP"


def emit_clear(fill_code_length):
    """Aga Blit Clear(x,y,w,h) -> 1/0; no new graphics.library code.

    AMOS passes h in D3, with w,y,x in successive longs from A3.
    Prepare a temporary [h,w,y,x] stack at A7 and call the EXISTING
    R14 Fill entry with pen D3=0. Fill consumes four scratch longs,
    but the AMOS argument pointer A3 must ultimately advance by 12 bytes.
    The wrapper therefore restores original A3 and adds 12 after the call.

    No original D0/D1/D4-D7/A0-A2/A4-A6 values are overwritten, D2=0
    and D3=result are returned by Fill; the CPU stack is balanced.
    Fill already validates all BitMap pointers, bounds, depth and DMA.
    """
    assert 0 < fill_code_length <= 32700 and fill_code_length % 2 == 0
    c = Code()
    c.move(A(3), PRE(7))           # save original AMOS argument pointer
    c.move(M(3, 8), PRE(7))        # x
    c.move(M(3, 4), PRE(7))        # y
    c.move(M(3, 0), PRE(7))        # width
    c.move(D(3), PRE(7))          # height -> [SP]=h,w,y,x
    c.move(A(7), A(3))            # temporary A3 points to 4 scratch longs
    c.move(I(0), D(3))            # pen=0, reuse validated R14 Fill

    call_at = len(c.b)
    c.word(0x6100)                # BSR.W from entry 21 back to entry 20
    # Branch displacement is relative to the extension word address.
    displacement = -(fill_code_length + len(DELIMITER) + call_at + 2)
    assert -32768 <= displacement <= -1
    c.word(displacement)

    c.quick(8, A(7))              # discard scratch h,w
    c.quick(8, A(7))              # discard scratch y,x
    c.move(POST(7), A(3))         # restore caller AMOS argument pointer
    c.quick(8, A(3))              # skip 2 AMOS longs
    c.quick(4, A(3))              # skip final AMOS long: A3 += 12
    c.raw("4e75")                # RTS, D2/D3 returned by validated Fill

    code = c.out()
    assert len(code) % 2 == 0
    return code, {"call_at": call_at, "bsr_displacement": displacement,
                  "fill_size": fill_code_length, "code_size": len(code)}


def build():
    base = BASE.read_bytes()
    assert digest(base) == BASE_SHA256, "R14 archive missing or changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "LAST_GOOD changed"
    tokens, old, _ = split(base)
    assert len(old) == 21 and tokens.endswith(bytes(6))
    assert old[FILL_ENTRY][-2:] == bytes.fromhex("4e75")

    clear, details = emit_clear(len(old[FILL_ENTRY]))
    new = list(old)
    new[FILL_ENTRY] += DELIMITER
    new.append(clear)
    assert new[:FILL_ENTRY] == old[:FILL_ENTRY]
    assert new[FILL_ENTRY] == old[FILL_ENTRY] + DELIMITER

    new_tokens = (tokens[:-6] + token("aga blit clear", 1, ENTRY,
                                      "00,0,0,0") + bytes(6))
    title = (b"AMOSPro AGA M6 Blit Clear R15 0.7.2\0"
             b"$VER: AMOSPro_AGA 0.7.2\0")
    if len(title) % 2: title += b"\0"
    code = b"".join(new)
    payload = (pack(">4I", len(new) * 2, len(new_tokens),
                    len(code), len(title))
               + b"\0\0AP20"
               + b"".join(pack(">H", len(s) // 2) for s in new)
               + new_tokens + code + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    words = len(payload) // 4
    result = (base[:20] + pack(">I", words) + base[24:28]
              + pack(">I", words) + payload + base[-4:])

    audit = inspect(parse(result))
    assert not audit["issues"], audit["issues"]
    matches = [r for r in audit["tokens"] if r["name"] == "aga blit clear"]
    assert len(matches) == 1
    assert (matches[0]["function"], matches[0]["signature"]) == (
        ENTRY, "00,0,0,0")
    assert any(x["index"] == ENTRY and x["getp"]
               for x in audit["parameter_checks"])
    parsed_tokens, parsed_parts, _ = split(result)
    assert parsed_tokens == new_tokens and parsed_parts == new
    return result, {"version": VERSION, "entry": ENTRY,
                    "size": len(result), "sha256": digest(result),
                    "runtime_validation": "NOT_TESTED", **details}


if __name__ == "__main__":
    assert len({p.resolve() for p in (BASE, DEST, ARCHIVE, LAST_GOOD)}) == 4
    candidate, info = build()
    assert build()[0] == candidate, "R15 builder not reproducible"
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(candidate)
    DEST.write_bytes(candidate)
    assert ARCHIVE.read_bytes() == DEST.read_bytes() == candidate
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print("M6 R15 Clear candidate, WinUAE NOT TESTED:", info)
