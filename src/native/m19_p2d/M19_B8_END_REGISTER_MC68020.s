; AGA_NATIVE_MIN_CPU: MC68020
; M19 B8 End/Registrar, source tools/m19_b8_b7_hook_emit.py.
; BOBS+$071EE..+$07364 = 374 bytes (362 code, 12 source data).
; P2b replaces the original End register epilogue with its cleanup bridge.
B8_END1_A5 equ $01CC
B8_END2_A5 equ $01D0
B8_REGISTER_FRAME equ 32
B8_REGISTER_POST equ 4

b8_b7_end_trampoline_entry:
    movem.l d0-d7/a0-a6,-(a7)
    lea b8_b7_end_trampoline_entry(pc),a4
    move.l B8_END1_A5(a5),d0
    move.l B8_END2_A5(a5),d1
    cmp.l d1,d0
    bne.w b8_b7_end_return
    move.l a4,d1
    cmp.l d1,d0
    bne.w b8_b7_end_return
    lea b7_end_entry(pc),a0
    move.l a0,B8_END1_A5(a5)
    move.l a0,B8_END2_A5(a5)
    bsr.w b7_end_entry
    lea b8_b7_hook_root(pc),a0
    move.l (a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w b8_b7_end_return
    tst.l d0
    beq.w b8_b7_end_return
    movea.l 4(a0),a4
    move.l a4,d0
    tst.l d0
    beq.w b8_b7_end_return
    jsr (a4)
    tst.l d3
    beq.w b8_b7_end_pending
    bsr.w b8_b7_clear_root
    bra.w b8_b7_end_return

; b8_b7_end_pending = UNIT_BOBS+$0724C, source-owned alias in BOBS.
    lea b7_end_entry(pc),a4
    move.l B8_END1_A5(a5),d0
    move.l B8_END2_A5(a5),d1
    cmp.l d1,d0
    bne.w b8_b7_end_return
    move.l a4,d1
    cmp.l d1,d0
    bne.w b8_b7_end_return
    lea b8_b7_end_trampoline_entry(pc),a0
    move.l a0,B8_END1_A5(a5)
    move.l a0,B8_END2_A5(a5)

b8_b7_end_return:
    bra.w p2b_close_return
    rts

    dc.b $42,$38,$52,$47  ; B8RG magic DATA, not executable

; b8_b7_register_entry = UNIT_BOBS+$0727C, source-owned alias.
    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)
    lea -B8_REGISTER_FRAME(a7),a7
    movea.l a7,a2
    move.l a0,B8_REGISTER_POST(a2)
    move.l #0,(a2)
    bsr.w registry_cpu_guard
    tst.l d0
    beq.w b8_b7_register_return
    move.l a5,d0
    tst.l d0
    beq.w b8_b7_register_return
    andi.l #1,d0
    bne.w b8_b7_register_return
    move.l B8_REGISTER_POST(a2),d0
    tst.l d0
    beq.w b8_b7_register_return
    andi.l #1,d0
    bne.w b8_b7_register_return
    movea.l B8_REGISTER_POST(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8_b7_register_return
    move.l B8_END1_A5(a5),d0
    move.l B8_END2_A5(a5),d1
    cmp.l d1,d0
    bne.w b8_b7_register_return
    lea b7_end_entry(pc),a4
    move.l a4,d1
    cmp.l d1,d0
    beq.w b8_b7_register_check_root
    lea b8_b7_end_trampoline_entry(pc),a4
    move.l a4,d1
    cmp.l d1,d0
    bne.w b8_b7_register_return

; b8_b7_register_check_root = UNIT_BOBS+$072F8.
    lea b8_b7_hook_root(pc),a0
    move.l (a0),d0
    tst.l d0
    beq.w b8_b7_register_commit
    move.l a5,d1
    cmp.l d1,d0
    bne.w b8_b7_register_return
    move.l 4(a0),d0
    move.l B8_REGISTER_POST(a2),d1
    cmp.l d1,d0
    bne.w b8_b7_register_return
    bra.w b8_b7_register_arm
; b8_b7_register_commit = UNIT_BOBS+$0731E.
    move.l a5,(a0)
    move.l B8_REGISTER_POST(a2),d0
    move.l d0,4(a0)
; b8_b7_register_arm = UNIT_BOBS+$07328.
    lea b8_b7_end_trampoline_entry(pc),a0
    move.l a0,B8_END1_A5(a5)
    move.l a0,B8_END2_A5(a5)
    move.l #1,(a2)
; b8_b7_register_return = UNIT_BOBS+$0733A.
    move.l (a2),d3
    lea B8_REGISTER_FRAME(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts

L_BOBS_07348:
b8_b7_clear_root:
    lea b8_b7_hook_root(pc),a0
    move.l #0,(a0)
    move.l #0,4(a0)
    rts

L_BOBS_0735C:
b8_b7_hook_root:
    dcb.b 8,0
