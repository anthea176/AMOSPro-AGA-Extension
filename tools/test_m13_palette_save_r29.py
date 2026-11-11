#!/usr/bin/env python3
"""M13/R29 68000 Gate A: native palette-only IFF export and OS error paths.

Uses actual AP20 machine-code under Unicorn, Capstone disassembly, and
AmigaOS mocks; DOES NOT validate runtime AMOS/WinUAE or PPaint imports.
"""
import struct
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000

from ap20_utils import digest, split
from audit_ap20 import parse, inspect as audit
from build_m13_palette_save_r29 import (
    build,BASE,BASE_SHA256,LAST_GOOD,LAST_GOOD_SHA256,
    ENTRY_SAVE,OLD_ENTRIES,API,GETP,
)
from m13_palette_save_r29_emit import emit_save
from test_m13_palette_r28 import PaletteMachine, COLORMAP
from test_m5_generic import CODE,STOP,DR,AR,STATE,NAME,DOSLIB,GFX,chunk

class SaveMachine(PaletteMachine):
    def __init__(self,raw,depth=8,colors=None,fail_open=False,
                 fail_write=False,short_write=False,fail_close=False,
                 allocation_failure=0):
        super().__init__(raw,data=None,depth=depth,colors=colors,
                         allocation_failure=allocation_failure)
        self.fail_open=fail_open
        self.fail_write=fail_write
        self.short_write=short_write
        self.fail_close=fail_close
        self.saved=None
        self.deleted=0
        self.write_calls=0
        self.get_calls=0
        self.first_count=None
        self.palette_rgb=[
            tuple(((i*(k+3)*7+31+k*17)&255)*0x01010101 for k in range(3))
            for i in range(256)
        ]
        self.uc.mem_write(DOSLIB-48,b'\x4e\x75')
        self.uc.mem_write(DOSLIB-72,b'\x4e\x75')

    def os_call(self,uc,address,size,user):
        if address==GFX-900:
            self.get_calls+=1
            assert self.a(0)==COLORMAP,"GetRGB32 must use private screen ColorMap"
            first,count=self.d(0),self.d(1)
            logical=self.get(STATE+20)
            assert first==0 and 1<=count<=min(logical,256)
            assert count<=struct.unpack(">H",uc.mem_read(COLORMAP+2,2))[0]
            self.first_count=count
            vals=[v for i in range(count) for v in self.palette_rgb[i]]
            uc.mem_write(self.a(1),struct.pack(">"+("I"*len(vals)),*vals))
            self._return()
            return
        if address==DOSLIB-30:
            assert self.d(2)==1006,"must use MODE_NEWFILE to replace"
            assert self.cstring(self.d(1))==b"test.iff"
            if self.fail_open:
                self._return()
            else:
                self.open_files+=1
                self.saved=b""       # old file truncated, per DOS NEWFILE
                self._return(7)
            return
        if address==DOSLIB-48:
            self.write_calls+=1
            assert self.open_files==1
            assert self.d(1)==7
            n=self.d(3)
            payload=bytes(uc.mem_read(self.d(2),n))
            if self.fail_write:
                self._return(0xffffffff)
            elif self.short_write:
                self.saved=payload[:-1]
                self._return(n-1)
            else:
                self.saved=payload
                self._return(n)
            return
        if address==DOSLIB-36:
            assert self.open_files==1
            self.open_files-=1
            self._return(0 if self.fail_close else 1)
            return
        if address==DOSLIB-72:
            assert self.open_files==0
            assert self.cstring(self.d(1))==b"test.iff"
            self.deleted+=1
            self.saved=None
            self._return(1)
            return
        super().os_call(uc,address,size,user)

def expected_iff(m,depth,n):
    cmap=bytes((m.palette_rgb[i][k]>>24)&255 for i in range(n) for k in range(3))
    bmhd=struct.pack(">HHhhBBBBHBBhh",320,256,0,0,depth,0,0,0,0,1,1,320,256)
    content=b"ILBM"+chunk(b"BMHD",bmhd)+chunk(b"CMAP",cmap)
    return b"FORM"+struct.pack(">I",len(content))+content, cmap

def test_machine(raw,depth=8,colors=None,**kw):
    m=SaveMachine(raw,depth=depth,colors=colors,**kw)
    result=m.execute(ENTRY_SAVE)
    assert not m.owned and not m.open_libraries and not m.open_files
    assert m.plane_writes==0 and m.rgb_writes==0
    assert m.saved is None or m.saved.startswith(b"FORM")
    return m,result

def run():
    candidate,report=build()
    assert candidate==build()[0],"builder not deterministic"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    oldtok,old,_=split(BASE.read_bytes())
    newtok,segments,_=split(candidate)
    assert len(old)==OLD_ENTRIES and len(segments)==OLD_ENTRIES+1
    assert segments[:39]==old[:39]
    assert segments[39]==old[39]+GETP
    assert newtok.startswith(oldtok[:-6])
    assert len([x for x in audit(parse(candidate))["tokens"] if x["name"].startswith("aga ")])==35
    assert not audit(parse(candidate))["issues"]

    machinecode,labels=emit_save()
    assert segments[ENTRY_SAVE]==machinecode
    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    end=labels["dosname"]
    dis=list(md.disasm(machinecode[:end],0))
    assert sum(i.size for i in dis)==end
    assert not any(i.mnemonic in ("dc.w","illegal","trap") for i in dis)
    boundaries={i.address for i in dis}
    assert all(v in boundaries or v==end for v in labels.values() if v<=end)

    count=0
    # Palette sizes, depths, no BODY, correct CMAP high bytes and IFF lengths.
    for depth in range(1,9):
        for n in (1,2,1<<depth):
            m,result=test_machine(candidate,depth=depth,colors=n)
            assert result==1,(depth,n,result)
            assert m.write_calls==m.get_calls==1 and m.first_count==n
            expected,cmap=expected_iff(m,depth,n)
            assert m.saved==expected,(depth,n,len(m.saved),len(expected))
            assert int.from_bytes(m.saved[4:8],"big")==len(m.saved)-8
            assert m.saved[12:16]==b"BMHD" and m.saved[40:44]==b"CMAP"
            assert int.from_bytes(m.saved[44:48],"big")==n*3
            assert b"BODY" not in m.saved
            assert m.saved[-1]==0 if (n&1) else True
            count+=1
    # Native R28 palette loader must accept each R29 output without BODY.
    from test_m13_palette_r28 import PaletteMachine as R28Machine
    for depth in (1,4,8):
        m,saved_ok=test_machine(candidate,depth=depth)
        assert saved_ok==1
        incoming=R28Machine(BASE.read_bytes(),data=m.saved,depth=depth)
        assert incoming.load()==1,"R29 IFF must reload with frozen R28"
        expected,cmap=expected_iff(m,depth,1<<depth)
        assert bytes((x>>24)&255 for triple in incoming.palette_rgb[:1<<depth] for x in triple)==cmap
        assert incoming.plane_writes==0
        count+=1
    # Logical palette bound smaller than ColorMap.Count.
    m,result=test_machine(candidate,depth=4,colors=32)
    assert result==1 and m.first_count==16
    count+=1
    # Rejection before clobbering an existing file.
    for off,val in ((0,0),(8,0),(12,0),(16,0),(20,0),(20,257),
                    (28,0),(28,9),(24,0x400),(24,0x800),(24,0x80)):
        m=SaveMachine(candidate)
        m.put(STATE+off,val)
        result=m.execute(ENTRY_SAVE)
        assert result==0 and m.saved is None and m.write_calls==0,(off,val,result)
        assert not m.owned and not m.open_files and not m.open_libraries
        count+=1
    for cmap_count in (0,257):
        m=SaveMachine(candidate,colors=cmap_count)
        result=m.execute(ENTRY_SAVE)
        assert result==0 and m.write_calls==0 and not m.owned
        count+=1
    # Empty / too long AMOS string.
    for filename in (b"",b"x"*256):
        m=SaveMachine(candidate)
        m.uc.mem_write(NAME,struct.pack(">H",len(filename))+filename)
        result=m.execute(ENTRY_SAVE)
        assert result==0 and m.saved is None and not m.owned
        count+=1
    # Allocation failure, DOS open, short/error writes, Close failure.
    for stage in (1,2):
        m,result=test_machine(candidate,allocation_failure=stage)
        assert result==0 and m.saved is None
        count+=1
    for kwargs in (dict(fail_open=True),dict(fail_write=True),
                   dict(short_write=True),dict(fail_close=True)):
        m,result=test_machine(candidate,**kwargs)
        assert result==0 and m.saved is None,kwargs
        if kwargs.get("fail_open"):
            assert m.deleted==0 and m.write_calls==0
        else:
            assert m.deleted==1
        count+=1
    print("M13 R29 native 68000 Gate A PASS:",count,"scenarios",flush=True)
    print("M13 R29 candidate:",{k:v for k,v in report.items() if k!="labels"},flush=True)
    print("Gate B WinUAE / Gate C Compiler / Gate D physical AGA: NOT TESTED")

if __name__=="__main__":
    run()
