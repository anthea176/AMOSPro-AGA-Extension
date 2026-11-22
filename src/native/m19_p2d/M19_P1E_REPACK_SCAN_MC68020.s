; AGA_NATIVE_MIN_CPU: MC68020
; P1e repack bank directory scan and keep/filter rule.
; Source m19_p1e_bank_repack_emit.py::emit_bank_repack.
; BOBS+$087C2..+$08820 = 94 MC68020 instruction bytes, no data.
P1E_SCAN_HEADER equ 32
P1E_SCAN_ENTRY equ 40
P1E_SCAN_COUNT equ 36
P1E_SCAN_LAST equ 20
P1E_SCAN_FIRST equ 16
P1E_SCAN_DATA_SIZE equ 44
P1E_SCAN_ENTRIES equ 40

repack_scan_init:
    movea.l (a2),a4
    adda.l #P1E_SCAN_HEADER,a4
    move.l P1E_SCAN_COUNT(a2),d7
L_BOBS_087CE:
repack_scan:
    tst.l d7
    beq.w L_BOBS_08820
    move.l #0,d0
    move.w (a4),d0
    tst.l P1E_SCAN_LAST(a2)
    beq.w repack_insert_scan
    cmp.l P1E_SCAN_FIRST(a2),d0
    bcs.w repack_keep
    cmp.l P1E_SCAN_LAST(a2),d0
    bls.w repack_scan_next
    bra.w repack_keep
L_BOBS_087F8:
repack_insert_scan:
    cmp.l P1E_SCAN_FIRST(a2),d0
    beq.w L_BOBS_089CA
L_BOBS_08800:
repack_keep:
    move.l 16(a4),d0
    add.l 24(a4),d0
    add.l P1E_SCAN_DATA_SIZE(a2),d0
    move.l d0,P1E_SCAN_DATA_SIZE(a2)
    addq.l #1,P1E_SCAN_ENTRIES(a2)
L_BOBS_08814:
repack_scan_next:
    adda.l #P1E_SCAN_ENTRY,a4
    subq.l #1,d7
    bra.w repack_scan
