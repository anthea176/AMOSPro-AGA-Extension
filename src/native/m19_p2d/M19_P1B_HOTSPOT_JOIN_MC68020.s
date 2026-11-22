; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$07962..$079F2 (144 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P1B_JOIN_START_ZERO equ 0

p1b_image_hotspot_join:
p1b_native_base_len:
    move.l 64(a4),d3
    move.l a4,d0
    addi.l #$00000080,d0
    movea.l d0,a1
    bsr.w L_BOBS_0627E
    tst.l d3
    beq.w L_BOBS_0500C
    move.l 128(a4),d0
    tst.l d0
    beq.w L_BOBS_0500C
    movea.l d0,a0
    move.l #P1B_JOIN_START_ZERO,d5
    move.w 8(a0),d5
    cmpi.l #$00000001,d5
    bcs.w L_BOBS_0500C
    cmpi.l #$00001000,d5
    bhi.w L_BOBS_0500C
    move.l a0,d0
    addi.l #$00000020,d0
    bcs.w L_BOBS_0500C
    movea.l d0,a0
L_BOBS_079B2:
p1b_find_image:
    move.l #$00000000,d0
    move.w (a0),d0
    move.l 68(a4),d1
    cmp.l d1,d0
    beq.w L_BOBS_079DC
    move.l a0,d0
    addi.l #$00000028,d0
    bcs.w L_BOBS_0500C
    movea.l d0,a0
    subq.l #1,d5
    bne.w L_BOBS_079B2
    bra.w L_BOBS_0500C
L_BOBS_079DC:
p1b_image_found:
    move.l a4,d0
    addi.l #$0000006C,d0
    movea.l d0,a3
    move.l 72(a4),d1
    move.l 76(a4),d4
    bra.w L_BOBS_0A0AA
