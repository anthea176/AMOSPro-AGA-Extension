#!/usr/bin/env python3
"""Independent fail-closed audit of mouse/key LEA data offsets in active binary."""
from pathlib import Path
from hashlib import sha256
from compiler_bridge_v2_probe import unwrap_native_parts_v2, DISPATCH_V2
from compiler_relocation import GETP, unpack_ap20
from active_library import R82_SHA, R83_SHA, R84_SHA, R85_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA

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
    digest=sha256(image).hexdigest()
    if digest in (R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA):
        # Modular V2 groups cannot be read as a single V2 monolith.
        # P0c redirects public Close to its BOBS unit, so only the real
        # multi-unit segment table and pinned builder may certify its identity.
        # Verify the unchanged native AGA unit against frozen R84, then run
        # all seven LEA checks plus eight negative cases on exact R82 source.
        from build_agapic_v2_r82_full_preview import build as build_r82
        ancestor,_=build_r82()
        assert sha256(ancestor).hexdigest()==R82_SHA
        _,original=unwrap_native_parts_v2(ancestor)
        last_good=Path("dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
        assert sha256(last_good).hexdigest()==R84_SHA
        _,units,_=unpack_ap20(image)
        _,frozen_units,_=unpack_ap20(last_good)
        group_indices={
            R87_SHA:(86,85,87),
            R88_SHA:(87,86,88),
            P0C_SHA:(91,90,92),
            P0D_SHA:(92,91,93),
            AP20_ISLANDS_SHA:(142,177,178),
            B7_SHA:(142,177,181),
            B7M1_SHA:(142,177,181),
            B7M2_SHA:(142,177,181),
            B8_SHA:(142,177,184),
        }
        aga_index,bob_index,entry_count=group_indices[digest]
        assert len(units)==entry_count, "Unexpected modular segment count"
        if digest in (AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA):
            assert units[aga_index].startswith(frozen_units[84]), "AP20 islands inherited R84 AGA/state prefix altered"
        else:
            assert units[aga_index]==frozen_units[84], "Inherited R84 AGA/state group altered"
        assert units[bob_index].startswith(DISPATCH_V2), "BOBS dispatch modified"
        if digest==B8_SHA:
            from build_m19_b8_first_update_in_memory import build_b8_first_update
            candidate,meta=build_b8_first_update()
            assert image==candidate and meta['sha256']==B8_SHA
            assert meta['public_commands']==88 and meta['ap20_entries']==184
            assert meta['native_groups']==[142,153,156,177,181]
            assert meta['pc16_max']==29962
            from build_m19_ap20_islands_in_memory import build as build_islands
            baseline,_=build_islands()
            _,earlier_groups,_=unpack_ap20(baseline)
            assert units[aga_index]==earlier_groups[aga_index], "B8 altered frozen AGA/state unit"
            assert units[bob_index].startswith(earlier_groups[bob_index]), "B8 altered frozen Bob unit"
        elif digest in (B7_SHA,B7M1_SHA,B7M2_SHA):
            from build_m19_p0j_end_lifecycle_in_memory import build as build_b7, build_multiframe
            if digest==B7M2_SHA:
                from build_m19_b7m2_close_reset_in_memory import build_close_reset
                rebuilt,meta=build_close_reset()
                assert meta['predecessor_sha']==B7M1_SHA
                assert meta['appended_bytes']==34 and len(rebuilt)==102400
            else:
                rebuilt,meta=(build_multiframe() if digest==B7M1_SHA else build_b7())
            assert image==rebuilt and meta['sha256']==digest
            assert meta['public_commands']==86 and meta['ap20_entries']==181
            assert meta['native_groups']==[142,153,156,177]
            from build_m19_ap20_islands_in_memory import build as build_islands
            baseline, _=build_islands()
            _,earlier_groups,_=unpack_ap20(baseline)
            assert units[aga_index]==earlier_groups[aga_index], "B7 altered old AGA/state native group"
        elif digest==AP20_ISLANDS_SHA:
            from build_m19_ap20_islands_in_memory import build as build_islands
            rebuilt,meta=build_islands()
            assert image==rebuilt and meta['sha256']==AP20_ISLANDS_SHA
            assert meta['native_groups'][94]==aga_index
            assert meta['native_groups'][93]==bob_index
        elif digest==P0D_SHA:
            from build_m19_p0d_bob_blit_in_memory import build as build_p0d
            rebuilt,meta=build_p0d()
            assert image==rebuilt and meta['sha256']==P0D_SHA
        elif digest==P0C_SHA:
            from build_m19_p0c_screen_close_in_memory import build as build_p0c
            rebuilt, meta=build_p0c()
            assert image==rebuilt and meta["sha256"]==P0C_SHA, "Active P0c builder mismatch"
            assert meta["old_aga_group"]==aga_index and meta["bridge_group"]==bob_index
            assert meta["screen_close_index"]==8 and meta["program_end_hook"].startswith("PRIVATE")
        elif digest==R88_SHA:
            from build_m19_p28_r88_in_memory import build as build_r88
            assert image==build_r88()[0], "Active R88 SHA-pinned build differs"
        else:
            from build_m19_p25_no_probe import build as build_r87
            assert image==build_r87()[0], "Active R87 SHA-pinned build differs"
        # R84 retained the complete R82 state source; no offsets or LEA
        # opcodes are accepted without checking their frozen source bytes.
        parts=original
    elif sha256(image).hexdigest() in (R83_SHA,R84_SHA,R85_SHA):
        # Check inherited native input-state code independently from source.
        from build_agapic_v2_r82_full_preview import build as build_r82
        frozen, _ = build_r82()
        assert sha256(frozen).hexdigest()==R82_SHA
        last_good=Path("dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
        assert sha256(last_good).hexdigest()==R84_SHA
        from build_aga_r83_modular import build as build_r83
        historical_r83,_=build_r83()
        assert sha256(historical_r83).hexdigest()==R83_SHA
        _, original=unwrap_native_parts_v2(frozen)
        _, units, _=unpack_ap20(image)
        digest=sha256(image).hexdigest()
        idx={R83_SHA:82,R84_SHA:84,R85_SHA:86}[digest]
        assert len(units)=={82:83,84:85,86:87}[idx]
        if idx in (84,86):
            _, r83parts, _=unpack_ap20(historical_r83)
            assert units[idx].startswith(r83parts[82]), "R84/R85 changed inherited R83 AGA code"
        else:
            assert image==historical_r83
        if idx==86:
            last_tokens,last_parts,_=unpack_ap20(last_good)
            assert units[86]==last_parts[84], "R85 altered protected AGA native bytes"
            assert units[85].startswith(DISPATCH_V2), "R85 BOBS group missing"
        core=units[idx][len(DISPATCH_V2):]
        frozen_aga=b"".join(original[:70])
        assert core[:len(frozen_aga)]==frozen_aga, "R83 active AGA/State code changed"
        parts=original
    else:
        _,parts=unwrap_native_parts_v2(image)
    target=check(parts)
    negative_cases(parts)
    print("CURRENT INPUT DATA PASS: offset",target,"7 LEAs, 8 negatives; B7/B8 source-built modular AGA group verified against R84 LAST_GOOD")

if __name__=="__main__":
    main()
