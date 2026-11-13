"""M18/R67 deterministic source-backed append of FICON8 screen capture.

No output file unless an explicitly validated main promotion is requested.
The AMOS Compiler is NOT invoked by this native builder.
"""
from hashlib import sha256
from audit_ap20 import inspect,parse,token
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2,DISPATCH_V2
from build_m18_r66_fichip_dynamic import build as build_r66
from m18_ficon_capture_emit import emit_ficon_capture,ENTRY_INDEX,GETADR_MARKER

R66_SHA="e57840e0c4f1379840e1254f1fb9ab800ce1ad712556efbd872047ea8822c7ca"
API=("aga f icon capture",1,ENTRY_INDEX,"00,0,0,0")
TITLE=(b"AMOSPro AGA M18 FIcon Screen Capture R67 0.13.12 candidate\0"
       b"$VER: AMOSPro_AGA 0.13.12\0")
TITLE+=bytes(len(TITLE)%2)

def build():
    previous,_=build_r66()
    assert sha256(previous).hexdigest()==R66_SHA,"R66 WinUAE A/B PASS base changed"
    tokens,parts=unwrap_native_parts_v2(previous)
    assert len(parts)==ENTRY_INDEX==66
    assert not parts[-1].endswith(GETP)
    body,labels=emit_ficon_capture()
    assert body.count(GETADR_MARKER)==1
    newparts=list(parts)
    newparts[-1]+=GETP
    newparts.append(body)
    newtokens=tokens[:-6]+token(*API)+bytes(6)
    src=repack_ap20(previous,newtokens,newparts,TITLE)
    out=wrap_native_ap20_v2(src,TITLE)
    rt,entries,title=unpack_ap20(out)
    assert (rt,title)==(newtokens,TITLE)
    assert len(entries)==68 and len(newparts)==67
    assert entries[-1]==DISPATCH_V2+b"".join(newparts)
    assert unwrap_native_parts_v2(out)==(newtokens,newparts)
    assert newparts[:65]==parts[:65] and newparts[65]==parts[65]+GETP
    assert len(entries[-1])<65534
    audit=inspect(parse(out))
    assert not audit["issues"],audit["issues"]
    prev_api=[t for t in inspect(parse(previous))["tokens"] if t["name"].startswith("aga ")]
    api=[t for t in audit["tokens"] if t["name"].startswith("aga ")]
    assert len(prev_api)==60 and len(api)==61 and api[:-1]==prev_api
    assert (api[-1]["name"],api[-1]["function"],api[-1]["signature"])==(API[0],API[2],API[3])
    assert any(x["index"]==ENTRY_INDEX and x["parameters"]==4 and x["getp"]
               for x in audit["parameter_checks"])
    return out,dict(version="R67 v0.13.12",sha256=sha256(out).hexdigest(),
                    bytes=len(out),commands=len(api),ap20_entries=len(entries),
                    native_bytes=len(body),compiler_v2_bytes=len(entries[-1]))

if __name__=="__main__":
    import argparse,base64
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emit-base64",action="store_true")
    a=p.parse_args()
    lib,meta=build()
    assert build()[0]==lib
    print("M18 R67 SCREEN FICON8 CAPTURE IN-MEMORY BUILDER",meta)
    if a.emit_base64:
        s=base64.b64encode(lib).decode("ascii")
        print("M18_R67_LIB_BASE64_BEGIN")
        for i in range(0,len(s),120):print("M18_R67_LIB_BASE64",s[i:i+120])
        print("M18_R67_LIB_BASE64_END")
