"""EXPERIMENT ONLY: AP20 Compiler bridge with unsigned 16-bit entry offsets.

Never an installable library builder. The R46/R54/R57 legacy dispatcher and
compiler_relocation.py are deliberately left unchanged. Generated AP20 bytes
exist in memory only, for read-only Gate A experimentation.
"""
from __future__ import annotations

from struct import pack, unpack_from

from compiler_relocation import (
    DISPATCH, GETP, RBSR, is_compiler_wrapped, repack_ap20, unpack_ap20,
)

# R57 dispatcher uses MOVE.W (A0)+,D0 / ADDA.W D0,A0 (signed).
# Add MOVEQ #0,D0 to clear the high half, and use ADDA.L D0,A0.
# LEA 14(PC),A0 still points exactly at the appended native-code start.
DISPATCH_V2 = bytes.fromhex(
    '598f48e78080206f000c700030182f48000c41fa000ed1c02f4800084cdf01014e75'
)
MAX_UNIT_BYTES = 65534  # +APComp.s LSL.W on the AP20 word count.
assert len(DISPATCH) == 32 and len(DISPATCH_V2) == 34
assert DISPATCH_V2[:10] == DISPATCH[:10]
assert DISPATCH_V2[10:12] == bytes.fromhex('7000')
assert DISPATCH_V2[12:22] == DISPATCH[10:20]
assert DISPATCH_V2[22:24] == bytes.fromhex('d1c0')
assert DISPATCH_V2[24:] == DISPATCH[22:]
assert (20 + 14) == len(DISPATCH_V2)  # LEA displacement base (PC after extension).


def is_v2_wrapped(raw: bytes) -> bool:
    """Check only the V2 marker, not generic/unknown external bridges."""
    _tokens, parts, _title = unpack_ap20(raw)
    return len(parts) >= 2 and parts[-1].startswith(DISPATCH_V2)


def wrap_native_ap20_v2(native: bytes, title: bytes) -> bytes:
    """Build a V2 AP20 image IN MEMORY; no file output, no official promotion."""
    tokens, parts, _old_title = unpack_ap20(native)
    if is_compiler_wrapped(native) or is_v2_wrapped(native):
        raise ValueError('already wrapped: legacy/V2 bridging must not be nested')
    if len(title) & 1:
        raise ValueError('AP20 title must be even length')
    if len(parts) >= 65535:
        raise ValueError('AP20 bridge index would overflow')
    code = b''.join(parts)
    if len(code) + len(DISPATCH_V2) > MAX_UNIT_BYTES:
        raise ValueError('V2 AP20 group too large for the 16-bit Compiler size')
    target_index = len(parts)
    offsets = []
    at = 0
    stubs = []
    for part in parts:
        offsets.append(at)
        if part in (b'', GETP):
            stubs.append(part)
        else:
            if at > 0xffff or (at & 1):
                raise ValueError('unaligned/out-of-range unsigned entry offset')
            stub = RBSR + pack('>HH', target_index, at) + b'\x4e\x75'
            if part.endswith(GETP):
                stub += GETP
            stubs.append(stub)
        at += len(part)
    assert at == len(code)
    image = repack_ap20(native, tokens, stubs + [DISPATCH_V2 + code], title)
    assert is_v2_wrapped(image)
    return image


def unwrap_native_parts_v2(wrapped: bytes) -> tuple[bytes, list[bytes]]:
    """Lossless source reconstruction; reject wrong bridge and corrupt stubs."""
    tokens, segments, _title = unpack_ap20(wrapped)
    if not is_v2_wrapped(wrapped):
        raise ValueError('not a V2 Compiler bridge')
    code = segments[-1][len(DISPATCH_V2):]
    stubs = segments[:-1]
    n = len(stubs)
    starts: list[int | None] = [None] * (n + 1)
    starts[-1] = len(code)
    for i, stub in enumerate(stubs):
        if stub in (b'', GETP):
            continue
        if len(stub) not in (8, 12) or stub[:4] != RBSR + pack('>H', n):
            raise ValueError(f'bad V2 entry {i}')
        if stub[6:8] != b'\x4e\x75' or (len(stub) == 12 and stub[8:] != GETP):
            raise ValueError(f'bad RTS/GetP tail on entry {i}')
        starts[i] = unpack_from('>H', stub, 4)[0]
        if starts[i] & 1:
            raise ValueError(f'odd V2 entry offset {i}')
    for i in range(n - 1, -1, -1):
        if starts[i] is None:
            starts[i] = starts[i + 1] - (4 if stubs[i] == GETP else 0)
        if starts[i] < 0 or starts[i] > starts[i + 1]:
            raise ValueError(f'wrong V2 offset order at entry {i}')
    if starts[0] != 0:
        raise ValueError('missing first V2 entry at zero')
    native_parts = [code[starts[i]:starts[i + 1]] for i in range(n)]
    for i, (original, stub) in enumerate(zip(native_parts, stubs)):
        if stub in (b'', GETP):
            if original != stub:
                raise ValueError(f'bad V2 empty marker {i}')
        else:
            expected = RBSR + pack('>HH', n, starts[i]) + b'\x4e\x75'
            if original.endswith(GETP):
                expected += GETP
            if expected != stub:
                raise ValueError(f'V2 entry offset/markers corrupted: {i}')
    return tokens, native_parts
