#!/usr/bin/env python3
"""R70 regression trap and R71 AP20/CPU-flow branch-target gate (read only).

The original 256 Musashi tests execute entry 55 directly and cannot catch
Clear -> Fill -> helper or the number-bank wrappers.  These binary-level
tests reject the exact historical R70 and deliberately corrupted R71 edges.
They do not assert a WinUAE/AMOS runtime PASS.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack_into

from build_opt020_p1e_r69 import build as build_r69
from build_opt020_p2_r70 import build as build_r70
from build_opt020_p2_r71 import R71_SHA, build as build_r71
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from native_relative_links import LINKS, assert_native_links, link_positions, relink_native_parts

ROOT = Path(__file__).resolve().parents[1]


def expect_failure(parts: list[bytes], fragment: str) -> None:
    try:
        assert_native_links(parts)
    except AssertionError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"Broken native link accepted: {fragment}")


def main() -> None:
    before = (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes()
    protected = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(protected).hexdigest() == (
        "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
    )
    r69, _ = build_r69()
    r70, _ = build_r70()
    r71, meta = build_r71()
    assert sha256(r71).hexdigest() == R71_SHA and r71 == build_r71()[0]
    t69, p69 = unwrap_native_parts_v2(r69)
    t70, p70 = unwrap_native_parts_v2(r70)
    t71, p71 = unwrap_native_parts_v2(r71)
    assert t69 == t70 == t71 and len(p69) == len(p70) == len(p71) == 70

    # The R69 helper target is correct; old bank wrappers target GetP -2.
    old = [link_positions(p69, link) for link in LINKS]
    assert [(a, e) for a, e, _ in old] == [
        (30128, 30128), (26058, 26060), (21088, 21090)
    ], old
    bad = [link_positions(p70, link) for link in LINKS]
    assert [(a, e) for a, e, _ in bad] == [
        (30128, 30350), (26280, 26060), (21310, 21090)
    ], bad
    expect_failure(p70, "Fill -> RasterPort helper")

    assert relink_native_parts(p70) == p71
    assert relink_native_parts(p71) == p71, "Relink must be idempotent"
    assert_native_links(p71)
    assert [link_positions(p71, link)[:2] for link in LINKS] == [
        (30350, 30350), (26060, 26060), (21090, 21090)
    ]
    modified = {i for i, (a, b) in enumerate(zip(p69, p71)) if a != b}
    assert modified == {20, 55, 57, 58}, modified
    assert p69[59] == p71[59], "P1e Region unexpectedly changed"
    assert all(p69[i] == p71[i] for i in range(70) if i not in modified)

    # Fault injection: a change of one extension word must fail closed.
    for link in LINKS:
        mutated = list(p71)
        patch = bytearray(mutated[link.source_entry])
        at = link.source_offset + 2
        disp = int.from_bytes(patch[at:at + 2], "big", signed=True)
        pack_into(">h", patch, at, disp - 2)
        mutated[link.source_entry] = bytes(patch)
        expect_failure(mutated, link.name)
        # Patch function must repair exactly the injected fault.
        assert relink_native_parts(mutated) == p71

    assert (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes() == before
    assert (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes() == protected
    if sha256(before).hexdigest() == R71_SHA:
        assert before == r71, "Installed R71 differs from deterministic builder"
    print("OPT020/P2 R71 BRANCH GATE A PASS: 3 destinations, old R70 rejected,")
    print("3 mutated branch words rejected, corrected 70-native-entry V2 exact.")
    print("NO WinUAE Gate B or AMOS Compiler Gate C performed.", meta)


if __name__ == "__main__":
    main()
