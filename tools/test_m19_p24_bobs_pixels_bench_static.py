#!/usr/bin/env python3
"""M19 P2.4 archived UNVALIDATED design model: 1x1 pixel oracle.

This does NOT execute AMOS or WinUAE. It checks that the sole new active
ASC encodes valid source/descriptor layouts and expected pixel values
before the author runs the real Runtime and Compiler gates.
"""
from __future__ import annotations

from hashlib import sha1, sha256
from pathlib import Path
from struct import unpack_from
import re

from m16_agapic import pack_image

ROOT = Path(__file__).resolve().parents[1]
ASC_NAME = "M19_P24_BOBS_PIXELS_BENCH_01_UNVALIDATED.asc"
LEGACY_GIT_SHA = "19ad2044252783454f4082c118e53b34a6b83478"
R84_SHA = "46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d"
R87_SHA = "02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302"
from build_m19_p25_no_probe import build as build_r87


def git_blob_sha(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def decode_single_pixel_v1(data: bytes) -> int:
    """The AMOS source CHECK_PIXEL performs the exact same bit extraction."""
    assert data[:6] == b"AGAPIC"
    assert (unpack_from(">H", data, 6)[0],
            unpack_from(">H", data, 12)[0],
            unpack_from(">H", data, 14)[0],
            unpack_from(">H", data, 16)[0]) == (1, 1, 1, 8)
    stream = unpack_from(">I", data, 24)[0]
    end = unpack_from(">I", data, 28)[0]
    assert stream >= 40 and stream + 17 == end == len(data)
    assert data[stream] == 0  # one literal RLE group
    return sum((1 << bit) for bit in range(8)
               if data[stream + 1 + 2 * bit] & 128)


def pixel_at(objects, x: int, y: int) -> int:
    value = 1  # background index
    for kind, bank, ox, oy, mode in objects:
        w = h = 40 if kind == 1 else 16
        sx, sy = x - ox, y - oy
        if not (0 <= sx < w and 0 <= sy < h):
            continue
        if kind == 1:
            assert bank in (12, 13)
            source = (3 if bank == 12 else 4) if 8 <= sx < 32 and 8 <= sy < 32 else 0
        else:
            assert kind == 2 and bank == 11
            source = 5 if 0 < sx < 15 and 0 < sy < 15 else 0
        if mode == 0 or source:
            value = source
    return value


def check_model():
    v1 = (1, 12, 100, 100, 1)
    icon = (2, 11, 105, 105, 1)
    v2 = (1, 13, 108, 108, 1)
    cases = [
        ("z", [v1, icon, v2],
         ((116, 116, 4), (110, 110, 5),
          (100, 100, 1), (130, 130, 4))),
        ("v2-opaque", [v1, icon, (1, 13, 108, 108, 0)],
         ((110, 110, 0), (116, 116, 4))),
        ("ficon-opaque", [v1, (2, 11, 105, 105, 0), v2],
         ((105, 105, 0), (106, 106, 5))),
        ("z-inverse", [v1, v2, icon],
         ((116, 116, 5), (110, 110, 5))),
        ("clip-negative", [v1, (2, 11, -8, -8, 1), v2],
         ((0, 0, 5), (7, 7, 1))),
        ("clip-right-bottom", [v1, (2, 11, 315, 250, 1), v2],
         ((319, 255, 5), (315, 250, 1))),
        ("clip-v1-v2", [(1, 12, -8, -8, 1), icon, (1, 13, 300, 240, 1)],
         ((0, 0, 3), (25, 25, 1), (319, 255, 4), (300, 240, 1))),
    ]
    flattened = []
    for name, objects, probes in cases:
        for x, y, wanted in probes:
            actual = pixel_at(objects, x, y)
            assert actual == wanted, (name, x, y, wanted, actual)
            flattened.append((x, y, wanted))
    # After the explicit swap, the formerly visible front remains pen 1.
    flattened.append((116, 116, 1))
    assert len(flattened) == 19
    return flattened


def verify_script(text: str, model):
    assert text.startswith("' M19 P2.4")
    assert text.endswith("Return\n")
    assert text.count("Gosub CHECK_PIXEL") == 19
    regex = r"_PX=(-?\d+) : _PY=(-?\d+) : _WANT=(\d+) : Gosub CHECK_PIXEL"
    probes = [(int(x), int(y), int(p)) for x, y, p in re.findall(regex, text)]
    assert probes == model, ("ASC expected pixels drifted", probes, model)
    assert "If _PIXEL_OK<>19 or _SWAPS<>2 or _SOURCE_OK<>2" in text
    assert "If _PIXEL_BAD<>0" in text and "_PARITY_OK<>3" in text
    assert "If _LEN<=40 or _LEN<>_LEN2 or Length(27)<>Length(28)" in text
    assert "If Peek(_S27+_J)<>Peek(_S28+_J)" in text
    assert "For _J=0 To _LEN-1" in text
    assert "If (Peek(_PP+_STREAM+1+2*_PL) And 128)<>0" in text
    assert "If Peek(_PP+_STREAM)<>0" in text
    assert "If Deek(_PP+16)<>8 or _STREAM<40 or _STREAM+17<>_END" in text
    assert "If _PIXCAP=0" in text
    assert "Loke _DP,$424F4231" in text
    assert "Reserve As Data 20,76" in text
    assert "Reserve As Data 24,96" in text
    assert "Reserve As Data 25,176" in text
    assert "Reserve As Data 26,336" in text
    assert "_NOBJ(0)=4 : _NOBJ(1)=8 : _NOBJ(2)=16" in text
    assert "_BANKS(0)=24 : _BANKS(1)=25 : _BANKS(2)=26" in text
    assert "_REPS=64" in text
    assert "For _PASS=0 To 1" in text
    assert "If _PASS=1" in text and "_BM=1-_ORD" in text
    assert "For _ITER=1 To _REPS" in text
    assert "_D=Aga Bob Batch(_BN,_N)" in text
    assert "_D=Aga Bank Image Draw(_OBANK(_I),_OX(_I),_OY(_I),_OMODE(_I))" in text
    assert "_D=Aga F Icon(_OBANK(_I),_OICON(_I),_OX(_I),_OY(_I),_OMODE(_I))" in text
    assert "BENCH_BOBS " in text and "BASIC_TICKS " in text and "BATCH_TICKS " in text
    assert "RESULT " in text and "ERR " in text and "VERDICT " in text
    assert "Trap Open Out 1,_LOG$" in text and "Trap Close 1" in text
    assert "CLOSE_RETURNED " in text
    assert "M19_P24_RUNTIME.TXT" in text and "M19_P24_COMPILED.TXT" in text
    bench = text.split("' Benchmark: 64 repeated draw-only frames", 1)[1]
    timed = bench.split("CLEANUP:", 1)[0]
    assert "Aga Swap" not in timed and "Aga Wait Vbl" not in timed
    assert "Aga Bank Image Capture" not in timed and "Aga Blit Fill" not in timed
    assert "Amal" not in text and "Bload" not in text and "Load Iff" not in text
    assert "For _B=10 To 28" in text
    assert "If _ERR<>3" in text  # do not erase pre-existing banks


def main():
    last_good = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    current_lib = (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes()
    assert len(last_good) == 67904 and sha256(last_good).hexdigest() == R84_SHA
    candidate, meta=build_r87()
    assert meta["commands"]==77 and meta["ap20_entries"]==87
    current_sha=sha256(current_lib).hexdigest()
    assert len(current_lib)==73184 and current_sha==R87_SHA
    assert current_lib==candidate and meta["sha256"]==R87_SHA
    assert b"R87 v0.13.32" in candidate and meta["native_units"]["BOBS"]==5220
    active = list((ROOT / "tests/current").glob("*.asc"))
    assert len(active) == 1 and active[0].name == "M19_P26_R87_DRAW_BENCH_01.asc"
    legacy = ROOT / "tests/passed/M19_P23_BOBS_BATCH_01.asc"
    assert legacy.exists() and git_blob_sha(legacy.read_bytes()) == LEGACY_GIT_SHA
    source = (ROOT / "tests/design" / ASC_NAME).read_bytes().decode("latin-1")
    model = check_model()
    verify_script(source, model)
    assert "Aga Bob Probe" not in source
    assert "LIBRARY_EXPECTED R87_V0.13.32" in source
    for colour in range(256):
        test_bank = pack_image(1, 1, 8, bytes((colour,)))
        assert decode_single_pixel_v1(test_bank) == colour
    print("M19 P2.4 ARCHIVED UNVALIDATED DESIGN: 19 expected pixels,"
          " 256 v1 capture decode colours, 4/8/16 descriptor sizes, 3 byte-identical"
          " full-image parity checks specified, two AB/BA benchmark passes.")
    print("P2.4 DESIGN FILE IS NOT THE ACTIVE ASC. R87 Runtime/Compiled NOT TESTED.")


if __name__ == "__main__":
    main()
