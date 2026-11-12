#!/usr/bin/env python3
"""M16/R47 capture static AP20/68000 gate (NOT AMOS/WinUAE Gate B/C).

Verify native emitter, AMOS-main Rjsr relocation markers, strict instruction
boundaries after patching those markers ONLY IN THE DISASSEMBLY COPY, and
deterministic compiler-safe candidate built from frozen R46 C1.
No production/candidate file is written by this test.
"""
from __future__ import annotations
import hashlib
from struct import unpack_from
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000

from build_m16_capture_r47 import build, LAST_GOOD, CURRENT, API
from m16_capture_r47_emit import (
    emit_capture, IDX_GETADR, IDX_EFF, IDX_RESERVE, IDX_CHANGE,
)
from compiler_relocation import unpack_ap20, unwrap_native_parts, is_compiler_wrapped
from audit_ap20 import inspect,parse,amos20_parameter_limit_errors

BRIDGE=b"\xfe\x11\xf7\x00"


def run():
    base=LAST_GOOD.read_bytes()
    before=hashlib.sha256(base).hexdigest()
    assert base==CURRENT.read_bytes() and len(base)==29964
    asm,labels=emit_capture()
    assert len(asm)%2==0 and len(asm)>700
    assert asm[:4]==bytes.fromhex("48e7efee")
    assert asm[labels["core"]:labels["core"]+4]==bytes.fromhex("48e77ffe")
    assert asm[labels["bank_name"]:]==b"AGAPIC  "
    markers=[]
    executable=bytearray(asm[:labels["bank_name"]])
    off=0
    while True:
        p=asm.find(BRIDGE,off)
        if p<0: break
        index=unpack_from(">H",asm,p+4)[0]
        markers.append(index)
        assert p+6<=labels["bank_name"]
        # For Capstone alone, replace linker pseudo opcode with 6-byte
        # 68000 JSR absolute LONG. The production candidate stays untouched.
        executable[p:p+6]=bytes.fromhex("4eb9000e0000")
        off=p+6
    assert markers==[IDX_GETADR,IDX_GETADR,IDX_RESERVE,IDX_CHANGE,IDX_EFF],markers
    decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions=list(decoder.disasm(executable,0))
    assert sum(i.size for i in instructions)==len(executable), (
        "invalid wrapper 68000 code",len(executable),
        sum(i.size for i in instructions),instructions[-7:])
    boundaries={inst.address for inst in instructions}
    assert all(offset in boundaries for name,offset in labels.items()
               if name!="bank_name"),labels
    assert not any(inst.mnemonic in ("dc.w","illegal","trap","bkpt")
                   for inst in instructions)

    binary,info=build()
    duplicate,info2=build()
    assert binary==duplicate and info==info2
    assert is_compiler_wrapped(binary)
    tok,parts,_=unpack_ap20(binary)
    assert len(parts)==58 and info["commands"]==51
    native_tok,native_parts=unwrap_native_parts(binary)
    assert native_tok==tok and len(native_parts)==57
    assert native_parts[-1]==asm
    audit=inspect(parse(binary))
    assert not audit["issues"],audit["issues"]
    # R47 is a frozen failed candidate: its 6-arg token cannot work under
    # AMOS Library_GetParams (only 5 are supported). Do NOT promote it.
    assert amos20_parameter_limit_errors(parse(binary)) == [
        "aga image capture: 6 arguments exceed AMOS extension limit 5"
    ]
    item=[t for t in audit["tokens"] if t["name"]==API[0]]
    assert len(item)==1 and item[0]["signature"]==API[3]
    assert CURRENT.read_bytes()==LAST_GOOD.read_bytes()==base
    assert hashlib.sha256(base).hexdigest()==before
    print("M16/R47 experimental CAPTURE WRAPPER STATIC PASS:",
          len(instructions),"68000 instructions,",len(markers),
          "AMOS bank relocators,",len(asm),"native bytes,",len(binary),
          "compiler-wrapped candidate bytes")
    print("R47 AMOS parser gate FAIL by design: six numeric parameters exceed AMOS maximum five")
    print("Native bank manager runtime + Interpreter/Compiler Gates B/C: NOT VALIDATED")


if __name__=="__main__":
    run()
