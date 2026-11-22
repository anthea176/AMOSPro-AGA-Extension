#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-backed UNIT142 MC68020: exact P2d staging and isolated edit gate.

The audit export supplies only candidate mnemonic spelling. The authoritative
bytes are the SHA-pinned, emitter-built P2d AP20 unit. Neither this tool nor
the direct assembler writes into dist/ or changes an AMOS campaign.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory

from active_library import P2D_SHA
from compiler_relocation import unpack_ap20

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "src/asm_migration/m19_p2d/M19_P2D_UNIT142_MC68020.s"
NATIVE_DIR = ROOT / "src/native/m19_p2d"
WRAPPER = NATIVE_DIR / "M19_P2D_UNIT142_EDITABLE.s"
STAGED_NAME = "M19_P2D_UNIT142_MC68020.s"
MASTER_NAME = "M19_P2D_AP20_SOURCE.s"
GROUP_SIZE = 0xF514
GROUP_SHA = "8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7"
ANNOT = re.compile(r"\s+;\s+\+\$([A-F0-9]{5}): ([A-F0-9]+)\s*$")
LABEL = re.compile(r"[A-Za-z_][A-Za-z_0-9]*:\s*$")

# (file, start label, end label, start, end, instructions, inner labels,
#  mutable symbol, baseline, edit, mnemonic to replace, replacement,
#  differing byte offset within UNIT142, old byte, new byte)
SPANS = (
    (
        "M19_UNIT142_DISPATCH_V2_MC68020.s",
        "UNIT_UNIT142:\n", "ENTRY_UNIT142_00022:\n",
        0x00000, 0x00022, 11, 0,
        "UNIT142_DISPATCH_STACK", 4, 3,
        "    subq.l #4,a7", "    subq.l #UNIT142_DISPATCH_STACK,a7",
        0x00000, 0x59, 0x57,
    ),
    (
        "M19_UNIT142_INIT_ENTRY_MC68020.s",
        "ENTRY_UNIT142_00022:\n", "L_UNIT142_0005A:\n",
        0x00022, 0x0005A, 17, 2,
        "UNIT142_INIT_COUNT", 9, 10,
        "    moveq #9,d0", "    moveq #UNIT142_INIT_COUNT,d0",
        0x00045, 9, 10,
    ),
    (
        "M19_UNIT142_GRAPHICS_GUARD_MC68020.s",
        "ENTRY_UNIT142_002C2:\n", "L_UNIT142_0030C:\n",
        0x002C2, 0x0030C, 28, 2,
        "UNIT142_GRAPHICS_INITIAL_D3", 0, 1,
        "    moveq #0,d3", "    moveq #UNIT142_GRAPHICS_INITIAL_D3,d3",
        0x002CD, 0, 1,
    ),
    (
        "M19_UNIT142_GRAPHICS_SCREEN_MC68020.s",
        "ENTRY_UNIT142_00322:\n", "L_UNIT142_00448:\n",
        0x00322, 0x00448, 86, 5,
        "UNIT142_SCREEN_INITIAL_D3", 0, 1,
        "    moveq #0,d3", "    moveq #UNIT142_SCREEN_INITIAL_D3,d3",
        0x00327, 0, 1,
    ),
    (
        "M19_UNIT142_IFF_LOAD_BODY_MC68020.s",
        "ENTRY_UNIT142_00D3C:\n",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$0153A: 203C00000000\n",
        0x00D3C, 0x0153A, 513, 50,
        "UNIT142_IFF_LOAD_ZERO", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_IFF_LOAD_ZERO,d2",
        0x00ECB, 0, 1,
    ),
    (
        "M19_UNIT142_IFF_PALETTE_BODY_MC68020.s",
        "ENTRY_UNIT142_015D8:\n",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$01BC4: 203C00000000\n",
        0x015D8, 0x01BC4, 338, 35,
        "UNIT142_IFF_PALETTE_CAP", 7, 8,
        "    cmpi.l #$00000007,8(a5)", "    cmpi.l #UNIT142_IFF_PALETTE_CAP,8(a5)",
        0x016F9, 7, 8,
    ),
    (
        "M19_UNIT142_IFF_AP20_PRECALL_MC68020.s",
        "ENTRY_UNIT142_01BDE:\n",
        "    dc.b $FE,$11,$F7,$00,$00,$8C  ; +$01E0C: FE11F700008C\n",
        0x01BDE, 0x01E0C, 164, 21,
        "UNIT142_IFF_FAILURE", -1, 0,
        "    moveq #-1,d3", "    moveq #UNIT142_IFF_FAILURE,d3",
        0x01C1D, 255, 0,
    ),
    (
        "M19_UNIT142_COLOR_RANGE_MC68020.s",
        "ENTRY_UNIT142_0299A:\n",
        "    dc.b $47,$65,$74,$50  ; +$02BB6: 47657450\n",
        0x0299A, 0x02BB6, 153, 7,
        "UNIT142_COLOR_RANGE_CAP", 384, 385,
        "    cmpi.l #$00000180,d4", "    cmpi.l #UNIT142_COLOR_RANGE_CAP,d4",
        0x029BD, 128, 129,
    ),
    (
        "M19_UNIT142_ENTRY_02E64_MC68020.s",
        "ENTRY_UNIT142_02E64:\n",
        "    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$030E8: 000000000000000000000000\n",
        0x02E64, 0x030E8, 184, 20,
        "UNIT142_ENTRY_02E64_COUNT", 63, 64,
        "    moveq #63,d7", "    moveq #UNIT142_ENTRY_02E64_COUNT,d7",
        0x02EF7, 63, 64,
    ),
    (
        "M19_UNIT142_ENTRY_03270_MC68020.s",
        "ENTRY_UNIT142_03270:\n",
        "    dc.b $47,$65,$74,$50  ; +$034F0: 47657450\n",
        0x03270, 0x034F0, 193, 8,
        "UNIT142_ENTRY_03270_ZERO", 0, 1,
        "    moveq #0,d3", "    moveq #UNIT142_ENTRY_03270_ZERO,d3",
        0x0327D, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_034F4_MC68020.s",
        "ENTRY_UNIT142_034F4:\n",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$03986: 203C00000000\n",
        0x034F4, 0x03986, 284, 20,
        "UNIT142_ENTRY_034F4_ZERO", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_ENTRY_034F4_ZERO,d2",
        0x03657, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_03C46_MC68020.s",
        "ENTRY_UNIT142_03C46:\n",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$040FC: 203C00000000\n",
        0x03C46, 0x040FC, 280, 23,
        "UNIT142_ENTRY_03C46_ZERO", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_ENTRY_03C46_ZERO,d2",
        0x03D9F, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_0530E_MC68020.s",
        "ENTRY_UNIT142_0530E:\n",
        "    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$47,$65,$74,$50  ; +$056FA: 000000000000000047657450\n",
        0x0530E, 0x056FA, 279, 15,
        "UNIT142_ENTRY_0530E_LIMIT", 112, 113,
        "    cmpi.l #$00000070,d7", "    cmpi.l #UNIT142_ENTRY_0530E_LIMIT,d7",
        0x0533F, 112, 113,
    ),
    (
        "M19_UNIT142_ENTRY_0609E_MC68020.s",
        "ENTRY_UNIT142_0609E:\n",
        "    dc.b $47,$65,$74,$50  ; +$06528: 47657450\n",
        0x0609E, 0x06528, 327, 19,
        "UNIT142_ENTRY_0609E_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_0609E_ZERO,d3",
        0x060AF, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_06678_MC68020.s",
        "ENTRY_UNIT142_06678:\n",
        "    dc.b $47,$65,$74,$50  ; +$07006: 47657450\n",
        0x06678, 0x07006, 663, 55,
        "UNIT142_ENTRY_06678_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_06678_ZERO,d3",
        0x066A1, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_0700A_MC68020.s",
        "ENTRY_UNIT142_0700A:\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$07254: FE11F700031D\n",
        0x0700A, 0x07254, 154, 6,
        "UNIT142_ENTRY_0700A_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_0700A_ZERO,d3",
        0x07051, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_04256_MC68020.s",
        "ENTRY_UNIT142_04256:\n",
        "    dc.b $47,$65,$74,$50  ; +$044E6: 47657450\n",
        0x04256, 0x044E6, 182, 4,
        "UNIT142_ENTRY_04256_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_04256_ZERO,d3",
        0x04263, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_044EA_MC68020.s",
        "ENTRY_UNIT142_044EA:\n",
        "    dc.b $47,$65,$74,$50  ; +$0479A: 47657450\n",
        0x044EA, 0x0479A, 195, 2,
        "UNIT142_ENTRY_044EA_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_044EA_ZERO,d3",
        0x044F7, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_0479E_MC68020.s",
        "ENTRY_UNIT142_0479E:\n",
        "    dc.b $47,$65,$74,$50  ; +$04B3C: 47657450\n",
        0x0479E, 0x04B3C, 271, 8,
        "UNIT142_ENTRY_0479E_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_0479E_ZERO,d3",
        0x047AD, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_04B40_MC68020.s",
        "ENTRY_UNIT142_04B40:\n",
        "    dc.b $47,$65,$74,$50  ; +$04D48: 47657450\n",
        0x04B40, 0x04D48, 158, 8,
        "UNIT142_ENTRY_04B40_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_04B40_ZERO,d3",
        0x04B4B, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_04D4C_MC68020.s",
        "ENTRY_UNIT142_04D4C:\n",
        "    dc.b $47,$65,$74,$50  ; +$04F54: 47657450\n",
        0x04D4C, 0x04F54, 158, 8,
        "UNIT142_ENTRY_04D4C_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_04D4C_ZERO,d3",
        0x04D57, 0, 1,
    ),
    (
        "M19_UNIT142_ENTRY_04F58_MC68020.s",
        "ENTRY_UNIT142_04F58:\n",
        "    dc.b $47,$65,$74,$50  ; +$0514C: 47657450\n",
        0x04F58, 0x0514C, 147, 6,
        "UNIT142_ENTRY_04F58_ZERO", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_ENTRY_04F58_ZERO,d3",
        0x04F67, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_078A4_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0789E: FE11F700031D\n",
        "    dc.b $4E,$71,$4E,$71,$4E,$71,$4E,$71,$4E,$71,$4E,$71  ; +$07B2A: 4E714E714E714E714E714E71\n",
        0x078A4, 0x07B2A, 198, 13,
        "UNIT142_BLOCK_078A4_MIN", 16, 17,
        "    cmpi.l #$00000010,d3", "    cmpi.l #UNIT142_BLOCK_078A4_MIN,d3",
        0x078B9, 16, 17,
    ),
    (
        "M19_UNIT142_BLOCK_07BC8_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$07BC2: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$08564: 47657450\n",
        0x07BC8, 0x08564, 666, 53,
        "UNIT142_BLOCK_07BC8_MIN", 16, 17,
        "    cmpi.l #$00000010,d4", "    cmpi.l #UNIT142_BLOCK_07BC8_MIN,d4",
        0x07BDD, 16, 17,
    ),
    (
        "M19_UNIT142_BLOCK_08618_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$08612: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$08CD6: 47657450\n",
        0x08618, 0x08CD6, 474, 34,
        "UNIT142_BLOCK_08618_MIN", 24, 25,
        "    cmpi.l #$00000018,d5", "    cmpi.l #UNIT142_BLOCK_08618_MIN,d5",
        0x0861F, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_08D78_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$08D72: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$09424: 47657450\n",
        0x08D78, 0x09424, 431, 24,
        "UNIT142_BLOCK_08D78_MIN", 24, 25,
        "    cmpi.l #$00000018,d5", "    cmpi.l #UNIT142_BLOCK_08D78_MIN,d5",
        0x08D7F, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_09C80_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$09C7A: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$09F66: 47657450\n",
        0x09C80, 0x09F66, 191, 7,
        "UNIT142_BLOCK_09C80_MIN", 24, 25,
        "    cmpi.l #$00000018,d5", "    cmpi.l #UNIT142_BLOCK_09C80_MIN,d5",
        0x09C87, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_0A006_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0A000: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$0A472: 47657450\n",
        0x0A006, 0x0A472, 295, 8,
        "UNIT142_BLOCK_0A006_MIN", 24, 25,
        "    cmpi.l #$00000018,d5", "    cmpi.l #UNIT142_BLOCK_0A006_MIN,d5",
        0x0A00D, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_0A476_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0A472: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0A6DC: FE11F700031D\n",
        0x0A476, 0x0A6DC, 163, 6,
        "UNIT142_BLOCK_0A476_VALUE", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_0A476_VALUE,d3",
        0x0A4AD, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0A71A_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$0A714: FE11F7000330\n",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$0AB90: FE11F7000333\n",
        0x0A71A, 0x0AB90, 284, 7,
        "UNIT142_BLOCK_0A71A_VALUE", 24, 25,
        "    cmpi.l #$00000018,d0", "    cmpi.l #UNIT142_BLOCK_0A71A_VALUE,d0",
        0x0A735, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_0B0A6_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0B0A0: FE11F700031D\n",
        "    dc.b $41,$47,$41,$43,$42,$4C,$4B,$20  ; +$0B58A: 41474143424C4B20\n",
        0x0B0A6, 0x0B58A, 311, 9,
        "UNIT142_BLOCK_0B0A6_VALUE", 24, 25,
        "    cmpi.l #$00000018,d5", "    cmpi.l #UNIT142_BLOCK_0B0A6_VALUE,d5",
        0x0B1FB, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_0BA5E_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0BA58: FE11F700031D\n",
        "    dc.b $41,$47,$41,$43,$42,$4C,$4B,$20  ; +$0BF52: 41474143424C4B20\n",
        0x0BA5E, 0x0BF52, 315, 9,
        "UNIT142_BLOCK_0BA5E_VALUE", 24, 25,
        "    cmpi.l #$00000018,d5", "    cmpi.l #UNIT142_BLOCK_0BA5E_VALUE,d5",
        0x0BBC3, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_0C41C_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0C416: FE11F700031D\n",
        "    dc.b $60,$00,$00,$08  ; +$0C8BA: 60000008\n",
        0x0C41C, 0x0C8BA, 319, 7,
        "UNIT142_BLOCK_0C41C_VALUE", 8, 9,
        "    cmpi.l #$00000008,d0", "    cmpi.l #UNIT142_BLOCK_0C41C_VALUE,d0",
        0x0C5D7, 8, 9,
    ),
    (
        "M19_UNIT142_BLOCK_0C946_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0C940: FE11F700031D\n",
        "    dc.b $60,$00,$00,$08  ; +$0CED4: 60000008\n",
        0x0C946, 0x0CED4, 394, 13,
        "UNIT142_BLOCK_0C946_VALUE", 8, 9,
        "    cmpi.l #$00000008,d0", "    cmpi.l #UNIT142_BLOCK_0C946_VALUE,d0",
        0x0CB09, 8, 9,
    ),
    (
        "M19_UNIT142_BLOCK_0CF3E_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0CF38: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$0D332: 47657450\n",
        0x0CF3E, 0x0D332, 252, 17,
        "UNIT142_BLOCK_0CF3E_VALUE", 24, 25,
        "    cmpi.l #$00000018,d0", "    cmpi.l #UNIT142_BLOCK_0CF3E_VALUE,d0",
        0x0CF51, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_0D336_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0D332: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0D68E: FE11F700031D\n",
        0x0D336, 0x0D68E, 220, 10,
        "UNIT142_BLOCK_0D336_VALUE", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_0D336_VALUE,d3",
        0x0D3A3, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0D99A_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$0D994: FE11F7000320\n",
        "    dc.b $41,$47,$41,$50,$49,$43,$20,$20,$48,$E7,$EF,$EE  ; +$0DCFC: 414741504943202048E7EFEE\n",
        0x0D99A, 0x0DCFC, 235, 25,
        "UNIT142_BLOCK_0D99A_VALUE", 8, 9,
        "    cmpi.l #$00000008,d1", "    cmpi.l #UNIT142_BLOCK_0D99A_VALUE,d1",
        0x0DA99, 8, 9,
    ),
    (
        "M19_UNIT142_BLOCK_0219C_MC68020.s",
        "ENTRY_UNIT142_0219C:\n",
        "    dc.b $47,$65,$74,$50  ; +$0235C: 47657450\n",
        0x0219C, 0x0235C, 136, 6,
        "UNIT142_BLOCK_0219C_RESULT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0219C_RESULT,d2",
        0x02359, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0282C_MC68020.s",
        "ENTRY_UNIT142_0282C:\n",
        "    dc.b $47,$65,$74,$50  ; +$02996: 47657450\n",
        0x0282C, 0x02996, 107, 6,
        "UNIT142_BLOCK_0282C_RESULT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0282C_RESULT,d2",
        0x02993, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_05150_MC68020.s",
        "ENTRY_UNIT142_05150:\n",
        "    dc.b $2F,$0E,$2F,$08,$2F,$0A,$61,$00,$FF,$DC,$4A,$80  ; +$052CA: 2F0E2F082F0A6100FFDC4A80\n",
        0x05150, 0x052CA, 107, 9,
        "UNIT142_BLOCK_05150_RESULT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_05150_RESULT,d2",
        0x052AB, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_05706_MC68020.s",
        "ENTRY_UNIT142_05706:\n",
        "    dc.b $47,$65,$74,$50  ; +$058C2: 47657450\n",
        0x05706, 0x058C2, 129, 7,
        "UNIT142_BLOCK_05706_RESULT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_05706_RESULT,d2",
        0x058BF, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_058C6_MC68020.s",
        "ENTRY_UNIT142_058C6:\n",
        "    dc.b $47,$65,$74,$50  ; +$05C76: 47657450\n",
        0x058C6, 0x05C76, 258, 22,
        "UNIT142_BLOCK_058C6_RESULT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_058C6_RESULT,d2",
        0x05C73, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_05C7A_MC68020.s",
        "ENTRY_UNIT142_05C7A:\n",
        "    dc.b $47,$65,$74,$50  ; +$0609A: 47657450\n",
        0x05C7A, 0x0609A, 290, 24,
        "UNIT142_BLOCK_05C7A_RESULT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_05C7A_RESULT,d2",
        0x06097, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_07482_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$0747C: FE11F7000320\n",
        "L_UNIT142_077D0:\n",
        0x07482, 0x077D0, 229, 23,
        "UNIT142_BLOCK_07482_RESULT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_07482_RESULT,d2",
        0x074AF, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0D7C8_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$0D7C2: FE11F7000330\n",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$0D980: FE11F7000333\n",
        0x0D7C8, 0x0D980, 110, 6,
        "UNIT142_BLOCK_0D7C8_EDIT", 1095188816, 1095188817,
        "    move.l #$41474150,(a0)", "    move.l #UNIT142_BLOCK_0D7C8_EDIT,(a0)",
        0x0D7E9, 80, 81,
    ),
    (
        "M19_UNIT142_BLOCK_01F32_MC68020.s",
        "    dc.b $4E,$71  ; +$01F30: 4E71\n",
        "    dc.b $FE,$11,$F7,$00,$00,$8C  ; +$020E0: FE11F700008C\n",
        0x01F32, 0x020E0, 124, 21,
        "UNIT142_BLOCK_01F32_EDIT", 0, 1,
        "    moveq #0,d0", "    moveq #UNIT142_BLOCK_01F32_EDIT,d0",
        0x0206D, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_095EC_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$095E6: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0978A: FE11F700031D\n",
        0x095EC, 0x0978A, 102, 1,
        "UNIT142_BLOCK_095EC_EDIT", 24, 25,
        "    cmpi.l #$00000018,d5", "    cmpi.l #UNIT142_BLOCK_095EC_EDIT,d5",
        0x095F3, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_09790_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0978A: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$0992C: 47657450\n",
        0x09790, 0x0992C, 111, 8,
        "UNIT142_BLOCK_09790_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_09790_EDIT,d2",
        0x09929, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0AF3A_MC68020.s",
        "    dc.b $4C,$DF,$77,$F7,$74,$00,$4E,$75,$47,$65,$74,$50  ; +$0AF2E: 4CDF77F774004E7547657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0B0A0: FE11F700031D\n",
        0x0AF3A, 0x0B0A0, 96, 3,
        "UNIT142_BLOCK_0AF3A_EDIT", 0, 1,
        "    move.l #$00000000,72(a2)", "    move.l #UNIT142_BLOCK_0AF3A_EDIT,72(a2)",
        0x0AF4B, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_09B16_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$09B10: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$09C7A: FE11F700031D\n",
        0x09B16, 0x09C7A, 87, 1,
        "UNIT142_BLOCK_09B16_EDIT", 24, 25,
        "    cmpi.l #$00000018,d5", "    cmpi.l #UNIT142_BLOCK_09B16_EDIT,d5",
        0x09B1D, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_0B8FE_MC68020.s",
        "    dc.b $4C,$DF,$77,$F7,$74,$00,$4E,$75,$47,$65,$74,$50  ; +$0B8F2: 4CDF77F774004E7547657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0BA58: FE11F700031D\n",
        0x0B8FE, 0x0BA58, 92, 3,
        "UNIT142_BLOCK_0B8FE_EDIT", 0, 1,
        "    move.l #$00000000,72(a2)", "    move.l #UNIT142_BLOCK_0B8FE_EDIT,72(a2)",
        0x0B90F, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0652C_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$06528: 47657450\n",
        "    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$47,$65,$74,$50  ; +$0666C: 000000000000000047657450\n",
        0x0652C, 0x0666C, 93, 9,
        "UNIT142_BLOCK_0652C_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0652C_EDIT,d2",
        0x06607, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0411A_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$04116: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$04252: 47657450\n",
        0x0411A, 0x04252, 77, 4,
        "UNIT142_BLOCK_0411A_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0411A_EDIT,d2",
        0x0424F, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_03A24_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$03A20: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$03B4E: 47657450\n",
        0x03A24, 0x03B4E, 90, 2,
        "UNIT142_BLOCK_03A24_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_03A24_EDIT,d2",
        0x03B4B, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_00A80_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$00A7C: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$00B9E: 47657450\n",
        0x00A80, 0x00B9E, 88, 8,
        "UNIT142_BLOCK_00A80_EDIT", 0, 1,
        "    moveq #0,d3", "    moveq #UNIT142_BLOCK_00A80_EDIT,d3",
        0x00A85, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_01E12_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$00,$8C  ; +$01E0C: FE11F700008C\n",
        "    dc.b $4E,$71  ; +$01F30: 4E71\n",
        0x01E12, 0x01F30, 88, 11,
        "UNIT142_BLOCK_01E12_EDIT", 0, 1,
        "    moveq #0,d4", "    moveq #UNIT142_BLOCK_01E12_EDIT,d4",
        0x01E33, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0D694_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0D68E: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0D7A4: FE11F700031D\n",
        0x0D694, 0x0D7A4, 72, 4,
        "UNIT142_BLOCK_0D694_EDIT", 1, 2,
        "    andi.l #$00000001,d0", "    andi.l #UNIT142_BLOCK_0D694_EDIT,d0",
        0x0D6A9, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_02584_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$02580: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$0268C: 47657450\n",
        0x02584, 0x0268C, 77, 8,
        "UNIT142_BLOCK_02584_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_02584_EDIT,d2",
        0x02689, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_07360_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$0735A: FE11F7000330\n",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$07468: FE11F7000333\n",
        0x07360, 0x07468, 66, 2,
        "UNIT142_BLOCK_07360_EDIT", 1095188816, 1095188817,
        "    move.l #$41474150,(a0)", "    move.l #UNIT142_BLOCK_07360_EDIT,(a0)",
        0x07381, 80, 81,
    ),
    (
        "M19_UNIT142_BLOCK_00BA2_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$00B9E: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$00C9A: 47657450\n",
        0x00BA2, 0x00C9A, 75, 9,
        "UNIT142_BLOCK_00BA2_EDIT", 0, 1,
        "    moveq #0,d3", "    moveq #UNIT142_BLOCK_00BA2_EDIT,d3",
        0x00BA7, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_03B52_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$03B4E: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$03C42: 47657450\n",
        0x03B52, 0x03C42, 69, 2,
        "UNIT142_BLOCK_03B52_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_03B52_EDIT,d2",
        0x03C3F, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0273C_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$02738: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$02828: 47657450\n",
        0x0273C, 0x02828, 66, 8,
        "UNIT142_BLOCK_0273C_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0273C_EDIT,d2",
        0x02825, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_02C9A_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$02C96: 47657450\n",
        "    dc.b $69,$6E,$70,$75,$74,$2E,$64,$65,$76,$69,$63,$65  ; +$02D7E: 696E7075742E646576696365\n",
        0x02C9A, 0x02D7E, 72, 11,
        "UNIT142_BLOCK_02C9A_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_02C9A_EDIT,d2",
        0x02D7B, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0725A_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$07254: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0733C: FE11F700031D\n",
        0x0725A, 0x0733C, 61, 3,
        "UNIT142_BLOCK_0725A_EDIT", 1, 2,
        "    andi.l #$00000001,d0", "    andi.l #UNIT142_BLOCK_0725A_EDIT,d0",
        0x0726F, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_020E6_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$00,$8C  ; +$020E0: FE11F700008C\n",
        "    dc.b $47,$65,$74,$50  ; +$02198: 47657450\n",
        0x020E6, 0x02198, 54, 9,
        "UNIT142_BLOCK_020E6_EDIT", 0, 1,
        "    moveq #0,d4", "    moveq #UNIT142_BLOCK_020E6_EDIT,d4",
        0x02107, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_08568_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$08564: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$08612: FE11F700031D\n",
        0x08568, 0x08612, 43, 1,
        "UNIT142_BLOCK_08568_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_08568_EDIT,d3",
        0x08591, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_02690_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0268C: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$02738: 47657450\n",
        0x02690, 0x02738, 49, 5,
        "UNIT142_BLOCK_02690_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_02690_EDIT,d2",
        0x02735, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_099C6_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$099C0: FE11F7000330\n",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$09A66: FE11F7000333\n",
        0x099C6, 0x09A66, 44, 2,
        "UNIT142_BLOCK_099C6_EDIT", 24, 25,
        "    cmpi.l #$00000018,d0", "    cmpi.l #UNIT142_BLOCK_099C6_EDIT,d0",
        0x099D5, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_00C9E_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$00C9A: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$00D38: 47657450\n",
        0x00C9E, 0x00D38, 47, 4,
        "UNIT142_BLOCK_00C9E_EDIT", 128, 129,
        "    move.l #$00000080,d0", "    move.l #UNIT142_BLOCK_00C9E_EDIT,d0",
        0x00CED, 128, 129,
    ),
    (
        "M19_UNIT142_BLOCK_08CDA_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$08CD6: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$08D72: FE11F700031D\n",
        0x08CDA, 0x08D72, 38, 1,
        "UNIT142_BLOCK_08CDA_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_08CDA_EDIT,d3",
        0x08D03, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_09F6A_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$09F66: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0A000: FE11F700031D\n",
        0x09F6A, 0x0A000, 39, 1,
        "UNIT142_BLOCK_09F6A_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_09F6A_EDIT,d3",
        0x09F8D, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_00764_MC68020.s",
        "    dc.b $51,$C8,$FF,$FC,$4E,$75,$47,$65,$74,$50  ; +$0075A: 51C8FFFC4E7547657450\n",
        "    dc.b $47,$65,$74,$50,$48,$E7,$FF,$FE,$24,$6D,$01,$C8  ; +$007F6: 4765745048E7FFFE246D01C8\n",
        0x00764, 0x007F6, 48, 3,
        "UNIT142_BLOCK_00764_EDIT", 0, 1,
        "    moveq #0,d6", "    moveq #UNIT142_BLOCK_00764_EDIT,d6",
        0x00789, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_031E4_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$031E0: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$0326C: 47657450\n",
        0x031E4, 0x0326C, 45, 7,
        "UNIT142_BLOCK_031E4_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_031E4_EDIT,d2",
        0x03269, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_09564_MC68020.s",
        "    dc.b $46,$49,$43,$4F,$4E,$38,$20,$20,$47,$65,$74,$50  ; +$09558: 4649434F4E38202047657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$095E6: FE11F700031D\n",
        0x09564, 0x095E6, 34, 1,
        "UNIT142_BLOCK_09564_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_09564_EDIT,d3",
        0x09587, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_01540_MC68020.s",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$0153A: 203C00000000\n",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$015BA: 203C00000000\n",
        0x01540, 0x015BA, 31, 7,
        "UNIT142_BLOCK_01540_EDIT", 1, 2,
        "    move.l #$00000001,d0", "    move.l #UNIT142_BLOCK_01540_EDIT,d0",
        0x015B5, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_0398C_MC68020.s",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$03986: 203C00000000\n",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$03A06: 203C00000000\n",
        0x0398C, 0x03A06, 31, 7,
        "UNIT142_BLOCK_0398C_EDIT", 1, 2,
        "    move.l #$00000001,d0", "    move.l #UNIT142_BLOCK_0398C_EDIT,d0",
        0x03A01, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_09A9E_MC68020.s",
        "    dc.b $46,$49,$43,$48,$49,$50,$38,$20,$47,$65,$74,$50  ; +$09A92: 464943484950382047657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$09B10: FE11F700031D\n",
        0x09A9E, 0x09B10, 29, 1,
        "UNIT142_BLOCK_09A9E_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_09A9E_EDIT,d3",
        0x09ABB, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_094BE_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$094B8: FE11F7000330\n",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$0952C: FE11F7000333\n",
        0x094BE, 0x0952C, 29, 1,
        "UNIT142_BLOCK_094BE_EDIT", 24, 25,
        "    cmpi.l #$00000018,d0", "    cmpi.l #UNIT142_BLOCK_094BE_EDIT,d0",
        0x094CD, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_02BBA_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$02BB6: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$02C26: 47657450\n",
        0x02BBA, 0x02C26, 35, 3,
        "UNIT142_BLOCK_02BBA_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_02BBA_EDIT,d2",
        0x02C23, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_02C2A_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$02C26: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$02C96: 47657450\n",
        0x02C2A, 0x02C96, 35, 3,
        "UNIT142_BLOCK_02C2A_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_02C2A_EDIT,d2",
        0x02C93, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_07B56_MC68020.s",
        "    dc.b $4E,$71,$4E,$71,$47,$65,$74,$50  ; +$07B4E: 4E714E7147657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$07BC2: FE11F700031D\n",
        0x07B56, 0x07BC2, 31, 1,
        "UNIT142_BLOCK_07B56_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_07B56_EDIT,d3",
        0x07B91, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0C8D8_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0C8D4: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0C940: FE11F700031D\n",
        0x0C8D8, 0x0C940, 28, 1,
        "UNIT142_BLOCK_0C8D8_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_0C8D8_EDIT,d3",
        0x0C8F9, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_02D90_MC68020.s",
        "    dc.b $00,$00,$47,$65,$74,$50  ; +$02D8A: 000047657450\n",
        "    dc.b $47,$65,$74,$50  ; +$02DF6: 47657450\n",
        0x02D90, 0x02DF6, 29, 4,
        "UNIT142_BLOCK_02D90_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_02D90_EDIT,d2",
        0x02DF3, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_02DFA_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$02DF6: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$02E60: 47657450\n",
        0x02DFA, 0x02E60, 29, 4,
        "UNIT142_BLOCK_02DFA_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_02DFA_EDIT,d2",
        0x02E5D, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0317C_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$03178: 47657450\n",
        "    dc.b $47,$65,$74,$50  ; +$031E0: 47657450\n",
        0x0317C, 0x031E0, 33, 3,
        "UNIT142_BLOCK_0317C_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0317C_EDIT,d2",
        0x031DD, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_09428_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$09424: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$09486: FE11F700031D\n",
        0x09428, 0x09486, 23, 1,
        "UNIT142_BLOCK_09428_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_09428_EDIT,d3",
        0x0943F, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_09930_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0992C: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0998E: FE11F700031D\n",
        0x09930, 0x0998E, 23, 1,
        "UNIT142_BLOCK_09930_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_09930_EDIT,d3",
        0x09947, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0781C_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$07816: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$07874: 47657450\n",
        0x0781C, 0x07874, 23, 2,
        "UNIT142_BLOCK_0781C_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0781C_EDIT,d2",
        0x07871, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0C3C2_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0C3BE: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0C416: FE11F700031D\n",
        0x0C3C2, 0x0C416, 22, 1,
        "UNIT142_BLOCK_0C3C2_EDIT", 0, 1,
        "    move.l #$00000000,d3", "    move.l #UNIT142_BLOCK_0C3C2_EDIT,d3",
        0x0C3E1, 0, 1,
    ),
)

MODULE_DESCRIPTION = {
    "M19_UNIT142_DISPATCH_V2_MC68020.s": "AP20 V2 dispatcher",
    "M19_UNIT142_INIT_ENTRY_MC68020.s": "AGA init/entry",
    "M19_UNIT142_GRAPHICS_GUARD_MC68020.s": "graphics library guard",
    "M19_UNIT142_GRAPHICS_SCREEN_MC68020.s": "graphics screen preflight",
    "M19_UNIT142_IFF_LOAD_BODY_MC68020.s": "IFF load preflight body",
    "M19_UNIT142_IFF_PALETTE_BODY_MC68020.s": "IFF screen and palette validation",
    "M19_UNIT142_IFF_AP20_PRECALL_MC68020.s": "IFF AP20 pre-call controls",
    "M19_UNIT142_COLOR_RANGE_MC68020.s": "color range/entry validation",
    "M19_UNIT142_ENTRY_02E64_MC68020.s": "public entry $02E64",
    "M19_UNIT142_ENTRY_03270_MC68020.s": "public entry $03270",
    "M19_UNIT142_ENTRY_034F4_MC68020.s": "public entry $034F4",
    "M19_UNIT142_ENTRY_03C46_MC68020.s": "public entry $03C46",
    "M19_UNIT142_ENTRY_0530E_MC68020.s": "public entry $0530E",
    "M19_UNIT142_ENTRY_0609E_MC68020.s": "public entry $0609E",
    "M19_UNIT142_ENTRY_06678_MC68020.s": "public entry $06678",
    "M19_UNIT142_ENTRY_0700A_MC68020.s": "public entry $0700A",
    "M19_UNIT142_ENTRY_04256_MC68020.s": "public entry $04256",
    "M19_UNIT142_ENTRY_044EA_MC68020.s": "public entry $044EA",
    "M19_UNIT142_ENTRY_0479E_MC68020.s": "public entry $0479E",
    "M19_UNIT142_ENTRY_04B40_MC68020.s": "public entry $04B40",
    "M19_UNIT142_ENTRY_04D4C_MC68020.s": "public entry $04D4C",
    "M19_UNIT142_ENTRY_04F58_MC68020.s": "public entry $04F58",
    "M19_UNIT142_BLOCK_078A4_MC68020.s": "verified block $078A4",
    "M19_UNIT142_BLOCK_07BC8_MC68020.s": "verified block $07BC8",
    "M19_UNIT142_BLOCK_08618_MC68020.s": "verified block $08618",
    "M19_UNIT142_BLOCK_08D78_MC68020.s": "verified block $08D78",
    "M19_UNIT142_BLOCK_09C80_MC68020.s": "verified block $09C80",
    "M19_UNIT142_BLOCK_0A006_MC68020.s": "verified block $0A006",
    "M19_UNIT142_BLOCK_0A476_MC68020.s": "verified block $0A476",
    "M19_UNIT142_BLOCK_0A71A_MC68020.s": "verified block $0A71A",
    "M19_UNIT142_BLOCK_0B0A6_MC68020.s": "verified block $0B0A6",
    "M19_UNIT142_BLOCK_0BA5E_MC68020.s": "verified block $0BA5E",
    "M19_UNIT142_BLOCK_0C41C_MC68020.s": "verified block $0C41C",
    "M19_UNIT142_BLOCK_0C946_MC68020.s": "verified block $0C946",
    "M19_UNIT142_BLOCK_0CF3E_MC68020.s": "verified block $0CF3E",
    "M19_UNIT142_BLOCK_0D336_MC68020.s": "verified block $0D336",
    "M19_UNIT142_BLOCK_0D99A_MC68020.s": "verified block $0D99A",
    "M19_UNIT142_BLOCK_0219C_MC68020.s": "public entry $0219C",
    "M19_UNIT142_BLOCK_0282C_MC68020.s": "public entry $0282C",
    "M19_UNIT142_BLOCK_05150_MC68020.s": "public entry $05150",
    "M19_UNIT142_BLOCK_05706_MC68020.s": "public entry $05706",
    "M19_UNIT142_BLOCK_058C6_MC68020.s": "public entry $058C6",
    "M19_UNIT142_BLOCK_05C7A_MC68020.s": "public entry $05C7A",
    "M19_UNIT142_BLOCK_07482_MC68020.s": "native block $07482",
    "M19_UNIT142_BLOCK_0D7C8_MC68020.s": "source-verified clean block $0D7C8",
    "M19_UNIT142_BLOCK_01F32_MC68020.s": "source-verified clean block $01F32",
    "M19_UNIT142_BLOCK_095EC_MC68020.s": "source-verified clean block $095EC",
    "M19_UNIT142_BLOCK_09790_MC68020.s": "source-verified clean block $09790",
    "M19_UNIT142_BLOCK_0AF3A_MC68020.s": "source-verified clean block $0AF3A",
    "M19_UNIT142_BLOCK_09B16_MC68020.s": "source-verified clean block $09B16",
    "M19_UNIT142_BLOCK_0B8FE_MC68020.s": "source-verified clean block $0B8FE",
    "M19_UNIT142_BLOCK_0652C_MC68020.s": "source-verified clean block $0652C",
    "M19_UNIT142_BLOCK_0411A_MC68020.s": "source-verified clean block $0411A",
    "M19_UNIT142_BLOCK_03A24_MC68020.s": "source-verified clean block $03A24",
    "M19_UNIT142_BLOCK_00A80_MC68020.s": "source-verified clean block $00A80",
    "M19_UNIT142_BLOCK_01E12_MC68020.s": "source-verified clean block $01E12",
    "M19_UNIT142_BLOCK_0D694_MC68020.s": "source-verified clean block $0D694",
    "M19_UNIT142_BLOCK_02584_MC68020.s": "source-verified clean block $02584",
    "M19_UNIT142_BLOCK_07360_MC68020.s": "source-verified clean block $07360",
    "M19_UNIT142_BLOCK_00BA2_MC68020.s": "source-verified clean block $00BA2",
    "M19_UNIT142_BLOCK_03B52_MC68020.s": "source-verified clean block $03B52",
    "M19_UNIT142_BLOCK_0273C_MC68020.s": "source-verified clean block $0273C",
    "M19_UNIT142_BLOCK_02C9A_MC68020.s": "source-verified clean block $02C9A",
    "M19_UNIT142_BLOCK_0725A_MC68020.s": "source-verified clean block $0725A",
    "M19_UNIT142_BLOCK_020E6_MC68020.s": "source-verified clean block $020E6",
    "M19_UNIT142_BLOCK_08568_MC68020.s": "source-verified clean block $08568",
    "M19_UNIT142_BLOCK_02690_MC68020.s": "source-verified clean block $02690",
    "M19_UNIT142_BLOCK_099C6_MC68020.s": "source-verified clean block $099C6",
    "M19_UNIT142_BLOCK_00C9E_MC68020.s": "source-verified clean block $00C9E",
    "M19_UNIT142_BLOCK_08CDA_MC68020.s": "source-verified clean block $08CDA",
    "M19_UNIT142_BLOCK_09F6A_MC68020.s": "source-verified clean block $09F6A",
    "M19_UNIT142_BLOCK_00764_MC68020.s": "source-verified clean block $00764",
    "M19_UNIT142_BLOCK_031E4_MC68020.s": "source-verified clean block $031E4",
    "M19_UNIT142_BLOCK_09564_MC68020.s": "source-verified clean block $09564",
    "M19_UNIT142_BLOCK_01540_MC68020.s": "source-verified clean block $01540",
    "M19_UNIT142_BLOCK_0398C_MC68020.s": "source-verified clean block $0398C",
    "M19_UNIT142_BLOCK_09A9E_MC68020.s": "source-verified clean block $09A9E",
    "M19_UNIT142_BLOCK_094BE_MC68020.s": "source-verified clean block $094BE",
    "M19_UNIT142_BLOCK_02BBA_MC68020.s": "source-verified clean block $02BBA",
    "M19_UNIT142_BLOCK_02C2A_MC68020.s": "source-verified clean block $02C2A",
    "M19_UNIT142_BLOCK_07B56_MC68020.s": "source-verified clean block $07B56",
    "M19_UNIT142_BLOCK_0C8D8_MC68020.s": "source-verified clean block $0C8D8",
    "M19_UNIT142_BLOCK_02D90_MC68020.s": "source-verified clean block $02D90",
    "M19_UNIT142_BLOCK_02DFA_MC68020.s": "source-verified clean block $02DFA",
    "M19_UNIT142_BLOCK_0317C_MC68020.s": "source-verified clean block $0317C",
    "M19_UNIT142_BLOCK_09428_MC68020.s": "source-verified clean block $09428",
    "M19_UNIT142_BLOCK_09930_MC68020.s": "source-verified clean block $09930",
    "M19_UNIT142_BLOCK_0781C_MC68020.s": "source-verified clean block $0781C",
    "M19_UNIT142_BLOCK_0C3C2_MC68020.s": "source-verified clean block $0C3C2",
}


class Unit142Error(ValueError):
    pass


def demand(condition, message):
    if not condition:
        raise Unit142Error(message)


def strip_annotations(text):
    lines = []
    for line in text.splitlines():
        match = ANNOT.search(line)
        lines.append(line[:match.start()].rstrip() if match else line)
    return "\n".join(lines) + "\n"


def expected_sources():
    audit = AUDIT.read_text("ascii")
    # Validate all 62,740 native bytes in order, not just the changed slices.
    whole = bytearray()
    annotations = 0
    for line in audit.splitlines():
        match = ANNOT.search(line)
        if match is None:
            continue
        demand(int(match.group(1), 16) == len(whole),
               "UNIT142 original audit offset discontinuity")
        whole.extend(bytes.fromhex(match.group(2)))
        annotations += 1
    demand(annotations == 14693 and len(whole) == GROUP_SIZE and
           sha256(whole).hexdigest() == GROUP_SHA,
           "UNIT142 complete SHA-pinned native group changed")

    wrapper = strip_annotations(audit)
    marker = "; AGA_NATIVE_PURPOSE: AUDIT_ONLY"
    demand(wrapper.count(marker) == 1, "UNIT142 audit marker missing")
    wrapper = wrapper.replace(
        marker, "; PARTIAL_SOURCE_MIGRATION: UNIT142 pinned MC68020 code, audit remainder"
    ).replace(
        "; PARTIAL MC68020 MNEMONIC RESTORATION (not an installable .Lib)",
        "; Selected native spans source-owned; remaining legacy mnemonics/data pinned"
    )

    modules = []
    for (filename, start, stop, lo, hi, instruction_count, label_count,
         symbol, old_value, new_value, opcode, replacement,
         diff, old_byte, new_byte) in SPANS:
        begin = audit.find(start)
        end = audit.find(stop, begin + len(start))
        demand(begin >= 0 and end > begin and
               audit.find(start, begin + len(start)) < 0,
               "UNIT142 source boundaries absent/ambiguous: " + filename)
        fragment = audit[begin+len(start):end]
        lines, at, instructions, labels = [], lo, 0, 0
        for line in fragment.splitlines():
            if not line.strip():
                continue
            if LABEL.fullmatch(line):
                labels += 1
                lines.append(line)
                continue
            match = ANNOT.search(line)
            demand(match is not None and int(match.group(1), 16) == at and
                   not line.lstrip().lower().startswith("dc."),
                   "UNIT142 unclassified data/misaligned code: " + filename)
            at += len(bytes.fromhex(match.group(2)))
            instructions += 1
            lines.append(line[:match.start()].rstrip())
        demand(at == hi and instructions == instruction_count and
               labels == label_count and
               whole[diff] == old_byte and lo <= diff < hi,
               "UNIT142 source byte/label/extension count drift: " + filename)
        code = "\n".join(lines).rstrip() + "\n"
        demand(code.count(opcode) == 1 and
               new_value != old_value,
               "UNIT142 edit constant ambiguous: " + filename)
        header = (
            "; AGA_NATIVE_MIN_CPU: MC68020\n"
            "; UNIT142 " + MODULE_DESCRIPTION[filename] + " source-verified against pinned P2d emitter.\n"
            f"; UNIT142+${lo:05X}..${hi:05X}, {hi-lo} instructions/data bytes.\n"
            + symbol + f" equ {old_value}\n\n"
        )
        module = header + code.replace(opcode, replacement)
        original_fragment = strip_annotations(fragment)
        # A source region can start after a raw GetP/AMOS Main marker.
        # The wrapper has its source offsets stripped, including those markers.
        compact_start = strip_annotations(start)
        target = compact_start + original_fragment
        demand(wrapper.count(target) == 1,
               "UNIT142 wrapper region missing/ambiguous: " + filename)
        wrapper = wrapper.replace(
            target, compact_start + '    include "' + filename + '"\n'
        )
        modules.append((lo, hi, filename, module))
    return bytes(whole), wrapper, modules


def verify(official):
    demand(len(official) == 136020 and
           sha256(official).hexdigest() == P2D_SHA,
           "UNIT142 official P2d source builder SHA differs")
    native, wrapper, modules = expected_sources()
    tokens, groups, title = unpack_ap20(official)
    matches = [i for i, g in enumerate(groups)
               if len(g) == GROUP_SIZE and sha256(g).hexdigest() == GROUP_SHA]
    demand(len(matches) == 1 and
           groups[matches[0]] == native,
           "UNIT142 absent/ambiguous in authoritative P2d AP20")
    for lo, hi, filename, source in modules:
        demand(groups[matches[0]][lo:hi] == native[lo:hi],
               "UNIT142 source slice mismatch: " + filename)
        demand((NATIVE_DIR / filename).read_text("ascii") == source,
               "UNIT142 editable source differs from pinned proof: " + filename)
    demand(WRAPPER.read_text("ascii") == wrapper,
           "UNIT142 native wrapper not derived exactly from pinned source")
    print("UNIT142_SOURCE_PROVEN: 49632 bytes / 89 MC68020 modules, AP20 group",
          matches[0], "unit", len(native))
    return matches[0]


def stage(folder, official):
    verify(official)
    (folder / STAGED_NAME).write_bytes(WRAPPER.read_bytes())
    for filename, *_ in SPANS:
        (folder / filename).write_bytes((NATIVE_DIR / filename).read_bytes())


def edit_gate(staged, assembler):
    official = (staged / "M19_P2D_ASM_REBUILT_CHECK.Lib").read_bytes()
    group = verify(official)
    demand((staged / STAGED_NAME).is_file() and
           (staged / MASTER_NAME).is_file() and
           all((staged / spec[0]).is_file() for spec in SPANS),
           "UNIT142 staged source missing")
    with TemporaryDirectory(prefix="unit142_mc68020_edit_") as temp:
        folder = Path(temp)
        for source in staged.glob("*.s"):
            shutil.copy2(source, folder / source.name)
        for (filename, _start, _stop, _lo, _hi, _inst, _labels,
             symbol, old_value, new_value, _opcode, _replacement,
             _diff, _old, _new) in SPANS:
            path = folder / filename
            text = path.read_text("ascii")
            before = symbol + " equ " + str(old_value)
            demand(text.count(before) == 1,
                   "UNIT142 mutation not unique: " + filename)
            path.write_text(text.replace(
                before, symbol + " equ " + str(new_value)),
                encoding="ascii", newline="\n")
        output = folder / "UNIT142_EDITED_UNTESTED.Lib"
        command = [str(assembler.resolve()), "-Fbin", "-m68020",
                   "-no-opt", "-quiet", "-o", str(output), MASTER_NAME]
        result = subprocess.run(command, cwd=folder, capture_output=True,
                                text=True, check=False)
        demand(result.returncode == 0,
               "UNIT142 vasm edit failed: " + result.stderr)
        edited = output.read_bytes()
        tok0, units0, title0 = unpack_ap20(official)
        tok1, units1, title1 = unpack_ap20(edited)
        demand(len(edited) == len(official) and tok0 == tok1 and
               title0 == title1 and len(units0) == len(units1) and
               all(a == b for i, (a, b) in enumerate(zip(units0, units1))
                   if i != group), "UNIT142 edit corrupted unrelated AP20")
        base, changed = units0[group], units1[group]
        deltas = [i for i, (a, b) in enumerate(zip(base, changed)) if a != b]
        expected = {spec[12]: (spec[13], spec[14]) for spec in SPANS}
        demand(deltas == sorted(expected) and
               all((base[i], changed[i]) == pair
                   for i, pair in expected.items()),
               "UNIT142 isolated one-byte edits escaped expected offsets")
    print("UNIT142_EDIT_TEST_PASS: 89 exact bytes, only UNIT142, no AP20 drift")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    opts = parser.add_mutually_exclusive_group(required=True)
    opts.add_argument("--check", action="store_true")
    opts.add_argument("--self-test-edit", action="store_true")
    parser.add_argument("--staged", type=Path)
    parser.add_argument("--vasm", type=Path)
    args = parser.parse_args()
    if args.self_test_edit:
        demand(args.staged is not None and args.vasm is not None,
               "--self-test-edit requires --staged and --vasm")
        edit_gate(args.staged, args.vasm)
    else:
        from build_m19_p2d_editable_asm import prove_source_provenance
        verify(prove_source_provenance()[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
