#!/usr/bin/env python3
"""M19/P0a R88-only host reference: capture and atomic AGBO bank updates.

DOES NOT alter AMOS banks, patch AP20, access WinUAE, or prove the native
bank-list replacement protocol.  A real 68k port must separately verify
AMOS Bnk.GetAdr/Reserve/Change, Exec ownership and Compiler relocation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from m19_p0a_multi_bob_abk import (
    MAX_IMAGE_ID, MAX_SIDE, empty_bank, make_abk, make_mask,
    no_mask, parse_abk, parse_payload, put_image,
)


@dataclass(frozen=True)
class BackBitmap:
    """Snapshot of the *inactive*, Safe AGA BitMap with physical row stride.

    Bitplanes are independent contiguous byte buffers; plane index 0 carries
    colour bit 0.  The constructor rejects truncated physical rows before a
    single pixel is read, just as the native entry must do.
    """

    width: int
    height: int
    depth: int
    row_bytes: int
    planes: tuple[bytes, ...]
    safe: bool = False

    def validate(self) -> None:
        for name, value in (("width", self.width), ("height", self.height),
                            ("depth", self.depth), ("row_bytes", self.row_bytes)):
            if type(value) is not int:
                raise ValueError(f"invalid {name}")
        if (not 1 <= self.width <= MAX_SIDE or
                not 1 <= self.height <= MAX_SIDE or
                not 1 <= self.depth <= 8 or
                self.width * self.height > 4 * 1024 * 1024):
            raise ValueError("invalid back buffer geometry")
        if (self.row_bytes < 2 * ((self.width + 15) // 16)
                or self.row_bytes > 65534 or self.row_bytes & 1):
            raise ValueError("invalid physical BitMap row stride")
        if type(self.planes) is not tuple or len(self.planes) != self.depth:
            raise ValueError("BitMap depth and plane count differ")
        for plane in self.planes:
            if type(plane) is not bytes or len(plane) != self.row_bytes * self.height:
                raise ValueError("incomplete back buffer plane")
        if self.safe is not True:
            raise ValueError("back buffer Safe notification not acquired")


def read_back_rectangle(bitmap: BackBitmap, x1: int, y1: int,
                        x2: int, y2: int) -> tuple[int, int, bytes]:
    """Extract indexed pixels from a safe planar back buffer, INCLUSIVE XY.

    Never infer the physical byte stride from screen width: it can be larger.
    The output does not include a mask; Make AGA Bob Mask is a separate step.
    """
    bitmap.validate()
    for name, value in (("x1", x1), ("y1", y1), ("x2", x2), ("y2", y2)):
        if type(value) is not int:
            raise ValueError(f"invalid {name}")
    if not (0 <= x1 <= x2 < bitmap.width and
            0 <= y1 <= y2 < bitmap.height):
        raise ValueError("rectangle outside back buffer or inverted")
    width, height = x2 - x1 + 1, y2 - y1 + 1
    out = bytearray(width * height)
    for y in range(y1, y2 + 1):
        physical = y * bitmap.row_bytes
        dest = (y - y1) * width
        for x in range(x1, x2 + 1):
            off = physical + (x >> 3)
            bit = 0x80 >> (x & 7)
            color = 0
            for depth, plane in enumerate(bitmap.planes):
                if plane[off] & bit:
                    color |= 1 << depth
            out[dest + x - x1] = color
    return width, height, bytes(out)


@dataclass(frozen=True)
class _BankRecord:
    """One AMOS DATA bank payload and identity, no extra numbered bank."""
    payload: bytes
    identity: int


class HostBobBanks:
    """Test double of the desired AMOS transaction semantics, NOT an API.

    A new payload is built, parsed and accepted by an optional allocation
    guard *before* the sole numbered bank record is replaced.  Failure keeps
    both original bytes and identity.  Erase/Load invalidate current selection
    until select() is explicitly called again, without caching native pointers.
    """

    def __init__(self, allocate: Callable[[int], bool] | None = None):
        self._banks: dict[int, _BankRecord] = {}
        self._selected: tuple[int, int] | None = None
        self._next_identity = 1
        self._allocate = allocate or (lambda n: True)

    def _identity(self) -> int:
        identity = self._next_identity
        self._next_identity += 1
        return identity

    @staticmethod
    def _number(number: int) -> None:
        if type(number) is not int or not 5 <= number <= 65535:
            raise ValueError("AMOS bank must be 5..65535")

    def _stage(self, payload: bytes) -> None:
        parse_payload(payload)
        if self._allocate(len(payload)) is not True:
            raise MemoryError("private replacement allocation rejected")

    def select(self, number: int) -> None:
        self._number(number)
        old = self._banks.get(number)
        if old is None:
            payload = empty_bank()
            self._stage(payload)
            old = _BankRecord(payload, self._identity())
            self._banks[number] = old
        else:
            # IMPORTANT: never replace or erase an occupied foreign bank.
            parse_payload(old.payload)
        self._selected = (number, old.identity)

    def current_number(self) -> int | None:
        return None if self._selected is None else self._selected[0]

    def payload(self, number: int) -> bytes:
        self._number(number)
        return self._banks[number].payload

    def _selected_record(self) -> tuple[int, _BankRecord]:
        if self._selected is None:
            raise ValueError("Aga Bob Bank must select a live bank first")
        number, identity = self._selected
        bank = self._banks.get(number)
        if bank is None or bank.identity != identity:
            raise ValueError("bank replaced/erased: Aga Bob Bank must reselect")
        parse_payload(bank.payload)
        return number, bank

    def _commit(self, number: int, old: _BankRecord, candidate: bytes) -> None:
        self._stage(candidate)
        # Atomic *model* assignment. Native AMOS linking must still be proven.
        if self._banks.get(number) is not old:
            raise RuntimeError("bank changed during preparation")
        fresh = _BankRecord(candidate, self._identity())
        self._banks[number] = fresh
        self._selected = (number, fresh.identity)

    def capture(self, image_id: int, bitmap: BackBitmap,
                x1: int, y1: int, x2: int, y2: int) -> None:
        if type(image_id) is not int or not 1 <= image_id <= MAX_IMAGE_ID:
            raise ValueError("image id must be 1..4096")
        number, old = self._selected_record()
        width, height, pixels = read_back_rectangle(bitmap, x1, y1, x2, y2)
        candidate = put_image(old.payload, image_id, width, height,
                              bitmap.depth, pixels)
        self._commit(number, old, candidate)

    def mask(self, image_id: int, transparent_index: int) -> None:
        number, old = self._selected_record()
        self._commit(number, old, make_mask(old.payload, image_id, transparent_index))

    def unmask(self, image_id: int) -> None:
        number, old = self._selected_record()
        candidate = no_mask(old.payload, image_id)
        if candidate != old.payload:
            self._commit(number, old, candidate)

    def save(self, number: int) -> bytes:
        return make_abk(number, self.payload(number))

    def erase(self, number: int) -> None:
        self._number(number)
        self._banks.pop(number, None)
        # Never pretend that an earlier selection still addresses live data.
        # _selected_record checks identity or presence on every operation.

    def load(self, file: bytes, *, into: int | None = None) -> None:
        source_number, flags, bank = parse_abk(file)
        number = source_number if into is None else into
        self._number(number)
        self._stage(bank.raw)
        self._banks[number] = _BankRecord(bank.raw, self._identity())
        # Existing selection intentionally NOT rebound to the replacement.

    def inject_foreign_bank_for_test(self, number: int, payload: bytes) -> None:
        """Model a foreign AMOS DATA bank for refusal testing only."""
        self._number(number)
        if type(payload) is not bytes:
            raise ValueError("foreign bank payload must be bytes")
        self._banks[number] = _BankRecord(payload, self._identity())