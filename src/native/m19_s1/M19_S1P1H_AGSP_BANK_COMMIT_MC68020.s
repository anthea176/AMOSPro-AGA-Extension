; AGA_NATIVE_MIN_CPU: MC68020
; M19 S1-P1h: corrected AGSP DATA bank transaction, AMOS Professional 365.
; SAME OS/Main conventions as the source-verified P2d P1e Bob editor.
; NO exported token, NO Sprite DMA, no automatic dist promotion.
;
; A0 -> request (16 bytes), trusted and preallocated by future AP20 wrapper:
;   +0 pointer to COMPLETE, VALIDATED AGSP v1 payload (2-byte aligned)
;   +4 payload byte length (32..16MiB, even)
;   +8 bank number as LONG (5..65535)
;  +12 reserved (must be zero)
; A5 = live AMOS Main context. Cur_Banks(A5) at $05EA holds the
; ADDRESS of the program's bank-list head cell, not the head node.
;
; Result D3=1 success, 0 refusal; D2=0 integer; other caller
; registers preserved. Request/payload must remain alive until return.
; The caller MUST prove whole memory allocations and validate all AGSP
; directory entries/pixels. This routine checks container/top-level and
; the AMOS-owned destination node, not full pixel canonicality.
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
    move.l a0,d0
    beq.w agsp_c_reject
    btst #0,d0
    bne.w agsp_c_reject
    move.l a0,AGSP_F_REQUEST(a2)
    movea.l a0,a4
    tst.l 12(a4)
    bne.w agsp_c_reject
    move.l (a4),AGSP_F_SOURCE(a2)
    move.l 4(a4),AGSP_F_LENGTH(a2)
    move.l 8(a4),AGSP_F_BANK(a2)
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
    move.l AGSP_F_SOURCE(a2),d1
    beq.w agsp_c_reject
    btst #0,d1
    bne.w agsp_c_reject
    add.l d0,d1
    bcs.w agsp_c_reject
    subq.l #1,d1

    ; Exec.TypeOfMem at endpoints, additional span ownership remains caller's.
    movea.l $0004.w,a6
    movea.l AGSP_F_REQUEST(a2),a1
    jsr -534(a6)
    tst.l d0
    beq.w agsp_c_reject
    movea.l AGSP_F_SOURCE(a2),a1
    jsr -534(a6)
    tst.l d0
    beq.w agsp_c_reject
    move.l AGSP_F_SOURCE(a2),d0
    add.l AGSP_F_LENGTH(a2),d0
    subq.l #1,d0
    movea.l d0,a1
    jsr -534(a6)
    tst.l d0
    beq.w agsp_c_reject

    ; Validate AGSP envelope BEFORE any AMOS Main list modification.
    movea.l AGSP_F_SOURCE(a2),a4
    cmpi.l #AGSP_MAGIC,(a4)
    bne.w agsp_c_reject
    cmpi.w #1,4(a4)
    bne.w agsp_c_reject
    tst.w 6(a4)
    bne.w agsp_c_reject
    moveq #0,d0
    move.w 8(a4),d0
    cmpi.l #4096,d0
    bhi.w agsp_c_reject
    cmpi.w #48,10(a4)
    bne.w agsp_c_reject
    cmpi.l #32,12(a4)
    bne.w agsp_c_reject
    mulu.w #48,d0
    addi.l #32,d0
    cmp.l AGSP_F_LENGTH(a2),d0
    bhi.w agsp_c_reject
    cmp.l 16(a4),d0
    bne.w agsp_c_reject
    move.l 20(a4),d0
    cmp.l AGSP_F_LENGTH(a2),d0
    bne.w agsp_c_reject
    tst.l 24(a4)
    beq.w agsp_c_reject
    tst.l 28(a4)
    bne.w agsp_c_reject

    ; AMOS +B.s Bnk.Change loads Cur_Banks(A5), then (A0).
    ; Preserve the owner cell ADDRESS separately from its current head.
    movea.l AGSP_CUR_BANKS(a5),a4
    move.l a4,d0
    beq.w agsp_c_reject
    btst #0,d0
    bne.w agsp_c_reject
    move.l a4,AGSP_F_HEAD_ADDR(a2)
    move.l (a4),AGSP_F_HEAD_SNAPSHOT(a2)
    move.l (a4),d0
    beq.w agsp_c_lookup
    btst #0,d0
    bne.w agsp_c_reject
agsp_c_lookup:
    move.l AGSP_F_BANK(a2),d0
    dc.w $FE11,$F700,AGSP_MAIN_GETADR
    move.l a0,d0
    beq.w agsp_c_old_absent
    cmpi.l #24,d0
    bcs.w agsp_c_reject
    btst #0,d0
    bne.w agsp_c_reject
    move.l d0,AGSP_F_OLD_DATA(a2)
    subi.l #24,d0
    move.l d0,AGSP_F_OLD_NODE(a2)
    movea.l d0,a4
    move.l 8(a4),d0
    cmp.l AGSP_F_BANK(a2),d0
    bne.w agsp_c_reject
    moveq #0,d0
    move.w 12(a4),d0
    beq.w agsp_c_old_flags_ok   ; AMOS may normalize saved DATA flags to 0
    andi.w #$FFFD,d0
    cmpi.w #1,d0
    bne.w agsp_c_reject
agsp_c_old_flags_ok:
    cmpi.l #AGSP_NAME_0,16(a4)
    bne.w agsp_c_reject
    cmpi.l #AGSP_NAME_1,20(a4)
    bne.w agsp_c_reject
    move.l 4(a4),d0
    cmpi.l #48,d0
    bcs.w agsp_c_reject
    cmpi.l #$01000010,d0
    bhi.w agsp_c_reject
    movea.l AGSP_F_OLD_DATA(a2),a4
    cmpi.l #AGSP_MAGIC,(a4)
    bne.w agsp_c_reject
    subi.l #16,d0
    cmp.l 20(a4),d0
    bne.w agsp_c_reject
agsp_c_old_absent:
    ; Allocate detached node only; official list remains untouched.
    lea AGSP_F_TEMP_HEAD(a2),a0
    move.l AGSP_F_LENGTH(a2),d0
    addi.l #16,d0
    move.l #AGSP_PUBLIC_CLEAR,d1
    dc.w $FE11,$F700,AGSP_MAIN_LIST_CREATE
    tst.l d0
    beq.w agsp_c_reject
    move.l a1,d0
    beq.w agsp_c_reject
    move.l a1,AGSP_F_NEW_NODE(a2)
    movea.l a1,a4
    move.l AGSP_F_BANK(a2),8(a4)
    move.w #1,12(a4)           ; generic AMOS DATA bank (not Sprite OCS)
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
    ; Do not call Bnk.GetAdr through an owner cell that has changed.
    move.l AGSP_CUR_BANKS(a5),d0
    cmp.l AGSP_F_HEAD_ADDR(a2),d0
    bne.w agsp_c_reject
    ; Fail on ANY bank number/owner/head drift while staging.
    move.l AGSP_F_BANK(a2),d0
    dc.w $FE11,$F700,AGSP_MAIN_GETADR
    move.l a0,d0
    cmp.l AGSP_F_OLD_DATA(a2),d0
    bne.w agsp_c_reject
    move.l AGSP_CUR_BANKS(a5),d0
    cmp.l AGSP_F_HEAD_ADDR(a2),d0
    bne.w agsp_c_reject
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
