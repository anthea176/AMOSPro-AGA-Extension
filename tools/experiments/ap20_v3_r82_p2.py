#!/usr/bin/env python3
"""P2: append an isolated public MC68020 entry to exact promoted R82, IN MEMORY.

The entire original R82 native monolith is unmodified. Only RBSR stub target
indices are shifted to account for the extra public AP20 entry. A separate
native dispatcher unit pushes aggregate native code beyond 64 KiB.

No .Lib is written, no APSystem slot is modified, and no Compiler Gate C
or WinUAE Gate B is claimed.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from audit_ap20 import inspect, parse, token
from compiler_relocation import RBSR, GETP, repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from active_library import R82_SHA

PROMOTED = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
CURRENT = ROOT / "dist/AMOSPro_AGA.Lib"
R82_NATIVE_STUBS = 80
OLD_GROUP = 80
NEW_PROBE_INDEX = 80
NEW_R82_GROUP = 82
NEW_PROBE_GROUP = 81
PUBLIC_TOKEN = ("aga v3 size probe", 1, NEW_PROBE_INDEX, "0")
PAD_NATIVE_BYTES = 12000
CODE_PROBE = bytes.fromhex("764d49c34e75")  # MOVEQ #77,D3; EXTB.L D3; RTS
NEW_NATIVE = CODE_PROBE + bytes.fromhex("4e71") * ((PAD_NATIVE_BYTES - len(CODE_PROBE)) // 2)
NEW_UNIT = DISPATCH_V2 + NEW_NATIVE
TITLE = b"R82 AP20 V3 TWO-UNIT PROBE - NEVER INSTALL AS LAST_GOOD\0"
TITLE += bytes(len(TITLE) & 1)



def validate_interpreter_rbsr(segments: list[bytes]) -> dict[int, int]:
    """Model AMOS365 +B.s Library_Reloc/GRouB, including its ILLEGAL trap.

    The interpreter patches an RBSR marker into BSR.W; displacement is
    target entry START minus address (stub START + 2), strictly -32766..32766.
    This is independent from the CPU-only absolute-JSR test and MUST pass
    for every RBSR, especially the new entry 80.
    """
    starts = []
    offset = 0
    for item in segments:
        if len(item) & 1:
            raise ValueError("Unaligned AP20 entry")
        starts.append(offset)
        offset += len(item)
    result = {}
    for i, part in enumerate(segments):
        if not part.startswith(RBSR):
            continue
        if len(part) not in (8, 12) or part[6:8] != bytes.fromhex("4e75"):
            raise ValueError("Unrecognized RBSR marker")
        target = unpack_from(">H", part, 2)[0]
        if target >= len(segments) or not segments[target].startswith(DISPATCH_V2):
            raise ValueError("Bad RBSR dispatcher target at entry %d" % i)
        displacement = starts[target] - (starts[i] + 2)
        if not -32766 < displacement < 32766 or displacement & 1:
            raise ValueError("AMOS365 GRouB ILLEGAL: BSR.W out of range at %d: %d" %
                             (i, displacement))
        result[i] = displacement
    if NEW_PROBE_INDEX not in result or 0 not in result:
        raise ValueError("Missing mandatory native entry relocations")
    return result


def r82_bytes() -> bytes:
    """Historical P2 source is frozen R82, independently of active P5."""
    promoted = PROMOTED.read_bytes()
    if len(promoted) != 64112 or sha256(promoted).hexdigest() != R82_SHA:
        raise ValueError("R82 original LAST_GOOD source mismatch")
    return promoted


def build_in_memory(promoted: bytes) -> tuple[bytes, dict]:
    if sha256(promoted).hexdigest() != R82_SHA:
        raise ValueError("Refusing non-promoted R82 ancestor")
    tokens, original, _ = unpack_ap20(promoted)
    if len(original) != R82_NATIVE_STUBS + 1 or not original[-1].startswith(DISPATCH_V2):
        raise ValueError("R82 monolith has an unexpected AP20 layout")
    if tokens[-6:] != bytes(6):
        raise ValueError("Missing canonical token terminator")

    old_unit = original[-1]
    if len(old_unit) != 60972 or len(old_unit) > 65534:
        raise ValueError("R82 single-unit size drift")
    if len(NEW_UNIT) != 12034:
        raise ValueError("Experimental second unit size drift")
    if len(old_unit) + len(NEW_UNIT) <= 65536:
        raise ValueError("This probe does not exceed 64 KiB")

    existing_stubs = original[:-1]
    rebased = []
    for i, stub in enumerate(existing_stubs):
        if stub in (b"", GETP):
            rebased.append(stub)
            continue
        if (len(stub) not in (8, 12) or stub[:4] != RBSR + pack(">H", OLD_GROUP)
                or stub[6:8] != bytes.fromhex("4e75")
                or (len(stub) == 12 and stub[8:] != GETP)):
            raise ValueError("Unexpected R82 old RBSR stub %d" % i)
        rebased.append(stub[:2] + pack(">H", NEW_R82_GROUP) + stub[4:])

    new_stub = RBSR + pack(">HH", NEW_PROBE_GROUP, 0) + bytes.fromhex("4e75")
    ntokens = tokens[:-6] + token(*PUBLIC_TOKEN) + bytes(6)
    segments = rebased + [new_stub, NEW_UNIT, old_unit]
    relocations = validate_interpreter_rbsr(segments)
    image = repack_ap20(promoted, ntokens, segments, TITLE)
    parsed_tokens, built, name = unpack_ap20(image)
    if (parsed_tokens != ntokens or built != segments or name != TITLE
            or built[NEW_R82_GROUP] != old_unit or built[NEW_PROBE_GROUP] != NEW_UNIT):
        raise AssertionError("Multi-unit R82 AP20 roundtrip mismatch")

    audit = inspect(parse(image))
    if audit["issues"]:
        raise AssertionError(("AP20 token/parameter audit", audit["issues"]))
    baseline = inspect(parse(promoted))
    old_names = [t["name"] for t in baseline["tokens"] if t["name"].startswith("aga ")]
    new_names = [t["name"] for t in audit["tokens"] if t["name"].startswith("aga ")]
    if len(old_names) != 74 or new_names != old_names + [PUBLIC_TOKEN[0]]:
        raise AssertionError("R82 public tokens changed or probe missing")
    if len(built) != 83:
        raise AssertionError("Unexpected R82+probe entry count")
    for before, after in zip(existing_stubs, rebased):
        if before not in (b"", GETP):
            if after != before[:2] + pack(">H", NEW_R82_GROUP) + before[4:]:
                raise AssertionError("Existing R82 RBSR changed beyond target index")
        elif before != after:
            raise AssertionError("R82 marker mutated")
    return image, {
        "r82_sha256": R82_SHA,
        "r82_monolith_bytes": len(old_unit),
        "new_unit_bytes": len(NEW_UNIT),
        "sum_native_units_bytes": len(old_unit) + len(NEW_UNIT),
        "total_file_bytes": len(image),
        "tokens": len(new_names),
        "ap20_entries": len(built),
        "probe_entry": NEW_PROBE_INDEX,
        "probe_native_group": NEW_PROBE_GROUP,
        "max_interpreter_bsr_displacement": max(abs(d) for d in relocations.values()),
        "interpreter_rbsr_count": len(relocations),
        "cpu": "MC68020+",
        "winuae_gate_b": "NOT TESTED",
        "compiler_gate_c": "NOT TESTED",
    }


def call_probe_on_mc68020(candidate: bytes) -> None:
    """Execute the REAL interpreter-style BSR.W after GRouB-style patching."""
    from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
    from unicorn.m68k_const import (
        UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
        UC_M68K_REG_A7, UC_M68K_REG_A0, UC_M68K_REG_D0,
        UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_A5,
    )
    _, parts, _ = unpack_ap20(candidate)
    stub = parts[NEW_PROBE_INDEX]
    if stub != RBSR + pack(">HH", NEW_PROBE_GROUP, 0) + bytes.fromhex("4e75"):
        raise ValueError("Wrong public probe stub")
    relocations = validate_interpreter_rbsr(parts)
    starts = []
    pos = 0
    for item in parts:
        starts.append(pos)
        pos += len(item)
    base, stop, sp = 0x100000, 0x20000, 0x500000
    original = b"".join(parts)
    machine = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    machine.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    machine.mem_map(0, 0x600000)
    machine.mem_write(base, original)
    # Match AMOS365: replace RBSR with actual BSR.W + 16-bit displacement.
    for i, delta in relocations.items():
        machine.mem_write(base + starts[i], pack(">Hh", 0x6100, delta))
    machine.mem_write(stop, bytes.fromhex("4e71"))
    machine.mem_write(sp, pack(">I", stop))
    regs = {UC_M68K_REG_A0: 0x1b0000, UC_M68K_REG_A5: 0x1c0000,
            UC_M68K_REG_D0: 0xaabbccdd, UC_M68K_REG_D2: 0x12345678}
    for reg, value in regs.items():
        machine.reg_write(reg, value)
    machine.reg_write(UC_M68K_REG_D3, 0)
    machine.reg_write(UC_M68K_REG_SR, 0x2000)
    machine.reg_write(UC_M68K_REG_A7, sp)
    expected = base + starts[NEW_PROBE_GROUP] + len(DISPATCH_V2)
    visits = []
    def hook(_machine, pc, _size, _user):
        if pc == expected:
            visits.append(pc)
    machine.hook_add(UC_HOOK_CODE, hook)
    machine.emu_start(base + starts[NEW_PROBE_INDEX], stop, count=300)
    assert visits == [expected], "Real BSR.W did not reach MC68020 native unit"
    assert machine.reg_read(UC_M68K_REG_PC) == stop
    assert machine.reg_read(UC_M68K_REG_A7) == sp + 4
    assert machine.reg_read(UC_M68K_REG_D3) == 77
    assert all(machine.reg_read(reg) == value for reg, value in regs.items())
    # Native code was not modified, unlike the RBSR stubs patched by AMOS.
    for group in (NEW_R82_GROUP, NEW_PROBE_GROUP):
        assert machine.mem_read(base + starts[group], len(parts[group])) == parts[group]




class PromotedR82TwoUnitP2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = r82_bytes()
        cls.candidate, cls.meta = build_in_memory(cls.source)

    def test_base_r82_exact_and_all_public_tokens_preserved(self):
        self.assertEqual(self.meta["r82_monolith_bytes"], 60972)
        self.assertEqual(self.meta["tokens"], 75)
        self.assertEqual(self.meta["ap20_entries"], 83)

    def test_total_beyond_64k_both_units_bounded(self):
        self.assertEqual(self.meta["sum_native_units_bytes"], 73006)
        self.assertEqual(self.meta["new_unit_bytes"], 12034)
        self.assertGreater(self.meta["sum_native_units_bytes"], 65536)
        self.assertLessEqual(self.meta["r82_monolith_bytes"], 65534)
        self.assertLessEqual(self.meta["new_unit_bytes"], 65534)

    def test_new_public_probe_dispatches_on_mc68020(self):
        call_probe_on_mc68020(self.candidate)

    def test_interpreter_bsr_all_entries_in_range(self):
        _, parts, _ = unpack_ap20(self.candidate)
        relocs = validate_interpreter_rbsr(parts)
        self.assertGreater(len(relocs), 60)
        self.assertEqual(relocs[NEW_PROBE_INDEX], 6)
        self.assertLess(self.meta["max_interpreter_bsr_displacement"], 32766)
        self.assertEqual(self.meta["interpreter_rbsr_count"], len(relocs))

    def test_interpreter_rejects_old_crashing_layout(self):
        _, parts, _ = unpack_ap20(self.candidate)
        wrong = [bytes(part) for part in parts]
        for i in range(R82_NATIVE_STUBS):
            s = wrong[i]
            if s.startswith(RBSR):
                wrong[i] = s[:2] + pack(">H", OLD_GROUP+1) + s[4:]
        s = wrong[NEW_PROBE_INDEX]
        wrong[NEW_PROBE_INDEX] = s[:2] + pack(">H", OLD_GROUP+2) + s[4:]
        wrong[NEW_R82_GROUP], wrong[NEW_PROBE_GROUP] = (
            wrong[NEW_PROBE_GROUP], wrong[NEW_R82_GROUP])
        with self.assertRaisesRegex(ValueError, "BSR.W out of range"):
            validate_interpreter_rbsr(wrong)

    def test_deterministic_no_overwrite(self):
        candidate, info = build_in_memory(self.source)
        self.assertEqual(candidate, self.candidate)
        self.assertEqual(info, self.meta)
        self.assertEqual(r82_bytes(), self.source)

    def test_rejects_bad_base_without_silent_repair(self):
        corrupt = bytearray(self.source)
        corrupt[56] ^= 1
        with self.assertRaises(ValueError):
            build_in_memory(bytes(corrupt))


if __name__ == "__main__":
    unittest.main(verbosity=2)
