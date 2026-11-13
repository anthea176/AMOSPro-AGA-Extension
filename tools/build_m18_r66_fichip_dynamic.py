"""Deterministic R66 append: Chip Bank Create + Chip Stage from R65.

All author-facing outputs are built in-memory until native Gate A PASS.
Never alters LAST_GOOD or invokes the AMOS Compiler.
"""
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2,DISPATCH_V2
from build_m18_r65_ficon_bank_put import build as build_r65
from m18_fichip_dynamic_emit import (
    emit_chip_bank_create,emit_chip_stage,ENTRY_CREATE,ENTRY_STAGE,
    GETADR_MARKER,RESERVE_MARKER,CHANGE_MARKER,EFF_MARKER)
R65_SHA="6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2"
APIS=(("aga f chip bank create",1,ENTRY_CREATE,"00,0"),
      ("aga f chip stage",1,ENTRY_STAGE,"00,0,0"))
TITLE=(b"AMOSPro AGA M18 Dynamic Chip Cache R66 0.13.11 candidate\0"
       b"$VER: AMOSPro_AGA 0.13.11\0")
TITLE+=bytes(len(TITLE)%2)

def build():
    base,_=build_r65()
    assert sha256(base).hexdigest()==R65_SHA,"R65 A/B validated base changed"
    tokens,old=unwrap_native_parts_v2(base)
    assert len(old)==ENTRY_CREATE==64 and not old[-1].endswith(GETP)
    create,labels_create=emit_chip_bank_create()
    stage,labels_stage=emit_chip_stage()
    assert create.count(GETADR_MARKER)==2 and stage.count(GETADR_MARKER)==2
    for marker in (RESERVE_MARKER,CHANGE_MARKER,EFF_MARKER):
        assert create.count(marker)==1 and stage.count(marker)==0
    parts=list(old)
    parts[-1]+=GETP
    parts.append(create+GETP)
    parts.append(stage)
    newtokens=tokens[:-6]+b"".join(token(*api) for api in APIS)+bytes(6)
    source=repack_ap20(base,newtokens,parts,TITLE)
    out=wrap_native_ap20_v2(source,TITLE)
    nt,entries,title=unpack_ap20(out)
    assert (nt,title)==(newtokens,TITLE) and len(entries)==67
    assert entries[-1]==DISPATCH_V2+b"".join(parts)
    assert unwrap_native_parts_v2(out)==(newtokens,parts)
    assert parts[:63]==old[:63] and parts[63]==old[63]+GETP
    assert parts[64]==create+GETP and parts[65]==stage
    assert len(entries[-1])<65534
    audit=inspect(parse(out))
    assert not audit["issues"],audit["issues"]
    prior=[x for x in inspect(parse(base))["tokens"] if x["name"].startswith("aga ")]
    current=[x for x in audit["tokens"] if x["name"].startswith("aga ")]
    assert len(prior)==58 and len(current)==60 and current[:-2]==prior
    for entry,api in zip(current[-2:],APIS):
        assert (entry["name"],entry["function"],entry["signature"])==(api[0],api[2],api[3])
        assert any(x["index"]==api[2] and x["getp"] and x["parameters"]==(2 if api[2]==ENTRY_CREATE else 3) for x in audit["parameter_checks"])
    return out,dict(version="R66 v0.13.11",sha256=sha256(out).hexdigest(),
                    bytes=len(out),commands=len(current),ap20_entries=len(entries),
                    create_native_bytes=len(create),stage_native_bytes=len(stage),
                    compiler_v2_bytes=len(entries[-1]))
if __name__=="__main__":
    import argparse,base64
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    raw,meta=build()
    assert build()[0]==raw
    print("M18 R66 DYNAMIC CHIP CACHE IN-MEMORY BUILDER",meta)
    if args.emit_base64:
        b64=base64.b64encode(raw).decode("ascii")
        print("M18_R66_LIB_BASE64_BEGIN")
        for at in range(0,len(b64),120):
            print("M18_R66_LIB_BASE64",b64[at:at+120])
        print("M18_R66_LIB_BASE64_END")
