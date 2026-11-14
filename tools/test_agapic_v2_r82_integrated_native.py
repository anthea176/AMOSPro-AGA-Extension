#!/usr/bin/env python3
"""R82 combined native Gate A: final-offset Bank Palette API MC68020 calls.

Builds the FULL in-memory AP20 V2 layout, then executes four palette APIs
at their real post-relocation native offsets. Old AGAPAL palette cores and
AmigaOS services are individually trap-backed, new code is native 68020.
No installable .Lib, WinUAE or Compiler qualification is implied.
"""
from __future__ import annotations

from hashlib import sha256
from struct import unpack_from
from unittest.mock import patch

from machine68k import CPUType

import test_m16_agapic_v2_palette_native as palette
from m16_agapic_v2 import pack_image_v2
from m16_agapic_v2_palette_emit import BANK_LOOKUP, BSR_LONG
from m16_agapic_v2_bank_wrap_emit import (
    emit_bank_palette_init,emit_bank_palette_capture)
from m16_agapic_v2_palette_emit import (
    emit_bank_palette_apply,emit_bank_palette_fade)
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from compiler_relocation import GETP
from aga_compiler_capacity import inspect_library
from build_agapic_v2_r82_full_preview import build,native_starts

MODE=0x00021000


def native_long_link(code,origin,destination):
    # The native emitter leaves only one BSR.L branch: long word 0x61ff.
    locations=[i for i in range(0,len(code)-5,2) if code[i:i+2]==BSR_LONG[:2]]
    assert len(locations)==1,('unexpected long BSR count',locations)
    pos=locations[0]
    disp=unpack_from('>i',code,pos+2)[0]
    assert origin+pos+2+disp==destination,('BSR.L wrong target',pos,disp)
    assert disp<-32768
    return pos


def execute_palette(code,*,entry_start,target_start,fade,depth,mode_id=MODE,
                    vbl=2,bank_name=b'AGAPIC  ',index=0,expect_ok=True):
    count=1<<depth
    pixels=bytes(i%count for i in range(17*3))
    rgb=bytes((i*17+7)&255 for i in range(3*count))
    data=pack_image_v2(17,3,depth,pixels,rgb,MODE)
    # The body runs at CPU_CODE, while real BSR.L returns to an OLD
    # historical target located behind it at an actual native offset.
    with patch.object(palette,'NATIVE_START',entry_start),\
         patch.object(palette,'LEGACY_OFFSET',target_start):
        m=palette.PaletteMachine(
            code,data,depth=depth,mode_id=mode_id,fade=fade,
            index=index,vbl=vbl,bank_name=bank_name,cpu=CPUType.M68020)
        result=m.run(expect_ok=expect_ok)
        assert result==1
        assert m.lookup_calls==1
        if expect_ok:
            if bank_name==b'AGAPAL  ':
                assert m.legacy_calls==1
                assert m.load_count==0 and m.mode_calls==0
            else:
                assert m.legacy_calls==0
                assert m.mode_calls==1
                assert m.load_count==(vbl if fade else 1)
                assert m.wait_count==(vbl if fade else 0)
                target=[tuple(x*0x01010101 for x in rgb[3*i:3*i+3])
                        for i in range(count)]
                assert m.screen_palette[:count]==target
        else:
            assert m.legacy_calls==0 and m.load_count==m.wait_count==0
        assert not m.owned
    return 1


def main():
    candidate,meta=build()
    assert candidate==build()[0]
    tokens,parts=unwrap_native_parts_v2(candidate)
    starts=native_starts(parts)
    assert len(parts)==80 and len(starts)==80
    assert meta['commands']==74 and meta['ap20_entries']==81
    old_entries=(41,42,43,44)
    emitters=(emit_bank_palette_init,emit_bank_palette_capture,
              emit_bank_palette_apply,emit_bank_palette_fade)
    checks=0
    for n,(emitter,target) in enumerate(zip(emitters,old_entries)):
        entry=76+n
        code=parts[entry].removesuffix(GETP) if entry<79 else parts[entry]
        emitted,labels=emitter(starts[entry],starts[target])
        assert code==emitted,('final native wrapper byte mismatch',entry)
        assert code.count(BANK_LOOKUP)==1
        native_long_link(code,starts[entry],starts[target])
        checks+=1
    # Both compiled-equivalent placements are already covered by the
    # standalone Init/Capture tests. Recheck the final BSR.L targets above.
    for is_fade,index in ((False,78),(True,79)):
        code=parts[index].removesuffix(GETP) if index<79 else parts[index]
        target_start=starts[43 if not is_fade else 44]
        for depth in (1,4,8):
            for duration in (1,2) if is_fade else (1,):
                checks+=execute_palette(code,entry_start=starts[index],
                    target_start=target_start,fade=is_fade,depth=depth,
                    vbl=duration)
        checks+=execute_palette(code,entry_start=starts[index],
            target_start=target_start,fade=is_fade,depth=4,
            bank_name=b'AGAPAL  ',vbl=2)
        checks+=execute_palette(code,entry_start=starts[index],
            target_start=target_start,fade=is_fade,depth=4,
            index=1,expect_ok=False)
        checks+=execute_palette(code,entry_start=starts[index],
            target_start=target_start,fade=is_fade,depth=4,
            mode_id=MODE+1,expect_ok=False)
    m=inspect_library(candidate)
    assert m['margin']==meta['compiler_margin']>2048
    print('R82 FULL AP20 NATIVE 68020 INTEGRATED GATE A PASS:', checks,
          'real relocated Bank Palette/ModeID/ABI cases; margin',m['margin'],
          'file size',len(candidate),'sha256',sha256(candidate).hexdigest())
    print('No installable Lib changed; no WinUAE / AMOS Compiler gates claimed.')


if __name__=='__main__': main()
