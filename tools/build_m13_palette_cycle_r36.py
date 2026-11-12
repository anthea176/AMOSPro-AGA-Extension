#!/usr/bin/env python3
"""R36 0.10.8 deterministic AP20 builder (RGB32 Palette Cycle).

R35 WinUAE-PASS is the immutable build base. Never modifies LAST_GOOD or
dist; emits only in memory, and (on request) base64 for GitHub publication
after Gate A CPU/CI has passed.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split,digest
from audit_ap20 import parse,inspect,token
from m13_palette_cycle_r36_emit import emit_cycle,ENTRY_CYCLE,BASE_ENTRIES,GETP

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib"
BASE_SHA256="ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256="0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib"
VERSION="R36 0.10.8"
API=(("aga palette cycle",ENTRY_CYCLE,"00,0,0"),)

def build():
    frozen=BASE.read_bytes()
    assert digest(frozen)==BASE_SHA256,"R35 archive mutated"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD must match WinUAE-PASS R38"
    tok,parts,_=split(frozen)
    assert len(parts)==BASE_ENTRIES and not parts[-1].endswith(GETP)
    base_audit=inspect(parse(frozen))
    assert not base_audit["issues"]
    assert len([x for x in base_audit["tokens"] if x["name"].startswith("aga ")])==41
    cycle,labels=emit_cycle()
    assert len(cycle)%2==0 and len(cycle)>300
    updated=list(parts)
    updated[-1]+=GETP
    updated.append(cycle)
    assert updated[:ENTRY_CYCLE-1]==parts[:ENTRY_CYCLE-1]
    assert updated[ENTRY_CYCLE-1]==parts[ENTRY_CYCLE-1]+GETP
    assert updated[ENTRY_CYCLE]==cycle
    newtok=tok[:-6]+token("aga palette cycle",1,ENTRY_CYCLE,"00,0,0")+bytes(6)
    title=b"AMOSPro AGA M13 Palette Cycle R36 0.10.8\0$VER: AMOSPro_AGA 0.10.8\0"
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
    assert len(named)==42
    matches=[x for x in named if x["name"]=="aga palette cycle"]
    assert len(matches)==1
    assert (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,ENTRY_CYCLE,"00,0,0")
    assert any(x["index"]==ENTRY_CYCLE and x["parameters"]==3 and x["getp"]
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
    assert binary==build()[0],"R36 not deterministic"
    print("R36 in-memory candidate:",{k:v for k,v in report.items() if k!="labels"},flush=True)
    if args.emit_base64:
        print("R36_BASE64_BEGIN",flush=True)
        encoded=base64.b64encode(binary).decode("ascii")
        for i in range(0,len(encoded),76):
            print(encoded[i:i+76],flush=True)
        print("R36_BASE64_END",flush=True)
