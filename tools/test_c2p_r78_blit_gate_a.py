#!/usr/bin/env python3
"""R78 Blit Gate A: execute actual 68000 opcode stream on Musashi CPU 68020.

Exact pixels, clipping in all directions, zero opaque, source row pitch,
invalid params/metadata, physical overlap, stale destinations, canaries,
CPU000 fail closed and full AP20/LEA provenance. NO WinUAE Gate B claimed.
"""
from __future__ import annotations
from struct import pack
from machine68k import CPUType,Register
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from build_c2p_r78_blit import build,API
from c2p_r78_blit_emit import emit_blit,BANK
from test_c2p_r74_open_gate_a import (
    Harness as OpenHarness,SAVED,CODE,STOP,STACK,STATE,DB,
    BANKPTR,EXEC,AMOS,ARGS,C2P_LIB,CONTEXT,
)
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from build_c2p_r76_rpg_fix import SITES,state_offset
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from compiler_relocation import GETP

SRC=0x130000
SRCBANK=13
SRC_SIZE=2048
BLIT_CODE=CODE+0x8000
DEST_BYTES=320*256
CANARY=b"R78_DST_CANARY"

class H(OpenHarness):
    def __init__(self,*,depth=8,cpu=CPUType.M68020,flags=2):
        super().__init__(depth=depth,cpu=cpu,flags=flags)
        self.src_ptr=SRC
        self.source_len=SRC_SIZE
        self.missing_src=False
        self.bad_mem_src=False
        self.mem.w_block(SRC,bytes([0])*SRC_SIZE)
        self.mem.w_block(SRC-24,pack(">IIIHH8s",0,SRC_SIZE+16,SRCBANK,1,0,b"SPRITE  "))
        self.mem.w_block(BANKPTR+DEST_BYTES,CANARY)
        blob,_=emit_blit()
        self.mem.w_block(BLIT_CODE,blob.replace(BANK,bytes.fromhex("4eb9")+pack(">I",0x2800)))
        assert blob.count(BANK)==2

    def bank_lookup(self,op,pc):
        self.calls.append("getadr")
        number=self.cpu.r_reg(Register.D0)
        ptr=0
        if number==self.bank:ptr=BANKPTR
        elif number==SRCBANK and not self.missing_src:ptr=self.src_ptr
        self.ret(0,a0=ptr)

    def type_of_mem(self,op,pc):
        self.calls.append("type")
        address=self.cpu.r_reg(Register.A1)
        bank_ok=(BANKPTR-24<=address<BANKPTR+self.banklength)
        source_ok=(self.src_ptr-24<=address<self.src_ptr+self.source_len)
        valid=(bank_ok or source_ok or 0x121000<=address<0x121040)
        if self.bad_mem_src and source_ok:valid=False
        self.ret(1 if valid else 0)

    def blit(self,*,bank=SRCBANK,pitch=32,sx=0,sy=0,w=16,h=16,dx=50,dy=50):
        args=(dx,h,w,sy,sx,pitch,bank)
        for i,val in enumerate(args):
            self.mem.w32(ARGS+i*4,val&0xffffffff)
        self.cpu.w_sp(STACK)
        self.mem.w32(STACK,STOP)
        for reg,value in SAVED.items():self.cpu.w_reg(reg,value)
        self.cpu.w_reg(Register.A3,ARGS)
        self.cpu.w_reg(Register.D3,dy&0xffffffff)
        self.cpu.w_reg(Register.D2,0xfee1deaf)
        prior=(self.mem.r_block(STATE,40),self.mem.r_block(DB,48))
        self.calls=[]
        self.cpu.w_pc(BLIT_CODE)
        r=self.m.execute(5_000_000)
        assert r.result is self.end,("R78 did not return",r,self.cpu.r_pc(),self.calls)
        assert self.cpu.r_sp()==STACK+4
        assert self.cpu.r_reg(Register.A3)==ARGS+28,"seven arguments not consumed"
        assert self.cpu.r_reg(Register.D2)==0
        for reg,val in SAVED.items():
            assert self.cpu.r_reg(reg)==val,("AP20 register clobbered",reg)
        assert self.mem.r_block(STATE,40)==prior[0],"blit modified screen state"
        assert self.mem.r_block(DB,48)==prior[1],"blit modified DB/front/back/cookie"
        assert self.mem.r_block(BANKPTR+DEST_BYTES,len(CANARY))==CANARY
        assert self.mem.r_block(DB+48,9)==b"DB_CANARY"
        assert not any(x in self.calls for x in ("destroy","closelib","waitblit",
            "blitbitmap","convert","openlib")),("blit called SDK/Blitter",self.calls)
        return self.cpu.r_reg(Register.D3)

def ref_blit(image,source,*,pitch,sx,sy,w,h,dx,dy):
    dest=bytearray(image)
    painted=0
    for j in range(h):
        y=dy+j
        if y<0 or y>=256:continue
        for i in range(w):
            x=dx+i
            if 0<=x<320:
                dest[y*320+x]=source[(sy+j)*pitch+sx+i]
                painted+=1
    return bytes(dest),painted

def run_valid(depth=8,*,pitch=32,sx=0,sy=0,w=16,h=16,dx=50,dy=50):
    harn=H(depth=depth)
    try:
        source=bytes((x*17+y*13)%256 for y in range(64) for x in range(32))
        harn.mem.w_block(SRC,source)
        dest=bytes((i*3+19)&255 for i in range(DEST_BYTES))
        harn.mem.w_block(BANKPTR,dest)
        assert harn.run()==1,"Open needed before Blit"
        params=dict(pitch=pitch,sx=sx,sy=sy,w=w,h=h,dx=dx,dy=dy)
        expected,npix=ref_blit(dest,source,**params)
        assert npix>0
        assert harn.blit(**params)==1
        actual=harn.mem.r_block(BANKPTR,DEST_BYTES)
        assert actual==expected,("incorrect clipping or pixels",depth,params,
                                 next((i for i,(a,b) in enumerate(zip(actual,expected))
                                       if a!=b),None))
        assert harn.mem.r_block(SRC,len(source))==source,"source bank modified"
        assert harn.calls.count("getadr")==2,"must re-fetch both banks"
        return 1
    finally:harn.cleanup()

def run_reject(label,*,alter=None,**kwargs):
    harn=H()
    try:
        assert harn.run()==1
        harn.mem.w_block(BANKPTR,bytes([91])*DEST_BYTES)
        before=harn.mem.r_block(BANKPTR,DEST_BYTES)
        if alter:alter(harn)
        before=harn.mem.r_block(BANKPTR,DEST_BYTES)
        assert harn.blit(**kwargs)==0,(label,harn.calls)
        assert harn.mem.r_block(BANKPTR,DEST_BYTES)==before,("wrote on rejected call",label)
        return 1
    finally:harn.cleanup()

def no_ctx(h):h.mem.w32(DB+40,0)
def null_lib(h):h.mem.w32(DB+24,0)
def bad_src_flags(h):h.mem.w16(SRC-12,2)
def bad_src_number(h):h.mem.w32(SRC-16,14)
def bad_src_len(h):h.mem.w32(SRC-20,16+32)
def missing_src(h):h.missing_src=True
def bad_type(h):h.bad_mem_src=True
def short_dest(h):h.mem.w32(BANKPTR-20,16+81919)
def bad_dest_flags(h):h.mem.w16(BANKPTR-12,2)
def alias(h):
    # A second, separately numbered DATA bank placed INSIDE bank 12;
    # both headers are independently valid, but the allocations overlap.
    h.src_ptr=BANKPTR+4096
    h.mem.w_block(h.src_ptr-24,
       pack(">IIIHH8s",0,2048+16,SRCBANK,1,0,b"ALIAS   "))

def cpu_000():
    h=H(cpu=CPUType.M68000,flags=0)
    try:
        # Artificially supply an active C2P context to prove CPU guard.
        for off,value in ((24,C2P_LIB),(28,CONTEXT),(32,12),(36,8),
                          (40,0x43325031)):
            h.mem.w32(DB+off,value)
        before=h.mem.r_block(BANKPTR,DEST_BYTES)
        assert h.blit()==0 and h.mem.r_block(BANKPTR,DEST_BYTES)==before
        assert not h.calls,("68000 accessed bank before CPU guard",h.calls)
        return 1
    finally:h.cleanup()

def main():
    candidate,meta=build()
    _,parts=unwrap_native_parts_v2(candidate)
    code,labels=emit_blit()
    assert len(parts)==74 and parts[73]==code and parts[72].endswith(GETP)
    assert meta["commands"]==68 and meta["ap20_entries"]==75
    assert state_offset(parts)==12070 and code.count(BANK)==2
    for i,at,opcode in SITES:
        assert parts[i][at:at+4]==opcode.to_bytes(2,"big")+bytes.fromhex("2f26")
    assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    patched=code.replace(BANK,bytes.fromhex("4eb9")+pack(">I",0x2800))
    assert len(patched)==len(code)
    decoded=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(patched,0))
    assert sum(x.size for x in decoded)==len(code),(
        "R78 unsupported or malformed 68000 native opcode",
        [(x.address,x.mnemonic,x.op_str) for x in decoded[-10:]],len(code))
    count=0
    for depth in range(4,9):
        count+=run_valid(depth=depth)
    for geometry in (
        dict(dx=-3,dy=30),dict(dx=310,dy=20),
        dict(dx=50,dy=-4),dict(dx=50,dy=247),
        dict(dx=-5,dy=-6),dict(dx=315,dy=251),
        dict(pitch=32,sx=6,sy=3,w=12,h=17,dx=13,dy=33),
        dict(pitch=32,sx=0,sy=0,w=32,h=32,dx=0,dy=0),
        dict(pitch=32,sx=0,sy=0,w=32,h=32,dx=288,dy=224),
        dict(pitch=0x7fffffff,sx=0,sy=0,w=16,h=1,dx=4,dy=4),
    ):
        count+=run_valid(**geometry)
    for label,kwargs in (
        ("no ctx",dict(alter=no_ctx)),
        ("no lib",dict(alter=null_lib)),
        ("src flags",dict(alter=bad_src_flags)),
        ("src bank header",dict(alter=bad_src_number)),
        ("src short",dict(alter=bad_src_len,sy=4)),
        ("missing src",dict(alter=missing_src)),
        ("src no memory",dict(alter=bad_type)),
        ("dest short",dict(alter=short_dest)),
        ("dest flags",dict(alter=bad_dest_flags)),
        ("physical overlap",dict(alter=alias)),
        ("same bank",dict(bank=12)),
        ("wrong src bank",dict(bank=14)),
        ("bad src pitch",dict(pitch=0)),
        ("negative pitch",dict(pitch=-2)),
        ("negative srcx",dict(sx=-1)),
        ("negative srcy",dict(sy=-1)),
        ("bad w",dict(w=0)),
        ("bad h",dict(h=0)),
        ("wide",dict(w=321)),
        ("high",dict(h=257)),
        ("row exceeds pitch",dict(sx=20,pitch=32,w=20)),
        ("out of src",dict(sy=63,h=2)),
        ("overflow srcy",dict(sy=0x7fffffff,h=3)),
        ("overflow pitch*row",dict(sy=0x70000000,pitch=16)),
        ("beyond right",dict(dx=320)),
        ("beyond left",dict(dx=-320)),
        ("beyond bottom",dict(dy=256)),
        ("beyond top",dict(dy=-256)),
        ("partial no x",dict(dx=-16)),
        ("partial no y",dict(dy=-16)),
    ):
        count+=run_reject(label,**kwargs)
    count+=cpu_000()
    assert count==46,("case count",count)
    print("R78 C2P BLIT NATIVE GATE A PASS",count,
          "68000/020 CPU, exact opaque pixels and clipping, no out-of-bounds,",
          "API/ABI and source lineage; WinUAE/Compiler NOT TESTED",meta["sha256"])

if __name__=="__main__":main()
