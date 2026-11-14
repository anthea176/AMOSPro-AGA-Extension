#!/usr/bin/env python3
"""R79 Zoom native Gate A: run the exact 68k bytes and compare pixel-by-pixel.

Tests true nearest neighbour, non-integer scales, negative destination
clipping preserving source samples, bank validation, CPU ABI and canaries.
Never treats native Gate A as an AMOS/WinUAE/Compiler Gate B/C.
"""
from __future__ import annotations
from struct import pack
from machine68k import CPUType,Register
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from build_c2p_r79_zoom import build,API
from c2p_r79_zoom_emit import emit_zoom,BANK
from test_c2p_r78_blit_gate_a import (
    H as BlitHarness,SRC,SRCBANK,SRC_SIZE,DEST_BYTES,CANARY,
    no_ctx,null_lib,bad_src_flags,bad_src_number,bad_src_len,
    missing_src,bad_type,short_dest,bad_dest_flags,alias,
)
from test_c2p_r74_open_gate_a import (
    SAVED,CODE,STOP,STACK,STATE,DB,BANKPTR,EXEC,AMOS,ARGS,
    C2P_LIB,CONTEXT,
)
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from build_c2p_r76_rpg_fix import SITES,state_offset
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from compiler_relocation import GETP

ZOOM_CODE=CODE+0xc000
SOURCE=bytes((x*13+y*7+x*y*3)&255 for y in range(64) for x in range(32))

class H(BlitHarness):
    def __init__(self,*,depth=8,cpu=CPUType.M68020,flags=2):
        super().__init__(depth=depth,cpu=cpu,flags=flags)
        blob,_=emit_zoom()
        assert blob.count(BANK)==2
        patched=blob.replace(BANK,bytes.fromhex("4eb9")+pack(">I",0x2800))
        assert len(patched)==len(blob)
        self.mem.w_block(ZOOM_CODE,patched)
        self.mem.w_block(SRC,SOURCE)

    def zoom(self,*,bank=SRCBANK,pitch=32,sx=0,sy=0,sw=16,sh=16,
             dx=50,dy=40,dw=32,dh=32):
        # AP20 function ABI: D3=last DstH, nine args at (A3)+.
        params=(dw,dy,dx,sh,sw,sy,sx,pitch,bank)
        for i,value in enumerate(params):
            self.mem.w32(ARGS+i*4,value&0xffffffff)
        self.cpu.w_sp(STACK);self.mem.w32(STACK,STOP)
        for reg,value in SAVED.items():
            self.cpu.w_reg(reg,value)
        self.cpu.w_reg(Register.A3,ARGS)
        self.cpu.w_reg(Register.D3,dh&0xffffffff)
        self.cpu.w_reg(Register.D2,0xfee1deaf)
        previous=(self.mem.r_block(STATE,40),self.mem.r_block(DB,48))
        self.calls=[]
        self.cpu.w_pc(ZOOM_CODE)
        ret=self.m.execute(25_000_000)
        assert ret.result is self.end,(
            "R79 did not return normally",ret,self.cpu.r_pc(),self.calls)
        assert self.cpu.r_sp()==STACK+4
        assert self.cpu.r_reg(Register.A3)==ARGS+36,(
            "10-param ABI must consume 9 stack parameters")
        assert self.cpu.r_reg(Register.D2)==0, "R79 D2 integer result flag"
        for reg,value in SAVED.items():
            assert self.cpu.r_reg(reg)==value,("AP20 clobbered register",reg)
        assert self.mem.r_block(STATE,40)==previous[0],"screen state changed"
        assert self.mem.r_block(DB,48)==previous[1],"C2P DB state changed"
        assert self.mem.r_block(BANKPTR+DEST_BYTES,len(CANARY))==CANARY
        assert self.mem.r_block(DB+48,9)==b"DB_CANARY"
        assert not any(x in self.calls for x in ("destroy","closelib","waitblit",
               "blitbitmap","convert","openlib")),("R79 called SDK/Blitter",self.calls)
        return self.cpu.r_reg(Register.D3)

def reference(dest,source,*,pitch,sx,sy,sw,sh,dx,dy,dw,dh):
    expected=bytearray(dest)
    count=0
    for y in range(max(0,dy),min(256,dy+dh)):
        py=sy+((y-dy)*sh)//dh
        for x in range(max(0,dx),min(320,dx+dw)):
            px=sx+((x-dx)*sw)//dw
            expected[y*320+x]=source[py*pitch+px]
            count+=1
    return bytes(expected),count

def valid_case(name,depth=8,**geometry):
    h=H(depth=depth)
    try:
        assert h.run()==1,("Open failed",depth,name)
        base=dict(pitch=32,sx=0,sy=0,sw=16,sh=16,
                  dx=50,dy=40,dw=32,dh=32)
        base.update(geometry)
        dest=bytes((i*5+91)&255 for i in range(DEST_BYTES))
        h.mem.w_block(BANKPTR,dest)
        before=h.mem.r_block(SRC,len(SOURCE))
        correct,count=reference(dest,SOURCE,**base)
        assert count>0,(name,base)
        result=h.zoom(**base)
        actual=h.mem.r_block(BANKPTR,DEST_BYTES)
        assert result==1,(name,depth,base,result,h.calls)
        assert actual==correct,("wrong zoom samples",name,depth,base,
            next((i for i,(a,b) in enumerate(zip(actual,correct))
                  if a!=b),None))
        assert h.mem.r_block(SRC,len(SOURCE))==before,("source changed",name)
        assert h.calls.count("getadr")==2,("must resolve both banks",name,h.calls)
        return 1
    finally:h.cleanup()

def reject_case(name,*,mutate=None,**opts):
    h=H()
    try:
        assert h.run()==1,name
        h.mem.w_block(BANKPTR,bytes([91])*DEST_BYTES)
        if mutate:mutate(h)
        before=h.mem.r_block(BANKPTR,DEST_BYTES)
        result=h.zoom(**opts)
        assert result==0,(name,result,h.calls)
        assert h.mem.r_block(BANKPTR,DEST_BYTES)==before,(
            "rejected Zoom wrote pixels",name)
        return 1
    finally:h.cleanup()

def cpu_000():
    h=H(cpu=CPUType.M68000,flags=0)
    try:
        for off,val in ((24,C2P_LIB),(28,CONTEXT),(32,12),(36,8),
                        (40,0x43325031)):
            h.mem.w32(DB+off,val)
        before=h.mem.r_block(BANKPTR,DEST_BYTES)
        assert h.zoom()==0
        assert h.mem.r_block(BANKPTR,DEST_BYTES)==before
        assert h.calls==[],("CPU000 must reject before Bnk.GetAdr",h.calls)
        return 1
    finally:h.cleanup()

def main():
    candidate,meta=build()
    _,parts=unwrap_native_parts_v2(candidate)
    code,labels=emit_zoom()
    assert meta["commands"]==69 and meta["ap20_entries"]==76
    assert len(parts)==75 and parts[74]==code and parts[73].endswith(GETP)
    assert len(code)<10000 and code.count(BANK)==2
    assert state_offset(parts)==12070
    for e,at,op in SITES:
        assert parts[e][at:at+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
    assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    patched=code.replace(BANK,bytes.fromhex("4eb9")+pack(">I",0x2800))
    assert len(patched)==len(code)
    decoded=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(patched,0))
    assert sum(x.size for x in decoded)==len(code),(
        "non-68000 opcode or mis-encoded Zoom",
        [(x.address,x.mnemonic,x.op_str) for x in decoded[-12:]])
    total=0
    for depth in range(4,9):
        total+=valid_case("zoom x2",depth=depth)
    for name,geometry in (
        ("identity",dict(sw=32,sh=32,dw=32,dh=32)),
        ("reduce 2x",dict(sw=32,sh=32,dw=16,dh=16)),
        ("enlarge 4x",dict(sw=8,sh=8,dw=32,dh=32)),
        ("noninteger",dict(sw=13,sh=11,dw=29,dh=7)),
        ("single source pixel",dict(sx=3,sy=5,sw=1,sh=1,dw=63,dh=29)),
        ("full destination",dict(sw=32,sh=32,dx=0,dy=0,dw=320,dh=256)),
        ("edge bottom right",dict(sw=32,sh=32,dx=300,dy=240,dw=32,dh=32)),
        ("clip left",dict(sw=32,sh=32,dx=-8,dy=30,dw=64,dh=64)),
        ("clip top",dict(sw=32,sh=32,dx=30,dy=-9,dw=64,dh=64)),
        ("clip right",dict(sw=32,sh=32,dx=307,dy=50,dw=48,dh=40)),
        ("clip bottom",dict(sw=32,sh=32,dx=40,dy=235,dw=48,dh=40)),
        ("clip top left",dict(sw=29,sh=29,dx=-17,dy=-11,dw=32,dh=32)),
        ("clip bottom right",dict(sw=29,sh=29,dx=315,dy=251,dw=32,dh=32)),
        ("one visible left",dict(sw=32,sh=32,dx=-319,dy=5,dw=320,dh=32)),
        ("one visible top",dict(sw=32,sh=32,dx=5,dy=-255,dw=32,dh=256)),
        ("last pixel right",dict(sw=1,sh=1,dx=319,dy=255,dw=1,dh=1)),
        ("source subrect",dict(sx=3,sy=7,sw=11,sh=13,dx=15,dy=12,dw=29,dh=33)),
        ("uneven reduction",dict(sx=8,sy=4,sw=23,sh=17,dw=7,dh=9)),
        ("large pitch one line",dict(pitch=2048,sx=0,sy=0,sw=16,sh=1,dw=23,dh=5)),
    ):
        total+=valid_case(name,**geometry)
    for name,kwargs in (
        ("missing context",dict(mutate=no_ctx)),
        ("null SDK",dict(mutate=null_lib)),
        ("source flags",dict(mutate=bad_src_flags)),
        ("source header number",dict(mutate=bad_src_number)),
        ("source short",dict(mutate=bad_src_len,sy=4)),
        ("missing source",dict(mutate=missing_src)),
        ("source not memory",dict(mutate=bad_type)),
        ("short destination",dict(mutate=short_dest)),
        ("bad destination flags",dict(mutate=bad_dest_flags)),
        ("physical bank alias",dict(mutate=alias)),
        ("same bank id",dict(bank=12)),
        ("bad source bank id",dict(bank=14)),
        ("low source bank id",dict(bank=4)),
        ("large source bank id",dict(bank=65536)),
        ("pitch zero",dict(pitch=0)),
        ("pitch negative",dict(pitch=-1)),
        ("source X negative",dict(sx=-1)),
        ("source Y negative",dict(sy=-1)),
        ("source width zero",dict(sw=0)),
        ("source height zero",dict(sh=0)),
        ("dest width zero",dict(dw=0)),
        ("dest height zero",dict(dh=0)),
        ("source width too large",dict(sw=321)),
        ("source height too large",dict(sh=257)),
        ("dest width too large",dict(dw=321)),
        ("dest height too large",dict(dh=257)),
        ("source row overruns pitch",dict(sx=20,sw=20)),
        ("source Y beyond data",dict(sy=63,sh=2)),
        ("source size multiplication overflow",dict(sy=0x7fffffff,sh=3)),
        ("big pitch multiplication overflow",dict(pitch=0x7fffffff,sy=3)),
        ("X addition signed overflow",dict(sx=0x7fffffff,sw=2)),
        ("destination fully left",dict(dx=-319,dw=100)),
        ("destination fully top",dict(dy=-255,dh=100)),
        ("destination X too negative",dict(dx=-320)),
        ("destination Y too negative",dict(dy=-256)),
        ("destination X too large",dict(dx=320)),
        ("destination Y too large",dict(dy=256)),
    ):
        total+=reject_case(name,**kwargs)
    total+=cpu_000()
    assert total==5+19+37+1,("test case count drift",total)
    print("R79 C2P ZOOM NATIVE GATE A PASS",total,
          "exact nearest pixels, clipping, bank isolation, CPU/ABI and canaries;",
          "WinUAE/Compiler NOT TESTED",meta["sha256"],flush=True)

if __name__=="__main__":main()
