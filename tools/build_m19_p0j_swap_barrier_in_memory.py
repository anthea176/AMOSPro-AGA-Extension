#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b5 AP20 four-island Swap barrier candidate: IN MEMORY ONLY.

Two existing public tokens (Swap function / Screen Close instruction)
are re-indexed to two new zero-argument stubs AFTER the native BOBS unit.
The existing public stubs, original AGA native Swap and old BOBS/AGA bytes
are kept intact. The new wrappers are the only appended native code.
No public Aga Bob Draw token or active Lib/ASC replacement.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from

from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from audit_ap20 import inspect, parse, walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from build_m19_p0j_explicit_safe_draw_in_memory import build as build_b4
from m19_p0j_explicit_safe_draw_emit import emit_explicit_bob_draw
from m19_p0j_swap_barrier_emit import (
    emit_swap_barrier, AGA_SWAP_OFFSET, SWAP_SIGNATURE,
)

B4_SHA = 'b6a318118d0f8c58ab839d905c4094b8de27b6f481d411c647626266d69a6a7b'
B4_NATIVE_SHA = '6cde37acbee13004acf4cf23582b267a11247c28c85011896de7570c190b60e8'
BOBS = 177
TITLE = (b'AMOSPro AGA M19 P0j-b5 PRIVATE BOB FAILURE SWAP BARRIER SOURCE ONLY\0'
         b'$VER: AGA M19 P0j-b5 guarded Swap/Close EXPERIMENT UNINSTALLED\0')
TITLE += bytes(len(TITLE) & 1)


def _token_entry(tokens, name, role):
    rows = [r for r in walk_tokens(tokens) if r['name'] == name]
    if len(rows) != 1 or rows[0][role] <= 1:
        raise ValueError('Missing unique ' + name + ' ' + role)
    return rows[0], rows[0][role]


def build() -> tuple[bytes, dict]:
    base, meta = build_b4()
    if len(base) != 100596 or meta['sha256'] != B4_SHA or sha256(base).hexdigest() != B4_SHA:
        raise ValueError('P0j-b4 source ancestry mismatch')
    tokens, parts, _ = unpack_ap20(base)
    old, old_labels = emit_explicit_bob_draw()
    if len(old) != 20104 or sha256(old).hexdigest() != B4_NATIVE_SHA:
        raise ValueError('P0j-b4 exact native source mismatch')
    if len(parts) != 178 or not parts[BOBS].endswith(old):
        raise ValueError('P0j-b4 native BOBS island changed')
    revised, labels = emit_swap_barrier()
    if not revised.startswith(old):
        raise ValueError('Swap barrier altered P0j-b4 native bytes')
    delta = revised[len(old):]
    if not delta or len(delta) & 1 or len(parts[BOBS]) + len(delta) > MAX_UNIT_BYTES:
        raise ValueError('P0j-b5 native append invalid')
    swap_tok, swap_index = _token_entry(tokens, 'aga swap', 'function')
    close_tok, close_index = _token_entry(tokens, 'aga screen close', 'instruction')
    if swap_tok['instruction'] != 1 or close_tok['function'] != 1:
        raise ValueError('Swap/Close token ABI or form drift')
    original_swap = parts[swap_index]
    if (not original_swap.startswith(RBSR) or
            original_swap[6:8] != b'\x4e\x75' or original_swap[8:] not in (b'', GETP)):
        raise ValueError('Legacy Swap stub malformed')
    unit, offset = unpack_from('>HH', original_swap, 2)
    if (unit not in (142, 153, 156, 177) or
            len(DISPATCH_V2) + offset != AGA_SWAP_OFFSET or
            not parts[unit].startswith(DISPATCH_V2)):
        raise ValueError('Legacy AGA Swap relocation/source offset drift')
    aga = parts[unit]
    sig_offset = len(DISPATCH_V2) + offset
    if (unpack_from('>I', aga, sig_offset)[0] != SWAP_SIGNATURE[0] or
            unpack_from('>H', aga, sig_offset+4)[0] != SWAP_SIGNATURE[1] or
            unpack_from('>I', aga, sig_offset+6)[0] != SWAP_SIGNATURE[2]):
        raise ValueError('Original AGA Swap native entry signature changed')
    original_close = parts[close_index]
    if not original_close.startswith(RBSR) or original_close[6:8] != b'\x4e\x75':
        raise ValueError('Original Close stub malformed')

    result_parts = list(parts)
    result_parts[BOBS] += delta
    # Put both new stubs AFTER the BOBS unit: PC16 within 21 KiB, not
    # a 50 KiB branch from the old AGA island.
    new_stub_indices = {}
    for name, previous_stub, label in (
        ('swap', original_swap, 'guarded_swap_entry'),
        ('close', original_close, 'guarded_close_entry'),
    ):
        native_offset = len(parts[BOBS]) - len(DISPATCH_V2) + labels[label] - len(old)
        if native_offset & 1 or native_offset + len(DISPATCH_V2) >= len(result_parts[BOBS]):
            raise ValueError('Guard target outside native BOBS source')
        new_stub_indices[name] = len(result_parts)
        result_parts.append(RBSR + pack('>HH', BOBS, native_offset) + previous_stub[6:])
    new_tokens = bytearray(tokens)
    new_tokens[swap_tok['offset']+2:swap_tok['offset']+4] = pack('>H', new_stub_indices['swap'])
    new_tokens[close_tok['offset']:close_tok['offset']+2] = pack('>H', new_stub_indices['close'])
    new_tokens = bytes(new_tokens)
    result = repack_ap20(base, new_tokens, result_parts, TITLE)
    if unpack_ap20(result) != (new_tokens, result_parts, TITLE):
        raise ValueError('AP20/HUNK compiler layout not reproducible')
    old_api, new_api = inspect(parse(base)), inspect(parse(result))
    if (old_api['issues'] or new_api['issues'] or
            [(r['name'], r['signature']) for r in old_api['tokens']] !=
            [(r['name'], r['signature']) for r in new_api['tokens']]):
        raise ValueError('P0j-b5 public token signature/ABI changed')
    groups = [i for i, p in enumerate(result_parts) if p.startswith(DISPATCH_V2)]
    distance = pc16_displacements(result_parts)
    if groups != [142, 153, 156, 177] or max(map(abs, distance.values())) >= 32766:
        raise ValueError('P0j-b5 V2 native unit or PC16 span drift')
    if (result_parts[:BOBS] != parts[:BOBS] or
            result_parts[BOBS][:len(parts[BOBS])] != parts[BOBS] or
            any(result_parts[k] != parts[k] for k in range(BOBS))):
        raise ValueError('Historical native code was modified')
    return result, dict(
        sha256=sha256(result).hexdigest(), size=len(result),
        native_sha=sha256(revised).hexdigest(), native_bytes=len(revised),
        native_added=len(delta), previous_sha=B4_SHA,
        public_commands=85, ap20_entries=len(result_parts),
        native_groups=groups, pc16_max=max(map(abs, distance.values())),
        new_public_stubs=new_stub_indices, original_swap_index=swap_index,
        original_close_index=close_index, original_aga_group=unit,
        original_swap_offset=AGA_SWAP_OFFSET,
        guarded_draw_offset=labels['guarded_frame_draw_entry'],
        guarded_swap_offset=labels['guarded_swap_entry'],
        guarded_close_offset=labels['guarded_close_entry'],
        installed_lib='UNCHANGED', public_draw='NOT EXPOSED',
        gate_a='NATIVE TEST REQUIRED', gate_b='NOT TESTED',
        gate_c='NOT TESTED', gate_d='NOT TESTED')


if __name__ == '__main__':
    candidate, report = build()
    print('M19 P0j-b5 AP20 PRIVATE SWAP BARRIER SOURCE ONLY', report)
