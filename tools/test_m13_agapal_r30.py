#!/usr/bin/env python3
"""R30 M13 native 68000 Gate A tests, actual AP20 code in Unicorn.

Check the approved Aga Palette Bank Init(Start(bank),count) only.
The memory bank is an AMOS DATA fixture with a genuine documented
24-byte in-memory AMOS header. TypeOfMem is an OS stub, not a runtime
AMOS allocation proof. Gate B AMOS/WinUAE remains separate.
"""
from struct import pack,unpack_from
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from ap20_utils import split,digest
from audit_ap20 import parse,inspect as audit
from build_m13_agapal_r30 import (
    build,BASE,BASE_SHA256,LAST_GOOD,LAST_GOOD_SHA256,
    ENTRY_INDEX,BASE_ENTRIES,API,GETP,
)
from m13_agapal_r30_emit import emit_init
from agapal_r30_layout import init_payload,payload_size,parse_payload
from test_m5_generic import Machine,CODE,STOP,STACK,DR,AR,AMOS,EXEC

ARGS=0x58000
BANK=0x62000

class BankMachine(Machine):
    def __init__(self,binary,count=8,flags=1,bankno=10,declared=None,
                 type_header=True,type_end=True,name=b"Data    "):
        super().__init__(binary,None,None)
        self.uc.mem_write(EXEC-534,b"\x4e\x75")
        self.count=count
        self.bankno=bankno
        self.length=payload_size(count)
        self.declared=declared if declared is not None else self.length
        self.type_header=type_header
        self.type_end=type_end
        self.type_calls=0
        self.writes=[]
        header=pack(">IIIHH8s",0,self.declared+16,bankno,flags,0,name)
        assert len(header)==24
        self.uc.mem_write(BANK-24,header)
        self.uc.mem_write(BANK,b"\xa5"*self.length)
        self.original_header=bytes(self.uc.mem_read(BANK-24,24))
        self.uc.hook_add(UC_HOOK_MEM_WRITE,self.bank_write,begin=BANK-24,
                         end=BANK+self.length-1)

    def bank_write(self,uc,access,address,size,value,user):
        self.writes.append((address,size))
        assert self.type_calls>=2,"write before memory validation"
        assert BANK-8<=address and address+size<=BANK+self.length,(
            "out of bank bounds",hex(address),size)

    def os_call(self,uc,address,size,user):
        if address != EXEC-534:
            return super().os_call(uc,address,size,user)
        self.type_calls+=1
        address_arg=self.a(1)
        if self.type_calls==1:
            assert address_arg==BANK-24,hex(address_arg)
            typ=4 if self.type_header else 0
        elif self.type_calls==2:
            assert address_arg==BANK+self.length-1,hex(address_arg)
            typ=4 if self.type_end else 0
        else:
            raise AssertionError("unexpected extra TypeOfMem call")
        uc.reg_write(DR[0],typ)
        uc.reg_write(DR[1],0xdeadbeef)
        uc.reg_write(AR[0],0xbad000)
        uc.reg_write(AR[1],0xbad100)
        pc=self.get(self.a(7))
        uc.reg_write(AR[7],self.a(7)+4)
        uc.reg_write(UC_M68K_REG_PC,pc)

    def run(self,n=None,ptr=BANK):
        n=self.count if n is None else n
        for i,r in enumerate(DR):
            self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS,ptr)
        self.uc.reg_write(DR[3],n&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_INDEX],STOP,count=2000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,"stack not restored"
        assert self.a(3)==ARGS+4,"one A3 parameter must be consumed"
        for r,v in saved.items():
            if r in (DR[2],DR[3],AR[3]):
                continue
            assert self.uc.reg_read(r)==v,(r,v,self.uc.reg_read(r))
        assert self.d(2)==0,"AMOS integer D2 result not set"
        return self.d(3)

    def get_native(self):
        return bytes(self.uc.mem_read(BANK-24,24))
    def get_payload(self):
        return bytes(self.uc.mem_read(BANK,self.length))

def run():
    candidate,meta=build()
    assert candidate==build()[0],"non-deterministic builder"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    oldtok,old,_=split(BASE.read_bytes())
    tokens,sections,_=split(candidate)
    assert len(old)==BASE_ENTRIES and len(sections)==BASE_ENTRIES+1
    assert sections[:40]==old[:40]
    assert sections[40]==old[40]+GETP
    assert tokens.startswith(oldtok[:-6])
    assert audit(parse(candidate))["issues"]==[]
    assert len([x for x in audit(parse(candidate))["tokens"]
                if x["name"].startswith("aga ")])==36
    code,labels=emit_init()
    assert sections[ENTRY_INDEX]==code
    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    dis=list(md.disasm(code,0))
    assert sum(x.size for x in dis)==len(code)
    boundaries={x.address for x in dis}
    assert all(x in boundaries for x in labels.values()),labels
    assert not any(x.mnemonic in ("dc.w","illegal","trap") for x in dis)
    assert any("mulu.w" in x.mnemonic for x in dis), "68000 16x16 multiply required"
    trials=0
    for slots in (1,2,3,8,16,32,64,256):
        for chip in (False,True):
            m=BankMachine(candidate,count=slots,flags=3 if chip else 1)
            result=m.run()
            assert result==1,(slots,chip,result)
            assert m.type_calls==2
            assert m.get_native()[:16]==m.original_header[:16]
            assert m.get_native()[16:24]==b"AGAPAL  "
            expected=init_payload(slots)
            assert m.get_payload()==expected,(slots,chip,"payload mismatch")
            assert parse_payload(m.get_payload()).palettes==slots
            assert m.writes and all(0<sz<=8 for addr,sz in m.writes)
            trials+=1

    # Failure is atomic: no name/data bytes may change.
    cases=[
        dict(n=0),dict(n=-1),dict(n=257),dict(n=65536),
        dict(ptr=0),dict(ptr=1),dict(ptr=23),dict(ptr=BANK+1),
        dict(flags=0),dict(flags=2),dict(flags=4),dict(flags=5),
        dict(flags=9),dict(flags=0xffff),
        dict(bankno=0),dict(bankno=1),dict(bankno=4),
        dict(bankno=65536),dict(declared=16+7*776),
        dict(declared=16+9*776),
        dict(type_header=False),dict(type_end=False),
    ]
    for test in cases:
        n=test.get("n",8)
        ptr=test.get("ptr",BANK)
        parameters={k:v for k,v in test.items() if k not in ("n","ptr")}
        m=BankMachine(candidate,**parameters)
        before=m.get_native()+m.get_payload()
        value=m.run(n,ptr)
        assert value==0,(test,value)
        assert m.get_native()+m.get_payload()==before,(
            "failure mutated existing bank",test)
        assert not m.writes,("write on failed init",test)
        trials+=1

    # Re-initializing an already populated bank is a deliberate clear.
    m=BankMachine(candidate,count=8,name=b"AGAPAL  ")
    m.uc.mem_write(BANK,init_payload(8))
    m.uc.mem_write(BANK+80,b"RBG"+b"\xff"*765)
    assert m.run()==1
    assert m.get_payload()==init_payload(8)
    trials+=1
    print("R30 AGAPAL bank init native 68000 Gate A PASS:",trials,
          "cases",flush=True)
    print("R30 candidate:",{k:v for k,v in meta.items()
                           if k!="labels"},flush=True)
    print("Gate B WinUAE / Gate C Compiler / Gate D physical: NOT TESTED")

if __name__=="__main__":
    run()
