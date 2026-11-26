#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Rebuild exact P2j first, then P2k from source; no dist writes."""
import argparse
from hashlib import sha1,sha256
from pathlib import Path
from struct import pack
import shutil,subprocess,tempfile,json
from audit_ap20 import inspect,parse,token,walk_tokens,token_role_issues
from ap20_v2_island_dispatch import pc16_displacements
from compiler_relocation import GETP,RBSR,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from build_m19_s1p2k_close_in_memory import build_s1p2k_close,ROOT,SRC
from build_m19_s1p2j_in_memory import build_s1p2j
from active_library import S1P1I_SHA,S1P2I_SHA,S1P2J_SHA,S1P2K_SHA, S1P2LB_SHA,S1P2LC_SHA,P2DL2B_SHA,verify_s1p2i,verify_s1p2j,verify_s1p2k
MASTER='M19_S1P1I_BANK_PUBLIC_MC68020.s'
APIS=(('aga sprite','00,0,0,0'),('aga sprite off','00'),('aga sprite bank free','00'))

def build_s1p2k(vasm):
    vasm=Path(vasm).resolve()
    installed=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    active=installed
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    if sha256(active).hexdigest()==S1P2LC_SHA:
        from verify_m19_s1p2l_c_delivery import recover_p2lb
        active=recover_p2lb(active,good)
    if sha256(active).hexdigest()==S1P2LB_SHA:
        from verify_m19_s1p2l_b_delivery import recover_p2k
        active=recover_p2k(active,good)
    assert sha256(active).hexdigest() in (S1P2J_SHA,S1P2K_SHA)
    exact,_=build_s1p2j(vasm)
    verify_s1p2j(exact,good)
    if sha256(active).hexdigest()==S1P2J_SHA:
        assert exact==active
    else:
        verify_s1p2k(active,good)
    assert sha256(good).hexdigest()==P2DL2B_SHA
    parent,meta=build_s1p2k_close(vasm)
    tok,parts,title=unpack_ap20(parent)
    at=len(parts[207])-len(DISPATCH_V2)
    assert parts[142][-16:]==bytes.fromhex('00000000414753490001001000000000')
    delta=meta['root']-0x1c2
    with tempfile.TemporaryDirectory(prefix='aga-s1p2i-') as temp:
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
            for name in ('M19_S1P2K_PUBLIC_MC68020.s',
                         'M19_S1P2A_CHIP_PREPARE_MC68020.s',
                         'M19_S1P2J_RETIRE_MC68020.s',
                         'p2i_reclaim_core.s',
                         'M19_S1P2K_PERSIST_ROOT_MC68020.s'):
                f.write('    include "'+name+'"\n')
        out=Path(temp)/'native.bin'
        subprocess.run([str(vasm),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                        '-quiet','-o',str(out),str(folder/MASTER)],cwd=folder,check=True)
        native=out.read_bytes()
    assert DISPATCH_V2+native[:at]==parts[207]
    assert all(native[at+i:at+i+2]==b'\x60\x00' for i in (0,4,8))
    assert len(native)+len(DISPATCH_V2)<=MAX_UNIT_BYTES
    newparts=list(parts)
    newparts[207]=DISPATCH_V2+native
    updated=tok[:-6]
    for j,(name,sig) in enumerate(APIS):
        entry=len(newparts)+1
        newparts.extend((GETP,RBSR+pack('>HH',207,at+4*j)+b'\x4e\x75'))
        updated+=token(name,1,entry,sig)
    updated+=tok[-6:]
    oldlinks=pc16_displacements(parts)
    links=pc16_displacements(newparts)
    assert all(links[k]==v for k,v in oldlinks.items())
    assert set(links)-set(oldlinks)=={209,211,213}
    out=repack_ap20(parent,updated,newparts,title)
    assert unpack_ap20(out)==(updated,newparts,title)
    audit=inspect(parse(out))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    before=list(walk_tokens(tok));after=list(walk_tokens(updated))
    assert after[:-3]==before
    assert [(x['name'],x['instruction'],x['function'],x['signature']) for x in after[-3:]]==[
        (name,1,209+j*2,sig) for j,(name,sig) in enumerate(APIS)]
    assert len([row for row in after if row['signature']])==105 and len(newparts)==214
    assert [i for i,(a,b) in enumerate(zip(parts,newparts)) if a!=b]==[207]
    assert (ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()==installed
    assert (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()==good
    prior_tok,prior_parts,prior_title=unpack_ap20(exact)
    assert updated==prior_tok and title==prior_title.replace(b'S1-P2j',b'S1-P2k')
    assert [i for i,(x,y) in enumerate(zip(prior_parts,newparts)) if x!=y]==[142,207]
    # Existing links are byte-stable; the three Sprite stubs move by
    # exactly the group-207 size delta. Validate their actual signed PC16.
    prior_links=pc16_displacements(prior_parts)
    growth=len(newparts[207])-len(prior_parts[207])
    assert set(prior_links)==set(links)
    assert all(links[k]==v-(growth if k in (209,211,213) else 0)
               for k,v in prior_links.items())
    verify_s1p2k(out,good)
    if sha256(active).hexdigest()==S1P2K_SHA:
        assert out==active
    return out,dict(meta,sha256=sha256(out).hexdigest(),bytes=len(out),
        git_blob=sha1(f'blob {len(out)}'.encode()+b'\0'+out).hexdigest(),
        commands=105,entries=214,native_sprite=len(native),sprite_at=at,
        cell_delta=delta,pc16_max=max(map(abs,links.values())),
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    args=p.parse_args()
    _,info=build_s1p2k(args.vasm)
    print('S1P2K_IN_MEMORY '+json.dumps(info,sort_keys=True),flush=True)
