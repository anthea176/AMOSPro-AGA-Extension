#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0d AP20 V2 candidate in MEMORY ONLY: Aga Bob Blit(I,X,Y).

Rebuilds from the exactly pinned R88/P0b -> P0c verified source graph.
Adds ONE public numeric function, shifts only public AP20 V2 group indices,
appends ONLY native MC68020 code to the existing BOBS group; original AGA,
C2P, IFF native group bytes are unchanged. No .Lib, ASC or LAST_GOOD writes.

Gate A must execute BOTH native public function ABI (GetP, AMOS stack) and
a re-read candidate with Compiler-V2 layout. This script does not itself
run the real AMOS Compiler or demonstrate actual WinUAE DMA.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack,unpack_from
from audit_ap20 import inspect,parse,token
from compiler_relocation import unpack_ap20,repack_ap20,RBSR,GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from build_m19_p0c_screen_close_in_memory import (
    build as build_p0c,verify_aga_legacy,OLD_BOBS,OLD_AGA,
)
from m19_p0c_program_end_bridge_emit import emit_program_end_bridge
from m19_p0d_public_blit_emit import emit_public_blit
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

P0C_SIZE=87020
P0C_SHA='277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a'
FIRST_NEW_STUB=88
OLD_GROUP_START=88
OLD_BOBS=90
OLD_AGA=91
NEW_BOBS=91
NEW_AGA=92
PUBLIC=('aga bob blit',1,FIRST_NEW_STUB,'00,0,0')
TITLE=(b'AMOSPro AGA M19 P0d MC68020 BOB BLIT EXPERIMENT GATE A ONLY\0'
       b'$VER: AMOSPro_AGA M19 P0d uninstalled native Bob Blit Gate A\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    original,prior=build_p0c()
    if (len(original)!=P0C_SIZE or sha256(original).hexdigest()!=P0C_SHA
            or prior['public_commands']!=82 or prior['ap20_entries']!=92):
        raise ValueError('P0c exact base/provenance mismatch')
    orig_tokens,orig_parts,orig_title=unpack_ap20(original)
    verify_aga_legacy(orig_parts)
    if len(orig_parts)!=92 or not orig_parts[OLD_BOBS].startswith(DISPATCH_V2):
        raise ValueError('P0c V2 group layout changed')

    old_native,old_labels=emit_program_end_bridge()
    new_native,labels=emit_public_blit()
    if not new_native.startswith(old_native):
        raise ValueError('P0c native prefix was altered')
    if not orig_parts[OLD_BOBS].endswith(old_native):
        raise ValueError('P0c actual BOBS unit/source mismatch')
    appended=new_native[len(old_native):]
    if not appended or len(appended)%2:
        raise ValueError('P0d native suffix missing or odd')
    bobs=orig_parts[OLD_BOBS]+appended
    if len(bobs)>65534 or len(bobs)%2:
        raise ValueError('P0d BOBS unit exceeds Compiler 16-bit bound')
    entry=(len(orig_parts[OLD_BOBS])-len(DISPATCH_V2)) + (
        labels['public_bob_blit_entry']-len(old_native))
    if entry&1 or not (0 <= entry < 65534):
        raise ValueError('public Bob Blit offset is not word aligned')

    # Existing public RBSR group labels move +1 after the new token stub.
    # The preceding last No Mask stub gains a GetP delimiter for the new
    # 3-parameter Blit function, exactly as P0a/P0b builders do.
    public_parts=[]
    for index,part in enumerate(orig_parts[:OLD_GROUP_START]):
        if part in (b'',GETP):
            public_parts.append(part)
            continue
        if (part[:2]!=RBSR or len(part) not in (8,12)
                or part[6:8]!=bytes.fromhex('4e75')):
            raise ValueError(f'unrecognized AP20 public stub {index}')
        group,offset=unpack_from('>HH',part,2)
        if group not in (88,89,90,91):
            raise ValueError(f'unrecognized old V2 target {index}:{group}')
        new_part=RBSR+pack('>HH',group+1,offset)+part[6:]
        if index==FIRST_NEW_STUB-1:
            if len(new_part)!=8:
                raise ValueError('last old No Mask stub unexpectedly has GetP')
            new_part+=GETP
        public_parts.append(new_part)
    public_parts.append(RBSR+pack('>HH',NEW_BOBS,entry)+bytes.fromhex('4e75'))
    parts=public_parts+[
        orig_parts[88],orig_parts[89],bobs,orig_parts[OLD_AGA]]
    if len(parts)!=93 or any(len(p)>65534 or len(p)%2 for p in parts):
        raise ValueError('P0d AP20 V2 segment count/length')
    if parts[92]!=orig_parts[91] or parts[89:91]!=orig_parts[88:90]:
        raise ValueError('old AGA/C2P/IFF native groups mutated')

    tokens=orig_tokens[:-6]+token(*PUBLIC)+bytes(6)
    candidate=repack_ap20(original,tokens,parts,TITLE)
    if unpack_ap20(candidate)!=(tokens,parts,TITLE):
        raise ValueError('candidate AP20 HUNK/V2 roundtrip mismatch')
    before=inspect(parse(original))
    after=inspect(parse(candidate))
    if after['issues'] or after['tokens'][:-1]!=before['tokens']:
        raise ValueError(('public AP20 tokens damaged',after['issues']))
    command=after['tokens'][-1]
    if (command['name'],command['instruction'],command['function'],
            command['signature'])!=PUBLIC:
        raise ValueError(('Bob Blit token mismatch',command))
    checks=[p for p in after['parameter_checks']
            if p['index']==FIRST_NEW_STUB and p['role']=='function']
    if len(checks)!=1 or checks[0]['parameters']!=3 or not checks[0]['getp']:
        raise ValueError('function 3-argument GetP is not recognized')
    if len([c for c in after['tokens'] if c['name'].startswith(
            ('aga ','get aga ','make aga ','no aga '))])!=83:
        raise ValueError('unexpected API command count')
    for i in range(OLD_GROUP_START):
        if orig_parts[i] in (b'',GETP):
            assert parts[i]==orig_parts[i]
        else:
            group,offset=unpack_from('>HH',orig_parts[i],2)
            assert unpack_from('>HH',parts[i],2)==(group+1,offset)
    lengths=interpreter_rbsr_displacements(parts)
    if FIRST_NEW_STUB not in lengths:
        raise ValueError('interpreter Bob Blit RBSR link missing')
    max_reach=max(map(abs,lengths.values()))
    if max_reach>=32766:
        raise ValueError(f'interpreter PC16 RBSR out of range: {max_reach}')
    return candidate,dict(
        previous_sha=P0C_SHA,sha256=sha256(candidate).hexdigest(),
        bytes=len(candidate),commands=83,entries=93,
        public_index=FIRST_NEW_STUB,group=NEW_BOBS,entry=entry,
        public_signature=PUBLIC,bobs_bytes=len(bobs),
        native_append_bytes=len(appended),max_rbsr=max_reach,
        labels=labels, gate_a='PENDING',gate_b='NOT TESTED',
        gate_c='NOT TESTED',gate_d='NOT TESTED')


if __name__=='__main__':
    _,meta=build()
    print('M19 P0d in-memory AP20 V2 experiment', {
        k:v for k,v in meta.items() if k!='labels'})
