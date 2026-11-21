#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b4: persistent 64-Bob Safe Blitter WITHOUT selected shadow.

Two PRIVATE native BOBS entrypoints, no AMOS token/Lib/Swap:
  explicit_safe_blit_entry(D3=bank,D0=image,D1=X,D4=Y,A5=owner)
    validates the real AGA Safe back BitMap; calls P0j-b3's explicit
    image resolver; branches into the ORIGINAL P0d safe painter after
    the resolver at an exact zero-byte source label. Its safety checks,
    clipping, graphics.library Blit and WaitBlit remain byte-identical.
  explicit_frame_draw_entry(A5=owner)
    P0h/P0j-a prevalidates all 64 sources/images BEFORE any DMA,
    traverses active Bob IDs 1..64 in order using P0g per-bank stamps,
    uses P0j-b2 explicit Chip preparation/caching, arms original End
    callback, then paints into the NON-displayed Safe back BitMap.

This entry never reads or writes bank_active_state, even momentarily.
Failures after earlier paint may leave a PARTIALLY modified HIDDEN back
buffer: NO Swap occurs, and the caller MUST not present a failed frame.
The selected-bank P0i public source remains preserved but is NOT used
by the new frame path. Foreground synchronous painting only; an
asynchronous mutation between preflight and DMA is not supported.
"""
from __future__ import annotations
from hashlib import sha256
from m68k_emit import Code,D,A,M,I
from m19_p0d_safe_bank_blit_emit import F as DF
from m19_p0j_explicit_image_resolve_emit import emit_explicit_bank_image_resolve,FRAME as RES_FRAME

FRAME=160
RECORD=96
MAX_BOBS=64
F=dict(ident=0,result=4,bank=8,image=12,x=16,y=20,state=24,gfx=28)
assert RECORD+24<=FRAME
assert RES_FRAME==192

def emit_explicit_bob_draw() -> tuple[bytes,dict[str,int]]:
    previous,labels=emit_explicit_bank_image_resolve()
    if 'draw_live_image_resolved' not in labels:
        raise ValueError('Missing original P0d zero-byte Safe image join')
    c=Code();c.raw(previous.hex());c.labels.update(labels)
    B,L=c.branch,c.label

    # Identical P0d Safe prechecks, except the original source bank
    # is resolved by the explicit b3 function without shadow projection.
    def DS(src,key):c.move(src,M(4,DF[key]))
    def DG(key,dst):c.move(M(4,DF[key]),dst)
    def nonzero_even(key):
        DG(key,D(0))
        c.tst(D(0));B(7,'draw_reject')
        c.imm('and',1,D(0));B(6,'draw_reject')
    def mapped(key):
        DG(key,A(1))
        c.raw('2c780004');c.call_os(-534)
        c.tst(D(0));B(7,'draw_reject')

    L('explicit_safe_blit_entry')
    c.raw('48e7efee4fefff00')  # P0d ABI + 256-byte frame
    c.move(A(7),A(4))
    DS(D(3),'bank');DS(D(0),'image')
    DS(D(1),'x');DS(D(4),'y')
    DS(A(3),'saved_a3');DS(I(0),'result')
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'draw_reject')
    c.move(A(5),D(0));c.tst(D(0));B(7,'draw_reject')
    c.imm('and',1,D(0));B(6,'draw_reject')

    c.move(M(5,0x1c8),D(0));DS(D(0),'state')
    nonzero_even('state');mapped('state')
    DG('state',A(0))
    c.move(M(0,0),D(0));c.tst(D(0));B(7,'draw_reject')
    c.move(M(0,8),D(0));DS(D(0),'gfx')
    nonzero_even('gfx')
    DG('state',A(0));c.move(M(0,32),D(0));DS(D(0),'db')
    nonzero_even('db');mapped('db')
    for off,key,upper in ((12,'screen_w',4096),(16,'screen_h',4096),
                          (28,'depth',8)):
        DG('state',A(0));c.move(M(0,off),D(0))
        c.imm('cmp',1,D(0));B(5,'draw_reject')
        c.imm('cmp',upper,D(0));B(2,'draw_reject')
        DS(D(0),key)

    # Exact front/back ScreenBuffer selection as P0d, no implicit Swap.
    DG('db',A(0));c.move(M(0,8),D(0))
    c.tst(D(0));B(7,'explicit_safe_front_zero')
    c.imm('cmp',1,D(0));B(6,'draw_reject')
    c.move(M(0,0),D(1));DS(D(1),'back_sb')
    c.move(M(0,4),D(1));DS(D(1),'front_sb')
    B(0,'explicit_safe_buffers_ready')
    L('explicit_safe_front_zero')
    c.move(M(0,4),D(1));DS(D(1),'back_sb')
    c.move(M(0,0),D(1));DS(D(1),'front_sb')
    L('explicit_safe_buffers_ready')
    nonzero_even('back_sb');nonzero_even('front_sb')
    DG('back_sb',D(0));DG('front_sb',D(1))
    c.alu('cmp',D(1),0);B(7,'draw_reject')
    mapped('back_sb')
    DG('back_sb',A(0));c.move(M(0,0),D(0));DS(D(0),'bitmap')
    nonzero_even('bitmap');mapped('bitmap')

    DG('bank',D(3));DG('image',D(0))
    c.move(A(4),A(1))      # original 36-byte descriptor at frame start
    B(1,'explicit_image_resolve_entry')
    c.tst(D(3));B(7,'draw_reject')
    # The ORIGINAL P0d SafePort/Blitter/WaitBlit function finishes us.
    B(0,'draw_live_image_resolved')

    emit_frame_draw(c)

    native=c.out()
    if (not native.startswith(previous)
            or c.labels['explicit_safe_blit_entry']!=len(previous)
            or c.labels['explicit_frame_draw_entry']<=c.labels['explicit_safe_blit_entry']
            or len(native)&1 or len(native)>=32766):
        raise ValueError('P0j-b4 changed P0d bytes / invalid source PC16')
    return native,c.labels


def emit_frame_draw(c: Code, *, traversal=None, frame_bytes=FRAME):
    """Emit the checked frame renderer with its default or supplied traversal."""
    B,L=c.branch,c.label
    def FS(src,key):c.move(src,M(2,F[key]))
    def FG(key,dst):c.move(M(2,F[key]),dst)
    def output_record():
        c.move(A(2),D(0));c.imm('add',RECORD,D(0))
        c.move(D(0),A(1))

    L('explicit_frame_draw_entry')
    c.raw('48e7efee')          # preserve AMOS ABI
    c.word(0x4fef);c.word(-frame_bytes)
    c.move(A(7),A(2))
    FS(I(0),'result')
    # Full P0h bank stamps + P0j-a image preflight: NO DMA before this.
    B(1,'image_frame_preflight_entry')
    c.tst(D(3));B(7,'explicit_frame_return')
    c.move(M(5,0x1c8),D(0));FS(D(0),'state')
    c.tst(D(0));B(7,'explicit_frame_return')
    FG('state',A(0));c.move(M(0,8),D(0));FS(D(0),'gfx')
    c.tst(D(0));B(7,'explicit_frame_return')
    c.imm('and',1,D(0));B(6,'explicit_frame_return')
    if traversal is None:
        FS(I(1),'ident')
        L('explicit_frame_next')
        FG('ident',D(0))
        c.imm('cmp',MAX_BOBS,D(0));B(2,'explicit_frame_done')
    else:
        traversal.begin(c)
        L('explicit_frame_next')
        traversal.next(c)

    output_record();FG('ident',D(0))
    B(1,'relay_read_entry')
    c.tst(D(3));B(7,'explicit_frame_advance')
    output_record();FG('ident',D(0))
    B(1,'relay_checked_read_entry')
    c.tst(D(3));B(7,'explicit_frame_return')
    c.move(M(2,RECORD+0),D(0));FS(D(0),'bank')
    c.move(M(2,RECORD+4),D(0));FS(D(0),'image')
    c.move(M(2,RECORD+8),D(0));FS(D(0),'x')
    c.move(M(2,RECORD+12),D(0));FS(D(0),'y')

    FG('bank',D(3));FG('gfx',A(4))
    B(1,'explicit_registry_prepare_entry')
    c.tst(D(3));B(7,'explicit_frame_return')
    B(1,'program_end_arm_entry')
    c.tst(D(3));B(7,'explicit_frame_unwind')
    FG('bank',D(3));FG('image',D(0))
    FG('x',D(1));FG('y',D(4))
    L('explicit_frame_paint_call')
    B(1,'explicit_safe_blit_entry')
    c.tst(D(3));B(7,'explicit_frame_return')

    L('explicit_frame_advance')
    if traversal is None:
        FG('ident',D(0));c.quick(1,D(0));FS(D(0),'ident')
    B(0,'explicit_frame_next')
    L('explicit_frame_unwind')
    FG('bank',D(3));FG('gfx',A(4))
    B(1,'registry_free_entry')
    B(0,'explicit_frame_return')
    L('explicit_frame_done')
    FS(I(1),'result')
    L('explicit_frame_return')
    FG('result',D(3))
    c.word(0x4fef);c.word(frame_bytes)
    c.raw('4cdf77f7')           # restore AMOS preserved
    c.raw('74004e75')           # D2=0; RTS


if __name__=='__main__':
    data,labels=emit_explicit_bob_draw()
    print('M19 P0j-b4 MC68020 PRIVATE NO-SHADOW 64-BOB DRAW SOURCE ONLY',
          len(data),sha256(data).hexdigest(),
          'Safe entry',labels['explicit_safe_blit_entry'],
          'frame entry',labels['explicit_frame_draw_entry'],
          'NO public Draw/Lib/WinUAE')
