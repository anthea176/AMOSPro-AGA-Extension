#!/usr/bin/env python3
"""M13 R29 0.10.1: reproducible palette-only IFF save candidate, in memory.

R28 is immutable and WinUAE-PASS. Only add GetP after its last AP20
entry and append Aga Palette Save(file$) as the sole new named token.
No other entry, binary on disk or LAST_GOOD is written by this builder.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m13_palette_save_r29_emit import emit_save

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256="ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c"
LAST_GOOD_SHA256="0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231"
OLD_ENTRIES=40
ENTRY_SAVE=40
GETP=b"GetP"
API=(("aga palette save",ENTRY_SAVE,"02"),)
VERSION="R29 0.10.1"

def build():
    raw=BASE.read_bytes()
    assert digest(raw)==BASE_SHA256,"R28 frozen archive changed"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD changed"
    tokens,old,_=split(raw)
    assert len(old)==OLD_ENTRIES and old[-1].endswith(bytes.fromhex("74004e75"))
    assert not old[-1].endswith(GETP)
    old_report=inspect(parse(raw))
    assert not old_report["issues"]
    assert len([x for x in old_report["tokens"] if x["name"].startswith("aga ")])==34
    assert "aga palette save" not in [x["name"] for x in old_report["tokens"]]
    save,labels=emit_save()
    assert len(save)>128 and len(save)%2==0
    parts=list(old)
    parts[-1]+=GETP
    parts.append(save)
    assert parts[:39]==old[:39]
    assert parts[39]==old[39]+GETP
    assert parts[40]==save
    new_tokens=tokens[:-6]+token("aga palette save",1,ENTRY_SAVE,"02")+bytes(6)
    title=b"AMOSPro AGA M13 Palette Save R29 0.10.1\0$VER: AMOSPro_AGA 0.10.1\0"
    if len(title)&1:title+=b"\0"
    code=b"".join(parts)
    payload=(pack(">4I",len(parts)*2,len(new_tokens),len(code),len(title))
             +b"\0\0AP20"+b"".join(pack(">H",len(x)//2) for x in parts)
             +new_tokens+code+title+b"\0\0")
    payload+=bytes(-len(payload)%4)
    words=pack(">I",len(payload)//4)
    candidate=raw[:20]+words+raw[24:28]+words+payload+raw[-4:]
    report=inspect(parse(candidate))
    assert not report["issues"],report["issues"]
    tok1,seg1,_=split(candidate)
    assert tok1==new_tokens and seg1==parts
    named=[t for t in report["tokens"] if t["name"].startswith("aga ")]
    assert len(named)==35
    row=next(x for x in named if x["name"]=="aga palette save")
    assert (row["instruction"],row["function"],row["signature"])==(1,ENTRY_SAVE,"02")
    assert any(x["index"]==ENTRY_SAVE and x["parameters"]==1 and x["getp"] for x in report["parameter_checks"])
    return candidate,{
        "version":VERSION, "size":len(candidate), "sha256":digest(candidate),
        "segments":len(parts),"named_commands":len(named),
        "new_command":API[0],"unchanged_entries":tuple(range(39)),
        "prior_final_entry_getp_only":39,"labels":labels,
        "Gate_A":"REQUIRES_CPU_CI","Gate_B":"NOT_TESTED",
    }

if __name__=="__main__":
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--emit-base64",action="store_true")
    args=cli.parse_args()
    data,meta=build()
    assert data==build()[0],"R29 builder not deterministic"
    print("M13 R29 candidate in-memory:",meta,flush=True)
    if args.emit_base64:
        print("R29_BASE64_BEGIN",flush=True)
        print(base64.b64encode(data).decode("ascii"),flush=True)
        print("R29_BASE64_END",flush=True)
