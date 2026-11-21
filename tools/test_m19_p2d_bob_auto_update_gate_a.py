#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A of the P2d auto-update candidate with Exec and hardware simulated."""

import unittest
from struct import unpack_from

from audit_ap20 import walk_tokens
from build_m19_p1d_limit_bob_in_memory import build_p1d
from build_m19_p2d_in_memory import build_p2d
from compiler_relocation import GETP, unpack_ap20
from m19_p0j_swap_barrier_emit import DIRTY, READY
from m19_p2d_bob_auto_update_emit import emit_bob_auto_update
from test_m19_p0d_safe_bank_blit_native import SIZE
from test_m19_p0j_pending_close_end_gate_a import DB
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p2b_bob_flip_gate_a import AMOS, expected, machine
from test_m19_p2c_bob_planes_gate_a import planes


class AutoUpdateGateA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline, cls.p1d = build_p1d()

    def machine(self, layout):
        m = machine(layout, self.baseline, self.p1d, emitter=emit_bob_auto_update_pair)
        _, _, offset = emit_bob_auto_update(self.p1d['context_delta'])
        m.fifth = m.entry + offset
        m.labels['guarded_swap_entry'] = m.labels['p2d_public_swap']
        return m

    def set_mode(self, m, value, **kwargs):
        return m.token('p2d_public_auto_update', value, (), **kwargs)

    def swap(self, m):
        return m.invoke_guard('swap', count=20_000_000)

    @staticmethod
    def paint_count(m):
        return sum(event[0] in ('BltMask', 'BltOpaque') for event in m.paint_blits)

    def test_build_and_dispatch(self):
        image, meta = build_p2d()
        self.assertEqual(build_p2d()[0], image)
        tokens, parts, _ = unpack_ap20(image)
        self.assertEqual(parts[meta['function']-1], GETP)
        signatures = {
            'aga bob clear': 'function', 'aga bob update': 'function',
            'aga bob bank free': 'instruction', 'aga x bob': 'function',
            'aga y bob': 'function', 'aga i bob': 'function',
        }
        services = [row[signatures[row['name']]] for row in walk_tokens(tokens)
                    if row['name'] in signatures]
        self.assertEqual(len(services), len(signatures))
        for entry in (meta['swap'], meta['function'], *services):
            group, offset = unpack_from('>HH', parts[entry], 2)
            self.assertEqual(group, meta['group'])
            self.assertEqual(dispatch_models(parts, group, offset, entry), 2)

    def test_ready_retry_and_real_pixels_with_modes(self):
        for layout in ('interpreted', 'compiled'):
            with self.subTest(layout=layout):
                m = self.machine(layout)
                self.assertEqual(self.set_mode(m, 1), 0)  # Prior fixture draw is READY.
                self.assertEqual(self.swap(m), 1)
                m.put(DB+20, 0)
                self.assertEqual(self.set_mode(m, -1), 0)
                self.assertEqual(self.set_mode(m, 2), 0)
                self.assertEqual(self.set_mode(m, 1, owner=AMOS+0x1000), 0)
                self.assertEqual(self.set_mode(m, 1), 1)
                self.assertEqual(m.flip(1, 1), 1)
                self.assertEqual(planes(m, 2, 0x24), 1)
                back = m.active_back_planes()
                expected_back, _ = expected(m, 1, 0, masks=(255, 0x24))
                visits = m.native_swap_visits
                draws = self.paint_count(m)
                page = m.get(DB+8)
                m.swap_accept = False
                self.assertEqual(self.swap(m), 0)
                self.assertEqual(m.native_swap_visits, visits+1)
                self.assertEqual(m.get(DB+8), page)
                self.assertEqual(m.status(), READY)
                self.assertGreater(self.paint_count(m), draws)
                self.assertEqual(m.read_back(), expected_back)
                draws = self.paint_count(m)
                self.assertEqual(self.set_mode(m, 0), 0)
                self.assertEqual(self.swap(m), 0)
                m.swap_accept = True
                self.assertEqual(self.swap(m), 1)
                self.assertEqual(self.paint_count(m), draws)
                self.assertNotEqual(m.get(DB+8), page)
                self.assertEqual([bytes(m.uc.mem_read(a, SIZE)) for a in back], expected_back)
                self.assertEqual(m.status(), 0)
                m.put(DB+20, 0)
                self.assertEqual(self.set_mode(m, 0), 1)
                self.assertEqual(self.swap(m), 1)
                self.assertEqual(self.paint_count(m), draws)

    def test_failure_does_not_present_then_clear_recovers(self):
        for layout in ('interpreted', 'compiled'):
            with self.subTest(layout=layout):
                m = self.machine(layout)
                self.assertEqual(self.swap(m), 1)
                m.put(DB+20, 0)
                self.assertEqual(self.set_mode(m, 1), 1)
                self.assertEqual(m.flip(2, 1), 1)
                m.fail_variant = True
                visits = m.native_swap_visits
                self.assertEqual(self.swap(m), 0)
                self.assertEqual(m.status(), DIRTY)
                self.assertEqual(self.swap(m), 0)
                self.assertEqual(m.native_swap_visits, visits)
                self.assertEqual(m.clear(), 1)
                m.fail_variant = False
                self.assertEqual(self.swap(m), 1)
                self.assertEqual(m.native_swap_visits, visits+1)

    def test_explicit_update_and_restoration_of_both_pages(self):
        for layout in ('interpreted', 'compiled'):
            with self.subTest(layout=layout):
                m = self.machine(layout)
                self.assertEqual(self.swap(m), 1)
                m.put(DB+20, 0)
                self.assertEqual(self.set_mode(m, 1), 1)
                backgrounds = {}
                for cycle in range(2):
                    physical = m.get(DB+8)
                    backgrounds[physical] = m.read_back()
                    self.assertEqual(m.flip(1, cycle+1), 1)
                    if cycle == 0:
                        self.assertEqual(m.direct(m.entry + m.labels['p2d_service_update'],
                                                  maxcount=20_000_000), 1)
                    draws = self.paint_count(m)
                    self.assertEqual(self.swap(m), 1)
                    if cycle == 0:
                        self.assertEqual(self.paint_count(m), draws)
                    m.put(DB+20, 0)
                for ident in (1, 2):
                    self.assertEqual(m.public('off', ident=ident), 1)
                for _ in range(2):
                    physical = m.get(DB+8)
                    page = m.active_back_planes()
                    self.assertEqual(self.swap(m), 1)
                    self.assertEqual([bytes(m.uc.mem_read(a, SIZE)) for a in page],
                                     backgrounds[physical])
                    m.put(DB+20, 0)

    def test_empty_page_and_both_close_paths_reset_mode(self):
        for layout in ('interpreted', 'compiled'):
            for close in ('close', 'end'):
                with self.subTest(layout=layout, close=close):
                    m = self.machine(layout)
                    self.assertEqual(self.swap(m), 1)
                    m.put(DB+20, 0)
                    self.assertEqual(m.public('off', ident=1), 1)
                    self.assertEqual(m.public('off', ident=2), 1)
                    self.assertEqual(self.set_mode(m, 1), 1)
                    mode = m.entry + m.labels['p2d_mode']
                    self.assertEqual(m.get(mode), AMOS)
                    before = self.paint_count(m)
                    self.assertEqual(self.swap(m), 1)
                    self.assertEqual(self.paint_count(m), before)
                    self.assertEqual(m.get(m.entry + m.labels['p2d_service_root']), 0)
                    m.put(DB+20, 0)
                    if close == 'close':
                        m.invoke_guard('close')
                    else:
                        m.invoke_callback()
                    self.assertEqual(m.get(m.real_state), 0)
                    self.assertEqual(m.get(mode), 0)


def emit_bob_auto_update_pair(context_delta):
    native, labels, _ = emit_bob_auto_update(context_delta)
    return native, labels


if __name__ == '__main__':
    unittest.main(verbosity=2)
