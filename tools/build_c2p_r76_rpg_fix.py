#!/usr/bin/env python3
"""R76 RPG regression correction; deterministic C2P Open+Convert candidate.

The R74 insertion of 138 bytes into entry08 moved a static 144-byte
keyboard/mouse state block embedded at the END of native entry33.
Seven LEA 11932(a2),an instructions still used R73's old displacement.
One of them is in Aga Screen Open, which clears all 144 bytes and hence
overwrote native executable instructions in R74/R75 on every new screen.

Patch exactly those seven LEA.W operands to State->actual state block.
Do not edit the historical R73/R74/R75 builders or binaries, and do not
touch LAST_GOOD. No WinUAE or Compiler gate is claimed by this builder.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256

from audit_ap20 import inspect, parse
from build_opt020_p3_r73 import build as build_r73
from build_c2p_r75_convert import build as build_r75
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74

R73_SHA="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
R75_SHA="c5a5a0e45e5b07012247937bf1af0371836f0d119577c102d62a28f4ca1ad3af"
STATE_ENTRY0_OFFSET=0x1a0
R73_MOUSE_STATE_DELTA=11932
MOUSE_STATE_SIZE=144
INSERTION_BYTES=138
# Each tuple: (native AP20 entry, LEA instruction byte offset, EA opcode).
# These seven and ONLY these seven read the mouse/keyboard state block.
SITES=(
    (6,0x02e2,0x41ea),  # Aga Screen Open: CLR.L x36 = 144 bytes
    (31,0x0038,0x45ea), # Aga Mouse Pressed, active
    (31,0x0048,0x45ea), # Aga Mouse Pressed, inactive
    (32,0x0038,0x45ea), # Aga Mouse Released, active
    (32,0x0048,0x45ea), # Aga Mouse Released, inactive
    (33,0x003e,0x45ea), # shared mouse event processor
    (33,0x022c,0x45ea), # key/OS event injection helper
)
TITLE=b"AMOSPro AGA C2P RPG fix R76 0.13.21 candidate\0$VER: AMOSPro_AGA 0.13.21\0"
TITLE+=bytes(len(TITLE)&1)


def state_offset(parts):
    """Derive target from actual native DATA, never hardcode new address."""
    assert len(parts)>33 and parts[33].endswith(bytes(MOUSE_STATE_SIZE)+GETP), (
        "entry33 data layout changed: fail closed")
    static_offset=sum(len(p) for p in parts[:33])+len(parts[33])-len(GETP)-MOUSE_STATE_SIZE
    return static_offset-STATE_ENTRY0_OFFSET


def patch(parts):
    """Mutates ONLY seven, fixed-size LEA.W displacement words."""
    assert len(parts)==72
    target=state_offset(parts)
    assert target==R73_MOUSE_STATE_DELTA+INSERTION_BYTES==12070,(
        "R76 expected input block moved by exactly +138",target)
    assert 0<=target<=0x7fff
    changed=[]
    old_count=sum(bytes(p).count(b"\x2e\x9c") for p in parts)
    assert old_count==len(SITES),("unexpected old mouse displacement count",old_count)
    for entry,pos,opcode in SITES:
        original=bytes(parts[entry][pos:pos+4])
        assert original==opcode.to_bytes(2,"big")+R73_MOUSE_STATE_DELTA.to_bytes(2,"big"),(
            "not the exact audited LEA instruction",entry,pos,original.hex())
        p=bytearray(parts[entry])
        p[pos+2:pos+4]=target.to_bytes(2,"big")
        parts[entry]=bytes(p)
        changed.append((entry,pos))
    assert sum(bytes(p).count(b"\x2e\x9c") for p in parts)==0
    assert sum(bytes(p).count(b"\x2f\x26") for p in parts)>=len(SITES)
    assert len(changed)==7
    return target,changed


def build():
    previous,_meta=build_r75()
    assert sha256(previous).hexdigest()==R75_SHA, "R75 source pin changed"
    r73,_=build_r73()
    assert sha256(r73).hexdigest()==R73_SHA, "R73 LAST_GOOD source pin changed"
    _,r73parts=unwrap_native_parts_v2(r73)
    assert state_offset(r73parts)==R73_MOUSE_STATE_DELTA,(
        "R73 baseline state address is not the audited source address")
    tokens,original=unwrap_native_parts_v2(previous)
    assert len(original)==72
    parts=list(original)
    expected,changed=patch(parts)
    assert set(i for i in range(len(parts)) if parts[i]!=original[i])=={6,31,32,33}
    for i in range(len(parts)):
        assert len(parts[i])==len(original[i]),("entry size changed",i)
    assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    new=wrap_native_ap20_v2(repack_ap20(previous,tokens,parts,TITLE),TITLE)
    ntokens,unwrapped=unwrap_native_parts_v2(new)
    assert ntokens==tokens and unwrapped==parts, "Compiler V2 roundtrip drift"
    _,entries,title=unpack_ap20(new)
    assert title==TITLE and len(entries)==73
    assert_native_links(unwrapped[:70]);check_cross_r74(unwrapped[:70])
    audit=inspect(parse(new))
    assert not audit["issues"],audit["issues"]
    public=[t for t in audit["tokens"] if t["name"].startswith("aga ")]
    assert len(public)==66 and public[-1]["name"]=="aga c2p convert"
    return new,dict(version="R76 v0.13.21 C2P RPG input-state relocation fix",
        sha256=sha256(new).hexdigest(),size=len(new),commands=66,
        ap20_entries=73,leas_patched=len(changed),target=expected,
        affected_entries=sorted({e for e,_ in changed}),
        gate_a="PENDING native CPU test",gate_b="NOT TESTED")


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-base64",action="store_true")
    arg=ap.parse_args()
    candidate,info=build()
    assert candidate==build()[0], "R76 non-deterministic build"
    print("R76 RPG INPUT RELOCATION",info,flush=True)
    if arg.emit_base64:
        print("R76_B64_BEGIN")
        b64=base64.b64encode(candidate).decode("ascii")
        for i in range(0,len(b64),120):print("R76_B64",b64[i:i+120])
        print("R76_B64_END")


if __name__=="__main__":main()
