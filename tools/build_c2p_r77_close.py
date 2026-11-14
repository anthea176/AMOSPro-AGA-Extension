#!/usr/bin/env python3
"""Deterministic R77 C2P Close candidate, APPEND ONLY to SHA-pinned R76.

No changed native entries 0..71 except adding AP20 GETP terminator to 71.
In particular entry08 code, seven mouse/key LEAs, and static input-state data
remain byte-identical. R73 LAST_GOOD is never written or modified.

Without --emit-base64 this builder writes no files.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from build_c2p_r76_rpg_fix import (
    build as build_r76, state_offset, SITES,
)
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from c2p_r77_close_emit import emit_close

R76_SHA="9e0a77f3e69c06cfcc96b00b8dc1f23122d559f617beac8762310c5f4bb53897"
API=("aga c2p close",1,72,"0")
TITLE=b"AMOSPro AGA C2P Close R77 0.13.22 candidate\0$VER: AMOSPro_AGA 0.13.22\0"
TITLE+=bytes(len(TITLE)&1)

def build():
    previous,oldmeta=build_r76()
    assert sha256(previous).hexdigest()==R76_SHA, "R76 native source pin drift"
    tokens,original=unwrap_native_parts_v2(previous)
    assert len(original)==72 and not original[-1].endswith(GETP)
    assert state_offset(original)==12070, "R76 input-state target changed"
    assert all(original[e][p:p+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
               for e,p,op in SITES)
    assert_native_links(original[:70]);check_cross_r74(original[:70])
    code,labels=emit_close()
    assert 0<len(code)<1500
    parts=list(original)
    parts[-1]+=GETP
    parts.append(code)
    assert len(parts)==73 and parts[:71]==original[:71]
    assert parts[71]==original[71]+GETP and parts[72]==code
    assert state_offset(parts)==12070, "appending R77 shifted legacy data!"
    ntokens=tokens[:-6]+token(*API)+bytes(6)
    native=repack_ap20(previous,ntokens,parts,TITLE)
    current=wrap_native_ap20_v2(native,TITLE)
    again_tokens,again_parts=unwrap_native_parts_v2(current)
    assert again_tokens==ntokens and again_parts==parts,"AP20 V2 roundtrip drift"
    _,entries,title=unpack_ap20(current)
    assert title==TITLE and len(entries)==74
    assert_native_links(again_parts[:70]);check_cross_r74(again_parts[:70])
    assert all(again_parts[e][p:p+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
               for e,p,op in SITES),"R76 input LEA drift"
    audit=inspect(parse(current))
    assert not audit["issues"],audit["issues"]
    apis=[row for row in audit["tokens"] if row["name"].startswith("aga ")]
    assert len(apis)==67
    assert (apis[-1]["name"],apis[-1]["function"],apis[-1]["signature"])==(
        API[0],API[2],API[3])
    return current,dict(version="R77 v0.13.22 C2P Close",
      sha256=sha256(current).hexdigest(),size=len(current),
      commands=67,ap20_entries=74,code_bytes=len(code),
      native_changed_from_r76=[71,72],r76_sha=R76_SHA,
      mouse_state_target=state_offset(parts),
      gate_a="PENDING CPU-native test",gate_b="NOT TESTED")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-base64",action="store_true")
    args=ap.parse_args()
    data,meta=build()
    assert data==build()[0], "non-deterministic R77"
    print("R77 CLOSE BUILDER",meta,flush=True)
    if args.emit_base64:
        print("R77_B64_BEGIN",flush=True)
        raw=base64.b64encode(data).decode("ascii")
        for i in range(0,len(raw),120):
            print("R77_B64",raw[i:i+120],flush=True)
        print("R77_B64_END",flush=True)

if __name__=="__main__":main()
