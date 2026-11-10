"""Pure Python M7 Copper staging contract — NOT an Amiga Copper implementation.

Only validates the planned R16 input grammar. No graphics.library calls,
hardware writes, executable 68000 routines or .Lib files are generated here.
The future builder may reuse this safety policy, but runtime needs independent
68000/WinUAE checks.
"""
from dataclasses import dataclass


MAX_USER_INSTRUCTIONS = 64
WAIT_MAX_V = 255
WAIT_MAX_H = 222
COLOR_FIRST = 0x180
COLOR_LAST = 0x1BE


class CopperInputError(ValueError):
    pass


@dataclass(frozen=True)
class Wait:
    v: int
    h: int


@dataclass(frozen=True)
class Move:
    register: int
    value: int


class CopperProgram:
    """Conservative, staged user-Copper API contract; no OS side effects."""

    def __init__(self):
        self._armed = False
        self.clear()

    def clear(self):
        if self._armed:
            raise CopperInputError("Copper Off required before clearing active plan")
        self._steps = []
        self._ended = False
        self._last_wait = None
        return 1

    @property
    def instructions(self):
        return tuple(self._steps)

    def _can_append(self):
        if self._ended or self._armed:
            raise CopperInputError("program is sealed or armed")
        # Reserve one instruction for CEND at installation.
        if len(self._steps) >= MAX_USER_INSTRUCTIONS - 1:
            raise CopperInputError("copper instruction budget exceeded")

    @staticmethod
    def _word(value, name):
        if type(value) is not int:
            raise CopperInputError(f"{name} must be an integer")
        return value

    def wait(self, v, h):
        self._can_append()
        v = self._word(v, "vertical")
        h = self._word(h, "horizontal")
        if not (0 <= v <= WAIT_MAX_V and 0 <= h <= WAIT_MAX_H):
            raise CopperInputError("CWAIT coordinates outside documented bounds")
        if self._last_wait is not None and (v, h) <= self._last_wait:
            raise CopperInputError("CWAIT positions must strictly advance")
        self._steps.append(Wait(v, h))
        self._last_wait = v, h
        return 1

    def move(self, register, value):
        self._can_append()
        register = self._word(register, "register")
        value = self._word(value, "value")
        # M7 first raster gate: COLOR00..COLOR31 only. Never let AMOS
        # write COPxLC, bitplane pointers, DMA or BPLCON3 by arbitrary index.
        if not (COLOR_FIRST <= register <= COLOR_LAST and
                (register - COLOR_FIRST) % 2 == 0):
            raise CopperInputError("only COLOR00..COLOR31 are permitted")
        # Initial R16/OCS-safe 12-bit palette subset; no AGA bank changes.
        if not 0 <= value <= 0x0FFF:
            raise CopperInputError("RGB4 color must fit 12 bits")
        self._steps.append(Move(register, value))
        return 1

    def end(self):
        if self._ended or self._armed:
            raise CopperInputError("CEND already applied")
        if not self._steps:
            raise CopperInputError("refuse to install an empty Copper list")
        if len(self._steps) >= MAX_USER_INSTRUCTIONS:
            raise CopperInputError("CEND exceeds the instruction budget")
        self._ended = True
        return 1

    def on(self):
        # A future implementation must additionally own the actual UCopList,
        # attach via ViewPort.UCopIns and rebuild via Intuition, atomically.
        if not self._ended or self._armed:
            raise CopperInputError("CEND is required before Copper On")
        self._armed = True
        return 1

    def off(self):
        # Contract only: actual detach/free order requires native design.
        self._armed = False
        return 1
