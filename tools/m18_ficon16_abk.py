#!/usr/bin/env python3
"""M18/R61 8-plane Unity-style Fast Icon AMOS DATA bank (.abk) host utility.

Bank name 'FICON8  ', inner payload 12 + count*288. AmBk envelope follows
the proven M16 AGAPIC data bank format. Host validation only; native Load
under WinUAE needs separate Gates B/C. Flag=1 expresses Fast preference,
not a guarantee of actual allocation in Fast RAM.
"""
from __future__ import annotations
import argparse,base64
from hashlib import sha256
from struct import Struct
from m18_ficon16_model import build_bank,parse_bank

ABK_HEADER=Struct(">4sHHI8s")
BANK_NAME=b"FICON8  "
BANK_NO=10

def make_abk(bank:int,payload:bytes,*,chip:bool=False)->bytes:
    if type(bank) is not int or not 5<=bank<=65535:
        raise ValueError("AMOS DATA bank number 5..65535 required")
    parse_bank(payload)    # validates ALL icon masks & full size
    return (ABK_HEADER.pack(b"AmBk",bank,3 if chip else 1,
                            len(payload)+8,BANK_NAME)+payload)

def parse_abk(raw:bytes):
    if type(raw) is not bytes or len(raw)<ABK_HEADER.size:
        raise ValueError("short AMOS Fast Icon ABK")
    magic,number,flags,length,name=ABK_HEADER.unpack_from(raw)
    if (magic!=b"AmBk" or not 5<=number<=65535 or flags not in (1,3)
        or length!=len(raw)-12 or name!=BANK_NAME):
        raise ValueError("invalid AMOS Fast Icon DATA ABK")
    return number,flags,parse_bank(raw[ABK_HEADER.size:])

def sample_icons()->tuple[bytes,...]:
    return (
      bytes([0]*256),
      bytes([255]*256),
      bytes((3*x+5*y)&255 for y in range(16) for x in range(16)),
      bytes(((x*11+y*7)&255) if (x+y)%4 else 0
            for y in range(16) for x in range(16)),
    )

def binary()->bytes:
    return make_abk(BANK_NO,build_bank(sample_icons()))

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    parser.add_argument("--write",type=str,default=None)
    args=parser.parse_args()
    raw=binary()
    assert parse_abk(raw)[2].count==4
    print("M18 FICON8 SAMPLE",len(raw),"SHA256",sha256(raw).hexdigest())
    if args.write:
        from pathlib import Path
        Path(args.write).write_bytes(raw)
    if args.emit_base64:
        code=base64.b64encode(raw).decode("ascii")
        print("M18_FICON_ABK_BASE64_BEGIN")
        for pos in range(0,len(code),120):
            print("M18_FICON_ABK_BASE64",code[pos:pos+120])
        print("M18_FICON_ABK_BASE64_END")
if __name__=="__main__":
    main()
