#!/usr/bin/env python3
"""R52 target verification, safely INSPECT the patched JSR FnOne destination.

R51 Gate B returns 1: FE11/F700/0142 relocated to 4EB9 + even/nonzero
address. R49/R50 still fail on execution. This diagnostic reads exactly
three instructions at the target, only AFTER exec.library TypeOfMem(-534)
accepts BOTH first and last bytes. No Rjsr execution, bank or screen use.

AMOS official +Lib.s: Lib_Par FnOne = MOVEQ #1,D3; Ret_Int
=> 7601 7400 4e75 (three words). Different bytes may indicate incorrect
main-library index/entry, not necessarily proof of the fault by themselves.
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
R51=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.6_R51_RJSR_RELOCATION_PROBE.Lib"
R51_SHA="04808ea9c89afb171a2c82f1ab61efd8bc912a0449d13cb20e942ad655ba7aea"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.7_R52_FNONE_TARGET_PROBE.Lib"
IDX_FNONE=322
MARKER=b"\xfe\x11\xf7\x00"+pack(">H",IDX_FNONE)
TARGET_CODE=b"\x76\x01\x74\x00\x4e\x75"
TYPE_OF_MEM=-534
def emit_probe():
    c=Code()
    c.raw("48e7efee")              # preserve AP20 register set
    for reg in (7,6,5,4,0):       # h,w,y,x,bank from (A3)+; mask in D3
        c.move(POST(3),D(reg))
    for reg,value in ((3,-1),(7,16),(6,16),(5,16),(4,16),(0,11)):
        c.imm("cmp",value,D(reg))
        c.branch(6,"bad_args")
    c.branch(0,"after_marker")    # never execute the Rjsr itself
    c.label("marker")
    c.raw(MARKER.hex())
    c.label("after_marker")
    c.lea(0,"marker")
    c.move(M(0),D(0),"w")
    c.imm("cmp",0x4eb9,D(0),"w")   # must be JSR absolute long
    c.branch(6,"malformed")
    c.move(M(0,2),D(7))           # candidate target held in D7
    c.tst(D(7))
    c.branch(7,"malformed")
    c.move(D(7),D(1))
    c.imm("and",1,D(1))
    c.branch(6,"malformed")
    # Bounds check: TypeOfMem returns zero for addresses outside managed RAM.
    # ROM or other memory absent from Exec MemList may also yield zero.
    c.move(D(7),A(1))
    c.raw("2c780004")             # MOVEA.L 4.W,A6 = exec.library
    c.call_os(TYPE_OF_MEM)
    c.tst(D(0))
    c.branch(7,"unmapped")
    c.move(D(7),D(0))
    c.imm("add",5,D(0))
    c.branch(5,"malformed")      # reject 32-bit wraparound
    c.move(D(0),A(1))
    c.raw("2c780004")
    c.call_os(TYPE_OF_MEM)
    c.tst(D(0))
    c.branch(7,"unmapped")
    c.move(D(7),A(0))
    for offset,word in ((0,0x7601),(2,0x7400),(4,0x4e75)):
        c.move(M(0,offset),D(0),"w")
        c.imm("cmp",word,D(0),"w")
        c.branch(6,"different")
    c.move(I(1),D(3))             # 1 exact first three instructions FnOne
    c.branch(0,"done")
    c.label("different")
    c.move(I(2),D(3))             # 2 different first three target words
    c.branch(0,"done")
    c.label("unmapped")
    c.move(I(3),D(3))             # 3 Exec cannot verify target region
    c.branch(0,"done")
    c.label("malformed")
    c.move(I(4),D(3))             # 4 unpatched/malformed JSR target
    c.branch(0,"done")
    c.label("bad_args")
    c.move(I(0),D(3))
    c.label("done")
    c.raw("4cdf77f7")            # restore D0-D1,D4-D7,A0-A2,A4-A6
    c.raw("74004e75")            # D2=integer return, RTS
    raw=c.out()
    assert len(raw)%2==0 and raw.count(MARKER)==1
    assert c.labels["marker"]+6==c.labels["after_marker"]
    return raw,c.labels
def build():
    good=GOOD.read_bytes()
    assert sha256(good).hexdigest()==LAST_GOOD_SHA
    verify_active(ROOT)
    old=R51.read_bytes()
    assert sha256(old).hexdigest()==R51_SHA and len(old)==32012
    token,wrapped,title=unpack_ap20(old)
    tok,parts=unwrap_native_parts(old)
    assert token==tok and len(wrapped)==58 and len(parts)==57
    nexttitle=(title.decode("ascii").replace("R51 0.12.6","R52 0.12.7")
               .replace("AGA 0.12.6","AGA 0.12.7")).encode("ascii")
    assert nexttitle!=title and len(nexttitle)==len(title)
    native=native_from_promoted(good,nexttitle)
    origin,baseparts,_=unpack_ap20(native)
    assert token.startswith(origin[:-6])
    assert len(baseparts)==56 and parts[:55]==baseparts[:55]
    assert parts[55]==baseparts[55]+b"GetP"
    code,labels=emit_probe()
    pad=len(parts[-1])-len(code)
    assert pad>=0 and pad%2==0
    newparts=list(parts)
    newparts[-1]=code+b"\x4e\x71"*(pad//2)
    raw=repack_ap20(native,token,newparts,nexttitle)
    candidate=wrap_native_ap20(raw,nexttitle)
    t,sections,_=unpack_ap20(candidate)
    assert t==token and len(sections)==58 and sections[:56]==wrapped[:56]
    assert len(candidate)==len(old)==32012
    assert unwrap_native_parts(candidate)==(token,newparts)
    report=inspect(parse(candidate))
    assert not report["issues"]
    assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==51
    if ARCHIVE.is_file():
        assert ARCHIVE.read_bytes()==candidate,"R52 archive modified"
    return candidate,dict(size=len(candidate),sha256=sha256(candidate).hexdigest(),
        native_len=len(code),nop_padding=pad,marker=IDX_FNONE,
        commands=51,entries=58,labels=labels,gate="Gate A only; no WinUAE Gate B")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--emit-base64",action="store_true")
    args=p.parse_args()
    code,meta=build()
    assert (code,meta)==build()
    print("R52 FNON TARGET BYTE CHECK STATIC GATE A PASS",
          {k:v for k,v in meta.items() if k!="labels"},flush=True)
    if args.emit_base64:
        print("R52_BINARY_BEGIN",flush=True)
        print(base64.b64encode(code).decode("ascii"),flush=True)
        print("R52_BINARY_END",flush=True)
if __name__=="__main__":
    main()
