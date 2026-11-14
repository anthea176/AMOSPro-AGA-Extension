#!/usr/bin/env python3
"""Independent, stdlib-only negative tests for AP20 16-bit size guard."""
from __future__ import annotations
import struct
from aga_compiler_capacity import (
    DISPATCH_V2, MAX_COMPILER_UNIT, R81_MONOLITH, inspect_library, forecast,
    branch_width,
)


def synthetic_ap20(native_length: int) -> bytes:
    if native_length < 0 or native_length & 1:
        raise ValueError('bad synthetic code size')
    # Two entry stubs: 8 bytes plus final unit dispatcher + 68020 native data.
    parts = [bytes(8), DISPATCH_V2 + bytes(native_length)]
    c = sum(map(len, parts))
    j = 2 * len(parts)
    tokens = b'\0' * 6
    title = b'PROBE\0'
    payload = (struct.pack('>4I', j, len(tokens), c, len(title))
               + b'\0\0AP20'
               + struct.pack('>2H', *(len(x) // 2 for x in parts))
               + tokens + b''.join(parts) + title + b'\0\0')
    payload += bytes(-len(payload) % 4)
    size = len(payload) // 4
    return (struct.pack('>5I', 0x3f3, 0, 1, 0, 0)
            + struct.pack('>I', size) + struct.pack('>I', 0x3e9)
            + struct.pack('>I', size) + payload + struct.pack('>I', 0x3f2))


def expect_fail(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('expected rejection')


def main():
    v = inspect_library(synthetic_ap20(0))
    assert v['monolith_bytes'] == len(DISPATCH_V2)
    assert v['margin'] == MAX_COMPILER_UNIT - len(DISPATCH_V2)
    maxnative = MAX_COMPILER_UNIT - len(DISPATCH_V2)
    assert inspect_library(synthetic_ap20(maxnative))['margin'] == 0
    expect_fail(lambda: inspect_library(synthetic_ap20(maxnative + 2)))
    expect_fail(lambda: inspect_library(synthetic_ap20(4)[:-2]))
    expect_fail(lambda: inspect_library(b'broken'))
    expect_fail(lambda: inspect_library(synthetic_ap20(4).replace(b'AP20',b'AP99')))
    assert forecast(MAX_COMPILER_UNIT - R81_MONOLITH, 0) == 8500
    assert forecast(8500, 8498) == 2
    assert forecast(8500, 8500) == 0
    expect_fail(lambda: forecast(8500, 8502))
    expect_fail(lambda: forecast(8500, -2))
    expect_fail(lambda: forecast(8500, 1))
    assert branch_width(57000, 1000) == 'long-68020'
    assert branch_width(1000, 32000) == 'word'
    assert branch_width(1000, 36000) == 'long-68020'
    print('AP20 COMPILER V2 BUDGET HOST TEST PASS: 14 checks')


if __name__ == '__main__':
    main()
