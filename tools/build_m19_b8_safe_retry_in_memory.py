#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 SafePort bounded Clear-retry AP20 (source-only, append-only).

A frozen, byte-exact B8 115744-byte AP20 image is the ONLY predecessor.
Original 88 token signatures, 184 entries and B7 68020 native unit stay
byte-exact. Append a small Safe-aware Clear wrapper to fifth unit and
redirect the existing Clear AP20 V2 stub (182) ONLY. No new public API.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack,unpack_from
from pprint import pprint
import argparse
import base64

from audit_ap20 import inspect,parse
from compiler_relocation import RBSR,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_first_update_in_memory import build_b8_first_update
from m19_b8_first_update_emit import emit_b8_first_update
from m19_b8_safe_retry_emit import emit_b8_safe_retry,MAX_SAFE_VBLS

PREDECESSOR_SHA='00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae'
GROUP=181
CLEAR=182
TITLE=(b'AMOSPro AGA M19 B8 S1 bounded SafePort Clear retry MC68020\0'
       b'$VER: AMOSPro_AGA M19 B8 S1 SAFE CANDIDATE\0')
TITLE+=bytes(len(TITLE)&1)


def build_b8_safe_retry():
    previous,report=build_b8_first_update()
    if (len(previous)!=115744 or sha256(previous).hexdigest()!=PREDECESSOR_SHA
            or report['sha256']!=PREDECESSOR_SHA):
        raise ValueError('B8 predecessor mismatch; frozen baseline cannot move')
    tokens,parts,_=unpack_ap20(previous)
    if len(parts)!=184 or not parts[GROUP].startswith(DISPATCH_V2):
        raise ValueError('B8 five-unit Compiler V2 baseline changed')
    old,labs=emit_b8_first_update()
    new,newlabs=emit_b8_safe_retry()
    if not new.startswith(old) or parts[GROUP]!=DISPATCH_V2+old:
        raise ValueError('B8 native fifth-unit ancestor changed')
    if (parts[CLEAR]!=RBSR+pack('>HH',GROUP,labs['b8_service_clear_guard_entry'])+b'\x4e\x75'):
        raise ValueError('Old public Clear stub is not exactly source-pinned')
    changed=list(parts)
    changed[GROUP]+=new[len(old):]
    if len(changed[GROUP])>=MAX_UNIT_BYTES:
        raise ValueError('Native unit exceeds AP20 V2 limit')
    newtarget=newlabs['b8_service_clear_wait_safe_entry']
    assert not newtarget&1 and newtarget<len(changed[GROUP])-len(DISPATCH_V2)
    changed[CLEAR]=RBSR+pack('>HH',GROUP,newtarget)+b'\x4e\x75'
    for i in range(len(parts)):
        if i not in (CLEAR,GROUP) and changed[i]!=parts[i]:
            raise ValueError('Historical AP20 section unexpectedly modified')
    assert changed[GROUP][:len(parts[GROUP])]==parts[GROUP]
    image=repack_ap20(previous,tokens,changed,TITLE)
    if unpack_ap20(image)!=(tokens,changed,TITLE):
        raise ValueError('AP20/V2 reproducibility roundtrip failure')
    audit_before=inspect(parse(previous))
    audit_after=inspect(parse(image))
    if (audit_before['issues'] or audit_after['issues']
            or audit_before['tokens']!=audit_after['tokens']):
        raise ValueError('Unexpected public API change')
    groups=[i for i,p in enumerate(changed) if p.startswith(DISPATCH_V2)]
    reaches=pc16_displacements(changed)
    limit=max(map(abs,reaches.values()))
    if groups!=[142,153,156,177,181] or limit>=32766:
        raise ValueError('Compiler PC16 out of range or group change')
    assert len([x for x in audit_after['tokens'] if x['name']=='aga bob clear'])==1
    return image,dict(sha256=sha256(image).hexdigest(),
        bytes=len(image),predecessor_sha=PREDECESSOR_SHA,
        public_commands=88,ap20_entries=184,native_groups=groups,
        pc16_max=limit,clear_stub=CLEAR,clear_native_offset=newtarget,
        wait_tof_max=MAX_SAFE_VBLS,new_native_bytes=len(new)-len(old),
        b7_byte_exact=True,b8_byte_prefix_exact=True,
        source_only=True,gate_a='TEST REQUIRED',
        gate_b='NOT TESTED',gate_c='NOT TESTED',
        last_good='UNCHANGED')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--emit-base64',action='store_true',
                   help='CI-only exact-byte transfer after Gate A')
    args=p.parse_args()
    image,report=build_b8_safe_retry()
    assert image==build_b8_safe_retry()[0], 'non-deterministic b8 s1'
    print('M19 B8 S1 BOUNDED SAFE CLEAR AP20 candidate IN MEMORY',flush=True)
    pprint(report)
    if args.emit_base64:
        print('B8S1_B64_BEGIN',flush=True)
        encoded=base64.b64encode(image).decode('ascii')
        for n in range(0,len(encoded),120):
            print('B8S1_B64',encoded[n:n+120],flush=True)
        print('B8S1_B64_END',flush=True)
