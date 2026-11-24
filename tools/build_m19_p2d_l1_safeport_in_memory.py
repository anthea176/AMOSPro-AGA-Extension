#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build P2d L1 SafePort candidate from verified editable Motorola source.

Never edit the P2d master or use a disassembly/installed .Lib as new code.
The overlay is assembled by vasm -m68020 in a disposable directory; only
the returned in-memory image is the candidate. No installable output.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import shutil
from struct import unpack_from
import subprocess
import tempfile

from active_library import P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, S1P1F_SHA, verify_active, verify_p2d_l2b
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, walk_tokens
from build_m19_p2d_in_memory import build_p2d
from compiler_bridge_v2_probe import MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'src/native/m19_p2d'
OVERLAY = ROOT / 'src/native/m19_p2d_l1'
MASTER = 'M19_P2D_LINKED_EDITABLE.s'
UNIT = 142
BASE_UNIT_SIZE = 62740
PATCHES = (
    ('M19_UNIT142_BLOCK_00C9E_MC68020.s',
     '    move.l #UNIT142_BLOCK_00C9E_EDIT,d0\n',
     'M19_L1_BACK_FILL_ENTRY_MC68020.s', 0x00CE8, bytes.fromhex('203c00000080')),
    ('M19_UNIT142_IFF_LOAD_BODY_MC68020.s',
     '    movea.l (a5),a2\n    movea.l 8(a2),a6\n    jsr -228(a6)\n',
     'M19_L1_IFF_ENTRY_MC68020.s', 0x00E88, bytes.fromhex('24552c6a0008')),
)
TAIL = 'M19_L1_SAFEPORT_TAIL_MC68020.s'
TITLE = b'AMOSPro AGA M19 P2d L1 SafePort MC68020 candidate\0$VER: AMOSPro_AGA M19 P2d-L1\0'
TITLE += bytes(len(TITLE) & 1)


def need(condition, message):
    if not condition:
        raise ValueError('P2d L1: ' + message)


def assemble(vasm: Path, folder: Path) -> bytes:
    output = folder / 'assembled.bin'
    result = subprocess.run(
        [str(vasm), '-Fbin', '-m68020', '-no-opt', '-quiet', '-o',
         str(output), MASTER], cwd=folder, capture_output=True, text=True,
        timeout=120)
    need(result.returncode == 0, 'vasm: ' + result.stdout + result.stderr)
    return output.read_bytes()


def build_l1(vasm: Path):
    vasm = vasm.resolve()
    need(vasm.is_file(), 'pinned vasm executable required')
    active, protected, _ = verify_active(ROOT)
    need(sha256(active).hexdigest() in (S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, S1P1F_SHA),
         'active S1-P1e/L2 identity changed; new authorization required')
    base, meta = build_p2d()
    need(sha256(base).hexdigest() == P2D_SHA, 'P2d source SHA mismatch')
    if protected != base:
        verify_p2d_l2b(protected, base)
    need(len(base) == 136020 and (meta['commands'], meta['entries']) == (100,203),
         'unexpected P2d size/API')
    tok, parts, title = unpack_ap20(base)
    need(len(parts[UNIT]) == BASE_UNIT_SIZE, 'UNIT142 reference size changed')
    with tempfile.TemporaryDirectory(prefix='aga-p2d-l1-') as temp:
        folder = Path(temp) / 'source'
        shutil.copytree(BASE, folder)
        need(assemble(vasm, folder) == base, 'editable P2d master not exact')
        for filename, anchor, snippet, offset, expected in PATCHES:
            need(parts[UNIT][offset:offset+6] == expected,
                 'source-proven entry anchor drift: ' + filename)
            path = folder / filename
            text = path.read_text(encoding='ascii')
            need(text.count(anchor) == 1, 'ambiguous source anchor: ' + filename)
            replacement = '    include "' + snippet + '"\n'
            if filename.endswith('IFF_LOAD_BODY_MC68020.s'):
                replacement += '    jsr -228(a6)\n'
            path.write_text(text.replace(anchor, replacement), encoding='ascii')
            shutil.copyfile(OVERLAY / snippet, folder / snippet)
        master_unit = folder / 'M19_P2D_UNIT142_EDITABLE.s'
        with master_unit.open('a', encoding='ascii') as stream:
            stream.write('\n    include "' + TAIL + '"\n')
        shutil.copyfile(OVERLAY / TAIL, folder / TAIL)
        native_assembled = assemble(vasm, folder)
    newtok, newparts, newtitle = unpack_ap20(native_assembled)
    need(newtok == tok and newtitle == title and len(newparts) == len(parts),
         'assembler changed P2d public API/title/directory count')
    need(all(p == q for i,(p,q) in enumerate(zip(parts,newparts)) if i != UNIT),
         'non-UNIT142 entries changed')
    oldunit, newunit = parts[UNIT], newparts[UNIT]
    need(BASE_UNIT_SIZE < len(newunit) <= MAX_UNIT_BYTES and len(newunit)%2 == 0,
         'UNIT142 exceeds Compiler WORD count/alignment')
    restored = bytearray(newunit[:BASE_UNIT_SIZE])
    targets = []
    for _,_,_,offset,expected in PATCHES:
        need(newunit[offset:offset+2] == b'\x60\xff',
             'expected MC68020 BRA.L at source patch')
        target = offset + 2 + unpack_from('>i',newunit,offset+2)[0]
        need(BASE_UNIT_SIZE <= target < len(newunit) and target%2 == 0,
             'branch target not in appended native helper')
        targets.append(target)
        restored[offset:offset+6] = expected
    need(bytes(restored) == oldunit, 'legacy code/data moved or changed')
    need(pc16_displacements(newparts) == pc16_displacements(parts),
         'legacy AP20 PC16 displacement changed')
    image = repack_ap20(base, tok, newparts, TITLE)
    need(unpack_ap20(image) == (tok,newparts,TITLE), 'AP20 round-trip failed')
    need(not inspect(parse(image))['issues'], 'AP20 audit issues')
    # AP20 walk includes the initial unnamed dummy token; count named API
    # exactly as the repository's bilingual README coverage gate does.
    named = {r['name'] for r in walk_tokens(tok) if r['name'].lower().startswith(
        ('aga ', 'get aga ', 'make aga ', 'no aga '))}
    need(len(named) == 100, 'public command count changed')
    need((ROOT/'dist/AMOSPro_AGA.Lib').read_bytes() == active
         and (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes() == protected,
         'protected binary changed')
    return image, dict(sha256=sha256(image).hexdigest(), bytes=len(image),
                       commands=100, entries=203, unit142=len(newunit),
                       appended=len(newunit)-BASE_UNIT_SIZE, targets=targets,
                       pc16_max=max(map(abs,pc16_displacements(newparts).values())),
                       runtime_tested=False, compiler_tested=False)


if __name__ == '__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm',type=Path,required=True)
    _,info=build_l1(cli.parse_args().vasm)
    print('P2D_L1_SOURCE_IN_MEMORY',info)
