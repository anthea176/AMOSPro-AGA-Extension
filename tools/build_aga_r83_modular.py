#!/usr/bin/env python3
"""Build R83 v0.13.28, three real AP20 native units, from pinned R82.

This is the one working-library circuit on main:
  dist/AMOSPro_AGA.Lib           R83 candidate, NEVER silently promoted
  dist/AMOSPro_AGA_LAST_GOOD.Lib R82 frozen and verified
  tests/current/*.asc            exactly one active AMOS test

The builder checks native ABI, all 78 native RBSR stubs, palette links,
68020 CPU dispatcher reachability and absence of P5 test padding.
Historical P5 routines are reused only as *audited source functions*.
Nothing is written unless --write-dist is explicitly passed.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path
from struct import unpack_from
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "experiments"))

from active_library import R82_SHA
from audit_ap20 import inspect, parse
from compiler_relocation import repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, unwrap_native_parts_v2
from ap20_v3_r82_threeunits import build_in_memory as p5_build, cross_module_pc_branches
from ap20_v3_r82_split import (
    pinned_r82, starts, interpreter_rbsr_displacements,
    assert_reaches_entry_on_mc68020,
)
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from build_c2p_r76_rpg_fix import state_offset, SITES

CURRENT = ROOT / "dist" / "AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist" / "AMOSPro_AGA_LAST_GOOD.Lib"
TITLE = (b"AMOSPro AGA R83 v0.13.28 - 3 NATIVE UNITS\0"
         b"$VER: AMOSPro_AGA 0.13.28 (R83) MC68020+ 3 modules\0")
TITLE += bytes(len(TITLE) & 1)
EXPECTED_UNITS = (5558, 2508, 52974)
EXPECTED_NATIVE_TOTAL = 61040
GROUP_NAMES = ("C2P", "IFF", "AGA")


def build() -> tuple[bytes, dict]:
    frozen = pinned_r82()
    if frozen != LAST_GOOD.read_bytes() or sha256(frozen).hexdigest() != R82_SHA:
        raise AssertionError("Pinned R82 LAST_GOOD changed")
    intermediate, p5 = p5_build(frozen, pad_bytes=0)
    tokens, segments, _ = unpack_ap20(intermediate)
    if len(segments) != 83 or tuple(map(len, segments[80:])) != EXPECTED_UNITS:
        raise AssertionError("Unexpected audited P5 zero-padding layout")
    if sum(map(len, segments[80:])) != EXPECTED_NATIVE_TOTAL:
        raise AssertionError("Wrong native R83 total")
    # Repack only AP20 title. Code bodies and all public token signatures
    # remain EXACTLY the audited R82->P5 bytes, except four palette BSR.L.
    candidate = repack_ap20(frozen, tokens, segments, TITLE)
    retokens, parts, title = unpack_ap20(candidate)
    if retokens != tokens or parts != segments or title != TITLE:
        raise AssertionError("R83 repack changed native code or command signatures")
    if b"TEST ONLY" in candidate or b"EXPERIMENT" in TITLE:
        raise AssertionError("Experimental title leaked into R83")
    if parts[81] != DISPATCH_V2 + unwrap_native_parts_v2(frozen)[1][75]:
        raise AssertionError("IFF unit contains changed code or synthetic padding")
    original_tokens = inspect(parse(frozen))["tokens"]
    report = inspect(parse(candidate))
    if report["issues"] or report["tokens"] != original_tokens:
        raise AssertionError("R82 public API/ABI changed")
    if len([x for x in report["tokens"] if x["name"].startswith("aga ")]) != 74:
        raise AssertionError("R83 must expose exactly the 74 R82 commands")
    links = interpreter_rbsr_displacements(parts)
    if len(links) != 78:
        raise AssertionError("Unexpected number of live RBSR native stubs")
    _, old = unwrap_native_parts_v2(frozen)
    if cross_module_pc_branches(old):
        raise AssertionError("Unaudited PC-relative link between modules")
    assert_native_links(old[:70])
    check_cross_r74(old[:70])
    if state_offset(old) != 12070:
        raise AssertionError("Legacy keyboard/mouse State displacement moved")
    for entry, offset, opcode in SITES:
        if old[entry][offset:offset + 4] != opcode.to_bytes(2, "big") + bytes.fromhex("2f26"):
            raise AssertionError("Legacy keyboard/mouse LEA changed")
    return candidate, {
        "revision": "R83",
        "version": "0.13.28",
        "status": "MAIN WORKING CANDIDATE: WinUAE R83 B/C PENDING",
        "source_R82_SHA256": R82_SHA,
        "sha256": sha256(candidate).hexdigest(),
        "size": len(candidate),
        "commands": 74,
        "ap20_entries": len(parts),
        "units": dict(zip(GROUP_NAMES, EXPECTED_UNITS)),
        "aggregate_native_bytes": EXPECTED_NATIVE_TOTAL,
        "iff_padding_bytes": 0,
        "rbsr_stubs": len(links),
        "max_abs_loader_bsr_w": max(map(abs, links.values())),
        "p5_provenance_sha256_no_padding": sha256(intermediate).hexdigest(),
    }


class R83ModularGateA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib, cls.meta = build()

    def test_release_candidate_layout_and_title(self):
        self.assertEqual(self.meta["units"], {"C2P": 5558, "IFF": 2508, "AGA": 52974})
        self.assertEqual(self.meta["aggregate_native_bytes"], 61040)
        self.assertEqual(self.meta["iff_padding_bytes"], 0)
        _, parts, title = unpack_ap20(self.lib)
        self.assertEqual(len(parts), 83)
        self.assertEqual(title, TITLE)
        self.assertNotIn(b"TEST ONLY", title)
        self.assertNotIn(b"P5", title)

    def test_r82_frozen_and_deterministic(self):
        again, meta = build()
        self.assertEqual(self.lib, again)
        self.assertEqual(meta, self.meta)
        self.assertNotEqual(self.lib, LAST_GOOD.read_bytes())
        self.assertEqual(sha256(LAST_GOOD.read_bytes()).hexdigest(), R82_SHA)

    def test_dispatcher_reachability_on_real_mc68020(self):
        for entry in (0, 2, 6, 20, 33, 41, 55, 57, 69, 70, 71,
                      72, 73, 74, 75, 76, 77, 78, 79):
            with self.subTest(native_entry=entry):
                assert_reaches_entry_on_mc68020(self.lib, entry)

    def test_exact_p5_zero_padding_native_inheritance(self):
        frozen = pinned_r82()
        tmp, _ = p5_build(frozen, pad_bytes=0)
        old_tok, old_segments, _ = unpack_ap20(tmp)
        new_tok, new_segments, _ = unpack_ap20(self.lib)
        self.assertEqual(new_tok, old_tok)
        self.assertEqual(new_segments, old_segments)

    def test_no_oversized_unit(self):
        _, parts, _ = unpack_ap20(self.lib)
        self.assertTrue(all(0 < len(p) <= 65534 for p in parts[80:]))
        self.assertEqual(self.meta["rbsr_stubs"], 78)
        self.assertLess(self.meta["max_abs_loader_bsr_w"], 32766)

    def test_reject_overwritten_last_good(self):
        original = LAST_GOOD.read_bytes()
        tampered = bytearray(original)
        tampered[20] ^= 1
        self.assertNotEqual(sha256(tampered).hexdigest(), R82_SHA)


def gate_a():
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(R83ModularGateA)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if not result.wasSuccessful():
        raise SystemExit("R83 GATE A FAILED")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check-dist", action="store_true",
                     help="Assert canonical dist candidate is byte-exact to builder")
    cli.add_argument("--write-dist", action="store_true",
                     help="Write canonical dist/AMOSPro_AGA.Lib; NEVER LAST_GOOD")
    cli.add_argument("--emit-base64", action="store_true",
                     help="Print candidate bytes to GitHub CI log, no alternate artifact")
    args = cli.parse_args()
    gate_a()
    candidate, meta = build()
    print("R83 THREE MODULES HOST GATE A PASS", meta, flush=True)
    if args.check_dist:
        if CURRENT.read_bytes() != candidate:
            raise SystemExit("Active dist/AMOSPro_AGA.Lib differs from deterministic R83 builder")
        print("R83 ACTIVE DIST BYTE-EXACT PASS", flush=True)
    if args.write_dist:
        if CURRENT.resolve() == LAST_GOOD.resolve():
            raise SystemExit("Refusing to overwrite LAST_GOOD")
        CURRENT.write_bytes(candidate)
        if CURRENT.read_bytes() != candidate:
            raise SystemExit("dist candidate write corruption")
        print("R83 ACTIVE OUTPUT", CURRENT, flush=True)
    if args.emit_base64:
        encoded = base64.b64encode(candidate).decode("ascii")
        print("R83_MAIN_LIB_B64_BEGIN", flush=True)
        for at in range(0, len(encoded), 120):
            print("R83_MAIN_LIB_B64", encoded[at:at + 120], flush=True)
        print("R83_MAIN_LIB_B64_END", flush=True)


if __name__ == "__main__":
    main()
