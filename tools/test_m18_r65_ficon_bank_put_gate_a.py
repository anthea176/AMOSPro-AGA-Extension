#!/usr/bin/env python3
"""R65 AP20 actual 68000 bulk FICON8 Bank Put native Gate A.

Mocked AMOS GetAdr and Exec TypeOfMem; two real 68000 layouts (interpreter
and relocated/compiler-style). Validates exact 288-byte packed slot, all
unrelated bytes, canaries, error atomicity, ABI and metadata. NOT WinUAE B/C.
"""
from __future__ import annotations
from struct import pack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import Machine,DR,AR,AMOS,EXEC,STACK,STOP
from amos_link_test_support import main_table,relocate,MAIN_BASE
from amos_main_abi import declarations
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from m18_ficon16_model import build_bank,parse_bank
from m18_ficon_bank_put_model import put_chunky
from build_m18_r65_ficon_bank_put import build
from build_m18_r64_ficon_bank_create import build as build_r64
from m18_ficon_bank_put_emit import emit_ficon_bank_put,GETADR_MARKER,ENTRY_INDEX
from hashlib import sha256

DEST=0x900000
SOURCE=0xb00000
ENTRY=0x180000
COMPILED=0x1a0000
ARGUMENTS=0x58000
DST_GUARD=b"R65-DEST-GUARD"
SRC_GUARD=b"R65-SOURCE-GUARD"
PIXELS=[
    bytes(0 if (x+y)%3==0 else (x*17+y*11)&255
          for y in range(16) for x in range(16)),
    bytes([255]*256),
    bytes([0]*256),
    bytes((128 if (x in (0,15) or y in (0,15))
           else 1 if ((x+y)&1) else 0) for y in range(16) for x in range(16)),
]

class PutMachine(Machine):
    def __init__(self,lib,*,layout="interpreted",count=4,
                 pix=PIXELS[0],offset=3,src_len=None,src_flags=1,
                 dst_flags=1,missing_dst=False,missing_src=False,
                 mutation=None,mem_fail=None):
        super().__init__(lib,None)
        self.dest=build_bank((bytes(256),)*count)
        self.source=b"hdr"+pix+b"t"*(17)
        if offset!=3:
            # Offset is an argument; use a generic source whose image is at
            # that offset for positive in-bounds cases.
            self.source=bytes([0x7e])*max(offset,0)+pix+bytes([0xf5])*7
        if src_len is not None:
            self.source=self.source[:src_len]
        self.pixels=pix
        self.offset=offset
        self.mem_fail=mem_fail
        self.banks={12:DEST,13:SOURCE}
        if missing_dst:self.banks.pop(12)
        if missing_src:self.banks.pop(13)
        self.uc.mem_write(DEST-24,pack(">IIIHH8s",0,len(self.dest)+16,12,dst_flags,0,b"FICON8  "))
        self.uc.mem_write(DEST,self.dest)
        self.uc.mem_write(DEST+len(self.dest),DST_GUARD)
        self.uc.mem_write(SOURCE-24,pack(">IIIHH8s",0,len(self.source)+16,13,src_flags,0,b"PIXDATA "))
        self.uc.mem_write(SOURCE,self.source)
        self.uc.mem_write(SOURCE+len(self.source),SRC_GUARD)
        if mutation:mutation(self)
        self.dest_before=bytes(self.uc.mem_read(DEST,len(self.dest)))
        self.source_before=bytes(self.uc.mem_read(SOURCE,len(self.source)))
        self.dst_guard_before=bytes(self.uc.mem_read(DEST+len(self.dest),len(DST_GUARD)))
        self.src_guard_before=bytes(self.uc.mem_read(SOURCE+len(self.source),len(SRC_GUARD)))
        self.main_calls=[]
        self.type_calls=[]
        table,_=main_table(self.uc)
        getadr=next(idx for idx,name,*_ in declarations() if name=="Bnk.GetAdr")
        self.getadr_addr=table[getadr]
        self.uc.mem_write(self.getadr_addr,bytes.fromhex("4e75"))
        self.uc.mem_write(EXEC-534,bytes.fromhex("4e75"))
        self.uc.hook_add(UC_HOOK_CODE,self.main_call,begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        _,parts=unwrap_native_parts_v2(lib)
        assert len(parts)==ENTRY_INDEX+1
        self.entry=ENTRY if layout=="interpreted" else COMPILED
        self.uc.mem_write(self.entry,relocate(parts[ENTRY_INDEX],self.entry,
                        {ENTRY_INDEX+1:self.entry+0x2000},self.uc))

    def _return(self,value):
        self.uc.reg_write(DR[0],value&0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000)
        self.uc.reg_write(AR[1],0xbad100)
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def main_call(self,uc,address,size,user):
        if address!=self.getadr_addr:
            raise AssertionError(("unexpected AMOS service",hex(address)))
        self.main_calls.append("Bnk.GetAdr")
        assert self.a(5)==AMOS
        pointer=self.banks.get(self.d(0),0)
        self.uc.reg_write(AR[0],pointer)
        self.uc.reg_write(AR[1],pointer)
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def os_call(self,uc,address,size,user):
        if address!=EXEC-534:
            raise AssertionError(("unexpected OS call",hex(address)))
        addr=self.a(1)
        self.type_calls.append(addr)
        covered=(DEST-24<=addr<DEST+len(self.dest) or
                 SOURCE-24<=addr<SOURCE+len(self.source))
        if self.mem_fail=="dest_end" and addr==DEST+len(self.dest)-1:
            covered=False
        if self.mem_fail=="source_end" and addr==SOURCE+len(self.source)-1:
            covered=False
        self._return(int(covered))

    def run_put(self,*,dest_bank=12,icon=2,source_bank=13,offset=None,
                expected=True,limit=2400000):
        if offset is None:offset=self.offset
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGUMENTS)
        for i,v in enumerate((source_bank,icon,dest_bank)):
            self.put(ARGUMENTS+i*4,v)
        self.uc.reg_write(DR[3],offset&0xffffffff)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:self.uc.emu_start(self.entry,STOP,count=limit)
        except Exception as e:
            raise AssertionError(("R65 68000 exception",str(e),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),
                "dest",dest_bank,"icon",icon,"src",source_bank,"offset",offset,
                "main calls",self.main_calls,"OS",self.type_calls)) from e
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,("No RTS",self.main_calls)
        assert self.a(7)==STACK+4 and self.a(3)==ARGUMENTS+12,"ABI stack"
        assert self.d(2)==0 and self.d(3)==int(expected),(
            "wrong result",self.d(2),self.d(3),dest_bank,icon,source_bank,offset)
        for reg,val in before.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==val,("register clobbered",reg)
        output=bytes(self.uc.mem_read(DEST,len(self.dest)))
        assert bytes(self.uc.mem_read(SOURCE,len(self.source)))==self.source_before
        assert bytes(self.uc.mem_read(DEST+len(self.dest),len(DST_GUARD)))==self.dst_guard_before
        assert bytes(self.uc.mem_read(SOURCE+len(self.source),len(SRC_GUARD)))==self.src_guard_before
        if expected:
            oracle=put_chunky(self.dest_before,icon,self.source_before,offset)
            assert output==oracle,("wrong packed planar words",
                                   next((i for i,(x,y) in enumerate(zip(output,oracle))
                                         if x!=y),None))
            assert parse_bank(output).count==len(self.dest_before[12:])//288
            assert self.main_calls==["Bnk.GetAdr","Bnk.GetAdr"]
        else:
            assert output==self.dest_before,"rejected call modified FICON bank"
        return 1

def fail_mutation(kind):
    def mutate(m):
        p=DEST
        if kind=="header":m.uc.mem_write(p+6,b"\0\x20")
        elif kind=="name":m.uc.mem_write(p-8,b"AGAPIC  ")
        elif kind=="length":m.put(p-20,len(m.dest)+17)
        elif kind=="flags":m.uc.mem_write(p-12,bytes.fromhex("0002"))
        elif kind=="number":m.put(p-16,11)
        elif kind=="count":m.uc.mem_write(p+4,bytes.fromhex("0003"))
        elif kind=="source_number":m.put(SOURCE-16,15)
        elif kind=="source_flags":m.uc.mem_write(SOURCE-12,bytes.fromhex("0002"))
        elif kind=="source_length":m.put(SOURCE-20,16+255)
        elif kind=="source_pointer":m.banks[13]=1
        else:raise ValueError(kind)
    return mutate

def main():
    lib,meta=build()
    assert build()[0]==lib,"R65 builder is nondeterministic"
    base,_=build_r64()
    _,previous=unwrap_native_parts_v2(base)
    _,parts=unwrap_native_parts_v2(lib)
    body,labels=emit_ficon_bank_put()
    assert len(previous)==63 and len(parts)==64
    assert parts[:62]==previous[:62] and parts[62]==previous[62]+b"GetP"
    assert parts[63]==body and body.count(GETADR_MARKER)==2
    code=body.replace(GETADR_MARKER,bytes.fromhex("4eb900030000"))
    decoder=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(code,0))
    assert sum(ins.size for ins in decoder)==len(code),"invalid native instruction(s)"
    assert not any(x.mnemonic.lower() in ("illegal","dc.w","trap","stop") for x in decoder)
    assert labels["row"]<labels["pixel"]<labels["plane"]<labels["fail"]
    count=0
    for layout in ("interpreted","compiled"):
        for icon in (1,2,3,4):
            for pix in PIXELS:
                count+=PutMachine(lib,layout=layout,pix=pix).run_put(icon=icon)
        for flags in (0,1,3):
            count+=PutMachine(lib,layout=layout,src_flags=flags,dst_flags=flags).run_put()
        count+=PutMachine(lib,layout=layout,count=4096).run_put(icon=4096)
        count+=PutMachine(lib,layout=layout,offset=0).run_put(offset=0)
        count+=PutMachine(lib,layout=layout,offset=7).run_put(offset=7)
        for opts in (
            dict(dest_bank=4),dict(dest_bank=65536),dict(dest_bank=-1),
            dict(source_bank=4),dict(source_bank=65536),
            dict(source_bank=12),dict(icon=0),dict(icon=-1),dict(icon=5),
            dict(icon=4097),dict(offset=-1),dict(offset=1000),
        ):
            count+=PutMachine(lib,layout=layout).run_put(expected=False,**opts)
        for args in (
            dict(missing_dst=True),dict(missing_src=True),
            dict(src_len=255),dict(mem_fail="dest_end"),
            dict(mem_fail="source_end"),
        ):
            count+=PutMachine(lib,layout=layout,**args).run_put(expected=False)
        for kind in ("header","name","length","flags","number",
                     "count","source_number","source_flags","source_length",
                     "source_pointer"):
            count+=PutMachine(lib,layout=layout,
                              mutation=fail_mutation(kind)).run_put(expected=False)
    assert meta["commands"]==58 and meta["ap20_entries"]==65
    print("M18/R65 FICON8 BANK PUT GATE A PASS",count,
          "real M68000 cases, two ABI layouts; exact slot and error atomicity")
    print("M18_R65_CANDIDATE_SHA256",meta["sha256"],
          "BYTES",meta["bytes"],"NO WINUAE GATE B/C CLAIMED")
if __name__=="__main__":
    main()
