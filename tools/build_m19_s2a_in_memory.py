#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-only S2a, rebuild exact P2m UNIT207, preserve every other unit.
No binary disassembly, no writes to dist or tests/current.
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from hashlib import sha1, sha256
from pathlib import Path
from audit_ap20 import inspect, parse, token_role_issues, walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from compiler_relocation import repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from build_m19_s1p2k_close_in_memory import SRC, ROOT
from build_m19_s1p2k_in_memory import MASTER
from build_m19_s1p2l_a_in_memory import protected, expanded, headroom, RESERVE
from verify_m19_s1p2m_delivery import verify_library, verify_asc, P2M_SHA, ABK_SHA

S2=ROOT/'src/native/m19_s2'
PUBLIC='M19_S1P2M_PUBLIC_MC68020.s'
CHANGE='M19_S2A_FRAME_CHANGE_MC68020.s'
STAGE='M19_S2A_FRAME_STAGE_MC68020.s'
PARENT_INCLUDES=(PUBLIC,'M19_S1P2A_CHIP_PREPARE_MC68020.s',
                 'M19_S1P2M_RETIRE_MC68020.s','p2i_reclaim_core.s',
                 'M19_S1P2M_PERSIST_ROOT_MC68020.s')

def once(source,old,new):
    assert source.count(old)==1, ('source anchor',old)
    return source.replace(old,new)

def public_source(source):
    source=once(source,'I_FRAME equ 140\n', '''S_SCRATCH equ 140
S_LENGTH equ 144
S_OLD equ 148
S_NEW equ 152
S_VIEW equ 156
S_CI equ 160
S_TABLE equ 164
S_LOF equ 168
S_SHF equ 172
I_FRAME equ 176
''')
    source=once(source,'''    move.l I_IMAGE(a2),d0
    cmp.l 36(a4),d0
    bne.w p2i_end
    ; An active immutable image can move. Retired/pending records cannot.
    move.l #-140,I_PHASE(a2)
    cmpi.l #15,12(a4)
    bne.w p2i_end
''','''    ; Only active, certain records may move or change frames.
    move.l #-140,I_PHASE(a2)
    cmpi.l #15,12(a4)
    bne.w p2i_end
    tst.l 36(a4)
    beq.w p2i_end
    move.l I_IMAGE(a2),d0
    cmp.l 36(a4),d0
    bne.w s2a_change
''')
    source=once(source,'''    movea.l sp,a2
p2i_move:
''','''    movea.l sp,a2
    ; Initial publication must still point at slot A, never blank B.
    move.l #-160,I_PHASE(a2)
    movea.l I_CHIP(a2),a1
    lea 48(a1),a0
    move.l a0,d0
    cmp.l (a1),d0
    bne.w p2i_retire_failed
p2i_move:
''')
    return once(source,'''    lea 48(a1),a0
    move.l a0,d0
    cmp.l (a1),d0
    bne.w p2i_no
    moveq #1,d0
    rts
p2i_no:
''','''    lea 48(a1),a0
    move.l a0,d0
    cmp.l (a1),d0
    beq.s s2a_active_ok
    move.l a1,d0
    add.l 44(a1),d0
    bcs.w p2i_no
    cmp.l (a1),d0
    bne.w p2i_no
s2a_active_ok:
    moveq #1,d0
    rts
p2i_no:
''')

def assemble(vasm,delta,variant):
    with tempfile.TemporaryDirectory(prefix='aga-s2a-') as td:
        folder=Path(td)/'native'
        shutil.copytree(SRC,folder)
        p=folder/'M19_S1P2A_CHIP_PREPARE_MC68020.s'
        p.write_text(once(p.read_text(encoding='ascii'),
                     '    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"',''),encoding='ascii')
        s=(folder/'M19_S1P2M_RECLAIM_MC68020.s').read_text(encoding='ascii')
        (folder/'p2i_reclaim_core.s').write_text(s[s.index('AGSP_P2G_RECLAIM:'):],encoding='ascii')
        if variant:
            p=folder/PUBLIC
            p.write_text(public_source(p.read_text(encoding='ascii')),encoding='ascii')
            for name in (CHANGE,STAGE):
                shutil.copyfile(S2/name,folder/name)
        with (folder/MASTER).open('a',encoding='ascii') as f:
            f.write(f'\nP2I_CELL_DELTA equ {delta}\n')
            for name in PARENT_INCLUDES+((CHANGE,STAGE) if variant else ()):
                f.write('    include "'+name+'"\n')
        out=Path(td)/'native.bin'
        subprocess.run([str(vasm),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                        '-quiet','-o',str(out),str(folder/MASTER)],cwd=folder,
                       check=True,timeout=120)
        return out.read_bytes()

def build_s2a(vasm):
    vasm=Path(vasm).resolve()
    before=protected()
    parent,good,asc,abk=before
    assert sha256(parent).hexdigest()==P2M_SHA
    verify_library(parent,good)
    verify_asc(asc)
    assert sha256(abk).hexdigest()==ABK_SHA
    tok,old,title=unpack_ap20(parent)
    root=65408
    delta=root-0x1c2
    at=6126
    assert len(old[142])==65424 and len(old[207])==10380
    assert old[142][root:]==bytes.fromhex('00000000414753490001001000000000')
    # Authenticate the original native source assembly, not just its prefix.
    assert DISPATCH_V2+assemble(vasm,delta,False)==old[207]
    native=assemble(vasm,delta,True)
    assert native[:at]==old[207][len(DISPATCH_V2):len(DISPATCH_V2)+at]
    assert all(native[at+i:at+i+2]==bytes.fromhex('6000') for i in (0,4,8))
    parts=list(old)
    parts[207]=DISPATCH_V2+native
    assert parts[207]!=old[207] and len(parts[207])<=MAX_UNIT_BYTES
    assert all(parts[i]==old[i] for i in range(214) if i!=207)
    links=pc16_displacements(parts)
    assert headroom(parts)>=RESERVE
    newtitle=title.replace(b'S1-P2m',b'S2a-P1')
    assert newtitle!=title and len(newtitle)==len(title)
    out=repack_ap20(parent,tok,parts,newtitle)
    assert unpack_ap20(out)==(tok,parts,newtitle)
    audit=inspect(parse(out))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([x for x in walk_tokens(tok) if x['signature']])==105
    assert protected()==before
    return out,dict(parent_sha=P2M_SHA,sha256=sha256(out).hexdigest(),
        git_blob=sha1(f'blob {len(out)}'.encode()+b'\0'+out).hexdigest(),
        bytes=len(out),commands=105,entries=214,root=root,cell_delta=delta,
        sprite_at=at,native_sprite=len(native),unit142=len(parts[142]),
        unit142_free=MAX_UNIT_BYTES-len(parts[142]),unit207=len(parts[207]),
        pc16_max=max(map(abs,links.values())),unit207_pc16_free=headroom(parts),
        reserve_bytes=RESERVE,reserve_pc16=max(map(abs,pc16_displacements(expanded(parts,RESERVE)).values())),
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    _,meta=build_s2a(p.parse_args().vasm)
    print('S2A_BUILT '+json.dumps(meta,sort_keys=True),flush=True)
