#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1a numeric getters, append-only to fifth AP20 B8 group, IN MEMORY.

The exact promoted P0 candidate is the source ancestor; no P0 unit changes.
The new public stubs reach native group 181 with signed PC16. The native
read bridge resolves the separate BOBS group via P0 validated callbacks.
No new .Lib or active ASC is written.
"""
from __future__ import annotations
from hashlib import sha256
from struct import pack,unpack_from

from audit_ap20 import inspect,parse,token,walk_tokens
from compiler_relocation import RBSR,GETP,unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_s1_bank_free_in_memory import build_bank_free
from m19_b8_s1_bank_free_bridge_emit import emit_b8_s1_bank_free_bridge
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters,INVALID

P0_SHA='f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d'
BOBS=177
FIFTH=181
BASE_ENTRIES=185
P1A_SHA='165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a'
P1A_BYTES=118816
P1A_NATIVE_SHA='9e9785488bf7fcf5b9062e38439ebdf4e1e032ee226df0a97850df95a386512e'
API=(('aga x bob','x'),('aga y bob','y'),('aga i bob','image'))
TITLE=(b'AMOSPro AGA M19 P1a Bob X/Y/I getters MC68020 SOURCE ONLY\0'
       b'$VER: AMOSPro_AGA M19 P1a Gate A UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build_p1a() -> tuple[bytes,dict]:
    old,meta=build_bank_free()
    if (len(old)!=117896 or sha256(old).hexdigest()!=P0_SHA
            or meta['sha256']!=P0_SHA or meta['pc16_max']!=31092):
        raise ValueError('Promoted P0 Bank Free deterministic source drift')
    tokens,parts,_=unpack_ap20(old)
    if (len(parts)!=BASE_ENTRIES or
            any(not parts[i].startswith(DISPATCH_V2) for i in (BOBS,FIFTH))):
        raise ValueError('P0 five-group AP20 base missing')
    previous,_=emit_b8_s1_bank_free_bridge()
    native,labels=emit_m19_p1a_getters()
    if not native.startswith(previous) or not parts[FIFTH].endswith(previous):
        raise ValueError('P0 fifth source is not byte-exact')
    before=inspect(parse(old))
    if before['issues']:
        raise ValueError('P0 AP20 source already has token violations')
    if any(row['name'] in {name for name,_ in API}
           for row in walk_tokens(tokens)):
        raise ValueError('P1a token already exposed')
    entries=list(parts)
    origin=len(parts[FIFTH])-len(DISPATCH_V2)-len(previous)
    entries[FIFTH]+=native[len(previous):]
    if (len(entries[FIFTH])>=MAX_UNIT_BYTES or
            not entries[FIFTH].startswith(parts[FIFTH]) or
            entries[BOBS]!=parts[BOBS]):
        raise ValueError('P1a fifth source overflowed or damaged BOBS')
    # AMOS GetP is stored directly before each parameterized function.
    if not entries[184].endswith(bytes.fromhex('4e75')):
        raise ValueError('P0 Bank Free tail changed')
    entries[184]+=GETP
    targets={}
    new_tokens=tokens[:-6]
    for i,(name,field) in enumerate(API):
        index=BASE_ENTRIES+i
        offset=origin+labels['p1a_get_'+field+'_entry']
        if offset<0 or offset&1 or offset>=len(entries[FIFTH])-len(DISPATCH_V2):
            raise ValueError('P1a function native target outside fifth group')
        stub=RBSR+pack('>HH',FIFTH,offset)+b'\x4e\x75'
        if i<2:
            stub+=GETP
        entries.append(stub)
        new_tokens+=token(name,1,index,'00')
        targets[name]=(FIFTH,offset,index)
    new_tokens+=tokens[-6:]
    image=repack_ap20(old,new_tokens,entries,TITLE)
    if unpack_ap20(image)!=(new_tokens,entries,TITLE):
        raise ValueError('AP20 candidate roundtrip mismatch')
    after=inspect(parse(image))
    if after['issues'] or after['tokens'][:-3]!=before['tokens']:
        raise ValueError(('P1a token/API regression',after['issues']))
    for i,((name,_),actual) in enumerate(zip(API,after['tokens'][-3:])):
        if (actual['name'],actual['instruction'],
            actual['function'],actual['signature'])!=(name,1,BASE_ENTRIES+i,'00'):
            raise ValueError('P1a not an AMOS 1-argument numeric function')
    if (len(entries)!=188 or entries[184]!=parts[184]+GETP
            or not entries[185].endswith(GETP)
            or not entries[186].endswith(GETP)
            or entries[187][-2:]!=b'\x4e\x75'):
        raise ValueError('GetP placement and RTS mismatch')
    if any(entries[i]!=parts[i] for i in range(185) if i not in (FIFTH,184)):
        raise ValueError('P0 original AP20 section changed')
    for name,(group,off,index) in targets.items():
        if (unpack_from('>HH',entries[index],2)!=(group,off)
                or not entries[index].startswith(RBSR)):
            raise ValueError('Native AP20 RBSR target invalid: '+name)
    groups=[i for i,p in enumerate(entries) if p.startswith(DISPATCH_V2)]
    spans=pc16_displacements(entries)
    pc16=max(map(abs,spans.values()))
    if groups!=[142,153,156,177,181] or pc16>=32766:
        raise ValueError('P1a Compiler/interpreter native group PC16 overflow')
    if (len(image)!=P1A_BYTES or sha256(image).hexdigest()!=P1A_SHA
            or sha256(native).hexdigest()!=P1A_NATIVE_SHA):
        raise ValueError('Exact M19 P1a Gate A candidate/source hash drift')
    commands=[x for x in after['tokens']
              if x['name'].startswith(('aga ','get aga ','make aga ','no aga '))]
    if len(commands)!=92:
        raise ValueError('P1a public command count 89+3 changed')
    return image,dict(sha256=sha256(image).hexdigest(),bytes=len(image),
        p0_sha=P0_SHA,predecessor_sha=meta['sha256'],
        public_commands=92,ap20_entries=188,
        native_groups=groups,pc16_max=pc16,
        appended_native_bytes=len(native)-len(previous),
        source_native_sha=sha256(native).hexdigest(),
        targets=targets,refusal_sentinel=INVALID,
        source_only=True,installed=False,gate_a='TESTS REQUIRED',
        gate_b='NOT TESTED',gate_c='NOT TESTED',gate_d='NOT TESTED')


if __name__=='__main__':
    binary,meta=build_p1a()
    if build_p1a()[0]!=binary:
        raise ValueError('P1a in-memory rebuild is not reproducible')
    print('M19 P1a public numeric getters IN MEMORY ONLY',meta)
