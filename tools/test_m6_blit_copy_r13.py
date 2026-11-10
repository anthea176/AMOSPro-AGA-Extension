#!/usr/bin/env python3
"""M6/R13: execute actual 68000 Copy entry with mocked graphics.library.

Covers AP20 GetP stack consumption, AMOS registers, front/back selection,
strict geometry rejection, masked/misaligned and overlapping rectangle
semantics, and mandatory WaitBlit. CPU/logic gate ONLY, not WinUAE PASS.
"""
from struct import pack

from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000

from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from build_m6_blit_copy_r13 import build, BASE, LAST_GOOD,     BASE_SHA256, LAST_GOOD_SHA256, emit_copy, ENTRY
from test_m5_generic import (
    Machine, CODE, GFX, STATE, AMOS, DB, SB, BITMAP, SCREEN, STACK, STOP,
    DR, AR,
)


class CopyMachine(Machine):
    def __init__(self, raw, width=320, height=256, depth=4, front=0):
        rowbytes = ((width+15)//16)*2
        meta = dict(width=width, height=height, depth=depth,
                    camg=0x21000, row_bytes=rowbytes)
        super().__init__(raw, None, meta)
        self.uc.mem_write(GFX-30, bytes.fromhex("4e75"))
        self.uc.mem_write(BITMAP+0x100, bytes(self.uc.mem_read(BITMAP, 40)))
        self.put(SB+0x100, BITMAP+0x100)
        self.put(DB, SB)
        self.put(DB+4, SB+0x100)
        self.put(DB+8, front)
        self.expected_bitmap = BITMAP+0x100 if front == 0 else BITMAP
        self.blits = []
        self.waits = 0
        self.pending = None
        for i, pointer in enumerate(self.planes):
            self.uc.mem_write(pointer, bytes(((17*i+23*n) & 255)
                                              for n in range(self.plane_size)))

    def snapshot(self):
        return [bytes(self.uc.mem_read(p, self.plane_size)) for p in self.planes]

    def perform_pending(self):
        if self.pending is None:
            return
        sx,sy,dx,dy,w,h = self.pending
        # Snapshot source before writing; this models memmove/overlap.
        before = [bytearray(p) for p in self.snapshot()]
        after = [bytearray(p) for p in before]
        stride = self.stride
        for plane in range(len(self.planes)):
            for y in range(h):
                for x in range(w):
                    si = (sy+y)*stride + (sx+x)//8
                    di = (dy+y)*stride + (dx+x)//8
                    bit = 1 << (7-((sx+x)&7))
                    destbit = 1 << (7-((dx+x)&7))
                    if before[plane][si] & bit:
                        after[plane][di] |= destbit
                    else:
                        after[plane][di] &= 255 ^ destbit
            self.uc.mem_write(self.planes[plane], bytes(after[plane]))
        self.pending = None

    def os_call(self, uc, address, size, user):
        if address == GFX-30:
            assert self.a(0) == self.a(1) == self.expected_bitmap
            assert self.a(2) == 0, "TempA must be NULL"
            assert self.d(6) & 255 == 0xC0 and self.d(7) & 255 == 255
            sx,sy,dx,dy,w,h = [self.d(i) for i in range(6)]
            assert 0 <= sx and 0 <= sy and 0 <= dx and 0 <= dy
            assert w > 0 and h > 0
            assert sx+w <= self.meta['width'] and dx+w <= self.meta['width']
            assert sy+h <= self.meta['height'] and dy+h <= self.meta['height']
            assert self.pending is None, "previous blit not synchronized"
            self.pending = sx,sy,dx,dy,w,h
            self.blits.append(self.pending)
            # Simulate volatile AmigaOS caller-scratch registers.
            uc.reg_write(DR[0], self.meta['depth'])
            uc.reg_write(DR[1], 0xDEADBEEF)
            uc.reg_write(AR[0], 0xBAD000)
            uc.reg_write(AR[1], 0xBAD100)
            return_pc = self.get(self.a(7))
            uc.reg_write(AR[7], self.a(7)+4)
            uc.reg_write(UC_M68K_REG_PC, return_pc)
            return
        if address == GFX-228:
            self.waits += 1
            self.perform_pending()
        super().os_call(uc, address, size, user)

    def run_copy(self, args):
        assert len(args) == 6
        for i,reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200+i)
        for i,reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], 0x58000)
        sx,sy,dx,dy,w,h = args
        for i,value in enumerate((w,dy,dx,sy,sx)):
            self.put(0x58000+4*i, value)
        self.uc.reg_write(DR[3], h)
        saved = {r:self.uc.reg_read(r) for r in DR + AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY], STOP, count=200000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4, "CPU stack unbalanced"
        for reg,old in saved.items():
            if reg in (DR[2], DR[3], AR[3]):
                continue
            assert self.uc.reg_read(reg) == old, (reg,old,self.uc.reg_read(reg))
        assert self.d(2) == 0, "AMOS result type not integer"
        assert self.a(3) == 0x58000+20, "GetP A3 consumption must be +20"
        return self.d(3)


def run():
    candidate, report = build()
    assert build()[0] == candidate, "builder non-reproducible"
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    tok0,seg0,_ = split(BASE.read_bytes())
    tok1,seg1,_ = split(candidate)
    assert len(seg0) == 19 and len(seg1) == 20
    assert seg0[:18] == seg1[:18]
    assert seg1[18] == seg0[18] + b"GetP"
    assert seg1[19] == emit_copy()[0]
    audited=inspect(parse(candidate))
    assert not audited["issues"]
    row=[x for x in audited["tokens"] if x['name']=='aga blit copy']
    assert len(row)==1 and row[0]['function']==19
    assert row[0]['signature']=='00,0,0,0,0,0'
    asm,labels=emit_copy()
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    decoded=list(dis.disasm(asm,0))
    assert sum(i.size for i in decoded)==len(asm)
    boundaries={i.address for i in decoded}
    assert all(pos in boundaries for pos in labels.values())
    assert all(i.mnemonic not in ('dc.w','illegal') for i in decoded)

    for front in (0,1):
        for args in ((0,0,160,128,96,80),
                     (160,128,176,144,96,80),
                     (1,3,2,5,41,19),
                     (0,0,0,0,320,256),
                     (0,0,319,255,1,1)):
            m=CopyMachine(candidate,front=front)
            before=m.snapshot()
            assert m.run_copy(args)==1, args
            assert m.blits == [args] and m.waits==1 and m.pending is None
            if args[0:2]!=args[2:4]:
                assert m.snapshot()!=before, args
    invalid=(
        (-1,0,0,0,1,1),(0,-1,0,0,1,1),
        (0,0,-1,0,1,1),(0,0,0,-1,1,1),
        (0,0,0,0,0,1),(0,0,0,0,1,0),
        (0,0,0,0,-1,1),(0,0,0,0,1,-1),
        (310,0,0,0,20,1),(0,250,0,0,1,20),
        (0,0,310,0,20,1),(0,0,0,250,1,20),
        (0x7fffffff,0,0,0,1,1),
        (0,0,0,0,0x7fffffff,1),
    )
    for args in invalid:
        m=CopyMachine(candidate)
        before=m.snapshot()
        assert m.run_copy(args)==0, args
        assert m.blits==[] and m.waits==0 and m.snapshot()==before

    for field,offset,value in (
        ('screen',0,0),
        ('gfx',8,0),
        ('dbstate',32,0),
        ('bad_width',12,0x10000),
        ('bad_height',16,0),
        ('bad_depth',28,9),
    ):
        m=CopyMachine(candidate)
        m.put(STATE+offset,value)
        assert m.run_copy((0,0,0,0,64,32))==0, field
        assert not m.blits
    for case in ('no_sb','no_bitmap','short_stride','short_rows','depth_mismatch'):
        m=CopyMachine(candidate)
        if case=='no_sb':
            m.put(DB+4,0)
        elif case=='no_bitmap':
            m.put(SB+0x100,0)
        elif case=='short_stride':
            m.uc.mem_write(BITMAP+0x100,pack('>H',2))
        elif case=='short_rows':
            m.uc.mem_write(BITMAP+0x102,pack('>H',1))
        else:
            m.uc.mem_write(BITMAP+0x105,bytes([3]))
        assert m.run_copy((0,0,0,0,64,32))==0, case
        assert not m.blits

    print("M6 R13 CPU PASS: 10 valid blits + overlap/un-aligned, "
          "14 bounds rejects, 6 state rejects, 5 bitmap rejects, "
          "GetP +20, D2=0, preserved registers, WaitBlit once")
    print("M6 preview SHA256",report['sha256'],"bytes",report['size'])
    print("Runtime: NOT TESTED under AMOS/WinUAE/Compiler/hardware")


if __name__=="__main__":
    run()
