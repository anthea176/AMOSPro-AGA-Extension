#!/usr/bin/env python3
"""M16/R48 experimental five-argument capture candidate, R47 parser fix.

Derive from untouched R46 C1 LAST_GOOD, never from R47's unusable 6-param
candidate. Capture and mask setter live together inside ONE wrapped AP20
Compiler-safe segment; never distribute the native parts directly.
Gate A CPU/CI is not WinUAE Gate B, nor Compiler Gate C.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import argparse
import base64
from audit_ap20 import parse,inspect,token,amos20_parameter_limit_errors
from compiler_relocation import (native_from_promoted,unpack_ap20,
    repack_ap20,wrap_native_ap20,unwrap_native_parts,is_compiler_wrapped)
from m16_capture_r48_emit import emit_capture,emit_mask_setter

ROOT=Path(__file__).resolve().parents[1]
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
CURRENT=ROOT/"dist/AMOSPro_AGA.Lib"
EXPECTED_SHA="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
API_CAPTURE=("aga image capture",1,56,"00,0,0,0,0")
API_MASK=("aga image capture mask",1,57,"00")
TITLE="AMOSPro AGA M16 Image Capture R48 0.12.3 experimental"

def build():
    stable=LAST_GOOD.read_bytes()
    assert sha256(stable).hexdigest()==EXPECTED_SHA
    assert CURRENT.read_bytes()==stable, "R46 C1 official must remain untouched"
    old_tokens,old_wrapped,_=unpack_ap20(stable)
    assert len(old_wrapped)==57 and is_compiler_wrapped(stable)
    raw_title=(TITLE+" NATIVE INPUT\0$VER: AMOSPro_AGA 0.12.3\0").encode("ascii")
    raw_title+=bytes(len(raw_title)%2)
    native=native_from_promoted(stable,raw_title)
    tokens,parts,_=unpack_ap20(native)
    assert tokens==old_tokens and len(parts)==56 and not is_compiler_wrapped(native)
    original=list(parts)
    capture,labels=emit_capture()
    setter=emit_mask_setter(capture,labels)
    assert capture[labels["capture_mask_index"]:labels["capture_mask_index"]+4]==b"\xff"*4
    assert len(capture)%2==len(setter)%2==0
    parts[-1]+=b"GetP"  # parameter collection of Capture(5)
    parts.append(capture+b"GetP")  # parameter collection of Mask(1)
    parts.append(setter)
    new_tokens=tokens[:-6]+token(*API_CAPTURE)+token(*API_MASK)+bytes(6)
    raw=repack_ap20(native,new_tokens,parts,raw_title)
    title=(TITLE+"\0$VER: AMOSPro_AGA 0.12.3\0").encode("ascii")
    title+=bytes(len(title)%2)
    candidate=wrap_native_ap20(raw,title)
    tok,wrapped,_=unpack_ap20(candidate)
    assert tok==new_tokens and len(wrapped)==59
    assert unwrap_native_parts(candidate)==(new_tokens,parts)
    assert parts[:55]==original[:55]
    assert parts[55]==original[55]+b"GetP"
    assert wrapped[-1][32:]==b"".join(parts)
    report=inspect(parse(candidate))
    assert not report["issues"],report["issues"]
    assert not amos20_parameter_limit_errors(parse(candidate))
    commands=[x for x in report["tokens"] if x["name"].startswith("aga ")]
    assert len(commands)==52
    for api,nargs in ((API_CAPTURE,5),(API_MASK,1)):
        named=[x for x in commands if x["name"]==api[0]]
        assert len(named)==1
        assert (named[0]["instruction"],named[0]["function"],named[0]["signature"])==api[1:]
        assert any(x["index"]==api[2] and x["parameters"]==nargs and x["getp"]
                   for x in report["parameter_checks"])
    assert len(wrapped[-1])<32768
    assert len(candidate)>len(stable)
    return candidate,dict(version="M16 R48 v0.12.3 EXPERIMENTAL",
                          bytes=len(candidate),sha256=sha256(candidate).hexdigest(),
                          commands=52,segments=59,
                          native_capture_bytes=len(capture),
                          native_setter_bytes=len(setter),
                          monolith_bytes=len(wrapped[-1]),
                          labels=labels,
                          gate_b="NOT TESTED",gate_c="NOT TESTED")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    candidate,info=build()
    other,info2=build()
    assert candidate==other and info==info2
    print("R48 FIVE-ARGUMENT PARSER/COMPILER-SAFE STRUCTURE PASS",
          {k:v for k,v in info.items() if k!="labels"})
    print("NO RUNTIME CLAIM: WinUAE and AMOS Compiler still untested")
    if args.emit_base64:
        print("R48_CANDIDATE_BASE64_BEGIN")
        print(base64.b64encode(candidate).decode("ascii"))
        print("R48_CANDIDATE_BASE64_END")

if __name__=="__main__":
    main()
