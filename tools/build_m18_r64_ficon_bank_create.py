"""M18/R64 deterministic in-memory R63 -> R64 Fast Icon bank-create AP20.

Use only R63 pinned deterministic builder. --emit-base64 exposes the exact
candidate for controlled publication at dist/AMOSPro_AGA.Lib after Gate A PASS.
No builder writes a .Lib, modifies LAST_GOOD or invokes AMOS Compiler.
"""
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2,DISPATCH_V2
from build_m18_r63_chip_blit import build as build_r63
from m18_ficon_bank_create_emit import (
    emit_ficon_bank_create,ENTRY_INDEX,GETADR_MARKER,RESERVE_MARKER,
    CHANGE_MARKER,EFF_MARKER,
)
R63_SHA="fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba"
API=("aga f icon bank create",1,ENTRY_INDEX,"00,0")
TITLE=(b"AMOSPro AGA M18 Fast Icon Create R64 0.13.9 candidate\0"
       b"$VER: AMOSPro_AGA 0.13.9\0")
TITLE+=bytes(len(TITLE)%2)

def build():
    base,meta=build_r63()
    assert sha256(base).hexdigest()==R63_SHA,"R63 immutable base diverged"
    tokens,old=unwrap_native_parts_v2(base)
    assert len(old)==ENTRY_INDEX==62 and not old[-1].endswith(GETP)
    native,labels=emit_ficon_bank_create()
    assert native.count(GETADR_MARKER)==2
    assert native.count(RESERVE_MARKER)==native.count(CHANGE_MARKER)==native.count(EFF_MARKER)==1
    parts=list(old)
    parts[-1]+=GETP
    parts.append(native)
    newtokens=tokens[:-6]+token(*API)+bytes(6)
    source=repack_ap20(base,newtokens,parts,TITLE)
    out=wrap_native_ap20_v2(source,TITLE)
    nt,entries,title=unpack_ap20(out)
    assert nt==newtokens and title==TITLE and len(entries)==64
    assert entries[-1]==DISPATCH_V2+b"".join(parts)
    assert unwrap_native_parts_v2(out)==(newtokens,parts)
    assert parts[:61]==old[:61] and parts[61]==old[61]+GETP
    assert len(entries[-1])<65534
    audit=inspect(parse(out))
    assert not audit["issues"],audit["issues"]
    previous=[t for t in inspect(parse(base))["tokens"] if t["name"].startswith("aga ")]
    current=[t for t in audit["tokens"] if t["name"].startswith("aga ")]
    assert len(previous)==56 and len(current)==57 and current[:-1]==previous
    assert (current[-1]["name"],current[-1]["function"],current[-1]["signature"])==(
        API[0],API[2],API[3])
    assert any(t["index"]==ENTRY_INDEX and t["parameters"]==2 and t["getp"]
               for t in audit["parameter_checks"])
    return out,dict(version="R64 v0.13.9",sha256=sha256(out).hexdigest(),
                    bytes=len(out),commands=len(current),ap20_entries=len(entries),
                    new_entry_index=ENTRY_INDEX,new_native_bytes=len(native),
                    compiler_v2_bytes=len(entries[-1]))

if __name__=="__main__":
    import argparse,base64
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,info=build()
    assert build()[0]==binary
    print("M18 R64 FICON8 BANK CREATE IN-MEMORY BUILDER",info)
    if args.emit_base64:
        encoded=base64.b64encode(binary).decode("ascii")
        print("M18_R64_LIB_BASE64_BEGIN")
        for offset in range(0,len(encoded),120):
            print("M18_R64_LIB_BASE64",encoded[offset:offset+120])
        print("M18_R64_LIB_BASE64_END")
