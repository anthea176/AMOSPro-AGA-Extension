; AGA_NATIVE_MIN_CPU: MC68020
; M19 P2c - handwritten AGA Bob Planes / plane-mask application / reset.
; AUTHORITY: tools/m19_p2c_bob_planes_emit.py, included in M19 P2d.
; BOBS offsets $0B4C4..$0B58B, exactly 200 instruction bytes.
; The former 16-byte p2c_reset_slot DC.B block is now three opcodes.
; This is an INCLUDE file for M19_P2D_BOBS_MC68020.s.

P2C_FRAME_BYTES         equ 40
P2C_FRAME_MASK          equ 0
P2C_FRAME_BOB           equ 4
P2C_FRAME_PARAMPTR      equ 8
P2C_BOB_CHECKED         equ 16
P2C_OWNER_SCREEN        equ 0
P2C_SLOT_MASK_OFFSET    equ 40
P2C_PRIVATE_RP          equ 64
P2C_RASTPORT_MASK       equ 24
P2C_MAX_BOBS            equ 64

p2c_public_planes:
    movem.l d0-d1/d4-d7/a0-a6,-(a7)
    lea -P2C_FRAME_BYTES(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l (a3)+,P2C_FRAME_BOB(a2)
    move.l a3,P2C_FRAME_PARAMPTR(a2)
    cmpi.l #255,d3
    bhi.w p2c_set_fail
    bsr.w p1c_context
    move.l a0,d0
    beq.w p2c_set_fail
    lea p2b_owner(pc),a0
    move.l (a0),d0
    beq.w p2c_set_check
    move.l a5,d1
    cmp.l d1,d0
    bne.w p2c_set_fail

L_BOBS_0B4FE:
p2c_set_check:
    lea P2C_BOB_CHECKED(a2),a1
    move.l P2C_FRAME_BOB(a2),d0
    bsr.w relay_checked_read_entry
    tst.l d3
    beq.w p2c_set_fail
    lea p2b_owner(pc),a0
    move.l a5,(a0)
    move.l P2C_FRAME_BOB(a2),d0
    bsr.w p2b_slot
    move.l (a2),d3
    eori.b #$FF,d3
    move.l d3,P2C_SLOT_MASK_OFFSET(a0)
    moveq #1,d3
    bra.w p2c_set_return

L_BOBS_0B52E:
p2c_set_fail:
    moveq #0,d3

L_BOBS_0B530:
p2c_set_return:
    move.l P2C_FRAME_PARAMPTR(a2),d2
    lea P2C_FRAME_BYTES(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a6
    movea.l d2,a3
    moveq #0,d2
    rts

L_BOBS_0B542:
p2c_apply_planes:
    lea P2C_PRIVATE_RP(a4),a1
    lea p2b_owner(pc),a0
    move.l a5,d0
    cmp.l (a0),d0
    bne.w p2c_apply_done
    lea p1d_drawing_id(pc),a0
    move.l (a0),d0
    beq.w p2c_apply_done
    cmpi.l #P2C_MAX_BOBS,d0
    bhi.w p2c_apply_done
    bsr.w p2b_slot
    move.l P2C_SLOT_MASK_OFFSET(a0),d3
    beq.w p2c_apply_done
    eori.b #$FF,d3
    move.b d3,P2C_RASTPORT_MASK(a1)

L_BOBS_0B57A:
p2c_apply_done:
    rts

p2c_reset_slot:
    move.l #0,(a3)
    move.l #0,P2C_SLOT_MASK_OFFSET(a3)
    rts
