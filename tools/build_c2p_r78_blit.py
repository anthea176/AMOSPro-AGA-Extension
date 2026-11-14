#!/usr/bin/env python3
"""Deterministic R78 C2P Blit candidate, appended to SHA-pinned R77.

Build is in-memory by default, DOES NOT modify dist or LAST_GOOD.
Bnk.GetAdr is re-resolved on EACH Blit (source AND destination), all
bounds checked before pixel writes. Only AP20 last entry GETP and one
new pure-68000 native entry are appended, no earlier byte changes.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from build_c2p_r77_close import build as build_r77
from build_c2p_r76_rpg_fix import SITES,state_offset
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from c2p_r78_blit_emit import emit_blit,BANK

R77_SHA="81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11"
API=("aga c2p blit",1,73,"00,0,0,0,0,0,0,0")
TITLE=b"AMOSPro AGA C2P Blit R78 0.13.23 candidate\0$VER: AMOSPro_AGA 0.13.23\0"
TITLE+=bytes(len(TITLE)&1)

def build():
    previous,_=build_r77()
    assert sha256(previous).hexdigest()==R77_SHA,"R77 ancestor drift"
    tokens,original=unwrap_native_parts_v2(previous)
    assert len(original)==73 and not original[-1].endswith(GETP)
    assert state_offset(original)==12070
    for e,pos,opcode in SITES:
        assert original[e][pos:pos+4]==opcode.to_bytes(2,"big")+bytes.fromhex("2f26")
    assert_native_links(original[:70]);check_cross_r74(original[:70])
    code,labels=emit_blit()
    assert 0<len(code)<8000 and code.count(BANK)==2
    parts=list(original)
    parts[-1]+=GETP
    parts.append(code)
    assert len(parts)==74 and parts[:72]==original[:72]
    assert parts[72]==original[72]+GETP and parts[73]==code
    assert state_offset(parts)==12070, "R78 moved R76 keyboard static zone"
    ntokens=tokens[:-6]+token(*API)+bytes(6)
    native=repack_ap20(previous,ntokens,parts,TITLE)
    current=wrap_native_ap20_v2(native,TITLE)
    again_tokens,again_parts=unwrap_native_parts_v2(current)
    assert again_tokens==ntokens and again_parts==parts,"AP20 V2 roundtrip drift"
    _,entries,title=unpack_ap20(current)
    assert title==TITLE and len(entries)==75
    assert_native_links(again_parts[:70]);check_cross_r74(again_parts[:70])
    assert all(again_parts[e][p:p+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
               for e,p,op in SITES), "R76/R77 mouse/key LEA drift"
    a=inspect(parse(current))
    assert not a["issues"],a["issues"]
    public=[x for x in a["tokens"] if x["name"].startswith("aga ")]
    assert len(public)==68
    assert (public[-1]["name"],public[-1]["function"],public[-1]["signature"])==(
        API[0],API[2],API[3])
    return current,dict(version="R78 v0.13.23 C2P Blit",
        sha256=sha256(current).hexdigest(),size=len(current),commands=68,
        ap20_entries=75,code_bytes=len(code),
        native_changed_from_r77=[72,73],r77_sha=R77_SHA,
        mouse_state_target=state_offset(parts),
        gate_a="PENDING native CPU test",gate_b="NOT TESTED")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emit-base64",action="store_true")
    opt=p.parse_args()
    raw,meta=build()
    assert raw==build()[0],"R78 output must be deterministic"
    print("R78 C2P BLIT BUILDER",meta,flush=True)
    if opt.emit_base64:
        print("R78_B64_BEGIN",flush=True)
        b64=base64.b64encode(raw).decode("ascii")
        for i in range(0,len(b64),120):
            print("R78_B64",b64[i:i+120],flush=True)
        print("R78_B64_END",flush=True)

if __name__=="__main__":main()
