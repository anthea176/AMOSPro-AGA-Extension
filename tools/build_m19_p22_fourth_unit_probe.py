#!/usr/bin/env python3
"""M19 P2.2: experimental FOURTH AP20 native unit on pinned R84 (no Batch yet).

Prove an independent BOBS native unit is reachable in interpreted and
compiler-V2 routing. The ONLY new public function is Aga Bob Probe(), a
disposable infrastructure witness returning 1. It DOES NOT render anything.

Working candidate is written ONLY to dist/AMOSPro_AGA.Lib with --write-dist.
Frozen dist/AMOSPro_AGA_LAST_GOOD.Lib remains SHA-pinned and unmodified.
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
# Only one active candidate in dist; LAST_GOOD remains frozen.
PROBE_CODE = bytes.fromhex("760174004e75")  # MOVEQ #1,D3 / MOVEQ #0,D2 / RTS
TITLE = (
    b"AMOSPro AGA R85 v0.13.30 FOUR NATIVE UNITS - TEST ONLY\0"
    b"$VER: AMOSPro_AGA 0.13.30 (R85) MC68020+ BOBS PROBE ONLY\0"
)
TITLE += bytes(len(TITLE) & 1)
BASE_PUBLIC, NEW_PUBLIC = 82, 83
GROUP_C2P, GROUP_IFF, GROUP_BOBS, GROUP_AGA = 83, 84, 85, 86
GROUP_REMAP = {82: GROUP_C2P, 83: GROUP_IFF, 84: GROUP_AGA}
NEW_FUNCTION = ("aga bob probe", 1, BASE_PUBLIC, "0")


def build() -> tuple[bytes, dict]:
    protected = PROTECTED.read_bytes()
    if len(protected) != 67904 or sha256(protected).hexdigest() != R84_SHA:
        raise ValueError("R84 LAST_GOOD SHA/size mismatch; refusing candidate")
    # Active may be R84 or this deterministic candidate; checked below.
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
        new_stub = RBSR + pack(">HH", GROUP_REMAP[group], offset) + stub[6:]
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
    # The AMOS loader BSR.W reach is signed 16-bit: BOBS cannot be
    # placed AFTER the 56580-byte AGA core (measured +64652 bytes).
    # Keep the two small historical units, then BOBS, then AGA.
    segments = stubs + units[:2] + [bob_unit, units[2]]
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
    if (pp[GROUP_C2P] != old[82] or pp[GROUP_IFF] != old[83]
            or pp[GROUP_AGA] != old[84]):
        raise AssertionError("Historical native C2P/IFF/AGA bytes changed")
    links = interpreter_rbsr_displacements(pp)
    if len(links) != 81 or BASE_PUBLIC not in links:
        raise AssertionError("Wrong number of interpreter RBSR links")
    if len(segments[GROUP_BOBS]) != 40:
        raise AssertionError("Unexpected fourth dispatcher+probe length")
    active_sha=sha256(ACTIVE.read_bytes()).hexdigest()
    if ACTIVE.read_bytes() not in (protected, built) and active_sha!="69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc":
        # Historical R85 builder is read-only on newer active candidates.
        raise ValueError("Unknown dist active library, refuse candidate overwrite")
    if active_sha=="69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc" and sha256(PROTECTED.read_bytes()).hexdigest()!=R84_SHA:
        raise ValueError("R84 LAST_GOOD modified")
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
    parser.add_argument("--write-dist", action="store_true",
        help="Write ONLY dist/AMOSPro_AGA.Lib; protect LAST_GOOD SHA256")
    parser.add_argument("--emit-base64", action="store_true",
        help="Emit exact candidate base64 for committing the active dist file")
    args = parser.parse_args()
    data, report = build()
    print("M19 P2.2 FOURTH NATIVE UNIT STATIC GATE", report, flush=True)
    if args.write_dist:
        if sha256(ACTIVE.read_bytes()).hexdigest()=="69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc":
            raise SystemExit("REFUSED: historical R85 probe must not overwrite active R88")
        if ACTIVE.resolve() == PROTECTED.resolve():
            raise SystemExit("Refusing to overwrite LAST_GOOD")
        original = PROTECTED.read_bytes()
        if len(original) != 67904 or sha256(original).hexdigest() != R84_SHA:
            raise SystemExit("Refuse write: LAST_GOOD SHA mismatch")
        ACTIVE.write_bytes(data)
        if ACTIVE.read_bytes() != data or PROTECTED.read_bytes() != original:
            raise AssertionError("Candidate corrupted or LAST_GOOD altered")
        print("M19 P2.2 ACTIVE CANDIDATE dist/AMOSPro_AGA.Lib",
              report["sha256"], flush=True)
    if args.emit_base64:
        import base64
        encoded = base64.b64encode(data).decode("ascii")
        print("M19_P22_DIST_LIB_B64_BEGIN", flush=True)
        for pos in range(0, len(encoded), 120):
            print("M19_P22_DIST_LIB_B64", encoded[pos:pos + 120], flush=True)
        print("M19_P22_DIST_LIB_B64_END", flush=True)


if __name__ == "__main__":
    main()
