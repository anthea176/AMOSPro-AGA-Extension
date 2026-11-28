#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P1e bounded ViewPort chain tests in the exact public AP20 models."""
from test_m19_s2c_mixed_public_cpu import MixedPublic,VP
from test_m19_s2c_diagnostic_cpu import code
from test_m19_s2b_public_gate_a import GFX
from unicorn.m68k_const import UC_M68K_REG_D0
from struct import pack

TAIL=0x40008000
STEP=64

def chain(m,n):
    # Existing modeled Z3 memory (0x40000000..0x4000ffff).
    # Nonzero canary fields: only Next is relevant, not foreign contents.
    for i in range(n):
        p=TAIL+i*STEP
        nxt=p+STEP if i+1<n else 0
        m.uc.mem_write(p,pack('>I',nxt)+bytes([0x40+i])*60)
    m.put32(VP,TAIL if n else 0)

def tail_bytes(m,n):
    return m.read(TAIL,n*STEP)

class MutateAfterAcquire(MixedPublic):
    def on_code(self,uc,address,size,user):
        d0=uc.reg_read(UC_M68K_REG_D0)
        super().on_code(uc,address,size,user)
        if address==GFX-408 and d0==3 and self.named:
            self.put32(TAIL,VP)

def cases(image,info,layout):
    count=0
    def fresh(n=1,db=False,cls=MixedPublic):
        m=cls(image,info,layout,db)
        chain(m,n)
        return m
    # Single and mixed lifecycles on 1, 2 and 16 successors, DB on/off.
    for n in (1,2,16):
        for db in (False,True):
            m=fresh(n,db)
            tail=tail_bytes(m,n)
            assert m.sprite(n=2,image=3,x=32,y=112)==1
            simple=m.snapshot(2)
            assert m.sprite(n=4,image=9,x=32,y=136)==1
            m.assert_attached(4,9,32,136)
            for img,x in ((10,48),(9,64)):
                assert m.sprite(n=4,image=img,x=x,y=120)==1
                m.assert_attached(4,img,x,120)
                assert m.sprite(n=4,image=img,x=x+8,y=128)==1
                m.assert_attached(4,img,x+8,128)
                assert m.snapshot(2)==simple and tail_bytes(m,n)==tail
            assert m.off(n=4)==1
            assert m.snapshot(2)==simple
            assert m.sprite(n=4,image=9)==1
            assert m.sprite(n=6,image=9)==1
            assert m.sprite(n=60,image=9)<0
            m.close(end=db)
            m.empty_sprites()
            assert tail_bytes(m,n)==tail
            count+=1
    # Refusals before any GetSprite. Unmapped, odd, overflow, head/self,
    # non-head cycle, and a chain exceeding the deliberate 16-node bound.
    for ptr,detail in ((0x50000000,1),(TAIL+1,1),(0xfffffffe,1),(VP,0)):
        m=fresh()
        m.put32(VP,ptr)
        assert m.sprite(n=2,image=9)==code(1,5,detail)
        m.empty_sprites()
        assert not m.sprite_calls
        count+=1
    for n,link,detail in ((1,TAIL,0),(2,VP,0),(2,TAIL,2),(17,None,2)):
        m=fresh(n)
        if link is not None:m.put32(TAIL+(n-1)*STEP,link)
        assert m.sprite(n=2,image=9)==code(1,5,detail)
        m.empty_sprites()
        assert not m.sprite_calls
        count+=1
    # Invalid link after the two acquisitions must retire both receipts.
    m=fresh(1,cls=MutateAfterAcquire)
    assert m.sprite(n=2,image=9)==code(2,5,0)
    m.empty_sprites()
    count+=1
    # A new invalid chain after WaitTOF refuses before staging, retaining
    # the exact visible frame and all ownership; repair only test fixture.
    m=fresh(2)
    assert m.sprite(n=2,image=9)==1
    before=m.snapshot(2)
    m.wait_mutation=lambda x:x.put32(TAIL,VP)
    assert m.sprite(n=2,image=10)==code(7,5,0)
    assert m.snapshot(2)==before
    m.put32(TAIL,TAIL+STEP)
    assert m.off(n=2)==1
    m.empty_sprites()
    count+=1
    assert count==16
    print('S2CE_VIEWPORT_CHAIN_PASS',layout,count,flush=True)
