; AGA_NATIVE_MIN_CPU: MC68020
; M19 S1-P1d: first public candidate "Aga Sprite Bank N".
; Instruction ABI: D3=N, A5=AMOS Main. D3 boolean result; D2 integer 0.
; Creates empty AGSP bank with canonical payload if absent, otherwise checks
; pre-existing AGSP DATA bank and validates ALL pixels/RGB24 via strict P1c.
; NO Sprite DMA and NO Get AGA Sprite token yet; only an in-memory AP20 test.
;
AGSP_S1_PUBLIC_BANK_ENTRY:
    bra.w agsp_s1_select_body
AGSP_S1_PRIVATE_CAPTURE_ENTRY:
    bra.w AGSP_P1C_PIPELINE_ENTRY
    include "M19_S1P1C_CAPTURE_PIPELINE_MC68020.s"

AGSP_S1_F_BANK equ 0
AGSP_S1_F_OLD  equ 4
AGSP_S1_F_TMP  equ 16
AGSP_S1_FRAME  equ 48
AGSP_S1_DATA_NAME0 equ $41474153
AGSP_S1_DATA_NAME1 equ $50525420
AGSP_S1_DATA_MAGIC equ $41475350

agsp_s1_select_body:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    suba.l #AGSP_S1_FRAME,sp
    movea.l sp,a2
    move.l d3,AGSP_S1_F_BANK(a2)
    moveq #0,d3
    moveq #0,d2
    move.l AGSP_S1_F_BANK(a2),d0
    cmpi.l #5,d0
    bcs.w agsp_s1_select_end
    cmpi.l #65535,d0
    bhi.w agsp_s1_select_end

    ; Read via the AMOS Main ABI already proven in P2d.
    dc.w $FE11,$F700,797       ; Bnk.GetAdr(D0) -> A0 payload pointer
    move.l a0,d0
    bne.w agsp_s1_have_bank

    ; New AGSP DATA: build in a private AMOS list then atomic publication.
    lea agsp_s1_empty(pc),a4
    lea AGSP_S1_F_TMP(a2),a0
    move.l a4,(a0)
    move.l #32,4(a0)
    move.l AGSP_S1_F_BANK(a2),8(a0)
    clr.l 12(a0)
    bsr.w AGSP_P1C_BANK_COMMIT
    tst.l d3
    beq.w agsp_s1_select_end
    move.l AGSP_S1_F_BANK(a2),d0
    dc.w $FE11,$F700,797       ; resolve bank number again after alloc
    move.l a0,d0
    beq.w agsp_s1_select_fail

agsp_s1_have_bank:
    ; Do not hijack Bob AGBO, Sprite OCS, AGTM or other existing DATA banks.
    cmpi.l #24,d0
    bcs.w agsp_s1_select_fail
    btst #0,d0
    bne.w agsp_s1_select_fail
    movea.l d0,a4
    moveq #0,d1
    move.w -12(a4),d1         ; AMOS DATA flags may normalize to zero on Load
    beq.w agsp_s1_flags_ok
    andi.w #$FFFD,d1
    cmpi.w #1,d1
    bne.w agsp_s1_select_fail
agsp_s1_flags_ok:
    cmpi.l #AGSP_S1_DATA_NAME0,-8(a4)
    bne.w agsp_s1_select_fail
    cmpi.l #AGSP_S1_DATA_NAME1,-4(a4)
    bne.w agsp_s1_select_fail
    cmpi.l #AGSP_S1_DATA_MAGIC,(a4)
    bne.w agsp_s1_select_fail
    move.l -20(a4),d0
    cmpi.l #48,d0
    bcs.w agsp_s1_select_fail
    cmpi.l #$01000010,d0
    bhi.w agsp_s1_select_fail
    subi.l #16,d0
    move.l d0,AGSP_S1_F_OLD(a2)
    cmp.l 20(a4),d0
    bne.w agsp_s1_select_fail
    ; Bank node is AMOS owned. TypeOfMem covers endpoints, caller's Main
    ; list ownership is established by Bnk.GetAdr.
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w agsp_s1_select_fail
    move.l a4,d0
    add.l AGSP_S1_F_OLD(a2),d0
    bcs.w agsp_s1_select_fail
    subq.l #1,d0
    movea.l d0,a1
    jsr -534(a6)
    tst.l d0
    beq.w agsp_s1_select_fail
    movea.l a4,a0
    move.l AGSP_S1_F_OLD(a2),d0
    bsr.w AGSP_P1C_VALIDATE
    tst.l d0
    beq.w agsp_s1_select_fail
    ; Persist ONLY bank id and Main owner, never a stale DMA pointer.
    lea agsp_s1_selection_state(pc),a0
    move.l a5,(a0)
    move.l AGSP_S1_F_BANK(a2),4(a0)
    moveq #1,d3
    bra.w agsp_s1_select_end
agsp_s1_select_fail:
    moveq #0,d3
agsp_s1_select_end:
    adda.l #AGSP_S1_FRAME,sp
    movem.l (sp)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts

    ; AGSP v1 empty payload, 32 bytes. NOT a legacy OCS sprite bank.
agsp_s1_empty:
    dc.l AGSP_S1_DATA_MAGIC
    dc.w 1,0,0,48
    dc.l 32,32,32,1,0

agsp_s1_selection_state:
    dc.l 0,0
