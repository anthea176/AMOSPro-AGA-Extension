#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S1-P1g: correct only the public Get AGA Sprite AP20 instruction signature.

All 208 code units are reconstructed by the historical source builder, then
preserved byte-for-byte. No native emitter changes and no distribution writes.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from active_library import S1P1F_SHA, S1P1G_SHA, verify_s1p1f, verify_s1p1g
from audit_ap20 import token, token_role_issues, walk_tokens
from build_m19_s1p1f_l2b_get_sprite_ap20 import TITLE as P1F_TITLE, build_s1p1f
from compiler_relocation import repack_ap20, unpack_ap20

ROOT = Path(__file__).resolve().parents[1]
TITLE = P1F_TITLE.replace(b'S1-P1f', b'S1-P1g')
S1_APIS = (('aga sprite bank', 204, 1, 'I0'),
           ('get aga sprite', 206, 1, 'I0,0,0,0,0,0'))


def correct_s1p1f(parent: bytes, protected: bytes) -> bytes:
    """Rebuild declarations from the verified L2b token table and source ABI."""
    verify_s1p1f(parent, protected)
    oldtok, _, _ = unpack_ap20(protected)
    _, parts, _ = unpack_ap20(parent)
    tokens = oldtok[:-6] + b''.join(token(*api) for api in S1_APIS) + oldtok[-6:]
    assert not token_role_issues(list(walk_tokens(tokens)))
    image = repack_ap20(parent, tokens, parts, TITLE)
    assert sha256(image).hexdigest() == S1P1G_SHA
    assert verify_s1p1g(image, protected) == parent
    return image


def build_s1p1g(vasm: Path, native: bytes):
    active = (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes()
    protected = (ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    parent, meta = build_s1p1f(vasm, native)
    assert sha256(parent).hexdigest() == S1P1F_SHA
    image = correct_s1p1f(parent, protected)
    if sha256(active).hexdigest() == S1P1G_SHA:
        assert image == active
    assert (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes() == active
    assert (ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes() == protected
    return image, dict(meta, sha256=S1P1G_SHA, bytes=len(image),
                       token_parent_sha256=S1P1F_SHA, instruction_signature=S1_APIS[-1][3])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm', type=Path, required=True)
    p.add_argument('--native', type=Path, required=True)
    a = p.parse_args()
    _, meta = build_s1p1g(a.vasm, a.native.read_bytes())
    print('S1-P1g source in memory:', meta, flush=True)


if __name__ == '__main__':
    main()
