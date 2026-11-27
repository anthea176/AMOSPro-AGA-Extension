#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2c-P1c source-built mixed display and Close/End. Never installs."""
import argparse,json,shutil
from hashlib import sha1,sha256
from pathlib import Path
from struct import pack,unpack_from
from audit_ap20 import inspect,parse,walk_tokens,token_role_issues
from compiler_relocation import GETP,RBSR,unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_s2b_close_in_memory import close_registry,compact_root,relax_local
from build_m19_s2r_in_memory import ROOT,MASTER,protected,assemble_bin,assemble,START,END,PATCHES,RECLAIM_PATCHES,branch_target,RESERVE
from build_m19_s2c_capture_in_memory import build_s2c_capture,once
from build_m19_s2c_registry_cpu import prepare_lifecycle,S2,NAMES

P1A_SHA='bafb14e768ce43824cc2512493c14c0d34bbbdeb18c57fc91e3634784475423e'
OLD_GROUP,SPR=207,213
APIS=('aga sprite','aga sprite off','aga sprite bank free')
MAP={209:208,211:210,213:212}
COMMON=dict(zip(('M19_S2B_PERSIST_ROOT_MC68020.s','M19_S2B_REGISTRY_MC68020.s',
                 'M19_S2B_RETIRE_PAIR_MC68020.s','M19_S2B_ALLOCATE_MC68020.s'),NAMES))

def build_s2c(vasm, *, diagnostic=False):
    vasm=Path(vasm).resolve()
    before=protected()
    staged={}
    def close_observer(folder,old,root):
        for dst,src in COMMON.items():
            if 'ALLOCATE' in dst:continue
            s=(S2/src).read_text(encoding='ascii')
            if 'REGISTRY' in dst:s=close_registry(s)
            if 'PERSIST' in dst:s=compact_root(once(s,'    bra.w s2b_p2h_enter\n    bra.w s2b_p2h_leave\n',''))
            (folder/dst).write_text(relax_local(s),encoding='ascii')
        _,parts,_=unpack_ap20(assemble(vasm,folder))
        new=parts[142]
        assert len(new)==len(old)==63350 and new[END:]==old[END:]
        normalized=bytearray(new)
        normalized[START:END]=old[START:END]
        targets=[]
        for off,span in PATCHES+RECLAIM_PATCHES:
            targets.append(branch_target(new,off))
            assert START<=targets[-1]<END
            if len(span)==8:assert new[off+6:off+8]==b'\x4e\x71'
            normalized[off:off+len(span)]=old[off:off+len(span)]
        assert bytes(normalized)==old and len(set(targets))==4
        staged.update(close=new,targets=targets,root=root)
    def sprite_observer(folder,native,delta,at):
        assert delta==staged['root']-0x1c2
        for dst,src in COMMON.items():shutil.copyfile(S2/src,folder/dst)
        shutil.copyfile(S2/'M19_S2C_PUBLIC_MC68020.s',folder/'M19_S2B_PUBLIC_MC68020.s')
        p=folder/'M19_S2C_AGSP_CHIP_PAIR_MC68020.s'
        p.write_text(once((S2/p.name).read_text(encoding='ascii'),
                     '    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"',''),encoding='ascii')
        prepare_lifecycle(folder)
        p=folder/'s2c_v5_frame.s'
        s=p.read_text(encoding='ascii')
        # Public adapter receives AMOS Main A5 and public stack A3.
        # The standalone P0d and P1b ABIs remain unchanged.
        s=once(s,'CF_BYTES  equ 28','CF_AMOS   equ 28\nCF_PUBLIC equ 32\nCF_BYTES  equ 36')
        s=once(s,'    move.l d0,CF_LEN(sp)\n','    move.l d0,CF_LEN(sp)\n    move.l a5,CF_AMOS(sp)\n    move.l a3,CF_PUBLIC(sp)\n')
        s=once(s,'    cmp.l CF_ID(sp),d1\n    bne.w s2c_f_source_bad\n',
            '    cmp.l CF_ID(sp),d1\n    bne.w s2c_f_source_bad\n'
            '    movem.l d1-d7/a0-a6,-(sp)\n'
            '    movea.l CF_AMOS+56(sp),a5\n    movea.l CF_PUBLIC+56(sp),a2\n'
            '    bsr.w s2a_expect\n    movem.l (sp)+,d1-d7/a0-a6\n'
            '    tst.l d0\n    beq.w s2c_f_source_bad\n')
        s=once(s,'    bset #7,3(a0)\n','    bset #7,3(a0)\n'
            '    movea.l CF_PUBLIC(sp),a2\n    move.l I_X(a2),d2\n    move.l I_Y(a2),d3\n')
        p.write_text(s,encoding='ascii')
        if diagnostic:
            from m19_s2c_diagnostic_emit import instrument
            public=folder/'M19_S2B_PUBLIC_MC68020.s'
            lifecycle=folder/'s2c_v5_lifecycle.s'
            frame=p
            outputs=instrument(public.read_text(encoding='ascii'),
                               lifecycle.read_text(encoding='ascii'),
                               frame.read_text(encoding='ascii'))
            for path,source in zip((public,lifecycle,frame),outputs):
                path.write_text(source,encoding='ascii')
        master=folder/MASTER
        with master.open('a',encoding='ascii') as out:
            out.write('\n    include "M19_S2C_AGSP_CHIP_PAIR_MC68020.s"\n    include "s2c_v5_lifecycle.s"\n')
        full=assemble_bin(vasm,folder,master,'s2c_p1c_sprite.bin')
        assert full[:at]==native[:at]
        assert all(full[at+i:at+i+2]==b'\x60\x00' for i in (0,4,8))
        staged.update(sprite=DISPATCH_V2+full,at=at)
    parent,info=build_s2c_capture(vasm,sprite_source_observer=sprite_observer,
                                    close_source_observer=close_observer)
    assert sha256(parent).hexdigest()==P1A_SHA
    tok,parts,title=unpack_ap20(parent)
    new=list(parts)
    new[142]=staged['close']
    # All five incoming RBSR callers precede the island. No new absolute
    # code addresses or cross-unit mutable selection. The old positions
    # 208..213 are exactly three GetP/RBSR pairs, not shared tokens.
    assert len(parts)==219
    new[207:214]=parts[208:214]+[staged['sprite']]
    for old_i,new_i in ((204,204),(206,206),*MAP.items()):
        stub=parts[old_i]
        assert parts[old_i-1]==GETP and len(stub)==8 and stub[:2]==RBSR
        g,off=unpack_from('>HH',stub,2)
        assert g==OLD_GROUP and stub[6:]==b'\x4e\x75'
        new[new_i]=RBSR+pack('>HH',SPR,off)+stub[6:]
        assert new[new_i-1]==GETP
    nt=bytearray(tok);rows=list(walk_tokens(tok))
    for name,old_i in zip(APIS,MAP):
        row=next(x for x in rows if x['name']==name)
        assert row['function']==old_i and row['instruction']==1
        nt[row['offset']+2:row['offset']+4]=pack('>H',MAP[old_i])
    nt=bytes(nt)
    assert len(new)==len(parts) and all(new[i]==parts[i] for i in range(len(parts))
        if i not in (142,204,206,207,208,209,210,211,212,213))
    assert all(len(p)<=MAX_UNIT_BYTES for p in new)
    links=pc16_displacements(new)
    trial=list(new);trial[SPR]+=bytes(RESERVE)
    assert len(trial[SPR])<=MAX_UNIT_BYTES
    reserve_links=pc16_displacements(trial)
    nz=title.replace(b'S2c-P1',b'S2c-D1' if diagnostic else b'S2c-P2')
    assert nz!=title and len(nz)==len(title)
    image=repack_ap20(parent,nt,new,nz)
    assert unpack_ap20(image)==(nt,new,nz)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert [(r['name'],r['signature']) for r in rows]==[(r['name'],r['signature']) for r in audit['tokens']]
    assert len([r for r in rows if r['signature']])==105
    from verify_m19_s2c_delivery import S2C_SHA, verify_library
    if sha256(before[0]).hexdigest()==S2C_SHA:
        if diagnostic:
            verify_library(before[0],before[1])
            ct,cp,cz=unpack_ap20(before[0])
            assert nt==ct and nz==cz.replace(b'S2c-P2',b'S2c-D1')
            assert len(cp)==len(new)
            assert [i for i,(a,b) in enumerate(zip(cp,new)) if a!=b]==[SPR]
        else:
            verify_library(image,before[1])
            assert image==before[0]
    assert protected()==before
    return image,dict(info,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        parent_sha=P1A_SHA,targets=staged['targets'],sprite_group=SPR,record_bytes=72,
        unit207=len(new[207]),sprite_unit_bytes=len(new[SPR]),
        sprite_group_free=MAX_UNIT_BYTES-len(new[SPR]),native_sprite=len(new[SPR])-len(DISPATCH_V2),
        pc16_max=max(map(abs,links.values())),reserve_pc16=max(map(abs,reserve_links.values())),
        unit207_pc16_free=None,attached_display=True,installable=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    image,meta=build_s2c(a.vasm)
    again,m2=build_s2c(a.vasm)
    assert image==again and meta==m2
    print('S2C_P1C_EXACT_BUILD_PASS '+json.dumps(meta,sort_keys=True),flush=True)
