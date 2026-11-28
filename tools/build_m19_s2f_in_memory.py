#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2f candidate: prove exact active S2e first, then source-built clipping.
No installed library, ASC, ABK, LAST_GOOD, archive or release writes."""
import argparse,json
from hashlib import sha256
from pathlib import Path
from active_library import S2E_SHA,P2DL2B_SHA
from build_m19_s2d_in_memory import build_s2d,protected
from build_m19_s2e_in_memory import build_s2e
from compiler_relocation import unpack_ap20
from audit_ap20 import inspect,parse,token_role_issues,walk_tokens

def build_s2f(vasm):
    before=protected()
    from verify_m19_s2f_delivery import S2F_SHA,pre_s2f_pair,verify_library
    from verify_m19_s2g_delivery import pre_s2g_pair
    s2f_parent=pre_s2g_pair(before)
    lineage=pre_s2f_pair(s2f_parent)
    assert sha256(lineage[0]).hexdigest()==S2E_SHA
    assert sha256(before[1]).hexdigest()==P2DL2B_SHA
    parent,meta=build_s2e(vasm)
    assert parent==lineage[0] and meta['sha256']==S2E_SHA
    image,info=build_s2d(vasm,hotspots=True,clipping=True)
    ot,old,oz=unpack_ap20(parent)
    nt,new,nz=unpack_ap20(image)
    assert nt==ot and len(new)==len(old)==219
    assert nz==oz.replace(b'0.15.0-alpha.2',b'0.15.0-alpha.3')
    assert [i for i,(a,b) in enumerate(zip(old,new)) if a!=b]==[142,213]
    assert info['record_bytes']==188 and info['unit142_free']>0
    assert info['sprite_at']==meta['sprite_at'] and info['root']==meta['root']
    assert new[142][info['root']:info['root']+16]==old[142][info['root']:info['root']+16]
    assert info['pc16_max']<=32767 and info['reserve_pc16']<=32767
    assert info['reserve_bytes']==meta['reserve_bytes']==16384
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([x for x in walk_tokens(nt) if x['signature']])==105
    if sha256(s2f_parent[0]).hexdigest()==S2F_SHA:
        verify_library(image,before[1])
        assert image==s2f_parent[0]
    assert protected()==before
    return image,dict(info,parent_sha=S2E_SHA,hotspots=True,clipping=True,
                      registry_bytes=672,registry_version=8,installable=False,
                      compiler_tested=False,runtime_tested=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    data,info=build_s2f(a.vasm)
    other,second=build_s2f(a.vasm)
    assert data==other and info==second
    print('S2F_EXACT_BUILD_PASS '+json.dumps(info,sort_keys=True),flush=True)
