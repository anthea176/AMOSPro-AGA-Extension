; AMOS Professional AGA - M8 R19 v0.8.3
; REAL MOTOROLA 68000 SOURCE - new X/Y mouse functions.
;
; Based on tools/build_m8_mouse_position_r19.py and independently checked
; against R19 AP20 entries 28/29 (108 instruction bytes each).
; This is the R19 DELTA, not an old M1/M3 source and not a DC.W disassembly.
;
; AP20 integer function convention:
;   A5 = AMOSBase; A3 = parameter stack (not modified; zero args).
;   Return D3 = integer coordinate, D2 = 0 (integer type).
;   -1 if no owned window/screen or outside logical dimensions.
;
; The AP20 offset table points at these routines as entries 28 and 29.
; The literal 'GetP' after Mouse X belongs to the AP20 dispatcher and
; is never executed by the 68000. The main monolithic .s includes all
; earlier entries and AP20 headers.

AGA_StatePtr   equ $01C8
AGA_Screen     equ 0
AGA_Width      equ 12
AGA_Height     equ 16
AGA_Window     equ 36
Win_LeftEdge   equ 4
Win_TopEdge    equ 6
Win_MouseY     equ 12
Win_MouseX     equ 14
Win_Screen     equ 46

; ---------------------------------------------------------------
; _X = Aga Mouse X
; ---------------------------------------------------------------
Aga_Mouse_X:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    movea.l AGA_StatePtr(a5),a2     ; shared extension state
    move.l  a2,d0
    tst.l   d0
    beq.w   .BadX
    movea.l AGA_Screen(a2),a4       ; owned Intuition Screen*
    move.l  a4,d0
    tst.l   d0
    beq.w   .BadX
    movea.l AGA_Window(a2),a1       ; owned Intuition Window*
    move.l  a1,d0
    tst.l   d0
    beq.w   .BadX
    move.l  Win_Screen(a1),d0       ; reject foreign window
    move.l  a4,d1
    cmp.l   d1,d0
    bne.w   .BadX
    move.l  AGA_Width(a2),d0
    tst.l   d0
    beq.w   .BadX
    bmi.w   .BadX
    move.w  Win_MouseX(a1),d3       ; signed window-relative X
    ext.l   d3
    move.w  Win_LeftEdge(a1),d1    ; signed window offset
    ext.l   d1
    add.l   d1,d3                 ; logical screen X
    tst.l   d3
    bmi.w   .BadX
    cmp.l   d0,d3                 ; upper bound exclusive
    bcc.w   .BadX
    bra.w   .DoneX
.BadX:
    move.l  #-1,d3
.DoneX:
    movem.l (sp)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq   #0,d2                ; AMOS integer result
    rts

    dc.b "GetP"                 ; AP20 delimiter for next entry

; ---------------------------------------------------------------
; _Y = Aga Mouse Y
; ---------------------------------------------------------------
Aga_Mouse_Y:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    movea.l AGA_StatePtr(a5),a2
    move.l  a2,d0
    tst.l   d0
    beq.w   .BadY
    movea.l AGA_Screen(a2),a4
    move.l  a4,d0
    tst.l   d0
    beq.w   .BadY
    movea.l AGA_Window(a2),a1
    move.l  a1,d0
    tst.l   d0
    beq.w   .BadY
    move.l  Win_Screen(a1),d0
    move.l  a4,d1
    cmp.l   d1,d0
    bne.w   .BadY
    move.l  AGA_Height(a2),d0
    tst.l   d0
    beq.w   .BadY
    bmi.w   .BadY
    move.w  Win_MouseY(a1),d3
    ext.l   d3
    move.w  Win_TopEdge(a1),d1
    ext.l   d1
    add.l   d1,d3
    tst.l   d3
    bmi.w   .BadY
    cmp.l   d0,d3
    bcc.w   .BadY
    bra.w   .DoneY
.BadY:
    move.l  #-1,d3
.DoneY:
    movem.l (sp)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq   #0,d2
    rts
