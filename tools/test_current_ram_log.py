#!/usr/bin/env python3
"""Static minimum RAM: logging contract for a single current AMOS test."""
from pathlib import Path
import re

def verify(source):
    required={
        "run mode":r"\bPrg\s+State\b",
        "RAM filename":r"RAM:",
        "trapped open":r"\bTrap\s+Open\s+Out\b",
        "file print":r"\bPrint\s*#\s*\d+",
        "trapped close":r"\bTrap\s+Close\b",
        "I/O result":r"\bErrtrap\b",
        "mode field":r"RUN_MODE",
        "result field":r"\bRESULT\b",
        "close field":r"CLOSE_RETURNED",
    }
    for label,pattern in required.items():
        assert re.search(pattern,source,re.I),("missing AMOS RAM log",label)
    executable=[line.strip() for line in source.splitlines()
                if line.strip() and not line.lstrip().startswith("'")]
    assert executable and executable[-1].lower()=="end", (
        "ASC must end normally, not wait forever to preserve results")
    after_status=source[source.upper().rfind("CLOSE_RETURNED"):]
    assert not re.search(r"(?im)^\s*Do\s*\r?\n\s*(?:Aga\s+)?Wait\s+Vbl\s*\r?\n\s*Loop\s*$",after_status), (
        "terminal result holding VBL loop forbidden")

def main():
    scripts=sorted(Path("tests/current").glob("*.asc"))
    assert len(scripts)<=1,"Only one ASC is allowed in tests/current"
    if not scripts:
        print("CURRENT RAM LOG PASS (no active ASC)")
        return
    verify(scripts[0].read_bytes().decode("latin-1"))
    print("CURRENT RAM LOG STATIC PASS:",scripts[0])

if __name__=="__main__":
    main()
