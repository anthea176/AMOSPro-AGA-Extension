; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 P1d Screen Open rectangle reset, from source-pinned M19 emitter.
; UNIT142+$0F4E2..$0F514, 50 bytes of MC68020 instructions.
UNIT142_P1D_OPEN_OK equ 1

    jsr (UNIT142_P1C_OPEN_ENTRY.l,pc)
    cmpi.l #UNIT142_P1D_OPEN_OK,d3
    bne.w UNIT142_P1D_OPEN_RETURN
    move.l d0,-(a7)
    move.l a0,-(a7)
    lea UNIT142_P1D_LIMIT_TABLE(pc),a0
    move.l #260,d0
UNIT142_P1D_CLEAR_LOOP:
    move.l #0,(a0)+
    subq.l #1,d0
    bne.w UNIT142_P1D_CLEAR_LOOP
    movea.l (a7)+,a0
    move.l (a7)+,d0
UNIT142_P1D_OPEN_RETURN:
    rts
