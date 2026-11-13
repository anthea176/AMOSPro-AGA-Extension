#!/usr/bin/env python3
"""OPT020/P1c real Musashi 68EC020/68020 RLE/clip validation.

Packet decoding AND horizontal/vertical span decisions are Motorola
machine code. P1b BFINS draws fully visible groups on the same native
CPU family. Python only orchestrates, prevalidates format, and paints
bounded fragments; this is NOT an AP20/WinUAE/Compiler Gate.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from random import Random

from capstone import CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020, Cs
from machine68k import CPUType

from m16_agapic import pack_image, parse_payload
from opt020_p1c_rle_clip_emit import (
    emit_rle_row_020, emit_clip_x_020, emit_clip_y_020)
from opt020_p1c_native_runner import RealNativeRLEClip
from opt020_p1c_region import draw_native_plan
from test_opt020_p1b_native import make_atlas
from test_m18_agapic_atlas_model import as_planar, reference


def check_instruction_streams():
    result = {}
    for name, emit in (
        ("RLE", emit_rle_row_020),
        ("CLIP_X", emit_clip_x_020),
        ("CLIP_Y", emit_clip_y_020),
    ):
        blob = emit()
        instructions = list(
            Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020).
            disasm(blob, 0x1000))
        names = [ins.mnemonic.lower().split(".", 1)[0] for ins in instructions]
        assert sum(ins.size for ins in instructions) == len(blob), (
            "invalid 68020 instruction", name, blob.hex(), names)
        assert names.count("rts") >= 1
        assert "cmp" in names and "sub" in names if name != "CLIP_Y" else "sub" in names
        if name == "RLE":
            assert "mulu" in names and "adda" in names, names
            assert names.count("rts") == 2
        if name == "CLIP_X":
            assert names.count("rts") == 2
        result[name] = (len(blob), sha256(blob).hexdigest())
    return result


def check_rle_decoder(native):
    rng = Random(0x198020)
    valid = 0
    for depth in (1, 2, 4, 8):
        for masked in (False, True):
            for width in (1, 16, 17, 33, 65, 257, 4096):
                h = 3 if width < 257 else 1
                # Repeating consecutive groups and literals across rows.
                pixels = bytes((x % 16 + y * 3) % (1 << depth)
                               for y in range(h) for x in range(width))
                mask = (bytes((x + y * 2) % 5 != 0
                              for y in range(h) for x in range(width))
                        if masked else None)
                img = parse_payload(pack_image(width, h, depth, pixels, mask))
                for row in range(h):
                    start, stop = img.offsets[row:row + 2]
                    got = native.decode_row(img.raw[start:stop],
                                            img.group_bytes, img.groups_per_row)
                    expected = tuple(img.row_groups(row))
                    assert got == expected, (
                        "native row decode differs from independent AGAPIC",
                        native.kind, width, depth, masked, row)
                    valid += 1

    group = bytes.fromhex("f000aa5500ff")
    samples = (
        (b"", 1, 6),
        (b"\x00" + group[:-1], 1, 6),      # literal truncated
        (b"\x80" + group[:-1], 1, 6),      # repeat truncated
        (b"\xff" + group, 1, 6),          # count 128 > row 1
        (b"\x00" + group + b"\xff", 1, 6), # trailing garbage
        (b"\x02" + group * 2, 3, 6),      # literal requires 3
        (b"\x81" + group, 1, 6),          # repeat count 2 > 1
        (b"\x80" + group, 0, 6),          # group count zero
        (b"\x80" + group, 257, 6),        # max group count exceeded
        (b"\x80" + group, 1, 0),          # invalid byte size
        (b"\x80" + group, 1, 1),
        (b"\x80" + group, 1, 19),
        (b"\x80" + group, 1, 20),
    )
    rejected = 0
    for row, count, size in samples:
        answer = native.decode_row(row, size, count, expect_valid=False)
        assert answer is None
        rejected += 1
    return valid, rejected


def check_native_clipping(native):
    x_tests = y_tests = 0
    for source_w in (1, 17, 33, 65):
        for sx in sorted({0, min(3, source_w - 1), source_w - 1}):
            for right in sorted({sx + 1, source_w}):
                for gx in range(0, source_w, 16):
                    for x in (-65, -16, -1, 0, 5, 65):
                        for dw in (1, 17, 57):
                            left = max(gx, sx, sx - x)
                            end = min(gx + 16, right, source_w, sx + dw - x)
                            expected = ((left - gx, end - gx)
                                        if left < end else (0, 0))
                            got = native.clip_x(gx, sx, right, x, dw, source_w)
                            assert got == expected, (
                                "native X clip mismatch", native.kind,
                                gx, sx, right, x, dw, expected, got)
                            x_tests += 1
    for sy in (0, 3, 10):
        for source_y in (0, 3, 10, 16, 30):
            for y in (-50, -1, 0, 5, 32767):
                for sh in (1, 22):
                    dest_y = source_y - sy + y
                    expect_visible = 0 <= dest_y < sh
                    visible, got_y = native.clip_y(source_y, sy, y, sh)
                    assert visible == expect_visible
                    if visible:
                        assert got_y == dest_y
                    y_tests += 1
    return x_tests, y_tests


def check_full_region(native):
    rng = Random(0x199020)
    tests = nat = frag = rows = 0
    for depth in (1, 2, 4, 8):
        for masked in (False, True):
            img, pix, mask = make_atlas(depth, masked)
            for rect in ((0, 0, 65, 11), (3, 1, 47, 8),
                         (16, 2, 32, 7)):
                for x, y in ((0, 0), (1, 3), (5, -2),
                             (-19, 1), (36, 8), (57, 22)):
                    for mode in ((0, 1) if masked else (0,)):
                        background = bytes(
                            rng.randrange(1 << depth)
                            for _ in range(57 * 22))
                        planes, stride = as_planar(background, 57, 22, depth)
                        predicted, count = reference(
                            background, 57, 22, pix, mask,
                            img.width, rect, x, y, mode)
                        target, _ = as_planar(predicted, 57, 22, depth)
                        old = native.write_calls
                        result = draw_native_plan(
                            img, *rect, x, y, planes, 57, 22, mode,
                            native.write_group, native, stride)
                        assert result.pixels == count
                        assert result.native_groups == native.write_calls - old
                        assert planes == target, (
                            "full planar mismatch", native.kind, depth,
                            masked, rect, x, y, mode, result)
                        assert all(p[-12:] == bytes([0xa5] * 12)
                                   for p in planes), "guard modified"
                        tests += 1
                        nat += result.native_groups
                        frag += result.fallback_pixels
                        rows += result.decoded_rows
    assert nat > 0 and frag > 0 and rows > 0
    return tests, nat, frag, rows


def check_safe_preflight(native):
    img, pix, _ = make_atlas(8, False)
    planes, stride = as_planar(bytes([42] * (57 * 22)), 57, 22, 8)
    corrupt = replace(img, raw=img.raw[:-1])
    invalid_cases = [
        (img, (-1, 0, 8, 4, 0, 0, 0)),
        (img, (64, 0, 2, 1, 0, 0, 0)),
        (img, (0, 0, 0, 4, 0, 0, 0)),
        (img, (0, 0, 16, 4, 0, 0, 1)),
        (img, (0, 0, 16, 4, 32768, 0, 0)),
        (replace(img, depth=7), (0, 0, 16, 4, 0, 0, 0)),
        (corrupt, (0, 0, 16, 4, 0, 0, 0)),
    ]
    rejects = 0
    for image, args in invalid_cases:
        before = [bytes(p) for p in planes]
        count = (native.row_calls, native.clip_x_calls, native.clip_y_calls)

        def forbidden(*unused):
            raise AssertionError("draw attempted on invalid data")
        try:
            draw_native_plan(image, *args[:6], planes, 57, 22, args[6],
                             forbidden, native, stride)
        except ValueError:
            assert [bytes(p) for p in planes] == before
            assert count == (native.row_calls, native.clip_x_calls,
                             native.clip_y_calls)
            rejects += 1
        else:
            raise AssertionError("invalid data accepted")
    return rejects


def main():
    kernels = check_instruction_streams()
    summary = []
    for cpu in (CPUType.M68EC020, CPUType.M68020):
        native = RealNativeRLEClip(cpu)
        try:
            dec, refuse = check_rle_decoder(native)
            x_checks, y_checks = check_native_clipping(native)
            whole, groups, fallback, rows = check_full_region(native)
            preflight = check_safe_preflight(native)
            summary.append((cpu, dec, refuse, x_checks, y_checks,
                            whole, groups, fallback, rows, preflight))
        finally:
            native.close()
    print("OPT020/P1c REAL CPU RLE+X/Y CLIP PASS:", summary)
    print("68020-native kernel sizes/SHA256:", kernels)
    print("NO AP20, no R69, no WinUAE/hardware speed, no Compiler Gate C")
    print("R68 LAST_GOOD unmodified. P1c decoded packet pointers and geometry "
          "are executed by 68EC020/68020, Python orchestrates and prevalidates.")


if __name__ == "__main__":
    main()
