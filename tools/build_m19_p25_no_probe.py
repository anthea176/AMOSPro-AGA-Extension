#!/usr/bin/env python3
"""M19 P2.5 R87: production-shaped four-unit BOBS without Aga Bob Probe.

Reconstruct from pinned R84 LAST_GOOD and the R86 source-backed native
BOBS emitter. No modification to the three inherited R84 native groups.
Only dist/AMOSPro_AGA.Lib may be changed, with explicit --write-dist.
"""
from __future__ import annotations

import argparse
import sys
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools" / "experiments")]
from active_library import R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, P1E_SHA, P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, S1P1F_SHA
from audit_ap20 import inspect, parse, token
from compiler_relocation import unpack_ap20, repack_ap20, RBSR, GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements
from m19_bob_batch_emit import emit_bob_batch

PROTECTED = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
ACTIVE = ROOT / "dist/AMOSPro_AGA.Lib"
TITLE = (b"AMOSPro AGA R87 v0.13.32 FOUR UNITS NATIVE BOBS BATCH - CANDIDATE\0"
         b"$VER: AMOSPro_AGA 0.13.32 (R87) MC68020+ BOBS BATCH CANDIDATE\0")
TITLE += bytes(len(TITLE) & 1)
BASE_PUBLIC = 82
BATCH_ENTRY = 82
GROUP_C2P, GROUP_IFF, GROUP_BOBS, GROUP_AGA = 83, 84, 85, 86
REMAP = {82: GROUP_C2P, 83: GROUP_IFF, 84: GROUP_AGA}
API = ("aga bob batch", 1, BATCH_ENTRY, "00,0")
# SHA-pinned R87 candidate: only the source-backed deterministic output is accepted.


def build() -> tuple[bytes, dict]:
    live_good=PROTECTED.read_bytes()
    if (len(live_good),sha256(live_good).hexdigest()) not in ((117896,P0_FREE_SHA),(124444,P1E_SHA),(136020,P2D_SHA),(136708,P2DL2B_SHA)):
        raise ValueError("Unrecognized author-promoted P0/P1e LAST_GOOD")
    from build_aga_r84_agapic import build as build_r84
    protected,r84_meta=build_r84()
    if len(protected)!=67904 or r84_meta['sha256']!=R84_SHA:
        raise ValueError("Historical R84 source SHA mismatch; refusing R87 build")
    previous, old, _ = unpack_ap20(protected)
    if len(old) != 85 or tuple(map(len, old[82:])) != (5558, 2508, 56580):
        raise ValueError("Pinned R84 unit layout changed")
    if previous[-6:] != bytes(6):
        raise ValueError("Malformed R84 public token terminator")
    if any(not u.startswith(DISPATCH_V2) or len(u) > 65534 for u in old[82:]):
        raise ValueError("Malformed historical Compiler V2 group")
    report_r84 = inspect(parse(protected))
    if report_r84["issues"] or len([x for x in report_r84["tokens"]
                                    if x["name"].startswith("aga ")]) != 76:
        raise ValueError("R84 historical signature set changed")

    native, labels = emit_bob_batch()
    if not native.startswith(bytes.fromhex("48e7efee")) or len(native) & 1:
        raise ValueError("Native batch output malformed")
    unit = DISPATCH_V2 + native
    if len(unit) & 1 or len(unit) > 65534:
        raise ValueError("BOBS Compiler V2 size exceeds 65,534 bytes")

    stubs = []
    for index, stub in enumerate(old[:BASE_PUBLIC]):
        if stub in (b"", GETP):
            stubs.append(stub)
            continue
        if not (stub[:2] == RBSR and len(stub) in (8, 12)
                and stub[6:8] == b"\x4e\x75"):
            raise ValueError(f"Unknown R84 public stub at {index}")
        old_group, entry = unpack_from(">HH", stub, 2)
        if old_group not in REMAP:
            raise ValueError(f"Unexpected historical group {old_group}")
        rewritten = RBSR + pack(">HH", REMAP[old_group], entry) + stub[6:]
        if index == BASE_PUBLIC - 1:
            if len(rewritten) != 8:
                raise ValueError("Historical last entry already has GetP")
            rewritten += GETP
        stubs.append(rewritten)

    # Only one public BOBS entry, no diagnostic token/stub/routine.
    stubs.append(RBSR + pack(">HH", GROUP_BOBS, 0) + b"\x4e\x75")
    entries = stubs + [old[82], old[83], unit, old[84]]
    if len(entries) != 87:
        raise AssertionError("R87 must have 83 public + 4 native entries")
    tokens = previous[:-6] + token(*API) + bytes(6)
    output = repack_ap20(protected, tokens, entries, TITLE)
    if sha256(output).hexdigest() != R87_SHA:
        raise ValueError("R87 deterministic source SHA differs from pinned binary")
    unpacked_tokens, unpacked_entries, unpacked_title = unpack_ap20(output)
    if (unpacked_tokens, unpacked_entries, unpacked_title) != (tokens, entries, TITLE):
        raise AssertionError("R87 AP20 pack/unpack not byte exact")

    report = inspect(parse(output))
    if report["issues"] or report["tokens"][:-1] != report_r84["tokens"]:
        raise ValueError(("R84 signatures/ABI changed", report["issues"]))
    if (report["tokens"][-1]["name"],report["tokens"][-1]["function"],
        report["tokens"][-1]["signature"]) != (API[0], API[2], API[3]):
        raise ValueError("Batch token or 2-argument signature invalid")
    if any(x["name"] == "aga bob probe" for x in report["tokens"]):
        raise ValueError("Aga Bob Probe leaked into R87 public tokens")
    if len([x for x in report["tokens"] if x["name"].startswith("aga ")]) != 77:
        raise ValueError("R87 must have exactly 77 AGA commands")
    if not any(x["index"] == BATCH_ENTRY and x["parameters"] == 2 and x["getp"]
               for x in report["parameter_checks"]):
        raise ValueError("GetP two-parameter ABI lost on Batch")
    if (unpacked_entries[GROUP_C2P], unpacked_entries[GROUP_IFF],
        unpacked_entries[GROUP_AGA]) != tuple(old[82:]):
        raise ValueError("Frozen R84 native engine differs")
    if unpacked_entries[GROUP_BOBS] != DISPATCH_V2 + native:
        raise ValueError("Unexpected probe or padding in BOBS unit")
    links = interpreter_rbsr_displacements(unpacked_entries)
    if len(links) != 81 or BATCH_ENTRY not in links:
        raise ValueError("Unexpected interpreter RBSR entry count")
    if max(map(abs, links.values())) >= 32766:
        raise ValueError("Interpreter BSR.W signed reach exceeded")
    if any(len(unpacked_entries[i]) > 65534 for i in
           (GROUP_C2P, GROUP_IFF, GROUP_BOBS, GROUP_AGA)):
        raise ValueError("Compiler V2 unit exceeds 65,534 bytes")
    active = ACTIVE.read_bytes()
    current_sha = sha256(active).hexdigest()
    if current_sha not in (R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA,P2D_SHA,S1P1E_SHA,P2DL2_SHA,P2DL2B_SHA, S1P1F_SHA):
        raise ValueError("Unknown dist/ candidate: refusing overwrite")

    return output, {
        "version": "R87 v0.13.32 M19 P2.5 no embedded probe",
        "status": "GATE A CANDIDATE; WINUAE RUNTIME/COMPILED PENDING",
        "bytes": len(output),
        "sha256": sha256(output).hexdigest(),
        "commands": 77,
        "ap20_entries": len(entries),
        "native_units": {
            "C2P":len(entries[GROUP_C2P]),
            "IFF":len(entries[GROUP_IFF]),
            "BOBS":len(entries[GROUP_BOBS]),
            "AGA":len(entries[GROUP_AGA]),
        },
        "native_batch_bytes":len(native),
        "batch_entry":BATCH_ENTRY,
        "batch_offset":0,
        "native_labels":labels,
        "native_bsr_w_reach":max(map(abs,links.values())),
        "gate_a":"9/9 MC68020 PASS (CI 43719479059)",
        "gate_b":"NOT TESTED",
        "gate_c":"NOT TESTED",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write-dist", action="store_true")
    p.add_argument("--check-dist", action="store_true")
    args = p.parse_args()
    candidate, meta = build()
    report = dict(meta)
    report.pop("native_labels")
    print("M19 P2.5 R87 BOBS WITHOUT PROBE", report, flush=True)
    if args.check_dist and ACTIVE.read_bytes() != candidate:
        raise SystemExit("dist/AMOSPro_AGA.Lib is not the deterministic R87 candidate")
    if args.write_dist:
        if sha256(ACTIVE.read_bytes()).hexdigest() in (R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA,P2D_SHA,S1P1E_SHA,P2DL2_SHA,P2DL2B_SHA, S1P1F_SHA):
            raise SystemExit("REFUSED: historical R87 builder must not replace newer R88/P0c/P0d/AP20/B7 active candidate")
        frozen = PROTECTED.read_bytes()
        if ACTIVE.resolve() == PROTECTED.resolve() or sha256(frozen).hexdigest() != P0_FREE_SHA:
            raise SystemExit("R84 LAST_GOOD protection failure")
        ACTIVE.write_bytes(candidate)
        if ACTIVE.read_bytes() != candidate or PROTECTED.read_bytes() != frozen:
            raise AssertionError("R87 output or R84 LAST_GOOD changed unexpectedly")
        print("ACTIVE CANDIDATE", str(ACTIVE), meta["sha256"], flush=True)


if __name__ == "__main__":
    main()
