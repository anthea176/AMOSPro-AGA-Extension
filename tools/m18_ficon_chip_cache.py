#!/usr/bin/env python3
"""M18/P5 host contract for a persistent, AMOS-owned Chip Fast Icon cache.

An AMOS DATA bank named 'FICHIP8 ' with flags=3 owns *all* memory; the user
erases the bank normally. No native allocation, global pointers or leaks.
The cache is separate from either private AGA screen buffer and remains valid
across Swap, Screen Close and Screen Open until replaced/erased/re-staged.

Payload: 12-byte Unity-style header, count*288 bytes of cached slots,
then count validity bytes. Each slot is 32 bytes VISIBLE mask + 8*32
bytes of contiguous planar data. Valid[i]=1 only after a successful stage.
No blitter touches Fast RAM. Native Stage/Blit must check MEMF_CHIP on
cache allocations BEFORE DMA; ABK flags alone cannot prove placement.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import Struct,pack,unpack_from
from m18_ficon16_model import parse_bank, SIDE, DEPTH, MIN_COUNT, MAX_COUNT

ABK_HEAD=Struct(">4sHHI8s")
HEADER=Struct(">IHHHH")
NAME=b"FICHIP8 "
SLOT=288
assert len(NAME)==8

@dataclass(frozen=True)
class Cache:
    data: bytes
    count: int
    def slot(self,index:int)->bytes:
        if not isinstance(index,int) or not 1<=index<=self.count:
            raise ValueError("cache icon index out of bounds")
        if self.data[HEADER.size+self.count*SLOT+index-1]!=1:
            raise ValueError("icon was not staged")
        offset=HEADER.size+(index-1)*SLOT
        return self.data[offset:offset+SLOT]

def empty_payload(count:int)->bytes:
    if type(count) is not int or not MIN_COUNT<=count<=MAX_COUNT:
        raise ValueError("invalid count")
    total=HEADER.size+count*(SLOT+1)
    return HEADER.pack(total,count,SIDE,SIDE,DEPTH)+bytes(count*(SLOT+1))

def make_abk(count:int=4,bank:int=11)->bytes:
    if type(bank) is not int or not 5<=bank<=65535:
        raise ValueError("invalid DATA bank number")
    payload=empty_payload(count)
    return ABK_HEAD.pack(b"AmBk",bank,3,len(payload)+8,NAME)+payload

def parse_abk(raw:bytes)->tuple[int,Cache]:
    if type(raw) is not bytes or len(raw)<ABK_HEAD.size:
        raise ValueError("invalid cache ABK")
    magic,bank,flags,size,name=ABK_HEAD.unpack_from(raw)
    if (magic!=b"AmBk" or name!=NAME or not 5<=bank<=65535
        or flags!=3 or size!=len(raw)-12):
        raise ValueError("cache bank must be a Chip-preferred AMOS DATA bank")
    return bank,parse_cache(raw[ABK_HEAD.size:])

def parse_cache(blob:bytes)->Cache:
    if type(blob) is not bytes or len(blob)<HEADER.size:
        raise ValueError("short cache")
    size,count,w,h,depth=HEADER.unpack_from(blob)
    if (not MIN_COUNT<=count<=MAX_COUNT or (w,h,depth)!=(16,16,8)
        or size!=len(blob) or size!=HEADER.size+count*(SLOT+1)):
        raise ValueError("malformed FICHIP8 cache")
    for index in range(count):
        valid=blob[HEADER.size+count*SLOT+index]
        if valid not in (0,1):
            raise ValueError("invalid ready marker")
        if valid:
            offset=HEADER.size+index*SLOT
            # Visible mask must match OR of all eight colour planes.
            for y in range(16):
                vis=unpack_from(">H",blob,offset+2*y)[0]
                merged=0
                for plane in range(8):
                    merged|=unpack_from(">H",blob,offset+32+plane*32+2*y)[0]
                if vis!=merged:
                    raise ValueError("noncanonical cached visible mask")
    return Cache(blob,count)

def stage(cache_blob:bytes,source_blob:bytes,index:int)->bytes:
    cache=parse_cache(cache_blob)
    source=parse_bank(source_blob)
    if not 1<=index<=min(cache.count,source.count):
        raise ValueError("cache/source index mismatch")
    source_slot=source.icon(index)
    out=bytearray(cache.data)
    base=HEADER.size+(index-1)*SLOT
    marker=HEADER.size+cache.count*SLOT+index-1
    out[marker]=0  # not ready until all 288 bytes are copied
    for row in range(16):
        preserve=unpack_from(">H",source_slot,row*18)[0]
        out[base+row*2:base+row*2+2]=pack(">H",preserve^0xffff)
        for plane in range(8):
            src=row*18+2+plane*2
            dst=base+32+plane*32+row*2
            out[dst:dst+2]=source_slot[src:src+2]
    out[marker]=1
    return parse_cache(bytes(out)).data

def draw_model(cache_blob:bytes,index:int,x:int,y:int,mode:int,
               planes:list[bytearray],width:int,height:int,stride:int):
    """Independent pixel oracle for the Chip cached bank (not real DMA)."""
    cache=parse_cache(cache_blob)
    slot=cache.slot(index)
    if mode not in (0,1) or any(type(v) is not int for v in (x,y,mode)):
        raise ValueError("invalid coordinates or mode")
    if not(-32768<=x<=32767 and -32768<=y<=32767):
        raise ValueError("out-of-range coordinate")
    if not(1<=width<=4096 and 1<=height<=4096 and stride>=((width+15)//16)*2
           and stride%2==0 and len(planes)==8
           and all(len(p)>=height*stride for p in planes)):
        raise ValueError("invalid back-buffer bitmap")
    for row in range(16):
        py=y+row
        if py<0 or py>=height:continue
        mask=unpack_from(">H",slot,row*2)[0]
        for col in range(16):
            px=x+col
            if px<0 or px>=width:continue
            bit=0x8000>>col
            if mode==1 and not mask&bit:continue
            dest=py*stride+(px//8)
            destbit=0x80>>(px%8)
            for p,plane in enumerate(planes):
                src=unpack_from(">H",slot,32+p*32+row*2)[0]
                if src&bit:plane[dest]|=destbit
                else:plane[dest]&=(~destbit & 255)
    return 1

def staged_sample_abk(bank:int=11)->bytes:
    """AMOS-ready persistent Chip bank with the SAME four icons as R61."""
    from m18_ficon16_abk import binary as r61_sample,parse_abk as parse_source
    _,_,source=parse_source(r61_sample())
    data=empty_payload(source.count)
    for index in range(1,source.count+1):
        data=stage(data,source.raw,index)
    abk=ABK_HEAD.pack(b"AmBk",bank,3,len(data)+8,NAME)+data
    assert parse_abk(abk)[1].count==source.count
    return abk

if __name__=="__main__":
    from pathlib import Path
    from hashlib import sha256
    import base64,argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--prepared",action="store_true",
                        help="ready-to-draw FICHIP8 bank with R61 sample icons")
    parser.add_argument("--write")
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    abk=staged_sample_abk() if args.prepared else make_abk()
    assert parse_abk(abk)[1].count==4
    if args.write:Path(args.write).write_bytes(abk)
    print("M18/P5 CHIP CACHE ABK",len(abk),
          "prepared" if args.prepared else "empty",
          "SHA256",sha256(abk).hexdigest())
    if args.emit_base64:
        encoded=base64.b64encode(abk).decode("ascii")
        print("M18_R62_CHIP_ABK_BASE64_BEGIN")
        for at in range(0,len(encoded),120):
            print("M18_R62_CHIP_ABK_BASE64",encoded[at:at+120])
        print("M18_R62_CHIP_ABK_BASE64_END")
