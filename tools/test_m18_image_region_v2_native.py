#!/usr/bin/env python3
"""R82 image Region v1/v2: real 68020 pixel/ABI and ModeID Gate A.

Only OS ModeID query is trap-backed. The exact R60 region RLE/painter
executes as generated native instructions. No installable build claimed.
"""
from __future__ import annotations

from hashlib import sha256
from unittest.mock import patch
from machine68k import CPUType, Register

import test_opt020_p1e_region as legacy
from test_opt020_p1e_region import LiveRegionCPU
GFX=0x34b00
SCREEN=0x34a00
from m16_agapic import pack_image
from m16_agapic_v2 import pack_image_v2, parse_payload_any
from m18_image_region_v2_emit import emit_image_region_v2, LVO_GETVPMODEID, GETADR_MARKER

MODE_ID=0x00021000
ORIGINAL_EXPECTED=legacy.expected_planes


class ImageRegionV2CPU(LiveRegionCPU):
    def __init__(self,native,payload,depth,mode_id=MODE_ID,*,cpu=CPUType.M68020):
        super().__init__(cpu,native,payload,base=0x1c000,depth=depth,
                         front=0,bank_flag=0,draw_api=False,
                         attnflags=2 if cpu==CPUType.M68020 else 0)
        self.mode_id=mode_id
        self.mode_calls=0
        self._trap(GFX+LVO_GETVPMODEID,self.mode_query)

    def mode_query(self,_opcode,_pc):
        self.mode_calls+=1
        assert self.cpu.r_reg(Register.A0)==SCREEN+44
        self.return_to_caller(self.mode_id)


def expected_v2(back,payload,sx,sy,w,h,x,y,mode,**kw):
    info=parse_payload_any(payload)
    return ORIGINAL_EXPECTED(back,info.image.raw,sx,sy,w,h,x,y,mode,**kw)


def run_case(native,payload,depth,*,sx=3,sy=2,w=18,h=9,x=7,y=11,
             mode=0,screen_mode=MODE_ID,ok=True,cpu=CPUType.M68020):
    machine=ImageRegionV2CPU(native,payload,depth,screen_mode,cpu=cpu)
    try:
        with patch.object(legacy,'expected_planes',expected_v2):
            machine.run(bank=10,sx=sx,sy=sy,w=w,h=h,x=x,y=y,
                        mode=mode,expect_ok=ok)
        assert machine.bank_calls==int(cpu==CPUType.M68020)
        if ok:
            assert machine.mode_calls==int(parse_payload_any(payload).version==2)
        else:
            assert machine.mode_calls<=1
        return 1
    finally:
        machine.close()


def main():
    native,labels=emit_image_region_v2()
    assert native==emit_image_region_v2()[0]
    assert native.count(GETADR_MARKER)==1
    assert native.count(bytes.fromhex('4eaefce8'))==1
    assert 1700<len(native)<5000 and len(native)%2==0
    assert labels['header_v1']<labels['row_begin']<labels['paint_group']
    count=0
    for depth in (4,8):
        w,h=31,15
        pixels=bytes((7*i+3*(i//w)) % (1<<depth) for i in range(w*h))
        mask=bytes((i%4)!=0 for i in range(w*h))
        pal=bytes((i*13+depth)&255 for i in range(3*(1<<depth)))
        for masked in (False,True):
            m=mask if masked else None
            v1=pack_image(w,h,depth,pixels,m)
            v2=pack_image_v2(w,h,depth,pixels,pal,MODE_ID,m)
            for mode in ((0,1) if masked else (0,)):
                for x,y in ((0,0),(7,11),(-9,-4),(57,39)):
                    count+=run_case(native,v1,depth,x=x,y=y,mode=mode)
                    count+=run_case(native,v2,depth,x=x,y=y,mode=mode)
                count+=run_case(native,v2,depth,mode=mode,
                                screen_mode=MODE_ID+1,ok=False)
    pix=bytes((i*7)&15 for i in range(31*15))
    pal=bytes((i*3)&255 for i in range(48))
    src=pack_image_v2(31,15,4,pix,pal,MODE_ID)
    for off,width,value in ((6,2,3),(8,2,0),(32,4,0),
                            (32,4,0xffffffff),(36,2,5),(38,2,2),
                            (40,4,0),(44,4,0),(48,4,0),
                            (52,4,1),(56,4,1),(60,4,1),
                            (20,4,32),(24,4,0)):
        bad=bytearray(src)
        bad[off:off+width]=value.to_bytes(width,'big')
        count+=run_case(native,bytes(bad),4,ok=False)
    count+=run_case(native,src,4,ok=False,cpu=CPUType.M68000)
    count+=run_case(native,src,4,ok=False,sx=30,w=4)
    print('R82 IMAGE REGION v1/v2 MC68020 GATE A PASS',count,
          'native cases; code bytes',len(native),
          'mode, crop, pixel, mask, RLE and CPU000 guards')


if __name__=='__main__': main()
