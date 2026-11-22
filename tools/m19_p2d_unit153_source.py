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
    return bytes(raw), module, wrapper


def verify(official):
    demand(len(official) == 136020 and
           sha256(official).hexdigest() == P2D_SHA, "official P2d SHA changed")
    raw, module, wrapper = expected_sources()
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
    print("UNIT153_SOURCE_PROVEN: 446 bytes, group", group)
    return group


def stage(folder, official):
    verify(official)
    (folder / "M19_P2D_UNIT153_MC68020.s").write_bytes(WRAPPER.read_bytes())
    (folder / MODULE.name).write_bytes(MODULE.read_bytes())


def edit_gate(staged, assembler):
    reference = (staged / "M19_P2D_ASM_REBUILT_CHECK.Lib").read_bytes()
    group = verify(reference)
    demand((staged / "M19_P2D_UNIT153_MC68020.s").is_file() and
           (staged / MODULE.name).is_file() and
           (staged / "M19_P2D_AP20_SOURCE.s").is_file(),
           "UNIT153 staging incomplete")
    with TemporaryDirectory(prefix="unit153_source_edit_") as tmp:
        folder = Path(tmp)
        for file in staged.glob("*.s"):
            shutil.copy2(file, folder / file.name)
        source = (folder / MODULE.name).read_text("ascii")
        old = "UNIT153_INITIAL_D3 equ 0"
        demand(source.count(old) == 1, "UNIT153 edit constant ambiguous")
        (folder / MODULE.name).write_text(
            source.replace(old, "UNIT153_INITIAL_D3 equ 1"),
            encoding="ascii", newline="\n"
        )
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
        demand(diffs == [0x381] and lhs[0x381] == 0 and rhs[0x381] == 1,
               "UNIT153 one-byte mutation drift")
    print("UNIT153_EDIT_TEST_PASS: one byte at $00381 only")


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
