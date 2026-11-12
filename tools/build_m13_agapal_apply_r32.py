#!/usr/bin/env python3
"""R32 0.10.4 deterministic in-memory AP20 builder.

Append ONLY the approved function Aga Palette Bank Apply(Start(bank),index)
to frozen WinUAE-PASS R31. This builder never writes dist/ or LAST_GOOD.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split,digest
from audit_ap20 import parse,inspect,token
from m13_agapal_apply_r32_emit import emit_apply,ENTRY_APPLY,BASE_ENTRIES,GETP

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib"
BASE_SHA256="0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256="0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib"
API=(("aga palette bank apply",ENTRY_APPLY,"00,0"),)
VERSION="R32 0.10.4"

def build():
    original=BASE.read_bytes()
    assert digest(original)==BASE_SHA256,"R31 WinUAE-PASS frozen archive changed"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD must match WinUAE-PASS R38"
    tok,parts,_=split(original)
    assert len(parts)==BASE_ENTRIES and not parts[-1].endswith(GETP)
    baseline=inspect(parse(original))
    assert not baseline["issues"]
    assert len([a for a in baseline["tokens"] if a["name"].startswith("aga ")])==37
    assert not any(a["name"]==API[0][0] for a in baseline["tokens"])
    apply,labels=emit_apply()
    assert len(apply)%2==0 and len(apply)>300
    updated=list(parts)
    updated[-1]+=GETP
    updated.append(apply)
    assert updated[:42]==parts[:42]
    assert updated[42]==parts[42]+GETP
    assert updated[43]==apply
    newtok=tok[:-6]+token("aga palette bank apply",1,ENTRY_APPLY,"00,0")+bytes(6)
    title=b"AMOSPro AGA M13 AGAPAL Bank Apply R32 0.10.4\0$VER: AMOSPro_AGA 0.10.4\0"
    if len(title)%2:title+=b"\0"
    code=b"".join(updated)
    payload=(pack(">4I",2*len(updated),len(newtok),len(code),len(title))
        +b"\0\0AP20"+b"".join(pack(">H",len(x)//2) for x in updated)
        +newtok+code+title+b"\0\0")
    payload+=bytes(-len(payload)%4)
    size=pack(">I",len(payload)//4)
    binary=original[:20]+size+original[24:28]+size+payload+original[-4:]
    report=inspect(parse(binary))
    assert not report["issues"],report["issues"]
    actualtok,segments,_=split(binary)
    assert actualtok==newtok and segments==updated
    named=[a for a in report["tokens"] if a["name"].startswith("aga ")]
    assert len(named)==38
    rows=[a for a in named if a["name"]=="aga palette bank apply"]
    assert len(rows)==1 and (rows[0]["instruction"],rows[0]["function"],rows[0]["signature"])==(1,43,"00,0")
    assert any(a["index"]==43 and a["parameters"]==2 and a["getp"] for a in report["parameter_checks"])
    return binary,{
        "version":VERSION,"size":len(binary),"sha256":digest(binary),
        "named_commands":len(named),"segments":len(updated),
        "new_command":API[0],"labels":labels,
        "Gate_A":"REQUIRES_CPU_CI","Gate_B":"WINUAE_PASS_SCENARIO"
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,report=build()
    assert binary==build()[0],"R32 builder not deterministic"
    print("R32 candidate in-memory:",report,flush=True)
    if args.emit_base64:
        print("R32_BASE64_BEGIN",flush=True)
        print(base64.b64encode(binary).decode("ascii"),flush=True)
        print("R32_BASE64_END",flush=True)
