#!/usr/bin/env python3
"""M17/R57: replace R55 helper IN PLACE, with exact Compiler-safe footprint.

R56 appended its 580-byte RastPort implementation after 620 bytes of
unreachable R55 helper. R57 uses the user-proven R55 Compiler bridge layout
without moving ANY existing native entry, stub or dispatcher offset:
- original Fill BRA.W remains unchanged and targets the old helper start;
- original R55 helper is overwritten by R56's 580 bytes plus 40 NOP bytes;
- Clear's BSR.W and all other entries are byte-for-byte unchanged.

This is a *compiler-relocation hypothesis test*, not a claim of runtime
compatibility. Only dist/AMOSPro_AGA.Lib may be the installable current binary.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path
from struct import unpack_from

from audit_ap20 import inspect, parse
from compiler_relocation import (
    is_compiler_wrapped, unpack_ap20, unwrap_native_parts,
    repack_ap20, wrap_native_ap20,
)
from build_m17_blit_group_r55 import build as build_r55
from m17_blit_group_r55_emit import emit_fill_grouped
from m17_r56_rastport_emit import emit_fill_r56

ROOT=Path(__file__).resolve().parents[1]
ACTIVE=ROOT/"dist/AMOSPro_AGA.Lib"
R54_SOURCE=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib"
SHA_R54="f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0"
SHA_R55="97f48ccb946ced9bad0b661cbabff00440a4e5a07aeef49021b215b269fcf9ad"
FILL_ENTRY,CLEAR_ENTRY,LAST_ENTRY=20,21,58
TITLE=b"AMOSPro AGA M17 RastPort R57 0.13.2 current\0$VER: AMOSPro_AGA 0.13.2\0"
TITLE+=bytes(len(TITLE)%2)


def build():
    assert sha256(R54_SOURCE.read_bytes()).hexdigest()==SHA_R54, "LAST_GOOD changed"
    stable, r55meta=build_r55()
    assert sha256(stable).hexdigest()==SHA_R55, "R55 base must match user-tested compiler PASS"
    assert is_compiler_wrapped(stable)
    tokens, parts55=unwrap_native_parts(stable)
    assert len(parts55)==59
    group,_=emit_fill_grouped()
    rast,labels=emit_fill_r56()
    assert len(group)==620 and len(rast)==580, "native layout drift"
    assert parts55[LAST_ENTRY].endswith(group)
    assert parts55[FILL_ENTRY][:2]==bytes.fromhex("6000")
    assert unpack_from(">h",parts55[CLEAR_ENTRY],24)[0]==-572
    padding=bytes.fromhex("4e71")*20
    replace=rast+padding
    assert len(replace)==len(group) and len(replace)==620
    starts=[]
    at=0
    for entry in parts55:
        starts.append(at);at+=len(entry)
    assert at==30748, "R55 native bytes shifted"
    old_helper_start=at-len(group)
    assert old_helper_start==30128
    fill_jump=starts[FILL_ENTRY]+2+unpack_from(">h",parts55[FILL_ENTRY],2)[0]
    assert fill_jump==old_helper_start
    assert starts[CLEAR_ENTRY]+24+unpack_from(">h",parts55[CLEAR_ENTRY],24)[0]==starts[FILL_ENTRY]

    parts=list(parts55)
    parts[LAST_ENTRY]=parts55[LAST_ENTRY][:-len(group)]+replace
    assert parts[FILL_ENTRY]==parts55[FILL_ENTRY]
    assert parts[CLEAR_ENTRY]==parts55[CLEAR_ENTRY]
    assert all(parts[i]==parts55[i] for i in range(59) if i!=LAST_ENTRY)
    assert len(parts[LAST_ENTRY])==len(parts55[LAST_ENTRY])

    native=repack_ap20(stable,tokens,parts,TITLE)
    result=wrap_native_ap20(native,TITLE)
    newtokens,newparts=unwrap_native_parts(result)
    assert newtokens==tokens and newparts==parts
    a=unpack_ap20(stable)[1]
    b=unpack_ap20(result)[1]
    assert len(a)==len(b)==60 and b[:-1]==a[:-1], "AP20 stubs not preserved"
    assert len(a[-1])==len(b[-1])==30780
    assert b[-1][:32]==a[-1][:32], "Compiler dispatcher changed"
    assert b[-1][32:32+old_helper_start]==a[-1][32:32+old_helper_start], "old native code changed"
    assert b[-1][-620:]==replace and b[-1][32:][-620:-40]==rast
    report=inspect(parse(result))
    assert not report["issues"]
    assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==53
    return result,{
        "version":"M17 R57 0.13.2 (Gate A CPU only)",
        "sha256":sha256(result).hexdigest(),"size":len(result),
        "monolith":len(b[-1]),"commands":53,"ap20_entries":60,
        "fill_native_start":starts[FILL_ENTRY],"old_helper_start":old_helper_start,
        "new_helper_bytes":len(rast),"nop_padding_bytes":len(padding),
        "labels":labels,
        "gate_A":"PENDING CPU/CI", "gate_B":"NOT TESTED", "gate_C":"NOT TESTED",
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-base64", action="store_true",
                    help="CI log transfer into the single active dist library only")
    args=ap.parse_args()
    candidate,info=build()
    assert build()[0]==candidate, "R57 builder not deterministic"
    print("R57 deterministic build", {k:v for k,v in info.items() if k!="labels"})
    if args.emit_base64:
        print("R57_BASE64_BEGIN")
        value=base64.b64encode(candidate).decode("ascii")
        for at in range(0,len(value),128):
            print("R57_BASE64 "+value[at:at+128])
        print("R57_BASE64_END")
