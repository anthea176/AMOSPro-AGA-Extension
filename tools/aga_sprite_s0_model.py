#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S0 host-only contract for one OS-owned AGA hardware sprite.

No native AmigaOS calls, hardware access, AP20 tokens or display output.
An external adapter MUST prove DMA detachment before channel/image release.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class Phase(Enum):
    EMPTY = auto()
    DATA_READY = auto()
    CHANNEL_OWNED = auto()
    VISIBLE = auto()
    DMA_DETACHED = auto()
    RELEASED = auto()


@dataclass
class SpriteS0:
    phase: Phase = Phase.EMPTY
    screen: int | None = None
    viewport: int | None = None
    image: int | None = None
    channel: int | None = None
    x: int | None = None
    y: int | None = None
    events: list[tuple[str, int]] = field(default_factory=list)

    def _same_owner(self, screen: int, viewport: int) -> bool:
        return screen == self.screen and viewport == self.viewport

    def prepare(self, screen: int, viewport: int, image: int | None) -> bool:
        """Record separately acquired image and the owning private viewport."""
        if self.phase not in (Phase.EMPTY, Phase.RELEASED):
            return False
        if not all(isinstance(v, int) and v > 0 for v in (screen, viewport)):
            return False
        if not isinstance(image, int) or image <= 0:
            return False  # OOM or missing image: no state/resource changed
        self.screen, self.viewport, self.image = screen, viewport, image
        self.channel, self.x, self.y = None, None, None
        self.phase = Phase.DATA_READY
        return True

    def acquire(self, granted_channel: int) -> bool:
        """Record what GetSprite(-1) returned; never select a channel here."""
        if self.phase != Phase.DATA_READY:
            return False
        if not isinstance(granted_channel, int) or not 0 <= granted_channel <= 7:
            return False  # -1 means none available; no FreeSprite permitted
        self.channel = granted_channel
        self.phase = Phase.CHANNEL_OWNED
        return True

    def present(self, screen: int, viewport: int, x: int, y: int) -> bool:
        if not self._same_owner(screen, viewport):
            return False
        if self.phase not in (Phase.CHANNEL_OWNED, Phase.VISIBLE):
            return False
        if not isinstance(x, int) or not isinstance(y, int):
            return False
        # Software state only: real adapter validates screen-space coordinates.
        self.x, self.y = x, y
        self.phase = Phase.VISIBLE
        return True

    def confirm_dma_detached(self, screen: int, viewport: int) -> bool:
        """Record an EXTERNALLY proven DMA detach, not perform it.

        Caller MUST NOT infer this simply from one VBL, Bob Swap or
        an unverified ChangeSprite(NULL) call.
        """
        if not self._same_owner(screen, viewport):
            return False
        if self.phase not in (Phase.CHANNEL_OWNED, Phase.VISIBLE):
            return False
        self.phase = Phase.DMA_DETACHED
        return True

    def release(self, screen: int, viewport: int) -> bool:
        """Produce ordered cleanup obligations; no actual FreeSprite call."""
        if self.phase == Phase.RELEASED:
            return True  # idempotence, no double free
        if not self._same_owner(screen, viewport):
            return False
        if self.phase not in (Phase.DATA_READY, Phase.DMA_DETACHED):
            return False
        if self.channel is not None:
            self.events.append(("free_owned_channel", self.channel))
        if self.image is not None:
            self.events.append(("free_owned_image", self.image))
        self.phase = Phase.RELEASED
        self.screen = self.viewport = self.image = self.channel = None
        self.x = self.y = None
        return True

    def can_close_screen(self, screen: int) -> bool:
        return self.phase in (Phase.EMPTY, Phase.RELEASED) or self.screen != screen
