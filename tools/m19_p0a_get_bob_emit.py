"""M19 P0a R88-only native Get AGA Bob capture; not an installed AMOS command.

AMOS Professional syntax (proposed): Get AGA Bob I,X1,Y1,X2,Y2
IN D3=Y2, A3 pops X2,Y1,X1,I.  OUT D2=0, D3=1/0.

In the R88-derived BOBS group, this routine shares Aga Bob Bank's PC-relative
active_state and its private non-destructive bank-transaction entry.

Stage, validate and *only then publish* a complete AGBO v1 DATA payload.
Read only the inactive Safe AGA ScreenBuffer. No screen/Blitter writes.
No reuse of R89+ implementation or test fixtures.
"""
from __future__ import annotations
from m68k_emit import Code, D, A, M, POST, I
from amos_main_abi import main_index, rjsr
from m19_p0a_bank_select_emit import emit_bank_select
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5

STATE_PTR=0x1C8
GETADR=rjsr(main_index('Bnk.GetAdr'))
MAX_SIZE=0x01000000
MAGIC=0x4147424F
HEADER=32
ENTRY=40
FRAME=320
K=(
 'img_id x1 y1 x2 y2 bank bankptr head old_size old_count old_start old_gen '
 'old_replaced old_last old_cursor old_entry old_stride old_depth old_height '
 'old_pixlen old_masklen old_total new_count new_size new_start '
 'width height depth dst_stride plane_bytes capture_bytes '
 'state db bitmap src_stride screen_w screen_h src_row0 src_bit0 '
 'temp new_dir new_cursor inserted old_index new_root '
 'src_plane_ref src_plane_base dst_plane_base src_row dst_row '
 'planes_left rows_left pixels_left cursor scan_id old_node '
 'return_value pad_last old_limit scanned_len'
).split()
F={name:4*i for i,name in enumerate(K)}
assert len(K)==len(F) and 4*len(K)<=FRAME


def emit_get_bob():
    bank_code,bank_labels=emit_bank_select()
    c=Code(); c.raw(bank_code.hex())
    c.labels.update({'bank_'+key:value for key,value in bank_labels.items()})
    B,L=c.branch,c.label
    def S(r,k):c.move(r,M(2,F[k]))
    def G(k,r):c.move(M(2,F[k]),r)
    def nz(r,to='fail'):
        c.move(r,D(0));c.tst(D(0));B(7,to)
    def osbase():c.raw('2c780004') # MOVEA.L (4).W,A6
    def mem_chip(r):
        c.move(r,A(1));osbase();c.call_os(-534)
        c.imm('and',2,D(0));c.tst(D(0));B(7,'fail')
    def check_add(r,src,to='fail'):
        c.alu('add',src,r);B(5,to)
    L('get_entry')
    c.raw('48e7efee')
    c.raw('4feffec0') # LEA -320(SP),SP
    c.move(A(7),A(2))
    S(D(3),'y2')
    for field in ('x2','y1','x1','img_id'):
        c.move(POST(3),D(7));S(D(7),field)
    c.move(I(0),M(2,F['temp']))
    c.move(I(0),M(2,F['return_value']))
    c.move(I(0),D(3))

    G('img_id',D(0));c.imm('cmp',1,D(0));B(5,'fail')
    c.imm('cmp',4096,D(0));B(2,'fail')
    for coord in ('x1','y1','x2','y2'):
        G(coord,D(0));c.tst(D(0));B(11,'fail')
        c.imm('cmp',4096,D(0));B(2,'fail')
    G('x1',D(0));G('x2',D(1));c.alu('cmp',D(0),1);B(5,'fail')
    G('y1',D(0));G('y2',D(1));c.alu('cmp',D(0),1);B(5,'fail')

    # Bank selection must be live in the currently running AMOS program.
    c.lea(0,'bank_active_state')
    c.move(M(0,0),D(0));c.imm('cmp',5,D(0));B(5,'fail')
    c.imm('cmp',65535,D(0));B(2,'fail');S(D(0),'bank')
    c.move(M(0,4),D(0));c.tst(D(0));B(7,'fail');S(D(0),'bankptr')
    c.move(M(0,8),D(0));c.tst(D(0));B(7,'fail');S(D(0),'head')
    c.move(M(5,CUR_BANKS_A5),D(0));G('head',D(1))
    c.alu('cmp',D(1),0);B(6,'fail')
    G('bank',D(0));c.raw(GETADR.hex())
    c.move(A(0),D(0));G('bankptr',D(1));c.alu('cmp',D(1),0)
    B(6,'fail')
    G('bankptr',D(0));c.imm('cmp',24,D(0));B(3,'fail')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'fail')
    c.move(D(0),A(4))
    c.move(M(4,-20),D(0));c.imm('cmp',48,D(0));B(5,'fail')
    c.imm('cmp',MAX_SIZE+16,D(0));B(2,'fail')
    c.imm('sub',16,D(0));S(D(0),'old_size')
    G('bankptr',D(0));c.imm('sub',24,D(0));c.move(D(0),A(1));
    osbase();c.call_os(-534);c.tst(D(0));B(7,'fail')
    G('bankptr',D(0));G('old_size',D(1));check_add(0,D(1))
    c.quick(1,D(0),sub=True);c.move(D(0),A(1));
    osbase();c.call_os(-534);c.tst(D(0));B(7,'fail')
    G('bankptr',A(4))
    c.move(M(4,-16),D(0));G('bank',D(1));c.alu('cmp',D(1),0);B(6,'fail')
    c.move(I(0),D(0));c.move(M(4,-12),D(0),'w')
    c.tst(D(0));B(7,'old_flags_good')
    c.imm('and',0xfffd,D(0),'w');c.imm('cmp',1,D(0),'w');B(6,'fail')
    L('old_flags_good')
    c.move(M(4,-8),D(0));c.imm('cmp',0x41474142,D(0));B(6,'fail')
    c.move(M(4,-4),D(0));c.imm('cmp',0x4F425320,D(0));B(6,'fail')
    c.move(M(4,0),D(0));c.imm('cmp',MAGIC,D(0));B(6,'fail')
    c.move(I(0),D(0));c.move(M(4,4),D(0),'w');c.imm('cmp',1,D(0));B(6,'fail')
    c.tst(M(4,6),'w');B(6,'fail')
    c.move(I(0),D(0));c.move(M(4,8),D(0),'w')
    c.imm('cmp',4096,D(0));B(2,'fail');S(D(0),'old_count')
    c.move(I(0),D(0));c.move(M(4,10),D(0),'w')
    c.imm('cmp',ENTRY,D(0));B(6,'fail')
    c.move(M(4,12),D(0));c.imm('cmp',HEADER,D(0));B(6,'fail')
    G('old_count',D(0));c.raw('c0fc0028')  # MULU.W #40,D0
    c.imm('add',HEADER,D(0));G('bankptr',A(4));
    c.alu('cmp',M(4,16),0);B(6,'fail')
    G('old_size',D(1));c.alu('cmp',D(1),0);B(2,'fail');S(D(0),'old_start')
    c.move(M(4,20),D(0));G('old_size',D(1));c.alu('cmp',D(1),0);B(6,'fail')
    c.move(M(4,24),D(0));c.tst(D(0));B(7,'fail')
    c.imm('cmp',-1,D(0));B(7,'fail') # generation exhausted
    S(D(0),'old_gen')
    c.tst(M(4,28));B(6,'fail')
    c.move(I(0),M(2,F['old_replaced']))
    c.move(I(0),M(2,F['old_last']))
    G('old_start',D(0));S(D(0),'old_cursor')
    G('bankptr',D(0));c.imm('add',HEADER,D(0));S(D(0),'old_entry')
    c.move(I(0),M(2,F['old_index']))

    # Strict full AGBO directory and original data / masks padding validation.
    L('validate_old_loop')
    G('old_index',D(0));G('old_count',D(1));c.alu('cmp',D(1),0)
    B(12,'old_validated')
    G('old_entry',A(4))
    c.move(I(0),D(0));c.move(M(4,0),D(0),'w')
    G('old_last',D(1));c.alu('cmp',D(1),0);B(3,'fail')
    c.imm('cmp',4096,D(0));B(2,'fail');S(D(0),'old_last')
    G('img_id',D(1));c.alu('cmp',D(1),0);B(6,'not_replaced')
    c.move(I(1),M(2,F['old_replaced']))
    L('not_replaced')
    for pos,key in ((2,'old_stride'),(4,'old_height'),(6,'old_depth')):
        c.move(I(0),D(0));c.move(M(4,pos),D(0),'w')
        c.imm('cmp',1,D(0));B(5,'fail')
        c.imm('cmp',8 if key=='old_depth' else 4096,D(0));B(2,'fail')
        S(D(0),key)
    # Every stored image also satisfies the host model's 4 Mi-pixel ceiling.
    G('old_stride',D(0));G('old_height',D(1));c.word(0xc0c1)
    c.imm('cmp',0x400000,D(0));B(2,'fail')
    # Compute exact expected row stride from old image width.
    G('old_stride',D(0));c.imm('add',15,D(0))
    c.shift(0,4,left=False);c.shift(0,1,left=True)
    c.move(I(0),D(1));c.move(M(4,8),D(1),'w')
    c.alu('cmp',D(1),0);B(6,'fail');S(D(0),'old_stride')
    c.move(I(0),D(0));c.move(M(4,10),D(0),'w')
    c.imm('and',0xfffe,D(0));c.tst(D(0));B(6,'fail')
    # plane_bytes = row_stride * height; then multiply by depth using sum.
    G('old_stride',D(0));G('old_height',D(1));c.word(0xc0c1)
    c.move(D(0),D(6));G('old_depth',D(5));c.move(I(0),D(7))
    L('old_depth_sum')
    c.alu('add',D(6),7);B(5,'fail')
    c.quick(1,D(5),sub=True);B(6,'old_depth_sum')
    G('old_entry',A(4));c.move(M(4,16),D(0));c.alu('cmp',D(7),0);B(6,'fail')
    S(D(7),'old_pixlen')
    G('old_cursor',D(0));c.alu('cmp',M(4,12),0);B(6,'fail')
    c.move(M(4,24),D(0));c.tst(D(0));B(7,'no_mask')
    # mask flag 1 => exact one-plane payload, contiguous.
    c.move(I(0),D(0));c.move(M(4,10),D(0),'w')
    c.imm('cmp',1,D(0));B(6,'fail')
    c.move(M(4,24),D(0));c.alu('cmp',D(6),0);B(6,'fail')
    G('old_cursor',D(0));G('old_pixlen',D(1));check_add(0,D(1))
    c.alu('cmp',M(4,20),0);B(6,'fail')
    S(D(6),'old_masklen');B(0,'mask_checked')
    L('no_mask')
    c.tst(M(4,20));B(6,'fail')
    c.move(I(0),D(0));c.move(M(4,10),D(0),'w')
    c.tst(D(0));B(6,'fail')
    c.move(I(0),M(2,F['old_masklen']))
    L('mask_checked')
    G('old_cursor',D(0));G('old_pixlen',D(1));check_add(0,D(1))
    G('old_masklen',D(1));check_add(0,D(1))
    G('old_size',D(1));c.alu('cmp',D(1),0);B(2,'fail')
    S(D(0),'old_cursor')
    # Reserved fields must be zero even when old bank was loaded from disk.
    G('old_entry',A(4));c.tst(M(4,32));B(6,'fail')
    c.tst(M(4,36));B(6,'fail')
    # Verify trailing unused bits in every word, for both planes and mask.
    G('bankptr',A(0));G('old_entry',A(4))
    c.move(M(4,12),D(0));c.alu('add',A(0),0)
    c.move(D(0),A(0))
    c.move(I(0),D(0));c.move(M(4,2),D(0),'w')
    G('old_stride',D(1));G('old_height',D(2));G('old_depth',D(3))
    B(1,'check_padding');c.tst(D(0));B(7,'fail')
    G('old_masklen',D(0));c.tst(D(0));B(7,'padding_ok')
    G('bankptr',D(0));G('old_entry',A(4));check_add(0,M(4,20))
    c.move(D(0),A(0))
    c.move(I(0),D(0));c.move(M(4,2),D(0),'w')
    G('old_stride',D(1));G('old_height',D(2));c.move(I(1),D(3))
    B(1,'check_padding');c.tst(D(0));B(7,'fail')
    L('padding_ok')
    # Old replaced image size is removed from the target payload size.
    G('old_entry',A(4))
    c.move(I(0),D(0));c.move(M(4,0),D(0),'w')
    G('img_id',D(1));c.alu('cmp',D(1),0);B(6,'not_replaced_size')
    G('old_pixlen',D(0));G('old_masklen',D(1));check_add(0,D(1))
    S(D(0),'old_total');
    L('not_replaced_size')
    G('old_entry',D(0));c.imm('add',ENTRY,D(0));S(D(0),'old_entry')
    G('old_index',D(0));c.quick(1,D(0));S(D(0),'old_index')
    B(0,'validate_old_loop')
    L('old_validated')
    G('old_cursor',D(0));G('old_size',D(1));c.alu('cmp',D(1),0);B(6,'fail')

    # Verify live AGA screen and inactive back buffer BEFORE allocating output.
    c.move(M(5,STATE_PTR),A(4));nz(A(4));S(A(4),'state')
    for pos in (0,8,32):
        c.move(M(4,pos),D(0));c.tst(D(0));B(7,'fail')
    for pos,key in ((12,'screen_w'),(16,'screen_h'),(28,'depth')):
        c.move(M(4,pos),D(0));c.imm('cmp',1,D(0));B(5,'fail')
        c.imm('cmp',8 if key=='depth' else 4096,D(0));B(2,'fail')
        S(D(0),key)
    G('x2',D(0));G('screen_w',D(1));c.alu('cmp',D(1),0);B(12,'fail')
    G('y2',D(0));G('screen_h',D(1));c.alu('cmp',D(1),0);B(12,'fail')
    G('x2',D(0));G('x1',D(1));c.alu('sub',D(1),0);c.quick(1,D(0));S(D(0),'width')
    G('y2',D(0));G('y1',D(1));c.alu('sub',D(1),0);c.quick(1,D(0));S(D(0),'height')
    G('width',D(0));G('height',D(1));c.word(0xc0c1)
    c.imm('cmp',0x400000,D(0));B(2,'fail')
    G('width',D(0));c.imm('add',15,D(0))
    c.shift(0,4,left=False);c.shift(0,1,left=True);S(D(0),'dst_stride')
    G('height',D(1));c.word(0xc0c1);S(D(0),'plane_bytes')
    G('depth',D(5));c.move(D(0),D(6));c.move(I(0),D(0))
    L('new_depth_sum')
    c.alu('add',D(6),0);B(5,'fail')
    c.quick(1,D(5),sub=True);B(6,'new_depth_sum')
    S(D(0),'capture_bytes')
    # Calculate new payload size before allocation; fail on overflow, >16MiB.
    G('old_count',D(0));G('old_replaced',D(1));c.imm('cmp',0,D(1));B(6,'count_done')
    c.quick(1,D(0));
    L('count_done')
    c.imm('cmp',4096,D(0));B(2,'fail');S(D(0),'new_count')
    c.raw('c0fc0028') ;c.imm('add',HEADER,D(0));S(D(0),'new_start')
    G('old_size',D(0));G('old_replaced',D(1));c.tst(D(1));B(6,'subtract_old')
    c.imm('add',ENTRY,D(0));B(5,'fail')
    B(0,'add_capture')
    L('subtract_old')
    G('old_total',D(1));c.alu('sub',D(1),0);B(11,'fail')
    L('add_capture')
    G('capture_bytes',D(1));check_add(0,D(1))
    c.imm('cmp',MAX_SIZE,D(0));B(2,'fail');S(D(0),'new_size')

    G('state',A(4));c.move(M(4,32),A(0));S(A(0),'db')
    c.move(M(0,8),D(0));c.tst(D(0));B(7,'front_zero')
    c.imm('cmp',1,D(0));B(6,'fail')
    G('db',A(0));c.move(M(0),A(1));B(0,'back_found')
    L('front_zero')
    G('db',A(0));c.move(M(0,4),A(1))
    L('back_found')
    nz(A(1));c.move(M(1),A(0));nz(A(0));S(A(0),'bitmap')
    c.move(I(0),D(0));c.move(M(0),D(0),'w')
    c.imm('cmp',2,D(0));B(5,'fail')
    c.imm('cmp',65534,D(0));B(2,'fail')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'fail')
    S(D(0),'src_stride')
    c.shift(0,3,left=True);G('screen_w',D(1));c.alu('cmp',D(1),0);B(5,'fail')
    G('bitmap',A(0));c.move(I(0),D(0));c.move(M(0,2),D(0),'w')
    G('screen_h',D(1));c.alu('cmp',D(1),0);B(5,'fail')
    c.move(I(0),D(0));c.move(M(0,5),D(0),'b')
    G('depth',D(1));c.alu('cmp',D(1),0);B(6,'fail')
    G('x1',D(0));c.shift(0,3,left=False)
    G('y1',D(1));G('src_stride',D(5));c.word(0xc2c5) # MULU.W D5,D1
    check_add(1,D(0));S(D(1),'src_row0')
    G('x1',D(0));c.imm('and',7,D(0));c.move(I(7),D(1))
    c.alu('sub',D(0),1);S(D(1),'src_bit0')
    # Validate physical source Chip memory boundaries for ALL source planes.
    G('bitmap',A(4));c.quick(8,A(4));G('depth',D(6))
    L('check_chip_loop')
    c.move(POST(4),D(7));c.tst(D(7));B(7,'fail')
    c.imm('cmp',-1,D(7));B(7,'fail')
    c.move(D(7),D(0));c.imm('and',1,D(0));B(6,'fail')
    c.move(D(7),D(0));G('src_row0',D(1));check_add(0,D(1))
    c.move(D(0),A(1));osbase();c.call_os(-534)
    c.imm('and',2,D(0));c.tst(D(0));B(7,'fail')
    G('y2',D(0));G('src_stride',D(1));c.word(0xc0c1)
    G('x2',D(1));c.shift(1,3,left=False);check_add(0,D(1))
    check_add(0,D(7));c.move(D(0),A(1));osbase();c.call_os(-534)
    c.imm('and',2,D(0));c.tst(D(0));B(7,'fail')
    c.quick(1,D(6),sub=True);B(6,'check_chip_loop')

    # Safe, and wait for all preceding graphics Blitter writes to complete.
    G('db',A(4));c.move(M(4,20),D(0));c.imm('and',1,D(0))
    B(7,'safe_ready')
    c.move(M(4,12),A(0));nz(A(0))
    osbase();c.call_os(-372);c.tst(D(0));B(7,'fail')
    G('db',A(4));c.move(M(4,20),D(0));
    c.imm('and',0xfffffffe,D(0));c.move(D(0),M(4,20))
    L('safe_ready')
    G('state',A(4));c.move(M(4,8),A(6));c.call_os(-228)

    # Private scratch AGBO payload: no numbered intermediary AMOS bank.
    G('new_size',D(0));c.move(I(0x10001),D(1))
    osbase();c.call_os(-684)
    c.tst(D(0));B(7,'fail');S(D(0),'temp');S(D(0),'new_root')
    c.move(D(0),A(4));
    c.move(I(MAGIC),M(4,0))
    c.move(I(1,'w'),M(4,4),'w');c.move(I(0,'w'),M(4,6),'w')
    G('new_count',D(0));c.move(D(0),M(4,8),'w')
    c.move(I(ENTRY,'w'),M(4,10),'w')
    c.move(I(HEADER),M(4,12))
    G('new_start',D(0));c.move(D(0),M(4,16))
    G('new_size',D(0));c.move(D(0),M(4,20))
    G('old_gen',D(0));c.quick(1,D(0));c.move(D(0),M(4,24))
    c.move(I(0),M(4,28))
    G('temp',D(0));c.imm('add',HEADER,D(0));S(D(0),'new_dir')
    G('temp',D(0));G('new_start',D(1));check_add(0,D(1));S(D(0),'new_cursor')
    c.move(I(0),M(2,F['inserted']))
    G('bankptr',D(0));c.imm('add',HEADER,D(0));S(D(0),'old_entry')
    c.move(I(0),M(2,F['old_index']))

    L('build_entries')
    G('old_index',D(0));G('old_count',D(1));c.alu('cmp',D(1),0)
    B(12,'after_old_entries')
    G('old_entry',A(4));c.move(I(0),D(0));c.move(M(4),D(0),'w')
    S(D(0),'scan_id')
    G('img_id',D(1));c.alu('cmp',D(1),0)
    B(5,'maybe_insert_before')   # scan_id < target? copy old
    B(7,'replace_here')          # equal (BEQ, never BNE)
    # scan_id > target: insert first, then copy old.
    G('inserted',D(0));c.tst(D(0));B(6,'copy_old_entry')
    B(1,'emit_new_entry')
    L('maybe_insert_before')
    B(0,'copy_old_entry')
    L('replace_here')
    B(1,'emit_new_entry')
    B(0,'advance_old')
    L('copy_old_entry')
    B(1,'emit_copy_old')
    L('advance_old')
    G('old_entry',D(0));c.imm('add',ENTRY,D(0));S(D(0),'old_entry')
    G('old_index',D(0));c.quick(1,D(0));S(D(0),'old_index')
    B(0,'build_entries')
    L('after_old_entries')
    G('inserted',D(0));c.tst(D(0));B(6,'finished_entries')
    B(1,'emit_new_entry')
    L('finished_entries')
    G('new_cursor',D(0));G('temp',D(1));c.alu('sub',D(1),0)
    G('new_size',D(1));c.alu('cmp',D(1),0);B(6,'fail')

    # Prevalidated scratch goes to atomic private AMOS transaction. It
    # verifies original bank identity again after any memory allocation.
    G('temp',A(0));G('new_size',D(1));G('bank',D(3))
    B(1,'bank_commit')
    c.tst(D(3));B(7,'fail')
    G('bank',D(0));c.raw(GETADR.hex())
    c.move(A(0),D(0));c.tst(D(0));B(7,'fail')
    c.lea(0,'bank_active_state')
    c.move(D(0),M(0,4))
    G('head',D(1));c.move(D(1),M(0,8))
    c.move(I(1),M(2,F['return_value']))
    B(0,'done')

    L('fail')
    L('done')
    G('temp',A(1));c.move(A(1),D(0));c.tst(D(0));B(7,'no_scratch')
    osbase();c.call_os(-690)
    L('no_scratch')
    G('return_value',D(3))
    c.raw('4fef0140') # LEA +320(SP),SP
    c.raw('4cdf77f7')
    c.raw('74004e75')

    # Internal routine: validate unreferenced zero bits at the end of every
    # planar row.  A0=planes, D0=width, D1=stride, D2=rows, D3=plane count.
    # Return D0=1 on valid, 0 otherwise, no reads beyond exact image length.
    L('check_padding')
    c.move(D(0),D(5));c.imm('and',15,D(5))
    c.tst(D(5));B(7,'padding_accept')
    c.move(I(0xffff,'w'),D(4),'w')
    L('padding_shift')
    c.raw('e24c')        # LSR.W #1,D4
    c.quick(1,D(5),sub=True);B(6,'padding_shift')
    c.move(D(2),D(6));c.word(0xccc3) # MULU.W D3,D6
    c.move(A(0),A(1));c.alu('add',D(1),1);c.quick(2,A(1),sub=True)
    L('padding_loop')
    c.move(I(0),D(7));c.move(M(1),D(7),'w')
    c.alu('and',D(4),7,'w');c.tst(D(7),'w');B(6,'padding_reject')
    c.alu('add',D(1),1)
    c.quick(1,D(6),sub=True);B(6,'padding_loop')
    L('padding_accept')
    c.move(I(1),D(0));c.raw('4e75')
    L('padding_reject')
    c.move(I(0),D(0));c.raw('4e75')

    # Helper: copy D0 even bytes from A0 to A1; clobbers D0,D6 only.
    L('copy_bytes')
    c.move(D(0),D(6));c.shift(6,2,left=False)
    c.tst(D(6));B(7,'copy_tail')
    L('copy_long_loop')
    c.move(POST(0),POST(1))
    c.quick(1,D(6),sub=True);B(6,'copy_long_loop')
    L('copy_tail')
    c.imm('and',2,D(0));c.tst(D(0));B(7,'copy_return')
    c.move(POST(0),POST(1),'w')
    L('copy_return')
    c.raw('4e75')

    # Copy an existing well-formed entry and its entire pixel+mask block.
    L('emit_copy_old')
    G('old_entry',A(0));G('new_dir',A(1));c.move(I(10),D(6))
    L('copy_entry_longs')
    c.move(POST(0),POST(1))
    c.quick(1,D(6),sub=True);B(6,'copy_entry_longs')
    G('new_dir',A(4))
    G('new_cursor',D(0));G('temp',D(1));c.alu('sub',D(1),0)
    c.move(D(0),M(4,12))
    G('old_entry',A(0));c.move(M(0,16),D(5))
    c.move(M(0,24),D(7))
    c.tst(D(7));B(7,'copied_mask_offset')
    G('new_cursor',D(0));c.alu('add',D(5),0)
    G('temp',D(1));c.alu('sub',D(1),0)
    c.move(D(0),M(4,20))
    L('copied_mask_offset')
    G('old_entry',A(0));G('bankptr',D(0));c.alu('add',M(0,12),0)
    c.move(D(0),A(0));G('new_cursor',A(1))
    G('old_entry',A(4));c.move(M(4,16),D(0));c.alu('add',M(4,24),0)
    B(1,'copy_bytes')
    G('old_entry',A(4));c.move(M(4,16),D(0));c.alu('add',M(4,24),0)
    G('new_cursor',D(1));c.alu('add',D(0),1);S(D(1),'new_cursor')
    G('new_dir',D(1));c.imm('add',ENTRY,D(1));S(D(1),'new_dir')
    c.raw('4e75')

    # Capture current image, always WITHOUT mask. Other images keep their
    # exact masks, hotspots, pixel data and bitplane depths.
    L('emit_new_entry')
    G('new_dir',A(4))
    G('img_id',D(0));c.move(D(0),M(4,0),'w')
    G('width',D(0));c.move(D(0),M(4,2),'w')
    G('height',D(0));c.move(D(0),M(4,4),'w')
    G('depth',D(0));c.move(D(0),M(4,6),'w')
    G('dst_stride',D(0));c.move(D(0),M(4,8),'w')
    c.move(I(0,'w'),M(4,10),'w')
    G('new_cursor',D(0));G('temp',D(1));c.alu('sub',D(1),0)
    c.move(D(0),M(4,12))
    G('capture_bytes',D(0));c.move(D(0),M(4,16))
    for o in (20,24,32,36):c.move(I(0),M(4,o))
    for o in (28,30):c.move(I(0,'w'),M(4,o),'w')
    G('bitmap',D(0));c.imm('add',8,D(0));S(D(0),'src_plane_ref')
    G('new_cursor',D(0));S(D(0),'dst_plane_base')
    G('depth',D(0));S(D(0),'planes_left')
    L('capture_plane')
    G('src_plane_ref',A(4));c.move(POST(4),D(0));S(D(0),'src_plane_base')
    S(A(4),'src_plane_ref')
    G('dst_plane_base',D(0));S(D(0),'dst_row')
    G('src_row0',D(0));S(D(0),'src_row')
    G('height',D(0));S(D(0),'rows_left')
    L('capture_row')
    G('src_plane_base',D(0));G('src_row',D(1));c.alu('add',D(1),0)
    c.move(D(0),A(0));G('dst_row',A(1))
    G('src_bit0',D(1));c.move(I(7),D(2))
    G('width',D(7))
    L('capture_pixel')
    c.move(I(0),D(0));c.move(M(0),D(0),'b')
    c.word(0x0300)      # BTST D1,D0
    B(7,'capture_pixel_empty')
    c.word(0x05d1)      # BSET D2,(A1), 68k memory byte bit
    L('capture_pixel_empty')
    c.quick(1,D(1),sub=True);B(10,'src_bit_positive')
    c.quick(1,A(0));c.move(I(7),D(1))
    L('src_bit_positive')
    c.quick(1,D(2),sub=True);B(10,'dst_bit_positive')
    c.quick(1,A(1));c.move(I(7),D(2))
    L('dst_bit_positive')
    c.quick(1,D(7),sub=True);B(6,'capture_pixel')
    G('src_row',D(0));G('src_stride',D(1));c.alu('add',D(1),0);S(D(0),'src_row')
    G('dst_row',D(0));G('dst_stride',D(1));c.alu('add',D(1),0);S(D(0),'dst_row')
    G('rows_left',D(0));c.quick(1,D(0),sub=True);S(D(0),'rows_left')
    B(6,'capture_row')
    G('dst_plane_base',D(0));G('plane_bytes',D(1))
    c.alu('add',D(1),0);S(D(0),'dst_plane_base')
    G('planes_left',D(0));c.quick(1,D(0),sub=True);S(D(0),'planes_left')
    B(6,'capture_plane')
    G('new_cursor',D(0));G('capture_bytes',D(1));c.alu('add',D(1),0)
    S(D(0),'new_cursor')
    G('new_dir',D(0));c.imm('add',ENTRY,D(0));S(D(0),'new_dir')
    c.move(I(1),M(2,F['inserted']))
    c.raw('4e75')

    raw=c.out()
    assert len(raw)%2==0 and len(raw)<32766
    assert c.labels['get_entry']==len(bank_code)
    assert c.labels['bank_active_state']==bank_labels['active_state']
    return raw,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw,labels=emit_get_bob()
    print('M19 P0a GET AGA BOB R88 native',len(raw),sha256(raw).hexdigest(),labels['get_entry'])
