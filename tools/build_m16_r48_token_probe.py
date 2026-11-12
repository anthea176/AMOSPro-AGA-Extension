#!/usr/bin/env python3
"""R48 token/ABI DIAGNOSTIC ONLY — never a functional capture library.

Controlled R47 comparison: retain the *exact* six-argument token, original
AP20 function index, original 58 entries, old functions, and 32,012-byte
library size. Replace ONLY the R47 new native routine with a side-effect-free
parameter probe. This distinguishes parser/token link from the R47 bank code.

R46 C1 LAST_GOOD and the archived R47 candidate are read-only sources.
NO AMOS bank calls, I/O, allocations, screens, swaps, or bank changes.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
from pathlib import Path
from audit_ap20 import parse, inspect
from compiler_relocation import (native_from_promoted, unpack_ap20,
     repack_ap20, wrap_native_ap20, unwrap_native_parts, is_compiler_wrapped)
from m68k_emit import Code,D,POST,I
from active_library import verify_active

ROOT=Path(__file__).resolve().parents[1]
GOOD=ROOT/"dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
OFFICIAL=ROOT/"dist/AMOSPro_AGA.Lib"
R47=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.2_IMAGE_CAPTURE_R47_CANDIDATE.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.3_R48_TOKEN_ABI_PROBE.Lib"
GOOD_SHA="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
R47_SHA="a550e9662cda1890aa8331c6e849e702300e6070e8e2caaf2fab9918613944d5"
SIZE_R47=32012
# Exact same token/name/function/signature as the historical R47.
TOKEN_NAME="aga image capture"
VERSION="AMOSPro AGA M16 Image Capture R48 0.12.3 experimental"

def native_probe():
    """D3=-1, A3+ = (h,w,y,x,bank). Returns D3=1 only for 11/16/16/16/16/-1.
    All five longwords are ALWAYS consumed. D2=0 integer. Preserves all
    other AMOS registers, except A3 per function ABI.
    """
    c=Code()
    c.raw("48e7efee")                 # native AMOS AP20 preserved registers
    for register in (7,6,5,4,0):       # H,W,Y,X,Bank from (A3)+
        c.move(POST(3),D(register))
    for register,value in ((3,-1),(7,16),(6,16),(5,16),(4,16),(0,11)):
        c.imm("cmp",value,D(register))
        c.branch(6,"bad")              # BNE; do not touch banks/screens
    c.move(I(1),D(3))
    c.branch(0,"done")
    c.label("bad")
    c.move(I(0),D(3))
    c.label("done")
    c.raw("4cdf77f7")                 # restore D0-D1,D4-D7,A0-A2,A4-A6
    c.raw("74004e75")                 # D2=0 integer, RTS
    result=c.out()
    assert result and len(result)%2==0
    return result

def build():
    stable=GOOD.read_bytes()
    assert hashlib.sha256(stable).hexdigest()==GOOD_SHA
    verify_active(ROOT)  # active candidate allowed; frozen C1 source is LAST_GOOD
    frozen=R47.read_bytes()
    assert hashlib.sha256(frozen).hexdigest()==R47_SHA
    assert len(frozen)==SIZE_R47

    # Recover the exact historical R47 token/entry boundaries; no guesswork.
    r47_tokens,r47_parts,r47_title=unpack_ap20(frozen)
    assert len(r47_parts)==58 and is_compiler_wrapped(frozen)
    native_tokens,native_parts=unwrap_native_parts(frozen)
    assert native_tokens==r47_tokens and len(native_parts)==57
    assert native_parts[55].endswith(b"GetP")
    audit=inspect(parse(frozen))
    assert not audit["issues"]
    token=[t for t in audit["tokens"] if t["name"]==TOKEN_NAME]
    assert len(token)==1
    assert (token[0]["instruction"],token[0]["function"],token[0]["signature"])==(1,56,"00,0,0,0,0,0")
    assert len([t for t in audit["tokens"] if t["name"].startswith("aga ")])==51

    # New title has precisely the same byte length as R47's.
    old_title=r47_title.decode("ascii")
    new_title=(old_title.replace("R47 0.12.2","R48 0.12.3")
                        .replace("AGA 0.12.2","AGA 0.12.3")).encode("ascii")
    assert len(new_title)==len(r47_title) and new_title!=r47_title
    raw_title=new_title
    # Use R46 C1 as immutable baseline and compare to R47 native history.
    native=native_from_promoted(stable,raw_title)
    old_tokens,base_parts,_=unpack_ap20(native)
    assert r47_tokens.startswith(old_tokens[:-6]) and len(r47_tokens)>len(old_tokens)
    assert len(base_parts)==56 and base_parts[:55]==native_parts[:55]
    assert native_parts[55]==base_parts[55]+b"GetP"

    # Same R47 native boundaries, only new terminal routine differs.
    core=native_probe()
    restored=list(native_parts)
    candidate=None
    # Match the complete historical R47 HUNK length exactly, thus excluding
    # gross library-size difference from the controlled parser comparison.
    for pad_bytes in range(0,SIZE_R47,2):
        restored[-1]=core + b"\x4e\x71"*(pad_bytes//2)
        raw=repack_ap20(native,r47_tokens,restored,raw_title)
        wrapped=wrap_native_ap20(raw,new_title)
        if len(wrapped)>=SIZE_R47:
            if len(wrapped)==SIZE_R47:
                candidate=wrapped
            break
    assert candidate is not None, "Cannot match R47 size with NOP padding"
    tok,parts,_=unpack_ap20(candidate)
    assert len(parts)==58 and tok==r47_tokens
    assert unwrap_native_parts(candidate)==(r47_tokens,restored)
    assert parts[:56]==r47_parts[:56], "Existing AMOS function stubs were changed"
    assert candidate!=frozen and candidate!=stable
    report=inspect(parse(candidate))
    assert not report["issues"],report["issues"]
    assert [t for t in report["tokens"] if t["name"].startswith("aga ")]==[
      t for t in audit["tokens"] if t["name"].startswith("aga ")]
    if ARCHIVE.is_file():
        assert ARCHIVE.read_bytes()==candidate,"Frozen R48 artifact differs"
    return candidate, dict(size=len(candidate), sha256=hashlib.sha256(candidate).hexdigest(),
       tokens=51, ap20_entries=len(parts), routine_probe_bytes=len(core),
       nop_padding=pad_bytes, gate="STATIC ONLY, WinUAE B and Compiler C UNTESTED")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--emit-base64",action="store_true")
    a=p.parse_args()
    raw,meta=build()
    raw2,meta2=build()
    assert raw==raw2 and meta==meta2
    print("R48 CONTROLLED TOKEN/ABI PROBE STATIC PASS",meta,flush=True)
    if a.emit_base64:
        print("R48_BINARY_BEGIN",flush=True)
        print(base64.b64encode(raw).decode("ascii"),flush=True)
        print("R48_BINARY_END",flush=True)

if __name__=="__main__":
    main()
