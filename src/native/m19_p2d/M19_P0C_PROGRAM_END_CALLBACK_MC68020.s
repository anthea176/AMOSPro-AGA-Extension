; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p0c_program_end_bridge_emit.py::emit_program_end_bridge
; Audited bytes checked against the official M19 P2d library.
; BOBS+$048FA..$049A8 (174 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0C_CALLBACK_OWNER_ALIGNMENT equ 1

    movem.l d0-d7/a0-a6,-(a7)
    bsr.w registry_cpu_guard
    tst.l d0
    beq.w end_bridge_return
    move.l a5,d0
    tst.l d0
    beq.w end_bridge_return
    andi.l #P0C_CALLBACK_OWNER_ALIGNMENT,d0
    bne.w end_bridge_return
    move.l 456(a5),d0
    cmpi.l #$00000168,d0
    bcs.w end_bridge_return
    subi.l #$00000168,d0
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w end_bridge_return
    movea.l d0,a4
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w end_bridge_return
    move.l (a4),d0
    cmpi.l #$48E7FFFE,d0
    bne.w end_bridge_return
    move.l 4(a4),d0
    cmpi.l #$246D01C8,d0
    bne.w end_bridge_return
    move.l 8(a4),d0
    cmpi.l #$60000978,d0
    bne.w end_bridge_return
    lea program_end_bridge_entry(pc),a0
    move.l a0,d1
    move.l 460(a5),d0
    cmp.l d1,d0
    bne.w end_bridge_return
    move.l 464(a5),d0
    cmp.l d1,d0
    bne.w end_bridge_return
    bsr.w screen_preclose_entry
    tst.l d3
    beq.w end_bridge_return
    move.l a4,460(a5)
    move.l a4,464(a5)
    jsr (a4)
end_bridge_return:
    movem.l (a7)+,d0-d7/a0-a6
    rts
