; AGA_NATIVE_MIN_CPU: MC68020
; P1e repack: final result, blank image metadata and zeroed plane.
; Source tools/m19_p1e_bank_repack_emit.py::emit_bank_repack.
; BOBS+$089B6..+$08A6E = 184 MC68020 instruction bytes, no data.
P1E_FINAL_BLANK_FLAG equ 68
P1E_FINAL_FIRST equ 16
P1E_FINAL_WIDTH equ 24
P1E_FINAL_HEIGHT equ 28
P1E_FINAL_DEPTH equ 32
P1E_FINAL_STRIDE equ 52
P1E_FINAL_TABLE_BYTES equ 72
P1E_FINAL_FULL_BYTES equ 60
P1E_FINAL_PLANE_BYTES equ 48
P1E_FINAL_BLANK_BYTES equ 56
P1E_FINAL_TARGET equ 8
P1E_FINAL_FRAME equ 96

repack_emit_done:
    tst.l P1E_FINAL_BLANK_FLAG(a2)
    beq.w repack_prepared
    bsr.w repack_init_blank
L_BOBS_089C2:
repack_prepared:
    move.l P1E_FINAL_FULL_BYTES(a2),d3
    bra.w repack_return
L_BOBS_089CA:
repack_bad:
    move.l #0,d3
L_BOBS_089D0:
repack_return:
    lea P1E_FINAL_FRAME(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_089DC:
repack_init_blank:
    move.l P1E_FINAL_FIRST(a2),d0
    move.w d0,(a0)
    move.l P1E_FINAL_WIDTH(a2),d0
    move.w d0,2(a0)
    move.l P1E_FINAL_HEIGHT(a2),d0
    move.w d0,4(a0)
    move.l P1E_FINAL_DEPTH(a2),d0
    move.w d0,6(a0)
    move.l P1E_FINAL_STRIDE(a2),d0
    move.w d0,8(a0)
    move.w #1,10(a0)
    move.l P1E_FINAL_TABLE_BYTES(a2),d0
    move.l d0,12(a0)
    move.l P1E_FINAL_PLANE_BYTES(a2),d4
    move.l d4,24(a0)
    move.l P1E_FINAL_BLANK_BYTES(a2),d5
    move.l d5,d6
    sub.l d4,d6
    move.l d6,16(a0)
    add.l d6,d0
    move.l d0,20(a0)
    move.l #0,28(a0)
    move.l #0,32(a0)
    move.l #0,36(a0)
    movea.l P1E_FINAL_TARGET(a2),a6
    move.l P1E_FINAL_TABLE_BYTES(a2),d0
    adda.l d0,a6
    add.l d5,d0
    move.l d0,P1E_FINAL_TABLE_BYTES(a2)
    lsr.l #1,d5
L_BOBS_08A54:
repack_zero_loop:
    move.w #0,(a6)+
    subq.l #1,d5
    bne.w repack_zero_loop
    adda.l #40,a0
    move.l #0,P1E_FINAL_BLANK_FLAG(a2)
    rts
