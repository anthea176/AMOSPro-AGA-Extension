; AGA_NATIVE_MIN_CPU: MC68020
; S2c-P1a: private 2/4-plane capture pipeline, source-only contract hardening.
; Compiles the five separately tested MC68020 units into one native image.
; A0 -> preallocated request of 96 bytes, A5 AMOS Main state.
; +00..+35 = exact bridge request (state ptr, RGB32, RGB24, descriptor,
;             8*H planes, 48-byte palette, X,Y,H,transparent, zero)
; +36 LONG bank number (5..65535), +40 WORD image id (1..4096)
; +42 WORD hotspot X, +44 WORD hotspot Y, +46 WORD reserved zero
; +48 LONG old AGSP payload (0 if no bank), +52 LONG old payload bytes
; +56 LONG repack request[40], +60 LONG detached payload staging buffer
; +64 LONG detached staging capacity, +68 LONG commit request[32]
; +72..95 expected live owner/bank/payload/length/generation/flags snapshot
; Returns D3=1 on success, D3=0 on refusal, D2=0 integer.
; Caller must validate allocation spans, ownership, selected bank and
; source bitmap, and must freeze screen & bank lifetime through the call.
; Gate A with mocked Main/graphics only; NO AP20 token or DMA Sprite.
;
AGSP_P1C_PIPELINE_ENTRY:
    bra.w agsp_p1c_pipeline_body

    include "M19_S1P1I_SCREEN_RGB24_MC68020.s"
    include "M19_S2C_AGSP_CAPTURE_MC68020.s"
    include "M19_S2C_AGSP_REPACK_MC68020.s"

AGSP_P1C_F_REQ    equ 0
AGSP_P1C_F_COLORS equ 4
AGSP_P1C_F_SIZE   equ 8
AGSP_P1C_F_FRAME  equ 16

agsp_p1c_pipeline_body:
    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(sp)
    suba.l #AGSP_P1C_F_FRAME,sp
    movea.l sp,a2
    moveq #0,d3
    moveq #0,d2
    move.l a0,d0
    beq.w agsp_p1c_pipeline_end
    btst #0,d0
    bne.w agsp_p1c_pipeline_end
    move.l a0,AGSP_P1C_F_REQ(a2)
    movea.l a0,a6
    tst.w 46(a6)
    bne.w agsp_p1c_pipeline_end
    move.l 36(a6),d0
    cmpi.l #5,d0
    bcs.w agsp_p1c_pipeline_end
    cmpi.l #65535,d0
    bhi.w agsp_p1c_pipeline_end
    moveq #0,d0
    move.w 40(a6),d0
    beq.w agsp_p1c_pipeline_end
    cmpi.w #4096,d0
    bhi.w agsp_p1c_pipeline_end
    move.l 48(a6),d0
    beq.w agsp_p1c_old_zero
    btst #0,d0
    bne.w agsp_p1c_pipeline_end
    tst.l 52(a6)
    beq.w agsp_p1c_pipeline_end
    bra.w agsp_p1c_old_valid
agsp_p1c_old_zero:
    tst.l 52(a6)
    bne.w agsp_p1c_pipeline_end
agsp_p1c_old_valid:
    moveq #56,d4
agsp_p1c_check_buffers:
    move.l 0(a6,d4.w),d0
    beq.w agsp_p1c_pipeline_end
    btst #0,d0
    bne.w agsp_p1c_pipeline_end
    addq.w #4,d4
    cmpi.w #60,d4
    bls.w agsp_p1c_check_buffers
    move.l 68(a6),d0
    beq.w agsp_p1c_pipeline_end
    btst #0,d0
    bne.w agsp_p1c_pipeline_end
    move.l 64(a6),d0
    cmpi.l #176,d0
    bcs.w agsp_p1c_pipeline_end
    cmpi.l #$01000000,d0
    bhi.w agsp_p1c_pipeline_end

    ; Reject contradictory or stale capture snapshot before reading screen.
    move.l 36(a6),d0
    cmp.l 76(a6),d0
    bne.w agsp_p1c_pipeline_end
    move.l 48(a6),d0
    cmp.l 80(a6),d0
    bne.w agsp_p1c_pipeline_end
    move.l 52(a6),d0
    cmp.l 84(a6),d0
    bne.w agsp_p1c_pipeline_end
    move.l (a6),d0
    cmp.l $01C8(a5),d0
    bne.w agsp_p1c_pipeline_end
    lea 72(a6),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w agsp_p1c_pipeline_end

    ; Private L2b ScreenBuffer and RGB32 -> RGB24 snapshot.
    movea.l a6,a0
    bsr.w AGSP_P1B_SCREEN_PREPARE
    tst.l d0
    beq.w agsp_p1c_pipeline_end

    ; Planar pixel extraction; rejects more than 15 opaque RGB24 colors.
    movea.l 12(a6),a0
    bsr.w AGSP_S2C_CAPTURE
    tst.l d0
    beq.w agsp_p1c_pipeline_end
    move.l d1,AGSP_P1C_F_COLORS(a2)

    ; Check the original bank again BEFORE dereferencing it in repack.
    lea 72(a6),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w agsp_p1c_pipeline_end

    ; Repack image into detached full AGSP v1 multi-image payload.
    movea.l 56(a6),a4
    move.l 48(a6),(a4)
    move.l 52(a6),4(a4)
    move.l 16(a6),8(a4)
    move.l 20(a6),12(a4)
    move.l 60(a6),16(a4)
    move.l 64(a6),20(a4)
    move.w 40(a6),24(a4)
    move.w 28(a6),26(a4)
    move.w AGSP_P1C_F_COLORS+2(a2),28(a4)
    move.w 30(a6),30(a4)
    move.w 42(a6),32(a4)
    move.w 44(a6),34(a4)
    clr.l 36(a4)
    movea.l a4,a0
    bsr.w AGSP_S2C_REPACK_ONE
    tst.l d1
    beq.w agsp_p1c_pipeline_end
    tst.l d0
    beq.w agsp_p1c_pipeline_end
    move.l d0,AGSP_P1C_F_SIZE(a2)

    ; Full structural/RGB24/pixel validation BEFORE publishing to AMOS.
    movea.l 60(a6),a0
    move.l AGSP_P1C_F_SIZE(a2),d0
    bsr.w AGSP_P1C_VALIDATE
    tst.l d0
    beq.w agsp_p1c_pipeline_end

    ; Commit after all extraction, repack and verification succeeded.
    movea.l 68(a6),a4
    move.l 60(a6),(a4)
    move.l AGSP_P1C_F_SIZE(a2),4(a4)
    lea 72(a6),a0
    lea 8(a4),a1
    moveq #5,d7
agsp_i_pipeline_snapshot_copy:
    move.l (a0)+,(a1)+
    dbra d7,agsp_i_pipeline_snapshot_copy
    movea.l a4,a0
    bsr.w AGSP_P1C_BANK_COMMIT
    ; D3 returned as success/refusal by commit routine.
agsp_p1c_pipeline_end:
    adda.l #AGSP_P1C_F_FRAME,sp
    movem.l (sp)+,d0-d1/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts

    include "M19_S1P1C_AGSP_VALIDATE_MC68020.s"
    include "M19_S1P1I_BANK_GUARDS_MC68020.s"
    include "M19_S1P1I_AGSP_BANK_COMMIT_MC68020.s"
