#!/usr/bin/env python3
"""OPT020/P2 Gate A: reuse P1e painter in the *actual* R46 Image Draw entry.

Native Musashi 68EC020/68020 runs old DATA/AGAPIC RLE+Safe+Intuition preflight
with BFINS painting of the full image, preserving R46 Start/Length/X/Y/Mode.
CPU 68000 refuses before any 020 instruction. In-memory Compiler V2 ONLY.
No second active ASC, binary, WinUAE result or AMOS Compiler is created.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack_into, unpack_from

from machine68k import CPUType
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

from audit_ap20 import inspect, parse
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from m16_agapic import pack_image
from m16_agapic_sample import sample
from m16_image_draw_r45_emit import ENTRY_INDEX, emit_image_draw, F, F020
from test_opt020_p1e_region import LiveRegionCPU

ROOT = Path(__file__).resolve().parents[1]
R69_SHA = "9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"
R70_SHA = "fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"
R71_SHA = "1f4cdaabcc0e4ec641b1a60aec06e780187d66b7aaef172131fc7a7011ec85b0"
R72_SHA = "fdb98db259618fbdc3802843e2d6e836cb64acf2d68dc50bbe1133d46d36e67b"
R68_SHA = "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"


def check(native, blob, depth, *, x, y, mode, front=0, flag=0,
          cpu_type=CPUType.M68020, attnflags=2, pending=0,
          safe_ready=True, expect_ok=True, source_len=None,
          source_start=None, invalid_mem_at=0, w=17, h=7, stride=12,
          screen_width=64, screen_height=42):
    m = LiveRegionCPU(
        cpu_type, native, blob, base=0x1c000, depth=depth,
        screen_width=screen_width, screen_height=screen_height, stride=stride,
        front=front, bank_flag=flag, pending=pending,
        safe_ready=safe_ready, attnflags=attnflags,
        invalid_mem_at=invalid_mem_at, draw_api=True,
    )
    try:
        m.run(x=x, y=y, mode=mode, sx=0, sy=0, w=w, h=h,
              source_len=source_len, source_start=source_start,
              expect_ok=expect_ok)
        assert m.bank_calls == 0, "Image Draw must not call Bnk.GetAdr"
    finally:
        m.close()


def v2_check(native):
    path = ROOT / "dist/AMOSPro_AGA.Lib"
    protected_path = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
    active = path.read_bytes()
    protected = protected_path.read_bytes()
    actual_sha = sha256(active).hexdigest()
    assert actual_sha in (R69_SHA, R70_SHA, R71_SHA, R72_SHA), "Unrecognized active P1e/P2 candidate"
    assert sha256(protected).hexdigest() == R68_SHA, "R68 LAST_GOOD changed"
    old, labels = emit_image_draw(accept_loaded_flags_zero=True)
    assert emit_image_draw(accept_loaded_flags_zero=True)[0] == old
    assert not any(n.startswith("p1e_") for n in labels)
    if actual_sha == R70_SHA:
        from build_opt020_p2_r70 import build as build_r70
        assert active == build_r70()[0], "Installed R70 differs from deterministic source"
        from build_opt020_p1e_r69 import build as build_r69
        baseline = build_r69()[0]  # Historical Image Draw core for isolated P2
    elif actual_sha == R72_SHA:
        from build_opt020_p2_r72 import build as build_r72
        from build_opt020_p1e_r69 import build as build_r69
        from native_relative_links import assert_native_links
        assert active == build_r72()[0], "Installed R72 differs from deterministic source"
        assert_native_links(unwrap_native_parts_v2(active)[1])
        baseline = build_r69()[0]
    elif actual_sha == R71_SHA:
        from build_opt020_p2_r71 import build as build_r71
        from build_opt020_p1e_r69 import build as build_r69
        assert active == build_r71()[0], "Installed R71 differs from deterministic source"
        baseline = build_r69()[0]
    else:
        baseline = active
    tokens, parts = unwrap_native_parts_v2(baseline)
    assert len(parts) == 70 and parts[ENTRY_INDEX] == old + GETP
    trial = list(parts)
    trial[ENTRY_INDEX] = native + GETP
    # Do not change the public API, even when building the probe in memory.
    _, _, title = unpack_ap20(baseline)
    repacked = repack_ap20(baseline, tokens, trial, title)
    compiler = wrap_native_ap20_v2(repacked, title)
    assert unwrap_native_parts_v2(compiler) == (tokens, trial)
    tt, entry, t = unpack_ap20(compiler)
    assert tt == tokens and t == title and len(entry) == 71
    assert entry[-1] and len(entry[-1]) < 65534
    assert all(a == b for i, (a, b) in enumerate(zip(parts, trial))
               if i != ENTRY_INDEX)
    issues = inspect(parse(compiler))
    assert not issues["issues"], issues["issues"]
    assert len([c for c in issues["tokens"] if c["name"].startswith("aga ")]) == 64
    assert any(p["index"] == ENTRY_INDEX and p["parameters"] == 5 and p["getp"]
               for p in issues["parameter_checks"])
    assert path.read_bytes() == active and protected_path.read_bytes() == protected
    return len(compiler), len(entry[-1])


def main():
    historical, _ = emit_image_draw(accept_loaded_flags_zero=True)
    original, _ = emit_image_draw()
    native, labels = emit_image_draw(accept_loaded_flags_zero=True, opt020=True)
    assert native != historical and native != original
    assert {"paint_group", "paint_done", "p1e_clip_x", "p1e_full_16",
            "p1e_fragment", "success", "reject"} <= set(labels)
    assert len(native) < 6000 and len(native) % 2 == 0
    assert F020["srcx"] == 128 and F020["regionh"] == 140
    assert max(F.values()) == 124
    disasm = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
                  .disasm(native, 0))
    assert sum(item.size for item in disasm) == len(native), "020 code undecodable"
    assert any(item.mnemonic.startswith("bfins") for item in disasm)
    assert not any(item.mnemonic in ("illegal", "trap", "bkpt", "dc.w")
                   for item in disasm)
    v2_bytes, mono_bytes = v2_check(native)

    cases = 0
    coords = ((0, 0), (1, 1), (-7, -2), (50, 32), (63, 41),
              (64, 8), (9, 42), (-40, -40), (7, 19))
    for depth in (1, 2, 4, 8):
        w, h = 17, 7
        pixels = bytes(((i * 11 + j * 7) ^ (i >> 2)) & ((1 << depth) - 1)
                       for j in range(h) for i in range(w))
        mask = bytes(int((i + j * 3) % 5 != 0)
                     for j in range(h) for i in range(w))
        for masked in (False, True):
            blob = pack_image(w, h, depth, pixels, mask if masked else None)
            for front in (0, 1):
                modes = (0, 1) if masked else (0,)
                for mode in modes:
                    for n, (x, y) in enumerate(coords):
                        flag = (0, 1, 3)[(n + depth + int(masked)) % 3]
                        kind = (CPUType.M68020, CPUType.M68EC020)[n % 2]
                        check(native, blob, depth, x=x, y=y, front=front,
                              mode=mode, flag=flag, cpu_type=kind, w=w, h=h)
                        cases += 1
    # REAL 64x40x4 AGAPIC bank, same 1836-byte DATA payload and positions
    # as the R70 WinUAE ASC. Earlier 17x7 synthetic tests cannot catch
    # group-per-row/real-bank/physical-screen edge or nested-RTS failures.
    actual_bank, _, _ = sample()
    assert len(actual_bank) == 1836
    for mode, x, y in (
        (0, 18, 20), (1, 108, 20), (1, 197, 22),
        (1, -15, 196), (0, 291, 182), (1, 256, -17),
        (1, 105, 241), (0, 320, 256),
    ):
        check(native, actual_bank, 4, x=x, y=y, mode=mode,
              w=64, h=40, stride=40, screen_width=320,
              screen_height=256, flag=0)
        cases += 1
        print("P2 ACTUAL AGAPIC 64x40 PASS:", mode, x, y, flush=True)
    print("P2 actual full-size bank/WinUAE positions CPU PASS", flush=True)
    blob = pack_image(17, 7, 4, bytes((i * 3) & 15 for i in range(119)),
                      bytes((i % 7) != 0 for i in range(119)))
    for flag in (0, 1, 3):
        for pending, ready, success in ((0, False, True),
                                        (1, False, False),
                                        (3, True, True),
                                        (3, False, False)):
            check(native, blob, 4, x=1, y=2, mode=1, flag=flag,
                  pending=pending, safe_ready=ready, expect_ok=success)
            cases += 1
    # Illegal CPU must reject *before* the first 020 operation.
    for kind, attn in ((CPUType.M68000, 0), (CPUType.M68020, 0)):
        check(native, blob, 4, x=0, y=0, mode=1,
              cpu_type=kind, attnflags=attn, pending=3, expect_ok=False)
        cases += 1
    for flag in (2, 4, 0xffff):
        check(native, blob, 4, x=0, y=0, mode=1,
              flag=flag, pending=3, expect_ok=False)
        cases += 1
    for length in (0, 20, len(blob) + 16):
        check(native, blob, 4, x=0, y=0, mode=1,
              source_len=length, pending=3, expect_ok=False)
        cases += 1
    for start in (0, 0xc0001):
        check(native, blob, 4, x=0, y=0, mode=1,
              source_start=start, expect_ok=False)
        cases += 1
    for mode in (2, 0xffffffff):
        check(native, blob, 4, x=0, y=0, mode=mode, expect_ok=False)
        cases += 1
    for bad_at in (1, 2):
        check(native, blob, 4, x=0, y=0, mode=1,
              invalid_mem_at=bad_at, expect_ok=False)
        cases += 1

    # Strict RLE PASS 0: refuse corrupt packets without polling Safe.
    from struct import pack_into
    corruptions = (
        lambda b: b.__setitem__(0, 0),
        lambda b: pack_into(">H", b, 6, 2),
        lambda b: pack_into(">H", b, 16, 9),
        lambda b: pack_into(">I", b, 24, 0),
        lambda b: pack_into(">I", b, 28, len(b) + 1),
        lambda b: pack_into(">I", b, 32, 0),
    )
    for mutate in corruptions:
        broken = bytearray(blob)
        mutate(broken)
        check(native, bytes(broken), 4, x=0, y=0, mode=1,
              pending=3, expect_ok=False)
        cases += 1

    print("OPT020/P2 Image Draw real R46 preflight + P1e BFINS CPU Gate A PASS:",
          cases, "native CPU020 runs, 68000 safe refusal, 1/2/4/8 planes,")
    print("opaque/masked, x/y clip, DATA 0/1/3, Safe, invalid RLE, AP20 ABI.")
    print("Legacy R46 68000 emitter remains byte-identical (historical CI).")
    print("Compiler V2 memory-only:", v2_bytes, "bytes, mono", mono_bytes)
    print("Native byte count:", len(native), "SHA256:", sha256(native).hexdigest())
    print("NO candidate/lib/ASC updated; no WinUAE benchmark or AMOS Compiler.")


if __name__ == "__main__":
    main()
