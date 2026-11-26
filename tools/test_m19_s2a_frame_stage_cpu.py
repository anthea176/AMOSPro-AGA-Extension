#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2a detached frame staging: MC68020 CPU, exact P2a layout; no DMA."""
import argparse
from pathlib import Path
from struct import pack
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from m19_s1_agsp_bank import empty_bank, put_capture
from test_m19_s1p2a_chip_prepare_cpu import expected

CODE, STOP, STACK, LIVE, SOURCE = 0x20000, 0x30000, 0xb0000, 0x100000, 0x140000
REGS=(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,
      UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,
      UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)

def fixture(height,active=0):
    cmap=bytes.fromhex('000000ff462424dc751a73ff')
    first=bytes((x+y)%4 for y in range(height) for x in range(16))
    second=bytes((x if x<4 else (3*x+y+1))%4
                 for y in range(height) for x in range(16))
    payload=put_capture(empty_bank(),1,first,16,height,0,0,16,height,cmap,0)
    payload=put_capture(payload,2,second,16,height,0,0,16,height,cmap,0)
    live=bytearray(expected(payload,1))
    source=expected(payload,2)
    frame=8+4*height
    # Same data allocation as P2m, stable descriptor at LIVE.
    # Simulate the current slot; the alternate slot is safe by test premise.
    live[0:4]=pack('>I',LIVE+48+active*frame)
    live[6:10]=pack('>HH',32,16)
    live[10:12]=pack('>H',2)
    data=bytes(live[48:48+frame])
    live[48:]=bytes([0xa5])*(frame*2)
    live[48+active*frame:48+(active+1)*frame]=data
    assert data[4:-4]!=source[52:48+frame-4]
    return bytes(live),source,LIVE+48+(1-active)*frame,frame

def run(code,live,source,spare,frame,ok=True,*,a0=LIVE,a1=SOURCE,n0=None,n1=None):
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    uc.mem_map(0,0x200000)
    uc.mem_write(CODE,code)
    uc.mem_write(LIVE-16,bytes([0x5a])*(len(live)+32))
    uc.mem_write(SOURCE-16,bytes([0x6b])*(len(source)+32))
    uc.mem_write(LIVE,live)
    uc.mem_write(SOURCE,source)
    writes=[]
    def on_write(u,access,address,size,value,user):
        if STACK-4096<=address and address+size<=STACK+4:
            return
        assert ok and spare<=address and address+size<=spare+frame, (
            'unexpected nonstack write',hex(address),size)
        writes.append((address,size))
    uc.hook_add(UC_HOOK_MEM_WRITE,on_write)
    uc.reg_write(UC_M68K_REG_SR,0x2000)
    for i,reg in enumerate(REGS):uc.reg_write(reg,0x55001000+i)
    uc.reg_write(UC_M68K_REG_A0,a0)
    uc.reg_write(UC_M68K_REG_A1,a1)
    uc.reg_write(UC_M68K_REG_D2,spare)
    saved={reg:uc.reg_read(reg) for reg in REGS}
    uc.reg_write(UC_M68K_REG_D0,len(live) if n0 is None else n0)
    uc.reg_write(UC_M68K_REG_D1,len(source) if n1 is None else n1)
    uc.reg_write(UC_M68K_REG_A7,STACK)
    uc.mem_write(STACK,pack('>I',STOP))
    uc.emu_start(CODE,STOP,count=100000)
    assert uc.reg_read(UC_M68K_REG_PC)==STOP
    assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
    assert all(uc.reg_read(reg)==v for reg,v in saved.items())
    result=(uc.reg_read(UC_M68K_REG_D0),uc.reg_read(UC_M68K_REG_D1))
    want=bytearray(live)
    if ok:
        assert result==(spare,frame)
        offset=spare-LIVE
        want[offset:offset+frame]=source[48:48+frame]
        # Every byte of the alternate slot must have been written once.
        assert writes==[(spare+off,4) for off in range(0,frame,4)]
    else:
        assert result==(0,0) and not writes
    assert bytes(uc.mem_read(LIVE,len(live)))==bytes(want)
    assert bytes(uc.mem_read(SOURCE,len(source)))==source
    for addr,count,marker in ((LIVE-16,16,0x5a),(LIVE+len(live),16,0x5a),
                              (SOURCE-16,16,0x6b),(SOURCE+len(source),16,0x6b)):
        assert bytes(uc.mem_read(addr,count))==bytes([marker])*count
    return bytes(want)

def mutate(data,offset,value):
    result=bytearray(data)
    result[offset:offset+len(value)]=value
    assert result!=data
    return bytes(result)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('native',type=Path)
    code=ap.parse_args().native.read_bytes()
    cases=0
    for h in (1,16,255,256):
        for active in (0,1):
            run(code,*fixture(h,active));cases+=1
    live,source,spare,frame=fixture(16)
    # Alternating slots with a simulated, external retirement receipt.
    # This tests the staging ABI and bounds only, not the OS handoff.
    for i in range(100):
        old=live
        live=run(code,live,source,spare,frame)
        # Detached copy of the previous frame for the next stage.
        previous=int.from_bytes(old[:4],'big')
        copy=bytearray(source)
        copy[48:48+frame]=old[previous-LIVE:previous-LIVE+frame]
        source=bytes(copy)
        live=live[:0]+pack('>I',spare)+live[4:]
        spare=previous
        cases+=1
    live,source,spare,frame=fixture(16)
    for kwargs in (dict(a0=0),dict(a1=0),dict(a0=LIVE+1),
                   dict(a1=SOURCE+1),dict(a1=LIVE),dict(a0=0xfffffff0),
                   dict(a1=0xfffffff0),dict(n0=len(live)-2),
                   dict(n1=len(source)+2),dict(n0=70,n1=70),
                   dict(n0=2114,n1=2114)):
        run(code,live,source,spare,frame,False,**kwargs);cases+=1
    for bad in (0,LIVE+48,spare+2,SOURCE+48):
        run(code,live,source,bad,frame,False);cases+=1
    for off,value in ((0,pack('>I',LIVE+50)),(4,pack('>H',0)),
                      (10,pack('>H',3)),(12,pack('>I',len(live)-4)),
                      (18,pack('>H',4)),(20,pack('>I',0)),
                      (24,pack('>I',1)),(40,pack('>I',46)),
                      (44,pack('>I',spare-LIVE+4))):
        run(code,mutate(live,off,value),source,spare,frame,False);cases+=1
    for off,value in ((0,pack('>I',SOURCE+48)),(4,pack('>H',17)),
                      (6,pack('>I',1)),(10,pack('>H',2)),
                      (12,pack('>I',len(source)+4)),(16,pack('>H',0)),
                      (18,pack('>H',2)),(20,pack('>I',1)),
                      (24,pack('>I',1)),(28,bytes.fromhex('ff')),
                      (32,bytes.fromhex('ff')),(36,bytes.fromhex('ff')),
                      (40,pack('>I',50)),(44,pack('>I',50)),
                      (48,pack('>I',1)),(48+frame-4,pack('>I',1))):
        run(code,live,mutate(source,off,value),spare,frame,False);cases+=1
    print('S2A_STAGE_CPU_PASS',cases,'cases; no OS/DMA/publication test')

if __name__=='__main__':
    main()
