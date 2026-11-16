#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0f source-only per-object AGBO bank stamp binder appended in AGA.

Keep original P0d + P0e Close and P0f bank-stamp exactly as source-built.
The public Set/Off tokens are UNCHANGED and still route through old P0e.
This intermediate binary is NOT an installed persistent Draw candidate.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys
from compiler_relocation import unpack_ap20,repack_ap20
from audit_ap20 import parse,inspect
from build_m19_p0f_bank_stamp_in_memory import build as build_stamp
from m19_p0f_bank_stamp_emit import emit_bank_stamp
from m19_p0f_object_identity_emit import emit_object_identity

sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

AGA=94
TITLE=(b'AMOSPro AGA M19 P0f source-only private object stamp binder Gate A\0'
       b'$VER: AMOSPro_AGA P0f private bank-identity guard UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    previous,prior=build_stamp()
    tokens,parts,_=unpack_ap20(previous)
    oldstamp,_=emit_bank_stamp()
    identity,labels=emit_object_identity()
    if len(parts)!=95 or not parts[AGA].endswith(oldstamp) or (
            not identity.startswith(oldstamp)):
        raise ValueError('P0f source stamp / AGA placement drift')
    append=identity[len(oldstamp):]
    if not append or (len(append)&1):
        raise ValueError('missing identity binder source suffix')
    changed=list(parts)
    changed[AGA]+=append
    if len(changed[AGA])>65534:
        raise ValueError('AGA Compiler V2 native unit size overflow')
    output=repack_ap20(previous,tokens,changed,TITLE)
    if unpack_ap20(output)!=(tokens,changed,TITLE):
        raise ValueError('AP20 HUNK roundtrip mismatch')
    if changed[:AGA]!=parts[:AGA] or changed[AGA][:len(parts[AGA])]!=parts[AGA]:
        raise ValueError('P0d/P0e provenance or original P0f stamp corrupted')
    a=inspect(parse(output));old=inspect(parse(previous))
    if a['issues'] or a['tokens']!=old['tokens']:
        raise ValueError('public API modified by private identity binder')
    before=interpreter_rbsr_displacements(parts)
    after=interpreter_rbsr_displacements(changed)
    if before!=after or max(map(abs,after.values()))!=32576:
        raise ValueError('P0f private identity binder changed PC16 stubs')
    return output,dict(
        sha256=sha256(output).hexdigest(),size=len(output),
        previous_sha=prior['sha256'],public_commands=85,ap20_entries=95,
        group=AGA,aga_bytes=len(changed[AGA]),old_stamp_bytes=len(oldstamp),
        binder_bytes=len(append),binder_labels=labels,
        public_set_bind='NOT YET ROUTED',draw='NOT IMPLEMENTED',
        end_hook='NOT INTEGRATED',pc16_max=32576,pc16_margin=190,
        gate_a='PENDING',gate_b='NOT TESTED',gate_c='NOT TESTED')


if __name__=='__main__':
    _,meta=build()
    print('M19 P0f AGA PER-OBJECT IDENTITY BINDER PRIVATE V2 SOURCE ONLY',
          {k:v for k,v in meta.items() if k!='binder_labels'})
