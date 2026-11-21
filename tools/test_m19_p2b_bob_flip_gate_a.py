#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2b public dispatch, native render/collision and Chip lifecycle in emulation."""
from pathlib import Path
from struct import unpack_from
import unittest

from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from amos_link_test_support import relocate
from build_m19_p2b_in_memory import build_p2b
from build_m19_p1d_limit_bob_in_memory import build_p1d
from compiler_relocation import GETP, RBSR, unpack_ap20
from m19_p0a_multi_bob_abk import parse_payload
from m19_p2a_bob_collision_model import Rect, collision
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters
from m19_p1d_limit_bob_emit import emit_limit_bobs
from m19_p2b_bob_flip_emit import BLOCK, MODE, SLOT_BYTES, emit_bob_flip
from m19_p2b_bob_orientation_model import OrientedImage
from test_m19_p0d_safe_bank_blit_native import oracle as paint
from test_m19_p0j_pending_close_end_gate_a import ready, DB
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p1d_limit_bob_gate_a import load_native
from test_m19_p1c_bob_priority_gate_a import invoke
from test_m19_p2a_public_gate_a import ARGS, PublicMachine
from test_m19_p2b_planar_orientation020_gate_a import oracle
from test_m5_generic import AMOS, AR, DR, EXEC, GFX, STACK, STOP

ROOT = Path(__file__).resolve().parents[1]


class FlipMachine(PublicMachine):
    def __init__(self, source, layout):
        self.variants = {}
        self.next_variant = 0x230000
        self.variant_allocations = 0
        self.fail_variant = False
        super().__init__(source, layout)
        for offset in (198, 210):
            vector = EXEC-offset
            self.uc.mem_write(vector, b'\x4e\x75')

    def os_call(self, uc, address, size, user):
        if address == EXEC-198 and self.d(1) == 2:
            if self.fail_variant:
                return self._os_return(0)
            pointer = self.next_variant
            length = self.d(0)
            self.next_variant += (length+15) & -16
            self.variants[pointer] = length
            self.variant_allocations += 1
            return self._os_return(pointer)
        if address == EXEC-210 and self.a(1) in self.variants:
            assert self.variants.pop(self.a(1)) == self.d(0)
            return self._os_return(0)
        if address == EXEC-534 and any(p <= self.a(1) < p+n for p,n in self.variants.items()):
            return self._os_return(2)
        if address in (GFX-606, GFX-636):
            self.chip_live.update(self.variants)
            try:
                return super().os_call(uc, address, size, user)
            finally:
                for p in self.variants:
                    del self.chip_live[p]
        return super().os_call(uc, address, size, user)

    def token(self, entry, mode, arguments, *, owner=AMOS):
        for i, reg in enumerate(DR+AR[:7]):
            self.uc.reg_write(reg, 0x42000+32*i)
        self.uc.reg_write(AR[3], ARGS)
        self.uc.reg_write(AR[5], owner)
        self.uc.reg_write(DR[3], mode & 0xffffffff)
        for i, argument in enumerate(arguments):
            self.put(ARGS+4*i, argument & 0xffffffff)
        saved = {reg: self.uc.reg_read(reg) for reg in DR+AR[:7]
                 if reg not in (DR[2], DR[3], AR[3])}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(self.entry+self.labels[entry], STOP, count=15000000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert (self.d(2), self.a(3), self.a(7)) == (0, ARGS+4*len(arguments), STACK+4)
        assert all(self.uc.reg_read(reg) == val for reg,val in saved.items())
        result = self.d(3)
        return result if result < 0x80000000 else result-0x100000000

    def flip(self, ident, mode, **kwargs):
        return self.token('p2b_public_flip', mode, (ident,), **kwargs)

    def collide(self, mode):
        return self.token('p2a_public_bob_col', mode, (2,1))


def machine(layout, p1d_binary, p1d, *, emitter=emit_bob_flip):
    _, parts, _ = unpack_ap20(p1d_binary)
    m = ready(layout, cls=FlipMachine, inject_failure=False)
    _, _, _, reset = load_native(m, parts, p1d)
    native, labels = emitter(p1d['context_delta'])
    baseline, _ = emit_limit_bobs(p1d['context_delta'])
    previous = relocate(baseline, m.entry, {}, m.uc)
    patched = relocate(native, m.entry, {}, m.uc)
    for offset, (old, new) in enumerate(zip(previous, patched)):
        if old != new:
            m.uc.mem_write(m.entry+offset, bytes([new]))
    m.uc.mem_write(m.entry+len(previous), patched[len(previous):])
    m.uc.ctl_remove_cache(m.entry, m.entry+len(native))
    m.labels.update(labels)
    m.labels['routed_paint_all_entry'] = labels['b8_b7_draw_trampoline_entry']
    m.labels['guarded_close_entry'] = labels['b8_b7_close_trampoline_entry']
    m.labels['public_aga_bob_entry'] = labels['b8_b7_bob_set_bootstrap_entry']
    m.fifth_source, m.fifth_labels = emit_m19_p1a_getters()
    m.uc.mem_write(m.fifth, m.fifth_source)
    m.uc.ctl_remove_cache(m.fifth, m.fifth+len(m.fifth_source))
    assert invoke(m, reset) == 1
    return m


def expected(m, a, b, masks=(255, 255)):
    images = [parse_payload(m.bank_payload(bank)).image(1) for bank in (10,11)]
    views = [OrientedImage(image, bool(mode&1), bool(mode&2))
             for image,mode in zip(images,(a,b))]
    bobs = [view.collision_bob(i,bank,x,y)
            for view,(i,bank,x,y) in zip(views, ((1,10,5,7),(2,11,9,11)))]
    result = m.read_back()
    for bob, image, mode, mask in zip(bobs, images, (a,b), masks):
        painted = paint(result, oracle(image,mode), bob.origin_x, bob.origin_y)
        result = [new if mask & (1 << plane) else old
                  for plane, (old, new) in enumerate(zip(result, painted))]
    return result, bobs


class BobFlipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline, cls.p1d = build_p1d()

    def test_ap20_public_slot(self):
        binary, meta = build_p2b()
        _, parts, _ = unpack_ap20(binary)
        index = meta['function']
        self.assertEqual(parts[index-1], GETP)
        self.assertTrue(parts[index].startswith(RBSR))
        self.assertEqual(unpack_from('>H', parts[index], 2)[0], meta['bob_group'])
        self.assertLess(meta['pc16_max'],32766)
        offset = unpack_from('>H', parts[index], 4)[0]
        self.assertEqual(dispatch_models(parts, meta['bob_group'], offset, index), 2)
        if (ROOT/'dist/AMOSPro_AGA.Lib').read_bytes() == binary:
            print('P2B_CANONICAL', meta)

    def test_draw_and_collision_use_exact_same_variants(self):
        for layout in ('interpreted','compiled'):
            m = machine(layout, self.baseline, self.p1d)
            self.assertEqual(m.flip(0,1), 0)
            self.assertEqual(m.flip(1,4), 0)
            self.assertEqual(m.flip(1,1,owner=AMOS+0x1000), 0)
            self.assertEqual(m.flip(64,1), 0)
            self.assertEqual(m.invoke_guard('swap'), 1)
            m.put(DB+20, 0)
            update = m.fifth+m.fifth_labels['b8_service_update_first_entry']
            for first, second in ((0,0),(1,0),(1,2),(3,1),(2,3),(0,0)):
                with self.subTest(layout=layout, modes=(first,second)):
                    self.assertEqual(m.flip(1,first), 1)
                    self.assertEqual(m.flip(2,second), 1)
                    page = m.get(DB+8)
                    background = m.read_back()
                    pixels, bobs = expected(m, first, second)
                    self.assertEqual(m.direct(update, maxcount=20_000_000), 1)
                    self.assertEqual(m.read_back(), pixels)
                    allocations = m.variant_allocations
                    for mode in (0,1):
                        ref = collision(*bobs, screen=Rect(0,0,320,256), mode='mask' if mode else 'rect')
                        self.assertEqual(m.collide(mode), int(ref))
                    self.assertEqual(m.variant_allocations, allocations)
                    self.assertEqual(m.get(DB+8), page)
                    self.assertEqual(m.clear(), 1)
                    self.assertEqual(m.read_back(), background)
                    self.assertEqual(m.invoke_guard('swap'), 1)
                    self.assertNotEqual(m.get(DB+8), page)
                    m.put(DB+20, 0)
            self.assertFalse(m.variants)

    def test_failed_allocation_and_bank_free(self):
        for layout in ('interpreted','compiled'):
            m = machine(layout, self.baseline, self.p1d)
            self.assertEqual(m.flip(1,1), 1)
            m.fail_variant = True
            self.assertEqual(m.collide(1), -1)
            self.assertFalse(m.variants)
            m.fail_variant = False
            m.collide(1)
            self.assertEqual(len(m.variants), 1)
            self.assertEqual(m.invoke_guard('swap'), 1)
            m.put(DB+20, 0)
            self.assertEqual(m.free(10),1)
            self.assertFalse(m.variants)
            self.assertEqual(m.collide(1), -1)

    def test_edit_invalidates_generation_and_pending_close_keeps_resources(self):
        for layout in ('interpreted','compiled'):
            m = machine(layout, self.baseline, self.p1d)
            assert m.flip(1,1) == 1
            m.collide(1)
            old, = m.variants
            assert m.invoke_guard('swap') == 1
            m.put(DB+20, 0)
            assert m.call_edit('ins', (10,3,8,6,8)) == 1
            m.collide(1)
            self.assertEqual(len(m.variants), 1)
            self.assertNotIn(old, m.variants)
            m.put(DB+20, 3)
            m.safe_after, m.disp_after = None, None
            m.invoke_guard('close')
            self.assertNotEqual(m.get(m.real_state), 0)
            self.assertEqual(len(m.variants), 1)
            m.put(DB+20, 0)
            m.invoke_guard('close')
            self.assertFalse(m.variants)

    def test_failed_paint_does_not_present_the_back_page(self):
        for layout in ('interpreted','compiled'):
            m = machine(layout, self.baseline, self.p1d)
            assert m.invoke_guard('swap') == 1
            m.put(DB+20, 0)
            assert m.flip(2,1) == 1
            m.fail_variant = True
            self.assertEqual(m.frame(), 0)
            self.assertEqual(m.invoke_guard('swap'), 0)
            self.assertFalse(m.variants)

    def test_close_and_end_release_tracked_variants(self):
        for layout in ('interpreted','compiled'):
            for shutdown in ('close','end'):
                with self.subTest(layout=layout, shutdown=shutdown):
                    m = machine(layout, self.baseline, self.p1d)
                    self.assertEqual(m.flip(1,3), 1)
                    m.collide(1)
                    self.assertEqual(len(m.variants),1)
                    if shutdown == 'close':
                        m.invoke_guard('close')
                    else:
                        m.invoke_callback()
                    self.assertEqual(m.get(m.real_state),0)
                    self.assertFalse(m.variants)
                    self.assertEqual(m.get(m.entry+m.labels['p2b_owner']),0)
                    slot = m.entry+m.labels['p2b_slots']
                    self.assertEqual((m.get(slot+MODE),m.get(slot+BLOCK)),(0,0))


if __name__ == '__main__':
    unittest.main(verbosity=2)
