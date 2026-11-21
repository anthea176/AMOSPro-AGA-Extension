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

AUDIT_DIR = ROOT / 'src' / 'asm_migration' / 'm19_p2d'
EDITABLE_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2D_CONTROLS_MC68020.s'
BOBS_FILE = 'M19_P2D_BOBS_MC68020.s'
MASTER_FILE = 'M19_P2D_AP20_SOURCE.s'
SOURCE_NAME = 'M19_P2D_CONTROLS_MC68020.s'
START_LABEL = 'p2d_public_auto_update:'
END_LABEL = 'L_BOBS_0B72A:'


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


def prove_source_provenance() -> tuple[bytes, int, int, int, int]:
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
    require((start, end, end-start) == (0xB58C, 0xB72A, 414),
            f'P2d handwritten module boundaries changed: {start:x}:{end:x}')
    require(parts[group][done:done+2] == bytes.fromhex('7601'),
            'expected two-byte moveq #1,d3 at p2d_set_done missing')
    return lib, group, start, end, done


def staged_sources(folder: Path, *, module_text: str | None = None) -> None:
    """Create one complete AP20 assembly project; replace only verified P2d region."""
    require(AUDIT_DIR.is_dir(), f'missing audited P2d assembly: {AUDIT_DIR}')
    require(EDITABLE_FILE.is_file(), f'missing authored module: {EDITABLE_FILE}')
    for name in (MASTER_FILE, BOBS_FILE, 'M19_P2D_UNIT142_MC68020.s',
                 'M19_P2D_UNIT153_MC68020.s',
                 'M19_P2D_UNIT156_MC68020.s'):
        p = AUDIT_DIR / name
        require(p.is_file(), f'missing audit source dependency: {p}')
        shutil.copyfile(p, folder / name)
    text = (folder / BOBS_FILE).read_text(encoding='ascii')
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


def verify_link(original: bytes, image: bytes, group: int,
                start: int, end: int, *, allow_edited: bool) -> list[int]:
    """Reject AP20 topology/geometry changes and changes outside the owned code."""
    require(len(image) == len(original),
            f'changed binary length {len(image)}, expected {len(original)}')
    old_tokens, old_parts, old_title = unpack_ap20(original)
    tokens, parts, title = unpack_ap20(image)
    require((tokens, title, len(parts)) == (old_tokens, old_title, len(old_parts)),
            'AP20 tokens, title, or entry count changed')
    require(all(x == y for i, (x, y) in enumerate(zip(old_parts, parts)) if i != group),
            'modified an AP20 unit outside the controlled P2d BOBS module')
    require(len(parts[group]) == len(old_parts[group]),
            'BOBS size/entry offsets changed; variable-length relocation NOT supported')
    differences = [i for i, (a, b) in enumerate(zip(old_parts[group], parts[group])) if a != b]
    require(all(start <= i < end for i in differences),
            'a byte outside the authored P2d module differs from the reference')
    if not allow_edited:
        require(not differences and image == original,
                f'baseline assembly differs in BOBS at {differences[:8]}')
    report = inspect(parse(image))
    require(not report['issues'], f'AP20 parsing issues: {report["issues"]}')
    return differences


def build(assembler: Path, target: Path, *, allow_edited: bool = False,
          module_text: str | None = None) -> tuple[bytes, list[int]]:
    original, group, start, end, _ = prove_source_provenance()
    target.mkdir(parents=True, exist_ok=True)
    staged_sources(target, module_text=module_text)
    output = target / ('M19_P2D_EDITED_UNTESTED.Lib' if allow_edited
                       else 'M19_P2D_ASM_REBUILT_CHECK.Lib')
    result = checked_vasm(assembler, target / MASTER_FILE, output)
    differences = verify_link(original, result, group, start, end,
                              allow_edited=allow_edited)
    print('P2D ASM', 'EDITED UNTESTED' if allow_edited else 'BASELINE EXACT',
          'BYTES', len(result), 'DIFF', len(differences),
          'SHA256', sha256(result).hexdigest())
    return result, differences


def test_editability(assembler: Path) -> None:
    """Prove a REAL one-instruction edit changes only its own machine-code byte."""
    _, group, start, end, done = prove_source_provenance()
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
    print('P2D_EDITABILITY_TEST PASS: MOVEQ #1,D3 -> #2,D3, one byte changed,')
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
