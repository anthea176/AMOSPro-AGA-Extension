#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e split-layout candidate built in memory only: Bob Set/Off.

The source-pinned P0d BOBS and AGA native units are NEVER patched. The
P0e object table and source-authored generic bridge are appended to AGA;
the BOBS group gains only a small relay plus the Set/Off AMOS wrappers.

This reduces the signed interpreter branch from reserved stub 0. The
Compiler V2 relocation uses the real AGA Init A5+0x1c8 State anchor,
never a guessed cross-unit address. Not an installed candidate.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from
import sys

from audit_ap20 import inspect,parse,token
from compiler_relocation import GETP,RBSR,unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from build_m19_p0d_bob_blit_in_memory import build as build_p0d
from build_m19_p0e_v2_bridge_in_memory import build as build_old_bridge
from m19_p0e_split_bridge_emit import (
    P0D,AGA_CORE,OBJ,AGA_OFFSETS,AGA_BRIDGE_DELTA,
    emit_split_bobs_public,
)
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

P0D_SHA='bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be'
SPLIT_SHA='ca7dae58934056e4baf7cd3515a02363b05db75ece934afcd721988a952783ec'
OLD_BRIDGE_SHA='f49037880fe75a3314364642336b3e5fb8f9e7854214cc1a23049fbc1becd0de'
OLD_PUBLIC=89
NEW_BOBS=93
NEW_AGA=94
API=(('aga bob',OLD_PUBLIC,1,'I0,0,0,0'),
     ('aga bob off',OLD_PUBLIC+1,1,'I0'))
TITLE=(b'AMOSPro AGA M19 P0e 020 SPLIT BOBS AGA OBJECT SET OFF GATE A ONLY\0'
       b'$VER: AMOSPro_AGA M19 P0e SPLIT BRIDGE IN MEMORY NOT INSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    original,meta=build_p0d()
    if (meta['sha256']!=P0D_SHA or sha256(original).hexdigest()!=P0D_SHA
            or len(original)!=91300):
        raise ValueError('P0d canonical source provenance drift')
    old_bridge,bridge_meta=build_old_bridge()
    if bridge_meta['sha256']!=OLD_BRIDGE_SHA or (
            sha256(old_bridge).hexdigest()!=OLD_BRIDGE_SHA):
        raise ValueError('P0e old bridge provenance drift')
    old_tokens,old_parts,_=unpack_ap20(original)
    if len(old_parts)!=93 or len(old_parts[92])!=56580 or (
            not old_parts[91].startswith(DISPATCH_V2)):
        raise ValueError('P0d native unit layout drift')

    bobs,labels=emit_split_bobs_public()
    if not bobs.startswith(P0D) or not old_parts[91].endswith(P0D):
        raise ValueError('P0d BOBS source was modified')
    suffix=bobs[len(P0D):]
    aga_suffix=OBJ+AGA_CORE
    if not suffix or len(suffix)&1 or len(aga_suffix)&1:
        raise ValueError('odd/empty native source suffix')
    if not all(0<=x<len(AGA_CORE) and x%2==0 for x in AGA_OFFSETS.values()):
        raise ValueError('AGA bridge offsets invalid')
    if AGA_BRIDGE_DELTA!=58462:
        raise ValueError('AGA State native offset/bridge provenance drift')

    stubs=[]
    for i,p in enumerate(old_parts[:OLD_PUBLIC]):
        if p in (b'',GETP):
            stubs.append(p)
            continue
        if p[:2]!=RBSR or p[6:8]!=bytes.fromhex('4e75') or len(p) not in (8,12):
            raise ValueError(f'legacy public stub {i} invalid')
        group,offset=unpack_from('>HH',p,2)
        if group not in (89,90,91,92):
            raise ValueError(('unknown source group',i,group))
        revised=RBSR+pack('>HH',group+2,offset)+p[6:]
        if i==OLD_PUBLIC-1:
            if len(revised)!=8:
                raise ValueError('Bob Blit GetP footer already present')
            revised+=GETP
        stubs.append(revised)
    offset={name:len(old_parts[91])-len(DISPATCH_V2)
            +labels[lab]-len(P0D)
            for name,lab in (
                ('aga bob','public_aga_bob_entry'),
                ('aga bob off','public_aga_bob_off_entry'))}
    assert all(v%2==0 and v<65534 for v in offset.values())
    stubs.append(RBSR+pack('>HH',NEW_BOBS,offset['aga bob'])
                 +bytes.fromhex('4e75')+GETP)
    stubs.append(RBSR+pack('>HH',NEW_BOBS,offset['aga bob off'])
                 +bytes.fromhex('4e75'))
    parts=stubs+old_parts[89:91]+[
        old_parts[91]+suffix,old_parts[92]+aga_suffix]
    if len(parts)!=95 or any(len(p)>65534 or len(p)&1 for p in parts):
        raise ValueError('Compiler V2 group count/size invalid')
    if parts[91:93]!=old_parts[89:91] or not (
            parts[93].startswith(old_parts[91]) and
            parts[94].startswith(old_parts[92])):
        raise ValueError('P0d native prefix/source mutated')
    tokens=old_tokens[:-6]+b''.join(token(*row) for row in API)+bytes(6)
    candidate=repack_ap20(original,tokens,parts,TITLE)
    if unpack_ap20(candidate)!=(tokens,parts,TITLE):
        raise ValueError('HUNK AP20 V2 source roundtrip failed')
    old_audit=inspect(parse(original))
    audit=inspect(parse(candidate))
    if audit['issues'] or audit['tokens'][:-2]!=old_audit['tokens']:
        raise ValueError(('original AP20 API was changed',audit['issues']))
    for expected,got in zip(API,audit['tokens'][-2:]):
        if (got['name'],got['instruction'],got['function'],got['signature'])!=expected:
            raise ValueError(('new AP20 token ABI invalid',got,expected))
    links=interpreter_rbsr_displacements(parts)
    reach=max(map(abs,links.values()))
    if any(i not in links for i in (0,70,88,89,90)) or reach>=32766:
        raise ValueError(f'signed-PC16 interpreter branch invalid: {reach}')
    if 32766-reach<80:
        raise ValueError(f'BOBS relay did not recover useful PC16 budget: {32766-reach}')
    if (len(candidate)!=94508 or len(suffix)!=332 or len(AGA_CORE)!=470
            or reach!=32552 or sha256(candidate).hexdigest()!=SPLIT_SHA):
        raise ValueError('P0e split bridge byte-exact source/PC16 drift')
    assert all(parts[g].startswith(DISPATCH_V2) for g in (91,92,93,94))
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),size=len(candidate),
        previous_sha=P0D_SHA,public_commands=85,ap20_entries=95,
        bobs_relay_bytes=len(suffix),aga_bridge_bytes=len(AGA_CORE),
        object_table_bytes=len(OBJ),bobs_bytes=len(parts[93]),
        aga_bytes=len(parts[94]),interpreter_reach=reach,
        pc16_margin=32766-reach,preexisting_reach=meta['max_rbsr'],
        worst_displacements=sorted(links.items(),key=lambda p:abs(p[1]),reverse=True)[:8],
        tokens=API,public_offsets=offset,relay_labels=labels,
        aga_offsets=AGA_OFFSETS,aga_bridge_delta=AGA_BRIDGE_DELTA,
        gate_a='PENDING',gate_b='NOT TESTED',gate_c='NOT TESTED',
        draw='NOT IMPLEMENTED',close_reset='NOT IMPLEMENTED')


if __name__=='__main__':
    _,m=build()
    print('M19 P0e SPLIT BOBS/AGA SAFE AP20 SOURCE-ONLY', {
        k:v for k,v in m.items() if k!='relay_labels'})
