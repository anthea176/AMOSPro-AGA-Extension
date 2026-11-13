#!/usr/bin/env python3
"""OPT020/P3 Fast Icons real native 68020 Gate A (no WinUAE, no binary output).

Run both production emitters in Musashi: full FICON8 Capture with real
AMOS/Exec/Graphics trap-backed memory, and Draw's native 16x16 core.
Opaque/masked, 8 planes, aligned/unaligned X, clipping, ABI, Safe, canaries.
No benchmarks and no changes to the active R72 Lib or tests/current/.
"""
from __future__ import annotations
from hashlib import sha256
from random import Random
from struct import pack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from machine68k import Machine, CPUType, Register

from m18_ficon16_model import build_bank, parse_bank, draw_cpu
from m18_ficon16_native_shifted_emit import emit_ficon16_shifted_cpu
from m18_ficon_ap20_emit import emit_ficon_ap20
from m18_ficon_capture_emit import emit_ficon_capture, GETADR_MARKER
from opt020_p1_bitfield_emit import bitfield_020

CODE=0x1c000
STOP=0x1800
EXEC=0x8000
GFX=0x9000
BANK_SERVICE=0x2800
AMOS=0x32000
STATE=0x34000
DB=0x34200
SB0=0x34400
SB1=0x34500
BMP0=0x34600
BMP1=0x34700
PORT=0x34800
BACK=0x40000
FRONT=0x80000
BANK=0xc0000
PARAMS=0xd0000
STACK=0xe0000
WIDTH=64
HEIGHT=42
STRIDE=12
DEPTH=8
SAVE = {
    Register.D0:0x12345678, Register.D1:0x23456789,
    Register.D4:0x456789ab, Register.D5:0x56789abc,
    Register.D6:0x6789abcd, Register.D7:0x789abcde,
    Register.A0:0x30000, Register.A1:0x30200,
    Register.A2:0x30400, Register.A4:0x30600,
    Register.A5:AMOS, Register.A6:0x30800,
}


def pixels(width=WIDTH,height=HEIGHT,seed=0):
    # Check high AGA palette bits, repeated zero and all indices 0..255.
    return bytes((((x*29+y*17+seed*13)^((x*y)>>2))&255)
                 for y in range(height) for x in range(width))


def planar(pixels_,width=WIDTH,height=HEIGHT,stride=STRIDE):
    out=[bytearray(stride*height) for _ in range(8)]
    for y in range(height):
        for x in range(width):
            v=pixels_[y*width+x]
            for plane in range(8):
                if v&(1<<plane):
                    out[plane][y*stride+(x>>3)] |= 0x80>>(x&7)
    return tuple(bytes(p) for p in out)


class Harness:
    def __init__(self,code,cpu_type,kind,*,front=0,pending=0,safe_ready=True,
                 attnflags=2):
        self.m=Machine(cpu_type,1024)
        self.mem,self.cpu=self.m.mem,self.m.cpu
        self.kind=kind
        self.front=front
        self.pending=pending
        self.safe_ready=safe_ready
        self.calls={"bank":0,"type":0,"getmsg":0,"waitblit":0}
        self.mem.w32(0,STACK)
        self.mem.w32(4,CODE)
        self.cpu.execute(self.cpu.pulse_reset())
        self.mem.w32(4,EXEC)
        self.mem.w16(EXEC+0x128,attnflags)
        self.end=self.m.create_execute_end("opt020-p3-done")
        self.trap(STOP,lambda _op,_pc:self.end)
        self.trap(BANK_SERVICE,self.bank_lookup)
        self.trap(EXEC-534,self.type_of_mem)
        self.trap(EXEC-372,self.get_msg)
        self.trap(GFX-228,self.wait_blit)
        self.mem.w_block(CODE,code)
        self.mem.w32(AMOS+0x1c8,STATE)
        for off,val in ((0,0x35000),(8,GFX),(12,WIDTH),(16,HEIGHT),
                        (28,DEPTH),(32,DB)):
            self.mem.w32(STATE+off,val)
        for off,val in ((0,SB0),(4,SB1),(8,front),(12,PORT),(20,pending)):
            self.mem.w32(DB+off,val)
        self.mem.w32(SB0,BMP0)
        self.mem.w32(SB1,BMP1)
        self.physical={}
        for index,prefix in enumerate((BACK,FRONT)):
            bank=planar(pixels(seed=index+1))
            addresses=[prefix+0x3000*i for i in range(DEPTH)]
            self.physical[prefix]=addresses
            for p,a in zip(bank,addresses):
                self.mem.w_block(a,p)
                self.mem.w_block(a-16,bytes([0xA7])*16)
                self.mem.w_block(a+STRIDE*HEIGHT,bytes([0x7A])*16)
        for bmp,ptrs in ((BMP0,self.physical[FRONT if front==0 else BACK]),
                         (BMP1,self.physical[BACK if front==0 else FRONT])):
            self.mem.w_block(bmp,pack(">HHBBH",STRIDE,HEIGHT,0,DEPTH,0))
            for i,address in enumerate(ptrs):
                self.mem.w32(bmp+8+4*i,address)
        self.backptrs=self.physical[BACK]
        self.frontptrs=self.physical[FRONT]
        self.back_before=self.read_planes(self.backptrs)
        self.front_before=self.read_planes(self.frontptrs)
        original=[bytes([((p*13+i*17)&255) for i in range(256)])
                  for p in range(4)]
        self.bankraw=build_bank(tuple(original))
        self.mem.w_block(BANK,self.bankraw)
        self.mem.w_block(BANK-24,pack(">IIIHH8s",
                         0,len(self.bankraw)+16,12,1,0,b"FICON8  "))
        self.mem.w_block(BANK+len(self.bankraw),b"\xD3"*16)

    def trap(self,addr,cb):
        ident=self.m.traps.alloc(cb)
        self.mem.w16(addr,0xA000|ident)

    def result_from_service(self,d0=0,a0=None):
        sp=self.cpu.r_sp()
        pc=self.mem.r32(sp)
        self.cpu.w_sp(sp+4)
        self.cpu.w_pc(pc)
        self.cpu.w_reg(Register.D0,d0&0xffffffff)
        self.cpu.w_reg(Register.D1,0xDEADBEEF)
        self.cpu.w_reg(Register.A0,0xBAD000 if a0 is None else a0)
        self.cpu.w_reg(Register.A1,0xBAD100 if a0 is None else a0)

    def bank_lookup(self,_op,_pc):
        self.calls["bank"]+=1
        assert self.cpu.r_reg(Register.A5)==AMOS
        ptr=BANK if self.cpu.r_reg(Register.D0)==12 else 0
        self.result_from_service(1 if ptr else 0,a0=ptr)

    def type_of_mem(self,_op,_pc):
        self.calls["type"]+=1
        address=self.cpu.r_reg(Register.A1)
        is_bank=BANK-24<=address<BANK+len(self.bankraw)
        is_chip=any(a<=address<a+STRIDE*HEIGHT for addrs in
                    (self.backptrs,self.frontptrs) for a in addrs)
        self.result_from_service(1 if is_bank else 3 if is_chip else 0)

    def get_msg(self,_op,_pc):
        self.calls["getmsg"]+=1
        assert self.cpu.r_reg(Register.A0)==PORT
        self.result_from_service(0x34900 if self.safe_ready else 0)

    def wait_blit(self,_op,_pc):
        self.calls["waitblit"]+=1
        self.result_from_service(0)

    def read_planes(self,ptrs):
        return tuple(self.mem.r_block(a,STRIDE*HEIGHT) for a in ptrs)

    def checks(self):
        assert self.read_planes(self.frontptrs)==self.front_before
        for ptrs in (self.backptrs,self.frontptrs):
            for a in ptrs:
                assert self.mem.r_block(a-16,16)==b"\xA7"*16
                assert self.mem.r_block(a+STRIDE*HEIGHT,16)==b"\x7A"*16
        assert self.mem.r_block(BANK+len(self.bankraw),16)==b"\xD3"*16

    def run(self,*,x,y,mode=0,icon=2,bank=12,entry="capture"):
        self.cpu.w_sp(STACK)
        self.mem.w32(STACK,STOP)
        for reg,value in SAVE.items():
            self.cpu.w_reg(reg,value)
        if entry in ("capture","wrapper"):
            self.cpu.w_reg(Register.D3,(
                y if entry=="capture" else mode)&0xffffffff)
            self.cpu.w_reg(Register.A3,PARAMS)
            values=(x,icon,bank) if entry=="capture" else (y,x,icon,bank)
            for i,value in enumerate(values):
                self.mem.w32(PARAMS+i*4,value&0xffffffff)
        else:
            self.cpu.w_reg(Register.A0,BANK+12+(icon-1)*288)
            self.cpu.w_reg(Register.A1,PARAMS)
            for i,p in enumerate(self.backptrs):self.mem.w32(PARAMS+i*4,p)
            self.cpu.w_reg(Register.D0,x&0xffffffff)
            self.cpu.w_reg(Register.D1,y&0xffffffff)
            self.cpu.w_reg(Register.D2,STRIDE)
            self.cpu.w_reg(Register.D3,mode)
            self.cpu.w_reg(Register.D4,WIDTH)
            self.cpu.w_reg(Register.D5,HEIGHT)
            self.cpu.w_reg(Register.A3,0x2F000)
        saved={reg:self.cpu.r_reg(reg) for reg in SAVE}
        if entry=="draw":
            # A0/A1/D0/D1/D4/D5 are genuine core inputs.
            for key in (Register.A0,Register.A1,Register.D0,Register.D1,
                        Register.D4,Register.D5):
                saved[key]=self.cpu.r_reg(key)
        try:
            res=self.m.execute(5_000_000)
        except Exception as exc:
            raise AssertionError(("Native CPU exception",self.kind,entry,x,y,
                                  mode,hex(self.cpu.r_pc()))) from exc
        assert res.result is self.end,("CPU did not return",self.kind,
                                       entry,x,y,self.cpu.r_pc(),res)
        assert self.cpu.r_sp()==STACK+4,"A7 leak"
        assert self.cpu.r_reg(Register.A3)==(
            PARAMS+12 if entry=="capture" else
            PARAMS+16 if entry=="wrapper" else 0x2F000),"A3 modified"
        assert self.cpu.r_reg(Register.D2)==0,"AP20 D2 not cleared"
        for reg,val in saved.items():
            assert self.cpu.r_reg(reg)==val,("register clobber",reg,
                                            self.kind,entry,x,y)
        return self.cpu.r_reg(Register.D3)

    def close(self):
        self.m.cleanup()


def capture_one(binary,*,cpu_type,front,x,y,pending=0,expected=True,
                attnflags=2):
    # Patch only the authorised 6-byte AMOS Bnk.GetAdr relocatable marker.
    assert binary.count(GETADR_MARKER)==1
    code=binary.replace(GETADR_MARKER,b"\x4e\xb9"+pack(">I",BANK_SERVICE))
    assert len(code)==len(binary)
    m=Harness(code,cpu_type,"Capture",front=front,pending=pending,
              attnflags=attnflags)
    try:
        result=m.run(x=x,y=y,entry="capture")
        assert result==int(expected),("capture D3",cpu_type,front,x,y,result)
        m.checks()
        assert m.read_planes(m.backptrs)==m.back_before
        after=m.mem.r_block(BANK,len(m.bankraw))
        if expected:
            taken=bytes(pixels(seed=1)[
                yy*WIDTH+xx] for yy in range(y,y+16) for xx in range(x,x+16))
            expected_slot=build_bank((taken,)*4)[12:300]
            expected_bank=bytearray(m.bankraw)
            off=12+288
            expected_bank[off:off+288]=expected_slot
            assert after==bytes(expected_bank),("capture pixel mismatch",x,y,front)
            assert m.calls["waitblit"]==1
            assert m.calls["getmsg"]==int(bool(pending&1))
        else:
            assert after==m.bankraw,"invalid capture touched the bank"
            assert m.calls["waitblit"]==0
            if not (attnflags&2):
                assert m.calls["bank"]==m.calls["getmsg"]==0
        return 1
    finally:m.close()


def draw_one(core,*,cpu_type,x,y,mode,expected_ok=True,attnflags=2):
    m=Harness(core,cpu_type,"Draw",front=0,attnflags=attnflags)
    try:
        baseline=[bytearray(p) for p in m.back_before]
        expected=[bytearray(p) for p in baseline]
        bank=parse_bank(m.bankraw)
        if expected_ok:
            draw_cpu(bank,2,x,y,mode,expected,WIDTH,HEIGHT,STRIDE,
                     alignment="pixel")
        result=m.run(x=x,y=y,mode=mode,entry="draw")
        assert result==int(expected_ok),(
            "draw result",cpu_type,x,y,mode,result)
        got=m.read_planes(m.backptrs)
        assert got==tuple(bytes(p) for p in expected),(
            "draw pixel mismatch",cpu_type,x,y,mode,
            next((p for p in range(DEPTH)
                  if got[p]!=bytes(expected[p])),None))
        assert m.mem.r_block(BANK,len(m.bankraw))==m.bankraw
        assert m.calls=={"bank":0,"type":0,"getmsg":0,"waitblit":0}
        m.checks()
        return 1
    finally:m.close()


def wrapper_one(wrapper,*,cpu_type,front,x,y,mode=0,bank=12,icon=2,
                pending=0,safe_ready=True,expected_ok=True,attnflags=2):
    assert wrapper.count(GETADR_MARKER)==1
    code=wrapper.replace(GETADR_MARKER,b"\x4e\xb9"+pack(">I",BANK_SERVICE))
    m=Harness(code,cpu_type,"Draw AP20",front=front,
              pending=pending,safe_ready=safe_ready,attnflags=attnflags)
    try:
        baseline=[bytearray(p) for p in m.back_before]
        target=[bytearray(p) for p in baseline]
        if expected_ok:
            draw_cpu(parse_bank(m.bankraw),icon,x,y,mode,target,
                     WIDTH,HEIGHT,STRIDE,alignment="pixel")
        result=m.run(x=x,y=y,mode=mode,icon=icon,bank=bank,entry="wrapper")
        assert result==int(expected_ok),("Aga F Icon return",cpu_type,
                                         x,y,mode,bank,icon,result)
        assert m.read_planes(m.backptrs)==tuple(bytes(p) for p in target),(
            "Aga F Icon AP20 pixels",cpu_type,x,y,mode,front)
        assert m.mem.r_block(BANK,len(m.bankraw))==m.bankraw
        assert m.calls["waitblit"]==0
        if expected_ok:
            assert m.calls["bank"]==1,"Bnk.GetAdr not invoked"
            visible=(-16<x<WIDTH and -16<y<HEIGHT)
            assert m.calls["getmsg"]==int(bool(pending&1) and visible)
        else:
            assert m.calls["getmsg"]<=int(bool(pending&1))
            if not (attnflags&2):
                assert m.calls["bank"]==m.calls["getmsg"]==0
        m.checks()
        return 1
    finally:m.close()


def main():
    old_core,_=emit_ficon16_shifted_cpu()
    new_core,l_draw=emit_ficon16_shifted_cpu(opt020=True)
    old_capture,_=emit_ficon_capture()
    new_capture,l_cap=emit_ficon_capture(opt020=True)
    wrapper,l_wrapper=emit_ficon_ap20(opt020=True)
    assert wrapper.endswith(new_core)
    assert l_wrapper["core"] < len(wrapper)
    assert old_core!=new_core and old_capture!=new_capture
    assert "p3_plane" in l_draw and "pixel" not in l_cap
    decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
    for name,blob in (("Draw core",new_core),("Capture",new_capture)):
        inst=list(decoder.disasm(blob,CODE))
        assert sum(i.size for i in inst)==len(blob),(
            "M68K instruction decoding failed",name,len(blob),
            sum(i.size for i in inst))
        names=[i.mnemonic.lower().split(".")[0] for i in inst]
        assert "bfins" in names or "bfextu" in names
        assert not any(v in ("illegal","trap","dc","bkpt","stop") for v in names)
    assert new_capture.count(bitfield_020(
        0xe9c0,4,4,offset_reg=1,width=16))==1

    tested=0
    for cpu_type in (CPUType.M68EC020,CPUType.M68020):
        for x,y in ((0,0),(1,1),(7,3),(8,2),(15,5),(16,6),
                    (31,7),(48,26)):
            for front in (0,1):
                tested+=capture_one(new_capture,cpu_type=cpu_type,
                                    front=front,x=x,y=y,pending=x&1)
        for x,y in ((-16,3),(-7,3),(-1,3),(0,0),(1,1),(7,8),
                    (8,4),(15,8),(16,16),(31,1),(32,-8),
                    (47,12),(48,26),(54,14),(63,39),(64,3),
                    (8,42),(8,-16)):
            for mode in (0,1):
                tested+=draw_one(new_core,cpu_type=cpu_type,x=x,y=y,mode=mode)
    # Historical core must match the same pixel oracle on representative paths.
    for x,y,mode in ((0,0,0),(1,1,1),(-7,3,0),(48,26,1)):
        tested+=draw_one(old_core,cpu_type=CPUType.M68020,x=x,y=y,mode=mode)
    for x,y in ((-1,3),(49,3),(3,-1),(3,27)):
        tested+=capture_one(new_capture,cpu_type=CPUType.M68020,
                            front=0,x=x,y=y,expected=False)
    for cpu_type in (CPUType.M68EC020,CPUType.M68020):
        for x,y,mode in ((0,0,0),(1,1,1),(7,8,0),(15,5,1),
                         (32,13,0),(48,26,1),(-7,9,1),
                         (54,14,0),(64,3,0)):
            tested+=wrapper_one(wrapper,cpu_type=cpu_type,front=0,
                                x=x,y=y,mode=mode,pending=x&1)
        for x,y,mode,bank,icon,safe_ready in (
            (8,8,2,12,2,True), (8,8,1,4,2,True),
            (8,8,1,12,0,True),(8,8,1,12,2,False)):
            tested+=wrapper_one(wrapper,cpu_type=cpu_type,front=1,
                                x=x,y=y,mode=mode,bank=bank,icon=icon,
                                pending=1,safe_ready=safe_ready,
                                expected_ok=False)
    # 68000/68010-class CPU or missing Exec AFF_68020: no BFxxx may run.
    # All three call surfaces must reject *before* bank/Safe/memory writes.
    for cpu_type,flags in ((CPUType.M68000,0),(CPUType.M68020,0)):
        tested+=capture_one(new_capture,cpu_type=cpu_type,front=0,
                            x=7,y=3,expected=False,attnflags=flags)
        tested+=draw_one(new_core,cpu_type=cpu_type,x=7,y=3,mode=1,
                         expected_ok=False,attnflags=flags)
        tested+=wrapper_one(wrapper,cpu_type=cpu_type,front=0,
                            x=7,y=3,mode=1,pending=1,expected_ok=False,
                            attnflags=flags)
    print("OPT020 P3 NATIVE CPU GATE A PASS",tested,
          "capture+draw real 68EC020/68020 cases, 8 planes, ABI, guards")
    print("Only source emitters tested; P3 AP20/WinUAE candidate NOT validated.")


if __name__=="__main__":
    main()
