#!/usr/bin/env python3
"""M19 P2.5 R87: read-only preflight of minimal AMOS smoke source.

This does not compile AMOS or execute WinUAE. The historical R86 source and
R87 smoke file is archived byte-for-byte, separately from the P2.6 benchmark.
"""
from __future__ import annotations

from hashlib import sha1, sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SMOKE="M19_P25_R87_BOBS_SMOKE_01.asc"
SMOKE_GIT="347e35d4e79b4afc331a732f33c448bbb61ddef9"
R86_PASSED_GIT="19ad2044252783454f4082c118e53b34a6b83478"
DRAFT_GIT="30c2e09f3b7b365aec8ef47fc741311ba1cb984a"
R84_SHA="46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d"
R87_SHA="02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302"

def blob_sha(b:bytes)->str:
    return sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def main()->None:
    good=(ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    active=(ROOT/"dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib").read_bytes()
    assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA, "LAST_GOOD changed"
    assert len(active)==73184 and sha256(active).hexdigest()==R87_SHA, "R87 archived predecessor changed"
    active_candidate=(ROOT/"dist/AMOSPro_AGA.Lib").read_bytes()
    assert len(active_candidate)==102360 and sha256(active_candidate).hexdigest()=="838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403"
    files=sorted((ROOT/"tests/current").glob("*.asc"))
    assert len(files)==1, files  # historical R87 test must not pin the active B7 campaign name
    raw=(ROOT/"tests/passed"/SMOKE).read_bytes()
    assert blob_sha(raw)==SMOKE_GIT, "Smoke changed without requalification"
    assert blob_sha((ROOT/"tests/passed/M19_P23_BOBS_BATCH_01.asc").read_bytes())==R86_PASSED_GIT
    assert blob_sha((ROOT/"tests/design/M19_P24_BOBS_PIXELS_BENCH_01_UNVALIDATED.asc").read_bytes())==DRAFT_GIT
    s=raw.decode("latin-1")
    assert "Aga Bob Probe" not in s
    assert "Gosub" not in s and "Then" not in s
    assert "LIBRARY_EXPECTED R87_V0.13.32" in s
    assert "M19_P25_RUNTIME.TXT" in s and "M19_P25_COMPILED.TXT" in s
    assert "Trap Open Out 1,_LOG$" in s
    assert "Trap Close 1" in s
    assert "CLOSE_RETURNED " in s
    assert "_BANKS_SAFE=0" in s
    assert "Next _B\n_BANKS_SAFE=1" in s
    assert "If _BANKS_SAFE=1\n   For _B=10 To 22" in s
    assert s.count("_OK=Aga Bob Batch(20,3)")==3
    assert s.count("If Aga Bob Batch(")==3
    assert "Aga Bank Image Capture(18,110,110,1,1,-1,1)" in s
    assert s.count("Aga Swap")==1
    assert "If _ERR=0 and (_CAP<>2 or _DRAW<>3 or _REJECT<>3)" in s
    assert "PARITY_OK" not in s and "PIXEL_OK" not in s
    assert max(map(len,s.splitlines()))<=220
    assert s.endswith("End\n")
    print("M19 P2.5 ARCHIVED SMOKE PASS: R87 SHA, R84 frozen, one B7 active ASC,"
          " bank ownership, 3 batch draws, 3 invalid calls and RAM logs.")
    print("M19 P2.5 R87 Runtime B and Compiled C PASS in user-provided logs; P2.6 benchmark NOT TESTED.")

if __name__=="__main__":
    main()
