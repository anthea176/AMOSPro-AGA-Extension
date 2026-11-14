#!/usr/bin/env python3
"""Isolated AP20 multi-unit V3 *structural* experiment, not installable code.

No writes to repository dist/, LAST_GOOD, or active test state.
The copied unit content is deliberately independent, using synthetic 68k code.
No WinUAE/AMOS Compiler pass is claimed by this in-memory test.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack, unpack_from
import unittest

RBSR = bytes.fromhex('fe31')
RTS = bytes.fromhex('4e75')
NOP = bytes.fromhex('4e71')
DISPATCH_V2 = bytes.fromhex('598f48e78080206f000c700030182f48000c41fa000ed1c02f4800084cdf01014e75')
MAX_UNIT = 65534
TITLE = b'AP20 V3 isolated multiunit probe\0'
if len(TITLE) & 1:
    TITLE += b'\0'
TOKENS = bytes(6)


def template() -> bytes:
    return pack('>5I', 0x3f3, 0, 1, 0, 0) + pack('>I', 0) + pack('>I', 0x3e9) + pack('>I', 0) + pack('>I', 0x3f2)


def pack_ap20(base: bytes, tokens: bytes, parts: list[bytes], title: bytes) -> bytes:
    if any(len(s) & 1 or len(s) // 2 > 0xffff for s in parts):
        raise ValueError('Invalid AP20 section length')
    if not parts or len(parts) >= 65536 or len(title) & 1 or len(tokens) & 1:
        raise ValueError('Invalid AP20 alignment or count')
    code = b''.join(parts)
    body = (pack('>4I', 2 * len(parts), len(tokens), len(code), len(title))
            + b'\0\0AP20' + b''.join(pack('>H', len(p) // 2) for p in parts)
            + tokens + code + title + b'\0\0')
    body += bytes((-len(body)) % 4)
    n = pack('>I', len(body) // 4)
    result = base[:20] + n + base[24:28] + n + body + base[-4:]
    if unpack_ap20(result) != (tokens, parts, title):
        raise AssertionError('AP20 pack/unpack mismatch')
    return result


def unpack_ap20(raw: bytes) -> tuple[bytes, list[bytes], bytes]:
    if len(raw) < 64 or len(raw) & 3 or unpack_from('>5I', raw) != (0x3f3, 0, 1, 0, 0):
        raise ValueError('Invalid HUNK header')
    if unpack_from('>I', raw, 24)[0] != 0x3e9 or raw[-4:] != pack('>I', 0x3f2):
        raise ValueError('Invalid HUNK sections')
    words = unpack_from('>I', raw, 28)[0]
    if len(raw) != 36 + words * 4 or unpack_from('>I', raw, 20)[0] != words:
        raise ValueError('Invalid HUNK length')
    j, t, c, l = unpack_from('>4I', raw, 32)
    if j & 1 or j < 2 or raw[48:54] != b'\0\0AP20' or 54 + j + t + c + l + 2 > len(raw) - 4:
        raise ValueError('Invalid AP20 sections')
    lengths = unpack_from('>' + str(j // 2) + 'H', raw, 54)
    if sum(lengths) * 2 != c:
        raise ValueError('Invalid AP20 length table')
    pos = 54 + j
    tokens, pos = raw[pos:pos + t], pos + t
    code, pos = raw[pos:pos + c], pos + c
    title = raw[pos:pos + l]
    parts, cursor = [], 0
    for n in lengths:
        parts.append(code[cursor:cursor + 2 * n])
        cursor += 2 * n
    return tokens, parts, title


@dataclass(frozen=True)
class Layout:
    groups: tuple[tuple[int, int], ...]
    bridges: tuple[int, ...]
    offsets: tuple[int, ...]
    unit_sizes: tuple[int, ...]
    total_native: int


def wrap_multiunit(native: bytes, boundaries: tuple[int, ...], *, independent_test_only: bool = False) -> tuple[bytes, Layout]:
    if not independent_test_only:
        raise ValueError('Refuse unverified production use: native cross-unit links not audited')
    tokens, bodies, _ = unpack_ap20(native)
    n = len(bodies)
    if any(not x or x.endswith(b'GetP') or x.startswith(RBSR) for x in bodies):
        raise ValueError('Prototype only accepts nonempty independent plain native routines')
    marks = (0,) + boundaries + (n,)
    if not all(0 <= a < b <= n for a, b in zip(marks, marks[1:])):
        raise ValueError('Bad module boundaries')
    if any(marks[i] >= marks[i + 1] for i in range(len(marks) - 1)):
        raise ValueError('Overlapping module boundaries')
    stubs: list[bytes] = [b''] * n
    units: list[bytes] = []
    bridges: list[int] = [0] * n
    offsets: list[int] = [0] * n
    spans = tuple(zip(marks, marks[1:]))
    for k, (lo, hi) in enumerate(spans):
        unit = DISPATCH_V2 + b''.join(bodies[lo:hi])
        if len(unit) > MAX_UNIT:
            raise ValueError('Compiler V2 per-unit 16-bit limit exceeded')
        if len(unit) & 1:
            raise ValueError('Unaligned unit')
        ptr = 0
        for i in range(lo, hi):
            if ptr > 0xffff or ptr & 1:
                raise ValueError('Unrepresentable local branch offset')
            bridges[i], offsets[i] = n + k, ptr
            stubs[i] = RBSR + pack('>HH', n + k, ptr) + RTS
            ptr += len(bodies[i])
        units.append(unit)
    wrapped = pack_ap20(native, tokens, stubs + units, TITLE)
    layout = Layout(spans, tuple(bridges), tuple(offsets), tuple(map(len, units)), sum(map(len, bodies)))
    return wrapped, layout


def unwrap_multiunit(wrapped: bytes, boundaries: tuple[int, ...]) -> list[bytes]:
    tokens, parts, _ = unpack_ap20(wrapped)
    groups = len(boundaries) + 1
    n = len(parts) - groups
    if n <= 0:
        raise ValueError('Not a multiunit image')
    marks = (0,) + boundaries + (n,)
    if any(a >= b for a, b in zip(marks, marks[1:])):
        raise ValueError('Bad module boundaries')
    stubs = parts[:n]
    recovered = [b''] * n
    for module, (lo, hi) in enumerate(zip(marks, marks[1:])):
        unit = parts[n + module]
        if not unit.startswith(DISPATCH_V2) or len(unit) > MAX_UNIT:
            raise ValueError('Invalid compiler module')
        body = unit[len(DISPATCH_V2):]
        starts = []
        for i in range(lo, hi):
            stub = stubs[i]
            if len(stub) != 8 or stub[:2] != RBSR or stub[6:] != RTS:
                raise ValueError('Invalid AP20 bridge stub')
            dest, off = unpack_from('>HH', stub, 2)
            if dest != n + module or off & 1:
                raise ValueError('Wrong AP20 module target or alignment')
            starts.append(off)
        if not starts or starts[0] != 0 or any(a >= b for a, b in zip(starts, starts[1:])):
            raise ValueError('Wrong local offset order')
        for i, (a, b) in enumerate(zip(starts, starts[1:] + [len(body)]), start=lo):
            if b <= a or b > len(body):
                raise ValueError('Invalid local routine bounds')
            recovered[i] = body[a:b]
    return recovered


def synthetic_demo() -> tuple[bytes, list[bytes], tuple[int, ...]]:
    # MOVQ #17, D3 / RTS then NOPs; padding is unreachable, not a benchmark.
    def padded(value: int, length: int) -> bytes:
        if length < 4 or length & 1:
            raise ValueError('Bad test length')
        return bytes((0x76, value)) + RTS + NOP * ((length - 4) // 2)
    bodies = [padded(17, 40000), padded(34, 4), padded(51, 42000), padded(68, 4)]
    native = pack_ap20(template(), TOKENS, bodies, TITLE)
    return native, bodies, (2,)


class MultiunitStructuralTests(unittest.TestCase):
    def setUp(self):
        self.native, self.bodies, self.cuts = synthetic_demo()

    def test_over_64k_total_in_two_bounded_units(self):
        wrapped, lay = wrap_multiunit(self.native, self.cuts, independent_test_only=True)
        self.assertGreater(len(wrapped), 65536)
        self.assertEqual(lay.total_native, 82008)
        self.assertEqual(lay.unit_sizes, (40038, 42038))
        self.assertEqual(lay.bridges, (4, 4, 5, 5))
        self.assertEqual(lay.offsets, (0, 40000, 0, 42000))
        self.assertEqual(unwrap_multiunit(wrapped, self.cuts), self.bodies)

    def test_deterministic_repacking(self):
        a, _ = wrap_multiunit(self.native, self.cuts, independent_test_only=True)
        b, _ = wrap_multiunit(self.native, self.cuts, independent_test_only=True)
        self.assertEqual(a, b)
        _, parts, _ = unpack_ap20(a)
        self.assertEqual(len(parts), 6)
        self.assertEqual(parts[4][:len(DISPATCH_V2)], DISPATCH_V2)
        self.assertEqual(parts[5][:len(DISPATCH_V2)], DISPATCH_V2)

    def test_reject_cross_unit_misrouting(self):
        data, _ = wrap_multiunit(self.native, self.cuts, independent_test_only=True)
        token, parts, title = unpack_ap20(data)
        parts[3] = parts[3][:2] + pack('>H', 4) + parts[3][4:]
        bad = pack_ap20(data, token, parts, title)
        with self.assertRaises(ValueError):
            unwrap_multiunit(bad, self.cuts)

    def test_reject_invalid_local_offset(self):
        data, _ = wrap_multiunit(self.native, self.cuts, independent_test_only=True)
        tok, parts, title = unpack_ap20(data)
        parts[1] = parts[1][:4] + pack('>H', 40001) + parts[1][6:]
        bad = pack_ap20(data, tok, parts, title)
        with self.assertRaises(ValueError):
            unwrap_multiunit(bad, self.cuts)

    def test_reject_unit_overflow(self):
        parts = [NOP * (65502 // 2), NOP * 2]
        src = pack_ap20(template(), TOKENS, parts, TITLE)
        with self.assertRaises(ValueError):
            wrap_multiunit(src, (), independent_test_only=True)

    def test_reject_unsafe_inputs(self):
        with self.assertRaises(ValueError):
            wrap_multiunit(self.native, self.cuts)
        for wrong in ((0,), (2, 2), (4,), (3, 2)):
            with self.assertRaises(ValueError):
                wrap_multiunit(self.native, wrong, independent_test_only=True)
        invalid = pack_ap20(template(), TOKENS, [self.bodies[0], b'GetP', *self.bodies[2:]], TITLE)
        with self.assertRaises(ValueError):
            wrap_multiunit(invalid, self.cuts, independent_test_only=True)


def main() -> None:
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
