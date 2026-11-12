#!/usr/bin/env python3
"""M16/R47 experimental Aga Image Capture compiler-safe candidate builder.

Derive native parts from the official promoted R46 C1, append the new
capture entry and AP20 token, and FINALLY wrap via compiler_relocation.
Do not install or promote candidate here. WinUAE/Compiler runtime Gates
are NOT verified, particularly AMOS main bank Rjsr ABI 297/300/316/319.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
from pathlib import Path

from audit_ap20 import parse, inspect, token
from compiler_relocation import (native_from_promoted, unpack_ap20,
                                 repack_ap20, wrap_native_ap20,
                                 unwrap_native_parts, is_compiler_wrapped)
from m16_capture_r47_emit import emit_capture
from active_library import verify_active

ROOT=Path(__file__).resolve().parents[1]
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
CURRENT=ROOT/"dist/AMOSPro_AGA.Lib"
LAST_GOOD_SHA="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
ENTRY=56
API=("aga image capture",1,ENTRY,"00,0,0,0,0,0")
NAME="AMOSPro AGA M16 Image Capture R47 0.12.2 experimental"


def build() -> tuple[bytes,dict]:
    stable=LAST_GOOD.read_bytes()
    assert sha256(stable).hexdigest()==LAST_GOOD_SHA
    verify_active(ROOT)  # historical R47 is always reconstructed from LAST_GOOD
    old_tokens,old_parts,_=unpack_ap20(stable)
    assert len(old_parts)==57 and is_compiler_wrapped(stable)
    rawtitle=(NAME+" NATIVE INPUT\0$VER: AMOSPro_AGA 0.12.2\0").encode("ascii")
    rawtitle+=bytes(len(rawtitle)%2)
    native=native_from_promoted(stable,rawtitle)
    tok,parts,_=unpack_ap20(native)
    assert tok==old_tokens and len(parts)==56 and not is_compiler_wrapped(native)
    original_parts=list(parts)
    assert not parts[-1].endswith(b"GetP")
    assembly, labels=emit_capture()
    assert len(assembly)%2==0 and len(assembly)>700
    assert b"\xfe\x11\xf7\0" in assembly, "missing AMOS main-library Rjsr relocation"
    parts[-1]=parts[-1]+b"GetP"
    parts.append(assembly)
    newtok=tok[:-6]+token(*API)+bytes(6)
    raw=repack_ap20(native,newtok,parts,rawtitle)
    assert unpack_ap20(raw)==(newtok,parts,rawtitle)
    title=(NAME+"\0$VER: AMOSPro_AGA 0.12.2\0").encode("ascii")
    title+=bytes(len(title)%2)
    binary=wrap_native_ap20(raw,title)
    got_tokens,wrapped,_=unpack_ap20(binary)
    assert got_tokens==newtok and len(wrapped)==58
    assert unwrap_native_parts(binary)==(newtok,parts)
    assert parts[:55]==original_parts[:55]
    assert parts[55]==original_parts[55]+b"GetP"
    assert wrapped[-1][32:]==b"".join(parts)
    report=inspect(parse(binary))
    assert not report["issues"],report["issues"]
    commands=[x for x in report["tokens"] if x["name"].startswith("aga ")]
    assert len(commands)==51
    cmd=[x for x in commands if x["name"]==API[0]]
    assert len(cmd)==1
    assert (cmd[0]["instruction"],cmd[0]["function"],cmd[0]["signature"])==API[1:]
    assert any(x["index"]==ENTRY and x["parameters"]==6 and x["getp"]
               for x in report["parameter_checks"])
    assert binary!=stable and len(binary)>len(stable)
    return binary,dict(
        version="M16 R47 0.12.2 experimental",
        bytes=len(binary),sha256=sha256(binary).hexdigest(),
        commands=51,segments=58,entry=ENTRY,
        native_capture_bytes=len(assembly),labels=labels,
        CPU_core="325 cases PASS on CI",
        bank_bridge="ABI NOT YET VALIDATED in WinUAE",
        compiler="wrapper structure PASS is NOT Compiler Gate C",
    )


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,meta=build()
    other,meta2=build()
    assert binary==other and meta==meta2, "non-deterministic candidate"
    print("M16/R47 CAPTURE COMPILER-WRAPPED CANDIDATE STATIC PASS:",
          {k:v for k,v in meta.items() if k!="labels"})
    print("Candidate IS NOT LAST_GOOD and must NOT be installed without WinUAE")
    if args.emit_base64:
        print("M16_R47_CAPTURE_LIB_BASE64_BEGIN")
        print(base64.b64encode(binary).decode("ascii"))
        print("M16_R47_CAPTURE_LIB_BASE64_END")


if __name__=="__main__":
    main()
