#!/usr/bin/env python3
"""Experimental R46/AMOS Compiler Gate C: AP20 relocatable entry bridge.

Keep the entire original R46 68000 code byte-for-byte in one 27,888-byte
AP20 routine, below the 32-KiB per-routine limit. Existing BSR.w and
PC-relative state then stay within a single relocated copy, while Rbsr
stubs dispatch public entries. Not a WinUAE/Compiler PASS. No promotion.
"""
import argparse
from pathlib import Path
from struct import pack, unpack_from
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib'
SHA = '5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580'
CANDIDATE_SHA = 'd2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b'
CANDIDATE = ROOT / 'dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib'
# A7 artificial return slot; save D0/A0; read the 16-bit offset immediately
# after the caller's Rbsr; restore its return address to the stub RTS;
# RTS into the unmodified original function, then RTS back to the caller.
DISPATCH = bytes.fromhex('598f48e78080206f000c30182f48000c41fa000ed0c02f4800084cdf01014e75')
assert len(DISPATCH) == 32


def digest(data):
    return sha256(data).hexdigest()


def read_ap20(data):
    assert len(data) == 29288 and digest(data) == SHA, 'unexpected R46 source'
    assert unpack_from('>5I', data) == (0x3f3, 0, 1, 0, 0)
    assert unpack_from('>I', data, 24)[0] == 0x3e9
    assert data[48:54] == b'\0\0AP20' and data[-4:] == pack('>I', 0x3f2)
    j, t, c, l = unpack_from('>4I', data, 32)
    assert j == 112 and c == 27856
    sizes = unpack_from('>56H', data, 54)
    off = 54 + j
    tokens = data[off:off+t]
    off += t
    parts = []
    for words in sizes:
        parts.append(data[off:off+2*words]); off += 2*words
    assert sum(map(len, parts)) == c
    return tokens, parts


def build(source):
    tokens, old = read_ap20(source)
    whole = b''.join(old)
    assert len(whole) == 27856 and len(whole)+len(DISPATCH) < 32768
    assert old[16] == b'' and old[1] == b'GetP'
    stubs = []
    offset = 0
    for part in old:
        if not part or part == b'GetP':
            stub = part  # preserve empty and marker-only AP20 entries
        else:
            assert offset < 32768 and not offset & 1
            stub = b'\xfe\x31' + pack('>HH', 56, offset) + b'\x4e\x75'
            if part.endswith(b'GetP'): stub += b'GetP'
        stubs.append(stub)
        offset += len(part)
    assert offset == len(whole)
    parts = stubs + [DISPATCH + whole]
    title = b'AMOSPro AGA M16 R46 Compiler Gate C candidate 0.12.1-C1\0$VER: AMOSPro_AGA 0.12.1-C1\0'
    title += bytes(len(title) % 2)
    code = b''.join(parts)
    payload = (pack('>4I', 2*len(parts), len(tokens), len(code), len(title))
        + b'\0\0AP20' + b''.join(pack('>H', len(p)//2) for p in parts)
        + tokens + code + title + b'\0\0')
    payload += bytes(-len(payload) % 4)
    words = pack('>I', len(payload)//4)
    candidate = source[:20] + words + source[24:28] + words + payload + source[-4:]
    assert len(candidate) == 29964 and digest(candidate) == CANDIDATE_SHA
    return candidate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    source = args.input.read_bytes()
    result = build(source)
    assert build(source) == result, 'non-deterministic candidate'
    print('Gate C candidate (EXPERIMENTAL, NOT WinUAE PASS):', len(result), digest(result))
    if args.output:
        assert args.output.resolve() == CANDIDATE.resolve(), 'write only the experimental candidate'
        assert not args.output.exists(), 'never overwrite a candidate'
        args.output.write_bytes(result)
