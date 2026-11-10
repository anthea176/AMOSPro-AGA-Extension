; M3a AGA demo routine (Genam source candidate, NOT YET NATIVE ASSEMBLED).
; Embedded routine for AMOSPro_AGA extension, slot 14 / 68020+ / KS3.0+.
; In the parent extension: dc.w L_Nul,L_FnAgaDemo ; "aga demo", "0"
; and Lib_Par FnAgaDemo immediately before these instructions.
;
; This procedure opens a temporary Intuition PAL screen, fills all 256
; palette indices with a gradient, waits 151 VBLs, closes resources.
; Registers D2/D3 carry AMOS numeric result (D3=0 or 1, D2=0).
; The WinUAE-distributed prototype HUNK is regenerated with
; tools/build_m3_compact.py; this listing is not its assembled source.

Exec_OpenLibrary    equ -552
Exec_CloseLibrary   equ -414
Int_OpenScreenTags  equ -612
Int_CloseScreen     equ -66
Gfx_SetRGB32        equ -852
Gfx_SetAPen         equ -342
Gfx_RectFill        equ -306
Gfx_WaitTOF         equ -270
SA_Width            equ $80000023
SA_Height           equ $80000024
SA_Depth            equ $80000025
SA_DisplayID        equ $80000032
PAL_Lores           equ $00021000
Screen_VP           equ $2C
Screen_RP           equ $54
Gfx_ChipRevBits0    equ $EC

AGA_Demo_Begin:
    movem.l d0-d1/d4-d7/a0-a6,-(sp)
    moveq   #0,d3
    move.l  $4.w,a6
    btst    #1,$129(a6)
    beq.w   AGA_Demo_Exit

    lea     AGA_Demo_IntName(pc),a1
    moveq   #39,d0
    jsr     Exec_OpenLibrary(a6)
    tst.l   d0
    beq.w   AGA_Demo_Exit
    movea.l d0,a4

    move.l  $4.w,a6
    lea     AGA_Demo_GfxName(pc),a1
    moveq   #39,d0
    jsr     Exec_OpenLibrary(a6)
    tst.l   d0
    beq.w   AGA_Demo_CloseInt
    movea.l d0,a5

    move.b  Gfx_ChipRevBits0(a5),d0
    andi.b  #$0C,d0
    cmpi.b  #$0C,d0
    bne.w   AGA_Demo_CloseGfx

; Local stack tags: SA_Width=320, Height=256, Depth=8, PAL Lores.
    lea     -40(sp),sp
    movea.l sp,a1
    move.l  #SA_Width,(a1)+
    move.l  #320,(a1)+
    move.l  #SA_Height,(a1)+
    move.l  #256,(a1)+
    move.l  #SA_Depth,(a1)+
    move.l  #8,(a1)+
    move.l  #SA_DisplayID,(a1)+
    move.l  #PAL_Lores,(a1)+
    moveq   #0,d0
    move.l  d0,(a1)+
    move.l  d0,(a1)+
    suba.l  a0,a0
    movea.l sp,a1
    movea.l a4,a6
    jsr     Int_OpenScreenTags(a6)
    lea     40(sp),sp
    tst.l   d0
    beq.w   AGA_Demo_CloseGfx
    movea.l d0,a3

    moveq   #0,d6
AGA_Demo_Gradient:
    move.l  d6,d0               ; Index 0..255
    move.l  d6,d1
    lsl.l   #8,d1
    swap    d1                  ; Red 0..255 in top byte
    move.l  #255,d2
    sub.l   d6,d2
    lsl.l   #8,d2
    swap    d2                  ; Green 255..0
    move.l  #$30000000,d3       ; Blue fixed
    lea     Screen_VP(a3),a0
    movea.l a5,a6
    jsr     Gfx_SetRGB32(a6)

    move.l  d6,d0               ; Set pen to index
    lea     Screen_RP(a3),a1
    jsr     Gfx_SetAPen(a6)
    moveq   #0,d0               ; x1 = 0
    move.l  d6,d1               ; y1 = current index
    move.l  #319,d2             ; x2 = 319
    move.l  d6,d3               ; y2 = same line
    lea     Screen_RP(a3),a1
    jsr     Gfx_RectFill(a6)
    addq.l  #1,d6
    cmpi.l  #256,d6
    bne.w   AGA_Demo_Gradient

    move.w  #150,d7
AGA_Demo_VBL:
    movea.l a5,a6
    jsr     Gfx_WaitTOF(a6)
    dbra    d7,AGA_Demo_VBL

    movea.l a3,a0
    movea.l a4,a6
    jsr     Int_CloseScreen(a6)
    moveq   #1,d3
    bra.w   AGA_Demo_CloseGfx

AGA_Demo_CloseGfx:
    movea.l a5,a1
    move.l  $4.w,a6
    jsr     Exec_CloseLibrary(a6)
AGA_Demo_CloseInt:
    movea.l a4,a1
    move.l  $4.w,a6
    jsr     Exec_CloseLibrary(a6)
AGA_Demo_Exit:
    movem.l (sp)+,d0-d1/d4-d7/a0-a6
    moveq   #0,d2
    rts

AGA_Demo_IntName:
    dc.b    "intuition.library",0
    even
AGA_Demo_GfxName:
    dc.b    "graphics.library",0
    even
