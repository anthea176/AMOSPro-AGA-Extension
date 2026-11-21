#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build M19 P2a installable candidate entirely from frozen P1e sources.

Only dist/AMOSPro_AGA.Lib is a candidate. LAST_GOOD P1e is never touched.
New numeric API: Aga Bob Col(A,B,Mode), 0=rect,1=mask, 1/0/-1 return.
"""
from __future__ import annotations
from hashlib import sha256
from struct import pack,pack_into,unpack_from
from active_library import P1E_SHA
from audit_ap20 import inspect,parse,token,walk_tokens
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from compiler_relocation import RBSR,GETP,repack_ap20,unpack_ap20
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p1e_bank_edit_in_memory import build_p1e
from m19_p1e_bank_edit_emit import emit_bank_edit
from m19_p2a_public_bob_col_emit import emit_p2a_public_col

NAME='aga bob col'
SIGNATURE='00,0,0'
TITLE=b'AMOSPro AGA M19 P2a Bob Collision MC68020\0$VER: AMOSPro_AGA M19 P2a\0'
TITLE+=bytes(len(TITLE)%2)


def build_p2a() -> tuple[bytes,dict]:
    original,base=build_p1e()
    if sha256(original).hexdigest()!=P1E_SHA or len(original)!=124444:
        raise ValueError('P1e promoted source/hash drift')
    tokens,parts,title=unpack_ap20(original)
    if len(parts)!=196 or base['commands']!=96:
        raise ValueError('P1e AP20 layout changed')
    group=base['group']
    if group!=188:
        raise ValueError('P1e source group drift')
    old,old_labels=emit_bank_edit(base['context_delta'])
    native,labels=emit_p2a_public_col(base['context_delta'])
    if not parts[group].startswith(DISPATCH_V2) or not parts[group].endswith(old):
        raise ValueError('BOBS native ancestry not P1e')
    prefix=len(parts[group])-len(old)
    expanded=parts[group][:prefix]+native
    if len(expanded)>MAX_UNIT_BYTES or len(expanded)%2:
        raise ValueError('P2a BOBS unit > AP20 65534 bytes')
    # Insert a GETP/function stub immediately BEFORE the native group:
    # avoids signed PC16 overflow to the beginning of the native unit.
    offset=prefix-len(DISPATCH_V2)+labels['p2a_public_bob_col']
    if offset<0 or offset>=len(expanded)-len(DISPATCH_V2):
        raise ValueError('P2a native function target outside unit')
    changed=[]
    for i,p in enumerate(parts):
        if i==group:
            changed.append(GETP)
            changed.append(RBSR+pack('>HH',group+2,offset)+b'\x4e\x75')
        item=expanded if i==group else p
        if item.startswith(RBSR):
            target=unpack_from('>H',item,2)[0]
            if target>=group:
                item=item[:2]+pack('>H',target+2)+item[4:]
        changed.append(item)
    assert len(changed)==198 and changed[group+2]==expanded
    new_tokens=bytearray(tokens[:-6])
    expectation=[]
    for row in walk_tokens(tokens):
        a,b=(row['instruction'],row['function'])
        a+=2*(a>=group);b+=2*(b>=group)
        pack_into('>HH',new_tokens,row['offset'],a,b)
        expectation.append((row['name'],a,b,row['signature']))
    new_tokens.extend(token(NAME,1,group+1,SIGNATURE))
    new_tokens.extend(tokens[-6:])
    new_tokens=bytes(new_tokens)
    result=repack_ap20(original,new_tokens,changed,TITLE)
    if unpack_ap20(result)!=(new_tokens,changed,TITLE):
        raise ValueError('P2a AP20 HUNK roundtrip failed')
    audit=inspect(parse(result))
    if audit['issues']:
        raise ValueError('P2a token/GEtP AP20 issues: '+str(audit['issues']))
    expected=expectation+[(NAME,1,group+1,SIGNATURE)]
    if [(r['name'],r['instruction'],r['function'],r['signature'])
        for r in audit['tokens']]!=expected:
        raise ValueError('P2a token index mapping drift')
    disps=pc16_displacements(changed)
    return result,dict(sha256=sha256(result).hexdigest(),bytes=len(result),
        public_commands=97,entries=len(changed),groups=[
            i for i,p in enumerate(changed) if p.startswith(DISPATCH_V2)],
        bob_group=group+2,code_bytes=len(native),group_bytes=len(expanded),
        public_offset=offset,pc16_max=max(map(abs,disps.values())),
        p1e_sha=P1E_SHA)


if __name__=='__main__':
    b,meta=build_p2a()
    assert build_p2a()[0]==b
    print('P2A_PUBLIC_LIB_CANDIDATE',meta)
