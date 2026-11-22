; AGA_NATIVE_MIN_CPU: MC68020
; Source: tools/m19_p1e_bank_edit_emit.py::emit_bank_edit
; BOBS+$08306..+$0840A (260 bytes) P1e object and stamp address validation
P1E_OBJECT_SLOT_COUNT equ 64

edit_objects:
    movea.l 40(a2),a0
    adda.l #$0000DE56,a0
    move.l a0,100(a2)
    move.l 100(a2),d0
    tst.l d0
    beq.w L_BOBS_085E8
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_085E8
    move.l 100(a2),d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_085E8
    movea.l 100(a2),a0
    move.l (a0),d0
    beq.w L_BOBS_08350
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_085E8
L_BOBS_08350:
edit_object_addresses:
    movea.l 40(a2),a0
    adda.l #$0000DE5E,a0
    move.l a0,92(a2)
    move.l 92(a2),d0
    tst.l d0
    beq.w L_BOBS_085E8
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_085E8
    move.l 92(a2),d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_085E8
    move.l 92(a2),d0
    addi.l #$000005FF,d0
    bcs.w L_BOBS_085E8
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_085E8
    movea.l 40(a2),a0
    adda.l #$0000EAE2,a0
    move.l a0,96(a2)
    move.l 96(a2),d0
    tst.l d0
    beq.w L_BOBS_085E8
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_085E8
    move.l 96(a2),d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_085E8
    move.l 96(a2),d0
    addi.l #$000003FF,d0
    bcs.w L_BOBS_085E8
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_085E8
    movea.l 92(a2),a4
    movea.l 96(a2),a6
    move.l #P1E_OBJECT_SLOT_COUNT,d7
