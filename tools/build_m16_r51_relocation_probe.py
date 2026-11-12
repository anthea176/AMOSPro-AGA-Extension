#!/usr/bin/env python3
"""R51 loader-relocation observation: examine Rjsr bytecode but NEVER run it.

R50 ended in a real Amiga 80000004 illegal-instruction alert. R51 performs
the same six-argument AP20 function call, but branches AROUND the main-library
Rjsr FnOne pseudo-instruction, then reads the bytes at the embedded marker.
The AMOS extension loader should have replaced FE11F7000142 with JSR absolute
long (4EB9XXXXXXXX). This diagnostic safely differentiates loader relocation
from a bad JSR target. Does NOT capture images or access banks.
"""
from __future__ import annotations
import argparse,base64
from pathlib import Path
from hashlib import sha256
from struct import pack
from audit_ap20 import inspect,parse
from active_library import verify_active,LAST_GOOD_SHA
from compiler_relocation import (unpack_ap20,unwrap_native_parts,
    native_from_promoted,repack_ap20,wrap_native_ap20)
from m68k_emit import Code,D,A,M,POST,I
ROOT=Path(__file__).resolve().parents[1]
GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
R50=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.5_R50_RJSR_FNONE_PROBE.Lib"
R50_SHA="984cbd5f6485c9f1133eafe356d23c290b2e457902d4f518df3776ffbb5f5eef"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.6_R51_RJSR_RELOCATION_PROBE.Lib"
IDX_FNONE=322
MARKER=b"\xfe\x11\xf7\x00"+pack(">H",IDX_FNONE)
def emit_probe():
    c=Code()
    c.raw("48e7efee")          # save all AMOS-regs as in R48/R50
    for reg in (7,6,5,4,0):
        c.move(POST(3),D(reg))
    for reg,val in ((3,-1),(7,16),(6,16),(5,16),(4,16),(0,11)):
        c.imm("cmp",val,D(reg))
        c.branch(6,"bad_args")
    c.branch(0,"after_marker")  # BRA.w: skip unsafe Rjsr pseudo-instruction
    c.label("marker")
    c.raw(MARKER.hex())
    c.label("after_marker")
    c.lea(0,"marker")            # read bytes at precisely the skipped marker
    c.move(M(0),D(0),"w")
    c.imm("cmp",0x4eb9,D(0),"w")    # patched JSR absolute
    c.branch(6,"try_raw")
    c.move(M(0,2),D(0))           # patched absolute target address
    c.tst(D(0))
    c.branch(7,"unknown")
    c.move(D(0),D(1))
    c.imm("and",1,D(1))
    c.branch(6,"unknown")         # odd address: invalid
    c.move(I(1),D(3))             # 1: patched JSR, target nonzero/even
    c.branch(0,"done")
    c.label("try_raw")
    c.move(M(0),D(0),"w")
    c.imm("cmp",0xfe11,D(0),"w")   # raw FE11 pseudo-opcode still unpatched
    c.branch(6,"unknown")
    c.move(I(2),D(3))             # 2: loader left FE11 unpatched
    c.branch(0,"done")
    c.label("unknown")
    c.move(I(3),D(3))             # 3: unexpected opcode/null/odd target
    c.branch(0,"done")
    c.label("bad_args")
    c.move(I(0),D(3))
    c.label("done")
    c.raw("4cdf77f7")            # restore established native AP20 preserved regs
    c.raw("74004e75")            # D2=0 numeric, RTS
    out=c.out()
    assert out.count(MARKER)==1 and len(out)%2==0
    assert c.labels["marker"]+6==c.labels["after_marker"]
    return out,c.labels
def build():
    good=GOOD.read_bytes()
    assert sha256(good).hexdigest()==LAST_GOOD_SHA
    verify_active(ROOT)
    r50=R50.read_bytes()
    assert sha256(r50).hexdigest()==R50_SHA and len(r50)==32012
    token,wrapped,title=unpack_ap20(r50)
    tok,old_parts=unwrap_native_parts(r50)
    assert tok==token and len(wrapped)==58 and len(old_parts)==57
    name=title.decode("ascii")
    updated=(name.replace("R50 0.12.5","R51 0.12.6")
                 .replace("AGA 0.12.5","AGA 0.12.6")).encode("ascii")
    assert updated!=title and len(updated)==len(title)
    native=native_from_promoted(good,updated)
    original,base_parts,_=unpack_ap20(native)
    assert token.startswith(original[:-6])
    assert len(base_parts)==56 and old_parts[:55]==base_parts[:55]
    assert old_parts[55]==base_parts[55]+b"GetP"
    code,labels=emit_probe()
    tail=len(old_parts[-1])-len(code)
    assert tail>=0 and tail%2==0
    updated_parts=list(old_parts)
    updated_parts[-1]=code+b"\x4e\x71"*(tail//2)
    raw=repack_ap20(native,token,updated_parts,updated)
    candidate=wrap_native_ap20(raw,updated)
    tk,pieces,_=unpack_ap20(candidate)
    assert len(candidate)==32012 and tk==token and len(pieces)==58
    assert pieces[:56]==wrapped[:56]
    assert unwrap_native_parts(candidate)==(tk,updated_parts)
    report=inspect(parse(candidate))
    assert not report["issues"]
    assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==51
    if ARCHIVE.exists():
        assert ARCHIVE.read_bytes()==candidate,"R51 immutable archive differs"
    return candidate,dict(size=len(candidate),sha256=sha256(candidate).hexdigest(),
           native_bytes=len(code),nop_padding=tail,entry=56,commands=51,
           rjsr_marker=IDX_FNONE,labels=labels,gate="Gate A only, WinUAE B not tested")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    blob,meta=build()
    assert (blob,meta)==build(),"non deterministic"
    print("R51 RELOCATION BYTE INSPECTION GATE A PASS",
      {k:v for k,v in meta.items() if k!="labels"},flush=True)
    if args.emit_base64:
        print("R51_BINARY_BEGIN",flush=True)
        print(base64.b64encode(blob).decode("ascii"),flush=True)
        print("R51_BINARY_END",flush=True)
if __name__=="__main__":
    main()
