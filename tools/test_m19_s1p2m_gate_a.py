#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Functional S1-P2m Gate A; MC68020 AP20 routes, modeled OS, not DMA proof."""
import argparse, json, os, unittest
from pathlib import Path
from unicorn.m68k_const import *
from build_m19_s1p2m_in_memory import build_s1p2m, protected
from test_m19_s1p2k_gate_a import TransactionMachine
from test_m19_s1p2i_gate_a import SpriteMachine, CI, INTUI, STATE, TASK
from test_m19_s1p2j_gate_a import FAST_TABLE
from test_m19_s1p1c_amos_bank_commit import EXEC
from test_m19_s1p1c_pipeline import GFX, SCREEN
from test_m19_s1p1i_l2b_integration_gate_a import chain
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases, verify_linked_source
from test_m19_p2d_l1_safeport_gate_a import run_cases
import test_m19_p2d_l2_first_bind_gate_a as l2_gate

class LifecycleMachine(TransactionMachine):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.published=set()
        self.released_at={}
        self.records={}
        self.freed_chip=set()
        self.late_at=None

    def on_code(self,uc,address,size,user):
        a0=uc.reg_read(UC_M68K_REG_A0)
        a1=uc.reg_read(UC_M68K_REG_A1)
        a2=uc.reg_read(UC_M68K_REG_A2)
        d0=uc.reg_read(UC_M68K_REG_D0)
        if address==EXEC-690 and a1 in self.ever:
            assert a1 in self.released_at
            if a1 in self.published:
                assert self.tofs-self.released_at[a1]>=2,'free before two frame boundaries'
                assert self.get(FAST_TABLE+8)==self.get(FAST_TABLE+12)==0
                for ch in (2,3):
                    assert (self.word(CI+90+8*ch)<<16 | self.word(CI+94+8*ch))==CI+176
            assert not self.read(GFX+166,1)[0]&4
            assert self.get(self.named+56)==0
            self.ever.remove(a1)
            self.freed_chip.add(a1)
            # Bypass only historical blanket prohibition on exposed FreeVec.
            return SpriteMachine.on_code(self,uc,address,size,user)
        if address==EXEC-690 and a1 in self.records:
            assert self.records[a1] in self.freed_chip
        if address==GFX-420:
            assert a2==a1+48,'private blank publication is no longer used'
            self.published.add(a1)
        result=super().on_code(uc,address,size,user)
        if address==GFX-408 and d0==2 and uc.reg_read(UC_M68K_REG_D0)&65535==2:
            self.records[self.get(self.named+56)]=a0
        if address==GFX-414 and d0==2:
            for chip in self.ever:
                self.released_at[chip]=self.tofs
        if address==GFX-270 and self.late_at==self.tofs:
            self.copper(2,next(iter(self.ever))+48)
        return result

    def reopen(self):
        assert self.get(STATE)==0 and not self.db
        for off,value in ((0,SCREEN),(4,INTUI),(8,GFX),(12,320),(16,256),(20,256),(28,8),(32,0),(36,0)):
            self.put32(STATE+off,value)
        self.put32(GFX+34,0x96000)
        self.put32(GFX+50,0x97000)
        self.put32(GFX+54,0x98000)
        self.put32(CI+164,0x12345678)
        assert self.select(29)==1

    def clear_refs(self):
        for ch in (2,3):
            self.put32(FAST_TABLE+ch*4,0)
            self.copper(ch,CI+176)

    def no_sprite(self):
        self.empty()
        assert not self.ever
        assert self.read(GFX+166,1)[0]&12==0
        assert self.get(FAST_TABLE+8)==self.get(FAST_TABLE+12)==0

def functional_cases(image,info,layouts=('runtime','compiled')):
    for layout in layouts:
        def new(db=False):
            m=LifecycleMachine(image,info,layout,db)
            assert m.select(29)==1
            return m
        m=new()
        m.pending_view=True
        m.put32(CI+164,0)
        count=0
        for screen in range(10):
            if screen:m.reopen()
            before=dict(m.allocations)
            for cycle in range(10):
                assert m.sprite()==1
                assert m.sprite(x=40+cycle*2)==1
                assert m.off()==1 and m.off()==1
                m.no_sprite()
                assert m.allocations==before
                count+=1
            assert m.sprite()==1
            m.close(end=bool(screen&1))
            assert m.get(STATE)==0
            assert m.bankfree()==1
            m.no_sprite()
            assert m.allocations==before
            assert m.bank(29)==m.payload
        assert count==100 and len(m.freed_chip)==110
        print('S1P2M_100_CYCLES_10_CLOSES_PASS',layout,count,flush=True)
        for end in (False,True):
            m=new(True);assert m.sprite()==1
            m.erase()
            for x in range(34,234,2):assert m.sprite(x=x)==1
            m.close(end);assert m.get(STATE)==0
            assert m.bankfree()==1;m.no_sprite()
            m=new(True);assert m.sprite()==1
            m.block_replies=True
            m.close(end)
            assert m.get(STATE)!=0 and m.get(m.cell)!=0
            assert m.get(m.get(m.named+56)+12)==20
            assert not m.freed_chip
            m.block_replies=False
            m.close(end);assert m.get(STATE)==0;m.no_sprite()
        m=new();assert m.sprite()==1
        m.close_ok=False;m.close()
        assert m.get(STATE)==SCREEN and m.named and not m.freed_chip
        m.close_ok=True;m.close()
        assert m.get(STATE)==0;m.no_sprite()
        m=new();assert m.sprite()==1;m.keep_refs=True
        assert m.off()==0;m.held()
        assert m.sprite()==-140
        m.close();assert m.get(STATE)==0 and not m.get(m.cell)
        m.held();assert m.bankfree()==0
        m.keep_refs=False;m.clear_refs()
        assert m.bankfree()==1;m.no_sprite()
        m=new();assert m.sprite()==1;m.late_at=m.tofs+2
        assert m.off()==0;m.held()
        m.late_at=None;m.clear_refs()
        assert m.off()==1;m.no_sprite()
        for address,value in ((GFX+208,1),(GFX+38,1)):
            m=new();assert m.sprite()==1
            saved=m.get(address);m.put32(address,value)
            assert m.off()==0;m.held()
            m.put32(address,saved);m.clear_refs()
            assert m.off()==1;m.no_sprite()
        for failure,expected in ((1,-134),(2,-124),(3,-126)):
            m=new();m.fail_temp_at=failure
            assert m.sprite()==expected;m.no_sprite()
        for ch,expected in ((2,-141),(3,-142)):
            m=new();m.reject_channel=ch
            assert m.sprite()==expected;m.no_sprite()
        m=new();m.cmap=bytes(768)
        assert m.sprite()==-153;m.no_sprite()
        m=new();m.image_noop=True
        assert m.sprite()==-160;m.no_sprite()
        m=new();assert m.sprite()==1
        assert m.bankfree()==1 and m.bankfree()==1;m.no_sprite()
        assert m.bank(29)==m.payload
        assert m.select(29)==1 and m.sprite()==1 and m.off()==1;m.no_sprite()
        m=new();assert m.sprite()==1
        m.task=TASK+4;assert m.off()==0 and m.sprite()==-139
        m.task=TASK
        m.put32(m.named+52,0x00020070)
        assert m.off()==0 and not m.freed_chip
        m.put32(m.named+52,0x00030070)
        assert m.off()==1;m.no_sprite()
        m=new();assert m.sprite()==1
        m.fail_attempt=True;assert m.off()==0 and not m.freed_chip
        m.fail_attempt=False;assert m.off()==1;m.no_sprite()
        print('S1P2M_NEGATIVE_LIFETIME_CASES_PASS',layout,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s1p2m(a.vasm)
    print('S1P2M_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    functional_cases(image,info)
    chain(image)
    prior,meta=build_l2(a.vasm)
    verify_linked_source(a.vasm,before[1])
    assert run_pattern_cases(prior,image)==184
    assert run_cases(image,info)==172
    l2_gate.IMAGE,l2_gate.META=image,meta
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
    assert result.wasSuccessful() and result.testsRun==10
    second,second_info=build_s1p2m(a.vasm)
    assert second==image and second_info==info
    assert protected()==before
    print('S1P2M_FULL_GATE_A_PASS '+json.dumps(info,sort_keys=True),flush=True)

if __name__=='__main__':main()
