#!/usr/bin/env python3
"""Corrected public AP20 capture, independent main table, mocked bank services.

Test emitted native wrapper on Unicorn M68000. Rjsr is resolved via a source-derived negative address table.
Both a contiguous interpreter layout and separate Compiler layout are modeled. No claim that numeric linkage,
AMOS memory allocator or Compiler C1 relocation works on WinUAE.
"""
from __future__ import annotations

import struct
from collections import deque
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_PC

from build_aga_current import HISTORICAL_RAW
from build_m16_capture import build
from compiler_relocation import unpack_ap20
from amos_link_test_support import main_table,relocate
from amos_main_abi import declarations
from m16_capture_emit import emit_capture
from m16_agapic import parse_payload,unpack_image
from test_m16_image_draw_r45 import ImageMachine, sample_pixels, ARGS, BANK
from test_m5_generic import CODE, EXEC, DR, AR, AMOS, STACK, STOP

NEW_CODE=0x180000
MAIN_BASE=0x30000
BANK_NEW=0xE00000
TEMP_BASE=0xE80000  # Separate from front planes (through 0xBC0000), bank E00000 and stack F00000




class CaptureMachine(ImageMachine):
    def __init__(self,*,width=80,height=48,depth=4,front=0,pending=0,
                 safe_ready=True,alloc_fail=False,reserve_fail=False,
                 occupied=False,layout="interpreted",binary=None,
                 late_collision=False,reserve_overflow=False):
        # Original immutable native R46 is used ONLY as mock machine context;
        # new capture code lives at an independent address.
        super().__init__(HISTORICAL_RAW.read_bytes(),b"AGAPIC"*8,
                         width=width,height=height,depth=depth,
                         front=front,pending=pending,safe_ready=safe_ready)
        binary=build()[0] if binary is None else binary
        _,parts,_=unpack_ap20(binary)
        table,names=main_table(self.uc)
        self.target_names={addr:names[idx] for idx,addr in table.items()}
        # Bank service hooks are bound by symbolic identity from the reference,
        # never by constants imported from the emitter.
        self.bank_targets={table[idx]:name for idx,name,*_ in declarations()
                           if name in ("Bnk.GetAdr","Bnk.Reserve","Bnk.Eff","Bnk.Change")}
        self.layout=layout
        if layout=="interpreted":
            addresses={}
            cursor=NEW_CODE
            for i,part in enumerate(parts):
                addresses[i]=cursor
                cursor+=len(part)
            selected=range(len(parts))
        elif layout=="compiled":
            # Only entry 56 and its Rbsr dependency 57 are copied, not adjacent
            # to other entries. One monolith preserves internal PC references.
            addresses={56:NEW_CODE,57:NEW_CODE+0x400}
            selected=(56,57)
        else:
            raise ValueError(layout)
        for i in selected:
            part=parts[i]
            if layout=="compiled" and part.endswith(b"GetP"):
                part=part[:-4]
            self.uc.mem_write(addresses[i],relocate(part,addresses[i],addresses,self.uc))
        self.entry=addresses[56]
        self.capture_labels=emit_capture()[1]
        self.capture_code=parts[-1]
        self.mono_end=addresses[57]+len(parts[57])
        self.alloc_fail=alloc_fail
        self.reserve_fail=reserve_fail
        self.late_collision=late_collision
        self.reserve_overflow=reserve_overflow
        self.buffers={}
        self.alloc_count=0
        self.free_count=0
        self.reserve_count=0
        self.erase_count=0
        self.change_count=0
        self.main_calls=[]
        self.banks={10:BANK}
        if occupied:
            self.banks[11]=BANK
        self.trace=deque(maxlen=28)
        self.uc.mem_write(EXEC-684,b"\x4e\x75")
        self.uc.mem_write(EXEC-690,b"\x4e\x75")
        self.uc.hook_add(UC_HOOK_CODE,self.main_call,
                         begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        for addr in self.bank_targets:
            self.uc.mem_write(addr,b"\x4e\x75")
        self.uc.hook_add(UC_HOOK_CODE,self.debug_hook,
                         begin=NEW_CODE,end=self.mono_end-1)

    def debug_hook(self,uc,address,size,user):
        self.trace.append((hex(address),bytes(uc.mem_read(address,2)).hex()))

    def pop_return(self):
        sp=self.a(7)
        ret=self.get(sp)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,ret)

    def main_call(self,uc,address,size,user):
        assert address in self.bank_targets,(
            "wrong AMOS symbol called",hex(address),self.target_names.get(address))
        name=self.bank_targets[address]
        self.main_calls.append(name)
        assert self.a(5)==AMOS,"AMOS A5 base lost in dispatcher"
        if name=="Bnk.GetAdr":
            bank=self.d(0)
            p=self.banks.get(bank,0)
            # Bnk.GetAdr returns A0=A1=DATA pointer, D0=native bank flags.
            self.uc.reg_write(AR[0],p)
            self.uc.reg_write(AR[1],p)
            # D0 is only a WORD of flags when found; unchanged when missing.
            if p:
                self.uc.reg_write(DR[0],(bank & 0xffff0000)|1)
            self.uc.reg_write(DR[1],p)
        elif name=="Bnk.Reserve":
            self.reserve_count+=1
            num,size,flags=self.d(0),self.d(2),self.d(1)
            assert num not in self.banks,("destructive bank replacement",num)
            assert 32<size<=300000
            assert flags==1,("not Fast-preferred DATA",flags)
            assert bytes(uc.mem_read(self.a(0),8))==b"AGAPIC  "
            if self.reserve_fail:
                ptr=0
            elif self.reserve_overflow:
                ptr=0xfffffff0
                self.banks[num]=ptr
            else:
                ptr=BANK_NEW
                self.banks[num]=ptr
                self.uc.mem_write(ptr,bytes(size))
                self.uc.mem_write(ptr-24,
                    struct.pack(">IIIHH8s",0,size+16,num,1,0,b"AGAPIC  "))
            self.uc.reg_write(DR[0],ptr)
            self.uc.reg_write(AR[0],ptr)
            self.uc.reg_write(AR[1],ptr)
            self.uc.reg_write(DR[1],0xdeadbeef)  # documented volatile
        elif name=="Bnk.Eff":
            self.erase_count+=1
            num=self.d(0)
            assert num!=10 and num in self.banks
            self.banks.pop(num)
        elif name=="Bnk.Change":
            self.change_count+=1
        self.pop_return()

    def os_call(self,uc,address,size,user):
        if address==EXEC-684:
            self.alloc_count+=1
            size=self.d(0)
            assert 0<size<8192
            assert self.d(1)==1
            if self.alloc_fail:
                ptr=0
            else:
                ptr=TEMP_BASE
                self.buffers[ptr]=size
                self.uc.mem_write(ptr,bytes(size))
            if self.late_collision:
                self.banks[11]=BANK
            self._ret(ptr)
            return
        if address==EXEC-690:
            self.free_count+=1
            ptr=self.a(1)
            assert ptr in self.buffers
            del self.buffers[ptr]
            self._ret(0)
            return
        super().os_call(uc,address,size,user)

    def run_capture(self,bank=11,x=5,y=5,w=19,h=9,index=-1,
                    instruction_limit=12000000):
        for i,reg in enumerate(DR):
            self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]):
            self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,val in enumerate((h,w,y,x,bank)):
            self.put(ARGS+4*i,val)
        self.uc.reg_write(DR[3],index & 0xffffffff)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        before=self.snapshot()
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.entry,STOP,count=instruction_limit)
        except Exception as exc:
            raise AssertionError((
                "native capture exception",str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),list(self.trace),
                "main calls",self.main_calls,
                "alloc",self.alloc_count,self.free_count,
                "banks",self.banks)) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.a(3)==ARGS+20, "five stacked arguments not consumed"
        for reg,old in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==old,(
                    "AMOS calling convention changed",reg,
                    hex(old),hex(self.uc.reg_read(reg)))
        assert self.d(2)==0, "return type must be integer"
        assert self.d(3) in (0,1)
        assert before==self.snapshot(),"capture modified back-buffer"
        assert not self.buffers,"leaked temporary AllocVec"
        return self.d(3),before

    def captured(self,bank=11):
        ptr=self.banks[bank]
        size=self.get(ptr-20)-16
        assert 32<size<=0x100000
        return parse_payload(bytes(self.uc.mem_read(ptr,size)))


def compare(m,bank,x,y,w,h,index,before):
    depth=m.meta["depth"]; sw=m.meta["width"]; sh=m.meta["height"]
    pixels=sample_pixels(before,sw,sh,depth,m.stride)
    expected=bytes(pixels[(y+yy)*sw+x+xx]
                   for yy in range(h) for xx in range(w))
    image=m.captured(bank)
    actual,mask=unpack_image(image)
    assert (image.width,image.height,image.depth)==(w,h,depth)
    assert actual==expected,("capture pixel mismatch",depth,x,y,w,h,index)
    assert mask==(None if index==-1 else
                  bytes(int(px!=index) for px in expected)),(
                      "capture transparency mismatch",depth,index)
    assert m.alloc_count==m.free_count==1
    assert m.reserve_count==m.change_count==1
    assert m.erase_count==0
    assert all(p==m.front_before[i]
               for i,p in enumerate(
                   bytes(m.uc.mem_read(ptr,m.plane_size))
                   for ptr in m.frontplanes))


def run(layout):
    cases=0
    def machine(**kwargs):
        return CaptureMachine(layout=layout,**kwargs)
    for depth in (1,4,8):
        for index in (-1,0,(1<<depth)-1):
            m=machine(depth=depth)
            ok,before=m.run_capture(index=index)
            assert ok==1,("valid capture refused",depth,index,
                           m.main_calls,m.alloc_count,m.reserve_count)
            compare(m,11,5,5,19,9,index,before)
            cases+=1
    # Strict out-of-screen rectangles and invalid transparency.
    invalid=(
        dict(x=-1),dict(y=-1),dict(w=0),dict(h=0),
        dict(x=79,w=2),dict(y=47,h=2),
        dict(index=-2),dict(index=16),
        dict(bank=4),dict(bank=65536),
        dict(x=0x7fffffff),dict(y=0x7fffffff),
        dict(w=0x7fffffff),dict(h=0x7fffffff),
    )
    for opts in invalid:
        m=machine()
        ok,before=m.run_capture(**opts)
        assert ok==0 and 11 not in m.banks
        assert m.reserve_count==m.erase_count==m.change_count==0
        assert m.alloc_count==m.free_count
        cases+=1
    # Duplicate bank (including AMCAF or unknown bank type) cannot be touched.
    m=machine(occupied=True)
    ok,before=m.run_capture()
    assert ok==0 and m.banks[11]==BANK and m.reserve_count==0
    cases+=1
    # Temporary memory failure must never reserve a bank.
    m=machine(alloc_fail=True)
    ok,before=m.run_capture()
    assert ok==0 and m.alloc_count==1 and m.reserve_count==0
    cases+=1
    # Bank allocator failure must free temp and preserve other banks.
    m=machine(reserve_fail=True)
    ok,before=m.run_capture()
    assert ok==0 and m.reserve_count==1 and m.free_count==1
    assert 11 not in m.banks
    cases+=1
    # SafePort missing message: no wait and no bank changes.
    m=machine(pending=1,safe_ready=False)
    ok,before=m.run_capture()
    assert ok==0 and m.getmsg_calls==1 and 11 not in m.banks
    assert m.reserve_count==0
    cases+=1
    # Screen absent, late collision, and cleanup after an invalid reserve result.
    m=machine()
    m.put(AMOS+456,0)
    ok,_=m.run_capture()
    assert ok==0 and not m.main_calls and m.alloc_count==0
    cases+=1
    m=machine(late_collision=True)
    protected=bytes(m.uc.mem_read(BANK,48))
    ok,_=m.run_capture()
    assert ok==0 and m.banks[11]==BANK and m.reserve_count==0
    assert m.alloc_count==m.free_count==1
    assert bytes(m.uc.mem_read(BANK,48))==protected
    cases+=1
    m=machine(reserve_overflow=True)
    ok,_=m.run_capture()
    assert ok==0 and 11 not in m.banks and m.banks[10]==BANK
    assert m.reserve_count==m.erase_count==m.free_count==1
    assert m.change_count==0
    cases+=1
    # Historical R47 must now fail on the source-derived table, whereas its
    # old direct mock replacement could pass all pixel tests.
    old=(__import__("pathlib").Path(__file__).resolve().parents[1]/
         "dist/experimental/AMOSPro_AGA_M16_v0.12.2_IMAGE_CAPTURE_R47_CANDIDATE.Lib").read_bytes()
    m=machine(binary=old)
    try:
        m.run_capture()
    except AssertionError as exc:
        assert "wrong AMOS symbol called" in str(exc) and "InSort" in str(exc),str(exc)
    else:
        raise AssertionError("old R47 must not pass the independent linker")
    cases+=1
    print("M16 corrected public AP20 capture",layout,"Gate A:",
          cases,"functional/lifecycle scenarios PASS")
    print("Still NOT WinUAE/AMOS main-library Rjsr runtime and NOT Compiler Gate C")


if __name__=="__main__":
    run("interpreted")
    run("compiled")
