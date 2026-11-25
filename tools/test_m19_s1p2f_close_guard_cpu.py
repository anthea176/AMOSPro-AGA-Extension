#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exercise actual reassembled P1i UNIT142 Close/End entries and P2e.
Legacy continuation is deliberately intercepted before destructive OS work.
This is a component/route test, not full WinUAE or DMA qualification.
"""
import argparse
from pathlib import Path
from struct import pack
from build_m19_s1p2f_close_guard_in_memory import build_s1p2f
from compiler_relocation import unpack_ap20
from test_m19_s1p2e_retire_cpu import (
    Machine,CODE,STOP,GFX,CI,TABLE,VP,STACK,REC,CHIP,NEUTRAL,PRESERVED,
)
from unicorn.m68k_const import *

OWNER=0xc0000
STATE=CODE+0x1c2
SCREEN=VP-44
PATHS={
    'close':(0x7fa,0x920,0x8c8),
    'end':(0x5a,0x1ea,0x16a),
}

class Routed(Machine):
    def __init__(self,unit,root,route,flags=15,mode='ok',bound=True):
        super().__init__(unit,flags,mode)
        self.entry,self.continue_at,self.return_at=PATHS[route]
        self.root=CODE+root
        self.forwarded=0
        self.aux=0
        self.w32(OWNER+456,STATE)
        self.w32(STATE,SCREEN)
        self.w32(STATE+8,GFX)
        self.w32(STATE+32,0)
        self.w32(REC+8,VP)
        if bound:
            self.u.mem_write(self.root,pack('>4I',REC,OWNER,STATE,SCREEN))
        self.expected_root=self.read(self.root,16)
    def on_code(self,uc,addr,size,user):
        if addr==CODE+0x9e4:
            self.aux+=1
        if addr==CODE+self.continue_at:
            self.forwarded+=1
            # Legacy continuation is not tested here. Return through its
            # real original MOVEM/RTS epilogue with the original frame.
            uc.reg_write(UC_M68K_REG_PC,CODE+self.return_at)
            return
        super().on_code(uc,addr,size,user)
    def invoke(self):
        u=self.u
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(PRESERVED):u.reg_write(r,0x55000000+i)
        u.reg_write(UC_M68K_REG_A5,OWNER)
        u.reg_write(UC_M68K_REG_D0,0x12345678)
        u.reg_write(UC_M68K_REG_D1,0x87654321)
        saved={r:u.reg_read(r) for r in (*PRESERVED,UC_M68K_REG_D0,UC_M68K_REG_D1)}
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(CODE+self.entry,STOP,count=200000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items()),'legacy ABI'
        for p in (CHIP-16,CHIP+192,REC-16,REC+28):
            assert self.read(p,16)==b'\x5a'*16
        assert self.read(self.root,16)==self.expected_root,'root lost'
    def check_route(self,forward,flags,calls):
        self.invoke()
        assert (self.forwarded,self.aux)==(forward,forward),(self.forwarded,self.aux)
        assert self.r32(REC+12)==flags
        assert self.calls==calls,(self.calls,calls)

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm',type=Path,required=True)
    args=cli.parse_args()
    candidate,info=build_s1p2f(args.vasm)
    unit=unpack_ap20(candidate)[1][142]
    root=info['root']
    full=['blank','tof','tof','free3','free2','tof','tof']
    cases=0
    for path in PATHS:
        def new(flags=15,mode='ok',bound=True):
            return Routed(unit,root,path,flags,mode,bound)
        for flags in (0,4):
            m=new(flags);m.w32(REC+8,0xdead0000)
            m.check_route(1,flags,[]);cases+=1
        m=new(bound=False)
        m.check_route(1,15,[]);cases+=1
        m=new();m.check_route(1,4,full);cases+=1
        # Repeat after retirement with stale VP and newly acquired OS channel.
        m.calls=[];m.forwarded=m.aux=0
        m.w32(REC+8,0xdead0000);m.w8(GFX+166,13);m.w32(TABLE+8,0x120000)
        m.check_route(1,4,[]);cases+=1
        m=new(mode='retain')
        m.check_route(1,4,full);cases+=1
        for flags,calls in ((5,['free2','tof','tof']),
                            (7,['free3','free2','tof','tof']),
                            (13,['blank','tof','tof','free2','tof','tof'])):
            new(flags).check_route(1,4,calls);cases+=1
        for mode in ('blank_noop','blank_copper_stale','lost_owner'):
            new(mode=mode).check_route(0,15,['blank','tof','tof']);cases+=1
        for off,value in ((4,OWNER+4),(8,STATE+4),(12,SCREEN+2)):
            m=new();m.w32(m.root+off,value);m.expected_root=m.read(m.root,16)
            m.check_route(0,15,[]);cases+=1
        for addr,value in ((REC+8,VP+2),(STATE,0),(STATE+8,0),(REC+12,3)):
            m=new();m.w32(addr,value)
            m.check_route(0,3 if addr==REC+12 else 15,[]);cases+=1
        m=new();m.w16(CI+88,0x180)
        m.check_route(0,15,[]);cases+=1
        print('S1P2F_ROUTE_PASS',path,cases,flush=True)
    print('S1P2F_ROUTING_CPU_PASS',cases,info,flush=True)

if __name__=='__main__':main()
