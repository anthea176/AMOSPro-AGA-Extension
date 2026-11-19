#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""In-memory AP20 HUNK, B7-m2 frozen ancestry and native group isolation."""
from __future__ import annotations

from pathlib import Path
from hashlib import sha256

from audit_ap20 import inspect,parse,walk_tokens
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import unpack_ap20
from build_m19_b7m2_close_reset_in_memory import build_close_reset
from build_m19_b8_fifth_group_in_memory import build_b8_fifth_group
from m19_b8_back_selector_emit import emit_b8_back_selector
from m19_b8_snapshot_pool_emit import emit_b8_snapshot_pool

ROOT=Path(__file__).resolve().parents[1]


def main():
    base,origin=build_close_reset()
    installed=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    current=(ROOT/'tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc').read_bytes()
    assert installed==base
    assert sha256(installed).hexdigest()=='242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'
    assert len(current)==10911
    assert sha256(current).hexdigest()=='a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec'
    candidate,meta=build_b8_fifth_group()
    assert candidate!=installed
    assert meta['base_sha']==origin['sha256']
    assert meta['public_commands']==86
    assert meta['ap20_entries']==182
    assert meta['native_groups']==[142,153,156,177,181]
    assert meta['fifth_unit_bytes']==3606
    assert meta['old_pc16_max']==meta['new_pc16_max']
    tokens,parts,_=unpack_ap20(base)
    n_tokens,after,_=unpack_ap20(candidate)
    assert n_tokens==tokens and len(after)==len(parts)+1
    assert after[:len(parts)]==parts
    core,_=emit_b8_back_selector()
    pool,_=emit_b8_snapshot_pool()
    assert after[181]==DISPATCH_V2+core+pool
    assert inspect(parse(candidate))['tokens']==inspect(parse(base))['tokens']
    assert not any(t['name'] in ('aga bob clear','aga bob update')
                   for t in walk_tokens(tokens))
    print('M19 B8 fifth native group SOURCE-ONLY Gate A AP20 PASS',meta)
    print('Active Lib/ASC and all old Compiler stubs EXACTLY preserved')


if __name__=='__main__':main()
