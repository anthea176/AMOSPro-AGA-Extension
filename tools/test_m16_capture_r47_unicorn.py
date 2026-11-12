#!/usr/bin/env python3
"""M16/R47 actual 68000 capture wrapper Gate A under simulated AMOS calls.

Test emitted native wrapper on Unicorn M68000. Rjsr AP20 linker markers
are replaced ONLY IN THE EMULATED CODE COPY by equal-length JSR abs.l
to distinct mocked AMOS main routines. No claim that numeric linkage,
AMOS memory allocator or Compiler C1 relocation works on WinUAE.
"""
from __future__ import annotations

import struct
from collections import deque
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_PC

from build_aga_current import HISTORICAL_RAW
from m16_capture_r47_emit import (
    emit_capture, IDX_GETADR, IDX_RESERVE, IDX_EFF, IDX_CHANGE,
)
from m16_agapic import parse_payload,unpack_image
from test_m16_image_draw_r45 import ImageMachine, sample_pixels, ARGS, BANK
from test_m5_generic import CODE, EXEC, DR, AR, AMOS, STACK, STOP

NEW_CODE=0x180000
MAIN_BASE=0x30000
BANK_NEW=0xE00000
TEMP_BASE=0xB00000
MOCK_IDS=(IDX_GETADR,IDX_RESERVE,IDX_EFF,IDX_CHANGE)
EXTERNAL=b"\xfe\x11\xf7\x00"


def linked_test_code():
    raw, labels=emit_capture()
    out=bytearray(raw)
    i=0
    found=[]
    while (pos:=raw.find(EXTERNAL,i))>=0:
        idx=struct.unpack_from(">H",raw,pos+4)[0]
        assert idx in MOCK_IDS
        out[pos:pos+6]=bytes.fromhex("4eb9")+struct.pack(">I",MAIN_BASE+16*idx)
        found.append(idx)
        i=pos+6
    assert found==[IDX_GETADR,IDX_GETADR,IDX_RESERVE,IDX_CHANGE,IDX_EFF]
    return bytes(out), labels


class CaptureMachine(ImageMachine):
    def __init__(self,*,width=80,height=48,depth=4,front=0,pending=0,
                 safe_ready=True,alloc_fail=False,reserve_fail=False,
                 occupied=False):
        # Original immutable native R46 is used ONLY as mock machine context;
        # new capture code lives at an independent address.
        super().__init__(HISTORICAL_RAW.read_bytes(),b"AGAPIC"*8,
                         width=width,height=height,depth=depth,
                         front=front,pending=pending,safe_ready=safe_ready)
        code,labels=linked_test_code()
        self.capture_labels=labels
        self.capture_code=code
        self.uc.mem_write(NEW_CODE,code)
        self.alloc_fail=alloc_fail
        self.reserve_fail=reserve_fail
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
                         begin=MAIN_BASE,end=MAIN_BASE+0x2000)
        for idx in MOCK_IDS:
            self.uc.mem_write(MAIN_BASE+idx*16,b"\x4e\x75")
        self.uc.hook_add(UC_HOOK_CODE,self.debug_hook,
                         begin=NEW_CODE,end=NEW_CODE+len(code)-1)

    def debug_hook(self,uc,address,size,user):
        self.trace.append((hex(address),bytes(uc.mem_read(address,2)).hex()))

    def pop_return(self):
        sp=self.a(7)
        ret=self.get(sp)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,ret)

    def main_call(self,uc,address,size,user):
        idx=(address-MAIN_BASE)//16
        assert address==MAIN_BASE+idx*16 and idx in MOCK_IDS,hex(address)
        self.main_calls.append(idx)
        if idx==IDX_GETADR:
            bank=self.d(0)
            p=self.banks.get(bank,0)
            # Bnk.GetAdr returns A0=A1=DATA pointer, D0=native bank flags.
            self.uc.reg_write(AR[0],p)
            self.uc.reg_write(AR[1],p)
            self.uc.reg_write(DR[0],1 if p else 0)
        elif idx==IDX_RESERVE:
            self.reserve_count+=1
            num,size,flags=self.d(0),self.d(2),self.d(1)
            assert num not in self.banks,("destructive bank replacement",num)
            assert 32<size<=300000
            assert flags==1,("not Fast-preferred DATA",flags)
            assert bytes(uc.mem_read(self.a(0),8))==b"AGAPIC  "
            if self.reserve_fail:
                ptr=0
            else:
                ptr=BANK_NEW
                self.banks[num]=ptr
                self.uc.mem_write(ptr,bytes(size))
                self.uc.mem_write(ptr-24,
                    struct.pack(">IIIHH8s",0,size+16,num,1,0,b"AGAPIC  "))
            self.uc.reg_write(DR[0],ptr)
            self.uc.reg_write(AR[0],ptr)
        elif idx==IDX_EFF:
            self.erase_count+=1
            num=self.d(0)
            assert num!=10 and num in self.banks
            self.banks.pop(num)
        elif idx==IDX_CHANGE:
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
            self.uc.emu_start(NEW_CODE,STOP,count=instruction_limit)
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


def run():
    cases=0
    for depth in (1,4,8):
        for index in (-1,0,(1<<depth)-1):
            m=CaptureMachine(depth=depth)
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
    )
    for opts in invalid:
        m=CaptureMachine()
        ok,before=m.run_capture(**opts)
        assert ok==0 and 11 not in m.banks
        assert m.reserve_count==m.erase_count==m.change_count==0
        assert m.alloc_count==m.free_count
        cases+=1
    # Duplicate bank (including AMCAF or unknown bank type) cannot be touched.
    m=CaptureMachine(occupied=True)
    ok,before=m.run_capture()
    assert ok==0 and m.banks[11]==BANK and m.reserve_count==0
    cases+=1
    # Temporary memory failure must never reserve a bank.
    m=CaptureMachine(alloc_fail=True)
    ok,before=m.run_capture()
    assert ok==0 and m.alloc_count==1 and m.reserve_count==0
    cases+=1
    # Bank allocator failure must free temp and preserve other banks.
    m=CaptureMachine(reserve_fail=True)
    ok,before=m.run_capture()
    assert ok==0 and m.reserve_count==1 and m.free_count==1
    assert 11 not in m.banks
    cases+=1
    # SafePort missing message: no wait and no bank changes.
    m=CaptureMachine(pending=1,safe_ready=False)
    ok,before=m.run_capture()
    assert ok==0 and m.getmsg_calls==1 and 11 not in m.banks
    assert m.reserve_count==0
    cases+=1
    print("M16/R47 native 68000 CAPTURE WRAPPER Gate A SIMULATED AMOS:",
          cases,"functional/lifecycle scenarios PASS")
    print("Still NOT WinUAE/AMOS main-library Rjsr runtime and NOT Compiler Gate C")


if __name__=="__main__":
    run()
