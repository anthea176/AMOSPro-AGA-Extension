#!/usr/bin/env python3
"""Static contract and independent pixel reference for P2 integrated AMOS bench.

Does not run AMOS or emulate the native P2d library. WinUAE Gate B and real
AMOS Compiler Gate C require separate evidence.
"""
from pathlib import Path
from hashlib import sha1, sha256

ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "examples/bob_p2_all_in_one/M19_P2_ALL_IN_ONE.asc"
PASSED = ROOT / "tests/passed/M19_P2_ALL_IN_ONE.asc"
EVIDENCE = ROOT / "docs/evidence"
SOURCE_BLOB = "c48d334fd4508d402d28399bffdfec08d4cb4acb"


def pixels_f32():
    p = {(x, y): 165 for y in range(32) for x in range(32)
         if x < 6 or (y < 6 and x >= 6) or (12 <= y <= 17 and 6 <= x < 22)}
    p.update({(x, y): 90 for y in range(1, 5) for x in range(23, 28)})
    return p


def pixels_l32():
    p = {(x, y): 90 for y in range(32) for x in range(32)
         if x < 6 or (y >= 26 and x >= 6)}
    p.update({(x, y): 165 for y in range(27, 31) for x in range(19, 24)})
    return p


def oriented(p, mode, x, y):
    return p.get((31 - x if mode & 1 else x,
                  31 - y if mode & 2 else y), 0)


def reference_geometry():
    f, l = pixels_f32(), pixels_l32()
    for mode0 in range(4):
        mode1 = 3 - mode0
        actual = (
            oriented(f, mode0, 0, 7),
            oriented(f, mode0, 16, 31),
            oriented(l, mode1, 0, 7),
            oriented(l, mode1, 0, 31),
            oriented(l, mode1, 31, 31),
        )
        expected = (
            0 if mode0 & 1 else 165,
            165 if mode0 & 2 else 0,
            0 if mode1 & 1 else 90,
            0 if mode1 == 3 else 90,
            0 if mode1 == 2 else 90,
        )
        assert actual == expected, (mode0, actual, expected)
    for mask0, mask1 in ((255, 255), (1, 2), (0, 0),
                         (129, 66), (255, 255)):
        assert oriented(f, 0, 0, 7) & mask0 == 165 & mask0
        assert oriented(l, 0, 0, 7) & mask1 == 90 & mask1
    return 20, 10


def verify_source():
    raw = ASC.read_bytes()
    assert raw.isascii() and b"\r" not in raw
    assert PASSED.read_bytes() == raw, "Frozen test and public example differ"
    git_header = b"blob " + str(len(raw)).encode() + b"\x00"
    assert sha1(git_header + raw).hexdigest() == SOURCE_BLOB, "Validated ASC changed"
    source = raw.decode("ascii")
    assert source.startswith("' M19 P2 P2a/P2b/P2c/P2d/P2e")
    assert source.endswith("\nEnd\n")
    assert all(len(line) <= 220 for line in source.splitlines())
    for snippet in (
        "Amal 0,_AMAL0$ To _ADDR0",
        "Amal 1,_AMAL1$ To _ADDR1",
        "For _FRAME=1 To 240",
        "Aga Bob Col(1,2,0)",
        "Aga Bob Col(1,2,1)",
        "Aga Bob Col(1,2,2)",
        "Aga Bob Flip(1,_FLIP_MODE0)",
        "Aga Bob Flip(2,_FLIP_MODE1)",
        "Aga Bob Flip(1,4)",
        "Aga Bob Planes(1,_PLANES_MASK0)",
        "Aga Bob Planes(2,_PLANES_MASK1)",
        "Aga Bob Planes(1,-1)",
        "Aga Bob Planes(2,256)",
        "Aga Bob Auto Update(1)",
        "Aga Bob Auto Update(0)",
        "Get AGA Bob 3,80,16,111,47",
        "Get AGA Bob 4,128,16,159,47",
        "Make AGA Bob Mask 3,0",
        "Make AGA Bob Mask 4,0",
        "For _FLIP_STAGE=0 To 4",
        "For _PLANES_STAGE=0 To 5",
        "_COL_CHECKS<>8",
        "_FLIP_PIX0<>8 or _FLIP_PIX1<>12",
        "_PLANES_PIX0<>5 or _PLANES_PIX1<>5",
        "If _SWAP<>1",
        "_SWAP_RETRY_LIMIT=4",
        "Amos To Back",
        "Amos To Front",
        "SOURCE_TAG P2_FULL_V1_20261121",
    ):
        assert snippet in source, (ASC, snippet)
    assert "Trap Open Out 1,_LOG$" in source
    assert "Print #1,\"RUN_MODE \";_MODE$" in source
    return len(raw)


def verify_evidence() -> None:
    cases = (
        ("RUNTIME", 1632, "864f6b17652033b99f06ec34df3ce85f3a1579bbb52c033d67d62e178852c627", "1"),
        ("COMPILED", 1633, "296f562f73a83d91f419d60a4538e35ef05d55f0c159012949fc5482ce88bf41", "-1"),
    )
    entries = {}
    for mode, expected_size, digest, expected_state in cases:
        path = EVIDENCE / f"M19_P2_ALL_IN_ONE_{mode}_PASS_2026-11-21.TXT"
        raw = path.read_bytes()
        assert len(raw) == expected_size and sha256(raw).hexdigest() == digest
        assert raw.count(b"\r\n") == 97, f"{mode}: original CRLF log corrupted"
        fields = {}
        for line in raw.decode("ascii").splitlines():
            pair = line.strip().split(None, 1)
            if len(pair) == 2:
                fields[pair[0]] = pair[1]
        expected = {
            "TEST": "M19 P2 ALL IN ONE",
            "SOURCE_TAG": "P2_FULL_V1_20261121",
            "PRG_STATE": expected_state, "RUN_MODE": mode,
            "RESULT": "1", "ERR": "0", "VERDICT": "PASS",
            "PHASE_LAST": "4", "VALID_SAMPLES": "240", "SWAPS": "252",
            "SWAP_REFUSALS": "121", "SWAP_RECOVERED": "121",
            "RETRY_VBLS": "121", "COL_CHECKS": "8",
            "FLIP_PIX0": "8", "FLIP_PIX1": "12",
            "PLANES_PIX0": "5", "PLANES_PIX1": "5",
            "AUTO_ENABLE": "1", "AUTO_DISABLE": "1",
            "CLOSE_RETURNED": "1",
        }
        for name, val in expected.items():
            assert fields[name] == val, (mode, name, fields.get(name), val)
        entries[mode] = fields
    rt, comp = entries["RUNTIME"].copy(), entries["COMPILED"].copy()
    for key in ("PRG_STATE", "RUN_MODE"):
        del rt[key]
        del comp[key]
    assert rt == comp, "Runtime and compiled logs differ outside mode identifiers"


def main():
    verify_evidence()
    n = verify_source()
    flip, planes = reference_geometry()
    print(f"P2 ALL IN ONE STATIC PASS: {n} ASCII bytes; "
          f"8 collision checks, {flip} Flip pixel predictions, "
          f"{planes} Planes pixel predictions; "
          "WinUAE/Compiler runs evidenced by byte-exact user logs; "
          "static reference test only")


if __name__ == "__main__":
    main()
