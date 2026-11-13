#!/usr/bin/env python3
"""Static and current AP20 API preflight for examples/fast_icons_r67.

Does NOT execute AMOS, WinUAE or the AMOS Compiler. Do not infer Gate B/C.
The ten legacy root example ASC files and historical cases are untouched.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from audit_ap20 import inspect,parse

PACKAGE=ROOT/"examples/fast_icons_r67"
SOURCE=PACKAGE/"FAST_ICON_LAB.asc"
COMMANDS=(
    "Aga Detect",
    "Aga F Icon Bank Create",
    "Aga F Icon Bank Put",
    "Aga F Chip Bank Create",
    "Aga F Chip Stage",
    "Aga F Icon Capture",
    "Aga F Icon",
    "Aga F Blit",
    "Aga Screen Open",
    "Aga Double Buffer",
    "Aga Palette Set",
    "Aga Blit Clear",
    "Aga Blit Fill",
    "Aga Text",
    "Aga Swap",
    "Aga Wait Vbl",
    "Aga Mouse Pressed",
    "Aga Key",
    "Aga Screen Close",
    "Aga Mouse X",
)

def require(condition:bool,message:str)->None:
    if not condition:
        raise AssertionError(message)

def main()->None:
    b=SOURCE.read_bytes()
    source=b.decode("ascii")
    require(b"\r" not in b and source.endswith("End\n"),"AMOS source must be ASCII LF + final End")
    lines=[l for l in source.splitlines() if l.strip() and not l.lstrip().startswith("'")]
    for start,stop in (("If","End If"),("For","Next")):
        one=sum(bool(re.match(r"^\s*"+start+r"\b",l,re.I)) for l in lines)
        two=sum(bool(re.match(r"^\s*"+stop+r"\b",l,re.I)) for l in lines)
        require(one==two,f"Unbalanced AMOS {start}/{stop}: {one} vs {two}")
    require(not any(re.search(r"\bThen\b",l,re.I) for l in lines),"AMOS If cannot use Then")
    require(not any(re.match(r"^\s*(?:Save|Load|Bsave|Bload|Open|Write|Input)\b",l,re.I)
                    for l in lines),"Showcase must never read/write files")
    require("Fsel$(" not in source,"Showcase must be asset-free")
    require("Reserve As Data 13,256" in source and
            "Aga F Icon Bank Create(12,8)" in source and
            "Aga F Chip Bank Create(11,8)" in source,"Wrong active bank allocations")
    require(source.index("_PUTS=_PUTS+1")<source.index("_STAGES=_STAGES+1"),
            "Stage must be explicitly after Put")
    require("_RESTAGE=Aga F Chip Stage(12,11,2)" in source and
            "_REPUT=Aga F Icon Bank Put(12,2,13,0)" in source,
            "Missing source modification + explicit re-stage example")
    require("_SRCDRAW=Aga F Icon(12,2,31,45,0)" in source and
            "_CAP=Aga F Icon Capture(12,5,31,45)" in source and
            "_CAPSTAGE=Aga F Chip Stage(12,11,5)" in source,
            "Missing exact unaligned capture -> staging pipeline")
    require("For _I=0 To 287" in source and
            "Peek(Start(12)+12+288+_I)<>Peek(Start(12)+12+4*288+_I)" in source,
            "Must verify all 288 capture bytes, not only success return")
    require(all(f"Aga F Icon(12,_ID,{x},_RY,{mode})" in source
                for x,mode in ((109,1),(164,0))),"Missing CPU masked/opaque render")
    require(all(f"Aga F Blit(11,_ID,{x},_RY,{mode})" in source
                for x,mode in ((219,1),(274,0))),"Missing Blitter masked/opaque render")
    require("Aga Palette Set(255,255,255,255)" in source,
            "High pen 255 must be explicitly configured")
    require("For _FRAME=1 To 1200" in source and
            "For _TRY=1 To 20" in source and
            "If _READY=0" in source and
            "Aga Wait Vbl" in source,"Bounded Safe/swap retry and frames required")
    require(all(s in source for s in ("Aga Screen Close","Amos To Front",
            "Erase 13 : Erase 12 : Erase 11",'Print "RESULT ";_RESULT',
            'Print "CLOSE RETURNED"')),"No complete teardown/result")
    current=inspect(parse((ROOT/"dist/AMOSPro_AGA.Lib").read_bytes()))
    require(not current["issues"],"Active AP20 binary audit failed")
    valid={v["name"].casefold() for v in current["tokens"]}
    for name in COMMANDS:
        require(name.casefold() in valid,f"API missing in active library: {name}")
        require(name in source,f"Demo does not exercise {name}")
    for p,index,disclaimer in (
        ("README.fr.md","fast_icons_r67/","n'a pas encore été essayée séparément"),
        ("README.md","fast_icons_r67/","NOT been independently tested"),
    ):
        body=(PACKAGE/p).read_text("utf-8")
        require(disclaimer in body,f"Missing runtime-test disclaimer in {p}")
        require("FAST_ICON_LAB.asc" in body and "FICHIP8" in body and "FICON8" in body,
                f"Incomplete source/bank documentation in {p}")
        intro=(ROOT/"examples"/p).read_text("utf-8")
        require(index in intro and "FAST_ICON_LAB.asc" in intro,
                f"Public examples index must link demo: {p}")
    print("M18/R67 FAST ICON LAB STATIC PASS: ASCII AMOS balanced,",
          "six Fast Icon commands, CPU/Blitter modes, 288 byte capture,",
          "safe cleanup and EN/FR docs; WinUAE interpreted run still required.")

if __name__=="__main__":
    main()
