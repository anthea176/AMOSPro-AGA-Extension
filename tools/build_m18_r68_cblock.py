"""M18/R68 deterministic IN-MEMORY CBlock RAW Chip candidate builder.

No disk output by default. Gates A native / simulated Compiler V2 ONLY.
Never runs AMOS Compiler, never changes LAST_GOOD or a historical library.
"""
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2,DISPATCH_V2
from build_m18_r67_ficon_capture import build as build_r67
from m18_cblock_bank_emit import (
    emit_capture,emit_draw,emit_restore,ENTRY_CAPTURE,ENTRY_DRAW,ENTRY_RESTORE,
    GETADR,RESERVE,CHANGE,EFF,
)

R67_SHA="ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5"
# Explicit method parameter allows a truly identical CPU8/CPU16/Blitter benchmark.
APIS=(
    ("aga c block capture",1,ENTRY_CAPTURE,"00,0,0,0,0,0"),
    ("aga c block draw",1,ENTRY_DRAW,"00,0,0,0"),
    ("aga c block restore",1,ENTRY_RESTORE,"00,0"),
)
TITLE=(b"AMOSPro AGA M18 CBlock Chip R68 0.13.13 candidate\0"
       b"$VER: AMOSPro_AGA 0.13.13\0")
TITLE+=bytes(len(TITLE)%2)

def build():
    prior,_=build_r67()
    assert sha256(prior).hexdigest()==R67_SHA,"R67 A/B validated base changed"
    tokens,old=unwrap_native_parts_v2(prior)
    assert len(old)==ENTRY_CAPTURE==67 and not old[-1].endswith(GETP)
    chunks=[]
    for gen in (emit_capture,emit_draw,emit_restore):
        body,labels=gen()
        assert body.count(GETADR)==(2 if gen==emit_capture else 1)
        assert {"copy_core","reject","leave","check_planes","safe"}<=set(labels)
        assert len(body)<15000 and len(body)%2==0
        chunks.append(body)
    parts=list(old)
    parts[-1]+=GETP
    parts.extend((chunks[0]+GETP,chunks[1]+GETP,chunks[2]))
    ntokens=tokens[:-6]+b"".join(token(*api) for api in APIS)+bytes(6)
    src=repack_ap20(prior,ntokens,parts,TITLE)
    out=wrap_native_ap20_v2(src,TITLE)
    tt,entries,title=unpack_ap20(out)
    assert (tt,title)==(ntokens,TITLE) and len(entries)==71
    assert entries[-1]==DISPATCH_V2+b"".join(parts)
    assert unwrap_native_parts_v2(out)==(ntokens,parts)
    assert parts[:66]==old[:66] and parts[66]==old[66]+GETP
    assert len(entries[-1])<65534
    audit=inspect(parse(out))
    assert not audit["issues"],audit["issues"]
    prev=[t for t in inspect(parse(prior))["tokens"] if t["name"].startswith("aga ")]
    new=[t for t in audit["tokens"] if t["name"].startswith("aga ")]
    assert len(prev)==61 and len(new)==64 and new[:-3]==prev
    for got,api,params in zip(new[-3:],APIS,(6,4,2)):
        assert (got["name"],got["function"],got["signature"])==(api[0],api[2],api[3])
        assert any(p["index"]==api[2] and p["parameters"]==params and p["getp"]
                   for p in audit["parameter_checks"])
    return out,dict(version="R68 v0.13.13",sha256=sha256(out).hexdigest(),
                    bytes=len(out),commands=len(new),ap20_entries=len(entries),
                    native_bytes=[len(c) for c in chunks],
                    compiler_v2_bytes=len(entries[-1]))

if __name__=="__main__":
    import base64,argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    blob,meta=build()
    assert build()[0]==blob
    print("M18/R68 CBLOCK CHIP IN-MEMORY BUILDER",meta,flush=True)
    if args.emit_base64:
        s=base64.b64encode(blob).decode("ascii")
        print("M18_R68_LIB_BASE64_BEGIN")
        for pos in range(0,len(s),120):
            print("M18_R68_LIB_BASE64",s[pos:pos+120])
        print("M18_R68_LIB_BASE64_END")
