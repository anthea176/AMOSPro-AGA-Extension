#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2e source candidate. Exact S2d-P3e source reconstruction first.
Only Close/End registry metadata and Sprite native island may differ.
No writes to canonical library, campaigns, protected fixtures or archives.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
from active_library import S2D_SHA,P2DL2B_SHA
from build_m19_s2d_in_memory import build_s2d,protected
from compiler_relocation import unpack_ap20
from audit_ap20 import inspect,parse,token_role_issues

def build_s2e(vasm):
    before=protected()
    from verify_m19_s2e_delivery import S2E_SHA,pre_s2e_pair,verify_library
    from verify_m19_s2f_delivery import pre_s2f_pair
    s2e_parent=pre_s2f_pair(before)
    lineage=pre_s2e_pair(s2e_parent)
    assert sha256(lineage[0]).hexdigest()==S2D_SHA
    assert sha256(before[1]).hexdigest()==P2DL2B_SHA
    parent,parent_info=build_s2d(vasm)
    assert parent==lineage[0] and parent_info['sha256']==S2D_SHA
    image,info=build_s2d(vasm,hotspots=True)
    ot,old,oz=unpack_ap20(parent)
    nt,new,nz=unpack_ap20(image)
    assert nt==ot and len(new)==len(old)==219
    assert nz==oz.replace(b'0.15.0-alpha.1',b'0.15.0-alpha.2')
    assert [i for i,(a,b) in enumerate(zip(old,new)) if a!=b]==[142,213]
    assert info['record_bytes']==172 and info['unit142_free']>0
    assert info['pc16_max']==parent_info['pc16_max']==3658
    assert info['reserve_pc16']==3658
    assert info['sprite_at']==parent_info['sprite_at']
    assert info['root']==parent_info['root']
    assert new[142][info['root']:info['root']+16]==old[142][info['root']:info['root']+16]
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    if sha256(s2e_parent[0]).hexdigest()==S2E_SHA:
        verify_library(image,before[1])
        assert image==s2e_parent[0]
    assert protected()==before
    return image,dict(info,parent_sha=S2D_SHA,hotspots=True,
                      registry_bytes=624,registry_version=7,installable=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    data,info=build_s2e(a.vasm)
    other,second=build_s2e(a.vasm)
    assert data==other and info==second
    print('S2E_EXACT_BUILD_PASS '+json.dumps(info,sort_keys=True),flush=True)
