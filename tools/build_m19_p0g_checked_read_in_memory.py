#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0g: source-only checked per-object Draw prerequisite, no API switch.

Byte-exact P0f source first. Append a separate private BOBS relay that
validates original source-bank stamp before returning a 24-byte object
record; do not replace the raw read. No public Draw or Chip/Blitter yet.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

from audit_ap20 import inspect, parse
from compiler_relocation import repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from m19_p0e_split_bridge_emit import AGA_CORE
from m19_p0f_object_identity_emit import emit_object_identity
from build_m19_p0f_public_bound_in_memory import build as build_p0f, emit_bound_public
from m19_p0g_checked_read_emit import emit_checked_read, checked_read_offset

sys.path.insert(0, str(Path(__file__).resolve().parent / 'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

BOBS, AGA = 93, 94
TITLE = (b'AMOSPro AGA M19 P0g private checked Bob read SOURCE ONLY\0'
         b'$VER: AMOSPro_AGA P0g private Draw preflight UNINSTALLED\0')
TITLE += bytes(len(TITLE) & 1)


def build() -> tuple[bytes, dict]:
    old, old_meta = build_p0f()
    tokens, parts, _ = unpack_ap20(old)
    original, old_labels = emit_bound_public()
    revised, labels = emit_checked_read()
    identity, identity_labels = emit_object_identity()
    if len(parts) != 95 or not parts[BOBS].endswith(original):
        raise ValueError('P0f public BOBS source provenance mismatch')
    if not parts[AGA].endswith(identity):
        raise ValueError('P0f checked identity group missing')
    if checked_read_offset() != len(AGA_CORE) + identity_labels['identity_check_entry']:
        raise ValueError('Relocated AGA identity offset mismatch')
    suffix = revised[len(original):]
    if not suffix or len(suffix) & 1 or len(suffix) > 24:
        raise ValueError('Unexpected checked-read native suffix size')
    updated = list(parts)
    updated[BOBS] += suffix
    if len(updated[BOBS]) > 65534 or not updated[BOBS].startswith(parts[BOBS]):
        raise ValueError('V2 Compiler BOBS unit overflow / prefix drift')
    if updated[AGA] != parts[AGA] or updated[:BOBS] != parts[:BOBS]:
        raise ValueError('A historical AP20 native group or stub was changed')
    candidate = repack_ap20(old, tokens, updated, TITLE)
    rt, entries, title = unpack_ap20(candidate)
    if (rt, entries, title) != (tokens, updated, TITLE):
        raise ValueError('AP20/HUNK repack changed source bytes')
    before = inspect(parse(old))
    after = inspect(parse(candidate))
    if before['issues'] or after['issues'] or before['tokens'] != after['tokens']:
        raise ValueError('P0g introduced an unintended public token/ABI change')
    if len([p for p in entries if p.startswith(DISPATCH_V2)]) != 4:
        raise ValueError('P0g unexpectedly changed the native unit count')
    old_links = interpreter_rbsr_displacements(parts)
    new_links = interpreter_rbsr_displacements(updated)
    reach = max(map(abs, new_links.values()))
    if set(old_links) != set(new_links) or reach >= 32766 or 32766 - reach < 64:
        raise ValueError('P0g exceeded signed AP20 GRouB PC16 margin')
    if len(entries) != 95 or old_meta['public_commands'] != 85:
        raise ValueError('P0g must retain the P0f public ABI')
    return candidate, dict(
        sha256=sha256(candidate).hexdigest(), size=len(candidate),
        predecessor_sha=old_meta['sha256'], public_commands=85,
        ap20_entries=95, native_groups=4, appended_bobs_bytes=len(suffix),
        checked_read_offset=checked_read_offset(),
        raw_read_entry=old_labels['relay_read_entry'],
        checked_read_entry=labels['relay_checked_read_entry'],
        pc16_reach=reach, pc16_margin=32766-reach,
        active_dist='UNCHANGED', public_draw='NOT IMPLEMENTED',
        gate_a='SOURCE BUILT, NATIVE TEST REQUIRED',
        gate_b='NOT TESTED', gate_c='NOT TESTED')


if __name__ == '__main__':
    print('M19 P0g PRIVATE CHECKED READ SOURCE ONLY', build()[1])
