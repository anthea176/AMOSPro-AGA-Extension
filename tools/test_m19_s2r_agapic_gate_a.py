#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exercise moved public AGAPIC Info/Capture through real new V2 stubs.

Use the established R84 mock OS/bank service and pixel oracle, but a fresh
explicit MC68020 Unicorn fixture and the exact source-built candidate bytes.
The two layouts model Runtime BSR.W and separately placed Compiler JSR.L.
"""
from collections import deque
from struct import pack, unpack_from
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import UC_CPU_M68K_M68020, UC_M68K_REG_SR, UC_M68K_REG_PC
from audit_ap20 import walk_tokens
from compiler_relocation import unpack_ap20, RBSR
from amos_link_test_support import main_table, relocate
from amos_main_abi import declarations
from test_r84_agapic_capture_native import CaptureV2Machine, compare, MODE, COLORMAP
from test_m16_capture import MAIN_BASE, BANK_NEW
from test_m16_image_draw_r45 import ARGS, BANK, SAFE_PORT, SAFE_MSG
from test_m5_generic import EXEC, GFX, SCREEN, STATE, DB, SB, BITMAP, AMOS, DR, AR, STACK, STOP
from m16_agapic_v2 import parse_payload_any

class Relocated(CaptureV2Machine):
    def __init__(self,image,layout,depth=4,pending=0,safe_ready=True,alloc_fail=False,occupied=False):
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x1000000)
        self.uc.mem_write(STOP,b'\x4e\x71')
        self.meta=dict(width=80,height=48,depth=depth)
        self.stride=18
        self.plane_size=self.stride*48
        self.planes=[0x600000+i*0x80000 for i in range(depth)]
        for i,p in enumerate(self.planes):
            self.uc.mem_write(p,bytes((17*i+23*n)&255 for n in range(self.plane_size)))
        self.put(4,EXEC)
        self.put(AMOS+456,STATE)
        for off,value in ((0,SCREEN),(8,GFX),(12,80),(16,48),(20,1<<depth),
                          (24,MODE),(28,depth),(32,DB)):
            self.put(STATE+off,value)
        self.put(DB,SB)
        self.put(DB+4,SB)
        self.put(DB+8,0)
        self.put(DB+12,SAFE_PORT)
        self.put(DB+20,pending)
        self.put(SB,BITMAP)
        self.uc.mem_write(BITMAP,pack('>HHBBH',self.stride,48,0,depth,0))
        for i,p in enumerate(self.planes):self.put(BITMAP+8+4*i,p)
        self.put(SCREEN+48,COLORMAP)
        self.uc.mem_write(COLORMAP+2,pack('>H',1<<depth))
        self.modeid=MODE
        self.palette=bytes((i*11+7)&255 for i in range(3*(1<<depth)))
        self.rgb_calls=self.mode_calls=0
        self.pending_safe=pending
        self.safe_ready=safe_ready
        self.alloc_fail=alloc_fail
        self.reserve_fail=self.reserve_overflow=self.late_collision=False
        self.alloc_count=self.free_count=self.reserve_count=self.change_count=self.erase_count=0
        self.type_calls=self.getmsg_calls=0
        self.os_calls=[]
        self.buffers={}
        self.banks={}
        if occupied:
            self.banks[11]=BANK
            self.put(BANK-20,16+8)
            self.put(BANK-16,11)
            self.uc.mem_write(BANK-12,b'\x00\x01\x00\x00FOREIGN ')
            self.uc.mem_write(BANK,b'FOREIGN!')
        self.main_calls=[]
        self.trace=deque(maxlen=28)
        table,names=main_table(self.uc)
        self.target_names={addr:names[idx] for idx,addr in table.items()}
        self.bank_targets={table[idx]:name for idx,name,*_ in declarations()
                           if name in ('Bnk.GetAdr','Bnk.Reserve','Bnk.Eff','Bnk.Change')}
        for addr in self.bank_targets:self.uc.mem_write(addr,b'\x4e\x75')
        self.uc.hook_add(UC_HOOK_CODE,self.main_call,begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        for addr in (EXEC-684,EXEC-690,EXEC-534,EXEC-372,GFX-792,GFX-900):
            self.uc.mem_write(addr,b'\x4e\x75')
            self.uc.hook_add(UC_HOOK_CODE,self.os_call,begin=addr,end=addr)
        tok,parts,_=unpack_ap20(image)
        rows={r['name']:r for r in walk_tokens(tok)}
        names=('aga bank image info','aga bank image capture')
        indices=[rows[n]['function'] for n in names]
        group=unpack_from('>H',parts[indices[0]],2)[0]
        if layout=='runtime':
            starts=[]
            pc=0x180000
            for p in parts:
                starts.append(pc)
                pc+=len(p)
            base=starts[group]
        else:
            base=0x380000
        self.uc.mem_write(base,relocate(parts[group],base,{},self.uc))
        for i,index in enumerate(indices):
            stub=parts[index]
            assert stub[:2]==RBSR and unpack_from('>H',stub,2)[0]==group
            if layout=='runtime':
                pc=starts[index]
                code=pack('>Hh',0x6100,base-(pc+2))+stub[4:]
            else:
                pc=0x180000+i*0x20
                code=pack('>HIH',0x4eb9,base,unpack_from('>H',stub,4)[0])+b'\x4e\x75'
            self.uc.mem_write(pc,code)
            if i==0:self.info_entry=pc
            else:self.entry=pc
        self.uc.hook_add(UC_HOOK_CODE,self.debug_hook,begin=base,end=base+len(parts[group])-1)
    def os_call(self,uc,address,size,user):
        if address==EXEC-534:
            p=self.a(1)
            valid=any(ptr-24<=p<ptr+self.get(ptr-20)-16 for ptr in self.banks.values())
            self._ret(int(valid))
            return
        if address==EXEC-372:
            assert self.a(0)==SAFE_PORT
            self._ret(SAFE_MSG if self.safe_ready else 0)
            return
        return super().os_call(uc,address,size,user)
    def image_info(self,field,bank=11):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS,bank)
        self.uc.reg_write(DR[3],field&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(self.info_entry,STOP,count=500000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP and self.a(7)==STACK+4
        assert self.a(3)==ARGS+4 and self.d(2)==0
        assert all(self.uc.reg_read(r)==v for r,v in saved.items() if r not in (DR[2],DR[3],AR[3]))
        return self.d(3)

def cases(image,layout):
    count=0
    for depth in (1,4,8):
        for version in (1,2):
            for index in (-1,0,(1<<depth)-1):
                m=Relocated(image,layout,depth)
                ok,before=m.capture(version=version,index=index)
                assert ok==1
                compare(m,before,version=version,index=index)
                ptr=m.banks[11]
                raw=bytes(m.uc.mem_read(ptr,m.get(ptr-20)-16))
                expected=(19,9,depth,0 if version==1 else 1<<depth,0 if version==1 else MODE)
                for field,want in enumerate(expected,1):
                    assert m.image_info(field)==want
                    count+=1
                for field in (0,6,-1):
                    assert m.image_info(field)==0xffffffff
                    count+=1
                assert m.image_info(1,bank=12)==0xffffffff
                assert bytes(m.uc.mem_read(ptr,len(raw)))==raw
                assert parse_payload_any(raw).version==version
                count+=2
    for version in (1,2):
        for kw in (dict(x=-1),dict(w=0),dict(x=79,w=2),dict(index=-2),dict(bank=4)):
            m=Relocated(image,layout)
            ok,_=m.capture(version=version,**kw)
            assert ok==0 and not m.banks and not m.reserve_count
            count+=1
        for cfg in (dict(alloc_fail=True),dict(pending=1,safe_ready=False),dict(occupied=True)):
            m=Relocated(image,layout,**cfg)
            ok,_=m.capture(version=version)
            assert ok==0 and not m.reserve_count and m.alloc_count==m.free_count+(1 if cfg.get('alloc_fail') else 0)
            if cfg.get('occupied'):
                assert m.banks[11]==BANK and bytes(m.uc.mem_read(BANK,8))==b'FOREIGN!'
            count+=1
    print('S2R_AGAPIC_PUBLIC_PASS',layout,count,flush=True)
