#!/usr/bin/env python3
"""OPT020 P1d real native clipped fragments + RLE region comparisons.

The only Python pixel logic below is the independent expected-value oracle.
The tested *renderer* writes every full and partial group via CPU020 code.
Still experimental: no global native AGAPIC preflight/AP20/WinUAE.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from random import Random
from capstone import CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020, Cs
from machine68k import CPUType

from opt020_p1d_fragment_emit import emit_fragment_020
from opt020_p1d_native_runner import RealNativeP1d
from opt020_p1d_region import draw_native_plan_p1d
from test_opt020_p1b_native import make_atlas
from test_m18_agapic_atlas_model import as_planar, reference


def test_opcodes():
    blob = emit_fragment_020()
    ins = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020).
               disasm(blob, 0x1c00))
    mn = [p.mnemonic.lower().split(".", 1)[0] for p in ins]
    assert sum(p.size for p in ins) == len(blob), mn
    assert mn.count("bfextu") == 3 and mn.count("bfins") == 1, mn
    assert mn.count("eor") == 2 and mn[-1] == "rts", mn
    assert len(blob) < 0x100
    return len(blob), sha256(blob).hexdigest()


def check_direct(cpu):
    rng = Random(0x2020d)
    n = 0
    native = RealNativeP1d(cpu)
    try:
        for depth in (1, 2, 4, 8):
            for left in (0, 1, 4, 7, 8, 15):
                widths = sorted({1, min(3, 16-left), 16-left})
                for width in widths:
                    for shift in range(8):
                        for mask in (0, 0xffff, 0xa55a, 0x8001):
                            words = [rng.randrange(65536) for _ in range(depth)]
                            planes = [bytearray(rng.randbytes(8))
                                      for _ in range(depth)]
                            target = [bytearray(p) for p in planes]
                            for bit in range(width):
                                srcbit = 0x8000 >> (left+bit)
                                if not (mask & srcbit):
                                    continue
                                byte, pos = divmod(shift+bit, 8)
                                dstbit = 0x80 >> pos
                                for p, src in zip(target, words):
                                    if src & srcbit:
                                        p[byte] |= dstbit
                                    else:
                                        p[byte] &= 255 ^ dstbit
                            native.write_fragment(words, mask, shift, left,
                                                  width, planes, 0)
                            assert planes == target, (
                                "fragment bytes differ", cpu, depth,
                                left, width, shift, mask,
                                [p.hex() for p in planes],
                                [p.hex() for p in target])
                            n += 1
        assert n == native.fragment_calls and n > 500
    finally:
        native.close()
    return n


def check_regions(cpu):
    rng = Random(0x20d020)
    native = RealNativeP1d(cpu)
    tests = fulls = frags = frag_pixels = decoded = 0
    try:
        for depth in (1,2,4,8):
            for masked in (False, True):
                image, colours, mask = make_atlas(depth, masked)
                for rectangle in ((0,0,65,11),(3,1,47,8),(16,2,32,7)):
                    for x,y in ((0,0),(1,3),(5,-2),(-19,1),(36,8),(57,22)):
                        for mode in ((0,1) if masked else (0,)):
                            backdrop = bytes(rng.randrange(1<<depth)
                                             for _ in range(57*22))
                            planes,stride = as_planar(backdrop,57,22,depth)
                            expected,count = reference(
                                backdrop,57,22,colours,mask,image.width,
                                rectangle,x,y,mode)
                            expected_planes,_=as_planar(expected,57,22,depth)
                            oldf,oldp = native.write_calls,native.fragment_calls
                            result = draw_native_plan_p1d(
                                image,*rectangle,x,y,planes,57,22,mode,
                                native,stride)
                            assert planes == expected_planes, (
                                "region mismatch",cpu,depth,masked,rectangle,
                                x,y,mode,result)
                            assert result.pixels == count
                            assert native.write_calls-oldf == result.native_groups
                            assert (native.fragment_calls-oldp ==
                                    result.native_fragments)
                            assert all(p[-12:] == b"\xa5"*12 for p in planes)
                            fulls += result.native_groups
                            frags += result.native_fragments
                            frag_pixels += result.fragment_pixels
                            decoded += result.decoded_rows
                            tests += 1
        assert fulls>0 and frags>0 and frag_pixels>0 and decoded>0
    finally:
        native.close()
    return tests,fulls,frags,frag_pixels,decoded


def check_rejections(cpu):
    native = RealNativeP1d(cpu)
    image,_,_=make_atlas(8,False)
    planes,stride=as_planar(bytes([42]*(57*22)),57,22,8)
    invalid = [
        (image,(-1,0,8,4,0,0,0)),
        (image,(64,0,2,1,0,0,0)),
        (image,(0,0,0,4,0,0,0)),
        (image,(0,0,16,4,0,0,1)),
        (image,(0,0,16,4,32768,0,0)),
        (replace(image,depth=7),(0,0,16,4,0,0,0)),
        (replace(image,raw=image.raw[:-1]),(0,0,16,4,0,0,0)),
    ]
    found=0
    try:
        for img,args in invalid:
            old=[bytes(p) for p in planes]
            counts=(native.row_calls,native.clip_x_calls,
                    native.clip_y_calls,native.write_calls,native.fragment_calls)
            try:
                draw_native_plan_p1d(
                    img,*args[:6],planes,57,22,args[6],native,stride)
            except ValueError:
                assert [bytes(p) for p in planes]==old
                assert counts==(native.row_calls,native.clip_x_calls,
                                native.clip_y_calls,native.write_calls,
                                native.fragment_calls)
                found+=1
            else:
                raise AssertionError("invalid input accepted")
    finally:
        native.close()
    return found


def main():
    size,digest=test_opcodes()
    totals=[0]*7
    for cpu in (CPUType.M68EC020,CPUType.M68020):
        direct=check_direct(cpu)
        tests,fulls,frags,pix,rows=check_regions(cpu)
        refused=check_rejections(cpu)
        print(cpu,"PASS",direct,"direct fragments",tests,
              "complete AGAPIC regions",fulls,"full native groups",
              frags,"native partial groups",pix,"partial visible pixels",
              rows,"native RLE rows",refused,"nonmutating rejections")
        for i,x in enumerate((direct,tests,fulls,frags,pix,rows,refused)):
            totals[i]+=x
    print("OPT020 P1d NATIVE FRAGMENTS PASS:",totals)
    print("Fragment code bytes / SHA256",size,digest)
    print("ZERO scalar Python pixel writes in tested renderer. "
          "Global AGAPIC preflight remains Python. "
          "Not an AP20/Compiler/WinUAE gate.")


if __name__=="__main__":
    main()
