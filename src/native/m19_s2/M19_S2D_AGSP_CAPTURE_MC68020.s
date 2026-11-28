; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P0: standalone 16/32/64px capture kernel for the 0.15.0-alpha.1 workstream.
; Derived from the exact S2c source; existing S2c entry/descriptor stay intact.
; NOT AP20-linked or installed. NO DMA, no OS callbacks, no bank mutation.
;
; A0 -> validated descriptor (big endian):
;  +00 8 LONG pointers to source bitplanes 0..7 (first DEPTH nonzero)
;  +32 LONG pointer to 256*3-byte RGB24 ColorMap snapshot (RGB8 triples)
;  +36 LONG pointer to stage image planes (>=4*(CAPTURE_WIDTH/8)*CAPTURE_HEIGHT bytes)
;  +40 LONG pointer to stage 16*3 RGB24 local palette (48 bytes)
;  +44 LONG source bytesPerRow (even, 1..65535)
;  +48 WORD source width (1..4096)
;  +50 WORD source height (1..4096)
;  +52 WORD source depth (1..8)
;  +54 WORD capture X (>=0)
;  +56 WORD capture Y (>=0)
;  +58 WORD capture height (1..256)
;  +60 WORD source transparent pen 0..255
;  +62 WORD explicit capture width (16/32/64)
;
; Output: D0=1 success or 0 refused; D1=opaque color count on success.
; Preserves D2-D7/A2-A6. Requires valid accessible memory spans from caller.
; The caller MUST prove bitmap addresses, ColorMap snapshot ownership, Safe
; synchronization, and isolated stage buffers BEFORE calling this kernel.
; Stage is not published to an AMOS bank until D0=1; on error it can be junk.
; Color mapping is RGB24 exact, first appearance, max 15 opaque + transparent.
; The zero/unused local RGB slots remain zero, black can be opaque.
; Output depth=2 for 0..3 opaque, 4 for 4..15; plane-major (W/8)*H*depth.
; Stage must have 4*(W/8)*H bytes, only the actual image is written.
; The caller pins disjoint input and output spans and a stable snapshot.
;
AGSP_S2D_CAPTURE:
    movem.l d2-d7/a2-a6,-(sp)
    suba.w #64,sp
    movea.l sp,a3
    clr.l 60(a3)           ; 15 RGB32 slots, count.W at +60
    movea.l a0,a4
    moveq #0,d0
    moveq #0,d1
    move.l a4,d0
    beq.w AGSP_S2D_FAIL
    btst #0,d0
    bne.w AGSP_S2D_FAIL
    move.l 32(a4),d0
    beq.w AGSP_S2D_FAIL
    move.l 36(a4),d0
    beq.w AGSP_S2D_FAIL
    btst #0,d0
    bne.w AGSP_S2D_FAIL
    move.l 40(a4),d0
    beq.w AGSP_S2D_FAIL
    btst #0,d0
    bne.w AGSP_S2D_FAIL
    move.w 62(a4),d0
    cmpi.w #16,d0
    beq.s AGSP_S2D_WIDTH_OK
    cmpi.w #32,d0
    beq.s AGSP_S2D_WIDTH_OK
    cmpi.w #64,d0
    bne.w AGSP_S2D_FAIL
AGSP_S2D_WIDTH_OK:
    move.l 44(a4),d0
    beq.w AGSP_S2D_FAIL
    cmpi.l #65535,d0
    bhi.w AGSP_S2D_FAIL
    btst #0,d0
    bne.w AGSP_S2D_FAIL
    moveq #0,d1
    move.w 48(a4),d1
    beq.w AGSP_S2D_FAIL
    cmpi.w #4096,d1
    bhi.w AGSP_S2D_FAIL
    move.l d1,d2
    addq.l #7,d2
    lsr.l #3,d2
    cmp.l d2,d0
    bcs.w AGSP_S2D_FAIL
    move.w 50(a4),d0
    beq.w AGSP_S2D_FAIL
    cmpi.w #4096,d0
    bhi.w AGSP_S2D_FAIL
    move.w 52(a4),d0
    beq.w AGSP_S2D_FAIL
    cmpi.w #8,d0
    bhi.w AGSP_S2D_FAIL
    moveq #0,d0
    move.w 54(a4),d0
    moveq #0,d2
    move.w 62(a4),d2
    add.l d2,d0
    cmp.l d1,d0
    bhi.w AGSP_S2D_FAIL
    moveq #0,d1
    move.w 56(a4),d1
    moveq #0,d0
    move.w 58(a4),d0
    beq.w AGSP_S2D_FAIL
    cmpi.w #256,d0
    bhi.w AGSP_S2D_FAIL
    add.l d1,d0
    moveq #0,d1
    move.w 50(a4),d1
    cmp.l d1,d0
    bhi.w AGSP_S2D_FAIL
    move.w 60(a4),d0
    cmpi.w #255,d0
    bhi.w AGSP_S2D_FAIL
    move.w 52(a4),d0
    movea.l a4,a5
AGSP_S2D_CHECK_PLANES:
    tst.l (a5)+
    beq.w AGSP_S2D_FAIL
    subq.w #1,d0
    bne.w AGSP_S2D_CHECK_PLANES

    ; PASS 1 - build up to fifteen distinct RGB24 colors before altering stage output.
    moveq #0,d6
AGSP_S2D_SCAN_ROW:
    moveq #0,d7
AGSP_S2D_SCAN_COL:
    moveq #0,d2
    move.w 54(a4),d2
    add.w d7,d2
    moveq #0,d3
    move.w 56(a4),d3
    add.w d6,d3
    bsr.w AGSP_S2D_READ_INDEX
    cmp.w 60(a4),d0
    beq.w AGSP_S2D_SCAN_NEXT
    bsr.w AGSP_S2D_READ_RGB
    moveq #0,d4
AGSP_S2D_SCAN_MATCH:
    cmp.w 60(a3),d4
    bcc.s AGSP_S2D_SCAN_NEW
    move.w d4,d5
    lsl.w #2,d5
    cmp.l 0(a3,d5.w),d0
    beq.s AGSP_S2D_SCAN_NEXT
    addq.w #1,d4
    bra.s AGSP_S2D_SCAN_MATCH
AGSP_S2D_SCAN_NEW:
    cmpi.w #15,d4
    bcc.w AGSP_S2D_FAIL       ; 16th distinct opaque RGB, no stage writes
    lsl.w #2,d4
    move.l d0,0(a3,d4.w)
    addq.w #1,60(a3)
AGSP_S2D_SCAN_NEXT:
    addq.w #1,d7
    cmp.w 62(a4),d7
    bcs.w AGSP_S2D_SCAN_COL
    addq.w #1,d6
    cmp.w 58(a4),d6
    bcs.w AGSP_S2D_SCAN_ROW

    ; PASS 2 - stage palette and plane-major pixels, never touch display.
    movea.l 36(a4),a5
    moveq #0,d4
    move.w 58(a4),d4
    moveq #0,d2
    move.w 62(a4),d2
    lsr.w #4,d2             ; longwords per row for two planes
    mulu.w d2,d4
    cmpi.w #3,60(a3)
    bls.s AGSP_S2D_ZERO_PLANES
    add.w d4,d4
AGSP_S2D_ZERO_PLANES:
    clr.l (a5)+
    subq.w #1,d4
    bne.w AGSP_S2D_ZERO_PLANES
    movea.l 40(a4),a5
    moveq #11,d4
AGSP_S2D_ZERO_PALETTE:
    clr.l (a5)+
    dbra d4,AGSP_S2D_ZERO_PALETTE

    movea.l 40(a4),a5
    adda.l #3,a5
    moveq #0,d6
AGSP_S2D_COPY_PALETTE:
    cmp.w 60(a3),d6
    bcc.w AGSP_S2D_DRAW_START
    move.l d6,d4
    lsl.l #2,d4
    move.l 0(a3,d4.l),d0
    move.l d0,d2
    swap d2
    move.b d2,(a5)+
    move.l d0,d2
    lsr.l #8,d2
    move.b d2,(a5)+
    move.b d0,(a5)+
    addq.w #1,d6
    bra.w AGSP_S2D_COPY_PALETTE

AGSP_S2D_DRAW_START:
    moveq #0,d6
AGSP_S2D_DRAW_ROW:
    moveq #0,d7
AGSP_S2D_DRAW_COL:
    moveq #0,d2
    move.w 54(a4),d2
    add.w d7,d2
    moveq #0,d3
    move.w 56(a4),d3
    add.w d6,d3
    bsr.w AGSP_S2D_READ_INDEX
    cmp.w 60(a4),d0
    beq.w AGSP_S2D_DRAW_NEXT
    bsr.w AGSP_S2D_READ_RGB
    moveq #0,d4
AGSP_S2D_DRAW_MATCH:
    cmp.w 60(a3),d4
    bcc.w AGSP_S2D_FAIL       ; changed snapshot, detached stage not publishable
    move.w d4,d5
    lsl.w #2,d5
    cmp.l 0(a3,d5.w),d0
    beq.s AGSP_S2D_WRITE_PIXEL
    addq.w #1,d4
    bra.s AGSP_S2D_DRAW_MATCH
AGSP_S2D_WRITE_PIXEL:
    addq.w #1,d4            ; local opaque index 1..15
    moveq #0,d5
    move.w d6,d5
    moveq #0,d2
    move.w 62(a4),d2
    lsr.w #3,d2
    mulu.w d2,d5           ; row offset = y * bytesPerRow
    move.w d7,d2
    lsr.w #3,d2
    add.l d2,d5
    moveq #7,d1
    move.w d7,d2
    andi.w #7,d2
    sub.w d2,d1
    movea.l 36(a4),a5
    moveq #0,d2
    move.w 58(a4),d2
    moveq #0,d3
    move.w 62(a4),d3
    lsr.w #3,d3
    mulu.w d3,d2           ; one complete plane, (W/8)*height bytes
    moveq #2,d3
    cmpi.w #3,60(a3)
    bls.s AGSP_S2D_WRITE_PLANE
    moveq #4,d3
AGSP_S2D_WRITE_PLANE:
    btst #0,d4
    beq.s AGSP_S2D_PLANE_NEXT
    bset d1,0(a5,d5.l)
AGSP_S2D_PLANE_NEXT:
    lsr.w #1,d4
    add.l d2,d5
    subq.w #1,d3
    bne.s AGSP_S2D_WRITE_PLANE
AGSP_S2D_DRAW_NEXT:
    addq.w #1,d7
    cmp.w 62(a4),d7
    bcs.w AGSP_S2D_DRAW_COL
    addq.w #1,d6
    cmp.w 58(a4),d6
    bcs.w AGSP_S2D_DRAW_ROW

    moveq #1,d0
    moveq #0,d1
    move.w 60(a3),d1
    bra.w AGSP_S2D_EXIT
AGSP_S2D_FAIL:
    moveq #0,d0
    moveq #0,d1
AGSP_S2D_EXIT:
    adda.w #64,sp
    movem.l (sp)+,d2-d7/a2-a6
    rts

; Helper: D2=x, D3=y; A4=descriptor; D0=source pixel pen.
; Preserves all main-loop registers except D0, condition codes.
AGSP_S2D_READ_INDEX:
    movem.l d2-d5/a5-a6,-(sp)
    move.l 44(a4),d4
    mulu.w d4,d3
    moveq #0,d5
    move.w d2,d5
    lsr.l #3,d5
    add.l d5,d3
    moveq #7,d5
    andi.w #7,d2
    sub.w d2,d5
    moveq #0,d0
    movea.l a4,a5
    moveq #1,d2
    move.w 52(a4),d4
AGSP_S2D_READ_PLANE:
    movea.l (a5)+,a6
    btst d5,0(a6,d3.l)
    beq.w AGSP_S2D_READ_ZERO
    or.w d2,d0
AGSP_S2D_READ_ZERO:
    add.w d2,d2
    subq.w #1,d4
    bne.w AGSP_S2D_READ_PLANE
    movem.l (sp)+,d2-d5/a5-a6
    rts

; Helper: D0=source pen; A4=descriptor; D0=$00RRGGBB.
AGSP_S2D_READ_RGB:
    movem.l d5/a5,-(sp)
    move.w d0,d5
    mulu.w #3,d5
    movea.l 32(a4),a5
    moveq #0,d0
    move.b 0(a5,d5.l),d0
    lsl.l #8,d0
    move.b 1(a5,d5.l),d0
    lsl.l #8,d0
    move.b 2(a5,d5.l),d0
    movem.l (sp)+,d5/a5
    rts
