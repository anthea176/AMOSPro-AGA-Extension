#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-backed UNIT142 MC68020: exact P2d staging and isolated edit gate.

The audit export supplies only candidate mnemonic spelling. The authoritative
bytes are the SHA-pinned, emitter-built P2d AP20 unit. Neither this tool nor
the direct assembler writes into dist/ or changes an AMOS campaign.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory

from active_library import P2D_SHA
from compiler_relocation import unpack_ap20

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "src/asm_migration/m19_p2d/M19_P2D_UNIT142_MC68020.s"
NATIVE_DIR = ROOT / "src/native/m19_p2d"
WRAPPER = NATIVE_DIR / "M19_P2D_UNIT142_EDITABLE.s"
STAGED_NAME = "M19_P2D_UNIT142_MC68020.s"
MASTER_NAME = "M19_P2D_AP20_SOURCE.s"
GROUP_SIZE = 0xF514
GROUP_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"
ANNOT = re.compile(r"\s+;\s+\+\$([A-F0-9]{5}): ([A-F0-9]+)\s*$")
LABEL = re.compile(r"[A-Za-z_][A-Za-z_0-9]*:\s*$")

# (file, start label, end label, start, end, instructions, inner labels,
#  mutable symbol, baseline, edit, mnemonic to replace, replacement,
#  differing byte offset within UNIT142, old byte, new byte)
SPANS = (
    (
        "M19_UNIT142_DISPATCH_V2_MC68020.s",
        "UNIT_UNIT142:\n", "ENTRY_UNIT142_00022:\n",
        0x00000, 0x00022, 11, 0,
        "UNIT142_DISPATCH_STACK", 4, 3,
        "    subq.l #4,a7", "    subq.l #UNIT142_DISPATCH_STACK,a7",
        0x00000, 0x59, 0x57,
    ),
    (
        "M19_UNIT142_INIT_ENTRY_MC68020.s",
        "ENTRY_UNIT142_00022:\n", "L_UNIT142_0005A:\n",
        0x00022, 0x0005A, 17, 2,
        "UNIT142_INIT_COUNT", 9, 10,
        "    moveq #9,d0", "    moveq #UNIT142_INIT_COUNT,d0",
        0x00045, 9, 10,
    ),
    (
        "M19_UNIT142_GRAPHICS_GUARD_MC68020.s",
        "ENTRY_UNIT142_002C2:\n", "L_UNIT142_0030C:\n",
        0x002C2, 0x0030C, 28, 2,
        "UNIT142_GRAPHICS_INITIAL_D3", 0, 1,
        "    moveq #0,d3", "    moveq #UNIT142_GRAPHICS_INITIAL_D3,d3",
        0x002CD, 0, 1,
    ),
    (
        "M19_UNIT142_GRAPHICS_SCREEN_MC68020.s",
        "ENTRY_UNIT142_00322:\n", "L_UNIT142_00448:\n",
        0x00322, 0x00448, 86, 5,
        "UNIT142_SCREEN_INITIAL_D3", 0, 1,
        "    moveq #0,d3", "    moveq #UNIT142_SCREEN_INITIAL_D3,d3",
        0x00327, 0, 1,
    ),
)


class Unit142Error(ValueError):
    pass


def demand(condition, message):
    if not condition:
        raise Unit142Error(message)


def strip_annotations(text):
    lines = []
    for line in text.splitlines():
        match = ANNOT.search(line)
        lines.append(line[:match.start()].rstrip() if match else line)
    return "\n".join(lines) + "\n"


def expected_sources():
    audit = AUDIT.read_text("ascii")
    # Validate all 62,740 native bytes in order, not just the changed slices.
    whole = bytearray()
    annotations = 0
    for line in audit.splitlines():
        match = ANNOT.search(line)
        if match is None:
            continue
        demand(int(match.group(1), 16) == len(whole),
               "UNIT142 original audit offset discontinuity")
        whole.extend(bytes.fromhex(match.group(2)))
        annotations += 1
    demand(annotations == 14693 and len(whole) == GROUP_SIZE and
           sha256(whole).hexdigest() == GROUP_SHA,
           "UNIT142 complete SHA-pinned native group changed")

    wrapper = strip_annotations(audit)
    marker = "; AGA_NATIVE_PURPOSE: AUDIT_ONLY"
    demand(wrapper.count(marker) == 1, "UNIT142 audit marker missing")
    wrapper = wrapper.replace(
        marker, "; PARTIAL_SOURCE_MIGRATION: UNIT142 pinned MC68020 code, audit remainder"
    ).replace(
        "; PARTIAL MC68020 MNEMONIC RESTORATION (not an installable .Lib)",
        "; Selected native spans source-owned; remaining legacy mnemonics/data pinned"
    )

    modules = []
    for (filename, start, stop, lo, hi, instruction_count, label_count,
         symbol, old_value, new_value, opcode, replacement,
         diff, old_byte, new_byte) in SPANS:
        begin = audit.find(start)
        end = audit.find(stop, begin + len(start))
        demand(begin >= 0 and end > begin and
               audit.find(start, begin + len(start)) < 0,
               "UNIT142 source boundaries absent/ambiguous: " + filename)
        fragment = audit[begin+len(start):end]
        lines, at, instructions, labels = [], lo, 0, 0
        for line in fragment.splitlines():
            if not line.strip():
                continue
            if LABEL.fullmatch(line):
                labels += 1
                lines.append(line)
                continue
            match = ANNOT.search(line)
            demand(match is not None and int(match.group(1), 16) == at and
                   not line.lstrip().lower().startswith("dc."),
                   "UNIT142 unclassified data/misaligned code: " + filename)
            at += len(bytes.fromhex(match.group(2)))
            instructions += 1
            lines.append(line[:match.start()].rstrip())
        demand(at == hi and instructions == instruction_count and
               labels == label_count and
               whole[diff] == old_byte and lo <= diff < hi,
               "UNIT142 source byte/label/extension count drift: " + filename)
        code = "\n".join(lines).rstrip() + "\n"
        demand(code.count(opcode) == 1 and
               new_value != old_value,
               "UNIT142 edit constant ambiguous: " + filename)
        header = (
            "; AGA_NATIVE_MIN_CPU: MC68020\n"
            "; UNIT142 " + filename + " source-verified against pinned P2d emitter.\n"
            f"; UNIT142+${lo:05X}..${hi:05X}, {hi-lo} instructions/data bytes.\n"
            + symbol + f" equ {old_value}\n\n"
        )
        module = header + code.replace(opcode, replacement)
        original_fragment = strip_annotations(fragment)
        target = start + original_fragment
        demand(wrapper.count(target) == 1,
               "UNIT142 wrapper region missing/ambiguous: " + filename)
        wrapper = wrapper.replace(
            target, start + '    include "' + filename + '"\n'
        )
        modules.append((lo, hi, filename, module))
    return bytes(whole), wrapper, modules


def verify(official):
    demand(len(official) == 136020 and
           sha256(official).hexdigest() == P2D_SHA,
           "UNIT142 official P2d source builder SHA differs")
    native, wrapper, modules = expected_sources()
    tokens, groups, title = unpack_ap20(official)
    matches = [i for i, g in enumerate(groups)
               if len(g) == GROUP_SIZE and sha256(g).hexdigest() == GROUP_SHA]
    demand(len(matches) == 1 and
           groups[matches[0]] == native,
           "UNIT142 absent/ambiguous in authoritative P2d AP20")
    for lo, hi, filename, source in modules:
        demand(groups[matches[0]][lo:hi] == native[lo:hi],
               "UNIT142 source slice mismatch: " + filename)
        demand((NATIVE_DIR / filename).read_text("ascii") == source,
               "UNIT142 editable source differs from pinned proof: " + filename)
    demand(WRAPPER.read_text("ascii") == wrapper,
           "UNIT142 native wrapper not derived exactly from pinned source")
    print("UNIT142_SOURCE_PROVEN: 458 bytes / 4 MC68020 modules, AP20 group",
          matches[0], "unit", len(native))
    return matches[0]


def stage(folder, official):
    verify(official)
    (folder / STAGED_NAME).write_bytes(WRAPPER.read_bytes())
    for filename, *_ in SPANS:
        (folder / filename).write_bytes((NATIVE_DIR / filename).read_bytes())


def edit_gate(staged, assembler):
    official = (staged / "M19_P2D_ASM_REBUILT_CHECK.Lib").read_bytes()
    group = verify(official)
    demand((staged / STAGED_NAME).is_file() and
           (staged / MASTER_NAME).is_file() and
           all((staged / spec[0]).is_file() for spec in SPANS),
           "UNIT142 staged source missing")
    with TemporaryDirectory(prefix="unit142_mc68020_edit_") as temp:
        folder = Path(temp)
        for source in staged.glob("*.s"):
            shutil.copy2(source, folder / source.name)
        for (filename, _start, _stop, _lo, _hi, _inst, _labels,
             symbol, old_value, new_value, _opcode, _replacement,
             _diff, _old, _new) in SPANS:
            path = folder / filename
            text = path.read_text("ascii")
            before = symbol + " equ " + str(old_value)
            demand(text.count(before) == 1,
                   "UNIT142 mutation not unique: " + filename)
            path.write_text(text.replace(
                before, symbol + " equ " + str(new_value)),
                encoding="ascii", newline="\n")
        output = folder / "UNIT142_EDITED_UNTESTED.Lib"
        command = [str(assembler.resolve()), "-Fbin", "-m68020",
                   "-no-opt", "-quiet", "-o", str(output), MASTER_NAME]
        result = subprocess.run(command, cwd=folder, capture_output=True,
                                text=True, check=False)
        demand(result.returncode == 0,
               "UNIT142 vasm edit failed: " + result.stderr)
        edited = output.read_bytes()
        tok0, units0, title0 = unpack_ap20(official)
        tok1, units1, title1 = unpack_ap20(edited)
        demand(len(edited) == len(official) and tok0 == tok1 and
               title0 == title1 and len(units0) == len(units1) and
               all(a == b for i, (a, b) in enumerate(zip(units0, units1))
                   if i != group), "UNIT142 edit corrupted unrelated AP20")
        base, changed = units0[group], units1[group]
        deltas = [i for i, (a, b) in enumerate(zip(base, changed)) if a != b]
        expected = {spec[12]: (spec[13], spec[14]) for spec in SPANS}
        demand(deltas == sorted(expected) and
               all((base[i], changed[i]) == pair
                   for i, pair in expected.items()),
               "UNIT142 four one-byte edits escaped expected offsets")
    print("UNIT142_EDIT_TEST_PASS: 4 exact bytes, only UNIT142, no AP20 drift")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    opts = parser.add_mutually_exclusive_group(required=True)
    opts.add_argument("--check", action="store_true")
    opts.add_argument("--self-test-edit", action="store_true")
    parser.add_argument("--staged", type=Path)
    parser.add_argument("--vasm", type=Path)
    args = parser.parse_args()
    if args.self_test_edit:
        demand(args.staged is not None and args.vasm is not None,
               "--self-test-edit requires --staged and --vasm")
        edit_gate(args.staged, args.vasm)
    else:
        from build_m19_p2d_editable_asm import prove_source_provenance
        verify(prove_source_provenance()[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
