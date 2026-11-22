#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Validate that residual BOBS dc.b sequences are identified data only."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/native/m19_p2d/M19_P2D_BOBS_EDITABLE.s"
RAW_START = re.compile(r"^\s*dc\.b\b", re.IGNORECASE)
RAW_LINE = re.compile(
    r"^\s*dc\.b\s+([^;]+?)\s*;\s*\+\$([0-9A-F]{5}):\s*([0-9A-F]+)\s*$",
    re.IGNORECASE,
)
EXPECTED = (
    (0x020A2, 0x020CE),  # active bank and canonical AGBO image
    (0x03772, 0x03792),  # pixel masks
    (0x046CC, 0x046D4),  # registry state
    (0x06D36, 0x06D4E),  # frame-guard state
    (0x07E1C, 0x07E20),  # P1d drawing ID
    (0x0C4FE, 0x0C51E),  # P2d scratch
    (0x0DA10, 0x0DA30),  # P2d service state
    (0x0E5B0, 0x0E5C8),  # P2d mode
)
OPCODES = (
    ("nop", 0x068FE, "4E71"),
    ("nop", 0x06900, "4E71"),
    ("rts", 0x071EC, "4E75"),
)


class InventoryError(ValueError):
    pass


def collect(text: str) -> tuple[tuple[int, int], ...]:
    result: list[list[int]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not RAW_START.match(line):
            continue
        hit = RAW_LINE.fullmatch(line)
        if not hit:
            raise InventoryError(f"unannotated dc.b line {number}")
        arguments, at, raw_hex = hit.groups()
        try:
            values = bytes(int(x.strip().removeprefix("$"), 16)
                           for x in arguments.split(","))
            expected = bytes.fromhex(raw_hex)
        except ValueError as exc:
            raise InventoryError(f"invalid dc.b line {number}") from exc
        if not expected or values != expected:
            raise InventoryError(f"byte mismatch in dc.b line {number}")
        first, last = int(at, 16), int(at, 16) + len(expected)
        if result and first < result[-1][1]:
            raise InventoryError(f"overlapping dc.b offset 0x{first:05X}")
        if result and first == result[-1][1]:
            result[-1][1] = last
        else:
            result.append([first, last])
    return tuple(tuple(pair) for pair in result)


def check(text: str) -> None:
    got = collect(text)
    if got != EXPECTED:
        raise InventoryError(f"unexpected BOBS data ranges: {got!r}")
    for mnemonic, offset, opcode in OPCODES:
        pattern = (
            r"^\s*%s\s+;\s*\+\$%05X:\s*%s\s*$"
            % (mnemonic, offset, opcode)
        )
        if len(re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)) != 1:
            raise InventoryError(
                f"missing/duplicate {mnemonic} at 0x{offset:05X}"
            )
    size = sum(b - a for a, b in got)
    if size != 200:
        raise InventoryError(f"BOBS data size changed to {size}")
    print("BOBS_RAW_DATA_ONLY_PASS: 200 data bytes; 2 NOP + RTS decoded")


def self_test() -> None:
    good = (
        "    dc.b $00,$01 ; +$00010: 0001\n"
        "    dc.b $02 ; +$00012: 02\n"
        "    nop ; +$00013: 4E71\n"
        "    dc.b $03 ; +$00020: 03\n"
    )
    if collect(good) != ((0x10, 0x13), (0x20, 0x21)):
        raise InventoryError("scanner failed to identify data islands")
    for bad in (
        "    dc.b $00,$02 ; +$00010: 0001\n",
        "    dc.b $00,$01\n",
        "    dc.b $00 ; +$00010: 00\n"
        "    dc.b $01 ; +$0000F: 01\n",
    ):
        try:
            collect(bad)
        except InventoryError:
            continue
        raise InventoryError("scanner accepted corrupt input")
    print("BOBS_RAW_INVENTORY_SELF_TEST_PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--check", action="store_true")
    choice.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            check(SOURCE.read_text(encoding="ascii"))
        return 0
    except (InventoryError, OSError) as error:
        print("[ERROR] " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
