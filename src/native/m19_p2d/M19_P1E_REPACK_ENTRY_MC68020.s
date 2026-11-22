; AGA_NATIVE_MIN_CPU: MC68020
; Original source m19_p1e_bank_repack_emit.py::emit_bank_repack.
; P1e AGBO bank payload repacker entry and numeric range validation.
; BOBS+$0866C..+$08722, 182 instruction bytes; no embedded data.
P1E_REPACK_STACK equ 96
P1E_REPACK_FIRST equ 16
P1E_REPACK_LAST equ 20
P1E_REPACK_GENERATION equ 64
P1E_REPACK_COUNT equ 36
P1E_REPACK_ENTRIES equ 40
P1E_REPACK_DATA_SIZE equ 44
P1E_REPACK_EMIT_BLANK equ 68
P1E_REPACK_RESULT equ 76
P1E_REPACK_MAX_ID equ 4096

edit_repack:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -P1E_REPACK_STACK(a7),a7
    movea.l a7,a2
    move.l (a0),(a2)
    move.l 4(a0),4(a2)
    move.l 8(a0),8(a2)
    move.l 12(a0),12(a2)
    move.l 16(a0),16(a2)
    move.l 20(a0),20(a2)
    move.l 24(a0),24(a2)
    move.l 28(a0),28(a2)
    move.l 32(a0),32(a2)
    move.l #0,P1E_REPACK_RESULT(a2)
    movea.l (a2),a0
    move.l 24(a0),d0
    cmpi.l #-1,d0
    beq.w L_BOBS_089CA
    addq.l #1,d0
    move.l d0,P1E_REPACK_GENERATION(a2)
    move.l #0,d0
    move.w 8(a0),d0
    move.l d0,P1E_REPACK_COUNT(a2)
    move.l #0,P1E_REPACK_ENTRIES(a2)
    move.l #0,P1E_REPACK_DATA_SIZE(a2)
    move.l P1E_REPACK_FIRST(a2),d0
    cmpi.l #1,d0
    bcs.w L_BOBS_089CA
    cmpi.l #P1E_REPACK_MAX_ID,d0
    bhi.w L_BOBS_089CA
    move.l P1E_REPACK_LAST(a2),d0
    beq.w L_BOBS_08722
    cmp.l P1E_REPACK_FIRST(a2),d0
    bcs.w L_BOBS_089CA
    cmpi.l #P1E_REPACK_MAX_ID,d0
    bhi.w L_BOBS_089CA
    move.l #0,P1E_REPACK_EMIT_BLANK(a2)
    bra.w L_BOBS_087C2
