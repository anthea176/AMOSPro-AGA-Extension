#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build S2b integrated source-only candidate from exact S2a parent."""
import argparse, json, shutil, subprocess, tempfile
from hashlib import sha1,sha256
from pathlib import Path
from audit_ap20 import inspect,parse,token_role_issues,walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from compiler_relocation import repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from build_m19_s2a_in_memory import build_s2a,MASTER,SRC,ROOT,once,protected
from build_m19_s2b_close_in_memory import build_s2b_close
from build_m19_s1p2l_a_in_memory import headroom,expanded,RESERVE
from verify_m19_s2a_delivery import verify_library,verify_asc,verify_abk,S2A_SHA

S2=ROOT/'src/native/m19_s2'
FILES=('M19_S2B_PUBLIC_MC68020.s','M19_S2B_RETIRE_PAIR_MC68020.s',
       'M19_S2B_REGISTRY_MC68020.s','M19_S2B_ALLOCATE_MC68020.s',
       'M19_S2B_PERSIST_ROOT_MC68020.s','M19_S2B_FRAME_CHANGE_MC68020.s',
       'M19_S2B_FRAME_STAGE_MC68020.s')

def build_s2b(vasm, *, close_source_observer=None, sprite_source_observer=None):
    vasm=Path(vasm).resolve()
    before=protected()
    bank=(ROOT/'tests/current/AGSP_S2A_ANIMATION.ABK').read_bytes()
    from verify_m19_s2b_delivery import pre_s2b_pair,S2B_SHA,verify_library as verify_s2b
    parent,good,asc,abk=pre_s2b_pair(before)
    assert sha256(parent).hexdigest()==S2A_SHA
    verify_library(parent,good);verify_asc(asc);verify_abk(bank)
    reconstructed,_=build_s2a(vasm)
    assert reconstructed==parent
    tok,old,title=unpack_ap20(parent)
    close,info=build_s2b_close(vasm,source_observer=close_source_observer)
    _,units,_=unpack_ap20(close)
    root=info['root']
    delta=root-0x1c2
    assert len(units[142])<=MAX_UNIT_BYTES and root==len(units[142])-16
    assert units[142][-16:]==old[142][-16:]
    assert all(units[i]==old[i] for i in range(208) if i not in (142,207))
    at=6126
    with tempfile.TemporaryDirectory(prefix='aga-s2b-') as td:
        folder=Path(td)/'native'
        shutil.copytree(SRC,folder)
        p=folder/'M19_S1P2A_CHIP_PREPARE_MC68020.s'
        p.write_text(once(p.read_text(encoding='ascii'),
                     '    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"',''),encoding='ascii')
        for name in FILES:
            shutil.copyfile(S2/name,folder/name)
        with (folder/MASTER).open('a',encoding='ascii') as f:
            f.write(f'\nP2I_CELL_DELTA equ {delta}\n')
            for name in (FILES[0],'M19_S1P2A_CHIP_PREPARE_MC68020.s')+FILES[1:]:
                f.write('    include "'+name+'"\n')
        out=Path(td)/'native.bin'
        subprocess.run([str(vasm),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                        '-quiet','-o',str(out),str(folder/MASTER)],cwd=folder,
                       check=True,timeout=120)
        native=out.read_bytes()
        if sprite_source_observer is not None:
            sprite_source_observer(folder,native,delta)
    assert native[:at]==old[207][len(DISPATCH_V2):len(DISPATCH_V2)+at]
    assert all(native[at+i:at+i+2]==bytes.fromhex('6000') for i in (0,4,8))
    parts=list(old);parts[142]=units[142];parts[207]=DISPATCH_V2+native
    assert [i for i,(a,b) in enumerate(zip(parts,old)) if a!=b]==[142,207]
    assert len(parts[207])<=MAX_UNIT_BYTES
    links=pc16_displacements(parts)
    assert headroom(parts)>=RESERVE
    title2=title.replace(b'S2a-P1',b'S2b-P1')
    assert title2!=title and len(title2)==len(title)
    image=repack_ap20(parent,tok,parts,title2)
    assert unpack_ap20(image)==(tok,parts,title2)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([x for x in walk_tokens(tok) if x['signature']])==105
    verify_s2b(image,good)
    if sha256(before[0]).hexdigest()==S2B_SHA:assert image==before[0]
    assert protected()==before
    assert (ROOT/'tests/current/AGSP_S2A_ANIMATION.ABK').read_bytes()==bank
    return image,dict(info,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        parent_sha=S2A_SHA,commands=105,entries=214,sprite_at=at,
        cell_delta=delta,native_sprite=len(native),unit142_free=MAX_UNIT_BYTES-len(parts[142]),
        unit207=len(parts[207]),pc16_max=max(map(abs,links.values())),
        unit207_pc16_free=headroom(parts),reserve_bytes=RESERVE,
        reserve_pc16=max(map(abs,pc16_displacements(expanded(parts,RESERVE)).values())),
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    v=p.parse_args().vasm
    a,info=build_s2b(v)
    b,other=build_s2b(v)
    assert a==b and info==other
    print('S2B_EXACT_BUILD_PASS '+json.dumps(info,sort_keys=True),flush=True)
