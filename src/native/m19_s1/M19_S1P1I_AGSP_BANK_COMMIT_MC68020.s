; AGA_NATIVE_MIN_CPU: MC68020
; M19 S1-P1i: AGSP transaction, exact expected snapshot from caller.
; Source: AMOS365 list ABI, P2d P1e editor, preserved P1h transaction.
; A0 -> 32-byte trusted request: stage ptr, stage len, then 24-byte
; expected owner/bank/payload/length/generation/flags (six LONGs).
; D3 boolean, D2=0; preserve other AMOS caller registers.
; No published changes before final owner, head and bank checks.
; No DMA or callbacks initiated except the standard Bnk.Change.
;
; AMOS_MAIN pseudo opcodes from same P2d source:
AGSP_MAIN_LIST_CREATE equ 91
AGSP_MAIN_LIST_DELETE equ 93
AGSP_MAIN_GETADR equ 797
AGSP_MAIN_BANK_CHANGE equ 819
AGSP_NAME_0 equ $41474153  ; "AGAS"
AGSP_NAME_1 equ $50525420  ; "PRT "
AGSP_MAGIC equ $41475350   ; "AGSP"
AGSP_PUBLIC_CLEAR equ $00010001
AGSP_CUR_BANKS equ $05EA
AGSP_MAX_PAYLOAD equ $01000000
AGSP_FRAME_SIZE equ 96
AGSP_F_REQUEST equ 0
AGSP_F_SOURCE equ 4
AGSP_F_LENGTH equ 8
AGSP_F_BANK equ 12
AGSP_F_OLD_DATA equ 16
AGSP_F_OLD_NODE equ 20
AGSP_F_NEW_NODE equ 24
AGSP_F_TEMP_HEAD equ 28
AGSP_F_HEAD_ADDR equ 32
AGSP_F_HEAD_SNAPSHOT equ 36
AGSP_F_LINK_ADDR equ 40
AGSP_F_FLAGS equ 44

AGSP_P1C_BANK_COMMIT:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    suba.l #AGSP_FRAME_SIZE,sp
    movea.l sp,a2
    clr.l AGSP_F_OLD_DATA(a2)
    clr.l AGSP_F_OLD_NODE(a2)
    clr.l AGSP_F_NEW_NODE(a2)
    clr.l AGSP_F_TEMP_HEAD(a2)
    moveq #0,d3
    moveq #0,d2
    moveq #32,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_c_reject
    move.l a0,AGSP_F_REQUEST(a2)
    movea.l a0,a4
    move.l (a4),AGSP_F_SOURCE(a2)
    move.l 4(a4),AGSP_F_LENGTH(a2)
    move.l 12(a4),AGSP_F_BANK(a2)
    move.l AGSP_F_BANK(a2),d0
    cmpi.l #5,d0
    bcs.w agsp_c_reject
    cmpi.l #65535,d0
    bhi.w agsp_c_reject
    move.l AGSP_F_LENGTH(a2),d0
    cmpi.l #32,d0
    bcs.w agsp_c_reject
    cmpi.l #AGSP_MAX_PAYLOAD,d0
    bhi.w agsp_c_reject
    btst #0,d0
    bne.w agsp_c_reject
    ; Validate whole detached payload and original live bank snapshot.
    movea.l AGSP_F_SOURCE(a2),a0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_c_reject
    move.l AGSP_F_LENGTH(a2),d0
    bsr.w AGSP_P1C_VALIDATE
    tst.l d0
    beq.w agsp_c_reject
    movea.l AGSP_F_REQUEST(a2),a4
    lea 8(a4),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w agsp_c_reject
    move.l 8(a4),AGSP_F_HEAD_ADDR(a2)
    move.l 16(a4),AGSP_F_OLD_DATA(a2)
    move.l 28(a4),AGSP_F_FLAGS(a2)
    move.l 16(a4),d0
    beq.w agsp_i_commit_new
    subi.l #24,d0
    move.l d0,AGSP_F_OLD_NODE(a2)
    move.l 24(a4),d0
    cmpi.l #$FFFFFFFF,d0
    beq.w agsp_c_reject
    addq.l #1,d0
    bra.w agsp_i_commit_gen
agsp_i_commit_new:
    moveq #1,d0
agsp_i_commit_gen:
    movea.l AGSP_F_SOURCE(a2),a0
    cmp.l 24(a0),d0
    bne.w agsp_c_reject
    movea.l AGSP_F_HEAD_ADDR(a2),a4
    move.l (a4),AGSP_F_HEAD_SNAPSHOT(a2)

    ; Allocate detached node only; official list remains untouched.
    lea AGSP_F_TEMP_HEAD(a2),a0
    move.l AGSP_F_LENGTH(a2),d0
    addi.l #16,d0
    move.l #AGSP_PUBLIC_CLEAR,d1
    move.l AGSP_F_FLAGS(a2),d4
    andi.l #2,d4
    or.l d4,d1               ; preserve original Chip preference
    dc.w $FE11,$F700,AGSP_MAIN_LIST_CREATE
    move.l AGSP_F_TEMP_HEAD(a2),AGSP_F_NEW_NODE(a2)
    tst.l d0
    beq.w agsp_c_reject
    cmp.l AGSP_F_NEW_NODE(a2),d0
    bne.w agsp_c_reject
    move.l a1,d0
    cmp.l AGSP_F_NEW_NODE(a2),d0
    bne.w agsp_c_reject
    movea.l a1,a4
    movea.l a4,a0
    move.l AGSP_F_LENGTH(a2),d0
    addi.l #24,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_c_reject
    tst.l (a4)
    bne.w agsp_c_reject
    move.l AGSP_F_LENGTH(a2),d0
    addi.l #16,d0
    cmp.l 4(a4),d0
    bne.w agsp_c_reject
    move.l AGSP_F_BANK(a2),8(a4)
    move.l AGSP_F_FLAGS(a2),d0
    andi.w #2,d0
    ori.w #1,d0
    move.w d0,12(a4)          ; DATA, preserve Chip bit; normalize zero
    clr.w 14(a4)
    move.l #AGSP_NAME_0,16(a4)
    move.l #AGSP_NAME_1,20(a4)
    movea.l AGSP_F_SOURCE(a2),a0
    lea 24(a4),a1
    move.l AGSP_F_LENGTH(a2),d6
    move.l d6,d7
    lsr.l #2,d6
    beq.w agsp_c_copy_tail
agsp_c_copy_longs:
    move.l (a0)+,(a1)+
    subq.l #1,d6
    bne.w agsp_c_copy_longs
agsp_c_copy_tail:
    btst #1,d7
    beq.w agsp_c_recheck
    move.w (a0)+,(a1)+

agsp_c_recheck:
    ; Revalidate the caller's original snapshot, not a late replacement.
    movea.l AGSP_F_REQUEST(a2),a0
    adda.l #8,a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w agsp_c_reject
    movea.l AGSP_F_HEAD_ADDR(a2),a4
    move.l (a4),d0
    cmp.l AGSP_F_HEAD_SNAPSHOT(a2),d0
    bne.w agsp_c_reject

    ; Walk bounded active list, find predecessor cell of old node.
    move.l a4,AGSP_F_LINK_ADDR(a2)
    move.l AGSP_F_OLD_NODE(a2),d5
    move.l #65535,d6
agsp_c_seek:
    movea.l AGSP_F_LINK_ADDR(a2),a4
    move.l (a4),d0
    cmp.l d5,d0
    beq.w agsp_c_publish_replace
    tst.l d0
    beq.w agsp_c_seek_end
    btst #0,d0
    bne.w agsp_c_reject
    ; Even in insert mode, reject duplicate ID if Bnk.GetAdr lied.
    movea.l d0,a4
    movea.l a4,a0
    moveq #12,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_c_reject
    move.l 8(a4),d1
    cmp.l AGSP_F_BANK(a2),d1
    beq.w agsp_c_reject
    move.l a4,AGSP_F_LINK_ADDR(a2)
    subq.l #1,d6
    bne.w agsp_c_seek
    bra.w agsp_c_reject
agsp_c_seek_end:
    tst.l d5
    bne.w agsp_c_reject

    ; Insert at original list head, regardless of unrelated bank nodes.
    movea.l AGSP_F_HEAD_ADDR(a2),a4
    movea.l AGSP_F_NEW_NODE(a2),a1
    move.l (a4),(a1)
    move.l a1,(a4)             ; THE single pointer publication
    clr.l AGSP_F_TEMP_HEAD(a2)
    bra.w agsp_c_notify

agsp_c_publish_replace:
    tst.l d5
    beq.w agsp_c_seek_end
    movea.l AGSP_F_OLD_NODE(a2),a0
    movea.l AGSP_F_NEW_NODE(a2),a1
    move.l (a0),(a1)
    movea.l AGSP_F_LINK_ADDR(a2),a4
    move.l a1,(a4)             ; THE single pointer publication
    clr.l (a0)                 ; unlink old after replacement
    move.l a0,AGSP_F_TEMP_HEAD(a2)

agsp_c_notify:
    ; Bnk.Change needs the old bank allocation still alive for callbacks.
    dc.w $FE11,$F700,AGSP_MAIN_BANK_CHANGE
    move.l AGSP_F_OLD_NODE(a2),d0
    beq.w agsp_c_success
    lea AGSP_F_TEMP_HEAD(a2),a0
    movea.l AGSP_F_OLD_NODE(a2),a1
    dc.w $FE11,$F700,AGSP_MAIN_LIST_DELETE
agsp_c_success:
    moveq #1,d3
    bra.w agsp_c_exit
agsp_c_reject:
    ; If Lst.Cree succeeded but any precommit check fails, delete only stage.
    move.l AGSP_F_NEW_NODE(a2),d0
    beq.w agsp_c_exit
    lea AGSP_F_TEMP_HEAD(a2),a0
    movea.l AGSP_F_NEW_NODE(a2),a1
    dc.w $FE11,$F700,AGSP_MAIN_LIST_DELETE
agsp_c_exit:
    adda.l #AGSP_FRAME_SIZE,sp
    movem.l (sp)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
