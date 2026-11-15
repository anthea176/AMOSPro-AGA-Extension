#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0b MC68020 exclusive Make/No AGA Bob Mask AP20 source builder.

Uses the frozen R88-derived P0a source constructor and appends exactly two
independent-mask commands into the existing BOBS native unit. Does not change
``dist/``, ``tests/current/``, ``tests/passed/`` or R84 LAST_GOOD. A candidate
is not installable until its exact native CPU Gate A is proven.
"""
from __future__ import annotations
from hashlib import sha256
from struct import pack,unpack_from

from audit_ap20 import inspect,parse,token
from compiler_relocation import unpack_ap20,repack_ap20,RBSR,GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements
from build_m19_p0a_r88_get_in_memory import build as build_get
from m19_p0a_get_bob_emit import emit_get_bob
from m19_p0b_masks_emit import emit_mask_commands

PREVIOUS_SHA='e98a1a17a5e1de579dd100c5cdeba2b8372f62f175274a4412ddeea21034e3b0'
MAKE_INDEX=86
NO_INDEX=87
BOBS_GROUP=90
TITLE=(b'AMOSPro AGA M19 P0b MC68020 MULTI-IMAGE MASK GATE A EXPERIMENT\0'
       b'$VER: AMOSPro_AGA M19 P0b 020 mask commands Gate A ONLY\0')
TITLE+=bytes(len(TITLE)&1)
APIS=(('make aga bob mask',MAKE_INDEX,1,'I0,0'),
      ('no aga bob mask',NO_INDEX,1,'I0'))


def build():
    original,prior_meta=build_get()
    if sha256(original).hexdigest()!=PREVIOUS_SHA or prior_meta['commands']!=80:
        raise ValueError('P0a active source or exact old AP20 candidate changed')
    old_tokens,old_parts,_=unpack_ap20(original)
    if len(old_parts)!=90 or len(old_parts[88])&1 or not old_parts[86].startswith(DISPATCH_V2):
        raise ValueError('unexpected P0a Compiler V2 layout')
    previous,_=emit_get_bob()
    combined,labels=emit_mask_commands()
    if not old_parts[88].endswith(previous) or combined[:len(previous)]!=previous:
        raise ValueError('Get AGA Bob native prefix altered')
    if labels['mask_make_entry']!=len(previous):
        raise ValueError('mask append offset mismatch')
    added=combined[len(previous):]
    make_offset=len(old_parts[88])-len(DISPATCH_V2)
    no_offset=make_offset+labels['mask_no_entry']-labels['mask_make_entry']
    new_bobs=old_parts[88]+added
    if len(new_bobs)>65534 or len(new_bobs)&1:
        raise ValueError('BOBS native unit exceeds unsigned 16-bit Compiler allocation')
    stubs=[]
    for index,original_part in enumerate(old_parts[:MAKE_INDEX]):
        if original_part in (b'',GETP):
            stubs.append(original_part)
            continue
        if (original_part[:2]!=RBSR or len(original_part) not in (8,12)
                or original_part[6:8]!=b'\x4e\x75'):
            raise ValueError(f'P0a previous stub {index} malformed')
        group,offset=unpack_from('>HH',original_part,2)
        if group not in (86,87,88,89):
            raise ValueError(f'unknown previous native unit {group}')
        stub=RBSR+pack('>HH',group+2,offset)+original_part[6:]
        if index==MAKE_INDEX-1:
            if len(stub)!=8:
                raise ValueError('preceding Get AGA Bob has unexpected GetP')
            stub+=GETP
        stubs.append(stub)
    stubs.append(RBSR+pack('>HH',BOBS_GROUP,make_offset)+b'\x4e\x75'+GETP)
    stubs.append(RBSR+pack('>HH',BOBS_GROUP,no_offset)+b'\x4e\x75')
    parts=stubs+list(old_parts[86:88])+[new_bobs]+[old_parts[89]]
    if len(parts)!=92 or any(len(p)>65534 or len(p)&1 for p in parts):
        raise ValueError('AP20 V2 unit count or size invalid')
    tokens=old_tokens[:-6]+b''.join(token(*a) for a in APIS)+bytes(6)
    candidate=repack_ap20(original,tokens,parts,TITLE)
    restored,entries,title=unpack_ap20(candidate)
    if (restored,entries,title)!=(tokens,parts,TITLE):
        raise ValueError('non-exact AP20 HUNK round-trip')
    previous_audit=inspect(parse(original))
    audit=inspect(parse(candidate))
    if audit['issues'] or audit['tokens'][:-2]!=previous_audit['tokens']:
        raise ValueError(('AP20 token regression',audit['issues']))
    for i,api in enumerate(APIS):
        t=audit['tokens'][-2+i]
        if (t['name'],t['instruction'],t['function'],t['signature'])!=api:
            raise ValueError(('AP20 API syntax regression',api,t))
    if not any(p['index']==MAKE_INDEX and p['parameters']==2 and p['getp']
               for p in audit['parameter_checks']):
        raise ValueError('Make AGA Bob Mask GetP delimiter/signature missing')
    if not any(p['index']==NO_INDEX and p['parameters']==1 and p['getp']
               for p in audit['parameter_checks']):
        raise ValueError('No AGA Bob Mask GetP delimiter/signature missing')
    if len([a for a in audit['tokens'] if a['name'].startswith(('aga ','get aga ','make aga ','no aga '))])!=82:
        raise ValueError('unexpected number of AGA commands')
    if parts[88]!=old_parts[86] or parts[89]!=old_parts[87] or parts[91]!=old_parts[89]:
        raise ValueError('previous native units unexpectedly modified')
    links=interpreter_rbsr_displacements(parts)
    if any(k not in links for k in (84,85,MAKE_INDEX,NO_INDEX)) or max(map(abs,links.values()))>=32766:
        raise ValueError('signed interpreter BSR.W range invalid')
    return candidate,dict(base_sha=prior_meta['base_sha'],old_sha=PREVIOUS_SHA,
        sha256=sha256(candidate).hexdigest(),size=len(candidate),commands=82,
        entries=92,bobs_bytes=len(new_bobs),mask_native_bytes=len(added),
        make_index=MAKE_INDEX,no_index=NO_INDEX,
        make_offset=make_offset,no_offset=no_offset,group=BOBS_GROUP,
        max_reach=max(map(abs,links.values())),labels=labels,
        gate_a='NON TESTE',gate_b='NON TESTE',gate_c='NON TESTE')


if __name__=='__main__':
    _,info=build()
    print('M19 P0b source-only candidate', {k:v for k,v in info.items() if k!='labels'})
