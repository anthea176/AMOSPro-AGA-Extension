#!/usr/bin/env python3
"""Host reference for selecting the destination planes written by each AGA Bob."""

from m19_bob_clear_update_model import Bob, BobFrameModel


def compose_planes(source: int, background: int, write_mask: int) -> int:
    """Copy selected source bits to the same destination plane indices."""
    return (background & ~write_mask) | (source & write_mask)


class BobPlanesModel(BobFrameModel):
    """Apply each slot's plane selection inside the existing frame transaction."""

    def __init__(self, width: int, height: int, depth: int, *, backing_budget: int = 1 << 24):
        super().__init__(width, height, depth, backing_budget=backing_budget)
        self._write_masks: dict[int, int] = {}

    def set_planes(self, slot: int, mask: int) -> bool:
        if (type(slot) is not int or type(mask) is not int or not self.screen_open
                or not 0 <= mask <= 255 or slot not in self.objects
                or not self.objects[slot].active):
            return self._deny('invalid plane selection or inactive Bob')
        self._write_masks[slot] = mask & ((1 << self.depth) - 1)
        self.last_error = ''
        return True

    def _compose_pixel(self, bob: Bob, source: int, background: int) -> int:
        return compose_planes(source, background, self._write_masks.get(bob.number, 255))

    def close(self) -> None:
        super().close()
        self._write_masks.clear()
