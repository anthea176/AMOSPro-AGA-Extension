#!/usr/bin/env python3
"""Current integrity: R32 candidate current, R31 WinUAE-PASS LAST_GOOD, R30 archive frozen."""
from pathlib import Path
import hashlib
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
HASHES = {
    "dist/AMOSPro_AGA.Lib": "0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib": "0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib": "0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib": "446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib": "fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib": "ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c",
    "dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib": "64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe",
    "dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib": "0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287",
    "dist/experimental/AMOSPro_AGA_M10_v0.9.1_RECT_OVERLAP_R25.Lib": "4835473771629bea697d64c9213ff1064013597f7dabc519914f4ea013af6da6",
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
    "dist/AMOSPro_AGA_LAST_GOOD.Lib": "0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41",
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
    from build_m10_rect_overlap_r25 import build as build_r25, ENTRY as RECT_ENTRY
    from build_m11_text_r26 import build as build_r26, ENTRY as TEXT_ENTRY
    from build_m12_blit_safe_r27 import build as build_r27, RELOCATED
    from build_m13_palette_r28 import build as build_r28, OLD_ENTRIES, ENTRY_LOAD, ENTRY_SET, ENTRY_GET, GETP, API
    from build_m13_palette_save_r29 import build as build_r29, ENTRY_SAVE, API as API_R29
    from build_m13_agapal_r30 import build as build_r30, ENTRY_INDEX as ENTRY_INIT, API as API_R30
    from build_m13_agapal_capture_r31 import build as build_r31, ENTRY_CAPTURE, API as API_R31
    from build_m13_agapal_apply_r32 import build as build_r32, ENTRY_APPLY, API as API_R32

    binaries = {}
    for relative, expected in HASHES.items():
        raw = verify_hunk(ROOT / relative)
        assert hashlib.sha256(raw).hexdigest() == expected, relative
        binaries[relative] = raw

    candidate = binaries["dist/AMOSPro_AGA.Lib"]
    r10 = binaries["dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib"]
    r27 = binaries["dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib"]
    assert binaries["dist/AMOSPro_AGA_LAST_GOOD.Lib"] == binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib"]
    r28 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib"]
    r29 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib"]
    r30 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib"]
    r31 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib"]
    r32 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib"]
    assert candidate == r32, "dist must contain the actual R32 test candidate"
    r26 = binaries["dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib"]
    r25 = binaries["dist/experimental/AMOSPro_AGA_M10_v0.9.1_RECT_OVERLAP_R25.Lib"]
    assert hashlib.sha256(r10).hexdigest() == "e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3", "historical R10 archive mutated"
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
    assert built24 == binaries["dist/experimental/AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib"] == build_r24()[0], "R24 not reproducible"
    built25, detail25 = build_r25()
    assert r25 == built25 == build_r25()[0], "Frozen R25 not reproducible"
    built26, detail26 = build_r26()
    assert r26 == built26 == build_r26()[0], "Frozen R26 not reproducible"
    built27, detail27 = build_r27()
    assert r27 == built27 == build_r27()[0], "Frozen R27 not reproducible"
    built28, info28 = build_r28()
    assert r28 == built28 == build_r28()[0], "frozen R28 not reproducible"
    built29, info29 = build_r29()
    assert r29 == built29 == build_r29()[0], "frozen R29 not reproducible"
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
    tok24, seg24, _ = split(built24)
    tok25, seg25, _ = split(r25)
    tok26, seg26, _ = split(r26)
    tok27, seg27, _ = split(r27)
    tok28, seg28, _ = split(r28)
    tok29, seg29, _ = split(r29)
    tok30, seg30, _ = split(r30)
    tok31, seg31, _ = split(r31)
    tok32, seg32, _ = split(r32)
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
    assert not inspect(parse(built24))["issues"], "R24 AP20 malformed"
    assert tok25.startswith(tok24[:-6]) and tok25 != tok24, "R25 token missing"
    assert len(seg25) == len(seg24) + 1 == RECT_ENTRY + 1 == 36
    assert seg25[:RECT_ENTRY-1] == seg24[:RECT_ENTRY-1], "R25 moved prior routines"
    assert seg25[RECT_ENTRY-1] == seg24[RECT_ENTRY-1] + b"GetP", "R24 hotspot modified"
    assert seg25[RECT_ENTRY], "R25 rect overlap code missing"
    assert not inspect(parse(candidate))["issues"], "R25 AP20 invalid"
    assert tok26.startswith(tok25[:-6]) and tok26 != tok25, "R26 token missing"
    assert len(seg26) == len(seg25) + 1 == TEXT_ENTRY + 1 == 37
    assert seg26[:TEXT_ENTRY-1] == seg25[:TEXT_ENTRY-1], "R26 changed previous entries"
    assert seg26[TEXT_ENTRY-1] == seg25[TEXT_ENTRY-1] + b"GetP", "R25 rect entry altered"
    assert seg26[TEXT_ENTRY], "R26 Text missing"
    assert not inspect(parse(candidate))["issues"], "R26 AP20 invalid"
    assert tok27 == tok26, "R27 must retain the R26 AMOS token table"
    assert len(seg27) == len(seg26) == 37
    assert [i for i in range(37) if seg27[i] != seg26[i]] == list(RELOCATED), (
        "R27 changed entries beyond Safe Blitters and R23 audited relocation"
    )
    assert seg27[TEXT_ENTRY] == seg26[TEXT_ENTRY], "R26 AGA Text changed"
    assert not inspect(parse(candidate))["issues"], "R27 AP20 invalid"
    assert len(seg28)==40 and OLD_ENTRIES==len(seg27)==37
    assert seg28[:36]==seg27[:36], "R28 modified frozen R27 entries"
    assert seg28[36]==seg27[36]+GETP, "R28 modified frozen Aga Text"
    assert seg28[ENTRY_LOAD].endswith(GETP) and seg28[ENTRY_SET].endswith(GETP)
    assert seg28[ENTRY_GET] and not seg28[ENTRY_GET].endswith(GETP)
    assert tok28.startswith(tok27[:-6]) and tok28!=tok27
    audit28=inspect(parse(r28))
    assert not audit28["issues"], "R28 AP20 invalid"
    named28=[r for r in audit28["tokens"] if r["name"].startswith("aga ")]
    assert len(named28)==34
    for name,index,sig in API:
        rows=[r for r in named28 if r["name"]==name]
        assert len(rows)==1 and rows[0]["function"]==index
        assert rows[0]["signature"]==sig
    assert len(seg29)==41 and seg29[:39]==seg28[:39], "R29 changed frozen R28 code"
    assert seg29[39]==seg28[39]+GETP, "R29 must add GetP to R28 final entry only"
    assert seg29[ENTRY_SAVE] and not seg29[ENTRY_SAVE].endswith(GETP)
    assert tok29.startswith(tok28[:-6]) and tok29!=tok28
    audit29=inspect(parse(r29))
    assert not audit29["issues"], "R29 AP20 invalid"
    named29=[r for r in audit29["tokens"] if r["name"].startswith("aga ")]
    assert len(named29)==35
    for name,index,sig in API_R29:
        rows=[r for r in named29 if r["name"]==name]
        assert len(rows)==1 and (rows[0]["instruction"],rows[0]["function"],rows[0]["signature"])==(1,index,sig)
    assert len(seg30)==42 and seg30[:40]==seg29[:40], "R30 modified inherited R29 entries"
    assert seg30[40]==seg29[40]+GETP, "R30 changed R29 Save instead of adding GetP"
    assert seg30[ENTRY_INIT] and not seg30[ENTRY_INIT].endswith(GETP), "R30 Init missing"
    assert tok30.startswith(tok29[:-6]) and tok30!=tok29
    audit30=inspect(parse(r30))
    assert not audit30["issues"], "R30 AP20 invalid"
    named30=[r for r in audit30["tokens"] if r["name"].startswith("aga ")]
    assert len(named30)==36, "R30 named command count"
    for name,index,sig in API_R30:
        rows=[r for r in named30 if r["name"]==name]
        assert len(rows)==1 and (rows[0]["instruction"],rows[0]["function"],rows[0]["signature"])==(1,index,sig)
    built30,info30=build_r30()
    assert r30==built30==build_r30()[0], "frozen R30 not reproducible"
    assert len(seg31)==43 and seg31[:41]==seg30[:41], "R31 changed inherited R30 code"
    assert seg31[41]==seg30[41]+GETP, "R31 changed R30 Bank Init except GetP"
    assert seg31[ENTRY_CAPTURE] and not seg31[ENTRY_CAPTURE].endswith(GETP)
    assert tok31.startswith(tok30[:-6]) and tok31!=tok30
    audit31=inspect(parse(r31))
    assert not audit31["issues"], "R31 AP20 invalid"
    named31=[row for row in audit31["tokens"] if row["name"].startswith("aga ")]
    assert len(named31)==37, "R31 named-command count"
    for name,index,sig in API_R31:
        matches=[row for row in named31 if row["name"]==name]
        assert len(matches)==1 and (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,index,sig)
    built31, info31=build_r31()
    assert r31==built31==build_r31()[0], "frozen R31 not reproducible"
    assert len(seg32)==44 and seg32[:42]==seg31[:42], "R32 modified inherited R31 segments"
    assert seg32[42]==seg31[42]+GETP, "R32 changed frozen R31 Capture except GetP"
    assert seg32[ENTRY_APPLY] and not seg32[ENTRY_APPLY].endswith(GETP), "R32 Apply missing"
    assert tok32.startswith(tok31[:-6]) and tok32!=tok31
    audit32=inspect(parse(r32))
    assert not audit32["issues"], "R32 AP20 invalid"
    named32=[row for row in audit32["tokens"] if row["name"].startswith("aga ")]
    assert len(named32)==38, "R32 named-command count"
    for name,index,sig in API_R32:
        matches=[row for row in named32 if row["name"]==name]
        assert len(matches)==1 and (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,index,sig)
    built32,info32=build_r32()
    assert candidate==r32==built32==build_r32()[0], "R32 current/archive not reproducible"
    assert candidate!=r31
    assert binaries["dist/AMOSPro_AGA_LAST_GOOD.Lib"]==r31
    print("PASS: R32 current/archive 38 AP20 tokens; LAST_GOOD is WinUAE-PASS R31;"
          " R10 historical archive and R26/R25/R24/R23/R22/R21/R20/R19/R18/R17/R16/M6 frozen")


if __name__ == "__main__":
    main()
