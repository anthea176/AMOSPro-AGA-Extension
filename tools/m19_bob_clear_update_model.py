#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0 Clear/Update: pixel-exact, source-only reference model.

No AMOS token, native 68k code or library is emitted here. The backing-store
algorithm must be proved independently before mapping it to the real AGA
Safe/Disp, bitplanes and managed Chip/Fast allocations.

Contract:
  Clear: on the current inactive physical page, restore the complete
         background snapshot taken immediately before its previous Draw.
         The other page, active Bob objects and the front page are untouched.
  Update: preflight all active images/owners, Clear this page if needed,
          capture its clean background, then paint all active Bobs in ID order.
          Success arms READY; failure latches DIRTY; NEVER performs Swap.
  Swap: explicitly requested by the caller; DIRTY forbids it.

A full-screen snapshot per physical page is a correctness-first baseline,
NOT a promise of acceptable 68020/Chip performance. See the design report.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

CLEAN, DIRTY, READY = 0, 1, 2
MAX_BOBS = 64


@dataclass(frozen=True)
class BobImage:
    pixels: tuple[tuple[int, ...], ...]
    depth: int
    mask: tuple[tuple[bool, ...], ...] | None = None

    def __post_init__(self):
        height = len(self.pixels)
        width = len(self.pixels[0]) if height else 0
        if not 1 <= self.depth <= 8 or not height or not width:
            raise ValueError('empty image or depth outside 1..8')
        if any(len(row) != width or any(not 0 <= x < 1 << self.depth for x in row)
               for row in self.pixels):
            raise ValueError('invalid pixels, stride or palette index')
        if self.mask is not None and (
            len(self.mask) != height or
            any(len(row) != width for row in self.mask)
        ):
            raise ValueError('mask dimensions differ from image')

    @property
    def width(self) -> int:
        return len(self.pixels[0])

    @property
    def height(self) -> int:
        return len(self.pixels)


@dataclass(frozen=True)
class Bank:
    revision: int
    images: dict[int, BobImage]


@dataclass(frozen=True)
class Bob:
    number: int
    bank: int
    revision: int
    image: int
    x: int
    y: int
    active: bool = True


class BobFrameModel:
    """Deterministic functional oracle, NOT a native implementation."""

    def __init__(self, width: int, height: int, depth: int,
                 *, backing_budget: int = 1 << 24):
        if not 1 <= depth <= 8 or not 1 <= width <= 4096 or not 1 <= height <= 4096:
            raise ValueError('invalid screen geometry')
        self.width, self.height, self.depth = width, height, depth
        self.backing_budget = backing_budget
        self.front = 0
        self.pages = [[[0] * width for _ in range(height)] for _ in range(2)]
        self.saved: list[list[list[int]] | None] = [None, None]
        self.banks: dict[int, Bank] = {}
        self.objects: dict[int, Bob] = {}
        self.status = CLEAN
        self.screen_open = True
        self.swaps = 0
        self.draw_calls = 0
        self.last_error = ''
        self._revision = 0

    @property
    def back(self) -> int:
        return 1 - self.front

    @property
    def backing_bytes_per_page(self) -> int:
        # Planar pitch is 16-pixel word-aligned, not width bytes.
        return 2 * ((self.width + 15) // 16) * self.height * self.depth

    @property
    def backing_reserved(self) -> int:
        return sum(self.backing_bytes_per_page for p in self.saved if p is not None)

    @staticmethod
    def _copy(page: list[list[int]]) -> list[list[int]]:
        return [row.copy() for row in page]

    def _deny(self, why: str, *, dirty: bool = False) -> bool:
        self.last_error = why
        if dirty:
            self.status = DIRTY
        return False

    def install_bank(self, n: int, images: dict[int, BobImage]) -> bool:
        if not 5 <= n <= 65535 or not images or any(not 1 <= i <= 4096 for i in images):
            return self._deny('invalid bank or image ID')
        self._revision += 1
        self.banks[n] = Bank(self._revision, dict(images))
        return True

    def erase_bank(self, n: int) -> None:
        self.banks.pop(n, None)

    def put(self, n: int, bank: int, image: int, x: int, y: int) -> bool:
        source = self.banks.get(bank)
        if (not self.screen_open or not 1 <= n <= MAX_BOBS or source is None
                or image not in source.images or not -32768 <= x <= 32767
                or not -32768 <= y <= 32767):
            return self._deny('invalid Bob or missing source')
        self.objects[n] = Bob(n, bank, source.revision, image, x, y)
        return True

    def off(self, n: int) -> bool:
        previous = self.objects.get(n)
        if previous is None or not self.screen_open:
            return self._deny('Bob does not exist')
        self.objects[n] = replace(previous, active=False)
        return True

    def edit_background(self, x: int, y: int, color: int) -> bool:
        # Refuse painting scenery over the old Bobs. The caller must Clear
        # the current page first, draw new scenery, then call Update.
        if (not self.screen_open or self.status != CLEAN
                or self.saved[self.back] is not None):
            return self._deny('Clear required before changing background')
        if not 0 <= x < self.width or not 0 <= y < self.height or not 0 <= color < 1 << self.depth:
            return self._deny('background coordinate/color outside screen')
        self.pages[self.back][y][x] = color
        return True

    def clear(self) -> bool:
        if not self.screen_open or self.status == READY:
            return self._deny('screen closed or frame READY (Swap required)')
        old = self.saved[self.back]
        if old is None:
            if self.status == DIRTY:
                return self._deny('no valid snapshot; close screen to recover')
            self.last_error = ''
            return True
        self.pages[self.back] = self._copy(old)
        self.saved[self.back] = None
        self.status = CLEAN
        self.last_error = ''
        return True

    def _preflight(self) -> list[tuple[Bob, BobImage]] | None:
        result = []
        for n in sorted(self.objects):
            obj = self.objects[n]
            if not obj.active:
                continue
            bank = self.banks.get(obj.bank)
            if bank is None or bank.revision != obj.revision:
                return None
            image = bank.images.get(obj.image)
            if image is None or image.depth != self.depth:
                return None
            result.append((obj, image))
        return result

    def update(self, *, inject_fault_after_pixels: int | None = None) -> bool:
        if not self.screen_open or self.status != CLEAN:
            return self._deny('screen closed or frame not CLEAN')
        draw_list = self._preflight()
        if draw_list is None:
            return self._deny('stale bank, invalid image or depth', dirty=True)
        old = self.saved[self.back]
        if old is None and self.backing_reserved + self.backing_bytes_per_page > self.backing_budget:
            return self._deny('no backing memory: reject before painting', dirty=True)
        # Explicit earlier Clear removes the saved snapshot, so background
        # edits made by the caller between Clear and Update survive.
        if old is not None:
            if not self.clear():
                return False
        self.saved[self.back] = self._copy(self.pages[self.back])
        self.status = DIRTY
        self.draw_calls += 1
        painted = 0
        for bob, image in draw_list:
            for sy in range(image.height):
                y = bob.y + sy
                if y < 0 or y >= self.height:
                    continue
                for sx in range(image.width):
                    x = bob.x + sx
                    if x < 0 or x >= self.width:
                        continue
                    if image.mask is not None and not image.mask[sy][sx]:
                        continue
                    if inject_fault_after_pixels is not None and painted >= inject_fault_after_pixels:
                        return self._deny('injected mid-paint fault', dirty=True)
                    self.pages[self.back][y][x] = image.pixels[sy][sx]
                    painted += 1
        self.status = READY
        self.last_error = ''
        return True

    def swap(self) -> bool:
        if not self.screen_open or self.status == DIRTY:
            return self._deny('screen closed or frame DIRTY')
        self.front = 1 - self.front
        self.swaps += 1
        self.status = CLEAN
        self.last_error = ''
        return True

    def close(self) -> None:
        self.saved = [None, None]
        self.objects.clear()
        self.status = CLEAN
        self.screen_open = False
        self.last_error = ''

    def reopen(self) -> None:
        if self.screen_open:
            raise ValueError('close first')
        self.pages = [[[0] * self.width for _ in range(self.height)] for _ in range(2)]
        self.saved = [None, None]
        self.front = 0
        self.status = CLEAN
        self.screen_open = True


if __name__ == '__main__':
    print('M19 P0 Bob Clear/Update: source-only planar reference model; NO native Lib/AP20 tokens')
