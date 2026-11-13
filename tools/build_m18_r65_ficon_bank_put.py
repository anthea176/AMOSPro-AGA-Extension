"""M18/R65 deterministic append of FICON8 Bank Put to SHA-pinned R64.

No on-disk write by build(). After native Gate A PASS, --emit-base64 emits
the exact installable candidate for single-path promotion into dist/ only.
"""
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2,DISPATCH_V2
from build_m18_r64_ficon_bank_create import build as build_r64
from m18_ficon_bank_put_emit import emit_ficon_bank_put,ENTRY_INDEX,GETADR_MARKER

R64_SHA="4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c"
API=("aga f icon bank put",1,ENTRY_INDEX,"00,0,0,0")
TITLE=(b"AMOSPro AGA M18 Fast Icon Put R65 0.13.10 candidate\0"
       b"$VER: AMOSPro_AGA 0.13.10\0")
TITLE+=bytes(len(TITLE)%2)

def build():
    base,old_meta=build_r64()
    assert sha256(base).hexdigest()==R64_SHA,"R64 A/B validated base changed"
    tokens,old=unwrap_native_parts_v2(base)
    assert len(old)==ENTRY_INDEX==63 and not old[-1].endswith(GETP)
    body,labels=emit_ficon_bank_put()
    assert body.count(GETADR_MARKER)==2
    parts=list(old)
    parts[-1]+=GETP
    parts.append(body)
    tokens65=tokens[:-6]+token(*API)+bytes(6)
    source=repack_ap20(base,tokens65,parts,TITLE)
    out=wrap_native_ap20_v2(source,TITLE)
    nt,entries,title=unpack_ap20(out)
    assert (nt,title)==(tokens65,TITLE) and len(entries)==65
    assert entries[-1]==DISPATCH_V2+b"".join(parts)
    assert unwrap_native_parts_v2(out)==(tokens65,parts)
    assert parts[:62]==old[:62] and parts[62]==old[62]+GETP
    assert len(entries[-1])<65534
    audit=inspect(parse(out))
    assert not audit["issues"],audit["issues"]
    old_tokens=[t for t in inspect(parse(base))["tokens"] if t["name"].startswith("aga ")]
    new_tokens=[t for t in audit["tokens"] if t["name"].startswith("aga ")]
    assert len(old_tokens)==57 and len(new_tokens)==58 and new_tokens[:-1]==old_tokens
    assert (new_tokens[-1]["name"],new_tokens[-1]["function"],
            new_tokens[-1]["signature"])==(API[0],API[2],API[3])
    assert any(t["index"]==ENTRY_INDEX and t["parameters"]==4 and t["getp"]
               for t in audit["parameter_checks"])
    return out,dict(version="R65 v0.13.10",sha256=sha256(out).hexdigest(),
                    bytes=len(out),commands=len(new_tokens),ap20_entries=len(entries),
                    new_entry_index=ENTRY_INDEX,new_native_bytes=len(body),
                    compiler_v2_bytes=len(entries[-1]))
if __name__=="__main__":
    import argparse,base64
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--emit-base64",action="store_true")
    args=a.parse_args()
    raw,meta=build()
    assert build()[0]==raw
    print("M18 R65 FICON8 BANK PUT IN-MEMORY BUILDER",meta)
    if args.emit_base64:
        b64=base64.b64encode(raw).decode("ascii")
        print("M18_R65_LIB_BASE64_BEGIN")
        for p in range(0,len(b64),120):print("M18_R65_LIB_BASE64",b64[p:p+120])
        print("M18_R65_LIB_BASE64_END")
