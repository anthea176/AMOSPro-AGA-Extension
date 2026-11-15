#!/usr/bin/env python3
"""M19 P2.3 R86: build genuine fourth-unit BOBS batch candidate from frozen R84.

No historical 76-command signature or native C2P/IFF/AGA unit changes.
Only dist/AMOSPro_AGA.Lib may be written, and only with --write-dist.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools" / "experiments")]
from active_library import R84_SHA, R85_SHA, R87_SHA
from audit_ap20 import inspect, parse, token
from compiler_relocation import unpack_ap20, repack_ap20, RBSR, GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements
from build_m19_p22_fourth_unit_probe import PROBE_CODE
from m19_bob_batch_emit import emit_bob_batch

PROTECTED = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
ACTIVE = ROOT / "dist/AMOSPro_AGA.Lib"
TITLE = (b"AMOSPro AGA R86 v0.13.31 FOUR UNITS NATIVE BOBS BATCH - GATE A CANDIDATE\0"
         b"$VER: AMOSPro_AGA 0.13.31 (R86) MC68020+ BOBS BATCH CANDIDATE\0")
TITLE += bytes(len(TITLE) & 1)
BASE_PUBLIC = 82
FIRST_NEW = 82
BATCH_ENTRY = 83
GROUP_C2P, GROUP_IFF, GROUP_BOBS, GROUP_AGA = 84, 85, 86, 87
REMAP = {82: GROUP_C2P, 83: GROUP_IFF, 84: GROUP_AGA}
APIS = (("aga bob probe", 1, FIRST_NEW, "0"),
        ("aga bob batch", 1, BATCH_ENTRY, "00,0"))


def build() -> tuple[bytes, dict]:
    original = PROTECTED.read_bytes()
    if len(original) != 67904 or sha256(original).hexdigest() != R84_SHA:
        raise ValueError("R84 LAST_GOOD mismatch; refusing build")
    previous, old, _ = unpack_ap20(original)
    if len(old) != 85 or tuple(map(len, old[82:])) != (5558, 2508, 56580):
        raise ValueError("Pinned R84 three-unit layout changed")
    if previous[-6:] != bytes(6):
        raise ValueError("Invalid R84 AP20 public terminator")
    if any(not u.startswith(DISPATCH_V2) or len(u) > 65534 for u in old[82:]):
        raise ValueError("Unexpected historical Compiler V2 modules")
    if not old[BASE_PUBLIC-1].endswith(b"\x4e\x75"):
        raise ValueError("R84 final public entry malformed")

    original_report = inspect(parse(original))
    if original_report["issues"] or len([x for x in original_report["tokens"] if x["name"].startswith("aga ")]) != 76:
        raise ValueError("R84 public API signature count changed")

    core, labels = emit_bob_batch()
    if len(core) & 1 or not core.startswith(bytes.fromhex("48e7efee")):
        raise ValueError("BOBS native routine malformed")
    unit = DISPATCH_V2 + PROBE_CODE + core
    if len(unit) > 65534 or len(unit) & 1:
        raise ValueError("BOBS Compiler V2 unit exceeds 65534 bytes")
    old_stubs = []
    for i, stub in enumerate(old[:BASE_PUBLIC]):
        if stub in (b"", GETP):
            old_stubs.append(stub)
            continue
        if not (stub[:2] == RBSR and len(stub) in (8, 12)
                and stub[6:8] == b"\x4e\x75"):
            raise ValueError(f"R84 stub {i} malformed")
        group, off = unpack_from(">HH", stub, 2)
        if group not in REMAP:
            raise ValueError(f"Unexpected historical group {group}")
        rebased = RBSR + pack(">HH", REMAP[group], off) + stub[6:]
        if i == BASE_PUBLIC-1:
            if len(rebased) != 8:
                raise ValueError("R84 last stub unexpectedly has GetP")
            rebased += GETP
        old_stubs.append(rebased)
    # Previous probe stays callable. Its marker now points to Batch's args.
    old_stubs.append(RBSR + pack(">HH", GROUP_BOBS, 0)
                     + b"\x4e\x75" + GETP)
    old_stubs.append(RBSR + pack(">HH", GROUP_BOBS, len(PROBE_CODE))
                     + b"\x4e\x75")
    segments = old_stubs + [old[82], old[83], unit, old[84]]
    if len(segments) != 88:
        raise AssertionError("Expected 84 public entries + 4 native groups")
    tokens = previous[:-6] + b"".join(token(*api) for api in APIS) + bytes(6)
    output = repack_ap20(original, tokens, segments, TITLE)
    tk, parts, title = unpack_ap20(output)
    if (tk, parts, title) != (tokens, segments, TITLE):
        raise AssertionError("AP20 pack roundtrip failed")
    report = inspect(parse(output))
    if report["issues"]:
        raise ValueError(("Invalid public AP20 ABI", report["issues"]))
    if report["tokens"][:-2] != original_report["tokens"]:
        raise ValueError("One or more historical R84 tokens/signatures changed")
    if [(x["name"],x["function"],x["signature"]) for x in report["tokens"][-2:]] != [
            (api[0],api[2],api[3]) for api in APIS]:
        raise ValueError("Probe/Batch public tokens malformed")
    if not any(x["index"]==BATCH_ENTRY and x["parameters"]==2
               and x["getp"] for x in report["parameter_checks"]):
        raise ValueError("Batch GetP two-argument ABI missing")
    if (parts[GROUP_C2P], parts[GROUP_IFF], parts[GROUP_AGA]) != tuple(old[82:]):
        raise ValueError("R84 historical native group modified")
    links = interpreter_rbsr_displacements(parts)
    if len(links) != 82 or BATCH_ENTRY not in links:
        raise ValueError("Wrong number of RBSR links")
    if max(map(abs, links.values())) >= 32766:
        raise ValueError("Signed loader BSR.W reach exceeded")
    if any(len(parts[x]) > 65534 for x in (GROUP_C2P,GROUP_IFF,GROUP_BOBS,GROUP_AGA)):
        raise ValueError("16-bit module exceeds size")
    if ACTIVE.read_bytes() not in (original, output) and (
            sha256(ACTIVE.read_bytes()).hexdigest() not in (R85_SHA, R87_SHA)):
        raise ValueError("Unknown active candidate: refusing overwrite")
    return output, {
        "version": "R86 v0.13.31 M19 P2.3",
        "status": "GATE A CANDIDATE; WINUAE B/C PENDING",
        "bytes": len(output),
        "sha256": sha256(output).hexdigest(),
        "commands": 78,
        "ap20_entries": len(parts),
        "native_units": {
            "C2P":len(parts[GROUP_C2P]),
            "IFF":len(parts[GROUP_IFF]),
            "BOBS":len(parts[GROUP_BOBS]),
            "AGA":len(parts[GROUP_AGA]),
        },
        "native_batch_bytes": len(core),
        "probe_offset": 0,
        "batch_offset": len(PROBE_CODE),
        "native_labels": labels,
        "native_bsr_w_reach": max(map(abs,links.values())),
        "gate_b": "NOT TESTED",
        "gate_c": "NOT TESTED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-dist", action="store_true")
    parser.add_argument("--check-dist", action="store_true")
    args = parser.parse_args()
    candidate, meta = build()
    report = dict(meta)
    report.pop("native_labels")
    print("M19 P2.3 NATIVE BOBS R86 BUILD", report, flush=True)
    if args.check_dist and ACTIVE.read_bytes() != candidate:
        raise SystemExit("Active dist candidate differs from deterministic R86 builder")
    if args.write_dist:
        frozen = PROTECTED.read_bytes()
        if (ACTIVE.resolve() == PROTECTED.resolve()
                or sha256(frozen).hexdigest() != R84_SHA):
            raise SystemExit("LAST_GOOD protection failure")
        ACTIVE.write_bytes(candidate)
        if ACTIVE.read_bytes() != candidate or PROTECTED.read_bytes() != frozen:
            raise AssertionError("Candidate corrupted or LAST_GOOD changed")
        print("ACTIVE CANDIDATE", ACTIVE, meta["sha256"], flush=True)


if __name__ == "__main__":
    main()
