#!/usr/bin/env python3
"""Build M5.3 RAW ILBM fixtures from validated ByteRun1 originals."""
from pathlib import Path
import hashlib, struct

ROOT=Path(__file__).resolve().parents[1]
CASES=(
    ('Clown.iff','Clown_RAW.iff','8a7cb07f1936fc39d93b1ffc39a54a33336cab304d3a9ce1a4787ef1b54c915e'),
    ('KEKKO.IFF','KEKKO_RAW.IFF','fbd1d7e23972959bb145b01b9ad305de9b2cb966b506ea841e6c15beb3578899'),
)

def be32(b,p): return struct.unpack_from('>I',b,p)[0]
def put32(n): return struct.pack('>I',n)

def chunks(raw):
    assert raw[:4]==b'FORM' and raw[8:12]==b'ILBM'
    end=8+be32(raw,4)
    p=12
    out=[]
    while p<end:
        assert p+8<=end
        ident=raw[p:p+4]
        size=be32(raw,p+4)
        ds=p+8
        de=ds+size
        assert de+(size&1)<=end
        out.append((ident,bytearray(raw[ds:de])))
        p=de+(size&1)
    assert p==end
    return out

def decode_byterun(body,height,depth,rowbytes):
    src=0
    out=bytearray()
    for _ in range(height*depth):
        written=0
        while written<rowbytes:
            assert src<len(body)
            n=body[src]; src+=1
            if n<=127:
                count=n+1
                assert src+count<=len(body)
                assert written+count<=rowbytes
                out += body[src:src+count]
                src += count
                written += count
            elif n>=129:
                count=257-n
                assert src<len(body)
                assert written+count<=rowbytes
                out += bytes([body[src]])*count
                src += 1
                written += count
            # 128 = NOP
        assert written==rowbytes
    assert src==len(body)
    return out

def build_one(src_path,dst_path):
    raw=src_path.read_bytes()
    ch=chunks(raw)
    bmhd=next(data for ident,data in ch if ident==b'BMHD')
    body=next(data for ident,data in ch if ident==b'BODY')
    width,height=struct.unpack_from('>HH',bmhd,0)
    depth=bmhd[8]
    assert bmhd[9]==0 and bmhd[10]==1
    rowbytes=((width+15)//16)*2
    raw_body=decode_byterun(body,height,depth,rowbytes)

    payload=bytearray(b'ILBM')
    for ident,data in ch:
        data=bytearray(data)
        if ident==b'BMHD':
            data[10]=0
        elif ident==b'BODY':
            data=raw_body
        payload += ident + put32(len(data)) + data
        if len(data)&1:
            payload += b'\0'

    out=b'FORM'+put32(len(payload))+payload
    dst_path.write_bytes(out)
    return out

def main():
    for src_name,dst_name,expected in CASES:
        out=build_one(ROOT/src_name,ROOT/dst_name)
        got=hashlib.sha256(out).hexdigest()
        assert got==expected,(dst_name,got)
        print(dst_name,len(out),got)

if __name__=='__main__':
    main()
