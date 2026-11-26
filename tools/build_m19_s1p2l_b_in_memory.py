#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2l-b source-only diagnostic route: retain the exact qualified P2l-a prefix."""
import argparse, json, shutil, subprocess, tempfile
from hashlib import sha256, sha1
from pathlib import Path
from struct import pack
from audit_ap20 import inspect, parse, token_role_issues
from ap20_v2_island_dispatch import pc16_displacements
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from build_m19_s1p2l_a_in_memory import (
    build_s1p2la, protected, headroom, expanded, ROOT, SRC, MASTER, PROBE, GROUP, RESERVE,
)

P2LA_SHA='c94a75424c03c236c33a3b4e6356978878dd04ae769ea3d25e8ec114fd9e6060'
P2LA_BLOB='f44083d21ba84f403dfee8e84a9653a45373a3d6'
ADAPTER='M19_S1P2LB_DMA_DIAG_ROUTE_MC68020.s'
DIAG_ARGUMENT=-19000
BANK_FREE_ENTRY=213

def build_s1p2lb(vasm):
    vasm=Path(vasm).resolve()
    original=protected()
    parent,meta=build_s1p2la(vasm)
    assert len(parent)==149892 and sha256(parent).hexdigest()==P2LA_SHA
    assert sha1(b'blob 149892'+bytes(1)+parent).hexdigest()==P2LA_BLOB
    tok,parts,title=unpack_ap20(parent)
    assert len(parts)==214 and len(parts[142])==65276
    assert len(parts[GROUP])==11020 and meta['probe_native']==812
    assert parts[212]==GETP
    assert parts[BANK_FREE_ENTRY]==RBSR+pack('>HH',GROUP,meta['sprite_at']+8)+b'\x4e\x75'
    assert headroom(parts)==21714
    delta=meta['cell_delta']
    with tempfile.TemporaryDirectory(prefix='aga-s1p2lb-') as temp:
        folder=Path(temp)/'native'
        shutil.copytree(SRC,folder)
        p=folder/'M19_S1P2A_CHIP_PREPARE_MC68020.s'
        s=p.read_text(encoding='ascii')
        a='    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"'
        assert s.count(a)==1
        p.write_text(s.replace(a,''),encoding='ascii')
        s=(folder/'M19_S1P2K_RECLAIM_MC68020.s').read_text(encoding='ascii')
        (folder/'p2i_reclaim_core.s').write_text(s[s.index('AGSP_P2G_RECLAIM:'):],encoding='ascii')
        with (folder/MASTER).open('a',encoding='ascii') as f:
            f.write(f'\nP2I_CELL_DELTA equ {delta}\n')
            for name in ('M19_S1P2K_PUBLIC_MC68020.s','M19_S1P2A_CHIP_PREPARE_MC68020.s',
                         'M19_S1P2J_RETIRE_MC68020.s','p2i_reclaim_core.s',
                         'M19_S1P2K_PERSIST_ROOT_MC68020.s',PROBE,ADAPTER):
                f.write('    include "'+name+'"\n')
        out=Path(temp)/'native.bin'
        subprocess.run([str(vasm),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                        '-quiet','-o',str(out),str(folder/MASTER)],
                       cwd=folder,check=True,timeout=120)
        native=out.read_bytes()
    group=DISPATCH_V2+native
    assert group.startswith(parts[GROUP])
    growth=len(group)-len(parts[GROUP])
    assert 0<growth<=128 and not growth&1
    adapter_offset=len(parts[GROUP])-len(DISPATCH_V2)
    newparts=list(parts)
    newparts[GROUP]=group
    newparts[BANK_FREE_ENTRY]=RBSR+pack('>HH',GROUP,adapter_offset)+b'\x4e\x75'
    assert [i for i,(x,y) in enumerate(zip(parts,newparts)) if x!=y]==[GROUP,BANK_FREE_ENTRY]
    assert newparts[142]==parts[142]==unpack_ap20(original[0])[1][142]
    assert newparts[GROUP][:len(parts[GROUP])]==parts[GROUP]
    assert len(group)<=MAX_UNIT_BYTES
    links=pc16_displacements(newparts)
    assert all(links[k]==v-(growth if k in (209,211,213) else 0)
               for k,v in pc16_displacements(parts).items())
    remaining=headroom(newparts)
    assert remaining==21714-growth and remaining>=RESERVE
    reserve=expanded(newparts,RESERVE)
    newtitle=title.replace(b'S1-P2l',b'S1-P2l-b')
    assert newtitle!=title and len(newtitle)%2==0
    image=repack_ap20(parent,tok,newparts,newtitle)
    assert unpack_ap20(image)==(tok,newparts,newtitle)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    from verify_m19_s1p2l_b_delivery import P2LB_SHA, recover_p2k
    predecessor=recover_p2k(image,original[1])
    from verify_m19_s1p2l_c_delivery import P2LC_SHA, recover_p2lb
    if sha256(original[0]).hexdigest()==P2LC_SHA:
        assert image==recover_p2lb(original[0],original[1])
    elif sha256(original[0]).hexdigest()==P2LB_SHA:
        assert image==original[0]
    else:
        assert predecessor==original[0]
    assert protected()==original
    return image,dict(meta,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+bytes(1)+image).hexdigest(),
        native_sprite=len(native),unit207=len(group),unit207_pc16_free=remaining,
        unit207_word_free=MAX_UNIT_BYTES-len(group),
        pc16_max=max(map(abs,links.values())),
        reserve_pc16=max(map(abs,pc16_displacements(reserve).values())),
        parent_sha=P2LA_SHA,diag_argument=DIAG_ARGUMENT,
        diag_native=growth,diag_offset=adapter_offset,
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    _,meta=build_s1p2lb(a.vasm)
    print('S1P2LB_IN_MEMORY '+json.dumps(meta,sort_keys=True),flush=True)
