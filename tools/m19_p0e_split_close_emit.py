#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e source-only Screen Close wrapper: reset objects before P0d Close.

All P0d bytes, the P0e generic AGA core, and the split public Set/Off
entries remain byte-exact; the actual AP20 Screen Close stub must be
redirected to this new wrapper by a separate source-only builder.

First, successfully reset the 64-slot table while the AGA State and
Screen still exist. Then call the fully verified existing P0c/P0d public
Screen Close bridge (Chip/Blitter cleanup, original native Close).
NO installed Lib / actual AMOS Compiler / WinUAE claim.
"""
from __future__ import annotations

from m68k_emit import Code,D
from m19_p0e_split_bridge_emit import emit_split_bobs_public


def emit_split_with_close(*, put_offset: int|None=None) -> tuple[bytes,dict[str,int]]:
    base,lab=emit_split_bobs_public(put_offset=put_offset)
    c=Code()
    c.raw(base.hex())
    c.labels.update(lab)
    B,L=c.branch,c.label
    L('public_aga_p0e_close_entry')
    c.raw('48e7fffe')          # save ALL D0-D7/A0-A6 like old Close ABI
    B(1,'relay_reset_entry')
    c.tst(D(3));B(7,'p0e_close_return')  # no half-close if reset failed
    B(1,'screen_close_bridge_entry')    # real P0d close (Chip then AGA)
    L('p0e_close_return')
    c.raw('4cdf7fff')
    c.raw('4e75')
    result=c.out()
    assert result.startswith(base)
    assert c.labels['public_aga_p0e_close_entry']==len(base)
    assert len(result)%2==0 and len(result)<32766
    return result,c.labels


if __name__=='__main__':
    from hashlib import sha256
    result,labels=emit_split_with_close()
    print('M19 P0e SOURCE ONLY reset-before-Close',
          len(result),len(result)-labels['public_aga_p0e_close_entry'],
          sha256(result).hexdigest())
