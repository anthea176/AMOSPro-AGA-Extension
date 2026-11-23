#!/usr/bin/env python3
"""Deterministic S1-P1e 320x256 8-plane ILBM, RGB24 CMAP capture fixture.

Three 16x16 zones: x13 has 3 opaque colors, x80 has 3 distinct opaque
colors, x48 has 4 opaque colors and MUST be rejected by S1.
Never distributed as an end-user example; generate under tests/proto/.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from

W,H,DEPTH,BPR=320,256,8,40
SHA256='b39aa201dddd878405c828687973b3b874ae5d0f8cc1f09d1617dda7ff0628b9'
NAME='AGSP_CAPTURE_320X256.iff'
DEFAULT=Path(__file__).resolve().parents[1]/'tests/proto/agsp_capture'/NAME
PALETTE=((0,0,0),(255,70,40),(36,220,117),(26,115,255),(255,230,16))


def pixel(x:int,y:int)->int:
    if 5<=y<21:
        if 13<=x<29:
            return (x-13+y-5)%4
        if 80<=x<96:
            return (3*(x-80)+y-5)%4
        if 48<=x<64:
            return 1+((x-48+y-5)%4)
    return 0


def packbits(data:bytes)->bytes:
    out=bytearray()
    i=0
    while i<len(data):
        run=1
        while i+run<len(data) and data[i+run]==data[i] and run<128:
            run+=1
        if run>=3:
            out.extend((257-run,data[i]))
            i+=run
            continue
        start=i
        i+=run
        while i<len(data) and i-start<128:
            match=1
            while i+match<len(data) and data[i+match]==data[i] and match<128:
                match+=1
            if match>=3 or i-start+match>128:
                break
            i+=match
        chunk=data[start:i]
        out.append(len(chunk)-1)
        out.extend(chunk)
    return bytes(out)


def unpackbits(data:bytes,expected:int)->tuple[bytes,int]:
    out=bytearray()
    i=0
    while len(out)<expected:
        control=data[i]
        i+=1
        if control<128:
            n=control+1
            out.extend(data[i:i+n])
            i+=n
        elif control>128:
            n=257-control
            out.extend(bytes((data[i],))*n)
            i+=1
    assert len(out)==expected
    return bytes(out),i


def chunk(name:bytes,payload:bytes)->bytes:
    assert len(name)==4
    return name+pack('>I',len(payload))+payload+bytes(len(payload)&1)


def build()->bytes:
    bmhd=pack('>HHhhBBBBHBBhh',W,H,0,0,DEPTH,0,1,0,0,1,1,W,H)
    assert len(bmhd)==20
    cmap=bytes(v for color in PALETTE for v in color)+bytes((256-len(PALETTE))*3)
    body=bytearray()
    uncompressed=bytearray()
    for y in range(H):
        line=[pixel(x,y) for x in range(W)]
        for plane in range(DEPTH):
            bits=bytearray(BPR)
            for x,index in enumerate(line):
                if index&(1<<plane):
                    bits[x>>3]|=1<<(7-(x&7))
            raw=bytes(bits)
            uncompressed.extend(raw)
            compressed=packbits(raw)
            check,used=unpackbits(compressed,BPR)
            assert used==len(compressed) and check==raw
            body.extend(compressed)
    form_data=(b'ILBM'+chunk(b'BMHD',bmhd)+chunk(b'CMAP',cmap)
               +chunk(b'CAMG',pack('>I',0))+chunk(b'BODY',bytes(body)))
    result=b'FORM'+pack('>I',len(form_data))+form_data
    assert unpack_from('>I',result,4)[0]==len(result)-8
    assert len(uncompressed)==W*H
    for x,ncolors in ((13,3),(48,4),(80,3)):
        colors={pixel(px,py) for py in range(5,21) for px in range(x,x+16)}
        opaque=colors-({0} if x!=48 else set())
        assert len(opaque)==ncolors
    assert len(result)==5428 and sha256(result).hexdigest()==SHA256
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--output',type=Path,default=DEFAULT)
    args=parser.parse_args()
    result=build()
    if args.check:
        assert args.output.read_bytes()==result, 'ILBM data differ from pinned model'
        print('S1_P1E_ILBM_BYTE_EXACT_PASS',len(result),SHA256)
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_bytes(result)
        print('S1_P1E_ILBM_WRITTEN',len(result),SHA256,args.output)


if __name__=='__main__':
    main()
