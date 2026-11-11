#!/usr/bin/env python3
"""M12 R27 0.9.3: no-new-token Safe-aware Blit Copy/Fill/Clear candidate.

Build *in memory* from the immutable R26 0.9.2 WinUAE-PASS archive.
The live library, R26/R25/R24 archives and LAST_GOOD are never written.
Only segments 19 Copy, 20 Fill, and 21 Clear's internal BSR displacement
may change; remaining 34 AP20 segments and the token table stay identical.
Gate A CPU must pass before any R27 binary is published.
"""
import argparse
import base64
from pathlib import Path

from ap20_utils import split, rebuild, digest
from audit_ap20 import parse, inspect
from build_m6_blit_copy_r13 import emit_copy
from build_m6_blit_fill_r14 import emit_fill
from build_m6_blit_clear_r15 import emit_clear
from m12_blit_safe_r27_emit import emit_copy_safe, emit_fill_safe

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256="0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287"
LAST_GOOD_SHA256="e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3"
COPY_ENTRY=19
FILL_ENTRY=20
CLEAR_ENTRY=21
TEXT_ENTRY=36
GETP=b"GetP"
VERSION="R27 0.9.3"

def build():
    frozen=BASE.read_bytes()
    assert digest(frozen)==BASE_SHA256, "R26 WinUAE-PASS archive changed"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256, "LAST_GOOD changed"
    tokens,original,_=split(frozen)
    assert len(original)==37 and original[TEXT_ENTRY], "R26 AP20 layout changed"
    copy_orig,_=emit_copy()
    fill_orig,_=emit_fill()
    clear_orig,_=emit_clear(len(fill_orig))
    assert original[COPY_ENTRY]==copy_orig+GETP, "R26 Copy not R13 byte-exact"
    assert original[FILL_ENTRY]==fill_orig+GETP, "R26 Fill not R14 byte-exact"
    assert original[CLEAR_ENTRY]==clear_orig, "R26 Clear wrapper changed"
    copy_safe,labels_copy=emit_copy_safe()
    fill_safe,labels_fill=emit_fill_safe()
    clear_safe,details_clear=emit_clear(len(fill_safe))
    assert len(copy_safe)>len(copy_orig), "Copy guard missing"
    assert len(fill_safe)>len(fill_orig), "Fill guard missing"
    assert clear_safe!=clear_orig, "Clear BSR was not updated"
    updated=list(original)
    updated[COPY_ENTRY]=copy_safe+GETP
    updated[FILL_ENTRY]=fill_safe+GETP
    updated[CLEAR_ENTRY]=clear_safe
    assert all(updated[i]==original[i] for i in range(37) if i not in
               (COPY_ENTRY,FILL_ENTRY,CLEAR_ENTRY)), "non-target code mutated"
    title=(b"AMOSPro AGA M12 Safe Blitter R27 0.9.3\0"
           b"$VER: AMOSPro_AGA 0.9.3\0")
    if len(title)&1: title+=b"\0"
    candidate=rebuild(frozen,updated,title)
    new_tokens,new_parts,_=split(candidate)
    assert new_tokens==tokens and new_parts==updated
    audit=inspect(parse(candidate))
    assert not audit["issues"],audit["issues"]
    named=[r for r in audit["tokens"] if r["name"].startswith("aga ")]
    assert len(named)==31 and len([r for r in named if r["name"]=="aga text"])==1
    assert len(updated)==37
    return candidate,{
        "version":VERSION,"size":len(candidate),"sha256":digest(candidate),
        "segments":len(updated),"named_commands":len(named),
        "changed_segments":(COPY_ENTRY,FILL_ENTRY,CLEAR_ENTRY),
        "copy_guard_labels":labels_copy,"fill_guard_labels":labels_fill,
        "clear_wrapper":details_clear,
        "Gate_A":"REQUIRES_CPU_CI","Gate_B_WinUAE":"NOT_TESTED",
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,info=build()
    assert binary==build()[0], "R27 not deterministic"
    print("M12 R27 in-memory candidate:",info,flush=True)
    if args.emit_base64:
        print("R27_BASE64_BEGIN",flush=True)
        print(base64.b64encode(binary).decode("ascii"),flush=True)
        print("R27_BASE64_END",flush=True)
