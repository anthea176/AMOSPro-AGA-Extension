#!/usr/bin/env python3
"""R50 minimal Rjsr control: call harmless AMOS main FnOne instead of Bnk.GetAdr.

Same AP20 6-arg token and exactly the same R49 68000 routine layout.
Only 4 native bytes change: relocated main index 297 -> 322 and the
following MOVE.L A0,D0 -> MOVEQ #0,D0 (forced benign success on return).
R49 returned/crashed at Bnk.GetAdr; this control isolates the main linker.
"""
import argparse,base64
from hashlib import sha256
from pathlib import Path
from struct import pack
from active_library import verify_active,C1_SHA
from compiler_relocation import (native_from_promoted,unpack_ap20,
            unwrap_native_parts,repack_ap20,wrap_native_ap20)
from audit_ap20 import inspect,parse
from build_m16_r49_getadr_probe import native_probe as probe49
ROOT=Path(__file__).resolve().parents[1]
GOOD=ROOT/"dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
R49=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.4_R49_GETADR_PROBE.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.5_R50_RJSR_FNONE_PROBE.Lib"
R49_HASH="c18a0992ee148beb437aecc2c1c865338630b40e34bc989c72dfb26313d5657e"
IDX_FNONE=322
OLD=b"\xfe\x11\xf7\x00"+pack(">H",297)+b"\x20\x08"
NEW=b"\xfe\x11\xf7\x00"+pack(">H",IDX_FNONE)+b"\x70\x00"
def native_probe():
    orig=probe49()
    assert orig.count(OLD)==1 and len(orig)==128
    out=orig.replace(OLD,NEW)
    assert len(out)==len(orig) and out.count(NEW)==1
    return out
def build():
    good=GOOD.read_bytes()
    assert sha256(good).hexdigest()==LAST_GOOD_SHA
    verify_active(ROOT)
    prev=R49.read_bytes()
    assert sha256(prev).hexdigest()==R49_HASH and len(prev)==32012
    tok,segments,title=unpack_ap20(prev)
    t,parts=unwrap_native_parts(prev)
    assert t==tok and len(segments)==58 and len(parts)==57
    name=title.decode("ascii")
    title2=(name.replace("R49 0.12.4","R50 0.12.5")
                 .replace("AGA 0.12.4","AGA 0.12.5")).encode("ascii")
    assert title!=title2 and len(title)==len(title2)
    native=native_from_promoted(good,title2)
    original,baseparts,_=unpack_ap20(native)
    assert tok.startswith(original[:-6]) and parts[:55]==baseparts[:55]
    assert parts[55]==baseparts[55]+b"GetP"
    oldprobe=probe49()
    assert parts[-1].startswith(oldprobe)
    updated=list(parts)
    updated[-1]=native_probe()+parts[-1][len(oldprobe):]
    raw=repack_ap20(native,tok,updated,title2)
    candidate=wrap_native_ap20(raw,title2)
    t2,s2,_=unpack_ap20(candidate)
    assert len(candidate)==32012 and t2==tok and len(s2)==58
    assert s2[:56]==segments[:56]
    assert unwrap_native_parts(candidate)==(tok,updated)
    audit=inspect(parse(candidate))
    assert not audit["issues"]
    assert len([x for x in audit["tokens"] if x["name"].startswith("aga ")])==51
    if ARCHIVE.exists():
        assert ARCHIVE.read_bytes()==candidate
    return candidate,dict(size=len(candidate),sha256=sha256(candidate).hexdigest(),
             index=IDX_FNONE,ap20_entries=58,commands=51,gate="Gate A only")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    raw,info=build()
    assert (raw,info)==build()
    print("R50 SAFE MAIN RJSR STATIC PASS",info,flush=True)
    if args.emit_base64:
        print("R50_BINARY_BEGIN",flush=True)
        print(base64.b64encode(raw).decode(),flush=True)
        print("R50_BINARY_END",flush=True)
if __name__=="__main__":
    main()
