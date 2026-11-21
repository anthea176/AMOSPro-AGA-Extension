#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Link an editable handwritten P2d Bob controls module into the P2d AP20 ASM.

This is an incremental native-source migration, not a production promotion.
Remaining units are the verified P2d audit-assembly baseline until migrated.
Only builds into a user-specified output directory. No writes into dist/.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from functools import lru_cache
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from active_library import P2D_SHA
from build_m19_p2d_in_memory import build_p2d
from build_m19_p1e_bank_edit_in_memory import build_p1e
from compiler_relocation import unpack_ap20
from audit_ap20 import inspect, parse
from m19_p2d_bob_auto_update_emit import emit_bob_auto_update
from m19_p2b_bob_flip_emit import emit_bob_flip
from m19_p2b_planar_orientation020_emit import emit_planar_orientation020

AUDIT_DIR = ROOT / 'src' / 'asm_migration' / 'm19_p2d'
EDITABLE_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2D_CONTROLS_MC68020.s'
PLANES_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2C_PLANES_MC68020.s'
FLIP_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_FLIP_PUBLIC_MC68020.s'
PLANAR_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_PLANAR_MC68020.s'
SLOTS_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_SLOTS_DATA_MC68020.s'
BOBS_FILE = 'M19_P2D_BOBS_MC68020.s'
MASTER_FILE = 'M19_P2D_AP20_SOURCE.s'
SOURCE_NAME = 'M19_P2D_CONTROLS_MC68020.s'
START_LABEL = 'p2d_public_auto_update:'
END_LABEL = 'L_BOBS_0B72A:'
P2C_START_LABEL = 'p2c_public_planes:'
P2C_END_LABEL = 'ENTRY_BOBS_0B58C:'
P2C_SOURCE_NAME = 'M19_P2C_PLANES_MC68020.s'
FLIP_SOURCE_NAME = 'M19_P2B_FLIP_PUBLIC_MC68020.s'
FLIP_START = 0x9E36
FLIP_END = 0x9F26
PLANAR_SOURCE_NAME = 'M19_P2B_PLANAR_MC68020.s'
SLOTS_SOURCE_NAME = 'M19_P2B_SLOTS_DATA_MC68020.s'
PLANAR_START = 0xA28E
PLANAR_END = 0xA4C0


class SourceError(RuntimeError):
    pass


def require(test: bool, reason: str) -> None:
    if not test:
        raise SourceError(reason)


def checked_vasm(assembler: Path, source: Path, output: Path) -> bytes:
    """Assemble Motorola source with a real MC68020 target, no optimization."""
    require(assembler.is_file(), f'vasm not found: {assembler}')
    cmd = [str(assembler.resolve()), '-Fbin', '-m68020', '-no-opt',
           '-quiet', '-o', str(output.resolve()), source.name]
    result = subprocess.run(cmd, cwd=source.parent, capture_output=True,
                            text=True, check=False)
    require(result.returncode == 0,
            f'vasm return {result.returncode} on {source.name}:\n'
            f'{result.stdout}\n{result.stderr}')
    require(output.is_file(), 'vasm returned success without an output file')
    return output.read_bytes()


@lru_cache(maxsize=1)
def prove_source_provenance() -> tuple[bytes, int, int, int, int, int, int]:
    """Require exact P2d native builder and exact source-region boundaries."""
    lib = (ROOT / 'dist' / 'AMOSPro_AGA.Lib').read_bytes()
    good = (ROOT / 'dist' / 'AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    require(len(lib) == 136020 and sha256(lib).hexdigest() == P2D_SHA,
            'official P2d source is not the selected 136020-byte baseline')
    require(good == lib, 'LAST_GOOD differs from P2d; refused')
    rebuilt, info = build_p2d()
    require(rebuilt == lib and info['sha256'] == P2D_SHA,
            'native Python builder does not reproduce the official P2d')
    _, parts, _ = unpack_ap20(lib)
    group = info['group']
    _, p1e_info = build_p1e()
    native, labels, service_off = emit_bob_auto_update(p1e_info['context_delta'])
    require(parts[group].endswith(native), 'native BOBS suffix diverged')
    prefix = len(parts[group]) - len(native)
    start = prefix + labels['p2d_public_auto_update']
    end = prefix + service_off
    done = prefix + labels['p2d_set_done']
    planes = prefix + labels['p2c_public_planes']
    planes_fail = prefix + labels['p2c_set_fail']
    require((planes, planes_fail, start - planes) == (0xB4C4, 0xB52E, 200),
            'P2c planes native module boundaries changed')
    require((start, end, end-start) == (0xB58C, 0xB72A, 414),
            f'P2d handwritten module boundaries changed: {start:x}:{end:x}')
    require(parts[group][done:done+2] == bytes.fromhex('7601'),
            'expected two-byte moveq #1,d3 at p2d_set_done missing')
    return lib, group, planes, start, end, done, planes_fail


@lru_cache(maxsize=1)
def prove_planar_provenance() -> tuple[int, int, int, bytes]:
    """The exact P2b materializer bytes come from the Python source emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    context = p1e['context_delta']
    # The original P2b unit is the exact prefix of the subsequently extended P2d.
    full, labels = emit_bob_flip(context)
    fragment, frag_labels = emit_planar_orientation020()
    _, parts, _ = unpack_ap20(original)
    native, _, _ = emit_bob_auto_update(context)
    base = len(parts[group]) - len(native)
    start = base + labels['p2b_owner'] - len(fragment)
    end = base + labels['p2b_owner']
    require((start, end) == (PLANAR_START, PLANAR_END),
            f'P2b planar source offsets changed: {start:x}..{end:x}')
    require(parts[group][start:end] == fragment,
            'P2b handwritten source ancestry differs from official P2d')
    require(full[labels['p2b_owner'] - len(fragment):labels['p2b_owner']] == fragment,
            'P2b materializer not adjacent to owned slots')
    require('invalid' in frag_labels, 'P2b invalid label absent')
    return start, end, start + frag_labels['invalid'], fragment


@lru_cache(maxsize=1)
def prove_flip_public_provenance() -> tuple[int, int, int, bytes]:
    """Pin the public Flip / slot-cache block to its original P2b emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels = emit_bob_flip(p1e['context_delta'])
    _, parts, _ = unpack_ap20(original)
    base = PLANAR_END - labels['p2b_owner']
    start = base + labels['p2b_slot']
    public = base + labels['p2b_public_flip']
    end = base + labels['p2b_variant']
    failure = base + labels['p2b_flip_fail']
    require((start, public, failure, end) ==
            (FLIP_START, 0x9E96, 0x9F12, FLIP_END),
            'source P2b Flip public offsets differ from pinned P2d')
    fragment = native[labels['p2b_slot']:labels['p2b_variant']]
    require(len(fragment) == FLIP_END - FLIP_START and
            parts[group][start:end] == fragment,
            'P2b Flip module is not identical to source emitter')
    return start, end, failure, fragment


def replace_raw_flip_public(text: str) -> str:
    """Replace exactly 240 annotated audit bytes, including mixed DC.B/code."""
    anchor = 'L_BOBS_09E36:\np2b_slot:\n'
    first = text.find(anchor)
    last = text.find('p2b_variant:\n', first)
    require(first >= 0 and last > first and
            text.find(anchor, first + len(anchor)) < 0,
            'unique P2b Flip public/variant boundary not found')
    old = text[first:last]
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', old)
    require(matches and
            'ENTRY_BOBS_09E96:\np2b_public_flip:' in old and
            'p2b_flip_fail:' in old,
            'P2b public Flip audit labels missing')
    cursor = FLIP_START
    data = bytearray()
    for offset, value in matches:
        require(int(offset, 16) == cursor,
                'P2b Flip audit offsets are no longer contiguous')
        chunk = bytes.fromhex(value)
        data.extend(chunk)
        cursor += len(chunk)
    require(cursor == FLIP_END and
            bytes(data) == prove_flip_public_provenance()[3],
            'P2b public Flip raw/code bytes differ from authoritative emitter')
    return (text[:first] + 'L_BOBS_09E36:\n    include "' +
            FLIP_SOURCE_NAME + '"\n' + text[last:])


def replace_raw_planar_block(text: str) -> str:
    """Replace only the source-pinned 562-byte DC.B block, not other data."""
    first_line = ('    dc.b $53,$85,$66,$00,$FF,$DA,$4E,$75,$48,$E7,$CF,$FE'
                  '  ; +$0A286: 53856600FFDA4E75' + '48E7CFFE\n')
    # The source audit records a 12-byte line at $A286. The first eight
    # bytes close p2b_purge; the next four begin the materializer.
    # Keep the prefix as bytes, then insert the actual handwritten source.
    start = text.find(first_line)
    require(start >= 0, 'P2b source bytes at $A286 are not the pinned baseline')
    stop = text.find('L_BOBS_0A4C0:', start)
    require(stop > start, 'P2b owner data label missing after materializer')
    original_block = text[start:stop]
    lines = original_block.splitlines()
    require(len(lines) > 40 and all('dc.b ' in line for line in lines),
            'P2b materializer is not a contiguous unclassified data block')
    hexdump = ''.join(line.split('  ; +$')[1].split(': ')[1]
                      for line in lines)
    expected = bytes.fromhex(hexdump)
    require(len(expected) == PLANAR_END - 0xA286,
            'unclassified materializer byte coverage changed')
    require(expected[:8] == bytes.fromhex('53856600ffda4e75'),
            'P2b purge epilogue changed')
    require(expected[8:] == prove_planar_provenance()[3],
            'unclassified bytes differ from original P2b code emitter')
    replacement = ('    dc.b $53,$85,$66,$00,$FF,$DA,$4E,$75'
                   '  ; +$0A286: 53856600FFDA4E75\n'
                   '    include "' + PLANAR_SOURCE_NAME + '"\n')
    return text[:start] + replacement + text[stop:]


def replace_raw_p2b_slot_data(text: str) -> str:
    """Convert source-proven 4-byte owner + 4096-byte object table from raw."""
    anchor = 'L_BOBS_0A4C0:\np2b_owner:\n'
    first = text.find(anchor)
    last = text.find('ENTRY_BOBS_0B4C4:', first)
    require(first >= 0 and last > first,
            'BOBS 64-slot zeroed data has changed from the source baseline')
    lines = text[first + len(anchor):last].splitlines()
    require(len(lines) > 300 and all(line.startswith('    dc.b ') for line in lines),
            'raw P2b slots are not a contiguous zeroed data region')
    hexdump = ''.join(line.split('  ; +$')[1].split(': ')[1]
                      for line in lines)
    values = bytes.fromhex(hexdump)
    require(len(values) == 4 + 64 * 64 and not any(values),
            'BOBS p2b_owner/p2b_slots bytes differ from emitter zeros')
    return (text[:first] + 'L_BOBS_0A4C0:\n    include "' +
            SLOTS_SOURCE_NAME + '"\n' + text[last:])


def staged_sources(folder: Path, *, module_text: str | None = None,
                   planes_text: str | None = None,
                   planar_text: str | None = None,
                   flip_text: str | None = None) -> None:
    """Create one complete AP20 assembly project; replace only verified P2d region."""
    require(AUDIT_DIR.is_dir(), f'missing audited P2d assembly: {AUDIT_DIR}')
    require(EDITABLE_FILE.is_file(), f'missing authored module: {EDITABLE_FILE}')
    require(PLANES_FILE.is_file(), f'missing authored module: {PLANES_FILE}')
    require(PLANAR_FILE.is_file(), f'missing authored module: {PLANAR_FILE}')
    require(FLIP_FILE.is_file(), f'missing authored module: {FLIP_FILE}')
    require(SLOTS_FILE.is_file(), f'missing source-owned data: {SLOTS_FILE}')
    for name in (MASTER_FILE, BOBS_FILE, 'M19_P2D_UNIT142_MC68020.s',
                 'M19_P2D_UNIT153_MC68020.s',
                 'M19_P2D_UNIT156_MC68020.s'):
        p = AUDIT_DIR / name
        require(p.is_file(), f'missing audit source dependency: {p}')
        shutil.copyfile(p, folder / name)
    text = (folder / BOBS_FILE).read_text(encoding='ascii')
    text = replace_raw_flip_public(text)
    text = replace_raw_planar_block(text)
    text = replace_raw_p2b_slot_data(text)
    require(text.count(P2C_START_LABEL) == 1 and text.count(P2C_END_LABEL) == 1,
            'audited P2c assembly has ambiguous module boundaries')
    p2c_first = text.index(P2C_START_LABEL)
    p2c_last = text.index(P2C_END_LABEL, p2c_first)
    require(text[p2c_first:p2c_last].count('p2c_reset_slot:') == 1 and
            'dc.b ' in text[p2c_first:p2c_last],
            'P2c reset slot missing from raw audit baseline')
    text = (text[:p2c_first] + '    include "' + P2C_SOURCE_NAME + '"\n' +
            text[p2c_last:])
    require(text.count(START_LABEL) == 1 and text.count(END_LABEL) == 1,
            'audited P2d assembly has ambiguous module boundaries')
    first = text.index(START_LABEL)
    last = text.index(END_LABEL, first)
    old_region = text[first:last]
    require(old_region.count('p2d_close:') == 1 and
            old_region.count('p2d_mode:') == 1 and
            'dc.b ' in old_region, 'mismatched historical P2d assembly region')
    text = (text[:first] + '    include "' + SOURCE_NAME + '"\n' +
            text[last:])
    (folder / BOBS_FILE).write_text(text, encoding='ascii', newline='\n')
    source = module_text if module_text is not None else EDITABLE_FILE.read_text('ascii')
    require(source.count('p2d_public_auto_update:') == 1 and
            source.count('p2d_close:') == 1 and
            source.count('p2d_mode:') == 1 and
            source.count('dcb.b 12,0') == 1,
            'handwritten source missing mandatory routines or state')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', source),
            'unclassified data directive inside handwritten routine')
    (folder / SOURCE_NAME).write_text(source, encoding='ascii', newline='\n')
    planes_source = (planes_text if planes_text is not None
                     else PLANES_FILE.read_text('ascii'))
    require(planes_source.count('p2c_public_planes:') == 1 and
            planes_source.count('p2c_apply_planes:') == 1 and
            planes_source.count('p2c_reset_slot:') == 1,
            'handwritten P2c module incomplete')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', planes_source),
            'unclassified opcode/data directive inside P2c module')
    (folder / P2C_SOURCE_NAME).write_text(planes_source, encoding='ascii', newline='\n')
    flip_source = (flip_text if flip_text is not None
                   else FLIP_FILE.read_text('ascii'))
    for label in ('p2b_slot:', 'p2b_mode:', 'p2b_free_slot:',
                  'p2b_public_flip:', 'p2b_flip_fail:'):
        require(flip_source.count(label) == 1,
                f'P2b public Flip module missing {label}')
    # Vasm chooses 6/10-byte LEA variants, whereas the source emitter
    # uses exactly 8 bytes: 41FB 0170 + PC-relative full displacement.
    # These are the four explicitly classified instruction exceptions.
    cleaned = flip_source
    for symbol, count in (('p2b_slots', 1), ('p2b_owner', 3)):
        pair = ('    dc.w $41FB,$0170\n    dc.l ' + symbol + '-(*-2)')
        require(flip_source.count(pair) == count,
                f'P2b exact PC32 LEA mismatch: {symbol}')
        cleaned = cleaned.replace(pair, '')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', cleaned),
            'unclassified opcode/data directive inside P2b public Flip')
    (folder / FLIP_SOURCE_NAME).write_text(flip_source, encoding='ascii',
                                           newline='\n')
    planar_source = (planar_text if planar_text is not None
                     else PLANAR_FILE.read_text('ascii'))
    for label in ('p2b_planar_orientation_entry:',
                  'p2b_planar_measure:', 'p2b_planar_chip_prepare_entry:'):
        require(planar_source.count(label) == 1,
                f'P2b materializer source label missing: {label}')
    # 68020 MULU.L D4,D3: the emitter uses a noncanonical but legal
    # extension word $3000; vasm's canonical choice is $3003.
    # Preserve ONE source-verified legacy encoding, fail on all other DC opcodes.
    exception = '    dc.w $4C04,$3000   ; exact MULU.L D4,D3; documented encoder exception'
    require(planar_source.count(exception) == 1,
            'P2b original MULU.L extension exception altered')
    inspected = planar_source.replace(exception, '')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', inspected),
            'unclassified opcode/data directive inside P2b materializer')
    (folder / PLANAR_SOURCE_NAME).write_text(planar_source,
                                            encoding='ascii', newline='\n')
    slots = SLOTS_FILE.read_text('ascii')
    require(slots.count('p2b_owner:') == 1 and
            slots.count('p2b_slots:') == 1 and
            slots.count('dcb.b P2B_SLOT_STATE_BYTES,0') == 1 and
            slots.count('P2B_SLOT_COUNT         equ 64') == 1 and
            slots.count('P2B_SLOT_BYTES         equ 64') == 1,
            'P2b table source contract changed')
    (folder / SLOTS_SOURCE_NAME).write_text(slots,
                                           encoding='ascii', newline='\n')


def verify_link(original: bytes, image: bytes, group: int,
                planes_start: int, control_start: int, control_end: int,
                *, allow_edited: bool) -> list[int]:
    """Reject AP20 topology/geometry changes and changes outside the owned code."""
    if len(image) != len(original):
        try:
            _, op, _ = unpack_ap20(original)
            _, np, _ = unpack_ap20(image)
            first = next((i for i, (a, b) in enumerate(zip(op[group], np[group]))
                          if a != b), min(len(op[group]), len(np[group])))
            import difflib
            old_frag = op[group][PLANAR_START:PLANAR_END]
            delta = len(np[group]) - len(op[group])
            new_frag = np[group][PLANAR_START:PLANAR_END+delta]
            matcher = difflib.SequenceMatcher(None, old_frag, new_frag,
                                              autojunk=False)
            changes = []
            for tag, a, b, c, d in matcher.get_opcodes():
                if tag != 'equal':
                    changes.append((tag, f'{PLANAR_START+a:05X}',
                                    old_frag[a:b].hex(), new_frag[c:d].hex()))
            context = (f'BOBS original={len(op[group])} compiled={len(np[group])}; '
                       f'first_diff=${first:05X}; '
                       f'orig={op[group][first:first+24].hex()}; '
                       f'new={np[group][first:first+24].hex()}; '
                       f'PLANAR changes={changes[:16]}')
        except Exception as exc:
            context = f'AP20 parse failed: {exc}'
        raise SourceError(f'changed binary length {len(image)}, expected '
                          f'{len(original)}; {context}')
    old_tokens, old_parts, old_title = unpack_ap20(original)
    tokens, parts, title = unpack_ap20(image)
    require((tokens, title, len(parts)) == (old_tokens, old_title, len(old_parts)),
            'AP20 tokens, title, or entry count changed')
    require(all(x == y for i, (x, y) in enumerate(zip(old_parts, parts)) if i != group),
            'modified an AP20 unit outside the controlled P2d BOBS module')
    require(len(parts[group]) == len(old_parts[group]),
            'BOBS size/entry offsets changed; variable-length relocation NOT supported')
    differences = [i for i, (a, b) in enumerate(zip(old_parts[group], parts[group])) if a != b]
    planar_start, planar_end, _, _ = prove_planar_provenance()
    flip_start, flip_end, _, _ = prove_flip_public_provenance()
    require(all((planes_start <= i < control_end) or
                (planar_start <= i < planar_end) or
                (flip_start <= i < flip_end) for i in differences),
            'a byte outside the authored P2b/P2c/P2d modules differs from the reference')
    if not allow_edited:
        require(not differences and image == original,
                f'baseline assembly differs in BOBS at {differences[:8]}')
    report = inspect(parse(image))
    require(not report['issues'], f'AP20 parsing issues: {report["issues"]}')
    return differences


def build(assembler: Path, target: Path, *, allow_edited: bool = False,
          module_text: str | None = None,
          planes_text: str | None = None,
          planar_text: str | None = None,
          flip_text: str | None = None) -> tuple[bytes, list[int]]:
    original, group, planes_start, control_start, control_end, _, _ = prove_source_provenance()
    target.mkdir(parents=True, exist_ok=True)
    staged_sources(target, module_text=module_text, planes_text=planes_text,
                   planar_text=planar_text, flip_text=flip_text)
    output = target / ('M19_P2D_EDITED_UNTESTED.Lib' if allow_edited
                       else 'M19_P2D_ASM_REBUILT_CHECK.Lib')
    result = checked_vasm(assembler, target / MASTER_FILE, output)
    differences = verify_link(original, result, group, planes_start,
                              control_start, control_end, allow_edited=allow_edited)
    print('P2D ASM', 'EDITED UNTESTED' if allow_edited else 'BASELINE EXACT',
          'BYTES', len(result), 'DIFF', len(differences),
          'SHA256', sha256(result).hexdigest())
    return result, differences


def test_editability(assembler: Path) -> None:
    """Prove a REAL one-instruction edit changes only its own machine-code byte."""
    _, group, planes_start, start, end, done, planes_fail = prove_source_provenance()
    with TemporaryDirectory(prefix='p2d_native_edit_') as d:
        root = Path(d)
        original, baseline_diff = build(assembler, root/'baseline')
        require(not baseline_diff, 'no-edit compile changed the binary')
        source = EDITABLE_FILE.read_text('ascii')
        before = 'p2d_set_done:\n    moveq #1,d3'
        require(source.count(before) == 1, 'no unique source instruction to edit')
        altered = source.replace(before, 'p2d_set_done:\n    moveq #2,d3')
        modified, diffs = build(assembler, root/'modified',
                                allow_edited=True, module_text=altered)
        require(diffs == [done+1], f'wrong edited byte(s): {diffs[:12]}, expected {done+1}')
        require(modified != original and len(modified) == len(original),
                'edit was ignored or changed AP20 size')
        require(unpack_ap20(modified)[1][group][done:done+2] == b'\x76\x02',
                'modified instruction did not encode MOVEQ #2,D3')
        require(start <= done < end, 'edit escaped the authored module')

        planes_source = PLANES_FILE.read_text('ascii')
        needle = 'p2c_set_fail:\n    moveq #0,d3'
        require(planes_source.count(needle) == 1,
                'missing uniquely modifiable P2c failure instruction')
        planes_edited = planes_source.replace(needle,
                        'p2c_set_fail:\n    moveq #1,d3')
        modified_planes, plane_diffs = build(
            assembler, root/'modified_planes', allow_edited=True,
            planes_text=planes_edited)
        require(plane_diffs == [planes_fail+1],
                f'P2c wrong edited byte: {plane_diffs}, expected {planes_fail+1}')
        require(unpack_ap20(modified_planes)[1][group][planes_fail:planes_fail+2]
                == b'\x76\x01', 'P2c modified opcode did not assemble')
        require(planes_start <= planes_fail < start,
                'P2c modified opcode escaped the authored module')

        planar_start, planar_end, invalid, _ = prove_planar_provenance()
        planar_source = PLANAR_FILE.read_text('ascii')
        needle = 'p2b_planar_invalid:\n    moveq #0,d3'
        require(planar_source.count(needle) == 1,
                'P2b planar failure opcode not uniquely editable')
        planar_edited = planar_source.replace(
            needle, 'p2b_planar_invalid:\n    moveq #1,d3')
        changed_planar, planar_diffs = build(
            assembler, root/'modified_planar', allow_edited=True,
            planar_text=planar_edited)
        require(planar_diffs == [invalid+1],
                f'P2b planar edit affected {planar_diffs}, expected {[invalid+1]}')
        require(unpack_ap20(changed_planar)[1][group][invalid:invalid+2] == b'\x76\x01',
                'P2b planar MOVEQ #1,D3 was not encoded')
        require(planar_start <= invalid < planar_end,
                'P2b modified opcode escaped authored materializer')

        flip_start, flip_end, flip_fail, _ = prove_flip_public_provenance()
        flip_source = FLIP_FILE.read_text('ascii')
        flip_needle = 'p2b_flip_fail:\n    moveq #0,d3'
        require(flip_source.count(flip_needle) == 1,
                'P2b public Flip failure opcode not uniquely editable')
        flip_edit = flip_source.replace(
            flip_needle, 'p2b_flip_fail:\n    moveq #1,d3')
        changed_flip, flip_diffs = build(
            assembler, root/'modified_flip', allow_edited=True,
            flip_text=flip_edit)
        require(flip_diffs == [flip_fail+1],
                f'P2b Flip edit changed {flip_diffs}, expected {[flip_fail+1]}')
        require(unpack_ap20(changed_flip)[1][group][flip_fail:flip_fail+2]
                == b'\x76\x01', 'P2b Flip failure instruction was not encoded')
        require(flip_start <= flip_fail < flip_end,
                'P2b public Flip edit escaped authored region')
    print('P2D_EDITABILITY_TEST PASS: MOVEQ #1,D3 -> #2,D3, one byte changed,')
    print('P2C_EDITABILITY_TEST PASS: MOVEQ #0,D3 -> #1,D3, one byte changed')
    print('P2B_PLANAR_EDITABILITY_TEST PASS: MOVEQ #0,D3 -> #1,D3, one byte changed')
    print('P2B_FLIP_EDITABILITY_TEST PASS: MOVEQ #0,D3 -> #1,D3, one byte changed')
    print('AP20 topology and all other groups unchanged; NOT a WinUAE Runtime test')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vasm', required=True, type=Path)
    parser.add_argument('--out', type=Path,
                        default=ROOT/'src'/'generated'/'p2d_editable')
    parser.add_argument('--allow-edited', action='store_true',
                        help='Output a same-size edited candidate ONLY in --out, NOT dist/')
    parser.add_argument('--self-test-edit', action='store_true',
                        help='Prove real modified-source vasm roundtrip without publishing a Lib')
    args = parser.parse_args()
    try:
        if args.self_test_edit:
            test_editability(args.vasm)
        else:
            build(args.vasm, args.out.resolve(), allow_edited=args.allow_edited)
        return 0
    except (SourceError, AssertionError, OSError, ValueError) as exc:
        print('[ERROR] P2d editable ASM: '+str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
