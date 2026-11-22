; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 public entry $05150 source-verified against pinned P2d emitter.
; UNIT142+$05150..$052CA, 378 instructions/data bytes.
UNIT142_BLOCK_05150_RESULT equ 0

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d7
    movea.l (a3)+,a4
    move.l #$00000000,d3
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_052A6
    move.l (a2),d6
    tst.l d6
    beq.w L_UNIT142_052A6
    move.l 8(a2),d0
    tst.l d0
    beq.w L_UNIT142_052A6
    tst.l d7
    bne.w L_UNIT142_051CA
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_05198
    move.l #$00000000,d0
    move.w (a4),d0
    tst.l d0
    bne.w L_UNIT142_052A6
L_UNIT142_05198:
    movea.l d6,a0
    bsr.w L_UNIT142_052AE
    tst.l d0
    beq.w L_UNIT142_051C0
    lea L_UNIT142_05302(pc),a1
    move.l #$00000000,(a1)
    move.l #$00000000,4(a1)
    movea.l d0,a1
    movea.l 8(a2),a6
    bsr.w L_UNIT142_056A6
L_UNIT142_051C0:
    move.l #$00000001,d3
    bra.w L_UNIT142_052A6
L_UNIT142_051CA:
    cmpi.l #$000000FF,d7
    bhi.w L_UNIT142_052A6
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_052A6
    move.l #$00000000,d5
    move.w (a4),d5
    tst.l d5
    beq.w L_UNIT142_052A6
    cmpi.l #$0000007F,d5
    bhi.w L_UNIT142_052A6
    lea -176(a7),a7
    lea 16(a7),a0
    movea.l a4,a1
    addq.l #2,a1
    move.l d5,d4
    subq.l #1,d4
L_UNIT142_05204:
    move.b (a1)+,d0
    tst.b d0
    beq.w L_UNIT142_052A2
    move.b d0,(a0)+
    dbra d4,L_UNIT142_05204
    clr.b (a0)
    lea 16(a7),a0
    move.l a0,(a7)
    move.w d7,4(a7)
    move.w #$0000,6(a7)
    move.l #$6469736B,144(a7)
    move.l #$666F6E74,148(a7)
    move.l #$2E6C6962,152(a7)
    move.l #$72617279,156(a7)
    clr.b 160(a7)
    lea 144(a7),a1
    move.l #$00000000,d0
    movea.l $0004.w,a6
    jsr -552(a6)
    tst.l d0
    beq.w L_UNIT142_052A2
    movea.l d0,a6
    movea.l a7,a0
    jsr -30(a6)
    move.l d0,d4
    movea.l a6,a1
    movea.l $0004.w,a6
    jsr -414(a6)
    tst.l d4
    beq.w L_UNIT142_052A2
    movea.l d6,a0
    bsr.w L_UNIT142_052AE
    move.l d0,d5
    lea L_UNIT142_05302(pc),a1
    move.l d6,(a1)
    move.l d4,4(a1)
    tst.l d5
    beq.w L_UNIT142_0529C
    movea.l d5,a1
    movea.l 8(a2),a6
    bsr.w L_UNIT142_056A6
L_UNIT142_0529C:
    move.l #$00000001,d3
L_UNIT142_052A2:
    lea 176(a7),a7
L_UNIT142_052A6:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_05150_RESULT,d2
    rts
L_UNIT142_052AE:
    lea L_UNIT142_05302(pc),a1
    move.l (a1),d0
    move.l a0,d1
    cmp.l d1,d0
    bne.w L_UNIT142_052C2
    move.l 4(a1),d0
    rts
L_UNIT142_052C2:
    move.l #$00000000,d0
    rts
