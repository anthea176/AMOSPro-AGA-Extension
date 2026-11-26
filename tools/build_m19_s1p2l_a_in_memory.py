#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2l-a: source-only private observer in UNIT207, frozen UNIT142."""
import argparse, json, shutil, subprocess, tempfile
from hashlib import sha256, sha1
from pathlib import Path
from audit_ap20 import inspect, parse, token_role_issues
from ap20_v2_island_dispatch import pc16_displacements
from compiler_relocation import repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from build_m19_s1p2k_in_memory import build_s1p2k, ROOT, SRC, MASTER
from active_library import S1P2K_SHA, S1P2LB_SHA, P2DL2B_SHA, verify_s1p2k

PROBE='M19_S1P2L_DMA_OBSERVE_MC68020.s'
GROUP=207
RESERVE=16384
ACTIVE_ASC='987d45cd1f14aa62df944c7af35eda6884b0a44a70d3b7f0415e0ff2dd8a2c1e'

def protected():
    return tuple((ROOT/p).read_bytes() for p in (
        'dist/AMOSPro_AGA.Lib', 'dist/AMOSPro_AGA_LAST_GOOD.Lib',
        'tests/current/SPRITE_PUBLIC.asc','tests/current/AGSP_S1P1E_FINAL.ABK'))

def expanded(parts, growth):
    assert growth>=0 and not growth&1
    out=list(parts)
    out[GROUP]+=bytes(growth)
    if len(out[GROUP])>MAX_UNIT_BYTES:
        raise ValueError('UNIT207 WORD count overflow')
    pc16_displacements(out)
    return out

def headroom(parts):
    lo,hi=0,(MAX_UNIT_BYTES-len(parts[GROUP]))//2+1
    while lo+1<hi:
        mid=(lo+hi)//2
        try:
            expanded(parts,2*mid)
        except ValueError:
            hi=mid
        else:
            lo=mid
    expanded(parts,lo*2)
    try:
        expanded(parts,lo*2+2)
    except ValueError:
        return lo*2
    raise AssertionError('Capacity boundary was not rejected')

def build_s1p2la(vasm):
    vasm=Path(vasm).resolve()
    original=protected()
    from verify_m19_s1p2l_b_delivery import P2LB_ASC_SHA, recover_p2k
    identities=tuple(sha256(x).hexdigest() for x in original)
    assert identities[1]==P2DL2B_SHA
    assert identities[3]=='225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93'
    assert (identities[0],identities[2]) in ((S1P2K_SHA,ACTIVE_ASC),(S1P2LB_SHA,P2LB_ASC_SHA))
    predecessor=original[0] if identities[0]==S1P2K_SHA else recover_p2k(original[0],original[1])
    base,meta=build_s1p2k(vasm)
    assert base==predecessor
    verify_s1p2k(base,original[1])
    tok,parts,title=unpack_ap20(base)
    assert len(parts)==214 and len(parts[142])==65276
    assert len(parts[GROUP])==10208
    assert headroom(parts)==22526
    delta=meta['root']-0x1c2
    with tempfile.TemporaryDirectory(prefix='aga-s1p2la-') as temp:
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
                         'M19_S1P2K_PERSIST_ROOT_MC68020.s',PROBE):
                f.write('    include "'+name+'"\n')
        out=Path(temp)/'native.bin'
        subprocess.run([str(vasm),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                        '-quiet','-o',str(out),str(folder/MASTER)],
                       cwd=folder,check=True,timeout=120)
        native=out.read_bytes()
    group=DISPATCH_V2+native
    assert group.startswith(parts[GROUP]) and len(group)>len(parts[GROUP])
    growth=len(group)-len(parts[GROUP])
    assert not growth&1
    newparts=list(parts)
    newparts[GROUP]=group
    assert [i for i,(x,y) in enumerate(zip(parts,newparts)) if x!=y]==[GROUP]
    links=pc16_displacements(newparts)
    assert all(links[k]==v-(growth if k in (209,211,213) else 0)
               for k,v in pc16_displacements(parts).items())
    reserve=expanded(newparts,RESERVE)
    remaining=headroom(newparts)
    assert remaining==22526-growth and remaining>=RESERVE
    newtitle=title.replace(b'S1-P2k',b'S1-P2l')
    assert newtitle!=title
    image=repack_ap20(base,tok,newparts,newtitle)
    assert unpack_ap20(image)==(tok,newparts,newtitle)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert protected()==original
    return image,dict(meta,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+bytes(1)+image).hexdigest(),
        unit142=65276,unit142_free=258,native_sprite=len(native),
        probe_offset=len(parts[GROUP]),probe_native=growth,
        unit207=len(group),unit207_word_free=MAX_UNIT_BYTES-len(group),
        unit207_pc16_free=remaining,pc16_max=max(map(abs,links.values())),
        reserve_bytes=RESERVE,reserve_pc16=max(map(abs,pc16_displacements(reserve).values())),
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    _,meta=build_s1p2la(a.vasm)
    print('S1P2LA_IN_MEMORY '+json.dumps(meta,sort_keys=True),flush=True)
