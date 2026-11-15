#!/usr/bin/env python3
"""M19 P2.8 source-only AGAPIC v1/v2 -> explicit-mask planar snapshot.

Internal, NOT installed in AMOSPro_AGA.Lib. The cache is an owned AMOS
DATA-bank payload when exported as ABK, never a live pointer into the
AGAPIC source. No implicit lifetime across Erase/Load. ABK flags=3 is a
Chip-memory *request*, not proof of DMA-reachable Chip allocation.

Version 1 layout (all big endian, bytes):
  0  magic 'AGPC'
  4  u16 version=1
  6  u16 flags: 1=independent visibility plane, 2=ready snapshot
  8  u16 width
 10  u16 height
 12  u16 source depth (1..8)
 14  u16 row stride in bytes (2*ceil(width/16))
 16  u32 v2 screen ModeID, or 0xffffffff for v1
 20  u32 visibility offset (0 if source has no mask)
 24  u32 first colour plane offset
 28  u32 total length
 32  u32 generation (>0, increment on explicit restage)
 36  u32 reserved=0
 40  32-byte sha256 of the original AGAPIC payload
 72  optional visibility plane, rows padded to 16 bits, 1=draw
     depth separate bitplanes, each row word aligned, MSB leftmost.

In the 16x16x8 case, bytes after header are 32-byte visibility +
8*32-byte colour planes: the tested M18/P5 native Chip Blitter core's
288-byte slot contract. v2 palette is metadata of the *source*, not part
of the cache. Preserve and validate ModeID before painting from v2.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from struct import Struct, pack, unpack_from

from m16_agapic import unpack_image
from m16_agapic_v2 import parse_payload_any

MAGIC=b'AGPC'
NAME=b'AGPCACHE'
VERSION=1
FLAG_HAS_MASK=1
FLAG_READY=2
V1_MODE_ID=0xffffffff
HEADER=Struct('>4s6H6I32s')
ABK_HEADER=Struct('>4sHHI8s')
MAX_BYTES=16*1024*1024
MAX_PIXELS=4*1024*1024
NATIVE_SIDE=16
NATIVE_DEPTH=8
NATIVE_SLOT=288
assert HEADER.size==72 and ABK_HEADER.size==20 and len(NAME)==8

@dataclass(frozen=True)
class PlanarSnapshot:
    raw: bytes
    width: int
    height: int
    depth: int
    stride: int
    has_mask: bool
    mode_id: int
    generation: int
    source_sha256: bytes
    mask_offset: int
    planes_offset: int

    @property
    def plane_size(self)->int:
        return self.stride*self.height

    def visible(self,x:int,y:int)->bool:
        if not 0<=x<self.width or not 0<=y<self.height:
            raise IndexError('pixel coordinate outside snapshot')
        if not self.has_mask:
            return True
        pos=self.mask_offset+y*self.stride+(x>>4)*2
        return bool(unpack_from('>H',self.raw,pos)[0] & (0x8000>>(x&15)))

    def colour(self,x:int,y:int)->int:
        if not 0<=x<self.width or not 0<=y<self.height:
            raise IndexError('pixel coordinate outside snapshot')
        value=0
        off=y*self.stride+(x>>4)*2
        bit=0x8000>>(x&15)
        for p in range(self.depth):
            word=unpack_from('>H',self.raw,self.planes_offset+p*self.plane_size+off)[0]
            if word & bit:
                value|=1<<p
        return value

    def native_chip_slot_16x16x8(self,*,mode:int,screen_mode_id:int|None=None)->bytes:
        """Tested M18/P5 native core source layout, NOT a safe DMA pointer.

        Only an actual Chip DATA allocation and verified runtime wrapper
        may pass the returned bytes to BltMaskBitMapRastPort.
        """
        if (self.width,self.height,self.depth)!=(16,16,8):
            raise ValueError('legacy native core supports only 16x16x8')
        validate_mode(self,mode,screen_mode_id=screen_mode_id)
        if self.has_mask:
            mask=self.raw[self.mask_offset:self.mask_offset+32]
        else:
            mask=b'\xff'*32  # mode 0 ignores mask; mode 1 was rejected
        slot=mask+self.raw[self.planes_offset:self.planes_offset+256]
        assert len(slot)==NATIVE_SLOT
        return slot


def cache_from_agapic(source:bytes,*,generation:int=1)->bytes:
    """Parse full RLE/palette and build a ready immutable snapshot atomically.

    No cache output survives a malformed source. Explicit re-stage after
    source mutation/Load is required to observe new source content.
    """
    if type(source) is not bytes or type(generation) is not int or not 1<=generation<=0xffffffff:
        raise ValueError('bad source or generation')
    original=parse_payload_any(source)  # strict v1/v2 parser, all RLE checked
    image=original.image
    pixels,mask=unpack_image(image)
    w,h,depth=image.width,image.height,image.depth
    if w*h>MAX_PIXELS:
        raise ValueError('source pixel count too large')
    stride=2*((w+15)//16)
    plane_size=stride*h
    mask_offset=HEADER.size if mask is not None else 0
    planes_offset=HEADER.size+(plane_size if mask is not None else 0)
    total=planes_offset+depth*plane_size
    if total>MAX_BYTES:
        raise ValueError('cache exceeds 16 MiB')
    result=bytearray(total)
    for y in range(h):
        for x in range(w):
            idx=y*w+x
            off=y*stride+(x>>4)*2
            wordbit=0x8000>>(x&15)
            if mask is not None and mask[idx]:
                at=mask_offset+off
                value=unpack_from('>H',result,at)[0]|wordbit
                result[at:at+2]=pack('>H',value)
            colour=pixels[idx]
            for p in range(depth):
                if colour&(1<<p):
                    at=planes_offset+p*plane_size+off
                    value=unpack_from('>H',result,at)[0]|wordbit
                    result[at:at+2]=pack('>H',value)
    mode_id=V1_MODE_ID if original.version==1 else original.mode_id
    if type(mode_id) is not int or not 0<=mode_id<=0xffffffff:
        raise ValueError('v2 invalid screen ModeID')
    flags=FLAG_READY|(FLAG_HAS_MASK if mask is not None else 0)
    HEADER.pack_into(result,0,MAGIC,VERSION,flags,w,h,depth,stride,
                     mode_id,mask_offset,planes_offset,total,generation,0,
                     sha256(source).digest())
    return bytes(result)


def parse_cache(raw:bytes,*,expected_source:bytes|None=None)->PlanarSnapshot:
    if type(raw) is not bytes or not HEADER.size<=len(raw)<=MAX_BYTES:
        raise ValueError('invalid cache size')
    (magic,version,flags,w,h,depth,stride,mode_id,mask_off,plane_off,
     size,generation,reserved,source_sha)=HEADER.unpack_from(raw)
    if magic!=MAGIC or version!=VERSION or flags&~3 or not(flags&FLAG_READY):
        raise ValueError('wrong AGPC version/flags or incomplete staging')
    if (not 1<=w<=4096 or not 1<=h<=4096 or not 1<=depth<=8 or
        w*h>MAX_PIXELS or stride!=2*((w+15)//16) or
        not 1<=generation<=0xffffffff or reserved!=0):
        raise ValueError('invalid AGPC geometry/generation')
    planesize=stride*h
    if mask_off!=(HEADER.size if flags&FLAG_HAS_MASK else 0):
        raise ValueError('invalid AGPC visibility offset')
    if (plane_off!=HEADER.size+(planesize if flags&FLAG_HAS_MASK else 0)
        or size!=len(raw) or size!=plane_off+depth*planesize):
        raise ValueError('invalid AGPC plane offsets/length')
    if expected_source is not None and sha256(expected_source).digest()!=source_sha:
        raise ValueError('cache source digest differs: re-stage explicitly')
    for off in ([mask_off] if mask_off else [])+[
        plane_off+p*planesize for p in range(depth)]:
        rem=w&15
        if rem:
            unused=(1<<(16-rem))-1
            for y in range(h):
                if unpack_from('>H',raw,off+y*stride+stride-2)[0]&unused:
                    raise ValueError('nonzero bits outside width')
    return PlanarSnapshot(raw,w,h,depth,stride,bool(flags&FLAG_HAS_MASK),
                          mode_id,generation,source_sha,mask_off,plane_off)


def validate_mode(snap:PlanarSnapshot,mode:int,*,screen_mode_id:int|None=None)->None:
    if type(mode) is not int or mode not in (0,1):
        raise ValueError('bad paint mode')
    if mode and not snap.has_mask:
        raise ValueError('mask mode requires independent source alpha')
    if snap.mode_id!=V1_MODE_ID:
        if screen_mode_id is None or screen_mode_id!=snap.mode_id:
            raise ValueError('AGAPIC v2 ModeID mismatch')


def paint_cpu(canvas:list[bytearray],snap:PlanarSnapshot,x:int,y:int,mode:int,
              *,screen_mode_id:int|None=None)->None:
    """Reference CPU bitmap painter; back-buffer ownership is caller's job."""
    validate_mode(snap,mode,screen_mode_id=screen_mode_id)
    if type(x) is not int or type(y) is not int or not -32768<=x<=32767 or not -32768<=y<=32767:
        raise ValueError('coordinate outside API signed16 range')
    if not canvas or len({len(row) for row in canvas})!=1:
        raise ValueError('invalid destination')
    sh,sw=len(canvas),len(canvas[0])
    # Clip geometry before inspecting any cache pixel.
    sx0=max(0,-x);sy0=max(0,-y)
    sx1=min(snap.width,sw-x);sy1=min(snap.height,sh-y)
    for sy in range(sy0,sy1):
        for sx in range(sx0,sx1):
            if mode==0 or snap.visible(sx,sy):
                canvas[y+sy][x+sx]=snap.colour(sx,sy)


def make_cache_abk(source:bytes,bank:int,*,generation:int=1,chip:bool=True)->bytes:
    """AMOS-owned DATA bank. Chip preference is NOT a DMA guarantee."""
    if type(bank) is not int or not 5<=bank<=65535:
        raise ValueError('invalid AMOS bank number')
    cache=cache_from_agapic(source,generation=generation)
    return ABK_HEADER.pack(b'AmBk',bank,3 if chip else 1,len(cache)+8,NAME)+cache


def parse_cache_abk(abk:bytes,*,expected_source:bytes|None=None)->tuple[int,int,PlanarSnapshot]:
    if type(abk) is not bytes or len(abk)<ABK_HEADER.size:
        raise ValueError('bad bank envelope')
    magic,bank,flags,size,name=ABK_HEADER.unpack_from(abk)
    if (magic!=b'AmBk' or not 5<=bank<=65535 or flags not in (1,3)
        or name!=NAME or size!=len(abk)-12):
        raise ValueError('invalid AMOS bank header')
    return bank,flags,parse_cache(abk[ABK_HEADER.size:],expected_source=expected_source)
