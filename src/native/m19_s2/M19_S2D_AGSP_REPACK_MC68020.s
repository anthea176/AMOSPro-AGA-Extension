; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P0: private AGSP v1 repacker for one 16/32/64px, 2/4bpp capture.
; Derived from S2c. Only the detached request changes; disk format remains v1.
; CPU-backed staging only, NOT an AMOS bank publisher or AP20 token.
; Input A0 -> 40-byte request, prevalidated memory spans:
; +0 old AGSP payload pointer (0 for empty), +4 old payload size (0 empty)
; +8 staged planes [(W/8)*H*depth, depth=2/4 inferred from colors], +12 RGB24 local palette [48]
; +16 destination staging pointer, +20 staging capacity (<=16MiB)
; +24 WORD image ID 1..4096, +26 WORD H 1..256
; +28 WORD opaque colors 0..15, +30 WORD source transparent pen 0..255
; +32 WORD signed hotspot X, +34 WORD signed hotspot Y, +36 WORD width 16/32/64, +38 WORD zero
; Output D0 = resulting AGSP payload length on success, 0 on failure.
; D1 = 1 success / 0 failure. Preserves D2-D7/A2-A6.
; Full pixel canonicality of existing AGSP requires caller validation;
; this module checks header, dimensions, directory ordering and data bounds.
; No memory writes on input/capacity refusal; old payload never mutated.
; On success caller may publish the whole payload through an AMOS
; detached-node transaction after separately verifying the destination.

AGSP_S2DR_OLD      equ 0
AGSP_S2DR_OLDLEN   equ 4
AGSP_S2DR_PLANE    equ 8
AGSP_S2DR_PAL      equ 12
AGSP_S2DR_DST      equ 16
AGSP_S2DR_CAP      equ 20
AGSP_S2DR_ID       equ 24
AGSP_S2DR_HEIGHT   equ 28
AGSP_S2DR_COLORS   equ 32
AGSP_S2DR_TRANS    equ 36
AGSP_S2DR_HOTX     equ 40
AGSP_S2DR_HOTY     equ 44
AGSP_S2DR_OLDCOUNT equ 48
AGSP_S2DR_NEWCOUNT equ 52
AGSP_S2DR_OLDEND   equ 56
AGSP_S2DR_NEWEND   equ 60
AGSP_S2DR_CURSOR   equ 64
AGSP_S2DR_GEN      equ 68
AGSP_S2DR_NEWLEN   equ 72
AGSP_S2DR_REPLACE  equ 76
AGSP_S2DR_FOUND    equ 80
AGSP_S2DR_LASTID   equ 84
AGSP_S2DR_LASTPTR  equ 88
AGSP_S2DR_NEWDEPTH equ 92
AGSP_S2DR_WIDTH    equ 96
AGSP_S2DR_STRIDE   equ 100
AGSP_S2DR_FRAME    equ 104

AGSP_S2D_REPACK_ONE:
    movem.l d2-d7/a2-a6,-(sp)
    suba.l #AGSP_S2DR_FRAME,sp
    movea.l sp,a2
    movea.l a0,a6
    moveq #0,d0
    moveq #0,d1
    move.l a6,d0
    beq.w agsp_s2dr_bad
    btst #0,d0
    bne.w agsp_s2dr_bad
    tst.w 38(a6)
    bne.w agsp_s2dr_bad
    moveq #0,d0
    move.w 36(a6),d0
    cmpi.w #16,d0
    beq.s agsp_s2dr_input_width_ok
    cmpi.w #32,d0
    beq.s agsp_s2dr_input_width_ok
    cmpi.w #64,d0
    bne.w agsp_s2dr_bad
agsp_s2dr_input_width_ok:
    move.l d0,AGSP_S2DR_WIDTH(a2)
    lsr.l #3,d0
    move.l d0,AGSP_S2DR_STRIDE(a2)
    move.l (a6),AGSP_S2DR_OLD(a2)
    move.l 4(a6),AGSP_S2DR_OLDLEN(a2)
    move.l 8(a6),AGSP_S2DR_PLANE(a2)
    move.l 12(a6),AGSP_S2DR_PAL(a2)
    move.l 16(a6),AGSP_S2DR_DST(a2)
    move.l 20(a6),AGSP_S2DR_CAP(a2)
    moveq #0,d0
    move.w 24(a6),d0
    cmpi.l #1,d0
    bcs.w agsp_s2dr_bad
    cmpi.l #4096,d0
    bhi.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_ID(a2)
    moveq #0,d0
    move.w 26(a6),d0
    beq.w agsp_s2dr_bad
    cmpi.l #256,d0
    bhi.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_HEIGHT(a2)
    moveq #0,d0
    move.w 28(a6),d0
    cmpi.l #15,d0
    bhi.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_COLORS(a2)
    moveq #2,d1
    cmpi.l #3,d0
    bls.s agsp_s2dr_new_depth
    moveq #4,d1
agsp_s2dr_new_depth:
    move.l d1,AGSP_S2DR_NEWDEPTH(a2)
    moveq #0,d0
    move.w 30(a6),d0
    cmpi.l #255,d0
    bhi.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_TRANS(a2)
    move.w 32(a6),AGSP_S2DR_HOTX+2(a2)
    move.w 34(a6),AGSP_S2DR_HOTY+2(a2)
    clr.l AGSP_S2DR_FOUND(a2)
    clr.l AGSP_S2DR_REPLACE(a2)
    clr.l AGSP_S2DR_LASTID(a2)
    clr.l AGSP_S2DR_OLDCOUNT(a2)
    move.l #1,AGSP_S2DR_GEN(a2)
    move.l #32,AGSP_S2DR_OLDEND(a2)
    move.l AGSP_S2DR_CAP(a2),d0
    cmpi.l #32,d0
    bcs.w agsp_s2dr_bad
    cmpi.l #$01000000,d0
    bhi.w agsp_s2dr_bad
    moveq #8,d6
agsp_s2dr_ptrs:
    move.l 0(a6,d6.w),d0
    beq.w agsp_s2dr_bad
    btst #0,d0
    bne.w agsp_s2dr_bad
    addq.w #4,d6
    cmpi.w #16,d6
    bls.w agsp_s2dr_ptrs
    move.l AGSP_S2DR_OLDLEN(a2),d5
    beq.w agsp_s2dr_old_empty
    cmpi.l #32,d5
    bcs.w agsp_s2dr_bad
    cmpi.l #$01000000,d5
    bhi.w agsp_s2dr_bad
    movea.l AGSP_S2DR_OLD(a2),a3
    move.l a3,d0
    beq.w agsp_s2dr_bad
    btst #0,d0
    bne.w agsp_s2dr_bad
    cmp.l AGSP_S2DR_DST(a2),d0
    beq.w agsp_s2dr_bad
    cmpi.l #$41475350,(a3)
    bne.w agsp_s2dr_bad
    cmpi.w #1,4(a3)
    bne.w agsp_s2dr_bad
    tst.w 6(a3)
    bne.w agsp_s2dr_bad
    moveq #0,d6
    move.w 8(a3),d6
    cmpi.l #4096,d6
    bhi.w agsp_s2dr_bad
    move.l d6,AGSP_S2DR_OLDCOUNT(a2)
    cmpi.w #48,10(a3)
    bne.w agsp_s2dr_bad
    cmpi.l #32,12(a3)
    bne.w agsp_s2dr_bad
    move.l d6,d0
    mulu.w #48,d0
    addi.l #32,d0
    cmp.l d5,d0
    bhi.w agsp_s2dr_bad
    cmp.l 16(a3),d0
    bne.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_OLDEND(a2)
    cmp.l 20(a3),d5
    bne.w agsp_s2dr_bad
    move.l 24(a3),d0
    beq.w agsp_s2dr_bad
    cmpi.l #$ffffffff,d0
    beq.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_GEN(a2)
    tst.l 28(a3)
    bne.w agsp_s2dr_bad
    lea 32(a3),a3
    move.l AGSP_S2DR_OLDEND(a2),AGSP_S2DR_CURSOR(a2)
    moveq #0,d5
agsp_s2dr_validate_next:
    tst.l d6
    beq.w agsp_s2dr_validate_end
    moveq #0,d0
    move.w (a3),d0
    cmp.l AGSP_S2DR_LASTID(a2),d0
    bls.w agsp_s2dr_bad
    cmpi.l #4096,d0
    bhi.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_LASTID(a2)
    moveq #0,d1
    move.w 2(a3),d1
    cmpi.w #16,d1
    beq.w agsp_s2dr_width_ok
    cmpi.w #32,d1
    beq.w agsp_s2dr_width_ok
    cmpi.w #64,d1
    bne.w agsp_s2dr_bad
agsp_s2dr_width_ok:
    lsr.l #3,d1
    cmp.w 8(a3),d1
    bne.w agsp_s2dr_bad
    moveq #0,d0
    move.w 4(a3),d0
    beq.w agsp_s2dr_bad
    cmpi.w #256,d0
    bhi.w agsp_s2dr_bad
    mulu.w d1,d0
    moveq #0,d1
    move.w 6(a3),d1
    cmpi.w #2,d1
    beq.w agsp_s2dr_depth_ok
    cmpi.w #4,d1
    bne.w agsp_s2dr_bad
agsp_s2dr_depth_ok:
    mulu.w d1,d0
    tst.w 10(a3)
    bne.w agsp_s2dr_bad
    cmp.l 16(a3),d0
    bne.w agsp_s2dr_bad
    move.l AGSP_S2DR_CURSOR(a2),d1
    cmp.l 12(a3),d1
    bne.w agsp_s2dr_bad
    add.l d0,d1
    bcs.w agsp_s2dr_bad
    cmp.l 20(a3),d1
    bne.w agsp_s2dr_bad
    cmpi.l #48,24(a3)
    bne.w agsp_s2dr_bad
    addi.l #48,d1
    bcs.w agsp_s2dr_bad
    cmp.l AGSP_S2DR_OLDLEN(a2),d1
    bhi.w agsp_s2dr_bad
    move.l d1,AGSP_S2DR_CURSOR(a2)
    moveq #0,d0
    move.w 32(a3),d0
    cmpi.w #4,6(a3)
    beq.w agsp_s2dr_four_depth
    cmpi.l #3,d0
    bhi.w agsp_s2dr_bad
    bra.w agsp_s2dr_colors_ok
agsp_s2dr_four_depth:
    cmpi.l #15,d0
    bhi.w agsp_s2dr_bad
agsp_s2dr_colors_ok:
    cmpi.w #255,34(a3)
    bhi.w agsp_s2dr_bad
    tst.l 36(a3)
    bne.w agsp_s2dr_bad
    tst.l 40(a3)
    bne.w agsp_s2dr_bad
    tst.l 44(a3)
    bne.w agsp_s2dr_bad
    moveq #0,d0
    move.w (a3),d0
    cmp.l AGSP_S2DR_ID(a2),d0
    bne.w agsp_s2dr_no_match
    move.l 16(a3),d0
    addi.l #48,d0
    move.l d0,AGSP_S2DR_REPLACE(a2)
    move.l #1,AGSP_S2DR_FOUND(a2)
agsp_s2dr_no_match:
    adda.l #48,a3
    subq.l #1,d6
    bra.w agsp_s2dr_validate_next
agsp_s2dr_validate_end:
    move.l AGSP_S2DR_CURSOR(a2),d0
    cmp.l AGSP_S2DR_OLDLEN(a2),d0
    bne.w agsp_s2dr_bad
agsp_s2dr_old_empty:
    move.l AGSP_S2DR_OLDCOUNT(a2),d0
    tst.l AGSP_S2DR_FOUND(a2)
    bne.w agsp_s2dr_same_count
    addq.l #1,d0
agsp_s2dr_same_count:
    cmpi.l #4096,d0
    bhi.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_NEWCOUNT(a2)
    mulu.w #48,d0
    addi.l #32,d0
    move.l d0,AGSP_S2DR_NEWEND(a2)
    move.l AGSP_S2DR_OLDLEN(a2),d1
    beq.w agsp_s2dr_size_empty
    sub.l AGSP_S2DR_OLDEND(a2),d1
agsp_s2dr_size_empty:
    add.l d1,d0
    bcs.w agsp_s2dr_bad
    sub.l AGSP_S2DR_REPLACE(a2),d0
    bcs.w agsp_s2dr_bad
    move.l AGSP_S2DR_HEIGHT(a2),d1
    mulu.w AGSP_S2DR_NEWDEPTH+2(a2),d1
    mulu.w AGSP_S2DR_STRIDE+2(a2),d1
    addi.l #48,d1
    add.l d1,d0
    bcs.w agsp_s2dr_bad
    cmpi.l #$01000000,d0
    bhi.w agsp_s2dr_bad
    cmp.l AGSP_S2DR_CAP(a2),d0
    bhi.w agsp_s2dr_bad
    move.l d0,AGSP_S2DR_NEWLEN(a2)

    ; All input validation complete. Now write only to the detached stage.
    movea.l AGSP_S2DR_DST(a2),a0
    move.l #$41475350,(a0)
    move.w #1,4(a0)
    clr.w 6(a0)
    move.w AGSP_S2DR_NEWCOUNT+2(a2),8(a0)
    move.w #48,10(a0)
    move.l #32,12(a0)
    move.l AGSP_S2DR_NEWEND(a2),16(a0)
    move.l AGSP_S2DR_NEWLEN(a2),20(a0)
    move.l AGSP_S2DR_GEN(a2),d0
    addq.l #1,d0
    move.l d0,24(a0)
    clr.l 28(a0)
    lea 32(a0),a4
    movea.l a0,a5
    adda.l AGSP_S2DR_NEWEND(a2),a5
    clr.l AGSP_S2DR_FOUND(a2)
    movea.l AGSP_S2DR_OLD(a2),a3
    tst.l AGSP_S2DR_OLDLEN(a2)
    beq.w agsp_s2dr_copy_end
    adda.l #32,a3
    move.l AGSP_S2DR_OLDCOUNT(a2),d6
agsp_s2dr_copy_next:
    tst.l d6
    beq.w agsp_s2dr_copy_end
    tst.l AGSP_S2DR_FOUND(a2)
    bne.w agsp_s2dr_copy_after_insert
    moveq #0,d0
    move.w (a3),d0
    cmp.l AGSP_S2DR_ID(a2),d0
    bcs.w agsp_s2dr_copy_after_insert
    bsr.w agsp_s2dr_emit_new
agsp_s2dr_copy_after_insert:
    moveq #0,d0
    move.w (a3),d0
    cmp.l AGSP_S2DR_ID(a2),d0
    beq.w agsp_s2dr_copy_skip
    bsr.w agsp_s2dr_emit_old
agsp_s2dr_copy_skip:
    adda.l #48,a3
    subq.l #1,d6
    bra.w agsp_s2dr_copy_next
agsp_s2dr_copy_end:
    tst.l AGSP_S2DR_FOUND(a2)
    bne.w agsp_s2dr_copy_done
    bsr.w agsp_s2dr_emit_new
agsp_s2dr_copy_done:
    move.l a5,d0
    sub.l AGSP_S2DR_DST(a2),d0
    cmp.l AGSP_S2DR_NEWLEN(a2),d0
    bne.w agsp_s2dr_bad
    move.l d0,d1
    moveq #1,d0
    exg d0,d1                   ; D0 = size, D1 = 1
    bra.w agsp_s2dr_exit

agsp_s2dr_emit_new:
    move.w AGSP_S2DR_ID+2(a2),(a4)
    move.w AGSP_S2DR_WIDTH+2(a2),2(a4)
    move.w AGSP_S2DR_HEIGHT+2(a2),4(a4)
    move.w AGSP_S2DR_NEWDEPTH+2(a2),6(a4)
    move.w AGSP_S2DR_STRIDE+2(a2),8(a4)
    clr.w 10(a4)
    move.l a5,d0
    sub.l AGSP_S2DR_DST(a2),d0
    move.l d0,12(a4)
    move.l AGSP_S2DR_HEIGHT(a2),d1
    mulu.w AGSP_S2DR_NEWDEPTH+2(a2),d1
    mulu.w AGSP_S2DR_STRIDE+2(a2),d1
    move.l d1,16(a4)
    add.l d1,d0
    move.l d0,20(a4)
    move.l #48,24(a4)
    move.w AGSP_S2DR_HOTX+2(a2),28(a4)
    move.w AGSP_S2DR_HOTY+2(a2),30(a4)
    move.w AGSP_S2DR_COLORS+2(a2),32(a4)
    move.w AGSP_S2DR_TRANS+2(a2),34(a4)
    clr.l 36(a4)
    clr.l 40(a4)
    clr.l 44(a4)
    adda.l #48,a4
    movea.l AGSP_S2DR_PLANE(a2),a0
    move.l AGSP_S2DR_HEIGHT(a2),d7
    mulu.w AGSP_S2DR_NEWDEPTH+2(a2),d7
    mulu.w AGSP_S2DR_STRIDE+2(a2),d7
    lsr.l #2,d7             ; copy exact number of longwords
    subq.l #1,d7
agsp_s2dr_new_planes:
    move.l (a0)+,(a5)+
    dbra d7,agsp_s2dr_new_planes
    movea.l AGSP_S2DR_PAL(a2),a0
    moveq #11,d7
agsp_s2dr_new_palette:
    move.l (a0)+,(a5)+
    dbra d7,agsp_s2dr_new_palette
    move.l #1,AGSP_S2DR_FOUND(a2)
    rts

agsp_s2dr_emit_old:
    movea.l a4,a1
    movea.l a3,a0
    moveq #11,d7
agsp_s2dr_copy_entry:
    move.l (a0)+,(a4)+
    dbra d7,agsp_s2dr_copy_entry
    move.l a5,d0
    sub.l AGSP_S2DR_DST(a2),d0
    move.l d0,12(a1)
    move.l 16(a3),d1
    add.l d1,d0
    move.l d0,20(a1)
    movea.l AGSP_S2DR_OLD(a2),a0
    adda.l 12(a3),a0
    move.l 16(a3),d7
    addi.l #48,d7
    lsr.l #2,d7
    subq.l #1,d7
agsp_s2dr_copy_pixels:
    move.l (a0)+,(a5)+
    dbra d7,agsp_s2dr_copy_pixels
    rts

agsp_s2dr_bad:
    moveq #0,d0
    moveq #0,d1
agsp_s2dr_exit:
    adda.l #AGSP_S2DR_FRAME,sp
    movem.l (sp)+,d2-d7/a2-a6
    rts
