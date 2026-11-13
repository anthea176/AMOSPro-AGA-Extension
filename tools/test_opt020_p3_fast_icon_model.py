#!/usr/bin/env python3
"""OPT020/P3 Fast Icons: source identity and bitfield model (NO Gate A claim).

Offline/CPU-free preflight. A real 68020 executable test is still required
before a new AP20 candidate can replace the proven R72 working library.
"""
from __future__ import annotations
import random
from hashlib import sha256
from struct import pack, unpack
from build_m18_r61_ficon import build as build_r61
from build_m18_r67_ficon_capture import build as build_r67
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from m18_ficon_ap20_emit import emit_ficon_ap20
from m18_ficon16_native_shifted_emit import emit_ficon16_shifted_cpu
from m18_ficon_capture_emit import emit_ficon_capture
from opt020_p1_bitfield_emit import bitfield_020

def read_span(buf,at,bit):
    n=(bit+23)//8
    assert 0<=bit<8 and at>=0 and at+n<=len(buf)
    return (int.from_bytes(buf[at:at+n],'big')>>(8*n-bit-16))&0xffff

def write_span(buf,at,bit,value):
    n=(bit+23)//8
    assert 0<=bit<8 and at>=0 and at+n<=len(buf)
    offset=8*n-bit-16
    mask=0xffff<<offset
    old=int.from_bytes(buf[at:at+n],'big')
    buf[at:at+n]=((old&~mask)|((value&0xffff)<<offset)).to_bytes(n,'big')

def rows_for(pixels,width,height):
    stride=((width+15)//16)*2
    planes=[bytearray(stride*height) for _ in range(8)]
    for y in range(height):
        for x in range(width):
            for p in range(8):
                if (pixels[y*width+x]>>p)&1:
                    planes[p][y*stride+(x>>3)] |= 0x80>>(x&7)
    return planes,stride

def test_model():
    rng=random.Random(0x020003)
    count=0
    for width in (16,17,23,31,32,33,47,64,65,320):
        height=3
        bg=bytes(rng.randrange(256) for _ in range(width*height))
        planes,stride=rows_for(bg,width,height)
        for x in range(width-15):
            for y in (0,height-1):
                # Capture: BFEXTU 16 bits from each of eight planar bytes.
                words=[read_span(p,y*stride+(x>>3),x&7) for p in planes]
                visible=0
                for word in words:visible|=word
                preserve=visible^0xffff
                for u in range(16):
                    col=bg[y*width+x+u]
                    assert bool(preserve&(0x8000>>u))==(col==0)
                    for plane in range(8):
                        assert bool(words[plane]&(0x8000>>u))==bool(col&(1<<plane))
                # Draw: compare BFEXTU/AND/OR/BFINS to independent pixel loop.
                colors=bytes(rng.choice((0,0,1,3,7,15,31,127,128,255)) for _ in range(16))
                src=[sum(((v>>p)&1)<<(15-i) for i,v in enumerate(colors))
                     for p in range(8)]
                mask=sum((0x8000>>u) for u,v in enumerate(colors) if v==0)
                for mode in (0,1):
                    fast=[bytearray(z) for z in planes]
                    scalar=[bytearray(z) for z in planes]
                    visible=0xffff if mode==0 else mask^0xffff
                    for p in range(8):
                        at=y*stride+(x>>3)
                        old=read_span(fast[p],at,x&7)
                        new=(old&(~visible&0xffff))|(src[p]&visible)
                        write_span(fast[p],at,x&7,new)
                    for u,col in enumerate(colors):
                        if mode and col==0: continue
                        at=y*stride+((x+u)>>3)
                        bit=0x80>>((x+u)&7)
                        for p in range(8):
                            if (col>>p)&1:scalar[p][at]|=bit
                            else:scalar[p][at]&=~bit&255
                    assert fast==scalar,(width,x,y,mode)
                    count+=1
    assert count>=1000
    return count

def main():
    # Pinned historical builders must not change when opt020 is OFF.
    r61,_=build_r61()
    r67,_=build_r67()
    assert sha256(r61).hexdigest()==(
        "ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f")
    assert sha256(r67).hexdigest()==(
        "ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5")
    assert unwrap_native_parts_v2(r61)[1][60]==emit_ficon_ap20()[0]
    assert unwrap_native_parts_v2(r67)[1][66]==emit_ficon_capture()[0]
    core_old,_=emit_ficon16_shifted_cpu()
    core_new,lnew=emit_ficon16_shifted_cpu(opt020=True)
    draw020,draw_labels=emit_ficon_ap20(opt020=True)
    cap_old,_=emit_ficon_capture()
    cap020,cap_labels=emit_ficon_capture(opt020=True)
    assert core_new!=core_old and draw020.endswith(core_new)
    assert "p3_plane" in lnew and "p3_fallback" in lnew
    assert "pixel" not in cap_labels and "check_plane" in cap_labels
    assert "pixel" in emit_ficon_capture()[1]
    assert cap020!=cap_old and len(cap020)<len(cap_old)
    assert bitfield_020(0xe9c0,4,4,offset_reg=1)==bytes.fromhex("e9d44850")
    assert bitfield_020(0xe9c0,4,0,offset_reg=7)==bytes.fromhex("e9d409d0")
    assert bitfield_020(0xefc0,4,0,offset_reg=7)==bytes.fromhex("efd409d0")
    assert bitfield_020(0xefc0,4,5,offset_reg=7)==bytes.fromhex("efd459d0")
    assert cap020.count(bytes.fromhex("e9d44850"))==1
    assert core_new.count(bytes.fromhex("e9d409d0"))==1
    assert core_new.count(bytes.fromhex("efd409d0"))==1
    assert core_new.count(bytes.fromhex("efd459d0"))==1
    assert draw_labels["core"] < len(draw020)
    assert test_model()>=1000
    print("P3 SOURCE/MODEL PASS: 8 planes capture+draw, masked/opaque, arbitrary X")
    print("HISTORICAL R61/R67 BYTE IDENTICAL. 68020 CPU + WinUAE NOT TESTED.")

if __name__=="__main__":
    main()
