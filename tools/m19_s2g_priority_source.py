#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2g-P1a: opt-in overlay of exact S2f production sources, no token yet."""
from m19_s2f_clip_source import transform as s2f_transform, once

PUBLIC = "M19_S2D_PUBLIC_MC68020.s"

def transform(name, source):
    source = s2f_transform(name, source)
    if name != PUBLIC:
        return source
    source = once(source,
        "    bra.w p2i_bank_free\n",
        "    bra.w p2i_bank_free\n    bra.w s2g_pub_sprite5\n")
    source = once(source, "I_FRAME equ 468",
        "W_LAYER equ 468\nI_FRAME equ 472")
    source = once(source,
        "    movea.l sp,a2\n    move.l d3,I_IMAGE(a2)\n",
        "    movea.l sp,a2\n    clr.l W_LAYER(a2)\ns2g_pub_args:\n"
        "    move.l d3,I_IMAGE(a2)\n")
    source = once(source,
        "    cmpi.l #4096,I_IMAGE(a2)\n    bhi.w p2i_end\n    bsr.w p2i_context",
        "    cmpi.l #4096,I_IMAGE(a2)\n    bhi.w p2i_end\n"
        "    move.l #-210,I_PHASE(a2)\n"
        "    cmpi.l #3,W_LAYER(a2)\n    bhi.w p2i_end\n"
        "    bsr.w p2i_context")
    source = once(source,
        "s2d_pub_active:\n    movea.l I_REC(a2),a4\n"
        "    cmpi.l #31,24(a4)\n    bne.w p2i_end\n",
        "s2d_pub_active:\n    movea.l I_REC(a2),a4\n"
        "    cmpi.l #31,24(a4)\n    bne.w p2i_end\n"
        "    move.l #-206,I_PHASE(a2)\n"
        "    bsr.w s2g_pub_same_layer\n"
        "    tst.l d0\n    beq.w p2i_end\n")
    source = once(source,
        "    move.l d1,d6\n    beq.w p2i_no\n    clr.l W_CWIDTH(a2)",
        "    move.l d1,d6\n    bsr.w s2g_pub_layer_mask\n"
        "    beq.w p2i_no\n    clr.l W_CWIDTH(a2)")
    return source + '\n    include "M19_S2G_PRIORITY_MC68020.s"\n'
