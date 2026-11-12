#!/usr/bin/env python3
"""M13 R28 0.10.0: reproducible AGA palette base candidate (source-only).

Start ONLY from frozen WinUAE-PASS R27. Keep 37 original 68000 segments,
append GetP to the final R26 Text entry and add three new entries:
Palette Load (ILBM CMAP only), Set (RGB8), Get (packed 00RRGGBB).
No existing entry is recompiled/repatched; no R23 cross-entry relocation
required because all growth follows its private dispatcher and R26 Text.
No file is written by this builder (including when --emit-base64 is used).
LAST_GOOD is the latest WinUAE-confirmed R38, not the historical R10.
"""
from pathlib import Path
from struct import pack
import argparse
import base64

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m13_palette_r28_emit import emit_load, emit_set, emit_get

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256="64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe"
LAST_GOOD_SHA256="9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf"
OLD_ENTRIES=37
ENTRY_LOAD=37
ENTRY_SET=38
ENTRY_GET=39
GETP=b"GetP"
API=(
    ("aga palette load", ENTRY_LOAD, "02"),
    ("aga palette set", ENTRY_SET, "00,0,0,0"),
    ("aga palette get", ENTRY_GET, "00"),
)
VERSION="R28 0.10.0"

def build():
    raw=BASE.read_bytes()
    assert digest(raw)==BASE_SHA256,"Frozen R27 changed"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,"LAST_GOOD changed"
    tok0,old,_=split(raw)
    assert len(old)==OLD_ENTRIES and old[-1].endswith(bytes.fromhex("74004e75"))
    assert not old[-1].endswith(GETP)
    report0=inspect(parse(raw))
    assert not report0["issues"]
    assert len([x for x in report0["tokens"] if x["name"].startswith("aga ")])==31
    expected={x["name"] for x in report0["tokens"]}
    assert not any(n in expected for n,_,_ in API)

    load,labels_load=emit_load()
    setter,labels_set=emit_set()
    getter,labels_get=emit_get()
    assert all(len(x)>16 and len(x)%2==0 for x in (load,setter,getter))
    parts=list(old)
    parts[-1]+=GETP
    # Every parameterized AP20 entry needs a GetP separator in the
    # immediately preceding segment, not only before the first new entry.
    parts.extend((load+GETP,setter+GETP,getter))
    assert len(parts)==40
    assert parts[:36]==old[:36]
    assert parts[36]==old[36]+GETP
    assert parts[ENTRY_LOAD]==load+GETP
    assert parts[ENTRY_SET]==setter+GETP
    assert parts[ENTRY_GET]==getter
    tokens=tok0[:-6]+b"".join(token(name,1,index,sig)
                                 for name,index,sig in API)+bytes(6)
    title=b"AMOSPro AGA M13 Palette Base R28 0.10.0\0$VER: AMOSPro_AGA 0.10.0\0"
    if len(title)&1:title+=b"\0"
    code=b"".join(parts)
    payload=(pack(">4I",len(parts)*2,len(tokens),len(code),len(title))
             +b"\0\0AP20"+b"".join(pack(">H",len(x)//2) for x in parts)
             +tokens+code+title+b"\0\0")
    payload+=bytes(-len(payload)%4)
    words=pack(">I",len(payload)//4)
    candidate=raw[:20]+words+raw[24:28]+words+payload+raw[-4:]
    audit=inspect(parse(candidate))
    assert not audit["issues"],audit["issues"]
    tok1,segments,_=split(candidate)
    assert tok1==tokens and segments==parts
    named=[r for r in audit["tokens"] if r["name"].startswith("aga ")]
    assert len(named)==34
    for name,index,sig in API:
        matches=[r for r in named if r["name"]==name]
        assert len(matches)==1
        assert (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,index,sig)
        count=len(sig[1:].split(",")) if len(sig)>1 else 0
        assert any(x["index"]==index and x["parameters"]==count and x["getp"]
                   for x in audit["parameter_checks"]),name
    return candidate,{
        "version":VERSION,"size":len(candidate),"sha256":digest(candidate),
        "segments":len(parts),"named_commands":len(named),
        "new_commands":API,
        "unchanged_entries":tuple(range(36)),
        "text_entry_getp_only":36,
        "labels":{"load":labels_load,"set":labels_set,"get":labels_get},
        "Gate_A":"REQUIRES_CPU_CI","Gate_B_WinUAE":"NOT_TESTED",
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    raw,meta=build()
    assert raw==build()[0],"R28 builder not deterministic"
    print("M13 R28 in-memory candidate:",meta,flush=True)
    if args.emit_base64:
        print("R28_BASE64_BEGIN",flush=True)
        print(base64.b64encode(raw).decode("ascii"),flush=True)
        print("R28_BASE64_END",flush=True)
