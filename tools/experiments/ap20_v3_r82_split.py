#!/usr/bin/env python3
"""P4: split the ACTUAL R82 native body into C2P and AGA+palettes AP20 units.

This is an experimental, MC68020+ library, not R82 LAST_GOOD, and not a
claim of WinUAE or Compiler support. Only source-backed relative links are
rewritten. 12 KiB of unreachable NOP padding stresses the >64-KiB boundary.
Build never touches dist/, tests/current/, main, or promoted R82 files.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path
from struct import pack, pack_into, unpack_from
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

CURRENT = ROOT / "dist/AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_PUBLIC = 80
C2P_GROUP = 80
AGA_GROUP = 81
C2P_INDICES = frozenset(range(70, 76))
PAD_DEFAULT = 12000
PAD_MAX = 65534
EXPECTED_AGA_CORE = 49828
EXPECTED_C2P_NATIVE = 7998
EXPECTED_PALETTES = 3112
# (source public entry, native BSR.L instruction offset, legacy target entry)
# From R82 source emitters, checked against original binary before patch.
PALETTE_LINKS = ((76, 90, 41), (77, 90, 42), (78, 146, 43),
                 (79, 174, 44))
TITLE = (b"AMOSPro AGA R82 TRUE SPLIT C2P/AGA V3 EXPERIMENT - NOT LAST_GOOD\0"
         b"$VER: AP20 V3 R82 split EXPERIMENT\0")
TITLE += bytes(len(TITLE) & 1)


def pinned_r82() -> bytes:
    """Use frozen R82 LAST_GOOD as build source; active dist may be P5."""
    protected = LAST_GOOD.read_bytes()
    if len(protected) != 64112 or sha256(protected).hexdigest() != R82_SHA:
        raise ValueError("R82 LAST_GOOD frozen source mismatch")
    return protected


def starts(parts: list[bytes]) -> list[int]:
    result, offset = [], 0
    for p in parts:
        if len(p) & 1:
            raise ValueError("Misaligned AP20 native entry")
        result.append(offset)
        offset += len(p)
    return result


def interpreter_rbsr_displacements(segments: list[bytes]) -> dict[int, int]:
    """Reproduce +B.s GRouB: target(entry) - (stub_start+2), signed BSR.W."""
    offsets = starts(segments)
    result = {}
    for i, stub in enumerate(segments):
        if not stub.startswith(RBSR):
            continue
        if len(stub) not in (8, 12) or stub[6:8] != bytes.fromhex("4e75"):
            raise ValueError(f"Unknown RBSR syntax in entry {i}")
        if len(stub) == 12 and stub[8:] != GETP:
            raise ValueError(f"Malformed GetP marker at entry {i}")
        target = unpack_from(">H", stub, 2)[0]
        if target >= len(segments) or not segments[target].startswith(DISPATCH_V2):
            raise ValueError(f"Invalid RBSR target group at entry {i}")
        displacement = offsets[target] - (offsets[i] + 2)
        if not -32766 < displacement < 32766 or displacement & 1:
            raise ValueError(
                f"AMOS365 ILLEGAL GRouB: entry {i} displacement {displacement}")
        result[i] = displacement
    if 0 not in result or 70 not in result or 76 not in result:
        raise ValueError("Missing live public RBSR stubs")
    return result


def remap_palette_links(old_parts: list[bytes]) -> tuple[list[bytes], list[tuple]]:
    """Patch only the four SOURCE-AUDITED 68020 BSR.L palette links.

    Original targets are checked byte-exactly before changing the displacement.
    Reject an unexpected caller, opcode, target, or native entry size.
    """
    original_offsets = starts(old_parts)
    core_indices = [*range(70), *range(76, 80)]
    new_core_offsets = starts([old_parts[i] for i in core_indices])
    new_offset = dict(zip(core_indices, new_core_offsets))
    changed, report = list(old_parts), []
    for entry, insn, target in PALETTE_LINKS:
        old = old_parts[entry]
        if old[insn:insn + 2] != bytes.fromhex("61ff"):
            raise ValueError(f"R82 BSR.L instruction missing: {entry}:{insn}")
        old_disp = unpack_from(">i", old, insn + 2)[0]
        absolute_target = original_offsets[entry] + insn + 2 + old_disp
        if absolute_target != original_offsets[target]:
            raise ValueError(f"Original R82 palette link {entry}->{target} drift")
        new_disp = new_offset[target] - (new_offset[entry] + insn + 2)
        patched = bytearray(old)
        pack_into(">i", patched, insn + 2, new_disp)
        if new_offset[entry] + insn + 2 + unpack_from(">i", patched, insn + 2)[0] != new_offset[target]:
            raise AssertionError("BSR.L failed to reach the new legacy target")
        changed[entry] = bytes(patched)
        if len(changed[entry]) != len(old):
            raise AssertionError("Palette entry length changed")
        report.append((entry, target, old_disp, new_disp))
    if [i for i in range(80) if changed[i] != old_parts[i]] != [76, 77, 78, 79]:
        raise AssertionError("Unexpected R82 native mutations")
    return changed, report


def build_in_memory(source: bytes, *, pad_bytes: int = PAD_DEFAULT):
    """Build two genuine native modules, preserving every public R82 token."""
    if sha256(source).hexdigest() != R82_SHA:
        raise ValueError("Refusing non-pinned R82 source")
    if pad_bytes < 0 or pad_bytes > PAD_MAX or pad_bytes & 1:
        raise ValueError("Invalid experimental padding")
    tokens, old_parts = unwrap_native_parts_v2(source)
    if len(old_parts) != BASE_PUBLIC or tokens[-6:] != bytes(6):
        raise ValueError("Unexpected R82 public AP20 table")
    # The historical core has all known cross-entry BSR.W, BRA.W and state.
    assert_native_links(old_parts[:70])
    check_cross_r74(old_parts[:70])
    if state_offset(old_parts) != 12070:
        raise ValueError("R82 State layout changed")
    for entry, off, opcode in SITES:
        if old_parts[entry][off:off + 4] != pack(">HH", opcode, 12070):
            raise ValueError(f"R82 static input-state LEA drift: {entry}:{off}")
    if (sum(map(len, old_parts[:70])) != EXPECTED_AGA_CORE
            or sum(map(len, old_parts[70:76])) != EXPECTED_C2P_NATIVE
            or sum(map(len, old_parts[76:80])) != EXPECTED_PALETTES):
        raise ValueError("Unexpected R82 native family boundary")

    new_parts, link_report = remap_palette_links(old_parts)
    assert_native_links(new_parts[:70])
    check_cross_r74(new_parts[:70])
    if state_offset(new_parts) != 12070:
        raise ValueError("Native static input state unexpectedly moved")
    c2p_body = b"".join(new_parts[70:76])
    core_body = b"".join(new_parts[:70] + new_parts[76:])
    padded_c2p = c2p_body + bytes.fromhex("4e71") * (pad_bytes // 2)
    c2p_unit = DISPATCH_V2 + padded_c2p
    aga_unit = DISPATCH_V2 + core_body
    if len(c2p_unit) > 65534 or len(aga_unit) > 65534:
        raise ValueError("AMOS Compiler V2 individual unit exceeds 16-bit size")
    if pad_bytes and len(c2p_unit) + len(aga_unit) <= 65536:
        raise ValueError("Stress candidate must exceed aggregate 64 KiB")

    # Each unit's offsets are relative to its OWN 34-byte native dispatcher.
    core_indices = [*range(70), *range(76, 80)]
    core_offsets = dict(zip(core_indices, starts([new_parts[i] for i in core_indices])))
    c2p_offsets = dict(zip(range(70, 76), starts(new_parts[70:76])))
    layout = {}
    stubs = []
    for i, body in enumerate(old_parts):
        group, off = ((C2P_GROUP, c2p_offsets[i]) if i in C2P_INDICES
                      else (AGA_GROUP, core_offsets[i]))
        layout[i] = (group, off)
        if body in (b"", GETP):
            stubs.append(body)
        else:
            if off & 1 or off > 65535:
                raise ValueError("Native entry has invalid 16-bit unit offset")
            stub = RBSR + pack(">HH", group, off) + bytes.fromhex("4e75")
            if body.endswith(GETP):
                stub += GETP
            stubs.append(stub)
    segments = stubs + [c2p_unit, aga_unit]
    displacements = interpreter_rbsr_displacements(segments)
    image = repack_ap20(source, tokens, segments, TITLE)
    new_tokens, rebuilt, return_title = unpack_ap20(image)
    if new_tokens != tokens or rebuilt != segments or return_title != TITLE:
        raise AssertionError("Split AP20 packing roundtrip failed")
    issue_report = inspect(parse(image))
    if issue_report["issues"]:
        raise AssertionError(("Token/GetP ABI", issue_report["issues"]))
    previous = inspect(parse(source))
    pub_before = [t for t in previous["tokens"] if t["name"].startswith("aga ")]
    pub_after = [t for t in issue_report["tokens"] if t["name"].startswith("aga ")]
    if len(pub_before) != 74 or pub_after != pub_before:
        raise AssertionError("R82 API name/indices/signatures changed")
    if rebuilt[AGA_GROUP][len(DISPATCH_V2):] != core_body:
        raise AssertionError("Core bytes changed unexpectedly")
    if rebuilt[C2P_GROUP][len(DISPATCH_V2):len(DISPATCH_V2) + len(c2p_body)] != c2p_body:
        raise AssertionError("C2P bytes changed unexpectedly")
    return image, {
        "base_sha256": R82_SHA,
        "size": len(image),
        "sha256": sha256(image).hexdigest(),
        "api_commands": 74,
        "ap20_entries": len(segments),
        "c2p_group": C2P_GROUP,
        "aga_group": AGA_GROUP,
        "c2p_original_bytes": len(c2p_body),
        "aga_original_bytes": len(core_body),
        "c2p_unit_bytes": len(c2p_unit),
        "aga_unit_bytes": len(aga_unit),
        "aggregate_native_units": len(c2p_unit) + len(aga_unit),
        "padding_bytes": pad_bytes,
        "rbsr_calls": len(displacements),
        "max_interpreter_bsr_displacement": max(map(abs, displacements.values())),
        "palette_relative_links_rebased": link_report,
        "gate_b_winuae": "NOT TESTED",
        "gate_c_compiler": "NOT TESTED",
    }


def assert_reaches_entry_on_mc68020(image: bytes, index: int) -> None:
    """Real MC68020 BSR.W + native V2 dispatcher, stop before handler body.

    This does NOT run the target's actual AGA/C2P function; WinUAE must.
    """
    from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
    from unicorn.m68k_const import (
        UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
        UC_M68K_REG_A7, UC_M68K_REG_D3,
    )
    _, parts, _ = unpack_ap20(image)
    positions = starts(parts)
    links = interpreter_rbsr_displacements(parts)
    if index not in links:
        raise ValueError("No public RBSR link for requested entry")
    stub = parts[index]
    group, off = unpack_from(">HH", stub, 2)
    base, stack = 0x100000, 0x400000
    machine = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    machine.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    machine.mem_map(0, 0x500000)
    machine.mem_write(base, b"".join(parts))
    for number, relative in links.items():
        machine.mem_write(base + positions[number], pack(">Hh", 0x6100, relative))
    target = base + positions[group] + len(DISPATCH_V2) + off
    hits = []
    def trace(cpu, pc, _size, _data):
        if pc == target:
            hits.append(pc)
            cpu.emu_stop()
    machine.hook_add(UC_HOOK_CODE, trace)
    machine.reg_write(UC_M68K_REG_SR, 0x2000)
    machine.reg_write(UC_M68K_REG_A7, stack)
    machine.reg_write(UC_M68K_REG_D3, off)
    machine.emu_start(base + positions[index], target + 2, count=180)
    if hits != [target]:
        raise AssertionError(f"68020 dispatcher failed for entry {index}")


class GenuineR82ModuleSplit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = pinned_r82()
        cls.image, cls.meta = build_in_memory(cls.source)

    def test_true_two_unit_layout_over_64k(self):
        self.assertEqual(self.meta["c2p_unit_bytes"], 20032)
        self.assertEqual(self.meta["aga_unit_bytes"], 52974)
        self.assertEqual(self.meta["aggregate_native_units"], 73006)
        self.assertGreater(self.meta["size"], 65536)
        self.assertEqual(self.meta["ap20_entries"], 82)
        self.assertEqual(self.meta["api_commands"], 74)

    def test_boot_interpreter_relocation_bounds(self):
        _, parts, _ = unpack_ap20(self.image)
        links = interpreter_rbsr_displacements(parts)
        self.assertEqual(self.meta["rbsr_calls"], len(links))
        self.assertLess(self.meta["max_interpreter_bsr_displacement"], 32766)
        self.assertIn(0, links)
        self.assertIn(70, links)
        self.assertIn(79, links)
        self.assertLess(abs(links[79]), 32766)

    def test_palette_cross_entry_bsr_l_recalculated(self):
        for source, target, old, new in self.meta["palette_relative_links_rebased"]:
            self.assertEqual(source - target > 0, True)
            self.assertEqual(new - old, EXPECTED_C2P_NATIVE)
        self.assertEqual(
            [(a, b) for a, b, _, _ in self.meta["palette_relative_links_rebased"]],
            [(76, 41), (77, 42), (78, 43), (79, 44)])

    def test_68020_real_dispatchers_core_c2p_and_palette(self):
        for index in (0, 6, 20, 41, 55, 57, 70, 71, 72, 73, 74, 75,
                      76, 77, 78, 79):
            with self.subTest(index=index):
                assert_reaches_entry_on_mc68020(self.image, index)

    def test_refuse_oversize_or_out_of_range(self):
        with self.assertRaisesRegex(ValueError, "ILLEGAL GRouB"):
            build_in_memory(self.source, pad_bytes=30000)
        with self.assertRaises(ValueError):
            build_in_memory(self.source, pad_bytes=1)

    def test_all_source_metadata_preserved_and_deterministic(self):
        again, report = build_in_memory(self.source)
        self.assertEqual(self.image, again)
        self.assertEqual(self.meta, report)
        self.assertEqual(pinned_r82(), self.source)
        nopad, no_pad_meta = build_in_memory(self.source, pad_bytes=0)
        self.assertEqual(no_pad_meta["aggregate_native_units"], 61006)
        self.assertLess(len(nopad), len(self.image))

    def test_refuse_corrupt_original(self):
        altered = bytearray(self.source)
        altered[120] ^= 1
        with self.assertRaises(ValueError):
            build_in_memory(bytes(altered))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true",
                        help="Emit a CI-artifact reconstruction source, not installed")
    parser.add_argument("--output", type=Path, help="Explicit disposable file only")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GenuineR82ModuleSplit)
    success = unittest.TextTestRunner(verbosity=2).run(suite)
    if not success.wasSuccessful():
        raise SystemExit(1)
    image, meta = build_in_memory(pinned_r82())
    print("R82 TRUE TWO-MODULE HOST GATE A PASS", meta, flush=True)
    if args.output:
        dest = args.output.resolve()
        forbidden = [(ROOT / "dist").resolve(), (ROOT / "tests/current").resolve()]
        if (dest.name != "AMOSPro_AGA_V3_R82_SPLIT_TEST.Lib"
                or any(dest == base or base in dest.parents for base in forbidden)):
            raise SystemExit("Refusing output outside explicitly named safe test location")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(image)
        if sha256(dest.read_bytes()).hexdigest() != meta["sha256"]:
            raise SystemExit("Output differs from validated candidate")
        print("EXPERIMENTAL_OUTPUT", dest, flush=True)
    if args.emit_base64:
        encoded = base64.b64encode(image).decode("ascii")
        print("R82_SPLIT_V3_B64_BEGIN", flush=True)
        for pos in range(0, len(encoded), 120):
            print("R82_SPLIT_V3_B64", encoded[pos:pos + 120], flush=True)
        print("R82_SPLIT_V3_B64_END", flush=True)


if __name__ == "__main__":
    main()
