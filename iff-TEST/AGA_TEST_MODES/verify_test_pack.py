#!/usr/bin/env python3
"""Independent structural and planar check for the shipped ILBM fixtures.
Does not import the fixture generator. Stdlib only (preview PNG not decoded).
"""
from pathlib import Path
import hashlib
import json
import struct

ROOT=Path(__file__).resolve().parent
EXPECTED={
    'HAM6_PAL_320x256.iff':(320,256,6,0x00021800,16),
    'HAM8_PAL_320x256.iff':(320,256,8,0x00021800,64),
    'SHIRES_PAL_1280x256.iff':(1280,256,4,0x00029020,16),
    'SHIRES_LACE_PAL_1280x512.iff':(1280,512,4,0x00029024,16),
    'DBLPAL_320x256.iff':(320,256,4,0x000A1000,16),
    'DBLNTSC_320x200.iff':(320,200,4,0x00091000,16),
}

def parse_file(data):
    assert data[:4]==b'FORM' and data[8:12]==b'ILBM'
    assert len(data)-8==int.from_bytes(data[4:8],'big')
    chunks={}
    pos=12
    while pos<len(data):
        assert pos+8<=len(data)
        name=data[pos:pos+4]
        size=struct.unpack_from('>I',data,pos+4)[0]
        value=data[pos+8:pos+8+size]
        assert len(value)==size and name not in chunks
        chunks[name]=value
        pos+=8+size+(size&1)
    assert pos==len(data) and set(chunks)=={b'BMHD',b'CMAP',b'CAMG',b'BODY'}
    return chunks

def check_body(body,rb,depth,height):
    at=0
    index_or=0
    for _ in range(height):
        for p in range(depth):
            row=bytearray()
            while len(row)<rb:
                assert at<len(body),'truncated run'
                v=body[at];at+=1
                signed=v if v<128 else v-256
                if signed>=0:
                    n=signed+1
                    assert at+n<=len(body) and len(row)+n<=rb
                    row+=body[at:at+n];at+=n
                elif signed!=-128:
                    n=1-signed
                    assert at<len(body) and len(row)+n<=rb
                    row+=body[at:at+1]*n;at+=1
            index_or|=int(any(row))<<p
    assert at==len(body),(at,len(body))
    assert index_or!=0,'all planes empty'
    return at

def main():
    recs=json.loads((ROOT/'manifest.json').read_text(encoding='utf8'))
    assert len(recs)==len(EXPECTED)
    for row in recs:
        name=row['file']
        assert name in EXPECTED and (ROOT/name).exists()
        data=(ROOT/name).read_bytes()
        chunks=parse_file(data)
        meta=struct.unpack('>HHhhBBBBHBBhh',chunks[b'BMHD'])
        w,h,d=meta[0],meta[1],meta[4]
        mode=struct.unpack('>I',chunks[b'CAMG'])[0]
        assert meta[5]==0 and meta[6]==1,('masking/compression',name)
        assert (w,h,d,mode,len(chunks[b'CMAP'])//3)==EXPECTED[name]
        assert hashlib.sha256(data).hexdigest()==row['sha256']
        body=chunks[b'BODY']
        assert check_body(body,((w+15)//16)*2,d,h)==len(body)
        if name.startswith('HAM'):
            assert mode&0x800
            assert d in (6,8)
            ops=row['op_counts']
            assert all(int(ops.get(str(i),0))>=100 for i in range(4))
        assert (ROOT/row['reference_png']).exists()
        print('PASS',name,'CAMG',hex(mode), 'bytes',len(data))
    print('PASS all',len(recs),'ILBM files; no WinUAE runtime implied')

if __name__=='__main__':
    main()
