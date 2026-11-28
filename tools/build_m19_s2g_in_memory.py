#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Private S2g-P1a integration, byte-exact S2f parent, no installation.

Build a five-integer entry and a test-only GetP/Rbsr stub. Do not declare
an overloaded AMOS token until actual token grammar is verified. The
extra stub sits BEFORE the Sprite island to preserve the PC16 reserve.
"""
import argparse
import json
from hashlib import sha1, sha256
from pathlib import Path
from struct import pack, unpack_from
from audit_ap20 import inspect, parse, token_role_issues, walk_tokens
from compiler_relocation import GETP, RBSR, unpack_ap20, repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_s2f_in_memory import build_s2f, protected
from build_m19_s2d_in_memory import build_s2d
from verify_m19_s2f_delivery import S2F_SHA

OLD_GROUP=213
NEW_GROUP=215
PRIVATE_ENTRY=214
RTS=bytes.fromhex('4e75')
RESERVE=16384

def shifted(index):
    return index+2 if index>=OLD_GROUP else index

def build_s2g(vasm):
    before=protected()
    parent,old_info=build_s2f(vasm)
    assert sha256(parent).hexdigest()==S2F_SHA
    from verify_m19_s2g_delivery import pre_s2g_pair
    assert parent==pre_s2g_pair(before)[0]  # exact historical S2f after activation
    tok,old,title=unpack_ap20(parent)
    intermediate,info=build_s2d(vasm,hotspots=True,clipping=True,priority=True)
    nt,parts,newtitle=unpack_ap20(intermediate)
    assert nt==tok and len(parts)==len(old)==219
    assert newtitle==title.replace(b'0.15.0-alpha.3',b'0.15.0-alpha.4.p1a')
    assert [i for i,(a,b) in enumerate(zip(old,parts)) if a!=b]==[OLD_GROUP]
    assert info['root']==old_info['root'] and info['sprite_at']==old_info['sprite_at']
    assert info['record_bytes']==188 and parts[142]==old[142]
    at=info['sprite_at']
    start=len(DISPATCH_V2)+at
    assert parts[OLD_GROUP][:start]==old[OLD_GROUP][:start]
    offset=at+12
    assert parts[OLD_GROUP][len(DISPATCH_V2)+offset:len(DISPATCH_V2)+offset+2]==b'\x60\x00'
    # Insert adjacent to native unit: no native source is derived from binary.
    # Only existing public Rbsr indices and token numeric references can shift.
    updated=[]
    for part in parts:
        if part.startswith(RBSR):
            group,off=unpack_from('>HH',part,2)
            part=RBSR+pack('>HH',shifted(group),off)+part[6:]
        updated.append(part)
    updated[OLD_GROUP:OLD_GROUP]=[
        GETP,RBSR+pack('>HH',NEW_GROUP,offset)+RTS]
    tokens=bytearray(tok)
    rows=list(walk_tokens(tok))
    for row in rows:
        for i,role in enumerate(('instruction','function')):
            pos=row['offset']+i*2
            tokens[pos:pos+2]=pack('>H',shifted(row[role]))
    tokens=bytes(tokens)
    after=list(walk_tokens(tokens))
    assert len(after)==len(rows)
    assert [(r['name'],r['signature']) for r in after]==[
        (r['name'],r['signature']) for r in rows]
    assert all(r['function']!=PRIVATE_ENTRY and r['instruction']!=PRIVATE_ENTRY
               for r in after), 'private entry must not be tokenized'
    assert updated[NEW_GROUP]==parts[OLD_GROUP]
    assert updated[142]==old[142]
    assert len(updated)==221 and updated[PRIVATE_ENTRY-1]==GETP
    assert all(len(p)<=MAX_UNIT_BYTES for p in updated)
    links=pc16_displacements(updated)
    trial=list(updated)
    trial[NEW_GROUP]+=bytes(RESERVE)
    assert len(trial[NEW_GROUP])<=MAX_UNIT_BYTES
    reserved=pc16_displacements(trial)
    image=repack_ap20(parent,tokens,updated,newtitle)
    assert unpack_ap20(image)==(tokens,updated,newtitle)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert sum(bool(r['signature']) for r in after)==105
    assert protected()==before
    return image,dict(info,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        parent_sha=S2F_SHA,commands=105,entries=len(updated),sprite_group=NEW_GROUP,
        private_entry=PRIVATE_ENTRY,private_offset=offset,
        pc16_max=max(map(abs,links.values())),
        reserve_pc16=max(map(abs,reserved.values())),reserve_bytes=RESERVE,
        registry_bytes=672,registry_version=8,public_overload=False,
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    a=p.parse_args()
    data,info=build_s2g(a.vasm)
    second,meta=build_s2g(a.vasm)
    assert data==second and info==meta
    print('S2G_P1A_PRIVATE_EXACT_BUILD_PASS '+json.dumps(info,sort_keys=True),flush=True)
