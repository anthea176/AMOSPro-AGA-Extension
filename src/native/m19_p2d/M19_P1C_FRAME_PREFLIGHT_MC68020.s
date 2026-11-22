; AGA_NATIVE_MIN_CPU: MC68020
; P1c priority frame preflight from m19_p1c_bob_priority_emit.py.
; BOBS+$07BBA..+$07C18, 94 MC68020 code bytes; no data.
; 416-byte local frame = 160-byte frame plus 64 priority keys.
P1C_FRAME_BYTES equ 416
P1C_OWNER_A5 equ $01C8

explicit_frame_draw_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -P1C_FRAME_BYTES(a7),a7
    movea.l a7,a2
    move.l #0,4(a2)
    bsr.w image_frame_preflight_entry
    tst.l d3
    beq.w explicit_frame_return
    move.l P1C_OWNER_A5(a5),d0
    move.l d0,24(a2)
    tst.l d0
    beq.w explicit_frame_return
    movea.l 24(a2),a0
    move.l 8(a0),d0
    move.l d0,28(a2)
    tst.l d0
    beq.w explicit_frame_return
    andi.l #1,d0
    bne.w explicit_frame_return
    move.l #1,44(a2)
    move.l #0,36(a2)
    bsr.w p1c_read_mode
    move.l d0,40(a2)
