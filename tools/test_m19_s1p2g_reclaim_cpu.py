#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Run both real UNIT142 routes through CloseScreen and candidate FreeVec.
OS calls mocked; no claim of DMA/WinUAE or physical Amiga qualification.
"""
import argparse
from struct import pack
from build_m19_s1p2f_close_guard_in_memory import build_s1p2f
from compiler_relocation import unpack_ap20
from test_m19_s1p2e_retire_cpu import (
    Machine,CODE,STOP,GFX,CI,TABLE,VP,STACK,REC,CHIP,NEUTRAL,PRESERVED,SIZE,
)
from test_m19_s1p2f_close_guard_cpu import OWNER,STATE,SCREEN
from unicorn.m68k_const import *

EXEC,INTUI=0x70000,0x78000
ENTRIES={'close':0x7fa,'end':0x5a}
IDLE=CI+164
FULL=['blank','tof','tof','free3','free2','tof','tof']

class Closed(Machine):
    def __init__(self,unit,root,route,flags=15,mode='ok',bound=True):
        super().__init__(unit,flags,mode)
        self.root=CODE+root
        self.entry=CODE+ENTRIES[route]
        self.bound=bound
        self.freed=[]
        self.close_success=mode!='close_fail'
        self.w32(4,EXEC)
        for addr in (EXEC-414,EXEC-690,INTUI-66):
            self.u.mem_write(addr,b'\x4e\x75')
        self.w32(OWNER+456,STATE)
        self.w32(STATE,SCREEN)
        self.w32(STATE+4,INTUI)
        self.w32(STATE+8,GFX)
        self.w32(STATE+32,0)
        self.w32(STATE+36,0)
        self.w32(REC+8,VP)
        self.w32(GFX+34,0x110000)
        self.w32(GFX+50,0x120000)
        self.w32(GFX+54,IDLE)
        self.w32(CI+164,0xfffffffe)
        if bound:self.u.mem_write(self.root,pack('>4I',REC,OWNER,STATE,SCREEN))
    def on_write(self,uc,access,a,n,value,user):
        if STATE<=a and a+n<=STATE+40:return
        if self.root<=a and a+n<=self.root+16:return
        super().on_write(uc,access,a,n,value,user)
    def on_code(self,uc,addr,size,user):
        if addr==INTUI-66:
            assert uc.reg_read(UC_M68K_REG_A0)==SCREEN
            self.calls.append('close')
            if self.close_success:
                self.w32(GFX+34,0 if self.mode!='view_busy' else 0x110000)
                self.w32(GFX+50,IDLE if self.mode!='list_busy' else 0x120000)
                self.w32(GFX+54,IDLE)
                if self.mode=='bad_wait':self.w32(CI+164,0xffdffffe)
                if self.mode=='desc_stale':self.w32(TABLE+20,CHIP)
                if self.mode=='ptr_stale':self.copper(5,CHIP+48)
                if self.mode=='channel_reused':
                    self.w8(GFX+166,5);self.copper(2,0x150000)
            uc.reg_write(UC_M68K_REG_D0,int(self.close_success))
            return
        if addr==EXEC-690:
            p=uc.reg_read(UC_M68K_REG_A1)
            assert self.close_success and self.calls.count('close')==1
            assert self.read(self.root,16)==bytes(16)
            assert p==(CHIP if not self.freed else REC)
            assert p not in self.freed
            assert self.r32(REC+12) in (0,4)
            self.freed.append(p)
            self.calls.append('free_chip' if p==CHIP else 'free_record')
            self.u.mem_write(p,b'\xA5'*(SIZE if p==CHIP else 28))
            return
        if addr==EXEC-414:
            p=uc.reg_read(UC_M68K_REG_A1)
            assert p in (GFX,INTUI)
            self.calls.append('close_gfx' if p==GFX else 'close_intui')
            return
        if addr==GFX-270 and self.mode=='view_changes' and 'close' in self.calls:
            self.w32(GFX+34,0x110000)
        super().on_code(uc,addr,size,user)
    def invoke(self):
        u=self.u
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(PRESERVED):u.reg_write(r,0x55001000+i)
        u.reg_write(UC_M68K_REG_A5,OWNER)
        u.reg_write(UC_M68K_REG_D0,0x12345678)
        u.reg_write(UC_M68K_REG_D1,0x87654321)
        saved={r:u.reg_read(r) for r in (*PRESERVED,UC_M68K_REG_D0,UC_M68K_REG_D1)}
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(self.entry,STOP,count=250000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items()),'legacy ABI'
        for p in (CHIP-16,CHIP+SIZE,REC-16,REC+28):
            assert self.read(p,16)==b'\x5a'*16
    def check(self,free,screen,closed,calls):
        self.invoke()
        assert self.freed==([CHIP,REC] if free else []),(self.mode,self.freed)
        assert self.r32(STATE)==screen
        assert self.r32(STATE+8)==(0 if closed else GFX)
        assert self.r32(STATE+4)==(0 if closed else INTUI)
        assert self.calls==calls,(self.mode,self.calls,calls)
        if free or not self.bound:assert self.read(self.root,16)==bytes(16)
        else:
            assert self.r32(self.root)==REC
            assert self.r32(self.root+12)==(0 if closed else SCREEN)

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm',required=True)
    args=cli.parse_args()
    candidate,info=build_s1p2f(args.vasm,reclaim=True)
    unit=unpack_ap20(candidate)[1][142]
    root=info['root']
    cases=0
    finish=['close_gfx','close_intui']
    for route in ENTRIES:
        def new(flags=15,mode='ok',bound=True):
            return Closed(unit,root,route,flags,mode,bound)
        m=new()
        m.check(True,0,True,FULL+['close','tof','tof','free_chip','free_record']+finish);cases+=1
        m.calls=[]
        m.invoke()
        assert m.calls==[] and m.freed==[CHIP,REC];cases+=1
        new(0).check(True,0,True,['close','free_chip','free_record']+finish);cases+=1
        new(bound=False).check(False,0,True,['close']+finish);cases+=1
        new(mode='close_fail').check(False,SCREEN,False,FULL+['close']);cases+=1
        for mode in ('view_busy','list_busy','bad_wait','channel_reused','retain'):
            new(mode=mode).check(False,0,True,FULL+['close']+finish);cases+=1
        for mode in ('view_changes','desc_stale','ptr_stale'):
            new(mode=mode).check(False,0,True,FULL+['close','tof','tof']+finish);cases+=1
        m=new(mode='close_fail')
        m.check(False,SCREEN,False,FULL+['close']);cases+=1
        m.close_success=True;m.mode='ok';m.calls=[]
        m.check(True,0,True,['close','tof','tof','free_chip','free_record']+finish);cases+=1
        print('S1P2G_ROUTE_PASS',route,cases,flush=True)
    print('S1P2G_RECLAIM_CPU_PASS',cases,info,flush=True)

if __name__=='__main__':main()
