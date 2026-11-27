#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Read-only authentication of exact qualified S2b and historical S2a."""
from hashlib import sha256
from pathlib import Path
from subprocess import check_output
from struct import pack,unpack_from
from active_library import S2B_SHA,S2A_SHA,P2DL2B_SHA,frozen_s1p1i
from verify_m19_s1p2m_delivery import blob,ABK_SHA
from audit_ap20 import inspect,parse,token,token_role_issues,walk_tokens
from compiler_relocation import GETP,RBSR,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v2_island_dispatch import pc16_displacements
from m19_s1_agsp_bank import parse_abk

ROOT=Path(__file__).resolve().parents[1]
S2A_REF='4719388fbc67e80a12973e686937d0cda1c12553'
S2B_BLOB='6a9493b69c5fa64a0cb167722423cfee7f18bbb3'
S2B_ASC_SHA='2cda351432ba495589c4848ef8c2d640426e18c6e71287d643a506e2e21acde0'
S2B_ASC_BLOB='2d1737f64cff84a24ff7551386abd672dc59b738'
S2B_ABK_SHA='eb0060bce79d15785d5d6f6caf31f8819adfd518b0e179dca5feb025b80b2c78'
S2B_ABK_BLOB='c122c79976bce5afad051f487d77af8cc296f2cc'
PALETTES=('000000ff462824dc751a73ff','000000f8d85a34c5e06849bb','000000ff81c96bc34ffefefe')

def verify_library(candidate,good):
    assert len(candidate)==152876 and sha256(candidate).hexdigest()==S2B_SHA
    assert blob(candidate)==S2B_BLOB and sha256(good).hexdigest()==P2DL2B_SHA
    p1i=frozen_s1p1i(candidate,good)
    ot,old,otitle=unpack_ap20(p1i)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==214 and len(parts[142])==65524 and len(parts[207])==13756
    assert [i for i,(x,y) in enumerate(zip(old,parts)) if x!=y]==[142,207]
    assert parts[207].startswith(old[207]) and len(old[207])==len(DISPATCH_V2)+6126
    assert title==otitle.replace(b'S1-P1i',b'S2b-P1')
    assert parts[142][-16:]==bytes.fromhex('00000000414753490001001000000000')
    apis=(('aga sprite','00,0,0,0'),('aga sprite off','00'),('aga sprite bank free','00'))
    assert tok==ot[:-6]+b''.join(token(n,1,209+2*j,sig) for j,(n,sig) in enumerate(apis))+ot[-6:]
    for j in range(3):
        assert parts[208+2*j]==GETP
        assert parts[209+2*j]==RBSR+pack('>HH',207,6126+4*j)+bytes.fromhex('4e75')
    native=parts[142]
    restored=bytearray(native[:len(old[142])])
    targets=[]
    for offset,original in ((0x9d4,bytes.fromhex('6100000e6000ff46')),
                            (0x9dc,bytes.fromhex('610000066000f808')),
                            (0x128,bytes.fromhex('4eaeffbe4292')),
                            (0x886,bytes.fromhex('61004a424292'))):
        assert old[142][offset:offset+len(original)]==original
        assert native[offset:offset+2]==bytes.fromhex('60ff')
        if len(original)==8:assert native[offset+6:offset+8]==bytes.fromhex('4e71')
        targets.append(offset+2+unpack_from('>i',native,offset+2)[0])
        restored[offset:offset+len(original)]=original
    assert targets==[63334,63390,64306,64330] and restored==old[142]
    assert max(map(abs,pc16_displacements(parts).values()))==13786
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([x for x in walk_tokens(tok) if x['signature']])==105
    return True

def verify_asc(asc):
    assert len(asc)==8954 and sha256(asc).hexdigest()==S2B_ASC_SHA and blob(asc)==S2B_ASC_BLOB
    assert b'SOURCE_TAG M19_S2B_MULTI_SPRITE_V1' in asc
    assert b'PASS_S2B_MULTI_SPRITE' in asc and b'AGSP_S2B_MULTI.ABK' in asc
    return True

def verify_abk(data):
    assert len(data)==1012 and sha256(data).hexdigest()==S2B_ABK_SHA and blob(data)==S2B_ABK_BLOB
    bank,flags,payload=parse_abk(data)
    assert bank==29 and flags==1 and len(payload.images)==6
    for k,hexpal in enumerate(PALETTES):
        a,b=payload.image(3+2*k),payload.image(4+2*k)
        assert (a.width,a.height,a.depth,a.palette)==(b.width,b.height,b.depth,b.palette)
        assert (a.width,a.height,a.depth)==(16,16,2)
        assert a.palette==bytes.fromhex(hexpal)+bytes(36) and a.planes!=b.planes
    return True

def historical(path):
    return check_output(['git','show',S2A_REF+':'+path],cwd=ROOT)

def pre_s2b_library(candidate,good):
    if sha256(candidate).hexdigest()!=S2B_SHA:return candidate
    verify_library(candidate,good)
    from verify_m19_s2a_delivery import verify_library as verify_s2a
    parent=historical('dist/AMOSPro_AGA.Lib')
    verify_s2a(parent,good)
    t,parts,title=unpack_ap20(candidate)
    pt,prior,ptitle=unpack_ap20(parent)
    assert t==pt and title==ptitle.replace(b'S2a-P1',b'S2b-P1')
    assert [i for i,(x,y) in enumerate(zip(prior,parts)) if x!=y]==[142,207]
    return parent

def pre_s2b_pair(original):
    candidate,good,asc,abk=original
    if sha256(candidate).hexdigest()!=S2B_SHA:return original
    verify_asc(asc)
    verify_abk((ROOT/'tests/current/AGSP_S2B_MULTI.ABK').read_bytes())
    from verify_m19_s2a_delivery import verify_asc as verify_s2a_asc,verify_abk as verify_s2a_abk
    verify_s2a_abk((ROOT/'tests/current/AGSP_S2A_ANIMATION.ABK').read_bytes())
    assert sha256(abk).hexdigest()==ABK_SHA
    oldasc=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_s2a_asc(oldasc)
    return pre_s2b_library(candidate,good),good,oldasc,abk
