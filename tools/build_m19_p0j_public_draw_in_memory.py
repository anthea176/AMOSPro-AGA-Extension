#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b6: source-only AP20 public FUNCTION Aga Bob Draw -> guarded B5.

The only new command in this candidate is the zero-argument numerical
function Aga Bob Draw. Its AP20 stub targets the already validated B5
guarded_frame_draw_entry. The four native groups and all old stubs/tokens
are byte-identical. No installable Lib, ASC, or LAST_GOOD is written.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from

from audit_ap20 import inspect, parse, token, walk_tokens
from compiler_relocation import RBSR, repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p0j_swap_barrier_in_memory import build as build_b5
from m19_p0j_swap_barrier_emit import emit_swap_barrier

B5_SHA = 'a5a08853f331b7c70d8e71eb95911bee3d8944f18feb107fda2249f10477d55e'
B5_NATIVE_SHA = 'd02eb6c89863fbb769d699296a923dc2997e2b39184c2c7d51800c28c10c1b5e'
BOBS = 177
API_NAME = 'aga bob draw'
TITLE = (b'AMOSPro AGA M19 P0j-b6 PUBLIC DRAW TOKEN SOURCE-ONLY Gate A\0'
         b'$VER: AMOSPro_AGA P0j-b6 guarded Draw function UNINSTALLED\0')
TITLE += bytes(len(TITLE) & 1)


def build() -> tuple[bytes, dict]:
    old, meta = build_b5()
    if len(old) != 101460 or sha256(old).hexdigest() != B5_SHA:
        raise ValueError('P0j-b5 source ancestry mismatch')
    tokens, parts, _ = unpack_ap20(old)
    if len(parts) != 180 or meta['public_commands'] != 85:
        raise ValueError('P0j-b5 AP20 layout changed')
    if any(r['name'] == API_NAME for r in walk_tokens(tokens)):
        raise ValueError('Aga Bob Draw token already present')
    native, labels = emit_swap_barrier()
    if (len(native) != 20944 or sha256(native).hexdigest() != B5_NATIVE_SHA
            or not parts[BOBS].endswith(native)):
        raise ValueError('P0j-b5 guarded native code changed')

    # Existing source BOBS group ends with the entire emitted B5 native.
    # Native AP20 offsets are relative to the end of the 34-byte dispatcher.
    target = len(parts[BOBS]) - len(DISPATCH_V2) - len(native)
    target += labels['guarded_frame_draw_entry']
    if (target & 1 or target < 0 or
            target >= len(parts[BOBS]) - len(DISPATCH_V2)):
        raise ValueError('Guarded draw target not inside BOBS island')

    new_index = len(parts)
    new_parts = list(parts) + [RBSR + pack('>HH', BOBS, target) + b'\x4e\x75']
    new_tokens = (tokens[:-6] + token(API_NAME, 1, new_index, '0')
                  + tokens[-6:])
    if new_parts[:len(parts)] != parts:
        raise ValueError('P0j-b6 modified existing AP20 sections')
    candidate = repack_ap20(old, new_tokens, new_parts, TITLE)
    if unpack_ap20(candidate) != (new_tokens, new_parts, TITLE):
        raise ValueError('AP20/HUNK roundtrip changed source')

    prior, current = inspect(parse(old)), inspect(parse(candidate))
    if (prior['issues'] or current['issues']
            or current['tokens'][:-1] != prior['tokens']):
        raise ValueError('P0j-b6 altered previous token signatures')
    last = current['tokens'][-1]
    if (last['name'], last['signature'], last['instruction'],
            last['function']) != (API_NAME, '0', 1, new_index):
        raise ValueError('Aga Bob Draw is not a 0-arg numerical function')
    if len(current['tokens']) != len(prior['tokens']) + 1:
        raise ValueError('More than one token added')
    groups = [i for i, part in enumerate(new_parts) if part.startswith(DISPATCH_V2)]
    spans = pc16_displacements(new_parts)
    if groups != [142, 153, 156, 177] or max(map(abs, spans.values())) >= 32766:
        raise ValueError('P0j-b6 native island / PC16 displacement overflow')
    group, target_from_stub = unpack_from('>HH', new_parts[new_index], 2)
    if (group, target_from_stub) != (BOBS, target):
        raise ValueError('AP20 Draw stub does not target guarded draw')
    return candidate, dict(
        sha256=sha256(candidate).hexdigest(), size=len(candidate),
        predecessor_sha=B5_SHA, native_sha=B5_NATIVE_SHA,
        public_commands=86, ap20_entries=len(new_parts),
        native_groups=groups, pc16_max=max(map(abs, spans.values())),
        draw_token=API_NAME, draw_signature='0',
        draw_function_entry=new_index, draw_native_group=group,
        draw_native_offset=target, draw_native_label=labels['guarded_frame_draw_entry'],
        guarded_swap_entry=meta['new_public_stubs']['swap'],
        guarded_close_entry=meta['new_public_stubs']['close'],
        installed_lib='UNCHANGED', winuae_asc='UNCHANGED',
        gate_a='NATIVE TEST REQUIRED', gate_b='NOT TESTED',
        gate_c='NOT TESTED', gate_d='NOT TESTED')


if __name__ == '__main__':
    _raw, _meta = build()
    print('M19 P0j-b6 PUBLIC NUMERIC DRAW SOURCE-ONLY', _meta)
