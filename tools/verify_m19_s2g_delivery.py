#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Read-only S2g P1b exact identity and S2f lineage recovery.

This is an identity check, not a Gate A certificate. Activation must also
pin the public SHA/blob and CI results in active_library and delivery docs.
No file writes. The historical parent is the exact author-tested S2f.
"""
from pathlib import Path
from hashlib import sha256,sha1
from subprocess import check_output
from struct import pack
from audit_ap20 import inspect,parse,walk_tokens,token_role_issues
from compiler_relocation import unpack_ap20,repack_ap20,GETP,RBSR
from compiler_bridge_v2_probe import MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from verify_m19_s2f_delivery import (verify_library as verify_s2f,
    verify_asc as verify_s2f_asc,S2F_SHA)
from verify_m19_s2e_delivery import verify_abk

ROOT=Path(__file__).resolve().parents[1]
S2F_REF='ef8cd7c175d97f73fc058dd6d16b43da1acd0103'
P1A_SHA='e45e5cc3ba951f2216d50c3a752a6bc9d0a6d4fec9e13ee5cec59b3df1a37de0'
P1A_BLOB='5420d586f6178275566843d4a547e7fc36b43d22'
S2G_SHA='7c68fb4ba1f903fe11a0c079b37d4f8d54a5a8dcc8bce96b6de4c791b5be9e1d'
S2G_BLOB='e657167548082be034834130fdb188c42f37f595'
S2G_ASC_SHA='2a79bf1a996eafd25b3a3b027c2eb1aac7830a339681b8597fdfa687ce8be5aa'
S2G_ASC_BLOB='47db0fa032e487e525d40bfd3f584a8e879bb7b4'
VERSION=b'0.15.0-alpha.4'
PRIVATE_VERSION=VERSION+b'.p1a'

def historical(path):
    return check_output(['git','show',S2F_REF+':'+path],cwd=ROOT)

def blob(data):
    return sha1(f'blob {len(data)}'.encode()+b'\0'+data).hexdigest()

def verify_library(candidate,good):
    assert len(candidate)==162432 and sha256(candidate).hexdigest()==S2G_SHA and blob(candidate)==S2G_BLOB
    from build_m19_s2g_in_memory import shifted,PRIVATE_ENTRY,NEW_GROUP
    from build_m19_s2g_public_in_memory import overload
    parent=historical('dist/AMOSPro_AGA.Lib')
    verify_s2f(parent,good)
    assert sha256(parent).hexdigest()==S2F_SHA
    ot,old,oz=unpack_ap20(parent)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==221 and len(old)==219
    assert title==oz.replace(b'0.15.0-alpha.3',VERSION)
    pt=bytearray(ot)
    for row in walk_tokens(ot):
        for i,role in enumerate(('instruction','function')):
            pos=row['offset']+i*2
            pt[pos:pos+2]=pack('>H',shifted(row[role]))
    pt=bytes(pt)
    assert tok==overload(pt,PRIVATE_ENTRY)
    private_title=title.replace(VERSION,PRIVATE_VERSION)
    private=repack_ap20(parent,pt,parts,private_title)
    assert len(private)==162424
    assert sha256(private).hexdigest()==P1A_SHA and blob(private)==P1A_BLOB
    assert repack_ap20(parent,tok,parts,title)==candidate
    assert parts[142]==old[142] and len(parts[142])==65062
    assert parts[PRIVATE_ENTRY-1]==GETP
    assert parts[PRIVATE_ENTRY]==RBSR+pack('>HH',NEW_GROUP,6380)+b'\x4e\x75'
    assert len(parts[NEW_GROUP])==20074
    assert all(len(p)<=MAX_UNIT_BYTES for p in parts)
    assert max(map(abs,pc16_displacements(parts).values()))==3658
    trial=list(parts);trial[NEW_GROUP]+=bytes(16384)
    assert len(trial[NEW_GROUP])<=MAX_UNIT_BYTES
    assert max(map(abs,pc16_displacements(trial).values()))==3658
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    rows=[r for r in audit['tokens'] if r['signature']]
    assert len(rows)==106 and len({r['name'] for r in rows})==105
    return True

def verify_asc(asc,bank=None):
    assert len(asc)==25332 and sha256(asc).hexdigest()==S2G_ASC_SHA and blob(asc)==S2G_ASC_BLOB
    from prepare_m19_s2g_campaign import prepare
    if bank is None:
        bank=(ROOT/'tests/current/AGSP_HOTSPOT_TEST.ABK').read_bytes()
    verify_abk(bank)
    parent=historical('tests/current/SPRITE_PUBLIC.asc')
    verify_s2f_asc(parent)
    assert asc==prepare(parent,bank)
    assert b'SOURCE_TAG M19_S2G_PRIORITY_V1' in asc
    assert b'PASS_S2G_PRIORITY' in asc
    return True

def is_s2g(candidate):
    # Match title, then verify exact identity before treating it as S2g.
    _,_,title=unpack_ap20(candidate)
    return b'$VER: AGSP 0.15.0-alpha.4 L2b non-distributed' in title

def pre_s2g_library(candidate,good):
    if sha256(candidate).hexdigest()!=S2G_SHA:return candidate
    verify_library(candidate,good)
    return historical('dist/AMOSPro_AGA.Lib')

def pre_s2g_pair(original):
    candidate,good,asc,legacy_bank=original
    if sha256(candidate).hexdigest()!=S2G_SHA:return original
    parent=pre_s2g_library(candidate,good)
    verify_asc(asc)
    # Preserve original tuple's historical AGSP_S1P1E_FINAL.ABK.
    return parent,good,historical('tests/current/SPRITE_PUBLIC.asc'),legacy_bank

if __name__=='__main__':
    current=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    asc=(ROOT/'tests/current/SPRITE_PUBLIC.asc').read_bytes()
    verify_library(current,good)
    verify_asc(asc)
    print('S2G EXACT ACTIVE PAIR IDENTITY PASS',len(current),sha256(current).hexdigest(),blob(current),
          len(asc),sha256(asc).hexdigest(),blob(asc))
