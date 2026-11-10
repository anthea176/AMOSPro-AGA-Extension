#!/usr/bin/env python3
"""M8 R21 Gate A: test exact NewWindow RMBTRAP flag on native 68000.

Traces the actual R21 Aga Screen Open through Unicorn OS stubs to
OpenWindow(), verifies the Flags ULONG at NewWindow +14, and ensures
all R20 button routines remain unchanged. Not a WinUAE display test.
"""
from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from build_m8_rmbtrap_r21 import (
    build, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256, R21_SHA256,
    ENTRY_SCREEN_OPEN, SCREEN_OPEN_FLAGS_OFFSET, OLD_OPCODE, NEW_OPCODE,
    NEW_FLAGS, RMBTRAP_FLAG
)
from test_ntsc_pal_r10 import OpenMachine, NTSC, PAL, FALLOUT, INTUI
from test_m8_mouse_buttons_r20 import ButtonMachine


class RMBTrapOpenMachine(OpenMachine):
    def __init__(self, raw, accepted, available=None, window_ok=True):
        super().__init__(raw, accepted, available=available, window_ok=window_ok)
        self.flags_at_open = []

    def os_call(self, uc, address, size, user):
        if address == INTUI - 204:
            new_window = self.a(0)
            flags = self.get(new_window + 14)
            self.flags_at_open.append(flags)
            assert flags == NEW_FLAGS, hex(flags)
            assert (flags & RMBTRAP_FLAG) != 0
        super().os_call(uc, address, size, user)


def run():
    lib, info = build()
    assert lib == build()[0]
    assert digest(lib) == R21_SHA256
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    token_before, parts_before, _ = split(BASE.read_bytes())
    token_after, parts_after, title_after = split(lib)
    assert token_before == token_after
    assert len(parts_before) == len(parts_after) == 31
    assert [i for i in range(31) if parts_before[i] != parts_after[i]] == [6]
    old = parts_before[ENTRY_SCREEN_OPEN]
    new = parts_after[ENTRY_SCREEN_OPEN]
    assert old[SCREEN_OPEN_FLAGS_OFFSET:SCREEN_OPEN_FLAGS_OFFSET+8] == OLD_OPCODE
    assert new[SCREEN_OPEN_FLAGS_OFFSET:SCREEN_OPEN_FLAGS_OFFSET+8] == NEW_OPCODE
    assert len(old) == len(new) and sum(a != b for a,b in zip(old,new)) == 1
    assert parts_before[30] == parts_after[30], "Mouse Buttons R20 changed"
    assert parts_before[28:31] == parts_after[28:31], "Mouse X/Y/Buttons changed"
    assert title_after.startswith(b"AMOSPro AGA M8 Mouse RMBTrap R21 0.8.5")
    assert inspect(parse(lib))["issues"] == []

    cases = 0
    for width, height, mode, accepted, expected_result, window_ok in (
        (320, 256, NTSC, {NTSC}, 1, True),
        (640, 400, NTSC, {NTSC}, 1, True),
        (736, 482, NTSC, {PAL}, 1, True),
        (320, 256, FALLOUT, {FALLOUT}, 1, True),
        (320, 256, NTSC, {NTSC}, 0, False),
    ):
        m = RMBTrapOpenMachine(lib, accepted=accepted, window_ok=window_ok)
        result = m.execute(6, open_args=(width, height, 16, mode))
        assert result == expected_result, (width, height, result)
        assert m.flags_at_open == [NEW_FLAGS], m.flags_at_open
        if result:
            assert m.windows == [(width, height, 0x56000)]
        else:
            assert m.closed_screens == 1
        cases += 1

    for qualifier, expected in ((0,0),(0x4000,1),(0x2000,2),
                                (0x1000,4),(0x6000,3),(0x7000,7)):
        m = ButtonMachine(lib, qualifier=qualifier)
        assert m.buttons() == expected
        assert m.calls == ['open','peek','close']
        cases += 1

    print("M8 R21 Gate A CPU PASS:", cases,
          "native cases: OpenWindow() Flags=0x00031900 with RMBTRAP,"
          " bounds/fallback/cleanup and unchanged R20 button masks")
    print("R21 sha256", info['sha256'])
    print("Gate B AMOS WinUAE, Compiler and real hardware: NOT TESTED")


if __name__ == "__main__":
    run()
