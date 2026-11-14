#!/usr/bin/env python3
"""Independent, read-only AP20 Compiler V2 monolith capacity preflight.

Uses only Python stdlib. No .Lib is written. Does not attempt to prove CPU ABI,
RAM safety, native relative links, or AMOS runtime compatibility.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

MAX_COMPILER_UNIT = 65534  # APComp.s counts words, LSL.W
DISPATCH_V2 = bytes.fromhex(
    '598f48e78080206f000c700030182f48000c41fa000ed1c02f4800084cdf01014e75'
)
R81_SHA256 = '9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4'
R81_MONOLITH = 57034
R81_LIB_BYTES = 59972


def inspect_library(raw: bytes) -> dict[str, int | str]:
    """Parse HUNK/AP20 boundaries independently; fail closed on size overflow."""
    if len(raw) < 64 or len(raw) % 4:
        raise ValueError('invalid HUNK size/alignment')
    if struct.unpack_from('>5I', raw) != (0x3f3, 0, 1, 0, 0):
        raise ValueError('invalid HUNK header')
    if struct.unpack_from('>I', raw, 24)[0] != 0x3e9:
        raise ValueError('missing HUNK_CODE')
    if raw[-4:] != struct.pack('>I', 0x3f2):
        raise ValueError('missing HUNK_END')
    size_words = struct.unpack_from('>I', raw, 28)[0]
    if len(raw) != 36 + size_words * 4:
        raise ValueError('inconsistent HUNK length')
    j, t, c, l = struct.unpack_from('>4I', raw, 32)
    if j & 1 or j < 4 or raw[48:54] != b'\0\0AP20':
        raise ValueError('invalid AP20 table')
    if 54 + j + t + c + l + 2 > len(raw) - 4:
        raise ValueError('AP20 sections out of bounds')
    lengths = struct.unpack_from('>' + str(j // 2) + 'H', raw, 54)
    if sum(lengths) * 2 != c:
        raise ValueError('AP20 code lengths mismatch')
    code_start = 54 + j + t
    last = code_start + 2 * sum(lengths[:-1])
    monolith_bytes = 2 * lengths[-1]
    if raw[last:last + len(DISPATCH_V2)] != DISPATCH_V2:
        raise ValueError('not an AP20 Compiler V2 image')
    if monolith_bytes > MAX_COMPILER_UNIT:
        raise ValueError('Compiler V2 16-bit unit limit exceeded')
    return {
        'file_bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'entries': len(lengths),
        'monolith_bytes': monolith_bytes,
        'native_bytes': monolith_bytes - len(DISPATCH_V2),
        'limit': MAX_COMPILER_UNIT,
        'margin': MAX_COMPILER_UNIT - monolith_bytes,
    }


def forecast(margin: int, extra_native_bytes: int) -> int:
    if not isinstance(extra_native_bytes, int) or extra_native_bytes < 0 or extra_native_bytes & 1:
        raise ValueError('extra code size must be an even, nonnegative integer')
    rest = margin - extra_native_bytes
    if rest < 0:
        raise ValueError('candidate would exceed 16-bit AP20 Compiler V2 unit')
    return rest


def branch_width(source: int, destination: int) -> str:
    """Recommend PC-relative BSR width; native assembler must verify opcode and PC base."""
    displacement = destination - (source + 2)  # BSR.W legacy extension-word PC
    return 'word' if -32768 <= displacement <= 32767 else 'long-68020'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=Path)
    parser.add_argument('--planned-bytes', type=int, default=0)
    parser.add_argument('--assert-r81', action='store_true')
    args = parser.parse_args()
    result = inspect_library(args.library.read_bytes())
    if args.assert_r81 and (result['sha256'] != R81_SHA256 or
                            result['file_bytes'] != R81_LIB_BYTES or
                            result['monolith_bytes'] != R81_MONOLITH):
        raise SystemExit('R81 baseline differs from known promoted LAST_GOOD')
    rest = forecast(result['margin'], args.planned_bytes)
    print('AP20 COMPILER V2 BUDGET OK', result,
          'planned_bytes=', args.planned_bytes, 'remaining_after_plan=', rest)
    if rest < 2048:
        print('WARNING: less than 2 KiB remaining; new native code requires architecture review')


if __name__ == '__main__':
    main()
