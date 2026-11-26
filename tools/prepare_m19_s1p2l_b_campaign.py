#!/usr/bin/env python3
"""Prepare P2l-b diagnostic ASC from exact A/B/C-qualified P2k.
No active campaign write: output must be outside the repository.
This is not a delivery of a test library or a new public API.
"""
import argparse
from hashlib import sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OLD="987d45cd1f14aa62df944c7af35eda6884b0a44a70d3b7f0415e0ff2dd8a2c1e"
EDITS=(
    ("' M19 S1-P2k r4 - two launches, transaction quarantine.", "' M19 S1-P2l-b - diagnostic only, two launches."),
    ("_CHIP0=Chip Free : _FAST0=Fast Free", "_DIAG_START=-999 : _DIAG_ACTIVE=-999\n_DIAG_CLOSE=-999 : _DIAG_FRONT=-999\n_DIAG_OK=0 : _OBS$=\"NOT TESTED\"\n_CHIP0=Chip Free : _FAST0=Fast Free"),
    ("If Length(29)<>0\n   _ERR=2\nEnd If", "If Length(29)<>0\n   _ERR=2\nEnd If\nIf _ERR=0\n   _DIAG_START=Aga Sprite Bank Free(-19000)\nEnd If"),
    ("If _ATTEMPT=1\n   _OFF_RC=Aga Sprite Off(1)", "If _ERR=0\n   _DIAG_ACTIVE=Aga Sprite Bank Free(-19000)\nEnd If\nIf _ATTEMPT=1\n   _OFF_RC=Aga Sprite Off(1)"),
    ("   _CLOSE_RETURNED=1\n   Amos To Front", "   _CLOSE_RETURNED=1\n   If _ERR=0 and _CLEAN_ERR=0\n      _DIAG_CLOSE=Aga Sprite Bank Free(-19000)\n   End If\n   Amos To Front"),
    ("      _CLOSED=1\n   Else", "      _CLOSED=1\n      If _ERR=0 and _CLEAN_ERR=0\n         _DIAG_FRONT=Aga Sprite Bank Free(-19000)\n      End If\n   Else"),
    ("Trap Open Out 1,_LOG$", "' Keep sequence and diagnostic verdicts independent.\nIf _RESULT=1\n   _OBS$=\"DIAG_ROUTE_FAIL\"\n   If _PHASE=1\n      If _DIAG_START=-131 and _DIAG_ACTIVE=-180\n         _DIAG_OK=1\n      End If\n   Else\n      If _DIAG_START<=-180 and _DIAG_START>=-190\n         If _DIAG_ACTIVE<=-180 and _DIAG_ACTIVE>=-190\n            _DIAG_OK=1\n         End If\n      End If\n   End If\n   If _DIAG_CLOSE>-180 or _DIAG_CLOSE<-190\n      _DIAG_OK=0\n   End If\n   If _DIAG_FRONT>-180 or _DIAG_FRONT<-190\n      _DIAG_OK=0\n   End If\n   If _DIAG_START=-189 or _DIAG_ACTIVE=-189 or _DIAG_CLOSE=-189 or _DIAG_FRONT=-189\n      _DIAG_OK=0\n   End If\n   If _DIAG_OK=1\n      _OBS$=\"OBS_PENDING\"\n      If _DIAG_CLOSE=-190 or _DIAG_FRONT=-190\n         _OBS$=\"OBS_COMPATIBLE_ONLY\"\n      End If\n   End If\nEnd If\nTrap Open Out 1,_LOG$"),
    ("Print #1,\"SOURCE_TAG M19_S1P2K_R4_TRANSACTION_V1\"", "Print #1,\"SOURCE_TAG M19_S1P2LB_DMA_DIAG_V1\""),
    ("Print #1,\"DMA_FREE_PROVEN 0\"", "Print #1,\"DIAG_START \";_DIAG_START;\" DIAG_ACTIVE \";_DIAG_ACTIVE\nPrint #1,\"DIAG_CLOSE \";_DIAG_CLOSE;\" DIAG_FRONT \";_DIAG_FRONT\nPrint #1,\"DIAG_ROUTE_OK \";_DIAG_OK;\" OBSERVATION \";_OBS$\nPrint #1,\"DMA_FREE_PROVEN 0\""),
    ("Print \"RAM LOG \";_LOG$", "Print _OBS$\nPrint \"RAM LOG \";_LOG$"),
)

def prepare(raw):
    assert sha256(raw).hexdigest()==OLD
    crlf=b"\r\n" in raw
    s=raw.decode("ascii").replace("\r\n","\n")
    for old,new in EDITS:
        assert s.count(old)==1, old
        s=s.replace(old,new,1)
    s=s.replace("RAM:M19_S1P2K_","RAM:M19_S1P2LB_")
    assert s.count("Aga Sprite Bank Free(-19000)")==4
    assert s.count("Aga Sprite Bank Free(29)")==1
    assert s.count("Aga Screen Close")==1
    assert "DMA_FREE_PROVEN 0" in s
    assert all(len(line)<=200 for line in s.splitlines())
    return (s.replace("\n","\r\n") if crlf else s).encode("ascii")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    assert a.source.resolve()==ROOT/"tests/current/SPRITE_PUBLIC.asc"
    assert not a.output.resolve().is_relative_to(ROOT), "qualification output must be temporary"
    raw=a.source.read_bytes()
    result=prepare(raw)
    a.output.write_bytes(result)
    assert a.source.read_bytes()==raw
    print("P2LB_ASC_PREPARED",len(result),sha256(result).hexdigest())

if __name__=="__main__":
    main()
