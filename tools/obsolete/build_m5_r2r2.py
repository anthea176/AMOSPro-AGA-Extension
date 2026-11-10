#!/usr/bin/env python3
"""M5 R2R2 - fix ByteRun1 negative-run counter width."""
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.2_R2R2.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
OUT_SHA='dd84ed3ff713a6508bb1d3dc3abd6d2bcc2d8b896e2c1280ea30f928a28a45de'

def build():
    from build_m5_r2r1 import build as build_r2r1
    out=bytearray(build_r2r1())

    hits=[i for i in range(len(out)-1) if out[i:i+2]==b'\x44\x40']
    assert hits==[3442], hits
    out[3442:3444]=b'\x44\x80'  # NEG.W D0 -> NEG.L D0

    for old,new in (
        (b'R2R1',b'R2R2'),
        (b'0.2.1',b'0.2.2'),
        (b'0.2.1',b'0.2.2'),
    ):
        p=out.find(old)
        assert p>=0
        out[p:p+len(old)]=new

    out=bytes(out)
    assert len(out)==3708
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated test target',LIVE)
    print('Size',len(out))
    print('SHA256',OUT_SHA)
