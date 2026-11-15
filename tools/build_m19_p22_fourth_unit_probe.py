#!/usr/bin/env python3
"""M19 P2.2: experimental FOURTH AP20 native unit on pinned R84 (no Batch yet).

Prove an independent BOBS native unit is reachable in interpreted and
compiler-V2 routing. The ONLY new public function is Aga Bob Probe(), a
disposable infrastructure witness returning 1. It DOES NOT render anything.

Never modifies dist/ or LAST_GOOD. Optional binary output is restricted to
build/m19-p22/AMOSPro_AGA_M19_P22_4UNIT_PROBE.Lib for test installation.
R84 76-command public ABI and all three original native unit bytes remain
identical. Compiler Gate C and WinUAE Gate B require real AMOS validation.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "experiments"))

from active_library import R84_SHA
from audit_ap20 import inspect, parse, token
from compiler_relocation import unpack_ap20, repack_ap20, RBSR, GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements

PROTECTED = ROOT / "dist" / "AMOSPro_AGA_LAST_GOOD.Lib"
ACTIVE = ROOT / "dist" / "AMOSPro_AGA.Lib"
PROBE_OUTPUT = ROOT / "build" / "m19-p22" / "AMOSPro_AGA_M19_P22_4UNIT_PROBE.Lib"
PROBE_CODE = bytes.fromhex("760174004e75")  # MOVEQ #1,D3 / MOVEQ #0,D2 / RTS
TITLE = (
    b"M19 P2.2 FOUR NATIVE UNITS - EXPERIMENTAL PROBE ONLY\0"
    b"$VER: AMOSPro_AGA P2.2 TEST 68020+ NO BOB DRAW\0"
)
TITLE += bytes(len(TITLE) & 1)
BASE_PUBLIC, NEW_PUBLIC = 82, 83
GROUP_C2P, GROUP_IFF, GROUP_AGA, GROUP_BOBS = 83, 84, 85, 86
NEW_FUNCTION = ("aga bob probe", 1, BASE_PUBLIC, "0")


def build() -> tuple[bytes, dict]:
    protected = PROTECTED.read_bytes()
    if len(protected) != 67904 or sha256(protected).hexdigest() != R84_SHA:
        raise ValueError("R84 LAST_GOOD SHA/size mismatch; refusing candidate")
    active = ACTIVE.read_bytes()
    if active != protected:
        raise ValueError("R84 active library differs from LAST_GOOD")
    old_tokens, old, _ = unpack_ap20(protected)
    if len(old) != 85 or len(old_tokens) < 6 or old_tokens[-6:] != bytes(6):
        raise ValueError("Unexpected pinned R84 AP20 structure")
    if tuple(map(len, old[82:])) != (5558, 2508, 56580):
        raise ValueError("R84 C2P/IFF/AGA group layout drifted")
    if not old[81].endswith(bytes.fromhex("4e75")):
        raise ValueError("Last R84 public entry has no RTS")
    units = list(old[82:])
    if any(not u.startswith(DISPATCH_V2) or len(u) > 65534 for u in units):
        raise ValueError("Unexpected R84 Compiler V2 module")
    stubs = []
    for i, stub in enumerate(old[:BASE_PUBLIC]):
        if stub in (b"", GETP):
            stubs.append(stub)
            continue
        if not (stub.startswith(RBSR) and len(stub) in (8, 12)
                and stub[6:8] == bytes.fromhex("4e75")):
            raise ValueError(f"Unsupported historical R84 stub {i}")
        group, offset = unpack_from(">HH", stub, 2)
        if group not in (82, 83, 84):
            raise ValueError(f"Unknown historical group {group}")
        new_stub = RBSR + pack(">HH", group + 1, offset) + stub[6:]
        if i == BASE_PUBLIC - 1:
            # The old final token is now followed by Aga Bob Probe.
            if len(new_stub) != 8:
                raise ValueError("R84 last stub unexpectedly already contains GetP")
            new_stub += GETP
        stubs.append(new_stub)
    stubs.append(RBSR + pack(">HH", GROUP_BOBS, 0) + bytes.fromhex("4e75"))
    bob_unit = DISPATCH_V2 + PROBE_CODE
    if len(bob_unit) > 65534 or len(bob_unit) & 1:
        raise ValueError("New BOBS group exceeds Compiler 16-bit bound")
    segments = stubs + units + [bob_unit]
    if len(segments) != NEW_PUBLIC + 4:
        raise AssertionError("Four native unit structure incorrect")
    toks = old_tokens[:-6] + token(*NEW_FUNCTION) + bytes(6)
    built = repack_ap20(protected, toks, segments, TITLE)
    rt, pp, title = unpack_ap20(built)
    if (rt, pp, title) != (toks, segments, TITLE):
        raise AssertionError("AP20 roundtrip lost a field")
    original = inspect(parse(protected))
    candidate = inspect(parse(built))
    if original["issues"] or candidate["issues"]:
        raise AssertionError(("AP20 ABI issue", original["issues"], candidate["issues"]))
    if candidate["tokens"][:-1] != original["tokens"]:
        raise AssertionError("R84 76 public tokens altered")
    if candidate["tokens"][-1]["name"] != NEW_FUNCTION[0]:
        raise AssertionError("New probe function not published")
    if candidate["tokens"][-1]["function"] != BASE_PUBLIC:
        raise AssertionError("New probe function entry index changed")
    if [i["parameters"] for i in candidate["parameter_checks"]
            if i["index"] == BASE_PUBLIC]:
        raise AssertionError("Zero-argument probe must have no GetP check")
    if tuple(pp[NEW_PUBLIC:NEW_PUBLIC+3]) != tuple(old[BASE_PUBLIC:]):
        raise AssertionError("Historical native C2P/IFF/AGA bytes changed")
    links = interpreter_rbsr_displacements(pp)
    if len(links) != 81 or BASE_PUBLIC not in links:
        raise AssertionError("Wrong number of interpreter RBSR links")
    if len(segments[GROUP_BOBS]) != 40:
        raise AssertionError("Unexpected fourth dispatcher+probe length")
    return built, {
        "status": "EXPERIMENTAL ONLY; FOURTH BLOCK PROBE, NO BOB RENDER",
        "base": "R84 v0.13.29 LAST_GOOD",
        "sha256": sha256(built).hexdigest(),
        "size": len(built),
        "commands": 77,
        "ap20_entries": 87,
        "native_units": {
            "C2P": len(pp[GROUP_C2P]),
            "IFF": len(pp[GROUP_IFF]),
            "AGA": len(pp[GROUP_AGA]),
            "BOBS_PROBE": len(pp[GROUP_BOBS]),
        },
        "new_entry": BASE_PUBLIC,
        "bob_group": GROUP_BOBS,
        "rbsr_calls": len(links),
        "max_abs_amos_branch": max(map(abs, links.values())),
        "compiler_gate_c": "NOT TESTED",
        "winuae_gate_b": "NOT TESTED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        help="Write ONLY build/m19-p22/AMOSPro_AGA_M19_P22_4UNIT_PROBE.Lib")
    args = parser.parse_args()
    data, report = build()
    print("M19 P2.2 FOURTH NATIVE UNIT STATIC GATE", report, flush=True)
    if args.output:
        destination = args.output.resolve()
        if destination != PROBE_OUTPUT.resolve():
            raise SystemExit("Refusing output outside isolated build/m19-p22")
        if destination == PROTECTED.resolve() or destination == ACTIVE.resolve():
            raise SystemExit("Refusing to touch R84 LAST_GOOD/active")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        if sha256(destination.read_bytes()).hexdigest() != report["sha256"]:
            raise AssertionError("Written experimental candidate checksum mismatch")
        print("M19 P2.2 DISPOSABLE PROBE LIBRARY", destination, flush=True)


if __name__ == "__main__":
    main()
