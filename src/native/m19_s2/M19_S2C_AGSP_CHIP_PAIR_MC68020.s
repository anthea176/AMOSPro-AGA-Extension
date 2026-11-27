; AGA_NATIVE_MIN_CPU: MC68020
; S2c-P0b: detached 16px/4bpp pair preparation, derived from S1 P2a.
; A0 stable pinned AGSP v1 payload, D0 exact allocated extent, D1 image ID.
; D0=private AllocVec Chip block or 0; D1=exact extent or 0.
; D2-D7/A0-A6 preserved. No ViewPort, channel, Copper, publication or DMA calls.
; Caller proves extent/lifetime; TypeOfMem only checks mapped memory region.
; FreeVec allowed only while detached. No source pointer survives.
; Private layout (not the S1 P2a layout or an on-disk ABI):
; +00 and +12 SimpleSprite: posctldata=0,height,x=y=0,num=-1.
; +24 total.L, +28 image ID.W, +30 opaque count.W, +32 generation.L,
; +36 hotspot X/Y.W, +40 local RGB24 palette[48],
; +88 bytes per stream.L, +92 first stream offset.L=96.
; E0, O0, E1, O1 at +96+n*(8+4H).
; E0 and O0 contain planes 0/1 and 2/3, row interleaved; E1/O1 zero.
; Control and terminal words all zero, including ATTACH. The future
; OS adapter sets ATTACH on the odd live stream AFTER ChangeSprite.
; No proof of safe paired publication, double-buffering or retirement here.
AGSP_S2C_PREPARE_PAIR:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    move.l d0,d2
    move.l d1,d3
    cmpi.l #1,d3
    bcs.w s2c_pair_no
    cmpi.l #4096,d3
    bhi.w s2c_pair_no
    cmpi.l #32,d2
    bcs.w s2c_pair_no
    cmpi.l #$01000000,d2
    bhi.w s2c_pair_no
    btst #0,d2
    bne.w s2c_pair_no
    move.l a2,d0
    beq.w s2c_pair_no
    btst #0,d0
    bne.w s2c_pair_no
    add.l d2,d0
    bcs.w s2c_pair_no
    subq.l #1,d0
    move.l d0,d7
    movea.l $0004.w,a6
    movea.l a2,a1
    jsr -534(a6)             ; TypeOfMem first byte
    tst.l d0
    beq.w s2c_pair_no
    movea.l d7,a1
    jsr -534(a6)             ; TypeOfMem last byte
    tst.l d0
    beq.w s2c_pair_no
    movea.l a2,a0
    move.l d2,d0
    bsr.w AGSP_P1C_VALIDATE  ; existing P1i validator, exact full payload
    tst.l d0
    beq.w s2c_pair_no
    tst.l d1
    beq.w s2c_pair_no
    lea 32(a2),a3
    subq.l #1,d1
s2c_pair_find:
    cmp.w (a3),d3
    beq.w s2c_pair_found
    bcs.w s2c_pair_no            ; IDs strictly sorted
    adda.w #48,a3
    dbra d1,s2c_pair_find
    bra.w s2c_pair_no
s2c_pair_found:
    cmpi.w #16,2(a3)
    bne.w s2c_pair_no
    cmpi.w #4,6(a3)
    bne.w s2c_pair_no
    cmpi.w #4,32(a3)
    bcs.w s2c_pair_no
    moveq #0,d4
    move.w 4(a3),d4        ; validated 1..256
    move.l d4,d5
    lsl.l #2,d5
    addq.l #8,d5
    move.l d5,d6
    lsl.l #2,d6
    addi.l #96,d6
    move.l d6,d0
    move.l #$00010003,d1   ; MEMF_PUBLIC|MEMF_CHIP|MEMF_CLEAR
    jsr -684(a6)           ; AllocVec
    tst.l d0
    beq.w s2c_pair_no
    movea.l d0,a4
    btst #0,d0
    bne.w s2c_pair_free
    add.l d6,d0
    bcs.w s2c_pair_free
    subq.l #1,d0
    move.l d0,d7
    movea.l a4,a1
    jsr -534(a6)
    btst #1,d0             ; require actual MEMF_CHIP, not bank flags
    beq.w s2c_pair_free
    movea.l d7,a1
    jsr -534(a6)
    btst #1,d0
    beq.w s2c_pair_free

    ; No fallible operations after this point; allocation is detached.
    clr.l (a4)
    move.w d4,4(a4)
    clr.l 6(a4)
    move.w #-1,10(a4)
    clr.l 12(a4)
    move.w d4,16(a4)
    clr.l 18(a4)
    move.w #-1,22(a4)
    move.l d6,24(a4)
    move.w d3,28(a4)
    move.w 32(a3),30(a4)
    move.l 24(a2),32(a4)
    move.l 28(a3),36(a4)
    movea.l a2,a0
    adda.l 20(a3),a0
    lea 40(a4),a5
    moveq #11,d0
s2c_pair_palette:
    move.l (a0)+,(a5)+
    dbra d0,s2c_pair_palette
    move.l d5,88(a4)
    move.l #96,92(a4)
    ; Plane-major -> two 16-bit words per row in each detached stream.
    ; All POS/CTL, terminal and spare bytes remain MEMF_CLEAR zero.
    movea.l a2,a0
    adda.l 12(a3),a0
    move.l d4,d0
    add.l d0,d0
    movea.l a0,a1
    adda.l d0,a1
    movea.l a1,a2
    adda.l d0,a2
    movea.l a2,a3
    adda.l d0,a3
    lea 100(a4),a5
    movea.l a5,a6
    adda.l d5,a6
    move.w d4,d0
    subq.w #1,d0
s2c_pair_rows:
    move.w (a0)+,(a5)+
    move.w (a1)+,(a5)+
    move.w (a2)+,(a6)+
    move.w (a3)+,(a6)+
    dbra d0,s2c_pair_rows
    move.l a4,d0
    move.l d6,d1
    bra.w s2c_pair_return
s2c_pair_free:
    movea.l a4,a1
    jsr -690(a6)          ; FreeVec only of unpublished allocation
s2c_pair_no:
    moveq #0,d0
    moveq #0,d1
s2c_pair_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"
