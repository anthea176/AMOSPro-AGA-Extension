#!/usr/bin/env python3
"""R54 v0.12.9: two ADDITIVE bank-number convenience API functions.

R53 AGAPIC capture is immutable and already confirmed in AMOS interpreted and
a freshly compiled WinUAE executable on the tested scenario. Old command
signatures and native routines remain byte-for-byte unchanged.
R54 itself needs independent Gates A/B/C; LAST_GOOD is NOT promoted here.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from hashlib import sha256
from audit_ap20 import token,parse,inspect
from compiler_relocation import (unpack_ap20,unwrap_native_parts,
    repack_ap20,wrap_native_ap20,is_compiler_wrapped)
from m16_bank_api_r54_emit import (emit_bank_image_draw,emit_bank_font_select,
     IDX_GETADR,MARKER)
ROOT=Path(__file__).resolve().parents[1]
R53=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.8_IMAGE_CAPTURE_LINK_FIX_R53.Lib"
R53_SHA="4cc7d78998720748e70a1498ec28375b03a4f5b98e02b3510d253f797af7ae26"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib"
API_IMAGE=("aga bank image draw",1,57,"00,0,0,0")
API_FONT=("aga bank font select",1,58,"00")
TITLE=b"AMOSPro AGA M16 Bank Number R54 0.12.9 candidate\0$VER: AMOSPro_AGA 0.12.9\0"
TITLE+=bytes(len(TITLE)%2)

def build():
    lastgood=(ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(lastgood).hexdigest()=="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
    stable=R53.read_bytes()
    assert sha256(stable).hexdigest()==R53_SHA and len(stable)==32008
    assert is_compiler_wrapped(stable)
    tokens,orig=unwrap_native_parts(stable)
    assert len(orig)==57
    orig_report=inspect(parse(stable))
    assert not orig_report["issues"]
    assert len([v for v in orig_report["tokens"] if v["name"].startswith("aga ")])==51
    offsets=[]
    total=0
    for part in orig:
        offsets.append(total)
        total+=len(part)
    parts=list(orig)
    parts[-1]+=b"GetP"      # new index 57 accepts 4 parameters
    image_start=sum(map(len,parts))
    image,image_labels=emit_bank_image_draw(image_start,offsets[55])
    parts.append(image+b"GetP") # new index 58 accepts 1 parameter
    font_start=sum(map(len,parts))
    font,font_labels=emit_bank_font_select(font_start,offsets[49])
    parts.append(font)
    assert len(parts)==59
    assert parts[:56]==orig[:56]
    assert parts[56]==orig[56]+b"GetP"
    assert parts[57]==image+b"GetP" and parts[58]==font
    assert image.count(MARKER)==font.count(MARKER)==1 and IDX_GETADR==797
    tok=tokens[:-6]+token(*API_IMAGE)+token(*API_FONT)+bytes(6)
    native=repack_ap20(stable,tok,parts,TITLE)
    result=wrap_native_ap20(native,TITLE)
    assert unwrap_native_parts(result)==(tok,parts)
    report=inspect(parse(result))
    assert not report["issues"],report["issues"]
    named=[t for t in report["tokens"] if t["name"].startswith("aga ")]
    assert len(named)==53
    for api,argc in ((API_IMAGE,4),(API_FONT,1)):
        t=[x for x in named if x["name"]==api[0]]
        assert len(t)==1 and (t[0]["instruction"],t[0]["function"],t[0]["signature"])==api[1:]
        assert any(x["index"]==api[2] and x["parameters"]==argc and x["getp"]
                   for x in report["parameter_checks"])
    assert [t for t in named if t["name"] not in (API_IMAGE[0],API_FONT[0])]==[
      t for t in orig_report["tokens"] if t["name"].startswith("aga ")]
    token2,wrapped,_=unpack_ap20(result)
    assert tok==token2 and len(wrapped)==60
    assert len(wrapped[-1])<32768, "monolithic Compiler code overflow"
    if ARCHIVE.exists():
        assert ARCHIVE.read_bytes()==result,"Immutable R54 archive differs"
    return result,dict(version="R54 0.12.9 CANDIDATE",bytes=len(result),
             sha256=sha256(result).hexdigest(),commands=53,entries=60,
             monolith=len(wrapped[-1]),image_bytes=len(image),font_bytes=len(font),
             legacy_draw_offset=offsets[55],legacy_font_offset=offsets[49],
             image_labels=image_labels,font_labels=font_labels,
             gate_a="Pending CI",gate_b="NOT TESTED",gate_c="NOT TESTED")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    raw,info=build()
    assert (raw,info)==build(),"R54 nondeterministic"
    print("R54 BANK NUMBER ADDITIVE STATIC GATE A",
      {k:v for k,v in info.items() if not k.endswith("_labels")},flush=True)
    if args.emit_base64:
        import base64
        print("R54_BINARY_BEGIN",flush=True)
        print(base64.b64encode(raw).decode(),flush=True)
        print("R54_BINARY_END",flush=True)
if __name__=="__main__":
    main()
