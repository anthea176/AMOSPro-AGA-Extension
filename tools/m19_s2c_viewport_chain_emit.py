#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P1e source-only correction of P1d check 5.

A graphics View can contain multiple ViewPorts. ChangeSprite/MoveSprite
target the pinned head ViewPort. Validate a bounded read-only tail with
the existing TypeOfMem span guard. Never edit any ViewPort link or
foreign palette. This is structural corroboration, not a lock on
Intuition or proof of other ViewPorts' visibility.
"""
from m19_s2c_diagnostic_emit import once

def allow_viewport_chain(life):
    life=once(life,"""    tst.l (a0)              ; single active ViewPort
    bne.w s2cd_ctx_5
""","""    ; Intuition can link other ViewPorts behind our pinned active head.
    tst.l (a0)
    beq.s s2ce_vp_head_only
    bsr.w s2ce_vp_chain
    tst.l d0
    beq.w s2c_l_no
s2ce_vp_head_only:
""")
    # Head already passed the exact View/VP snapshot and span checks.
    # D2/A0 preserved across this helper; D0/D1 are result/diagnostic.
    # Existing span guard preserves D2/A0-A1/A6. D3-D7/A2-A5 untouched.
    # At most 16 successor ViewPorts; no recursion or foreign writes.
    return once(life,'    include "s2c_v5_frame.s"\n',"""s2ce_vp_chain:
    movem.l d2/a0,-(sp)
    moveq #15,d2
s2ce_vp_next:
    move.l (a0),d0
    beq.s s2ce_vp_ok
    cmp.l 4(sp),d0
    beq.s s2ce_vp_cycle
    cmpa.l d0,a0
    beq.s s2ce_vp_cycle
    movea.l d0,a0
    moveq #40,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.s s2ce_vp_unmapped
    dbra d2,s2ce_vp_next
    tst.l (a0)
    beq.s s2ce_vp_ok
    ; Bound exceeded (including a cycle not involving head/self).
    move.l #-327682,d1
    bra.s s2ce_vp_no
s2ce_vp_unmapped:
    move.l #-327681,d1
    bra.s s2ce_vp_no
s2ce_vp_cycle:
    move.l #-327680,d1
s2ce_vp_no:
    moveq #0,d0
    bra.s s2ce_vp_return
s2ce_vp_ok:
    moveq #1,d0
s2ce_vp_return:
    movem.l (sp)+,d2/a0
    rts

    include "s2c_v5_frame.s"
""")
