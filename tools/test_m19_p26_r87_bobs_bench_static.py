#!/usr/bin/env python3
"""M19 P2.6 R87 archived PASS benchmark source integrity (read-only)."""
from __future__ import annotations

from hashlib import sha1, sha256
from pathlib import Path
from struct import pack

ROOT = Path(__file__).resolve().parents[1]
TEST = "M19_P26_R87_DRAW_BENCH_01.asc"
ASC_BLOB = "c6c03b24bb273027492776ba24e53193ec52198b"
SMOKE_BLOB = "347e35d4e79b4afc331a732f33c448bbb61ddef9"
R87_SHA = "02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302"
R84_SHA = "46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d"

def git_blob(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def descriptors(n: int) -> bytes:
    assert n in (4,8,16)
    records=[]
    for i in range(n):
        x,y=20+(i%4)*44,20+(i//4)*44
        typ=i%3
        bank=13 if typ==1 else 11 if typ==2 else 12
        image_id=2 if typ==2 else 0
        kind=2 if typ==2 else 1
        records.append(pack(">iiIIHH",y,x,bank,image_id,kind,1))
    return pack(">IHHII",0x424F4231,1,20,n,0)+b"".join(records)

def main() -> None:
    current=(ROOT/"dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib").read_bytes()
    good=(ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    active=(ROOT/"dist/AMOSPro_AGA.Lib").read_bytes()
    assert len(active)==138044 and sha256(active).hexdigest()=="967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1"
    assert len(current)==73184 and sha256(current).hexdigest()==R87_SHA
    assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA
    asc=sorted((ROOT/"tests/current").glob("*.asc"))
    assert len(asc)==1 and asc[0].name=="M19_AP20_UNIT5_01.asc"
    data=(ROOT/"tests/passed"/TEST).read_bytes()
    assert git_blob(data)==ASC_BLOB, "Benchmark source changed without rechecking"
    smoke=(ROOT/"tests/passed/M19_P25_R87_BOBS_SMOKE_01.asc").read_bytes()
    assert git_blob(smoke)==SMOKE_BLOB, "Previously validated smoke altered"
    source=data.decode("latin-1")
    assert "Aga Bob Probe" not in source
    assert "Set Buffer 20" in source and "Aga Screen Close" in source
    assert "M19_P26_RUNTIME.TXT" in source and "M19_P26_COMPILED.TXT" in source
    assert "Trap Open Out 1,_LOG$" in source and "Trap Close 1" in source
    assert "CLOSE_RETURNED" in source
    assert "_BANKS_SAFE=0" in source and "Next _B\n_BANKS_SAFE=1" in source
    assert "For _B=10 To 26" in source
    assert "If _BANKS_SAFE=1\n   For _B=10 To 26" in source
    assert "Reserve As Data 24,96" in source
    assert "Reserve As Data 25,176" in source
    assert "Reserve As Data 26,336" in source
    assert "Loke _P,$424F4231 : Doke _P+4,1 : Doke _P+6,20" in source
    assert "Doke _R+16,_KIND(_I) : Doke _R+18,1" in source
    assert "For _PASS=0 To 1" in source and "_METHOD=1-_ORDER" in source
    assert "For _CASE=0 To 2" in source and "For _ORDER=0 To 1" in source
    assert "_REPS=64" in source and "For _REP=1 To _REPS" in source
    assert "_TIME(_CASE,_METHOD,_PASS)=Timer-_T0" in source
    assert "Aga Bank Image Draw(_SRC(_I),_OX(_I),_OY(_I),1)" in source
    assert "Aga F Icon(11,2,_OX(_I),_OY(_I),1)" in source
    assert "Aga Bob Batch(_BN,_N)" in source
    assert "Aga Swap" not in "\n".join(x for x in source.splitlines()
                                      if not x.lstrip().startswith("'"))
    assert "Aga Wait Vbl" not in "\n".join(x for x in source.splitlines()
                                          if not x.lstrip().startswith("'"))
    timed=source.split("_T0=Timer",1)[1].split("_TIME(_CASE,_METHOD,_PASS)",1)[0]
    assert "Aga Blit Fill(" not in timed
    assert "Aga Bank Image Capture(" not in timed
    assert "Wait Vbl" not in timed and "Aga Swap" not in timed
    assert "BOBS " in source and "BASIC_TICKS " in source and "BATCH_TICKS " in source
    assert "_BASIC_CALLS<>3584 or _BATCH_CALLS<>384" in source
    assert len(data)==7002 and max(map(len,source.splitlines()))<=200
    for n,size in ((4,96),(8,176),(16,336)):
        out=descriptors(n)
        assert len(out)==size
        assert int.from_bytes(out[8:12],"big")==n
        assert all(0<=20+(i%4)*44+40<=320 for i in range(n))
        assert all(0<=20+(i//4)*44+40<=256 for i in range(n))
    print("M19 P2.6 ARCHIVED SOURCE PASS: R84/R87 pinned, P2.6 archived unchanged,")
    print("one benchmark ASC; 4/8/16 descriptor layout; 64 x AB/BA; draw-only timing.")
    print("P2.6 R87 Runtime and Compiled PASS in user logs; does not validate P2.7.")

if __name__=="__main__":
    main()
