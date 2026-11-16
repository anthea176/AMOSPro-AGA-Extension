#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0f source-only: public Aga Bob routes via checked bank identity.

Only the four-byte BOBS relay target immediate changes. P0d legacy bytes,
P0e object tables/Close, P0f native stamp and object binder are preserved.
No public Draw, End integration, installed Lib or WinUAE/Compiler claim.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import sys
from compiler_relocation import unpack_ap20,repack_ap20
from audit_ap20 import inspect,parse
from m19_p0e_split_bridge_emit import AGA_CORE,P0D
from m19_p0e_split_close_emit import emit_split_with_close
from m19_p0f_object_identity_emit import emit_object_identity
from build_m19_p0f_object_identity_in_memory import build as oldbuild
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

BOBS=93
AGA=94
TITLE=(b'AMOSPro AGA M19 P0f CPU020 source-only identity-bound public Bob\0'
       b'$VER: AMOSPro_AGA P0f Set bank stamp only UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)

def bound_offset():
    _,labels=emit_object_identity()
    return len(AGA_CORE)+labels['identity_bind_entry']

def emit_bound_public():
    return emit_split_with_close(put_offset=bound_offset())

def build():
    previous,meta=oldbuild()
    tokens,parts,_=unpack_ap20(previous)
    native_old,_=emit_split_with_close()
    native_new,labels=emit_bound_public()
    if (len(parts)!=95 or not parts[BOBS].endswith(native_old)
            or len(native_old)!=len(native_new)
            or not native_new.startswith(P0D)):
        raise ValueError('canonical split Close/BOBS source drift')
    diff=[i for i,(a,b) in enumerate(zip(native_old,native_new)) if a!=b]
    if not 1<=len(diff)<=4 or min(diff)<len(P0D):
        raise ValueError(('unexpected BOBS native changes',diff))
    if (bound_offset()%2 or bound_offset()>=65534
            or not parts[AGA].endswith(emit_object_identity()[0])):
        raise ValueError('missing AGA checked identity binder target')
    revised=list(parts)
    revised[BOBS]=parts[BOBS][:-len(native_old)]+native_new
    if (revised[BOBS][:len(parts[BOBS])-len(native_old)]!=
            parts[BOBS][:len(parts[BOBS])-len(native_old)]
            or len(revised[BOBS])!=len(parts[BOBS])):
        raise ValueError('P0d old BOBS code modified')
    out=repack_ap20(previous,tokens,revised,TITLE)
    if unpack_ap20(out)!=(tokens,revised,TITLE):
        raise ValueError('HUNK AP20 roundtrip failed')
    prior=inspect(parse(previous));audit=inspect(parse(out))
    if audit['issues'] or audit['tokens']!=prior['tokens']:
        raise ValueError('public token table changed')
    before=interpreter_rbsr_displacements(parts)
    after=interpreter_rbsr_displacements(revised)
    if before!=after or max(map(abs,after.values()))!=32576:
        raise ValueError('P0f bound Set changed reserved PC16 branch span')
    return out,dict(
        sha256=sha256(out).hexdigest(),size=len(out),
        previous_sha=meta['sha256'],public_commands=85,
        ap20_entries=95,put_target_offset=bound_offset(),
        changed_BOBS_bytes=len(diff),pc16_reach=32576,pc16_margin=190,
        public_bob='SOURCE-ONLY BOUND',draw='NOT IMPLEMENTED',
        end='NOT INTEGRATED',gate_a='PENDING',
        gate_b='NOT TESTED',gate_c='NOT TESTED')

if __name__=='__main__':
    print('M19 P0f PUBLIC BOB CHECKED BIND SOURCE ONLY',build()[1])
