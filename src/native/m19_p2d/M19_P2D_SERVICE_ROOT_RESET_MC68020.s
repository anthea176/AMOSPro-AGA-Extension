; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$0E538..$0E59E (102 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P2D_SERVICE_RESET_INITIAL_RESULT equ 0

    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a4
    move.l #P2D_SERVICE_RESET_INITIAL_RESULT,(a4)
    lea p2d_service_root(pc),a0
    tst.l (a0)
    bne.w L_BOBS_0E59E
    lea L_BOBS_0E5B0(pc),a2
    move.l (a2),d0
    tst.l d0
    beq.w L_BOBS_0E566
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_0E59E
L_BOBS_0E566:
    move.l #$00000000,(a2)
    move.l #$00000000,4(a2)
    move.l #$00000000,8(a2)
    move.l #$00000000,12(a2)
    move.l #$00000000,16(a2)
    move.l #$00000000,20(a2)
    move.l #$00000001,(a4)
    bra.w L_BOBS_0E59E
