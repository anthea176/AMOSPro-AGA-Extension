#!/usr/bin/env python3
"""Current integrity: R24 Hotspot Hit; R23/R22/R21/R20/R19/R18/M6 and R10 frozen."""
from pathlib import Path
import hashlib
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
HASHES = {
    "dist/AMOSPro_AGA.Lib": "cc8776e7303c529492fe6761544f4b2be1180063f3787fa840f44129766e3671",
    "dist/experimental/AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib": "cc8776e7303c529492fe6761544f4b2be1180063f3787fa840f44129766e3671",
    "dist/experimental/AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib": "899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23",
    "dist/experimental/AMOSPro_AGA_M8_v0.8.6_MOUSE_EDGES_R22.Lib": "96e38d478bd97e7a65801e16e96ce08c0bbd4aaacb4a8a6644e4bc1289a0c997",
    "dist/experimental/AMOSPro_AGA_M8_v0.8.5_RMBTRAP_R21.Lib": "a72e3046df64e3ff8ebe12a5b4b0db45efebe27e17056919d31d11ca61e9c644",
    "dist/experimental/AMOSPro_AGA_M8_v0.8.4_MOUSE_BUTTONS_R20.Lib": "9d1e9d6fd13478947c016d3f95973efa2ac766f96c364e091f43c69daa8672fe",
    "dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib": "32c99d9d83affda67058fede26731dace6511ebc033b7974330e6f9eef39e295",
    "dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib": "600b8c2c38486004adef8c0e7924df877f7dd7829e1c622a89bbdc0db9f9808a",
    "dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib": "cfd73961d6cf75a6c57ed529b2bacc11908cd96a0aad615e325597d5bfb0a02a",
    "dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib": "ba55e92f1d50339b50a06c5b1903767bde549e6738dae320a0ef9ead6251bab1",
    "dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib": "44530d28cc33ab2aa1bb9bd81aa3f9799e3aca67a714c36891888c3ece4c6e6e",
    "dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib": "a8c43c478efdb2ddcb3547a807a2dba60bd125fc0d7ab5bb791ef565aeb90e4f",
    "dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib": "c71cab88d2294ed70c019f546d6c60ac72c278c1b625ded07d0aa6603e50a0cf",
    "dist/AMOSPro_AGA_LAST_GOOD.Lib": "e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3",
    "dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib": "b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec",
    "dist/experimental/AMOSPro_AGA_M5_v0.6.2_JEFF_POSITION_R11.Lib": "0e2419965f411c4e9419b1c7c8d07debdde525f13f7b8da80e2ed9d3ee30ea7b",
    "dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib": "e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3",
    "dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib": "58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c",
    "dist/experimental/AMOSPro_AGA_M5_v0.5.9_DB_SYNC_R8.Lib": "112dce3e7945a235430a0263e309126061639de0d8dcc0d9c319431b0f2f27a2",
    "dist/experimental/AMOSPro_AGA_M5_v0.4.5_M52R4.Lib": "b09a94bd4e1ce1487e2776c39e1dd3f75752dcf6f472261af178f47b584b2178",
    "dist/experimental/AMOSPro_AGA_M5_v0.4.6_M52R5.Lib": "33092d2affbc8fd1d74762cc56cb50d465b34ef71677bfaaa10b408a70cc3715",
    "archive/AMOSPro_AGA_M4b_v0.0.9_R6C_R1_WinUAE_OK.Lib": "a2d36ac198b5bfe18d50a223f4001c8ce0773d15310145d9d081abaddc2a6615",
    "dist/experimental/AMOSPro_AGA_M4b_v0.0.9_R6C_R1.Lib": "a2d36ac198b5bfe18d50a223f4001c8ce0773d15310145d9d081abaddc2a6615",
}


def verify_hunk(path):
    data = path.read_bytes()
    assert len(data) >= 36 and len(data) % 4 == 0, path
    head = struct.unpack_from(">8I", data)
    assert head[:5] == (0x3F3, 0, 1, 0, 0), path
    assert head[6] == 0x3E9 and head[5] == head[7], path
    assert len(data) == 36 + 4 * head[7], path
    assert data[-4:] == struct.pack(">I", 0x3F2), path
    return data


def main():
    sys.path.insert(0, str(ROOT / "tools"))
    from audit_ap20 import parse, inspect
    from ap20_utils import split
    from build_m5_generic import build as generic_r1, DEST as r1archive, OUT_SHA as r1sha
    from build_m5_generic_r2 import build as generic_r2, DEST as r2archive, OUT_SHA as r2sha
    from build_newscreen_a0_r12 import build as build_r12
    from build_m6_blit_copy_r13 import build as build_r13
    from build_m6_blit_fill_r14 import build as build_r14
    from build_m6_blit_clear_r15 import build as build_r15
    from build_m7_copper_clear_r16 import build as build_r16
    from build_m7_copper_on_off_r17 import build as build_r17
    from build_m7_copper_raster_r18 import build as build_r18, CINIT_2, CINIT_64
    from build_m8_mouse_position_r19 import build as build_r19, mouse_routine
    from build_m8_mouse_buttons_r20 import build as build_r20, emit_buttons
    from build_m8_rmbtrap_r21 import build as build_r21, OLD_OPCODE, NEW_OPCODE, SCREEN_OPEN_FLAGS_OFFSET
    from build_m8_mouse_edges_r22 import build as build_r22, patch_open_reset
    from build_m8_idcmp_r23 import build as build_r23, ENTRY_DISPATCH
    from build_m9_hotspot_hit_r24 import build as build_r24, ENTRY as HOTSPOT_ENTRY

    binaries = {}
    for relative, expected in HASHES.items():
        raw = verify_hunk(ROOT / relative)
        assert hashlib.sha256(raw).hexdigest() == expected, relative
        binaries[relative] = raw

    candidate = binaries["dist/AMOSPro_AGA.Lib"]
    r10 = binaries["dist/AMOSPro_AGA_LAST_GOOD.Lib"]
    assert candidate == binaries["dist/experimental/AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib"]
    assert r10 == binaries["dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib"]
    assert binaries["archive/AMOSPro_AGA_M4b_v0.0.9_R6C_R1_WinUAE_OK.Lib"] == binaries["dist/experimental/AMOSPro_AGA_M4b_v0.0.9_R6C_R1.Lib"]

    raw_r1, _ = generic_r1()
    raw_r2, _ = generic_r2()
    assert hashlib.sha256(raw_r1).hexdigest() == r1sha
    assert hashlib.sha256(raw_r2).hexdigest() == r2sha
    assert raw_r1 == verify_hunk(r1archive)
    assert raw_r2 == verify_hunk(r2archive)

    built12, _ = build_r12()
    assert built12 == binaries["dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib"] == build_r12()[0], "R12 not reproducible"
    built13, _ = build_r13()
    assert built13 == binaries["dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib"] == build_r13()[0], "R13 not reproducible"
    built14, _ = build_r14()
    assert built14 == binaries["dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib"] == build_r14()[0], "R14 not reproducible"
    built15, _ = build_r15()
    assert built15 == binaries["dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib"] == build_r15()[0], "R15 not reproducible"
    built16, _ = build_r16()
    assert built16 == binaries["dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib"] == build_r16()[0], "R16 not reproducible"
    built17, _ = build_r17()
    assert built17 == binaries["dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib"] == build_r17()[0], "R17 not reproducible"
    built18, _ = build_r18()
    assert built18 == binaries["dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib"] == build_r18()[0], "R18 not reproducible"
    built19, _ = build_r19()
    assert built19 == binaries["dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib"] == build_r19()[0], "R19 not reproducible"
    built20, _ = build_r20()
    assert built20 == binaries["dist/experimental/AMOSPro_AGA_M8_v0.8.4_MOUSE_BUTTONS_R20.Lib"] == build_r20()[0], "R20 not reproducible"
    built21, _ = build_r21()
    assert built21 == binaries["dist/experimental/AMOSPro_AGA_M8_v0.8.5_RMBTRAP_R21.Lib"] == build_r21()[0], "R21 not reproducible"
    built22, detail22 = build_r22()
    assert built22 == binaries["dist/experimental/AMOSPro_AGA_M8_v0.8.6_MOUSE_EDGES_R22.Lib"] == build_r22()[0], "R22 not reproducible"
    built23, detail23 = build_r23()
    assert built23 == binaries["dist/experimental/AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib"] == build_r23()[0], "R23 not reproducible"
    built24, detail24 = build_r24()
    assert candidate == built24 == build_r24()[0], "R24 not reproducible"
    assert inspect(parse(candidate))["issues"] == []
    assert inspect(parse(built14))["issues"] == []
    assert inspect(parse(built13))["issues"] == []
    assert inspect(parse(built12))["issues"] == []
    assert inspect(parse(r10))["issues"] == []
    tok10, seg10, _ = split(r10)
    tok12, seg12, _ = split(built12)
    tok13, seg13, _ = split(built13)
    tok14, seg14, _ = split(built14)
    tok15, seg15, _ = split(built15)
    tok16, seg16, _ = split(built16)
    tok17, seg17, _ = split(built17)
    tok18, seg18, _ = split(built18)
    tok19, seg19, _ = split(built19)
    tok20, seg20, _ = split(built20)
    tok21, seg21, _ = split(built21)
    tok22, seg22, _ = split(built22)
    tok23, seg23, _ = split(built23)
    tok24, seg24, _ = split(candidate)
    assert tok10 == tok12
    assert len(seg10) == len(seg12) == 19 and len(seg13) == 20
    assert [i for i in range(19) if seg10[i] != seg12[i]] == [6]
    assert seg13[:18] == seg12[:18]
    assert seg13[18] == seg12[18] + b"GetP"
    assert tok13 != tok12 and seg13[19]
    assert len(seg14) == 21
    assert seg14[:19] == seg13[:19], "R13 entries 0..18 changed"
    assert seg14[19] == seg13[19] + b"GetP", "R13 Copy changed"
    assert tok14 != tok13 and seg14[20]
    assert len(seg15) == 22
    assert seg15[:20] == seg14[:20], "R14 or earlier entries altered"
    assert seg15[20] == seg14[20] + b"GetP", "R14 Fill altered"
    assert tok15 != tok14 and seg15[21]
    assert len(seg16) == 23 and seg16[:22] == seg15, "R15 segments modified"
    assert tok16 != tok15 and seg16[22], "R16 Copper entry missing"
    assert len(seg17) == 25 and seg17[:22] == seg16[:22]
    assert seg17[22] == seg16[22] + b"GetP", "R16 Copper Clear changed"
    assert seg17[23][-4:] == b"GetP" and seg17[24], "R17 On/Off missing"
    assert tok17 != tok16
    assert len(seg18) == 28 and seg18[:22] == seg17[:22], "R18 changed M5/M6"
    assert seg17[22].count(CINIT_2) == 1 and seg18[22] == seg17[22].replace(CINIT_2, CINIT_64), "R18 Clear capacity delta"
    assert seg18[23] != seg17[23] and seg18[24] != seg17[24], "R18 On/Off gating delta"
    assert seg18[25].endswith(b"GetP") and seg18[26] and seg18[27], "R18 Wait/Move/End missing"
    assert tok18 != tok17
    assert len(seg19) == 30 and seg19[:27] == seg18[:27], "R19 changed preexisting entries"
    assert seg19[27] == seg18[27] + b"GetP", "R19 changed R18 Copper End"
    assert seg19[28] == mouse_routine("x")[0] + b"GetP"
    assert seg19[29] == mouse_routine("y")[0]
    assert tok19 != tok18
    assert len(seg20) == 31 and seg20[:29] == seg19[:29], "R20 altered R19 routines"
    assert seg20[29] == seg19[29] + b"GetP", "R20 changed R19 Mouse Y"
    assert seg20[30] == emit_buttons()[0] and tok20 != tok19, "R20 buttons missing"
    assert not inspect(parse(candidate))["issues"]

    assert tok21 == tok20, "R21 AP20 token table changed"
    assert len(seg21) == 31
    assert [i for i in range(31) if seg21[i] != seg20[i]] == [6], "R21 changed routines beyond Screen Open"
    assert (seg20[6][SCREEN_OPEN_FLAGS_OFFSET:SCREEN_OPEN_FLAGS_OFFSET+8] == OLD_OPCODE
            and seg21[6][SCREEN_OPEN_FLAGS_OFFSET:SCREEN_OPEN_FLAGS_OFFSET+8] == NEW_OPCODE)
    assert sum(x != y for x, y in zip(seg20[6], seg21[6])) == 1
    assert seg21[30] == emit_buttons()[0], "R21 altered R20 button routine"
    assert len(seg22) == 33 and len(seg21) == 31
    assert [i for i in range(31) if seg21[i] != seg22[i]] == [6, 30]
    assert seg22[6] == patch_open_reset(seg21[6], detail22["state_delta"])
    assert seg22[30] == seg21[30] + b"GetP"
    assert tok22.startswith(tok21[:-6])
    assert seg22[28:30] == seg21[28:30], "R22 altered mouse X/Y"
    assert inspect(parse(candidate))["issues"] == []
    assert tok23 == tok22, "R23 added or altered an AMOS command token"
    assert len(seg23) == len(seg22) + 1 == 34
    assert [i for i in range(33) if seg22[i] != seg23[i]] == [6, 17, 18, 31, 32]
    assert seg23[ENTRY_DISPATCH] and seg23[ENTRY_DISPATCH][-144:] == bytes(144)
    assert inspect(parse(candidate))["issues"] == []
    assert tok24.startswith(tok23[:-6]) and tok24 != tok23, "R24 missing AP20 token"
    assert len(seg24) == len(seg23) + 1 == HOTSPOT_ENTRY+1 == 35
    assert seg24[:HOTSPOT_ENTRY-1] == seg23[:HOTSPOT_ENTRY-1]
    assert seg24[HOTSPOT_ENTRY-1] == seg23[HOTSPOT_ENTRY-1] + b"GetP"
    assert seg24[HOTSPOT_ENTRY-1][-148:-4] == bytes(144), "R23 input state moved"
    assert seg24[HOTSPOT_ENTRY], "R24 hotspot 68000 code missing"
    assert not inspect(parse(candidate))["issues"], "R24 AP20 malformed"
    print("PASS: R24 current/archive reproducible; R23/R22/R21/R20/R19/R18/R17/R16/M6 frozen,"
          " LAST_GOOD R10 intact")


if __name__ == "__main__":
    main()
