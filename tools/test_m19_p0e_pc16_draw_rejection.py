#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e negative AP20 Gate A: prohibit naive extra Draw token.

The public two-operation candidate has PC16 reach 32760 from reserved
entry #0, the native AGA Init/dispatcher anchor. An 8-byte additional
public RBSR Draw stub necessarily moves its AGA group forward and makes
the signed AMOS365 GRouB BSR.W displacement 32768, OUT OF RANGE.
No Draw is implemented or installed here; this is a structural refusal
test, not a valid alternative API candidate or an emulated Compiler.
"""
from __future__ import annotations
from struct import pack,unpack_from
from compiler_relocation import RBSR,GETP,unpack_ap20
from build_m19_p0e_public_object_ops_in_memory import build
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements


def main():
    raw,meta=build()
    _,parts,_=unpack_ap20(raw)
    assert meta['public_commands']==85 and meta['ap20_entries']==95
    assert len(parts)==95 and parts[0][:2]==RBSR
    assert meta['new_pc16_reach']==32760
    assert meta['worst_stub_displacements'][0]==(0,32760)
    # Reshuffle ONLY an IN-MEMORY list of AP20 stubs, never a .Lib.
    # Insert the MINIMAL eight-byte RBSR for the third token (without any
    # native Draw implementation). This must already be rejected.
    shifted=[]
    for index,part in enumerate(parts[:91]):
        if part in (b'',GETP):
            shifted.append(part)
        else:
            if part[:2]!=RBSR or len(part) not in (8,12):
                raise AssertionError(('unexpected old stub',index))
            group,offset=unpack_from('>HH',part,2)
            assert group in (91,92,93,94)
            shifted.append(RBSR+pack('>HH',group+1,offset)+part[6:])
    stub=RBSR+pack('>HH',94,0)+bytes.fromhex('4e75')
    layout=shifted+[stub]+parts[91:]
    assert len(layout)==96 and len(stub)==8
    try:
        interpreter_rbsr_displacements(layout)
    except ValueError as exc:
        assert 'entry 0 displacement 32768' in str(exc),str(exc)
    else:
        raise AssertionError('unsafe signed PC16 layout falsely accepted')
    print('M19 P0e PC16 DRAW APPEND REFUSAL PASS:',
          'reserved stub 0 32760 + minimal new Draw stub 8 = 32768;',
          'new V2 group partition is mandatory; NO Draw token emitted')


if __name__=='__main__':
    main()
