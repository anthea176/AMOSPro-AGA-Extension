#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 B7/B8 cross-unit trampoline MC68020 Gate A.

Execute the SAME B7-m2 native prefix + local wrappers, plus independent
fifth-unit B8 source at two disjoint addresses. Original B7 AGA Close,
End, Bob reset and frame guard execute in Unicorn MC68020. All OS/graphics
services are mocked. No installation, real WinUAE or Compiler claim.
"""
from __future__ import annotations

from struct import pack
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

from amos_link_test_support import relocate
from build_m19_b8_b7_trampoline_in_memory import build_b8_b7_trampoline
from m19_b8_b7_hook_emit import emit_b8_b7_hooks, R as B7R
from m19_b7m2_close_reset_emit import emit_close_reset
from m19_b8_cross_unit_arm_emit import emit_b8_cross_unit_arm
from m19_b8_safe_lifecycle_emit import emit_b8_safe_lifecycle
from m19_b8_page_manager_emit import R as B8R
from m19_b8_snapshot_pool_emit import R as POOL
from test_m19_b7m2_close_reset_gate_a import CloseResetMachine, active_ids
from test_m19_p0j_pending_close_end_gate_a import ready, DB
from test_m5_generic import DR, AR, AMOS, EXEC, STACK, STOP

SNAP0=0xc10000
SNAP1=0xc20000
NBYTES=16

class Combined(CloseResetMachine):
    def __init__(self, source, layout):
        super().__init__(source,layout)
        self.native,self.labels=emit_b8_b7_hooks()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.labels['routed_paint_all_entry']=self.labels['b8_b7_draw_trampoline_entry']
        self.labels['guarded_close_entry']=self.labels['b8_b7_close_trampoline_entry']
        self.fifth=0xb00000 if layout=='interpreted' else 0xd00000
        self.fifth_source,self.fifth_labels=emit_b8_cross_unit_arm()
        self.uc.mem_write(self.fifth,self.fifth_source)
        self.b8post_calls=0
        self.snapshot_allocs={SNAP0:NBYTES,SNAP1:NBYTES}
        self.b8_frees=[]
        self.uc.hook_add(UC_HOOK_CODE,self._count_post,
                         begin=self.fifth+self.fifth_labels['b8_service_postclose_entry'],
                         end=self.fifth+self.fifth_labels['b8_service_postclose_entry'])

    def _count_post(self,uc,addr,size,unused):
        self.b8post_calls+=1

    def os_call(self,uc,address,size,user):
        if address==EXEC-210:
            pointer=self.a(1);n=self.d(0)
            assert self.snapshot_allocs.get(pointer)==n,('FreeMem',pointer,n)
            del self.snapshot_allocs[pointer]
            self.b8_frees.append((pointer,n))
            return self._os_return(0)
        if address==EXEC-534 and self.fifth<=self.a(1)<self.fifth+len(self.fifth_source):
            return self._os_return(1) # TypeOfMem for separately relocated B8.
        return super().os_call(uc,address,size,user)

    def b7_root(self):
        p=self.entry+self.labels['b8_b7_hook_root']
        return self.get(p+B7R['owner']),self.get(p+B7R['callback'])

    def setup_b8_pool(self):
        root=self.fifth+self.fifth_labels['b8_service_root']
        for offset,value in (
            (B8R['owner'],AMOS),(B8R['screen'],self.screen),
            (B8R['db'],DB),(B8R['epoch'],1)):
            self.put(root+offset,value)
        pool=self.fifth+self.fifth_labels['b8_pool_root']
        for offset,value in (
            (POOL['owner'],AMOS),(POOL['screen'],self.screen),
            (POOL['bitmap0'],0x55000),(POOL['ptr0'],SNAP0),
            (POOL['bytes0'],NBYTES),(POOL['bitmap1'],0x55100),
            (POOL['ptr1'],SNAP1),(POOL['bytes1'],NBYTES)):
            self.put(pool+offset,value)

    def direct(self,addr,*,a0=0,owner=AMOS,maxcount=8_000_000):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x32220+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x43200+i*0x100)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[0],a0)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:self.uc.emu_start(addr,STOP,count=maxcount)
        except Exception as exc:
            raise AssertionError(('trampoline native fault',str(exc),
                 hex(self.uc.reg_read(UC_M68K_REG_PC)),hex(addr))) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        for r,v in before.items():
            if r not in (DR[2],DR[3]):
                assert self.uc.reg_read(r)==v,('AMOS private ABI',r)
        assert self.d(2)==0 and self.d(3) in (0,1)
        return self.d(3)

    def arm(self,owner=AMOS):
        return self.direct(self.fifth+self.fifth_labels['b8_service_arm_b7_entry'],
                           owner=owner)


def main():
    candidate,report=build_b8_b7_trampoline()
    assert len(candidate)==report['size']
    assert report['public_commands']==86 and report['ap20_entries']==182
    assert report['native_groups']==[142,153,156,177,181]
    assert report['pc16_max']<32766 and report['close_stub_index']==179
    assert report['draw_stub_index']==180
    b7old,_=emit_close_reset()
    b7new,b7lab=emit_b8_b7_hooks()
    b8old,_=emit_b8_safe_lifecycle()
    b8new,b8lab=emit_b8_cross_unit_arm()
    assert b7new.startswith(b7old) and b8new.startswith(b8old)
    assert b7new[b7lab['b8_b7_register_magic']:
                 b7lab['b8_b7_register_entry']]==b'B8RG'
    # The magic is DATA not executable; decode the actual suffix sequences.
    for start,end in ((b7lab['b8_b7_draw_trampoline_entry'],b7lab['b8_b7_register_magic']),
                      (b7lab['b8_b7_register_entry'],b7lab['b8_b7_hook_root']),
                      (len(b8old),len(b8new))):
        native=b7new if end<=len(b7new) else b8new
        if start==len(b8old):native=b8new
        ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
                 .disasm(native[start:end],0x10000+start))
        assert ins and sum(i.size for i in ins)==end-start
    cases=0
    for layout in ('interpreted','compiled'):
        # Unbound: original B7 DRAW/CLOSE must behave identically.
        m=ready(layout,cls=Combined,inject_failure=False)
        assert m.b7_root()==(0,0);cases+=1
        assert m.invoke_guard('swap')==1
        m.put(DB+20,0)
        assert m.frame()==1 and m.callbacks()==(m.end_callback(),)*2;cases+=1
        m.invoke_guard('close')
        assert m.get(m.real_state)==0 and m.status()==0;cases+=1
        assert m.b8post_calls==0 and m.b8_frees==[];cases+=1

        # Register only with exact B7 End callback and live pool owner.
        m=ready(layout,cls=Combined,inject_failure=False)
        assert m.arm()==0 and m.b7_root()==(0,0);cases+=1
        m.setup_b8_pool()
        assert m.arm(owner=AMOS+0x100)==0;cases+=1
        assert m.arm()==1;cases+=1
        assert m.b7_root()==(AMOS,
            m.fifth+m.fifth_labels['b8_service_postclose_entry']);cases+=1
        assert m.callbacks()==(m.entry+m.labels['b8_b7_end_trampoline_entry'],)*2
        assert m.invoke_guard('swap')==1
        m.put(DB+20,0)
        assert m.frame()==1;cases+=1
        assert m.callbacks()==(m.entry+m.labels['b8_b7_end_trampoline_entry'],)*2
        assert m.b8post_calls==0 and m.b8_frees==[]
        m.invoke_guard('close')
        assert m.get(m.real_state)==0 and m.status()==0;cases+=1
        assert len(m.b8_frees)==2 and not m.snapshot_allocs;cases+=1
        assert m.b8post_calls==1 and m.b7_root()==(0,0);cases+=1
        assert m.callbacks()==(m.end_callback(),)*2
        m.invoke_guard('close')
        assert m.b8post_calls==1 and len(m.b8_frees)==2;cases+=1
        m.invoke_callback()
        assert m.callbacks()==(m.old_end,)*2;cases+=1
        assert len(m.b8_frees)==2 and m.b8post_calls==1

        # Direct End must retain B7 callback chain and call postclose once.
        n=ready(layout,cls=Combined,inject_failure=False)
        n.setup_b8_pool()
        assert n.arm()==1;cases+=1
        n.invoke_callback()
        assert n.get(n.real_state)==0;cases+=1
        assert n.status()==0 and len(n.b8_frees)==2;cases+=1
        assert n.callbacks()==(n.old_end,)*2 and n.b7_root()==(0,0)
        n.invoke_callback()
        assert len(n.b8_frees)==2 and n.b8post_calls==1;cases+=1

        # Failed Safe/Disp End keeps both pages allocated and re-arms shim.
        p=ready(layout,cls=Combined,inject_failure=True)
        p.setup_b8_pool()
        assert p.arm()==1;cases+=1
        p.invoke_callback()
        assert p.get(p.real_state)==p.screen;cases+=1
        assert len(p.b8_frees)==0 and p.b7_root()[0]==AMOS;cases+=1
        assert p.callbacks()==(p.entry+p.labels['b8_b7_end_trampoline_entry'],)*2
        p.safe_after=p.safe_count+1
        p.disp_after=p.disp_count+2
        p.invoke_callback()
        assert p.get(p.real_state)==0 and len(p.b8_frees)==2;cases+=1
        assert p.b7_root()==(0,0) and p.callbacks()==(p.old_end,)*2;cases+=1

        # Foreign or half-patched End callback cannot register B8.
        f=ready(layout,cls=Combined,inject_failure=False)
        f.setup_b8_pool()
        f.put(AMOS+0x1cc,0x123450)
        assert f.arm()==0 and f.b7_root()==(0,0);cases+=1

    print('M19 B8 B7/5th cross-unit Close/Draw/End MC68020 Gate A PASS',
          cases,'checks in two isolated layouts, B7 native Close/End',
          'and source-checked indirect B8; OS notifications mocked')
    print('AP20_SOURCE_ONLY',report)


if __name__=='__main__':main()
