#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2r-P1: source-only split of two independent AGAPIC entries, then reuse their
old space for the unchanged S2b collective Close/End source. No installed writes.

Reconstruct S2b first using its exact builder. The observers receive ONLY the
authoritative, prepared vasm source tree in the existing temporary directories.
No instruction is generated from a disassembly or copied out of an installed Lib.
"""
import argparse
import json
import subprocess
from hashlib import sha1, sha256
from pathlib import Path
from struct import pack, unpack_from

from audit_ap20 import inspect, parse, token_role_issues, walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from build_m19_s2b_in_memory import build_s2b, MASTER, protected
from build_m19_s2b_close_in_memory import assemble, once, PATCHES, RECLAIM_PATCHES
from build_m19_s1p2l_a_in_memory import headroom, RESERVE
from active_library import S2B_SHA, S2R_SHA, P2DL2B_SHA

ROOT=Path(__file__).resolve().parents[1]
U=142
SPR=207
START,END=0xCEEE,0xDD04
OLD_ROOT=65508
OLD_PREFIX=63334
NEW_GROUP=214
COMMANDS=(('aga bank image info',139,0xCEF2),
          ('aga bank image capture',141,0xD336))
ROOT_SOURCE='p2f_root:\n    dc.l 0,$41475349,$00010010,0\n'
CLOSE_INCLUDE='    opt o-,o1+,o2+,o4+,o5+,o8+,o9+,o10+,o11+,o12+\n    include "M19_S2B_CLOSE_GUARD_MC68020.s"\n    opt o-\n'
BLOCK_START='    dc.b $47,$65,$74,$50\n    include "M19_UNIT142_BLOCK_0CEF2_MC68020.s"\n'
BLOCK_END='    include "M19_UNIT142_P0E_OBJECT_CORE_MC68020.s"\n'

def assemble_bin(vasm,folder,master,name):
    out=folder/name
    subprocess.run([str(vasm),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                    '-quiet','-o',str(out),str(master)],cwd=folder,check=True,timeout=120)
    return out.read_bytes()

def branch_target(unit,offset):
    assert unit[offset:offset+2]==b'\x60\xff'
    return offset+2+unpack_from('>i',unit,offset+2)[0]

def prepare_close(vasm,folder,original):
    tok,parts,title=unpack_ap20(original)
    old=parts[U]
    assert len(old)==65524 and old[-16:]==bytes.fromhex('00000000414753490001001000000000')
    assert old[START:START+4]==GETP and old[0xD336-4:0xD336]==GETP
    assert old[END-8:END]==b'AGAPIC  '
    offsets=[o for o,_ in PATCHES+RECLAIM_PATCHES]
    assert [branch_target(old,o) for o in offsets]==[63334,63390,64306,64330]
    master=folder/'M19_P2D_UNIT142_EDITABLE.s'
    source=master.read_text(encoding='ascii')
    assert source.count(BLOCK_START)==source.count(BLOCK_END)==1
    a,b=source.index(BLOCK_START),source.index(BLOCK_END)
    assert a<b
    block=source[a:b]
    # Link the two routines together with their original literal tables, GetP
    # and Main Rjsr records. An undefined external label is a hard VASM error.
    pic_master=folder/'M19_S2R_AGAPIC_LINK.s'
    pic_master.write_text('; AGA_NATIVE_MIN_CPU: MC68020\n'
        '    include "M19_UNIT142_DISPATCH_V2_MC68020.s"\n'
        'ENTRY_UNIT142_00022:\n'+block,encoding='ascii')
    pic=assemble_bin(vasm,folder,pic_master,'s2r_agapic.bin')
    assert pic[:len(DISPATCH_V2)]==DISPATCH_V2
    # Proof that moving both complete source routines changed no instruction,
    # local branch, literal data or AMOS Main relocation record in that island.
    assert pic[len(DISPATCH_V2):]==old[START:END]

    # Move the same qualified Close/End includes into the vacated space;
    # retain every subsequent P0e/Bob anchor and the L1/L2b tail at its
    # previous offset. Keep the local Sprite root at the new end of UNIT142.
    guard=folder/'M19_S2B_CLOSE_GUARD_MC68020.s'
    guard.write_text(once(guard.read_text(encoding='ascii'),ROOT_SOURCE,''),encoding='ascii')
    source=once(source,block,CLOSE_INCLUDE+
        '    dcb.b $0DD04-(*-UNIT_UNIT142),0\n')
    # CLOSE_INCLUDE now appears twice: remove only the original appended copy.
    assert source.count(CLOSE_INCLUDE)==2 and source.endswith(CLOSE_INCLUDE)
    source=source[:-len(CLOSE_INCLUDE)]+ROOT_SOURCE
    master.write_text(source,encoding='ascii')
    nt,np,nz=unpack_ap20(assemble(vasm,folder))
    assert (nt,nz,len(np))==(tok,title,len(parts))
    assert all(x==y for i,(x,y) in enumerate(zip(parts,np)) if i!=U)
    new=np[U]
    assert len(new)==OLD_PREFIX+16 and new[-16:]==old[-16:]
    # The only changes in the inherited address space are the vacated span
    # and the four established source-level BRA.L Close/End dispatches.
    normalized=bytearray(new[:OLD_PREFIX])
    normalized[START:END]=old[START:END]
    targets=[]
    for offset,prior in PATCHES+RECLAIM_PATCHES:
        normalized[offset:offset+len(prior)]=old[offset:offset+len(prior)]
        targets.append(branch_target(new,offset))
        if len(prior)==8:assert new[offset+6:offset+8]==b'\x4e\x71'
    assert len(set(targets))==4 and all(START<=x<END and x%2==0 for x in targets)
    assert bytes(normalized)==old[:OLD_PREFIX]
    return dict(unit142=new,pic=pic,root=len(new)-16,targets=targets)

def build_s2r(vasm, *, sprite_source_observer=None):
    vasm=Path(vasm).resolve()
    before=protected()
    from verify_m19_s2r_delivery import pre_s2r_pair, verify_library
    historical=pre_s2r_pair(before)
    assert sha256(historical[0]).hexdigest()==S2B_SHA
    assert sha256(before[1]).hexdigest()==P2DL2B_SHA
    campaign=ROOT/'tests/current/AGSP_S2B_MULTI.ABK'
    abk=campaign.read_bytes()
    seen={}
    def close_source(folder,original):
        seen.update(prepare_close(vasm,folder,original))
    def sprite_source(folder,native,delta):
        assert seen['root']==OLD_PREFIX and delta==OLD_ROOT-0x1c2
        master=folder/MASTER
        new_delta=seen['root']-0x1c2
        master.write_text(once(master.read_text(encoding='ascii'),
              'P2I_CELL_DELTA equ '+str(delta)+'\n',
              'P2I_CELL_DELTA equ '+str(new_delta)+'\n'),encoding='ascii')
        split=assemble_bin(vasm,folder,master,'s2r_sprite.bin')
        # Same source, identical code except the relocated root displacement.
        old_operand=b'\x06\x80'+pack('>I',delta)
        new_operand=b'\x06\x80'+pack('>I',new_delta)
        assert native.count(old_operand)==1
        assert split==native.replace(old_operand,new_operand)
        seen['sprite']=DISPATCH_V2+split
        if sprite_source_observer is not None:
            sprite_source_observer(folder,split,new_delta)

    parent,info=build_s2b(vasm,close_source_observer=close_source,
                          sprite_source_observer=sprite_source)
    assert parent==historical[0] and info['sha256']==S2B_SHA
    tok,parts,title=unpack_ap20(parent)
    assert len(parts)==NEW_GROUP and info['root']==OLD_ROOT
    assert parts[U][START:END]==seen['pic'][len(DISPATCH_V2):]
    new=list(parts)
    new[U]=seen['unit142']
    new[SPR]=seen['sprite']
    assert len(new[SPR])==len(parts[SPR])
    # All historical indices remain in place. Only the two moved token
    # entry words are rebound to new local GetP/stub pairs. The four
    # now-unreferenced historical indices become empty AP20 entries.
    new.append(seen['pic'])
    nt=bytearray(tok)
    remapped={}
    rows=list(walk_tokens(tok))
    for name,old_entry,address in COMMANDS:
        row=next(r for r in rows if r['name']==name)
        assert row['function']==old_entry and row['instruction']==1
        assert parts[old_entry-1]==GETP
        assert parts[old_entry]==RBSR+pack('>HH',U,address-len(DISPATCH_V2))+b'\x4e\x75'
        assert [(r['name'],role) for r in rows for role in ('function','instruction')
                if r[role] in (old_entry-1,old_entry)]==[(name,'function')]
        new[old_entry-1:old_entry+1]=[b'',b'']
        new_index=len(new)+1
        new.extend((GETP,RBSR+pack('>HH',NEW_GROUP,address-START)+b'\x4e\x75'))
        nt[row['offset']+2:row['offset']+4]=pack('>H',new_index)
        remapped[name]=new_index
    nt=bytes(nt)
    assert [i for i,(x,y) in enumerate(zip(parts,new)) if x!=y]==[138,139,140,141,U,SPR]
    assert len(new)==219 and len(new[U])==63350 and len(new[NEW_GROUP])<MAX_UNIT_BYTES
    assert all(len(p)<=MAX_UNIT_BYTES for p in new)
    links=pc16_displacements(new)
    assert headroom(new)>=RESERVE
    nz=title.replace(b'S2b-P1',b'S2r-P1')
    assert nz!=title and len(nz)==len(title)
    image=repack_ap20(parent,nt,new,nz)
    result=inspect(parse(image))
    assert not result['issues'] and not token_role_issues(result['tokens'])
    assert [(r['name'],r['signature']) for r in rows]==[(r['name'],r['signature']) for r in result['tokens']]
    assert len([r for r in rows if r['signature']])==105
    assert unpack_ap20(image)==(nt,new,nz)
    verify_library(image,before[1])
    if sha256(before[0]).hexdigest()==S2R_SHA:assert image==before[0]
    assert protected()==before and campaign.read_bytes()==abk
    return image,dict(info,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        parent_sha=S2B_SHA,entries=len(new),unit142=len(new[U]),
        unit142_free=MAX_UNIT_BYTES-len(new[U]),root=seen['root'],
        cell_delta=seen['root']-0x1c2,targets=seen['targets'],
        moved_bytes=END-START,new_group=NEW_GROUP,new_group_bytes=len(new[NEW_GROUP]),
        remapped=remapped,unit207=len(new[SPR]),pc16_max=max(map(abs,links.values())),
        unit207_pc16_free=headroom(new),installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    v=p.parse_args().vasm
    a,info=build_s2r(v)
    b,other=build_s2r(v)
    assert a==b and info==other
    print('S2R_EXACT_BUILD_PASS '+json.dumps(info,sort_keys=True),flush=True)
