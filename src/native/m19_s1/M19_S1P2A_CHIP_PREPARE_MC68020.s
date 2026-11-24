; AGA_NATIVE_MIN_CPU: MC68020
; S1-P2a source-only component. No AP20, ViewPort, channels or DMA calls.
; A0 pinned read-only AGSP v1 payload, D0 exact allocated length,
; D1 image ID 1..4096. Caller owns a stable allocation for entire call.
; D0=private AllocVec Chip block or 0; D1=block length or 0.
; Preserve D2-D7/A0-A6. Caller owns a DETACHED allocation on success.
; FreeVec is allowed ONLY while detached; no published release API here.
; TypeOfMem checks memory region endpoints, not allocation extent.
; Layout 48 bytes header, then image, then same-height zero blank.
; 0..11 SimpleSprite (posctldata=0, height, x=y=0, num=-1)
; 12 length, 16 ID.W, 18 opaque count.W, 20 generation,
; 24 hotspot X/Y.W, 28 local RGB24 slots 0..3 (12 bytes),
; 40 image offset.L, 44 blank offset.L. image length=8+4*height.
; Header/blank are private; no pointers to source bank survive.
AGSP_P2A_PREPARE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    move.l d0,d2
    move.l d1,d3
    cmpi.l #1,d3
    bcs.w p2a_no
    cmpi.l #4096,d3
    bhi.w p2a_no
    cmpi.l #32,d2
    bcs.w p2a_no
    cmpi.l #$01000000,d2
    bhi.w p2a_no
    btst #0,d2
    bne.w p2a_no
    move.l a2,d0
    beq.w p2a_no
    btst #0,d0
    bne.w p2a_no
    add.l d2,d0
    bcs.w p2a_no
    subq.l #1,d0
    move.l d0,d7
    movea.l $0004.w,a6
    movea.l a2,a1
    jsr -534(a6)             ; TypeOfMem first byte
    tst.l d0
    beq.w p2a_no
    movea.l d7,a1
    jsr -534(a6)             ; TypeOfMem last byte
    tst.l d0
    beq.w p2a_no
    movea.l a2,a0
    move.l d2,d0
    bsr.w AGSP_P1C_VALIDATE  ; existing P1i validator, exact full payload
    tst.l d0
    beq.w p2a_no
    tst.l d1
    beq.w p2a_no
    lea 32(a2),a3
    subq.l #1,d1
p2a_find:
    cmp.w (a3),d3
    beq.w p2a_found
    bcs.w p2a_no            ; IDs strictly sorted
    adda.w #48,a3
    dbra d1,p2a_find
    bra.w p2a_no
p2a_found:
    cmpi.w #16,2(a3)
    bne.w p2a_no
    cmpi.w #2,6(a3)
    bne.w p2a_no
    moveq #0,d4
    move.w 4(a3),d4        ; validated 1..256
    move.l d4,d5
    lsl.l #2,d5
    addq.l #8,d5
    move.l d5,d6
    add.l d5,d6
    addi.l #48,d6
    move.l d6,d0
    move.l #$00010003,d1   ; MEMF_PUBLIC|MEMF_CHIP|MEMF_CLEAR
    jsr -684(a6)           ; AllocVec
    tst.l d0
    beq.w p2a_no
    movea.l d0,a4
    btst #0,d0
    bne.w p2a_free
    add.l d6,d0
    bcs.w p2a_free
    subq.l #1,d0
    move.l d0,d7
    movea.l a4,a1
    jsr -534(a6)
    btst #1,d0             ; require actual MEMF_CHIP, not bank flags
    beq.w p2a_free
    movea.l d7,a1
    jsr -534(a6)
    btst #1,d0
    beq.w p2a_free

    ; No fallible operations after this point; allocation is detached.
    clr.l (a4)
    move.w d4,4(a4)
    clr.w 6(a4)
    clr.w 8(a4)
    move.w #$FFFF,10(a4)
    move.l d6,12(a4)
    move.w d3,16(a4)
    move.w 32(a3),18(a4)
    move.l 24(a2),20(a4)
    move.l 28(a3),24(a4)
    movea.l a2,a0
    adda.l 20(a3),a0
    move.l (a0)+,28(a4)
    move.l (a0)+,32(a4)
    move.l (a0)+,36(a4)
    moveq #48,d0
    move.l d0,40(a4)
    add.l d5,d0
    move.l d0,44(a4)

    ; Plane-major -> two words per row. Control/footer and blank are zero
    ; from MEMF_CLEAR. No hardware control words are fabricated.
    movea.l a2,a0
    adda.l 12(a3),a0
    movea.l a0,a1
    move.l d4,d0
    add.l d0,d0
    adda.l d0,a1
    lea 52(a4),a5
    move.w d4,d0
    subq.w #1,d0
p2a_rows:
    move.w (a0)+,(a5)+
    move.w (a1)+,(a5)+
    dbra d0,p2a_rows
    move.l a4,d0
    move.l d6,d1
    bra.w p2a_return
p2a_free:
    movea.l a4,a1
    jsr -690(a6)          ; FreeVec only of unpublished allocation
p2a_no:
    moveq #0,d0
    moveq #0,d1
p2a_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"
