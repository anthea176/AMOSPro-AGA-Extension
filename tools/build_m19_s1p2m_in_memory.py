#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build S1-P2m in memory only. Exact active P2l-c parent is rebuilt first."""
import argparse, json, shutil, subprocess, tempfile
from hashlib import sha256, sha1
from pathlib import Path
from audit_ap20 import inspect, parse, token_role_issues, walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from compiler_relocation import RBSR, repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from build_m19_s1p2l_c_in_memory import build_s1p2lc, protected
from build_m19_s1p2k_close_in_memory import build_s1p2k_close, SRC
from build_m19_s1p2k_in_memory import MASTER
from build_m19_s1p2l_a_in_memory import headroom, expanded, RESERVE
from struct import pack

def build_s1p2m(vasm):
    vasm=Path(vasm).resolve()
    before=protected()
    parent,old_info=build_s1p2lc(vasm)
    assert parent==before[0]
    assert sha256(parent).hexdigest()=='148b4d06702f84dd6de3eacd069a55c4759164bb4dd3c74f319f81e6f077f3f5'
    tok,old,title=unpack_ap20(parent)
    base,meta=build_s1p2k_close(vasm,lifecycle=True)
    _,parts,_=unpack_ap20(base)
    delta=meta['root']-0x1c2
    at=old_info['sprite_at']
    assert parts[207]==old[207][:len(DISPATCH_V2)+at]
    with tempfile.TemporaryDirectory(prefix='aga-s1p2m-') as temp:
        folder=Path(temp)/'native'
        shutil.copytree(SRC,folder)
        p=folder/'M19_S1P2A_CHIP_PREPARE_MC68020.s'
        s=p.read_text(encoding='ascii')
        a='    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"'
        assert s.count(a)==1
        p.write_text(s.replace(a,''),encoding='ascii')
        s=(folder/'M19_S1P2M_RECLAIM_MC68020.s').read_text(encoding='ascii')
        (folder/'p2i_reclaim_core.s').write_text(s[s.index('AGSP_P2G_RECLAIM:'):],encoding='ascii')
        with (folder/MASTER).open('a',encoding='ascii') as f:
            f.write(f'\nP2I_CELL_DELTA equ {delta}\n')
            for name in ('M19_S1P2M_PUBLIC_MC68020.s','M19_S1P2A_CHIP_PREPARE_MC68020.s',
                         'M19_S1P2M_RETIRE_MC68020.s','p2i_reclaim_core.s',
                         'M19_S1P2M_PERSIST_ROOT_MC68020.s'):
                f.write('    include "'+name+'"\n')
        out=Path(temp)/'native.bin'
        subprocess.run([str(vasm),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                        '-quiet','-o',str(out),str(folder/MASTER)],cwd=folder,check=True,timeout=120)
        native=out.read_bytes()
    assert DISPATCH_V2+native[:at]==parts[207]
    assert all(native[at+i:at+i+2]==b'\x60\x00' for i in (0,4,8))
    new=list(old)
    new[142]=parts[142]
    new[207]=DISPATCH_V2+native
    new[213]=RBSR+pack('>HH',207,at+8)+bytes.fromhex('4e75')
    assert all(new[i]==old[i] for i in range(214) if i not in (142,207,213))
    assert len(new[142])<=MAX_UNIT_BYTES and len(new[207])<=MAX_UNIT_BYTES
    links=pc16_displacements(new)
    reserve=expanded(new,RESERVE)
    assert headroom(new)>=RESERVE
    newtitle=title.replace(b'S1-P2l-c',b'S1-P2m')
    assert newtitle!=title and len(newtitle)%2==0
    image=repack_ap20(parent,tok,new,newtitle)
    assert unpack_ap20(image)==(tok,new,newtitle)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([row for row in walk_tokens(tok) if row['signature']])==105
    assert protected()==before
    return image,dict(meta,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        commands=105,entries=214,native_sprite=len(native),sprite_at=at,
        cell_delta=delta,unit142_free=MAX_UNIT_BYTES-len(new[142]),unit207=len(new[207]),
        pc16_max=max(map(abs,links.values())),reserve_bytes=RESERVE,
        unit207_pc16_free=headroom(new),reserve_pc16=max(map(abs,pc16_displacements(reserve).values())),
        parent_sha=sha256(parent).hexdigest(),installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    _,meta=build_s1p2m(a.vasm)
    print('S1P2M_IN_MEMORY '+json.dumps(meta,sort_keys=True),flush=True)
