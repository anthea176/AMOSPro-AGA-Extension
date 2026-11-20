#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1b host oracle: AGBO hotspot positioning with P0 Clear/Update/Swap.

This is NOT native renderer validation. It deliberately leaves the original
P0 frame model and AGBO v1 format unchanged; every Bob retains LOGICAL X/Y.
"""
from __future__ import annotations

from m19_bob_clear_update_model import BobFrameModel, BobImage, DIRTY, READY, CLEAN
from m19_p0a_multi_bob_abk import parse_payload


def clipped_origin(x:int,y:int,hot_x:int,hot_y:int,
                   width:int,height:int,screen_w:int,screen_h:int
                   ) -> tuple[int,int]|None:
    """P0d-compatible origin: None means fully clipped (no DMA)."""
    if not (-32768<=x<=32767 and -32768<=y<=32767 and
            -32768<=hot_x<=32767 and -32768<=hot_y<=32767):
        raise ValueError('Bob/hotspot outside signed 16-bit range')
    if not (1<=width<=4096 and 1<=height<=4096 and
            1<=screen_w<=4096 and 1<=screen_h<=4096):
        raise ValueError('invalid AGBO or screen geometry')
    dx=x-hot_x
    dy=y-hot_y
    if not (-32768<=dx<=32767 and -32768<=dy<=32767):
        return None
    if dx>=screen_w or dy>=screen_h or dx+width<=0 or dy+height<=0:
        return None
    return dx,dy


class HotspotFrameModel(BobFrameModel):
    """Two-page functional model that uses AGBO per-image hotspots."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._hotspots:dict[int,dict[int,tuple[int,int]]]={}

    def install_bank(self,n:int,images:dict[int,BobImage])->bool:
        accepted=super().install_bank(n,images)
        if accepted:
            self._hotspots.pop(n,None)
        return accepted

    def install_agbo_bank(self,n:int,payload:bytes)->bool:
        source=parse_payload(payload)   # complete source validation first
        if not source.images:
            return self._deny('empty AGBO bank')
        images={}
        hotspots={}
        for image in source.images:
            pixels=tuple(tuple(image.colour(x,y)
                               for x in range(image.width))
                         for y in range(image.height))
            mask=(tuple(tuple(image.visible(x,y)
                              for x in range(image.width))
                        for y in range(image.height))
                  if image.mask is not None else None)
            images[image.image_id]=BobImage(pixels,image.depth,mask)
            hotspots[image.image_id]=(image.hotspot_x,image.hotspot_y)
        if not self.install_bank(n,images):
            return False
        self._hotspots[n]=hotspots
        return True

    def erase_bank(self,n:int)->None:
        super().erase_bank(n)
        self._hotspots.pop(n,None)

    def update(self,*,inject_fault_after_pixels:int|None=None)->bool:
        if not self.screen_open or self.status!=CLEAN:
            return self._deny('screen closed or frame not CLEAN')
        pairs=self._preflight()
        if pairs is None:
            return self._deny('stale bank, invalid image or depth',dirty=True)
        draw=[]
        for bob,img in pairs:
            hot=self._hotspots.get(bob.bank,{}).get(bob.image,(0,0))
            origin=clipped_origin(bob.x,bob.y,*hot,img.width,img.height,
                                  self.width,self.height)
            draw.append((img,origin))
        old=self.saved[self.back]
        if old is None and self.backing_reserved+self.backing_bytes_per_page>self.backing_budget:
            return self._deny('no backing memory',dirty=True)
        if old is not None and not self.clear():
            return False
        self.saved[self.back]=self._copy(self.pages[self.back])
        self.status=DIRTY
        self.draw_calls+=1
        painted=0
        for image,origin in draw:
            if origin is None:
                continue
            ox,oy=origin
            for sy in range(image.height):
                dy=oy+sy
                if not 0<=dy<self.height:
                    continue
                for sx in range(image.width):
                    dx=ox+sx
                    if not 0<=dx<self.width:
                        continue
                    if image.mask is not None and not image.mask[sy][sx]:
                        continue
                    if inject_fault_after_pixels is not None and painted>=inject_fault_after_pixels:
                        return self._deny('injected mid-paint fault',dirty=True)
                    self.pages[self.back][dy][dx]=image.pixels[sy][sx]
                    painted+=1
        self.status=READY
        self.last_error=''
        return True
