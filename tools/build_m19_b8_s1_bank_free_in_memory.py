#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0: Bank Select pre-stage + Bank Free AP20 (IN MEMORY, exact S1)."""
from __future__ import annotations

from hashlib import sha256
from pprint import pprint
from struct import pack,unpack_from

from audit_ap20 import inspect,parse,token,walk_tokens
from compiler_relocation import RBSR,GETP,unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_s1_bank_prestage_in_memory import (
    build_bank_prestage,PRESTAGE_SHA,PRESTAGE_BYTES
)
from m19_b8_s1_bank_prestage_emit import emit_b8_s1_bank_prestage
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free

BOBS=177
FREE=184
API=('aga bob bank free', FREE, 1, 'I0')
TITLE=(b'AMOSPro AGA M19 P0 Bank Chip Select+Free MC68020 candidate\0'
       b'$VER: AMOSPro_AGA M19 P0 BANK FREE GATE A CANDIDATE\0')
TITLE+=bytes(len(TITLE)&1)


def build_bank_free():
    old,meta=build_bank_prestage()
    if (len(old)!=PRESTAGE_BYTES or sha256(old).hexdigest()!=PRESTAGE_SHA
            or meta['sha256']!=PRESTAGE_SHA):
        raise ValueError('P0 pre-stage SHA/size mismatch')
    toks,parts,_=unpack_ap20(old)
    if len(parts)!=184 or parts[BOBS][:len(DISPATCH_V2)]!=DISPATCH_V2:
        raise ValueError('Expected exact five-unit P0 pre-stage AP20')
    prefix,labs=emit_b8_s1_bank_prestage()
    native,newlabs=emit_b8_s1_bank_free()
    if not native.startswith(prefix) or not parts[BOBS].endswith(prefix):
        raise ValueError('BOBS native suffix no longer byte exact')
    if any(t['name']==API[0] for t in walk_tokens(toks)):
        raise ValueError('Aga Bob Bank Free already tokenized')
    target=len(parts[BOBS])-len(DISPATCH_V2) + (newlabs['b8s1_bank_free_entry']-len(prefix))
    newparts=list(parts)
    newparts[BOBS]+=native[len(prefix):]
    if (target&1 or target<0 or len(newparts[BOBS])>=MAX_UNIT_BYTES
            or target>=len(newparts[BOBS])-len(DISPATCH_V2)):
        raise ValueError('BOBS target or V2 island exceeds capacity')
    # One-argument INSTRUCTION (D3=bank). AP20 GetP metadata is obligatory.
    newparts.append(RBSR+pack('>HH',BOBS,target)+b'\x4e\x75'+GETP)
    newtokens=toks[:-6]+token(*API)+toks[-6:]
    if len(newparts)!=185:
        raise ValueError('AP20 new instruction count wrong')
    image=repack_ap20(old,newtokens,newparts,TITLE)
    if unpack_ap20(image)!=(newtokens,newparts,TITLE):
        raise ValueError('AP20 roundtrip corruption')
    before,after=inspect(parse(old)),inspect(parse(image))
    if (before['issues'] or after['issues']
            or after['tokens'][:-1]!=before['tokens']):
        raise ValueError('Preexisting AP20 API/stubs changed')
    found=[t for t in after['tokens'] if t['name']==API[0]]
    if len(found)!=1 or (found[0]['instruction'],found[0]['function'],
                          found[0]['signature'])!=(FREE,1,'I0'):
        raise ValueError('Public Aga Bob Bank Free token is not an instruction')
    if any(newparts[i]!=parts[i] for i in range(len(parts)) if i!=BOBS):
        raise ValueError('Historical stub changed')
    if not newparts[BOBS].startswith(parts[BOBS]):
        raise ValueError('Pre-stage native prefix changed')
    groups=[i for i,p in enumerate(newparts) if p.startswith(DISPATCH_V2)]
    spans=pc16_displacements(newparts)
    pc16=max(map(abs,spans.values()))
    if groups!=[142,153,156,177,181] or pc16>=32766:
        raise ValueError('Compiler AP20 PC16 out of range')
    return image,dict(
       sha256=sha256(image).hexdigest(),bytes=len(image),
       predecessor_sha=PRESTAGE_SHA,public_commands=89,
       ap20_entries=185,native_groups=groups,pc16_max=pc16,
       bob_bank_index=164,bank_free_index=FREE,free_native_offset=target,
       appended_native_bytes=len(native)-len(prefix),
       old_bobs_prefix_byte_exact=True,b8_fifth_byte_exact=True,
       gate_a='TEST REQUIRED',gate_b='NOT TESTED',gate_c='NOT TESTED',
       installed=False,last_good='UNCHANGED')


if __name__=='__main__':
    import argparse,base64
    ap=argparse.ArgumentParser()
    ap.add_argument('--emit-base64',action='store_true')
    a=ap.parse_args()
    image,report=build_bank_free()
    assert build_bank_free()[0]==image
    print('M19 P0 BOB BANK FREE AP20 candidate IN MEMORY',flush=True)
    pprint(report)
    if a.emit_base64:
        print('P0_BANK_FREE_B64_BEGIN',flush=True)
        encoded=base64.b64encode(image).decode('ascii')
        for n in range(0,len(encoded),120):
            print('P0_BANK_FREE_B64',encoded[n:n+120],flush=True)
        print('P0_BANK_FREE_B64_END',flush=True)
