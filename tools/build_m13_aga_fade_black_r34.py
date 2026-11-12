#!/usr/bin/env python3
"""R34 0.10.6 deterministic AP20 builder (indexed Fade To Black).

R33 WinUAE-PASS is the immutable build base. Never modifies LAST_GOOD or
dist; emits only in memory, and (on request) base64 for GitHub publication
after Gate A CPU/CI has passed.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split,digest
from audit_ap20 import parse,inspect,token
from m13_aga_fade_black_r34_emit import emit_black,ENTRY_BLACK,BASE_ENTRIES,GETP

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib"
BASE_SHA256="e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f"
LAST_GOOD=ROOT/"dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"
LAST_GOOD_SHA256="0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib"
VERSION="R34 0.10.6"
API=(("aga fade to black",ENTRY_BLACK,"00"),)

def build():
    frozen=BASE.read_bytes()
    assert digest(frozen)==BASE_SHA256,"R33 archive mutated"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD must match WinUAE-PASS R38"
    tok,parts,_=split(frozen)
    assert len(parts)==BASE_ENTRIES and not parts[-1].endswith(GETP)
    base_audit=inspect(parse(frozen))
    assert not base_audit["issues"]
    assert len([x for x in base_audit["tokens"] if x["name"].startswith("aga ")])==39
    black,labels=emit_black()
    assert len(black)%2==0 and len(black)>300
    updated=list(parts)
    updated[-1]+=GETP
    updated.append(black)
    assert updated[:ENTRY_BLACK-1]==parts[:ENTRY_BLACK-1]
    assert updated[ENTRY_BLACK-1]==parts[ENTRY_BLACK-1]+GETP
    assert updated[ENTRY_BLACK]==black
    newtok=tok[:-6]+token("aga fade to black",1,ENTRY_BLACK,"00")+bytes(6)
    title=b"AMOSPro AGA M13 Fade To Black R34 0.10.6\0$VER: AMOSPro_AGA 0.10.6\0"
    if len(title)%2:title+=b"\0"
    code=b"".join(updated)
    payload=(pack(">4I",len(updated)*2,len(newtok),len(code),len(title))
        +b"\0\0AP20"+b"".join(pack(">H",len(s)//2) for s in updated)
        +newtok+code+title+b"\0\0")
    payload+=bytes(-len(payload)%4)
    size=pack(">I",len(payload)//4)
    binary=frozen[:20]+size+frozen[24:28]+size+payload+frozen[-4:]
    audit=inspect(parse(binary))
    assert not audit["issues"],audit["issues"]
    actualtok,segments,_=split(binary)
    assert actualtok==newtok and segments==updated
    named=[x for x in audit["tokens"] if x["name"].startswith("aga ")]
    assert len(named)==40
    matches=[x for x in named if x["name"]=="aga fade to black"]
    assert len(matches)==1
    assert (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,ENTRY_BLACK,"00")
    assert any(x["index"]==ENTRY_BLACK and x["parameters"]==1 and x["getp"]
               for x in audit["parameter_checks"])
    return binary,{"version":VERSION,"size":len(binary),"sha256":digest(binary),
                   "named_commands":len(named),"segments":len(updated),
                   "new_command":API[0],"labels":labels,
                   "Gate_A":"REQUIRES_CPU_CI","Gate_B":"NOT_TESTED"}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,report=build()
    assert binary==build()[0],"R34 not deterministic"
    print("R34 in-memory candidate:",{k:v for k,v in report.items() if k!="labels"},flush=True)
    if args.emit_base64:
        print("R34_BASE64_BEGIN",flush=True)
        encoded=base64.b64encode(binary).decode("ascii")
        for i in range(0,len(encoded),76):
            print(encoded[i:i+76],flush=True)
        print("R34_BASE64_END",flush=True)
