; AGA_NATIVE_MIN_CPU: MC68020
; S1-P1i: public Sprite bank selection + capture, source-only candidate.
; Same public instruction ABI as P1h. NO Sprite DMA.
; Invalidate selection on EVERY new selection attempt. Bind A5 AND the
; program-specific Cur_Banks cell, never a cached payload pointer.
AGSP_S1_PUBLIC_BANK_ENTRY:
    bra.w agsp_s1_select_body
AGSP_S1_PRIVATE_CAPTURE_ENTRY:
    bra.w AGSP_P1C_PIPELINE_ENTRY
AGSP_S1_PUBLIC_GET_ENTRY:
    bra.w agsp_s1_get_body
    include "M19_S1P1I_CAPTURE_PIPELINE_MC68020.s"

AGSP_S1_F_BANK equ 0
AGSP_S1_F_OWNER equ 4
AGSP_S1_F_TMP equ 16
AGSP_S1_FRAME equ 48
AGSP_S1_DATA_MAGIC equ $41475350

agsp_s1_select_body:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    suba.l #AGSP_S1_FRAME,sp
    movea.l sp,a2
    move.l d3,AGSP_S1_F_BANK(a2)
    lea agsp_s1_selection_state(pc),a0
    clr.l (a0)
    clr.l 4(a0)
    clr.l 8(a0)
    moveq #0,d3
    moveq #0,d2
    move.l AGSP_S1_F_BANK(a2),d0
    cmpi.l #5,d0
    bcs.w agsp_s1_select_fail
    cmpi.l #65535,d0
    bhi.w agsp_s1_select_fail
    move.l $05EA(a5),AGSP_S1_F_OWNER(a2)
    movea.l AGSP_S1_F_OWNER(a2),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w agsp_s1_select_fail
    move.l AGSP_S1_F_BANK(a2),d0
    dc.w $FE11,$F700,797
    move.l a0,d0
    bne.w agsp_s1_have_bank

    ; Creation is a transaction expecting this exact owner and absent ID.
    lea agsp_s1_empty(pc),a4
    lea AGSP_S1_F_TMP(a2),a0
    move.l a4,(a0)
    move.l #32,4(a0)
    move.l AGSP_S1_F_OWNER(a2),8(a0)
    move.l AGSP_S1_F_BANK(a2),12(a0)
    clr.l 16(a0)
    clr.l 20(a0)
    clr.l 24(a0)
    clr.l 28(a0)
    bsr.w AGSP_P1C_BANK_COMMIT
    tst.l d3
    beq.w agsp_s1_select_fail
    movea.l AGSP_S1_F_OWNER(a2),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w agsp_s1_select_fail
    move.l AGSP_S1_F_BANK(a2),d0
    dc.w $FE11,$F700,797
agsp_s1_have_bank:
    move.l AGSP_S1_F_BANK(a2),d0
    bsr.w AGSP_I_LIVE
    tst.l d0
    beq.w agsp_s1_select_fail
    movea.l AGSP_S1_F_OWNER(a2),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w agsp_s1_select_fail
    lea agsp_s1_selection_state(pc),a0
    move.l a5,(a0)
    move.l AGSP_S1_F_BANK(a2),4(a0)
    move.l AGSP_S1_F_OWNER(a2),8(a0)
    moveq #1,d3
    bra.w agsp_s1_select_end
agsp_s1_select_fail:
    moveq #0,d3
agsp_s1_select_end:
    adda.l #AGSP_S1_FRAME,sp
    movem.l (sp)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts

    include "M19_S1P1I_GET_PUBLIC_MC68020.s"
agsp_s1_empty:
    dc.l AGSP_S1_DATA_MAGIC
    dc.w 1,0,0,48
    dc.l 32,32,32,1,0
agsp_s1_selection_state:
    dc.l 0,0,0
