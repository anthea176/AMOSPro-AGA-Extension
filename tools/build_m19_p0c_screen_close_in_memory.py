#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""EXPERIMENT ONLY: P0c real public Screen Close -> BOBS Chip preclose -> AGA.

Builds an AP20 V2 image IN MEMORY ONLY from the exact P0b source constructor.
Changes exactly public stub 8, appends ONLY source-emitted BOBS native code,
and changes the version/title. ALL old AGA native bytes remain unchanged.
Never writes dist/, LAST_GOOD, current ASC or passed tests.

CPU020 Gate A must verify actual legacy AGA entry; real AMOS Compiler and
WinUAE Gates B/C are independent and NOT claimed. AMOS program End callback
remains an independent open requirement.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack,unpack_from

from audit_ap20 import inspect,parse
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP,RBSR,repack_ap20,unpack_ap20
from build_m19_p0b_masks_in_memory import build as build_p0b
from m19_p0b_masks_emit import emit_mask_commands
from m19_p0c_screen_close_bridge_emit import (
    emit_screen_close_bridge,AGA_STATE_OFFSET,AGA_CLOSE_ENTRY_OFFSET,
    CLOSE_STATE_DELTA,CLOSE_SIGNATURE,
)
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

P0B_SHA='f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9'
OLD_AGA=91
OLD_BOBS=90
CLOSE_PUBLIC_INDEX=8
P0B_ENTRIES=92
TITLE=(b'AMOSPro AGA M19 P0c PRIVATE CHIP SCREEN CLOSE BRIDGE GATE A ONLY\0'
       b'$VER: AMOSPro_AGA M19 P0c Screen Close bridge EXPERIMENT UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def verify_aga_legacy(parts):
    """Audit immutable R88/ P0b V2 entry signatures, never rewrite them."""
    if len(parts)!=P0B_ENTRIES or not parts[OLD_AGA].startswith(DISPATCH_V2):
        raise ValueError('P0b Compiler V2 layout changed')
    old_close=parts[CLOSE_PUBLIC_INDEX]
    if (old_close[:2]!=RBSR or old_close[6:8]!=bytes.fromhex('4e75')
            or old_close[8:] not in (b'',GETP)):
        raise ValueError('Aga Screen Close old public stub not recognized')
    group,old_offset=unpack_from('>HH',old_close,2)
    if (group,old_offset)!=(OLD_AGA,2008):
        raise ValueError(f'legacy Screen Close relocated unexpectedly: {group}:{old_offset}')
    aga=parts[OLD_AGA]
    if (aga[0x2c:0x2e]!=bytes.fromhex('41fa')
            or aga[0x30:0x34]!=bytes.fromhex('2b4801c8')):
        raise ValueError('AGA init no longer registers state in A5+456')
    state_target=0x2e+unpack_from('>h',aga,0x2e)[0]
    if state_target!=AGA_STATE_OFFSET:
        raise ValueError('AGA init state-relative LEA changed')
    close_target=len(DISPATCH_V2)+old_offset
    if close_target!=AGA_CLOSE_ENTRY_OFFSET:
        raise ValueError('real native Screen Close target mismatch')
    if close_target-state_target!=CLOSE_STATE_DELTA:
        raise ValueError('dynamic cross-unit link delta drift')
    observed=tuple(unpack_from('>I',aga,close_target+4*i)[0] for i in range(3))
    if observed!=CLOSE_SIGNATURE:
        raise ValueError('native Screen Close 020 prologue drift')
    if aga[state_target:state_target+40]!=bytes(40):
        raise ValueError('native AGA state init/data layout drift')
    return old_close


def build():
    base,old_meta=build_p0b()
    if (sha256(base).hexdigest()!=P0B_SHA or len(base)!=82376
            or old_meta['commands']!=82 or old_meta['entries']!=92):
        raise ValueError('frozen P0b builder or provenance changed')
    tokens,parts,_=unpack_ap20(base)
    baseline=inspect(parse(base))
    if baseline['issues'] or len([t for t in baseline['tokens'] if t['name'].startswith(('aga ','get aga ','make aga ','no aga '))])!=82:
        raise ValueError('frozen P0b tokens invalid')
    close_tokens=[t for t in baseline['tokens'] if t['name']=='aga screen close']
    if len(close_tokens)!=1 or close_tokens[0]['instruction']!=8:
        raise ValueError('public command index/type changed')
    original_close=verify_aga_legacy(parts)

    old_private,_=emit_mask_commands()
    extended,labels=emit_screen_close_bridge()
    bobs=parts[OLD_BOBS]
    if not bobs.startswith(DISPATCH_V2) or not bobs.endswith(old_private):
        raise ValueError('P0b original BOBS source prefix mismatch')
    if extended[:len(old_private)]!=old_private:
        raise ValueError('P0b source prefix altered by P0c')
    delta=extended[len(old_private):]
    if len(delta)&1 or not delta or len(bobs)+len(delta)>65534:
        raise ValueError('P0c BOBS native exceeds 16-bit Compiler V2 unit limit')
    new_bobs=bobs+delta
    bridge_offset=len(bobs)-len(DISPATCH_V2)+(labels['screen_close_bridge_entry']-len(old_private))
    if not 0<=bridge_offset<65534 or (bridge_offset&1):
        raise ValueError('P0c bridge offset beyond V2 group')
    new_stub=RBSR+pack('>HH',OLD_BOBS,bridge_offset)+original_close[6:]
    next_parts=list(parts)
    next_parts[CLOSE_PUBLIC_INDEX]=new_stub
    next_parts[OLD_BOBS]=new_bobs
    if next_parts[OLD_AGA]!=parts[OLD_AGA]:
        raise ValueError('historical AGA native unit was modified')
    if [i for i in range(P0B_ENTRIES) if next_parts[i]!=parts[i]]!=[8,90]:
        raise ValueError('unrelated AP20 unit modified')

    candidate=repack_ap20(base,tokens,next_parts,TITLE)
    nt,np,title=unpack_ap20(candidate)
    if (nt,np,title)!=(tokens,next_parts,TITLE):
        raise ValueError('AP20 HUNK V2 candidate round trip failed')
    audit=inspect(parse(candidate))
    if audit['issues'] or audit['tokens']!=baseline['tokens']:
        raise ValueError('AP20 public token inventory or GetP checks regressed')
    displacements=interpreter_rbsr_displacements(np)
    if CLOSE_PUBLIC_INDEX not in displacements:
        raise ValueError('interpreter RBSR for Aga Screen Close not linked')
    return candidate,dict(
        provenance=P0B_SHA,sha256=sha256(candidate).hexdigest(),size=len(candidate),
        public_commands=82,ap20_entries=92,native_bobs_bytes=len(new_bobs),
        source_delta_bytes=len(delta),screen_close_index=8,
        old_aga_group=OLD_AGA,old_aga_offset=2008,
        bridge_group=OLD_BOBS,bridge_offset=bridge_offset,
        rel_aga_close=CLOSE_STATE_DELTA,
        max_signed_rbsr=max(map(abs,displacements.values())),
        labels=labels,
        gate_a='PENDING',gate_b='NOT TESTED',gate_c='NOT TESTED',
        program_end_hook='NOT IMPLEMENTED')


if __name__=='__main__':
    _,report=build()
    print('M19 P0c Screen Close EXPERIMENT IN MEMORY ONLY',
          {k:v for k,v in report.items() if k!='labels'})
