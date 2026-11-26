#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Verify the exact P2l-b diagnostic lineage before any canonical activation.
No files are installed. Restore the verified P2k parent in memory only.
"""
from hashlib import sha256, sha1
from struct import pack
from compiler_relocation import GETP, RBSR, unpack_ap20, repack_ap20
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, token_role_issues
from active_library import S1P2K_SHA, P2DL2B_SHA, verify_s1p2k

P2LB_SHA = 'd9b690287c82c52a766d5ab4b015bb29d25057cbe55a630c0e30d88d46bd4ab1'
P2LB_BLOB = '17136bee1d0ac8ae1e5d9431c51fd1bdf24129f2'
P2LB_ASC_SHA = 'a4ab96585d9e95c65dfaf42b76d9ba8b764c4e50e5cbd2d97d56a1947712d239'

def recover_p2k(candidate, good):
    """Strict identity and exact predecessor recovery, not source synthesis."""
    assert len(candidate)==149940 and sha256(candidate).hexdigest()==P2LB_SHA
    assert sha1(b'blob 149940'+bytes(1)+candidate).hexdigest()==P2LB_BLOB
    assert sha256(good).hexdigest()==P2DL2B_SHA
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==214 and len(parts[142])==65276
    assert len(parts[207])==11064 and parts[212]==GETP
    assert parts[213]==RBSR+pack('>HH',207,10986)+bytes.fromhex('4e75')
    # The AP20 title includes multiple version strings. Restore every
    # occurrence, exactly inverse to both source builders. The recovered
    # parent SHA and byte equality remain mandatory.
    assert b'S1-P2l-b' in title and b'S1-P2k' not in title
    assert max(map(abs,pc16_displacements(parts).values()))==11094
    prior=list(parts)
    prior[207]=prior[207][:10208]
    prior[213]=RBSR+pack('>HH',207,6134)+bytes.fromhex('4e75')
    predecessor=repack_ap20(candidate,tok,prior,title.replace(b'S1-P2l-b',b'S1-P2k'))
    assert len(predecessor)==149080 and sha256(predecessor).hexdigest()==S1P2K_SHA
    verify_s1p2k(predecessor,good)
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    return predecessor

def verify_prepared(candidate,good,asc,original):
    assert recover_p2k(candidate,good)==original
    assert len(asc)==5998 and sha256(asc).hexdigest()==P2LB_ASC_SHA
    assert asc.count(b'Aga Sprite Bank Free(-19000)')==4
    assert asc.count(b'Aga Sprite Bank Free(29)')==1
    assert b'SOURCE_TAG M19_S1P2LB_DMA_DIAG_V1' in asc
    assert b'DMA_FREE_PROVEN 0' in asc
    return True

def check_active_pair():
    """Exact canonical P2k, P2l-b or P2l-c, paired ASC, protected fixture/L2b."""
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    current=(root/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(root/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    asc=(root/'tests/current/SPRITE_PUBLIC.asc').read_bytes()
    assert sha256(good).hexdigest()==P2DL2B_SHA
    assert sha256((root/'tests/current/AGSP_S1P1E_FINAL.ABK').read_bytes()).hexdigest()==(
        '225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93')
    assert [x.name for x in (root/'tests/current').glob('*.asc')]==['SPRITE_PUBLIC.asc']
    from verify_m19_s1p2l_c_delivery import P2LC_SHA, recover_p2lb, verify_asc
    if sha256(current).hexdigest()==P2LC_SHA:
        recover_p2lb(current,good)
        verify_asc(asc)
    elif sha256(current).hexdigest()==P2LB_SHA:
        recover_p2k(current,good)
        assert len(asc)==5998 and sha256(asc).hexdigest()==P2LB_ASC_SHA
    else:
        verify_s1p2k(current,good)
        assert len(asc)==4630 and sha256(asc).hexdigest()=='987d45cd1f14aa62df944c7af35eda6884b0a44a70d3b7f0415e0ff2dd8a2c1e'
    print("P2K/P2LB/P2LC exact active pair PASS",sha256(current).hexdigest())

if __name__=='__main__':
    check_active_pair()
