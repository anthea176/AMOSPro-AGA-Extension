#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2d-P1: link wide capture from the exact S2c-E1 source tree, in memory only.

No new token, no display/DMA implementation, no installed writes.
The historical S2c builder is reconstructed byte-for-byte before returning
a new image. All wide source substitutions happen in an independent copy
of the prepared source tree; the old builder's inputs are never modified.
"""
import argparse,json,shutil,tempfile
from hashlib import sha1,sha256
from pathlib import Path
from struct import pack,unpack_from
from active_library import S2CE_SHA,P2DL2B_SHA
from build_m19_s2c_in_memory import build_s2c,MASTER,ROOT,protected,assemble_bin,once,SPR,RESERVE
from compiler_relocation import RBSR,unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect,parse,token_role_issues,walk_tokens

FILES=('M19_S2D_GET_PUBLIC_MC68020.s','M19_S2D_CAPTURE_PIPELINE_MC68020.s',
       'M19_S2D_SCREEN_RGB24_MC68020.s','M19_S2D_AGSP_CAPTURE_MC68020.s',
       'M19_S2D_AGSP_REPACK_MC68020.s')

def build_s2d_capture(vasm, *, final_source_observer=None, final_close_source_observer=None):
    vasm=Path(vasm).resolve()
    before=protected()
    from verify_m19_s2d_delivery import pre_s2d_pair
    lineage=pre_s2d_pair(before)
    assert sha256(lineage[0]).hexdigest()==S2CE_SHA
    assert sha256(before[1]).hexdigest()==P2DL2B_SHA
    staged={}
    def observe(folder,full,delta,at):
        with tempfile.TemporaryDirectory(prefix='s2d_capture_') as tmp:
            work=Path(tmp)/'source'
            shutil.copytree(folder,work)
            master=work/MASTER
            src=master.read_text(encoding='ascii')
            marker='P2I_CELL_DELTA equ '+str(delta)+'\n'
            assert src.count(marker)==1
            prefix,suffix=src.split(marker)
            probe=work/'s2d_prefix.s'
            probe.write_text(prefix,encoding='ascii')
            assert assemble_bin(vasm,work,probe,'s2d_old_prefix.bin')==full[:at]
            for name in FILES:
                shutil.copyfile(ROOT/'src/native/m19_s2'/name,work/name)
            prefix=once(prefix,'include "M19_S2C_CAPTURE_PIPELINE_MC68020.s"',
                        'include "M19_S2D_CAPTURE_PIPELINE_MC68020.s"')
            prefix=once(prefix,'include "M19_S2C_GET_PUBLIC_MC68020.s"',
                        'include "M19_S2D_GET_PUBLIC_MC68020.s"')
            probe.write_text(prefix,encoding='ascii')
            new_prefix=assemble_bin(vasm,work,probe,'s2d_new_prefix.bin')
            master.write_text(prefix+marker+suffix,encoding='ascii')
            wide=assemble_bin(vasm,work,master,'s2d_capture_full.bin')
            new_at=len(new_prefix)
            assert wide[:new_at]==new_prefix
            assert all(wide[new_at+i:new_at+i+2]==b'\x60\x00' for i in (0,4,8))
            assert len(wide)-new_at==len(full)-at
            staged.update(old=DISPATCH_V2+full,new=DISPATCH_V2+wide,at=at,new_at=new_at)
            if final_source_observer is not None:
                final_source_observer(work,wide,delta,new_at)
    parent,info=build_s2c(vasm,diagnostic=True,viewport_chain=True,
                         final_sprite_source_observer=observe,
                         final_close_source_observer=final_close_source_observer)
    assert parent==lineage[0] and sha256(parent).hexdigest()==S2CE_SHA
    tok,parts,title=unpack_ap20(parent)
    assert len(parts)==219 and parts[SPR]==staged['old']
    new=list(parts);new[SPR]=staged['new']
    for index,old_offset in ((204,0),(206,8),(208,staged['at']),
                             (210,staged['at']+4),(212,staged['at']+8)):
        assert parts[index]==RBSR+pack('>HH',SPR,old_offset)+b'\x4e\x75'
        off=old_offset if index<208 else old_offset-staged['at']+staged['new_at']
        new[index]=RBSR+pack('>HH',SPR,off)+b'\x4e\x75'
    changed=[i for i,(x,y) in enumerate(zip(parts,new)) if x!=y]
    assert changed==[208,210,212,SPR]
    assert all(len(x)<=MAX_UNIT_BYTES for x in new)
    assert len(new[SPR])+RESERVE<=MAX_UNIT_BYTES
    links=pc16_displacements(new)
    trial=list(new);trial[SPR]+=bytes(RESERVE)
    reserve=pc16_displacements(trial)
    nz=title.replace(b'S2c-E1',b'S2d-P1')
    assert nz!=title and len(nz)==len(title)
    image=repack_ap20(parent,tok,new,nz)
    assert unpack_ap20(image)==(tok,new,nz)
    report=inspect(parse(image))
    assert not report['issues'] and not token_role_issues(report['tokens'])
    assert len([row for row in walk_tokens(tok) if row['signature']])==105
    assert protected()==before
    return image,dict(info,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        parent_sha=S2CE_SHA,sprite_unit_bytes=len(new[SPR]),
        native_sprite=len(new[SPR])-len(DISPATCH_V2),
        sprite_group_free=MAX_UNIT_BYTES-len(new[SPR]),
        sprite_at=staged['new_at'],pc16_max=max(map(abs,links.values())),
        reserve_pc16=max(map(abs,reserve.values())),wide_capture=True,
        wide_display=False,installable=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    v=p.parse_args().vasm
    a,info=build_s2d_capture(v)
    b,other=build_s2d_capture(v)
    assert a==b and info==other
    print('S2D_P1_CAPTURE_LINK_BUILD_PASS '+json.dumps(info,sort_keys=True),flush=True)
