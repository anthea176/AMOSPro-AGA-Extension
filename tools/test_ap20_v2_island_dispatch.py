#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 AP20 V2 island dispatch: source and MC68020 CPU Gate A.

Uses actual P0f AP20 commands and original native units. AMOS 365 +B.s
and Compiler relocation are MODELED with Unicorn, NOT run in WinUAE.
This cannot establish Gate B or C, or approve an installed .Lib.
"""
from __future__ import annotations

from struct import pack, unpack_from
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from audit_ap20 import inspect, parse, token
from ap20_v2_island_dispatch import dispatch_islands, pc16_displacements
from build_m19_ap20_islands_in_memory import build

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_A7,
    UC_M68K_REG_A0, UC_M68K_REG_D0, UC_M68K_REG_SR,
)
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

RTS = bytes.fromhex('4e75')


def template():
    return (pack('>5I',0x3f3,0,1,0,0) + pack('>I',0)
            + pack('>I',0x3e9) + pack('>I',0) + pack('>I',0x3f2))


def synthetic(grow=0):
    # Entry 3 has a trailing GetP marker that belongs to entry 4.
    # Native group 8 is initially >32K away from entry 0.
    groups = [DISPATCH_V2 + bytes.fromhex('4e71')*(15000+grow//2) + RTS,
              DISPATCH_V2 + bytes.fromhex('4e71')*3000 + RTS,
              DISPATCH_V2 + bytes.fromhex('4e71')*19000 + RTS]
    parts = [RBSR+pack('>HH',8,0)+RTS, b'',
             RBSR+pack('>HH',6,0)+RTS,
             RBSR+pack('>HH',8,0)+RTS+GETP,
             RBSR+pack('>HH',7,0)+RTS,
             RBSR+pack('>HH',6,0)+RTS] + groups
    tokens = (b'\0\x01\0\0\x80\xff'
              + token('aga alpha',1,2,'I')
              + token('aga beta',1,3,'I')
              + token('aga gamma',1,4,'0')
              + token('aga delta',1,5,'I')
              + b'\0'*6)
    title=b'AP20 synthetic island Gate A\0'
    title += bytes(len(title)&1)
    out=repack_ap20(template(),tokens,parts,title)
    assert inspect(parse(out))['issues']==[]
    return out


def static_tests():
    src=synthetic()
    out,report=dispatch_islands(src)
    _,parts,_=unpack_ap20(out)
    assert all(parts[report.group_map[i]].startswith(DISPATCH_V2)
               for i in (6,7,8))
    assert report.max_pc16<1000
    assert report.group_map[8] < report.group_map[6]
    assert report.entries>report.source_entries
    assert not inspect(parse(out))['issues']
    assert dispatch_islands(src)[0]==out
    for count in (0,2000,5000,10000):
        _,lay=dispatch_islands(synthetic(count))
        assert lay.max_pc16==report.max_pc16
    tok,source_parts,title=unpack_ap20(src)
    for kind in ('odd','wronggroup','oversize','badstub'):
        damaged=list(source_parts)
        if kind=='odd':
            damaged[4]=RBSR+pack('>HH',7,1)+RTS
        elif kind=='wronggroup':
            damaged[4]=RBSR+pack('>HH',5,0)+RTS
        elif kind=='oversize':
            damaged[6]+=b'\x4e\x71'*18000
        else:
            damaged[5]=b'\x4e\x75'+damaged[5][2:]
        broken=repack_ap20(src,tok,damaged,title)
        try:
            dispatch_islands(broken)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid source accepted: '+kind)
    return 8


def cpu():
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    for a,size in ((0x100000,0x100000),(0x300000,0x100000),
                   (0x500000,0x100000),(0x700000,0x100000),
                   (0x900000,0x100000),(0xA00000,0x20000)):
        u.mem_map(a,size)
    return u


def trace_entry(u,entry,target):
    # Stop BEFORE the native function's body executes: this tests only the
    # actual AP20 V2 machine dispatcher and the 32-bit relocation path.
    d0=0x91aabbcc
    a0=0x33445566
    u.reg_write(UC_M68K_REG_D0,d0)
    u.reg_write(UC_M68K_REG_A0,a0)
    u.reg_write(UC_M68K_REG_SR,0x2000)
    u.reg_write(UC_M68K_REG_A7,0xA08000)
    u.mem_write(0xA08000,pack('>I',0xA00100))
    u.emu_start(entry,target,count=250)
    assert u.reg_read(UC_M68K_REG_PC)==target,hex(u.reg_read(UC_M68K_REG_PC))
    assert u.reg_read(UC_M68K_REG_D0)==d0
    assert u.reg_read(UC_M68K_REG_A0)==a0
    assert u.reg_read(UC_M68K_REG_A7)==0xA07ffc


def main():
    checks=static_tests()
    candidate,meta=build()
    assert meta['old_pc16']==32576 and meta['new_pc16']<32000
    assert meta['tokens']==85
    _,parts,_=unpack_ap20(candidate)
    groups={i for i,p in enumerate(parts) if p.startswith(DISPATCH_V2)}
    calls=[i for i,p in enumerate(parts) if p.startswith(RBSR)]
    assert len(groups)==4 and 0 in calls
    cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
    insns=list(cs.disasm(DISPATCH_V2,0))
    assert sum(i.size for i in insns)==len(DISPATCH_V2)
    positions=[]
    pos=0
    for part in parts:
        positions.append(pos)
        pos+=len(part)
    by_group={}
    for i in calls:
        group,_=unpack_from('>HH',parts[i],2)
        by_group.setdefault(group,[]).append(i)
    selected=sorted(set([0]+[ids[0] for ids in by_group.values()]
                        +[ids[-1] for ids in by_group.values()]
                        +calls[::13]))
    u=cpu()
    base=0x100000
    raw=bytearray(b''.join(parts))
    for i,dist in pc16_displacements(parts).items():
        raw[positions[i]:positions[i]+4]=pack('>Hh',0x6100,dist)
    u.mem_write(base,bytes(raw))
    for i in selected:
        group,offset=unpack_from('>HH',parts[i],2)
        target=base+positions[group]+len(DISPATCH_V2)+offset
        trace_entry(u,base+positions[i],target)
        checks+=1
    # The same dispatcher at 4 independent, deliberately distant V2 bases,
    # with compiler-model JSR.L / uint16 offset / RTS in every stub.
    group_bases={g:0x300000+k*0x200000 for k,g in enumerate(sorted(groups))}
    for g,addr in group_bases.items():
        u.mem_write(addr,parts[g])
    for i in selected:
        g,off=unpack_from('>HH',parts[i],2)
        entry=0x101000+i*16
        u.mem_write(entry,bytes.fromhex('4eb9')+pack('>I',group_bases[g])
                    +pack('>H',off)+RTS)
        trace_entry(u,entry,group_bases[g]+len(DISPATCH_V2)+off)
        checks+=1
    print('M19 AP20 V2 DISPATCH ISLANDS MC68020 GATE A PASS',
          checks,'checks; SHA',meta['sha256'],'size',meta['size'],
          'PC16',meta['old_pc16'],'->',meta['new_pc16'],
          '; AMOS/Compiler/OS NOT EXECUTED')


if __name__=='__main__':
    main()
