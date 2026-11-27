#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Authenticate exact qualified S2r and recover SHA-pinned S2b predecessor.
Read-only. Keep original S2b sources, fixtures and historical tests intact.
"""
from hashlib import sha256
from pathlib import Path
from subprocess import check_output
from struct import pack,unpack_from
from active_library import S2R_SHA,S2B_SHA,P2DL2B_SHA
from verify_m19_s2b_delivery import verify_library as verify_s2b, verify_asc as verify_s2b_asc, verify_abk
from verify_m19_s1p2m_delivery import blob,ABK_SHA
from compiler_relocation import GETP,RBSR,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect,parse,walk_tokens,token_role_issues

ROOT=Path(__file__).resolve().parents[1]
S2B_REF='502739db328178d7abd47e8bc247a7c54d453139'
S2R_BLOB='61d8211e449ffd9cb41e3fb2b6ec9efdf352c88c'
S2R_ASC_SHA='d06f3c296d45a8766acdf678b03675c99ee702baf776a2f2f50e2da5aa8939e3'
S2R_ASC_BLOB='f1985251d4d37e978c4ec61b5e06f81fb3559ee4'
START,END=0xCEEE,0xDD04

def historical(path):
    return check_output(['git','show',S2B_REF+':'+path],cwd=ROOT)

def verify_library(candidate,good):
    assert len(candidate)==154352 and sha256(candidate).hexdigest()==S2R_SHA
    assert blob(candidate)==S2R_BLOB and sha256(good).hexdigest()==P2DL2B_SHA
    parent=historical('dist/AMOSPro_AGA.Lib')
    verify_s2b(parent,good)
    ot,old,oz=unpack_ap20(parent)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==219 and len(parts[142])==63350 and len(parts[207])==13756
    assert len(parts[214])==3640
    assert title==oz.replace(b'S2b-P1',b'S2r-P1')
    assert [i for i,(a,b) in enumerate(zip(old,parts)) if a!=b]==[138,139,140,141,142,207]
    assert parts[138:142]==[b'']*4
    assert parts[214]==DISPATCH_V2+old[142][START:END]
    assert parts[215]==parts[217]==GETP
    expected=bytearray(ot)
    for row in walk_tokens(ot):
        if row['name'] in ('aga bank image info','aga bank image capture'):
            entry,address,new=(139,0xCEF2,216) if row['name']=='aga bank image info' else (141,0xD336,218)
            assert row['function']==entry and row['instruction']==1
            assert parts[new]==RBSR+pack('>HH',214,address-START)+b'\x4e\x75'
            expected[row['offset']+2:row['offset']+4]=pack('>H',new)
    assert tok==bytes(expected)
    assert parts[142][-16:]==old[142][-16:]
    restored=bytearray(parts[142][:-16])
    restored[START:END]=old[142][START:END]
    targets=[]
    for offset,n in ((0x9d4,8),(0x9dc,8),(0x128,6),(0x886,6)):
        assert parts[142][offset:offset+2]==b'\x60\xff'
        targets.append(offset+2+unpack_from('>i',parts[142],offset+2)[0])
        if n==8:assert parts[142][offset+6:offset+8]==b'\x4e\x71'
        restored[offset:offset+n]=old[142][offset:offset+n]
    assert targets==[52974,53030,53946,53970]
    assert restored==old[142][:63334]
    a=b'\x06\x80'+pack('>I',65508-0x1c2)
    b=b'\x06\x80'+pack('>I',63334-0x1c2)
    assert old[207].count(a)==1 and parts[207]==old[207].replace(a,b)
    links=pc16_displacements(parts)
    assert max(map(abs,links.values()))==13786
    expanded=list(parts);expanded[207]+=bytes(16384)
    pc16_displacements(expanded)
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([r for r in walk_tokens(tok) if r['signature']])==105
    return True

def verify_asc(asc):
    assert len(asc)==11806 and sha256(asc).hexdigest()==S2R_ASC_SHA and blob(asc)==S2R_ASC_BLOB
    assert b'SOURCE_TAG M19_S2R_REPARTITION_V1' in asc
    assert b'PASS_S2R_REPARTITION' in asc and b'AGSP_S2B_MULTI.ABK' in asc
    return True

def pre_s2r_library(candidate,good):
    if sha256(candidate).hexdigest()!=S2R_SHA:return candidate
    verify_library(candidate,good)
    return historical('dist/AMOSPro_AGA.Lib')

def pre_s2r_pair(original):
    candidate,good,asc,abk=original
    if sha256(candidate).hexdigest()!=S2R_SHA:return original
    verify_asc(asc)
    verify_abk((ROOT/'tests/current/AGSP_S2B_MULTI.ABK').read_bytes())
    assert sha256(abk).hexdigest()==ABK_SHA
    parent=pre_s2r_library(candidate,good)
    oldasc=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_s2b_asc(oldasc)
    return parent,good,oldasc,abk

if __name__=='__main__':
    from active_library import verify_active
    from verify_m19_s1p2l_b_delivery import check_active_pair
    verify_active(ROOT)
    check_active_pair()
    print('S2r exact active pair verification PASS')
