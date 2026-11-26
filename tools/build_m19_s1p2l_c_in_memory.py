#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2l-c: source-derived idle detail only; no installed binary or DMA release."""
import argparse, json, shutil, subprocess, tempfile
from hashlib import sha256, sha1
from pathlib import Path
from audit_ap20 import inspect, parse, token_role_issues
from ap20_v2_island_dispatch import pc16_displacements
from compiler_relocation import repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from build_m19_s1p2l_b_in_memory import (
    build_s1p2lb, protected, headroom, expanded, SRC, MASTER, PROBE, GROUP, RESERVE, ADAPTER,
)

PARENT_SHA='d9b690287c82c52a766d5ab4b015bb29d25057cbe55a630c0e30d88d46bd4ab1'
PARENT_BLOB='17136bee1d0ac8ae1e5d9431c51fd1bdf24129f2'
DETAIL='M19_S1P2LC_IDLE_DETAIL_MC68020.s'
OLD_RETURN='p2l_not_idle:\n    move.l #-185,d0\n    rts\n'
NEW_RETURN='p2l_not_idle:\n    bra.w p2lc_idle_detail\n    nop\n    nop\n'

def build_s1p2lc(vasm):
    vasm=Path(vasm).resolve()
    original=protected()
    parent,meta=build_s1p2lb(vasm)
    from verify_m19_s1p2l_c_delivery import P2LC_SHA, recover_p2lb
    expected_parent=recover_p2lb(original[0],original[1]) if sha256(original[0]).hexdigest()==P2LC_SHA else original[0]
    assert parent==expected_parent and len(parent)==149940
    assert sha256(parent).hexdigest()==PARENT_SHA
    assert sha1(b'blob 149940'+bytes(1)+parent).hexdigest()==PARENT_BLOB
    tok,parts,title=unpack_ap20(parent)
    assert len(parts)==214 and len(parts[142])==65276 and len(parts[GROUP])==11064
    with tempfile.TemporaryDirectory(prefix='aga-s1p2lc-') as temp:
        folder=Path(temp)/'native'
        shutil.copytree(SRC,folder)
        p=folder/'M19_S1P2A_CHIP_PREPARE_MC68020.s'
        s=p.read_text(encoding='ascii')
        a='    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"'
        assert s.count(a)==1
        p.write_text(s.replace(a,''),encoding='ascii')
        s=(folder/'M19_S1P2K_RECLAIM_MC68020.s').read_text(encoding='ascii')
        (folder/'p2i_reclaim_core.s').write_text(s[s.index('AGSP_P2G_RECLAIM:'):],encoding='ascii')
        p=folder/PROBE
        s=p.read_text(encoding='ascii')
        assert s.count(OLD_RETURN)==1
        p.write_text(s.replace(OLD_RETURN,NEW_RETURN,1),encoding='ascii')
        with (folder/MASTER).open('a',encoding='ascii') as f:
            f.write(f'\nP2I_CELL_DELTA equ {meta["cell_delta"]}\n')
            for name in ('M19_S1P2K_PUBLIC_MC68020.s','M19_S1P2A_CHIP_PREPARE_MC68020.s',
                         'M19_S1P2J_RETIRE_MC68020.s','p2i_reclaim_core.s',
                         'M19_S1P2K_PERSIST_ROOT_MC68020.s',PROBE,ADAPTER,DETAIL):
                f.write('    include "'+name+'"\n')
        out=Path(temp)/'native.bin'
        subprocess.run([str(vasm),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                        '-quiet','-o',str(out),str(folder/MASTER)],
                       cwd=folder,check=True,timeout=120)
        native=out.read_bytes()
    group=DISPATCH_V2+native
    base=parts[GROUP]
    # Audit the exact same-size source branch replacement, not binary synthesis.
    old=bytes.fromhex('203cffffff474e75')
    offset=base.index(old,meta['probe_offset'])
    assert base.count(old)==1
    assert group[:offset]==base[:offset] and group[offset+8:len(base)]==base[offset+8:]
    assert group[offset:offset+2]==b'\x60\x00' and group[offset+4:offset+8]==b'\x4e\x71'*2
    assert offset+2+int.from_bytes(group[offset+2:offset+4],'big',signed=True)==len(base)
    growth=len(group)-len(base)
    assert 0<growth<=256 and not growth&1
    newparts=list(parts)
    newparts[GROUP]=group
    assert [i for i,(x,y) in enumerate(zip(parts,newparts)) if x!=y]==[GROUP]
    assert newparts[142]==parts[142] and newparts[213]==parts[213]
    assert len(group)<=MAX_UNIT_BYTES
    links=pc16_displacements(newparts)
    assert all(links[k]==v-(growth if k in (209,211,213) else 0)
               for k,v in pc16_displacements(parts).items())
    remaining=headroom(newparts)
    assert remaining==21714-44-growth and remaining>=RESERVE
    reserve=expanded(newparts,RESERVE)
    newtitle=title.replace(b'S1-P2l-b',b'S1-P2l-c')
    assert newtitle!=title and len(newtitle)==len(title)
    image=repack_ap20(parent,tok,newparts,newtitle)
    assert unpack_ap20(image)==(tok,newparts,newtitle)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len(image)==150056 and sha256(image).hexdigest()==P2LC_SHA
    assert recover_p2lb(image,original[1])==parent
    if sha256(original[0]).hexdigest()==P2LC_SHA:
        assert image==original[0]
    assert protected()==original
    return image,dict(meta,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+bytes(1)+image).hexdigest(),
        native_sprite=len(native),unit207=len(group),unit207_pc16_free=remaining,
        unit207_word_free=MAX_UNIT_BYTES-len(group),
        pc16_max=max(map(abs,links.values())),reserve_pc16=max(map(abs,pc16_displacements(reserve).values())),
        parent_sha=PARENT_SHA,idle_patch_offset=offset,idle_detail_bytes=growth,
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    _,meta=build_s1p2lc(a.vasm)
    print('S1P2LC_IN_MEMORY '+json.dumps(meta,sort_keys=True),flush=True)
