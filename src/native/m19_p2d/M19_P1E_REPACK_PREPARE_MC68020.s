; AGA_NATIVE_MIN_CPU: MC68020
; P1e repack: sizing, bounds, destination setup.
; Source tools/m19_p1e_bank_repack_emit.py::emit_bank_repack.
; BOBS+$08820..+$088EE = 206 MC68020 instruction bytes, no data.
P1E_PREP_ENTRIES equ 40
P1E_PREP_LAST equ 20
P1E_PREP_OLD_COUNT equ 36
P1E_PREP_DATA_BYTES equ 44
P1E_PREP_TABLE_BYTES equ 72
P1E_PREP_FULL_BYTES equ 60
P1E_PREP_TARGET equ 8
P1E_PREP_CAPACITY equ 12
P1E_PREP_GENERATION equ 64
P1E_PREP_MAX_IMAGES equ 4096
P1E_PREP_MAX_BANK_BYTES equ $01000000

repack_sized:
    move.l P1E_PREP_ENTRIES(a2),d0
    cmpi.l #P1E_PREP_MAX_IMAGES,d0
    bhi.w repack_bad
    tst.l P1E_PREP_LAST(a2)
    beq.w repack_insert
    cmp.l P1E_PREP_OLD_COUNT(a2),d0
    beq.w repack_bad
L_BOBS_0883E:
repack_insert:
    mulu.w #40,d0
    addi.l #32,d0
    move.l d0,P1E_PREP_TABLE_BYTES(a2)
    add.l P1E_PREP_DATA_BYTES(a2),d0
    cmpi.l #P1E_PREP_MAX_BANK_BYTES,d0
    bhi.w repack_bad
    move.l d0,P1E_PREP_FULL_BYTES(a2)
    move.l P1E_PREP_TARGET(a2),d1
    tst.l d1
    beq.w L_BOBS_089C2
    cmp.l P1E_PREP_CAPACITY(a2),d0
    bhi.w repack_bad
    add.l d1,d0
    bcs.w repack_bad
    move.l (a2),d4
    cmp.l d4,d0
    bls.w L_BOBS_0888C
    add.l 4(a2),d4
    bcs.w repack_bad
    cmp.l d4,d1
    bcs.w repack_bad
L_BOBS_0888C:
    movea.l P1E_PREP_TARGET(a2),a0
    movea.l (a2),a4
    move.l (a4),(a0)
    move.l 4(a4),4(a0)
    move.l 8(a4),8(a0)
    move.l 12(a4),12(a0)
    move.l 16(a4),16(a0)
    move.l 20(a4),20(a0)
    move.l 24(a4),24(a0)
    move.l 28(a4),28(a0)
    move.l P1E_PREP_ENTRIES(a2),d0
    move.w d0,8(a0)
    move.l P1E_PREP_TABLE_BYTES(a2),d0
    move.l d0,16(a0)
    move.l P1E_PREP_FULL_BYTES(a2),d0
    move.l d0,20(a0)
    move.l P1E_PREP_GENERATION(a2),d0
    move.l d0,24(a0)
    adda.l #32,a0
    adda.l #32,a4
    move.l P1E_PREP_OLD_COUNT(a2),d7
