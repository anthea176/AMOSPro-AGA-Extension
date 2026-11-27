#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Verify the exact S2c-P1c Gate A candidate and recover the pinned S2r parent.
Read-only: no installation or reconstruction from disassembled bytes.
"""
from hashlib import sha256, sha1
from pathlib import Path
from struct import pack, unpack_from
from subprocess import check_output
from active_library import S2C_SHA, S2R_SHA, P2DL2B_SHA
from compiler_relocation import GETP, RBSR, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, walk_tokens, token_role_issues

ROOT=Path(__file__).resolve().parents[1]
S2R_REF='31735f84f0da50ea4ba324f9bc63bec9313cd47a'
S2C_BLOB='7e8b5320c4098db053afb2bf8ce9f16bf611ff39'
S2C_ASC_SHA='48b9d1e47d63dd401482cfb0ecc8db0646aba68f173154c26ef2b5051f0496ec'
S2C_ASC_BLOB='6b9b4ec84b390c9041126a5231d029d126468ec3'
S2C_ABK_SHA='6f9a65305ca2a3ff7a65d8fc3af02afd75bc45810c94392733141bea434bc246'
S2C_ABK_BLOB='649788aaf7343b67797d4d0c3fae46b850c4a3c4'

def identity(data, size, digest, git_blob):
    assert len(data)==size and sha256(data).hexdigest()==digest
    assert sha1(f'blob {len(data)}'.encode()+bytes(1)+data).hexdigest()==git_blob
    return True

def historical(path):
    return check_output(['git','show',S2R_REF+':'+path],cwd=ROOT)

def verify_library(candidate,good):
    identity(candidate,159844,S2C_SHA,S2C_BLOB)
    assert len(good)==136708 and sha256(good).hexdigest()==P2DL2B_SHA
    from verify_m19_s2r_delivery import verify_library as verify_s2r, START, END
    parent=historical('dist/AMOSPro_AGA.Lib')
    verify_s2r(parent,good)
    ot,old,oz=unpack_ap20(parent)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==len(old)==219
    assert title==oz.replace(b'S2r-P1',b'S2c-P2')
    assert len(parts[142])==63350 and len(parts[213])==19246
    assert parts[213].startswith(DISPATCH_V2)
    assert all(len(p)<=MAX_UNIT_BYTES for p in parts)
    assert [i for i,(a,b) in enumerate(zip(old,parts)) if a!=b]==[142,204,206,207,208,209,210,211,212,213]
    restored=bytearray(parts[142])
    restored[START:END]=old[142][START:END]
    targets=[]
    for offset,n in ((0x9d4,8),(0x9dc,8),(0x128,6),(0x886,6)):
        assert parts[142][offset:offset+2]==bytes.fromhex('60ff')
        targets.append(offset+2+unpack_from('>i',parts[142],offset+2)[0])
        if n==8:assert parts[142][offset+6:offset+8]==bytes.fromhex('4e71')
        restored[offset:offset+n]=old[142][offset:offset+n]
    assert targets==[52974,53030,54250,54274] and bytes(restored)==old[142]
    expected=bytearray(ot)
    mapping={'aga sprite':(209,208),'aga sprite off':(211,210),'aga sprite bank free':(213,212)}
    for row in walk_tokens(ot):
        if row['name'] in mapping:
            before,after=mapping[row['name']]
            assert row['function']==before and row['instruction']==1
            assert old[before-1]==parts[after-1]==GETP
            expected[row['offset']+2:row['offset']+4]=pack('>H',after)
    assert tok==bytes(expected)
    for index,offset in ((204,0),(206,8),(208,0x1818),(210,0x181c),(212,0x1820)):
        assert parts[index]==RBSR+pack('>HH',213,offset)+bytes.fromhex('4e75')
        assert parts[index-1]==GETP
    assert MAX_UNIT_BYTES-len(parts[213])==46288
    pc16_displacements(parts)
    trial=list(parts)
    trial[213]+=bytes(16384)
    assert len(trial[213])<=MAX_UNIT_BYTES
    pc16_displacements(trial)
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([r for r in walk_tokens(tok) if r['signature']])==105
    return True

def verify_asc(asc):
    identity(asc,15459,S2C_ASC_SHA,S2C_ASC_BLOB)
    assert b'SOURCE_TAG M19_S2C_MIXED_V1' in asc
    assert b'PASS_S2C_MIXED' in asc and b'AGSP_S2C_MIXED.ABK' in asc
    return True

def verify_abk(abk):
    identity(abk,1460,S2C_ABK_SHA,S2C_ABK_BLOB)
    from m19_s1_agsp_bank import parse_abk
    bank,flags,payload=parse_abk(abk)
    assert bank==29 and flags==1 and len(payload.images)==8
    for k in range(4):
        a,b=payload.image(3+2*k),payload.image(4+2*k)
        assert (a.width,a.height,a.depth,a.palette)==(b.width,b.height,b.depth,b.palette)
        assert (a.width,a.height,a.depth)==(16,16,2 if k<3 else 4)
        assert a.planes!=b.planes
    return True

def pre_s2c_library(candidate,good):
    if sha256(candidate).hexdigest()!=S2C_SHA:return candidate
    verify_library(candidate,good)
    return historical('dist/AMOSPro_AGA.Lib')

def pre_s2c_pair(original):
    candidate,good,asc,abk=original
    if sha256(candidate).hexdigest()!=S2C_SHA:return original
    verify_asc(asc)
    verify_abk((ROOT/'tests/current/AGSP_S2C_MIXED.ABK').read_bytes())
    parent=pre_s2c_library(candidate,good)
    from verify_m19_s2r_delivery import verify_asc as verify_s2r_asc
    oldasc=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_s2r_asc(oldasc)
    return parent,good,oldasc,abk

if __name__=='__main__':
    from verify_m19_s1p2l_b_delivery import check_active_pair
    from active_library import verify_active
    verify_active(ROOT)
    check_active_pair()
    print('S2c exact active pair verification PASS')
