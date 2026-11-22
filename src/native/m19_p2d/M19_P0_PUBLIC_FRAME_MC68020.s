; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$05B6E..$05CF8 (394 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0_FRAME_ALL_OK_FLAG equ 1

public_aga_bob_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d4
    move.l (a3)+,d6
    move.l (a3)+,d5
    move.l (a3)+,d0
    bsr.w L_BOBS_05A48
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
ENTRY_BOBS_05B86:
public_aga_bob_off_entry:
    move.l d0,-(a7)
    move.l d3,d0
    bsr.w L_BOBS_05A6A
    move.l (a7)+,d0
    moveq #0,d2
    rts
ENTRY_BOBS_05B94:
public_aga_p0e_close_entry:
    movem.l d0-d7/a0-a6,-(a7)
    bsr.w L_BOBS_05A86
    tst.l d3
    beq.w L_BOBS_05BA6
    bsr.w L_BOBS_0479C
L_BOBS_05BA6:
p0e_close_return:
    movem.l (a7)+,d0-d7/a0-a6
    rts
L_BOBS_05BAC:
relay_checked_read_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l #$00000546,d7
    bra.w L_BOBS_05A94
L_BOBS_05BBA:
frame_bank_preflight_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -128(a7),a7
    movea.l a7,a2
    move.l #$00000000,4(a2)
    move.l #$00000000,12(a2)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_05CE8
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_05CE8
    andi.l #$00000001,d0
    bne.w L_BOBS_05CE8
    move.l a5,d0
    addi.l #$000001C8,d0
    bcs.w L_BOBS_05CE8
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_05CE8
    move.l 456(a5),d0
    move.l d0,8(a2)
    tst.l d0
    beq.w L_BOBS_05CE8
    andi.l #$00000001,d0
    bne.w L_BOBS_05CE8
    movea.l 8(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_05CE8
    movea.l 8(a2),a0
    tst.l (a0)
    beq.w L_BOBS_05CE8
    move.l 8(a2),d0
    cmpi.l #$00000168,d0
    bcs.w L_BOBS_05CE8
    subi.l #$00000168,d0
    movea.l d0,a4
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_05CE8
    move.l (a4),d0
    cmpi.l #$48E7FFFE,d0
    bne.w L_BOBS_05CE8
    move.l 4(a4),d0
    cmpi.l #$246D01C8,d0
    bne.w L_BOBS_05CE8
    move.l 8(a4),d0
    cmpi.l #$60000978,d0
    bne.w L_BOBS_05CE8
    move.l #$00000001,(a2)
L_BOBS_05C94:
frame_preflight_next:
    move.l (a2),d0
    cmpi.l #$00000040,d0
    bhi.w L_BOBS_05CE0
    move.l a2,d0
    addi.l #$00000040,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w L_BOBS_05A78
    tst.l d3
    beq.w L_BOBS_05CD6
    move.l a2,d0
    addi.l #$00000040,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w L_BOBS_05BAC
    tst.l d3
    beq.w L_BOBS_05CE8
    move.l 12(a2),d0
    addq.l #1,d0
    move.l d0,12(a2)
L_BOBS_05CD6:
frame_preflight_advance:
    move.l (a2),d0
    addq.l #1,d0
    move.l d0,(a2)
    bra.w L_BOBS_05C94
L_BOBS_05CE0:
frame_preflight_all_checked:
    move.l #P0_FRAME_ALL_OK_FLAG,4(a2)
L_BOBS_05CE8:
frame_preflight_return:
    move.l 4(a2),d3
    lea 128(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
