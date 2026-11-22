#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""UNIT153 P2d source-backed staged preflight and isolated edit gate."""
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
AUDIT = ROOT / "src/asm_migration/m19_p2d/M19_P2D_UNIT153_MC68020.s"
WRAPPER = ROOT / "src/native/m19_p2d/M19_P2D_UNIT153_EDITABLE.s"
MODULE = ROOT / "src/native/m19_p2d/M19_UNIT153_PUBLIC_PREFLIGHT_MC68020.s"
MODULE2 = ROOT / "src/native/m19_p2d/M19_UNIT153_ENTRY_GUARD_MC68020.s"
MODULE3 = ROOT / "src/native/m19_p2d/M19_UNIT153_POINTER_VALIDATE_MC68020.s"
MODULE4 = ROOT / "src/native/m19_p2d/M19_UNIT153_SECOND_GET_MC68020.s"
MODULE5 = ROOT / "src/native/m19_p2d/M19_UNIT153_SHORT_SERVICE_MC68020.s"
MODULE6 = ROOT / "src/native/m19_p2d/M19_UNIT153_BULK_PREFLIGHT_MC68020.s"
MODULE7 = ROOT / "src/native/m19_p2d/M19_UNIT153_POINTER_RECHECK_MC68020.s"
MODULE8 = ROOT / "src/native/m19_p2d/M19_UNIT153_MEMORY_WALK_MC68020.s"
MODULE9 = ROOT / "src/native/m19_p2d/M19_UNIT153_WALK_CLEANUP_MC68020.s"
GROUP_SIZE = 0x15B6
GROUP_SHA = "6eda5283af42617aa13ad81e24d9130abedc4528ed05b469de2d765d20b4d700"
START = "ENTRY_UNIT153_00372:\n"
STOP = "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00530: FE11F700031D\n"
ANNOT = re.compile(r"\s+;\s+\+\$([0-9A-F]{5}): ([0-9A-F]+)\s*$")
LABEL = re.compile(r"[A-Za-z_][A-Za-z_0-9]*:\s*$")
HEADER = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; UNIT153 public preflight source-verified against pinned P2d builder.\n"
    "; Group+$00372..$00530 (446 bytes): following AMOS Main GETADR marker preserved.\n"
    "UNIT153_INITIAL_D3 equ 0\n\n"
)


HEADER2 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-verified UNIT153 entry/system guard from pinned P2d emitter.\n"
    "; UNIT153+$00022..$00108 (230 code bytes); AMOS Main marker preserved.\n"
    "UNIT153_ENTRY_ZERO equ 0\n\n"
)
HEADER3 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-verified UNIT153 bank pointer validation and cleanup.\n"
    "; UNIT153+$0010E..$00362 (596 code bytes); C2P data preserved.\n"
    "UNIT153_MIN_POINTER_BYTES equ 24\n\n"
)
HEADER4 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-verified UNIT153 second pointer/image path, pinned P2d.\n"
    "; UNIT153+$00536..$00946 (1040 code bytes), GetP marker preserved.\n"
    "UNIT153_SECOND_MIN_POINTER_BYTES equ 24\n\n"
)
HEADER5 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-verified UNIT153 short service, pinned P2d.\n"
    "; UNIT153+$0094A..$009FE (180 code bytes), GetP marker preserved.\n"
    "UNIT153_SHORT_INITIAL_D3 equ 0\n\n"
)
HEADER6 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-verified UNIT153 bulk preflight, pinned P2d emitter.\n"
    "; UNIT153+$00A02..$00BD4 (466 code bytes); AMOS Main marker preserved.\n"
    "UNIT153_BULK_INITIAL_D3 equ 0\n\n"
)
HEADER7 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-verified UNIT153 pointer recheck, pinned P2d emitter.\n"
    "; UNIT153+$00BDA..$00C98 (190 code bytes); AMOS Main marker preserved.\n"
    "UNIT153_RECHECK_MIN_POINTER_BYTES equ 24\n\n"
)
HEADER8 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-verified UNIT153 memory walk, pinned P2d emitter.\n"
    "; UNIT153+$00C9E..$00EDA (572 code bytes); raw special gap preserved.\n"
    "UNIT153_MEMORY_WALK_MIN_POINTER_BYTES equ 24\n\n"
)
HEADER9 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-verified UNIT153 walk cleanup and result, pinned P2d.\n"
    "; UNIT153+$00F04..$00F9C (152 code bytes); GetP marker preserved.\n"
    "UNIT153_WALK_RESULT_ZERO equ 0\n\n"
)
EXTRA_SPANS = (
    (
        MODULE2,
        "ENTRY_UNIT153_00022:\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00108: FE11F700031D\n",
        0x22, 0x108, 62, 0, HEADER2,
        "    move.l #$00000000,d3",
        "    move.l #UNIT153_ENTRY_ZERO,d3",
    ),
    (
        MODULE3,
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00108: FE11F700031D\n",
        "L_UNIT153_00362:\n",
        0x10E, 0x362, 150, 4, HEADER3,
        "    cmpi.l #$00000018,d5",
        "    cmpi.l #UNIT153_MIN_POINTER_BYTES,d5",
    ),
    (
        MODULE4,
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00530: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$00946: 47657450\n",
        0x536, 0x946, 265, 5, HEADER4,
        "    cmpi.l #$00000018,d5",
        "    cmpi.l #UNIT153_SECOND_MIN_POINTER_BYTES,d5",
    ),
    (
        MODULE5,
        "ENTRY_UNIT153_0094A:\n",
        "    dc.b $47,$65,$74,$50  ; +$009FE: 47657450\n",
        0x94A, 0x9FE, 50, 2, HEADER5,
        "    move.l #$00000000,d3",
        "    move.l #UNIT153_SHORT_INITIAL_D3,d3",
    ),
    (
        MODULE6,
        "ENTRY_UNIT153_00A02:\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00BD4: FE11F700031D\n",
        0xA02, 0xBD4, 122, 0, HEADER6,
        "    move.l #$00000000,d3",
        "    move.l #UNIT153_BULK_INITIAL_D3,d3",
    ),
    (
        MODULE7,
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00BD4: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00C98: FE11F700031D\n",
        0xBDA, 0xC98, 51, 1, HEADER7,
        "    cmpi.l #$00000018,d5",
        "    cmpi.l #UNIT153_RECHECK_MIN_POINTER_BYTES,d5",
    ),
    (
        MODULE8,
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00C98: FE11F700031D\n",
        "    dc.b $53,$86,$12,$D8,$51,$CE,$FF,$FC,$20,$2A,$00,$4C  ; +$00EDA: 538612D851CEFFFC202A004C\n",
        0xC9E, 0xEDA, 159, 6, HEADER8,
        "    cmpi.l #$00000018,d5",
        "    cmpi.l #UNIT153_MEMORY_WALK_MIN_POINTER_BYTES,d5",
    ),
    (
        MODULE9,
        "L_UNIT153_00F04:\n",
        "    dc.b $47,$65,$74,$50  ; +$00F9C: 47657450\n",
        0xF04, 0xF9C, 46, 11, HEADER9,
        "    move.l #$00000000,d3",
        "    move.l #UNIT153_WALK_RESULT_ZERO,d3",
    ),
)


class Unit153Error(ValueError):
    pass


def demand(ok, msg):
    if not ok:
        raise Unit153Error(msg)


def expected_sources():
    audit = AUDIT.read_text("ascii")
    start = audit.find(START)
    stop = audit.find(STOP, start+len(START))
    demand(start >= 0 and stop > start and
           audit.find(START, start+len(START)) < 0,
           "UNIT153 source markers missing/ambiguous")
    lines, raw, at, n, labels = [], bytearray(), 0x372, 0, 0
    for line in audit[start+len(START):stop].splitlines():
        if LABEL.fullmatch(line):
            lines.append(line)
            labels += 1
            continue
        if not line.strip():
            continue
        m = ANNOT.search(line)
        demand(m is not None and int(m.group(1), 16) == at and
               not line.lstrip().lower().startswith("dc."),
               "unproven UNIT153 mnemonic/offset")
        op = bytes.fromhex(m.group(2))
        raw.extend(op)
        at += len(op)
        lines.append(line[:m.start()].rstrip())
        n += 1
    demand(at == 0x530 and n == 121 and labels == 2 and
           len(raw) == 446 and raw[0x381-0x372] == 0,
           "UNIT153 code length or mutation byte drift")
    body = "\n".join(lines).rstrip()+"\n"
    old = "    move.l #$00000000,d3"
    demand(body.count(old) == 1, "UNIT153 edited instruction nonunique")
    module = HEADER + body.replace(old, "    move.l #UNIT153_INITIAL_D3,d3")
    marker = "; AGA_NATIVE_PURPOSE: AUDIT_ONLY"
    demand(audit.count(marker) == 1, "AUDIT_ONLY source marker absent")
    wrapper = audit.replace(marker,
        "; PARTIAL_SOURCE_MIGRATION: UNIT153 public preflight native, audit remainder")
    original = audit[start+len(START):stop]
    demand(wrapper.count(original) == 1, "UNIT153 audited preflight ambiguous")
    wrapper = wrapper.replace(original,
        '    include "' + MODULE.name + '"\n')
    # Restore two further disjoint code-only spans. The audit source is
    # read-only: no source bytes are inferred from the installed .Lib.
    extras = []
    for path, begin_mark, end_mark, lo, hi, op_count, label_count, head, old, new in EXTRA_SPANS:
        begin = audit.find(begin_mark)
        end = audit.find(end_mark, begin+len(begin_mark))
        demand(begin >= 0 and end > begin and
               audit.find(begin_mark, begin+len(begin_mark)) < 0,
               "UNIT153 extra source markers missing/ambiguous: "+path.name)
        original_span = audit[begin+len(begin_mark):end]
        out_lines, native, offset, instructions, label_total = [], bytearray(), lo, 0, 0
        for line in original_span.splitlines():
            if LABEL.fullmatch(line):
                out_lines.append(line)
                label_total += 1
                continue
            if not line.strip():
                continue
            match = ANNOT.search(line)
            demand(match is not None and int(match.group(1), 16) == offset and
                   not line.lstrip().lower().startswith("dc."),
                   "UNIT153 extra unproven mnemonic/offset: "+path.name)
            opcode = bytes.fromhex(match.group(2))
            native.extend(opcode)
            offset += len(opcode)
            out_lines.append(line[:match.start()].rstrip())
            instructions += 1
        demand(offset == hi and len(native) == hi-lo and
               instructions == op_count and label_total == label_count,
               "UNIT153 extra code span/count drift: "+path.name)
        body = "\n".join(out_lines).rstrip()+"\n"
        demand(body.count(old) == 1 and wrapper.count(original_span) == 1,
               "UNIT153 extra edit anchor/replace ambiguous: "+path.name)
        authored = head + body.replace(old, new)
        wrapper = wrapper.replace(original_span,
            '    include "' + path.name + '"\n')
        extras.append((lo, bytes(native), path, authored))
    return bytes(raw), module, wrapper, extras


def verify(official):
    demand(len(official) == 136020 and
           sha256(official).hexdigest() == P2D_SHA, "official P2d SHA changed")
    raw, module, wrapper, extras = expected_sources()
    _, groups, _ = unpack_ap20(official)
    ids = [i for i, part in enumerate(groups)
           if len(part) == GROUP_SIZE and sha256(part).hexdigest() == GROUP_SHA]
    demand(len(ids) == 1, "UNIT153 source-built AP20 unit absent or ambiguous")
    group = ids[0]
    demand(groups[group][0x372:0x530] == raw,
           "UNIT153 builder bytes differ from pinned source")
    demand(MODULE.read_text("ascii") == module and
           WRAPPER.read_text("ascii") == wrapper,
           "UNIT153 authored module or wrapper differs from source proof")
    for begin, code, path, authored in extras:
        demand(groups[group][begin:begin+len(code)] == code,
               "UNIT153 extra source-built bytes differ: "+path.name)
        demand(path.read_text("ascii") == authored,
               "UNIT153 extra authored module differs: "+path.name)
    print("UNIT153_SOURCE_PROVEN: 3872 bytes / 9 modules, group", group)
    return group


def stage(folder, official):
    verify(official)
    (folder / "M19_P2D_UNIT153_MC68020.s").write_bytes(WRAPPER.read_bytes())
    (folder / MODULE.name).write_bytes(MODULE.read_bytes())
    for path in (MODULE2, MODULE3, MODULE4, MODULE5, MODULE6, MODULE7, MODULE8, MODULE9):
        (folder / path.name).write_bytes(path.read_bytes())


def edit_gate(staged, assembler):
    reference = (staged / "M19_P2D_ASM_REBUILT_CHECK.Lib").read_bytes()
    group = verify(reference)
    demand((staged / "M19_P2D_UNIT153_MC68020.s").is_file() and
           all((staged / module.name).is_file()
               for module in (MODULE, MODULE2, MODULE3, MODULE4, MODULE5, MODULE6, MODULE7, MODULE8, MODULE9)) and
           (staged / "M19_P2D_AP20_SOURCE.s").is_file(),
           "UNIT153 staging incomplete")
    with TemporaryDirectory(prefix="unit153_source_edit_") as tmp:
        folder = Path(tmp)
        for file in staged.glob("*.s"):
            shutil.copy2(file, folder / file.name)
        for module, old, new in (
            (MODULE, "UNIT153_INITIAL_D3 equ 0", "UNIT153_INITIAL_D3 equ 1"),
            (MODULE2, "UNIT153_ENTRY_ZERO equ 0", "UNIT153_ENTRY_ZERO equ 1"),
            (MODULE3, "UNIT153_MIN_POINTER_BYTES equ 24",
             "UNIT153_MIN_POINTER_BYTES equ 25"),
            (MODULE4, "UNIT153_SECOND_MIN_POINTER_BYTES equ 24",
             "UNIT153_SECOND_MIN_POINTER_BYTES equ 25"),
            (MODULE5, "UNIT153_SHORT_INITIAL_D3 equ 0",
             "UNIT153_SHORT_INITIAL_D3 equ 1"),
            (MODULE6, "UNIT153_BULK_INITIAL_D3 equ 0",
             "UNIT153_BULK_INITIAL_D3 equ 1"),
            (MODULE7, "UNIT153_RECHECK_MIN_POINTER_BYTES equ 24",
             "UNIT153_RECHECK_MIN_POINTER_BYTES equ 25"),
            (MODULE8, "UNIT153_MEMORY_WALK_MIN_POINTER_BYTES equ 24",
             "UNIT153_MEMORY_WALK_MIN_POINTER_BYTES equ 25"),
            (MODULE9, "UNIT153_WALK_RESULT_ZERO equ 0",
             "UNIT153_WALK_RESULT_ZERO equ 1"),
        ):
            source = (folder / module.name).read_text("ascii")
            demand(source.count(old) == 1,
                   "UNIT153 edit constant ambiguous: "+module.name)
            (folder / module.name).write_text(
                source.replace(old, new), encoding="ascii", newline="\n")
        binary = folder / "UNIT153_EDIT_UNTESTED.Lib"
        command = [str(assembler.resolve()), "-Fbin", "-m68020", "-no-opt",
                   "-quiet", "-o", str(binary), "M19_P2D_AP20_SOURCE.s"]
        result = subprocess.run(command, cwd=folder, capture_output=True,
                                text=True, check=False)
        demand(result.returncode == 0, "vasm UNIT153 edit failed: "+result.stderr)
        edited = binary.read_bytes()
        oldtokens, original, oldtitle = unpack_ap20(reference)
        tokens, changed, title = unpack_ap20(edited)
        demand(len(reference) == len(edited) and oldtokens == tokens and
               oldtitle == title and len(original) == len(changed) and
               all(x == y for i,(x,y) in enumerate(zip(original,changed))
                   if i != group), "UNIT153 edit changed unrelated AP20")
        lhs, rhs = original[group], changed[group]
        diffs = [i for i,(x,y) in enumerate(zip(lhs,rhs)) if x != y]
        expected = {0x33: (0, 1), 0x115: (24, 25), 0x381: (0, 1),
                    0x53D: (24, 25), 0x959: (0, 1),
                    0xA3D: (0, 1), 0xBE1: (24, 25),
                    0xCA5: (24, 25), 0xF09: (0, 1)}
        demand(diffs == sorted(expected) and
               all((lhs[i], rhs[i]) == pair for i, pair in expected.items()),
               "UNIT153 grouped one-byte mutations drift")
    print("UNIT153_EDIT_TEST_PASS: 9 exact one-byte mutations in UNIT153 only")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--self-test-edit", action="store_true")
    parser.add_argument("--staged", type=Path)
    parser.add_argument("--vasm", type=Path)
    args = parser.parse_args()
    try:
        if args.self_test_edit:
            demand(args.staged is not None and args.vasm is not None,
                   "--self-test-edit requires --staged/--vasm")
            edit_gate(args.staged, args.vasm)
        else:
            from build_m19_p2d_in_memory import build_p2d
            official, _ = build_p2d()
            verify(official)
        return 0
    except (Unit153Error, OSError) as err:
        print("[ERROR] UNIT153: " + str(err))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
