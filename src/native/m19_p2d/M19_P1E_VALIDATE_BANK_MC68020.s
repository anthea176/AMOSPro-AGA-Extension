; AGA_NATIVE_MIN_CPU: MC68020
; P1e checked AGBO bank wrapper from tools/m19_p1e_bank_edit_emit.py.
; BOBS+$08632..+$0865E = 44 MC68020 instruction bytes.
P1E_VALIDATOR_STACK equ 176
P1E_VALIDATOR_BANK equ 0
P1E_VALIDATOR_BANKPTR equ 12
P1E_VALIDATOR_CTX equ 4
P1E_VALIDATOR_GFX equ 8
P1E_VALIDATOR_RESULT equ 84

edit_validate_bank:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -P1E_VALIDATOR_STACK(a7),a7
    movea.l a7,a2
    move.l d3,P1E_VALIDATOR_BANK(a2)
    move.l a0,P1E_VALIDATOR_BANKPTR(a2)
    move.l #0,P1E_VALIDATOR_CTX(a2)
    move.l #0,P1E_VALIDATOR_GFX(a2)
    move.l #0,P1E_VALIDATOR_RESULT(a2)
    bra.w checked_stage_live_bank_valid
