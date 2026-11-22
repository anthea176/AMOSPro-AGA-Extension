; AGA_NATIVE_MIN_CPU: MC68020
; P1d per-Bob clipping rectangle, source m19_p1d_limit_bob_emit.py.
; BOBS+$07D7E..+$07DFE = 128 MC68020 code bytes, no data.
; D3=height; A3=width,Y,X,Bob ID; D3=success (1/0), D2=0.
P1D_MAX_BOB equ 64

p1d_limit_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d7
    move.l (a3)+,d6
    move.l (a3)+,d5
    move.l (a3)+,d4
    move.l (a3)+,d3
    cmpi.l #P1D_MAX_BOB,d3
    bhi.w p1d_refuse
    bsr.w p1c_context
    move.l a0,d0
    beq.w p1d_refuse
    adda.l #8,a0
    lsl.l #4,d3
    adda.l d3,a0
    tst.l d6
    ble.w p1d_reset_request
    tst.l d7
    ble.w p1d_refuse
    add.l d4,d6
    bvs.w p1d_refuse
    add.l d5,d7
    bvs.w p1d_refuse
    bra.w p1d_commit
L_BOBS_07DC6:
p1d_reset_request:
    tst.l d4
    bne.w p1d_refuse
    tst.l d5
    bne.w p1d_refuse
    tst.l d6
    bne.w p1d_refuse
    tst.l d7
    bne.w p1d_refuse
L_BOBS_07DDE:
p1d_commit:
    move.l d4,(a0)+
    move.l d5,(a0)+
    move.l d6,(a0)+
    move.l d7,(a0)+
    move.l #1,d3
    bra.w p1d_set_return
L_BOBS_07DF0:
p1d_refuse:
    move.l #0,d3
L_BOBS_07DF6:
p1d_set_return:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
