"""R61 P4 IN-MEMORY ONLY: additive AP20 AGA Fast Icon Compiler V2.

Build from pinned R60; no binary files written, no R61 install/promote.
"""
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import (
    unwrap_native_parts_v2,wrap_native_ap20_v2,DISPATCH_V2,
)
from build_m18_r60_image_region import build as build_r60
from m18_ficon_ap20_emit import emit_ficon_ap20,ENTRY_INDEX,GETADR_MARKER

R60_SHA="00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8"
API=("aga f icon",1,ENTRY_INDEX,"00,0,0,0,0")
TITLE=(b"AMOSPro AGA M18 FIcon R61 0.13.6 candidate\0"
       b"$VER: AMOSPro_AGA 0.13.6\0")
TITLE+=bytes(len(TITLE)%2)

def build():
    r60,_=build_r60()
    assert sha256(r60).hexdigest()==R60_SHA,"R60 immutable base changed"
    previous,old=unwrap_native_parts_v2(r60)
    assert len(old)==ENTRY_INDEX==60 and not old[-1].endswith(GETP)
    native,labels=emit_ficon_ap20()
    assert native.count(GETADR_MARKER)==1
    parts=list(old)
    parts[-1]+=GETP
    parts.append(native)
    tokens=previous[:-6]+token(*API)+bytes(6)
    source=repack_ap20(r60,tokens,parts,TITLE)
    output=wrap_native_ap20_v2(source,TITLE)
    nt,stubs,ntitle=unpack_ap20(output)
    assert nt==tokens and ntitle==TITLE
    assert len(stubs)==62
    assert stubs[-1]==DISPATCH_V2+b"".join(parts)
    assert unwrap_native_parts_v2(output)==(tokens,parts)
    assert parts[:59]==old[:59] and parts[59]==old[59]+GETP
    assert len(stubs[-1])<65534
    report=inspect(parse(output))
    assert not report["issues"],report["issues"]
    older=[t for t in inspect(parse(r60))["tokens"]
           if t["name"].startswith("aga ")]
    named=[t for t in report["tokens"] if t["name"].startswith("aga ")]
    assert named[:-1]==older and len(named)==len(older)+1
    assert (named[-1]["name"],named[-1]["function"],named[-1]["signature"]) == (
           API[0],API[2],API[3])
    assert any(t["index"]==ENTRY_INDEX and t["parameters"]==5 and t["getp"]
               for t in report["parameter_checks"])
    return output,{
        "version":"R61 0.13.6 IN MEMORY GATE A ONLY",
        "bytes":len(output),"sha256":sha256(output).hexdigest(),
        "public_commands":len(named),"ap20_entries":len(stubs),
        "compiler_v2_bytes":len(stubs[-1]),"new_entry_index":ENTRY_INDEX,
        "native_bytes":len(native),"core_offset":labels["core"],
    }

if __name__=="__main__":
    import argparse,base64
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,meta=build()
    assert build()[0]==binary
    print("M18/R61 IN-MEMORY BUILDER",meta)
    if args.emit_base64:
        encoded=base64.b64encode(binary).decode("ascii")
        print("M18_R61_LIB_BASE64_BEGIN")
        for at in range(0,len(encoded),120):
            print("M18_R61_LIB_BASE64",encoded[at:at+120])
        print("M18_R61_LIB_BASE64_END")
