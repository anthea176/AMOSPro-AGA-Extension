#!/usr/bin/env python3
"""M15/R40 v0.11.1 deterministic in-memory Plot candidate (not LAST_GOOD).

Base: immutable R38 WinUAE-PASS archive only. Append one AP20 numeric function,
leave previous R38 code/data exactly intact apart from final GetP delimiter.
Does not write DEST or LAST_GOOD; R40 was promoted after user-confirmed Gate B.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m15_plot_r40_emit import emit_plot, ENTRY_INDEX

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib"
BASE_SHA256 = "09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256 = "9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib"
GETP = b"GetP"
API = (("aga plot", ENTRY_INDEX, "00,0,0"),)
VERSION = "R40 0.11.1"


def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, "immutable R38 archive changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "R40 LAST_GOOD changed"
    old_tokens, old_segments, _ = split(frozen)
    assert len(old_segments) == ENTRY_INDEX == 50
    assert not old_segments[-1].endswith(GETP)
    assert old_segments[-1].endswith(bytes(8)), "R38 private font state modified"
    audit38 = inspect(parse(frozen))
    assert not audit38["issues"], audit38["issues"]
    assert len([x for x in audit38["tokens"] if x["name"].startswith("aga ")]) == 44
    code, labels = emit_plot()
    assert code.endswith(bytes.fromhex("4cdf77f774004e75"))

    parts = list(old_segments)
    parts[-1] = old_segments[-1] + GETP
    parts.append(code)
    assert parts[:-2] == old_segments[:-1]  # every other entry byte-identical
    assert parts[-2][-12:-4] == bytes(8)     # R38 private state retained
    assert parts[-2].endswith(GETP)

    new_tokens = old_tokens[:-6] + token(API[0][0], 1, ENTRY_INDEX, API[0][2]) + bytes(6)
    title = b"AMOSPro AGA M15 Plot R40 0.11.1\0$VER: AMOSPro_AGA 0.11.1\0"
    if len(title) & 1:
        title += b"\0"
    code_bytes = b"".join(parts)
    payload = (pack(">4I", len(parts)*2, len(new_tokens), len(code_bytes), len(title))
               + b"\0\0AP20"
               + b"".join(pack(">H", len(p)//2) for p in parts)
               + new_tokens + code_bytes + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    words = pack(">I", len(payload)//4)
    candidate = frozen[:20] + words + frozen[24:28] + words + payload + frozen[-4:]
    assert split(candidate)[:2] == (new_tokens, parts)
    audit = inspect(parse(candidate))
    assert not audit["issues"], audit["issues"]
    named = [x for x in audit["tokens"] if x["name"].startswith("aga ")]
    assert len(named) == 45
    got = [x for x in named if x["name"] == API[0][0]]
    assert len(got) == 1
    assert (got[0]["instruction"], got[0]["function"], got[0]["signature"]) == (1, ENTRY_INDEX, "00,0,0")
    assert any(c["index"] == ENTRY_INDEX and c["parameters"] == 3 and c["getp"]
               for c in audit["parameter_checks"])
    return candidate, dict(version=VERSION, sha256=digest(candidate),
        size=len(candidate), named_commands=45, segments=51,
        new_command=API[0], changed_segments=[49, 50],
        plot_labels=labels, Gate_A="CPU_CI_PASS", Gate_B="USER_WINUAE_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    binary, info = build()
    assert binary == build()[0], "R40 builder non-deterministic"
    print("R40 in-memory candidate:", {k: v for k, v in info.items()
                                      if k != "plot_labels"}, flush=True)
    if args.emit_base64:
        print("R40_BASE64_BEGIN", flush=True)
        encoded = base64.b64encode(binary).decode("ascii")
        for i in range(0, len(encoded), 76):
            print(encoded[i:i+76], flush=True)
        print("R40_BASE64_END", flush=True)
