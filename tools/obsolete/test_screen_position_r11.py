#!/usr/bin/env python3
"""Historical CPU diagnostic of rejected R11 Open entry (archive only).

Tests screen foregrounding and positive TopEdge correction on PAL retry,
including D0 Screen* preservation across destructive mock AmigaOS calls.
No runtime PASS under WinUAE or real Amiga is implied by this test.
"""
from test_ntsc_pal_r10 import OpenMachine, NTSC, PAL, FALLOUT
from test_m5_generic import INTUI, SCREEN, STATE
from build_screen_position_r11 import build, BASE, DEST, ARCHIVE, R11_SHA256
from ap20_utils import split, digest
from audit_ap20 import parse, inspect as audit


def signed16(value):
    value &= 0xffff
    return value if value < 0x8000 else value - 0x10000


class PositionMachine(OpenMachine):
    def __init__(self, raw, accepted, initial_top=0, available=None, window_ok=True):
        super().__init__(raw, accepted, available=available, window_ok=window_ok)
        self.initial_top = initial_top
        self.putw(SCREEN + 10, initial_top & 0xffff)
        self.front_calls = 0
        self.moves = []
        for lvo in (-252, -162):
            self.uc.mem_write(INTUI + lvo, b"\x4e\x75")

    def os_call(self, uc, address, size, user):
        if address == INTUI - 252:  # ScreenToFront(Screen*)
            assert self.a(0) == SCREEN
            self.front_calls += 1
            self.return_from_os(0)  # clobber D0,D1,A0,A1
        elif address == INTUI - 162:  # MoveScreen(Screen*, WORD dx, WORD dy)
            assert self.a(0) == SCREEN
            dx, dy = signed16(self.d(0)), signed16(self.d(1))
            assert dx == 0
            assert dy == -self.initial_top and dy < 0
            self.moves.append((dx, dy))
            self.putw(SCREEN + 10, (self.initial_top + dy) & 0xffff)
            self.return_from_os(0)
        else:
            super().os_call(uc, address, size, user)


def run_case(raw, requested, accepted, top, expected, front, moves,
             width=736, height=482, available=None, window_ok=True):
    m = PositionMachine(raw, accepted=accepted, initial_top=top,
                        available=available, window_ok=window_ok)
    result = m.execute(6, open_args=(width, height, 16, requested))
    assert result == expected, (requested, result)
    assert m.front_calls == front, (requested, m.front_calls, front)
    assert m.moves == moves, (requested, m.moves, moves)
    if expected == 1:
        assert m.get(STATE + 24) == requested, "logical ModeID changed"
        assert m.windows == [(width, height, SCREEN)]
        assert m.get(STATE + 12) == width and m.get(STATE + 16) == height
    else:
        assert m.get(STATE) == 0, "state not cleaned on failure"
    return m


def main():
    raw, manifest = build()
    original = BASE.read_bytes()
    assert raw == ARCHIVE.read_bytes()
    from build_screen_position_r11 import ROOT
    assert (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes() == BASE.read_bytes(), "Protected R10 changed"
    assert digest(raw) == R11_SHA256
    assert not audit(parse(raw))["issues"]
    t0, seg0, _ = split(original)
    t1, seg1, _ = split(raw)
    assert t0 == t1
    assert [i for i in range(19) if seg0[i] != seg1[i]] == [6]
    assert all(seg0[i] == seg1[i] for i in range(19) if i != 6)
    assert seg0[6][722:726].hex() == "4eaefd9c"
    assert seg1[6][722:726].hex() == "61000008"
    assert seg1[6][726:732] == seg0[6][726:732]
    assert seg1[6][-4:] == b"GetP"

    # Jeff only: NTSC opening fails, PAL succeeds and must be positioned.
    for width, height in ((736, 482), (724, 482), (640, 400)):
        m = run_case(raw, NTSC, {PAL}, 760, 1, 1, [(0, -760)],
                     width=width, height=height)
        assert [x[0x80000032] for x in m.attempted] == [NTSC, PAL]
        assert m.getw(SCREEN + 10) == 0
        assert m.mode_queries == [PAL]

    # Foreground even when already at y=0; no gratuitous MoveScreen.
    run_case(raw, NTSC, {PAL}, 0, 1, 1, [], width=736, height=482)

    # Legitimate negative overscan TopEdge is not overridden.
    m = run_case(raw, NTSC, {PAL}, -12, 1, 1, [])
    assert signed16(m.getw(SCREEN + 10)) == -12

    # Native modes retain R10 behavior: never touch ScreenToFront/MoveScreen.
    run_case(raw, FALLOUT, {FALLOUT}, 760, 1, 0, [],
             width=640, height=512)
    run_case(raw, NTSC, {NTSC}, 760, 1, 0, [])

    # Unavailable fallback: fail cleanly without presentation calls.
    run_case(raw, NTSC, set(), 760, 0, 0, [])
    run_case(raw, NTSC, set(), 760, 0, 0, [], available={PAL})
    run_case(raw, FALLOUT, set(), 760, 0, 0, [],
             width=640, height=512)

    # PAL opens but OpenWindow fails afterward: previous cleanup unchanged.
    m = run_case(raw, NTSC, {PAL}, 760, 0, 1, [(0, -760)], window_ok=False)
    assert m.closed_screens == 1

    print("R11 PASS Unicorn: Jeff positioned, ScreenToFront, MoveScreen,"
          " original pointer kept, native modes unchanged, cleanup OK")


if __name__ == "__main__":
    main()
