#!/usr/bin/env python3
"""R12: Unicorn CPU 68000 regression enforcing A0=NULL at OpenScreenTagList."""
from test_ntsc_pal_r10 import OpenMachine, NTSC, PAL, FALLOUT
from test_m5_generic import INTUI, SCREEN, STATE
from build_newscreen_a0_r12 import build, BASE, ARCHIVE, DEST, LAST_GOOD, LAST_GOOD_SHA256, R12_SHA256
from ap20_utils import split, digest
from audit_ap20 import parse, inspect as audit


class StrictOpenMachine(OpenMachine):
    def __init__(self, raw, accepted, available=None, window_ok=True):
        super().__init__(raw, accepted, available=available, window_ok=window_ok)
        self.a0_calls = []

    def os_call(self, uc, address, size, user):
        if address == INTUI - 612:
            a0 = self.a(0)
            self.a0_calls.append(a0)
            assert a0 == 0, "OpenScreenTagList: NewScreen A0 must be NULL: "+hex(a0)
        super().os_call(uc, address, size, user)


def case(data, mode, accepted, expected_modes, good,
         w=736, h=482, available=None, window_ok=True):
    m = StrictOpenMachine(data, accepted, available=available,
                          window_ok=window_ok)
    result = m.execute(6, open_args=(w, h, 16, mode))
    assert result == good, (mode, result)
    actual_modes = [tags[0x80000032] for tags in m.attempted]
    assert actual_modes == expected_modes
    assert m.a0_calls == [0] * len(expected_modes)
    for tags in m.attempted:
        assert tags[0x80000023] == w and tags[0x80000024] == h
        assert tags[0x80000025] == 4 and tags[0x8000003B] == 1
    if good:
        assert m.get(STATE+24) == mode, "Original logical CAMG lost"
        assert m.get(STATE+12) == w and m.get(STATE+16) == h
        assert m.windows == [(w,h,SCREEN)]
    else:
        assert m.get(STATE) == 0
        assert not m.owned and m.open_libraries == 0
    return m


def main():
    data, report = build()
    r10 = BASE.read_bytes()
    assert data == ARCHIVE.read_bytes() == DEST.read_bytes()
    # R10 is the frozen source archive. LAST_GOOD tracks latest WinUAE-PASS (R33).
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    assert digest(data) == R12_SHA256
    assert not audit(parse(data))["issues"]
    t0,p0,_ = split(r10)
    t1,p1,_ = split(data)
    assert t0 == t1
    assert [i for i in range(19) if p0[i] != p1[i]] == [6]
    assert all(p0[i] == p1[i] for i in range(19) if i != 6)
    assert p0[6][0x110:0x112] == bytes.fromhex("91c8")
    assert p1[6][652+70:652+76] == bytes.fromhex("91c84eaefd9c")
    for w,h in ((736,482),(724,482),(640,400)):
        m = case(data,NTSC,{PAL},[NTSC,PAL],1,w,h)
        assert m.mode_queries == [PAL]
    case(data,FALLOUT,{FALLOUT},[FALLOUT],1,640,512)
    case(data,NTSC,{NTSC},[NTSC],1)
    case(data,NTSC,set(),[NTSC],0)
    case(data,NTSC,set(),[NTSC,PAL],0,available={PAL})
    case(data,FALLOUT,set(),[FALLOUT],0,640,512)
    case(data,0,set(),[0],0,320,200)
    m = case(data,NTSC,{PAL},[NTSC,PAL],0,window_ok=False)
    assert m.closed_screens == 1
    print("R12 PASS Unicorn: NewScreen A0=NULL on BOTH calls, "
          "Jeff/PAL/NTSC paths, sizes and cleanup")


if __name__ == "__main__":
    main()
