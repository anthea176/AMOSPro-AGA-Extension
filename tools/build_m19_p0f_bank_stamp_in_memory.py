#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0f AGBO bank stamp appended PRIVATELY to AGA V2, in-memory only.

Strict byte-exact P0e split Close provenance, no change to its 85 tokens,
95 AP20 entries, BOBS/Chip/Blitter routines, Safe buffer, Close or End.
The native stamp needs the live AMOS main Bnk.GetAdr RJSR service and must
be verified under both real Runtime and compiled AMOS before any install.

This is only a private bank-identity PREREQUISITE for future Draw; no
object-slot binding or public Draw is implemented by this builder.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys
from compiler_relocation import unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from audit_ap20 import inspect,parse
from build_m19_p0e_split_close_in_memory import build as build_close
from m19_p0f_bank_stamp_emit import emit_bank_stamp,GETADR

sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

BASE_SHA='8185ae2d056da209a88c0b91e315d1cbb97acabadf7b55352e8cd7a348c1b207'
AGA_GROUP=94
TITLE=(b'AMOSPro AGA M19 P0f 020 PRIVATE BANK STAMP IN MEMORY GATE A\0'
       b'$VER: AMOSPro_AGA M19 P0f stamp guard SOURCE ONLY NOT INSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    original,old=build_close()
    if old['sha256']!=BASE_SHA or sha256(original).hexdigest()!=BASE_SHA:
        raise ValueError('P0e split Close canonical source drift')
    tokens,parts,_=unpack_ap20(original)
    if len(parts)!=95 or old['public_commands']!=85 or (
            not parts[AGA_GROUP].startswith(DISPATCH_V2)):
        raise ValueError('old Compiler V2 table/group drift')
    stamp,labels=emit_bank_stamp()
    if len(stamp)&1 or stamp.count(GETADR)!=1:
        raise ValueError('invalid native P0f AGBO identity stamp')
    newparts=list(parts)
    newparts[AGA_GROUP]+=stamp
    if len(newparts[AGA_GROUP])>65534 or (
            newparts[AGA_GROUP][:len(parts[AGA_GROUP])]!=parts[AGA_GROUP]):
        raise ValueError('AGA compiler group limit or prefix changed')
    new=repack_ap20(original,tokens,newparts,TITLE)
    if unpack_ap20(new)!=(tokens,newparts,TITLE):
        raise ValueError('AP20 compiler HUNK roundtrip failure')
    if newparts[:AGA_GROUP]!=parts[:AGA_GROUP]:
        raise ValueError('old BOBS/Close/Chip/Blitter/native groups altered')
    oldaudit=inspect(parse(original));audit=inspect(parse(new))
    if audit['issues'] or audit['tokens']!=oldaudit['tokens']:
        raise ValueError('public API changed')
    before=interpreter_rbsr_displacements(parts)
    after=interpreter_rbsr_displacements(newparts)
    if before!=after:
        raise ValueError('stamp changed the old signed PC16 stubs')
    assert max(map(abs,after.values()))==32576
    source_group_offset=len(parts[AGA_GROUP])-len(DISPATCH_V2)
    return new,dict(
        sha256=sha256(new).hexdigest(),size=len(new),previous_sha=BASE_SHA,
        public_commands=85,ap20_entries=95,group=AGA_GROUP,
        stamp_bytes=len(stamp),stamp_native_offset=source_group_offset,
        stamp_state_delta=len(parts[AGA_GROUP])-0x1c2,
        stamp_labels=labels,aga_bytes=len(newparts[AGA_GROUP]),
        pc16_max=max(map(abs,after.values())),pc16_margin=32766-32576,
        bank_identity='PRIVATE SNAPSHOT/VERIFY ONLY',
        draw='NOT IMPLEMENTED',end_reset='NOT IMPLEMENTED',
        gate_a='PENDING',gate_b='NOT TESTED',gate_c='NOT TESTED')


if __name__=='__main__':
    _,meta=build()
    print('M19 P0f AGA-BANK-STAMP PRIVATE AP20 SOURCE ONLY',
          meta)
