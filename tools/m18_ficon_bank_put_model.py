"""R65 host-only oracle for FICON8 Bank Put from 16x16 chunky byte indices.

This implements the PUBLIC CONTRACT, not native 68000 or Gate B.
Input byte buffer is AMOS DATA contents, offset zero based, 256 bytes/image.
Any failed precheck leaves the original immutable FICON8 data untouched.
"""
from __future__ import annotations
from m18_ficon16_model import HEADER, ROW, SIDE, DEPTH, SLOT_BYTES, parse_bank

def chunky_to_slot(pixels:bytes)->bytes:
    if type(pixels) is not bytes or len(pixels)!=SIDE*SIDE:
        raise ValueError("one complete 16x16 chunky 8-bit image required")
    slot=bytearray()
    for y in range(SIDE):
        preserve=0
        planes=[0]*DEPTH
        for x in range(SIDE):
            colour=pixels[y*SIDE+x]
            bit=0x8000 >> x
            if colour==0:
                preserve|=bit
            else:
                for p in range(DEPTH):
                    if colour&(1<<p):planes[p]|=bit
        slot.extend(ROW.pack(preserve,*planes))
    assert len(slot)==SLOT_BYTES
    return bytes(slot)

def put_chunky(bank:bytes,icon_id:int,source:bytes,offset:int,
               *,dest_number:int=12,source_number:int=13)->bytes:
    if (type(dest_number) is not int or type(source_number) is not int or
        not 5<=dest_number<=65535 or not 5<=source_number<=65535 or
        dest_number==source_number):
        raise ValueError("two distinct AMOS DATA bank numbers required")
    if type(icon_id) is not int or type(offset) is not int or offset<0:
        raise ValueError("invalid icon ID or source byte offset")
    valid=parse_bank(bank)
    if not 1<=icon_id<=valid.count:
        raise ValueError("icon ID outside FICON8 range")
    if type(source) is not bytes or offset>len(source)-256:
        raise ValueError("source bank too small for chunky pixels")
    first=HEADER.size+(icon_id-1)*SLOT_BYTES
    result=(bank[:first]+chunky_to_slot(source[offset:offset+256])+
            bank[first+SLOT_BYTES:])
    assert len(result)==len(bank) and parse_bank(result).count==valid.count
    return result
