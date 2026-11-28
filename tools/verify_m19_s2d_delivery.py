#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Authenticate exact 0.15.0-alpha.1 S2d-P3e and its pinned S2c parent.
Historical recovery reads Git objects, never synthesizes production source.
No file writes. All archived tests and LAST_GOOD remain unchanged.
"""
from pathlib import Path
from hashlib import sha256
from struct import pack,unpack_from
from subprocess import check_output
from active_library import S2D_SHA,S2CE_SHA,P2DL2B_SHA
from verify_m19_s2c_delivery import identity,verify_viewport_chain,verify_asc as verify_old_asc,verify_abk as verify_old_abk
from compiler_relocation import unpack_ap20,GETP,RBSR
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect,parse,walk_tokens,token_role_issues

ROOT=Path(__file__).resolve().parents[1]
PARENT_REF='caf0b6ba768328f78d3a148f54dfecc760ea1d8c'
S2D_BLOB='5f3c72b68c3b6b424d173a989eecf757f13f1c01'
S2D_ASC_SHA='520c1a8a4c964b288fc76a337b5a6389e33d28340a98a8b21b342abaddaa1a29'
S2D_ASC_BLOB='994f74916ec774b43b69688dce5401d26dd647d1'
S2D_ABK_SHA='f8816b944102c5826f9819b84747acd61fd4468423bf815c25e128a9dcfe4e64'
S2D_ABK_BLOB='0f3decda5863337c5a1f95fe1844a95df4d34823'

def historical(path):
    return check_output(['git','show',PARENT_REF+':'+path],cwd=ROOT)

def verify_library(candidate,good):
    identity(candidate,160148,S2D_SHA,S2D_BLOB)
    assert len(good)==136708 and sha256(good).hexdigest()==P2DL2B_SHA
    parent=historical('dist/AMOSPro_AGA.Lib')
    verify_viewport_chain(parent,good)
    ot,old,oz=unpack_ap20(parent)
    tok,parts,title=unpack_ap20(candidate)
    assert tok==ot and len(parts)==len(old)==219
    assert title==oz.replace(b'S2c-E1',b'0.15.0-alpha.1')
    assert [i for i,(a,b) in enumerate(zip(old,parts)) if a!=b]==[142,208,210,212,213]
    assert len(old[142])==63350 and len(parts[142])==65062
    assert parts[142][63334:63350]==old[142][63334:63350]
    restored=bytearray(parts[142][:63350])
    restored[0xCEEE:0xDD04]=old[142][0xCEEE:0xDD04]
    targets=[]
    for off,n in ((0x9d4,8),(0x9dc,8),(0x128,6),(0x886,6)):
        assert parts[142][off:off+2]==b'\x60\xff'
        targets.append(off+2+unpack_from('>i',parts[142],off+2)[0])
        if n==8:assert parts[142][off+6:off+8]==b'\x4e\x71'
        restored[off:off+n]=old[142][off:off+n]
    assert bytes(restored)==old[142] and targets==[52974,53030,53262,53286]
    assert len(parts[213])==17822 and parts[213].startswith(DISPATCH_V2)
    for idx,off in ((204,0),(206,8),(208,6368),(210,6372),(212,6376)):
        assert parts[idx-1]==GETP
        assert parts[idx]==RBSR+pack('>HH',213,off)+b'\x4e\x75'
    assert all(len(x)<=MAX_UNIT_BYTES for x in parts)
    assert MAX_UNIT_BYTES-len(parts[142])==472
    assert MAX_UNIT_BYTES-len(parts[213])==47712
    assert max(map(abs,pc16_displacements(parts).values()))==3658
    trial=list(parts);trial[213]+=bytes(16384)
    assert len(trial[213])<=MAX_UNIT_BYTES
    assert max(map(abs,pc16_displacements(trial).values()))==3658
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([r for r in walk_tokens(tok) if r['signature']])==105
    return True

def verify_asc(asc):
    identity(asc,16576,S2D_ASC_SHA,S2D_ASC_BLOB)
    assert b'SOURCE_TAG M19_S2D_WIDE_V1' in asc
    assert b'PASS_S2D_WIDE' in asc and b'AGSP_WIDE_TEST.ABK' in asc
    return True

def verify_abk(abk):
    identity(abk,6836,S2D_ABK_SHA,S2D_ABK_BLOB)
    from m19_s1_agsp_bank import parse_abk
    bank,flags,payload=parse_abk(abk)
    assert (bank,flags,len(payload.images))==(29,1,24)
    for group,w in enumerate((16,32,64)):
        for k in range(4):
            n=1+group*8+2*k
            a,b=payload.image(n),payload.image(n+1)
            assert (a.width,a.height,a.depth,a.palette)==(b.width,b.height,b.depth,b.palette)
            assert (a.width,a.height,a.depth)==(w,16,2 if k<3 else 4)
            assert a.planes!=b.planes
    return True

def pre_s2d_library(candidate,good):
    from verify_m19_s2e_delivery import pre_s2e_library
    candidate=pre_s2e_library(candidate,good)
    if sha256(candidate).hexdigest()!=S2D_SHA:return candidate
    verify_library(candidate,good)
    return historical('dist/AMOSPro_AGA.Lib')

def pre_s2d_pair(original):
    from verify_m19_s2e_delivery import pre_s2e_pair
    original=pre_s2e_pair(original)
    candidate,good,asc,abk=original
    if sha256(candidate).hexdigest()!=S2D_SHA:return original
    parent=pre_s2d_library(candidate,good)
    verify_asc(asc)
    verify_abk((ROOT/'tests/current/AGSP_WIDE_TEST.ABK').read_bytes())
    oldasc=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_old_asc(oldasc)
    verify_old_abk((ROOT/'tests/current/AGSP_S2C_MIXED.ABK').read_bytes())
    return parent,good,oldasc,abk

if __name__=='__main__':
    from active_library import verify_active
    from verify_m19_s1p2l_b_delivery import check_active_pair
    candidate,good,label=verify_active(ROOT)
    verify_library(candidate,good)
    check_active_pair()
    print('S2D EXACT ACTIVE TRIPLE PASS',S2D_SHA)
