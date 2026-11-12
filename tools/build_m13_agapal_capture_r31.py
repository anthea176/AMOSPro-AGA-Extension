#!/usr/bin/env python3
"""R31 0.10.3 in-memory AP20 builder, solely AGAPAL palette capture.

R31 0.10.3 has passed native CPU Gate A and interpreted AMOS/WinUAE
Gate B. Its exact published bytes are frozen in the R31 archive (R38 is LAST_GOOD); the WinUAE-PASS
R30 base remains frozen as a versioned archive.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split,digest
from audit_ap20 import parse,inspect,token
from m13_agapal_capture_r31_emit import emit_capture,ENTRY_CAPTURE,BASE_ENTRIES,GETP

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib"
BASE_SHA256="446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256="09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib"
API=(("aga palette bank capture",ENTRY_CAPTURE,"00,0"),)
VERSION="R31 0.10.3"

def build():
    original=BASE.read_bytes()
    assert digest(original)==BASE_SHA256,"frozen R30 archive changed"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD must match validated R38"
    tok,parts,_=split(original)
    assert len(parts)==BASE_ENTRIES and not parts[-1].endswith(GETP)
    audit0=inspect(parse(original))
    assert not audit0["issues"]
    assert len([a for a in audit0["tokens"] if a["name"].startswith("aga ")])==36
    assert not any(a["name"]==API[0][0] for a in audit0["tokens"])
    capture,labels=emit_capture()
    assert len(capture)%2==0 and len(capture)>300
    newparts=list(parts)
    newparts[-1]+=GETP
    newparts.append(capture)
    assert newparts[:41]==parts[:41]
    assert newparts[41]==parts[41]+GETP
    assert newparts[42]==capture
    newtok=tok[:-6]+token("aga palette bank capture",1,ENTRY_CAPTURE,"00,0")+bytes(6)
    title=b"AMOSPro AGA M13 AGAPAL Bank Capture R31 0.10.3\0$VER: AMOSPro_AGA 0.10.3\0"
    if len(title)%2:title+=b"\0"
    code=b"".join(newparts)
    payload=(pack(">4I",2*len(newparts),len(newtok),len(code),len(title))
        +b"\0\0AP20"+b"".join(pack(">H",len(x)//2) for x in newparts)
        +newtok+code+title+b"\0\0")
    payload+=bytes(-len(payload)%4)
    size=pack(">I",len(payload)//4)
    binary=original[:20]+size+original[24:28]+size+payload+original[-4:]
    report=inspect(parse(binary))
    assert not report["issues"],report["issues"]
    actualtok,segments,_=split(binary)
    assert actualtok==newtok and segments==newparts
    named=[a for a in report["tokens"] if a["name"].startswith("aga ")]
    assert len(named)==37
    rows=[a for a in named if a["name"]=="aga palette bank capture"]
    assert len(rows)==1 and (rows[0]["instruction"],rows[0]["function"],rows[0]["signature"])==(1,42,"00,0")
    assert any(a["index"]==42 and a["parameters"]==2 and a["getp"] for a in report["parameter_checks"])
    return binary,{
        "version":VERSION,"size":len(binary),"sha256":digest(binary),
        "named_commands":len(named),"segments":len(newparts),
        "new_command":API[0],"labels":labels,
        "Gate_A":"REQUIRES_CPU_CI","Gate_B":"NOT_TESTED"
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,report=build()
    assert binary==build()[0],"builder not deterministic"
    print("R31 candidate in-memory:",report,flush=True)
    if args.emit_base64:
        print("R31_BASE64_BEGIN",flush=True)
        print(base64.b64encode(binary).decode("ascii"),flush=True)
        print("R31_BASE64_END",flush=True)
