#!/usr/bin/env python3
"""M18/P3: Unicorn M68000 arbitrary-X word renderer vs independent P1 oracle.

Gate A CPU only. No AP20, Blitter DMA, physical Fast/Chip allocation,
WinUAE, performance measurement or change to R60 LAST_GOOD.
"""
from random import Random
from unicorn.m68k_const import UC_M68K_REG_A2,UC_M68K_REG_D6,UC_M68K_REG_D7
from m18_ficon16_native_shifted_emit import F
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from m18_ficon16_model import build_bank,parse_bank,draw_cpu
from m18_ficon16_native_shifted_emit import emit_ficon16_shifted_cpu
from m18_ficon16_native_aligned_emit import emit_ficon16_aligned_cpu
from test_m18_ficon16_native_aligned import (
    execute,as_planar,WIDTH,HEIGHT,STRIDE,
    ICON,POINTERS,CODE,
)

def main():
    code,labels=emit_ficon16_shifted_cpu()
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
             .disasm(code,0x10000))
    assert sum(x.size for x in ins)==len(code), 'non-68000 encoding detected'
    assert code==emit_ficon16_shifted_cpu()[0], 'non-deterministic emission'
    assert {'row','plane','half1','skip_row','mask0_clipped',
            'invalid','success','done'} <= set(labels)
    assert not any(i.mnemonic.lower() in ('jsr','jmp','trap','stop') for i in ins)
    rng=Random(0xF0162027)
    icons=(
        bytes([0]*256),
        bytes([255]*256),
        bytes(((x*19+y*13)&255) for y in range(16) for x in range(16)),
        bytes((rng.randrange(256) if (x+y)%5 else 0)
              for y in range(16) for x in range(16)),
    )
    bank=parse_bank(build_bank(icons))
    positions=(
        (-32768,-32768),(-17,-3),(-16,0),(-15,0),(-8,5),
        (-1,-1),(-1,0),(0,0),(0,-15),
        (WIDTH-16,2),(WIDTH-15,2),(WIDTH-1,1),
        (WIDTH,0),(WIDTH+1,0),(32767,32767),
        (1,HEIGHT-1),(15,HEIGHT-1),(17,HEIGHT),
    )+tuple((shift,3) for shift in range(16))+tuple(
        (16+shift,9) for shift in range(16))+tuple(
        (48+shift,HEIGHT-5) for shift in range(16))
    cases=0
    for icon_id in range(1,5):
        icon=bank.icon(icon_id)
        for x,y in positions:
            for mode in (0,1):
                pixels=bytes(rng.randrange(256) for _ in range(WIDTH*HEIGHT))
                before=as_planar(pixels)
                expected=[bytearray(p) for p in before]
                draw_cpu(bank,icon_id,x,y,mode,expected,WIDTH,HEIGHT,STRIDE)
                status,actual=execute(code,icon,before,x=x,y=y,mode=mode)
                assert status==1,(icon_id,x,y,mode,'return')
                if actual!=expected:
                    diff=[(plane,pos//STRIDE,pos%STRIDE,
                           f'{wanted:02x}',f'{got:02x}')
                          for plane,(exp,gotplane) in enumerate(zip(expected,actual))
                          for pos,(wanted,got) in enumerate(zip(exp,gotplane))
                          if wanted!=got][:12]
                    frames=[]
                    def on_code(uc,address,size,user_data):
                        if address!=CODE+labels['plane'] or len(frames)>1:
                            return
                        base=uc.reg_read(UC_M68K_REG_A2)
                        keys=['baseword','lastword','lastmask','shift',
                              'backshift','offset0','offset1','mask0','mask1']
                        vals={k:hex(int.from_bytes(uc.mem_read(base+F[k],4),'big'))
                              for k in keys}
                        vals.update(D6=hex(uc.reg_read(UC_M68K_REG_D6)),
                                    D7=hex(uc.reg_read(UC_M68K_REG_D7)))
                        frames.append(vals)
                    execute(code,icon,before,x=x,y=y,mode=mode,debug_hook=on_code)
                    raise AssertionError((icon_id,x,y,mode,'pixel mismatch',
                                          'plane,row,byte,expected,actual',diff,
                                          'first native frame',frames))
                cases+=1
    # The new general renderer must exactly match the already-qualified
    # aligned native 68000 fast path, including the edge and transparency.
    aligned,_=emit_ficon16_aligned_cpu()
    same=0
    for x,y in ((0,0),(16,1),(32,7),(48,27),(64,42),
                (-16,2),(0,-1),(80,0)):
        for mode in (0,1):
            before=as_planar(bytes(rng.randrange(256)
                                   for _ in range(WIDTH*HEIGHT)))
            icon=bank.icon(4)
            a_status,a=execute(aligned,icon,before,x=x,y=y,mode=mode)
            b_status,b=execute(code,icon,before,x=x,y=y,mode=mode)
            assert a_status==b_status==1 and a==b,(x,y,mode,'aligned')
            same+=1
    invalid=(
        dict(x=32768),dict(x=-32769),dict(y=32768),dict(y=-32769),
        dict(mode=-1),dict(mode=2),dict(width=0),dict(width=4097),
        dict(height=0),dict(height=4097),dict(stride=1),
        dict(stride=STRIDE-2),dict(stride=65536),dict(source=0),
        dict(source=ICON+1),dict(ptrs=0),dict(ptrs=POINTERS+1),
        dict(bad_plane=7),
    )
    before=as_planar(bytes([0x42]*(WIDTH*HEIGHT)))
    icon=bank.icon(3)
    for kwargs in invalid:
        status,after=execute(code,icon,before,**kwargs)
        assert status==0 and after==before,('invalid accepted or drew',kwargs)
    print('M18/P3 GENERAL X GATE A PASS:',len(code),'bytes;',
          cases,'pixel/ABI cases;',same,'aligned-native equivalences;',
          len(invalid),'rejections without writes')
    print('8 bitplanes; opaque/colour-zero mask; X=-15..+63, '
          'four-edge clipping, guard memory and stack/register integrity')
    print('CPU/Unicorn ONLY: no AP20, no WinUAE, no real Blitter.')

if __name__=='__main__':
    main()
