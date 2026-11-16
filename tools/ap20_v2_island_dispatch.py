#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 AP20 V2 dispatch islands, source-only and never an installed binary.

Keep each full native V2 unit byte-for-byte. Move its AP20 Rbsr entry stubs
next to the unit, and rebind the public tokens by entry index. The native
AMOS 365 +B.s and AMOS Compiler own the BSR.W/absolute-JSR relocation;
there is no guessed absolute pointer or cross-unit PC16 in this builder.

IMPORTANT: an AP20 GetP marker is associated with the following entry,
not the preceding instruction. Normalize trailing GetP to marker-only entries
before moving stubs, then audit the exact packed candidate.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack, unpack_from
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from audit_ap20 import inspect, parse, walk_tokens

RTS = bytes.fromhex('4e75')
MAX_PC16 = 32766  # fail closed using the existing AMOS365 signed GRouB guard


@dataclass(frozen=True)
class IslandReport:
    source_entries: int
    entries: int
    added_getp_markers: int
    max_pc16: int
    group_map: dict[int, int]
    entry_map: dict[int, int]
    group_ranges: dict[int, tuple[int, int]]


def _stub(part: bytes, groups: set[int]) -> tuple[int, int] | None:
    if not part.startswith(RBSR):
        if part not in (b'', GETP):
            raise ValueError('Unknown non-Rbsr public AP20 entry')
        return None
    if (len(part) not in (8, 12) or part[6:8] != RTS
            or (len(part) == 12 and part[8:] != GETP)):
        raise ValueError('Malformed AP20 Rbsr/RTS/GetP stub')
    g, offset = unpack_from('>HH', part, 2)
    if g not in groups or offset & 1:
        raise ValueError('Invalid native unit reference or alignment')
    return g, offset


def pc16_displacements(parts: list[bytes]) -> dict[int, int]:
    starts = []
    position = 0
    for part in parts:
        starts.append(position)
        position += len(part)
    groups = {i for i, p in enumerate(parts) if p.startswith(DISPATCH_V2)}
    links = {}
    for i, p in enumerate(parts):
        if not p.startswith(RBSR):
            continue
        target = _stub(p, groups)
        assert target is not None
        g, offset = target
        if offset >= len(parts[g]) - len(DISPATCH_V2):
            raise ValueError('Native offset exceeds source unit')
        disp = starts[g] - (starts[i] + 2)
        if abs(disp) >= MAX_PC16 or disp & 1:
            raise ValueError(f'AP20 GRouB PC16 overflow entry {i}: {disp}')
        links[i] = disp
    return links


def dispatch_islands(source: bytes, *, title: bytes | None = None,
                     group_order: tuple[int, ...] | None = None) -> tuple[bytes, IslandReport]:
    tokens, parts, old_title = unpack_ap20(source)
    groups = [i for i, p in enumerate(parts) if p.startswith(DISPATCH_V2)]
    if not groups or groups != list(range(groups[0], len(parts))):
        raise ValueError('Expected contiguous AP20 V2 native units at tail')
    public_count = groups[0]
    if public_count < 3:
        raise ValueError('No conventional AP20 public entry table')
    for g in groups:
        if len(parts[g]) > MAX_UNIT_BYTES or len(parts[g]) < len(DISPATCH_V2) + 2:
            raise ValueError('Invalid native unit size')
    old_group_set = set(groups)
    destinations = {i: _stub(p, old_group_set) for i, p in enumerate(parts[:public_count])}
    for i, target in destinations.items():
        if target is not None:
            g, off = target
            if off >= len(parts[g]) - len(DISPATCH_V2):
                raise ValueError(f'Entry {i} targets outside native unit')
    old_audit = inspect(parse(source))
    if old_audit['issues']:
        raise ValueError('Source token signatures/GetP invalid')
    if any(x['instruction'] >= public_count or x['function'] >= public_count
           for x in old_audit['tokens']):
        raise ValueError('Token refers to non-public/native AP20 unit')
    # The two reserved entry indices must not move (AMOS Init/dummy semantics).
    first_group = destinations[0][0] if destinations[0] else groups[0]
    order = tuple(group_order or (first_group, *(g for g in groups if g != first_group)))
    if set(order) != old_group_set or len(order) != len(groups) or order[0] != first_group:
        raise ValueError('Invalid group order: special entry 0 must remain local')
    new_parts = [parts[0], parts[1]]
    old_to_new = {0: 0, 1: 1}
    # Keep reserved original non-executable markers; remap all their refs too.
    for i in range(2, public_count):
        if destinations[i] is None:
            old_to_new[i] = len(new_parts)
            new_parts.append(parts[i])
    native_map = {}
    group_ranges = {}
    marker_count = 0
    for old_group in order:
        local_indices = [i for i in range(2, public_count)
                         if destinations[i] and destinations[i][0] == old_group]
        begin = len(new_parts)
        for i in local_indices:
            # GetP is the LAST FOUR BYTES of preceding old entry, and must
            # remain immediately before the relocated target entry.
            if parts[i - 1].endswith(GETP):
                new_parts.append(GETP)
                marker_count += 1
            old_to_new[i] = len(new_parts)
            _, offset = destinations[i]
            new_parts.append(RBSR + pack('>HH', 0, offset) + RTS)
        new_group = len(new_parts)
        native_map[old_group] = new_group
        new_parts.append(parts[old_group])
        group_ranges[old_group] = (begin, new_group)
    if len(old_to_new) != public_count:
        raise ValueError('Lost an AP20 public entry while regrouping')
    # Entry 0 and entry 1 stay at their original indices, with only the
    # Rbsr group index redirected when necessary.
    for i in (0, 1):
        if destinations[i]:
            _, offset = destinations[i]
            suffix = parts[i][6:]
            new_parts[i] = RBSR + pack('>HH', native_map[destinations[i][0]], offset) + suffix
    for i in range(2, public_count):
        if destinations[i]:
            _, offset = destinations[i]
            n = old_to_new[i]
            new_parts[n] = RBSR + pack('>HH', native_map[destinations[i][0]], offset) + RTS
    # Only the two numeric entry indices change in a public token record.
    new_tokens = bytearray(tokens)
    for row in walk_tokens(tokens):
        for j, role in enumerate(('instruction', 'function')):
            idx = row[role]
            if idx > 1:
                new_tokens[row['offset'] + j * 2:row['offset'] + j * 2 + 2] = pack('>H', old_to_new[idx])
    new_title = old_title if title is None else title
    candidate = repack_ap20(source, bytes(new_tokens), new_parts, new_title)
    new_audit = inspect(parse(candidate))
    if new_audit['issues']:
        raise ValueError('Relocated token ABI/GetP: ' + repr(new_audit['issues'][:5]))
    a = [(r['name'], r['signature']) for r in old_audit['tokens']]
    b = [(r['name'], r['signature']) for r in new_audit['tokens']]
    if a != b:
        raise ValueError('API changed during AP20 token remapping')
    for i, j in native_map.items():
        if new_parts[j] != parts[i]:
            raise ValueError('Native unit mutated')
    lengths = pc16_displacements(new_parts)
    if 0 not in lengths or not lengths:
        raise ValueError('Missing AMOS entry 0 Init/dispatch')
    return candidate, IslandReport(
        source_entries=len(parts), entries=len(new_parts),
        added_getp_markers=marker_count, max_pc16=max(map(abs, lengths.values())),
        group_map=native_map, entry_map=old_to_new, group_ranges=group_ranges)
