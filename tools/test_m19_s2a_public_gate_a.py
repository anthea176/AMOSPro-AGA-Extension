#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2a public AP20 routes on MC68020; modeled OS, NOT real DMA."""
import argparse, json, os, unittest
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from build_m19_s2a_in_memory import build_s2a, protected
import test_m19_s1p2m_gate_a as p2m
from test_m19_s1p2m_gate_a import LifecycleMachine
from test_m19_s1p2i_gate_a import STATE, CI, TASK
from test_m19_s1p2j_gate_a import FAST_TABLE
from test_m19_s1p1c_amos_bank_commit import EXEC
from test_m19_s1p1c_pipeline import SCREEN,GFX
from m19_s1_agsp_bank import empty_bank, put_capture, parse_payload, s0_interleaved_image

PALETTE=bytes.fromhex('000000ff462824dc751a73ff')
VIEW=0x96000

def animation_bank(extra=False):
    raw=empty_bank()
    entries=[(3,16,PALETTE,0),(4,16,PALETTE,0)]
    if extra:
        entries.extend(((5,16,bytes.fromhex('000000ee462824dc751a73ff'),0),
                        (6,17,PALETTE,0),(7,16,PALETTE,1)))
    for ident,h,cmap,hotspot in entries:
        pixels=bytes((x if y==0 else (x+y*(1 if ident==3 else 3)))%4
                     for y in range(h) for x in range(16))
        raw=put_capture(raw,ident,pixels,16,h,0,0,16,h,cmap,0,hotspot_x=hotspot)
    return raw

class AnimationMachine(LifecycleMachine):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.put32(VIEW,SCREEN+44)
        self.last_publication={}
        self.switches=0
        self.stage_writes=0
        self.change_noop=False
        self.skip_copper=False
        self.move_noop=False
        self.wait_mutation=None
        self.alloc_mutation=None
        self.uc.hook_add(UC_HOOK_MEM_WRITE,self.watch_frame)

    def install_animation(self,extra=False):
        self.erase()
        self.payload=animation_bank(extra)
        self.node=self.make_bank(29,b'AGASPRT ',self.payload)
        self.cmap=bytes(63)+PALETTE[3:12]+bytes(696)
        # Fixed nonoverlapping mock arena for positive transitions.
        self.newptr=0x220000

    def live(self):
        rec=self.get(self.root())
        chip=self.get(rec)
        return rec,chip,self.get(chip)

    def watch_frame(self,uc,access,addr,size,value,user):
        for base in self.ever:
            if base+48<=addr<base+self.allocations[base]:
                active=self.get(base)
                frame=self.get(base+44)-48
                assert active in (base+48,base+48+frame)
                spare=base+48+frame if active==base+48 else base+48
                assert spare<=addr and addr+size<=spare+frame, 'active slot overwritten'
                assert self.tofs-self.last_publication[base]>=2,'staging before fence'
                self.stage_writes+=size

    def on_code(self,uc,address,size,user):
        a0=uc.reg_read(UC_M68K_REG_A0)
        a1=uc.reg_read(UC_M68K_REG_A1)
        d0=uc.reg_read(UC_M68K_REG_D0)
        d1=uc.reg_read(UC_M68K_REG_D1)
        if address==GFX-420 and a1 in self.ever and self.get(FAST_TABLE+8)==a1:
            assert a0==SCREEN+44
            ptr=uc.reg_read(UC_M68K_REG_A2)
            old=self.get(a1)
            assert ptr in (a1+48,a1+self.get(a1+44)) and ptr!=old
            assert ptr>>16==old>>16
            assert self.tofs-self.last_publication[a1]>=2
            assert self.chip==self.ever, 'scratch not freed before publication'
            self.switches+=1
            self.sprite_calls.append('change')
            if not self.change_noop:
                # V40 ChangeSprite sets posctldata and falls through MoveSprite.
                self.put32(a1,ptr)
                if not self.skip_copper:self.copper(2,ptr)
                self.last_publication[a1]=self.tofs
            self.volatile(uc,0)
            return
        if address==GFX-426:
            assert a0==SCREEN+44 and a1 in self.ever
            ptr=self.get(a1)
            assert ptr in (a1+48,a1+self.get(a1+44))
            if not self.did_first_move:
                assert self.get(FAST_TABLE+8)==0
                self.did_first_move=True
            self.last_publication.setdefault(a1,self.tofs)
            self.put32(FAST_TABLE+8,a1)
            self.copper(2,ptr)
            self.moves.append((d0,d1))
            if not self.move_noop:
                self.put16(a1+6,d0);self.put16(a1+8,d1)
            self.volatile(uc,0)
            return
        result=super().on_code(uc,address,size,user)
        if address==GFX-270 and self.wait_mutation is not None:
            change=self.wait_mutation
            self.wait_mutation=None
            change(self)
        if address==EXEC-684 and d1==0x10003 and self.alloc_mutation is not None:
            change=self.alloc_mutation
            self.alloc_mutation=None
            change(self)
        return result

def pixels(m,ident):
    _,chip,ptr=m.live()
    im=parse_payload(m.payload).image(ident)
    raw=s0_interleaved_image(im)
    assert m.read(ptr+4,len(raw)-4)==raw[4:]
    assert m.word(chip+16)==ident
    assert m.get(m.get(m.root())+36)==ident

def snapshot(m):
    rec,chip,ptr=m.live()
    return (m.read(rec,40),m.read(chip,m.allocations[chip]),dict(m.allocations),
            m.switches,m.stage_writes)

def animation_cases(image,info):
    for layout in ('runtime','compiled'):
        def new(extra=False,db=False,crossing=False):
            m=AnimationMachine(image,info,layout,db)
            m.install_animation(extra)
            if crossing:m.newptr=0x22fd20
            assert m.select(29)==1
            assert m.sprite()==1
            pixels(m,3)
            return m
        for db in (False,True):
            m=new(db=db)
            rec,chip,old=m.live()
            initial=dict(m.allocations)
            for i in range(100):
                ident=4 if i%2==0 else 3
                before=m.tofs
                assert m.sprite(x=32+i,y=112,image=ident)==1
                assert m.tofs-before==2
                assert m.live()[:2]==(rec,chip) and m.live()[2]!=old
                old=m.live()[2]
                pixels(m,ident)
                assert m.allocations==initial and len(m.temp_live)==3
                assert m.sprite(x=34+i,image=ident)==1
                assert m.tofs-before==2 and m.live()[2]==old
            assert m.switches==100 and m.stage_writes==7200
            assert m.sprite_calls.count('get2')==m.sprite_calls.count('get3')==1
            assert not any(x.startswith('free') for x in m.sprite_calls)
            # Release from slot B too, both Close and End use unchanged UNIT142.
            assert m.sprite(image=4)==1
            m.close(end=db);assert m.get(STATE)==0;m.no_sprite()
            assert m.bank(29)==m.payload
        m=new(extra=True)
        for ident in (5,6,7,8):
            before=snapshot(m)
            assert m.sprite(image=ident)==-202
            assert snapshot(m)==before
        assert m.off()==1;m.no_sprite()
        # No selected bank, edited generation, and mutation during preparation.
        m=new();m.erase()
        assert m.sprite(image=4)==-201
        assert m.sprite(x=40)==1
        assert m.off()==1;m.no_sprite()
        for when in ('before','alloc','wait'):
            m=new()
            def edit(k):
                k.put32(k.node+48,k.get(k.node+48)+1)
            if when=='before':edit(m)
            elif when=='alloc':m.alloc_mutation=edit
            else:m.wait_mutation=edit
            before=snapshot(m)
            assert m.sprite(image=4)==-201
            assert snapshot(m)==before
            assert m.off()==1;m.no_sprite()
        m=new();m.fail_temp_at=m.temp_tries+1
        before=snapshot(m)
        assert m.sprite(image=4)==-202
        assert snapshot(m)==before
        assert m.off()==1;m.no_sprite()
        m=new(crossing=True)
        rec,chip,old=m.live()
        assert old>>16!=(chip+m.get(chip+44))>>16
        before=snapshot(m)
        assert m.sprite(image=4)==-204
        assert snapshot(m)==before
        assert m.off()==1;m.no_sprite()
        for address in (GFX+34,GFX+38,GFX+50,GFX+54,GFX+208,VIEW,SCREEN+56,
                        FAST_TABLE+8,FAST_TABLE+12,CI+104,CI+106,CI+110):
            m=new()
            size=2 if address in (CI+104,CI+106,CI+110) else 4
            original=m.read(address,size)
            m.uc.mem_write(address,bytes([0x5a])*size)
            before=snapshot(m)
            assert m.sprite(image=4)==-203
            assert snapshot(m)==before
            m.uc.mem_write(address,original)
            assert m.off()==1;m.no_sprite()
        # Stale alternate pointer appears after a frame wait: no staging.
        m=new()
        _,chip,old=m.live()
        m.wait_mutation=lambda k:k.copper(2,chip+k.get(chip+44))
        before=snapshot(m)
        assert m.sprite(image=4)==-203
        assert snapshot(m)==before
        m.copper(2,old)
        assert m.off()==1;m.no_sprite()
        for flag in ('change_noop','skip_copper','move_noop'):
            for pending in (False,True):
                m=new()
                setattr(m,flag,True)
                m.keep_refs=pending
                assert m.sprite(x=80,image=4)==-205
                if pending:
                    m.held()
                    assert m.get(m.get(m.root())+36)==0
                    assert m.sprite(image=4)==-140
                    m.keep_refs=False;m.clear_refs()
                    assert m.off()==1
                m.no_sprite()
        # Off and Bank Free release a displayed alternate slot.
        for bankfree in (False,True):
            m=new()
            assert m.sprite(image=4)==1
            assert (m.bankfree() if bankfree else m.off())==1
            m.no_sprite()
            assert m.bank(29)==m.payload
        print('S2A_PUBLIC_200_CHANGES_AND_NEGATIVES_PASS',layout,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    p.add_argument('--full',action='store_true')
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s2a(a.vasm)
    print('S2A_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    animation_cases(image,info)
    # Run the original P2m lifetime suite unchanged on the S2a candidate.
    p2m.LifecycleMachine=AnimationMachine
    p2m.functional_cases(image,info)
    if a.full:
        p2m.chain(image)
        prior,meta=p2m.build_l2(a.vasm)
        p2m.verify_linked_source(a.vasm,before[1])
        assert p2m.run_pattern_cases(prior,image)==184
        assert p2m.run_cases(image,info)==172
        p2m.l2_gate.IMAGE,p2m.l2_gate.META=image,meta
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(p2m.l2_gate.L2GateA))
        assert result.wasSuccessful() and result.testsRun==10
    second,second_info=build_s2a(a.vasm)
    assert second==image and second_info==info
    assert protected()==before
    print(('S2A_FULL_GATE_A_PASS ' if a.full else 'S2A_PUBLIC_GATE_A_PASS ')
          +json.dumps(info,sort_keys=True),flush=True)

if __name__=='__main__':main()
