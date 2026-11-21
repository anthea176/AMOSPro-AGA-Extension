#!/usr/bin/env python3
"""Host reference for opt-in Bob updates at the explicit AGA Swap boundary."""

from m19_bob_clear_update_model import CLEAN, DIRTY
from m19_p2c_bob_planes_model import BobPlanesModel


class BobAutoUpdateModel(BobPlanesModel):
    """Prepare a page at most once before it is presented."""

    def __init__(self, width: int, height: int, depth: int,
                 *, backing_budget: int = 1 << 24):
        super().__init__(width, height, depth, backing_budget=backing_budget)
        self.auto_update = False

    def set_auto_update(self, enabled: bool) -> bool:
        if type(enabled) is not bool or not self.screen_open or self.status != CLEAN:
            return self._deny('screen closed, invalid mode or frame not CLEAN')
        self.auto_update = enabled
        self.last_error = ''
        return True

    def swap(self, *, display_ready: bool = True,
             inject_fault_after_pixels: int | None = None) -> bool:
        if not self.screen_open or self.status == DIRTY:
            return super().swap()

        if self.auto_update and self.status == CLEAN and self.objects:
            if not self.update(inject_fault_after_pixels=inject_fault_after_pixels):
                return False

        if not display_ready:
            return self._deny('display swap refused; keep the prepared page')
        return super().swap()

    def close(self) -> None:
        super().close()
        self.auto_update = False
