#!/usr/bin/env python3
"""R82 prototype: REAL MC68020 AGAPIC v1/v2 image draw native CPU tests.

Standalone emitter only: no installed R82, no new public token, no build output,
no candidate .Lib, no AMOS/WinUAE/Compiler claim. The frozen R81 is untouched.
"""
from __future__ import annotations

import struct
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from machine68k import CPUType, Register
import test_opt020_p1e_region as legacy
from test_opt020_p1e_region import LiveRegionCPU
from m16_agapic import pack_image
from m16_agapic_v2 import pack_image_v2, parse_payload_any
from m16_agapic_v2_draw_emit import emit_image_draw_v2, LVO_GETVPMODEID

ROOT = Path(__file__).resolve().parents[1]
R81_SHA = '9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4'
from active_library import R82_SHA
MODE_ID = 0x00021000
GFX = 0x34b00
SCREEN = 0x34a00
BASE = 0x1c000
ORIGINAL_REFERENCE = legacy.expected_planes


class LiveV2CPU(LiveRegionCPU):
    def __init__(self, code, payload, depth, mode_id, *,
                 cpu=CPUType.M68020, **kw):
        super().__init__(cpu, code, payload, base=BASE, depth=depth, front=0,
                         bank_flag=0, draw_api=True,
                         attnflags=2 if cpu == CPUType.M68020 else 0, **kw)
        self.mode_id = mode_id
        self.mode_calls = 0
        self._trap(GFX + LVO_GETVPMODEID, self.get_vp_mode_id)

    def get_vp_mode_id(self, _opcode, _pc):
        self.mode_calls += 1
        assert self.cpu.r_reg(Register.A0) == SCREEN + 44
        self.return_to_caller(self.mode_id)


def expected(original, payload, sx, sy, w, h, x, y, mode, **kwargs):
    image = parse_payload_any(payload)
    return ORIGINAL_REFERENCE(original, image.image.raw, sx, sy, w, h,
                              x, y, mode, **kwargs)


def run_case(code, payload, depth, *, mode=0, screen_mode=MODE_ID,
             x=7, y=9, expected_ok=True, cpu=CPUType.M68020, **kw):
    source = parse_payload_any(payload) if expected_ok else None
    w = source.image.width if source else 17
    h = source.image.height if source else 7
    machine = LiveV2CPU(code, payload, depth, screen_mode, cpu=cpu, **kw)
    before = machine.snapshot()
    try:
        try:
            with patch.object(legacy, 'expected_planes', expected):
                machine.run(mode=mode, x=x, y=y, sx=0, sy=0, w=w, h=h,
                            expect_ok=expected_ok)
        except AssertionError:
            print('R82 rejection diagnostics:', {
                'source_version': int.from_bytes(payload[6:8], 'big'),
                'flags': int.from_bytes(payload[8:10], 'big'),
                'source_depth': depth,
                'mode_calls': machine.mode_calls,
                'type_calls': machine.type_calls,
                'getmsg_calls': machine.getmsg_calls,
                'palette_count': int.from_bytes(payload[36:38], 'big')
                    if len(payload) >= 38 else None,
                'payload_length': len(payload),
                'native_reject_stage': machine.cpu.r_reg(Register.D3)
            }, flush=True)
            raise
        assert machine.bank_calls == 0
        if expected_ok:
            assert machine.mode_calls == (1 if source.version == 2 else 0)
        else:
            assert machine.mode_calls <= 1
        if not expected_ok:
            assert machine.snapshot() == before
        return 1
    finally:
        machine.close()


def main():
    # Both INVALID_ID checks must use BEQ, not BNE (R82 regression).
    import inspect
    source = inspect.getsource(emit_image_draw_v2)
    assert source.count('c.imm("cmp",-1,D(0)); B(7,"reject")') == 2
    code, labels = emit_image_draw_v2()
    assert code == emit_image_draw_v2()[0], 'nondeterministic v2 emitter'
    assert len(code) % 2 == 0 and 1500 <= len(code) < 4500
    assert code.startswith(bytes.fromhex('48e7efee'))
    assert code.count(bytes.fromhex('4eaefce8')) == 1, 'GetVPModeID missing/wrong LVO'
    assert 'v2_screen_mode_ok' in labels and 'header_v1' in labels
    assert labels['paint_group'] < len(code)
    assert sha256((ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()).hexdigest() == R81_SHA
    assert sha256((ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()).hexdigest() in (R81_SHA,R82_SHA)
    count = 0
    for depth in (4, 8):
        w,h = 17,7
        pix = bytes((x * 7 + y * 3) % (1 << depth)
                    for y in range(h) for x in range(w))
        mask = bytes((x + y) % 3 != 0
                     for y in range(h) for x in range(w))
        palette = bytes((k * 11 + depth) & 255 for k in range(3 * (1 << depth)))
        for masked in (False,True):
            source_mask = mask if masked else None
            v1 = pack_image(w,h,depth,pix,source_mask)
            v2 = pack_image_v2(w,h,depth,pix,palette,MODE_ID,source_mask)
            for mode in ((0,1) if masked else (0,)):
                for x,y in ((0,0),(7,9),(-5,-4),(55,37)):
                    count += run_case(code,v1,depth,mode=mode,x=x,y=y)
                    count += run_case(code,v2,depth,mode=mode,x=x,y=y)
                count += run_case(code,v2,depth,mode=mode,screen_mode=MODE_ID+1,
                                  expected_ok=False)
    # Header corruption and strict rejection prior to any framebuffer write.
    palette = bytes(range(48))
    good = pack_image_v2(17,7,4,bytes((i%16) for i in range(119)),
                         palette,MODE_ID)
    for off,length,value in ((6,2,3),(8,2,0),(32,4,0),
                             (32,4,0xffffffff),(36,2,4),
                             (38,2,2),(40,4,65),(44,4,0),
                             (48,4,0),(52,4,1),(56,4,1),
                             (60,4,1),(20,4,32),(24,4,0)):
        broken=bytearray(good)
        broken[off:off+length]=int(value).to_bytes(length,'big')
        count += run_case(code,bytes(broken),4,expected_ok=False)
    count += run_case(code,good,4,expected_ok=False,cpu=CPUType.M68000)
    print('R82 AGAPIC v2 standalone native MC68020 Gate A PASS:',
          count, 'ABI/pixels/ModeID/rejections; native bytes',len(code))
    print('R81 unchanged; no AP20, WinUAE, AMOS Compiler or .Lib candidate')


if __name__ == '__main__':
    main()
