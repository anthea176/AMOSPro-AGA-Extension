#!/usr/bin/env python3
"""R81 OPT020 active AMOS source on R80 compatibility fixture. STATIC ONLY."""
from pathlib import Path
from test_current_ram_log import verify
from test_current_amos_blocks import scan

PATH=Path("tests/current/C2P_R80_IFF_CHUNKY_01.asc")

def main():
    src=PATH.read_bytes().decode("latin-1")
    assert not scan(PATH),scan(PATH)
    verify(src)
    assert ".chk" not in src.casefold() and "Bload" not in src
    assert src.count("Aga Iff To Chunky(")==3
    for call in ("_LD12=Aga Iff To Chunky(_IFF$,12)",
                 "_LD13=Aga Iff To Chunky(_IFF$,13)",
                 "_BADBANK=Aga Iff To Chunky(_IFF$,4)"):
        assert call in src,call
    assert src.index("_LD12=Aga Iff To Chunky")<src.index("_C2P=Aga C2P Open(12)")
    assert src.index("_LD13=Aga Iff To Chunky")<src.index("_B1=Aga C2P Blit")
    assert src.count("_PIXCOUNT=_PIXCOUNT+1")==14
    assert src.count("_GOLDCOUNT=_GOLDCOUNT+1")==14
    assert "If _W<>320 or _H<>256 or _D<4 or _D>8" in src
    assert "If _W<>320 or _H<>256 or _D<>8" not in src
    assert "_OPEN=Aga Screen Open(320,256,_COLORS,$00021000)" in src
    for count in (16,32,64,128,256):
        assert f"_COLORS={count}" in src
    assert "If _GOLDEN=1" in src
    assert src.index("If _GOLDEN=1")>src.index("If _PIXCOUNT<>14")
    # Every generic oracle reads the untouched bank 13, never demo-only numbers.
    expected=[
        ("319","319"),
        ("250*320","250*320"),
        ("170*320+70","90*320+20"),
        ("168*320+224","95*320+240"),
        ("225*320+122","3*320+237"),
        ("14*320+10","10*320+145"),
        ("95*320+92","64*320+199"),
        ("14*320+198","74*320+240"),
        ("176*320+132","176*320+234"),
        ("115*320","64*320+10"),
        ("255*320+319","74*320+146"),
        ("124","10*320+231"),
        ("108*320+79","145*320+82"),
        ("151*320+150","173*320+127")
    ]
    for dst,source in expected:
        assert f"If Peek(_PTR+{dst})=Peek(_SRC+{source})" in src
    assert all(s in src for s in ("CHUNKY_OK","CPU_ATTNFLAGS","PRG_STATE",
        "C2P_R81_RUNTIME.TXT","C2P_R81_INTERPRETED.TXT","C2P_R81_COMPILED.TXT"))
    assert src.index("Amos To Back")<src.index("Until _K=69")<src.index("Aga Screen Close")<src.index("Amos To Front")
    assert src.rstrip().endswith("End")
    print("R81 OPT020 AMOS IFF/BLIT/ZOOM ASC STATIC PASS (no external bank file)")

if __name__=="__main__":
    main()
