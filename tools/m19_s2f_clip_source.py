#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2f P2b overlay on S2e source copies only. Preserve original emitters."""
from m19_s2e_hotspot_source import transform as s2e_transform
from m19_s2f_cache_source import transform as raw_transform

PATCHES={
    "M19_S2D_PUBLIC_MC68020.s": [
        [
            "; S2e: one width per lifetime, three pairs, per-image signed hotspot.",
            "; S2f: signed logical anchor, fixed-width clipped representation."
        ],
        [
            "W_HOT equ 448\nI_FRAME equ 452",
            "W_HOT equ 448\nW_KEY equ 452\nW_CACHE equ 456\nW_CSIZE equ 460\nW_SAME equ 464\nI_FRAME equ 468"
        ],
        [
            "    move.l W_HOT(a2),W_R_HOT(a4)\n    lea W_PAL(a2),a0",
            "    move.l W_HOT(a2),W_R_HOT(a4)\n    move.l W_CACHE(a2),W_R_CACHE(a4)\n    move.l W_KEY(a2),W_R_KEY(a4)\n    lea W_PAL(a2),a0"
        ],
        [
            "    ; Ownership transferred into persistent receipt before any Get.\n    clr.l W_E(a2)",
            "    ; Ownership transferred into persistent receipt before any Get.\n    clr.l W_CACHE(a2)\n    clr.l W_E(a2)"
        ],
        [
            "    move.l I_IMAGE(a2),d0\n    cmp.l W_R_IMAGE(a4),d0\n    beq.w s2d_pub_move\n    move.l #-201,I_PHASE(a2)",
            "    move.l I_IMAGE(a2),d0\n    cmp.l W_R_IMAGE(a4),d0\n    bne.s s2f_pub_change\n    move.l #1,W_SAME(a2)\n    move.l W_KEY(a2),d0\n    cmp.l W_R_KEY(a4),d0\n    beq.w s2d_pub_move\n    bra.w s2f_pub_restage\ns2f_pub_change:\n    move.l #-201,I_PHASE(a2)"
        ],
        [
            "    bsr.w s2d_pub_expect\n    tst.l d0\n    beq.w p2i_end\n    movea.l I_REC(a2),a4\n    tst.l 80(a4)",
            "    bsr.w s2d_pub_expect\n    tst.l d0\n    beq.w p2i_end\ns2f_pub_restage:\n    movea.l I_REC(a2),a4\n    tst.l 80(a4)"
        ],
        [
            "    move.l W_R_STAGE(a4),d0\n    cmp.l I_IMAGE(a2),d0\n    beq.s s2d_pub_exchange\n    movea.l a4,a0",
            "    move.l W_R_STAGE(a4),d0\n    cmp.l I_IMAGE(a2),d0\n    bne.s s2f_pub_drop\n    move.l W_R_STAGEKEY(a4),d0\n    cmp.l W_KEY(a2),d0\n    beq.w s2d_pub_exchange\ns2f_pub_drop:\n    movea.l a4,a0"
        ],
        [
            "    clr.l W_R_STAGE(a4)\ns2d_pub_stage_new:\n    move.l #-202,I_PHASE(a2)\n    bsr.w s2d_pub_prepare\n    tst.l d0",
            "    clr.l W_R_STAGE(a4)\n    clr.l W_R_STAGEKEY(a4)\n    movea.l a4,a0\n    move.l #W_R_STAGECACHE,d0\n    bsr.w s2f_reg_free\ns2d_pub_stage_new:\n    move.l #-202,I_PHASE(a2)\n    tst.l W_SAME(a2)\n    beq.s s2f_pub_stage_bank\n    bsr.w s2f_pub_prepare_current\n    bra.s s2f_pub_stage_result\ns2f_pub_stage_bank:\n    bsr.w s2d_pub_prepare\ns2f_pub_stage_result:\n    tst.l d0"
        ],
        [
            "    move.l I_IMAGE(a2),W_R_STAGE(a4)\n    move.l #1,80(a4)\n    clr.l W_E(a2)",
            "    move.l I_IMAGE(a2),W_R_STAGE(a4)\n    move.l W_KEY(a2),W_R_STAGEKEY(a4)\n    move.l W_CACHE(a2),W_R_STAGECACHE(a4)\n    move.l #1,80(a4)\n    clr.l W_CACHE(a2)\n    clr.l W_E(a2)"
        ],
        [
            "    move.l d0,W_R_STAGE(a4)\n    move.l W_HOT(a2),W_R_HOT(a4)\n    bsr.w s2d_pub_expect",
            "    move.l d0,W_R_STAGE(a4)\n    move.l W_R_KEY(a4),d0\n    move.l W_R_STAGEKEY(a4),W_R_KEY(a4)\n    move.l d0,W_R_STAGEKEY(a4)\n    tst.l W_SAME(a2)\n    bne.w s2d_pub_move\n    move.l W_R_CACHE(a4),d0\n    move.l W_R_STAGECACHE(a4),W_R_CACHE(a4)\n    move.l d0,W_R_STAGECACHE(a4)\n    move.l W_HOT(a2),W_R_HOT(a4)\n    bsr.w s2d_pub_expect"
        ],
        [
            "    dbra d7,s2d_pub_private_loop\n    bra.w p2i_end",
            "    dbra d7,s2d_pub_private_loop\n    movea.l a2,a0\n    move.l #W_CACHE,d0\n    bsr.w s2f_reg_free\n    bra.w p2i_end"
        ],
        [
            "    clr.l W_B1(a2)\n    rts\n\np2i_context:",
            "    clr.l W_B1(a2)\n    clr.l W_CACHE(a2)\n    clr.l W_SAME(a2)\n    rts\n\np2i_context:"
        ],
        [
            "    include \"M19_S2E_HOTSPOT_MC68020.s\"",
            "    include \"M19_S2F_CLIP_KERNEL_MC68020.s\"\n    include \"M19_S2F_CACHE_MC68020.s\""
        ]
    ],
    "M19_S2D_REGISTRY_MC68020.s": [
        [
            "; S2e: named v7 registry, three inline ExtSprite receipts.",
            "; S2f: named v8 registry, three inline ExtSprite/cache receipts."
        ],
        [
            "W_REC_BYTES equ 172",
            "W_REC_BYTES equ 188"
        ],
        [
            "W_R_HOT equ 168 ; two signed WORDs from AGSP v1",
            "W_R_HOT equ 168 ; two signed WORDs from AGSP v1\nW_R_CACHE equ 172\nW_R_KEY equ 176\nW_R_STAGECACHE equ 180\nW_R_STAGEKEY equ 184"
        ],
        [
            "    addi.l #568,d0",
            "    addi.l #616,d0"
        ],
        [
            "    moveq #42,d1\ns2d_reg_zero:",
            "    moveq #46,d1\ns2d_reg_zero:"
        ],
        [
            "s2d_reg_peers:\n    lea 52(a2),a4",
            "s2d_reg_peers:\n    bsr.w s2f_reg_validate\n    tst.l d0\n    beq.w s2d_reg_bad\n    lea 52(a2),a4"
        ],
        [
            "    moveq #5,d2\ns2d_reg_outer:",
            "    moveq #7,d2\ns2d_reg_outer:"
        ],
        [
            "    moveq #5,d3\ns2d_reg_inner:",
            "    moveq #7,d3\ns2d_reg_inner:"
        ],
        [
            "    dc.b 4,8,52,56,72,76",
            "    dc.b 4,8,52,56,72,76,172,180"
        ],
        [
            "    bsr.w AGSP_S2D_EXT_RECLAIM\n    tst.l d0\n    beq.s s2d_drain_pending\n    movea.l a3,a0\n    moveq #42,d0",
            "    bsr.w AGSP_S2D_EXT_RECLAIM\n    tst.l d0\n    beq.s s2d_drain_pending\n    movea.l a3,a0\n    move.l #W_R_CACHE,d0\n    bsr.w s2f_reg_free\n    move.l #W_R_STAGECACHE,d0\n    bsr.w s2f_reg_free\n    movea.l a3,a0\n    moveq #46,d0"
        ]
    ],
    "M19_S2D_PERSIST_ROOT_MC68020.s": [
        [
            "; S2e v7 private named transaction; v6 must be refused.",
            "; S2f v8 private named transaction; v7 must be refused."
        ],
        [
            "; 624-byte allocation, root at +56, count +0, owner +4, State +8,",
            "; 672-byte allocation, root at +56, count +0, owner +4, State +8,"
        ],
        [
            "; Three 172-byte inline records at root+52/+224/+396 (pairs 2/4/6).",
            "; Three 188-byte inline records at root+52/+240/+428 (pairs 2/4/6)."
        ],
        [
            "    move.l #624,d0",
            "    move.l #672,d0"
        ],
        [
            "    move.l #$00070270,52(a3)",
            "    move.l #$000802a0,52(a3)"
        ],
        [
            "    move.w #128,d0 ; DBRA consumes only the low WORD (129 longs)",
            "    move.w #140,d0 ; DBRA consumes only the low WORD (141 longs)"
        ],
        [
            "    addi.l #623,d0",
            "    addi.l #671,d0"
        ],
        [
            "    cmpi.l #$00070270,52(a4)",
            "    cmpi.l #$000802a0,52(a4)"
        ]
    ]
}

def once(s,old,new):
    assert s.count(old)==1,(old,s.count(old))
    return s.replace(old,new,1)

def transform(name,source):
    source=s2e_transform(name,source)
    for old,new in PATCHES.get(name,()):
        source=once(source,old,new)
    if name=='M19_S2D_PUBLIC_MC68020.s':
        a='s2d_pub_prepare:\n';b='s2d_pub_pick:\n'
        assert source.count(a)==source.count(b)==1
        i,j=source.index(a),source.index(b)
        assert i<j
        source=source[:i]+'    include "M19_S2F_PUBLIC_MC68020.s"\n\n'+source[j:]
    elif name=='M19_S2D_REGISTRY_MC68020.s':
        source+='\n    include "M19_S2F_RECEIPT_MC68020.s"\n'
    elif name=='M19_S2D_EXT_PREPARE_MC68020.s':
        source=raw_transform(source)
    return source
