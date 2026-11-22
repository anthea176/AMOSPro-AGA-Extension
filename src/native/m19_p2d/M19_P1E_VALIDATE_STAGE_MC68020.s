; AGA_NATIVE_MIN_CPU: MC68020
; P1e checked/repacked stage handoff, from m19_p1e_bank_edit_emit.py.
; BOBS+$0865E..+$0866C = 14 MC68020 instruction bytes.
edit_validate_or_stage:
    move.l a1,d3
    bne.w checked_chip_stage
    move.l #1,d3
    rts
