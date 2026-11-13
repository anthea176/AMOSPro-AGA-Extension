#!/usr/bin/env python3
"""P5 Gate A: execute real M68000 Blitter core, mock only Exec/Gfx services.

Checks call ABI of BltMaskBitMapRastPort -636, BltBitMapRastPort -606,
InitRastPort -198, WaitBlit -228 and TypeOfMem -534. The mock DMA copy is
independent of the native implementation and is compared byte-for-byte to
the P1 pixel oracle. This is NOT an actual Amiga DMA or WinUAE Gate B/C.
"""
from __future__ import annotations
from random import Random
from struct import pack,unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68000,
    UC_M68K_REG_PC,UC_M68K_REG_SR,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,
)
from m18_ficon16_chip_blit_emit import emit_chip_cache_blit
from m18_ficon_chip_cache import empty_payload,stage,parse_cache
from m18_ficon16_model import build_bank,parse_bank,draw_cpu
from test_m18_ficon16_native_aligned import as_planar,WIDTH,HEIGHT,STRIDE

DR=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
AR=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
CODE=0x10000
STOP=0x12000
CHIP=0x20000
DBM=0x30000
FRONT=0x38000
PLANE=0x40000
FAST=0xb00000
EXEC=0x110000
GFX=0x100000
STACK=0xf0000
GUARD=bytes([0x5a])*32

def uword(uc,address):
    return unpack(">H",bytes(uc.mem_read(address,2)))[0]
def ulong(uc,address):
    return unpack(">I",bytes(uc.mem_read(address,4)))[0]
def r(uc,reg):return uc.reg_read(reg)

def run(code,slot,planes,*,x,y,mode,fast=False,width=WIDTH,height=HEIGHT,
        bad_plane=-1,seed=0):
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    uc.mem_map(0,0x1000000)
    uc.mem_write(CODE,code)
    uc.mem_write(STOP,bytes.fromhex("4e71"))
    uc.mem_write(4,pack(">I",EXEC))
    srcaddr=FAST if fast else CHIP
    uc.mem_write(srcaddr,slot+GUARD)
    ptrs=[PLANE+i*0x1000 for i in range(8)]
    bitmap=pack(">HHBBH",STRIDE,HEIGHT,0,8,0)+b"".join(pack(">I",p) for p in ptrs)
    if bad_plane>=0:
        bad=bytearray(bitmap)
        bad[8+4*bad_plane:12+4*bad_plane]=bytes(4)
        bitmap=bytes(bad)
    uc.mem_write(DBM,bitmap+GUARD)
    frontptrs=[FRONT+i*0x1000 for i in range(8)]
    for addr,p in zip(ptrs,planes):
        uc.mem_write(addr,bytes(p)+GUARD)
    for addr in frontptrs:uc.mem_write(addr,bytes([seed])*len(planes[0]))
    uc.mem_write(EXEC-534,bytes.fromhex("4e75"))
    for disp in (198,606,636,228):
        uc.mem_write(GFX-disp,bytes.fromhex("4e75"))

    calls=[]
    def ret():
        sp=r(uc,AR[7])
        pc=ulong(uc,sp)
        uc.reg_write(AR[7],sp+4)
        uc.reg_write(UC_M68K_REG_PC,pc)
    def hook(uc,address,size,user_data):
        if address==EXEC-534:
            ptr=r(uc,AR[1])
            # Fast RAM must be rejected as DMA source. Chip slot is contiguous.
            kind=2 if CHIP<=ptr<CHIP+288 or any(
                base<=ptr<base+len(planes[0]) for base in ptrs) else 4
            calls.append(("TypeOfMem",ptr,kind))
            uc.reg_write(DR[0],kind)
            ret()
            return
        if address==GFX-198:
            rp=r(uc,AR[1])
            uc.mem_write(rp,bytes(128))
            calls.append(("InitRastPort",rp))
            ret()
            return
        if address in (GFX-606,GFX-636):
            masked=address==GFX-636
            abm=r(uc,AR[0]);rp=r(uc,AR[1])
            assert ulong(uc,rp+4)==DBM,("not inactive BitMap",hex(rp))
            assert uword(uc,abm)==2 and uword(uc,abm+2)==16
            assert uc.mem_read(abm+5,1)==bytes([8])
            srcplanes=[ulong(uc,abm+8+4*i) for i in range(8)]
            assert srcplanes==[srcaddr+32+i*32 for i in range(8)]
            sx,sy,dx,dy,sw,sh,term=[r(uc,d) for d in DR[:7]]
            assert 0<=sx<16 and 0<=sy<16
            assert 0<=dx<WIDTH and 0<=dy<HEIGHT
            assert 1<=sw<=16 and 1<=sh<=16
            assert sx+sw<=16 and sy+sh<=16
            assert dx+sw<=WIDTH and dy+sh<=HEIGHT
            assert term==(0xe0 if masked else 0xc0)
            mask=r(uc,AR[2]) if masked else None
            if masked:assert mask==srcaddr
            calls.append(("BltMask" if masked else "BltOpaque",sx,sy,dx,dy,sw,sh))
            # Independently interpret the 8-plane 16x16 source Bitmap.
            for row in range(sh):
                for col in range(sw):
                    spx=sx+col;spy=sy+row;tx=dx+col;ty=dy+row
                    if masked:
                        maskword=uword(uc,mask+2*spy)
                        if not (maskword & (0x8000>>spx)):
                            continue
                    src_bit=0x80>>(spx%8)
                    dst_bit=0x80>>(tx%8)
                    for plane,srcptr in enumerate(srcplanes):
                        srcbyte=bytes(uc.mem_read(srcptr+2*spy+(spx//8),1))[0]
                        ptr=ptrs[plane]+STRIDE*ty+(tx//8)
                        original=bytes(uc.mem_read(ptr,1))[0]
                        new=(original|dst_bit) if (srcbyte & src_bit) else (original & (255^dst_bit))
                        uc.mem_write(ptr,bytes([new]))
            ret()
            return
        if address==GFX-228:
            calls.append(("WaitBlit",))
            assert len(calls)>=2 and calls[-2][0] in ("BltOpaque","BltMask")
            ret()
            return
        raise AssertionError("unexpected OS call "+hex(address))
    uc.hook_add(UC_HOOK_CODE,hook,begin=GFX-1000,end=EXEC)
    start={
        AR[0]:srcaddr,AR[1]:DBM,AR[2]:0x90302,AR[3]:0x90304,
        AR[4]:0x90306,AR[5]:0x90308,AR[6]:GFX,
        DR[0]:x&0xffffffff,DR[1]:y&0xffffffff,
        DR[2]:0x7788,DR[3]:mode&0xffffffff,
        DR[4]:width,DR[5]:height,DR[6]:0x6677,DR[7]:0x8899,
    }
    for reg,val in start.items():uc.reg_write(reg,val)
    uc.reg_write(UC_M68K_REG_SR,0x2000)
    uc.reg_write(AR[7],STACK)
    uc.mem_write(STACK,pack(">I",STOP))
    try:uc.emu_start(CODE,STOP,count=200000)
    except Exception as exc:
        raise AssertionError(("chip blitter CPU exception",str(exc),
                              "PC",hex(r(uc,UC_M68K_REG_PC)),
                              "X/Y/Mode",x,y,mode,"calls",calls[-8:])) from exc
    assert r(uc,UC_M68K_REG_PC)==STOP,"no RTS"
    assert r(uc,AR[7])==STACK+4,"stack imbalance"
    assert r(uc,DR[2])==0
    for reg,value in start.items():
        if reg not in (DR[2],DR[3]):
            assert r(uc,reg)==value,("register clobbered",reg)
    assert bytes(uc.mem_read(srcaddr,len(slot)+len(GUARD)))==slot+GUARD
    assert bytes(uc.mem_read(DBM+40,len(GUARD)))==GUARD
    after=[bytearray(uc.mem_read(ptr,len(p))) for ptr,p in zip(ptrs,planes)]
    for addr,p in zip(ptrs,planes):
        assert bytes(uc.mem_read(addr+len(p),32))==GUARD
    for addr in frontptrs:
        assert bytes(uc.mem_read(addr,len(planes[0])))==bytes([seed])*len(planes[0])
    return r(uc,DR[3]),after,calls

def main():
    raw,labels=emit_chip_cache_blit()
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
             .disasm(raw,CODE))
    assert sum(i.size for i in ins)==len(raw),"not 68000 instructions"
    assert raw==emit_chip_cache_blit()[0] and len(labels)>10
    rng=Random(0xB11F2026)
    icons=(bytes(256),bytes([255])*256,
           bytes((19*x+9*y)&255 for y in range(16) for x in range(16)),
           bytes(rng.randrange(256) if (x+y)%3 else 0
                 for y in range(16) for x in range(16)))
    source=parse_bank(build_bank(icons))
    cache=empty_payload(4)
    for n in range(1,5):cache=stage(cache,source.raw,n)
    tests=0
    for icon in range(1,5):
        slot=parse_cache(cache).slot(icon)
        for x,y in ((0,0),(1,7),(7,3),(15,0),(16,16),
                    (-15,-1),(-1,2),(49,7),(64,42),
                    (65,1),(-16,5),(17,42)):
            for mode in (0,1):
                bg=bytes(rng.randrange(256) for _ in range(WIDTH*HEIGHT))
                before=as_planar(bg)
                expected=[bytearray(z) for z in before]
                draw_cpu(source,icon,x,y,mode,expected,WIDTH,HEIGHT,STRIDE)
                ok,after,calls=run(raw,slot,before,x=x,y=y,mode=mode,seed=icon)
                assert ok==1 and after==expected,(icon,x,y,mode,"wrong blit pixels")
                visible=(-16<x<WIDTH and -16<y<HEIGHT)
                blits=[x for x in calls if x[0] in ("BltOpaque","BltMask")]
                assert len(blits)==int(visible),(icon,x,y,mode,"blit call")
                if visible:
                    assert len([x for x in calls if x[0]=="InitRastPort"])==1
                    assert len([x for x in calls if x[0]=="WaitBlit"])==1
                    assert len([x for x in calls if x[0]=="TypeOfMem"])==2
                tests+=1
    valid=parse_cache(cache).slot(4)
    bg=as_planar(bytes([0x32]*(WIDTH*HEIGHT)))
    for kw in ({"mode":2},{"mode":-1},{"width":0},{"height":0},
               {"bad_plane":7},{"fast":True}):
        args=dict(x=3,y=5,mode=1)
        args.update(kw)
        status,got,calls=run(raw,valid,bg,**args)
        assert status==0 and got==bg and not any(
            z[0] in ("BltOpaque","BltMask") for z in calls),kw
    print("M18/P5 NATIVE CHIP BLIT CPU/DMA ABI GATE A PASS:",
          len(raw),"bytes;",tests,"pixel oracle cases,",
          "6 invalid/Fast rejects, opaque/masked+WaitBlit")
    print("Unicorn OS hooks only: NOT real hardware DMA or WinUAE")
if __name__=="__main__":
    main()
