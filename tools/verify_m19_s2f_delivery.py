#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exact S2f delivery and historical S2e recovery, read-only."""
from pathlib import Path
from hashlib import sha256
from subprocess import check_output
from active_library import S2F_SHA,S2E_SHA,P2DL2B_SHA
from verify_m19_s2d_delivery import identity
from verify_m19_s2e_delivery import (verify_library as verify_s2e,
    verify_asc as verify_s2e_asc,verify_abk)
from compiler_relocation import unpack_ap20
from compiler_bridge_v2_probe import MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect,parse,walk_tokens,token_role_issues

ROOT=Path(__file__).resolve().parents[1]
PARENT_REF='65f0cce933d7bcf471378231a2a29d5e81580388'
S2F_BLOB='d58c985692d88b08df2d55b690b43ed47b087b13'
S2F_ASC_SHA='96c9c526f3e37d5e11d023b7ee8681e6114dc0e22f5aff1c8aaf6ff05590bb48'
S2F_ASC_BLOB='ece785049b2c82ad00e44455f84d7f7cbfb639af'

def historical(path):
    return check_output(['git','show',PARENT_REF+':'+path],cwd=ROOT)

def verify_library(candidate,good):
    identity(candidate,162288,S2F_SHA,S2F_BLOB)
    assert len(good)==136708 and sha256(good).hexdigest()==P2DL2B_SHA
    parent=historical('dist/AMOSPro_AGA.Lib')
    verify_s2e(parent,good)
    ot,old,oz=unpack_ap20(parent)
    tok,parts,title=unpack_ap20(candidate)
    assert tok==ot and len(parts)==len(old)==219
    assert title==oz.replace(b'0.15.0-alpha.2',b'0.15.0-alpha.3')
    assert [i for i,(a,b) in enumerate(zip(old,parts)) if a!=b]==[142,213]
    assert len(parts[142])==65062 and parts[142][63334:63350]==old[142][63334:63350]
    assert len(parts[213])==19964
    assert all(len(x)<=MAX_UNIT_BYTES for x in parts)
    assert MAX_UNIT_BYTES-len(parts[142])==472
    assert MAX_UNIT_BYTES-len(parts[213])==45570
    assert max(map(abs,pc16_displacements(parts).values()))==3658
    trial=list(parts);trial[213]+=bytes(16384)
    assert len(trial[213])<=MAX_UNIT_BYTES
    assert max(map(abs,pc16_displacements(trial).values()))==3658
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([r for r in walk_tokens(tok) if r['signature']])==105
    return True

def verify_asc(asc):
    identity(asc,22943,S2F_ASC_SHA,S2F_ASC_BLOB)
    assert b'SOURCE_TAG M19_S2F_CLIPPING_V1' in asc
    assert b'PASS_S2F_CLIPPING' in asc and b'AGSP_HOTSPOT_TEST.ABK' in asc
    return True

def pre_s2f_library(candidate,good):
    from verify_m19_s2g_delivery import pre_s2g_library
    candidate=pre_s2g_library(candidate,good)
    if sha256(candidate).hexdigest()!=S2F_SHA:return candidate
    verify_library(candidate,good)
    return historical('dist/AMOSPro_AGA.Lib')

def pre_s2f_pair(original):
    from verify_m19_s2g_delivery import pre_s2g_pair
    original=pre_s2g_pair(original)
    candidate,good,asc,abk=original
    if sha256(candidate).hexdigest()!=S2F_SHA:return original
    parent=pre_s2f_library(candidate,good)
    verify_asc(asc)
    verify_abk((ROOT/'tests/current/AGSP_HOTSPOT_TEST.ABK').read_bytes())
    oldasc=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_s2e_asc(oldasc)
    return parent,good,oldasc,abk

if __name__=='__main__':
    from active_library import verify_active
    from verify_m19_s1p2l_b_delivery import check_active_pair
    candidate,good,label=verify_active(ROOT)
    from verify_m19_s2g_delivery import pre_s2g_library
    verify_library(pre_s2g_library(candidate,good),good)
    check_active_pair()
    print('S2F EXACT LINEAGE AND ACTIVE PAIR PASS',S2F_SHA)
