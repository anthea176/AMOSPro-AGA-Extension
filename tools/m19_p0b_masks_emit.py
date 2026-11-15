#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0b source MC68020 Make/No AGA Bob Mask native entrypoints.

Uses the *validated P0a native unit source* and its private bank transaction,
not a decomposed binary. This emits a single BOBS unit prefix plus TWO public
entrypoints. No source generated in src/generated/; no library file is written.

Both operations first validate the complete AGBO directory, all ranges, planar
padding and selected bank identity. Only a private scratch payload is mutated.
The original AMOS DATA bank changes by a single transaction, retaining other
images/masks/pixels/hotspots. No AGA Bob Mask is a no-op when already opaque.
"""
from __future__ import annotations

from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr
from m19_p0a_get_bob_emit import emit_get_bob
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5
from m19_p0b_mask020_emit import emit_mask020

GETADR=rjsr(main_index('Bnk.GetAdr'))
MAX_SIZE=0x01000000
FRAME=256
K=('mode image_id colour bank bankptr head old_size old_count old_start old_gen '
   'cursor entry index last_id found target_plane_size target_mask_len target_width '
   'target_height target_depth target_stride new_size temp new_dir new_cursor '
   'width height depth stride plane_size pixlen masklen entry_id '
   'new_mask_len old_src return_value').split()
F={name:4*i for i,name in enumerate(K)}
assert len(K)==len(F) and len(K)*4 <= FRAME


def emit_mask_commands() -> tuple[bytes,dict[str,int]]:
    prior,labels=emit_get_bob()
    c=Code();c.raw(prior.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,k):c.move(src,M(2,F[k]))
    def G(k,dst):c.move(M(2,F[k]),dst)
    def reject():B(0,'m_fail')
    def check_add(reg,src):
        c.alu('add',src,reg);B(5,'m_fail') # BCS
    def osbase():c.raw('2c780004')  # MOVEA.L (4).W,A6
    def getbank():G('bank',D(0));c.raw(GETADR.hex())
    def memtype():osbase();c.call_os(-534)
    def copy(src,dst,n):
        c.move(src,A(0));c.move(dst,A(1));c.move(n,D(0))
        B(1,'copy_bytes')

    # Two separate AP20 entrypoints. MOVEM must occur before clobbering D0,
    # otherwise the return would corrupt an AMOS caller register.
    L('mask_make_entry')
    c.raw('48e7efee')
    c.move(I(1),D(0));B(0,'m_start')
    L('mask_no_entry')
    c.raw('48e7efee')
    c.move(I(0),D(0))
    L('m_start')
    c.raw('4fefff00')            # LEA -256(SP),SP
    c.move(A(7),A(2));S(D(0),'mode')
    c.move(I(0),M(2,F['temp']))
    c.move(I(0),M(2,F['return_value']))
    G('mode',D(0));c.tst(D(0));B(7,'m_args_no')
    S(D(3),'colour')
    c.move(POST(3),D(7));S(D(7),'image_id')
    B(0,'m_args_done')
    L('m_args_no')
    S(D(3),'image_id');S(I(0),'colour')
    L('m_args_done')
    c.move(I(0),D(3))
    # Validated MC68020 feature flag checked before AGBO or AMOS state use.
    c.raw('20780004')
    c.move(A(0),D(0));c.tst(D(0));B(7,'m_fail')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1)   # BTST #AFF_68020,D0
    B(7,'m_fail')
    G('image_id',D(0));c.imm('cmp',1,D(0));B(5,'m_fail')
    c.imm('cmp',4096,D(0));B(2,'m_fail')

    # Revalidate the selected AMOS bank and list head, mirroring Get AGA Bob.
    c.lea(0,'bank_active_state')
    c.move(M(0,0),D(0));c.imm('cmp',5,D(0));B(5,'m_fail')
    c.imm('cmp',65535,D(0));B(2,'m_fail');S(D(0),'bank')
    c.move(M(0,4),D(0));c.tst(D(0));B(7,'m_fail');S(D(0),'bankptr')
    c.move(M(0,8),D(0));c.tst(D(0));B(7,'m_fail');S(D(0),'head')
    c.move(M(5,CUR_BANKS_A5),D(0));G('head',D(1))
    c.alu('cmp',D(1),0);B(6,'m_fail')
    getbank();c.move(A(0),D(0));G('bankptr',D(1))
    c.alu('cmp',D(1),0);B(6,'m_fail')
    G('bankptr',D(0));c.imm('cmp',24,D(0));B(3,'m_fail')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'m_fail')
    c.move(D(0),A(4))
    c.move(M(4,-20),D(0));c.imm('cmp',48,D(0));B(5,'m_fail')
    c.imm('cmp',MAX_SIZE+16,D(0));B(2,'m_fail')
    c.imm('sub',16,D(0));S(D(0),'old_size')
    G('bankptr',A(4));c.move(A(4),A(1));memtype();c.tst(D(0));B(7,'m_fail')
    G('bankptr',D(0));G('old_size',D(1));check_add(0,D(1))
    c.quick(1,D(0),sub=True);c.move(D(0),A(1));memtype()
    c.tst(D(0));B(7,'m_fail')
    G('bankptr',A(4))
    c.move(M(4,-16),D(0));G('bank',D(1));c.alu('cmp',D(1),0);B(6,'m_fail')
    c.move(I(0),D(0));c.move(M(4,-12),D(0),'w')
    c.tst(D(0));B(7,'m_flags_ok')
    c.imm('and',0xfffd,D(0),'w');c.imm('cmp',1,D(0),'w');B(6,'m_fail')
    L('m_flags_ok')
    c.move(M(4,-8),D(0));c.imm('cmp',0x41474142,D(0));B(6,'m_fail')
    c.move(M(4,-4),D(0));c.imm('cmp',0x4f425320,D(0));B(6,'m_fail')
    c.move(M(4),D(0));c.imm('cmp',0x4147424f,D(0));B(6,'m_fail')
    c.move(I(0),D(0));c.move(M(4,4),D(0),'w');c.imm('cmp',1,D(0));B(6,'m_fail')
    c.tst(M(4,6),'w');B(6,'m_fail')
    c.move(I(0),D(0));c.move(M(4,8),D(0),'w');c.imm('cmp',4096,D(0));B(2,'m_fail')
    S(D(0),'old_count')
    c.move(I(0),D(0));c.move(M(4,10),D(0),'w');c.imm('cmp',40,D(0));B(6,'m_fail')
    c.move(M(4,12),D(0));c.imm('cmp',32,D(0));B(6,'m_fail')
    G('old_count',D(0));c.raw('c0fc0028');c.imm('add',32,D(0))
    c.alu('cmp',M(4,16),0);B(6,'m_fail')
    G('old_size',D(1));c.alu('cmp',D(1),0);B(2,'m_fail');S(D(0),'old_start')
    c.move(M(4,20),D(0));G('old_size',D(1));c.alu('cmp',D(1),0);B(6,'m_fail')
    c.move(M(4,24),D(0));c.tst(D(0));B(7,'m_fail');S(D(0),'old_gen')
    c.tst(M(4,28));B(6,'m_fail')
    G('old_start',D(0));S(D(0),'cursor')
    G('bankptr',D(0));c.imm('add',32,D(0));S(D(0),'entry')
    for k in ('index','last_id','found','target_mask_len'):
        c.move(I(0),M(2,F[k]))

    # Inspect EVERY image before staging, including padding and masks.
    L('m_check_entry')
    G('index',D(0));G('old_count',D(1));c.alu('cmp',D(1),0)
    B(12,'m_all_valid')
    G('entry',A(4))
    c.move(I(0),D(0));c.move(M(4),D(0),'w')
    G('last_id',D(1));c.alu('cmp',D(1),0);B(3,'m_fail')
    c.imm('cmp',4096,D(0));B(2,'m_fail');S(D(0),'last_id')
    for pos,k,upper in ((2,'width',4096),(4,'height',4096),(6,'depth',8)):
        c.move(I(0),D(0));c.move(M(4,pos),D(0),'w')
        c.imm('cmp',1,D(0));B(5,'m_fail')
        c.imm('cmp',upper,D(0));B(2,'m_fail');S(D(0),k)
    G('width',D(0));G('height',D(1));c.word(0xc0c1) # MULU.W D1,D0
    c.imm('cmp',0x400000,D(0));B(2,'m_fail')
    G('width',D(0));c.imm('add',15,D(0))
    c.shift(0,4,left=False);c.shift(0,1,left=True)
    G('entry',A(4));c.move(I(0),D(1));c.move(M(4,8),D(1),'w')
    c.alu('cmp',D(1),0);B(6,'m_fail');S(D(0),'stride')
    G('stride',D(0));G('height',D(1));c.word(0xc0c1)
    S(D(0),'plane_size')
    c.move(D(0),D(6));G('depth',D(5));c.move(I(0),D(7))
    L('m_sum_planes')
    c.alu('add',D(6),7);B(5,'m_fail')
    c.quick(1,D(5),sub=True);B(6,'m_sum_planes')
    G('entry',A(4));c.move(M(4,16),D(0));c.alu('cmp',D(7),0)
    B(6,'m_fail');S(D(0),'pixlen')
    G('cursor',D(0));c.alu('cmp',M(4,12),0);B(6,'m_fail')
    c.move(I(0),D(0));c.move(M(4,10),D(0),'w')
    c.imm('cmp',1,D(0));B(6,'m_unmasked')
    G('plane_size',D(1));c.move(M(4,24),D(0));c.alu('cmp',D(1),0)
    B(6,'m_fail')
    G('cursor',D(0));G('pixlen',D(1));check_add(0,D(1))
    c.alu('cmp',M(4,20),0);B(6,'m_fail')
    G('plane_size',D(0));S(D(0),'masklen');B(0,'m_mask_checked')
    L('m_unmasked')
    c.tst(D(0));B(6,'m_fail')
    c.tst(M(4,20));B(6,'m_fail')
    c.tst(M(4,24));B(6,'m_fail')
    c.move(I(0),M(2,F['masklen']))
    L('m_mask_checked')
    G('cursor',D(0));G('pixlen',D(1));check_add(0,D(1))
    G('masklen',D(1));check_add(0,D(1))
    G('old_size',D(1));c.alu('cmp',D(1),0);B(2,'m_fail');S(D(0),'cursor')
    G('entry',A(4));c.tst(M(4,32));B(6,'m_fail');c.tst(M(4,36));B(6,'m_fail')
    # Reuse P0a's independently CPU-validated padding checker.
    G('bankptr',D(0));G('entry',A(4));check_add(0,M(4,12))
    c.move(D(0),A(0));G('width',D(0));G('stride',D(1))
    G('height',D(2));G('depth',D(3));B(1,'check_padding')
    c.tst(D(0));B(7,'m_fail')
    G('masklen',D(0));c.tst(D(0));B(7,'m_padding_ok')
    G('bankptr',D(0));G('entry',A(4));check_add(0,M(4,20))
    c.move(D(0),A(0));G('width',D(0));G('stride',D(1))
    G('height',D(2));c.move(I(1),D(3));B(1,'check_padding')
    c.tst(D(0));B(7,'m_fail')
    L('m_padding_ok')
    G('entry',A(4));c.move(I(0),D(0));c.move(M(4),D(0),'w')
    G('image_id',D(1));c.alu('cmp',D(1),0);B(6,'m_not_target')
    c.move(I(1),M(2,F['found']))
    for frm,to in (('width','target_width'),('height','target_height'),
                   ('depth','target_depth'),('stride','target_stride'),
                   ('plane_size','target_plane_size'),('masklen','target_mask_len')):
        G(frm,D(0));S(D(0),to)
    G('mode',D(0));c.tst(D(0));B(7,'m_not_target')
    # C must be 0..(1<<image_depth)-1, rather than always 0..255.
    G('colour',D(7));c.tst(D(7));B(11,'m_fail')
    c.move(I(1),D(0));G('depth',D(1))
    L('m_colour_shift')
    c.shift(0,1,left=True)
    c.quick(1,D(1),sub=True);B(6,'m_colour_shift')
    c.alu('cmp',D(0),7);B(4,'m_fail')
    L('m_not_target')
    G('entry',D(0));c.imm('add',40,D(0));S(D(0),'entry')
    G('index',D(0));c.quick(1,D(0));S(D(0),'index')
    B(0,'m_check_entry')

    L('m_all_valid')
    G('cursor',D(0));G('old_size',D(1));c.alu('cmp',D(1),0);B(6,'m_fail')
    G('found',D(0));c.tst(D(0));B(7,'m_fail')
    G('mode',D(0));c.tst(D(0));B(6,'m_mutate')
    G('target_mask_len',D(0));c.tst(D(0));B(6,'m_mutate')
    # No AGA Bob Mask on an already opaque image is an ID-valid no-op.
    c.move(I(1),M(2,F['return_value']));B(0,'m_done')
    L('m_mutate')
    G('old_gen',D(0));c.imm('cmp',-1,D(0));B(7,'m_fail')
    G('old_size',D(0));G('target_mask_len',D(1))
    G('mode',D(2));c.tst(D(2));B(7,'m_remove_size')
    c.tst(D(1));B(6,'m_size_ok') # replace an existing mask: no size change
    G('target_plane_size',D(1));check_add(0,D(1));B(0,'m_size_ok')
    L('m_remove_size')
    c.alu('sub',D(1),0);B(11,'m_fail')
    L('m_size_ok')
    c.imm('cmp',MAX_SIZE,D(0));B(2,'m_fail')
    S(D(0),'new_size')
    c.move(I(0),D(1));c.move(I(0x10001),D(1));osbase();c.call_os(-684)
    c.tst(D(0));B(7,'m_fail')
    S(D(0),'temp')
    # Preserve header exactly except length/generation.
    G('bankptr',A(0));G('temp',A(1));c.move(I(32),D(0));B(1,'copy_bytes')
    G('temp',A(4))
    G('new_size',D(0));c.move(D(0),M(4,20))
    G('old_gen',D(0));c.quick(1,D(0));c.move(D(0),M(4,24))
    G('old_start',D(0));S(D(0),'cursor')
    G('bankptr',D(0));c.imm('add',32,D(0));S(D(0),'entry')
    G('temp',D(0));c.imm('add',32,D(0));S(D(0),'new_dir')
    G('temp',D(0));G('old_start',D(1));check_add(0,D(1));S(D(0),'new_cursor')
    c.move(I(0),M(2,F['index']))
    L('m_build_loop')
    G('index',D(0));G('old_count',D(1));c.alu('cmp',D(1),0);B(12,'m_build_complete')
    G('entry',A(0));G('new_dir',A(1));c.move(I(40),D(0));B(1,'copy_bytes')
    G('new_dir',A(4));G('new_cursor',D(0));G('temp',D(1))
    c.alu('sub',D(1),0);c.move(D(0),M(4,12))
    G('entry',A(4));c.move(M(4,16),D(0));S(D(0),'pixlen')
    c.move(M(4,24),D(0));S(D(0),'masklen')
    G('bankptr',D(0));G('cursor',D(1));check_add(0,D(1));S(D(0),'old_src')
    G('old_src',A(0));G('new_cursor',A(1));G('pixlen',D(0));B(1,'copy_bytes')
    G('entry',A(4));c.move(I(0),D(0));c.move(M(4,0),D(0),'w')
    G('image_id',D(1));c.alu('cmp',D(1),0);B(6,'m_copy_other_mask')
    # Selected image: replace/remove its independent mask.
    G('mode',D(0));c.tst(D(0));B(7,'m_remove_entry_mask')
    G('new_dir',A(4));c.move(I(1,'w'),M(4,10),'w')
    G('target_plane_size',D(0));S(D(0),'new_mask_len')
    c.move(D(0),M(4,24))
    G('new_cursor',D(0));G('pixlen',D(1));check_add(0,D(1))
    G('temp',D(1));c.alu('sub',D(1),0);c.move(D(0),M(4,20))
    # Compute the mask from STAGED copied planes, not original AMOS DATA.
    G('new_cursor',A(0));G('new_cursor',D(0));G('pixlen',D(1))
    check_add(0,D(1));c.move(D(0),A(1))
    G('target_width',D(0));G('target_height',D(1))
    G('target_depth',D(2));G('colour',D(3));G('target_stride',D(4))
    B(1,'mask_kernel')
    c.tst(D(3));B(7,'m_fail')
    B(0,'m_advance')
    L('m_remove_entry_mask')
    G('new_dir',A(4));c.move(I(0,'w'),M(4,10),'w')
    c.move(I(0),M(4,20));c.move(I(0),M(4,24))
    c.move(I(0),M(2,F['new_mask_len']))
    B(0,'m_advance')
    L('m_copy_other_mask')
    G('masklen',D(0));S(D(0),'new_mask_len')
    c.tst(D(0));B(7,'m_other_opaque')
    G('old_src',D(0));G('pixlen',D(1));check_add(0,D(1))
    c.move(D(0),A(0));G('new_cursor',D(0));G('pixlen',D(1))
    check_add(0,D(1));c.move(D(0),A(1))
    G('masklen',D(0));B(1,'copy_bytes')
    G('new_dir',A(4));G('new_cursor',D(0));G('pixlen',D(1))
    check_add(0,D(1));G('temp',D(1));c.alu('sub',D(1),0)
    c.move(D(0),M(4,20));B(0,'m_advance')
    L('m_other_opaque')
    G('new_dir',A(4));c.move(I(0),M(4,20))
    L('m_advance')
    G('new_cursor',D(0));G('pixlen',D(1));check_add(0,D(1))
    G('new_mask_len',D(1));check_add(0,D(1));S(D(0),'new_cursor')
    G('cursor',D(0));G('pixlen',D(1));check_add(0,D(1))
    G('masklen',D(1));check_add(0,D(1));S(D(0),'cursor')
    G('entry',D(0));c.imm('add',40,D(0));S(D(0),'entry')
    G('new_dir',D(0));c.imm('add',40,D(0));S(D(0),'new_dir')
    G('index',D(0));c.quick(1,D(0));S(D(0),'index')
    B(0,'m_build_loop')
    L('m_build_complete')
    G('new_cursor',D(0));G('temp',D(1));c.alu('sub',D(1),0)
    G('new_size',D(1));c.alu('cmp',D(1),0);B(6,'m_fail')
    # Commit by the already CPU-tested AMOS list transaction.
    G('temp',A(0));G('new_size',D(1));G('bank',D(3))
    B(1,'bank_commit')
    c.tst(D(3));B(7,'m_fail')
    getbank();c.move(A(0),D(0));c.tst(D(0));B(7,'m_fail')
    c.lea(0,'bank_active_state');c.move(D(0),M(0,4))
    G('head',D(1));c.move(D(1),M(0,8))
    c.move(I(1),M(2,F['return_value']))
    L('m_fail')
    L('m_done')
    G('temp',A(1));c.move(A(1),D(0));c.tst(D(0));B(7,'m_no_scratch')
    osbase();c.call_os(-690)
    L('m_no_scratch')
    G('return_value',D(3))
    c.raw('4fef0100')  # LEA +256(SP),SP
    c.raw('4cdf77f7')  # restore original caller registers
    c.raw('74004e75')  # D2=0, RTS

    # Self-contained private CPU020 BFEXTU kernel, including its 16-word tail
    # table. Internal PC-relative branch offsets are relocation-invariant.
    L('mask_kernel')
    mask,_=emit_mask020()
    c.raw(mask.hex())
    full=c.out()
    assert len(full)%2==0
    assert full[:len(prior)]==prior
    assert full[c.labels['mask_kernel']:] == mask
    assert c.labels['mask_make_entry']<c.labels['mask_no_entry']<c.labels['mask_kernel']
    return full,c.labels

if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_mask_commands()
    print('M19 P0b native MC68020 make/no mask source',len(raw),sha256(raw).hexdigest(),
          {k:labels[k] for k in ('mask_make_entry','mask_no_entry','mask_kernel')})
