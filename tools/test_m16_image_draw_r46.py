#!/usr/bin/env python3
"""M16/R46 Gate A: 68000/Unicorn reproduction of real AMOS DATA FLAGS=0.

R45 native sim had FLAG=1 only; WinUAE loaded a valid AGAPIC DATA bank
with FLAG=0, which R45 rejected. Test R45 rejection (frozen) and R46
accepted flags 0, 1 and 3; reject all other values without writes.
All pixel comparisons execute the real R46 68000 machine code.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000

from ap20_utils import split
from audit_ap20 import parse, inspect
from build_m16_image_draw_r46 import build, BASE, R45_FAILED, R45_SHA256, ARCHIVE_R44, ENTRY_INDEX, ARCHIVE_R46, CURRENT
from build_aga_compiler_bridge_r46 import build as wrap_r46_c1
from m16_image_draw_r45_emit import emit_image_draw
from m16_agapic import pack_image, parse_payload
from m16_agapic_sample import sample
from test_m16_image_draw_r45 import (
    ImageMachine, BANK, DB, sample_pixels, naive_copy)


def instance(binary,payload,flag=0,**kwargs):
    machine=ImageMachine(binary,payload,**kwargs)
    machine.uc.mem_write(BANK-12,int(flag).to_bytes(2,"big"))
    return machine


def check(binary,payload,*,flag=0,x=0,y=0,mode=1,depth=4,
          width=120,height=88,front=0,pending=0,safe_ready=True):
    img=parse_payload(payload)
    m=instance(binary,payload,flag,width=width,height=height,
               depth=depth,front=front,pending=pending,safe_ready=safe_ready)
    before=m.snapshot()
    bg=sample_pixels(before,width,height,depth,m.stride)
    got=m.draw_image(x,y,mode)
    if pending & 1 and not safe_ready:
        assert got == 0 and m.snapshot()==before and m.getmsg_calls==1
        return
    expected=naive_copy(bg,img,x,y,mode,width,height)
    after=sample_pixels(m.snapshot(),width,height,depth,m.stride)
    assert got==1 and after==expected, (
        "R46 output mismatch",flag,depth,front,mode,x,y,got,
        next((p for p,(a,b) in enumerate(zip(after,expected)) if a!=b),None))
    assert m.get(DB+20) == (pending&~1), "Safe bookkeeping"
    assert m.getmsg_calls == int(bool(pending&1))
    for p in range(depth):
        start=width*height
        assert bytes(m.uc.mem_read(m.frontplanes[p],m.plane_size)) == m.front_before[p], "front writes"


def must_reject(binary,payload,*,flag=0,x=0,y=0,mode=1,length=None,change=None):
    m=instance(binary,payload,flag)
    if change:
        change(m)
    before=m.snapshot()
    got=m.draw_image(x,y,mode,length=length)
    assert got==0 and before==m.snapshot() and m.getmsg_calls==0, (
        "R46 must reject without writes",flag,x,y,mode,got)


def main():
    data,_,_=sample()
    fixed,info=build()
    assert fixed == build()[0]
    if ARCHIVE_R46.exists():
        assert fixed == ARCHIVE_R46.read_bytes(), "R46 archived build mismatch"
    assert wrap_r46_c1(fixed) == (Path(__file__).resolve().parents[1]/"dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib").read_bytes(), "frozen R46 C1 must remain compiler-safe"
    old=R45_FAILED.read_bytes()
    assert hashlib.sha256(old).hexdigest()==R45_SHA256
    assert BASE.read_bytes()==ARCHIVE_R44.read_bytes()
    tok_old,seg_old,_=split(old)
    tok_new,seg_new,_=split(fixed)
    assert tok_new==tok_old and len(seg_new)==len(seg_old)==56
    assert seg_new[:55]==seg_old[:55] and seg_new[55]!=seg_old[55]
    assert seg_new[55]==emit_image_draw(accept_loaded_flags_zero=True)[0]
    report=inspect(parse(fixed))
    assert not report["issues"]
    assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==50
    asm,_=emit_image_draw(accept_loaded_flags_zero=True)
    inst=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(asm,0))
    assert sum(x.size for x in inst)==len(asm)
    assert not any(x.mnemonic in ("illegal","dc.w","trap","bkpt") for x in inst)

    # Reproduce the exact observed rejection in previously shipped R45.
    oldm=instance(old,data,flag=0)
    before=oldm.snapshot()
    assert oldm.draw_image(20,61,0)==0 and oldm.snapshot()==before
    # And the same valid loaded bank in R46 (first no-paint/outside, then paint).
    count=0
    for flag in (0,1,3):
        for front in (0,1):
            for mode in (0,1):
                for x,y in ((20,61), (1,1),(-1,4),(7,-8),(31,17),
                            (0,20),(119,87),(-50,-30),(120,88)):
                    check(fixed,data,flag=flag,front=front,mode=mode,x=x,y=y)
                    count+=1
    # R46 refuses other native flag values BEFORE Safe or bitmap writes.
    for flag in (2,4,5,6,7,8,0x100,0xffff):
        must_reject(fixed,data,flag=flag)
        count+=1
    for flag in (0,1,3):
        check(fixed,data,flag=flag,pending=1,safe_ready=False)
        check(fixed,data,flag=flag,pending=3,safe_ready=True)
        count+=2
    for depth in (1,2,4,8):
        width,height=17,7
        pix=bytes((x+3*y)%(1<<depth) for y in range(height) for x in range(width))
        mask=bytes(int((x+y)%3!=0) for y in range(height) for x in range(width))
        for has_mask in (False,True):
            blob=pack_image(width,height,depth,pix,mask if has_mask else None)
            for flag in (0,3):
                for mode in ((0,1) if has_mask else (0,)):
                    for x,y in ((-9,-2),(0,0),(1,7),(15,11),(63,33)):
                        check(fixed,blob,flag=flag,depth=depth,
                              width=64,height=40,mode=mode,x=x,y=y)
                        count+=1
    # Full bank header and RLE validation still applies when native FLAGS=0.
    for flag in (0,3):
        must_reject(fixed,data,flag=flag,length=20);count+=1
        must_reject(fixed,data,flag=flag,mode=2);count+=1
        must_reject(fixed,data,flag=flag,change=lambda m:m.put(BANK-20,0));count+=1
        must_reject(fixed,data,flag=flag,change=lambda m:m.put(BANK-16,4));count+=1
        must_reject(fixed,data,flag=flag,change=lambda m:m.uc.mem_write(BANK-8,b'AGAPAL  '));count+=1
        must_reject(fixed,data,flag=flag,change=lambda m:m.uc.mem_write(BANK,b'NOTPIC'));count+=1
        malformed=bytearray(data);malformed[11]=2
        must_reject(fixed,bytes(malformed),flag=flag);count+=1
        malformed=bytearray(data);struct.pack_into(">I",malformed,32,0)
        must_reject(fixed,bytes(malformed),flag=flag);count+=1
    print("M16/R46 native CPU Gate A PASS:",count,"real 68000 scenarios")
    print("WinUAE real bank native FLAGS=0 reproduced: R45 rejects, R46 accepts")
    print("0/1/3 accepted; 2/4/5/6/7/256/65535 rejected before any paint")
    print("Native R46: 50 commands / 56 segments frozen; official C1: 57 entries")
    print("R46 candidate SHA256",info["sha256"],"size",info["size"])
    print("R46 Gate B PASS from user WinUAE captures (not executed by CPU harness)")


if __name__=="__main__":
    main()
