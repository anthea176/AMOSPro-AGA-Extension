#!/usr/bin/env python3
"""M16/R49: minimal READ-ONLY Bnk.GetAdr relocation/ABI probe.

Identical R48 token, six-argument API, 58 AP20 entries, 32,012-byte HUNK.
The only effect compared with the WinUAE-PASS R48 token probe is ONE
AMOS main-library Rjsr Bnk.GetAdr(11) call (index 297). It returns:
1 if bank 11 free, 2 if occupied, 0 if six input arguments differ.
NO Bnk.Reserve, Bnk.Change, Bnk.Eff, screen, allocation or image capture.
Gate A is NOT a WinUAE test. Never promote or compile this diagnostic.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
from pathlib import Path
from struct import pack
from active_library import verify_active, C1_SHA
from audit_ap20 import parse,inspect
from compiler_relocation import (unpack_ap20,repack_ap20,wrap_native_ap20,
                                 unwrap_native_parts,native_from_promoted,
                                 is_compiler_wrapped)
from m68k_emit import Code,D,A,POST,I
from m16_capture_r47_emit import IDX_GETADR
ROOT=Path(__file__).resolve().parents[1]
GOOD=ROOT/"dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
R48=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.3_R48_TOKEN_ABI_PROBE.Lib"
R48_SHA="c30cfcc33ee50bb1f18c36225ccd7a5a6df7860e11201608d1801a0095687028"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.4_R49_GETADR_PROBE.Lib"
MARKER=b"\xfe\x11\xf7\x00"+pack(">H",IDX_GETADR)
assert IDX_GETADR==297
def native_probe():
    c=Code()
    c.raw("48e7efee")        # same AMOS preserved set as R48
    for reg in (7,6,5,4,0):
        c.move(POST(3),D(reg))  # height,width,y,x,bank; D3=mask
    for reg,val in ((3,-1),(7,16),(6,16),(5,16),(4,16),(0,11)):
        c.imm("cmp",val,D(reg))
        c.branch(6,"bad")
    c.move(I(11),D(0))
    c.raw(MARKER.hex())       # AMOS linker relocates this to Bnk.GetAdr
    c.move(A(0),D(0))
    c.tst(D(0))
    c.branch(6,"occupied")
    c.move(I(1),D(3))
    c.branch(0,"done")
    c.label("occupied")
    c.move(I(2),D(3))
    c.branch(0,"done")
    c.label("bad")
    c.move(I(0),D(3))
    c.label("done")
    c.raw("4cdf77f7")        # restore D0/D1/D4-D7/A0-A2/A4-A6
    c.raw("74004e75")        # D2 = numeric; RTS
    raw=c.out()
    assert raw.count(MARKER)==1 and len(raw)%2==0
    return raw
def build():
    good=GOOD.read_bytes()
    assert sha256(good).hexdigest()==LAST_GOOD_SHA
    verify_active(ROOT)       # active may be R48 now or R49 after publication
    r48=R48.read_bytes()
    assert sha256(r48).hexdigest()==R48_SHA
    assert is_compiler_wrapped(r48) and len(r48)==32012
    tokens,r48_stub,title=unpack_ap20(r48)
    r48_native_tokens,r48_native=unwrap_native_parts(r48)
    assert tokens==r48_native_tokens and len(r48_native)==57
    report=inspect(parse(r48))
    assert not report["issues"]
    item=[x for x in report["tokens"] if x["name"]=="aga image capture"]
    assert len(item)==1
    assert (item[0]["instruction"],item[0]["function"],item[0]["signature"])==(1,56,"00,0,0,0,0,0")
    oldtitle=title.decode("ascii")
    newtitle=(oldtitle.replace("R48 0.12.3","R49 0.12.4")
                       .replace("AGA 0.12.3","AGA 0.12.4")).encode("ascii")
    assert len(newtitle)==len(title) and newtitle!=title
    native=native_from_promoted(good,newtitle)
    orig_token,parts,_=unpack_ap20(native)
    assert tokens.startswith(orig_token[:-6])
    assert len(parts)==56 and parts[:55]==r48_native[:55]
    assert r48_native[55]==parts[55]+b"GetP"
    parts[-1]+=b"GetP"
    probe=native_probe()
    assert len(probe)<=len(r48_native[-1])
    pad=len(r48_native[-1])-len(probe)
    assert pad>=0 and pad%2==0
    parts.append(probe+b"\x4e\x71"*(pad//2))  # NOP-only tail; same R48 HUNK size
    raw=repack_ap20(native,tokens,parts,newtitle)
    candidate=wrap_native_ap20(raw,newtitle)
    assert len(candidate)==len(r48)==32012
    t,segments,_=unpack_ap20(candidate)
    assert t==tokens and len(segments)==58
    assert segments[:56]==r48_stub[:56]
    assert unwrap_native_parts(candidate)==(tokens,parts)
    audit=inspect(parse(candidate))
    assert not audit["issues"]
    assert [t for t in audit["tokens"] if t["name"].startswith("aga ")]==[
        t for t in report["tokens"] if t["name"].startswith("aga ")]
    if ARCHIVE.exists():
        assert ARCHIVE.read_bytes()==candidate,"Archived R49 altered"
    return candidate,dict(size=len(candidate),sha256=sha256(candidate).hexdigest(),
        six_args=6,ap20_entries=58,commands=51,main_rjsr=[IDX_GETADR],
        native_probe_bytes=len(probe),padding_bytes=pad,
        gate="Gate A only; Gate B not tested; never promotes LAST_GOOD")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    data,meta=build()
    data2,meta2=build()
    assert data==data2 and meta==meta2
    print("R49 GETADR READ-ONLY GATE A STATIC PASS",meta,flush=True)
    if args.emit_base64:
        print("R49_BINARY_BEGIN",flush=True)
        print(base64.b64encode(data).decode("ascii"),flush=True)
        print("R49_BINARY_END",flush=True)
if __name__=="__main__":
    main()
