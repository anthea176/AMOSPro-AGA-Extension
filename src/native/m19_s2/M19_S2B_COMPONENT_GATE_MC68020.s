; AGA_NATIVE_MIN_CPU: MC68020
; Private standalone entry table for component CI only; not an AP20 Lib.
    bra.w s2b_p2h_enter
    bra.w s2b_p2h_leave
    bra.w AGSP_S2B_SCAN
    bra.w AGSP_S2B_PICK
    bra.w AGSP_S2B_INSERT
    bra.w AGSP_S2B_ACQUIRE
    bra.w AGSP_S2B_DRAIN
    bra.w AGSP_S2B_PALETTE_MASK
    include "M19_S2B_PERSIST_ROOT_MC68020.s"
    include "M19_S2B_REGISTRY_MC68020.s"
    include "M19_S2B_ALLOCATE_MC68020.s"
    include "M19_S2B_RETIRE_PAIR_MC68020.s"
