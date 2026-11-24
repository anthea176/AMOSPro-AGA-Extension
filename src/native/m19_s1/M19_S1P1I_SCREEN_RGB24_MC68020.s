; AGA_NATIVE_MIN_CPU: MC68020
; S1-P1i: private AGA screen bridge, NOT an exported AP20 command.
; Based on verified P2d Bob back ScreenBuffer layout and AGAPIC GetRGB32.
; Caller owns/proves every memory span in the 36-byte request and stage.
; A0 -> request, big endian:
;   +0 state* (normally resolved from A5+$01C8 by future public wrapper)
;   +4 RGB32[256*3*4] scratch ; +8 RGB24[256*3] output
;   +12 capture descriptor[64] ; +16 AGSP planes stage[4*H]
;   +20 AGSP local RGB palette[48]
;   +24 WORD source x ; +26 WORD source y ; +28 WORD H 1..256
;   +30 WORD transparent pen ; +32 LONG reserved zero
; Output: D0=1, D1=256 or D0=0, D1=0. Save D2-D7/A2-A6.
; DB+20 bit0=Safe pending, as in source-owned L2b L1_AcquireSafe.
; Poll only pending Safe via DB+12; clear only bit0 on a real reply.
; No implicit Swap, no WaitPort, no DMA Sprite, no bank writes.
; Only 8-bit private AGA screens with at least 256 palette entries in S1-P1b.
; GetRGB32 graphics LVO -900, WaitBlit graphics LVO -228.

AGSP_P1B_SCREEN_PREPARE:
    movem.l d2-d7/a2-a6,-(sp)
    movea.l a0,a4
    moveq #0,d0
    moveq #0,d1
    move.l a4,d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    tst.l 32(a4)
    bne.w agsp_p1b_fail
    moveq #0,d6
agsp_p1b_check_outputs:
    move.l 4(a4,d6.w),d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    addq.w #4,d6
    cmpi.w #20,d6
    bcs.w agsp_p1b_check_outputs

    movea.l (a4),a5
    move.l a5,d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    movea.l a5,a0
    moveq #36,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_p1b_fail
    movea.l (a5),a0            ; intuition Screen
    move.l a0,d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    moveq #52,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_p1b_fail
    movea.l 48(a0),a0          ; Screen.ViewPort.ColorMap
    move.l a0,d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    moveq #4,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_p1b_fail
    move.w 2(a0),d0            ; ColorMap.Count
    cmpi.w #256,d0
    bcs.w agsp_p1b_fail

    move.l 20(a5),d0           ; private state palette count
    cmpi.l #256,d0
    bcs.w agsp_p1b_fail
    move.l 28(a5),d0           ; private state depth
    cmpi.l #8,d0
    bne.w agsp_p1b_fail
    move.l 12(a5),d2           ; width
    cmpi.l #16,d2
    bcs.w agsp_p1b_fail
    cmpi.l #4096,d2
    bhi.w agsp_p1b_fail
    move.l 16(a5),d3           ; height
    beq.w agsp_p1b_fail
    cmpi.l #4096,d3
    bhi.w agsp_p1b_fail
    moveq #0,d0
    move.w 24(a4),d0           ; X, unsigned
    addi.l #16,d0
    cmp.l d2,d0
    bhi.w agsp_p1b_fail
    moveq #0,d0
    move.w 28(a4),d0           ; H
    beq.w agsp_p1b_fail
    cmpi.l #256,d0
    bhi.w agsp_p1b_fail
    moveq #0,d1
    move.w 26(a4),d1           ; Y
    add.l d1,d0
    cmp.l d3,d0
    bhi.w agsp_p1b_fail
    move.w 30(a4),d0
    cmpi.w #255,d0
    bhi.w agsp_p1b_fail

    movea.l 32(a5),a0          ; private DoubleBuffer
    move.l a0,d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    moveq #24,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_p1b_fail
    movea.l a0,a2              ; DBState held across validation and OS calls
    move.l 8(a0),d0            ; front selector 0/1
    beq.w agsp_p1b_front_zero
    cmpi.l #1,d0
    bne.w agsp_p1b_fail
    movea.l (a0),a1            ; front1 => back0
    bra.w agsp_p1b_selected
agsp_p1b_front_zero:
    movea.l 4(a0),a1           ; front0 => back1
agsp_p1b_selected:
    move.l a1,d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    movea.l a1,a0
    moveq #4,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_p1b_fail
    movea.l (a1),a3            ; ScreenBuffer.sb_BitMap
    move.l a3,d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    movea.l a3,a0
    moveq #40,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_p1b_fail
    moveq #0,d0
    move.w (a3),d0             ; BitMap.BytesPerRow
    cmpi.w #2,d0
    bcs.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    move.l d0,d6
    lsl.l #3,d0
    cmp.l d2,d0
    bcs.w agsp_p1b_fail
    moveq #0,d0
    move.w 2(a3),d0            ; BitMap.Rows
    cmp.l d3,d0
    bcs.w agsp_p1b_fail
    moveq #0,d0
    move.b 5(a3),d0            ; BitMap.Depth
    cmpi.b #8,d0
    bne.w agsp_p1b_fail
    lea 8(a3),a0
    moveq #7,d7
agsp_p1b_check_planes:
    movea.l (a0)+,a1
    move.l a0,-(sp)
    movea.l a1,a0
    move.l d6,d0
    mulu.w d3,d0              ; stride * validated visible height
    bsr.w AGSP_I_SPAN
    movea.l (sp)+,a0
    tst.l d0
    beq.w agsp_p1b_fail
    dbra d7,agsp_p1b_check_planes

    ; The real P2d source uses the same graphics.library base at state+8.
    movea.l 8(a5),a6
    move.l a6,d0
    beq.w agsp_p1b_fail
    btst #0,d0
    bne.w agsp_p1b_fail
    ; Identical pending-bit semantics to L2b L1_AcquireSafe.
    move.l 20(a2),d0
    btst #0,d0
    beq.w agsp_i_back_safe
    movea.l 12(a2),a0
    moveq #34,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_p1b_fail
    movea.l $0004.w,a6
    jsr -372(a6)               ; Exec.GetMsg(SafePort)
    tst.l d0
    beq.w agsp_p1b_fail
    andi.l #$FFFFFFFE,20(a2)   ; never clear Disp or other bits
agsp_i_back_safe:
    movea.l 8(a5),a6
    jsr -228(a6)               ; WaitBlit while the back buffer is Safe

    ; GetRGB32(ColorMap, 0, 256, private RGB32 scratch)
    movea.l (a5),a0
    movea.l 48(a0),a0
    movea.l 4(a4),a1
    moveq #0,d0
    move.l #256,d1
    jsr -900(a6)

    ; 768 RGB24 bytes, copy high 8 bits from each 32-bit value.
    movea.l 4(a4),a0
    movea.l 8(a4),a1
    move.w #767,d7
agsp_p1b_copy_rgb:
    move.b (a0),(a1)+
    addq.l #4,a0
    dbra d7,agsp_p1b_copy_rgb

    movea.l 12(a4),a2          ; create validated kernel descriptor
    lea 8(a3),a0
    moveq #7,d7
agsp_p1b_copy_planes:
    move.l (a0)+,(a2)+
    dbra d7,agsp_p1b_copy_planes
    move.l 8(a4),(a2)+        ; 32 pointer to RGB24
    move.l 16(a4),(a2)+       ; 36 AGSP planar stage
    move.l 20(a4),(a2)+       ; 40 AGSP palette stage
    move.l d6,(a2)+          ; 44 stride as LONG
    move.w d2,(a2)+          ; 48 width
    move.w d3,(a2)+          ; 50 height
    move.w #8,(a2)+          ; 52 depth
    move.w 24(a4),(a2)+      ; 54 x
    move.w 26(a4),(a2)+      ; 56 y
    move.w 28(a4),(a2)+      ; 58 H
    move.w 30(a4),(a2)+      ; 60 transparency
    clr.w (a2)               ; 62 reserved
    moveq #1,d0
    move.l #256,d1
    bra.w agsp_p1b_exit
agsp_p1b_fail:
    moveq #0,d0
    moveq #0,d1
agsp_p1b_exit:
    movem.l (sp)+,d2-d7/a2-a6
    rts
