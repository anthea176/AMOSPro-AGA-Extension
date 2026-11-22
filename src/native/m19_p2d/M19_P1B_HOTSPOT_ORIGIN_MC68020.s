; AGA_NATIVE_MIN_CPU: MC68020
; P1b HotSpot source from tools/m19_p1b_hotspot_origin_emit.py.
; BOBS+$07A14..+$07AC2, 174 instruction bytes, no data.
; A0 validated AGBO directory record, A3 checked screen W/H.
; D1/D4 anchored X/Y; D3 visible=1, fully clipped=0; D2=0.
P1B_HOT_X equ 28
P1B_HOT_Y equ 30
P1B_MAX_SIDE equ 4096

p1b_hotspot_origin_entry:
    move.l d0,-(a7)
    move.l d1,d2
    move.w P1B_HOT_X(a0),d0
    ext.l d0
    sub.l d0,d2
    move.l d4,d3
    move.w P1B_HOT_Y(a0),d0
    ext.l d0
    sub.l d0,d3
    cmpi.l #-32768,d2
    blt.w p1b_no_overlap
    cmpi.l #32767,d2
    bgt.w p1b_no_overlap
    cmpi.l #-32768,d3
    blt.w p1b_no_overlap
    cmpi.l #32767,d3
    bgt.w p1b_no_overlap
    cmp.l (a3),d2
    bge.w p1b_no_overlap
    cmp.l 4(a3),d3
    bge.w p1b_no_overlap
    move.l #0,d0
    move.w 2(a0),d0
    tst.l d0
    ble.w p1b_no_overlap
    cmpi.l #P1B_MAX_SIDE,d0
    bgt.w p1b_no_overlap
    add.l d2,d0
    tst.l d0
    ble.w p1b_no_overlap
    move.l #0,d0
    move.w 4(a0),d0
    tst.l d0
    ble.w p1b_no_overlap
    cmpi.l #P1B_MAX_SIDE,d0
    bgt.w p1b_no_overlap
    add.l d3,d0
    tst.l d0
    ble.w p1b_no_overlap
    move.l d2,d1
    move.l d3,d4
    move.l #1,d3
    bra.w p1b_hotspot_return
p1b_no_overlap:
    move.l #0,d3
p1b_hotspot_return:
    move.l (a7)+,d0
    move.l #0,d2
    rts
