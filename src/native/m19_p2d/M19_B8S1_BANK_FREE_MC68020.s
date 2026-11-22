; AGA_NATIVE_MIN_CPU: MC68020
; B8 S1 source-backed Bank Free, handles 64 P0e object slots.
; Authority: tools/m19_b8_s1_bank_free_emit.py::emit_b8_s1_bank_free.
; BOBS+$076A8..+$07962: 698 instruction bytes; no additional data.
; P2b redirects registry Free through the verified variant purge bridge.
B8S1_FRAME equ 96
B8S1_STATE_A5 equ $01C8
B8S1_OBJECT_REL equ $DB42
B8S1_OBJECT_ROOT equ $0314
B8S1_OBJECT_TABLE equ $031C
B8S1_OBJECT_SIGNATURE equ $48E7EFEE
B8S1_MAX_OBJECTS equ 64
B8S1_SLOT_BYTES equ 24

b8s1_bank_free_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -B8S1_FRAME(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l #0,4(a2)
    bsr.w registry_cpu_guard
    tst.l d0
    beq.w b8s1_bank_free_return
    move.l a5,d0
    tst.l d0
    beq.w b8s1_bank_free_return
    andi.l #1,d0
    bne.w b8s1_bank_free_return
    movea.l a5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8s1_bank_free_return
    move.l (a2),d0
    cmpi.l #5,d0
    bcs.w b8s1_bank_free_return
    cmpi.l #65535,d0
    bhi.w b8s1_bank_free_return
    lea frame_guard_state(pc),a0
    tst.l (a0)
    bne.w b8s1_bank_free_return
    lea registry_state(pc),a0
    move.l (a0),d0
    tst.l d0
    beq.w b8s1_bank_free_registry_empty
    move.l a5,d1
    cmp.l d1,d0
    bne.w b8s1_bank_free_return
    tst.l 4(a0)
    beq.w b8s1_bank_free_return
    bra.w b8s1_bank_free_registry_ok
; b8s1_bank_free_registry_empty is a pinned BOBS equ, do not redefine
    tst.l 4(a0)
    bne.w b8s1_bank_free_return
; b8s1_bank_free_registry_ok is a pinned BOBS equ, do not redefine
    move.l B8S1_STATE_A5(a5),d0
    tst.l d0
    beq.w b8s1_bank_free_return
    move.l d0,d1
    andi.l #1,d1
    bne.w b8s1_bank_free_return
    move.l d0,8(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8s1_bank_free_return
    move.l 8(a2),d0
    addi.l #32,d0
    bcs.w b8s1_bank_free_return
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8s1_bank_free_return
    movea.l 8(a2),a0
    tst.l (a0)
    beq.w b8s1_bank_free_return
    move.l 8(a0),d0
    tst.l d0
    beq.w b8s1_bank_free_return
    move.l d0,d1
    andi.l #1,d1
    bne.w b8s1_bank_free_return
    move.l d0,32(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8s1_bank_free_return
    move.l 8(a2),d0
    addi.l #B8S1_OBJECT_REL,d0
    bcs.w b8s1_bank_free_return
    move.l d0,12(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8s1_bank_free_return
    movea.l 12(a2),a0
    move.l (a0),d0
    cmpi.l #B8S1_OBJECT_SIGNATURE,d0
    bne.w b8s1_bank_free_return
    move.l 12(a2),d0
    addi.l #B8S1_OBJECT_ROOT,d0
    bcs.w b8s1_bank_free_return
    move.l d0,16(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8s1_bank_free_return
    move.l 12(a2),d0
    addi.l #B8S1_OBJECT_TABLE,d0
    bcs.w b8s1_bank_free_return
    move.l d0,20(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8s1_bank_free_return
    move.l 20(a2),d0
    addi.l #1535,d0
    bcs.w b8s1_bank_free_return
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b8s1_bank_free_return
    movea.l 16(a2),a0
    move.l (a0),d0
    move.l d0,36(a2)
    tst.l d0
    beq.w b8s1_bank_free_scan_start
    move.l a5,d1
    cmp.l d1,d0
    bne.w b8s1_bank_free_return
b8s1_bank_free_scan_start:
    move.l 20(a2),d0
    move.l d0,24(a2)
    move.l #B8S1_MAX_OBJECTS,28(a2)
; b8s1_bank_free_scan is a pinned BOBS equ, do not redefine
    movea.l 24(a2),a0
    move.l 16(a0),d0
    cmpi.l #1,d0
    bhi.w b8s1_bank_free_return
    tst.l d0
    beq.w b8s1_bank_free_next_check
    move.l 36(a2),d1
    tst.l d1
    beq.w b8s1_bank_free_return
    movea.l 24(a2),a0
    move.l (a0),d0
    cmpi.l #5,d0
    bcs.w b8s1_bank_free_return
    cmpi.l #65535,d0
    bhi.w b8s1_bank_free_return
; b8s1_bank_free_next_check is a pinned BOBS equ, do not redefine
    move.l 24(a2),d0
    addi.l #24,d0
    bcs.w b8s1_bank_free_return
    move.l d0,24(a2)
    move.l 28(a2),d0
    subq.l #1,d0
    move.l d0,28(a2)
    bne.w b8s1_bank_free_scan
    move.l 20(a2),d0
    move.l d0,24(a2)
    move.l #B8S1_MAX_OBJECTS,28(a2)
; b8s1_bank_free_disable is a pinned BOBS equ, do not redefine
    movea.l 24(a2),a0
    tst.l 16(a0)
    beq.w b8s1_bank_free_next_off
    move.l (a0),d0
    move.l (a2),d1
    cmp.l d1,d0
    bne.w b8s1_bank_free_next_off
    movea.l 24(a2),a0
    move.l #0,16(a0)
; b8s1_bank_free_next_off is a pinned BOBS equ, do not redefine
    move.l 24(a2),d0
    addi.l #24,d0
    bcs.w b8s1_bank_free_return
    move.l d0,24(a2)
    move.l 28(a2),d0
    subq.l #1,d0
    move.l d0,28(a2)
    bne.w b8s1_bank_free_disable
    lea bank_active_state(pc),a0
    move.l (a0),d0
    move.l (a2),d1
    cmp.l d1,d0
    bne.w b8s1_bank_free_release
    move.l #0,(a0)
    move.l #0,4(a0)
    move.l #0,8(a0)
; b8s1_bank_free_release is a pinned BOBS equ, do not redefine
    move.l (a2),d3
    movea.l 32(a2),a4
    bsr.w p2b_bank_free
    tst.l d3
    beq.w b8s1_bank_free_return
    move.l #1,4(a2)
; b8s1_bank_free_return is a pinned BOBS equ, do not redefine
    move.l 4(a2),d3
    lea B8S1_FRAME(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
