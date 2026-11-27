#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Fault injection through the public AP20 Runtime/Compiler models."""
from test_m19_s2c_mixed_public_cpu import MixedPublic,VP,RGB
from test_m19_s2b_public_gate_a import COLORMAP,GFX
from unicorn.m68k_const import UC_M68K_REG_D0

def code(stage,check,detail=0):
    return -((stage<<24)|(check<<16)|detail)

class PostAcquire(MixedPublic):
    def on_code(self,uc,address,size,user):
        d0=uc.reg_read(UC_M68K_REG_D0)
        super().on_code(uc,address,size,user)
        if address==GFX-408 and d0==3 and self.named:
            c=bytearray(self.cmap)
            c[51]^=1
            self.cmap=bytes(c)

def cases(image,info,layout):
    def fresh():return MixedPublic(image,info,layout,False)
    def rejected(m,expect):
        rc=m.sprite(n=2,image=9)
        assert rc==expect,(layout,rc,expect)
        m.empty_sprites()
    for offset,actual,check in ((24,319,7),(26,255,8)):
        m=fresh();m.put16(VP+offset,actual)
        rejected(m,code(1,check,actual))
    m=fresh();m.put32(VP,VP)
    rejected(m,code(1,5))
    m=fresh();m.uc.mem_write(COLORMAP+18,b'\0')
    rejected(m,code(1,15,0))
    for index in (0,1,2,44):
        m=fresh();c=bytearray(m.cmap);c[51+index]^=1;m.cmap=bytes(c)
        rejected(m,code(1,64+index,RGB[index]*256+c[51+index]))
    m=PostAcquire(image,info,layout,False)
    rejected(m,code(2,64,RGB[0]*256+(RGB[0]^1)))
    m=fresh()
    assert m.sprite(n=2,image=9)==1
    old=m.snapshot(2)
    c=bytearray(m.cmap);c[51]^=1;m.cmap=bytes(c)
    assert m.sprite(n=2,image=9,x=40,y=112)==code(5,64,RGB[0]*256+c[51])
    assert m.snapshot(2)==old
    assert m.sprite(n=2,image=10,x=40,y=112)==code(6,64,RGB[0]*256+c[51])
    assert m.snapshot(2)==old
    m.cmap=bytes(51)+RGB+bytes(768-96)
    assert m.off(n=2)==1
    m.empty_sprites()
    print('S2CD_DIAGNOSTIC_FAULTS_PASS',layout,11,flush=True)
