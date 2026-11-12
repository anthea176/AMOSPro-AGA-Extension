"""AMOS AGA AP20 compiler-safe wrapping for production builds (standard library only).

The native source generator produces contiguous AP20 segments as before.
Call wrap_native_ap20 as the FINAL build step; Rbsr dispatchers keep every
old PC-relative data reference and BSR target in one compiler-copied unit.
Fail closed at the 32-KiB single-routine limit; never silently ship raw AP20.
"""
from __future__ import annotations

from struct import pack, unpack_from

RBSR = b'\xfe\x31'
GETP = b'GetP'
DISPATCH = bytes.fromhex('598f48e78080206f000c30182f48000c41fa000ed0c02f4800084cdf01014e75')
assert len(DISPATCH) == 32


def unpack_ap20(raw: bytes) -> tuple[bytes, list[bytes], bytes]:
    """Read and bound the single-HUNK AP20 format before changing anything."""
    if len(raw) < 64 or len(raw) % 4 or unpack_from('>5I', raw) != (0x3f3,0,1,0,0):
        raise ValueError('invalid HUNK header')
    if unpack_from('>I',raw,24)[0] != 0x3e9 or raw[-4:] != pack('>I',0x3f2):
        raise ValueError('invalid HUNK_CODE / HUNK_END')
    size_words=unpack_from('>I',raw,28)[0]
    if len(raw) != 36 + size_words*4 or unpack_from('>I',raw,20)[0]!=size_words:
        raise ValueError('inconsistent HUNK length')
    j,t,c,l=unpack_from('>4I',raw,32)
    if (j & 1) or raw[48:54] != b'\0\0AP20':
        raise ValueError('not an AP20 library')
    if 54+j+t+c+l+2 > len(raw)-4:
        raise ValueError('AP20 sections beyond HUNK')
    sizes=unpack_from('>'+str(j//2)+'H',raw,54)
    if sum(sizes)*2!=c:raise ValueError('AP20 entry sizes do not cover code')
    pos=54+j
    tokens=raw[pos:pos+t];pos+=t
    code=raw[pos:pos+c];pos+=c
    title=raw[pos:pos+l]
    parts=[];off=0
    for w in sizes:
        parts.append(code[off:off+2*w]);off+=2*w
    return tokens,parts,title


def repack_ap20(template: bytes, tokens: bytes, parts: list[bytes], title: bytes) -> bytes:
    """Repack any AP20 segment count (ap20_utils.rebuild requires unchanged count)."""
    assert all(len(p) % 2 == 0 for p in parts)
    assert len(parts) < 65536 and all(len(p) // 2 <= 65535 for p in parts)
    assert len(title) % 2 == 0 and len(tokens) % 2 == 0
    code = b''.join(parts)
    payload = (pack('>4I', 2*len(parts), len(tokens), len(code), len(title))
               + b'\0\0AP20' + b''.join(pack('>H', len(p)//2) for p in parts)
               + tokens + code + title + b'\0\0')
    payload += bytes(-len(payload) % 4)
    words = pack('>I', len(payload)//4)
    out = template[:20] + words + template[24:28] + words + payload + template[-4:]
    assert unpack_ap20(out) == (tokens, parts, title)
    return out


def is_compiler_wrapped(raw: bytes) -> bool:
    _, parts, _ = unpack_ap20(raw)
    return len(parts) >= 2 and parts[-1].startswith(DISPATCH)


def wrap_native_ap20(native: bytes, title: bytes) -> bytes:
    """Wrap an UNWRAPPED native AP20 library, preserving tokens/code byte-for-byte.

    Existing native-only source builders must feed their output here. If the
    monolithic unit would exceed the 68000 signed offset range, fail until a
    separately tested modular relocation solution has been implemented.
    """
    tokens, parts, _ = unpack_ap20(native)
    if is_compiler_wrapped(native):
        raise ValueError('already wrapped: refuse duplicate Rbsr bridge')
    if len(parts) >= 65535:
        raise ValueError('AP20 bridge index overflows')
    code = b''.join(parts)
    if len(code) + len(DISPATCH) >= 32768:
        raise ValueError('AP20 compiler-safe monolithic code exceeds signed 16-bit limit')
    if len(title) & 1:
        raise ValueError('AP20 title must be word-aligned')
    bridge_index = len(parts)
    at = 0
    new_parts = []
    for part in parts:
        if not part or part == GETP:
            stub = part
        else:
            if at > 32767 or (at & 1):
                raise ValueError('AP20 entry offset exceeds signed 16-bit range')
            stub = RBSR + pack('>HH', bridge_index, at) + b'\x4e\x75'
            if part.endswith(GETP):
                stub += GETP
        new_parts.append(stub)
        at += len(part)
    return repack_ap20(native, tokens, new_parts + [DISPATCH + code], title)


def unwrap_native_parts(wrapped: bytes) -> tuple[bytes, list[bytes]]:
    """Recover the native, editable AP20 parts from official compiler-safe C1.

    This recovers all original segment boundaries using entry offsets encoded
    inside the stubs. It returns native tokens and parts, NOT the historical
    title, which must be set explicitly for a future release.
    """
    tokens, segments, _ = unpack_ap20(wrapped)
    if len(segments) < 2 or not segments[-1].startswith(DISPATCH):
        raise ValueError('not a compiler-safe C1-style AP20 library')
    code = segments[-1][len(DISPATCH):]
    stubs = segments[:-1]
    count = len(stubs)
    offsets = [None] * (count+1)
    offsets[-1] = len(code)
    for i, p in enumerate(stubs):
        if not p or p == GETP:
            continue
        if len(p) not in (8, 12) or p[:4] != RBSR + pack('>H',count):
            raise ValueError(f'malformed AP20 Rbsr stub {i}')
        if p[6:8] != b'\x4e\x75' or (len(p)==12 and p[8:] != GETP):
            raise ValueError(f'malformed AP20 Rbsr stub tail {i}')
        offsets[i] = unpack_from('>H', p, 4)[0]
    for i in range(count-1,-1,-1):
        if offsets[i] is None:
            offsets[i] = offsets[i+1] - (4 if stubs[i] == GETP else 0)
        if offsets[i] < 0 or offsets[i] > offsets[i+1]:
            raise ValueError(f'invalid reconstructed AP20 offset {i}')
    if offsets[0] != 0:
        raise ValueError('first AP20 entry does not start at zero')
    original = [code[offsets[i]:offsets[i+1]] for i in range(count)]
    for i, stub in enumerate(stubs):
        part = original[i]
        if stub in (b'',GETP):
            if stub != part:
                raise ValueError(f'marker/empty entry changed {i}')
        else:
            expected = RBSR+pack('>HH',count,offsets[i])+b'\x4e\x75'
            if part.endswith(GETP):
                expected += GETP
            if stub != expected:
                raise ValueError(f'entry {i} does not match original code')
    return tokens, original


def native_from_promoted(promoted: bytes, title: bytes) -> bytes:
    """Reconstruct a native-segmented BUILD INPUT from the last good library.

    Future builders: native = native_from_promoted(LAST_GOOD.read_bytes(),
    b'new version title\\0...'); change native segments/tokens in memory;
    compiler_ready = wrap_native_ap20(native_candidate, final_title).
    """
    if len(title) & 1:
        raise ValueError('AP20 native title must be word aligned')
    tokens, native_parts = unwrap_native_parts(promoted)
    return repack_ap20(promoted, tokens, native_parts, title)
