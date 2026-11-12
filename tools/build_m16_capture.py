#!/usr/bin/env python3
"""R53 0.12.8 functional capture correction, not a diagnostic probe.

Build from immutable promoted R46 C1; keep old archives reproducible.
Publication is explicit via --publish after local Gate A has passed.
"""
from pathlib import Path
from hashlib import sha256
import argparse
from audit_ap20 import token, parse, inspect
from active_library import LAST_GOOD_SHA, verify_active
from compiler_relocation import (native_from_promoted, unpack_ap20,
    repack_ap20, wrap_native_ap20, unwrap_native_parts)
from m16_capture_emit import emit_capture

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.8_IMAGE_CAPTURE_LINK_FIX_R53.Lib"
API=("aga image capture",1,56,"00,0,0,0,0,0")
TITLE=b"AMOSPro AGA M16 Image Capture R53 0.12.8 link fix\0$VER: AMOSPro_AGA 0.12.8\0"
TITLE+=bytes(len(TITLE)%2)

def build():
    good=(ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(good).hexdigest()==LAST_GOOD_SHA
    native=native_from_promoted(good,TITLE)
    tokens,parts,_=unpack_ap20(native)
    original=list(parts)
    assert len(parts)==56
    code,labels=emit_capture()
    parts[-1]+=b"GetP"
    parts.append(code)
    tokens=tokens[:-6]+token(*API)+bytes(6)
    raw=repack_ap20(native,tokens,parts,TITLE)
    out=wrap_native_ap20(raw,TITLE)
    assert unwrap_native_parts(out)==(tokens,parts)
    assert parts[:55]==original[:55] and parts[55]==original[55]+b"GetP"
    report=inspect(parse(out))
    assert not report["issues"],report["issues"]
    assert len([t for t in report["tokens"] if t["name"].startswith("aga ")])==51
    assert any(c["index"]==56 and c["parameters"]==6 and c["getp"]
               for c in report["parameter_checks"])
    return out,dict(bytes=len(out),sha256=sha256(out).hexdigest(),
                    monolith=len(unpack_ap20(out)[1][-1]),labels=labels)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--publish",action="store_true")
    args=p.parse_args()
    raw,meta=build()
    assert (raw,meta)==build()
    if ARCHIVE.exists():
        assert ARCHIVE.read_bytes()==raw,"immutable R53 archive differs"
    if args.publish:
        from active_library import CANDIDATE_HASHES
        assert CANDIDATE_HASHES[ARCHIVE.relative_to(ROOT).as_posix()]==meta["sha256"]
        if not ARCHIVE.exists():
            ARCHIVE.write_bytes(raw)
        (ROOT/"dist/AMOSPro_AGA.Lib").write_bytes(raw)
        verify_active(ROOT)
    print("R53 functional capture:",{k:v for k,v in meta.items() if k!="labels"})
    print("Gate B/C WinUAE NOT TESTED; LAST_GOOD unchanged")
if __name__=="__main__":
    main()
