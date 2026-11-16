#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e source-only first two PUBLIC object-op shims, MC68020 minimum.

These are exact AMOS Professional numeric *instruction* argument wrappers.
They call the P0e PRIVATE BOBS->AGA bridge, which retains its validated
signature/owner/CPU checks and full object table; no public Draw exists yet.

  Aga Bob N,X,Y,I : D3=I, (A3)+ = Y, X, N. Saves D0/D1/D4-D7/A0-A2/A4-A6,
                    advances A3 exactly 12 bytes, D2=0, D3=success 1/0.
  Aga Bob Off N   : D3=N, preserves D0 and all other AMOS registers,
                    A3 unchanged, D2=0, D3=success 1/0.

The linked compiler V2 BOBS unit is near its signed PC16 limit; MUST
measure real displacements after adding two new AP20 stubs. Never append
more native code without rewriting that layout and passing CPU/ABI gates.
No installed .Lib, new active ASC, graphics drawing, or WinUAE claim.
"""
from __future__ import annotations

from m68k_emit import Code,D,POST
from m19_p0e_v2_object_bridge_emit import emit_v2_object_bridge


def emit_public_object_ops() -> tuple[bytes,dict[str,int]]:
    old,old_labels=emit_v2_object_bridge()
    c=Code()
    c.raw(old.hex())
    c.labels.update(old_labels)
    B,L=c.branch,c.label

    L('public_aga_bob_entry')
    c.raw('48e7efee')             # MOVEM.L AMOS preserved set,-(SP)
    c.move(D(3),D(4))            # image I from last parameter
    c.move(POST(3),D(6))         # Y (stacked third argument)
    c.move(POST(3),D(5))         # X
    c.move(POST(3),D(0))         # N
    B(1,'object_bridge_put_selected_entry')
    c.raw('4cdf77f7')             # restore D0/D1/D4-D7/A0-A2/A4-A6
    c.raw('74004e75')             # D2=0, RTS; D3 carries object status

    L('public_aga_bob_off_entry')
    c.raw('2f00')                 # MOVE.L D0,-(SP)
    c.move(D(3),D(0))            # N is the last/only AMOS argument
    B(1,'object_bridge_off_entry')
    c.raw('201f')                 # MOVE.L (SP)+,D0
    c.raw('74004e75')             # D2=0, RTS; D3 carries status

    blob=c.out()
    assert blob[:len(old)]==old
    assert c.labels['public_aga_bob_entry']==len(old)
    assert c.labels['public_aga_bob_off_entry']>len(old)
    assert len(blob)%2==0 and len(blob)<32766
    assert len(blob)-len(old)<=40, 'PC16 budget demands a compact thunk'
    return blob,c.labels


if __name__=='__main__':
    from hashlib import sha256
    data,labels=emit_public_object_ops()
    print('M19 P0e 020 PUBLIC OBJECT-SET/OFF SHIMS SOURCE ONLY',
          len(data),len(data)-labels['public_aga_bob_entry'],
          sha256(data).hexdigest(),
          'NO Draw / Close-reset / installed Lib / WinUAE')
