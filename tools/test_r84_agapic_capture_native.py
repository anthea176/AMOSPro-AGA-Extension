#!/usr/bin/env python3
"""Real native R84 versioned AGAPIC capture execution on simulated AMOS/WinUAE services.

The existing R53 native scanline RLE body is executed, NOT a host reencoder.
Only AMOS bank and Exec/graphics OS services are mocked; no WinUAE Gate B
claim. Checks v1/v2 pixels, RGB24/ModeID, ABI, cleanup and no bank overwrite.
"""
from __future__ import annotations
import struct
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_PC
from test_m16_capture import CaptureMachine,NEW_CODE,BANK_NEW,TEMP_BASE
from test_m16_image_draw_r45 import sample_pixels
from test_m5_generic import EXEC,GFX,SCREEN,DR,AR,AMOS,STACK,STOP
from test_m16_image_draw_r45 import ARGS
from amos_link_test_support import relocate
from m16_agapic_capture_v2_emit import emit_capture_versioned
from m16_agapic_v2 import parse_payload_any
from m16_agapic import unpack_image

COLORMAP=0x57000
MODE=0x00021000

class CaptureV2Machine(CaptureMachine):
    def __init__(self,*,depth=4,occupied=False,alloc_fail=False,
                 pending=0,safe_ready=True,modeid=MODE):
        super().__init__(width=80,height=48,depth=depth,occupied=occupied,
                         alloc_fail=alloc_fail,pending=pending,safe_ready=safe_ready)
        code,labels=emit_capture_versioned()
        self.uc.mem_write(NEW_CODE,relocate(code,NEW_CODE,{},self.uc))
        self.entry=NEW_CODE
        self.capture_labels=labels
        self.capture_code=code
        self.modeid=modeid
        self.rgb_calls=0
        self.mode_calls=0
        self.palette=bytes((i*11+7)&255 for i in range(3*(1<<depth)))
        self.put(SCREEN+48,COLORMAP)
        self.uc.mem_write(COLORMAP+2,struct.pack('>H',1<<depth))
        for addr in (GFX-792,GFX-900):
            self.uc.mem_write(addr,b'\x4e\x75')

    def os_call(self,uc,address,size,user):
        if address==EXEC-684:
            self.alloc_count+=1
            n=self.d(0)
            assert 0<n<=8192,('bad AllocVec length',n)
            assert self.d(1)==1
            if self.alloc_fail:
                pointer=0
            else:
                pointer=TEMP_BASE+len(self.buffers)*0x2000
                self.buffers[pointer]=n
                self.uc.mem_write(pointer,bytes(n))
            if self.late_collision:
                self.banks[11]=0xd00000
            self._ret(pointer)
            return
        if address==EXEC-690:
            self.free_count+=1
            ptr=self.a(1)
            assert ptr in self.buffers,('FreeVec unknown pointer',hex(ptr),self.buffers)
            del self.buffers[ptr]
            self._ret(0)
            return
        if address==GFX-792:
            self.mode_calls+=1
            assert self.a(0)==SCREEN+44,('GetVPModeID viewport',self.a(0))
            assert self.a(6)==GFX
            self._ret(self.modeid)
            return
        if address==GFX-900:
            self.rgb_calls+=1
            assert self.a(0)==COLORMAP,('GetRGB32 colormap',self.a(0))
            assert self.a(6)==GFX
            assert self.d(0)==0
            n=self.d(1)
            assert n==len(self.palette)//3
            start=self.a(1)
            for col in range(n):
                rgb=self.palette[3*col:3*col+3]
                self.uc.mem_write(start+12*col,struct.pack('>III',*(x<<24 for x in rgb)))
            self._ret(0)
            return
        return super().os_call(uc,address,size,user)

    def capture(self,*,version=2,bank=11,x=5,y=5,w=19,h=9,index=-1,
                limit=12000000):
        for i,r in enumerate(DR): self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]): self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,value in enumerate((index,h,w,y,x,bank)):
            self.put(ARGS+4*i,value)
        self.uc.reg_write(DR[3],version&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        before=self.snapshot()
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.entry,STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('native R84 capture exception',str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),list(self.trace),
                'main calls',self.main_calls,'alloc',self.alloc_count,
                self.free_count,'banks',self.banks)) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,('native capture did not return')
        assert self.a(7)==STACK+4,('SP ABI',self.a(7))
        assert self.a(3)==ARGS+24,('A3 must consume six stacked arguments',self.a(3))
        for reg,value in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==value,('register ABI',reg)
        assert self.d(2)==0
        assert self.d(3) in (0,1)
        assert before==self.snapshot(),('capture changed source back buffer')
        assert not self.buffers,('leaked AllocVec',self.buffers)
        return self.d(3),before

    def decoded(self,bank=11):
        ptr=self.banks[bank]
        length=self.get(ptr-20)-16
        return parse_payload_any(bytes(self.uc.mem_read(ptr,length)))

def compare(machine,before,*,version,index,x=5,y=5,w=19,h=9):
    value=machine.decoded()
    img=value.image
    assert value.version==version,(value.version,version)
    assert (img.width,img.height,img.depth)==(w,h,machine.meta['depth'])
    all_pixels=sample_pixels(before,machine.meta['width'],
                             machine.meta['height'],img.depth,machine.stride)
    expected=bytes(all_pixels[(y+yy)*machine.meta['width']+x+xx]
                   for yy in range(h) for xx in range(w))
    pixels,mask=unpack_image(img)
    assert pixels==expected,('captured pixels differ',version,img.depth)
    expected_mask=None if index==-1 else bytes(int(p!=index) for p in expected)
    assert mask==expected_mask,('captured transparency mismatch',version,img.depth)
    if version==1:
        assert value.palette is None and value.mode_id is None
        assert machine.rgb_calls==machine.mode_calls==0
    else:
        assert value.palette==machine.palette,('embedded RGB24 differs',img.depth)
        assert value.mode_id==MODE
        assert machine.rgb_calls==machine.mode_calls==1
    assert machine.reserve_count==machine.change_count==1
    assert machine.erase_count==0

def raw_stream(machine,bank=11):
    """Read the encoded RLE body using the real AGAPIC header offsets."""
    pointer=machine.banks[bank]
    length=machine.get(pointer-20)-16
    data=bytes(machine.uc.mem_read(pointer,length))
    start=int.from_bytes(data[24:28],'big')
    end=int.from_bytes(data[28:32],'big')
    assert 0<start<end==len(data),('invalid AGAPIC stream offsets',start,end,len(data))
    return data[start:end]


def main():
    count=0
    for depth in (1,4,8):
        for version in (1,2):
            for index in (-1,0,(1<<depth)-1):
                m=CaptureV2Machine(depth=depth)
                ok,before=m.capture(version=version,index=index)
                assert ok==1,('valid capture refused',version,depth,index,
                              m.main_calls,m.alloc_count,m.free_count)
                compare(m,before,version=version,index=index)
                count+=1
    # Regression for WinUAE ERR 17: identical source pixels and mask
    # captured in v1/v2 MUST have byte-identical compressed row streams.
    # The two formats differ only by their metadata/header offsets.
    for depth in (1,4,8):
        for index in (-1,0):
            v1=CaptureV2Machine(depth=depth)
            v2=CaptureV2Machine(depth=depth)
            ok1,_=v1.capture(version=1,index=index,w=64,h=40,x=5,y=4)
            ok2,_=v2.capture(version=2,index=index,w=64,h=40,x=5,y=4)
            assert ok1==ok2==1,('cross-format capture failed',depth,index)
            s1,s2=raw_stream(v1),raw_stream(v2)
            assert s1==s2,('R84 v1/v2 native RLE mismatch',
                           depth,index,len(s1),len(s2))
            count+=1
    for version in (0,3,-1):
        m=CaptureV2Machine()
        ok,_=m.capture(version=version)
        assert ok==0 and 11 not in m.banks
        assert not m.alloc_count and not m.reserve_count
        count+=1
    for version in (1,2):
        for kwargs in (dict(x=-1),dict(y=-1),dict(w=0),dict(h=0),
                       dict(x=79,w=2),dict(y=47,h=2),
                       dict(index=-2),dict(index=16),dict(bank=4),
                       dict(bank=65536)):
            m=CaptureV2Machine()
            ok,_=m.capture(version=version,**kwargs)
            assert ok==0 and 11 not in m.banks
            assert m.reserve_count==m.change_count==m.erase_count==0
            assert m.alloc_count==m.free_count
            count+=1
        m=CaptureV2Machine(occupied=True)
        ok,_=m.capture(version=version)
        assert ok==0 and m.banks[11]==0xd00000
        assert m.reserve_count==0 and m.alloc_count==m.free_count
        count+=1
        m=CaptureV2Machine(alloc_fail=True)
        ok,_=m.capture(version=version)
        assert ok==0 and m.reserve_count==0 and not m.buffers
        count+=1
        m=CaptureV2Machine(pending=1,safe_ready=False)
        ok,_=m.capture(version=version)
        assert ok==0 and m.reserve_count==0 and m.alloc_count==m.free_count
        count+=1
    print('R84 NATIVE VERSIONED AGAPIC CAPTURE MC68020 PASS',count,'cases')

if __name__=='__main__':
    main()
