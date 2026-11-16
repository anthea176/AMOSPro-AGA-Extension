#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-only AP20/Compiler V2 candidate: public Aga Bob + Aga Bob Off.

Based strictly on the pinned P0e BOBS->AGA source constructor, with the
original 83 AMOS commands, P0d Blitter/Close/End and private P0e objects
byte-identical. Adds two instruction tokens with correct GetP and AMOS365
argument ABI shims. DOES NOT install candidate or expose unfinished Draw.

The BOBS code is nearly at the PC16 boundary. Abort on any out-of-range
public BSR.W displacement, changed protected native unit, or token drift.
This is Gate A construction, NOT WinUAE/actual AMOS Compiler validation.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack,unpack_from
from pathlib import Path
import sys
from audit_ap20 import inspect,parse,token
from compiler_relocation import unpack_ap20,repack_ap20,RBSR,GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from build_m19_p0e_v2_bridge_in_memory import build as build_bridge
from m19_p0e_v2_object_bridge_emit import emit_v2_object_bridge
from m19_p0e_public_object_ops_emit import emit_public_object_ops
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

BASE_SHA='f49037880fe75a3314364642336b3e5fb8f9e7854214cc1a23049fbc1becd0de'
OLD_PUBLIC=89
NEW_BOBS=93
NEW_AGA=94
API=(
    ('aga bob',OLD_PUBLIC,1,'I0,0,0,0'),
    ('aga bob off',OLD_PUBLIC+1,1,'I0'),
)
TITLE=(b'AMOSPro AGA M19 P0e CPU020 OBJECT SET/OFF IN MEMORY Gate A\0'
       b'$VER: AMOSPro_AGA M19 P0e SET OFF no DRAW UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    previous,old=build_bridge()
    if old['sha256']!=BASE_SHA or sha256(previous).hexdigest()!=BASE_SHA:
        raise ValueError('P0e original verified cross-group bridge changed')
    old_tokens,old_parts,_=unpack_ap20(previous)
    if len(old_parts)!=93 or old['public_commands']!=83 or old['ap20_entries']!=93:
        raise ValueError('P0e bridge has unexpected public layout')
    old_native,old_labels=emit_v2_object_bridge()
    new_native,labels=emit_public_object_ops()
    if not new_native.startswith(old_native):
        raise ValueError('P0e cross-unit native prefix changed')
    if not old_parts[91].endswith(old_native):
        raise ValueError('P0e BOBS V2 code did not end with its source')
    appended=new_native[len(old_native):]
    if not appended or len(appended)&1:
        raise ValueError('missing public shim append')
    # Existing C2P, IFF, BOBS, AGA V2 groups move +2 after new stubs;
    # the binary contents of C2P, IFF, and AGA are NEVER touched.
    stubs=[]
    for i,part in enumerate(old_parts[:OLD_PUBLIC]):
        if part in (b'',GETP):
            stubs.append(part)
            continue
        if part[:2]!=RBSR or part[6:8]!=bytes.fromhex('4e75') or len(part) not in (8,12):
            raise ValueError(f'unrecognized public AP20 stub {i}')
        grp,off=unpack_from('>HH',part,2)
        if grp not in (89,90,91,92):
            raise ValueError(f'unknown original V2 group {grp} in stub {i}')
        shifted=RBSR+pack('>HH',grp+2,off)+part[6:]
        if i==OLD_PUBLIC-1:
            if len(shifted)!=8:
                raise ValueError('last Bob Blit stub already has a GetP marker')
            shifted+=GETP
        stubs.append(shifted)
    # The trailing four bytes GetP for the 1-arg Off must appear AFTER the
    # preceding 4-arg Bob's RTS, not at the end of Off (no following args).
    offsets={name:len(old_parts[91])-len(DISPATCH_V2)
             +labels[label]-len(old_native)
             for name,label in (
                 ('aga bob','public_aga_bob_entry'),
                 ('aga bob off','public_aga_bob_off_entry'))}
    stubs.append(RBSR+pack('>HH',NEW_BOBS,offsets['aga bob'])+bytes.fromhex('4e75')+GETP)
    stubs.append(RBSR+pack('>HH',NEW_BOBS,offsets['aga bob off'])+bytes.fromhex('4e75'))
    parts=stubs+old_parts[89:91]+[
        old_parts[91]+appended,old_parts[92],
    ]
    if len(parts)!=95 or any(len(part)>65534 or (len(part)&1) for part in parts):
        raise ValueError('bad Compiler V2 unit count/size')
    if parts[91:93]!=old_parts[89:91] or parts[94]!=old_parts[92] or (
            parts[93][:len(old_parts[91])]!=old_parts[91]):
        raise ValueError('one of the original native group bytes changed')
    tokens=old_tokens[:-6]+b''.join(token(*row) for row in API)+bytes(6)
    candidate=repack_ap20(previous,tokens,parts,TITLE)
    if unpack_ap20(candidate)!=(tokens,parts,TITLE):
        raise ValueError('AP20/HUNK byte-exact roundtrip failed')
    prior_audit=inspect(parse(previous))
    audit=inspect(parse(candidate))
    if audit['issues'] or audit['tokens'][:-2]!=prior_audit['tokens']:
        raise ValueError(('preexisting AMOS API changed',audit['issues']))
    for row,actual in zip(API,audit['tokens'][-2:]):
        if (actual['name'],actual['instruction'],actual['function'],actual['signature'])!=row:
            raise ValueError(('unrecognized AMOS token encoding',row,actual))
    for chk in audit['parameter_checks']:
        if chk['index'] in (OLD_PUBLIC,OLD_PUBLIC+1) and not chk['getp']:
            raise ValueError('public SET/OFF instruction did not receive GetP')
    links=interpreter_rbsr_displacements(parts)
    if not all(i in links for i in (0,70,88,OLD_PUBLIC,OLD_PUBLIC+1)):
        raise ValueError('old/new public entry missing from RBSR reach audit')
    reach=max(map(abs,links.values()))
    if reach>=32766:
        raise ValueError(f'new public Bob API exceeds signed PC16: {reach}')
    # Never mistake a new public compiler group for a 68000 flat monolith.
    assert all(parts[g].startswith(DISPATCH_V2) for g in (91,92,93,94))
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),length=len(candidate),
        previous_sha=BASE_SHA,public_commands=85,ap20_entries=95,
        bobs_bytes=len(parts[93]),aga_bytes=len(parts[94]),
        appended_bytes=len(appended),old_pc16_reach=old['rbsr_max'],
        new_pc16_reach=reach,pc16_margin=32766-reach,
        tokens=API,compiled_offsets=offsets,group=NEW_BOBS,
        gate_a='PENDING',gate_b='NOT TESTED',gate_c='NOT TESTED',
        draw='NOT IMPLEMENTED',close_reset='NOT IMPLEMENTED')


if __name__=='__main__':
    _raw,info=build()
    print('M19 P0e PUBLIC BOB SET/OFF AP20 V2 SOURCE-ONLY',
          info)
