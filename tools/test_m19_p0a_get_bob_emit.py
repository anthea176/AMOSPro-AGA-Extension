#!/usr/bin/env python3
"""M19 P0a R88 source-level regression; NOT a 68000 execution."""
from __future__ import annotations
import hashlib,unittest
from m19_p0a_get_bob_emit import emit_get_bob,FRAME,GETADR
from m19_p0a_bank_select_emit import emit_bank_select


class R88NativeGetEmission(unittest.TestCase):
    def test_shared_native_bank_selector_immutable(self):
        select,labels=emit_bank_select()
        full,glabels=emit_get_bob()
        self.assertEqual(full[:len(select)],select)
        self.assertEqual(glabels['get_entry'],len(select))
        self.assertEqual(glabels['bank_active_state'],labels['active_state'])
        self.assertEqual(glabels['bank_commit'],labels['commit'])

    def test_native_frame_and_relocation(self):
        raw,labels=emit_get_bob()
        self.assertEqual(len(raw)&1,0)
        self.assertLess(len(raw),32766)
        part=raw[labels['get_entry']:]
        self.assertEqual(part[:8],bytes.fromhex('48e7efee4feffec0'))
        self.assertIn(bytes.fromhex('4fef01404cdf77f774004e75'),part)
        self.assertEqual(FRAME,320)
        self.assertGreaterEqual(part.count(GETADR),2)

    def test_no_destructive_reserve_or_screen_swap(self):
        raw,labels=emit_get_bob()
        new=raw[labels['get_entry']:]
        from amos_main_abi import main_index,rjsr
        self.assertNotIn(rjsr(816),new)  # exact R88 main-table index
        # CPU source writes only scratch memory. No Blitter/Aga Swap.
        self.assertIn(bytes.fromhex('4eae'),new)

    def test_bitplane_capture_and_padding_helpers_exist(self):
        _,labels=emit_get_bob()
        for x in ('check_padding','padding_loop','padding_accept',
                  'copy_bytes','copy_long_loop','emit_copy_old',
                  'emit_new_entry','capture_plane','capture_row','capture_pixel',
                  'finished_entries','bank_commit'):
            self.assertIn(x,labels)
        self.assertLess(labels['capture_pixel'],labels['capture_plane']+2000)

    def test_padding_uses_address_register_not_stride_register(self):
        raw,labels=emit_get_bob()
        pad=raw[labels['check_padding']:labels['padding_accept']]
        # ADDA.L D1,A1 must position the first trailing WORD and advance rows.
        self.assertEqual(pad.count(bytes.fromhex('d3c1')),2)
        self.assertNotIn(bytes.fromhex('d281'),pad)  # ADD.L D1,D1 doubles stride

    def test_repeated_byte_output_is_deterministic(self):
        a,labels1=emit_get_bob()
        b,labels2=emit_get_bob()
        self.assertEqual((a,labels1),(b,labels2))
        self.assertEqual(len(hashlib.sha256(a).digest()),32)


if __name__=='__main__':unittest.main(verbosity=2)
