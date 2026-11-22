; AGA_NATIVE_MIN_CPU: MC68020
; P1e repack: selected directory entries, relocate pixels into target bank.
; Source tools/m19_p1e_bank_repack_emit.py::emit_bank_repack.
; BOBS+$088EE..+$089B6 = 200 MC68020 code bytes, no data.
P1E_COPY_FIRST equ 16
P1E_COPY_LAST equ 20
P1E_COPY_BLANK_FLAG equ 68
P1E_COPY_TABLE_BYTES equ 72
P1E_COPY_TARGET equ 8
P1E_COPY_COUNTER_STEP equ 40

repack_emit:
    tst.l d7
    beq.w repack_emit_done
    move.l #0,d0
    move.w (a4),d0
    tst.l P1E_COPY_LAST(a2)
    beq.w repack_check_blank
    cmp.l P1E_COPY_FIRST(a2),d0
    bcs.w repack_copy_data
    cmp.l P1E_COPY_LAST(a2),d0
    bls.w repack_next
    bra.w repack_copy_data
L_BOBS_08918:
repack_check_blank:
    tst.l P1E_COPY_BLANK_FLAG(a2)
    beq.w repack_copy_data
    cmp.l P1E_COPY_FIRST(a2),d0
    bcs.w repack_copy_data
    bsr.w repack_init_blank
L_BOBS_0892C:
repack_copy_data:
    move.l (a4),(a0)
    move.l 4(a4),4(a0)
    move.l 8(a4),8(a0)
    move.l 12(a4),12(a0)
    move.l 16(a4),16(a0)
    move.l 20(a4),20(a0)
    move.l 24(a4),24(a0)
    move.l 28(a4),28(a0)
    move.l 32(a4),32(a0)
    move.l 36(a4),36(a0)
    movea.l (a2),a1
    move.l 12(a4),d0
    adda.l d0,a1
    move.l P1E_COPY_TABLE_BYTES(a2),d0
    move.l d0,12(a0)
    move.l 16(a4),d4
    add.l d4,d0
    move.l 24(a4),d5
    tst.l d5
    beq.w L_BOBS_08988
    move.l d0,20(a0)
L_BOBS_08988:
    add.l d5,d4
    movea.l P1E_COPY_TARGET(a2),a6
    move.l P1E_COPY_TABLE_BYTES(a2),d0
    adda.l d0,a6
    add.l d4,d0
    move.l d0,P1E_COPY_TABLE_BYTES(a2)
    lsr.l #1,d4
L_BOBS_0899C:
    move.w (a1)+,(a6)+
    subq.l #1,d4
    bne.w L_BOBS_0899C
    adda.l #P1E_COPY_COUNTER_STEP,a0
L_BOBS_089AA:
repack_next:
    adda.l #P1E_COPY_COUNTER_STEP,a4
    subq.l #1,d7
    bra.w repack_emit
