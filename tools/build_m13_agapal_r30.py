#!/usr/bin/env python3
"""R30 0.10.2: deterministic AP20 candidate in memory, one new function.

Base R29 is WinUAE-validated and protected in LAST_GOOD. The new entry
accepts a trusted AMOS Start(bank) DATA pointer and a palette slot count.
Does not write dist files unless a separate Gate A-approved release step
explicitly publishes the emitted bytes.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split,digest
from audit_ap20 import parse,inspect,token
from m13_agapal_r30_emit import emit_init,ENTRY_INDEX,BASE_ENTRIES

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib"
BASE_SHA256="fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
LAST_GOOD_SHA256=BASE_SHA256
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib"
GETP=b"GetP"
API=(("aga palette bank init",ENTRY_INDEX,"00,0"),)
VERSION="R30 0.10.2"

def build():
    original=BASE.read_bytes()
    assert digest(original)==BASE_SHA256,"frozen R29 archive changed"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"R29 LAST_GOOD changed"
    tokens,parts,_=split(original)
    assert len(parts)==BASE_ENTRIES
    assert not parts[-1].endswith(GETP)
    a=inspect(parse(original))
    assert not a["issues"]
    assert len([t for t in a["tokens"] if t["name"].startswith("aga ")])==35
    assert not any(t["name"]==API[0][0] for t in a["tokens"])
    new_segment,labels=emit_init()
    assert len(new_segment)%2==0 and len(new_segment)>150
    blocks=list(parts)
    blocks[-1]+=GETP
    blocks.append(new_segment)
    assert blocks[:40]==parts[:40]
    assert blocks[40]==parts[40]+GETP
    assert blocks[41]==new_segment

    new_tokens=tokens[:-6]+token("aga palette bank init",1,ENTRY_INDEX,"00,0")+bytes(6)
    title=b"AMOSPro AGA M13 AGAPAL Bank Init R30 0.10.2\0$VER: AMOSPro_AGA 0.10.2\0"
    if len(title)%2:title+=b"\0"
    code=b"".join(blocks)
    payload=(pack(">4I",2*len(blocks),len(new_tokens),len(code),len(title))
        +b"\0\0AP20"+b"".join(pack(">H",len(x)//2) for x in blocks)
        +new_tokens+code+title+b"\0\0")
    payload+=bytes(-len(payload)%4)
    size=pack(">I",len(payload)//4)
    binary=original[:20]+size+original[24:28]+size+payload+original[-4:]
    report=inspect(parse(binary))
    assert not report["issues"],report["issues"]
    tok,seg,_=split(binary)
    assert tok==new_tokens and seg==blocks
    named=[x for x in report["tokens"] if x["name"].startswith("aga ")]
    assert len(named)==36
    matches=[x for x in named if x["name"]=="aga palette bank init"]
    assert len(matches)==1
    assert (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,41,"00,0")
    assert any(x["index"]==41 and x["parameters"]==2 and x["getp"] for x in report["parameter_checks"])
    return binary,{
        "version":VERSION,"size":len(binary),"sha256":digest(binary),
        "named_commands":len(named),"segments":len(blocks),
        "new_command":API[0],"labels":labels,
        "Gate_A":"REQUIRES_CPU_CI","Gate_B":"NOT_TESTED",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    binary,info=build()
    assert binary==build()[0],"builder not deterministic"
    print("R30 candidate in-memory:",info,flush=True)
    if args.emit_base64:
        print("R30_BASE64_BEGIN",flush=True)
        print(base64.b64encode(binary).decode("ascii"),flush=True)
        print("R30_BASE64_END",flush=True)
