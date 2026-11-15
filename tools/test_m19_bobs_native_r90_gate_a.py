#!/usr/bin/env python3
"""R90 actual MC68020 native masks and persistent Bob draw Gate A.

Exercises the compiled 68k body in Unicorn under two addresses, independent
planar pixel oracle, explicit mask/opaque 0, 1/4/8 depths, clipping, stale
bank relookup and preserved registers. Not a WinUAE/AMOS Compiler claim.
"""
from __future__ import annotations
from struct import unpack_from
from hashlib import sha256
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from amos_link_test_support import relocate
from compiler_relocation import unpack_ap20
from test_m19_bobs_native_r89_gate_a import (NativeBobMachine,
                                             NEWBANK,ARGS,pixel,W,H)
from test_m5_generic import DR,AR,AMOS,STACK,STOP
from build_m19_bobs_native_r89 import build as build_r89,R88
from build_m19_bobs_native_r90 import build,GROUP_BOBS


class Engine(NativeBobMachine):
    def __init__(self,candidate,report,layout='interpreter',depth=8):
        r89,_=build_r89()
        super().__init__(r89,layout=layout,depth=depth)
        _,parts,_=unpack_ap20(candidate)
        _,r88parts,_=unpack_ap20(R88.read_bytes())
        baseline_len=len(r88parts[86])
        native=parts[GROUP_BOBS][baseline_len:]
        self.uc.mem_write(self.entry,relocate(native,self.entry,{},self.uc))
        self.entries={
          'mask':self.entry+(report['mask_offset']-baseline_len),
          'nomask':self.entry+(report['no_mask_offset']-baseline_len),
          'set':self.entry+(report['bob_set_offset']-baseline_len),
          'off':self.entry+(report['bob_off_offset']-baseline_len),
          'draw':self.entry+(report['bob_draw_offset']-baseline_len),
        }
        self.saved_background=[bytes(self.uc.mem_read(p,self.stride*H))
                               for p in self.planes]

    def invoke(self,command,*params):
        order={'mask':(0,1),'nomask':(0,),'set':(0,1,2,3),
               'off':(0,),'draw':()}
        if command not in order:
            raise ValueError(command)
        # Actual AP20 parser: D3 gets rightmost argument, others are on A3
        # in reverse source order (except rightmost).
        args=list(reversed(params[:-1])) if params else []
        d3=params[-1] if params else 0
        for i,r in enumerate(DR):
            self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,v in enumerate(args):
            self.put(ARGS+4*i,v)
        self.uc.reg_write(DR[3],d3&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:self.uc.emu_start(self.entries[command],STOP,count=12_000_000)
        except Exception as error:
            raise AssertionError((
                'native 68020 engine fault',command,params,
                hex(self.uc.reg_read(UC_M68K_REG_PC)),
                str(error),self.calls[-8:],self.oscalls[-8:]
            )) from error
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,(command,params,'no RTS')
        assert self.a(7)==STACK+4,(command,'SP changed',hex(self.a(7)))
        assert self.a(3)==ARGS+len(args)*4,(command,'A3 wrong')
        assert self.d(2)==0,(command,'D2 integer type')
        for r,v in saved.items():
            if r not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(r)==v,(command,'ABI clobber',r,v,
                                               self.uc.reg_read(r))
        assert bytes(self.uc.mem_read(NEWBANK+131072,12))==b'R89-SENTINEL'
        return self.d(3)

    def restore_background(self):
        for p,raw in zip(self.planes,self.saved_background):
            self.uc.mem_write(p,raw)

    def framebuffer(self):
        planes=[bytes(self.uc.mem_read(p,self.stride*H)) for p in self.planes]
        out=bytearray(W*H)
        for y in range(H):
            for x in range(W):
                value=0
                for i,plane in enumerate(planes):
                    value|=((plane[y*self.stride+(x>>3)]>>
                             (7-(x&7)))&1)<<i
                out[y*W+x]=value
        return bytes(out)

    def source_image(self,i):
        raw=self.contents();p=40+(i-1)*24
        valid,w,h,depth,stride,offset,mask,nbytes=unpack_from('>IHHHHIII',raw,p)
        assert valid==1 and nbytes==depth*h*stride
        pixels=bytearray(w*h);transparent=bytearray([1]*(w*h))
        for y in range(h):
            for x in range(w):
                idx=y*w+x
                for plane in range(depth):
                    b=raw[offset+(y*depth+plane)*stride+(x>>3)]
                    pixels[idx]|=((b>>(7-(x&7)))&1)<<plane
                if mask:
                    b=raw[mask+y*stride+(x>>3)]
                    transparent[idx]=(b>>(7-(x&7)))&1
        return w,h,bytes(pixels),bytes(transparent)

    def expected(self,objects):
        before=bytearray(self.initial())
        for img,x,y in objects:
            iw,ih,pixels,alpha=self.source_image(img)
            for sy in range(ih):
                for sx in range(iw):
                    xx,yy=x+sx,y+sy
                    if 0<=xx<W and 0<=yy<H and alpha[sy*iw+sx]:
                        before[yy*W+xx]=pixels[sy*iw+sx]
        return bytes(before)

    def initial(self):
        planes=self.saved_background
        b=bytearray(W*H)
        for y in range(H):
            for x in range(W):
                v=0
                for plane,raw in enumerate(planes):
                    v|=((raw[y*self.stride+(x>>3)]>>(7-(x&7)))&1)<<plane
                b[y*W+x]=v
        return bytes(b)


def main():
    candidate,meta=build()
    runs=0
    for layout in ('interpreter','compiler_v2_copied_unit'):
        for depth in (1,4,8):
            m=Engine(candidate,meta,layout,depth)
            assert m.invoke('draw')==1,'empty draw should be a safe no-op'
            assert m.call('bank',(10,))==1
            assert m.call('get',(1,3,2,19,8))==1
            assert m.call('get',(2,17,1,47,12))==1
            src_idx=pixel(3,2)&((1<<depth)-1)
            assert m.invoke('mask',1,src_idx)==1
            assert m.source_image(1)[3][0]==0,'transparent index not masked'
            # Make 0 the transparency index separately (not forced globally).
            assert m.invoke('mask',1,0)==1
            _,_,first,masks=m.source_image(1)
            assert all((mask==0)==(pix==0) for mask,pix in zip(masks,first))
            assert m.invoke('nomask',2)==1
            assert all(b==1 for b in m.source_image(2)[3])
            assert m.invoke('set',1,20,14,1)==1
            assert m.invoke('set',2,44,18,2)==1
            m.restore_background()
            assert m.invoke('draw')==1
            actual=m.framebuffer();expected=m.expected(((1,20,14),(2,44,18)))
            assert actual==expected,(layout,depth,'two Bob pixels',
                     next((i for i,(a,b) in enumerate(zip(actual,expected))
                           if a!=b),-1))
            # Move object1 partially offscreen, remove object2.
            assert m.invoke('off',2)==1
            assert m.invoke('set',1,-8,H-3,1)==1
            m.restore_background()
            assert m.invoke('draw')==1
            assert m.framebuffer()==m.expected(((1,-8,H-3),))
            # No-mask: pixels with colour index zero must actually clear planes.
            assert m.invoke('nomask',1)==1
            m.restore_background()
            assert m.invoke('draw')==1
            assert m.framebuffer()==m.expected(((1,-8,H-3),))
            assert m.invoke('mask',0,0)==0
            assert m.invoke('mask',129,0)==0
            assert m.invoke('off',33)==0
            # Erase the source bank: objects must not access stale pointers.
            del m.banks[10]
            m.restore_background()
            assert m.invoke('draw')==1
            assert m.framebuffer()==m.initial()
            runs+=15
    print('R90 MC68020 NATIVE GATE A PASS:',runs,
          'mask/draw/ABI/pixel safety cases x 2 ABI layouts x 1,4,8 planes')
    print('R90 SHA256:',meta['sha256'],'bytes',meta['bytes'],
          'WinUAE B and actual AMOS Compiler C NOT RUN')


if __name__=='__main__':
    main()
