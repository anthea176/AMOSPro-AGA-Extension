#!/usr/bin/env python3
"""P5: split the genuine R82 into 3 AP20 native units (AGA/C2P/IFF).

This program inherits the exact SHA-pinned R82 native implementation.
No release, no update to main or dist, no claim of real WinUAE validation.
Only the four previously audited palette BSR.L displacements change.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from active_library import R82_SHA
from audit_ap20 import inspect, parse
from compiler_bridge_v2_probe import DISPATCH_V2, unwrap_native_parts_v2
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from build_c2p_r76_rpg_fix import SITES, state_offset
from ap20_v3_r82_split import (
    pinned_r82, starts, remap_palette_links,
    interpreter_rbsr_displacements, assert_reaches_entry_on_mc68020,
    PALETTE_LINKS,
)

EXPECTED_NATIVE = (49828, 5524, 2474, 3112)
PUBLIC_ENTRIES = 80
GROUP_C2P, GROUP_IFF, GROUP_CORE = 80, 81, 82
PAD_DEFAULT = 12000
PAD_MAX = 65534
TITLE = (b"AP20 V3 P5 R82 THREE GENUINE NATIVE UNITS - TEST ONLY\0"
         b"$VER: AP20 V3 R82 THREE UNIT EXPERIMENT\0")
TITLE += bytes(len(TITLE) & 1)
PUBLIC_GROUPS = {
    **{i: GROUP_C2P for i in range(70, 75)},
    75: GROUP_IFF,
    **{i: GROUP_CORE for i in [*range(70), *range(76, 80)]},
}


def cross_module_pc_branches(parts: list[bytes]) -> list[tuple]:
    """Conservative aligned scan for native BRA/BSR/Bcc.W or .L across groups.

    The generator intentionally preserves whole original function bodies.
    This scan is a defense in depth, NOT full 68020 instruction tracing:
    words inside other instructions/data may look like branches. A new
    candidate requires a new disassembly audit, not relaxing this gate.
    """
    from struct import unpack_from
    offsets = starts(parts)
    native = b"".join(parts)
    boundaries = [offsets[i] for i in range(len(parts))]

    def owner(at: int) -> int | None:
        if not (0 <= at < len(native)):
            return None
        for n in range(len(parts) - 1, -1, -1):
            if boundaries[n] <= at and parts[n]:
                return n
        return None

    edges = []
    for entry, part in enumerate(parts):
        if not part:
            continue
        group = PUBLIC_GROUPS[entry]
        for rel in range(0, max(0, len(part) - 5), 2):
            opcode = unpack_from(">H", part, rel)[0]
            if (opcode & 0xf000) != 0x6000:
                continue
            width = opcode & 0xff
            if width == 0:
                disp = unpack_from(">h", part, rel + 2)[0]
            elif width == 0xff:
                disp = unpack_from(">i", part, rel + 2)[0]
            else:
                continue
            target = offsets[entry] + rel + 2 + disp
            destination = owner(target)
            if destination is not None and PUBLIC_GROUPS[destination] != group:
                edges.append((entry, rel, destination, target, hex(opcode)))
    return edges


def build_in_memory(source: bytes, *, pad_bytes: int = PAD_DEFAULT):
    if sha256(source).hexdigest() != R82_SHA:
        raise ValueError("R82 input does not match immutable LAST_GOOD SHA")
    if pad_bytes < 0 or pad_bytes > PAD_MAX or pad_bytes & 1:
        raise ValueError("Padding must be even and within allowed maximum")
    tokens, old_parts = unwrap_native_parts_v2(source)
    if len(old_parts) != PUBLIC_ENTRIES or tokens[-6:] != bytes(6):
        raise ValueError("Unexpected R82 native/token layout")
    expected = (
        sum(map(len, old_parts[:70])),
        sum(map(len, old_parts[70:75])),
        len(old_parts[75]),
        sum(map(len, old_parts[76:])),
    )
    if expected != EXPECTED_NATIVE:
        raise ValueError(f"R82 native groups changed: {expected}")
    assert_native_links(old_parts[:70])
    check_cross_r74(old_parts[:70])
    if state_offset(old_parts) != 12070:
        raise ValueError("R82 static input state moved")
    for entry, site, opcode in SITES:
        if old_parts[entry][site:site + 4] != pack(">HH", opcode, 12070):
            raise ValueError(f"R82 keyboard/mouse LEA changed: {entry}:{site}")

    # All six known native core cross-entry links and seven keyboard/mouse
    # State offsets are still intra-unit and byte-for-byte unchanged.
    # Split the standalone IFF-to-chunky decoder off C2P Open/Close/Blit/Zoom.
    direct_edges = cross_module_pc_branches(old_parts)
    if direct_edges:
        raise ValueError(f"Native cross-unit PC-relative edge(s): {direct_edges}")

    remapped, palette_links = remap_palette_links(old_parts)
    assert_native_links(remapped[:70])
    check_cross_r74(remapped[:70])
    if state_offset(remapped) != 12070:
        raise ValueError("R82 shared state moved")
    if cross_module_pc_branches(remapped):
        raise ValueError("Palette rebase unexpectedly introduced cross-unit links")
    diff = [i for i, (x, y) in enumerate(zip(old_parts, remapped)) if x != y]
    if diff != [76, 77, 78, 79]:
        raise ValueError("Unexpected native changes outside four palette links")

    group_entries = {
        GROUP_C2P: [*range(70, 75)],
        GROUP_IFF: [75],
        GROUP_CORE: [*range(70), *range(76, 80)],
    }
    bodies = {group: b"".join(remapped[i] for i in indices)
              for group, indices in group_entries.items()}
    units = {
        GROUP_C2P: DISPATCH_V2 + bodies[GROUP_C2P],
        GROUP_IFF: DISPATCH_V2 + bodies[GROUP_IFF] + b"\x4e\x71" * (pad_bytes // 2),
        GROUP_CORE: DISPATCH_V2 + bodies[GROUP_CORE],
    }
    if any(len(unit) > 65534 or len(unit) & 1 for unit in units.values()):
        raise ValueError("AP20 Compiler 16-bit per-unit capacity exceeded")
    if pad_bytes and sum(map(len, units.values())) <= 65536:
        raise ValueError("P5 stress requires aggregate native >64 KiB")

    positions = {
        index: (group, starts([remapped[i] for i in indices])[at])
        for group, indices in group_entries.items()
        for at, index in enumerate(indices)
    }
    if set(positions) != set(range(PUBLIC_ENTRIES)):
        raise AssertionError("R82 public entry groups not a full partition")
    stubs = []
    for index, original in enumerate(remapped):
        if original in (b"", GETP):
            stubs.append(original)
            continue
        group, offset = positions[index]
        if offset & 1 or offset >= 65536:
            raise ValueError("Native 16-bit entry offset invalid")
        stub = RBSR + pack(">HH", group, offset) + bytes.fromhex("4e75")
        if original.endswith(GETP):
            stub += GETP
        stubs.append(stub)
    groups = [units[GROUP_C2P], units[GROUP_IFF], units[GROUP_CORE]]
    segments = stubs + groups
    relocations = interpreter_rbsr_displacements(segments)

    built = repack_ap20(source, tokens, segments, TITLE)
    new_tokens, unpacked, new_title = unpack_ap20(built)
    if new_tokens != tokens or unpacked != segments or new_title != TITLE:
        raise AssertionError("AP20 3-unit encoding roundtrip failed")
    current = inspect(parse(built))
    historical = inspect(parse(source))
    if current["issues"]:
        raise ValueError(f"AP20 scanner found issues: {current['issues']}")
    public_now = [x for x in current["tokens"] if x["name"].startswith("aga ")]
    public_old = [x for x in historical["tokens"] if x["name"].startswith("aga ")]
    if len(public_old) != 74 or public_now != public_old:
        raise ValueError("R82 API GetP and function signatures were modified")
    for group in (GROUP_C2P, GROUP_IFF, GROUP_CORE):
        native = unpacked[group][len(DISPATCH_V2):len(DISPATCH_V2) + len(bodies[group])]
        if native != bodies[group]:
            raise AssertionError("True native bytes changed after repacking")
    if any(x[:2] != b"\x4e\x71" for x in
           [units[GROUP_IFF][-2:]] if pad_bytes):
        raise AssertionError("Missing NOP test padding")

    return built, {
        "base_sha256": R82_SHA,
        "sha256": sha256(built).hexdigest(),
        "size": len(built),
        "api_commands": len(public_now),
        "ap20_entries": len(segments),
        "units": {k: len(v) for k, v in units.items()},
        "native_lengths": {k: len(v) for k, v in bodies.items()},
        "padding_bytes": pad_bytes,
        "aggregate_units_bytes": sum(map(len, units.values())),
        "rbsr_calls": len(relocations),
        "max_rbsr_displacement": max(abs(v) for v in relocations.values()),
        "palette_links": palette_links,
        "new_cross_group_pc_branches": 0,
        "gate_b_winuae": "NOT TESTED",
        "gate_c_compiler": "NOT TESTED",
    }


class R82ThreeGenuineUnits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = pinned_r82()
        cls.built, cls.info = build_in_memory(cls.base)

    def test_exact_three_genuine_units_over_64k(self):
        self.assertEqual(self.info["units"], {80: 5558, 81: 14508, 82: 52974})
        self.assertEqual(self.info["native_lengths"], {80: 5524, 81: 2474, 82: 52940})
        self.assertEqual(self.info["aggregate_units_bytes"], 73040)
        self.assertGreater(self.info["aggregate_units_bytes"], 65536)
        self.assertEqual(self.info["api_commands"], 74)
        self.assertEqual(self.info["ap20_entries"], 83)

    def test_all_rbsr_interpreter_displacements(self):
        _, segments, _ = unpack_ap20(self.built)
        offsets = starts(segments)
        actual = interpreter_rbsr_displacements(segments)
        self.assertEqual(len(actual), 78)
        self.assertLess(max(map(abs, actual.values())), 32766)
        self.assertIn(0, actual)
        self.assertIn(70, actual)
        self.assertIn(75, actual)
        self.assertIn(79, actual)
        self.assertLess(offsets[GROUP_CORE] - offsets[0], 32766)
        for entry, group in ((0, 82), (69, 82), (70, 80),
                             (74, 80), (75, 81), (76, 82), (79, 82)):
            self.assertEqual(unpack_from(">H", segments[entry], 2)[0], group)

    def test_real_mc68020_all_three_dispatchers(self):
        for entry in (0, 2, 6, 20, 41, 55, 57, 69, 70, 71,
                      72, 73, 74, 75, 76, 77, 78, 79):
            with self.subTest(entry=entry):
                assert_reaches_entry_on_mc68020(self.built, entry)

    def test_palette_long_branches_rebased_and_no_other_mutation(self):
        self.assertEqual(
            [(source, target) for source, target, _, _ in self.info["palette_links"]],
            [(76, 41), (77, 42), (78, 43), (79, 44)])
        for src, dst, old_disp, new_disp in self.info["palette_links"]:
            self.assertEqual(new_disp - old_disp, 7998)
        _, old_parts = unwrap_native_parts_v2(self.base)
        _, body, _ = unpack_ap20(self.built)
        self.assertEqual(body[80][len(DISPATCH_V2):], b"".join(old_parts[70:75]))
        self.assertEqual(
            body[81][len(DISPATCH_V2):len(DISPATCH_V2)+len(old_parts[75])],
            old_parts[75])

    def test_intra_unit_links_do_not_cross_iff_boundary(self):
        _, old_parts = unwrap_native_parts_v2(self.base)
        self.assertEqual(cross_module_pc_branches(old_parts), [])
        broken = list(old_parts)
        original = starts(old_parts)
        faulty = bytearray(broken[75])
        faulty[:4] = pack(">Hh", 0x6100, original[70] - (original[75] + 2))
        broken[75] = bytes(faulty)
        self.assertTrue(any(x[0] == 75 and x[2] == 70
                            for x in cross_module_pc_branches(broken)))

    def test_refuse_illegal_loader_and_oversize(self):
        with self.assertRaisesRegex(ValueError, "ILLEGAL GRouB"):
            build_in_memory(self.base, pad_bytes=35000)
        with self.assertRaises(ValueError):
            build_in_memory(self.base, pad_bytes=65000)
        with self.assertRaises(ValueError):
            build_in_memory(self.base, pad_bytes=1)

    def test_determinism_and_untouched_original_R82(self):
        again, report = build_in_memory(self.base)
        self.assertEqual(self.built, again)
        self.assertEqual(self.info, report)
        self.assertEqual(self.base, pinned_r82())
        no_padding, report2 = build_in_memory(self.base, pad_bytes=0)
        self.assertEqual(report2["aggregate_units_bytes"], 61040)
        self.assertEqual(len(self.built) - len(no_padding), PAD_DEFAULT)

    def test_reject_modified_R82(self):
        altered = bytearray(self.base)
        altered[100] ^= 1
        with self.assertRaisesRegex(ValueError, "immutable LAST_GOOD"):
            build_in_memory(bytes(altered))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(R82ThreeGenuineUnits)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if not result.wasSuccessful():
        raise SystemExit(1)
    binary, details = build_in_memory(pinned_r82())
    print("P5 THREE REAL AP20 UNITS CPU020 STRUCTURAL PASS", details, flush=True)
    if args.output is not None:
        target = args.output.resolve()
        forbidden = [(ROOT / "dist").resolve(),
                     (ROOT / "tests/current").resolve()]
        if (target.name != "AMOSPro_AGA_V3_R82_3UNITS_TEST.Lib" or
                any(parent == target or parent in target.parents
                    for parent in forbidden)):
            raise SystemExit("P5 refuses write outside isolated experiment output")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(binary)
        if sha256(target.read_bytes()).hexdigest() != details["sha256"]:
            raise AssertionError("Emitted P5 .Lib failed checksum")
        print("P5_DISPOSABLE_OUTPUT", target, flush=True)
    if args.emit_base64:
        encoded = base64.b64encode(binary).decode("ascii")
        print("P5_R82_3UNIT_B64_BEGIN", flush=True)
        for at in range(0, len(encoded), 120):
            print("P5_R82_3UNIT_B64", encoded[at:at + 120], flush=True)
        print("P5_R82_3UNIT_B64_END", flush=True)


if __name__ == "__main__":
    main()
