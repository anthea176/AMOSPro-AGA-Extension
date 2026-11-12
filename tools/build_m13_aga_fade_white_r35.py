#!/usr/bin/env python3
"""R35 0.10.7 deterministic AP20 builder (indexed Fade To White).

R34 WinUAE-PASS is the immutable build base. Never modifies LAST_GOOD or
dist; emits only in memory, and (on request) base64 for GitHub publication
after Gate A CPU/CI has passed.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split,digest
from audit_ap20 import parse,inspect,token
from m13_aga_fade_white_r35_emit import emit_white,ENTRY_WHITE,BASE_ENTRIES,GETP

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib"
BASE_SHA256="89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256="09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib"
VERSION="R35 0.10.7"
API=(("aga fade to white",ENTRY_WHITE,"00"),)

def build():
    frozen=BASE.read_bytes()
    assert digest(frozen)==BASE_SHA256,"R34 archive mutated"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD must match WinUAE-PASS R38"
    tok,parts,_=split(frozen)
    assert len(parts)==BASE_ENTRIES and not parts[-1].endswith(GETP)
    base_audit=inspect(parse(frozen))
    assert not base_audit["issues"]
    assert len([x for x in base_audit["tokens"] if x["name"].startswith("aga ")])==40
    white,labels=emit_white()
    assert len(white)%2==0 and len(white)>300
    updated=list(parts)
    updated[-1]+=GETP
    updated.append(white)
    assert updated[:ENTRY_WHITE-1]==parts[:ENTRY_WHITE-1]
    assert updated[ENTRY_WHITE-1]==parts[ENTRY_WHITE-1]+GETP
    assert updated[ENTRY_WHITE]==white
    newtok=tok[:-6]+token("aga fade to white",1,ENTRY_WHITE,"00")+bytes(6)
    title=b"AMOSPro AGA M13 Fade To White R35 0.10.7\0$VER: AMOSPro_AGA 0.10.7\0"
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
    assert len(named)==41
    matches=[x for x in named if x["name"]=="aga fade to white"]
    assert len(matches)==1
    assert (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,ENTRY_WHITE,"00")
    assert any(x["index"]==ENTRY_WHITE and x["parameters"]==1 and x["getp"]
               for x in audit["parameter_checks"])
    return binary,{"version":VERSION,"size":len(binary),"sha256":digest(binary),
                   "named_commands":len(named),"segments":len(updated),
                   "new_command":API[0],"labels":labels,
                   "Gate_A":"REQUIRES_CPU_CI","Gate_B":"WINUAE_PASS"}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,report=build()
    assert binary==build()[0],"R35 not deterministic"
    print("R35 in-memory candidate:",{k:v for k,v in report.items() if k!="labels"},flush=True)
    if args.emit_base64:
        print("R35_BASE64_BEGIN",flush=True)
        encoded=base64.b64encode(binary).decode("ascii")
        for i in range(0,len(encoded),76):
            print(encoded[i:i+76],flush=True)
        print("R35_BASE64_END",flush=True)
