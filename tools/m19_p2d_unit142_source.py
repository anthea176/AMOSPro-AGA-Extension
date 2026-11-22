#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-backed UNIT142 MC68020: exact P2d staging and isolated edit gate.

The audit export supplies only candidate mnemonic spelling. The authoritative
bytes are the SHA-pinned, emitter-built P2d AP20 unit. Neither this tool nor
the direct assembler writes into dist/ or changes an AMOS campaign.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
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
CBLOCK_CORE_SHA = "8a3df13b72b0a62f237b7df068cc9d3f47c70af759d0bc64949ed765cfd65a97"
CBLOCK_SPANS = ((0x0ABC6, 0x0AF3A), (0x0B58A, 0x0B8FE), (0x0BF52, 0x0C2C6))
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
    (
        "M19_UNIT142_BLOCK_0CEF2_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0CEEE: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0CF38: FE11F700031D\n",
        0x0CEF2, 0x0CF38, 17, 1,
        "UNIT142_BLOCK_0CEF2_EDIT", 1, 2,
        "    cmpi.l #$00000001,d0", "    cmpi.l #UNIT142_BLOCK_0CEF2_EDIT,d0",
        0x0CF13, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_0C2C6_MC68020.s",
        "    dc.b $4C,$DF,$77,$F7,$74,$00,$4E,$75,$47,$65,$74,$50  ; +$0C2BA: 4CDF77F774004E7547657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0C308: FE11F700031D\n",
        0x0C2C6, 0x0C308, 19, 1,
        "UNIT142_BLOCK_0C2C6_EDIT", 5, 6,
        "    cmpi.l #$00000005,d0", "    cmpi.l #UNIT142_BLOCK_0C2C6_EDIT,d0",
        0x0C2DF, 5, 6,
    ),
    (
        "M19_UNIT142_BLOCK_0C344_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0C340: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0C386: FE11F700031D\n",
        0x0C344, 0x0C386, 19, 1,
        "UNIT142_BLOCK_0C344_EDIT", 5, 6,
        "    cmpi.l #$00000005,d0", "    cmpi.l #UNIT142_BLOCK_0C344_EDIT,d0",
        0x0C35D, 5, 6,
    ),
    (
        "M19_UNIT142_BLOCK_077DC_MC68020.s",
        "    dc.b $41,$47,$41,$50,$49,$43,$20,$20,$47,$65,$74,$50  ; +$077D0: 414741504943202047657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$07816: FE11F700031D\n",
        0x077DC, 0x07816, 16, 1,
        "UNIT142_BLOCK_077DC_EDIT", 5, 6,
        "    cmpi.l #$00000005,d0", "    cmpi.l #UNIT142_BLOCK_077DC_EDIT,d0",
        0x07807, 5, 6,
    ),
    (
        "M19_UNIT142_BLOCK_0C30E_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0C308: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$0C340: 47657450\n",
        0x0C30E, 0x0C340, 14, 2,
        "UNIT142_BLOCK_0C30E_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0C30E_EDIT,d2",
        0x0C33D, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0C38C_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0C386: FE11F700031D\n",
        "    dc.b $47,$65,$74,$50  ; +$0C3BE: 47657450\n",
        0x0C38C, 0x0C3BE, 14, 2,
        "UNIT142_BLOCK_0C38C_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0C38C_EDIT,d2",
        0x0C3BB, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_07878_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$07874: 47657450\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0789E: FE11F700031D\n",
        0x07878, 0x0789E, 10, 1,
        "UNIT142_BLOCK_07878_EDIT", 5, 6,
        "    cmpi.l #$00000005,d0", "    cmpi.l #UNIT142_BLOCK_07878_EDIT,d0",
        0x0788F, 5, 6,
    ),
    (
        "M19_UNIT142_BLOCK_0949E_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$09498: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$094B8: FE11F7000330\n",
        0x0949E, 0x094B8, 7, 0,
        "UNIT142_BLOCK_0949E_EDIT", 1, 2,
        "    move.l #$00000001,d1", "    move.l #UNIT142_BLOCK_0949E_EDIT,d1",
        0x094AF, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_099A6_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$099A0: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$099C0: FE11F7000330\n",
        0x099A6, 0x099C0, 7, 0,
        "UNIT142_BLOCK_099A6_EDIT", 3, 4,
        "    move.l #$00000003,d1", "    move.l #UNIT142_BLOCK_099A6_EDIT,d1",
        0x099B7, 3, 4,
    ),
    (
        "M19_UNIT142_BLOCK_0A6FA_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0A6F4: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$0A714: FE11F7000330\n",
        0x0A6FA, 0x0A714, 7, 0,
        "UNIT142_BLOCK_0A6FA_EDIT", 3, 4,
        "    move.l #$00000003,d1", "    move.l #UNIT142_BLOCK_0A6FA_EDIT,d1",
        0x0A70B, 3, 4,
    ),
    (
        "M19_UNIT142_BLOCK_07342_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0733C: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$0735A: FE11F7000330\n",
        0x07342, 0x0735A, 7, 0,
        "UNIT142_BLOCK_07342_EDIT", 1, 2,
        "    move.l #$00000001,d1", "    move.l #UNIT142_BLOCK_07342_EDIT,d1",
        0x07351, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_0AB96_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$0AB90: FE11F7000333\n",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$0ABAE: FE11F7000320\n",
        0x0AB96, 0x0ABAE, 6, 1,
        "UNIT142_BLOCK_0AB96_EDIT", 1, 2,
        "    move.l #$00000001,d3", "    move.l #UNIT142_BLOCK_0AB96_EDIT,d3",
        0x0AB9B, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_0D7AA_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0D7A4: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$30  ; +$0D7C2: FE11F7000330\n",
        0x0D7AA, 0x0D7C2, 7, 0,
        "UNIT142_BLOCK_0D7AA_EDIT", 1, 2,
        "    move.l #$00000001,d1", "    move.l #UNIT142_BLOCK_0D7AA_EDIT,d1",
        0x0D7B9, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_0C8BE_MC68020.s",
        "    dc.b $60,$00,$00,$08  ; +$0C8BA: 60000008\n",
        "    dc.b $47,$65,$74,$50  ; +$0C8D4: 47657450\n",
        0x0C8BE, 0x0C8D4, 6, 2,
        "UNIT142_BLOCK_0C8BE_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0C8BE_EDIT,d2",
        0x0C8D1, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0CED8_MC68020.s",
        "    dc.b $60,$00,$00,$08  ; +$0CED4: 60000008\n",
        "    dc.b $47,$65,$74,$50  ; +$0CEEE: 47657450\n",
        0x0CED8, 0x0CEEE, 6, 2,
        "UNIT142_BLOCK_0CED8_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0CED8_EDIT,d2",
        0x0CEEB, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_09546_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$09540: FE11F7000320\n",
        "    dc.b $46,$49,$43,$4F,$4E,$38,$20,$20,$47,$65,$74,$50  ; +$09558: 4649434F4E38202047657450\n",
        0x09546, 0x09558, 5, 2,
        "UNIT142_BLOCK_09546_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_09546_EDIT,d2",
        0x09555, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_09A80_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$09A7A: FE11F7000320\n",
        "    dc.b $46,$49,$43,$48,$49,$50,$38,$20,$47,$65,$74,$50  ; +$09A92: 464943484950382047657450\n",
        0x09A80, 0x09A92, 5, 2,
        "UNIT142_BLOCK_09A80_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_09A80_EDIT,d2",
        0x09A8F, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0ABB4_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$0ABAE: FE11F7000320\n",
        "    dc.b $41,$47,$41,$43,$42,$4C,$4B,$20  ; +$0ABC6: 41474143424C4B20\n",
        0x0ABB4, 0x0ABC6, 5, 3,
        "UNIT142_BLOCK_0ABB4_EDIT", 0, 1,
        "    moveq #0,d2", "    moveq #UNIT142_BLOCK_0ABB4_EDIT,d2",
        0x0ABC3, 0, 1,
    ),
    (
        "M19_UNIT142_BLOCK_0746E_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$07468: FE11F7000333\n",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$0747C: FE11F7000320\n",
        0x0746E, 0x0747C, 3, 1,
        "UNIT142_BLOCK_0746E_EDIT", 1, 2,
        "    move.l #$00000001,88(a2)", "    move.l #UNIT142_BLOCK_0746E_EDIT,88(a2)",
        0x07473, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_09532_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$0952C: FE11F7000333\n",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$09540: FE11F7000320\n",
        0x09532, 0x09540, 3, 1,
        "UNIT142_BLOCK_09532_EDIT", 1, 2,
        "    move.l #$00000001,d3", "    move.l #UNIT142_BLOCK_09532_EDIT,d3",
        0x09537, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_09A6C_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$09A66: FE11F7000333\n",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$09A7A: FE11F7000320\n",
        0x09A6C, 0x09A7A, 3, 1,
        "UNIT142_BLOCK_09A6C_EDIT", 1, 2,
        "    move.l #$00000001,d3", "    move.l #UNIT142_BLOCK_09A6C_EDIT,d3",
        0x09A71, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_0D986_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$33  ; +$0D980: FE11F7000333\n",
        "    dc.b $FE,$11,$F7,$00,$03,$20  ; +$0D994: FE11F7000320\n",
        0x0D986, 0x0D994, 3, 1,
        "UNIT142_BLOCK_0D986_EDIT", 1, 2,
        "    move.l #$00000001,88(a2)", "    move.l #UNIT142_BLOCK_0D986_EDIT,88(a2)",
        0x0D98B, 1, 2,
    ),
    (
        "M19_UNIT142_BLOCK_00A62_MC68020.s",
        "    dc.b $7F,$FF,$4E,$75,$47,$65,$74,$50  ; +$00A5A: 7FFF4E7547657450\n",
        "    dc.b $47,$65,$74,$50  ; +$00A7C: 47657450\n",
        0x00A62, 0x00A7C, 8, 2,
        "UNIT142_BLOCK_00A62_EDIT", -270, -269,
        "    jsr -270(a6)", "    jsr UNIT142_BLOCK_00A62_EDIT(a6)",
        0x00A75, 242, 243,
    ),
    (
        "M19_UNIT142_BLOCK_0A6E2_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0A6DC: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0A6F4: FE11F700031D\n",
        0x0A6E2, 0x0A6F4, 5, 0,
        "UNIT142_BLOCK_0A6E2_EDIT", 24, 25,
        "    move.l 24(a2),d0", "    move.l UNIT142_BLOCK_0A6E2_EDIT(a2),d0",
        0x0A6E9, 24, 25,
    ),
    (
        "M19_UNIT142_BLOCK_0948C_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$09486: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$09498: FE11F700031D\n",
        0x0948C, 0x09498, 4, 0,
        "UNIT142_BLOCK_0948C_EDIT", 4, 5,
        "    move.l 4(a2),d0", "    move.l UNIT142_BLOCK_0948C_EDIT(a2),d0",
        0x09497, 4, 5,
    ),
    (
        "M19_UNIT142_BLOCK_09994_MC68020.s",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0998E: FE11F700031D\n",
        "    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$099A0: FE11F700031D\n",
        0x09994, 0x099A0, 4, 0,
        "UNIT142_BLOCK_09994_EDIT", 4, 5,
        "    move.l 4(a2),d0", "    move.l UNIT142_BLOCK_09994_EDIT(a2),d0",
        0x0999F, 4, 5,
    ),
    (
        "M19_UNIT142_BLOCK_015C0_MC68020.s",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$015BA: 203C00000000\n",
        "    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00  ; +$015C8: 646F732E6C69627261727900\n",
        0x015C0, 0x015C8, 3, 2,
        "UNIT142_BLOCK_015C0_EDIT", 0, 1,
        "    tst.l d0", "    ifne UNIT142_BLOCK_015C0_EDIT\n        tst.w d0\n    else\n        tst.l d0\n    endif",
        0x015C5, 128, 64,
    ),
    (
        "M19_UNIT142_BLOCK_01BCA_MC68020.s",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$01BC4: 203C00000000\n",
        "    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00  ; +$01BD2: 646F732E6C69627261727900\n",
        0x01BCA, 0x01BD2, 3, 2,
        "UNIT142_BLOCK_01BCA_EDIT", 0, 1,
        "    tst.l d0", "    ifne UNIT142_BLOCK_01BCA_EDIT\n        tst.w d0\n    else\n        tst.l d0\n    endif",
        0x01BCF, 128, 64,
    ),
    (
        "M19_UNIT142_BLOCK_03A0C_MC68020.s",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$03A06: 203C00000000\n",
        "    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00  ; +$03A14: 646F732E6C69627261727900\n",
        0x03A0C, 0x03A14, 3, 2,
        "UNIT142_BLOCK_03A0C_EDIT", 0, 1,
        "    tst.l d0", "    ifne UNIT142_BLOCK_03A0C_EDIT\n        tst.w d0\n    else\n        tst.l d0\n    endif",
        0x03A11, 128, 64,
    ),
    (
        "M19_UNIT142_BLOCK_04102_MC68020.s",
        "    dc.b $20,$3C,$00,$00,$00,$00  ; +$040FC: 203C00000000\n",
        "    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00  ; +$0410A: 646F732E6C69627261727900\n",
        0x04102, 0x0410A, 3, 2,
        "UNIT142_BLOCK_04102_EDIT", 0, 1,
        "    tst.l d0", "    ifne UNIT142_BLOCK_04102_EDIT\n        tst.w d0\n    else\n        tst.l d0\n    endif",
        0x04107, 128, 64,
    ),
    (
        "M19_UNIT142_BLOCK_002A2_MC68020.s",
        "    dc.b $20,$06,$4E,$75,$47,$65,$74,$50  ; +$0029A: 20064E7547657450\n",
        "    dc.b $20,$6D,$FF,$FC,$4E,$A8,$01,$90,$4E,$75,$47,$65  ; +$002A4: 206DFFFC4EA801904E754765\n",
        0x002A2, 0x002A4, 1, 1,
        "UNIT142_BLOCK_002A2_EDIT", 0, 1,
        "    rts", "    ifne UNIT142_BLOCK_002A2_EDIT\n        nop\n    else\n        rts\n    endif",
        0x002A3, 117, 113,
    ),
    (
        "M19_UNIT142_BLOCK_002B2_MC68020.s",
        "    dc.b $74,$50  ; +$002B0: 7450\n",
        "    dc.b $20,$6D,$FF,$FC,$4E,$A8,$01,$90,$4E,$75,$47,$65  ; +$002B4: 206DFFFC4EA801904E754765\n",
        0x002B2, 0x002B4, 1, 1,
        "UNIT142_BLOCK_002B2_EDIT", 0, 1,
        "    rts", "    ifne UNIT142_BLOCK_002B2_EDIT\n        nop\n    else\n        rts\n    endif",
        0x002B3, 117, 113,
    ),
    (
        "M19_UNIT142_BLOCK_02360_MC68020.s",
        "    dc.b $47,$65,$74,$50  ; +$0235C: 47657450\n",
        "    dc.b $2A,$1B,$28,$1B,$22,$1B,$20,$1B,$28,$6D,$01,$C8  ; +$02364: 2A1B281B221B201B286D01C8\n",
        0x02360, 0x02364, 1, 1,
        "UNIT142_BLOCK_02360_EDIT", 0, 2,
        "    bra.w L_UNIT142_078E6", "    bra.w L_UNIT142_078E6+UNIT142_BLOCK_02360_EDIT",
        0x02363, 132, 134,
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
    "M19_UNIT142_BLOCK_0CEF2_MC68020.s": "source-verified clean block $0CEF2",
    "M19_UNIT142_BLOCK_0C2C6_MC68020.s": "source-verified clean block $0C2C6",
    "M19_UNIT142_BLOCK_0C344_MC68020.s": "source-verified clean block $0C344",
    "M19_UNIT142_BLOCK_077DC_MC68020.s": "source-verified clean block $077DC",
    "M19_UNIT142_BLOCK_0C30E_MC68020.s": "source-verified clean block $0C30E",
    "M19_UNIT142_BLOCK_0C38C_MC68020.s": "source-verified clean block $0C38C",
    "M19_UNIT142_BLOCK_07878_MC68020.s": "source-verified clean block $07878",
    "M19_UNIT142_BLOCK_0949E_MC68020.s": "source-verified clean block $0949E",
    "M19_UNIT142_BLOCK_099A6_MC68020.s": "source-verified clean block $099A6",
    "M19_UNIT142_BLOCK_0A6FA_MC68020.s": "source-verified clean block $0A6FA",
    "M19_UNIT142_BLOCK_07342_MC68020.s": "source-verified clean block $07342",
    "M19_UNIT142_BLOCK_0AB96_MC68020.s": "source-verified clean block $0AB96",
    "M19_UNIT142_BLOCK_0D7AA_MC68020.s": "source-verified clean block $0D7AA",
    "M19_UNIT142_BLOCK_0C8BE_MC68020.s": "source-verified clean block $0C8BE",
    "M19_UNIT142_BLOCK_0CED8_MC68020.s": "source-verified clean block $0CED8",
    "M19_UNIT142_BLOCK_09546_MC68020.s": "source-verified clean block $09546",
    "M19_UNIT142_BLOCK_09A80_MC68020.s": "source-verified clean block $09A80",
    "M19_UNIT142_BLOCK_0ABB4_MC68020.s": "source-verified clean block $0ABB4",
    "M19_UNIT142_BLOCK_0746E_MC68020.s": "source-verified clean block $0746E",
    "M19_UNIT142_BLOCK_09532_MC68020.s": "source-verified clean block $09532",
    "M19_UNIT142_BLOCK_09A6C_MC68020.s": "source-verified clean block $09A6C",
    "M19_UNIT142_BLOCK_0D986_MC68020.s": "source-verified clean block $0D986",
    "M19_UNIT142_BLOCK_00A62_MC68020.s": "OS graphics LVO call",
    "M19_UNIT142_BLOCK_0A6E2_MC68020.s": "bank bridge offset",
    "M19_UNIT142_BLOCK_0948C_MC68020.s": "field bridge offset",
    "M19_UNIT142_BLOCK_09994_MC68020.s": "field bridge offset",
    "M19_UNIT142_BLOCK_015C0_MC68020.s": "stack epilogue tst $015C0",
    "M19_UNIT142_BLOCK_01BCA_MC68020.s": "stack epilogue tst $01BCA",
    "M19_UNIT142_BLOCK_03A0C_MC68020.s": "stack epilogue tst $03A0C",
    "M19_UNIT142_BLOCK_04102_MC68020.s": "stack epilogue tst $04102",
    "M19_UNIT142_BLOCK_002A2_MC68020.s": "return $002A2",
    "M19_UNIT142_BLOCK_002B2_MC68020.s": "return $002B2",
    "M19_UNIT142_BLOCK_02360_MC68020.s": "branch $02360",
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


def aga_bridge_expected_source(whole, wrapper):
    """Exact 470-byte P0e AGA bridge from verified original M19 emitter."""
    from generate_aga_multiunit_source import native_unit_source
    from m19_p0e_split_bridge_emit import AGA_CORE, AGA_OFFSETS

    demand(len(AGA_CORE) == 470 and
           sha256(AGA_CORE).hexdigest() ==
           "ddcd43fdfd7922650076dfccc6c31a347dea0b4f5df6350a629882ecb4f3046b" and
           whole[0x0E620:0x0E7F6] == AGA_CORE,
           "UNIT142 P0e AGA bridge source provenance differs")
    entries = [(i, AGA_OFFSETS[name]) for i, name in
               enumerate(("put", "off", "read", "reset"))]
    preview, cov = native_unit_source("P0E_AGA_BRIDGE", AGA_CORE, entries)
    demand(cov["bytes"] == 470 and cov["mnemonic_bytes"] == 470 and
           cov["raw_dc_bytes"] == 0, "UNIT142 P0e AGA bridge not pure ASM")
    prefix = "ENTRY_P0E_AGA_BRIDGE_00000:\n"
    demand(preview.count(prefix) == 1, "P0e AGA bridge entrypoint missing")
    body = preview[preview.index(prefix):]
    symbol = "UNIT142_P0E_AGA_BRIDGE_RESULT"
    op = "    moveq #0,d2"
    demand(body.count(op) == 1 and whole[0x0E7F3] == 0,
           "P0e AGA bridge isolated edit not source backed")
    header = (
        "; AGA_NATIVE_MIN_CPU: MC68020\n"
        "; UNIT142 P0e AGA object bridge source-backed from M19 emitter.\n"
        "; UNIT142+$0E620..$0E7F6, 470 bytes of Motorola instructions.\n"
        "; SHA256 ddcd43fdfd7922650076dfccc6c31a347dea0b4f5df6350a629882ecb4f3046b\n"
        + symbol + " equ 0\n\n"
    )
    module = header + body.replace(op, "    moveq #" + symbol + ",d2")
    first = "    dc.b $48,$E7,$EF,$EE,$2E,$3C,$00,$00,$00,$00,$60,$00\n"
    demand(wrapper.count(first) == 1 and
           wrapper.endswith("    dc.b $4E,$75\n"),
           "P0e bridge wrapper source boundaries changed")
    at = wrapper.index(first)
    demand("ENTRY_UNIT142_0F4E2:" in wrapper[at:],
           "P0e bridge would drop the undecoded public entry")
    def as_data(start, end):
        return "".join(
            "    dc.b " + ",".join("$%02X" % v for v in whole[i:min(i+12,end)]) + "\n"
            for i in range(start,end,12)
        )
    result = (
        wrapper[:at] + '    include "M19_UNIT142_P0E_AGA_BRIDGE_MC68020.s"\n'
        + as_data(0x0E7F6,0x0F4E2)
        + "ENTRY_UNIT142_0F4E2:\n"
        + as_data(0x0F4E2,0x0F514)
    )
    return result,(0x0E620,0x0E7F6,
        "M19_UNIT142_P0E_AGA_BRIDGE_MC68020.s",module)


def p0f_expected_source(whole, wrapper):
    """Four pure Motorola source spans from the source-pinned P0f emitter.

    Keep three uninterpreted AMOS/pseudo-branch sequences (14 bytes) and
    the 1,024-byte state table as DATA; do not claim they are CPU code.
    """
    from m19_p0f_object_identity_emit import emit_object_identity, STAMP_TABLE_BYTES
    from generate_aga_multiunit_source import native_unit_source

    emitted, labels = emit_object_identity()
    code_end = labels["identity_stamp_table"]
    demand(code_end == 1198 and len(emitted) == 2222 and
           STAMP_TABLE_BYTES == 1024 and
           emitted[code_end:] == bytes(1024) and
           whole[0x0E7F6:0x0F0A4] == emitted and
           sha256(emitted[:code_end]).hexdigest() ==
           "fa7d64ce347c08d0e523d5d31ac8a3e3b5175fdd38867bca76c6d7941aa9f2b4",
           "UNIT142 P0f identity source/storage not pinned")
    seeds = [(i,labels[name]) for i,name in enumerate((
        "stamp_capture_entry","stamp_verify_entry",
        "identity_bind_entry","identity_check_entry","identity_clear_entry"
    ))]
    preview,cov = native_unit_source("P0F_IDENTITY_CODE",emitted[:code_end],seeds)
    demand(cov["bytes"] == 1198 and cov["mnemonic_bytes"] == 1184 and
           cov["raw_dc_bytes"] == 14 and cov["unresolved_instruction_encodings"] == 2,
           "UNIT142 P0f code/pseudo-operations classification drift")
    tag = "ENTRY_P0F_IDENTITY_CODE_00000:\n"
    demand(preview.count(tag) == 1,"UNIT142 P0f code entrypoint lost")
    segments = (
        (0x000,0x0E2,"M19_UNIT142_P0F_STAMP_HEAD_MC68020.s",
         "UNIT142_P0F_STAMP_HEAD_EDIT","    move.l #$00000000,d7",0,0x009,0,1),
        (0x0E8,0x32E,"M19_UNIT142_P0F_STAMP_BODY_MC68020.s",
         "UNIT142_P0F_STAMP_BODY_EDIT","    cmpi.l #$00000030,d0",48,0x12F,48,49),
        (0x332,0x3F8,"M19_UNIT142_P0F_BIND_CHECK_MC68020.s",
         "UNIT142_P0F_BIND_CHECK_EDIT","    move.l #$00000000,24(a2)",0,0x385,0,1),
        (0x3FC,0x4AE,"M19_UNIT142_P0F_BIND_RETURN_MC68020.s",
         "UNIT142_P0F_BIND_RETURN_EDIT","    moveq #0,d2",0,0x4AB,0,1),
    )
    expected_raw = ((0x0E2,"FE11F700031D"),(0x32E,"6100F1DE"),(0x3F8,"6100F2BC"))
    chunks = [[] for _ in segments]
    raw = []
    pending = []
    for line in preview[preview.index(tag):].splitlines():
        if not line.strip():
            continue
        match = ANNOT.search(line)
        if match is None:
            demand(line.endswith(":") and line[0].isalpha(),
                   "UNIT142 P0f unknown preview syntax")
            pending.append(line)
            continue
        offset = int(match.group(1),16)
        selected = next((i for i,span in enumerate(segments)
                         if span[0] <= offset < span[1]),None)
        if selected is None:
            demand(not pending,"UNIT142 P0f label on pseudo-byte")
            raw.append((offset,match.group(2)))
        else:
            chunks[selected].extend(pending)
            chunks[selected].append(line)
            pending.clear()
    demand(not pending and tuple(raw) == expected_raw,
           "UNIT142 P0f three pseudo-operation boundaries changed")
    result = []
    for info,lines in zip(segments,chunks):
        lo,hi,filename,symbol,op,old_value,diff,old_byte,new_byte = info
        code = "\n".join(lines) + "\n"
        demand(code.count(op) == 1 and whole[0x0E7F6+diff] == old_byte and
               not any(line.lstrip().lower().startswith("dc.") for line in lines),
               "UNIT142 P0f editable source invalid: " + filename)
        old = "#0" if op == "    moveq #0,d2" else "#$%08X" % old_value
        header = (
            "; AGA_NATIVE_MIN_CPU: MC68020\n"
            f"; UNIT142 P0f source-owned segment ${lo:05X}..${hi:05X}, emitter-exact MC68020.\n"
            "; P0f whole code-and-markers SHA256 fa7d64ce347c08d0e523d5d31ac8a3e3b5175fdd38867bca76c6d7941aa9f2b4\n"
            f"{symbol} equ {old_value}\n\n"
        )
        source = header + code.replace(op, op.replace(old,"#"+symbol))
        result.append((0x0E7F6+lo,0x0E7F6+hi,filename,source,diff,old_value,old_byte,new_byte))
    first = "    dc.b $48,$E7,$EF,$EE,$2E,$3C,$00,$00,$00,$00,$60,$00\n"
    demand(wrapper.count(first) == 1 and
           wrapper.endswith("    dc.b $4E,$75\n") and
           "ENTRY_UNIT142_0F4E2:" in wrapper[wrapper.index(first):],
           "UNIT142 P0f raw envelope changed")
    def dc_range(lo,hi):
        return "".join(
            "    dc.b " + ",".join("$%02X" % x for x in whole[at:min(at+12,hi)]) + "\n"
            for at in range(lo,hi,12)
        )
    new = wrapper[:wrapper.index(first)]
    for i,info in enumerate(result):
        new += '    include "' + info[2] + '"\n'
        if i < len(expected_raw):
            off,hexbytes=expected_raw[i]
            lo=0x0E7F6+off
            demand(whole[lo:lo+len(hexbytes)//2] == bytes.fromhex(hexbytes),
                   "UNIT142 P0f raw pseudo bytes changed")
            new += dc_range(lo,lo+len(hexbytes)//2)
    new += "UNIT142_P0F_STAMP_TABLE:\n    dcb.b 1024,0\n"
    new += dc_range(0x0F0A4,0x0F4E2)
    new += "ENTRY_UNIT142_0F4E2:\n"
    new += dc_range(0x0F4E2,0x0F514)
    return new, [(lo,hi,name,src) for lo,hi,name,src,*_ in result]



LEGACY_OPEN_MODULES = (
    ("M19_UNIT142_LEGACY_OPEN_HEAD_MC68020.s",
     "8ad7223e1a99fdabc53faad372d3b3d0deb39451",
     0x00470, 0x005D4, "UNIT142_LEGACY_OPEN_HEAD_EDIT", 0, 1, 0x0047D),
    ("M19_UNIT142_LEGACY_OPEN_HELPERS_MC68020.s",
     "2e33983bfab09db24f52b4ce5cbfdaa56e948891",
     0x005F8, 0x00760, "UNIT142_LEGACY_OPEN_HELPER_EDIT", 1, 2, 0x005FF),
)

P1CD_PINNED_MODULES = (
    ("M19_UNIT142_P1C_PRIORITY_OPEN_MC68020.s",
     "5c5aaf4a0adf25deac48ba433d33b86e8ad5e384", 0x0F0A4, 0x0F0CA,
     "UNIT142_P1C_OPEN_OK"),
    ("M19_UNIT142_P1D_LIMIT_OPEN_MC68020.s",
     "8450b9fd2a38d191839c3eebd347e7f673bc9a58", 0x0F4E2, 0x0F514,
     "UNIT142_P1D_OPEN_OK"),
)


def p1cd_open_expected_sources(whole, wrapper):
    """Two Motorola source-owned Screen Open wrappers; only data remains dc."""
    from m19_p1c_bob_priority_emit import emit_priority_open
    from m19_p1d_limit_bob_emit import TABLE_BYTES, emit_limit_open

    open_offset = 0x0F0A4 - 34  # R88 AGA group, original Open V2+1102
    priority, context = emit_priority_open(1102, open_offset)
    limit = emit_limit_open(open_offset, 0x0F0D2 - 34)
    demand(len(priority) == 46 and context + 34 == 0x0F0CA and
           priority[-8:] == bytes(8) and
           whole[0x0F0A4:0x0F0D2] == priority and
           sha256(priority[:-8]).hexdigest() ==
           "4d688e2393ffff05d15217088b933f7da761c5a178965ef2cfd0fc50385ddec4",
           "UNIT142 P1c original Screen Open emitter differs")
    demand(TABLE_BYTES == 1040 and len(limit) == 1090 and
           limit[:TABLE_BYTES] == bytes(TABLE_BYTES) and
           whole[0x0F0D2:0x0F514] == limit and
           sha256(limit[TABLE_BYTES:]).hexdigest() ==
           "57f37fd84ce40213d3511d5b2b4cd64a5ed659b02271d94e1fe2327e2c6b54a2",
           "UNIT142 P1d original Screen Open emitter differs")
    def raw(start, end):
        return "".join(
            "    dc.b " + ",".join("$%02X" % x for x in whole[at:min(at+12,end)]) + "\n"
            for at in range(start, end, 12)
        )
    before = raw(0x0F0A4, 0x0F4E2)
    after = "ENTRY_UNIT142_0F4E2:\n" + raw(0x0F4E2, 0x0F514)
    demand(wrapper.count(before) == 1 and wrapper.count(after) == 1,
           "UNIT142 P1c/P1d pinned raw wrapper boundaries differ")
    changed = (
        "UNIT142_P1C_OPEN_ENTRY:\n"
        '    include "M19_UNIT142_P1C_PRIORITY_OPEN_MC68020.s"\n'
        "UNIT142_P1C_CONTEXT:\n"
        "    dcb.b 8,0\n"
        "UNIT142_P1D_LIMIT_TABLE:\n"
        "    dcb.b 1040,0\n"
    )
    wrapper = wrapper.replace(before, changed).replace(
        after, 'ENTRY_UNIT142_0F4E2:\n'
               '    include "M19_UNIT142_P1D_LIMIT_OPEN_MC68020.s"\n')
    result = []
    for filename, pinned_blob, lo, hi, _symbol in P1CD_PINNED_MODULES:
        raw_file = (NATIVE_DIR / filename).read_bytes()
        git_blob = sha1(("blob %d\0" % len(raw_file)).encode("ascii") + raw_file).hexdigest()
        demand(git_blob == pinned_blob and
               raw_file.decode("ascii").startswith("; AGA_NATIVE_MIN_CPU: MC68020\n"),
               "UNIT142 authored P1c/P1d code not pinned: " + filename)
        result.append((lo, hi, filename, raw_file.decode("ascii")))
    return wrapper, result

def p0f_external_bsr_sources(whole,wrapper):
    """Restore two genuine P0f BSR.W to source-verified P0e object entries.

    This is MOTOROLA code; the third P0f FE11 pseudo-call stays raw.
    Baseline displacement is calculated from verified original emitters,
    not inferred from an arbitrary disassembly dump.
    """
    from m19_p0e_object_table_emit import emit_object_table
    from m19_p0f_object_identity_emit import emit_object_identity

    object_src, object_labels = emit_object_table()
    identity_src, _ = emit_object_identity()
    demand(len(object_src) == 2332 and len(identity_src) == 2222 and
           object_labels["object_put_entry"] == 0 and
           object_labels["object_read_entry"] == 0x1A8,
           "UNIT142 P0e historical object entrypoints changed")
    verified = (
        (0x0E7F6+0x32E,0x0DD04+object_labels["object_put_entry"],
         "M19_UNIT142_P0F_BSR_PUT_MC68020.s",
         "UNIT142_P0F_PUT_BSR_DELTA","ENTRY_UNIT142_P0E_OBJECT_00000",
         "6100F1DE","F1DE"),
        (0x0E7F6+0x3F8,0x0DD04+object_labels["object_read_entry"],
         "M19_UNIT142_P0F_BSR_READ_MC68020.s",
         "UNIT142_P0F_READ_BSR_DELTA","ENTRY_UNIT142_P0E_OBJECT_001A8",
         "6100F2BC","F2BC"),
    )
    result=[]
    for pos,target,filename,symbol,label,hexbytes,disp in verified:
        start=pos-0x0E7F6
        demand(identity_src[start:start+4] == bytes.fromhex(hexbytes) and
               whole[pos:pos+4] == bytes.fromhex(hexbytes) and
               ((target-(pos+2))&0xFFFF) == int(disp,16),
               "UNIT142 P0f BSR source target/displacement unproven")
        kind = "Put" if "PUT" in filename else "Read"
        body = (
            "; AGA_NATIVE_MIN_CPU: MC68020\n"
            f"; UNIT142 P0f bridge BSR.W; historical M19 source targets P0e Object {kind}.\n"
            f"; Original +${pos:05X} {hexbytes}, resolves +${target:05X}.\n"
            f"{symbol} equ 0\n\n"
            f"    bsr.w {label}+{symbol}\n"
        )
        old = "    dc.b " + ",".join("$%02X" % q for q in bytes.fromhex(hexbytes)) + "\n"
        demand(wrapper.count(old) == 1,
               "UNIT142 P0f pinned raw branch not unique: " + filename)
        wrapper=wrapper.replace(old,f'    include "{filename}"\n')
        result.append((pos,pos+4,filename,body))
    return wrapper,result


def legacy_r83_screen_sources(whole, wrapper):
    """Exact R83 source-owned legacy Screen Open, with inline data kept raw."""
    from active_library import R83_SHA
    from build_aga_r83_modular import build as build_r83
    from generate_aga_multiunit_source import native_unit_source
    from m19_p1c_bob_priority_emit import emit_priority_open

    historical, info = build_r83()
    demand(info["sha256"] == R83_SHA and
           sha256(historical).hexdigest() == R83_SHA,
           "UNIT142 historical R83 builder provenance differs")
    _tk, units, _title = unpack_ap20(historical)
    reference = whole[0x00470:0x00764]
    demand(len(units[82]) == 52974 and
           units[82][0x00470:0x00764] == reference and
           sha256(reference).hexdigest() ==
           "f10138229ff9bd91bc90cbd08892c74c67f02cc21653b2d7219786749d0852ea",
           "UNIT142 legacy R83 Screen Open source drift")
    priority, _context = emit_priority_open(1102, 0x0F0A4 - 34)
    disp = int.from_bytes(priority[4:8], "big", signed=True)
    demand(priority[:4] == bytes.fromhex("4EBB0170") and
           0x0F0A4 + 2 + disp == 0x00470,
           "UNIT142 P1c live legacy Open call does not target $00470")

    preview, report = native_unit_source("LEGACY_SCREEN_OPEN", reference, [(0, 0)])
    demand(report["mnemonic_bytes"] == 714 and report["raw_dc_bytes"] == 42,
           "UNIT142 legacy Screen Open CFG classification changed")
    pos0 = preview.find("ENTRY_LEGACY_SCREEN_OPEN_00000:")
    pos164 = preview.find("L_LEGACY_SCREEN_OPEN_00164:")
    pos188 = preview.find("L_LEGACY_SCREEN_OPEN_00188:")
    pos2f0 = preview.find("    dc.b $47,$65,$74,$50  ; +$002F0: 47657450")
    demand(0 <= pos0 < pos164 < pos188 < pos2f0,
           "UNIT142 legacy Open code/data boundaries ambiguous")
    head = preview[pos0:pos164]
    helpers = preview[pos188:pos2f0]
    raw_nop = "    dc.b $4E,$71  ; +$00142: 4E71"
    demand(head.count(raw_nop) == 1 and "dc.b" not in helpers,
           "UNIT142 legacy Screen Open code unclassified")
    head = head.replace(raw_nop, "    nop                                                ; +$00142: 4E71")

    def symbolize(body, note, opcode, replacement):
        hits = [line for line in body.splitlines() if note in line]
        demand(len(hits) == 1 and hits[0].lstrip().startswith(opcode),
               "UNIT142 legacy Open isolated edit target not unique")
        return body.replace(hits[0], replacement, 1)

    head = symbolize(head, "; +$0000C: 7600", "moveq #0,d3",
                     "    moveq #UNIT142_LEGACY_OPEN_HEAD_EDIT,d3             ; +$0000C: 7600")
    helpers = symbolize(helpers, "; +$0018E: 7001", "moveq #1,d0",
                        "    moveq #UNIT142_LEGACY_OPEN_HELPER_EDIT,d0           ; +$0018E: 7001")
    sources = (
        "; AGA_NATIVE_MIN_CPU: MC68020\n"
        "; UNIT142 R83 source-proven legacy Screen Open, $00470..$005D4 (356 code bytes).\n"
        "UNIT142_LEGACY_OPEN_HEAD_EDIT equ 0\n\n" + head,
        "; AGA_NATIVE_MIN_CPU: MC68020\n"
        "; UNIT142 R83 source-proven legacy Screen Open helpers, $005F8..$00760 (360 code bytes).\n"
        "UNIT142_LEGACY_OPEN_HELPER_EDIT equ 1\n\n" + helpers,
    )
    demand(reference[0x164:0x176] == b"intuition.library\x00" and
           reference[0x176:0x188] == b"graphics.library\x00\x00" and
           reference[0x2F0:0x2F4] == b"GetP",
           "UNIT142 legacy Screen Open inline strings or GetP changed")

    def data_lines(a, b):
        return "".join(
            "    dc.b " + ",".join("$%02X" % x for x in whole[at:min(at+12,b)]) + "\n"
            for at in range(a, b, 12)
        )

    original = "L_UNIT142_0045A:\n" + data_lines(0x0045A, 0x00764)
    demand(wrapper.count(original) == 1,
           "UNIT142 legacy Screen Open original raw wrapper mismatch")
    replacement = (
        "L_UNIT142_0045A:\n" + data_lines(0x0045A, 0x00470)
        + '    include "M19_UNIT142_LEGACY_OPEN_HEAD_MC68020.s"\n'
        + "L_LEGACY_SCREEN_OPEN_00164:\n" + data_lines(0x005D4, 0x005E6)
        + "L_LEGACY_SCREEN_OPEN_00176:\n" + data_lines(0x005E6, 0x005F8)
        + '    include "M19_UNIT142_LEGACY_OPEN_HELPERS_MC68020.s"\n'
        + data_lines(0x00760, 0x00764)
    )
    wrapper = wrapper.replace(original, replacement)
    modules = []
    for spec, source in zip(LEGACY_OPEN_MODULES, sources):
        filename, blobpin, lo, hi, _symbol, _old, _new, _change = spec
        rawfile = (NATIVE_DIR / filename).read_bytes()
        gitblob = sha1(("blob %d\0" % len(rawfile)).encode("ascii") + rawfile).hexdigest()
        demand(gitblob == blobpin and rawfile.decode("ascii") == source,
               "UNIT142 legacy R83 authored module not emitter-exact: " + filename)
        modules.append((lo, hi, filename, source))
    demand(sum(hi-lo for lo,hi,_filename,_source in modules) == 716,
           "UNIT142 legacy Screen Open code coverage differs")
    return wrapper, modules


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
    # Private CBlock kernels: the pinned M18 source emitter is authoritative.
    from m18_cblock_copy_emit import emit_cblock_copy_core
    from generate_aga_multiunit_source import native_unit_source
    core, _core_labels = emit_cblock_copy_core()
    demand(len(core) == 872 and sha256(core).hexdigest() == CBLOCK_CORE_SHA,
           "UNIT142 CBlock native emitter drift")
    preview, coverage = native_unit_source("CBLOCK_CORE", core, [(0, 0)])
    demand(coverage["mnemonic_bytes"] == 872 and coverage["raw_dc_bytes"] == 0,
           "UNIT142 CBlock no longer fully source-decodable")
    index = preview.find("ENTRY_CBLOCK_CORE_00000:")
    demand(index >= 0, "UNIT142 CBlock ASM entry missing")
    body = preview[index:]
    demand(body.count("    moveq #0,d2") == 1, "UNIT142 CBlock edit ambiguous")
    for first, last in CBLOCK_SPANS:
        core_at = first + 8
        filename = "M19_UNIT142_CBLOCK_CORE_%05X_MC68020.s" % core_at
        symbol = "UNIT142_CBLOCK_%05X_RESULT" % core_at
        demand(whole[first:last] == b"AGACBLK " + core + b"GetP",
               "UNIT142 embedded CBlock source differs")
        header = (
            "; AGA_NATIVE_MIN_CPU: MC68020\n"
            "; UNIT142 CBlock core source-verified against the pinned M18 emitter.\n"
            + ("; UNIT142+$%05X..$%05X, 872 native instruction bytes.\n"
               % (core_at, last - 4))
            + (symbol + " equ 0\n\n")
        )
        renamed = body.replace("CBLOCK_CORE", "UNIT142_CORE_%05X" % core_at)
        code = header + renamed.replace("    moveq #0,d2",
                                        "    moveq #%s,d2" % symbol)
        sig = ("    dc.b $41,$47,$41,$43,$42,$4C,$4B,$20  ; +$%05X: 41474143424C4B20\n"
               % first)
        after = "ENTRY_UNIT142_%05X:\n" % last
        begin = audit.find(sig)
        end = audit.find(after, begin + len(sig))
        demand(begin >= 0 and end > begin,
               "UNIT142 embedded CBlock audit boundary mismatch")
        original = strip_annotations(audit[begin:end])
        demand(wrapper.count(original) == 1,
               "UNIT142 embedded CBlock wrapper boundary mismatch")
        replacement = (
            "    dc.b $41,$47,$41,$43,$42,$4C,$4B,$20\n"
            + ("L_UNIT142_%05X:\n" % core_at)
            + ('    include "%s"\n' % filename)
            + "    dc.b $47,$65,$74,$50\n"
        )
        wrapper = wrapper.replace(original, replacement)
        modules.append((core_at, last - 4, filename, code))
    # P0e object table: verify ORIGINAL Python emitter bytes, never infer
    # object semantics from the binary audit. Only its first 788 bytes are
    # executable; root (8) and 64 object slots (64x24) are zero DATA.
    from m19_p0e_object_table_emit import (
        ROOT_BYTES, MAX_OBJECTS, SLOT_BYTES, emit_object_table,
    )
    from generate_aga_multiunit_source import native_unit_source
    original, labels = emit_object_table()
    code_end = labels["object_root"]
    demand(len(original) == 2332 and code_end == 788
           and labels["object_table"] == code_end + ROOT_BYTES
           and original[code_end:] == bytes(ROOT_BYTES + MAX_OBJECTS * SLOT_BYTES),
           "UNIT142 P0e source table dimensions or zero data changed")
    demand(whole[0x0DD04:0x0DD04 + len(original)] == original
           and whole[0x0DCFC:0x0DD04] == b"AGAPIC  ",
           "UNIT142 P0e native source differs from exact P2d emitter")
    entries = [(i, labels[name]) for i, name in enumerate((
        "object_put_entry", "object_off_entry",
        "object_read_entry", "object_reset_entry",
    ))]
    candidate, coverage = native_unit_source(
        "P0E_OBJECT_CODE", original[:code_end], entries
    )
    demand(coverage["bytes"] == code_end
           and coverage["mnemonic_bytes"] == code_end
           and coverage["raw_dc_bytes"] == 0,
           "UNIT142 P0e source code not fully decoded into Motorola")
    entry = candidate.find("ENTRY_P0E_OBJECT_CODE_00000:")
    demand(entry >= 0, "UNIT142 P0e native entry absent")
    body = candidate[entry:]
    demand(body.count("    moveq #0,d2") == 1,
           "UNIT142 P0e object result ambiguous")
    filename = "M19_UNIT142_P0E_OBJECT_CORE_MC68020.s"
    symbol = "UNIT142_P0E_OBJECT_RESULT"
    header = (
        "; AGA_NATIVE_MIN_CPU: MC68020\n"
        "; UNIT142 P0e object table code source-verified against the exact historical emitter.\n"
        "; UNIT142+$0DD04..$0E018, 788 native instruction bytes.\n"
        + symbol + " equ 0\n\n"
    )
    module = header + body.replace("P0E_OBJECT_CODE", "UNIT142_P0E_OBJECT").replace(
        "    moveq #0,d2", "    moveq #" + symbol + ",d2"
    )
    first_marker = (
        "    dc.b $41,$47,$41,$50,$49,$43,$20,$20,$48,$E7,$EF,$EE"
        "  ; +$0DCFC: 414741504943202048E7EFEE\n"
    )
    begin = audit.find(first_marker)
    end_annotation = audit.find("  ; +$0E620: ", begin + len(first_marker))
    demand(begin >= 0 and end_annotation > begin,
           "UNIT142 P0e audit envelope boundaries missing")
    end = audit.rfind("\n", begin, end_annotation) + 1
    fragment = audit[begin:end]
    original_at = 0x0DCFC
    for line in fragment.splitlines():
        match = ANNOT.search(line)
        demand(match is not None
               and line.lstrip().startswith("dc.b")
               and int(match.group(1), 16) == original_at,
               "UNIT142 P0e mixed audit/data within source envelope")
        original_at += len(bytes.fromhex(match.group(2)))
    demand(original_at == 0x0E620,
           "UNIT142 P0e original source envelope not 2340 bytes")
    compact = strip_annotations(fragment)
    demand(wrapper.count(compact) == 1,
           "UNIT142 P0e raw wrapper fragment missing or ambiguous")
    replacement = (
        "    dc.b $41,$47,$41,$50,$49,$43,$20,$20\n"
        + ('    include "%s"\n' % filename)
        + "UNIT142_P0E_OBJECT_ROOT:\n"
        + "    dcb.b 8,0\n"
        + "UNIT142_P0E_OBJECT_TABLE:\n"
        + "    dcb.b 1536,0\n"
    )
    wrapper = wrapper.replace(compact, replacement)
    modules.append((0x0DD04, 0x0E018, filename, module))
    wrapper, aga_bridge = aga_bridge_expected_source(bytes(whole), wrapper)
    modules.append(aga_bridge)
    wrapper, p0f_modules = p0f_expected_source(bytes(whole),wrapper)
    modules.extend(p0f_modules)
    wrapper, p0f_bsr = p0f_external_bsr_sources(bytes(whole),wrapper)
    modules.extend(p0f_bsr)
    wrapper, p1cd = p1cd_open_expected_sources(bytes(whole),wrapper)
    modules.extend(p1cd)
    wrapper, legacy = legacy_r83_screen_sources(bytes(whole),wrapper)
    modules.extend(legacy)
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
    # The private CBlock core is embedded three times in UNIT142. Prove its
    # origin against the historical M18 Python emitter, not a disassembly.
    from m18_cblock_copy_emit import emit_cblock_copy_core
    cblock_core, _core_labels = emit_cblock_copy_core()
    cblock_spans = ((0x0ABC6, 0x0AF3A),
                    (0x0B58A, 0x0B8FE),
                    (0x0BF52, 0x0C2C6))
    cblock_expected = b"AGACBLK " + cblock_core + b"GetP"
    print("UNIT142_CBLOCK_SOURCE_PROBE", len(cblock_core),
          sha256(cblock_core).hexdigest(),
          "envelope", len(cblock_expected))
    demand(len(cblock_expected) == 884,
           "UNIT142 M18 CBlock core size unexpected; raw block kept intact")
    for lo, hi in cblock_spans:
        demand(native[lo:hi] == cblock_expected,
               "UNIT142 legacy CBlock emitter differs at $%05X" % lo)
    print("UNIT142_CBLOCK_PROVEN: three 884-byte core envelopes source-exact")
    for lo, hi, filename, source in modules:
        demand(groups[matches[0]][lo:hi] == native[lo:hi],
               "UNIT142 source slice mismatch: " + filename)
        demand((NATIVE_DIR / filename).read_text("ascii") == source,
               "UNIT142 editable source differs from pinned proof: " + filename)
    demand(WRAPPER.read_text("ascii") == wrapper,
           "UNIT142 native wrapper not derived exactly from pinned source")
    print("UNIT142_SOURCE_PROVEN: 56312 bytes / 137 MC68020 modules, AP20 group",
          matches[0], "unit", len(native))
    return matches[0]


def stage(folder, official):
    verify(official)
    (folder / STAGED_NAME).write_bytes(WRAPPER.read_bytes())
    for filename, *_ in SPANS:
        (folder / filename).write_bytes((NATIVE_DIR / filename).read_bytes())
    for first, _last in CBLOCK_SPANS:
        filename = "M19_UNIT142_CBLOCK_CORE_%05X_MC68020.s" % (first + 8)
        (folder / filename).write_bytes((NATIVE_DIR / filename).read_bytes())
    p0e_file = "M19_UNIT142_P0E_OBJECT_CORE_MC68020.s"
    (folder / p0e_file).write_bytes((NATIVE_DIR / p0e_file).read_bytes())
    (folder / "M19_UNIT142_P0E_AGA_BRIDGE_MC68020.s").write_bytes((NATIVE_DIR / "M19_UNIT142_P0E_AGA_BRIDGE_MC68020.s").read_bytes())
    (folder / "M19_UNIT142_P0F_STAMP_HEAD_MC68020.s").write_bytes((NATIVE_DIR / "M19_UNIT142_P0F_STAMP_HEAD_MC68020.s").read_bytes())
    (folder / "M19_UNIT142_P0F_STAMP_BODY_MC68020.s").write_bytes((NATIVE_DIR / "M19_UNIT142_P0F_STAMP_BODY_MC68020.s").read_bytes())
    (folder / "M19_UNIT142_P0F_BIND_CHECK_MC68020.s").write_bytes((NATIVE_DIR / "M19_UNIT142_P0F_BIND_CHECK_MC68020.s").read_bytes())
    (folder / "M19_UNIT142_P0F_BIND_RETURN_MC68020.s").write_bytes((NATIVE_DIR / "M19_UNIT142_P0F_BIND_RETURN_MC68020.s").read_bytes())
    (folder / "M19_UNIT142_P0F_BSR_PUT_MC68020.s").write_bytes((NATIVE_DIR / "M19_UNIT142_P0F_BSR_PUT_MC68020.s").read_bytes())
    (folder / "M19_UNIT142_P0F_BSR_READ_MC68020.s").write_bytes((NATIVE_DIR / "M19_UNIT142_P0F_BSR_READ_MC68020.s").read_bytes())
    for filename, *_rest in P1CD_PINNED_MODULES:
        (folder / filename).write_bytes((NATIVE_DIR / filename).read_bytes())
    for filename, *_rest in LEGACY_OPEN_MODULES:
        (folder / filename).write_bytes((NATIVE_DIR / filename).read_bytes())


def edit_gate(staged, assembler):
    official = (staged / "M19_P2D_ASM_REBUILT_CHECK.Lib").read_bytes()
    group = verify(official)
    demand((staged / STAGED_NAME).is_file() and
           (staged / MASTER_NAME).is_file() and
           all((staged / spec[0]).is_file() for spec in SPANS) and
           all((staged / ("M19_UNIT142_CBLOCK_CORE_%05X_MC68020.s" % (first + 8))).is_file()
               for first, _last in CBLOCK_SPANS) and
           (staged / "M19_UNIT142_P0E_OBJECT_CORE_MC68020.s").is_file() and
           (staged / "M19_UNIT142_P0E_AGA_BRIDGE_MC68020.s").is_file() and
           (staged / "M19_UNIT142_P0F_STAMP_HEAD_MC68020.s").is_file() and
           (staged / "M19_UNIT142_P0F_STAMP_BODY_MC68020.s").is_file() and
           (staged / "M19_UNIT142_P0F_BIND_CHECK_MC68020.s").is_file() and
           (staged / "M19_UNIT142_P0F_BIND_RETURN_MC68020.s").is_file() and
           (staged / "M19_UNIT142_P0F_BSR_PUT_MC68020.s").is_file() and
           (staged / "M19_UNIT142_P0F_BSR_READ_MC68020.s").is_file() and
           all((staged / filename).is_file() for filename, *_ in P1CD_PINNED_MODULES) and
           all((staged / filename).is_file() for filename, *_ in LEGACY_OPEN_MODULES),
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
        for first, _last in CBLOCK_SPANS:
            core_at = first + 8
            filename = "M19_UNIT142_CBLOCK_CORE_%05X_MC68020.s" % core_at
            symbol = "UNIT142_CBLOCK_%05X_RESULT" % core_at
            path = folder / filename
            text = path.read_text("ascii")
            original = symbol + " equ 0"
            demand(text.count(original) == 1,
                   "UNIT142 CBlock edit symbol ambiguous: " + filename)
            path.write_text(text.replace(original, symbol + " equ 1"),
                            encoding="ascii", newline="\n")
        p0e_file = folder / "M19_UNIT142_P0E_OBJECT_CORE_MC68020.s"
        p0e_source = p0e_file.read_text("ascii")
        p0e_before = "UNIT142_P0E_OBJECT_RESULT equ 0"
        demand(p0e_source.count(p0e_before) == 1,
               "UNIT142 P0e isolated edit symbol absent or ambiguous")
        p0e_file.write_text(p0e_source.replace(
            p0e_before, "UNIT142_P0E_OBJECT_RESULT equ 1"),
            encoding="ascii", newline="\n")
        bridge_file = folder / "M19_UNIT142_P0E_AGA_BRIDGE_MC68020.s"
        bridge_src = bridge_file.read_text("ascii")
        bridge_sym = "UNIT142_P0E_AGA_BRIDGE_RESULT equ 0"
        demand(bridge_src.count(bridge_sym) == 1,
               "UNIT142 P0e bridge edit symbol ambiguous")
        bridge_file.write_text(bridge_src.replace(
            bridge_sym, "UNIT142_P0E_AGA_BRIDGE_RESULT equ 1"), encoding="ascii", newline="\n")
        path = folder / "M19_UNIT142_P0F_STAMP_HEAD_MC68020.s"
        contents = path.read_text("ascii")
        before = "UNIT142_P0F_STAMP_HEAD_EDIT equ 0"
        demand(contents.count(before) == 1,
               "UNIT142 P0f edit symbol ambiguous: M19_UNIT142_P0F_STAMP_HEAD_MC68020.s")
        path.write_text(contents.replace(before, "UNIT142_P0F_STAMP_HEAD_EDIT equ 1"),
                        encoding="ascii", newline="\n")
        path = folder / "M19_UNIT142_P0F_STAMP_BODY_MC68020.s"
        contents = path.read_text("ascii")
        before = "UNIT142_P0F_STAMP_BODY_EDIT equ 48"
        demand(contents.count(before) == 1,
               "UNIT142 P0f edit symbol ambiguous: M19_UNIT142_P0F_STAMP_BODY_MC68020.s")
        path.write_text(contents.replace(before, "UNIT142_P0F_STAMP_BODY_EDIT equ 49"),
                        encoding="ascii", newline="\n")
        path = folder / "M19_UNIT142_P0F_BIND_CHECK_MC68020.s"
        contents = path.read_text("ascii")
        before = "UNIT142_P0F_BIND_CHECK_EDIT equ 0"
        demand(contents.count(before) == 1,
               "UNIT142 P0f edit symbol ambiguous: M19_UNIT142_P0F_BIND_CHECK_MC68020.s")
        path.write_text(contents.replace(before, "UNIT142_P0F_BIND_CHECK_EDIT equ 1"),
                        encoding="ascii", newline="\n")
        path = folder / "M19_UNIT142_P0F_BIND_RETURN_MC68020.s"
        contents = path.read_text("ascii")
        before = "UNIT142_P0F_BIND_RETURN_EDIT equ 0"
        demand(contents.count(before) == 1,
               "UNIT142 P0f edit symbol ambiguous: M19_UNIT142_P0F_BIND_RETURN_MC68020.s")
        path.write_text(contents.replace(before, "UNIT142_P0F_BIND_RETURN_EDIT equ 1"),
                        encoding="ascii", newline="\n")
        for filename,symbol in (("M19_UNIT142_P0F_BSR_PUT_MC68020.s","UNIT142_P0F_PUT_BSR_DELTA"),
                                ("M19_UNIT142_P0F_BSR_READ_MC68020.s","UNIT142_P0F_READ_BSR_DELTA")):
            path = folder / filename
            content = path.read_text("ascii")
            before = symbol + " equ 0"
            demand(content.count(before) == 1,
                   "UNIT142 P0f BSR symbol not unique: " + filename)
            path.write_text(content.replace(before,symbol + " equ 2"),
                            encoding="ascii",newline="\n")
        for filename, _hash, _lo, _hi, symbol in P1CD_PINNED_MODULES:
            path = folder / filename
            code = path.read_text("ascii")
            old = symbol + " equ 1"
            demand(code.count(old) == 1,
                   "UNIT142 P1c/P1d isolated edit symbol ambiguous: " + filename)
            path.write_text(code.replace(old, symbol + " equ 2"),
                            encoding="ascii", newline="\n")
        for filename, _blob, _lo, _hi, symbol, old, new, _diff in LEGACY_OPEN_MODULES:
            path = folder / filename
            text = path.read_text("ascii")
            before = symbol + " equ " + str(old)
            demand(text.count(before) == 1, "UNIT142 legacy Open edit ambiguous: "+filename)
            path.write_text(text.replace(before, symbol + " equ " + str(new)),
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
        expected.update({first + 8 + 869: (0, 1) for first, _last in CBLOCK_SPANS})
        expected[0x0E015] = (0, 1)
        expected[0x0E7F3] = (0, 1)
        expected[0x0E7FF] = (0, 1)
        expected[0x0E925] = (48, 49)
        expected[0x0EB7B] = (0, 1)
        expected[0x0ECA1] = (0, 1)
        expected[0x0EB27] = (0xDE, 0xE0)
        expected[0x0EBF1] = (0xBC, 0xBE)
        expected[0x0F0B1] = (1, 2)
        expected[0x0F4EF] = (1, 2)
        expected[0x0047D] = (0, 1)
        expected[0x005FF] = (1, 2)
        demand(len(expected) == 137, "UNIT142 R83 legacy Open edit count differs")
        demand(deltas == sorted(expected) and
               all((base[i], changed[i]) == pair
                   for i, pair in expected.items()),
               "UNIT142 isolated one-byte edits escaped expected offsets")
    print("UNIT142_EDIT_TEST_PASS: 137 exact bytes, only UNIT142, no AP20 drift")


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
