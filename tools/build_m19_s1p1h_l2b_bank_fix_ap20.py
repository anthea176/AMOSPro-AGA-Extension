#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S1-P1h: source-assembled corrected publisher on exact P1g / L2b.
No writes to dist; preserve historical source builders and all prior entries.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import subprocess
import tempfile

from active_library import P2DL2B_SHA, S1P1G_SHA, S1P1H_SHA, verify_s1p1g, verify_s1p1h
from audit_ap20 import inspect, parse, token_role_issues
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_s1p1g_l2b_get_sprite_ap20 import build_s1p1g
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'src/native/m19_s1'
MASTER='M19_S1P1H_BANK_PUBLIC_MC68020.s'
HISTORICAL='M19_S1P1D_BANK_PUBLIC_MC68020.s'


def assemble(vasm: Path, source: str) -> bytes:
    with tempfile.TemporaryDirectory(prefix='aga-s1p1h-') as temp:
        out=Path(temp)/'native.bin'
        subprocess.run([str(vasm.resolve()), '-I', str(NATIVE), '-Fbin',
                        '-m68020', '-no-opt', '-quiet', '-o', str(out),
                        str(NATIVE/source)], check=True, cwd=NATIVE)
        return out.read_bytes()


def build_s1p1h(vasm: Path):
    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert sha256(good).hexdigest()==P2DL2B_SHA
    historical=assemble(vasm,HISTORICAL)
    parent,meta=build_s1p1g(vasm,historical)
    assert sha256(parent).hexdigest()==S1P1G_SHA
    verify_s1p1g(parent,good)
    tok,old,title=unpack_ap20(parent)
    native=assemble(vasm,MASTER)
    assert len(native)>len(historical) and len(native)%2==0
    assert len(native)+len(DISPATCH_V2)<=MAX_UNIT_BYTES
    assert old[207]==DISPATCH_V2+historical
    assert len(old)==208 and native[:2]==historical[:2]==b'\x60\x00'
    parts=old[:207]+[DISPATCH_V2+native]
    title=title.replace(b'S1-P1g',b'S1-P1h')
    image=repack_ap20(parent,tok,parts,title)
    verify_s1p1h(image,good)
    if sha256(active).hexdigest()==S1P1H_SHA:
        assert image==active, 'Installed P1h differs from source reconstruction'
    assert unpack_ap20(image)==(tok,parts,title)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert [i for i,(a,b) in enumerate(zip(parts,old)) if a!=b]==[207]
    assert pc16_displacements(parts)==pc16_displacements(old)
    assert (ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()==active
    assert (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()==good
    return image,dict(meta,sha256=sha256(image).hexdigest(),bytes=len(image),
                      native_sha256=sha256(native).hexdigest(),native_size=len(native),
                      token_parent_sha256=S1P1G_SHA,commands=102,entries=208)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',type=Path,required=True)
    _,meta=build_s1p1h(p.parse_args().vasm)
    print('S1P1H source in memory:',meta,flush=True)
