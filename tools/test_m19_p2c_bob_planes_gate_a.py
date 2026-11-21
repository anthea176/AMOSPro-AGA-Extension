#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2c native Bob Planes, checked AP20 dispatch and pixel-exact drawing."""

import unittest
from struct import unpack_from

from build_m19_p1d_limit_bob_in_memory import build_p1d
from build_m19_p2c_in_memory import build_p2c
from compiler_relocation import GETP, RBSR, unpack_ap20
from m19_p2b_bob_flip_emit import SLOT_BYTES
from m19_p2c_bob_planes_emit import PLANE_SELECTION, emit_bob_planes
from test_m19_p0j_pending_close_end_gate_a import DB
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p1d_limit_bob_gate_a import set_limit
from test_m19_p2b_bob_flip_gate_a import AMOS, expected, machine


def planes(machine, ident, mask, *, owner=AMOS):
    return machine.token('p2c_public_planes', mask, (ident,), owner=owner)


class PlanesGateA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline, cls.p1d = build_p1d()

    def machine(self, layout):
        return machine(layout, self.baseline, self.p1d, emitter=emit_bob_planes)

    def test_ap20_slot(self):
        binary, meta = build_p2c()
        _, parts, _ = unpack_ap20(binary)
        index, group = meta['function'], meta['bob_group']
        self.assertEqual(parts[index-1], GETP)
        self.assertTrue(parts[index].startswith(RBSR))
        target, offset = unpack_from('>HH', parts[index], 2)
        self.assertEqual(target, group)
        self.assertLess(meta['pc16_max'], 32766)
        self.assertEqual(dispatch_models(parts, group, offset, index), 2)

    def test_opaque_and_masked_pixels_with_flip_and_restore(self):
        for layout in ('interpreted', 'compiled'):
            m = self.machine(layout)
            self.assertEqual(m.invoke_guard('swap'), 1)
            m.put(DB+20, 0)
            update = m.fifth + m.fifth_labels['b8_service_update_first_entry']
            for masks, modes in (((255,255),(0,0)), ((0,0),(0,0)),
                                 ((0x81,0x24),(1,0)), ((0x42,0x81),(2,3)),
                                 ((255,255),(3,1)), ((1,128),(0,0))):
                with self.subTest(layout=layout, masks=masks, modes=modes):
                    for i in range(2):
                        self.assertEqual(m.flip(i+1,modes[i]), 1)
                        self.assertEqual(planes(m,i+1,masks[i]), 1)
                    physical_page = m.get(DB+8)
                    background = m.read_back()
                    result, _ = expected(m, *modes, masks=masks)
                    self.assertEqual(m.direct(update,maxcount=20_000_000), 1)
                    self.assertEqual(m.read_back(), result)
                    self.assertEqual(m.get(DB+8), physical_page)
                    self.assertEqual(m.clear(), 1)
                    self.assertEqual(m.read_back(), background)
                    self.assertEqual(m.invoke_guard('swap'), 1)
                    self.assertNotEqual(m.get(DB+8), physical_page)
                    m.put(DB+20, 0)

    def test_refusals_slot_isolation_and_close_reset(self):
        for layout in ('interpreted', 'compiled'):
            m = self.machine(layout)
            slot = m.entry+m.labels['p2b_slots']+PLANE_SELECTION
            self.assertEqual(planes(m,1,0x81), 1)
            self.assertEqual(m.get(slot), 0x7e)
            self.assertEqual(m.get(slot+SLOT_BYTES), 0)
            for ident,mask in ((0,1),(65,1),(3,10),(1,-1),(1,256)):
                self.assertEqual(planes(m,ident,mask), 0)
            self.assertEqual(planes(m,1,0,owner=AMOS+0x1000), 0)
            self.assertEqual(m.get(slot), 0x7e)
            self.assertEqual(m.public('off', ident=1), 1)
            self.assertEqual(planes(m,1,255), 0)
            self.assertEqual(m.get(slot), 0x7e)
            self.assertEqual(set_limit(m, 2, (0,0,1,1)), 1)
            m.invoke_guard('close')
            self.assertEqual(m.get(m.real_state), 0)
            self.assertEqual(m.get(slot), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
