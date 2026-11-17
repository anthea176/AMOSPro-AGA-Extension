#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b3: explicit per-bank staged Chip image descriptor.

Private D3=source AGBO bank, D0=1-based image ID, A1=36-byte output,
A5=current AMOS owner. Result D3=1/0, D2=0, caller output unchanged on
failure, AMOS registers and stack preserved.

Uses P0j-b1 explicit_bank_lookup (correct live bank, generation,
P0c context, Chip ownership) and joins ORIGINAL byte-identical P0d
image resolver after its selected-bank lookup gate, at a zero-byte
anchor. The ORIGINAL directory, mask/offset and Chip span checks remain.

No read or write of selected-bank shadow, no Chip allocation/Blit/Swap,
no public Draw and no installed library.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code,D,A,M,I
from m19_p0d_bank_image_resolve_emit import F as RES_F
from m19_p0j_explicit_bank_stage_emit import emit_explicit_bank_stage

P0JB3_NATIVE_BYTES=19338
P0JB3_NATIVE_SHA256='ac4252e15ec04467d6789869f0f247c49249c5799276bfc07099811529d51437'
FRAME=192
SCRATCH=128
LOOKUP_DESCRIPTOR_BYTES=28
assert SCRATCH+LOOKUP_DESCRIPTOR_BYTES<=FRAME

def emit_explicit_bank_image_resolve() -> tuple[bytes,dict[str,int]]:
    previous,labels=emit_explicit_bank_stage()
    if 'resolve_live_payload' not in labels:
        raise ValueError('P0d zero-byte checked payload join anchor missing')
    c=Code();c.raw(previous.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,key):c.move(src,M(2,RES_F[key]))
    def G(key,dst):c.move(M(2,RES_F[key]),dst)

    L('explicit_image_resolve_entry')
    c.raw('48e7efee4fefff40')      # original P0d ABI + 192-byte local frame
    c.move(A(7),A(2))
    S(D(3),'bank');S(D(0),'image');S(A(1),'output')
    S(I(0),'result');S(I(0),'mask_ptr')
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'resolve_fail')
    G('image',D(0))
    c.imm('cmp',1,D(0));B(5,'resolve_fail')
    c.imm('cmp',4096,D(0));B(2,'resolve_fail')
    G('output',D(0));c.tst(D(0));B(7,'resolve_fail')
    c.imm('and',1,D(0));B(6,'resolve_fail')

    # Private 28-byte scratch at +128..+155; no shared state.
    G('bank',D(3))
    c.move(A(2),D(0));c.imm('add',SCRATCH,D(0))
    c.move(D(0),A(1))
    B(1,'explicit_bank_lookup_entry')
    c.tst(D(3));B(7,'resolve_fail')
    # b1 descriptor[0] is live source AGBO payload address, byte-exact.
    c.move(M(2,SCRATCH),D(0));S(D(0),'payload')
    c.tst(D(0));B(7,'resolve_fail')
    # Reuse original P0d image directory/Chip span/descriptor publication.
    B(0,'resolve_live_payload')

    native=c.out()
    if (not native.startswith(previous)
            or c.labels['explicit_image_resolve_entry']!=len(previous)
            or len(native)&1 or len(native)>=32766):
        raise ValueError('P0j-b3 modified earlier P0c/P0d code or overran PC16')
    if len(native)!=P0JB3_NATIVE_BYTES or sha256(native).hexdigest()!=P0JB3_NATIVE_SHA256:
        raise ValueError('P0j-b3 emitted MC68020 source SHA/size drift')
    return native,c.labels

if __name__=='__main__':
    data,labels=emit_explicit_bank_image_resolve()
    print('M19 P0j-b3 MC68020 EXPLICIT BANK IMAGE RESOLVER SOURCE ONLY',
          len(data),sha256(data).hexdigest(),
          'new bytes',len(data)-labels['explicit_image_resolve_entry'],
          'no bank_active_state, no public Draw/WinUAE')
