#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S0 HOST MODEL tests ONLY; never a native, WinUAE or Compiler proof."""
import unittest

from aga_sprite_s0_model import Phase, SpriteS0


class SpriteS0Tests(unittest.TestCase):
    def test_one_sprite_acquire_move_and_orderly_release(self):
        slot = SpriteS0()
        self.assertTrue(slot.prepare(100, 144, 500))
        self.assertTrue(slot.acquire(5))
        self.assertTrue(slot.present(100, 144, 12, 20))
        self.assertTrue(slot.present(100, 144, 120, 60))
        self.assertFalse(slot.can_close_screen(100))
        self.assertFalse(slot.release(100, 144))
        self.assertTrue(slot.confirm_dma_detached(100, 144))
        self.assertTrue(slot.release(100, 144))
        self.assertEqual(slot.events, [
            ("free_owned_channel", 5), ("free_owned_image", 500)])
        self.assertTrue(slot.can_close_screen(100))
        self.assertEqual(slot.phase, Phase.RELEASED)

    def test_no_channel_is_not_a_channel(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        self.assertFalse(slot.acquire(-1))
        self.assertEqual(slot.phase, Phase.DATA_READY)
        self.assertFalse(slot.present(100, 144, 5, 5))
        self.assertTrue(slot.release(100, 144))
        self.assertEqual(slot.events, [("free_owned_image", 500)])

    def test_not_reusing_occupied_or_invalid_channel(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        for channel in (-9, -1, 8, 100, None):
            self.assertFalse(slot.acquire(channel))
        self.assertTrue(slot.acquire(7))
        self.assertFalse(slot.acquire(0))  # no second channel acquisition
        self.assertEqual(slot.channel, 7)

    def test_zero_channel_only_when_allocated_by_os(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        self.assertTrue(slot.acquire(0))  # only when returned by the OS
        slot.confirm_dma_detached(100, 144)
        slot.release(100, 144)
        self.assertEqual(slot.events[0], ("free_owned_channel", 0))

    def test_owner_mismatch_fails_without_state_changes(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        slot.acquire(4)
        self.assertFalse(slot.present(101, 144, 1, 2))
        self.assertFalse(slot.present(100, 145, 1, 2))
        self.assertFalse(slot.confirm_dma_detached(101, 144))
        self.assertFalse(slot.release(101, 144))
        self.assertFalse(slot.release(100, 145))
        self.assertEqual(slot.phase, Phase.CHANNEL_OWNED)
        self.assertEqual(slot.events, [])

    def test_no_free_on_active_dma(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        slot.acquire(3)
        slot.present(100, 144, 22, 38)
        self.assertFalse(slot.release(100, 144))
        self.assertEqual(slot.events, [])

    def test_cannot_close_owner_screen_with_resource(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        self.assertFalse(slot.can_close_screen(100))
        self.assertTrue(slot.can_close_screen(200))
        self.assertTrue(slot.release(100, 144))
        self.assertTrue(slot.can_close_screen(100))

    def test_double_release_does_not_free_twice(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        slot.acquire(2)
        slot.confirm_dma_detached(100, 144)
        slot.release(100, 144)
        snapshot = list(slot.events)
        self.assertTrue(slot.release(100, 144))
        self.assertEqual(slot.events, snapshot)

    def test_open_close_reopen_uses_new_owner(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        slot.release(100, 144)
        self.assertTrue(slot.prepare(101, 145, 501))
        self.assertFalse(slot.release(100, 144))
        self.assertEqual(slot.image, 501)
        self.assertTrue(slot.release(101, 145))
        self.assertEqual(slot.events, [("free_owned_image", 500),
                                       ("free_owned_image", 501)])

    def test_oom_or_invalid_screen_no_side_effect(self):
        slot = SpriteS0()
        self.assertFalse(slot.prepare(100, 144, None))
        self.assertFalse(slot.prepare(0, 144, 500))
        self.assertFalse(slot.prepare(100, 0, 500))
        self.assertEqual(slot.phase, Phase.EMPTY)
        self.assertEqual(slot.events, [])

    def test_double_prepare_does_not_overwrite_ownership(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        self.assertFalse(slot.prepare(101, 145, 501))
        self.assertEqual((slot.screen, slot.viewport, slot.image), (100, 144, 500))

    def test_bob_swap_copper_not_part_of_s0_model(self):
        slot = SpriteS0()
        slot.prepare(100, 144, 500)
        slot.acquire(6)
        slot.present(100, 144, 20, 20)
        slot.confirm_dma_detached(100, 144)
        slot.release(100, 144)
        self.assertNotIn("swap", str(slot.events).lower())
        self.assertNotIn("copper", str(slot.events).lower())
        self.assertEqual(len(slot.events), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
