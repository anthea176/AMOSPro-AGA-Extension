#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0a experimental AP20 constructor with R88 *exact* frozen base.

No use of R89/R90 code, builders, examples or binaries. Does NOT write to
`dist/` or replace the active Lib / protected LAST_GOOD.
New public command: Aga Bob Bank N (bank selection + empty AGBO bank create).
Get AGA Bob capture is NOT exported until its full native implementation is
validated. Not yet a complete multi-image Bob engine.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from

# R88 stores the V2 reach validator under tools/experiments.
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/"experiments"))

from audit_ap20 import inspect,parse,token
from compiler_relocation import unpack_ap20,repack_ap20,RBSR,GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements
from m19_p0a_bank_select_emit import emit_bank_select
from active_library import P0_FREE_SHA, P1E_SHA

ROOT=Path(__file__).resolve().parents[1]
R88_SHA='69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc'
R84_SHA='46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d'
R88=ROOT/'dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib'
R84=ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
PUBLIC=84
OLD_LAST_PUBLIC=83
OLD_GROUP_START=84
NEW_GROUP_START=85
BOBS_GROUP=87
API=('aga bob bank',PUBLIC,1,'I0')
TITLE=(b'AMOSPro AGA M19 P0a R88-base BANK SELECT EXPERIMENT ONLY\0'
       b'$VER: AMOSPro_AGA M19 P0a derived from R88 0.13.33 GATE A ONLY\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    base=R88.read_bytes()
    good=R84.read_bytes()
    if len(base)!=75040 or sha256(base).hexdigest()!=R88_SHA:
        raise ValueError('R88 frozen candidate differs: refuse to build')
    # Historical R88 / P0 builder remains byte-identical after authorized P1e promotion.
    if (len(good),sha256(good).hexdigest()) not in ((117896,P0_FREE_SHA),(124444,P1E_SHA)):
        raise ValueError('Unrecognized author-promoted LAST_GOOD: refuse to build')
    from build_aga_r84_agapic import build as build_r84
    historical,r84_meta=build_r84()
    if len(historical)!=67904 or r84_meta['sha256']!=R84_SHA:
        raise ValueError('Historical R84 source differs: refuse to build')
    tokens,parts,_=unpack_ap20(base)
    if len(parts)!=88 or not parts[86].startswith(DISPATCH_V2):
        raise ValueError('R88 V2 four-unit layout changed')
    old=inspect(parse(base))
    if old['issues'] or len([v for v in old['tokens'] if v['name'].startswith('aga ')])!=78:
        raise ValueError('R88 token table changed')
    native,labels=emit_bank_select()
    # No new instructions can enter an old group at unknown offsets.
    entry=len(parts[86])-len(DISPATCH_V2)
    if entry!=7004:
        raise ValueError('BOBS group entry offset does not match R88')
    bob_unit=parts[86]+native
    if len(bob_unit)>65534 or len(bob_unit)&1:
        raise ValueError('BOBS unit exceeds Compiler V2 size')
    stubs=[]
    for index,original in enumerate(parts[:OLD_GROUP_START]):
        if original in (b'',GETP):
            stubs.append(original)
            continue
        if not (original[:2]==RBSR and len(original) in (8,12) and original[6:8]==b'\x4e\x75'):
            raise ValueError(f'Unknown R88 stub at {index}')
        group,offset=unpack_from('>HH',original,2)
        if not 84<=group<=87:
            raise ValueError(f'Unexpected R88 compiler native unit {group}')
        stub=RBSR+pack('>HH',group+1,offset)+original[6:]
        if index==OLD_LAST_PUBLIC:
            if len(stub)!=8:
                raise ValueError('Last R88 stub already has unexpected GetP')
            stub+=GETP
        stubs.append(stub)
    stubs.append(RBSR+pack('>HH',BOBS_GROUP,entry)+b'\x4e\x75')
    # All R88 native units retained at identical bytes except BOBS append.
    new_parts=stubs+list(parts[84:86])+[bob_unit]+[parts[87]]
    if len(new_parts)!=89 or any(len(v)>65534 for v in new_parts[85:]):
        raise ValueError('P0a AP20 unit constraints exceeded')
    new_tokens=tokens[:-6]+token(*API)+bytes(6)
    candidate=repack_ap20(base,new_tokens,new_parts,TITLE)
    restored,entries,title=unpack_ap20(candidate)
    if (restored,entries,title)!=(new_tokens,new_parts,TITLE):
        raise ValueError('Round-trip corruption')
    audit=inspect(parse(candidate))
    if audit['issues'] or audit['tokens'][:-1]!=old['tokens']:
        raise ValueError(('AP20 ABI/token regression',audit['issues']))
    if (audit['tokens'][-1]['name'],audit['tokens'][-1]['instruction'],
            audit['tokens'][-1]['signature'])!=(API[0],API[1],API[3]):
        raise ValueError('Aga Bob Bank must be a one-argument INSTRUCTION')
    if not any(v['index']==PUBLIC and v['parameters']==1 and v['getp']
               for v in audit['parameter_checks']):
        raise ValueError('GetP missing before new command')
    if len([v for v in audit['tokens'] if v['name'].startswith('aga ')])!=79:
        raise ValueError('Unexpected number of commands')
    # Compiler/native-ABI and interpreter signed branch reach.
    links=interpreter_rbsr_displacements(new_parts)
    if PUBLIC not in links or max(map(abs,links.values()))>=32766:
        raise ValueError('Interpreter BSR.W cannot reach M19 P0a native entry')
    return candidate,dict(base_sha=R88_SHA,sha256=sha256(candidate).hexdigest(),
        bytes=len(candidate),commands=79,ap20_entries=89,
        bob_unit_bytes=len(bob_unit),native_bytes=len(native),
        entry_offset=entry,public_index=PUBLIC,compiler_group=BOBS_GROUP,
        interpreter_max_reach=max(map(abs,links.values())),labels=labels,
        gate_a_cpu='NON TESTE',gate_b='NON TESTE',gate_c='NON TESTE')


if __name__=='__main__':
    binary,meta=build()
    print('M19 P0a R88-based IN-MEMORY candidate',
          {k:v for k,v in meta.items() if k!='labels'})
