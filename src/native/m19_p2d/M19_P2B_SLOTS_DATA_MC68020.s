; AGA_NATIVE_MIN_CPU: MC68020
; P2b state table, native source-defined DATA (not instructions).
; Source authority: tools/m19_p2b_bob_flip_emit.py
;   L('p2b_owner'); c.b.extend(bytes(4))
;   L('p2b_slots'); c.b.extend(bytes(64*SLOT_BYTES)), SLOT_BYTES=64
; Exactly 4100 zero-initialized bytes at BOBS +$0A4C0..$0B4C3.
; This file is included once by M19_P2D_BOBS_EDITABLE.s.

P2B_SLOT_COUNT         equ 64
P2B_SLOT_BYTES         equ 64
P2B_SLOT_STATE_BYTES   equ P2B_SLOT_COUNT*P2B_SLOT_BYTES

p2b_owner:
    dc.l 0                   ; current AMOS owner pointer; initially unbound
p2b_slots:
    dcb.b P2B_SLOT_STATE_BYTES,0  ; 64 records, initialized to zero
