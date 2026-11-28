#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-only S2e overlay of exact, Runtime-tested S2d sources.
No changes to original files. Apply only on independent builder copies.
AGSP format and public tokens remain unchanged.
"""
PATCHES={
    "M19_S2D_PUBLIC_MC68020.s": [
        [
            "; One width per lifetime with active records, three pairs, zero hotspot.",
            "; S2e: one width per lifetime, three pairs, per-image signed hotspot."
        ],
        [
            "I_FRAME equ 448",
            "W_HOT equ 448\nI_FRAME equ 452"
        ],
        [
            "    move.l W_COLORS(a2),W_R_COLORS(a4)\n    lea W_PAL(a2),a0",
            "    move.l W_COLORS(a2),W_R_COLORS(a4)\n    move.l W_HOT(a2),W_R_HOT(a4)\n    lea W_PAL(a2),a0"
        ],
        [
            "    move.l #-128,I_PHASE(a2)\n    bsr.w s2d_pub_geometry\n    tst.l d0\n    beq.w p2i_end\n    move.l #-153,I_PHASE(a2)",
            "    ; Same-frame Move keeps its captured hotspot even after bank Erase.\n    ; Changing frame validates geometry with the NEW image's hotspot below.\n    move.l I_IMAGE(a2),d0\n    cmp.l W_R_IMAGE(a4),d0\n    bne.s s2e_pub_active_palette\n    move.l W_R_HOT(a4),W_HOT(a2)\n    move.l #-128,I_PHASE(a2)\n    bsr.w s2d_pub_geometry\n    tst.l d0\n    beq.w p2i_end\ns2e_pub_active_palette:\n    move.l #-153,I_PHASE(a2)"
        ],
        [
            "    dbra d0,s2d_pub_same_palette\n    bsr.w s2d_pub_expect",
            "    dbra d0,s2d_pub_same_palette\n    ; Refuse invalid anchor before dropping a staged frame or allocating.\n    move.l #-128,I_PHASE(a2)\n    bsr.w s2d_pub_geometry\n    tst.l d0\n    beq.w p2i_end\n    move.l #-201,I_PHASE(a2)\n    bsr.w s2d_pub_expect"
        ],
        [
            "    bsr.w AGSP_S2D_EXT_EXCHANGE\n    tst.l d0",
            "    move.l I_X(a2),d0\n    move.l I_Y(a2),d1\n    bsr.w AGSP_S2D_EXT_EXCHANGE\n    tst.l d0"
        ],
        [
            "    move.l d0,W_R_STAGE(a4)\n    bsr.w s2d_pub_expect",
            "    move.l d0,W_R_STAGE(a4)\n    move.l W_HOT(a2),W_R_HOT(a4)\n    bsr.w s2d_pub_expect"
        ],
        [
            "s2d_pub_found:\n    tst.l 28(a4)\n    bne.w p2i_no",
            "s2d_pub_found:\n    move.l 28(a4),W_HOT(a2)"
        ],
        [
            "s2d_pub_geometry:\n    move.l #320,d0\n    sub.l W_WIDTH(a2),d0\n    cmp.l I_X(a2),d0\n    bcs.w p2i_no\n    move.l #256,d0\n    sub.l W_HEIGHT(a2),d0\n    cmp.l I_Y(a2),d0\n    bcs.w p2i_no\n    moveq #1,d0\n    rts",
            "s2d_pub_geometry:\n    move.l I_X(a2),d0\n    move.l I_Y(a2),d1\n    move.l W_HOT(a2),d2\n    move.l W_WIDTH(a2),d3\n    move.l W_HEIGHT(a2),d4\n    bsr.w AGSP_S2E_ANCHOR_TO_ORIGIN\n    tst.l d0\n    beq.w p2i_no\n    move.l d1,I_X(a2)\n    move.l d2,I_Y(a2)\n    rts"
        ],
        [
            "p2i_gfx_name:\n    dc.b \"graphics.library\",0\n    even",
            "p2i_gfx_name:\n    dc.b \"graphics.library\",0\n    even\n    include \"M19_S2E_HOTSPOT_MC68020.s\""
        ]
    ],
    "M19_S2D_REGISTRY_MC68020.s": [
        [
            "; S2d-P3: one named v6 registry, three inline ExtSprite receipts.",
            "; S2e: named v7 registry, three inline ExtSprite receipts."
        ],
        [
            "W_REC_BYTES equ 168",
            "W_REC_BYTES equ 172"
        ],
        [
            "W_R_PAL equ 120",
            "W_R_PAL equ 120\nW_R_HOT equ 168 ; two signed WORDs from AGSP v1"
        ],
        [
            "    addi.l #556,d0",
            "    addi.l #568,d0"
        ],
        [
            "    moveq #41,d1\ns2d_reg_zero:",
            "    moveq #42,d1\ns2d_reg_zero:"
        ],
        [
            "    moveq #41,d0\ns2d_drain_clear:",
            "    moveq #42,d0\ns2d_drain_clear:"
        ]
    ],
    "M19_S2D_PERSIST_ROOT_MC68020.s": [
        [
            "; S2d-P3 v6 private named transaction, derived from exact v5.",
            "; S2e v7 private named transaction; v6 must be refused."
        ],
        [
            "; 612-byte allocation, root at +56, count +0, owner +4, State +8,",
            "; 624-byte allocation, root at +56, count +0, owner +4, State +8,"
        ],
        [
            "; Three 168-byte inline records at root+52/+220/+388 (pairs 2/4/6).",
            "; Three 172-byte inline records at root+52/+224/+396 (pairs 2/4/6)."
        ],
        [
            "    move.l #612,d0",
            "    move.l #624,d0"
        ],
        [
            "    move.l #$00060264,52(a3)",
            "    move.l #$00070270,52(a3)"
        ],
        [
            "    moveq #125,d0\ns2b_empty_slots:",
            "    move.w #128,d0 ; DBRA consumes only the low WORD (129 longs)\ns2b_empty_slots:"
        ],
        [
            "    addi.l #611,d0",
            "    addi.l #623,d0"
        ],
        [
            "    cmpi.l #$00060264,52(a4)",
            "    cmpi.l #$00070270,52(a4)"
        ]
    ],
    "M19_S2D_EXT_FRAME_MC68020.s": [
        [
            "; Candidate must match width/kind/height/palette; no hot spot in this tranche.",
            "; Candidate must match width/kind/height/palette. Caller resolves hotspot."
        ],
        [
            "; A0 receipt, A6 graphics.library, D0/D1 x/y for move, ignored for exchange.",
            "; A0 receipt, A6 graphics.library, D0/D1 target top-left for move AND exchange."
        ],
        [
            "AGSP_S2D_EXT_EXCHANGE:\n    movem.l d2-d7/a0-a6,-(sp)\n    movea.l a0,a3",
            "AGSP_S2D_EXT_EXCHANGE:\n    movem.l d2-d7/a0-a6,-(sp)\n    move.l d1,-(sp)\n    move.l d0,-(sp)\n    movea.l a0,a3"
        ],
        [
            "    beq.w s2d_x_bad\n    cmpi.l #1,80(a3)",
            "    beq.w s2d_x_bad\n    move.l (sp),d2\n    move.l 4(sp),d3\n    bsr.w s2d_x_geometry\n    tst.l d0\n    beq.w s2d_x_bad\n    cmpi.l #1,80(a3)"
        ],
        [
            "s2d_x_ready:\n    bsr.w s2d_x_hidden\n    tst.l d0\n    beq.w s2d_x_uncertain\n    bsr.w s2d_x_reveal",
            "s2d_x_ready:\n    bsr.w s2d_x_hidden\n    tst.l d0\n    beq.w s2d_x_uncertain\n    ; Reveal directly at the target origin, never flash at old hotspot.\n    move.l (sp),d2\n    move.l 4(sp),d3\n    bsr.w s2d_x_reveal"
        ],
        [
            "s2d_x_return:\n    movem.l (sp)+,d2-d7/a0-a6",
            "s2d_x_return:\n    addq.l #8,sp\n    movem.l (sp)+,d2-d7/a0-a6"
        ]
    ]
}

def transform(name,source):
    for old,new in PATCHES.get(name,()):
        assert source.count(old)==1, (name,old)
        source=source.replace(old,new)
    return source
