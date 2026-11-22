; AGA_NATIVE_MIN_CPU: MC68020
; P1c owner context / priority mode, tools/m19_p1c_bob_priority_emit.py.
; BOBS+$07AE8..+$07B84 = 156 instruction bytes (no data).
; Verify Exec TypeOfMem -534, AGA owner and bounded State pointers.
P1C_STATE_A5      equ $01C8
P1C_CONTEXT_DELTA equ $EF08
P1C_CONTEXT_LAST  equ P1C_CONTEXT_DELTA+7
P1C_MODE_OFF      equ 4

p1c_context:
    bsr.w registry_cpu_guard
    tst.l d0
    beq.w p1c_no_context
    move.l a5,d0
    tst.l d0
    beq.w p1c_no_context
    andi.l #1,d0
    bne.w p1c_no_context
    movea.l a5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w p1c_no_context
    move.l P1C_STATE_A5(a5),d0
    tst.l d0
    beq.w p1c_no_context
    move.l d0,d1
    andi.l #1,d1
    bne.w p1c_no_context
    movea.l d0,a1
    jsr -534(a6)
    tst.l d0
    beq.w p1c_no_context
    movea.l P1C_STATE_A5(a5),a0
    tst.l (a0)
    beq.w p1c_no_context
    move.l a0,d0
    addi.l #P1C_CONTEXT_LAST,d0
    bcs.w p1c_no_context
    movea.l d0,a1
    jsr -534(a6)
    tst.l d0
    beq.w p1c_no_context
    movea.l P1C_STATE_A5(a5),a0
    adda.l #P1C_CONTEXT_DELTA,a0
    move.l a5,d0
    cmp.l (a0),d0
    bne.w p1c_no_context
    rts
L_BOBS_07B6C:
p1c_no_context:
    movea.l #0,a0
    rts
L_BOBS_07B74:
p1c_read_mode:
    bsr.w p1c_context
    move.l a0,d0
    beq.w p1c_read_return
    move.l P1C_MODE_OFF(a0),d0
L_BOBS_07B82:
p1c_read_return:
    rts
