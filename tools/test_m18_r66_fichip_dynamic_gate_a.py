#!/usr/bin/env python3
"""R66 Gate A: execute both real 68000 AP20 entries with mocked AMOS/Exec.

Verifies bank allocation in actual simulated Chip, strict DATA metadata,
unchanged existing banks, cleanup on late errors, exact FICHIP8 planar
stage/re-stage, atomic rejects, canaries, result/ABI, and relocations for
interpreted + compiler-style placements. NOT actual WinUAE Gate B/C.
"""
from struct import pack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import Machine,DR,AR,AMOS,EXEC,STACK,STOP
from amos_link_test_support import main_table,relocate,MAIN_BASE
from amos_main_abi import declarations
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from build_m18_r66_fichip_dynamic import build,APIS
from build_m18_r65_ficon_bank_put import build as build_r65
from m18_fichip_dynamic_emit import (
    emit_chip_bank_create,emit_chip_stage,ENTRY_CREATE,ENTRY_STAGE,
    GETADR_MARKER,RESERVE_MARKER,CHANGE_MARKER,EFF_MARKER)
from m18_ficon16_model import build_bank
from m18_ficon_chip_cache import empty_payload,parse_cache,stage

ENTRY=0x180000
COMPILED=0x1a0000
ARGUMENTS=0x58000
NEW=0xb00000
OLD=0xd00000
SRC=0x900000
GUARD=b"R66-GUARD-POST"
SENTINEL=b"DO-NOT-OVERWRITE-OLDER-BANK"
NAMES=("Bnk.GetAdr","Bnk.Reserve","Bnk.Change","Bnk.Eff")
PX=(
 bytes(0 if (x+y)%3==0 else ((x*17+y*11)&255) for y in range(16) for x in range(16)),
 bytes([255]*256),
 bytes([0]*256),
 bytes(range(256)),
)
CHIP_NAME=b"FICHIP8 "
SOURCE_NAME=b"FICON8  "

def setup_abi(m,idx,params):
    for i,r in enumerate(DR):m.uc.reg_write(r,0x1200+i)
    for i,r in enumerate(AR[:7]):m.uc.reg_write(r,0x40000+i*256)
    m.uc.reg_write(AR[5],AMOS)
    m.uc.reg_write(AR[3],ARGUMENTS)
    for i,n in enumerate(params[1:]):m.put(ARGUMENTS+4*i,n)
    m.uc.reg_write(DR[3],params[0]&0xffffffff)
    saved={reg:m.uc.reg_read(reg) for reg in DR+AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR,0x2000)
    m.uc.reg_write(AR[7],STACK)
    m.put(STACK,STOP)
    return saved

def assert_abi(m,saved,params):
    assert m.uc.reg_read(UC_M68K_REG_PC)==STOP
    assert m.a(7)==STACK+4
    assert m.a(3)==ARGUMENTS+4*(len(params)-1)
    assert m.d(2)==0
    for reg,val in saved.items():
        if reg not in (DR[2],DR[3],AR[3]):
            assert m.uc.reg_read(reg)==val,("R66 ABI register clobbered",reg)
    assert m.d(3) in (0,1)

class Services(Machine):
    def __init__(self,library,idx,layout):
        super().__init__(library,None)
        self.calls=[];self.type_calls=[]
        table,_=main_table(self.uc)
        self.addr={table[i]:name for i,name,*_ in declarations() if name in NAMES}
        assert set(self.addr.values())==set(NAMES)
        for a in self.addr:self.uc.mem_write(a,bytes.fromhex("4e75"))
        self.uc.mem_write(EXEC-534,bytes.fromhex("4e75"))
        self.uc.hook_add(UC_HOOK_CODE,self.bank_call,begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        _,parts=unwrap_native_parts_v2(library)
        assert len(parts)==ENTRY_STAGE+1
        self.entry=(ENTRY if layout=="interpreted" else COMPILED)
        self.uc.mem_write(self.entry,relocate(
            parts[idx],self.entry,{idx+1:self.entry+0x3000},self.uc))
        self.banks={10:OLD}
        self.uc.mem_write(OLD,SENTINEL)
        self.mode="create"
        self.nonchip=False
        self.fail_on=None
        self.reserve_fail=False
        self.bad_pointer=None
        self.late_collision=False
        self.gets=0
        self.last_total=0

    def _ret(self,ret=0,*,ptr=None):
        self.uc.reg_write(DR[0],ret&0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000 if ptr is None else ptr)
        self.uc.reg_write(AR[1],0xbad100 if ptr is None else ptr)
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def bank_call(self,uc,address,size,user):
        if address not in self.addr:
            raise AssertionError(("unexpected AMOS call",hex(address)))
        name=self.addr[address]
        self.calls.append(name)
        assert self.a(5)==AMOS
        if name=="Bnk.GetAdr":
            self.gets+=1
            number=self.d(0)
            if self.late_collision and self.gets==2 and number not in self.banks:
                self.banks[number]=OLD
            ptr=self.banks.get(number,0)
            self._ret(ptr,ptr=ptr)
        elif name=="Bnk.Reserve":
            bank,flags,total=self.d(0),self.d(1),self.d(2)
            assert flags==3 and 5<=bank<=65535
            assert bank not in self.banks,"R66 overwrote existing bank"
            assert bytes(uc.mem_read(self.a(0),8))==CHIP_NAME
            assert 12+4*289<=total<=12+4096*289
            self.last_total=total
            if self.reserve_fail:
                self._ret(0)
            else:
                ptr=NEW if self.bad_pointer is None else self.bad_pointer
                self.banks[bank]=ptr
                if ptr in (NEW,NEW+1):
                    self.uc.mem_write(ptr,bytes(total))
                    self.uc.mem_write(ptr-24,pack(">IIIHH8s",0,total+16,bank,flags,0,CHIP_NAME))
                    self.uc.mem_write(ptr+total,GUARD)
                self._ret(ptr)
        elif name=="Bnk.Change":
            ptr=next((pointer for pointer in self.banks.values() if pointer==NEW),None)
            assert ptr==NEW
            raw=bytes(self.uc.mem_read(NEW,self.last_total))
            assert parse_cache(raw).count==(self.last_total-12)//289
            self._ret()
        elif name=="Bnk.Eff":
            num=self.d(0)
            assert num!=10 and num in self.banks
            self.banks.pop(num)
            self._ret()

    def os_call(self,uc,address,size,user):
        if address!=EXEC-534:
            raise AssertionError(("unexpected Exec OS call",hex(address)))
        where=self.a(1)
        self.type_calls.append(where)
        iscache=(NEW-24<=where<NEW+self.last_total)
        issource=(SRC-24<=where<SRC+len(getattr(self,"source",b"")))
        if self.mode=="create":
            memflag=1 if self.nonchip else 3
            result=memflag if iscache else 0
        else:
            result=3 if iscache else 1 if issource else 0
            if self.nonchip and iscache:result=1
        if self.fail_on is not None and where==self.fail_on:result=0
        self._ret(result)

class CreateMachine(Services):
    def __init__(self,binary,layout="interpreted",*,nonchip=False,
                 occupied=False,reserve_fail=False,bad_pointer=None,
                 late_collision=False,fail_end=False):
        super().__init__(binary,ENTRY_CREATE,layout)
        self.nonchip=nonchip
        self.reserve_fail=reserve_fail
        self.bad_pointer=bad_pointer
        self.late_collision=late_collision
        if occupied:self.banks[11]=OLD
        self.fail_end=fail_end

    def run(self,bank=11,count=4,expected=1):
        params=(count,bank)
        saved=setup_abi(self,ENTRY_CREATE,params)
        if self.fail_end:
            self.fail_on=NEW+(12+count*289)-1
        try:self.uc.emu_start(self.entry,STOP,count=6500000)
        except Exception as ex:
            raise AssertionError(("Create 68000 crash",str(ex),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),bank,count,self.calls,
                list(map(hex,self.type_calls[-8:])))) from ex
        assert_abi(self,saved,params)
        assert self.d(3)==expected,(bank,count,expected,self.d(3),self.calls,
                                   list(map(hex,self.type_calls[-8:])))
        assert bytes(self.uc.mem_read(OLD,len(SENTINEL)))==SENTINEL
        if expected:
            assert self.calls==["Bnk.GetAdr","Bnk.GetAdr","Bnk.Reserve","Bnk.Change"]
            assert self.banks[bank]==NEW
            raw=bytes(self.uc.mem_read(NEW,self.last_total))
            assert raw==empty_payload(count)
            assert bytes(self.uc.mem_read(NEW+self.last_total,len(GUARD)))==GUARD
        else:
            assert "Bnk.Change" not in self.calls
            assert "Bnk.Reserve" not in self.calls or self.calls.count("Bnk.Reserve")==1
            if "Bnk.Reserve" in self.calls and not self.reserve_fail:
                assert self.calls[-1]=="Bnk.Eff",self.calls
                assert bank not in self.banks
        return 1

class StageMachine(Services):
    def __init__(self,binary,layout="interpreted",*,src_count=4,
                 cache_count=4,icon_pattern=PX,src_flags=1,
                 cache_flags=3,nonchip=False,missing=None,
                 corrupt=None,ready_slot=0,fail_on=None,alias=False):
        super().__init__(binary,ENTRY_STAGE,layout)
        self.mode="stage"
        self.nonchip=nonchip
        self.source=build_bank(tuple(icon_pattern[i%len(icon_pattern)]
                                     for i in range(src_count)))
        self.cache=empty_payload(cache_count)
        if ready_slot:
            self.cache=stage(self.cache,self.source,ready_slot)
        self.uc.mem_write(SRC-24,pack(">IIIHH8s",0,len(self.source)+16,12,src_flags,0,SOURCE_NAME))
        self.uc.mem_write(SRC,self.source)
        self.uc.mem_write(SRC+len(self.source),GUARD)
        self.uc.mem_write(NEW-24,pack(">IIIHH8s",0,len(self.cache)+16,11,cache_flags,0,CHIP_NAME))
        self.uc.mem_write(NEW,self.cache)
        self.uc.mem_write(NEW+len(self.cache),GUARD)
        self.last_total=len(self.cache)
        self.banks[12]=SRC;self.banks[11]=NEW
        if missing:self.banks.pop(missing,None)
        if alias:self.banks[11]=SRC
        if corrupt:
            target=NEW if corrupt.startswith("cache_") else SRC
            what=corrupt.split("_",1)[1]
            if what=="name":self.uc.mem_write(target-8,b"AGAPIC  ")
            elif what=="number":self.put(target-16,15)
            elif what=="flags":self.uc.mem_write(target-12,bytes.fromhex("0002"))
            elif what=="len":self.put(target-20,
                     (len(self.cache) if target==NEW else len(self.source))+17)
            elif what=="w":self.uc.mem_write(target+6,bytes.fromhex("0020"))
            elif what=="count":self.uc.mem_write(target+4,bytes.fromhex("0003"))
            elif what=="mask":
                self.uc.mem_write(target+12+288,bytes.fromhex("ffff")) # selected icon 2
            elif what=="marker":
                off=12+cache_count*288+1 # tested icon=2
                self.uc.mem_write(NEW+off,b"\x03")
            else:raise ValueError(corrupt)
        self.cache_before=bytes(self.uc.mem_read(NEW,len(self.cache)))
        self.source_before=bytes(self.uc.mem_read(SRC,len(self.source)))
        self.fail_on=fail_on

    def run(self,icon=2,source_bank=12,cache_bank=11,expected=1):
        params=(icon,cache_bank,source_bank)
        saved=setup_abi(self,ENTRY_STAGE,params)
        try:self.uc.emu_start(self.entry,STOP,count=6500000)
        except Exception as ex:
            raise AssertionError(("Stage 68000 crash",str(ex),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),
                icon,source_bank,cache_bank,self.calls,
                list(map(hex,self.type_calls[-12:])))) from ex
        assert_abi(self,saved,params)
        assert self.d(3)==expected,(
            "Stage wrong result",icon,source_bank,cache_bank,self.d(3),
            self.calls,list(map(hex,self.type_calls[-12:])))
        src=bytes(self.uc.mem_read(SRC,len(self.source)))
        result=bytes(self.uc.mem_read(NEW,len(self.cache)))
        assert src==self.source_before,"stage changed source bank"
        assert bytes(self.uc.mem_read(SRC+len(self.source),len(GUARD)))==GUARD
        assert bytes(self.uc.mem_read(NEW+len(self.cache),len(GUARD)))==GUARD
        assert bytes(self.uc.mem_read(OLD,len(SENTINEL)))==SENTINEL
        if expected:
            assert result==stage(self.cache_before,self.source_before,icon),(
                "staging not identical to host oracle",
                next((i for i,(a,b) in enumerate(zip(result,stage(
                    self.cache_before,self.source_before,icon))) if a!=b),None))
            assert parse_cache(result).slot(icon)
            assert self.calls==["Bnk.GetAdr","Bnk.GetAdr"]
        else:
            assert result==self.cache_before,"rejected stage modified cache"
        return 1

def main():
    lib,meta=build()
    assert build()[0]==lib,"R66 builder nondeterministic"
    old,_=build_r65()
    _,before=unwrap_native_parts_v2(old)
    _,after=unwrap_native_parts_v2(lib)
    assert len(before)==64 and len(after)==66
    assert after[:63]==before[:63] and after[63]==before[63]+b"GetP"
    create,lab1=emit_chip_bank_create()
    staged,lab2=emit_chip_stage()
    assert after[64]==create+b"GetP" and after[65]==staged
    assert create.count(GETADR_MARKER)==staged.count(GETADR_MARKER)==2
    assert create.count(RESERVE_MARKER)==create.count(CHANGE_MARKER)==create.count(EFF_MARKER)==1
    assert staged.count(RESERVE_MARKER)==staged.count(CHANGE_MARKER)==staged.count(EFF_MARKER)==0
    for native,labels in ((create,lab1),(staged,lab2)):
        body=native[:labels["bank_name"]] if "bank_name" in labels else native
        for marker in (GETADR_MARKER,RESERVE_MARKER,CHANGE_MARKER,EFF_MARKER):
            body=body.replace(marker,bytes.fromhex("4eb900030000"))
        decoded=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(body,0))
        assert sum(x.size for x in decoded)==len(body),"invalid 68000 opcode"
    checks=0
    for layout in ("interpreted","compiled"):
        for bank,count in ((11,4),(11,32),(11,256),(11,4096),(5,4)):
            checks+=CreateMachine(lib,layout).run(bank,count)
        for bank,count in ((11,0),(11,1),(11,3),(11,-1),(11,4097),
                           (4,4),(0,4),(65536,4),(-1,4)):
            checks+=CreateMachine(lib,layout).run(bank,count,0)
        for opts in (dict(occupied=True),dict(late_collision=True),
                     dict(reserve_fail=True),dict(nonchip=True),
                     dict(bad_pointer=NEW+1),dict(bad_pointer=0xfffffff0),
                     dict(fail_end=True)):
            checks+=CreateMachine(lib,layout,**opts).run(expected=0)
        for icon in (1,2,3,4):
            checks+=StageMachine(lib,layout).run(icon)
        for flags in (0,1,3):
            checks+=StageMachine(lib,layout,src_flags=flags,cache_flags=flags).run()
        checks+=StageMachine(lib,layout,src_count=4096,cache_count=4096).run(4096)
        checks+=StageMachine(lib,layout,src_count=8,cache_count=4).run()
        checks+=StageMachine(lib,layout,ready_slot=2).run()
        for kwargs in (
            dict(icon=0),dict(icon=-1),dict(icon=5),dict(icon=4097),
            dict(source_bank=4),dict(source_bank=-1),dict(source_bank=65536),
            dict(cache_bank=4),dict(cache_bank=-1),dict(cache_bank=65536),
            dict(source_bank=11),dict(cache_bank=12),
        ):
            checks+=StageMachine(lib,layout).run(expected=0,**kwargs)
        for options in (
            dict(nonchip=True),dict(missing=12),dict(missing=11),dict(alias=True),
            dict(corrupt="source_name"),dict(corrupt="cache_name"),
            dict(corrupt="source_flags"),dict(corrupt="cache_flags"),
            dict(corrupt="source_number"),dict(corrupt="cache_number"),
            dict(corrupt="source_len"),dict(corrupt="cache_len"),
            dict(corrupt="source_count"),dict(corrupt="cache_count"),
            dict(corrupt="source_mask"),dict(corrupt="cache_marker"),
            dict(fail_on=SRC+build_bank((PX[0],)*4).__len__()-1),
            dict(fail_on=NEW+len(empty_payload(4))-1),
        ):
            checks+=StageMachine(lib,layout,**options).run(expected=0)
    assert meta["commands"]==60 and meta["ap20_entries"]==67
    print("M18/R66 FICHIP8 DYNAMIC CREATE+STAGE Gate A PASS",checks,
          "real 68000/ABI cases, source intact, staging exact, Chip verified")
    print("M18_R66_CANDIDATE_SHA256",meta["sha256"],"BYTES",meta["bytes"],
          "NOT WinUAE B/C")
if __name__=="__main__":
    main()
