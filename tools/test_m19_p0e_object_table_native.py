#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e isolated object metadata CPU020 Gate A; no Amiga/AMOS execution.

Exec AttnFlags is emulated; no Blitter, OS allocations, AP20, compiler or WinUAE.
"""
from __future__ import annotations
from struct import pack, unpack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,
)
from m19_p0e_object_table_emit import MAX_OBJECTS,SLOT_BYTES,emit_object_table

DR=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
AR=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
EXEC=0x110000
STOP=0x18000
STACK=0xf0000
OUTPUT=0x510000
OWNER=0x40000
OTHER=0x42000
CANARY=bytes.fromhex('a5d0a5d0')*6


def native_machine(raw,labels,base):
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    uc.mem_map(0,0x1000000)
    uc.mem_write(base,raw)
    uc.mem_write(4,pack('>I',EXEC))
    uc.mem_write(EXEC+0x128,pack('>H',2))
    uc.mem_write(STOP,bytes.fromhex('4e71'))
    uc.mem_write(OUTPUT,CANARY)
    root=base+labels['object_root']
    table=base+labels['object_table']
    assert bytes(uc.mem_read(root,8+MAX_OBJECTS*SLOT_BYTES))==bytes(8+MAX_OBJECTS*SLOT_BYTES)
    return uc,root,table


def invoke(uc,base,labels,which,*,ident=1,bank=10,image=1,x=0,y=0,
           owner=OWNER,output=OUTPUT,limit=500000):
    uc.mem_write(OUTPUT,CANARY)
    for i,r in enumerate(DR):uc.reg_write(r,0x1740+i)
    for i,r in enumerate(AR[:7]):uc.reg_write(r,0x60000+i*256)
    mapping={DR[0]:ident&0xffffffff,DR[1]:bank&0xffffffff,
             DR[4]:image&0xffffffff,DR[5]:x&0xffffffff,
             DR[6]:y&0xffffffff,AR[5]:owner,AR[1]:output}
    for reg,val in mapping.items():uc.reg_write(reg,val)
    before={r:uc.reg_read(r) for r in DR+AR[:7]}
    uc.reg_write(UC_M68K_REG_SR,0x2000)
    uc.reg_write(AR[7],STACK)
    uc.mem_write(STACK,pack('>I',STOP))
    start=base+labels['object_'+which+'_entry']
    try:
        uc.emu_start(start,STOP,count=limit)
    except Exception as exc:
        raise AssertionError(('native object CPU020 fault',which,exc,
                              hex(uc.reg_read(UC_M68K_REG_PC)),ident,owner)) from exc
    assert uc.reg_read(UC_M68K_REG_PC)==STOP
    assert uc.reg_read(AR[7])==STACK+4
    assert uc.reg_read(DR[2])==0
    for r,value in before.items():
        if r not in (DR[2],DR[3]):
            assert uc.reg_read(r)==value,('object ABI clobbered',which,r)
    answer=uc.reg_read(DR[3])
    assert answer in (0,1),('invalid status',answer)
    return answer,bytes(uc.mem_read(OUTPUT,SLOT_BYTES))


def main():
    raw,labels=emit_object_table()
    assert raw==emit_object_table()[0]
    assert labels['object_put_entry']==0
    inst=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
              disasm(raw[:labels['object_root']],0x10000))
    assert sum(i.size for i in inst)==labels['object_root']
    assert all(not i.mnemonic.startswith('dc.') for i in inst)
    cases=0
    for base in (0x10000,0x21000):
        uc,root,table=native_machine(raw,labels,base)
        # No foreign process access; a reset explicitly binds the new owner.
        assert invoke(uc,base,labels,'read')[0]==0;cases+=1
        assert invoke(uc,base,labels,'off')[0]==0;cases+=1
        assert invoke(uc,base,labels,'reset')[0]==1;cases+=1
        assert unpack('>I',uc.mem_read(root,4))[0]==OWNER
        for i in range(1,MAX_OBJECTS+1):
            bank=10 if i%3 else 11
            image=(i%8)+1
            x=i-45;y=123-i
            assert invoke(uc,base,labels,'put',ident=i,bank=bank,
                          image=image,x=x,y=y)[0]==1
            status,record=invoke(uc,base,labels,'read',ident=i)
            assert status==1
            assert unpack('>IIIIII',record)==(bank,image,x&0xffffffff,
                                                y&0xffffffff,1,0)
            cases+=2
        # Different A5 cannot touch previous program's records.
        snapshot=bytes(uc.mem_read(table,MAX_OBJECTS*SLOT_BYTES))
        assert invoke(uc,base,labels,'put',ident=1,owner=OTHER)[0]==0
        assert invoke(uc,base,labels,'off',ident=1,owner=OTHER)[0]==0
        status,record=invoke(uc,base,labels,'read',ident=1,owner=OTHER)
        assert status==0 and record==CANARY
        assert bytes(uc.mem_read(table,MAX_OBJECTS*SLOT_BYTES))==snapshot
        cases+=3
        # Never modify ANY slot on invalid inputs.
        bad=({'ident':0},{'ident':65},{'bank':4},{'bank':65536},
             {'image':0},{'image':4097},{'x':-32769},{'x':32768},
             {'y':-32769},{'y':32768},{'owner':0},{'owner':3})
        for fields in bad:
            assert invoke(uc,base,labels,'put',**fields)[0]==0
            assert bytes(uc.mem_read(table,MAX_OBJECTS*SLOT_BYTES))==snapshot
            cases+=1
        # Off deactivates without losing image/bank identity; repeated Off OK.
        assert invoke(uc,base,labels,'off',ident=17)[0]==1
        assert invoke(uc,base,labels,'off',ident=17)[0]==1
        assert invoke(uc,base,labels,'read',ident=17)[0]==0
        assert unpack('>I',uc.mem_read(table+16*24+16,4))[0]==0
        assert unpack('>I',uc.mem_read(table+16*24,4))[0]==10
        cases+=3
        # Update same Bob number in place, no extra slot allocation.
        assert invoke(uc,base,labels,'put',ident=17,bank=11,image=5,
                      x=-50,y=900)[0]==1
        s,data=invoke(uc,base,labels,'read',ident=17)
        assert s==1 and unpack('>IIIIII',data)==(11,5,(-50)&0xffffffff,900,1,0)
        cases+=2
        assert invoke(uc,base,labels,'read',ident=1,output=0)[0]==0
        assert invoke(uc,base,labels,'read',ident=1,output=OUTPUT+1)[0]==0
        cases+=2
        # CPU preflight failure leaves all state as-is.
        snapshot=bytes(uc.mem_read(root,8+MAX_OBJECTS*SLOT_BYTES))
        uc.mem_write(EXEC+0x128,pack('>H',0))
        assert invoke(uc,base,labels,'put',ident=7)[0]==0
        assert invoke(uc,base,labels,'reset')[0]==0
        assert bytes(uc.mem_read(root,8+MAX_OBJECTS*SLOT_BYTES))==snapshot
        cases+=2
        uc.mem_write(EXEC+0x128,pack('>H',2))
        # Explicit reset does not allocate and permits fresh owner binding.
        assert invoke(uc,base,labels,'reset',owner=OTHER)[0]==1
        assert unpack('>I',uc.mem_read(root,4))[0]==OTHER
        assert bytes(uc.mem_read(table,MAX_OBJECTS*SLOT_BYTES))==bytes(MAX_OBJECTS*SLOT_BYTES)
        assert invoke(uc,base,labels,'put',ident=1,owner=OTHER)[0]==1
        assert invoke(uc,base,labels,'put',ident=1,owner=OWNER)[0]==0
        cases+=3
    print('M19 P0e PRIVATE MC68020 Bob OBJECT TABLE GATE A PASS',
          len(raw),'native bytes,',cases,'cases,',MAX_OBJECTS,'slots;',
          'NO public API / graphics / WinUAE / AMOS Compiler')


if __name__=='__main__':
    main()
