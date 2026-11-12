#!/usr/bin/env python3
"""M17/R58 V2 Gate A before publishing the single official candidate binary.

Uses original verified R57 builder, real AP20 tokens, full SHA/padding checks,
and Unicorn M68000 execution of the FAR entry at native offset 40000.
Does not write a binary. NOT a substitute for Gate B/C in WinUAE.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from

from audit_ap20 import inspect, parse
from build_m17_r57_rastport import build as build_r57
from build_m17_r58_compiler_bridge import (
    FAR_ENTRY_INDEX, FAR_NATIVE_OFFSET, FAR_PROBE, BRIDGE_ENTRY_INDEX, build,
)
from compiler_bridge_v2_probe import DISPATCH_V2, unwrap_native_parts_v2
from compiler_relocation import unpack_ap20, unwrap_native_parts
from test_compiler_bridge_v2_probe import emulate


def run() -> None:
    binary, info = build()
    assert build()[0] == binary
    r57, _ = build_r57()
    tok57, native57 = unwrap_native_parts(r57)
    tok58, native58 = unwrap_native_parts_v2(binary)
    assert len(native57) == 59 and len(native58) == 61
    assert native58[:59] == native57, "all R57 native instructions preserved exactly"
    assert len(native58[59]) == 40000-30748 and not any(native58[59])
    assert native58[60] == FAR_PROBE
    assert tok57[2:] == tok58[2:] and tok57[:2] != tok58[:2], "only Aga Probe index may change"
    assert unpack_from(">H", tok58, 6)[0] == FAR_ENTRY_INDEX
    tokens, entries, _title = unpack_ap20(binary)
    assert tokens == tok58 and len(entries) == 62
    assert len(entries[-1]) == 40000 + len(FAR_PROBE) + 34
    assert entries[-1][:34] == DISPATCH_V2
    assert unpack_from(">H", entries[FAR_ENTRY_INDEX], 2)[0] == BRIDGE_ENTRY_INDEX
    assert unpack_from(">H", entries[FAR_ENTRY_INDEX], 4)[0] == FAR_NATIVE_OFFSET
    assert inspect(parse(binary))["issues"] == []
    # Model AMOS Compiler's Rbsr as both possible far routine link types.
    # The 68000 executes the real 40000-byte output, including V2 dispatcher.
    close = bytes.fromhex("61000006") + pack(">H", FAR_NATIVE_OFFSET) + b"\x4e\x75\x4e\x71"
    emulate(close, entries[-1], FAR_NATIVE_OFFSET, absolute=False)
    far = b"\x4e\xb9" + pack(">I", 0x100000) + pack(">H", FAR_NATIVE_OFFSET) + b"\x4e\x75"
    emulate(far, entries[-1], FAR_NATIVE_OFFSET, absolute=True)
    print("R58 V2 ACTUAL M68000 40K PROBE PASS: BSR/JSR, D3=99, D2=0, ABI, stack", flush=True)
    print("R57 ALL 59 NATIVE ENTRIES IDENTICAL; AP20 53 TOKENS; SHA", info["sha256"], flush=True)
    print("R58 GATE B/C WINUAE NOT YET TESTED", flush=True)


if __name__ == "__main__":
    run()
