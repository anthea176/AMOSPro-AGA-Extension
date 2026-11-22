; AGA_NATIVE_MIN_CPU: MC68020
; P1d screen-local X/Y rectangle intersect from the trusted source:
; tools/m19_p1d_limit_bob_emit.py::emit_limit_bobs.
; BOBS+$07E6A..+$07F00 = 150 MC68020 instruction bytes, no data.
P1D_XSOURCE equ 252
P1D_YSOURCE equ 256
P1D_XDRAW equ 260
P1D_YDRAW equ 264
P1D_WIDTH equ 268
P1D_HEIGHT equ 272

p1d_intersect:
    move.l (a0),d0
    cmp.l 8(a0),d0
    beq.w p1d_visible
    move.l P1D_XDRAW(a4),d0
    move.l d0,d1
    add.l P1D_WIDTH(a4),d1
    cmp.l (a0),d0
    bge.w p1d_start_x
    move.l (a0),d0
L_BOBS_07E86:
p1d_start_x:
    cmp.l 8(a0),d1
    ble.w p1d_end_x
    move.l 8(a0),d1
L_BOBS_07E92:
p1d_end_x:
    cmp.l d0,d1
    ble.w p1d_invisible
    sub.l d0,d1
    move.l d1,P1D_WIDTH(a4)
    move.l d0,d1
    sub.l P1D_XDRAW(a4),d1
    add.l P1D_XSOURCE(a4),d1
    move.l d1,P1D_XSOURCE(a4)
    move.l d0,P1D_XDRAW(a4)
    move.l P1D_YDRAW(a4),d0
    move.l d0,d1
    add.l P1D_HEIGHT(a4),d1
    cmp.l 4(a0),d0
    bge.w p1d_start_y
    move.l 4(a0),d0
L_BOBS_07EC6:
p1d_start_y:
    cmp.l 12(a0),d1
    ble.w p1d_end_y
    move.l 12(a0),d1
L_BOBS_07ED2:
p1d_end_y:
    cmp.l d0,d1
    ble.w p1d_invisible
    sub.l d0,d1
    move.l d1,P1D_HEIGHT(a4)
    move.l d0,d1
    sub.l P1D_YDRAW(a4),d1
    add.l P1D_YSOURCE(a4),d1
    move.l d1,P1D_YSOURCE(a4)
    move.l d0,P1D_YDRAW(a4)
L_BOBS_07EF0:
p1d_visible:
    move.l #1,d0
    rts
L_BOBS_07EF8:
p1d_invisible:
    move.l #0,d0
    rts
