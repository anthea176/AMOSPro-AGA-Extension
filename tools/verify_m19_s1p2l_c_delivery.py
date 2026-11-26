#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Authenticate the exact P2l-c image and recover its P2l-b predecessor.
Inverse of the audited source delta ONLY for provenance, not source synthesis.
No library writes.
"""
from hashlib import sha256, sha1
from compiler_relocation import unpack_ap20, repack_ap20
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, token_role_issues
from verify_m19_s1p2l_b_delivery import P2LB_SHA, P2LB_BLOB, recover_p2k
from active_library import P2DL2B_SHA

P2LC_SHA='148b4d06702f84dd6de3eacd069a55c4759164bb4dd3c74f319f81e6f077f3f5'
P2LC_BLOB='86d9497e3a2d5446001b9b41fc25d2e6a878ae50'
P2LC_ASC_SHA='25a50fd84962dcdd0a52a45d496ad3413676d37aa4b3df4c2d74391d18c4a89e'
PARENT_UNIT=11064
PATCH=10978
OLD=bytes.fromhex('203cffffff474e75')
NEW=bytes.fromhex('600000544e714e71')

def recover_p2lb(candidate,good):
    assert len(candidate)==150056 and sha256(candidate).hexdigest()==P2LC_SHA
    assert sha1(b'blob 150056'+bytes(1)+candidate).hexdigest()==P2LC_BLOB
    assert sha256(good).hexdigest()==P2DL2B_SHA
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==214 and len(parts[142])==65276
    assert len(parts[207])==11178 and parts[207][PATCH:PATCH+8]==NEW
    assert b'S1-P2l-c' in title and b'S1-P2l-b' not in title
    assert max(map(abs,pc16_displacements(parts).values()))==11208
    prior=list(parts)
    prior[207]=parts[207][:PATCH]+OLD+parts[207][PATCH+8:PARENT_UNIT]
    parent=repack_ap20(candidate,tok,prior,title.replace(b'S1-P2l-c',b'S1-P2l-b'))
    assert len(parent)==149940 and sha256(parent).hexdigest()==P2LB_SHA
    assert sha1(b'blob 149940'+bytes(1)+parent).hexdigest()==P2LB_BLOB
    recover_p2k(parent,good)
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    return parent

def verify_asc(asc):
    assert len(asc)==6425 and sha256(asc).hexdigest()==P2LC_ASC_SHA
    assert asc.count(b'Aga Sprite Bank Free(-19000)')==4
    assert asc.count(b'Aga Sprite Bank Free(29)')==1
    assert b'SOURCE_TAG M19_S1P2LC_IDLE_DETAIL_V1' in asc
    assert b'DMA_FREE_PROVEN 0' in asc
    return True

def verify_prepared(candidate,good,asc,parent):
    assert recover_p2lb(candidate,good)==parent
    return verify_asc(asc)
