#!/usr/bin/env python3
"""R88-only experimental M19 P0a full native Get AGA Bob AP20 in MEMORY.

Never modifies the active dist/AMOSPro_AGA.Lib, tests/current, R84 LAST_GOOD
or any historical R89/R90 artifacts. The base is SHA-verified by the preceding
Aga Bob Bank R88 builder. No WinUAE / real Compiler validation is claimed.
"""
from __future__ import annotations
from hashlib import sha256
from struct import pack,unpack_from

from audit_ap20 import inspect,parse,token
from compiler_relocation import unpack_ap20,repack_ap20,RBSR,GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from build_m19_p0a_r88_bank_in_memory import build as build_bank
from m19_p0a_bank_select_emit import emit_bank_select
from m19_p0a_get_bob_emit import emit_get_bob
from ap20_v3_r82_split import interpreter_rbsr_displacements

PUBLIC=85
BANK_PUBLIC=84
OLD_GROUP_START=85
BOBS_GROUP=88
API=('get aga bob',PUBLIC,1,'I0,0,0,0,0')
TITLE=(b'AMOSPro AGA M19 P0a R88-base MULTI-IMAGE GET AGA BOB EXPERIMENT\0'
       b'$VER: AMOSPro_AGA M19 P0a from R88 0.13.33 GATE A ONLY\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    original,oldinfo=build_bank() # checks R88/R84 SHA and old 79 tokens
    orig_tokens,orig_parts,_=unpack_ap20(original)
    if len(orig_parts)!=89 or len(orig_parts[87])!=7038+len(emit_bank_select()[0]):
        raise ValueError('R88-derived Bank Select layout mismatch')
    select,_=emit_bank_select()
    combined,labels=emit_get_bob()
    if combined[:len(select)]!=select or labels['get_entry']!=len(select):
        raise ValueError('native Bank Select prefix was modified')
    if not orig_parts[87].endswith(select):
        raise ValueError('Bank Select not at end of R88 BOBS group')
    new_capture=combined[len(select):]
    entry=len(orig_parts[87])-len(DISPATCH_V2)
    if entry!=7004+len(select) or entry+len(new_capture)>65534:
        raise ValueError('BOBS append offset or Compiler unit size')
    new_bobs=orig_parts[87]+new_capture
    stubs=[]
    for index,original_part in enumerate(orig_parts[:OLD_GROUP_START]):
        if original_part in (b'',GETP):
            stubs.append(original_part)
            continue
        if not (original_part[:2]==RBSR and len(original_part) in (8,12)
                and original_part[6:8]==b'\x4e\x75'):
            raise ValueError(f'unknown R88-derived stub {index}')
        group,offset=unpack_from('>HH',original_part,2)
        if group not in (85,86,87,88):
            raise ValueError(f'unknown native group {group}')
        stub=RBSR+pack('>HH',group+1,offset)+original_part[6:]
        if index==BANK_PUBLIC:
            if len(stub)!=8:
                raise ValueError('Bank Select already has GetP')
            stub+=GETP
        stubs.append(stub)
    stubs.append(RBSR+pack('>HH',BOBS_GROUP,entry)+b'\x4e\x75')
    parts=stubs+list(orig_parts[85:87])+[new_bobs]+[orig_parts[88]]
    if len(parts)!=90 or any(len(p)>65534 or len(p)&1 for p in parts):
        raise ValueError('Compiler V2 part length')
    tokens=orig_tokens[:-6]+token(*API)+bytes(6)
    candidate=repack_ap20(original,tokens,parts,TITLE)
    unpacked_tokens,unpacked_parts,title=unpack_ap20(candidate)
    if (unpacked_tokens,unpacked_parts,title)!=(tokens,parts,TITLE):
        raise ValueError('AP20 rebuild is not lossless')
    oldaudit=inspect(parse(original))
    audit=inspect(parse(candidate))
    if audit['issues'] or audit['tokens'][:-1]!=oldaudit['tokens']:
        raise ValueError(('previous AP20 token regression',audit['issues']))
    last=audit['tokens'][-1]
    if (last['name'],last['instruction'],last['function'],last['signature'])!=API:
        raise ValueError('Get AGA Bob ABI/grammar mismatch')
    if not any(p['index']==PUBLIC and p['parameters']==5 and p['getp']
               for p in audit['parameter_checks']):
        raise ValueError('Get AGA Bob five numeric arguments lack GetP')
    if not any(p['index']==BANK_PUBLIC and p['parameters']==1 and p['getp']
               for p in audit['parameter_checks']):
        raise ValueError('preceding Bank Select GetP lost')
    if len([x for x in audit['tokens'] if x['name'].startswith(('aga ','get aga '))])!=80:
        raise ValueError('unexpected M19 AGA command count')
    # The existing R88 C2P, IFF and AGA native units remain byte-identical.
    if (parts[86],parts[87],parts[88],parts[89])!=(orig_parts[85],orig_parts[86],new_bobs,orig_parts[88]):
        raise ValueError('native unit mutation')
    links=interpreter_rbsr_displacements(parts)
    if PUBLIC not in links or BANK_PUBLIC not in links or max(map(abs,links.values()))>=32766:
        raise ValueError('interpreter BSR.W out of signed reach')
    return candidate,dict(base_sha=oldinfo['base_sha'],sha256=sha256(candidate).hexdigest(),
        size=len(candidate),commands=80,entries=90,
        bobs_bytes=len(new_bobs),capture_bytes=len(new_capture),capture_offset=entry,
        public_index=PUBLIC,group=BOBS_GROUP,reach=max(map(abs,links.values())),
        gate_a='NON TESTE',gate_b='NON TESTE',gate_c='NON TESTE',labels=labels)


if __name__=='__main__':
    binary,info=build()
    print('M19 P0a R88-only GET AGA BOB in-memory AP20',
          {k:v for k,v in info.items() if k!='labels'})
