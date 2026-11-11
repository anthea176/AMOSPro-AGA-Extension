#!/usr/bin/env python3
"""M13/R28 native 68000 Gate A: palette Load/Set/Get.

CPU/ABI and ColorMap mocks, never evidence of actual WinUAE rendering.
Validate no bitmap writes; GetRGB32 vs LoadRGB32 registers, all colour
bytes and indexed ranges; malformed/truncated IFF and resource cleanup.
"""
import struct
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from build_m13_palette_r28 import (
    build,BASE,BASE_SHA256,LAST_GOOD,LAST_GOOD_SHA256,OLD_ENTRIES,
    ENTRY_LOAD,ENTRY_SET,ENTRY_GET,GETP,API,
)
from m13_palette_r28_emit import emit_load,emit_set,emit_get
from ap20_utils import split,digest
from audit_ap20 import parse,inspect as audit
from test_m5_generic import (
    Machine, DR,AR,CODE,STOP,STACK,NAME,GFX,AMOS,STATE,SCREEN,
    fixture,replace_chunk,chunk,
)
from validate_ilbm import inspect as inspect_ilbm

COLORMAP=0x57000
ARGS=0x58000

class PaletteMachine(Machine):
    def __init__(self,raw,data=None,depth=8,colors=None,
                 allocation_failure=0):
        screen_fixture=fixture(width=320,height=256,depth=depth)
        meta,_=inspect_ilbm(screen_fixture)
        super().__init__(raw,data,meta,allocation_failure=allocation_failure)
        self.palette_rgb=[(0,0,0)]*256
        self.rgb_writes=0
        self.rgb_reads=0
        self.last_update=None
        self.put(SCREEN+48,COLORMAP)
        self.uc.mem_write(COLORMAP+2,struct.pack(">H",
                                (1<<depth) if colors is None else colors))
        self.uc.mem_write(GFX-900,b"\x4e\x75")
        self.expected_reads={}

    def _return(self,result=0):
        self.uc.reg_write(DR[0],result&0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000)
        self.uc.reg_write(AR[1],0xbad100)
        pc=self.get(self.a(7))
        self.uc.reg_write(AR[7],self.a(7)+4)
        self.uc.reg_write(UC_M68K_REG_PC,pc)

    def os_call(self,uc,address,size,user):
        if address==GFX-882:
            self.rgb_writes+=1
            assert self.a(0)==SCREEN+44, "LoadRGB32 wrong viewport"
            p=self.a(1)
            head=self.get(p)
            count,first=head>>16,head&0xffff
            cmcount=struct.unpack(">H",uc.mem_read(COLORMAP+2,2))[0]
            assert 1<=count<=cmcount and first+count<=cmcount,(first,count,cmcount)
            triplets=[]
            for j in range(count):
                rgb=tuple(self.get(p+4+j*12+i*4) for i in range(3))
                triplets.append(rgb)
                self.palette_rgb[first+j]=rgb
            assert self.get(p+4+count*12)==0
            self.last_update=(first,tuple(triplets))
            self._return()
            return
        if address==GFX-900:
            self.rgb_reads+=1
            assert self.a(0)==COLORMAP,"GetRGB32 wrong ColorMap"
            first,count=self.d(0),self.d(1)
            cmcount=struct.unpack(">H",uc.mem_read(COLORMAP+2,2))[0]
            assert 0<=first<cmcount and count==1
            uc.mem_write(self.a(1),struct.pack(">3I",*self.palette_rgb[first]))
            self._return()
            return
        return super().os_call(uc,address,size,user)

    def call_int(self,index,args):
        assert index in (ENTRY_SET,ENTRY_GET)
        for i,reg in enumerate(DR):
            self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]):
            self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,v in enumerate(reversed(args[:-1])):
            self.put(ARGS+i*4,v)
        self.uc.reg_write(DR[3],args[-1]&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[index],STOP,count=200000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,"hardware SP not restored"
        assert self.a(3)==ARGS+4*(len(args)-1)
        for reg,old in saved.items():
            if reg in (DR[2],DR[3],AR[3]):continue
            assert self.uc.reg_read(reg)==old,(index,reg,old,self.uc.reg_read(reg))
        assert self.d(2)==0
        return self.d(3)

    def set(self,index,r,g,b):
        return self.call_int(ENTRY_SET,(index,r,g,b))

    def get_color(self,index):
        return self.call_int(ENTRY_GET,(index,))

    def load(self):
        return self.execute(ENTRY_LOAD)

def make_palette_only(colors):
    cm=bytes((i*37+11)%256 for i in range(colors*3))
    body=b"ILBM"+chunk(b"CMAP",cm)
    return b"FORM"+struct.pack(">I",len(body))+body,cm

def run():
    r28,report=build()
    assert r28==build()[0],"R28 must be bit-reproducible"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    base_tok,old,_=split(BASE.read_bytes())
    newer_tok,parts,_=split(r28)
    assert len(old)==OLD_ENTRIES and len(parts)==OLD_ENTRIES+3
    assert parts[:36]==old[:36]
    assert parts[36]==old[36]+GETP
    assert newer_tok.startswith(base_tok[:-6])
    check=audit(parse(r28))
    assert not check["issues"]
    assert len([x for x in check["tokens"] if x["name"].startswith("aga ")])==34
    for name,index,sig in API:
        entries=[x for x in check["tokens"] if x["name"]==name]
        assert len(entries)==1 and entries[0]["function"]==index
        assert entries[0]["signature"]==sig

    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    code_entries=(
        (ENTRY_LOAD,emit_load()),
        (ENTRY_SET,emit_set()),
        (ENTRY_GET,emit_get()),
    )
    for index,(blob,labels) in code_entries:
        assert parts[index]==(blob+GETP if index!=ENTRY_GET else blob)
        end=labels.get("dosname",len(blob))
        ins=list(md.disasm(blob[:end],0))
        assert sum(i.size for i in ins)==end,("invalid 68000",index)
        boundaries={i.address for i in ins}
        assert all(value in boundaries or value==end
                   for value in labels.values() if value<=end)
        assert not any(i.mnemonic in ("dc.w","illegal","trap")
                       for i in ins)
    count=0
    for depth in (1,2,4,8):
        for pen in (0,(1<<depth)-1):
            for red,green,blue in ((0,0,0),(255,0,255),(18,164,251)):
                m=PaletteMachine(r28,depth=depth)
                assert m.set(pen,red,green,blue)==1
                assert m.rgb_writes==1 and m.last_update[0]==pen
                expected=tuple(x*0x01010101 for x in (red,green,blue))
                assert m.palette_rgb[pen]==expected,(depth,pen,m.palette_rgb[pen])
                got=m.get_color(pen)
                expected_packed=(red<<16)|(green<<8)|blue
                assert got==expected_packed, (
                    "palette readback", depth,pen,(red,green,blue),
                    hex(got),hex(expected_packed),m.rgb_reads,m.palette_rgb[pen])
                assert m.rgb_reads==1 and m.plane_writes==0
                count+=2

        # Every out-of-range index and component must fail before any OS calls.
        for pen,red,green,blue in ((-1,0,0,0),(1<<depth,0,0,0),
                                   (0,-1,0,0),(0,256,0,0),
                                   (0,0,-1,0),(0,0,256,0),
                                   (0,0,0,-1),(0,0,0,256)):
            m=PaletteMachine(r28,depth=depth)
            assert m.set(pen,red,green,blue)==0
            assert m.rgb_writes==m.rgb_reads==0 and m.plane_writes==0
            count+=1
        for pen in (-1,1<<depth,256):
            m=PaletteMachine(r28,depth=depth)
            assert m.get_color(pen)==0xffffffff
            assert m.rgb_reads==0
            count+=1

    for fail in ("screen","gfx","depth","mode","colors","colormap","cm_count"):
        m=PaletteMachine(r28)
        if fail=="screen":m.put(STATE,0)
        elif fail=="gfx":m.put(STATE+8,0)
        elif fail=="depth":m.put(STATE+28,9)
        elif fail=="mode":m.put(STATE+24,0x800)
        elif fail=="colors":m.put(STATE+20,0)
        elif fail=="colormap":m.put(SCREEN+48,0)
        elif fail=="cm_count":m.uc.mem_write(COLORMAP+2,b"\0\0")
        assert m.set(0,1,2,3)==0,fail
        assert m.get_color(0)==0xffffffff,fail
        assert m.rgb_writes==m.rgb_reads==0
        count+=2

    # Palette-only ILBM may have no BMHD/BODY: do not draw pixels.
    for depth in (1,2,4,8):
        for n in (1,1<<depth):
            data,cm=make_palette_only(n)
            m=PaletteMachine(r28,data=data,depth=depth)
            assert m.load()==1,(depth,n)
            assert m.rgb_writes==1 and m.last_update[0]==0
            assert m.last_update[1]==tuple(
                tuple(cm[i*3+j]*0x01010101 for j in range(3))
                for i in range(n)
            )
            assert m.plane_writes==0,"ILBM palette may not modify BODY"
            assert m.get_color(n-1)==(
                cm[(n-1)*3]<<16|cm[(n-1)*3+1]<<8|cm[(n-1)*3+2])
            count+=2

    # Standard palette-only IFF/ILBM as saved by Amiga paint software:
    # optional BMHD, optional range-cycle CRNG, no pixel BODY.
    # The palette importer must not require PicInfo or a picture.
    for with_bmhd in (False,True):
        for with_crng in (False,True):
            pal_data,cm=make_palette_only(32)
            parts=b"ILBM"
            if with_bmhd:
                bmhd=struct.pack(">HHhhBBBBHBBhh",
                                 0,0,0,0,0,0,0,0,0,1,1,0,0)
                parts+=chunk(b"BMHD",bmhd)
            if with_crng:
                parts+=chunk(b"CRNG",bytes.fromhex("0000000100000000"))
            parts+=chunk(b"CMAP",cm)
            palette_iff=b"FORM"+struct.pack(">I",len(parts))+parts
            m=PaletteMachine(r28,data=palette_iff)
            assert m.load()==1,("palette-only IFF",with_bmhd,with_crng)
            assert m.rgb_writes==1 and m.plane_writes==0
            assert m.palette_rgb[31]==tuple(
                cm[31*3+i]*0x01010101 for i in range(3))
            assert not m.owned and m.open_files==m.open_libraries==0
            count+=1

    # Ordinary ILBM pictures of unrelated geometry are also legitimate
    # palette sources; their compressed BODY and BMHD are ignored.
    for source_depth in (1,2,4,8):
        picture=fixture(width=17,height=2,depth=source_depth)
        m=PaletteMachine(r28,data=picture,depth=8)
        assert m.load()==1,source_depth
        assert m.rgb_writes==1 and m.plane_writes==0
        assert m.last_update[0]==0 and len(m.last_update[1])==1<<source_depth
        count+=1

    good,cm=make_palette_only(8)
    valid_form=b"FORM"+struct.pack(">I",len(good)-8)+good[8:]
    assert good==valid_form
    bad_formats=[
        None,b"",good[:7],good[:12],good[:-1],
        good[:8]+b"NOPE"+good[12:],
        make_palette_only(257)[0],
        b"FORM"+struct.pack(">I",4)+b"ILBM",
    ]
    for payload in (b"",b"abcde"):
        body=b"ILBM"+chunk(b"CMAP",payload)
        bad_formats.append(b"FORM"+struct.pack(">I",len(body))+body)
    body=b"ILBM"+chunk(b"CMAP",cm)+chunk(b"CMAP",cm)
    bad_formats.append(b"FORM"+struct.pack(">I",len(body))+body)
    # Reject malformed chunk/padding/declared length before writing CMAP.
    for n in (1,7,11,13,14,15,16,18,len(good)-2):
        bad_formats.append(good[:n])
    corrupted=bytearray(good)
    corrupted[16:20]=b"\xff"*4
    bad_formats.append(bytes(corrupted))
    for data in bad_formats:
        m=PaletteMachine(r28,data=data,depth=8)
        assert m.load()==0,(len(data) if data else None)
        assert m.plane_writes==m.rgb_writes==0
        assert not m.owned and m.open_files==m.open_libraries==0
        count+=1

    # The declared palette must fit BOTH ColorMap.Count and screen logical colors.
    data,_=make_palette_only(16)
    for limit in ("screen_colors","cm_count","screen_ptr","gfx","mode"):
        m=PaletteMachine(r28,data=data,depth=8)
        if limit=="screen_colors":m.put(STATE+20,8)
        elif limit=="cm_count":m.uc.mem_write(COLORMAP+2,struct.pack(">H",8))
        elif limit=="screen_ptr":m.put(STATE,0)
        elif limit=="gfx":m.put(STATE+8,0)
        elif limit=="mode":m.put(STATE+24,0x80)
        assert m.load()==0,limit
        assert m.rgb_writes==m.plane_writes==0
        count+=1
    for stage in (1,2,3):
        m=PaletteMachine(r28,data=data,depth=8,allocation_failure=stage)
        assert m.load()==0,stage
        assert not m.owned and m.rgb_writes==m.plane_writes==0
        count+=1

    print("M13 R28 native 68000 Gate A PASS:",count,
          "Palette Load/Set/Get, no pixel edits, ABI, leaks and malformed CMAP")
    print("M13 R28 in-memory candidate:",report)
    print("M13 R28 WinUAE: PASS user screenshot 2026-11-11 (M13-R28-PALETTE-01); AMOS Compiler/real AGA: NOT TESTED")

if __name__=="__main__":
    run()
