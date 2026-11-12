#!/usr/bin/env python3
"""M16/R45 provisional Gate A — real 68000 CPU/Unicorn image draw tests.

This tests the NEW native segment, not a Python drawing substitution.
AMOS interpreted/WinUAE and physical hardware remain untested.
"""
from __future__ import annotations

import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from build_m16_image_draw_r45 import (
    build, BASE, BASE_SHA256, ARCHIVE_R45, ARCHIVE_R44, ENTRY_INDEX, API, GETP)
from m16_image_draw_r45_emit import emit_image_draw
from m16_agapic import pack_image, parse_payload, unpack_image
from m16_agapic_sample import sample
from test_m6_blit_copy_r13 import CopyMachine
from test_m5_generic import CODE, EXEC, AMOS, STATE, DB, BITMAP, STACK, STOP, DR, AR

BANK = 0xD00000
ARGS = 0x58000
SAFE_PORT = 0x59100
SAFE_MSG = 0x59200
TYPEOFMEM = EXEC - 534
GETMSG = EXEC - 372
LOCS = (TYPEOFMEM, GETMSG)


def sample_pixels(src, width, height, depth, stride):
    planes = []
    rb = stride * height
    for p in range(depth):
        planes.append(bytearray(src[p][:rb]))
    pixels = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            ix = y * stride + (x >> 3)
            mask = 1 << (7 - (x & 7))
            colour = 0
            for plane in range(depth):
                if planes[plane][ix] & mask:
                    colour |= 1 << plane
            pixels[y * width + x] = colour
    return bytes(pixels)


def naive_copy(before, image, x, y, mode, screen_w, screen_h):
    pixels, mask = unpack_image(image)
    dst = bytearray(before)
    for sy in range(image.height):
        dy = sy + y
        if not 0 <= dy < screen_h:
            continue
        for sx in range(image.width):
            dx = sx + x
            if 0 <= dx < screen_w and (mode == 0 or mask[sy*image.width+sx]):
                dst[dy * screen_w + dx] = pixels[sy*image.width+sx]
    return bytes(dst)


class ImageMachine(CopyMachine):
    def __init__(self,binary,payload,*,width=320,height=256,
                 depth=4,front=0,pending=0,safe_ready=True):
        super().__init__(binary,width=width,height=height,depth=depth,front=front)
        self.put(DB+12,SAFE_PORT)
        self.put(DB+16,SAFE_PORT+0x100)
        self.put(DB+20,pending)
        self.pending_safe = pending
        self.safe_ready = safe_ready
        self.type_calls = 0
        self.getmsg_calls = 0
        self.os_calls = []
        self.payload = payload
        self.install_bank(payload)
        # Separate physical front bitplanes to catch accidental front writes.
        self.frontplanes=[]
        front_bitmap=BITMAP if front==0 else BITMAP+0x100
        for i in range(depth):
            address=0xA00000 + i*0x40000
            self.put(front_bitmap+8+i*4,address)
            self.uc.mem_write(address,b'\x33'*self.plane_size)
            self.frontplanes.append(address)
        self.front_before=[bytes(self.uc.mem_read(p,self.plane_size))
                           for p in self.frontplanes]
        for call in LOCS:
            self.uc.mem_write(call,b'\x4e\x75')

    def install_bank(self,payload):
        self.payload=payload
        self.uc.mem_write(BANK, payload)
        self.put(BANK-20,len(payload)+16)
        self.put(BANK-16,10)
        self.uc.mem_write(BANK-12,b'\x00\x01')
        self.uc.mem_write(BANK-8,b'AGAPIC  ')

    def _ret(self,value):
        self.uc.reg_write(DR[0],value & 0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000)
        self.uc.reg_write(AR[1],0xbad100)
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def os_call(self,uc,address,size,user):
        if address == TYPEOFMEM:
            self.type_calls+=1
            address_to_check=self.a(1)
            value=1 if BANK-24 <= address_to_check < BANK+len(self.payload) else 0
            self.os_calls.append(("TypeOfMem",address_to_check,value))
            self._ret(value)
        elif address == GETMSG:
            self.getmsg_calls+=1
            assert self.a(0)==SAFE_PORT, "only SafePort may be polled"
            self.os_calls.append(("GetMsg",self.pending_safe,self.safe_ready))
            self._ret(SAFE_MSG if self.safe_ready else 0)
        else:
            raise AssertionError(("Unexpected OS call",hex(address)))

    def draw_image(self,x=10,y=10,mode=1,start=BANK,length=None,
                   limit=12_000_000):
        if length is None:
            length=len(self.payload)
        for i,reg in enumerate(DR):
            self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]):
            self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,v in enumerate((y,x,length,start)):
            self.put(ARGS+4*i,v)
        self.uc.reg_write(DR[3],mode&0xffffffff)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_INDEX],STOP,count=limit)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP, "R45 did not RTS"
        assert self.a(7)==STACK+4, "R45 unbalanced stack"
        assert self.a(3)==ARGS+16, "R45 GetP must consume 4 stack LONGs"
        for reg,value in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==value,("R45 ABI register",reg)
        assert self.d(2)==0, "R45 result is integer"
        assert self.d(3) in (0,1), "R45 result must be boolean"
        assert [bytes(self.uc.mem_read(p,self.plane_size))
                for p in self.frontplanes] == self.front_before, "front modified"
        return self.d(3)


def check_paint(candidate,payload,*,x=10,y=10,mode=1,width=64,height=40,
                depth=4,front=0,pending=0,safe_ready=True):
    image=parse_payload(payload)
    assert image.depth==depth
    m=ImageMachine(candidate,payload,width=width,height=height,depth=depth,
                   front=front,pending=pending,safe_ready=safe_ready)
    before=m.snapshot()
    bg=sample_pixels(before,width,height,depth,m.stride)
    result=m.draw_image(x,y,mode)
    if pending & 1 and not safe_ready:
        assert result==0 and m.snapshot()==before and m.getmsg_calls==1
        assert m.get(DB+20)==pending
        return 1
    expected=naive_copy(bg,image,x,y,mode,width,height)
    after=sample_pixels(m.snapshot(),width,height,depth,m.stride)
    assert result==1, ("draw rejected",width,height,depth,front,pending,x,y)
    assert after==expected, ("wrong picture pixels",width,height,x,y,mode,
                            next((i for i,(a,b) in enumerate(zip(after,expected))
                                  if a!=b),None))
    # Bytes outside the visible width, and row-stride padding must stay exact.
    for a,b in zip(before,m.snapshot()):
        used=(width+7)//8
        for row in range(height):
            assert a[row*m.stride+used:(row+1)*m.stride] == b[
                row*m.stride+used:(row+1)*m.stride]
    assert m.get(DB+20)==(pending&~1)
    assert m.getmsg_calls==int(bool(pending&1))
    return 1


def rejects(candidate, payload, *, mode=1, x=0, y=0,
            length=None, start=BANK, mutant=None):
    m=ImageMachine(candidate,payload)
    if mutant:
        mutant(m)
    before=m.snapshot()
    assert m.draw_image(x,y,mode,start,length)==0, ("expected reject",mode,x,y)
    assert m.snapshot()==before, "rejected bank damaged bitmap"
    assert m.getmsg_calls==0, "rejected bank must not consume Safe"
    return 1


def run():
    candidate,info=build()
    assert candidate==build()[0], "R45 non-deterministic"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert BASE.read_bytes()==ARCHIVE_R44.read_bytes() and candidate==ARCHIVE_R45.read_bytes(), "R44 frozen or R45 archive mismatch"
    oldtok,old,_=split(BASE.read_bytes())
    newtok,new,_=split(candidate)
    assert len(old)==ENTRY_INDEX==55 and len(new)==56
    assert new[:54]==old[:54]
    assert new[54]==old[54]+GETP
    assert new[55]==emit_image_draw()[0]
    assert newtok.startswith(oldtok[:-6])
    report=inspect(parse(candidate))
    assert not report["issues"], report["issues"]
    named=[v for v in report["tokens"] if v["name"].startswith("aga ")]
    assert len(named)==50
    entry=[v for v in named if v["name"]=="aga image draw"]
    assert len(entry)==1
    assert (entry[0]["function"],entry[0]["signature"])==(55,"00,0,0,0,0")
    assert any(v["index"]==55 and v["parameters"]==5 and v["getp"]
               for v in report["parameter_checks"])
    asm,labels=emit_image_draw()
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    inst=list(dis.disasm(asm,0))
    assert sum(v.size for v in inst)==len(asm), "R45 contains invalid 68000 opcodes"
    starts={v.address for v in inst}
    assert all(p in starts for p in labels.values()), labels
    assert not any(v.mnemonic in ("illegal","dc.w","trap","bkpt")
                   for v in inst), "R45 opcode is not strict 68000"

    total=0
    # Exact reference image (includes visible pen 0 and masked pen 0).
    payload,pixels,mask=sample()
    for front in (0,1):
        for mode in (0,1):
            for x,y in ((0,0),(1,1),(-1,4),(7,-8),(31,17),
                        (0,20),(63,39),(-50,-30),(15,5)):
                total+=check_paint(candidate,payload,x=x,y=y,mode=mode,
                                   width=120,height=88,front=front)
    # Delayed safe reply: no CPU write; next call succeeds.
    total+=check_paint(candidate,payload,width=120,height=88,pending=1,safe_ready=False)
    total+=check_paint(candidate,payload,width=120,height=88,pending=3,safe_ready=False)
    total+=check_paint(candidate,payload,width=120,height=88,pending=3,safe_ready=True)
    for depth in (1,2,4,8):
        w,h=17,7
        pix=bytes((x+3*y)%(1<<depth) for y in range(h) for x in range(w))
        mask=bytes(int((x+y)%3!=0) for y in range(h) for x in range(w))
        for masked in (False,True):
            payload=pack_image(w,h,depth,pix,mask if masked else None)
            for mode in ((0,1) if masked else (0,)):
                for x,y in ((-9,-2),(0,0),(1,7),(15,11),(63,33)):
                    total+=check_paint(candidate,payload,x=x,y=y,mode=mode,
                                       width=64,height=40,depth=depth)

    bad=pack_image(17,7,4,bytes(17*7),bytes([1])*(17*7))
    for changes in (dict(mode=2),dict(mode=-1),dict(x=32768),
                    dict(y=-32769),dict(start=0),dict(start=BANK+1),
                    dict(length=20),dict(length=0x10000001),
                    dict(length=len(bad)+1)):
        total+=rejects(candidate,bad,**changes)
    # Reject wrong bank class, ID and length BEFORE reading pixels.
    for change in (lambda m:m.put(BANK-16,3),
                   lambda m:m.put(BANK-20,4),
                   lambda m:m.uc.mem_write(BANK-12,b'\x00\x00'),
                   lambda m:m.uc.mem_write(BANK-8,b'AGAPAL  '),
                   lambda m:m.uc.mem_write(BANK,b'BADPIC')):
        total+=rejects(candidate,bad,mutant=change)
    # Strict, TWO-PASS bank validation, before touching the back buffer.
    malformed=[
        (0,b'\x00'),  # signature corruption
        (7,b'\x02'),  # unsupported version
        (9,b'\x02'),  # reserved flags
        (11,b'\x02'), # unknown compression
        (17,b'\x09'), # depth >8
        (19,b'\x00'), # group byte width invalid (low byte nonzero)
        (23,b'\x00'), # table offset invalid (low byte 32 -> 0)
        (27,b'\x00'), # stream offset invalid (low byte nonzero)
        (31,b'\x00'), # total length invalid (low byte nonzero)
    ]
    for at,value in malformed:
        blob=bytearray(bad);blob[at:at+len(value)]=value
        total+=rejects(candidate,bytes(blob))
    total+=rejects(candidate,bad[:-1])
    # Strict row table, packet and last-group padding validation.
    parsed=parse_payload(bad)
    blob=bytearray(bad)
    struct.pack_into(">I",blob,32,0)
    total+=rejects(candidate,bytes(blob))     # row starts inside header
    blob=bytearray(bad)
    struct.pack_into(">I",blob,32+4*7,len(bad)-1)
    total+=rejects(candidate,bytes(blob))     # last row offset != payload length
    blob=bytearray(bad)
    blob[parsed.offsets[0]]=0xff
    total+=rejects(candidate,bytes(blob))     # RLE repeat count exceeds row
    blob=bytearray(bad)
    last_group_start=parsed.offsets[0]+1+10
    blob[last_group_start+1]|=1
    total+=rejects(candidate,bytes(blob))     # nonzero padded mask bit
    print("M16/R45 native CPU preliminary Gate A PASS:",total,"cases")
    print("AP20 50 commands / 56 segments, R44 byte-frozen, A3+16, D2=0")
    print("Exact opaque/masked output, right/left/top/bottom clipping, bad bank early refusal")
    print("NO AMOS/WinUAE Gate B, no Compiler/physical Amiga gate and no speed benchmark")
    print("Candidate SHA256:",info["sha256"],"bytes:",info["size"])


if __name__=="__main__":
    run()
