; AMOS Professional 365 / AGA extension M1 (v0.0.2) — Genam candidate
; WARNING: this source has not yet been assembled under native Genam.
; Current released HUNK uses tools/build_detect.py (public-domain
; AMOS 365 +Request.s ABI). Only a separate test AMOS may load it.
;
; 68020+ / AGA Alice+Lisa / Kickstart 3.0+. Extension slot 14.
; Uses 68000-safe opcodes to check CPU before performing graphics checks.
ExtNb          equ     14-1

                Include "+AGA_Size.s"
                Include "+AGA_Labels.s"
                Include "+AMOS_Includes.s"
                Include "+Version.s"

Start           dc.l    C_Tk-C_Off
                dc.l    C_Lib-C_Tk
                dc.l    C_Title-C_Lib
                dc.l    C_End-C_Title
                dc.w    0
                dc.b    "AP20"

                MCInit
C_Off
                REPT    Lib_Size
                MC
                ENDR

; TOKEN_START
C_Tk            dc.w    1,0
                dc.b    $80,-1
                dc.w    L_AgaProbe,L_Nul
                dc.b    "aga prob","e"+$80,"I",-1
                dc.w    L_Nul,L_FnAgaDetect
                dc.b    "aga detec","t"+$80,"0",-1
; TOKEN_END
                dc.w    0
                dc.l    0

                Lib_Ini 0
C_Lib
                Lib_Def Cold
                cmp.l   #"APex",d1
                bne.s   BadVersion
                lea     Warm(pc),a0
                move.l  a0,ExtAdr+ExtNb*16+4(a5)
                moveq   #ExtNb,d0
                move.w  #VerNumber,d1
                rts
BadVersion      moveq   #-1,d0
                sub.l   a0,a0
                rts
Warm            rts

                Lib_Empty

; Unused entry retained to match the M0 Requester-derived ABI layout.
                Lib_Par AgaReserved
                rts

                Lib_Par AgaProbe
                rts

; Integer function: returns 1 when CPU>=020 and gfx.library V39
; reports both Alice+Lisa. Does not modify AMOS screens.
; AMOS numeric result: d3=data and Ret_Int sets d2=0.
                Lib_Par FnAgaDetect
                move.l  d0,-(sp)
                move.l  d1,-(sp)
                move.l  a0,-(sp)
                move.l  a1,-(sp)
                move.l  a6,-(sp)
                moveq   #0,d3
                move.l  $4.w,a6             ; ExecBase
                btst    #1,$129(a6)         ; AttnFlags low byte ($128 UWORD, big-endian)
                beq.s   .Done
                lea     AgaGfxName(pc),a1
                moveq   #39,d0              ; V39: Kickstart 3.0
                jsr     -552(a6)            ; Exec OpenLibrary
                tst.l   d0
                beq.s   .Done
                move.l  d0,a1               ; GfxBase to close
                move.b  $EC(a1),d1          ; GfxBase.ChipRevBits0
                andi.b  #$0C,d1            ; AGA Alice+Lisa
                cmpi.b  #$0C,d1
                bne.s   .Close
                moveq   #1,d3
.Close          jsr     -414(a6)            ; Exec CloseLibrary(a1)
.Done           move.l  (sp)+,a6
                move.l  (sp)+,a1
                move.l  (sp)+,a0
                move.l  (sp)+,d1
                move.l  (sp)+,d0
                Ret_Int
AgaGfxName      dc.b    "graphics.library",0
                even

                Lib_Empty
                Lib_Empty
                Lib_End
C_Title         dc.b    "AMOSPro AGA detect V 0.0.2",0
                dc.b    "$VER: AMOSPro_AGA 0.0.2",0
                even
C_End           dc.w    0
                even
