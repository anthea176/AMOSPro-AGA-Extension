#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Real Unicorn MC68020 CPU test for a private BitMap backing-store copy.

Not a public AMOS Clear/Update command. Screen Safe/Disp, Exec ranges and
native OS allocation are mocked. Verifies ABI, plane bytes and refusal.
"""
from __future__ import annotations

from struct import pack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,
)
from m19_b8_planar_snapshot_emit import emit_planar_snapshot_core

DR=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
AR=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
EXEC=0x110000
STOP=0x18000
STACK=0xf0000
BITMAP=0x50000
SNAP=0x80000
OWNER=0x30000
PLANES=[0x60000 + 0x1000*i for i in range(8)]


class Machine:
    def __init__(self, src, base, *, depth=2, bpr=4, rows=2,
                 flags=2, invalid_plane=-1, snapshot=SNAP):
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x1000000)
        self.uc.mem_write(base,src)
        self.uc.mem_write(4,pack('>I',EXEC))
        self.uc.mem_write(EXEC+0x128,pack('>H',flags))
        self.uc.mem_write(STOP,bytes.fromhex('4e71'))
        self.uc.mem_write(EXEC-534,bytes.fromhex('4e75'))
        self.base=base
        self.bitmap=BITMAP
        self.snapshot=snapshot
        self.depth=depth
        self.bpr=bpr
        self.rows=rows
        self.bytecount=bpr*rows
        self.total=self.bytecount*depth
        self.regions=[(BITMAP,BITMAP+40),(SNAP,SNAP+0x1000)]
        self.plane_bytes=[]
        pointers=[]
        for i,addr in enumerate(PLANES):
            pointer=addr+1 if i==invalid_plane else addr
            pointers.append(pointer)
            payload=bytes((19*i + 3*j+1)&255 for j in range(self.bytecount))
            self.plane_bytes.append(payload)
            self.uc.mem_write(addr,payload)
            self.regions.append((addr,addr+self.bytecount))
        self.uc.mem_write(BITMAP,pack('>HHBBH',bpr,rows,0,depth,0)
                          +b''.join(pack('>I',p) for p in pointers))
        self.uc.mem_write(SNAP,b'\xee'*0x1000)
        self.calls=0
        self.uc.hook_add(UC_HOOK_CODE,self.os_call,
                         begin=EXEC-534,end=EXEC-534)

    def os_call(self,uc,address,size,user):
        if address!=EXEC-534: raise AssertionError(hex(address))
        self.calls+=1
        ptr=uc.reg_read(AR[1])
        ok=int(any(a<=ptr<b for a,b in self.regions))
        sp=uc.reg_read(AR[7])
        ret=int.from_bytes(uc.mem_read(sp,4),'big')
        uc.reg_write(AR[7],sp+4)
        uc.reg_write(DR[0],ok)
        uc.reg_write(DR[1],0xabc12345)
        uc.reg_write(AR[0],0xdecafbad)
        uc.reg_write(AR[1],0xabcd9876)
        uc.reg_write(UC_M68K_REG_PC,ret)

    def call(self,*,mode=0,capacity=None,bitmap=BITMAP,snapshot=None,limit=4000000):
        if capacity is None:capacity=self.total
        if snapshot is None:snapshot=self.snapshot
        uc=self.uc
        for i,r in enumerate(DR): uc.reg_write(r,0x123000+i)
        for i,r in enumerate(AR[:7]): uc.reg_write(r,0x340000+i*0x100)
        uc.reg_write(DR[0],capacity)
        uc.reg_write(DR[1],mode)
        uc.reg_write(AR[0],bitmap)
        uc.reg_write(AR[1],snapshot)
        uc.reg_write(AR[5],OWNER)
        before={r:uc.reg_read(r) for r in DR+AR[:7]}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK)
        uc.mem_write(STACK,pack('>I',STOP))
        try:uc.emu_start(self.base,STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('native CPU fault',exc,
                hex(uc.reg_read(UC_M68K_REG_PC)),self.calls)) from exc
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(AR[7])==STACK+4
        assert uc.reg_read(DR[2])==0
        for r,value in before.items():
            if r not in (DR[2],DR[3]):
                assert uc.reg_read(r)==value,('ABI broken',r)
        result=uc.reg_read(DR[3])
        assert result in (0,1)
        return result


def main():
    code,labels=emit_planar_snapshot_core()
    assert code==emit_planar_snapshot_core()[0]
    assert labels['b8_planar_snapshot_core_entry']==0
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(code,0x10000))
    assert sum(x.size for x in ins)==len(code)
    assert all(not x.mnemonic.startswith('dc.') for x in ins)
    cases=0
    for base in (0x20000,0x32000):
        for depth in (1,2,4,8):
            m=Machine(code,base,depth=depth)
            expected=b''.join(m.plane_bytes[:depth])
            assert m.call(mode=0)==1
            assert bytes(m.uc.mem_read(SNAP,len(expected)))==expected
            cases+=1
            for i in range(depth):m.uc.mem_write(PLANES[i],b'\xff'*m.bytecount)
            assert m.call(mode=1)==1
            assert b''.join(bytes(m.uc.mem_read(p,m.bytecount)) for p in PLANES[:depth])==expected
            cases+=1
        for kwargs in (dict(flags=0),dict(depth=9),dict(bpr=3),dict(invalid_plane=1)):
            m=Machine(code,base,**kwargs)
            original=bytes(m.uc.mem_read(SNAP,0x100))
            assert m.call()==0
            assert bytes(m.uc.mem_read(SNAP,0x100))==original
            cases+=1
        m=Machine(code,base)
        assert m.call(mode=2)==0;cases+=1
        assert m.call(capacity=m.total-1)==0;cases+=1
        assert m.call(snapshot=0)==0;cases+=1
        assert m.call(bitmap=0)==0;cases+=1
        assert m.call(snapshot=SNAP+1)==0;cases+=1
        m.regions=[r for r in m.regions if r[0]!=SNAP]+[(SNAP,SNAP+4)]
        assert m.call()==0;cases+=1
    print('M19 B8 planar snapshot REAL MC68020 Gate A PASS',cases,
          'independent CPU cases, two relocatable placements;',
          'OS TypeOfMem mocked, NO public AMOS token, NO WinUAE/Compiler')


if __name__=='__main__':main()
