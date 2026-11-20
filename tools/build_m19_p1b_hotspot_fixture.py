#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1b: deterministic 8x6 AGBO v1 masked Bob with HOTSPOT +4,+3.

The ONE active ASC can load this AmBk 26 resource for a real WinUAE
hotspot visual test. The file is not a native library, and no AMOS source
or current/passed test is changed by this generator.
"""
from __future__ import annotations
from hashlib import sha256
from m19_p0a_multi_bob_abk import empty_bank,put_image,set_hotspot,make_abk,parse_abk,parse_payload

BANK=26
NAME='M19_P1B_HOTSPOT_BANK26.abk'
ROWS=(
  (0,0,5,5,5,5,0,0),
  (0,5,4,4,4,4,5,0),
  (5,4,0,4,4,0,4,5),
  (5,4,0,4,4,0,4,5),
  (0,5,4,4,4,4,5,0),
  (0,0,5,5,5,5,0,0),
)
PIXELS=bytes(v for row in ROWS for v in row)
VISIBLE=bytes(1 if x else 0 for x in PIXELS)
def fixture()->bytes:
    payload=put_image(empty_bank(),1,8,6,8,PIXELS,visibility=VISIBLE)
    payload=set_hotspot(payload,1,4,3)
    image=parse_payload(payload).image(1)
    assert image.mask is not None and image.hotspot_x==4 and image.hotspot_y==3
    assert len(payload)==180
    raw=make_abk(BANK,payload)
    n,flags,bank=parse_abk(raw)
    assert n==BANK and flags==1 and bank.image(1)==image
    assert len(raw)==200
    return raw

if __name__=='__main__':
    import base64
    raw=fixture()
    s=base64.b64encode(raw).decode('ascii')
    print('P1B_FIXTURE_BEGIN',len(raw),sha256(raw).hexdigest(),len(s),flush=True)
    for i in range(0,len(s),512):
        print('P1B_FIXTURE_CHUNK',i//512,s[i:i+512],flush=True)
    print('P1B_FIXTURE_END',len(s),flush=True)
