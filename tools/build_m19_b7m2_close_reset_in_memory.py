#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B7-m2 source-only Close-reset candidate built entirely IN MEMORY.

Base: exact B7-m1 102360-byte installed build, reconstructed from its source.
Append only a BOBS native suffix and repoint the existing Screen Close stub.
Keep 86 public tokens / 181 AP20 entries / four 68020 native groups and
the original B7-m1 bytes unchanged. Do NOT install any library.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from

from audit_ap20 import inspect, parse, walk_tokens
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import RBSR, repack_ap20, unpack_ap20
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p0j_end_lifecycle_in_memory import build_multiframe
from m19_p0j_end_lifecycle_emit import emit_end_lifecycle_multiframe
from m19_b7m2_close_reset_emit import emit_close_reset

B7M1_SHA256 = '838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403'
B7M1_SIZE = 102360
BOBS = 177
CLOSE = 179
TITLE = (b'AMOSPro AGA M19 B7-m2 guarded Close Bob reset SOURCE ONLY\0'
         b'$VER: AGA M19 B7-m2 Close reset NOT INSTALLED\0')
TITLE += bytes(len(TITLE) & 1)


def build_close_reset() -> tuple[bytes, dict]:
    base, origin = build_multiframe()
    if (len(base) != B7M1_SIZE or origin['sha256'] != B7M1_SHA256
            or sha256(base).hexdigest() != B7M1_SHA256):
        raise ValueError('B7-m1 exact source ancestry mismatch')

    tokens, parts, _ = unpack_ap20(base)
    old_native, old_labels = emit_end_lifecycle_multiframe()
    revised, labels = emit_close_reset()
    if len(parts) != 181 or not parts[BOBS].endswith(old_native):
        raise ValueError('B7-m1 BOBS source or AP20 layout drift')
    if not revised.startswith(old_native):
        raise ValueError('B7-m2 rewrote frozen B7-m1 native source')

    close_tokens = [t for t in walk_tokens(tokens)
                    if t['name'] == 'aga screen close']
    if (len(close_tokens) != 1
            or close_tokens[0]['instruction'] != CLOSE
            or close_tokens[0]['function'] != 1):
        raise ValueError('Original Screen Close public ABI/index changed')
    old_stub = parts[CLOSE]
    if (not old_stub.startswith(RBSR) or len(old_stub) not in (8, 12)
            or old_stub[6:8] != b'\x4e\x75'):
        raise ValueError('Original Screen Close RBSR stub malformed')
    native_origin = len(parts[BOBS]) - len(DISPATCH_V2) - len(old_native)
    old_offset = native_origin + old_labels['guarded_close_entry']
    if unpack_from('>HH', old_stub, 2) != (BOBS, old_offset):
        raise ValueError('B7-m1 Close stub is not pinned to B5 guard')

    suffix = revised[len(old_native):]
    target = native_origin + labels['b7m2_close_reset_entry']
    if (not suffix or len(suffix) & 1 or target & 1
            or target < 0 or target + len(suffix) > MAX_UNIT_BYTES
            or len(parts[BOBS]) + len(suffix) > MAX_UNIT_BYTES):
        raise ValueError('Invalid B7-m2 native append or Close target')

    updated = list(parts)
    updated[BOBS] += suffix
    updated[CLOSE] = RBSR + pack('>HH', BOBS, target) + old_stub[6:]
    if (updated[BOBS][:len(parts[BOBS])] != parts[BOBS]
            or any(updated[i] != parts[i] for i in range(len(parts))
                   if i not in (BOBS, CLOSE))):
        raise ValueError('B7-m2 modified a protected AP20 native entry')

    candidate = repack_ap20(base, tokens, updated, TITLE)
    if unpack_ap20(candidate) != (tokens, updated, TITLE):
        raise ValueError('B7-m2 AP20 HUNK roundtrip failed')
    old_api, api = inspect(parse(base)), inspect(parse(candidate))
    if (old_api['issues'] or api['issues']
            or old_api['tokens'] != api['tokens']):
        raise ValueError('B7-m2 changed public tokens or signatures')
    groups = [i for i, part in enumerate(updated)
              if part.startswith(DISPATCH_V2)]
    spans = pc16_displacements(updated)
    pc16 = max(map(abs, spans.values()))
    if groups != [142, 153, 156, 177] or pc16 >= 32766:
        raise ValueError('B7-m2 exceeds four-unit Compiler PC16 budget')

    return candidate, dict(
        sha256=sha256(candidate).hexdigest(), size=len(candidate),
        predecessor_sha=B7M1_SHA256, public_commands=86, ap20_entries=181,
        native_groups=groups, pc16_max=pc16,
        native_sha256=sha256(revised).hexdigest(),
        native_bytes=len(revised), appended_bytes=len(suffix),
        close_stub=CLOSE, close_group=BOBS, close_native_offset=target,
        original_close_native_offset=old_offset,
        installed_lib='UNCHANGED', current_asc='UNCHANGED',
        gate_a='CPU020 TEST REQUIRED', gate_b='NOT TESTED',
        gate_c='NOT TESTED', gate_d='NOT TESTED')


if __name__ == '__main__':
    _, result = build_close_reset()
    print('M19 B7-m2 CLOSE RESET SOURCE ONLY:', result)
