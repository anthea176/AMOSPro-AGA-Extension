#!/usr/bin/env python3
"""R80 active AMOS test static guard. Not WinUAE validation."""
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
    assert all(s in src for s in ("CHUNKY_OK","CPU_ATTNFLAGS","PRG_STATE",
        "C2P_R80_RUNTIME.TXT","C2P_R80_INTERPRETED.TXT","C2P_R80_COMPILED.TXT"))
    assert src.index("Amos To Back")<src.index("Until _K=69")<src.index("Aga Screen Close")<src.index("Amos To Front")
    assert src.rstrip().endswith("End")
    print("R80 AMOS IFF DIRECT-CHUNKY ASC STATIC PASS (no external bank file)")

if __name__=="__main__":
    main()
