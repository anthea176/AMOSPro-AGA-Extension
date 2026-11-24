#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S1-P1f: reuse exact S1-P1e native source on promoted P2d-L2b.
No distribution writes. Source reconstruction and provenance are mandatory.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from active_library import P2DL2B_SHA, S1P1E_SHA, verify_active
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, walk_tokens
from build_m19_p2d_l2b_pattern_in_memory import build_l2b
from build_m19_s1p1e_get_sprite_ap20 import S1_APIS, build_get_aga_sprite_candidate
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20

ROOT = Path(__file__).resolve().parents[1]
TITLE = (b'AMOSPro AGA M19 S1-P1f L2b Get AGA Sprite MC68020 candidate\0'
         b'$VER: AGSP S1-P1f L2b non-distributed\0')
TITLE += bytes(len(TITLE) & 1)


def build_s1p1f(vasm: Path, native: bytes):
    active, good, _ = verify_active(ROOT)
    assert active == good and sha256(good).hexdigest() == P2DL2B_SHA
    base, meta = build_l2b(vasm)
    assert base == good and len(base) == 136708
    assert (meta['commands'], meta['entries']) == (100, 203)

    historical, old_meta = build_get_aga_sprite_candidate(native)
    assert len(historical) == 142000
    assert sha256(historical).hexdigest() == S1P1E_SHA
    assert old_meta['native_sha256'] == sha256(native).hexdigest()
    tok, parts, _ = unpack_ap20(base)
    sprite_tok, historical_parts, _ = unpack_ap20(historical)
    assert len(parts) == 203 and len(historical_parts) == 208
    assert [i for i, (a, b) in enumerate(zip(parts, historical_parts[:203]))
            if a != b] == [142, 202]
    before = list(walk_tokens(tok))
    after = list(walk_tokens(sprite_tok))
    assert after[:-2] == before
    assert [(t['name'], t['instruction'], t['function'], t['signature'])
            for t in after[-2:]] == [api[:4] for api in S1_APIS]

    suffix = historical_parts[203:]
    assert suffix[0] == suffix[2] == GETP
    assert suffix[1] == RBSR + bytes.fromhex('00cf00004e75')
    assert suffix[3] == RBSR + bytes.fromhex('00cf00084e75')
    assert suffix[4] == DISPATCH_V2 + native
    newparts = [*parts, *suffix]
    image = repack_ap20(base, sprite_tok, newparts, TITLE)
    assert unpack_ap20(image) == (sprite_tok, newparts, TITLE)
    assert not inspect(parse(image))['issues']
    links = pc16_displacements(newparts)
    old_links = pc16_displacements(parts)
    assert all(links[k] == v for k, v in old_links.items())
    assert set(links) == set(old_links) | {204, 206}
    assert (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes() == active
    assert (ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes() == good
    return image, dict(meta, sha256=sha256(image).hexdigest(),
                       bytes=len(image), commands=102, entries=208,
                       base_sha256=P2DL2B_SHA, sprite_parent_sha256=S1P1E_SHA,
                       native_sha256=sha256(native).hexdigest(),
                       native_size=len(native), pc16_max=max(map(abs, links.values())),
                       installable=False, runtime_tested=False, compiler_tested=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm', type=Path, required=True)
    p.add_argument('--native', type=Path, required=True)
    args = p.parse_args()
    _, meta = build_s1p1f(args.vasm, args.native.read_bytes())
    print('S1-P1f source in memory:', meta, flush=True)


if __name__ == '__main__':
    main()
