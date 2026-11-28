#!/usr/bin/env python3
"""Independent fail-closed audit of mouse/key LEA data offsets in active binary."""
from pathlib import Path
from hashlib import sha256
from compiler_bridge_v2_probe import unwrap_native_parts_v2, DISPATCH_V2
from compiler_relocation import GETP, unpack_ap20
from active_library import R82_SHA, R83_SHA, R84_SHA, R85_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, P1E_SHA, P2A_SHA, P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, S1P1F_SHA, S1P1G_SHA, S1P1H_SHA, S1P1I_SHA, S1P2I_SHA, S1P2J_SHA, S1P2K_SHA, S1P2LB_SHA, S1P2LC_SHA, S1P2M_SHA, S2A_SHA, S2B_SHA, S2R_SHA, S2C_SHA, S2CD_SHA, S2CE_SHA, SPRITE_L2B_HISTORICAL_SHAS, LAST_GOOD_SHA

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
    if digest in (P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, *SPRITE_L2B_HISTORICAL_SHAS):
        # P2d and S1-P1e are multi-unit Compiler V2. The frozen P2d
        # source is the reference; S1 must inherit all 203 entries exactly.
        # Only then audit the seven LEAs in the original R82 source.
        from active_library import verify_active, frozen_p2d
        from build_m19_p2d_in_memory import build_p2d
        from build_aga_r84_agapic import build as build_r84
        from build_agapic_v2_r82_full_preview import build as build_r82
        candidate, meta = build_p2d()
        assert sha256(candidate).hexdigest() == meta['sha256'] == P2D_SHA
        assert len(candidate) == 136020 and (meta['commands'], meta['entries']) == (100, 203)
        active, frozen, _ = verify_active(BINARY.parent.parent)
        assert active == image and sha256(frozen).hexdigest() == LAST_GOOD_SHA
        assert frozen_p2d(frozen) == candidate
        _, units, _ = unpack_ap20(candidate)
        if digest == S1P1E_SHA:
            _, active_units, _ = unpack_ap20(image)
            assert len(image) == 142000 and len(active_units) == 208
            assert active_units[:203] == units, 'S1-P1e altered inherited P2d AP20 entries'
            assert active_units[142] == units[142], 'S1-P1e altered input-state unit'
        elif digest in (S2R_SHA,S2C_SHA,S2CD_SHA,S2CE_SHA):
            # Authenticate the new island AND reconstruct the entire inherited
            # L2b prefix with only the known Close/End sites and moved bytes restored.
            from verify_m19_s2r_delivery import verify_library, START, END
            if digest in (S2C_SHA,S2CD_SHA,S2CE_SHA):
                from verify_m19_s2c_delivery import verify_library as verify_s2c_library
                verify_s2c_library(image,frozen)
            else:
                verify_library(image,frozen)
            _, inherited, _ = unpack_ap20(frozen)
            _, active_units, _ = unpack_ap20(image)
            assert len(inherited)==203 and len(active_units)==219
            assert [i for i,(x,y) in enumerate(zip(inherited,active_units)) if x!=y]==[138,139,140,141,142]
            old,new=inherited[142],active_units[142]
            restored=bytearray(new[:len(old)])
            restored[START:END]=active_units[214][len(DISPATCH_V2):]
            for offset,n in ((0x128,6),(0x886,6),(0x9d4,8),(0x9dc,8)):
                assert new[offset:offset+2]==b'\x60\xff'
                restored[offset:offset+n]=old[offset:offset+n]
            assert restored==old, 'Unexpected S2r inherited AGA/input-state change'
        elif digest in (S1P2I_SHA, S1P2J_SHA, S1P2K_SHA, S1P2LB_SHA, S1P2LC_SHA, S1P2M_SHA, S2A_SHA, S2B_SHA):
            # Exact source-pinned lifecycle variants contain six extra
            # AP20 entries and four audited Close/End dispatch patches.
            # Independently recover the L2b prefix by restoring ONLY those
            # four spans; never waive the inherited input-state comparison.
            from active_library import verify_s1p2i, verify_s1p2j, verify_s1p2k, verify_s1p2lb, verify_s1p2lc, verify_s1p2m, verify_s2a, verify_s2b
            from struct import unpack_from
            {S1P2I_SHA: verify_s1p2i, S1P2J_SHA: verify_s1p2j,
             S1P2K_SHA: verify_s1p2k, S1P2LB_SHA: verify_s1p2lb, S1P2LC_SHA: verify_s1p2lc, S1P2M_SHA: verify_s1p2m, S2A_SHA: verify_s2a, S2B_SHA: verify_s2b}[digest](image, frozen)
            assert sha256(frozen).hexdigest() == P2DL2B_SHA
            _, inherited, _ = unpack_ap20(frozen)
            _, active_units, _ = unpack_ap20(image)
            assert len(inherited) == 203 and len(active_units) == 214
            assert [i for i,(x,y) in enumerate(zip(inherited,active_units))
                    if x != y] == [142]
            old, new = inherited[142], active_units[142]
            assert len(old) < len(new) <= 65534 and not len(new)&1
            assert new[-16:] == bytes.fromhex('00000000414753490001001000000000')
            restored = bytearray(new[:len(old)])
            targets = []
            # Source-defined spans, reviewed against both P2f and P2k builders.
            for offset, original in (
                (0x128, bytes.fromhex('4eaeffbe4292')),
                (0x886, bytes.fromhex('61004a424292')),
                (0x9d4, bytes.fromhex('6100000e6000ff46')),
                (0x9dc, bytes.fromhex('610000066000f808')),
            ):
                assert old[offset:offset+len(original)] == original
                assert new[offset:offset+2] == b'\x60\xff'
                if len(original) == 8:
                    assert new[offset+6:offset+8] == b'\x4e\x71'
                target = offset + 2 + unpack_from('>i', new, offset+2)[0]
                assert len(old) <= target < len(new)-16 and not target&1
                targets.append(target)
                restored[offset:offset+len(original)] = original
            assert len(set(targets)) == 4
            assert restored == old, 'Unexpected inherited AGA/input-state change'
        elif digest in SPRITE_L2B_HISTORICAL_SHAS:
            # verify_active authenticated the exact candidate and its Sprite unit.
            # Independently require byte-identical inherited L2b AGA/State units.
            assert sha256(frozen).hexdigest() == P2DL2B_SHA
            _, inherited, _ = unpack_ap20(frozen)
            _, active_units, _ = unpack_ap20(image)
            assert len(inherited) == 203 and len(active_units) == 208
            assert active_units[:203] == inherited
            assert active_units[142] == inherited[142]
        elif digest == P2DL2B_SHA:
            from active_library import verify_p2d_l2b
            verify_p2d_l2b(image, candidate)
        elif digest == P2DL2_SHA:
            from active_library import verify_p2d_l2
            verify_p2d_l2(image, candidate)
        else:
            assert image == candidate
        r84, r84_meta = build_r84()
        assert len(r84) == 67904 and r84_meta['sha256'] == R84_SHA
        _, r84_units, _ = unpack_ap20(r84)
        assert len(units) == 203 and units[142].startswith(r84_units[84])
        assert units[meta['group']].startswith(DISPATCH_V2)
        ancestor, _ = build_r82()
        assert sha256(ancestor).hexdigest() == R82_SHA
        _, parts = unwrap_native_parts_v2(ancestor)
    elif digest in (R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA,P2A_SHA):
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
        assert sha256(last_good).hexdigest()==LAST_GOOD_SHA==P1E_SHA
        if digest==P1E_SHA:
            assert last_good==image, "Promoted P1e LAST_GOOD differs from active"
        from build_aga_r84_agapic import build as build_r84
        frozen_r84,r84meta=build_r84()
        assert len(frozen_r84)==67904 and r84meta['sha256']==R84_SHA
        _,units,_=unpack_ap20(image)
        _,frozen_units,_=unpack_ap20(frozen_r84)
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
            B8S1_SHA:(142,177,184),
            P0_FREE_SHA:(142,177,185),
            P1E_SHA:(142,188,196),
            P2A_SHA:(142,190,198),
        }
        aga_index,bob_index,entry_count=group_indices[digest]
        assert len(units)==entry_count, "Unexpected modular segment count"
        if digest in (AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA,P2A_SHA):
            assert units[aga_index].startswith(frozen_units[84]), "AP20 islands inherited R84 AGA/state prefix altered"
        else:
            assert units[aga_index]==frozen_units[84], "Inherited R84 AGA/state group altered"
        assert units[bob_index].startswith(DISPATCH_V2), "BOBS dispatch modified"
        if digest in (B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA,P2A_SHA):
            if digest==P2A_SHA:
                from build_m19_p2a_public_in_memory import build_p2a
                from build_m19_p1e_bank_edit_in_memory import build_p1e
                candidate,meta=build_p2a()
                ancestor,p1e_meta=build_p1e()
                _,ancestor_units,_=unpack_ap20(ancestor)
                assert image==candidate and meta['sha256']==P2A_SHA
                assert (len(image),meta['entries'],meta['public_commands'])==(129544,198,97)
                assert meta['bob_group']==190 and meta['pc16_max']==14130
                assert units[190].startswith(ancestor_units[p1e_meta['group']])
            elif digest==P1E_SHA:
                # Public P1e: source-pin five native V2 units and the
                # exact expanded AP20 directory, not monolithic unwrap.
                from build_m19_p1e_bank_edit_in_memory import build_p1e
                candidate,meta=build_p1e()
                assert image==candidate and meta['sha256']==P1E_SHA
                assert len(image)==124444 and meta['bytes']==124444
                assert meta['commands']==96 and meta['entries']==196
                assert meta['group']==188 and meta['pc16_max']==14130
            elif digest==P0_FREE_SHA:
                # P0 extends B8 S1 with Chip pre-stage and public Bank Free.
                # Verify the exact complete builder, not a V2 monolith export.
                from build_m19_b8_s1_bank_free_in_memory import build_bank_free
                candidate,meta=build_bank_free()
                assert image==candidate and meta['sha256']==P0_FREE_SHA
                assert len(candidate)==117896
                assert meta['public_commands']==89 and meta['ap20_entries']==185
                assert meta['native_groups']==[142,153,156,177,181]
                assert meta['pc16_max']==31092 and meta['bank_free_index']==184
            else:
                from build_m19_b8_first_update_in_memory import build_b8_first_update
                if digest==B8S1_SHA:
                    from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
                    candidate,meta=build_b8_safe_retry()
                else:
                    candidate,meta=build_b8_first_update()
                assert image==candidate and meta['sha256']==digest
                assert meta['public_commands']==88 and meta['ap20_entries']==184
                assert meta['native_groups']==[142,153,156,177,181]
                assert meta['pc16_max']==29962
            from build_m19_ap20_islands_in_memory import build as build_islands
            baseline,_=build_islands()
            _,earlier_groups,_=unpack_ap20(baseline)
            if digest in (P1E_SHA,P2A_SHA):
                assert units[aga_index].startswith(earlier_groups[aga_index]), "P1e altered inherited AGA/state prefix"
            else:
                assert units[aga_index]==earlier_groups[aga_index], "B8/P0 altered frozen AGA/state unit"
            if digest in (P1E_SHA,P2A_SHA):
                # P1b/P1c/P1d deliberately source-patched the old renderer.
                # Compare against the immediate P1d source-built ancestor,
                # not the pre-P1b AP20 Islands group at index 177.
                from build_m19_p1d_limit_bob_in_memory import build_p1d
                from m19_p1d_limit_bob_emit import emit_limit_bobs
                previous,p1d=build_p1d()
                _,p1d_parts,_=unpack_ap20(previous)
                p1d_native,_=emit_limit_bobs(p1d['context_delta'])
                assert p1d_parts[181].endswith(p1d_native)
                assert units[bob_index].startswith(
                    p1d_parts[181][:-len(p1d_native)]
                ), "P1e altered source-built P1d Bob prefix"
            else:
                assert units[bob_index].startswith(earlier_groups[bob_index]), "B8/P0 altered frozen Bob prefix"
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
        assert sha256(last_good).hexdigest()==LAST_GOOD_SHA
        from build_aga_r84_agapic import build as build_r84
        frozen_r84,_=build_r84()
        assert sha256(frozen_r84).hexdigest()==R84_SHA
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
            last_tokens,last_parts,_=unpack_ap20(frozen_r84)
            assert units[86]==last_parts[84], "R85 altered protected AGA native bytes"
            assert units[85].startswith(DISPATCH_V2), "R85 BOBS group missing"
        core=units[idx][len(DISPATCH_V2):]
        frozen_aga=b"".join(original[:70])
        assert core[:len(frozen_aga)]==frozen_aga, "R83 active AGA/State code changed"
        parts=original
    else:
        _,parts=unwrap_native_parts_v2(image)
    target=check(parts)
    if digest in (P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, *SPRITE_L2B_HISTORICAL_SHAS):
        assert target == 12070, 'P2d/S1 input State displacement changed'
    negative_cases(parts)
    print("CURRENT INPUT DATA PASS: offset",target,"7 LEAs, 8 negatives; active SHA-pinned multi-unit input-state lineage verified against R82/R84")

if __name__=="__main__":
    main()
