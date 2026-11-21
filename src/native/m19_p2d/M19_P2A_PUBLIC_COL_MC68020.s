; AGA_NATIVE_MIN_CPU: MC68020
; P2a public Aga Bob Col(A,B,Mode) source from:
; tools/m19_p2a_public_bob_col_emit.py and P2b geometry patch
; in tools/m19_p2b_bob_flip_emit.py.
; Original BOBS+$09D38..+$09E35, exactly 254 instruction bytes.
; D3 result = 1 hit, 0 no hit, -1 invalid. D2=0; GETP advances A3.
; Seven full-format 68020 PC-relative LEA references source-pinned below.

P2A_PUBLIC_FRAME         equ 256
P2A_PUBLIC_CTX           equ 16
P2A_PUBLIC_SCREEN        equ 64
P2A_PUBLIC_CALLBACKS     equ 80
P2A_PUBLIC_PRIVATE_CTX   equ 112
P2A_PUBLIC_IDENTITY_OFF  equ $E9A4
P2A_PUBLIC_OWNER_STATE   equ $01C8

p2a_public_bob_col:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -P2A_PUBLIC_FRAME(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l (a3)+,4(a2)
    move.l (a3)+,8(a2)
    move.l #$FFFFFFFF,12(a2)
    dc.w $4DFB,$0170
    dc.l p1c_context-(*-2)      ; LEA (bd.L,PC),A6
    jsr (a6)
    move.l a0,d5
    tst.l d5
    beq.w p2a_public_col_done
    andi.l #1,d5
    bne.w p2a_public_col_done
    move.l a0,P2A_PUBLIC_CTX(a2)
    movea.l P2A_PUBLIC_OWNER_STATE(a5),a0
    move.l 12(a0),d5
    move.l d5,P2A_PUBLIC_SCREEN(a2)
    move.l 16(a0),d5
    move.l d5,P2A_PUBLIC_SCREEN+4(a2)

    move.l a2,d5
    addi.l #P2A_PUBLIC_SCREEN,d5
    movea.l d5,a0
    move.l a0,P2A_PUBLIC_PRIVATE_CTX(a2)
    move.l P2A_PUBLIC_CTX(a2),d5
    addi.l #8,d5
    move.l d5,P2A_PUBLIC_PRIVATE_CTX+4(a2)

    dc.w $41FB,$0170
    dc.l p2a_pair_chip_resolve_entry-(*-2)
    move.l a0,P2A_PUBLIC_CALLBACKS(a2)

    ; Identity is resolved relative to live State, across native groups.
    move.l P2A_PUBLIC_OWNER_STATE(a5),d5
    addi.l #P2A_PUBLIC_IDENTITY_OFF,d5
    bcs.w p2a_public_col_done
    movea.l d5,a0
    move.l a0,P2A_PUBLIC_CALLBACKS+4(a2)

    dc.w $41FB,$0170
    dc.l explicit_image_resolve_entry-(*-2)
    move.l a0,P2A_PUBLIC_CALLBACKS+8(a2)
    dc.w $41FB,$0170
    dc.l p2a_pair_hotspot_entry-(*-2)
    move.l a0,P2A_PUBLIC_CALLBACKS+12(a2)
    dc.w $41FB,$0170
    dc.l explicit_bank_lookup_entry-(*-2)
    move.l a0,P2A_PUBLIC_CALLBACKS+16(a2)

    ; P2b explicitly redirects the P2a geometry callback to mirrored geometry.
    dc.w $41FB,$0170
    dc.l p2b_geometry-(*-2)
    move.l a0,P2A_PUBLIC_CALLBACKS+20(a2)
    dc.w $41FB,$0170
    dc.l p2a_pair_entry-(*-2)
    move.l a0,P2A_PUBLIC_CALLBACKS+24(a2)

    move.l 8(a2),d0
    move.l 4(a2),d1
    move.l (a2),d4
    move.l a2,d5
    addi.l #P2A_PUBLIC_PRIVATE_CTX,d5
    movea.l d5,a1
    move.l a2,d5
    addi.l #P2A_PUBLIC_CALLBACKS,d5
    movea.l d5,a4
    bsr.w p2a_collision_query_entry
    move.l d3,12(a2)
p2a_public_col_done:
    move.l 12(a2),d3
    lea P2A_PUBLIC_FRAME(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
