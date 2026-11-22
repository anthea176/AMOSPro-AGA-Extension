; AGA_NATIVE_MIN_CPU: MC68020
; P1e repack insertion/image sizing, from tools/m19_p1e_bank_repack_emit.py.
; BOBS+$08722..+$087C2 = 160 MC68020 instructions, no data.
P1E_INSERT_WIDTH equ 24
P1E_INSERT_HEIGHT equ 28
P1E_INSERT_DEPTH equ 32
P1E_INSERT_DATA_SIZE equ 44
P1E_INSERT_PLANE equ 48
P1E_INSERT_STRIDE equ 52
P1E_INSERT_BLANK_SIZE equ 56
P1E_INSERT_ENTRIES equ 40
P1E_INSERT_EMIT_BLANK equ 68
P1E_INSERT_MAX_SIDE equ 4096
P1E_INSERT_MAX_PIXELS equ $00400000

repack_insertion:
    move.l P1E_INSERT_WIDTH(a2),d0
    cmpi.l #1,d0
    bcs.w L_BOBS_089CA
    cmpi.l #P1E_INSERT_MAX_SIDE,d0
    bhi.w L_BOBS_089CA
    move.l P1E_INSERT_HEIGHT(a2),d0
    cmpi.l #1,d0
    bcs.w L_BOBS_089CA
    cmpi.l #P1E_INSERT_MAX_SIDE,d0
    bhi.w L_BOBS_089CA
    move.l P1E_INSERT_DEPTH(a2),d0
    cmpi.l #1,d0
    bcs.w L_BOBS_089CA
    cmpi.l #8,d0
    bhi.w L_BOBS_089CA
    move.l P1E_INSERT_WIDTH(a2),d0
    move.l P1E_INSERT_HEIGHT(a2),d1
    mulu.w d1,d0
    cmpi.l #P1E_INSERT_MAX_PIXELS,d0
    bhi.w L_BOBS_089CA
    move.l P1E_INSERT_WIDTH(a2),d0
    addi.l #15,d0
    lsr.l #4,d0
    lsl.l #1,d0
    move.l d0,P1E_INSERT_STRIDE(a2)
    mulu.w d1,d0
    move.l d0,P1E_INSERT_PLANE(a2)
    move.l P1E_INSERT_DEPTH(a2),d1
    addq.l #1,d1
    move.l #0,d4
L_BOBS_087A2:
repack_planes:
    add.l d0,d4
    subq.l #1,d1
    bne.w repack_planes
    move.l d4,P1E_INSERT_BLANK_SIZE(a2)
    move.l d4,P1E_INSERT_DATA_SIZE(a2)
    move.l #1,P1E_INSERT_ENTRIES(a2)
    move.l #1,P1E_INSERT_EMIT_BLANK(a2)
