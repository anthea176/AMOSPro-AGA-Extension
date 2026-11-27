#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-assembled attached frame change, V40 OS behavior model.

P0c historical tests remain intact. No actual DMA/raster or OS timing.
"""
import argparse
from pathlib import Path
from struct import pack
from unicorn.m68k_const import *
from test_m19_s2c_attached_lifecycle_cpu import (
    AttachedMachine, PAIRS, ACQUIRE, SHOW, MOVE, RETIRE, RGB, VP, CM,
    CODE, STOP, EXEC, GFX, CI, TABLE, STACK, RECS, CHIPS, BLANK, REGS)

CHANGE=20
SCRATCH=0x190000
LOF,SHF=0x1a0000,0x1a1000

class FrameMachine(AttachedMachine):
    def __init__(self,code):
        super().__init__(code)
        self.w32(GFX+50,LOF)
        self.w32(GFX+54,SHF)
        self.entry=None
        self.scratch_len=0
        self.source_addr=SCRATCH
        self.source_extent=None
        self.fail_hide=False
        self.fail_reveal=False
        self.slot_before=None
        self.slot_after=None
        self.staged=0
        self.wait_start=0
        self.wait_hook=None
        self.events=[]
        self.map_source=True
        self.change_after=None
    def ptr(self,n,slot,odd=False):
        return CHIPS[n]+96+(slot*2+int(odd))*(8+4*self.heights[n])
    def make_scratch(self,n,ident=2,seed=0):
        length=self.lengths[n];h=self.heights[n];stream=8+4*h
        colors=self.u16(CHIPS[n]+30)
        desc=pack('>I4H',0,h,0,0,65535)
        hdr=desc*2+pack('>I2HI2h48s2I',length,ident,colors,2,0,0,
                        bytes(3)+RGB[:3*colors]+bytes(45-3*colors),stream,96)
        even=bytes((i*11+seed+5)&255 for i in range(h*4))
        odd=bytes((i*17+seed+91)&255 for i in range(h*4))
        b=hdr+bytes(4)+even+bytes(8)+odd+bytes(4)+bytes(2*stream)
        assert len(b)==length
        self.scratch_len=length
        self.source_addr=SCRATCH
        self.source_extent=length
        self.u.mem_write(SCRATCH-16,bytes([0x9a])*16)
        self.u.mem_write(SCRATCH,b)
        self.u.mem_write(SCRATCH+length,bytes([0xc9])*16)
        return b
    def move_model(self,desc,x,y):
        ch=self.u16(desc+10);n=self.current
        assert ch in (n,n+1)
        p=self.u32(desc)
        assert p in (self.ptr(n,0,bool(ch&1)),self.ptr(n,1,bool(ch&1)))
        self.w16(desc+6,x);self.w16(desc+8,y)
        self.w32(TABLE+4*ch,desc)
        if not ch&1:
            odd=self.u32(TABLE+4*(ch+1))
            if odd:
                assert odd==CHIPS[n]+12
                if self.u8(self.u32(odd)+3)&128:self.move_model(odd,x,y)
        ctl=((y+self.heights[n])&255)<<8|(self.u8(p+3)&128)
        if y>=256:ctl|=4
        self.w32(p,((y&255)<<24)|((x&255)<<16)|ctl)
        self.pointer(ch,BLANK if y>256 else p)
    def os(self,u,address,size,user):
        d0=u.reg_read(UC_M68K_REG_D0);d1=u.reg_read(UC_M68K_REG_D1)
        a0=u.reg_read(UC_M68K_REG_A0);a1=u.reg_read(UC_M68K_REG_A1)
        a2=u.reg_read(UC_M68K_REG_A2);n=self.current
        if address==EXEC-534 and SCRATCH<=a1<SCRATCH+self.scratch_len:
            self.volatile(3 if self.map_source else 1)
        elif address==GFX-270:
            self.events.append('wait')
            super().os(u,address,size,user)
            if self.wait_hook:self.wait_hook(self,self.waits-self.wait_start)
        elif address==GFX-420:
            ch=self.u16(a1+10);assert a0==VP and ch in (n,n+1)
            assert self.state(n)==15 and self.u16(a1+8)==257
            if self.entry==CHANGE:
                assert a2==self.ptr(n,self.slot_after,bool(ch&1))
                assert all(self.u16(CI+94+8*i)==BLANK&65535 for i in (n,n+1))
                assert self.staged==2*(8+4*self.heights[n])
                self.events.append('even' if ch==n else 'odd')
            else:assert a2==self.ptr(n,0,bool(ch&1))
            self.changes.append(ch)
            if self.fail_change!=ch:
                self.w32(a1,a2);self.move_model(a1,self.u16(a1+6),257)
            if self.change_after==ch:self.rgb=bytes(45)
            self.volatile()
        elif address==GFX-426:
            assert a0==VP and a1==CHIPS[n] and self.state(n)==15
            op=self.u32(a1+12)
            assert self.u8(op+3)&128
            self.moves.append((d0,d1))
            if self.entry==CHANGE:
                if d1==257:
                    self.events.append('hide')
                    assert self.staged==2*(8+4*self.heights[n])
                    if not self.fail_hide:self.move_model(a1,d0,d1)
                else:
                    self.events.append('reveal')
                    assert self.u32(a1)==self.ptr(n,self.slot_after)
                    assert op==self.ptr(n,self.slot_after,True)
                    if not self.fail_reveal:self.move_model(a1,d0,d1)
            else:self.move_model(a1,d0,d1)
            self.volatile()
        else:super().os(u,address,size,user)
    def watch(self,u,access,address,size,value,user):
        if STACK-4096<=address and address+size<=STACK+4:return
        if self.entry!=CHANGE:return super().watch(u,access,address,size,value,user)
        n=self.current;p=CHIPS[n];stream=8+4*self.heights[n]
        target=self.ptr(n,self.slot_after)
        if address==RECS[n]+12 and size==4:return
        if address==p+28 and size==2:
            assert self.events[-1]=='reveal'
            return
        if address==target+stream+3 and size==1:
            assert self.state(n)==15 and self.events[-1]=='odd'
            assert all(self.u16(CI+94+8*i)==BLANK&65535 for i in (n,n+1))
            self.events.append('attach');return
        assert target<=address and address+size<=target+2*stream and size==4,(
            'unexpected native write',hex(address),size)
        assert self.state(n)==31 and self.waits-self.wait_start==2
        assert self.u32(p)==self.ptr(n,self.slot_before)
        assert self.u32(p+12)==self.ptr(n,self.slot_before,True)
        assert address==target+self.staged
        assert bytes(self.read(SCRATCH+96+self.staged,4))==pack('>I',value&0xffffffff)
        if not self.staged:self.events.append('stage')
        self.staged+=size
    def invoke(self,n,entry,x=0,y=0):
        if entry!=CHANGE:
            # Historical method checks immutable image data. Its pointer
            # assertions are only in visible(), which we replace below.
            self.entry=entry
            try:return super().invoke(n,entry,x,y)
            finally:self.entry=None
        self.current=n;self.entry=entry;self.events=[];self.staged=0
        self.wait_start=self.waits
        rec,chip=RECS[n],CHIPS[n];length=self.lengths[n];stream=8+4*self.heights[n]
        self.slot_before=0 if self.u32(chip)==self.ptr(n,0) else 1
        self.slot_after=1-self.slot_before
        before={i:self.slot(i) for i in range(8) if i not in (n,n+1)}
        peers={i:(self.read(RECS[i],44),self.read(CHIPS[i],self.lengths[i]))
               for i in self.lengths if i!=n}
        orig=self.read(rec,44);data=self.read(chip,length)
        source=self.read(SCRATCH-16,self.scratch_len+32)
        u=self.u;u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(REGS):u.reg_write(r,0x55000000+i)
        u.reg_write(UC_M68K_REG_A0,rec);u.reg_write(UC_M68K_REG_A1,GFX)
        u.reg_write(UC_M68K_REG_A2,self.source_addr)
        u.reg_write(UC_M68K_REG_D0,self.source_extent)
        saved={r:u.reg_read(r) for r in REGS}
        u.reg_write(UC_M68K_REG_A7,STACK);self.w32(STACK,STOP)
        u.emu_start(CODE+entry,STOP,count=1000000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items())
        result=(u.reg_read(UC_M68K_REG_D0),u.reg_read(UC_M68K_REG_D1))
        assert self.read(rec,12)==orig[:12] and self.read(rec+16,28)==orig[16:]
        assert self.read(chip-16,16)==bytes([0xa5])*16
        assert self.read(chip+length,16)==bytes([0xc3])*16
        assert self.read(SCRATCH-16,self.scratch_len+32)==source
        now=self.read(chip,length)
        assert now[24:28]==data[24:28] and now[30:96]==data[30:96]
        old=96+2*stream*self.slot_before
        assert now[old+4:old+stream]==data[old+4:old+stream]
        assert now[old+stream+4:old+2*stream]==data[old+stream+4:old+2*stream]
        assert all(self.slot(i)==s for i,s in before.items())
        assert all(self.read(RECS[i],44)==r and self.read(CHIPS[i],self.lengths[i])==b
                   for i,(r,b) in peers.items())
        if result==(1,0):
            assert self.events==['wait','wait','stage','hide','even','odd','attach','reveal']
            assert self.staged==2*stream
            self.visible_slot(n,self.slot_after,self.u16(chip+6),self.u16(chip+8))
            src=self.read(SCRATCH, self.scratch_len)
            off=96+2*stream*self.slot_after
            assert now[off+4:off+stream]==src[100:96+stream]
            assert now[off+stream+4:off+2*stream]==src[100+stream:96+2*stream]
            assert self.u16(chip+28)==self.u16(SCRATCH+28)
        else:assert self.u16(chip+28)==int.from_bytes(data[28:30],'big')
        self.entry=None;self.current=None
        return result
    def visible_slot(self,n,slot,x,y):
        p=CHIPS[n]
        assert self.state(n)==31
        assert self.u16(p+6)==self.u16(p+18)==x
        assert self.u16(p+8)==self.u16(p+20)==y
        for ch in (n,n+1):
            addr=self.ptr(n,slot,bool(ch&1))
            assert self.u32(p+12*(ch&1))==addr
            assert self.u32(TABLE+4*ch)==p+12*(ch&1)
            assert self.u16(CI+90+8*ch)==addr>>16
            assert self.u16(CI+94+8*ch)==addr&65535
        assert self.u32(self.ptr(n,slot))^self.u32(self.ptr(n,slot,True))==128

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes()
    cases=changes=0
    def new(n=2,height=16,colors=15):
        m=FrameMachine(code);m.record(n,height=height,colors=colors)
        assert m.invoke(n,ACQUIRE)==(1,0)
        assert m.invoke(n,SHOW,16,256-height)==(1,0)
        return m
    for n in PAIRS:
        for height in (1,16,255,256):
            for colors in (4,15):
                m=new(n,height,colors)
                for i in range(10):
                    m.make_scratch(n,2+i,i*9)
                    assert m.invoke(n,CHANGE)==(1,0)
                    m.visible_slot(n,(i+1)%2,16,256-height)
                    changes+=1
                assert m.waits==20
                assert m.invoke(n,MOVE,304,0)==(1,0)
                assert m.invoke(n,RETIRE)==(1,0)
                assert m.frees==[n+1,n] and m.waits==22
                cases+=1
        # Detached source rejects before any fence or store.
        for off,value,width in ((4,17,2),(16,17,2),(24,1,4),(28,0,2),(28,4097,2),
                                (30,14,2),(32,3,4),(36,1,4),(43,255,1),(88,1,4),
                                (92,92,4),(0,1,4),(12,1,4),(10,2,2),(22,3,2),
                                (6,1,2),(18,1,2),(96,1,4),(164,1,4),
                                (168,1,4),(236,1,4)):
            m=new(n);m.make_scratch(n);{1:m.w8,2:m.w16,4:m.w32}[width](SCRATCH+off,value)
            assert m.invoke(n,CHANGE)==(0,8) and m.state(n)==31 and not m.events
            m.visible_slot(n,0,16,240);cases+=1
        for which in ('alias','overlap','short','odd','zero','wrap','not_chip'):
            m=new(n);m.make_scratch(n)
            if which=='alias':m.source_addr=CHIPS[n]
            elif which=='overlap':m.source_addr=CHIPS[n]+2
            elif which=='short':m.source_extent-=2
            elif which=='odd':m.source_addr+=1
            elif which=='zero':m.source_addr=0
            elif which=='wrap':m.source_addr=0xfffffffe
            else:m.map_source=False
            assert m.invoke(n,CHANGE)==(0,8) and m.state(n)==31 and not m.events
            cases+=1
        for event in ('pointer','view','lof','shf','palette'):
            m=new(n);m.make_scratch(n)
            def fault(k,w):
                if w!=1:return
                if event=='pointer':k.pointer(n,BLANK)
                elif event=='view':k.w32(GFX+34,0)
                elif event=='lof':k.w32(GFX+50,LOF+2)
                elif event=='shf':k.w32(GFX+54,SHF+2)
                else:k.rgb=bytes(45)
            m.wait_hook=fault
            expected=(0,2) if event=='palette' else (0,6)
            assert m.invoke(n,CHANGE)==expected
            assert not m.staged and 'hide' not in m.events
            assert m.state(n)==(31 if event=='palette' else 15)
            cases+=1
        for event in ('hide','even','odd','palette','reveal'):
            m=new(n);m.make_scratch(n)
            if event=='hide':m.fail_hide=True
            elif event=='even':m.fail_change=n
            elif event=='odd':m.fail_change=n+1
            elif event=='palette':m.change_after=n+1
            else:m.fail_reveal=True
            assert m.invoke(n,CHANGE)==(0,6) and m.state(n)==15
            assert m.invoke(n,MOVE,0,0)==(0,3)
            assert m.invoke(n,RETIRE)==(1,0) and m.waits==4
            assert m.frees==[n+1,n];cases+=1
    # Three pairs active, alternate each independently and retire one at a time.
    m=FrameMachine(code)
    for n in PAIRS:
        m.record(n)
        assert m.invoke(n,ACQUIRE)==(1,0) and m.invoke(n,SHOW,n*16,n*16)==(1,0)
    for i in range(30):
        for n in PAIRS:
            m.make_scratch(n,2+i,i+n)
            assert m.invoke(n,CHANGE)==(1,0);changes+=1
            m.visible_slot(n,(i+1)%2,n*16,n*16)
    for n in (4,2,6):assert m.invoke(n,RETIRE)==(1,0)
    assert m.waits==186 and m.u8(GFX+166)==3
    print('S2C_ATTACHED_FRAME_CPU_PASS',changes,'changes;',cases,
          'additional cases; modeled OS, no DMA proof',flush=True)
if __name__=='__main__':main()
