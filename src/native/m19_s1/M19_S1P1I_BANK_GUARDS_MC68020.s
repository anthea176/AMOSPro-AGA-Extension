; AGA_NATIVE_MIN_CPU: MC68020
; S1-P1i shared contract guards. Source: AMOS365 +B.s / +Lib.s and
; P2d P1e edit preflight. TypeOfMem proves RAM endpoints, NOT allocation
; ownership/extent. The live AMOS list and OS-owned screen are trusted.
; Calls synchronous on the AMOS task; no guarantee against arbitrary
; direct Poke or hostile concurrent modification of AMOS structures.
;
; A0 start, D0 length: D0=1 RAM endpoints, 0 reject. Preserve all else.
AGSP_I_SPAN:
    movem.l d1/d4/a0-a1/a6,-(sp)
    move.l a0,d1
    beq.w agsp_i_span_no
    btst #0,d1
    bne.w agsp_i_span_no
    tst.l d0
    beq.w agsp_i_span_no
    add.l d0,d1
    bcs.w agsp_i_span_no
    subq.l #1,d1
    move.l d1,d4
    movea.l a0,a1
    movea.l $0004.w,a6
    jsr -534(a6)              ; Exec.TypeOfMem
    tst.l d0
    beq.w agsp_i_span_no
    movea.l d4,a1
    jsr -534(a6)
    tst.l d0
    beq.w agsp_i_span_no
    moveq #1,d0
    bra.w agsp_i_span_end
agsp_i_span_no:
    moveq #0,d0
agsp_i_span_end:
    movem.l (sp)+,d1/d4/a0-a1/a6
    rts

; A0 expected Cur_Banks cell, D0 boolean. A5 is live AMOS Main.
AGSP_I_OWNER:
    move.l a0,d0
    cmp.l $05EA(a5),d0
    bne.w agsp_i_owner_no
    moveq #4,d0
    bra.w AGSP_I_SPAN
agsp_i_owner_no:
    moveq #0,d0
    rts

; A0=live payload returned by Bnk.GetAdr, D0=bank.
; D0=1 valid, D1=length, D2=generation, D3=flags.
; D0=0 invalid; other result registers zero. Preserve A0/A1-A6,D4-D7.
AGSP_I_LIVE:
    movem.l d4-d7/a0-a4/a6,-(sp)
    move.l d0,d4
    movea.l a0,a4
    move.l a4,d0
    cmpi.l #24,d0
    bls.w agsp_i_live_no
    btst #0,d0
    bne.w agsp_i_live_no
    lea -24(a4),a0
    moveq #24,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_i_live_no
    cmp.l 8(a0),d4
    bne.w agsp_i_live_no
    moveq #0,d5
    move.w 12(a0),d5
    beq.w agsp_i_live_flags_ok
    cmpi.w #1,d5
    beq.w agsp_i_live_flags_ok
    cmpi.w #3,d5
    bne.w agsp_i_live_no
agsp_i_live_flags_ok:
    cmpi.l #$41474153,16(a0)
    bne.w agsp_i_live_no
    cmpi.l #$50525420,20(a0)
    bne.w agsp_i_live_no
    move.l 4(a0),d6
    cmpi.l #48,d6
    bcs.w agsp_i_live_no
    cmpi.l #$01000010,d6
    bhi.w agsp_i_live_no
    subi.l #16,d6
    btst #0,d6
    bne.w agsp_i_live_no
    movea.l a4,a0
    move.l d6,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_i_live_no
    move.l d6,d0
    bsr.w AGSP_P1C_VALIDATE
    tst.l d0
    beq.w agsp_i_live_no
    move.l d6,d1
    move.l 24(a4),d2
    move.l d5,d3
    moveq #1,d0
    bra.w agsp_i_live_end
agsp_i_live_no:
    moveq #0,d0
    moveq #0,d1
    moveq #0,d2
    moveq #0,d3
agsp_i_live_end:
    movem.l (sp)+,d4-d7/a0-a4/a6
    rts

; A0 -> trusted 24-byte snapshot: owner cell, bank, payload ptr, length,
; generation, flags (six LONGs). Missing bank: final four longs zero.
; Check owner BEFORE and AFTER native Bnk.GetAdr; compare full snapshot.
; D0 boolean, preserve all other registers. No mutation/allocation.
AGSP_I_EXPECT:
    movem.l d1-d7/a0-a6,-(sp)
    movea.l a0,a4
    movea.l (a4),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w agsp_i_expect_no
    move.l 4(a4),d0
    dc.w $FE11,$F700,797
    move.l a0,d0
    cmp.l 8(a4),d0
    bne.w agsp_i_expect_no
    tst.l d0
    bne.w agsp_i_expect_live
    tst.l 12(a4)
    bne.w agsp_i_expect_no
    tst.l 16(a4)
    bne.w agsp_i_expect_no
    tst.l 20(a4)
    bne.w agsp_i_expect_no
    bra.w agsp_i_expect_owner
agsp_i_expect_live:
    move.l 4(a4),d0
    bsr.w AGSP_I_LIVE
    tst.l d0
    beq.w agsp_i_expect_no
    cmp.l 12(a4),d1
    bne.w agsp_i_expect_no
    cmp.l 16(a4),d2
    bne.w agsp_i_expect_no
    cmp.l 20(a4),d3
    bne.w agsp_i_expect_no
agsp_i_expect_owner:
    movea.l (a4),a0
    bsr.w AGSP_I_OWNER
    bra.w agsp_i_expect_end
agsp_i_expect_no:
    moveq #0,d0
agsp_i_expect_end:
    movem.l (sp)+,d1-d7/a0-a6
    rts
