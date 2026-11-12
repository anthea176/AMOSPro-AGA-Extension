#!/usr/bin/env python3
"""R33 0.10.5 deterministic AP20 builder (AGAPAL blocking Fade To Bank).

R32 WinUAE-PASS is the immutable build base. Never modifies LAST_GOOD or
dist; emits only in memory, and (on request) base64 for GitHub publication
after Gate A CPU/CI has passed.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split,digest
from audit_ap20 import parse,inspect,token
from m13_agapal_fade_r33_emit import emit_fade,ENTRY_FADE,BASE_ENTRIES,GETP

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib"
BASE_SHA256="0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256="9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib"
VERSION="R33 0.10.5"
API=(("aga fade to bank",ENTRY_FADE,"00,0,0"),)

def build():
    frozen=BASE.read_bytes()
    assert digest(frozen)==BASE_SHA256,"R32 archive mutated"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD must match WinUAE-PASS R38"
    tok,parts,_=split(frozen)
    assert len(parts)==BASE_ENTRIES and not parts[-1].endswith(GETP)
    base_audit=inspect(parse(frozen))
    assert not base_audit["issues"]
    assert len([x for x in base_audit["tokens"] if x["name"].startswith("aga ")])==38
    fade,labels=emit_fade()
    assert len(fade)%2==0 and len(fade)>500
    updated=list(parts)
    updated[-1]+=GETP
    updated.append(fade)
    assert updated[:ENTRY_FADE-1]==parts[:ENTRY_FADE-1]
    assert updated[ENTRY_FADE-1]==parts[ENTRY_FADE-1]+GETP
    assert updated[ENTRY_FADE]==fade
    newtok=tok[:-6]+token("aga fade to bank",1,ENTRY_FADE,"00,0,0")+bytes(6)
    title=b"AMOSPro AGA M13 AGAPAL Fade To Bank R33 0.10.5\0$VER: AMOSPro_AGA 0.10.5\0"
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
    assert len(named)==39
    matches=[x for x in named if x["name"]=="aga fade to bank"]
    assert len(matches)==1
    assert (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,ENTRY_FADE,"00,0,0")
    assert any(x["index"]==ENTRY_FADE and x["parameters"]==3 and x["getp"]
               for x in audit["parameter_checks"])
    return binary,{"version":VERSION,"size":len(binary),"sha256":digest(binary),
                   "named_commands":len(named),"segments":len(updated),
                   "new_command":API[0],"labels":labels,
                   "Gate_A":"REQUIRES_CPU_CI","Gate_B":"WINUAE_PASS_SCENARIO"}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,report=build()
    assert binary==build()[0],"R33 not deterministic"
    print("R33 in-memory candidate:",{k:v for k,v in report.items() if k!="labels"},flush=True)
    if args.emit_base64:
        print("R33_BASE64_BEGIN",flush=True)
        encoded=base64.b64encode(binary).decode("ascii")
        for i in range(0,len(encoded),76):
            print(encoded[i:i+76],flush=True)
        print("R33_BASE64_END",flush=True)
