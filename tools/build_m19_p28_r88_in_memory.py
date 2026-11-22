#!/usr/bin/env python3
"""M19 P2.8 P1: experimental R88 AP20 image, generated IN MEMORY ONLY.

Reads frozen R87 archive; never modifies active candidate or R84 LAST_GOOD. Adds a 16x16x8 AGPC
independent-alpha masked Blitter wrapper to the R87 four-unit AP20. No
promotion, binary upload, tag or WinUAE claim. New public API tentative:
  Aga Cache Blit(CacheBank,X,Y,Mode) -> integer (0 rejection/1 success)
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/experiments'))

from active_library import R84_SHA,R87_SHA,P0_FREE_SHA,P1E_SHA,P2D_SHA
from audit_ap20 import inspect,parse,token
from compiler_relocation import unpack_ap20,repack_ap20,RBSR,GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements
from m19_p28_agpc_ap20_emit import emit_agpc_ap20,ENTRY_INDEX,GETADR_MARKER

ROOT=Path(__file__).resolve().parents[1]
R84=ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
R87=ROOT/'dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib'
BATCH_PUBLIC=82
CACHE_PUBLIC=83
GROUP_C2P=84
GROUP_IFF=85
GROUP_BOBS=86
GROUP_AGA=87
API=('aga cache blit',1,CACHE_PUBLIC,'00,0,0,0')
TITLE=(b'AMOSPro AGA R88 v0.13.33 M19 P2.8 AGPC MASKED BLITTER EXPERIMENT\0'
       b'$VER: AMOSPro_AGA 0.13.33 (R88) UNINSTALLED GATE A ONLY\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    good=R84.read_bytes();old=R87.read_bytes()
    # R88 remains an immutable historical reconstruction after P2d promotion.
    # Authenticate the protected release; never use it as the R88 input.
    if (len(good),sha256(good).hexdigest()) not in (
            (117896,P0_FREE_SHA),(124444,P1E_SHA),(136020,P2D_SHA)):
        raise ValueError('Unknown promoted P0/P1e/P2d LAST_GOOD')
    from build_aga_r84_agapic import build as build_r84
    historical,r84_meta=build_r84()
    if len(historical)!=67904 or r84_meta['sha256']!=R84_SHA:
        raise ValueError('Historical R84 source drift')
    if len(old)!=73184 or sha256(old).hexdigest()!=R87_SHA:
        raise ValueError('R87 historical predecessor differs from pinned binary')
    tokens,parts,_=unpack_ap20(old)
    if len(parts)!=87 or tuple(map(len,parts[83:]))!=(5558,2508,5220,56580):
        raise ValueError('R87 AP20 layout differs')
    original=inspect(parse(old))
    if original['issues'] or len([a for a in original['tokens'] if a['name'].startswith('aga ')])!=77:
        raise ValueError('R87 command contract differs')
    new_native,labels=emit_agpc_ap20()
    if not new_native.startswith(bytes.fromhex('48e7efee')) or new_native.count(GETADR_MARKER)!=1:
        raise ValueError('AGPC emitter malformed')
    entry=len(parts[GROUP_BOBS-1])-len(DISPATCH_V2)
    assert entry==5186
    bob_unit=parts[85]+new_native
    if len(bob_unit)>65534 or (len(bob_unit)&1):
        raise ValueError('Compiler V2 BOBS unit length limit')
    stubs=[]
    for index,oldstub in enumerate(parts[:CACHE_PUBLIC]):
        if oldstub in (b'',GETP):
            stubs.append(oldstub)
            continue
        if not(oldstub[:2]==RBSR and len(oldstub) in (8,12) and oldstub[6:8]==b'\x4e\x75'):
            raise ValueError(f'Unknown R87 stub {index}')
        group,offset=unpack_from('>HH',oldstub,2)
        if group not in (83,84,85,86):
            raise ValueError(f'Unknown native group {group}')
        newstub=RBSR+pack('>HH',group+1,offset)+oldstub[6:]
        if index==BATCH_PUBLIC:
            if len(newstub)!=8:
                raise ValueError('Unexpected GetP on R87 Batch stub')
            newstub+=GETP
        stubs.append(newstub)
    stubs.append(RBSR+pack('>HH',GROUP_BOBS,entry)+b'\x4e\x75')
    compiled_parts=stubs+[parts[83],parts[84],bob_unit,parts[86]]
    assert len(compiled_parts)==88
    newtokens=tokens[:-6]+token(*API)+bytes(6)
    candidate=repack_ap20(old,newtokens,compiled_parts,TITLE)
    rebuilt,unpacked,title=unpack_ap20(candidate)
    assert (rebuilt,unpacked,title)==(newtokens,compiled_parts,TITLE)
    report=inspect(parse(candidate))
    if report['issues'] or report['tokens'][:-1]!=original['tokens']:
        raise ValueError(('ABI/previous tokens changed',report['issues']))
    if (report['tokens'][-1]['name'],report['tokens'][-1]['function'],
        report['tokens'][-1]['signature'])!=(API[0],API[2],API[3]):
        raise ValueError('new cache token not 4-argument integer function')
    if len([a for a in report['tokens'] if a['name'].startswith('aga ')])!=78:
        raise ValueError('not 78 commands')
    if not any(v['index']==CACHE_PUBLIC and v['parameters']==4 and v['getp']
               for v in report['parameter_checks']):
        raise ValueError('new cache GetP ABI mismatch')
    if not any(v['index']==BATCH_PUBLIC and v['parameters']==2 and v['getp']
               for v in report['parameter_checks']):
        raise ValueError('existing Bob Batch GetP ABI mismatch')
    if (unpacked[GROUP_C2P],unpacked[GROUP_IFF],unpacked[GROUP_AGA])!=tuple(parts[i] for i in (83,84,86)):
        raise ValueError('R84 native groups changed')
    if unpacked[GROUP_BOBS] != parts[85]+new_native:
        raise ValueError('BOBS native payload differs')
    links=interpreter_rbsr_displacements(unpacked)
    if CACHE_PUBLIC not in links or BATCH_PUBLIC not in links:
        raise ValueError('native dispatch offset missing')
    if max(map(abs,links.values()))>=32766:
        raise ValueError('BSR.W reach limit exceeded')
    if any(len(unpacked[i])>65534 for i in (GROUP_C2P,GROUP_IFF,GROUP_BOBS,GROUP_AGA)):
        raise ValueError('Compiler copied unit exceeds limit')
    return candidate,dict(version='R88 v0.13.33 IN-MEMORY ONLY',sha256=sha256(candidate).hexdigest(),
                          bytes=len(candidate),api='Aga Cache Blit(CacheBank,X,Y,Mode)',
                          commands=78,entries=88,group_bobs_bytes=len(bob_unit),
                          native_entry_offset=entry,cache_native_bytes=len(new_native),
                          interpreter_reach=max(map(abs,links.values())),labels=labels,
                          gate_a='NOT TESTED',gate_b='NOT TESTED',gate_c='NOT TESTED')


if __name__=='__main__':
    candidate,info=build()
    info.pop('labels')
    print('M19 P2.8 R88 UNINSTALLED AP20 CANDIDATE',info)
    print('R88 active candidate, R87 archived and R84 LAST_GOOD protected; builder has no --write-dist')
