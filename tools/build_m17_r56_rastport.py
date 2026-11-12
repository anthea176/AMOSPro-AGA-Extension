#!/usr/bin/env python3
"""M17/R56: deterministic Compiler-safe Fill/Clear derived from R55.

Build is in-memory only. The single active file for this revision is
dist/AMOSPro_AGA.Lib; prior R55/R54 and passed tests are never written.
The frozen R55 native helper is retained behind a replaced entry BRA.W,
so no pre-existing PC-relative offset or Clear BSR.W changes.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from struct import pack,unpack_from
from pathlib import Path
from audit_ap20 import inspect,parse
from compiler_relocation import (
    unpack_ap20,unwrap_native_parts,repack_ap20,wrap_native_ap20,
    is_compiler_wrapped,
)
from build_m17_blit_group_r55 import build as build_r55
from m17_r56_rastport_emit import emit_fill_r56

ROOT=Path(__file__).resolve().parents[1]
ACTIVE=ROOT/"dist/AMOSPro_AGA.Lib"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
R54_SHA="f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0"
FILL_ENTRY=20
CLEAR_ENTRY=21
LAST_ENTRY=58
TITLE=b"AMOSPro AGA M17 RastPort R56 0.13.1 current\0$VER: AMOSPro_AGA 0.13.1\0"
TITLE+=bytes(len(TITLE)%2)


def build():
    r55,old_meta=build_r55()
    assert sha256(LAST_GOOD.read_bytes()).hexdigest()==R54_SHA
    assert is_compiler_wrapped(r55)
    tokens,old=unwrap_native_parts(r55)
    assert len(old)==59
    assert old[FILL_ENTRY][:2]==bytes.fromhex("6000")
    assert old[CLEAR_ENTRY][22:24]==bytes.fromhex("6100")
    assert unpack_from(">h",old[CLEAR_ENTRY],24)[0]==-572

    new_code,labels=emit_fill_r56()
    starts=[]
    offset=0
    for entry in old:
        starts.append(offset);offset+=len(entry)
    helper_start=offset
    disp=helper_start-(starts[FILL_ENTRY]+2)
    assert disp>0 and disp<32768 and (disp&1)==0
    parts=list(old)
    parts[FILL_ENTRY]=bytes.fromhex("6000")+pack(">h",disp)+old[FILL_ENTRY][4:]
    parts[LAST_ENTRY]=old[LAST_ENTRY]+new_code
    assert parts[FILL_ENTRY][4:]==old[FILL_ENTRY][4:]
    assert parts[CLEAR_ENTRY]==old[CLEAR_ENTRY]
    assert all(parts[i]==old[i] for i in range(59) if i not in (FILL_ENTRY,LAST_ENTRY))
    assert parts[LAST_ENTRY].startswith(old[LAST_ENTRY])
    assert starts[CLEAR_ENTRY]+24+unpack_from(">h",parts[CLEAR_ENTRY],24)[0]==starts[FILL_ENTRY]

    native=repack_ap20(r55,tokens,parts,TITLE)
    result=wrap_native_ap20(native,TITLE)
    nt,new_parts=unwrap_native_parts(result)
    assert nt==tokens and new_parts==parts
    old_wrapped=unpack_ap20(r55)[1]
    new_wrapped=unpack_ap20(result)[1]
    assert len(old_wrapped)==len(new_wrapped)==60
    assert new_wrapped[:-1]==old_wrapped[:-1]
    assert len(new_wrapped[-1])<32768
    audit=inspect(parse(result))
    assert audit["issues"]==[]
    assert len([x for x in audit["tokens"] if x["name"].startswith("aga ")])==53
    return result,{
        "version":"R56 0.13.1 current, Gate A only",
        "size":len(result),"sha256":sha256(result).hexdigest(),
        "entries":60,"commands":53,"monolith_size":len(new_wrapped[-1]),
        "native_helper_start":helper_start,"native_fill_start":starts[FILL_ENTRY],
        "new_code_size":len(new_code),"disp":disp,"labels":labels,
        "gates":"A pending / B,C,D NOT TESTED",
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--emit-base64",action="store_true",
                    help="CI handoff only: print binary bytes encoded, not another file")
    args=ap.parse_args()
    raw,meta=build()
    assert build()[0]==raw
    print("R56 deterministic Compiler-safe build",{
        key:value for key,value in meta.items() if key!="labels"
    },flush=True)
    if args.emit_base64:
        print("R56_BASE64_BEGIN",flush=True)
        value=base64.b64encode(raw).decode("ascii")
        for off in range(0,len(value),128):
            print("R56_BASE64 "+value[off:off+128],flush=True)
        print("R56_BASE64_END",flush=True)
