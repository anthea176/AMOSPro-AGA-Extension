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
MODULE3 = ROOT / "src/native/m19_p2d/M19_UNIT156_CONVERT_TAIL_MC68020.s"
MODULE4 = ROOT / "src/native/m19_p2d/M19_UNIT156_MAIN_BODY_MC68020.s"
MODULE5 = ROOT / "src/native/m19_p2d/M19_UNIT156_PUBLIC_GET_MC68020.s"
MODULE6 = ROOT / "src/native/m19_p2d/M19_UNIT156_DISPATCH_V2_MC68020.s"
STAGED_NAME = "M19_P2D_UNIT156_MC68020.s"
MASTER_NAME = "M19_P2D_AP20_SOURCE.s"
MODULE_NAME = MODULE.name
MODULE2_NAME = MODULE2.name
MODULE3_NAME = MODULE3.name
MODULE4_NAME = MODULE4.name
MODULE5_NAME = MODULE5.name
MODULE6_NAME = MODULE6.name
FIFTH, FIFTH_END = 0x00022, 0x00218
FIFTH_MARK = 'ENTRY_UNIT156_00022:\n'
FIFTH_END_MARK = '    move.l a0,d5                                       ; +$00218: 2A08\n'
FOURTH, FOURTH_END = 0x00218, 0x007EE
FOURTH_MARK = '    move.l a0,d5                                       ; +$00218: 2A08\n'
FOURTH_END_MARK = '    dc.b $00,$07,$67,$00,$00,$04,$0D,$D4,$52,$8C,$08,$00  ; +$007EE: 0007670000040DD4528C0800\n'
THIRD, THIRD_END = 0x00850, 0x00926
THIRD_MARK = 'L_UNIT156_00850:\n'
THIRD_END_MARK = 'L_UNIT156_00926:\n'
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
HEADER3 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Native UNIT156 conversion/cleanup tail from SHA-pinned P2d source.\n"
    "; UNIT156+$00850..$00926, 214 code bytes. One original raw MOVE classified.\n"
    "UNIT156_TAIL_ZERO equ 0\n\n"
)
HEADER4 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-backed UNIT156 main conversion body from pinned P2d emitter.\n"
    "; UNIT156+$00218..$007EE (1494 bytes), instructions only, no data.\n"
    "UNIT156_MIN_POINTER_BYTES equ 24\n\n"
)
HEADER5 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-backed UNIT156 public image/get pipeline; P2d emitter proven.\n"
    "; UNIT156+$00022..$00218, 502 bytes with symbolic AMOS Main pseudo-call.\n"
    "UNIT156_GET_MIN_IMAGE equ 5\n"
    "UNIT156_AMOS_MAIN_GETADR equ 797\n\n"
)


HEADER6 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-owned UNIT156 AP20 V2 dispatcher from pinned P2d emitter.\n"
    "; UNIT156+$00000..$00022, 34 executable bytes, ABI unchanged.\n"
    "UNIT156_DISPATCH_STACK_BYTES equ 4\n\n"
)


class Unit156Error(ValueError):
    pass


def demand(condition: bool, reason: str) -> None:
    if not condition:
        raise Unit156Error(reason)


def expected_sources() -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, str, str, str, str, str, str, str]:
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
        '; PARTIAL_SOURCE_MIGRATION: native UNIT156 dispatch + public + main + tail + nibble + DOS guard; audit remainder'
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
    third_begin = audit.find(THIRD_MARK)
    third_stop = audit.find(THIRD_END_MARK, third_begin+len(THIRD_MARK))
    demand(third_begin >= 0 and third_stop > third_begin,
           "UNIT156 tail labels changed")
    third_lines, third_bytes, at, raw_moves = [], bytearray(), THIRD, 0
    for line in audit[third_begin+len(THIRD_MARK):third_stop].splitlines():
        if LABEL.fullmatch(line):
            third_lines.append(line)
            continue
        if not line.strip():
            continue
        mark = ANNOT.search(line)
        demand(mark is not None and int(mark.group(1), 16) == at,
               "UNIT156 tail source audit offset drift")
        code_bytes = bytes.fromhex(mark.group(2))
        if line.lstrip().lower().startswith("dc.b "):
            demand(at == 0x00918 and code_bytes.hex() == "203c00000000" and
                   raw_moves == 0, "UNIT156 tail raw instruction not classified")
            third_lines.append("    move.l #UNIT156_TAIL_ZERO,d0")
            raw_moves += 1
        else:
            third_lines.append(line[:mark.start()].rstrip())
        third_bytes.extend(code_bytes)
        at += len(code_bytes)
    demand(at == THIRD_END and len(third_bytes) == 214 and raw_moves == 1 and
           third_bytes[0x0091D-THIRD] == 0,
           "UNIT156 tail emitter ownership or mutation byte changed")
    authored3 = HEADER3 + "\n".join(third_lines).rstrip()+"\n"
    raw_third = audit[third_begin:third_stop]
    demand(wrapper.count(raw_third) == 1,
           "UNIT156 tail staged wrapper differs from original audit")
    wrapper = wrapper.replace(
        raw_third, THIRD_MARK+'    include "'+MODULE3_NAME+'"\n'
    )
    fourth_begin = audit.find(FOURTH_MARK)
    fourth_stop = audit.find(FOURTH_END_MARK,
                             fourth_begin+len(FOURTH_MARK))
    demand(fourth_begin >= 0 and fourth_stop > fourth_begin,
           "UNIT156 main body source audit boundaries absent")
    fourth_bytes, fourth_lines, at = bytearray(), [], FOURTH
    for line in audit[fourth_begin:fourth_stop].splitlines():
        if LABEL.fullmatch(line):
            fourth_lines.append(line)
            continue
        if not line.strip():
            continue
        m = ANNOT.search(line)
        demand(m is not None and int(m.group(1), 16) == at and
               not line.lstrip().lower().startswith("dc."),
               "UNIT156 main body contains non-code or offset gap")
        opcode = bytes.fromhex(m.group(2))
        fourth_bytes.extend(opcode)
        at += len(opcode)
        fourth_lines.append(line[:m.start()].rstrip())
    demand(at == FOURTH_END and len(fourth_bytes) == 1494 and
           fourth_bytes[0x0021F-FOURTH] == 24,
           "UNIT156 main body emitter size/mutation byte wrong")
    source4 = "\n".join(fourth_lines).rstrip()+"\n"
    before = "    cmpi.l #$00000018,d5"
    demand(source4.count(before) == 1,
           "UNIT156 pointer threshold instruction is ambiguous")
    authored4 = HEADER4 + source4.replace(
        before, "    cmpi.l #UNIT156_MIN_POINTER_BYTES,d5"
    )
    raw_fourth = audit[fourth_begin:fourth_stop]
    demand(wrapper.count(raw_fourth) == 1,
           "UNIT156 main audit span differs from native wrapper")
    wrapper = wrapper.replace(
        raw_fourth, '    include "'+MODULE4_NAME+'"\n'
    )
    fifth_begin = audit.find(FIFTH_MARK)
    fifth_stop = audit.find(FIFTH_END_MARK,
                            fifth_begin+len(FIFTH_MARK))
    demand(fifth_begin >= 0 and fifth_stop > fifth_begin,
           "UNIT156 public pipeline audit boundaries changed")
    fifth_bytes, fifth_lines, at, pseudo = bytearray(), [], FIFTH, 0
    for line in audit[fifth_begin+len(FIFTH_MARK):fifth_stop].splitlines():
        if LABEL.fullmatch(line):
            fifth_lines.append(line)
            continue
        if not line.strip():
            continue
        mark = ANNOT.search(line)
        demand(mark is not None and int(mark.group(1), 16) == at,
               "UNIT156 public pipeline offset gap")
        opcode = bytes.fromhex(mark.group(2))
        if line.lstrip().lower().startswith("dc.b "):
            demand(at == 0x00212 and opcode.hex() == "fe11f700031d"
                   and pseudo == 0,
                   "UNIT156 public AMOS Main ABI pseudo-call changed")
            fifth_lines.append(
                "    dc.w $FE11,$F700,UNIT156_AMOS_MAIN_GETADR"
            )
            pseudo += 1
        else:
            fifth_lines.append(line[:mark.start()].rstrip())
        fifth_bytes.extend(opcode)
        at += len(opcode)
    demand(at == FIFTH_END and len(fifth_bytes) == 502 and pseudo == 1 and
           fifth_bytes[0x00203-FIFTH] == 5,
           "UNIT156 public source ownership or mutation byte changed")
    source5 = "\n".join(fifth_lines).rstrip()+"\n"
    before = "    cmpi.l #$00000005,d0"
    demand(source5.count(before) == 1,
           "UNIT156 public image minimum is not unique")
    authored5 = HEADER5 + source5.replace(
        before, "    cmpi.l #UNIT156_GET_MIN_IMAGE,d0"
    )
    original_fifth = audit[fifth_begin+len(FIFTH_MARK):fifth_stop]
    demand(wrapper.count(original_fifth) == 1,
           "UNIT156 public region differs from its source audit")
    wrapper = wrapper.replace(
        original_fifth, '    include "'+MODULE5_NAME+'"\n'
    )
    # AP20 V2 dispatcher remains code, not an audit-only blob.
    first = "UNIT_UNIT156:\n"
    last = "ENTRY_UNIT156_00022:\n"
    begin6 = audit.find(first)
    end6 = audit.find(last, begin6+len(first))
    demand(begin6 >= 0 and end6 > begin6 and
           audit.find(first, begin6+len(first)) < 0,
           "UNIT156 dispatcher markers missing/ambiguous")
    raw_dispatch = audit[begin6+len(first):end6]
    lines6, bytes6, offset6, count6 = [], bytearray(), 0, 0
    for line in raw_dispatch.splitlines():
        if not line.strip():
            continue
        match = ANNOT.search(line)
        demand(match is not None and int(match.group(1), 16) == offset6 and
               not line.lstrip().lower().startswith("dc."),
               "UNIT156 dispatcher is not clean source code")
        raw = bytes.fromhex(match.group(2))
        bytes6.extend(raw)
        offset6 += len(raw)
        lines6.append(line[:match.start()].rstrip())
        count6 += 1
    demand(offset6 == 0x22 and len(bytes6) == 34 and count6 == 11 and
           bytes6[:2] == bytes.fromhex("598f"),
           "UNIT156 dispatcher size or stack ABI changed")
    body6 = "\n".join(lines6).rstrip()+"\n"
    target = "    subq.l #4,a7"
    demand(body6.count(target) == 1 and wrapper.count(raw_dispatch) == 1,
           "UNIT156 dispatcher edit/replace ambiguous")
    authored6 = HEADER6 + body6.replace(
        target, "    subq.l #UNIT156_DISPATCH_STACK_BYTES,a7"
    )
    wrapper = wrapper.replace(
        raw_dispatch, '    include "'+MODULE6_NAME+'"\n'
    )
    return (bytes(encoded), bytes(second_bytes), bytes(third_bytes),
            bytes(fourth_bytes), bytes(fifth_bytes), bytes(bytes6),
            authored, authored2, authored3, authored4, authored5, authored6,
            wrapper)


def verify(official: bytes) -> int:
    demand(len(official) == 136020 and
           sha256(official).hexdigest() == P2D_SHA,
           "official P2d source builder SHA mismatch")
    chunk, chunk2, chunk3, chunk4, chunk5, chunk6, authored, authored2, authored3, authored4, authored5, authored6, wrapper = expected_sources()
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
    demand(parts[group][THIRD:THIRD_END] == chunk3,
           "original P2d builder differs from UNIT156 tail source")
    demand(parts[group][FOURTH:FOURTH_END] == chunk4,
           "original P2d builder differs from UNIT156 main body")
    demand(parts[group][FIFTH:FIFTH_END] == chunk5,
           "original P2d builder differs from UNIT156 public pipeline")
    demand(parts[group][:0x22] == chunk6,
           "original P2d builder differs from UNIT156 AP20 dispatcher")
    demand(MODULE.read_text("ascii") == authored,
           "UNIT156 authored mnemonic differs from pinned source")
    demand(MODULE2.read_text("ascii") == authored2,
           "UNIT156 DOS guard mnemonic differs from pinned source")
    demand(MODULE3.read_text("ascii") == authored3,
           "UNIT156 tail mnemonic differs from pinned source")
    demand(MODULE4.read_text("ascii") == authored4,
           "UNIT156 main body mnemonic differs from pinned source")
    demand(MODULE5.read_text("ascii") == authored5,
           "UNIT156 public pipeline mnemonic differs from pinned source")
    demand(MODULE6.read_text("ascii") == authored6,
           "UNIT156 dispatcher mnemonic differs from pinned source")
    demand(NATIVE.read_text("ascii") == wrapper,
           "UNIT156 editable wrapper differs from source-backed audit")
    print("UNIT156_SOURCE_PROVEN: 2330 bytes / 6 modules including dispatcher, group", group)
    return group


def stage(folder: Path, official: bytes) -> None:
    verify(official)
    (folder / STAGED_NAME).write_bytes(NATIVE.read_bytes())
    (folder / MODULE_NAME).write_bytes(MODULE.read_bytes())
    (folder / MODULE2_NAME).write_bytes(MODULE2.read_bytes())
    (folder / MODULE3_NAME).write_bytes(MODULE3.read_bytes())
    (folder / MODULE4_NAME).write_bytes(MODULE4.read_bytes())
    (folder / MODULE5_NAME).write_bytes(MODULE5.read_bytes())
    (folder / MODULE6_NAME).write_bytes(MODULE6.read_bytes())


def self_test_edit(staged: Path, assembler: Path) -> None:
    official = (staged / "M19_P2D_ASM_REBUILT_CHECK.Lib").read_bytes()
    group = verify(official)
    demand((staged / STAGED_NAME).is_file() and
           (staged / MODULE_NAME).is_file() and
           (staged / MODULE2_NAME).is_file() and
           (staged / MODULE3_NAME).is_file() and
           (staged / MODULE4_NAME).is_file() and
           (staged / MODULE5_NAME).is_file() and
           (staged / MODULE6_NAME).is_file() and
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
        source3 = (folder / MODULE3_NAME).read_text("ascii")
        before3 = "UNIT156_TAIL_ZERO equ 0"
        demand(source3.count(before3) == 1,
               "UNIT156 tail edit parameter ambiguous")
        (folder / MODULE3_NAME).write_text(
            source3.replace(before3, "UNIT156_TAIL_ZERO equ 1"),
            encoding="ascii", newline="\n"
        )
        source4 = (folder / MODULE4_NAME).read_text("ascii")
        before4 = "UNIT156_MIN_POINTER_BYTES equ 24"
        demand(source4.count(before4) == 1,
               "UNIT156 main body edit parameter ambiguous")
        (folder / MODULE4_NAME).write_text(
            source4.replace(before4, "UNIT156_MIN_POINTER_BYTES equ 25"),
            encoding="ascii", newline="\n"
        )
        source5 = (folder / MODULE5_NAME).read_text("ascii")
        before5 = "UNIT156_GET_MIN_IMAGE equ 5"
        demand(source5.count(before5) == 1,
               "UNIT156 public pipeline edit parameter ambiguous")
        (folder / MODULE5_NAME).write_text(
            source5.replace(before5, "UNIT156_GET_MIN_IMAGE equ 6"),
            encoding="ascii", newline="\n"
        )
        source6 = (folder / MODULE6_NAME).read_text("ascii")
        before6 = "UNIT156_DISPATCH_STACK_BYTES equ 4"
        demand(source6.count(before6) == 1,
               "UNIT156 dispatcher edit parameter ambiguous")
        (folder / MODULE6_NAME).write_text(
            source6.replace(before6, "UNIT156_DISPATCH_STACK_BYTES equ 3"),
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
        demand(differences == [0x00000, 0x00203, 0x0021F, 0x0091D, 0x00937, 0x009AF] and
               before_part[0] == 0x59 and after_part[0] == 0x57 and
               before_part[0x00203] == 5 and after_part[0x00203] == 6 and
               before_part[0x0021F] == 24 and after_part[0x0021F] == 25 and
               before_part[0x0091D] == 0 and after_part[0x0091D] == 1 and
               before_part[0x00937] == 0 and after_part[0x00937] == 1 and
               before_part[0x009AF] == 0 and after_part[0x009AF] == 1,
               "UNIT156 five independent edits not confined to expected bytes")
    print("UNIT156_EDIT_TEST_PASS: six isolated source-only byte mutations")


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
