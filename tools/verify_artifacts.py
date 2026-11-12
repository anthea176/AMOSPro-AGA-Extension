#!/usr/bin/env python3
"""Integrity: R46 C1 official Gate A/B/C integrated PASS; all earlier archives frozen."""
from pathlib import Path
import hashlib
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
HASHES = {
    "dist/AMOSPro_AGA.Lib": "d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib": "5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.2_IMAGE_CAPTURE_R47_CANDIDATE.Lib": "a550e9662cda1890aa8331c6e849e702300e6070e8e2caaf2fab9918613944d5",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.3_R48_TOKEN_ABI_PROBE.Lib": "c30cfcc33ee50bb1f18c36225ccd7a5a6df7860e11201608d1801a0095687028",
    "dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib": "d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib": "0d780b4648214c36e8f291d9575390462d174cd8ba22cac2188324b75bd220d7",
    "dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib": "0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc",
    "dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib": "9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf",
    "dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib": "6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc",
    "dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib": "0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc",
    "dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib": "0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231",
    "dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib": "09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366",
    "dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38_FAILED_BANK0.Lib": "948b9df308487ad9d8c427a25a04ab713725848a077e97d5966a6b8a393f94c5",
    "dist/experimental/AMOSPro_AGA_M14_v0.10.9_FONT_SELECT_R37.Lib": "bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib": "f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib": "ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib": "89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033",
    "dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib": "e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f",
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
    "dist/AMOSPro_AGA_LAST_GOOD.Lib": "d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b",
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
    from build_m13_agapal_fade_r33 import build as build_r33, ENTRY_FADE, API as API_R33
    from build_m13_aga_fade_black_r34 import build as build_r34, ENTRY_BLACK, API as API_R34
    from build_m13_aga_fade_white_r35 import build as build_r35, ENTRY_WHITE, API as API_R35
    from build_m13_palette_cycle_r36 import build as build_r36, ENTRY_CYCLE, API as API_R36
    from build_m14_font_select_r37 import build as build_r37, ENTRY_FONT_SELECT, API as API_R37
    from build_m14_font_bank_r38 import build as build_r38, ENTRY_INDEX as ENTRY_BANK_FONT, API as API_R38
    from build_m15_plot_r40 import build as build_r40, ENTRY_INDEX as ENTRY_PLOT, API as API_R40
    from build_m15_draw_r41 import build as build_r41, ENTRY_INDEX as ENTRY_DRAW, API as API_R41
    from build_m15_box_r42 import build as build_r42, ENTRY_INDEX as ENTRY_BOX, API as API_R42
    from build_m15_circle_r43 import build as build_r43, ENTRY_INDEX as ENTRY_CIRCLE, API as API_R43
    from build_m15bis_cursor_r44 import build as build_r44, ENTRY_INDEX as ENTRY_CURSOR, API as API_R44, OWNED_CLOSES
    from build_m16_image_draw_r45 import build as build_r45, ENTRY_INDEX as ENTRY_IMAGE, API as API_R45
    from build_m16_image_draw_r46 import build as build_r46
    from build_aga_current import build as build_current
    from compiler_relocation import unwrap_native_parts, native_from_promoted, wrap_native_ap20, unpack_ap20, is_compiler_wrapped

    binaries = {}
    for relative, expected in HASHES.items():
        raw = verify_hunk(ROOT / relative)
        assert hashlib.sha256(raw).hexdigest() == expected, relative
        binaries[relative] = raw

    candidate = binaries["dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"]  # frozen R44 for inherited historical assertions
    candidate_r45 = binaries["dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib"]
    candidate_r46 = binaries["dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib"]  # frozen native raw R46
    promoted = binaries["dist/AMOSPro_AGA.Lib"]  # 57-entry compiler-safe C1
    r10 = binaries["dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib"]
    r27 = binaries["dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib"]
    assert binaries["dist/AMOSPro_AGA_LAST_GOOD.Lib"] == promoted
    assert promoted == binaries["dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"]
    r28 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib"]
    r29 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib"]
    r30 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib"]
    r31 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib"]
    r32 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib"]
    r33 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib"]
    r34 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib"]
    r35 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib"]
    r36 = binaries["dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib"]
    assert candidate == binaries["dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"], "R44 candidate/archive mismatch"
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
    tok33, seg33, _ = split(r33)
    tok34, seg34, _ = split(r34)
    tok35, seg35, _ = split(r35)
    tok36, seg36, _ = split(r36)
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
    assert r32==built32==build_r32()[0], "R32 frozen archive not reproducible"
    assert r32!=r31
    assert len(seg33)==45 and seg33[:43]==seg32[:43], "R33 modified frozen R32 segments"
    assert seg33[43]==seg32[43]+GETP, "R33 changed R32 Apply except GetP"
    assert seg33[ENTRY_FADE] and not seg33[ENTRY_FADE].endswith(GETP), "R33 Fade missing"
    assert tok33.startswith(tok32[:-6]) and tok33!=tok32
    audit33=inspect(parse(r33))
    assert not audit33["issues"],"R33 AP20 invalid"
    named33=[row for row in audit33["tokens"] if row["name"].startswith("aga ")]
    assert len(named33)==39, "R33 named-command count"
    for name,index,sig in API_R33:
        matches=[row for row in named33 if row["name"]==name]
        assert len(matches)==1 and (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,index,sig)
    built33,info33=build_r33()
    assert r33==built33==build_r33()[0], "R33 frozen archive not reproducible"
    assert r33!=r32
    assert len(seg34)==46 and seg34[:44]==seg33[:44], "R34 modified frozen R33 segments"
    assert seg34[44]==seg33[44]+GETP, "R34 changed R33 Fade except GetP"
    assert seg34[ENTRY_BLACK] and not seg34[ENTRY_BLACK].endswith(GETP), "R34 segment missing"
    assert tok34.startswith(tok33[:-6]) and tok34!=tok33
    audit34=inspect(parse(r34))
    assert not audit34["issues"],"R34 AP20 invalid"
    named34=[row for row in audit34["tokens"] if row["name"].startswith("aga ")]
    assert len(named34)==40, "R34 named-command count"
    for name,index,sig in API_R34:
        matches=[row for row in named34 if row["name"]==name]
        assert len(matches)==1 and (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,index,sig)
    built34,info34=build_r34()
    assert r34==built34==build_r34()[0], "R34 frozen archive not reproducible"
    assert r34!=r33
    assert len(seg35)==47 and seg35[:45]==seg34[:45], "R35 changed frozen R34 segments"
    assert seg35[45]==seg34[45]+GETP, "R35 changed R34 Black except GetP"
    assert seg35[ENTRY_WHITE] and not seg35[ENTRY_WHITE].endswith(GETP), "R35 White segment missing"
    assert tok35.startswith(tok34[:-6]) and tok35!=tok34
    audit35=inspect(parse(r35))
    assert not audit35["issues"],"R35 AP20 invalid"
    named35=[row for row in audit35["tokens"] if row["name"].startswith("aga ")]
    assert len(named35)==41, "R35 named-command count"
    for name,index,sig in API_R35:
        matches=[row for row in named35 if row["name"]==name]
        assert len(matches)==1 and (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,index,sig)
    built35,info35=build_r35()
    assert r35==built35==build_r35()[0], "R35 frozen archive not reproducible"
    assert r35!=r34
    assert len(seg36)==48 and seg36[:46]==seg35[:46], "R36 changed frozen R35 code"
    assert seg36[46]==seg35[46]+GETP, "R36 changed R35 White except GetP"
    assert seg36[ENTRY_CYCLE] and not seg36[ENTRY_CYCLE].endswith(GETP), "R36 Cycle missing"
    assert tok36.startswith(tok35[:-6]) and tok36!=tok35
    audit36=inspect(parse(r36))
    assert not audit36["issues"], "R36 AP20 invalid"
    named36=[row for row in audit36["tokens"] if row["name"].startswith("aga ")]
    assert len(named36)==42, "R36 named-command count"
    for name,index,sig in API_R36:
        matched=[row for row in named36 if row["name"]==name]
        assert len(matched)==1 and (matched[0]["instruction"],matched[0]["function"],matched[0]["signature"])==(1,index,sig)
    built36,meta36=build_r36()
    assert r36==built36==build_r36()[0], "R36 immutable archive not reproducible"
    assert binaries["dist/AMOSPro_AGA_LAST_GOOD.Lib"]==promoted
    built37,meta37=build_r37()
    assert built37==build_r37()[0]==binaries["dist/experimental/AMOSPro_AGA_M14_v0.10.9_FONT_SELECT_R37.Lib"], "R37 archived build not reproducible"
    tok37,seg37,_=split(built37)
    assert len(seg37)==49 and len(seg36)==48 and seg37[47]==seg36[47]+b"GetP"
    assert [i for i in range(48) if seg37[i]!=seg36[i]]==[8,36,47], "R37 changed unrelated AP20 entries"
    assert tok37.startswith(tok36[:-6]) and tok37!=tok36
    audit37=inspect(parse(built37))
    assert not audit37["issues"], "R37 AP20 invalid"
    named37=[x for x in audit37["tokens"] if x["name"].startswith("aga ")]
    assert len(named37)==43 and sum(x["name"]=="aga font select" for x in named37)==1
    for name,index,sig in API_R37:
        found=[x for x in named37 if x["name"]==name]
        assert len(found)==1 and found[0]["function"]==index and found[0]["signature"]==sig
    assert built37!=r36 and meta37["sha256"]=="bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a"
    assert (ROOT/"tests/passed/M14_R37_FONT_SELECT_01.asc").is_file(), "R37 passed test not archived"
    assert not (ROOT/"tests/current/M14_R37_FONT_SELECT_01.asc").exists(), "R37 passed test must stay archived"
    built38,meta38=build_r38()
    assert built38==build_r38()[0]==binaries["dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib"], "R38 archived build not reproducible"
    tok38,seg38,_=split(built38)
    assert len(seg38)==50 and len(seg37)==49, "R38 AP20 segment count"
    assert seg38[:48]==seg37[:48] and seg38[48][:-4]!=seg37[48], "R38 modified frozen R37 entries"
    assert seg38[48][-4:]==b"GetP" and seg38[49], "R38 missing segment delimiter"
    assert tok38.startswith(tok37[:-6]) and tok38!=tok37
    audit38=inspect(parse(built38))
    assert not audit38["issues"], "R38 AP20 invalid"
    named38=[x for x in audit38["tokens"] if x["name"].startswith("aga ")]
    assert len(named38)==44 and sum(x["name"]=="aga font bank select" for x in named38)==1
    for name,index,sig in API_R38:
        found=[x for x in named38 if x["name"]==name]
        assert len(found)==1 and found[0]["function"]==index and found[0]["signature"]==sig
    assert meta38["sha256"]=="09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366" and meta38["size"]==23380
    assert (ROOT/"tests/passed/M14_R38_FONT_BANK_01.asc").is_file(), "R38 WinUAE PASS test must be archived"
    assert not (ROOT/"tests/current/M14_R38_FONT_BANK_01.asc").exists(), "R38 current test must be cleared"
    stress = ROOT/"tests/passed/M14_R38_CHIP_RAM_STRESS_01.asc"
    assert stress.is_file(), "R38 WinUAE memory stress test must be archived"
    stress_bytes = stress.read_bytes()
    git_blob = b"blob " + str(len(stress_bytes)).encode("ascii") + bytes([0]) + stress_bytes
    assert hashlib.sha1(git_blob).hexdigest()=="976635ad8562c88ed07753c71a4dc2a6d18c2e29", "R38 memory stress test bytes changed"
    assert not (ROOT/"tests/current/M14_R38_CHIP_RAM_STRESS_01.asc").exists(), "R38 WinUAE PASS memory stress test must be removed from current"

    built40,meta40=build_r40()
    assert built40==build_r40()[0]==binaries["dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib"], "R40 archived build not reproducible"
    assert meta40["sha256"]=="0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231" and meta40["size"]==23840
    tok40,seg40,_=split(built40)
    assert len(seg40)==51 and len(seg38)==50, "R40 segment count"
    assert seg40[:49]==seg38[:49], "R40 modified frozen R38 AP20 entries"
    assert seg40[49]==seg38[49]+b"GetP", "R40 changed R38 BankFont other than GetP"
    assert seg40[50], "R40 missing Plot entry"
    assert tok40.startswith(tok38[:-6]) and tok40!=tok38, "R40 token change invalid"
    audit40=inspect(parse(built40))
    assert not audit40["issues"], audit40["issues"]
    named40=[x for x in audit40["tokens"] if x["name"].startswith("aga ")]
    assert len(named40)==45 and sum(x["name"]=="aga plot" for x in named40)==1
    for name,index,sig in API_R40:
        found=[x for x in named40 if x["name"]==name]
        assert len(found)==1 and (found[0]["instruction"],found[0]["function"],found[0]["signature"])==(1,index,sig)
    assert any(x["index"]==ENTRY_PLOT and x["parameters"]==3 and x["getp"] for x in audit40["parameter_checks"])
    assert (ROOT/"tests/passed/M15_R40_PLOT_01.asc").is_file(), "R40 WinUAE test must be archived"
    assert not (ROOT/"tests/current/M15_R40_PLOT_01.asc").exists(), "R40 passed test must be removed from current"
    assert sorted(p.name for p in (ROOT/"tests/current").glob("*.asc")) == [], "No active ASC must remain after R46 Gate B PASS"
    plot_data=(ROOT/"tests/passed/M15_R40_PLOT_01.asc").read_bytes()
    plot_blob=b"blob "+str(len(plot_data)).encode("ascii")+bytes([0])+plot_data
    assert hashlib.sha1(plot_blob).hexdigest()=="6ab9cf4a91cca9f8097ffba40a32e2b85b049c38", "R40 passed ASC bytes modified"
    assert hashlib.sha256(binaries["dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib"]).hexdigest()=="0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc", "R41 archive changed"

    built41,meta41=build_r41()
    assert built41==build_r41()[0]==binaries["dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib"], "R41 frozen archive not reproducible"
    assert meta41["sha256"]=="0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc" and meta41["size"]==24816
    tok41,seg41,_=split(built41)
    assert len(seg41)==52 and len(seg40)==51, "R41 AP20 segment count"
    assert seg41[:50]==seg40[:50], "R41 changed frozen R40 entries"
    assert seg41[50]==seg40[50]+b"GetP", "R41 changed R40 Plot beyond final GetP"
    assert seg41[51], "R41 missing Draw entry"
    assert tok41.startswith(tok40[:-6]) and tok41!=tok40, "R41 token addition invalid"
    audit41=inspect(parse(built41))
    assert not audit41["issues"], audit41["issues"]
    named41=[x for x in audit41["tokens"] if x["name"].startswith("aga ")]
    assert len(named41)==46 and sum(x["name"]=="aga draw" for x in named41)==1
    for name,index,sig in API_R41:
        found=[x for x in named41 if x["name"]==name]
        assert len(found)==1 and (found[0]["instruction"],found[0]["function"],found[0]["signature"])==(1,index,sig)
    assert any(x["index"]==ENTRY_DRAW and x["parameters"]==5 and x["getp"] for x in audit41["parameter_checks"])
    assert (ROOT/"tests/passed/M15_R41_DRAW_01.asc").is_file(), "R41 WinUAE PASS test must be archived"
    assert not (ROOT/"tests/current/M15_R41_DRAW_01.asc").exists(), "R41 passed ASC must be removed from current"
    draw_data=(ROOT/"tests/passed/M15_R41_DRAW_01.asc").read_bytes()
    draw_blob=b"blob "+str(len(draw_data)).encode("ascii")+bytes([0])+draw_data
    assert hashlib.sha1(draw_blob).hexdigest()=="aa7de64b37a2842db21bc7452c2fab4570413e9f", "R41 passed ASC bytes modified"
    assert binaries["dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib"]==built41, "R41 historical archive changed"

    built42,meta42=build_r42()
    assert built42==build_r42()[0]==binaries["dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib"], "R42 archive not reproducible"
    assert meta42["sha256"]=="6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc" and meta42["size"]==25896
    tok42,seg42,_=split(built42)
    assert len(seg42)==53 and len(seg41)==52, "R42 AP20 segment count"
    assert seg42[:51]==seg41[:51], "R42 changed frozen R41 entries"
    assert seg42[51]==seg41[51]+b"GetP", "R42 changed R41 Draw beyond final GetP"
    assert seg42[52], "R42 missing Box entry"
    assert tok42.startswith(tok41[:-6]) and tok42!=tok41, "R42 token addition invalid"
    audit42=inspect(parse(built42))
    assert not audit42["issues"], audit42["issues"]
    named42=[x for x in audit42["tokens"] if x["name"].startswith("aga ")]
    assert len(named42)==47 and sum(x["name"]=="aga box" for x in named42)==1
    for name,index,sig in API_R42:
        found=[x for x in named42 if x["name"]==name]
        assert len(found)==1 and (found[0]["instruction"],found[0]["function"],found[0]["signature"])==(1,index,sig)
    assert any(x["index"]==ENTRY_BOX and x["parameters"]==5 and x["getp"] for x in audit42["parameter_checks"])
    assert (ROOT/"tests/passed/M15_R42_BOX_01.asc").is_file(), "R42 WinUAE passed test must be archived"
    assert not (ROOT/"tests/current/M15_R42_BOX_01.asc").exists(), "R42 test must be removed from current"
    box_data=(ROOT/"tests/passed/M15_R42_BOX_01.asc").read_bytes()
    box_blob=b"blob "+str(len(box_data)).encode("ascii")+bytes([0])+box_data
    assert hashlib.sha1(box_blob).hexdigest()=="dbf5cefb215cc0ae1359d648ea34c855a92b2012", "R42 passed ASC modified"
    assert binaries["dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib"]==built42, "R42 historical archive changed"
    built43,meta43=build_r43()
    assert built43==build_r43()[0]==binaries["dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib"], "R43 frozen archive changed"
    assert meta43["sha256"]=="9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf" and meta43["size"]==27092, "R43 candidate hash/size mismatch"
    tok43,seg43,_=split(built43)
    assert len(seg43)==54 and len(seg42)==53, "R43 AP20 segment count"
    assert seg43[:52]==seg42[:52], "R43 altered frozen R42 entries"
    assert seg43[52]==seg42[52]+b"GetP", "R43 changed R42 Box beyond GetP"
    assert seg43[53], "R43 Circle entry missing"
    assert tok43.startswith(tok42[:-6]) and tok43!=tok42, "R43 token addition invalid"
    audit43=inspect(parse(built43))
    assert not audit43["issues"], audit43["issues"]
    named43=[x for x in audit43["tokens"] if x["name"].startswith("aga ")]
    assert len(named43)==48 and sum(x["name"]=="aga circle" for x in named43)==1
    for name,index,sig in API_R43:
        found=[x for x in named43 if x["name"]==name]
        assert len(found)==1 and (found[0]["instruction"],found[0]["function"],found[0]["signature"])==(1,index,sig)
    assert any(x["index"]==ENTRY_CIRCLE and x["parameters"]==4 and x["getp"] for x in audit43["parameter_checks"])
    test_r43=ROOT/"tests/passed/M15_R43_CIRCLE_01.asc"
    assert test_r43.is_file(), "R43 Gate B PASS ASC must be archived"
    assert not (ROOT/"tests/current/M15_R43_CIRCLE_01.asc").exists(), "R43 test must not remain active after PASS"
    test_data=test_r43.read_bytes()
    test_blob=b"blob "+str(len(test_data)).encode("ascii")+bytes([0])+test_data
    assert len(test_data)==3466 and hashlib.sha1(test_blob).hexdigest()=="088158365a64accf0417fdda3fbba74e2e58ebf7", "R43 passed ASC bytes changed"
    assert binaries["dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib"]==built43, "R43 frozen archive changed"
    built44,meta44=build_r44()
    assert candidate==built44==build_r44()[0]==binaries["dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"], "R44 historical reproducibility mismatch"
    assert meta44["sha256"]=="0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc" and meta44["size"]==27460, "R44 candidate SHA/size mismatch"
    tok44,seg44,_=split(candidate)
    assert len(seg44)==55 and len(seg43)==54, "R44 segment count"
    assert tok44.startswith(tok43[:-6]) and tok44!=tok43, "R44 token addition"
    assert seg44[53]==seg43[53]+b"GetP", "R44 changed Circle beyond mandatory GetP"
    assert seg44[40]==seg43[40], "Palette Save private CloseWindow must be frozen"
    for i in range(53):
        if i not in OWNED_CLOSES:
            assert seg44[i]==seg43[i], ("R44 mutated unrelated entry",i)
        else:
            at=OWNED_CLOSES[i]
            assert seg43[i][at:at+4]==bytes.fromhex("4eaeffb8")
            assert seg44[i][:at]==seg43[i][:at] and seg44[i][at+4:]==seg43[i][at+4:]
            assert seg44[i][at:at+2]==bytes.fromhex("6100")
    audit44=inspect(parse(candidate))
    assert not audit44["issues"], audit44["issues"]
    names44=[x for x in audit44["tokens"] if x["name"].startswith("aga ")]
    assert len(names44)==49 and sum(x["name"]=="aga mouse cursor" for x in names44)==1
    for name,index,sig in API_R44:
        found=[x for x in names44 if x["name"]==name]
        assert len(found)==1 and (found[0]["instruction"],found[0]["function"],found[0]["signature"])==(1,index,sig)
    assert any(x["index"]==ENTRY_CURSOR and x["parameters"]==1 and x["getp"] for x in audit44["parameter_checks"])
    r44_test=ROOT/"tests/passed/M15BIS_R44_MOUSE_CURSOR_01.asc"
    assert r44_test.is_file(), "R44 WinUAE Gate B PASS original test not archived"
    assert not (ROOT/"tests/current/M15BIS_R44_MOUSE_CURSOR_01.asc").exists(), "R44 active test must be removed after Gate B"
    r44_bytes=r44_test.read_bytes()
    r44_blob=b"blob "+str(len(r44_bytes)).encode("ascii")+bytes([0])+r44_bytes
    assert len(r44_bytes)==3053 and hashlib.sha1(r44_blob).hexdigest()=="099f7125260c340dfbb4819f5770d1dbafd6789d", "R44 passed ASC modified"
    demo=ROOT/"examples/m15_2d_cursor.asc"
    assert demo.is_file(), "M15/M15bis combined demonstration missing"
    demo_bytes=demo.read_bytes()
    demo_blob=b"blob "+str(len(demo_bytes)).encode("ascii")+bytes([0])+demo_bytes
    assert len(demo_bytes)==6495 and hashlib.sha1(demo_blob).hexdigest()=="b9db059c7c3554d8f3bb59fca61ff2d54270a23b", "User-tested combined example modified"
    assert binaries["dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"]==candidate==built44, "R44 historical archive mismatch"
    print("PASS: R44 historical 49 AP20 commands / 55 segments, archived R44 and original ASC;")
    print("      R43 frozen, R44 native Gate A and user WinUAE Gate B PASS; combined demo user-confirmed")
    # R45 is a Gate-A-only candidate, NEVER the promoted LAST_GOOD before
    # explicit WinUAE confirmation; its new segment may not mutate R44.
    built45,meta45=build_r45()
    assert candidate_r45 == built45 == build_r45()[0] == binaries["dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib"], "R45 candidate/archive reproducibility mismatch"
    assert meta45["sha256"]=="0d780b4648214c36e8f291d9575390462d174cd8ba22cac2188324b75bd220d7" and meta45["size"]==29280, "R45 candidate size/SHA mismatch"
    tok45,seg45,_=split(candidate_r45)
    assert len(seg45)==56 and len(seg44)==55, "R45 segment count"
    assert seg45[:54]==seg44[:54], "R45 changed frozen R44 segments"
    assert seg45[54]==seg44[54]+b"GetP", "R45 changed R44 beyond mandatory GetP"
    assert len(seg45[55])>512, "R45 native draw function absent"
    assert tok45.startswith(tok44[:-6]) and tok45!=tok44, "R45 token table changed improperly"
    aud45=inspect(parse(candidate_r45))
    assert not aud45["issues"], aud45["issues"]
    named45=[v for v in aud45["tokens"] if v["name"].startswith("aga ")]
    assert len(named45)==50 and sum(v["name"]=="aga image draw" for v in named45)==1, "R45 named commands"
    for name,index,sig in API_R45:
        matches=[v for v in named45 if v["name"]==name]
        assert len(matches)==1 and (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,index,sig)
    assert any(v["index"]==ENTRY_IMAGE and v["parameters"]==5 and v["getp"] for v in aud45["parameter_checks"]), "R45 GetP absent"
    # Historical R45 failed as seen in WinUAE: bank metadata FLAGS=0,
    # old CPU validation required only 1 or 3. Preserve its exact ASC.
    test_r45=ROOT/"tests/failed/M16_R45_IMAGE_DRAW_01.asc"
    assert test_r45.is_file() and not (ROOT/"tests/passed/M16_R45_IMAGE_DRAW_01.asc").exists(), "failed R45 ASC must be archived separately"
    test_data=test_r45.read_bytes()
    test_blob=b"blob "+str(len(test_data)).encode("ascii")+bytes([0])+test_data
    assert len(test_data)==4241 and hashlib.sha1(test_blob).hexdigest()=="993b9b6b4eff2eaa3183437602868bbe2946d26a", "R45 failed ASC mutated"
    assert binaries["dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"]==candidate==built44 and candidate_r45!=candidate, "R44 historical archive must remain untouched"
    print("PASS: failed R45 50 AP20 commands / 56 segments, 29280 B frozen, WinUAE Gate B FAIL (flags=0);")

    # R46 repairs ONLY entry 55 in the failed R45 baseline; all AP20
    # signatures and 55 prior segments are exact byte matches.
    built46,meta46=build_r46()
    assert candidate_r46==built46==build_r46()[0]==binaries["dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib"], "R46 candidate/archive reproducibility mismatch"
    assert meta46["sha256"]=="5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580" and meta46["size"]==29288, "R46 candidate size/SHA mismatch"
    tok46,seg46,_=split(candidate_r46)
    assert tok46==tok45 and len(seg46)==len(seg45)==56
    assert seg46[:55]==seg45[:55] and seg46[55]!=seg45[55], "R46 changed historical code beyond drawing routine"
    aud46=inspect(parse(candidate_r46))
    assert not aud46["issues"], aud46["issues"]
    named46=[v for v in aud46["tokens"] if v["name"].startswith("aga ")]
    assert len(named46)==50 and sum(v["name"]=="aga image draw" for v in named46)==1, "R46 named commands changed"
    assert any(v["index"]==ENTRY_IMAGE and v["parameters"]==5 and v["getp"] for v in aud46["parameter_checks"])
    test_r46=ROOT/"tests/passed/M16_R46_IMAGE_DRAW_01.asc"
    assert test_r46.is_file() and not (ROOT/"tests/current/M16_R46_IMAGE_DRAW_01.asc").exists()
    new_data=test_r46.read_bytes()
    new_blob=b"blob "+str(len(new_data)).encode("ascii")+bytes([0])+new_data
    assert len(new_data)==4240 and hashlib.sha1(new_blob).hexdigest()=="83eff57323b1cacd0ea58a131ef1ebcec079eceb", "R46 Gate B PASS ASC original mutated"
    # Original R46 is frozen: raw code is source input only, NOT installable.
    # The reproducible C1 bridge is now the official R46 0.12.1-C1.
    built_current, meta_current = build_current()
    assert promoted == built_current == binaries["dist/AMOSPro_AGA_LAST_GOOD.Lib"], "C1 is not official LAST_GOOD"
    assert promoted != candidate_r46 and promoted not in (candidate_r45,candidate)
    assert len(promoted)==29964 and meta_current["sha256"]=="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
    assert is_compiler_wrapped(promoted) and not is_compiler_wrapped(candidate_r46)
    tok_c1, seg_c1, _ = unpack_ap20(promoted)
    assert tok_c1==tok46 and len(seg_c1)==57 and len(seg_c1[-1])==27888
    assert unwrap_native_parts(promoted)==(tok46,seg46)
    assert native_from_promoted(promoted,split(candidate_r46)[2])==candidate_r46
    assert wrap_native_ap20(candidate_r46,split(promoted)[2])==promoted
    audit_c1=inspect(parse(promoted))
    assert not audit_c1["issues"] and audit_c1["tokens"]==aud46["tokens"]
    verified_asc=(ROOT/"tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc").read_bytes()
    assert verified_asc==(ROOT/"examples/compiler_r46_all_in_one/COMPILER_R46_ALL_IN_ONE.asc").read_bytes()
    git_blob=b"blob "+str(len(verified_asc)).encode("ascii")+bytes([0])+verified_asc
    assert len(verified_asc)==5404 and hashlib.sha1(git_blob).hexdigest()=="eded9040e382e9177b3c929bfa19e3c61ee9dd69"
    print("PASS: official Compiler-safe R46 C1, 57 entries, 29964 bytes, 50 tokens, WinUAE integrated Gate C PASS;")
    print("      native R46/R44/R45 archives frozen, C1 bridge deterministic and future source reversible.")
    print("      R46 raw source: 56 segments / 29288 B, 258 native CPU Gate A scenarios and interpreted Gate B PASS.")


if __name__ == "__main__":
    main()
