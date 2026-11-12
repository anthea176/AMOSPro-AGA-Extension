#!/usr/bin/env python3
"""M17/R59 read-only compact V2 Gate A (not AMOS WinUAE Gate B/C).

R57 native code, public tokens and AP20 stubs must remain byte identical.
R58 is retained as the historical, user-tested 40K far-probe evidence.
The actual R59 V2 dispatcher is exercised on M68000 with BSR/JSR.
"""
from __future__ import annotations
from hashlib import sha256
from struct import pack, unpack_from
from audit_ap20 import inspect, parse
from build_m17_r57_rastport import build as build_r57
from build_m17_r58_compiler_bridge import build as build_r58, FAR_PROBE
from build_m17_r59_compact_v2 import build as build_r59, R59_TITLE
from compiler_bridge_v2_probe import DISPATCH_V2, unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import repack_ap20, unpack_ap20, unwrap_native_parts
from test_compiler_bridge_v2_probe import emulate

R58_SHA = "c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b"
R57_SHA = "aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0"


def run() -> None:
    r57, _ = build_r57()
    r58, _ = build_r58()
    r59, meta = build_r59()
    assert build_r59()[0] == r59
    assert sha256(r57).hexdigest() == R57_SHA
    assert sha256(r58).hexdigest() == R58_SHA
    assert r59 not in (r57, r58)
    token57, native57 = unwrap_native_parts(r57)
    token58, native58 = unwrap_native_parts_v2(r58)
    token59, native59 = unwrap_native_parts_v2(r59)
    assert len(native57) == len(native59) == 59
    assert len(native58) == 61 and native58[:59] == native57
    assert len(native58[59]) == 9252 and not any(native58[59])
    assert native58[60] == FAR_PROBE
    assert token59 == token57, "R59 must restore original Aga Probe mapping"
    assert token58 != token57, "R58 diagnostic redirection must be absent"
    assert native59 == native57, "R59 must preserve all R57 native routines"
    tok57, entries57, _ = unpack_ap20(r57)
    tok59, entries59, title59 = unpack_ap20(r59)
    assert tok57 == tok59 and title59 == R59_TITLE
    assert len(entries57) == len(entries59) == 60
    assert entries59[:-1] == entries57[:-1], "Every AP20 stub must be identical"
    assert entries59[-1] == DISPATCH_V2 + entries57[-1][32:]
    assert len(entries59[-1]) == 30782
    assert meta["native_bytes"] == 30748 and meta["padding_bytes"] == 0
    assert meta["ap20_entries"] == 60 and meta["public_commands"] == 53
    assert inspect(parse(r59))["issues"] == []

    # Temporary in-memory-only small NOP/RTS helper at a real R57 offset.
    probe_index = max(i for i, part in enumerate(native57)
                      if len(part) >= 4 and not (len(part) & 1))
    start = sum(map(len, native57[:probe_index]))
    parts = native57.copy()
    parts[probe_index] = bytes.fromhex("4e714e75") + bytes.fromhex("4e71") * (
        (len(parts[probe_index]) - 4) // 2)
    synthetic = wrap_native_ap20_v2(
        repack_ap20(r57, token57, parts, R59_TITLE), R59_TITLE)
    bridge = unpack_ap20(synthetic)[1][-1]
    assert len(bridge) == 30782
    assert unpack_from(">H", unpack_ap20(synthetic)[1][probe_index], 4)[0] == start
    rel = bytes.fromhex("61000006") + pack(">H", start) + bytes.fromhex("4e754e71")
    emulate(rel, bridge, start, absolute=False, expected_d3=0)
    abs_call = bytes.fromhex("4eb9") + pack(">I", 0x100000) + pack(">H", start) + bytes.fromhex("4e75")
    emulate(abs_call, bridge, start, absolute=True, expected_d3=0)
    print("R59 COMPACT V2 GATE A PASS: R57 native code, 53 tokens, 60 AP20 entries,")
    print("no padding, BSR/JSR 68000 stack and registers PASS", flush=True)
    print("R59 GATES B/C WINUAE NOT TESTED (requires new executable)", flush=True)


if __name__ == "__main__":
    run()
