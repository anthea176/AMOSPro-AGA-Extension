#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j stage 1: PRIVATE whole-frame AGBO image existence/geometry gate.

SOURCE ONLY. Preserve the exact P0i native BOBS bytes and all historical
AP20 tokens. Before any Chip staging or Blitter writes, this gate verifies
every active object's original bank stamp and scans the validated AGBO
directory to find the requested image and reject incompatible geometry.

This does NOT remove P0i's temporarily projected selected-bank shadow;
that requires new explicit-by-bank P0c staging/lookup AND P0d resolver
entrypoints. Full directory/Chip checks remain P0c's responsibility.
The private wrapper delegates to P0i ONLY after all 64 image checks pass.
No public Draw, installed Lib/ASC, WinUAE or true Compiler claim.
"""
from __future__ import annotations

from hashlib import sha256
from m68k_emit import Code,D,A,M,I
from amos_main_abi import main_index,rjsr
from m19_p0i_multibank_draw_emit import emit_multibank_paint,MAX_BOBS

GETADR=rjsr(main_index('Bnk.GetAdr'))
P0J_NATIVE_BYTES=18176
P0J_NATIVE_SHA256='a91a0b99a05811a7f333738e1327b90a90dfe1aa947ec712d4290f568b88f618'
FRAME_BYTES=160
RECORD_OFFSET=96
F=dict(ident=0,result=4,bank=8,image=12,ptr=16,count=20,
       remaining=24,entry=28,state=32,dir_bytes=36,payload_size=40,
       width=44,height=48,depth=52,stride=56,plane_bytes=60,
       pix_off=64,pix_len=68,mask_off=72,mask_len=76,flags=80,total=84)
assert RECORD_OFFSET+24<=FRAME_BYTES


def emit_image_preflight() -> tuple[bytes,dict[str,int]]:
    previous,previous_labels=emit_multibank_paint()
    c=Code()
    c.raw(previous.hex());c.labels.update(previous_labels)
    B,L=c.branch,c.label
    def S(src,name):c.move(src,M(2,F[name]))
    def G(name,dst):c.move(M(2,F[name]),dst)
    def dest():
        c.move(A(2),D(0))
        c.imm('add',RECORD_OFFSET,D(0))
        c.move(D(0),A(1))
    def checked_span(off_name,len_name):
        G(off_name,D(0));G('dir_bytes',D(1))
        c.alu('cmp',D(1),0);B(5,'img_gate_return')
        G('payload_size',D(1));G(len_name,D(7))
        c.alu('sub',D(7),1);B(5,'img_gate_return')
        c.alu('cmp',D(1),0);B(2,'img_gate_return')

    L('image_frame_preflight_entry')
    c.raw('48e7efee')             # preserve AMOS ABI
    c.raw('4fefff60')             # private 160-byte frame
    c.move(A(7),A(2))
    S(I(0),'result')

    # Check the real original AGA End, owner, CPU and all source-bank stamps
    # FIRST (P0h); no Chip allocation or DMA can precede this call.
    B(1,'frame_bank_preflight_entry')
    c.tst(D(3));B(7,'img_gate_return')
    c.move(M(5,0x1c8),D(0))
    S(D(0),'state')
    S(I(1),'ident')
    L('img_gate_next')
    G('ident',D(0))
    c.imm('cmp',MAX_BOBS,D(0))
    B(2,'img_gate_done')

    dest()
    G('ident',D(0))
    B(1,'relay_read_entry')
    c.tst(D(3))
    B(7,'img_gate_advance')         # inactive object, no source image

    dest()
    G('ident',D(0))
    B(1,'relay_checked_read_entry')
    c.tst(D(3));B(7,'img_gate_return')  # late bank mutation
    c.move(M(2,RECORD_OFFSET+0),D(0));S(D(0),'bank')
    c.move(M(2,RECORD_OFFSET+4),D(0));S(D(0),'image')

    # AMOS Bnk.GetAdr obtains the ORIGINAL bank, never selected shadow.
    # P0g has already verified owner, payload/generation and endpoints.
    G('bank',D(0))
    c.raw(GETADR.hex())
    c.move(A(0),D(0));S(D(0),'ptr')
    c.imm('cmp',24,D(0));B(3,'img_gate_return')
    c.imm('and',1,D(0));B(6,'img_gate_return')
    G('ptr',A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'img_gate_return')

    # At +8 is unsigned image count; entries of 40 bytes start at +32.
    G('ptr',A(0))
    c.move(I(0),D(0))
    c.move(M(0,8),D(0),'w')
    c.imm('cmp',1,D(0));B(5,'img_gate_return')
    c.imm('cmp',4096,D(0));B(2,'img_gate_return')
    S(D(0),'count')
    S(D(0),'remaining')
    c.word(0xc0fc);c.word(40)       # MULU.W #40,D0 => full 32-bit
    c.imm('add',32,D(0))
    S(D(0),'dir_bytes')
    G('ptr',A(0))
    c.move(M(0,20),D(1))          # AGBO validated payload length
    S(D(1),'payload_size')
    c.alu('cmp',D(1),0)
    B(2,'img_gate_return')         # directory longer than payload

    # Probe the complete directory's final byte before scanning its IDs.
    G('ptr',D(1))
    c.alu('add',D(1),0);B(5,'img_gate_return')
    c.quick(1,D(0),sub=True)
    c.move(D(0),A(1))
    c.raw('2c780004');c.call_os(-534)
    c.tst(D(0));B(7,'img_gate_return')
    G('ptr',D(0));c.imm('add',32,D(0))
    B(5,'img_gate_return')
    S(D(0),'entry')

    L('img_gate_scan')
    G('remaining',D(0));c.tst(D(0))
    B(7,'img_gate_return')          # image ID never found
    G('entry',A(0))
    c.move(I(0),D(0))
    c.move(M(0,0),D(0),'w')
    G('image',D(1))
    c.alu('cmp',D(1),0)
    B(7,'img_gate_found')
    G('entry',D(0))
    c.imm('add',40,D(0));B(5,'img_gate_return')
    S(D(0),'entry')
    G('remaining',D(0));c.quick(1,D(0),sub=True)
    S(D(0),'remaining')
    B(0,'img_gate_scan')

    L('img_gate_found')
    # Fully validate each USED image's geometry and payload spans.
    # P0c remains responsible for unused entries and planar padding.
    for name,offset,limit in (('width',2,4096),('height',4,4096),
                              ('depth',6,8),('stride',8,512)):
        G('entry',A(0))
        c.move(I(0),D(0));c.move(M(0,offset),D(0),'w')
        c.imm('cmp',1,D(0));B(5,'img_gate_return')
        c.imm('cmp',limit,D(0));B(2,'img_gate_return')
        S(D(0),name)

    G('state',A(0));c.move(M(0,28),D(1))
    G('depth',D(0));c.alu('cmp',D(1),0);B(6,'img_gate_return')
    G('width',D(0));c.imm('add',15,D(0))
    c.shift(0,4);c.shift(0,1,left=True)
    G('stride',D(1));c.alu('cmp',D(1),0);B(6,'img_gate_return')
    G('stride',D(0));G('height',D(1))
    c.word(0xc0c1)               # MULU.W D1,D0
    S(D(0),'plane_bytes')
    S(I(0),'total');G('depth',D(7))
    L('img_gate_depth_loop')
    G('total',D(0));G('plane_bytes',D(1))
    c.alu('add',D(1),0);B(5,'img_gate_return')
    S(D(0),'total');c.quick(1,D(7),sub=True)
    B(6,'img_gate_depth_loop')

    G('entry',A(0))
    c.move(M(0,12),D(0));S(D(0),'pix_off')
    c.move(M(0,16),D(0));S(D(0),'pix_len')
    c.move(M(0,20),D(0));S(D(0),'mask_off')
    c.move(M(0,24),D(0));S(D(0),'mask_len')
    c.move(I(0),D(0));c.move(M(0,10),D(0),'w')
    c.imm('cmp',1,D(0));B(2,'img_gate_return')
    S(D(0),'flags')
    G('pix_len',D(0));G('total',D(1))
    c.alu('cmp',D(1),0);B(6,'img_gate_return')
    checked_span('pix_off','pix_len')
    G('flags',D(0));c.tst(D(0))
    B(7,'img_gate_no_mask')
    G('mask_len',D(0));G('plane_bytes',D(1))
    c.alu('cmp',D(1),0);B(6,'img_gate_return')
    checked_span('mask_off','mask_len')
    B(0,'img_gate_advance')
    L('img_gate_no_mask')
    G('mask_off',D(0));c.tst(D(0));B(6,'img_gate_return')
    G('mask_len',D(0));c.tst(D(0));B(6,'img_gate_return')

    L('img_gate_advance')
    G('ident',D(0));c.quick(1,D(0))
    S(D(0),'ident')
    B(0,'img_gate_next')

    L('img_gate_done')
    S(I(1),'result')
    L('img_gate_return')
    G('result',D(3))
    c.raw('4fef00a0')            # release private frame
    c.raw('4cdf77f7')            # preserve AMOS registers
    c.raw('74004e75')            # D2=0; RTS

    # Frame draw is P0i byte-for-byte identical. No selection projection
    # occurs until AFTER all images pass this new private gate.
    L('routed_paint_prechecked_entry')
    c.raw('48e7efee')
    B(1,'image_frame_preflight_entry')
    c.tst(D(3));B(7,'img_gate_draw_return')
    B(1,'routed_paint_all_entry')
    L('img_gate_draw_return')
    c.raw('4cdf77f7')
    c.raw('74004e75')

    native=c.out()
    if (not native.startswith(previous)
            or c.labels['image_frame_preflight_entry']!=len(previous)
            or len(native)&1 or len(native)>=32766):
        raise ValueError('P0j source changed pinned P0i or exceeded PC16')
    if native.count(GETADR)!=previous.count(GETADR)+1:
        raise ValueError('P0j must use independently verified Bnk.GetAdr')
    if len(native)!=P0J_NATIVE_BYTES or sha256(native).hexdigest()!=P0J_NATIVE_SHA256:
        raise ValueError('P0j MC68020 native source byte-exact SHA drift')
    return native,c.labels


if __name__=='__main__':
    blob,labels=emit_image_preflight()
    print('M19 P0j MC68020 PRIVATE WHOLE-FRAME IMAGE GATE SOURCE ONLY',
          'native bytes',len(blob),'appended',len(blob)-labels['image_frame_preflight_entry'],
          'SHA256',sha256(blob).hexdigest(),
          'NO PUBLIC DRAW, NO DLL, NO WINUAE')
