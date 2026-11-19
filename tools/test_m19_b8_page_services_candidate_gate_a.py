#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exact in-memory AP20 source ancestry and token preservation for B8."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect,parse,walk_tokens
from compiler_relocation import unpack_ap20
from build_m19_b8_page_services_in_memory import build_b8_page_services
from build_m19_b8_planar_snapshot_in_memory import build_b8_private_snapshot
from m19_b8_back_selector_emit import emit_b8_back_selector
from m19_b8_planar_snapshot_emit import emit_planar_snapshot_core
from m19_b8_snapshot_pool_emit import emit_b8_snapshot_pool

ROOT=Path(__file__).resolve().parents[1]


def main():
    lib=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    asc=(ROOT/'tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc').read_bytes()
    assert len(lib)==102400
    assert sha256(lib).hexdigest()=='242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'
    assert len(asc)==10911
    assert sha256(asc).hexdigest()=='a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec'
    a,oldmeta=build_b8_private_snapshot()
    b,meta=build_b8_page_services()
    assert a!=b and oldmeta['sha256']==meta['predecessor_sha']
    assert meta['native_groups']==[142,153,156,177]
    assert meta['public_commands']==86 and meta['ap20_entries']==181
    assert meta['selector_bytes']==600 and meta['pool_bytes']==1172
    assert meta['appended_bytes']==1772
    assert meta['bobs_bytes']<32766 and meta['pc16_max']<32766
    tokens,parts,_=unpack_ap20(a)
    newtokens,after,_=unpack_ap20(b)
    assert tokens==newtokens and len(parts)==len(after)==181
    core,_=emit_planar_snapshot_core()
    selector,_=emit_b8_back_selector()
    pool,_=emit_b8_snapshot_pool()
    assert after[177]==parts[177]+selector[len(core):]+pool
    assert all(after[i]==parts[i] for i in range(181) if i!=177)
    assert inspect(parse(b))['tokens']==inspect(parse(a))['tokens']
    assert not any(t['name'] in ('aga bob clear','aga bob update')
                   for t in walk_tokens(newtokens))
    print('M19 B8 private page services SOURCE-ONLY AP20 PASS;',meta)
    print('B7-m2 installed Lib and current ASC untouched')


if __name__=='__main__':main()
