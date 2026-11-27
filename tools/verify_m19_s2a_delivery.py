#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Authenticate the exact S2a Gate A and campaign bytes. Read only."""
from hashlib import sha256
from pathlib import Path
from subprocess import check_output
from struct import pack
from active_library import S2A_SHA, P2DL2B_SHA, frozen_s1p1i
from verify_m19_s1p2m_delivery import blob, verify_library as verify_p2m, verify_asc as verify_p2m_asc, ABK_SHA
from audit_ap20 import inspect, parse, token, token_role_issues, walk_tokens
from compiler_relocation import GETP, RBSR, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v2_island_dispatch import pc16_displacements
from m19_s1_agsp_bank import parse_abk

ROOT=Path(__file__).resolve().parents[1]
P2M_REF='57a1a9d2085e5d887a1fccc5300a0de5eaeef709'
S2A_BLOB='190504fd46494224c6c32e20f17dcc3d6a027684'
S2A_ASC_SHA='d191282714b43d38b07585fa1054895885f8b2d1be403abcfd9f5f76d993ebdb'
S2A_ASC_BLOB='ac74e8773a86914a00f3a153487afe61a9803efc'
S2A_ABK_SHA='4b13eb9ac278ad56a73c043327a11d48a3d79d65807563409d94e64aa16d50aa'
S2A_ABK_BLOB='210179c9328e1ff032070b2dd40ffa8849e8294a'

def verify_library(candidate,good):
    assert len(candidate)==151164 and sha256(candidate).hexdigest()==S2A_SHA
    assert blob(candidate)==S2A_BLOB and sha256(good).hexdigest()==P2DL2B_SHA
    p1i=frozen_s1p1i(candidate,good)
    ot,old,otitle=unpack_ap20(p1i)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==214 and len(parts[142])==65424 and len(parts[207])==12142
    assert [i for i,(x,y) in enumerate(zip(old,parts)) if x!=y]==[142,207]
    assert parts[207].startswith(old[207]) and len(old[207])==len(DISPATCH_V2)+6126
    assert parts[142][-16:]==bytes.fromhex('00000000414753490001001000000000')
    assert title==otitle.replace(b'S1-P1i',b'S2a-P1')
    apis=(('aga sprite','00,0,0,0'),('aga sprite off','00'),('aga sprite bank free','00'))
    assert tok==ot[:-6]+b''.join(token(n,1,209+2*j,sig) for j,(n,sig) in enumerate(apis))+ot[-6:]
    for j in range(3):
        assert parts[208+2*j]==GETP
        assert parts[209+2*j]==RBSR+pack('>HH',207,6126+4*j)+bytes.fromhex('4e75')
    assert max(map(abs,pc16_displacements(parts).values()))==12172
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([x for x in walk_tokens(tok) if x['signature']])==105
    return True

def verify_asc(asc):
    assert len(asc)==7265 and sha256(asc).hexdigest()==S2A_ASC_SHA
    assert blob(asc)==S2A_ASC_BLOB
    assert b'SOURCE_TAG M19_S2A_FRAME_CHANGE_V1' in asc
    assert b'PASS_S2A_FRAME_CHANGE' in asc
    assert b'AGSP_S2A_ANIMATION.ABK' in asc
    return True

def verify_abk(data):
    assert len(data)==372 and sha256(data).hexdigest()==S2A_ABK_SHA
    assert blob(data)==S2A_ABK_BLOB
    bank,flags,payload=parse_abk(data)
    a,b=payload.image(3),payload.image(4)
    assert bank==29 and flags==1 and len(payload.images)==2
    assert (a.width,a.height,a.depth)==(b.width,b.height,b.depth)==(16,16,2)
    assert a.palette==b.palette and a.planes!=b.planes
    return True

def historical(path):
    return check_output(['git','show',P2M_REF+':'+path],cwd=ROOT)

def pre_s2a_library(candidate,good):
    if sha256(candidate).hexdigest()!=S2A_SHA:
        return candidate
    verify_library(candidate,good)
    parent=historical('dist/AMOSPro_AGA.Lib')
    verify_p2m(parent,good)
    t,parts,title=unpack_ap20(candidate)
    pt,prior,ptitle=unpack_ap20(parent)
    assert t==pt and title==ptitle.replace(b'S1-P2m',b'S2a-P1')
    assert [i for i,(x,y) in enumerate(zip(prior,parts)) if x!=y]==[207]
    return parent

def pre_s2a_pair(original):
    candidate,good,asc,abk=original
    if sha256(candidate).hexdigest()!=S2A_SHA:
        return original
    verify_asc(asc)
    verify_abk((ROOT/'tests/current/AGSP_S2A_ANIMATION.ABK').read_bytes())
    assert sha256(abk).hexdigest()==ABK_SHA
    parent=pre_s2a_library(candidate,good)
    oldasc=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_p2m_asc(oldasc)
    return parent,good,oldasc,abk
