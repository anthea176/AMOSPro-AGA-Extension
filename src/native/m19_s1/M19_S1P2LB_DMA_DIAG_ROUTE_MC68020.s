; AGA_NATIVE_MIN_CPU: MC68020
; S1-P2l-b diagnostic-only AP20 adapter, NOT a production API addition.
; All ordinary bank arguments tail-call the exact P2k Bank Free routine.
; Reserved out-of-domain test argument -19000 is READ-ONLY observation
; of the single retained registry; not a bank number, not a free request.
; -190 means sampled idle only. NEVER return 1 for this diagnostic.
; D3=argument/result, D2=integer type, all other AMOS registers preserved.
; No code pointer is published in persistent RAM; UNIT142 unchanged.
p2lb_bank_free:
    cmpi.l #-19000,d3
    beq.s p2lb_observe
    bra.w p2i_bank_free
p2lb_observe:
    movem.l d0-d1,-(sp)
    bsr.w p2l_observe
    cmpi.l #1,d0
    bne.s p2lb_result
    move.l #-190,d0
p2lb_result:
    move.l d0,d3
    movem.l (sp)+,d0-d1
    moveq #0,d2
    rts
