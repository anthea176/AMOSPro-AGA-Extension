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
MODULE10 = ROOT / "src/native/m19_p2d/M19_UNIT153_THIRD_PUBLIC_MC68020.s"
MODULE11 = ROOT / "src/native/m19_p2d/M19_UNIT153_THIRD_POINTER_MC68020.s"
MODULE12 = ROOT / "src/native/m19_p2d/M19_UNIT153_THIRD_VALIDATION_MC68020.s"
MODULE13 = ROOT / "src/native/m19_p2d/M19_UNIT153_THIRD_FINAL_MC68020.s"
MODULE14 = ROOT / "src/native/m19_p2d/M19_UNIT153_DISPATCH_V2_MC68020.s"
MODULE15 = ROOT / "src/native/m19_p2d/M19_UNIT153_WALK_COPY_TAIL_MC68020.s"
MODULE16 = ROOT / "src/native/m19_p2d/M19_UNIT153_THIRD_PIXEL_STEP_MC68020.s"
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
HEADER10 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; P2d UNIT153 third public preflight source-verified against emitter.\n"
    "; UNIT153+$00FA0..$011A6 (518 code bytes), AMOS Main marker preserved.\n"
    "UNIT153_THIRD_INITIAL_D3 equ 0\n\n"
)
HEADER11 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; P2d UNIT153 third bank pointer gate source-verified against emitter.\n"
    "; UNIT153+$011AC..$0126A (190 code bytes), AMOS Main marker preserved.\n"
    "UNIT153_THIRD_POINTER_MIN equ 24\n\n"
)
HEADER12 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; P2d UNIT153 third validation path source-verified against emitter.\n"
    "; UNIT153+$01270..$014F8 (648 code bytes), raw gap preserved.\n"
    "UNIT153_THIRD_VALID_MIN equ 24\n\n"
)
HEADER13 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; P2d UNIT153 third result/loop tail source-verified against emitter.\n"
    "; UNIT153+$0151A..$015B2 (152 code bytes), trailing GetP preserved.\n"
    "UNIT153_THIRD_FINAL_ZERO equ 0\n\n"
)
HEADER14 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; Source-owned UNIT153 AP20 V2 dispatcher from pinned P2d emitter.\n"
    "; UNIT153+$00000..$00022, 34 executable bytes, ABI unchanged.\n"
    "UNIT153_DISPATCH_STACK_BYTES equ 4\n\n"
)
HEADER15 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; UNIT153 P2d source-backed walk/copy completion $00EDA..$00F04.\n"
    "; CPU MC68020, 42 exact instruction bytes; no AMOS linker bytes.\n"
    "UNIT153_WALK_COPY_RESULT equ 1\n\n"
)
BODY15 = """L_UNIT153_00EDA:
    subq.l #1,d6
L_UNIT153_00EDC:
    move.b (a0)+,(a1)+
    dbra d6,L_UNIT153_00EDC
    move.l 76(a2),d0
    move.l a0,d5
    add.l d0,d5
    movea.l d5,a0
    move.l 80(a2),d0
    move.l a1,d5
    add.l d0,d5
    movea.l d5,a1
    dbra d7,L_UNIT153_00ED6
    move.l #UNIT153_WALK_COPY_RESULT,d3
    bra.w L_UNIT153_00F0A
"""
HEADER16 = (
    "; AGA_NATIVE_MIN_CPU: MC68020\n"
    "; UNIT153 P2d source-backed third-pixel loop $014F8..$0151A.\n"
    "; CPU MC68020, 34 exact instruction bytes; no AMOS linker bytes.\n"
    "UNIT153_THIRD_PIXEL_ADVANCE equ 1\n\n"
)
BODY16 = """L_UNIT153_014F8:
    move.l 100(a2),d0
    move.l a0,d1
    add.l d0,d1
    movea.l d1,a0
    move.l 104(a2),d0
    add.l d0,d4
    move.l 4(a2),d0
    cmp.l d0,d4
    bcs.w L_UNIT153_01516
    sub.l d0,d4
    addq.l #UNIT153_THIRD_PIXEL_ADVANCE,a0
L_UNIT153_01516:
    dbra d6,L_UNIT153_014F4
"""

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
    (
        MODULE10,
        "ENTRY_UNIT153_00FA0:\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$011A6: FE11F700031D\n",
        0xFA0, 0x11A6, 136, 0, HEADER10,
        "    move.l #$00000000,d3",
        "    move.l #UNIT153_THIRD_INITIAL_D3,d3",
    ),
    (
        MODULE11,
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$011A6: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0126A: FE11F700031D\n",
        0x11AC, 0x126A, 51, 1, HEADER11,
        "    cmpi.l #$00000018,d5",
        "    cmpi.l #UNIT153_THIRD_POINTER_MIN,d5",
    ),
    (
        MODULE12,
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0126A: FE11F700031D\n",
        "    dc.b $20,$2A,$00,$64,$22,$08,$D2,$80,$20,$41,$20,$2A  ; +$014F8: 202A00642208D2802041202A\n",
        0x1270, 0x14F8, 178, 9, HEADER12,
        "    cmpi.l #$00000018,d5",
        "    cmpi.l #UNIT153_THIRD_VALID_MIN,d5",
    ),
    (
        MODULE13,
        "L_UNIT153_0151A:\n",
        "    dc.b $47,$65,$74,$50  ; +$015B2: 47657450\n",
        0x151A, 0x15B2, 43, 10, HEADER13,
        "    move.l #$00000000,d3",
        "    move.l #UNIT153_THIRD_FINAL_ZERO,d3",
    ),
    (
        MODULE14,
        "UNIT_UNIT153:\n",
        "ENTRY_UNIT153_00022:\n",
        0x000, 0x022, 11, 0, HEADER14,
        "    subq.l #4,a7",
        "    subq.l #UNIT153_DISPATCH_STACK_BYTES,a7",
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
        "; PARTIAL_SOURCE_MIGRATION: UNIT153 dispatcher + public preflight native, audit remainder")
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
        # These two branch targets are actual instruction starts in the
        # source-pinned P2d group. Named labels add no bytes.
        if path == MODULE8:
            tail = "    bra.w L_UNIT153_00F50\n"
            demand(body.endswith(tail),
                   "UNIT153 previous loop anchor $00ED6 not at module8 end")
            body = body[:-len(tail)] + "L_UNIT153_00ED6:\n" + tail
        if path == MODULE12:
            tail = "    bra.w L_UNIT153_0158C\n"
            demand(body.endswith(tail),
                   "UNIT153 previous loop anchor $014F4 not at module12 end")
            body = body[:-len(tail)] + "L_UNIT153_014F4:\n" + tail
        authored = head + body.replace(old, new)
        wrapper = wrapper.replace(original_span,
            '    include "' + path.name + '"\n')
        extras.append((lo, bytes(native), path, authored))
    # The last two historical tails were preserved as raw audit bytes.
    # Their exact bytes are extracted from the SHA-pinned source audit and
    # verified against build_p2d() before accepting the editable source.
    for path, lo, hi, expected, authored in (
        (MODULE15, 0x00EDA, 0x00F04,
         bytes.fromhex(
             "538612D851CEFFFC202A004C2A08DA802045202A00502A09"
             "DA80224551CFFFDE263C0000000160000008"),
         HEADER15 + BODY15),
        (MODULE16, 0x014F8, 0x0151A,
         bytes.fromhex(
             "202A00642208D2802041202A0068D880202A0004B880"
             "650000069880528851CEFFDC"),
         HEADER16 + BODY16),
    ):
        at = lo
        lines = []
        original_bytes = bytearray()
        for line in audit.splitlines(keepends=True):
            match = ANNOT.search(line.rstrip("\n"))
            if match is None:
                continue
            offset = int(match.group(1), 16)
            if lo <= offset < hi:
                demand(offset == at and line.lstrip().startswith("dc.b "),
                       "UNIT153 original raw tail not contiguous: " + path.name)
                payload = bytes.fromhex(match.group(2))
                lines.append(line)
                original_bytes.extend(payload)
                at += len(payload)
        demand(at == hi and original_bytes == expected and
               len(expected) == hi-lo,
               "UNIT153 original raw tail bytes/source offset drift: " + path.name)
        original_span = "".join(lines)
        demand(wrapper.count(original_span) == 1,
               "UNIT153 raw tail wrapper replacement ambiguous: " + path.name)
        wrapper = wrapper.replace(original_span,
                                  '    include "' + path.name + '"\n')
        extras.append((lo, bytes(original_bytes), path, authored))
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
    # There are exactly 68 bytes of ABI metadata in this 5,558-byte group.
    # Anything neither source-owned code nor a proven ABI record is rejected.
    coverage = bytearray(GROUP_SIZE)
    owned = ((0x00372, raw),) + tuple((lo, code) for lo, code, _, _ in extras)
    for lo, code in owned:
        hi = lo + len(code)
        demand(0 <= lo < hi <= GROUP_SIZE and
               coverage[lo:hi] == bytes(hi-lo),
               "UNIT153 overlapping or invalid source-owned code")
        coverage[lo:hi] = b"\x01" * (hi-lo)
    amos_main = bytes.fromhex("FE11F700031D")
    records = (
        (0x00108, amos_main), (0x00362, b"c2p.library\x00"),
        (0x0036E, b"GetP"), (0x00530, amos_main),
        (0x00946, b"GetP"), (0x009FE, b"GetP"),
        (0x00BD4, amos_main), (0x00C98, amos_main),
        (0x00F9C, b"GetP"), (0x011A6, amos_main),
        (0x0126A, amos_main), (0x015B2, b"GetP"),
    )
    for lo, literal in records:
        hi = lo + len(literal)
        demand(coverage[lo:hi] == bytes(hi-lo) and
               groups[group][lo:hi] == literal,
               "UNIT153 AMOS ABI metadata unproven or overlaps code")
        coverage[lo:hi] = b"\x02" * len(literal)
    demand(coverage.count(1) == 5490 and coverage.count(2) == 68 and
           coverage.count(0) == 0 and len(extras) == 15,
           "UNIT153 remaining unclassified native bytes")
    print("UNIT153_SOURCE_PROVEN: 5490 bytes / 16 modules, group", group)
    print("UNIT153_REMAINDER_CLASSIFIED: 68 ABI bytes; 0 unclassified")
    return group


def stage(folder, official):
    verify(official)
    (folder / "M19_P2D_UNIT153_MC68020.s").write_bytes(WRAPPER.read_bytes())
    (folder / MODULE.name).write_bytes(MODULE.read_bytes())
    for path in (MODULE2, MODULE3, MODULE4, MODULE5, MODULE6, MODULE7, MODULE8, MODULE9, MODULE10, MODULE11, MODULE12, MODULE13, MODULE14, MODULE15, MODULE16):
        (folder / path.name).write_bytes(path.read_bytes())


def edit_gate(staged, assembler):
    reference = (staged / "M19_P2D_ASM_REBUILT_CHECK.Lib").read_bytes()
    group = verify(reference)
    demand((staged / "M19_P2D_UNIT153_MC68020.s").is_file() and
           all((staged / module.name).is_file()
               for module in (MODULE, MODULE2, MODULE3, MODULE4, MODULE5, MODULE6, MODULE7, MODULE8, MODULE9, MODULE10, MODULE11, MODULE12, MODULE13, MODULE14, MODULE15, MODULE16)) and
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
            (MODULE10, "UNIT153_THIRD_INITIAL_D3 equ 0",
             "UNIT153_THIRD_INITIAL_D3 equ 1"),
            (MODULE11, "UNIT153_THIRD_POINTER_MIN equ 24",
             "UNIT153_THIRD_POINTER_MIN equ 25"),
            (MODULE12, "UNIT153_THIRD_VALID_MIN equ 24",
             "UNIT153_THIRD_VALID_MIN equ 25"),
            (MODULE13, "UNIT153_THIRD_FINAL_ZERO equ 0",
             "UNIT153_THIRD_FINAL_ZERO equ 1"),
            (MODULE14, "UNIT153_DISPATCH_STACK_BYTES equ 4",
             "UNIT153_DISPATCH_STACK_BYTES equ 3"),
            (MODULE15, "UNIT153_WALK_COPY_RESULT equ 1",
             "UNIT153_WALK_COPY_RESULT equ 2"),
            (MODULE16, "UNIT153_THIRD_PIXEL_ADVANCE equ 1",
             "UNIT153_THIRD_PIXEL_ADVANCE equ 2"),
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
                    0xCA5: (24, 25), 0xF09: (0, 1),
                    0xFE7: (0, 1), 0x11B3: (24, 25),
                    0x1277: (24, 25), 0x1545: (0, 1),
                    0x0000: (0x59, 0x57),
                    0x0EFF: (1, 2), 0x1514: (0x52, 0x54)}
        demand(diffs == sorted(expected) and
               all((lhs[i], rhs[i]) == pair for i, pair in expected.items()),
               "UNIT153 grouped one-byte mutations drift")
    print("UNIT153_EDIT_TEST_PASS: 16 exact one-byte mutations in UNIT153 only")


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
