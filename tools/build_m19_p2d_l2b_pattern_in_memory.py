#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-only L2b candidate: Pattern back bitmap and bounded SafePort.

Rebuild exact L2 first. Reassemble the authoritative P2d master with the
same two L1 overlays and the new Pattern overlay in a disposable directory.
Keep all B8/L2 bytes and all other groups unchanged. No installable output.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import shutil
from struct import unpack_from
import tempfile

from active_library import P2DL2_SHA, P2DL2B_SHA, S1P1F_SHA, S1P1G_SHA, S1P1H_SHA, SPRITE_L2B_HISTORICAL_SHAS, verify_active, verify_p2d_l2, verify_p2d_l2b, frozen_p2d
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, walk_tokens
from build_m19_p2d_l1_safeport_in_memory import (
    BASE, ROOT, OVERLAY as L1_OVERLAY, PATCHES as L1_PATCHES,
    TAIL as L1_TAIL, assemble,
)
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import RBSR, repack_ap20, unpack_ap20

OVERLAY = ROOT / 'src/native/m19_p2d_l2b'
UNIT = 142
PRIOR_SIZE = 62960
OFFSET = 0x0077A
SOURCE = 'M19_UNIT142_BLOCK_00764_MC68020.s'
ANCHOR = '    movea.l (a2),a4\n    movea.l 8(a2),a6\n'
OLD = bytes.fromhex('28522c6a0008')
ENTRY = 'M19_L2B_PATTERN_ENTRY_MC68020.s'
TAIL = 'M19_L2B_PATTERN_TAIL_MC68020.s'
TITLE = b'AMOSPro AGA M19 P2d L2b Safe Pattern MC68020 candidate\0$VER: AMOSPro_AGA M19 P2d-L2b\0'
TITLE += bytes(len(TITLE) & 1)


def need(condition, message):
    if not condition:
        raise ValueError('P2d L2b: ' + message)


def replace_once(path, anchor, replacement):
    source = path.read_text(encoding='ascii')
    need(source.count(anchor) == 1, 'ambiguous source anchor: ' + path.name)
    path.write_text(source.replace(anchor, replacement), encoding='ascii')


def build_l2b(vasm: Path):
    active, protected, _ = verify_active(ROOT)
    active_sha = sha256(active).hexdigest()
    need(active_sha in (P2DL2_SHA, P2DL2B_SHA, *SPRITE_L2B_HISTORICAL_SHAS),
         'exact installed L2 or L2b required; no implicit transition')
    prior, meta = build_l2(vasm)
    need(sha256(prior).hexdigest() == P2DL2_SHA, 'L2 source rebuild drift')
    if active_sha == P2DL2_SHA:
        need(prior == active, 'installed L2 differs from its source rebuild')
    base = frozen_p2d(protected)
    verify_p2d_l2(prior, base)
    tok, old, _ = unpack_ap20(prior)
    base_tok, base_parts, base_title = unpack_ap20(base)
    need(tok == base_tok and len(old) == len(base_parts) == 203,
         'L2 API drift')
    api = {row['name']: row for row in walk_tokens(tok)}
    idx = api['aga screen pattern']['instruction']
    need(idx == 14 and old[idx].startswith(RBSR) and
         unpack_from('>HH', old[idx], 2) == (UNIT, 0x00764-len(DISPATCH_V2)),
         'Pattern AP20 dispatch drift')
    need(len(old[UNIT]) == PRIOR_SIZE and old[UNIT][OFFSET:OFFSET+6] == OLD,
         'Pattern source anchor bytes drift')
    with tempfile.TemporaryDirectory(prefix='aga-p2d-l2b-') as temp:
        folder = Path(temp) / 'source'
        shutil.copytree(BASE, folder)
        for filename, anchor, snippet, _, _ in L1_PATCHES:
            replacement = '    include "' + snippet + '"\n'
            if filename.endswith('IFF_LOAD_BODY_MC68020.s'):
                replacement += '    jsr -228(a6)\n'
            replace_once(folder / filename, anchor, replacement)
            shutil.copyfile(L1_OVERLAY / snippet, folder / snippet)
        replace_once(folder / SOURCE, ANCHOR, '    include "' + ENTRY + '"\n')
        for origin, name in ((L1_OVERLAY, L1_TAIL), (OVERLAY, ENTRY), (OVERLAY, TAIL)):
            shutil.copyfile(origin / name, folder / name)
        master = folder / 'M19_P2D_UNIT142_EDITABLE.s'
        with master.open('a', encoding='ascii') as stream:
            stream.write('\n    include "' + L1_TAIL + '"\n')
            stream.write('    include "' + TAIL + '"\n')
        assembled = assemble(vasm.resolve(), folder)
    t, p, title = unpack_ap20(assembled)
    need(t == base_tok and title == base_title and len(p) == len(base_parts),
         'assembler changed API or directory')
    need(all(a == b for i, (a, b) in enumerate(zip(p, base_parts)) if i != UNIT),
         'assembler changed another native group')
    new = p[UNIT]
    need(PRIOR_SIZE < len(new) <= MAX_UNIT_BYTES and len(new) % 2 == 0,
         'Compiler native unit size/alignment')
    need(new[OFFSET:OFFSET+2] == bytes.fromhex('60ff'), 'expected MC68020 BRA.L')
    target = OFFSET + 2 + unpack_from('>i', new, OFFSET+2)[0]
    need(target == PRIOR_SIZE, 'entry must target appended source')
    restored = bytearray(new[:PRIOR_SIZE])
    restored[OFFSET:OFFSET+6] = OLD
    need(bytes(restored) == old[UNIT], 'legacy or L1 bytes changed')
    parts = list(old)
    parts[UNIT] = new
    need(pc16_displacements(parts) == pc16_displacements(old), 'AP20 PC16 changed')
    image = repack_ap20(prior, tok, parts, TITLE)
    need(unpack_ap20(image) == (tok, parts, TITLE), 'AP20 round trip')
    need(not inspect(parse(image))['issues'], 'HUNK/AP20 audit')
    need([i for i, (a, b) in enumerate(zip(old, parts)) if a != b] == [UNIT],
         'non-Pattern group changed')
    need((ROOT/'dist/AMOSPro_AGA.Lib').read_bytes() == active and
         (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes() == protected,
         'distribution changed')
    verify_p2d_l2b(image, base)
    if active_sha == P2DL2B_SHA:
        need(image == active, 'installed L2b differs from exact source rebuild')
    elif active_sha in (*SPRITE_L2B_HISTORICAL_SHAS):
        need(image == protected, 'protected L2b differs from exact source rebuild')
    return image, dict(meta, sha256=sha256(image).hexdigest(), bytes=len(image),
                       unit142=len(new), pattern_appended=len(new)-PRIOR_SIZE,
                       pattern_branch=OFFSET, pattern_target=target,
                       predecessor=P2DL2_SHA)


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm', type=Path, required=True)
    _, metadata = build_l2b(cli.parse_args().vasm)
    print('P2D L2B SOURCE IN MEMORY', metadata, flush=True)
