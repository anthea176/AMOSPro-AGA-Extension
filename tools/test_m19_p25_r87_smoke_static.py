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
P0_FREE_SHA="f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d"
R87_SHA="02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302"
P1E_SHA="7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42"

def blob_sha(b:bytes)->str:
    return sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def main()->None:
    good=(ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    active=(ROOT/"dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib").read_bytes()
    from active_library import P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, verify_active
    checked, protected, _ = verify_active(ROOT)
    assert protected == good and (len(good), sha256(good).hexdigest()) in ((124444,P1E_SHA),(136020,P2D_SHA))
    from build_aga_r84_agapic import build as build_r84
    historic,r84meta=build_r84()
    assert len(historic)==67904 and r84meta['sha256']==R84_SHA
    assert len(active)==73184 and sha256(active).hexdigest()==R87_SHA, "R87 archived predecessor changed"
    active_candidate=(ROOT/"dist/AMOSPro_AGA.Lib").read_bytes()
    from active_library import B7M2_SHA,B8_SHA,B8S1_SHA,verify_active
    active_digest=sha256(active_candidate).hexdigest()
    assert active_digest in (B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA,P2D_SHA,S1P1E_SHA,P2DL2_SHA,P2DL2B_SHA), 'Unknown active canonical library'
    from build_m19_b8_first_update_in_memory import build_b8_first_update
    b8,report=build_b8_first_update()
    assert len(b8)==115744 and report['sha256']==B8_SHA
    if active_digest in (P2D_SHA,S1P1E_SHA,P2DL2_SHA,P2DL2B_SHA):
        assert active_candidate == checked and sha256(good).hexdigest() == P2D_SHA
    elif active_digest==P1E_SHA:
        from build_m19_p1e_bank_edit_in_memory import build_p1e
        candidate,info=build_p1e()
        assert active_candidate==good==candidate and info["sha256"]==P1E_SHA
    elif active_digest==P0_FREE_SHA:
        from build_m19_b8_s1_bank_free_in_memory import build_bank_free
        p0,meta=build_bank_free()
        assert active_candidate==p0 and len(p0)==117896 and meta['sha256']==P0_FREE_SHA
    elif active_digest==B8S1_SHA:
        from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
        s1,s1meta=build_b8_safe_retry()
        assert active_candidate==s1 and len(s1)==116104 and s1meta['sha256']==B8S1_SHA
    elif active_digest==B8_SHA:
        assert active_candidate==b8
    else:
        assert len(active_candidate)==102400 and active_digest==B7M2_SHA
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
    print("M19 P2.5 ARCHIVED SMOKE PASS: R87 SHA, R84 frozen, one SHA-verified current ASC,"
          " bank ownership, 3 batch draws, 3 invalid calls and RAM logs.")
    print("M19 P2.5 R87 Runtime B and Compiled C PASS in user-provided logs; P2.6 benchmark NOT TESTED.")

if __name__=="__main__":
    main()
