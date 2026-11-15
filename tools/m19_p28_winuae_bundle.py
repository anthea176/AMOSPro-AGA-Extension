#!/usr/bin/env python3
"""Generate exact R88 WinUAE AGAPIC/AGPC bank fixtures and experimental bundle.

This code writes to the explicitly supplied output directory, never dist/.
Generated fixture data belongs to the test; only experimental R88 library.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from m16_agapic import pack_image, make_abk, parse_abk
from m16_agapic_v2 import pack_image_v2, make_abk_v2, parse_abk_any
from m19_p28_agapic_planar_cache import make_cache_abk, parse_cache_abk
from build_m19_p28_r88_in_memory import build

MODE = 0x00021000
PIXELS = bytes(0 if (x + y) % 7 == 0 else (7*x + 13*y) & 255
               for y in range(16) for x in range(16))
ALPHA = bytes(0 if (x + y) % 13 == 0 or (3*x + 5*y) % 11 == 0 else 1
              for y in range(16) for x in range(16))
PALETTE = bytes((3*i+7)&255 for i in range(768))


def assets() -> dict[str, bytes]:
    assert any(p == 0 and a for p,a in zip(PIXELS,ALPHA))
    assert any(p != 0 and not a for p,a in zip(PIXELS,ALPHA))
    v1=pack_image(16,16,8,PIXELS,ALPHA)
    v2=pack_image_v2(16,16,8,PIXELS,PALETTE,MODE,ALPHA)
    f={
      'AGAPIC_P28_V1_BANK10.abk':make_abk(10,v1),
      'AGPC_P28_V1_BANK11.abk':make_cache_abk(v1,11,chip=True),
      'AGAPIC_P28_V2_BANK12.abk':make_abk_v2(12,v2),
      'AGPC_P28_V2_BANK13.abk':make_cache_abk(v2,13,chip=True),
    }
    b10,_,src1=parse_abk(f['AGAPIC_P28_V1_BANK10.abk'])
    b12,_,src2=parse_abk_any(f['AGAPIC_P28_V2_BANK12.abk'])
    assert (b10,b12)==(10,12)
    for name,source,num in [('AGPC_P28_V1_BANK11.abk',v1,11),
                             ('AGPC_P28_V2_BANK13.abk',v2,13)]:
        bank,flags,snap=parse_cache_abk(f[name],expected_source=source)
        assert bank==num and flags==3 and snap.raw.__len__()==360
        assert snap.width==snap.height==16 and snap.depth==8
        assert snap.generation==1 and snap.has_mask
        assert snap.native_chip_slot_16x16x8(mode=1,screen_mode_id=MODE)==snap.raw[72:360]
        for y in range(16):
            for x in range(16):
                i=16*y+x
                assert snap.colour(x,y)==PIXELS[i]
                assert snap.visible(x,y)==bool(ALPHA[i])
    assert src1.width==16 and src2.image.width==16
    assert len(f['AGPC_P28_V1_BANK11.abk'])==380
    assert len(f['AGPC_P28_V2_BANK13.abk'])==380
    return f


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--asc',type=Path,required=True)
    args=parser.parse_args()
    out=args.out
    out.mkdir(parents=True,exist_ok=True)
    for name,raw in assets().items():
        (out/name).write_bytes(raw)
        print('BANK FIXTURE',name,len(raw),sha256(raw).hexdigest())
    library,meta=build()
    assert len(library)==75040
    assert sha256(library).hexdigest()=='69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc'
    (out/'AMOSPro_AGA.Lib').write_bytes(library)
    asc=args.asc.read_bytes()
    assert asc.startswith(b"' M19 P2.8 R88 ")
    (out/args.asc.name).write_bytes(asc)
    (out/'README_P28.txt').write_text(
        'M19 P2.8 - R88 v0.13.33 EXPERIMENT ONLY. NOT LAST_GOOD.\n'
        'Copy AMOSPro_AGA.Lib temporarily to the AGA APSystem extension slot,\n'
        'restart AMOS; R87 is archived and R84 LAST_GOOD protected.\n'
        'Put four ABK files in the same current directory as the AMOS test.\n'
        'In an empty AMOS program: Project -> Merge ASCII -> '+args.asc.name+'\n'
        'Run Runtime then COMPILE THE SAME PROGRAM using AMOS Compiler V2.\n'
        'Collect RAM:M19_P28_RUNTIME.TXT and RAM:M19_P28_COMPILED.TXT.\n'
        'R88 is the active unpromoted GitHub candidate; R84 LAST_GOOD unchanged.\n'
        'Library SHA256 '+meta['sha256']+'\n',encoding='ascii')
    print('R88 GATE A ONLY BUNDLE READY:',out,len(library),meta['sha256'])


if __name__=='__main__':
    main()
