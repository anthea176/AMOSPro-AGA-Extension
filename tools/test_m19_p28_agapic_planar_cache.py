#!/usr/bin/env python3
"""M19 P2.8 Gate A: AGAPIC independent-alpha cache and tested M18/P5 native core.

The native M68000 code is unmodified M18 masked Blitter experiment, executed
under Unicorn with Exec/graphics OS hooks. This is NOT an installed AP20
command, not real DMA, not WinUAE, and NOT a measured FPS increase.
"""
from __future__ import annotations

from hashlib import sha256
from random import Random
from struct import pack,unpack_from

from m16_agapic import pack_image,parse_payload,render_cpu_model
from m16_agapic_v2 import pack_image_v2
from m18_ficon16_chip_blit_emit import emit_chip_cache_blit
from test_m18_ficon16_chip_blit import run
from test_m18_ficon16_native_aligned import as_planar,WIDTH,HEIGHT,STRIDE
from m19_p28_agapic_planar_cache import (
    HEADER,FLAG_HAS_MASK,FLAG_READY,MAX_BYTES,V1_MODE_ID,
    cache_from_agapic,parse_cache,make_cache_abk,parse_cache_abk,
    paint_cpu,validate_mode,
)

MODE_ID=0x00021000


def assert_reject(fn,expected=ValueError):
    try:fn()
    except expected:return
    raise AssertionError(f'Expected {expected.__name__} for {fn}')


def make_image(w:int,h:int,depth:int=8):
    pixels=bytearray(w*h)
    alpha=bytearray(w*h)
    for y in range(h):
        for x in range(w):
            i=y*w+x
            value=(x*7+y*13)&((1<<depth)-1)
            if (x+y)%7==0:value=0  # zero can be drawn OPAQUE
            pixels[i]=value
            alpha[i]=int((x*3+y*5)%11!=0 and (x+y)%9!=0)
            if (x+y)%13==0:alpha[i]=0;pixels[i]=6 & ((1<<depth)-1)  # nonzero invisible
    return bytes(pixels),bytes(alpha)


def host_model_cases()->int:
    rnd=Random(0xA92026)
    cases=0
    configs=((1,1,1),(15,17,4),(16,16,8),(17,19,8),(31,9,8),(37,23,8))
    for w,h,depth in configs:
        colours,mask=make_image(w,h,depth)
        for version in (1,2):
            for has_mask in (False,True):
                srcmask=mask if has_mask else None
                if version==1:
                    source=pack_image(w,h,depth,colours,srcmask)
                    expected_mode=V1_MODE_ID
                else:
                    palette=bytes((i*7)&255 for i in range(3*(1<<depth)))
                    source=pack_image_v2(w,h,depth,colours,palette,MODE_ID,srcmask)
                    expected_mode=MODE_ID
                result=cache_from_agapic(source,generation=3)
                a=parse_cache(result,expected_source=source)
                assert (a.width,a.height,a.depth,a.stride,a.has_mask,a.mode_id,a.generation)==(
                    w,h,depth,2*((w+15)//16),has_mask,expected_mode,3)
                assert a.source_sha256==sha256(source).digest()
                assert cache_from_agapic(source,generation=3)==result
                assert cache_from_agapic(source,generation=4)!=result
                assert len(result)==HEADER.size+(depth+int(has_mask))*a.plane_size
                for y in range(h):
                    for x in range(w):
                        i=y*w+x
                        assert a.colour(x,y)==colours[i]
                        assert a.visible(x,y)==(bool(mask[i]) if has_mask else True)
                # Literal AGAPIC original pixel+alpha oracle, unrelated to cache representation.
                original=parse_payload(source) if version==1 else None
                for mode in ((0,1) if has_mask else (0,)):
                    for x,y in ((0,0),(1,2),(-1,-3),(-15,4),(31,9),(59,39),(-40,0),(0,50)):
                        background=bytes(rnd.randrange(1<<depth) for _ in range(WIDTH*HEIGHT))
                        expected=as_planar(background)
                        if original is not None:
                            render_cpu_model(original,x,y,expected[:depth],WIDTH,HEIGHT,mode,STRIDE)
                        else:
                            # Independent source pixel model for v2 (palette must not change pixels).
                            bb=[bytearray(background[row*WIDTH:(row+1)*WIDTH]) for row in range(HEIGHT)]
                            for sy in range(h):
                                for sx in range(w):
                                    tx=x+sx;ty=y+sy
                                    if 0<=tx<WIDTH and 0<=ty<HEIGHT and (mode==0 or mask[sy*w+sx]):
                                        bb[ty][tx]=colours[sy*w+sx]
                            expected=as_planar(b''.join(bb))
                        canvas=[bytearray(background[row*WIDTH:(row+1)*WIDTH]) for row in range(HEIGHT)]
                        paint_cpu(canvas,a,x,y,mode,screen_mode_id=(MODE_ID if version==2 else None))
                        got=as_planar(b''.join(canvas))
                        assert expected==got,(w,h,depth,version,has_mask,mode,x,y)
                        cases+=1
                if not has_mask:
                    assert_reject(lambda:validate_mode(a,1,screen_mode_id=MODE_ID))
                if version==2:
                    assert_reject(lambda:validate_mode(a,0,screen_mode_id=MODE_ID^1))
                    assert_reject(lambda:validate_mode(a,0))
                # Owned-bank serialization, checksum, staging generation.
                abk=make_cache_abk(source,bank=31,generation=3,chip=True)
                bank,flags,staged=parse_cache_abk(abk,expected_source=source)
                assert bank==31 and flags==3 and staged.raw==result
                assert_reject(lambda:parse_cache(result,expected_source=source+b'X'))
    return cases


def invalid_cases()->int:
    colours,mask=make_image(17,19,8)
    source=pack_image(17,19,8,colours,mask)
    good=cache_from_agapic(source)
    tests=0
    def reject_bytes(index:int,payload:bytes):
        nonlocal tests
        altered=bytearray(good)
        altered[index:index+len(payload)]=payload
        assert_reject(lambda:parse_cache(bytes(altered)))
        tests+=1
    reject_bytes(0,b'XXXX')
    reject_bytes(4,pack('>H',2))
    reject_bytes(6,pack('>H',FLAG_HAS_MASK)) # ready absent
    reject_bytes(6,pack('>H',FLAG_HAS_MASK|FLAG_READY|4))
    reject_bytes(8,pack('>H',0))
    reject_bytes(10,pack('>H',0))
    reject_bytes(12,pack('>H',9))
    reject_bytes(14,pack('>H',6))
    reject_bytes(20,pack('>I',0))
    reject_bytes(24,pack('>I',0))
    reject_bytes(28,pack('>I',len(good)-2))
    reject_bytes(32,pack('>I',0))
    reject_bytes(36,pack('>I',1))
    # rightmost 15 unused bits in width=17, second word
    snap=parse_cache(good)
    reject_bytes(snap.planes_offset+snap.stride-2,pack('>H',0xffff))
    # Corrupt independent mask beyond end of visible width
    reject_bytes(snap.mask_offset+snap.stride-2,pack('>H',0xffff))
    assert_reject(lambda:cache_from_agapic(source,generation=0));tests+=1
    assert_reject(lambda:cache_from_agapic(source,generation=-1));tests+=1
    assert_reject(lambda:cache_from_agapic(source[:-1]));tests+=1
    assert_reject(lambda:make_cache_abk(source,bank=1));tests+=1
    assert_reject(lambda:parse_cache_abk(b'xxx'));tests+=1
    assert_reject(lambda:parse_cache(good[:-1]));tests+=1
    return tests


def real_native_alpha_cases()->int:
    """Execute M18 CPU instructions, mock ONLY OS/DMA with independent oracle."""
    raw,_=emit_chip_cache_blit()
    assert raw==emit_chip_cache_blit()[0]
    rng=Random(0xA6A020)
    pixels,mask=make_image(16,16,8)
    # Verify the alpha is genuinely independent from pen zero.
    assert any(v==0 and a for v,a in zip(pixels,mask))
    assert any(v!=0 and not a for v,a in zip(pixels,mask))
    tested=0
    for version in (1,2):
        pal=bytes((i*7)&255 for i in range(256*3))
        src=pack_image(16,16,8,pixels,mask) if version==1 else pack_image_v2(16,16,8,pixels,pal,MODE_ID,mask)
        snap=parse_cache(cache_from_agapic(src),expected_source=src)
        slot=snap.native_chip_slot_16x16x8(mode=1,screen_mode_id=(MODE_ID if version==2 else None))
        assert len(slot)==288
        # Native core checks MEMF_CHIP (rather than trusting ABK flags).
        for x,y in ((0,0),(1,7),(7,3),(15,0),(16,16),(-15,-1),
                    (-1,2),(49,7),(64,42),(65,1),(-16,5),(17,42)):
            for mode in (0,1):
                background=bytes(rng.randrange(256) for _ in range(WIDTH*HEIGHT))
                before=as_planar(background)
                canvas=[bytearray(background[row*WIDTH:(row+1)*WIDTH]) for row in range(HEIGHT)]
                paint_cpu(canvas,snap,x,y,mode,screen_mode_id=(MODE_ID if version==2 else None))
                expected=as_planar(b''.join(canvas))
                status,planes,calls=run(raw,slot,before,x=x,y=y,mode=mode,seed=version)
                assert status==1 and planes==expected,(version,x,y,mode)
                visible=(-16<x<WIDTH and -16<y<HEIGHT)
                assert len([c for c in calls if c[0].startswith('Blt')])==int(visible)
                if visible:
                    assert len([c for c in calls if c[0]=='WaitBlit'])==1
                    assert len([c for c in calls if c[0]=='TypeOfMem'])==2
                tested+=1
        bg=as_planar(bytes([41]*(WIDTH*HEIGHT)))
        status,after,calls=run(raw,slot,bg,x=3,y=2,mode=1,fast=True)
        assert status==0 and after==bg and not any(c[0].startswith('Blt') for c in calls)
    return tested


def main():
    host=host_model_cases()
    reject=invalid_cases()
    native=real_native_alpha_cases()
    assert host>=180 and reject>=19 and native==48
    print(f'M19 P2.8 HOST AGAPIC v1/v2 PLANAR INDEPENDENT ALPHA PASS: {host} parity, {reject} refusal cases')
    print(f'M19 P2.8 NATIVE 68000 M18 BLITTER CORE REUSE GATE A PASS: {native} pixel+ABI scenarios')
    print('No AP20 R88 binary built; no real DMA / WinUAE B,C / FPS data')

if __name__=='__main__':
    main()
