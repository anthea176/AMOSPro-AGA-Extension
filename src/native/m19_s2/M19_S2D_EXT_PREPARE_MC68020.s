; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P2a: detached OS-owned ExtSprite preparation (no DMA publication).
; Source: validated AGSP v1, 16/32/64 px, 2/4 planes, H=1..256.
; A0 = pinned payload, D0 exact allocated extent, D1 image ID.
; A6 = live, caller-owned graphics.library base; caller pins this library,
; the entire source allocation and source lifetime for the synchronous call.
; D0=detached even/single ExtSprite*, D1=detached odd ExtSprite* or 0.
; D0/D1 both 0 on refusal. Preserve D2-D7/A0-A6.
; The caller owns each returned pointer and must eventually FreeSpriteData
; (only when detached or separately proven retired). No AMOS bank mutation,
; channel acquisition, FMODE, ViewPort, palette, or ExtSprite-field writes.
; V39 attached uses documented control-bit repair on detached odd data.
; V40+ attached: SPRITEA_Attached reads planes 2 and 3 of the SAME BitMap.
; NDK graphics/gfx.h, graphics/sprite.h, exec/libraries.h;
; graphics.library InitBitMap/AllocSpriteDataA/FreeSpriteData autodocs.
;
S2D_E_BITMAP    equ 0
S2D_E_TAGS      equ 40
S2D_E_FRAME     equ 64
S2D_E_WIDTH_TAG equ $81000000
S2D_E_ATTACH_TAG equ $81000008
S2D_E_INITBM    equ -390
S2D_E_ALLOC     equ -1020
S2D_E_FREE      equ -1032

AGSP_S2D_PREPARE_EXT:
    movem.l d2-d7/a0-a6,-(sp)
    suba.w #S2D_E_FRAME,sp
    movea.l sp,a3
    movea.l a0,a4
    movea.l a6,a5
    move.l d0,d2
    move.l d1,d3
    move.l a5,d0
    beq.w s2d_ext_bad
    btst #0,d0
    bne.w s2d_ext_bad
    ; Base is a pinned Library, not a general caller-supplied memory probe.
    cmpi.w #34,18(a5)       ; lib_PosSize
    bcs.w s2d_ext_bad
    cmpi.w #1032,16(a5)     ; lib_NegSize covers FreeSpriteData
    bcs.w s2d_ext_bad
    cmpi.w #39,20(a5)       ; lib_Version
    bcs.w s2d_ext_bad
    cmpi.l #1,d3
    bcs.w s2d_ext_bad
    cmpi.l #4096,d3
    bhi.w s2d_ext_bad
    cmpi.l #32,d2
    bcs.w s2d_ext_bad
    cmpi.l #$01000000,d2
    bhi.w s2d_ext_bad
    btst #0,d2
    bne.w s2d_ext_bad
    move.l a4,d0
    beq.w s2d_ext_bad
    btst #0,d0
    bne.w s2d_ext_bad
    add.l d2,d0
    bcs.w s2d_ext_bad
    subq.l #1,d0
    move.l d0,d4
    movea.l $0004.w,a6
    movea.l a4,a1
    jsr -534(a6)           ; Exec.TypeOfMem first byte, not extent proof
    tst.l d0
    beq.w s2d_ext_bad
    movea.l d4,a1
    jsr -534(a6)           ; last byte
    tst.l d0
    beq.w s2d_ext_bad
    movea.l a4,a0
    move.l d2,d0
    bsr.w AGSP_P1C_VALIDATE
    tst.l d0
    beq.w s2d_ext_bad
    tst.l d1
    beq.w s2d_ext_bad
    lea 32(a4),a2
    subq.l #1,d1
s2d_ext_find:
    cmp.w (a2),d3
    beq.s s2d_ext_found
    bcs.w s2d_ext_bad
    adda.w #48,a2
    dbra d1,s2d_ext_find
    bra.w s2d_ext_bad
s2d_ext_found:
    moveq #0,d5
    move.w 6(a2),d5        ; canonical validator already proves 2 or 4
    moveq #0,d6
    move.w 2(a2),d6
    moveq #0,d7
    move.w 4(a2),d7
    moveq #0,d4
    move.w 8(a2),d4
    move.l d4,d2
    mulu.w d7,d2          ; exact bytes per plane
    movea.l a4,a0
    adda.l 12(a2),a0
    movea.l a0,a4         ; first plane, stable read-only memory

    ; A standard BitMap descriptor, initialized by graphics.library.
    ; Planes may reside in Fast: AllocSpriteDataA converts/copies them.
    movea.l a3,a0
    moveq #15,d0
s2d_ext_clear:
    clr.l (a0)+
    dbra d0,s2d_ext_clear
    lea S2D_E_BITMAP(a3),a0
    move.l d5,d0
    move.l d6,d1
    move.l d7,-(sp)
    move.l d2,-(sp)
    move.l d7,d2
    movea.l a5,a6
    jsr S2D_E_INITBM(a6)
    move.l (sp)+,d2
    move.l (sp)+,d7
    cmp.w S2D_E_BITMAP(a3),d4
    bne.w s2d_ext_bad
    cmp.w S2D_E_BITMAP+2(a3),d7
    bne.w s2d_ext_bad
    cmp.b S2D_E_BITMAP+5(a3),d5
    bne.w s2d_ext_bad
    lea S2D_E_BITMAP+8(a3),a0
    movea.l a4,a1
    move.w d5,d0
    subq.w #1,d0
s2d_ext_planes:
    move.l a1,(a0)+
    adda.l d2,a1
    dbra d0,s2d_ext_planes

    ; Explicit requested width; natural height and 1:1 replication.
    lea S2D_E_TAGS(a3),a1
    move.l #S2D_E_WIDTH_TAG,(a1)
    move.l d6,4(a1)
    lea S2D_E_BITMAP(a3),a2
    jsr S2D_E_ALLOC(a6)    ; AllocSpriteDataA(A2=BitMap,A1=tags)
    tst.l d0
    beq.w s2d_ext_bad
    move.l d0,d4
    moveq #0,d1
    cmpi.w #4,d5
    bne.w s2d_ext_success

    ; Second call converts high planes from same source bitmap.
    lea S2D_E_TAGS(a3),a1
    move.l #S2D_E_ATTACH_TAG,8(a1)
    move.l #1,12(a1)
    lea S2D_E_BITMAP(a3),a2
    jsr S2D_E_ALLOC(a6)
    tst.l d0
    beq.s s2d_ext_rollback
    cmp.l d4,d0
    beq.s s2d_ext_rollback
    move.l d0,d3
    cmpi.w #39,20(a5)
    bne.s s2d_ext_odd_ok
    movea.l d3,a0
    move.l d6,d0
    move.l d7,d1
    bsr.w AGSP_S2D_ATTACH39
    tst.l d0
    beq.s s2d_ext_rollback_both
s2d_ext_odd_ok:
    move.l d3,d1
s2d_ext_success:
    move.l d4,d0
    bra.s s2d_ext_return
s2d_ext_rollback_both:
    movea.l d3,a2
    jsr S2D_E_FREE(a6)
s2d_ext_rollback:
    movea.l d4,a2
    jsr S2D_E_FREE(a6)     ; only detached allocation, never FreeVec
s2d_ext_bad:
    moveq #0,d0
    moveq #0,d1
s2d_ext_return:
    adda.w #S2D_E_FRAME,sp
    movem.l (sp)+,d2-d7/a0-a6
    rts

    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"

    include "M19_S2D_EXT_ATTACH_V39_MC68020.s"
