#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0 Bank Select pre-stages Chip source, B8 S1 AP20 IN MEMORY ONLY.

No new public command, no frozen binary mutation, no dist/ install.
Replace *only* the existing Aga Bob Bank stub, with source-verified
unchanged signatures and native BOBS prefix; preserve all other sections.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack,unpack_from
from pprint import pprint

from audit_ap20 import inspect,parse
from compiler_relocation import RBSR,unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
from m19_b8_first_update_emit import emit_b8_b7_first_update
from m19_b8_s1_bank_prestage_emit import emit_b8_s1_bank_prestage

S1_SHA='3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a'
BOBS=177
TITLE=(b'AMOSPro AGA M19 P0 Bank Select Chip prestage SOURCE ONLY MC68020\0'
       b'$VER: AMOSPro_AGA M19 P0 Chip PRESTAGE GATE A ONLY\0')
TITLE+=bytes(len(TITLE)&1)


def build_bank_prestage():
    old,oldmeta=build_b8_safe_retry()
    if sha256(old).hexdigest()!=S1_SHA or len(old)!=116104:
        raise ValueError('Active B8 S1 SHA drift: no authorization to mutate')
    toks,parts,_=unpack_ap20(old)
    old7,labs=emit_b8_b7_first_update()
    new7,newlabs=emit_b8_s1_bank_prestage()
    if not new7.startswith(old7) or not parts[BOBS].endswith(old7):
        raise ValueError('BOBS unit does not match byte-exact B8 S1 source')
    audit=inspect(parse(old))
    selected=[t for t in audit['tokens'] if t['name']=='aga bob bank']
    if audit['issues'] or len(selected)!=1:
        raise ValueError('Missing unique public Aga Bob Bank command')
    token=selected[0]
    if token['signature']!='I0':
        raise ValueError('Aga Bob Bank argument ABI changed')
    index=token['instruction']
    native_origin=len(parts[BOBS])-len(DISPATCH_V2)-len(old7)
    oldoffset=native_origin+labs['bank_bank_select']
    oldstub=parts[index]
    if (not oldstub.startswith(RBSR) or len(oldstub) not in (8,12)
            or oldstub[6:8]!=b'\x4e\x75'
            or unpack_from('>HH',oldstub,2)!=(BOBS,oldoffset)):
        raise ValueError('Public Bank Select pointer no longer source-pinned')
    changed=list(parts)
    changed[BOBS]+=new7[len(old7):]
    newoffset=native_origin+newlabs['b8s1_bank_prestage_entry']
    if (newoffset&1 or len(changed[BOBS])>=MAX_UNIT_BYTES
            or not 0<=newoffset<len(changed[BOBS])-len(DISPATCH_V2)):
        raise ValueError('V2 unit or native target out of range')
    changed[index]=RBSR+pack('>HH',BOBS,newoffset)+oldstub[6:]
    if any(changed[i]!=parts[i] for i in range(len(parts)) if i not in (BOBS,index)):
        raise ValueError('Unrelated historical AP20 entry changed')
    assert changed[BOBS].startswith(parts[BOBS])
    image=repack_ap20(old,toks,changed,TITLE)
    if unpack_ap20(image)!=(toks,changed,TITLE):
        raise ValueError('AP20 roundtrip failed')
    post=inspect(parse(image))
    if post['issues'] or post['tokens']!=audit['tokens']:
        raise ValueError('Public command count/signature altered')
    groups=[i for i,p in enumerate(changed) if p.startswith(DISPATCH_V2)]
    pc16=max(map(abs,pc16_displacements(changed).values()))
    if len(changed)!=184 or groups!=[142,153,156,177,181] or pc16>=32766:
        raise ValueError('Compiler V2 group count or PC16 range changed')
    return image,dict(sha256=sha256(image).hexdigest(),
        bytes=len(image),predecessor_sha=S1_SHA,
        native_groups=groups,pc16_max=pc16,
        public_commands=88,ap20_entries=184,bank_index=index,
        bank_offset_old=oldoffset,bank_offset_new=newoffset,
        new_native_bytes=len(new7)-len(old7),
        old_bobs_prefix_byte_exact=True,b8_fifth_byte_exact=True,
        gate_a='NOT YET TESTED',gate_b='NOT TESTED',gate_c='NOT TESTED',
        installed=False,active_lib='UNCHANGED',current_asc='UNCHANGED',
        last_good='UNCHANGED')


if __name__=='__main__':
    image,info=build_bank_prestage()
    if build_bank_prestage()[0]!=image:
        raise ValueError('Non-reproducible AP20 candidate')
    print('M19 P0 BANK SELECT CHIP PRESTAGE AP20 SOURCE ONLY')
    pprint(info)
