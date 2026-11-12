#!/usr/bin/env python3
"""R54 Gate A: 68000 syntax, protected old API, two wrappers, bank ABI.

WinUAE Gates B/C remain untested; no promotion of R54.
"""
from __future__ import annotations
from struct import unpack_from
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from build_m16_bank_api_r54 import build,R53,API_IMAGE,API_FONT
from m16_bank_api_r54_emit import emit_bank_image_draw,emit_bank_font_select,MARKER
from compiler_relocation import unpack_ap20,unwrap_native_parts
from audit_ap20 import parse,inspect
from amos_main_abi import main_index
def check():
    raw,meta=build()
    assert (raw,meta)==build()
    old=R53.read_bytes()
    oldtok,original=unwrap_native_parts(old)
    tok,parts=unwrap_native_parts(raw)
    assert len(parts)==59 and parts[:56]==original[:56]
    assert parts[56]==original[56]+b"GetP"
    start=meta["image_labels"]["native_start"]
    legacy=meta["image_labels"]["native_target"]
    d,labels=emit_bank_image_draw(start,legacy)
    assert parts[57]==d+b"GetP"
    start=meta["font_labels"]["native_start"]
    legacy=meta["font_labels"]["native_target"]
    f,flabels=emit_bank_font_select(start,legacy)
    assert parts[58]==f
    assert d.count(MARKER)==f.count(MARKER)==1
    assert main_index("Bnk.GetAdr")==797
    for name,code,lab in (("image",d,labels),("font",f,flabels)):
        patched=code.replace(MARKER,bytes.fromhex("4eb9000e0000"))
        assert len(patched)==len(code)
        dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
        instructions=list(dis.disasm(patched,0))
        assert sum(x.size for x in instructions)==len(code),(name,instructions[-5:])
        starts={x.address for x in instructions}
        assert all(x in starts for x in lab.values() if isinstance(x,int) and 0<=x<len(code))
        assert "bsr.w" in " ".join(x.mnemonic for x in instructions) or any(x.mnemonic=="bsr" for x in instructions)
        offset=lab["delegate"]
        assert unpack_from(">h",code,offset+2)[0]==lab["delegate_displacement"]
        assert lab["native_start"]+offset+4+lab["delegate_displacement"]==lab["native_target"]
    old_tokens=[t for t in inspect(parse(old))["tokens"] if t["name"].startswith("aga ")]
    new_tokens=[t for t in inspect(parse(raw))["tokens"] if t["name"].startswith("aga ")]
    assert new_tokens[:len(old_tokens)]==old_tokens
    assert [x["name"] for x in new_tokens[-2:]]==[API_IMAGE[0],API_FONT[0]]
    wrapped=unpack_ap20(raw)[1]
    assert len(wrapped)==60 and len(wrapped[-1])<32768
    print("R54 Gate A AP20 68000 relocation PASS: 53 commands, two additive wrappers",
      len(d),len(f),"bytes")
    print("AMOS WinUAE Gate B/C: NOT TESTED; R53 last tested source remains immutable")
if __name__=="__main__": check()
