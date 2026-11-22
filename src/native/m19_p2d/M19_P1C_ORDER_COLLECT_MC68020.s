; AGA_NATIVE_MIN_CPU: MC68020
; P1c frame priority key collection / stable insertion from
; m19_p1c_bob_priority_emit.py::PriorityTraversal.begin.
; BOBS+$07C18..+$07C98 = 128 MC68020 instruction bytes; no data.
P1C_SCAN_ID equ 44
P1C_COUNT equ 36
P1C_SORT_MODE equ 40
P1C_CURSOR equ 32
P1C_RECORD equ 96
P1C_LIST equ 160

p1c_collect:
    move.l P1C_SCAN_ID(a2),d0
    cmpi.l #64,d0
    bhi.w p1c_collect_done
    move.l a2,d1
    addi.l #P1C_RECORD,d1
    movea.l d1,a1
    bsr.w relay_read_entry
    tst.l d3
    beq.w p1c_collect_next
    move.l P1C_SCAN_ID(a2),d7
    cmpi.l #2,P1C_SORT_MODE(a2)
    beq.w p1c_insert
    move.l P1C_RECORD+12(a2),d0
    addi.l #32768,d0
    lsl.l #7,d0
    or.l d0,d7
L_BOBS_07C58:
p1c_insert:
    move.l P1C_COUNT(a2),d0
    lsl.l #2,d0
    movea.l a2,a0
    adda.l #P1C_LIST,a0
    movea.l a0,a1
    adda.l d0,a0
L_BOBS_07C6A:
p1c_insert_scan:
    cmpa.l a1,a0
    beq.w p1c_store_key
    move.l -4(a0),d0
    cmp.l d7,d0
    bls.w p1c_store_key
    move.l d0,(a0)
    subq.l #4,a0
    bra.w p1c_insert_scan
L_BOBS_07C82:
p1c_store_key:
    move.l d7,(a0)
    addq.l #1,P1C_COUNT(a2)
L_BOBS_07C88:
p1c_collect_next:
    addq.l #1,P1C_SCAN_ID(a2)
    bra.w p1c_collect
L_BOBS_07C90:
p1c_collect_done:
    move.l #0,P1C_CURSOR(a2)
