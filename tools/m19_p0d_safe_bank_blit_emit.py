#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0d PRIVATE Safe AGA back-buffer -> staged AGBO Chip Blitter bridge.

SOURCE ONLY: append to verified P0c+P0d native BOBS source without changing
any installed AP20 stub, token, or official .Lib. No publicly callable AMOS
instruction exists for this private entry. No automatic Aga Swap.

Entry: A5=current AMOS program, D3=selected AGBO bank,
       D0=1-based image ID, D1=signed X, D4=signed Y.
Return: D3=1 success (including entirely offscreen), 0 refusal; D2=0.
All other AMOS-preserved registers (including A3/A5) and SP are retained.

Prerequisite: current bank was prepared using private P0c registry_prepare,
and the End callback was armed using private program_end_arm. These should
happen ONCE when the bank is selected, never once per Bob per frame.

The bridge calls the MC68020 image resolver (identity/generation and
allocation bounds), uses the ACTUAL AGA State at A5+0x1C8 and the existing
P0c/R27 DBState layout, selects the non-displayed ScreenBuffer's BitMap,
and handles only the SAFE pending flag (DBState+20 bit0) with nonblocking
Exec GetMsg(SafePort). No ReplyMsg, WaitPort, WaitVbl or polling.

The painter checks exact geometry, Chip source/mask and destination planes
then calls graphics.library BltBitMapRastPort/BltMaskBitMapRastPort and
WaitBlit before return. The caller must not mutate/Erase bank or swap while
the operation is in progress. Interruption-driven Bob drawing is unsupported.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I
from m19_p0d_bank_image_resolve_emit import emit_bank_image_resolve
from m19_p0d_private_blit_emit import emit_private_bob_blit

FRAME = 256
DESC_SIZE = 36
F = {name:64+4*i for i,name in enumerate((
    'bank image x y state db gfx back_sb front_sb bitmap depth '
    'screen_w screen_h result saved_a3'
).split())}
assert max(F.values())+4 <= FRAME


def emit_safe_bank_blit() -> tuple[bytes, dict[str,int]]:
    previous, labels = emit_bank_image_resolve()
    painter, painter_labels = emit_private_bob_blit()
    assert painter_labels['private_bob_blit_entry'] == 0
    c = Code()
    c.raw(previous.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label

    def S(src,name):
        c.move(src,M(4,F[name]))

    def G(name,dst):
        c.move(M(4,F[name]),dst)

    def nonzero_even(name):
        G(name,D(0))
        c.tst(D(0)); B(7,'draw_reject')
        c.imm('and',1,D(0)); B(6,'draw_reject')

    def mapped(name):
        G(name,A(1))
        c.raw('2c780004')         # ExecBase at (4).W
        c.call_os(-534)           # TypeOfMem
        c.tst(D(0)); B(7,'draw_reject')

    L('safe_bank_blit_entry')
    c.raw('48e7efee')              # save AMOS-preserved register set
    c.raw('4fefff00')              # LEA -256(SP),SP
    c.move(A(7),A(4))              # frame, descriptor at +0..+35
    S(D(3),'bank')
    S(D(0),'image')
    S(D(1),'x')
    S(D(4),'y')
    S(A(3),'saved_a3')
    S(I(0),'result')
    B(1,'registry_cpu_guard')
    c.tst(D(0)); B(7,'draw_reject')
    c.move(A(5),D(0)); c.tst(D(0)); B(7,'draw_reject')
    c.imm('and',1,D(0)); B(6,'draw_reject')

    # AGA state is obtained from the actual installed AGA Init, not a
    # surrogate AMOS screen pointer and not the OCS Screen Open state.
    c.move(M(5,0x1c8),D(0)); S(D(0),'state')
    nonzero_even('state')
    mapped('state')
    G('state',A(0))
    c.move(M(0,0),D(0)); c.tst(D(0)); B(7,'draw_reject')
    c.move(M(0,8),D(0)); S(D(0),'gfx')
    nonzero_even('gfx')
    G('state',A(0)); c.move(M(0,32),D(0)); S(D(0),'db')
    nonzero_even('db')
    mapped('db')
    for off,key,high in ((12,'screen_w',4096),(16,'screen_h',4096),
                         (28,'depth',8)):
        G('state',A(0)); c.move(M(0,off),D(0))
        c.imm('cmp',1,D(0)); B(5,'draw_reject')
        c.imm('cmp',high,D(0)); B(2,'draw_reject')
        S(D(0),key)

    # R27/P0a verified double-buffer layout: front 0 -> back SB1,
    # front 1 -> back SB0. Reject aliasing; never paint the front.
    G('db',A(0))
    c.move(M(0,8),D(0))
    c.tst(D(0)); B(7,'draw_front_zero')
    c.imm('cmp',1,D(0)); B(6,'draw_reject')
    c.move(M(0,0),D(1)); S(D(1),'back_sb')
    c.move(M(0,4),D(1)); S(D(1),'front_sb')
    B(0,'draw_have_buffers')
    L('draw_front_zero')
    c.move(M(0,4),D(1)); S(D(1),'back_sb')
    c.move(M(0,0),D(1)); S(D(1),'front_sb')
    L('draw_have_buffers')
    nonzero_even('back_sb')
    nonzero_even('front_sb')
    G('back_sb',D(0)); G('front_sb',D(1))
    c.alu('cmp',D(1),0); B(7,'draw_reject')    # BEQ: same SB
    mapped('back_sb')
    G('back_sb',A(0))
    c.move(M(0,0),D(0)); S(D(0),'bitmap')
    nonzero_even('bitmap')
    mapped('bitmap')

    # Resolve current selected AGBO image in the existing P0c Chip context.
    # This returns an ALL-OR-NOTHING 9-long descriptor at the frame start.
    G('bank',D(3)); G('image',D(0))
    c.move(A(4),A(1))
    B(1,'bank_image_resolve_entry')
    c.tst(D(3)); B(7,'draw_reject')
    # P0j-b4 joins the ORIGINAL Safe/Blitter after its own explicit
    # image resolver. Label only: no change to P0d native bytes.
    L('draw_live_image_resolved')

    G('depth',D(0))
    c.move(M(4,20),D(1))              # image depth in descriptor
    c.alu('cmp',D(1),0); B(6,'draw_reject')

    # Safe pending: GetMsg exactly once, no ReplyMsg. An empty SafePort
    # means refusal, no DMA and no implicit present. Preserve Disp bit.
    G('db',A(0)); c.move(M(0,20),D(0))
    c.imm('and',1,D(0)); B(7,'draw_safe_ready')
    G('db',A(0)); c.move(M(0,12),D(0))
    c.tst(D(0)); B(7,'draw_reject')
    c.move(D(0),A(0))
    c.raw('2c780004')                 # ExecBase
    c.call_os(-372)                  # GetMsg(SafePort)
    c.tst(D(0)); B(7,'draw_reject')
    G('db',A(0))
    c.move(M(0,20),D(0))
    c.imm('and',0xfffffffe,D(0))
    c.move(D(0),M(0,20))
    L('draw_safe_ready')

    # The verified private painter is independent of the metadata and
    # always completes its Blitter operation before returning.
    c.move(M(4,0),A(0))              # Chip pixel plane-0
    c.move(M(4,4),A(1))              # Chip mask or 0
    G('bitmap',A(2))                 # NON-displayed BitMap
    G('gfx',A(6))
    # The painter clips to actual logical AGA width/height, not BitMap
    # BytesPerRow*8 padding. A3 is private input, restored immediately.
    c.move(A(4),D(0)); c.imm('add',F['screen_w'],D(0))
    c.move(D(0),A(3))
    G('x',D(0)); G('y',D(1))
    c.move(M(4,16),D(3))             # stride
    c.move(M(4,8),D(4))              # width
    c.move(M(4,12),D(5))             # height
    c.move(M(4,20),D(6))             # depth
    c.move(M(4,24),D(7))             # bytes per plane
    B(1,'private_bob_blit_entry')
    G('saved_a3',A(3))
    c.tst(D(3)); B(7,'draw_reject')
    S(I(1),'result')

    L('draw_reject')
    G('result',D(3))
    c.raw('4fef0100')                # LEA 256(SP),SP
    c.raw('4cdf77f7')                # restore caller registers
    c.raw('74004e75')                # D2=0, RTS

    # Private painter already has its own balanced ABI and CPU guard.
    L('private_bob_blit_entry')
    c.labels['private_blit_build_bitmap'] = len(c.b) + painter_labels['private_blit_build_bitmap']
    c.labels['private_blit_clipped_ok'] = len(c.b) + painter_labels['ok']
    c.raw(painter.hex())
    raw = c.out()
    assert raw[:len(previous)] == previous
    assert c.labels['safe_bank_blit_entry'] == len(previous)
    assert c.labels['private_bob_blit_entry'] > c.labels['safe_bank_blit_entry']
    assert raw[c.labels['private_bob_blit_entry']:] == painter
    assert len(raw)<32766 and len(raw)%2 == 0
    return raw,c.labels


if __name__ == '__main__':
    from hashlib import sha256
    data, labels = emit_safe_bank_blit()
    print('M19 P0d PRIVATE MC68020 checked Safe->Blitter SOURCE ONLY',
          len(data), sha256(data).hexdigest(),
          'entry',labels['safe_bank_blit_entry'],
          'no AP20, .Lib, Runtime or Compiler Gate')
