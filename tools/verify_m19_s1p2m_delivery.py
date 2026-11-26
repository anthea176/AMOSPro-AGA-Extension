#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Authenticate exact P2m Gate A bytes. Historical parents come only from Git.
No repository writes, no source synthesis from a binary.
"""
from hashlib import sha1, sha256
from pathlib import Path
from struct import pack, unpack_from
from subprocess import check_output
from active_library import S1P2M_SHA, P2DL2B_SHA, frozen_s1p1i
from audit_ap20 import inspect, parse, token, token_role_issues, walk_tokens
from compiler_relocation import GETP, RBSR, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v2_island_dispatch import pc16_displacements

ROOT=Path(__file__).resolve().parents[1]
P2M_SHA=S1P2M_SHA
P2M_BLOB='a29e86a6414021e19b87615681dcc08fe406518c'
P2M_ASC_SHA='84d2dfddc753e2c05d8a05ff991fe8b4f3e6d36daa20110cc447add547aaa684'
P2M_ASC_BLOB='ddd9b676b9a3d4c0f4cccf08ca058cade61df9aa'
ABK_SHA='225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93'
P2LC_REF='04dca65dc3adde7336d211c6d151a0d0dc952442'

def blob(data):
    return sha1(('blob %d' % len(data)).encode()+bytes(1)+data).hexdigest()

def verify_library(candidate,good):
    assert len(candidate)==149400 and sha256(candidate).hexdigest()==P2M_SHA
    assert blob(candidate)==P2M_BLOB and sha256(good).hexdigest()==P2DL2B_SHA
    parent=frozen_s1p1i(candidate,good)
    ot,old,otitle=unpack_ap20(parent)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==214 and len(parts[142])==65424 and len(parts[207])==10380
    assert [i for i,(x,y) in enumerate(zip(old,parts)) if x!=y]==[142,207]
    assert parts[207].startswith(old[207]) and len(old[207])==len(DISPATCH_V2)+6126
    assert title==otitle.replace(b'S1-P1i',b'S1-P2m')
    apis=(('aga sprite','00,0,0,0'),('aga sprite off','00'),('aga sprite bank free','00'))
    assert tok==ot[:-6]+b''.join(token(n,1,209+2*j,sig) for j,(n,sig) in enumerate(apis))+ot[-6:]
    for j in range(3):
        assert parts[208+2*j]==GETP
        assert parts[209+2*j]==RBSR+pack('>HH',207,6126+4*j)+bytes.fromhex('4e75')
    new=parts[142]
    assert new[-16:]==bytes.fromhex('00000000414753490001001000000000')
    restored=bytearray(new[:len(old[142])])
    targets=[]
    for offset,original in ((0x9d4,bytes.fromhex('6100000e6000ff46')),
                            (0x9dc,bytes.fromhex('610000066000f808')),
                            (0x128,bytes.fromhex('4eaeffbe4292')),
                            (0x886,bytes.fromhex('61004a424292'))):
        assert old[142][offset:offset+len(original)]==original
        assert new[offset:offset+2]==bytes.fromhex('60ff')
        if len(original)==8:
            assert new[offset+6:offset+8]==bytes.fromhex('4e71')
        targets.append(offset+2+unpack_from('>i',new,offset+2)[0])
        restored[offset:offset+len(original)]=original
    assert targets==[63334,63392,64412,64436] and restored==old[142]
    prior_links=pc16_displacements(old)
    links=pc16_displacements(parts)
    assert set(links)==set(prior_links)|{209,211,213}
    assert all(links[k]==v for k,v in prior_links.items())
    assert max(map(abs,links.values()))==10410
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([x for x in walk_tokens(tok) if x['signature']])==105
    return True

def verify_asc(asc):
    assert len(asc)==6700 and sha256(asc).hexdigest()==P2M_ASC_SHA
    assert blob(asc)==P2M_ASC_BLOB
    assert b'SOURCE_TAG M19_S1P2M_FUNCTIONAL_V1' in asc
    assert b'PASS_FUNCTIONAL_LIFECYCLE' in asc
    assert b'Aga Sprite Bank Free(-19000)' not in asc
    return True

def historical(path):
    # Full-history clone required for predecessor builds, not active use.
    return check_output(['git','show',P2LC_REF+':'+path],cwd=ROOT)

def pre_p2m_library(candidate,good):
    if sha256(candidate).hexdigest()!=P2M_SHA:
        return candidate
    verify_library(candidate,good)
    from verify_m19_s1p2l_c_delivery import recover_p2lb
    parent=historical('dist/AMOSPro_AGA.Lib')
    recover_p2lb(parent,good)
    return parent

def pre_p2m_pair(original):
    candidate,good,asc,abk=original
    if sha256(candidate).hexdigest()!=P2M_SHA:
        return original
    verify_asc(asc)
    assert sha256(abk).hexdigest()==ABK_SHA
    parent=pre_p2m_library(candidate,good)
    from verify_m19_s1p2l_c_delivery import verify_asc as verify_parent_asc
    oldasc=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_parent_asc(oldasc)
    return parent,good,oldasc,abk
