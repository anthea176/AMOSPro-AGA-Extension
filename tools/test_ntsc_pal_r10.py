#!/usr/bin/env python3
"""68000 CPU/ABI tests of R10's *actual* Open AP20 code.

The OS model deliberately clobbers D0/D1/A0/A1. This validates the
post-failure mode retry and the original request in the state. It does
not imply a WinUAE, Amiga Compiler or native hardware runtime PASS.
"""
import struct

from unicorn.m68k_const import UC_M68K_REG_PC
from test_m5_generic import Machine, DR, AR, GFX, INTUI, STATE, SCREEN
from audit_ap20 import parse, inspect as audit
from ap20_utils import split, digest
from build_ntsc_pal_r10 import build, BASE, ARCHIVE, DEST, R10_SHA256

NTSC = 0x00019004
PAL = 0x00029004
FALLOUT = 0x00029000
WINDOW = 0x57000


class OpenMachine(Machine):
    def __init__(self, raw, accepted, available=None, window_ok=True):
        super().__init__(raw, None)
        self.accepted = set(accepted)
        self.available = set(accepted if available is None else available)
        self.window_ok = window_ok
        self.attempted = []
        self.mode_queries = []
        self.windows = []
        self.closed_screens = 0
        for base, lvos in ((INTUI, (-204, -66)), (GFX, (-798,))):
            for lvo in lvos:
                self.uc.mem_write(base + lvo, b"\x4e\x75")

    def return_from_os(self, result):
        uc = self.uc
        uc.reg_write(DR[0], result)
        uc.reg_write(DR[1], 0xDEADBEEF)
        uc.reg_write(AR[0], 0xBAD000)
        uc.reg_write(AR[1], 0xBAD100)
        pc = self.get(self.a(7))
        uc.reg_write(AR[7], self.a(7) + 4)
        uc.reg_write(UC_M68K_REG_PC, pc)

    def os_call(self, uc, address, size, user):
        if address == INTUI - 612:
            ptr = self.a(1)
            tags = {}
            for _ in range(16):
                tag = self.get(ptr)
                if tag == 0:
                    break
                tags[tag] = self.get(ptr + 4)
                ptr += 8
            else:
                raise AssertionError("Unterminated SA_* list")
            assert tags[0x8000003B] == 1  # SA_AutoScroll
            assert tags[0x80000039] == 1  # SA_FullPalette
            assert tags[0x80000025] == 4  # depth 4 in these fixtures
            self.attempted.append(dict(tags))
            self.return_from_os(SCREEN if tags[0x80000032] in self.accepted else 0)
        elif address == GFX - 798:
            self.mode_queries.append(self.d(0))
            self.return_from_os(0 if self.d(0) in self.available else 1)
        elif address == INTUI - 204:
            ptr = self.a(0)
            width, height = struct.unpack(">HH", self.uc.mem_read(ptr + 4, 4))
            screen = self.get(ptr + 30)
            self.windows.append((width, height, screen))
            assert screen == SCREEN
            self.return_from_os(WINDOW if self.window_ok else 0)
        elif address == INTUI - 66:
            assert self.a(0) == SCREEN
            self.closed_screens += 1
            self.return_from_os(1)
        else:
            super().os_call(uc, address, size, user)


def case(raw, requested, available, expected_modes, result, width=736, height=482,
         window_ok=True, mode_availability=None):
    m = OpenMachine(raw, accepted=available, available=mode_availability,
                    window_ok=window_ok)
    out = m.execute(6, open_args=(width, height, 16, requested))
    assert out == result, (hex(requested), available, out)
    attempts = [x[0x80000032] for x in m.attempted]
    assert attempts == expected_modes, [hex(x) for x in attempts]
    for tags in m.attempted:
        assert tags[0x80000023] == width, "Width modified"
        assert tags[0x80000024] == height, "Height modified"
        assert tags[0x80000025] == 4, "Depth modified"
    if result == 1:
        assert m.get(STATE + 24) == requested, "Logical CAMG no longer matches ILBM"
        assert m.get(STATE + 12) == width and m.get(STATE + 16) == height
        assert m.windows == [(width, height, SCREEN)]
    else:
        assert m.get(STATE) == 0
        assert not m.owned and m.open_libraries == 0
    return m


def main():
    output, manifest = build()
    old = BASE.read_bytes()
    assert output == ARCHIVE.read_bytes()
    from build_ntsc_pal_r10 import ROOT
    assert (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes() == output
    assert digest(output) == R10_SHA256
    assert audit(parse(output))["issues"] == []
    token0, seg0, _ = split(old)
    token1, seg1, _ = split(output)
    assert token0 == token1
    assert [i for i in range(19) if seg0[i] != seg1[i]] == [6]
    assert all(seg0[i] == seg1[i] for i in range(19) if i != 6)
    assert seg0[6][0x116:0x11A].hex() == "4eaefd9c"
    assert seg1[6][0x116:0x11A].hex() == "61000174"
    assert seg1[6][-4:] == b"GetP"

    # Original modes must never be changed when they work.
    m = case(output, FALLOUT, {FALLOUT}, [FALLOUT], 1, 640, 512)
    assert m.mode_queries == []
    m = case(output, NTSC, {NTSC}, [NTSC], 1)
    assert m.mode_queries == []

    # Jeff, even at 736 pixels, may fall back to PAL without cropping.
    for width, height in ((736, 482), (724, 482), (640, 400)):
        m = case(output, NTSC, {PAL}, [NTSC, PAL], 1, width, height)
        assert m.mode_queries == [PAL]

    # No PAL monitor -> no second OpenScreenTagList, return 0 with cleanup.
    m = case(output, NTSC, set(), [NTSC], 0)
    assert m.mode_queries == [PAL]

    # PAL mode exists but allocation fails -> second call returns NULL.
    m = case(output, NTSC, set(), [NTSC, PAL], 0, mode_availability={PAL})
    assert m.mode_queries == [PAL]

    # No fallback on native PAL/open errors or unrelated IDs.
    m = case(output, FALLOUT, set(), [FALLOUT], 0, 640, 512)
    assert m.mode_queries == []
    m = case(output, 0, set(), [0], 0, 320, 200)
    assert m.mode_queries == []

    # OpenWindow failure must still close Screen and clean up.
    m = case(output, NTSC, {PAL}, [NTSC, PAL], 0, window_ok=False)
    assert m.closed_screens == 1

    print("R10 PASS Unicorn: PAL/NTSC, Jeff 736/724/640, no truncation,"
          " no OS register assumption, fail-closed and window cleanup")


if __name__ == "__main__":
    main()
