#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2c-P1a: integrate only 2/4-plane Get AGA Sprite in exact S2r.

No installed writes and no attached display yet. The authoritative S2r
builder supplies the prepared sources, not disassembled native bytes.
Reassemble the modified prefix and full unit; adjust the three AP20
display entry offsets from the source-assembled prefix length.
"""
import argparse,json,shutil
from pathlib import Path
from hashlib import sha1,sha256
from struct import pack,unpack_from
from active_library import S2R_SHA
from build_m19_s2r_in_memory import build_s2r,assemble_bin,MASTER,ROOT,protected
from build_m19_s1p2l_a_in_memory import headroom,expanded,RESERVE
from compiler_relocation import RBSR,unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect,parse,walk_tokens,token_role_issues

FILES=('M19_S2C_GET_PUBLIC_MC68020.s','M19_S2C_CAPTURE_PIPELINE_MC68020.s',
       'M19_S2C_AGSP_CAPTURE_MC68020.s','M19_S2C_AGSP_REPACK_MC68020.s')
GROUP=207
APIS=('aga sprite','aga sprite off','aga sprite bank free')
OLD_AT=6126

def once(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)

def build_s2c_capture(vasm):
    vasm=Path(vasm).resolve()
    before=protected()
    assert sha256(before[0]).hexdigest()==S2R_SHA
    bank=ROOT/'tests/current/AGSP_S2B_MULTI.ABK'
    bank_before=bank.read_bytes()
    staged={}
    def observer(folder,native,delta):
        master=folder/MASTER
        src=master.read_text(encoding='ascii')
        marker='P2I_CELL_DELTA equ '+str(delta)+'\n'
        assert src.count(marker)==1
        prefix,suffix=src.split(marker)
        probe=folder/'s2c_capture_prefix.s'
        probe.write_text(prefix,encoding='ascii')
        old=assemble_bin(vasm,folder,probe,'s2c_capture_old_prefix.bin')
        assert len(old)==OLD_AT and old==native[:OLD_AT]
        for name in FILES:shutil.copyfile(ROOT/'src/native/m19_s2'/name,folder/name)
        prefix=once(prefix,'include "M19_S1P1I_CAPTURE_PIPELINE_MC68020.s"',
                          'include "M19_S2C_CAPTURE_PIPELINE_MC68020.s"')
        prefix=once(prefix,'include "M19_S1P1I_GET_PUBLIC_MC68020.s"',
                          'include "M19_S2C_GET_PUBLIC_MC68020.s"')
        probe.write_text(prefix,encoding='ascii')
        new=assemble_bin(vasm,folder,probe,'s2c_capture_new_prefix.bin')
        master.write_text(prefix+marker+suffix,encoding='ascii')
        full=assemble_bin(vasm,folder,master,'s2c_capture_full.bin')
        assert full[:len(new)]==new
        assert all(full[len(new)+i:len(new)+i+2]==b'\x60\x00' for i in (0,4,8))
        assert len(full)-len(new)==len(native)-OLD_AT
        staged.update(native=DISPATCH_V2+full,at=len(new),old_at=OLD_AT)
    parent,info=build_s2r(vasm,sprite_source_observer=observer)
    assert parent==before[0] and info['sha256']==S2R_SHA
    tok,parts,title=unpack_ap20(parent)
    new=list(parts);new[GROUP]=staged['native']
    rows=list(walk_tokens(tok))
    stubs=[]
    for j,name in enumerate(APIS):
        row=next(r for r in rows if r['name']==name)
        i=row['function']
        assert parts[i]==RBSR+pack('>HH',GROUP,OLD_AT+4*j)+b'\x4e\x75'
        new[i]=RBSR+pack('>HH',GROUP,staged['at']+4*j)+b'\x4e\x75'
        stubs.append(i)
    assert [i for i,(a,b) in enumerate(zip(parts,new)) if a!=b]==[GROUP]+stubs
    assert len(new)==219 and all(len(p)<=MAX_UNIT_BYTES for p in new)
    links=pc16_displacements(new)
    margin=headroom(new);assert margin>=RESERVE
    nz=title.replace(b'S2r-P1',b'S2c-P1')
    assert nz!=title and len(nz)==len(title)
    image=repack_ap20(parent,tok,new,nz)
    assert unpack_ap20(image)==(tok,new,nz)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([r for r in rows if r['signature']])==105
    assert protected()==before and bank.read_bytes()==bank_before
    return image,dict(info,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        parent_sha=S2R_SHA,unit207=len(new[GROUP]),sprite_at=staged['at'],
        growth=len(new[GROUP])-len(parts[GROUP]),native_sprite=len(new[GROUP])-len(DISPATCH_V2),
        pc16_max=max(map(abs,links.values())),
        reserve_pc16=max(map(abs,pc16_displacements(expanded(new,RESERVE)).values())),
        unit207_pc16_free=margin,reserve_bytes=RESERVE,installable=False,
        attached_display=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    x,meta=build_s2c_capture(a.vasm)
    y,other=build_s2c_capture(a.vasm)
    assert x==y and meta==other
    print('S2C_CAPTURE_EXACT_BUILD_PASS '+json.dumps(meta,sort_keys=True),flush=True)
