#!/usr/bin/env python3
"""M18/R64 Gate A: execute real 68000 bank-creation code with mocked AMOS.

Emulates the public AP20 body for interpreted / compiler-style relocation.
AMOS bank services are separate symbol-derived callbacks. Checks ABI,
allocation collisions, exact 12+288*N bank payload, zero-colour canonical
mask, unchanged older banks and cleanup. NOT a WinUAE Gate B/C.
"""
from __future__ import annotations
from struct import pack,unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from test_m5_generic import Machine,DR,AR,AMOS,STACK,STOP
from amos_link_test_support import main_table,relocate,MAIN_BASE
from amos_main_abi import declarations
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from m18_ficon16_model import parse_bank,SLOT_BYTES
from build_m18_r64_ficon_bank_create import build,API
from build_m18_r63_chip_blit import build as build_r63
from m18_ficon_bank_create_emit import (
    emit_ficon_bank_create,ENTRY_INDEX,NAME,GETADR_MARKER,RESERVE_MARKER,
    CHANGE_MARKER,EFF_MARKER,
)

ENTRY=0x180000
COMPILED=0x1a0000
ARGUMENTS=0x58000
NEW_BANK=0xb00000
EXISTING=0xd00000
SENTINEL=b"KEEP EXISTING BANK UNCHANGED!"
CANARY=b"GUARD-R64"
NAMES=("Bnk.GetAdr","Bnk.Reserve","Bnk.Change","Bnk.Eff")

class BankMachine(Machine):
    def __init__(self,binary,*,layout="interpreted",occupied=False,
                 reserve_fail=False,late_collision=False,bad_pointer=None):
        super().__init__(binary,None)
        table,names=main_table(self.uc)
        self.targets={table[idx]:name for idx,name,*_ in declarations()
                      if name in NAMES}
        assert set(self.targets.values())==set(NAMES)
        self.calls=[]
        self.lookups=0
        self.change_count=0
        self.erase_count=0
        self.reserve_count=0
        self.reserve_fail=reserve_fail
        self.late_collision=late_collision
        self.bad_pointer=bad_pointer
        self.banks={10:EXISTING}
        if occupied:self.banks[11]=EXISTING
        self.uc.mem_write(EXISTING,SENTINEL)
        self.uc.hook_add(UC_HOOK_CODE,self.bank_call,
                         begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        for address in self.targets:self.uc.mem_write(address,b"\\x4e\\x75")
        tokens,parts=unwrap_native_parts_v2(binary)
        assert len(parts)==ENTRY_INDEX+1
        if layout=="interpreted":
            self.entry=ENTRY
        elif layout=="compiled":
            self.entry=COMPILED
        else:raise ValueError(layout)
        self.uc.mem_write(self.entry,relocate(parts[ENTRY_INDEX],self.entry,
                                             {ENTRY_INDEX+1:self.entry+0x3000},
                                             self.uc))
        self.total=None

    def _return(self,ret=0):
        self.uc.reg_write(DR[0],ret&0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000)
        self.uc.reg_write(AR[1],0xbad100)
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def bank_call(self,uc,address,size,user):
        if address not in self.targets:return
        name=self.targets[address]
        self.calls.append(name)
        assert self.a(5)==AMOS,"AMOS A5 lost"
        if name=="Bnk.GetAdr":
            self.lookups+=1
            bank=self.d(0)
            if self.late_collision and self.lookups==2 and bank not in self.banks:
                self.banks[bank]=EXISTING
            p=self.banks.get(bank,0)
            self.uc.reg_write(AR[0],p)
            self.uc.reg_write(AR[1],p)
            self.uc.reg_write(DR[1],0xdeadbeef)
            self._return_bank_ptr(p)
        elif name=="Bnk.Reserve":
            self.reserve_count+=1
            num,flags,total=self.d(0),self.d(1),self.d(2)
            assert num not in self.banks,"destructive bank replacement"
            assert 5<=num<=65535 and flags==1
            assert 1164<=total<=1179660
            assert bytes(uc.mem_read(self.a(0),8))==NAME,"wrong bank name"
            self.total=total
            if self.reserve_fail:
                self._return(0)
            else:
                ptr=(NEW_BANK if self.bad_pointer is None
                     else self.bad_pointer)
                self.banks[num]=ptr
                if ptr==NEW_BANK or ptr==NEW_BANK+1:
                    self.uc.mem_write(ptr,bytes(total))
                    self.uc.mem_write(ptr-24,pack(">IIIHH8s",0,total+16,num,
                                                 flags,0,NAME))
                    self.uc.mem_write(ptr+total,CANARY)
                self._return(ptr)
        elif name=="Bnk.Change":
            self.change_count+=1
            number=next((n for n,p in self.banks.items() if p==NEW_BANK),None)
            assert number is not None
            payload=bytes(self.uc.mem_read(NEW_BANK,self.total))
            assert parse_bank(payload).count==(self.total-12)//288
            self._return()
        elif name=="Bnk.Eff":
            self.erase_count+=1
            number=self.d(0)
            assert number!=10 and number in self.banks
            self.banks.pop(number)
            self._return()

    def _return_bank_ptr(self,p):
        sp=self.a(7)
        # Bnk.GetAdr returns A0/A1 (not D0) for the requested bank.
        self.uc.reg_write(AR[0],p)
        self.uc.reg_write(AR[1],p)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def run_create(self,bank=11,count=4,*,limit=1800000):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGUMENTS)
        self.put(ARGUMENTS,bank)
        self.uc.reg_write(DR[3],count&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:self.uc.emu_start(self.entry,STOP,count=limit)
        except Exception as exc:
            raise AssertionError((
                "R64 68000 exception",str(exc),hex(self.uc.reg_read(UC_M68K_REG_PC)),
                "bank",bank,"count",count,"calls",self.calls)) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,"no RTS"
        assert self.a(7)==STACK+4,"SP not restored"
        assert self.a(3)==ARGUMENTS+4,"Bank argument not consumed"
        for reg,value in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==value,("clobbered register",reg)
        assert self.d(2)==0,"result must be integer"
        assert self.d(3) in (0,1),"result must be boolean"
        assert bytes(self.uc.mem_read(EXISTING,len(SENTINEL)))==SENTINEL
        return self.d(3)

def validate(binary,layout,bank,count,expected,**opts):
    m=BankMachine(binary,layout=layout,**opts)
    result=m.run_create(bank,count)
    assert result==expected,(layout,bank,count,opts,result,m.calls)
    if expected:
        assert m.calls==["Bnk.GetAdr","Bnk.GetAdr","Bnk.Reserve","Bnk.Change"],m.calls
        assert m.reserve_count==m.change_count==1 and m.erase_count==0
        raw=bytes(m.uc.mem_read(NEW_BANK,m.total))
        b=parse_bank(raw)
        assert b.count==count and len(raw)==12+count*SLOT_BYTES
        assert raw[:12]==pack(">IHHHH",len(raw),count,16,16,8)
        assert raw[12:30]==pack(">H8H",0xffff,*([0]*8))
        for i in (1,count//2,count):
            slot=b.icon(i)
            assert slot==pack(">H8H",0xffff,*([0]*8))*16
        assert bytes(m.uc.mem_read(NEW_BANK+m.total,len(CANARY)))==CANARY
    else:
        assert m.change_count==0,"failed function notified ready bank"
        assert m.reserve_count<=1,"multiple allocations"
        assert not any(n not in (10,11) for n in m.banks)
        if "Bnk.Reserve" in m.calls and not opts.get("reserve_fail"):
            assert m.erase_count==1,("allocation leaked",m.calls)
        else:assert m.erase_count==0
    return 1

def main():
    binary,info=build()
    assert build()[0]==binary,"builder is not deterministic"
    r63,_=build_r63()
    _,before=unwrap_native_parts_v2(r63)
    _,after=unwrap_native_parts_v2(binary)
    assert len(before)==62 and len(after)==63
    assert after[:61]==before[:61] and after[61]==before[61]+b"GetP"
    native,labels=emit_ficon_bank_create()
    assert after[62]==native
    assert native.count(GETADR_MARKER)==2
    assert native.count(RESERVE_MARKER)==native.count(CHANGE_MARKER)==native.count(EFF_MARKER)==1
    assert labels["empty_row"]<labels["erase_new"]<labels["return"]<labels["bank_name"]
    stripped=native[:labels["bank_name"]]
    for marker in (GETADR_MARKER,RESERVE_MARKER,CHANGE_MARKER,EFF_MARKER):
        stripped=stripped.replace(marker,bytes.fromhex("4eb900030000"))
    dis=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
             .disasm(stripped,0))
    assert sum(i.size for i in dis)==len(stripped),"R64 invalid 68000 opcodes"
    cases=0
    for layout in ("interpreted","compiled"):
        for number,count in ((11,4),(11,32),(11,256),(65535,4),
                             (5,4096)):
            cases+=validate(binary,layout,number,count,1)
        for number,count in ((11,0),(11,1),(11,3),(11,4097),
                             (11,-1),(11,65536),(4,4),(0,4),
                             (65536,4),(-1,4)):
            cases+=validate(binary,layout,number,count,0)
        cases+=validate(binary,layout,10,4,0) # occupied bank
        cases+=validate(binary,layout,11,4,0,occupied=True)
        cases+=validate(binary,layout,11,4,0,late_collision=True)
        cases+=validate(binary,layout,11,4,0,reserve_fail=True)
        cases+=validate(binary,layout,11,4,0,bad_pointer=NEW_BANK+1)
        cases+=validate(binary,layout,11,4,0,bad_pointer=0xfffffff0)
    assert info["commands"]==57 and info["ap20_entries"]==64
    print("M18/R64 FICON8 CREATE GATE A PASS:",cases,
          "native 68000 AP20 cases, both layouts, memory & ABI")
    print("RELEASE CANDIDATE SHA256",info["sha256"],
          "BYTES",info["bytes"],"No WinUAE Gate B/C yet.")
if __name__=="__main__":
    main()
