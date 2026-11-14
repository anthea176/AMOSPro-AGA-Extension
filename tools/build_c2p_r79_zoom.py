#!/usr/bin/env python3
"""R79 append-only C2P Zoom builder from exact SHA-pinned R78 (in memory).

No automatic dist write, Compiler Gate C, LAST_GOOD mutation or promotion.
"""
from __future__ import annotations
import argparse,base64
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from build_c2p_r78_blit import build as build_r78
from build_c2p_r76_rpg_fix import SITES,state_offset
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from c2p_r79_zoom_emit import emit_zoom,BANK

R78_SHA="9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c"
API=("aga c2p zoom",1,74,"00,0,0,0,0,0,0,0,0,0")
TITLE=b"AMOSPro AGA C2P Zoom R79 0.13.24 candidate\0$VER: AMOSPro_AGA 0.13.24\0"
TITLE+=bytes(len(TITLE)&1)

def build():
    previous,_=build_r78()
    assert sha256(previous).hexdigest()==R78_SHA,"R78 ancestor drift"
    tokens,original=unwrap_native_parts_v2(previous)
    assert len(original)==74 and not original[-1].endswith(GETP)
    assert state_offset(original)==12070
    for e,pos,op in SITES:
        assert original[e][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
    assert_native_links(original[:70]);check_cross_r74(original[:70])
    code,labels=emit_zoom()
    assert 0<len(code)<10000 and code.count(BANK)==2
    parts=list(original)
    parts[-1]+=GETP
    parts.append(code)
    assert len(parts)==75 and parts[:73]==original[:73]
    assert parts[73]==original[73]+GETP and parts[74]==code
    assert state_offset(parts)==12070,"R79 changed R76 keyboard static zone"
    new_tokens=tokens[:-6]+token(*API)+bytes(6)
    native=repack_ap20(previous,new_tokens,parts,TITLE)
    current=wrap_native_ap20_v2(native,TITLE)
    got_tokens,got_parts=unwrap_native_parts_v2(current)
    assert got_tokens==new_tokens and got_parts==parts,"R79 V2 native mismatch"
    _,entries,title=unpack_ap20(current)
    assert title==TITLE and len(entries)==76
    assert_native_links(got_parts[:70]);check_cross_r74(got_parts[:70])
    assert all(got_parts[e][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
               for e,pos,op in SITES),"R79 7 LEA mouse/key regression"
    audit=inspect(parse(current))
    assert not audit["issues"],audit["issues"]
    public=[t for t in audit["tokens"] if t["name"].startswith("aga ")]
    assert len(public)==69
    assert (public[-1]["name"],public[-1]["function"],public[-1]["signature"])==(
        API[0],API[2],API[3])
    return current,dict(version="R79 v0.13.24 C2P Zoom",
        sha256=sha256(current).hexdigest(),size=len(current),commands=69,
        ap20_entries=76,code_bytes=len(code),
        native_changed_from_r78=[73,74],r78_sha=R78_SHA,
        mouse_state_target=state_offset(parts),
        gate_a="PENDING native CPU test",gate_b="NOT TESTED",gate_c="NOT TESTED")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    raw,meta=build()
    assert raw==build()[0],"R79 output is non-deterministic"
    print("R79 C2P ZOOM BUILDER",meta,flush=True)
    if args.emit_base64:
        print("R79_B64_BEGIN",flush=True)
        b64=base64.b64encode(raw).decode("ascii")
        for i in range(0,len(b64),120):
            print("R79_B64",b64[i:i+120],flush=True)
        print("R79_B64_END",flush=True)

if __name__=="__main__":
    main()
