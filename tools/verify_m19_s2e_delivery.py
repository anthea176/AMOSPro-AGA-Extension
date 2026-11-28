#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exact S2e delivery and historical S2d recovery, read-only."""
from pathlib import Path
from hashlib import sha256
from subprocess import check_output
from active_library import S2E_SHA,S2D_SHA,P2DL2B_SHA
from verify_m19_s2d_delivery import (identity,verify_library as verify_s2d,
    verify_asc as verify_s2d_asc,verify_abk as verify_s2d_abk)
from compiler_relocation import unpack_ap20
from compiler_bridge_v2_probe import MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect,parse,walk_tokens,token_role_issues

ROOT=Path(__file__).resolve().parents[1]
PARENT_REF='fc16c5a49546aeffddb0d342842743d15e58cd38'
S2E_BLOB='6206d425dc787d9a1460bf0e7f85d2e7579c9037'
S2E_ASC_SHA='b11f05a88a311cce82da5eb10962133e0c703fcd18fef20fcb592ddfa294be84'
S2E_ASC_BLOB='38b69e5fdab38e8abde89b0d9ec9fa43dd1aba8e'
S2E_ABK_SHA='df3b9af963c65ada0d294708761f9990e240aa771e58b53bf8840d8c98d15d8a'
S2E_ABK_BLOB='fcc7f978aa73ae755d8028905f8e4a84c001214e'

def historical(path):
    return check_output(['git','show',PARENT_REF+':'+path],cwd=ROOT)

def verify_library(candidate,good):
    identity(candidate,160352,S2E_SHA,S2E_BLOB)
    assert len(good)==136708 and sha256(good).hexdigest()==P2DL2B_SHA
    parent=historical('dist/AMOSPro_AGA.Lib')
    verify_s2d(parent,good)
    ot,old,oz=unpack_ap20(parent)
    tok,parts,title=unpack_ap20(candidate)
    assert tok==ot and len(parts)==len(old)==219
    assert title==oz.replace(b'0.15.0-alpha.1',b'0.15.0-alpha.2')
    assert [i for i,(a,b) in enumerate(zip(old,parts)) if a!=b]==[142,213]
    assert len(parts[142])==65062 and parts[142][63334:63350]==old[142][63334:63350]
    assert len(parts[213])==18028
    assert all(len(x)<=MAX_UNIT_BYTES for x in parts)
    assert MAX_UNIT_BYTES-len(parts[142])==472
    assert MAX_UNIT_BYTES-len(parts[213])==47506
    assert max(map(abs,pc16_displacements(parts).values()))==3658
    trial=list(parts);trial[213]+=bytes(16384)
    assert len(trial[213])<=MAX_UNIT_BYTES
    assert max(map(abs,pc16_displacements(trial).values()))==3658
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([r for r in walk_tokens(tok) if r['signature']])==105
    return True

def verify_asc(asc):
    identity(asc,17604,S2E_ASC_SHA,S2E_ASC_BLOB)
    assert b'SOURCE_TAG M19_S2E_HOTSPOT_V1' in asc
    assert b'PASS_S2E_HOTSPOT' in asc and b'AGSP_HOTSPOT_TEST.ABK' in asc
    return True

def verify_abk(abk):
    identity(abk,6836,S2E_ABK_SHA,S2E_ABK_BLOB)
    from dataclasses import replace
    from m19_s1_agsp_bank import parse_abk
    prior=(ROOT/'tests/current/AGSP_WIDE_TEST.ABK').read_bytes()
    verify_s2d_abk(prior)
    _,_,old=parse_abk(prior)
    bank,flags,payload=parse_abk(abk)
    assert (bank,flags,len(payload.images))==(29,1,24)
    assert payload.generation==old.generation+24
    assert payload.images==tuple(replace(im,hotspot_x=im.width//2 if im.image_id%2 else -3,
        hotspot_y=8 if im.image_id%2 else -4) for im in old.images)
    return True

def pre_s2e_library(candidate,good):
    from verify_m19_s2f_delivery import pre_s2f_library
    candidate=pre_s2f_library(candidate,good)
    if sha256(candidate).hexdigest()!=S2E_SHA:return candidate
    verify_library(candidate,good)
    return historical('dist/AMOSPro_AGA.Lib')

def pre_s2e_pair(original):
    from verify_m19_s2f_delivery import pre_s2f_pair
    original=pre_s2f_pair(original)
    candidate,good,asc,abk=original
    if sha256(candidate).hexdigest()!=S2E_SHA:return original
    parent=pre_s2e_library(candidate,good)
    verify_asc(asc)
    verify_abk((ROOT/'tests/current/AGSP_HOTSPOT_TEST.ABK').read_bytes())
    oldasc=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_s2d_asc(oldasc)
    return parent,good,oldasc,abk

if __name__=='__main__':
    from active_library import verify_active
    from verify_m19_s1p2l_b_delivery import check_active_pair
    from verify_m19_s2f_delivery import pre_s2f_library
    candidate,good,label=verify_active(ROOT)
    verify_library(pre_s2f_library(candidate,good),good)
    check_active_pair()
    print('S2E EXACT LINEAGE AND ACTIVE PAIR PASS',S2E_SHA)
