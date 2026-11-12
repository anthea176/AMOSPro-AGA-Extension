#!/usr/bin/env python3
"""M15bis/R44 v0.11.5 reproducible in-memory AMOS AGA mouse cursor candidate.

Only approved private-window CloseWindow sites 0/8/17/18 are replaced
by length-preserving BSR.w into new R44 cleanup hook; R43 Circle gets GetP.
No modification to R43 archive or LAST_GOOD; no new shared-state fields.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m15bis_cursor_r44_emit import emit_cursor, ENTRY_INDEX

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib"
BASE_SHA256 = "9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256 = BASE_SHA256
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"
API = (("aga mouse cursor", ENTRY_INDEX, "00"),)
VERSION = "R44 0.11.5"
GETP = b"GetP"
CLOSE_LVO = bytes.fromhex("4eaeffb8")
BSR_W = bytes.fromhex("6100")
# Source-backed from actual immutable R43 AP20 segmentation.
OWNED_CLOSES = {0: 398, 8: 276, 17: 204, 18: 204}


def starts(parts):
    p = 0
    result = []
    for segment in parts:
        result.append(p)
        p += len(segment)
    return result


def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, "R43 WinUAE-PASS base changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "R43 LAST_GOOD changed"
    tokens, old, _ = split(frozen)
    assert len(old) == ENTRY_INDEX == 54
    assert not old[-1].endswith(GETP)
    audit43 = inspect(parse(frozen))
    assert not audit43["issues"], audit43["issues"]
    assert len([t for t in audit43["tokens"] if t["name"].startswith("aga ")]) == 48

    extension, labels = emit_cursor()
    assert extension[-8:] == bytes(8)
    segments = list(old)
    segments[-1] = old[-1] + GETP
    segments.append(extension)
    positions = starts(segments)
    target = positions[ENTRY_INDEX] + labels["close_window_hook"]
    changes = []
    for index, site in OWNED_CLOSES.items():
        body = bytearray(segments[index])
        assert body.count(CLOSE_LVO) == 1, (index, "unexpected CloseWindow call count")
        assert body[site:site+4] == CLOSE_LVO, (index,site,"R43 site changed")
        assert body[site-2:site] == bytes.fromhex("204b"), (index,"not Window* in A3")
        at = positions[index] + site
        delta = target - (at + 2)
        assert -32768 <= delta <= 32767, (index, delta)
        body[site:site+4] = BSR_W + pack(">h", delta)
        segments[index] = bytes(body)
        changes.append((index, site, delta))
    assert old[40].count(CLOSE_LVO) == 1, "separate Palette Save CloseWindow lost"
    assert segments[40] == old[40], "Palette Save private Window must not be altered"
    assert all(segments[i] == old[i] for i in range(len(old)-1)
               if i not in OWNED_CLOSES), "unexpected old segment changed"
    assert segments[53] == old[53] + GETP

    new_tokens = tokens[:-6] + token(*((API[0][0],1,ENTRY_INDEX,API[0][2]))) + bytes(6)
    title = b"AMOSPro AGA M15bis Mouse Cursor R44 0.11.5\0$VER: AMOSPro_AGA 0.11.5\0"
    if len(title) & 1:
        title += b"\0"
    code = b"".join(segments)
    payload = (pack(">4I",len(segments)*2,len(new_tokens),len(code),len(title))
        + b"\0\0AP20" + b"".join(pack(">H",len(p)//2) for p in segments)
        + new_tokens + code + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    words = pack(">I",len(payload)//4)
    candidate = frozen[:20]+words+frozen[24:28]+words+payload+frozen[-4:]
    assert split(candidate)[:2] == (new_tokens,segments)
    audit44 = inspect(parse(candidate))
    assert not audit44["issues"], audit44["issues"]
    named = [t for t in audit44["tokens"] if t["name"].startswith("aga ")]
    assert len(named) == 49
    found = [t for t in named if t["name"] == API[0][0]]
    assert len(found)==1 and (found[0]["instruction"],found[0]["function"],found[0]["signature"])==(1,ENTRY_INDEX,"00")
    assert any(t["index"]==ENTRY_INDEX and t["parameters"]==1 and t["getp"]
               for t in audit44["parameter_checks"])
    return candidate, dict(version=VERSION,size=len(candidate),sha256=digest(candidate),
        named_commands=49,segments=55,changed_segments=sorted(set(OWNED_CLOSES)|{53,54}),
        window_cleanup_sites=changes, labels=labels, Gate_A="PENDING",
        Gate_B="NOT_TESTED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args = parser.parse_args()
    raw,info=build()
    assert raw==build()[0], "R44 build not deterministic"
    print("M15bis/R44 in-memory candidate:", {k:v for k,v in info.items() if k!="labels"}, flush=True)
    if args.emit_base64:
        print("R44_BASE64_BEGIN",flush=True)
        encoded=base64.b64encode(raw).decode("ascii")
        for i in range(0,len(encoded),76):print(encoded[i:i+76],flush=True)
        print("R44_BASE64_END",flush=True)
