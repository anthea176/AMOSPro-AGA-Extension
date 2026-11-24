#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2d-L2: compose the verified L1 image with a source-assembled B8 fix.

Never overwrite the canonical distribution, historical P2d source or tests.
Only a single BNE.W displacement and an appended native helper change BOBS.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import shutil
from struct import unpack_from
import tempfile

from active_library import P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, S1P1F_SHA, S1P1G_SHA, verify_active, verify_p2d_l2, verify_p2d_l2b
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse
from build_m19_p2d_in_memory import build_p2d
from build_m19_p2d_l1_safeport_in_memory import BASE, ROOT, assemble, build_l1
from compiler_bridge_v2_probe import MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20

L1_SHA = 'f3adabb4c7f0f8d103586ee8eeb6b1db6a3e3cde5fe86ca16788eceb7b65cbcb'
GROUP = 202
GROUP_SIZE = 60928
OVERLAY = ROOT / 'src/native/m19_p2d_l2'
SOURCE = 'M19_P2D_SUPPORT_TAIL_MC68020.s'
ENTRY = 'M19_L2_FIRST_BIND_ENTRY_MC68020.s'
TAIL = 'M19_L2_FIRST_BIND_TAIL_MC68020.s'
MASTER = 'M19_P2D_BOBS_EDITABLE.s'
ANCHOR = ('    move.l 20(a4),d0\n'
          '    andi.l #$00000001,d0\n'
          '    bne.w L_BOBS_0C07A\n'
          '    move.l 8(a4),d0\n')
TITLE = b'AMOSPro AGA M19 P2d L2 SafePort+B8 MC68020 candidate\0$VER: AMOSPro_AGA M19 P2d-L2\0'
TITLE += bytes(len(TITLE) & 1)


def need(condition, message):
    if not condition:
        raise ValueError('P2d L2: ' + message)


def source_branch(unit):
    # Confirm the known source instruction sequence INSIDE the pinned
    # selector, not a scan for guessed executable code or binary disassembly.
    pattern = bytes.fromhex('202c00140280000000016600')
    start, end = 0x0BE32, 0x0C07A
    at = unit.find(pattern, start, end)
    need(at >= start and unit.find(pattern, at+2, end) < 0,
         'first Bind source anchor missing/ambiguous')
    offset = at + len(pattern) - 2
    need(offset + 2 + unpack_from('>h',unit,offset+2)[0] == end,
         'old refusal branch target drift')
    need(unit[offset+4:offset+8] == bytes.fromhex('202c0008'),
         'selector continuation drift')
    return offset


def build_l2(vasm: Path):
    vasm = vasm.resolve()
    active, protected, _ = verify_active(ROOT)
    need(sha256(active).hexdigest() in (S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, S1P1F_SHA, S1P1G_SHA), 'active candidate changed')
    base, baseinfo = build_p2d()
    need(sha256(base).hexdigest() == P2D_SHA, 'P2d source provenance changed')
    if protected != base:
        verify_p2d_l2b(protected, base)
    l1, l1info = build_l1(vasm)
    need(len(l1) == 136248 and sha256(l1).hexdigest() == L1_SHA,
         'L1 Gate A exact predecessor changed')
    tokens, prior, prior_title = unpack_ap20(base)
    l1tok, l1parts, _ = unpack_ap20(l1)
    need(l1tok == tokens and len(l1parts) == len(prior) == 203,
         'L1 API changed')
    need(all(a == b for i,(a,b) in enumerate(zip(prior,l1parts)) if i != 142),
         'unexpected L1 changes')
    old = prior[GROUP]
    need(baseinfo['group'] == GROUP and len(old) == GROUP_SIZE, 'BOBS group drift')
    branch = source_branch(old)
    with tempfile.TemporaryDirectory(prefix='aga-p2d-l2-') as temp:
        folder = Path(temp) / 'source'
        shutil.copytree(BASE, folder)
        path = folder / SOURCE
        text = path.read_text(encoding='ascii')
        need(text.count(ANCHOR) == 1, 'ambiguous assembly anchor')
        replacement = ('    move.l 20(a4),d0\n'
                       '    andi.l #$00000001,d0\n'
                       '    include "' + ENTRY + '"\n'
                       '    move.l 8(a4),d0\n')
        path.write_text(text.replace(ANCHOR,replacement),encoding='ascii')
        with (folder / MASTER).open('a',encoding='ascii') as stream:
            stream.write('\n    include "' + TAIL + '"\n')
        for name in (ENTRY,TAIL):
            shutil.copyfile(OVERLAY/name,folder/name)
        assembled = assemble(vasm,folder)
    t,p,title = unpack_ap20(assembled)
    need(t == tokens and title == prior_title and len(p) == len(prior),
         'assembled API/header drift')
    need(all(a == b for i,(a,b) in enumerate(zip(prior,p)) if i != GROUP),
         'assembler touched another native group or stub')
    new = p[GROUP]
    need(GROUP_SIZE < len(new) <= MAX_UNIT_BYTES and len(new)%2 == 0,
         'native Compiler size/alignment')
    need(new[branch:branch+2] == old[branch:branch+2] == b'\x66\x00',
         'expected same-width BNE.W')
    target = branch + 2 + unpack_from('>h',new,branch+2)[0]
    need(target == GROUP_SIZE, 'new branch does not target appended entry')
    restored = bytearray(new[:GROUP_SIZE])
    restored[branch:branch+4] = old[branch:branch+4]
    need(bytes(restored) == old, 'legacy BOBS instruction/data drift')
    parts = list(l1parts)
    parts[GROUP] = new
    links = pc16_displacements(parts)
    need(links == pc16_displacements(prior), 'original PC16 changed')
    image = repack_ap20(base,tokens,parts,TITLE)
    need(unpack_ap20(image) == (tokens,parts,TITLE), 'AP20 round trip')
    need(not inspect(parse(image))['issues'], 'AP20 audit issues')
    verify_p2d_l2(image, base)
    if sha256(active).hexdigest() == P2DL2_SHA:
        need(image == active, 'installed L2 differs from exact source rebuild')
    need((ROOT/'dist/AMOSPro_AGA.Lib').read_bytes() == active
         and (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes() == protected,
         'protected binaries changed')
    return image,dict(sha256=sha256(image).hexdigest(),bytes=len(image),
                      commands=100,entries=len(parts),l1_sha=L1_SHA,
                      group=GROUP,bobs_bytes=len(new),appended=len(new)-GROUP_SIZE,
                      branch=branch,target=target,pc16_max=max(map(abs,links.values())),
                      runtime_tested=False,compiler_tested=False)


if __name__ == '__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm',type=Path,required=True)
    _,meta=build_l2(cli.parse_args().vasm)
    print('P2D_L2_IN_MEMORY',meta)
