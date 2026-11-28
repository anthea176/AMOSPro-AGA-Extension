#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P3 integrated 0.15.0-alpha.1 source candidate. Never installs.
Reconstruct exact P1 and S2c-E1 through their authoritative builders.
Replace only the source-built Sprite and Close/End islands; preserve
all public tokens, fixed legacy offsets, canonical files and LAST_GOOD.
"""
import argparse,json,shutil,tempfile
from pathlib import Path
from hashlib import sha1,sha256
from struct import pack,unpack_from
from build_m19_s2d_capture_in_memory import build_s2d_capture,ROOT,MASTER,protected,assemble_bin,once
from build_m19_s2r_in_memory import assemble,START,END,PATCHES,RECLAIM_PATCHES,branch_target,ROOT_SOURCE,RESERVE
from build_m19_s2b_close_in_memory import compact_root,relax_local
from emit_m19_s2d_ext_close_slice import emit,section
from compiler_relocation import unpack_ap20,repack_ap20,RBSR
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect,parse,token_role_issues,walk_tokens

S2=ROOT/'src/native/m19_s2'
P1_SHA='7741b1945206bf2176ccf1dfed4f8ec8d65c5e64eccd09ae50e5804c53d6da76'
P3_FILES=('M19_S2D_PUBLIC_MC68020.s','M19_S2D_REGISTRY_MC68020.s',
          'M19_S2D_PERSIST_ROOT_MC68020.s','M19_S2D_EXT_PREPARE_MC68020.s',
          'M19_S2D_EXT_BLANK_CHANNELS_MC68020.s','M19_S2D_EXT_ATTACH_V39_MC68020.s',
          'M19_S2D_EXT_RETIRE_MC68020.s','M19_S2D_EXT_FRAME_MC68020.s',
          'M19_S2D_EXT_HIDDEN_SHOW_MC68020.s','M19_S2D_EXT_DROP_STAGE_MC68020.s')

def build_s2d(vasm, *, hotspots=False, clipping=False, priority=False):
    # Both historical paths remain byte-exact; S2f is an opt-in source overlay.
    assert not clipping or hotspots
    assert not priority or clipping
    if priority:
        from m19_s2g_priority_source import transform
    elif clipping:
        from m19_s2f_clip_source import transform
    elif hotspots:
        from m19_s2e_hotspot_source import transform
    else:
        def transform(name,source):return source
    vasm=Path(vasm).resolve()
    before=protected();staged={}
    def close_observer(folder,old,root):
        with tempfile.TemporaryDirectory(prefix='s2d_close_') as tmp:
            work=Path(tmp)/'source';shutil.copytree(folder,work)
            guard=work/'M19_S2B_CLOSE_GUARD_MC68020.s'
            assert 'M19_S2B_RETIRE_PAIR_MC68020.s' in guard.read_text(encoding='ascii')
            # Replace old v5 retirement implementation, not guard or actual
            # CloseScreen BOOL paths. Append compact proven slice after fixed root.
            guard.write_text(once(guard.read_text(encoding='ascii'),
                '    include "M19_S2B_RETIRE_PAIR_MC68020.s"\n',''),encoding='ascii')
            # v6 preclose already drains all records. Do not skip the
            # lifetime header cleanup when the root count is zero.
            reclaim=work/'M19_S2B_CLOSE_RECLAIM_MC68020.s'
            reclaim.write_text(once(reclaim.read_text(encoding='ascii'),
                '    tst.l (a3)\n    beq p2k_close_unlink\n',
                '    tst.l (a3)\n    bne p2k_close_unlink\n'),encoding='ascii')
            if clipping:
                name='M19_S2F_RECEIPT_MC68020.s'
                shutil.copyfile(S2/name,work/name)
            reg=transform(P3_FILES[1],(S2/P3_FILES[1]).read_text(encoding='ascii'))
            (work/'M19_S2B_REGISTRY_MC68020.s').write_text(relax_local(reg),encoding='ascii')
            persist=transform(P3_FILES[2],(S2/P3_FILES[2]).read_text(encoding='ascii'))
            persist=compact_root(once(persist,'    bra.w s2b_p2h_enter\n    bra.w s2b_p2h_leave\n',''))
            (work/'M19_S2B_PERSIST_ROOT_MC68020.s').write_text(relax_local(persist),encoding='ascii')
            master=work/'M19_P2D_UNIT142_EDITABLE.s'
            src=master.read_text(encoding='ascii')
            assert src.endswith(ROOT_SOURCE)
            # Retire/Reclaim helpers need no display code or AP20 dispatch.
            slice_src=emit(compact=True)
            mark='AGSP_S2D_EXT_RETIRE:\n'
            (work/'s2d_close_slice.s').write_text(slice_src[slice_src.index(mark):],encoding='ascii')
            master.write_text(src+'\n    include "s2d_close_slice.s"\n',encoding='ascii')
            _,parts,_=unpack_ap20(assemble(vasm,work))
            new=parts[142]
            assert len(new)<=MAX_UNIT_BYTES and len(new)>len(old)
            assert new[root:root+16]==old[root:root+16]
            assert root==len(old)-16
            norm=bytearray(new[:len(old)])
            norm[START:END]=old[START:END]
            targets=[]
            for off,span in PATCHES+RECLAIM_PATCHES:
                targets.append(branch_target(new,off))
                norm[off:off+len(span)]=old[off:off+len(span)]
                if len(span)==8:assert new[off+6:off+8]==b'\x4e\x71'
            assert len(set(targets))==4 and all(START<=x<END for x in targets)
            assert bytes(norm)==old
            staged.update(close=new,root=root,targets=targets)
    def sprite_observer(folder,wide,delta,at):
        with tempfile.TemporaryDirectory(prefix='s2d_sprite_') as tmp:
            work=Path(tmp)/'source';shutil.copytree(folder,work)
            master=work/MASTER
            src=master.read_text(encoding='ascii')
            marker='P2I_CELL_DELTA equ '+str(delta)+'\n'
            assert src.count(marker)==1 and delta==staged['root']-0x1c2
            prefix=src.split(marker)[0]
            probe=work/'s2d_prefix.s';probe.write_text(prefix,encoding='ascii')
            assert assemble_bin(vasm,work,probe,'prefix.bin')==wide[:at]
            for name in P3_FILES:
                if (hotspots and name in (P3_FILES[0],P3_FILES[1],P3_FILES[2],P3_FILES[7])
                    or clipping and name==P3_FILES[3]):
                    (work/name).write_text(transform(name,(S2/name).read_text(encoding='ascii')),encoding='ascii')
                else:
                    shutil.copyfile(S2/name,work/name)
            if clipping:
                for name in ('M19_S2F_RECEIPT_MC68020.s','M19_S2F_PUBLIC_MC68020.s',
                             'M19_S2F_CLIP_KERNEL_MC68020.s','M19_S2F_CACHE_MC68020.s',
                             'M19_S2F_PREPARE_PLANES_MC68020.s'):
                    shutil.copyfile(S2/name,work/name)
            elif hotspots:
                shutil.copyfile(S2/'M19_S2E_HOTSPOT_MC68020.s',work/'M19_S2E_HOTSPOT_MC68020.s')
            if priority:
                name='M19_S2G_PRIORITY_MC68020.s'
                shutil.copyfile(S2/name,work/name)
            prep=work/P3_FILES[3]
            prep.write_text(once(prep.read_text(encoding='ascii'),
                    '    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"\n',''),encoding='ascii')
            blank=work/P3_FILES[4]
            blank.write_text(once(blank.read_text(encoding='ascii'),
                    '    include "M19_S2D_EXT_ATTACH_V39_MC68020.s"\n',''),encoding='ascii')
            master.write_text(prefix+marker+''.join('    include "'+name+'"\n' for name in
                P3_FILES[:5]+(P3_FILES[6],P3_FILES[9])),encoding='ascii')
            native=assemble_bin(vasm,work,master,'p3_sprite.bin')
            assert native[:at]==wide[:at]
            assert all(native[at+i:at+i+2]==b'\x60\x00' for i in (0,4,8))
            staged.update(sprite=DISPATCH_V2+native,at=at)
    parent,info=build_s2d_capture(vasm,final_source_observer=sprite_observer,
                                 final_close_source_observer=close_observer)
    assert sha256(parent).hexdigest()==P1_SHA
    tok,old,title=unpack_ap20(parent)
    assert len(old)==219 and len(old[142])==63350
    parts=list(old);parts[142]=staged['close'];parts[213]=staged['sprite']
    assert all(len(x)<=MAX_UNIT_BYTES for x in parts)
    assert len(parts[213])+RESERVE<=MAX_UNIT_BYTES
    links=pc16_displacements(parts)
    trial=list(parts);trial[213]+=bytes(RESERVE)
    reserved=pc16_displacements(trial)
    # Preserve AP20 title terminators/padding; use standard version
    # at the actual integrated build, never rename historical artifacts.
    title2=title.replace(b'S2d-P1',b'0.15.0-alpha.4.p1a' if priority else
        (b'0.15.0-alpha.3' if clipping else (b'0.15.0-alpha.2' if hotspots else b'0.15.0-alpha.1')))
    assert title2!=title and not len(title2)&1
    image=repack_ap20(parent,tok,parts,title2)
    assert unpack_ap20(image)==(tok,parts,title2)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([x for x in walk_tokens(tok) if x['signature']])==105
    assert [i for i,(x,y) in enumerate(zip(old,parts)) if x!=y]==[142,213]
    from verify_m19_s2d_delivery import S2D_SHA,verify_library
    from verify_m19_s2e_delivery import pre_s2e_library
    lineage=pre_s2e_library(before[0],before[1])
    if not hotspots and sha256(lineage).hexdigest()==S2D_SHA:
        verify_library(image,before[1])
        assert image==lineage
    assert protected()==before
    return image,dict(info,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        parent_sha=P1_SHA,unit142=len(parts[142]),unit142_free=MAX_UNIT_BYTES-len(parts[142]),
        root=staged['root'],targets=staged['targets'],record_bytes=188 if clipping else (172 if hotspots else 168),
        sprite_unit_bytes=len(parts[213]),sprite_at=staged['at'],
        sprite_group_free=MAX_UNIT_BYTES-len(parts[213]),pc16_max=max(map(abs,links.values())),
        reserve_pc16=max(map(abs,reserved.values())),wide_display=True,installable=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args();image,info=build_s2d(a.vasm)
    print('S2D_P3_LINK_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    again,meta=build_s2d(a.vasm)
    assert image==again and info==meta
    print('S2D_P3_EXACT_BUILD_PASS '+json.dumps(info,sort_keys=True),flush=True)
