"""M18/R62 in-memory ONLY candidate, additive Chip Blitter Fast Icon AP20.

Pinned R61 and R60 unchanged. This is not installed in dist and not a
WinUAE Gate B/C build until the AP20 + 68000 DMA ABI Gate A passes.
"""
from hashlib import sha256
from audit_ap20 import parse,inspect,token
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2,DISPATCH_V2
from build_m18_r61_ficon import build as build_r61
from m18_ficon_chip_ap20_emit import emit_ficon_chip_ap20,GETADR_MARKER,ENTRY_INDEX

R61_SHA="ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f"
API=("aga f blit",1,ENTRY_INDEX,"00,0,0,0,0")
TITLE=(b"AMOSPro AGA M18 Chip Fast Icon R62 0.13.7 candidate\0"
       b"$VER: AMOSPro_AGA 0.13.7\0")
TITLE+=bytes(len(TITLE)%2)

def build():
    r61,_=build_r61()
    assert sha256(r61).hexdigest()==R61_SHA,"R61 prior candidate changed"
    tokens,old=unwrap_native_parts_v2(r61)
    assert len(old)==ENTRY_INDEX==61 and not old[-1].endswith(GETP)
    native,labels=emit_ficon_chip_ap20()
    assert native.count(GETADR_MARKER)==1
    parts=list(old)
    parts[-1]+=GETP
    parts.append(native)
    newtokens=tokens[:-6]+token(*API)+bytes(6)
    native_hunk=repack_ap20(r61,newtokens,parts,TITLE)
    out=wrap_native_ap20_v2(native_hunk,TITLE)
    nt,stub,title=unpack_ap20(out)
    assert nt==newtokens and title==TITLE and len(stub)==63
    assert stub[-1]==DISPATCH_V2+b"".join(parts)
    assert unwrap_native_parts_v2(out)==(newtokens,parts)
    assert parts[:60]==old[:60] and parts[60]==old[60]+GETP
    assert len(stub[-1])<65534
    report=inspect(parse(out))
    assert not report["issues"],report["issues"]
    orig_names=[v for v in inspect(parse(r61))["tokens"] if v["name"].startswith("aga ")]
    new_names=[v for v in report["tokens"] if v["name"].startswith("aga ")]
    assert new_names[:-1]==orig_names and len(new_names)==len(orig_names)+1
    assert (new_names[-1]["name"],new_names[-1]["function"],new_names[-1]["signature"])==(
        API[0],ENTRY_INDEX,API[3])
    assert any(v["index"]==ENTRY_INDEX and v["parameters"]==5 and v["getp"]
               for v in report["parameter_checks"])
    return out,dict(sha256=sha256(out).hexdigest(),bytes=len(out),
                    new_index=ENTRY_INDEX,new_native_bytes=len(native),
                    cpu_core_bytes=labels["core_bytes"],commands=len(new_names),
                    ap20_entries=len(stub),compiled_bytes=len(stub[-1]))

if __name__=="__main__":
    _,info=build()
    assert build()[1]==info
    print("M18 R62 CHIP BLIT UNINSTALLED IN-MEMORY BUILDER",info)
