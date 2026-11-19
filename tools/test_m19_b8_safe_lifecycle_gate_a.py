#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Native B8 Safe/GetMsg/WaitBlit + after-close private lifecycle Gate A.

Unicorn executes emitted MC68020 at two placements. Exec/graphics and the
completion of the original B7-m2 Close/End are MODELED, not real WinUAE.
The original B7-m2 callback and public AP20 stubs are not modified.
"""
from __future__ import annotations

from struct import pack
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from m19_b8_safe_lifecycle_emit import emit_b8_safe_lifecycle
from m19_b8_page_manager_emit import emit_b8_page_manager, R as ROOT
from test_m19_b8_page_manager_gate_a import (
    Machine, DR, AR, EXEC, DB, STATE, SCREEN, OWNER, OTHER, BMP0, BMP1,
    BPR, ROWS, PAGE_SIZE, PLANE10, PLANE11
)

GRAPHICS = 0x170000
SAFEPORT = 0x171000
SAFEMSG = 0x171080

class SafeMachine(Machine):
    def __init__(self, code, labels, base):
        self.safe_available=False
        self.getmsg_count=0
        self.waitblit_count=0
        super().__init__(code,labels,base)
        self.put(STATE+8,GRAPHICS)
        self.put(DB+12,SAFEPORT)
        self.regions.extend([(GRAPHICS,GRAPHICS+0x200),
                             (SAFEPORT,SAFEPORT+64), (SAFEMSG,SAFEMSG+64)])
        self.uc.hook_add(UC_HOOK_CODE,self.wait_blit,
                         begin=GRAPHICS-228,end=GRAPHICS-228)

    def os_call(self, uc, addr, size, ctx):
        if addr!=EXEC-372:
            return super().os_call(uc,addr,size,ctx)
        self.getmsg_count+=1
        assert uc.reg_read(AR[0]) == SAFEPORT
        ret=int.from_bytes(uc.mem_read(uc.reg_read(AR[7]),4),'big')
        result=SAFEMSG if self.safe_available else 0
        self.safe_available=False  # A notification may be consumed only once.
        sp=uc.reg_read(AR[7]);uc.reg_write(AR[7],sp+4)
        uc.reg_write(DR[0],result)
        uc.reg_write(DR[1],0x87654321)
        uc.reg_write(AR[0],0xbadd0000)
        uc.reg_write(AR[1],0xbadd0001)
        uc.reg_write(UC_M68K_REG_PC,ret)

    def wait_blit(self, uc, addr, size, ctx):
        assert uc.reg_read(AR[6]) == GRAPHICS
        assert not (self.get(DB+20)&1), 'WaitBlit before Safe delivered'
        self.waitblit_count+=1
        sp=uc.reg_read(AR[7])
        ret=int.from_bytes(uc.mem_read(sp,4),'big')
        uc.reg_write(AR[7],sp+4)
        uc.reg_write(DR[0],0xbeef1234)
        uc.reg_write(DR[1],0xbeef1235)
        uc.reg_write(AR[0],0xbadcafe0)
        uc.reg_write(AR[1],0xbadcafe1)
        uc.reg_write(UC_M68K_REG_PC,ret)

    def get(self, addr):
        return int.from_bytes(self.uc.mem_read(addr,4),'big')

    def call(self, op, owner=OWNER):
        assert ('b8_service_'+op+'_entry') in self.labels, op
        return super().call(op,owner=owner)


def main():
    raw,labels=emit_b8_safe_lifecycle()
    old,_=emit_b8_page_manager()
    assert raw.startswith(old) and len(raw)>len(old)
    for name in ('safe_acquire','safe_capture','safe_restore','postclose'):
        assert labels['b8_service_'+name+'_entry'] >= len(old)
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(raw[len(old):],0x10000))
    assert sum(x.size for x in ins)==len(raw)-len(old)
    cases=0
    for base in (0x20000,0x31000):
        m=SafeMachine(raw,labels,base)
        front=m.page(0);back=m.page(1)
        assert m.call('safe_capture')==0;cases+=1
        assert not m.getmsg_count and not m.waitblit_count
        assert m.call('bind')==1;cases+=1
        assert m.call('postclose')==0;cases+=1
        assert m.root()[ROOT['valid']//4]==0 and not m.free_calls
        assert m.call('safe_capture',owner=OTHER)==0;cases+=1
        assert not m.getmsg_count and not m.waitblit_count
        m.put(DB+20,3)  # Pending Safe AND Disp.
        assert m.call('safe_capture')==0;cases+=1
        assert m.get(DB+20)==3 and m.getmsg_count==1
        assert m.waitblit_count==0 and m.page(0)==front and m.page(1)==back
        m.safe_available=True
        assert m.call('safe_capture')==1;cases+=1
        assert m.getmsg_count==2 and m.waitblit_count==1
        assert m.get(DB+20)==2, 'Disp must not be consumed by Bob save'
        assert bytes(m.uc.mem_read(0xb0000,PAGE_SIZE))==back
        assert m.root()[ROOT['valid']//4]==2
        assert m.page(0)==front
        m.rewrite_page(1,0xee)
        assert m.call('safe_restore')==1;cases+=1
        assert m.page(1)==back and m.page(0)==front
        assert m.getmsg_count==2 and m.waitblit_count==2
        m.put(DB+8,1)
        assert m.call('safe_capture')==1;cases+=1
        assert m.root()[ROOT['valid']//4]==3
        assert bytes(m.uc.mem_read(0x80000,PAGE_SIZE))==front
        m.rewrite_page(0,0xff)
        assert m.call('safe_restore')==1;cases+=1
        assert m.page(0)==front and m.page(1)==back
        assert m.call('postclose')==0 and not m.free_calls;cases+=1
        m.put(STATE,0)  # Simulate a COMPLETED original native Close/End.
        assert m.call('postclose',owner=OTHER)==0;cases+=1
        assert not m.free_calls
        assert m.call('postclose')==1;cases+=1
        assert len(m.free_calls)==2 and not m.allocations
        assert m.call('postclose')==1 and len(m.free_calls)==2;cases+=1
        # Reopen modeled at same OS addresses, owner still the same.
        m.put(STATE,SCREEN)
        m.next_alloc=0
        assert m.call('bind')==1;cases+=1
        assert m.root()[ROOT['valid']//4]==0
        assert m.call('safe_restore')==0;cases+=1
        assert m.call('close')==1
        assert len(m.free_calls)==4
        # SafePort absent: never call GetMsg with an invalid port.
        t=SafeMachine(raw,labels,base)
        assert t.call('bind')==1
        t.put(DB+20,1);t.put(DB+12,0)
        assert t.call('safe_capture')==0;cases+=1
        assert t.get(DB+20)==1 and t.getmsg_count==0
        assert t.waitblit_count==0
        # Missing graphics.library must fail before consuming a message.
        t=SafeMachine(raw,labels,base)
        assert t.call('bind')==1
        t.put(STATE+8,0);t.put(DB+20,1);t.safe_available=True
        assert t.call('safe_capture')==0;cases+=1
        assert t.getmsg_count==0 and t.get(DB+20)==1
        # No actual Close/End: postclose cannot deallocate even when Safe.
        t=SafeMachine(raw,labels,base)
        assert t.call('bind')==1
        assert t.call('postclose')==0 and not t.free_calls;cases+=1
    print('M19 B8 MC68020 Safe/WaitBlit/post-Close Gate A PASS',cases,
          'cases, 2 relocations; Exec, graphics, Close/End MODELED')

if __name__=='__main__':
    main()
