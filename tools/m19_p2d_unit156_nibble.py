#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-backed UNIT156 nibble module: builder provenance and exact assembly."""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from shutil import copy2
import re
import subprocess
from tempfile import TemporaryDirectory

from active_library import P2D_SHA
from compiler_relocation import unpack_ap20

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "src/asm_migration/m19_p2d/M19_P2D_UNIT156_MC68020.s"
NATIVE = ROOT / "src/native/m19_p2d/M19_P2D_UNIT156_EDITABLE.s"
MODULE = ROOT / "src/native/m19_p2d/M19_UNIT156_NIBBLE_MC68020.s"
MODULE2 = ROOT / "src/native/m19_p2d/M19_UNIT156_DOS_GUARD_MC68020.s"
STAGED_NAME = "M19_P2D_UNIT156_MC68020.s"
MASTER_NAME = "M19_P2D_AP20_SOURCE.s"
MODULE_NAME = MODULE.name
MODULE2_NAME = MODULE2.name
SECOND, SECOND_END = 0x0099E, 0x009C8
SECOND_MARK = 'L_UNIT156_0099E:\n'
SECOND_END_MARK = '    dc.b $47,$65,$74,$50  ; +$009C8: 47657450\n'
UNIT_SIZE = 2508
UNIT_SHA = "4e14633eea1ed1fd906ee9f4691e3a0bfc3c6086aaea858f8d2fc1a88ea8f31b"
FIRST, LAST = 0x00932, 0x0095E
FIRST_MARK = "L_UNIT156_00932:\n"
LAST_MARK = "L_UNIT156_0095E:\n"
ANNOT = re.compile(r"\s+;\s+\+\$([A-F0-9]{5}): ([A-F0-9]+)\s*$")
LABEL = re.compile(r"[A-Za-z_][A-Za-z_0-9]*:\s*$")
HEADER = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-backed native UNIT156 nibble expansion from pinned P2d emitter.\n"
    "; UNIT156+$00932..$0095E, 44 code bytes. Neighboring data unchanged.\n"
    "; Read-only audit verified byte by byte before MC68020 direct assembly.\n"
    "UNIT156_NIBBLE_ZERO equ 0\n\n"
)
HEADER2 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-backed UNIT156 DOS readiness guard from pinned P2d emitter.\n"
    "; UNIT156+$0099E..$009C8, 42 code bytes; GetP marker preserved.\n"
    "UNIT156_DOS_ZERO equ 0\n\n"
)


class Unit156Error(ValueError):
    pass


def demand(condition: bool, reason: str) -> None:
    if not condition:
        raise Unit156Error(reason)


def expected_sources() -> tuple[bytes, bytes, str, str, str]:
    audit = AUDIT.read_text("ascii")
    begin = audit.find(FIRST_MARK)
    stop = audit.find(LAST_MARK, begin+len(FIRST_MARK))
    demand(begin >= 0 and stop > begin and
           audit.find(FIRST_MARK, begin+len(FIRST_MARK)) < 0,
           "UNIT156 audit markers changed")
    body, encoded, offset = [], bytearray(), FIRST
    for line in audit[begin+len(FIRST_MARK):stop].splitlines():
        if LABEL.fullmatch(line):
            body.append(line)
            continue
        if not line.strip():
            continue
        match = ANNOT.search(line)
        demand(match is not None and int(match.group(1), 16) == offset and
               not line.lstrip().lower().startswith("dc."),
               "UNIT156 audit is not clean contiguous code")
        opcode = bytes.fromhex(match.group(2))
        encoded.extend(opcode)
        offset += len(opcode)
        body.append(line[:match.start()].rstrip())
    demand(offset == LAST and len(encoded) == 44,
           "UNIT156 nibble region has wrong length")
    mnemonic = "\n".join(body).rstrip()+"\n"
    before = "    moveq #0,d0"
    demand(mnemonic.count(before) == 1 and encoded[0x937-FIRST] == 0,
           "UNIT156 expected one-byte edit not verified")
    authored = HEADER + mnemonic.replace(
        before, "    moveq #UNIT156_NIBBLE_ZERO,d0"
    )
    wrapper = (audit[:begin+len(FIRST_MARK)] +
               '    include "' + MODULE_NAME + '"\n' + audit[stop:])
    demand(wrapper.count('; AGA_NATIVE_PURPOSE: AUDIT_ONLY') == 1,
           'UNIT156 audit-only marker missing from original export')
    wrapper = wrapper.replace(
        '; AGA_NATIVE_PURPOSE: AUDIT_ONLY',
        '; PARTIAL_SOURCE_MIGRATION: native UNIT156 nibble + DOS guard; audit remainder'
    )
    second_begin = audit.find(SECOND_MARK)
    second_stop = audit.find(SECOND_END_MARK, second_begin+len(SECOND_MARK))
    demand(second_begin >= 0 and second_stop > second_begin,
           "UNIT156 DOS guard audit markers changed")
    second_lines, second_bytes, at = [], bytearray(), SECOND
    for line in audit[second_begin+len(SECOND_MARK):second_stop].splitlines():
        if LABEL.fullmatch(line):
            second_lines.append(line)
            continue
        if not line.strip():
            continue
        mark = ANNOT.search(line)
        demand(mark is not None and int(mark.group(1), 16) == at and
               not line.lstrip().lower().startswith("dc."),
               "UNIT156 DOS guard audit is not contiguous instructions")
        data = bytes.fromhex(mark.group(2))
        second_bytes.extend(data)
        at += len(data)
        second_lines.append(line[:mark.start()].rstrip())
    demand(at == SECOND_END and len(second_bytes) == 42 and
           second_bytes[0x009AF-SECOND] == 0,
           "UNIT156 DOS guard source-owned bytes incorrect")
    source2 = "\n".join(second_lines).rstrip()+"\n"
    target = "    move.l #$00000000,d0"
    demand(source2.count(target) == 1,
           "UNIT156 DOS guard editable opcode ambiguous")
    authored2 = HEADER2 + source2.replace(
        target, "    move.l #UNIT156_DOS_ZERO,d0"
    )
    raw_region = audit[second_begin:second_stop]
    demand(wrapper.count(raw_region) == 1,
           "UNIT156 second region changed before replacement")
    wrapper = wrapper.replace(
        raw_region, SECOND_MARK+'    include "'+MODULE2_NAME+'"\n'
    )
    return bytes(encoded), bytes(second_bytes), authored, authored2, wrapper


def verify(official: bytes) -> int:
    demand(len(official) == 136020 and
           sha256(official).hexdigest() == P2D_SHA,
           "official P2d source builder SHA mismatch")
    chunk, chunk2, authored, authored2, wrapper = expected_sources()
    _, parts, _ = unpack_ap20(official)
    matches = [i for i, part in enumerate(parts)
               if len(part) == UNIT_SIZE and
               sha256(part).hexdigest() == UNIT_SHA]
    demand(len(matches) == 1, "pinned UNIT156 native group absent/ambiguous")
    group = matches[0]
    demand(parts[group][FIRST:LAST] == chunk,
           "original P2d builder differs from UNIT156 audit nibble code")
    demand(parts[group][SECOND:SECOND_END] == chunk2,
           "original P2d builder differs from UNIT156 DOS guard source")
    demand(MODULE.read_text("ascii") == authored,
           "UNIT156 authored mnemonic differs from pinned source")
    demand(MODULE2.read_text("ascii") == authored2,
           "UNIT156 DOS guard mnemonic differs from pinned source")
    demand(NATIVE.read_text("ascii") == wrapper,
           "UNIT156 editable wrapper differs from source-backed audit")
    print("UNIT156_SOURCE_PROVEN: 44+42 native bytes, group", group)
    return group


def stage(folder: Path, official: bytes) -> None:
    verify(official)
    (folder / STAGED_NAME).write_bytes(NATIVE.read_bytes())
    (folder / MODULE_NAME).write_bytes(MODULE.read_bytes())
    (folder / MODULE2_NAME).write_bytes(MODULE2.read_bytes())


def self_test_edit(staged: Path, assembler: Path) -> None:
    official = (staged / "M19_P2D_ASM_REBUILT_CHECK.Lib").read_bytes()
    group = verify(official)
    demand((staged / STAGED_NAME).is_file() and
           (staged / MODULE_NAME).is_file() and
           (staged / MODULE2_NAME).is_file() and
           (staged / MASTER_NAME).is_file(),
           "UNIT156 staged source missing")
    with TemporaryDirectory(prefix="unit156_nibble_edit_") as temporary:
        folder = Path(temporary)
        for file in staged.glob("*.s"):
            copy2(file, folder / file.name)
        source = (folder / MODULE_NAME).read_text("ascii")
        before = "UNIT156_NIBBLE_ZERO equ 0"
        demand(source.count(before) == 1, "UNIT156 edit parameter ambiguous")
        (folder / MODULE_NAME).write_text(
            source.replace(before, "UNIT156_NIBBLE_ZERO equ 1"),
            encoding="ascii", newline="\n"
        )
        source2 = (folder / MODULE2_NAME).read_text("ascii")
        before2 = "UNIT156_DOS_ZERO equ 0"
        demand(source2.count(before2) == 1,
               "UNIT156 DOS guard edit parameter ambiguous")
        (folder / MODULE2_NAME).write_text(
            source2.replace(before2, "UNIT156_DOS_ZERO equ 1"),
            encoding="ascii", newline="\n"
        )
        output = folder / "UNIT156_EDIT_TEST_UNTESTED.Lib"
        command = [str(assembler.resolve()), "-Fbin", "-m68020",
                   "-no-opt", "-quiet", "-o", str(output), MASTER_NAME]
        result = subprocess.run(command, cwd=folder, capture_output=True,
                                text=True, check=False)
        demand(result.returncode == 0,
               "vasm failed UNIT156 one-byte edit: " + result.stderr)
        changed = output.read_bytes()
        _, original_parts, _ = unpack_ap20(official)
        _, edited_parts, _ = unpack_ap20(changed)
        demand(len(changed) == len(official) and
               len(edited_parts) == len(original_parts) and
               all(a == b for n,(a,b) in enumerate(
                   zip(original_parts, edited_parts)) if n != group),
               "UNIT156 edit changed unrelated AP20 code")
        before_part, after_part = original_parts[group], edited_parts[group]
        differences = [n for n, (a,b) in enumerate(zip(
            before_part, after_part)) if a != b]
        demand(differences == [0x00937, 0x009AF] and
               before_part[0x00937] == 0 and after_part[0x00937] == 1 and
               before_part[0x009AF] == 0 and after_part[0x009AF] == 1,
               "UNIT156 two independent edits not confined to expected bytes")
    print("UNIT156_EDIT_TEST_PASS: two isolated source-only byte mutations")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument("--check", action="store_true")
    options.add_argument("--self-test-edit", action="store_true")
    parser.add_argument("--staged", type=Path)
    parser.add_argument("--vasm", type=Path)
    args = parser.parse_args()
    try:
        if args.self_test_edit:
            demand(args.staged is not None and args.vasm is not None,
                   "--self-test-edit requires --staged and --vasm")
            self_test_edit(args.staged, args.vasm)
        else:
            from build_m19_p2d_in_memory import build_p2d
            official, _ = build_p2d()
            verify(official)
        return 0
    except (Unit156Error, OSError) as error:
        print("[ERROR] UNIT156: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
