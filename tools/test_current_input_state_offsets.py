#!/usr/bin/env python3
"""Independent fail-closed audit of mouse/key LEA data offsets in active binary."""
from pathlib import Path
from hashlib import sha256
from compiler_bridge_v2_probe import unwrap_native_parts_v2, DISPATCH_V2
from compiler_relocation import GETP, unpack_ap20
from active_library import R82_SHA, R83_SHA

BINARY=Path("dist/AMOSPro_AGA.Lib")
SITES=((6,0x02e2,0x41ea),(31,0x0038,0x45ea),(31,0x0048,0x45ea),
       (32,0x0038,0x45ea),(32,0x0048,0x45ea),
       (33,0x003e,0x45ea),(33,0x022c,0x45ea))

def check(parts):
    assert len(parts)>33, "native entry33 missing: audit required"
    assert parts[33].endswith(bytes(144)+GETP), "state data layout changed: audit required"
    target=sum(len(p) for p in parts[:33])+len(parts[33])-len(GETP)-144-0x1a0
    assert 0<=target<=0x7fff, ("bad LEA WORD displacement",target)
    for entry,pos,opcode in SITES:
        assert len(parts[entry])>=pos+4, ("LEA site missing",entry,pos)
        raw=parts[entry][pos:pos+4]
        assert int.from_bytes(raw[:2],"big")==opcode, ("LEA opcode changed",entry,pos)
        got=int.from_bytes(raw[2:],"big")
        assert got==target, ("LEA writes outside input state DATA",entry,pos,got,target)
    return target

def negative_cases(parts):
    for entry,pos,_ in SITES:
        mutant=list(parts)
        b=bytearray(mutant[entry])
        b[pos+3]^=1
        mutant[entry]=bytes(b)
        try:
            check(mutant)
        except AssertionError:
            pass
        else:
            raise AssertionError(("corrupted LEA accepted",entry,pos))
    mutant=list(parts)
    mutant[7]+=b"\x4e\x71"
    try:
        check(mutant)
    except AssertionError:
        pass
    else:
        raise AssertionError("shifted input state accepted")

def main():
    image=BINARY.read_bytes()
    if sha256(image).hexdigest()==R83_SHA:
        # Check actual R83 unit bytes independently from its builder.
        from build_agapic_v2_r82_full_preview import build as build_r82
        frozen, _ = build_r82()
        assert sha256(frozen).hexdigest()==R82_SHA
        assert Path("dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()==image, "R83 promoted LAST_GOOD changed"
        _, original=unwrap_native_parts_v2(frozen)
        _, units, _=unpack_ap20(image)
        assert len(units)==83
        core=units[82][len(DISPATCH_V2):]
        frozen_aga=b"".join(original[:70])
        assert core[:len(frozen_aga)]==frozen_aga, "R83 active AGA/State code changed"
        parts=original
    else:
        _,parts=unwrap_native_parts_v2(image)
    target=check(parts)
    negative_cases(parts)
    print("CURRENT INPUT DATA PASS: offset",target,"7 LEAs, 8 negatives; R83 core byte-verified if active")

if __name__=="__main__":
    main()
